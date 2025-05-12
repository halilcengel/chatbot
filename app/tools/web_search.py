import requests
from app.config import get_settings
from langchain.tools import Tool

settings = get_settings()

BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"

class BraveSearchError(Exception):
    pass

def brave_search(query: str, num_results: int = 3):
    """
    Query the Brave Search API and return a list of results.
    Each result is a dict with 'title', 'url', and 'snippet'.
    """
    api_key = settings.brave_search_api_key
    if not api_key:
        raise BraveSearchError("Brave Search API key is not set in the configuration.")

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": num_results,
    }
    response = requests.get(BRAVE_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise BraveSearchError(f"Brave Search API error: {response.status_code} {response.text}")
    data = response.json()
    results = []
    for item in data.get("web", {}).get("results", [])[:num_results]:
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("description"),
        })
    return results

def brave_search_tool_func(query: str) -> str:
    """LangChain tool wrapper for brave_search. Returns formatted string of results."""
    try:
        results = brave_search(query, num_results=3)
        if not results:
            return "No relevant web results found."
        formatted = "Web search results:\n"
        for i, r in enumerate(results, 1):
            formatted += f"\n{i}. {r['title']}\n{r['url']}\n{r['snippet'] or ''}\n"
        return formatted.strip()
    except BraveSearchError as e:
        return f"Brave Search error: {str(e)}"

def get_brave_search_tool():
    return Tool(
        name="Brave Web Search",
        func=brave_search_tool_func,
        description="Useful for answering questions about current events or when up-to-date information is needed from the web. Input should be a search query string."
    ) 