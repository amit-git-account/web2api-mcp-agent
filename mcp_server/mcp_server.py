"""
mcp_server.py

MCP server for the Web2API project.

Exposes tools so MCP clients (ChatGPT, Claude, VS Code, etc.)
can fetch top items from:

- Hacker News
- Product Hunt
- Reddit

It reuses the existing handlers in mcp_server.tools.
"""

"""
mcp_server.py

MCP server for the Web2API project.
"""
import os
import sys
import traceback
from typing import Any, Dict, List

# --- ensure project root is on sys.path so `mcp_server.*` imports work ---
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from mcp.server.fastmcp import FastMCP  # type: ignore[import]

# Import tools via the package name, NOT relative
from mcp_server.tools import (
    hn_get_top_posts_handler,
    ph_get_top_products_handler,
    reddit_get_top_posts_handler,
)



# Create the MCP server instance
mcp = FastMCP("web2api")


def _call_handler_safely(handler, args: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Call a legacy handler (which returns either a list or an error dict)
    and normalize error handling.
    """
    result = handler(args)

    if isinstance(result, dict) and result.get("error"):
        # Surface a clear error back to the MCP client
        details = result.get("details") or ""
        raise RuntimeError(f"{result['error']}. {details}")

    # We expect a list of dict-like items
    return list(result)  # type: ignore[arg-type]


def _normalize_items(source: str, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize different adapter outputs into a common schema.

    Output item shape:
      {
          "rank": int,
          "title": str,
          "link": str,
          "points": int | None,
          "comments": int | None,
          "source": str,   # e.g., "HackerNews", "ProductHunt", "Reddit"
      }
    """
    normalized: List[Dict[str, Any]] = []
    rank_counter = 1

    for item in raw_items:
        title = (
            item.get("title")
            or item.get("name")
            or "(no title)"
        )
        link = (
            item.get("link")
            or item.get("url")
            or item.get("discussion_url")
            or ""
        )
        points = (
            item.get("points")
            or item.get("score")
            or item.get("votes")
            or item.get("votes_count")
        )
        comments = (
            item.get("comments")
            or item.get("num_comments")
            or item.get("comments_count")
        )

        normalized.append(
            {
                "rank": item.get("rank", rank_counter),
                "title": title,
                "link": link,
                "points": points,
                "comments": comments,
                "source": source,
            }
        )
        rank_counter += 1

    return normalized


@mcp.tool()
async def hn_get_top_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top posts from the Hacker News front page.

    Args:
        limit: Maximum number of posts to return (default 10, max 50).
    """
    limit = max(1, min(limit, 50))
    raw_items = _call_handler_safely(hn_get_top_posts_handler, {"limit": limit})
    return _normalize_items("HackerNews", raw_items)


@mcp.tool()
async def ph_get_top_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top products from the Product Hunt front page.

    Args:
        limit: Maximum number of products to return (default 10, max 50).
    """
    limit = max(1, min(limit, 50))
    raw_items = _call_handler_safely(ph_get_top_products_handler, {"limit": limit})
    return _normalize_items("ProductHunt", raw_items)


@mcp.tool()
async def reddit_get_top_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top posts from r/all (hot) on Reddit.

    Args:
        limit: Maximum number of posts to return (default 10, max 50).
    """
    limit = max(1, min(limit, 50))
    raw_items = _call_handler_safely(reddit_get_top_posts_handler, {"limit": limit})
    return _normalize_items("Reddit", raw_items)


@mcp.tool()
async def get_feed(source: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Unified feed tool.

    Args:
        source: One of "hackernews", "producthunt", "reddit"
        limit: Maximum number of items to return (default 10, max 50).

    Returns:
        A list of normalized items with fields:
        [rank, title, link, points, comments, source]
    """
    source_key = source.lower().strip()
    limit = max(1, min(limit, 50))

    if source_key == "hackernews":
        raw = _call_handler_safely(hn_get_top_posts_handler, {"limit": limit})
        return _normalize_items("HackerNews", raw)
    elif source_key == "producthunt":
        raw = _call_handler_safely(ph_get_top_products_handler, {"limit": limit})
        return _normalize_items("ProductHunt", raw)
    elif source_key == "reddit":
        raw = _call_handler_safely(reddit_get_top_posts_handler, {"limit": limit})
        return _normalize_items("Reddit", raw)

    raise ValueError("Invalid source. Use one of: hackernews, producthunt, reddit.")


def main() -> None:
    """
    Entry point for running the MCP server over stdio.
    """
    try:
        mcp.run(transport="stdio")
    except Exception:
        # Log the full traceback to stderr so Claude can show it in logs
        print("Fatal error in MCP server:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # Re-raise so the process still exits (Claude will see disconnect)
        raise



if __name__ == "__main__":
    main()
