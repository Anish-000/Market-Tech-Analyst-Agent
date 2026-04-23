from tools.search import search_web
from tools.scraper import scrape_multiple
from memory.chroma_store import save_research, retrieve_similar_research


def researcher_agent(state: dict) -> dict:
    """
    Agent 1: Researcher
    - Checks memory for past research on the same topic
    - Searches the web for new results
    - Presents all sources to the user for selection (human-in-the-loop)
    - Scrapes the selected sources
    - Saves results to memory
    - Updates and returns the shared state
    """

    query = state["query"]
    print(f"\n[Researcher] Starting research for: '{query}'")

    # Step 1: Check memory for any past research on this topic
    past_research = retrieve_similar_research(query, n_results=3)
    if past_research:
        print(f"[Researcher] Found {len(past_research)} past research entries in memory.")
    else:
        print("[Researcher] No past research found. Starting fresh.")

    # Step 2: Search the web for fresh results
    search_results = search_web(query, max_results=10)

    # Step 3: Pause and ask the user which sources to focus on
    # We store the results in state and set a flag for the UI to handle
    state["search_results"] = search_results
    state["past_research"] = past_research
    state["awaiting_source_selection"] = True

    print(f"\n[Researcher] Found {len(search_results)} sources. Waiting for user to select sources.")
    return state


def researcher_agent_after_selection(state: dict) -> dict:
    """
    This runs after the user has selected their preferred sources.
    Scrapes the selected URLs and saves research to memory.
    """

    query = state["query"]
    selected_indices = state.get("selected_indices", [])
    search_results = state.get("search_results", [])

    # Get only the sources the user selected
    selected_sources = [search_results[i] for i in selected_indices if i < len(search_results)]
    selected_urls = [s["url"] for s in selected_sources]

    print(f"\n[Researcher] Scraping {len(selected_urls)} selected sources...")

    # Step 4: Scrape the selected pages
    scraped_data = scrape_multiple(selected_urls)

    # Step 5: Combine scraped content into one research block
    combined_content = ""
    for item in scraped_data:
        combined_content += f"\nSource: {item['url']}\n{item['content']}\n"

    # Also include past research as additional context
    past_research = state.get("past_research", [])
    if past_research:
        combined_content += "\n--- Past Research from Memory ---\n"
        for entry in past_research:
            combined_content += f"\n{entry['content']}\n"

    # Step 6: Save this research session to memory for future use
    save_research(topic=query, content=combined_content)

    # Step 7: Update state for the next agent
    state["raw_research"] = combined_content
    state["selected_sources"] = selected_sources
    state["awaiting_source_selection"] = False

    print("[Researcher] Research complete. Passing to Analyst.")
    return state