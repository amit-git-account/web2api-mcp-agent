"""
server.py

Entry point for the Web2API MCP Agent.

For MVP v0.1, this file will:
- Initialize logging
- Initialize the MCP server runtime (in a later step)
- Register tools defined in tools.py
- Start listening for MCP requests over stdio
"""

import logging
from typing import NoReturn

from . import tools


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure basic logging for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    )
    logger.info("Logging configured")


def run_server() -> NoReturn:
    """
    Main loop for the MCP server.

    For now, this is just a placeholder that logs startup and the registered tools.
    In a later step, we'll wire this into a real MCP stdio server implementation.
    """
    configure_logging()

    logger.info("Starting Web2API MCP Agent (MVP v0.1 skeleton)")

    # In the future, we'll initialize a real MCP server here and register tools.
    # For now, we just log the tools that would be exposed.
    available_tools = tools.list_tools()
    logger.info("Registered tools: %s", [t.name for t in available_tools])

    logger.info("MCP server skeleton is running (no real MCP protocol yet).")
    logger.info("Press Ctrl+C to exit.")

    try:
        # Placeholder "run forever" loop.
        # This is where an MCP event loop will eventually live.
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Web2API MCP Agent")


if __name__ == "__main__":
    run_server()
