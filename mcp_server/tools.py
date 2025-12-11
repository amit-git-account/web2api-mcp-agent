"""
tools.py

Defines the tools that the Web2API MCP Agent will expose.

For MVP v0.1, we define a simple in-memory representation of tools.
Later, these will be wired into a real MCP server implementation.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from .adapters.hackernews import fetch_top_posts
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


# --- Placeholder handlers ------------------------------------------------- #


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



# --- Tool registry -------------------------------------------------------- #


def get_tool_registry() -> List[Tool]:
    """
    Return the list of tools that this MCP server will expose.

    As we add more sites, we'll add more Tool entries here.
    """
    return [
        Tool(
            name="hn_get_top_posts",
            description="Fetch top posts from Hacker News (MVP dummy implementation).",
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
        )
    ]


def list_tools() -> List[Tool]:
    """Convenience wrapper for external callers (e.g., server.py)."""
    return get_tool_registry()
