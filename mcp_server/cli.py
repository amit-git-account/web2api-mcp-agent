"""
cli.py

Simple command-line interface to call tools from the Web2API MCP Agent.

This is NOT the full MCP implementation yet, but it lets you:
- Invoke a tool by name
- Pass arguments from the command line
- See the JSON output

Example:
    python3 -m mcp_server.cli --tool hn_get_top_posts --limit 5
"""

import argparse
import json
from typing import Any, Dict

from .tools import get_tool_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI interface for Web2API MCP Agent tools"
    )
    parser.add_argument(
        "--tool",
        required=True,
        help="Name of the tool to run (e.g., hn_get_top_posts)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional 'limit' argument for tools that support it (e.g., hn_get_top_posts)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Build a simple args dict for the tool handler
    tool_args: Dict[str, Any] = {}
    if args.limit is not None:
        tool_args["limit"] = args.limit

    # Look up the tool
    tools = get_tool_registry()
    tool_map = {t.name: t for t in tools}

    if args.tool not in tool_map:
        available = ", ".join(tool_map.keys())
        raise SystemExit(
            f"Unknown tool {args.tool!r}. Available tools: {available}"
        )

    tool = tool_map[args.tool]

    # Call the handler
    result = tool.handler(tool_args)

    # Print as pretty JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
