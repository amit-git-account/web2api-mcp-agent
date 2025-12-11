"""
tools.py

Defines the tools that the Web2API MCP Agent will expose.

For MVP v0.1, we define a simple in-memory representation of tools.
Later, these will be wired into a real MCP server implementation.
"""

"""
tools.py

Defines the tools that the Web2API MCP Agent will expose.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# Now that we're always importing through the `mcp_server` package,
# these simple relative imports are safe.
from .adapters.hackernews import fetch_top_posts
from .adapters.producthunt import fetch_top_products
from .adapters.reddit import fetch_top_posts as reddit_fetch_top_posts
from .utils.http_client import HttpError




@dataclass
class Tool:
    """
    Simple representation of a tool.

    In a real MCP implementation, this will map closely to the MCP Tool schema:
    - name
    - description
    - JSON schema for arguments
    - handler (callable)
    """

    name: str
    description: str
    handler: Callable[[Dict[str, Any]], Any]
    args_schema: Optional[Dict[str, Any]] = None


# --- Handlers ------------------------------------------------------------- #


def hn_get_top_posts_handler(args: Dict[str, Any]) -> Any:
    """
    Handler for Hacker News tool.

    - Reads 'limit' from args (default 10)
    - Uses the Hacker News adapter to fetch live data
    - Returns a list of posts (JSON-serializable)
    """
    raw_limit = args.get("limit", 10)

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = 10

    if limit <= 0:
        limit = 10

    try:
        posts = fetch_top_posts(limit=limit)
    except HttpError as exc:
        return {
            "error": "Failed to fetch Hacker News posts",
            "details": str(exc),
        }

    return posts


def ph_get_top_products_handler(args: Dict[str, Any]) -> Any:
    """
    Handler for Product Hunt tool.

    - Reads 'limit' from args (default 10)
    - Uses the Product Hunt adapter to fetch live data
    - Returns a list of products (JSON-serializable)
    """
    raw_limit = args.get("limit", 10)

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = 10

    if limit <= 0:
        limit = 10

    try:
        products = fetch_top_products(limit=limit)
    except HttpError as exc:
        return {
            "error": "Failed to fetch Product Hunt products",
            "details": str(exc),
        }

    return products


def reddit_get_top_posts_handler(args: Dict[str, Any]) -> Any:
    """
    Handler for Reddit tool.

    - Reads 'limit' from args (default 10)
    - Uses the Reddit adapter to fetch live data from r/all (hot)
    - Returns a list of posts (JSON-serializable)
    """
    raw_limit = args.get("limit", 10)

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = 10

    if limit <= 0:
        limit = 10

    try:
        posts = reddit_fetch_top_posts(limit=limit)
    except HttpError as exc:
        return {
            "error": "Failed to fetch Reddit posts",
            "details": str(exc),
        }

    return posts


# --- Tool registry -------------------------------------------------------- #


def get_tool_registry() -> List[Tool]:
    """
    Return the list of tools that this MCP server will expose.

    As we add more sites, we'll add more Tool entries here.
    """
    return [
        Tool(
            name="hn_get_top_posts",
            description="Fetch top posts from the Hacker News front page.",
            handler=hn_get_top_posts_handler,
            args_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of posts to return.",
                        "default": 10,
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="ph_get_top_products",
            description="Fetch top products from the Product Hunt front page.",
            handler=ph_get_top_products_handler,
            args_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of products to return.",
                        "default": 10,
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="reddit_get_top_posts",
            description="Fetch top posts from r/all (hot) on Reddit.",
            handler=reddit_get_top_posts_handler,
            args_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of posts to return.",
                        "default": 10,
                    }
                },
                "required": [],
            },
        ),
    ]


def get_tool_manifest() -> Dict[str, Any]:
    """
    Build a simple manifest describing available tools
    from the tool registry.

    This is a first step toward MCP-style tool discovery.
    """
    tools = get_tool_registry()
    return {
        "version": "0.1",
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.args_schema,
            }
            for t in tools
        ],
    }


def list_tools() -> List[Tool]:
    """Convenience wrapper for external callers (e.g., server.py)."""
    return get_tool_registry()
