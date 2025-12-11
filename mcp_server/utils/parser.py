"""
parser.py

Shared HTML parsing helpers.
"""

from typing import Optional

from bs4 import BeautifulSoup  # type: ignore


def parse_html(html: str) -> BeautifulSoup:
    """Return a BeautifulSoup DOM for the given HTML string."""
    return BeautifulSoup(html, "html.parser")


def safe_int(value: str) -> Optional[int]:
    """
    Convert a string to int, returning None if conversion fails.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
