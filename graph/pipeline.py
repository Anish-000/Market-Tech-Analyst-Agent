from langgraph.graph import StateGraph, END
from agents.researcher import researcher_agent, researcher_agent_after_selection
from agents.analyst import analyst_agent
from agents.writer import writer_agent
from typing import TypedDict, Any


# This defines the structure of the shared state dictionary
# Every agent reads from and writes to this same object
class ResearchState(TypedDict):
    query: str
    subject_a: str
    subject_b: str
    search_results_a: list
    search_results_b: list
    search_results: list
    past_research: list
    selected_indices: list
    selected_sources: list
    raw_research_a: str
    raw_research_b: str
    raw_research: str
    analysis: str
    pdf_path: str
    awaiting_source_selection: bool
    error: str


def should_wait_for_selection(state: dict) -> str:
    """
    This is a conditional edge function.
    It checks if we are waiting for user source selection.
    If yes, it stops at the waiting node.
    If no, it proceeds to scraping and analysis.
    """
    if state.get("awaiting_source_selection", False):
        return "wait"
    return "continue"


def waiting_node(state: dict) -> dict:
    """
    This node does nothing by itself.
    It simply acts as a pause point in the graph.
    The UI detects the awaiting_source_selection flag
    and renders the source selection screen.
    """
    return state


def build_pipeline():
    """
    Builds and compiles the full LangGraph pipeline.
    Returns a compiled graph ready to be invoked.
    """

    graph = StateGraph(ResearchState)

    # Add all nodes to the graph
    graph.add_node("researcher", researcher_agent)
    graph.add_node("waiting_for_selection", waiting_node)
    graph.add_node("researcher_after_selection", researcher_agent_after_selection)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("writer", writer_agent)

    # Define the flow
    # Start -> Researcher
    graph.set_entry_point("researcher")

    # Researcher -> check if waiting for user input
    graph.add_conditional_edges(
        "researcher",
        should_wait_for_selection,
        {
            "wait": "waiting_for_selection",
            "continue": "researcher_after_selection"
        }
    )

    # After user selects sources -> scrape and continue
    graph.add_edge("waiting_for_selection", "researcher_after_selection")

    # Researcher after selection -> Analyst
    graph.add_edge("researcher_after_selection", "analyst")

    # Analyst -> Writer
    graph.add_edge("analyst", "writer")

    # Writer -> End
    graph.add_edge("writer", END)

    return graph.compile()


# Initial empty state template
def get_initial_state(query: str) -> dict:
    return {
        "query": query,
        "subject_a": "",
        "subject_b": "",
        "search_results_a": [],
        "search_results_b": [],
        "search_results": [],
        "past_research": [],
        "selected_indices": [],
        "selected_sources": [],
        "raw_research_a": "",
        "raw_research_b": "",
        "raw_research": "",
        "analysis": "",
        "pdf_path": "",
        "awaiting_source_selection": False,
        "error": ""
    }