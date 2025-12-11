"""
http_client.py

Simple HTTP helpers for fetching HTML pages.
"""

import requests


class HttpError(Exception):
    """Custom exception for HTTP-related errors."""


def get_html(url: str, timeout: float = 5.0) -> str:
    """
    Fetch the raw HTML content for the given URL.

    Raises:
        HttpError: if the request fails or returns a non-2xx status.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HttpError(f"Failed to fetch URL {url!r}: {exc}") from exc

    return response.text
