from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web(query: str, max_results: int = 10) -> list:
    """
    Searches the web for the given query using Tavily.
    Returns a list of results, each containing title, url, and content.
    """
    print(f"[Search] Searching for: '{query}'")

    response = client.search(
        query=query,
        max_results=max_results,
        include_raw_content=False
    )

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title", "No title"),
            "url": item.get("url", ""),
            "content": item.get("content", "")
        })

    print(f"[Search] Found {len(results)} results.")
    return results