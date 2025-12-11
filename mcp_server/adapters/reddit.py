"""
reddit.py

Adapter for fetching top posts from Reddit (r/all, hot).

Uses Reddit's JSON endpoint. This is a simple, lightweight
integration suitable for demo purposes.
"""

from typing import Any, Dict, List

import requests

from ..utils.http_client import HttpError


REDDIT_URL = "https://www.reddit.com/r/all/hot.json"


def fetch_top_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top posts from r/all (hot) on Reddit.

    Args:
        limit: maximum number of posts to return (clamped to 1–50).

    Returns:
        A list of dicts with keys:
        - title (str)
        - link (str)
        - subreddit (str)
        - score (int)
        - comments (int)
        - rank (int)
        - over_18 (bool)
        - id (str)
    """
    if limit <= 0:
        limit = 10
    if limit > 50:
        limit = 50

    params = {"limit": limit}

    headers = {
        # A simple User-Agent string to be polite to Reddit
        "User-Agent": "web2api-mcp-agent/0.1 (demo script)",
    }

    try:
        resp = requests.get(REDDIT_URL, params=params, headers=headers, timeout=5.0)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HttpError(f"Failed to fetch Reddit data: {exc}") from exc

    data = resp.json()
    children = data.get("data", {}).get("children", [])

    posts: List[Dict[str, Any]] = []
    rank = 0

    for child in children:
        d = child.get("data", {})
        title = d.get("title", "").strip()
        if not title:
            continue

        permalink = d.get("permalink", "")
        if permalink and permalink.startswith("/"):
            link = "https://www.reddit.com" + permalink
        else:
            link = d.get("url", "")

        subreddit = d.get("subreddit", "")
        score = d.get("ups", 0)
        comments = d.get("num_comments", 0)
        over_18 = bool(d.get("over_18", False))
        post_id = d.get("id", "")

        rank += 1

        posts.append(
            {
                "title": title,
                "link": link,
                "subreddit": subreddit,
                "score": score,
                "comments": comments,
                "over_18": over_18,
                "rank": rank,
                "id": post_id,
            }
        )

    return posts[:limit]
