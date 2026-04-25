from tools.search import search_web
from tools.scraper import scrape_multiple
from memory.chroma_store import save_research, retrieve_similar_research
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.1
)


def extract_subjects(query: str) -> tuple:
    """
    Uses LLM to intelligently split the query into two subjects.
    e.g. "compare lays vs kurkure" -> ("Lays", "Kurkure")
    e.g. "iphone 14 pro vs samsung galaxy s23" -> ("iPhone 14 Pro", "Samsung Galaxy S23")
    """
    print(f"[Researcher] Extracting subjects from query: '{query}'")

    prompt = f"""
You are a query parser. The user wants to compare two things.
Extract exactly two subjects from this query and return them as:
SUBJECT_A: <first subject>
SUBJECT_B: <second subject>

Only return those two lines, nothing else.

Query: "{query}"
"""
    response = llm.invoke(prompt)
    lines = response.content.strip().split("\n")

    subject_a = ""
    subject_b = ""

    for line in lines:
        if line.startswith("SUBJECT_A:"):
            subject_a = line.replace("SUBJECT_A:", "").strip()
        elif line.startswith("SUBJECT_B:"):
            subject_b = line.replace("SUBJECT_B:", "").strip()

    # Fallback: split by common separators if LLM fails
    if not subject_a or not subject_b:
        for separator in [" vs ", " versus ", " and ", " or ", " compared to "]:
            if separator in query.lower():
                parts = query.lower().split(separator)
                subject_a = parts[0].strip().title()
                subject_b = parts[1].strip().title()
                break

    print(f"[Researcher] Subject A: '{subject_a}' | Subject B: '{subject_b}'")
    return subject_a, subject_b


def researcher_agent(state: dict) -> dict:
    """
    Agent 1: Researcher
    - Extracts two subjects from the query
    - Searches each subject individually
    - Checks memory for past research
    - Presents all sources for human selection
    """

    query = state["query"]
    print(f"\n[Researcher] Starting research for: '{query}'")

    # Step 1: Extract two subjects from the query
    subject_a, subject_b = extract_subjects(query)
    state["subject_a"] = subject_a
    state["subject_b"] = subject_b

    # Step 2: Check memory for past research
    past_research = retrieve_similar_research(query, n_results=3)
    if past_research:
        print(f"[Researcher] Found {len(past_research)} past research entries in memory.")
    else:
        print("[Researcher] No past research found. Starting fresh.")

    # Step 3: Search each subject individually
    print(f"[Researcher] Searching for '{subject_a}' independently...")
    search_results_a = search_web(f"{subject_a} review price features analysis", max_results=5)

    print(f"[Researcher] Searching for '{subject_b}' independently...")
    search_results_b = search_web(f"{subject_b} review price features analysis", max_results=5)

    # Step 4: Combine all results for the human selection screen
    # Tag each result so we know which subject it belongs to
    for r in search_results_a:
        r["subject"] = subject_a
    for r in search_results_b:
        r["subject"] = subject_b

    all_results = search_results_a + search_results_b

    state["search_results_a"] = search_results_a
    state["search_results_b"] = search_results_b
    state["search_results"] = all_results
    state["past_research"] = past_research
    state["awaiting_source_selection"] = True

    print(f"\n[Researcher] Found {len(search_results_a)} sources for '{subject_a}' and {len(search_results_b)} for '{subject_b}'.")
    print("[Researcher] Waiting for user source selection.")
    return state


def researcher_agent_after_selection(state: dict) -> dict:
    """
    Runs after user selects sources.
    Scrapes selected URLs separately for each subject.
    """

    query = state["query"]
    subject_a = state["subject_a"]
    subject_b = state["subject_b"]
    selected_indices = state.get("selected_indices", [])
    all_results = state.get("search_results", [])

    # Get selected sources
    selected_sources = [all_results[i] for i in selected_indices if i < len(all_results)]

    # Split selected sources back into their subjects
    sources_a = [s for s in selected_sources if s.get("subject") == subject_a]
    sources_b = [s for s in selected_sources if s.get("subject") == subject_b]

    print(f"\n[Researcher] Scraping {len(sources_a)} sources for '{subject_a}'...")
    scraped_a = scrape_multiple([s["url"] for s in sources_a])

    print(f"[Researcher] Scraping {len(sources_b)} sources for '{subject_b}'...")
    scraped_b = scrape_multiple([s["url"] for s in sources_b])

    # Build separate research blocks
    raw_research_a = f"=== DATA FOR: {subject_a} ===\n"
    for item in scraped_a:
        raw_research_a += f"\nSource: {item['url']}\n{item['content']}\n"

    raw_research_b = f"=== DATA FOR: {subject_b} ===\n"
    for item in scraped_b:
        raw_research_b += f"\nSource: {item['url']}\n{item['content']}\n"

    # Include past research as context
    past_research = state.get("past_research", [])
    past_context = ""
    if past_research:
        past_context = "\n--- Past Research from Memory ---\n"
        for entry in past_research:
            past_context += f"\n{entry['content']}\n"

    # Save to memory
    combined = raw_research_a + "\n" + raw_research_b + past_context
    save_research(topic=query, content=combined)

    state["raw_research_a"] = raw_research_a
    state["raw_research_b"] = raw_research_b
    state["raw_research"] = combined
    state["selected_sources"] = selected_sources
    state["awaiting_source_selection"] = False

    print("[Researcher] Research complete. Passing to Analyst.")
    return state