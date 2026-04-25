from tools.search import search_web
from tools.scraper import scrape_multiple
from memory.chroma_store import save_research, retrieve_similar_research
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.1
)


def extract_subjects(query: str) -> list:
    """
    Uses LLM to extract any number of subjects from the query.
    Returns a list of subject names.
    e.g. "compare lays, kurkure and haldirams" -> ["Lays", "Kurkure", "Haldirams"]
    e.g. "best budget phone" -> ["Budget Smartphones"]
    """
    print(f"[Researcher] Extracting subjects from query: '{query}'")

    prompt = f"""
You are a query parser. Extract all subjects the user wants to research or compare from this query.
Return ONLY a valid JSON array of strings. Nothing else. No explanation. No markdown.

Examples:
"compare lays vs kurkure" -> ["Lays", "Kurkure"]
"nvidia rtx 5090 vs amd rx 9070 vs rtx 4090" -> ["Nvidia RTX 5090", "AMD RX 9070", "Nvidia RTX 4090"]
"best budget smartphones" -> ["Budget Smartphones"]
"compare messi, ronaldo and mbappe" -> ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappe"]

Query: "{query}"
"""
    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Clean any accidental markdown
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        subjects = json.loads(raw)
        if isinstance(subjects, list) and len(subjects) > 0:
            print(f"[Researcher] Extracted {len(subjects)} subjects: {subjects}")
            return subjects
    except Exception:
        pass

    # Fallback: split by common separators
    print("[Researcher] LLM parse failed, using fallback splitter.")
    for separator in [" vs ", " versus ", " and ", " or ", ", "]:
        if separator in query.lower():
            parts = query.lower().split(separator)
            subjects = [p.strip().title() for p in parts if p.strip()]
            print(f"[Researcher] Fallback subjects: {subjects}")
            return subjects

    # Last resort: treat entire query as one subject
    return [query.strip().title()]


def researcher_agent(state: dict) -> dict:
    """
    Agent 1: Researcher
    - Extracts n subjects from the query dynamically
    - Searches each subject independently
    - Checks memory for past research
    - Prepares sources grouped by subject for human selection
    """

    query = state["query"]
    print(f"\n[Researcher] Starting research for: '{query}'")

    # Step 1: Extract all subjects dynamically
    subjects = extract_subjects(query)
    state["subjects"] = subjects

    # Step 2: Check memory for past research
    past_research = retrieve_similar_research(query, n_results=3)
    if past_research:
        print(f"[Researcher] Found {len(past_research)} past research entries in memory.")
    else:
        print("[Researcher] No past research found. Starting fresh.")

    # Step 3: Search each subject independently
    search_results_per_subject = {}
    all_results = []

    for subject in subjects:
        print(f"[Researcher] Searching independently for: '{subject}'...")
        results = search_web(
            f"{subject} review price features analysis",
            max_results=5
        )
        # Tag each result with its subject
        for r in results:
            r["subject"] = subject
        search_results_per_subject[subject] = results
        all_results.extend(results)

    state["search_results_per_subject"] = search_results_per_subject
    state["search_results"] = all_results
    state["past_research"] = past_research
    state["awaiting_source_selection"] = True

    total = len(all_results)
    print(f"\n[Researcher] Total sources found: {total} across {len(subjects)} subjects.")
    print("[Researcher] Waiting for user source selection.")
    return state


def researcher_agent_after_selection(state: dict) -> dict:
    """
    Runs after user selects sources.
    Scrapes selected URLs grouped by subject.
    Saves everything to memory.
    """

    query = state["query"]
    subjects = state["subjects"]
    selected_indices = state.get("selected_indices", [])
    all_results = state.get("search_results", [])

    # Get selected sources
    selected_sources = [
        all_results[i] for i in selected_indices if i < len(all_results)
    ]

    # Group selected sources by subject
    raw_research_per_subject = {}
    combined_research = ""

    for subject in subjects:
        subject_sources = [s for s in selected_sources if s.get("subject") == subject]
        urls = [s["url"] for s in subject_sources]

        if urls:
            print(f"[Researcher] Scraping {len(urls)} sources for '{subject}'...")
            scraped = scrape_multiple(urls)
        else:
            print(f"[Researcher] No sources selected for '{subject}', skipping scrape.")
            scraped = []

        subject_text = f"=== INDEPENDENT DATA FOR: {subject} ===\n"
        for item in scraped:
            subject_text += f"\nSource: {item['url']}\n{item['content']}\n"

        raw_research_per_subject[subject] = subject_text
        combined_research += subject_text + "\n"

    # Include past research as additional context
    past_research = state.get("past_research", [])
    if past_research:
        combined_research += "\n--- Past Research from Memory ---\n"
        for entry in past_research:
            combined_research += f"\n{entry['content']}\n"

    # Save to memory
    save_research(topic=query, content=combined_research)

    state["raw_research_per_subject"] = raw_research_per_subject
    state["raw_research"] = combined_research
    state["selected_sources"] = selected_sources
    state["awaiting_source_selection"] = False

    print("[Researcher] All subjects scraped. Passing to Analyst.")
    return state