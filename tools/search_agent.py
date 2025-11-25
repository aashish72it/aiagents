
from utils.logger import logger

def _is_ascii(s: str) -> bool:
    """Check if string contains only ASCII characters."""
    return all(ord(c) < 128 for c in s)

def _search_duckduckgo(query: str, max_results: int = 5):
    """
    Search DuckDuckGo and return structured results: title, link, snippet.
    Prefer English results using region="wt-wt".
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(
                query,
                region="wt-wt",         # Worldwide English
                safesearch="moderate",  # Suitable default
                max_results=max_results
            )

            structured_results = []
            for r in results:
                title = r.get("title") or "Untitled"
                link = r.get("href") or "#"
                snippet = r.get("body") or ""
                if _is_ascii(snippet):
                    structured_results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })

            # Fallback: if filtering removes everything, return original results
            return structured_results if structured_results else [
                {
                    "title": r.get("title") or "Untitled",
                    "link": r.get("href") or "#",
                    "snippet": r.get("body") or ""
                }
                for r in results
            ]
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed, fallback to LangChain tool: {e}")

    # Fallback: LangChain community wrapper
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        tool = DuckDuckGoSearchRun()
        out = tool.run(query)
        return [{"title": "Result", "link": "#", "snippet": out}]
    except Exception as e:
        logger.error(f"DuckDuckGo search fallback failed: {e}")
        return []

def search_tool(state):
    query = state.context.get("query") or state.goal
    state.attempts += 1
    res = _search_duckduckgo(query)
    state.result = {"query": query, "snippets": res}
    if not res:
        state.errors.append("No search results")
    return state
