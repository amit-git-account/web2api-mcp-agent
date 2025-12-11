"""
hackernews.py

Adapter for fetching top posts from Hacker News front page.
"""

from typing import Any, Dict, List

from ..utils.http_client import get_html, HttpError
from ..utils.parser import parse_html, safe_int


HN_URL = "https://news.ycombinator.com/"


def fetch_top_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top posts from the Hacker News front page.

    Args:
        limit: maximum number of posts to return.

    Returns:
        A list of dicts with keys:
        - title (str)
        - link (str)
        - rank (int or None)
        - points (int or None)
        - comments (int or None)
    """
    html = get_html(HN_URL)
    soup = parse_html(html)

    posts: List[Dict[str, Any]] = []

    # Each story row has class "athing"
    story_rows = soup.select("tr.athing")

    for story in story_rows:
        try:
            # Rank
            rank = None
            rank_text = story.select_one("span.rank")
            if rank_text and rank_text.text.strip().endswith("."):
                rank_value = rank_text.text.strip().rstrip(".")
                rank = safe_int(rank_value)

            # Title + link
            title_link = story.select_one("span.titleline > a")
            if not title_link:
                continue

            title = title_link.text.strip()
            link = title_link.get("href", "").strip()

            # Subtext row (points, comments) is the next <tr>
            subtext_row = story.find_next_sibling("tr")
            points = None
            comments = None
            if subtext_row:
                subtext = subtext_row.select_one("td.subtext")
                if subtext:
                    score_span = subtext.select_one("span.score")
                    if score_span and score_span.text:
                        # e.g., "123 points"
                        score_text = score_span.text.split()[0]
                        points = safe_int(score_text)

                    # The last <a> in subtext is usually the comments link: "45 comments"
                    links = subtext.find_all("a")
                    if links:
                        last_a = links[-1]
                        if "comment" in last_a.text:
                            parts = last_a.text.split()
                            if parts and parts[0].isdigit():
                                comments = safe_int(parts[0])

            posts.append(
                {
                    "title": title,
                    "link": link,
                    "rank": rank,
                    "points": points,
                    "comments": comments,
                }
            )

        except Exception:
            # Skip bad rows but keep going
            continue

    return posts[: max(0, limit)]
