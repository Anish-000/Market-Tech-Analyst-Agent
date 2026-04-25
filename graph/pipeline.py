from langgraph.graph import StateGraph, END
from agents.researcher import researcher_agent, researcher_agent_after_selection
from agents.analyst import analyst_agent
from agents.writer import writer_agent
from typing import TypedDict


class ResearchState(TypedDict):
    query: str
    subjects: list
    search_results_per_subject: dict
    search_results: list
    past_research: list
    selected_indices: list
    selected_sources: list
    raw_research_per_subject: dict
    raw_research: str
    analysis: str
    pdf_path: str
    awaiting_source_selection: bool
    error: str


def should_wait_for_selection(state: dict) -> str:
    if state.get("awaiting_source_selection", False):
        return "wait"
    return "continue"


def waiting_node(state: dict) -> dict:
    return state


def build_pipeline():
    graph = StateGraph(ResearchState)

    graph.add_node("researcher", researcher_agent)
    graph.add_node("waiting_for_selection", waiting_node)
    graph.add_node("researcher_after_selection", researcher_agent_after_selection)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("writer", writer_agent)

    graph.set_entry_point("researcher")

    graph.add_conditional_edges(
        "researcher",
        should_wait_for_selection,
        {
            "wait": "waiting_for_selection",
            "continue": "researcher_after_selection"
        }
    )

    graph.add_edge("waiting_for_selection", "researcher_after_selection")
    graph.add_edge("researcher_after_selection", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


def get_initial_state(query: str) -> dict:
    return {
        "query": query,
        "subjects": [],
        "search_results_per_subject": {},
        "search_results": [],
        "past_research": [],
        "selected_indices": [],
        "selected_sources": [],
        "raw_research_per_subject": {},
        "raw_research": "",
        "analysis": "",
        "pdf_path": "",
        "awaiting_source_selection": False,
        "error": ""
    }