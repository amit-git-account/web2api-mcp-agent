"""
stdio_server.py

A super simple JSON-over-stdin/stdout server for Web2API tools.

This is NOT a full MCP implementation yet.
It just:
- Reads a single JSON request from stdin
- Calls the requested tool handler
- Writes a JSON response to stdout

Example request (stdin):
    {"tool": "hn_get_top_posts", "args": {"limit": 5}}

Example run:
    echo '{"tool": "hn_get_top_posts", "args": {"limit": 3}}' | python3 -m mcp_server.stdio_server
"""

import json
import sys
from typing import Any, Dict

from .tools import get_tool_registry, get_tool_manifest


def main() -> None:
    # Build tool lookup map
    tools = get_tool_registry()
    tool_map = {t.name: t for t in tools}

    # Read all data from stdin
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        error = {"ok": False, "error": "No input received on stdin"}
        print(json.dumps(error, ensure_ascii=False))
        return

    try:
        request: Dict[str, Any] = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        error = {
            "ok": False,
            "error": "Invalid JSON in request",
            "details": str(exc),
        }
        print(json.dumps(error, ensure_ascii=False))
        return

    # Support a simple "list_tools" command for discovery
    command = request.get("command")
    if command == "list_tools":
        manifest = get_tool_manifest()
        response = {
            "ok": True,
            "command": "list_tools",
            "manifest": manifest,
        }
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return



    tool_name = request.get("tool")
    args = request.get("args", {})

    if tool_name not in tool_map:
        error = {
            "ok": False,
            "error": f"Unknown tool {tool_name!r}",
            "available_tools": list(tool_map.keys()),
        }
        print(json.dumps(error, ensure_ascii=False))
        return

    tool = tool_map[tool_name]

    # Ensure args is a dict
    if not isinstance(args, dict):
        error = {
            "ok": False,
            "error": "Request 'args' must be an object/dict",
        }
        print(json.dumps(error, ensure_ascii=False))
        return

    # Call the handler
    try:
        result = tool.handler(args)
        response: Dict[str, Any] = {
            "ok": True,
            "tool": tool_name,
            "result": result,
        }
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        response = {
            "ok": False,
            "error": f"Tool {tool_name!r} raised an exception",
            "details": str(exc),
        }

    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
