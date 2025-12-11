"""
producthunt.py

Adapter for fetching top posts from the Product Hunt front page.

Note: Product Hunt's HTML structure may change over time and parts
of the page may be client-side rendered. The CSS selectors here
might need adjustment if parsing stops working.
"""

from typing import Any, Dict, List, Optional

from ..utils.http_client import get_html, HttpError
from ..utils.parser import parse_html, safe_int


PH_URL = "https://www.producthunt.com/"


def fetch_top_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top products from the Product Hunt front page.

    Args:
        limit: maximum number of products to return.

    Returns:
        A list of dicts with keys:
        - name (str)
        - tagline (str or None)
        - link (str)
        - votes (int or None)
        - comments (int or None)
        - rank (int or None)
    """
    html = get_html(PH_URL)
    soup = parse_html(html)

    products: List[Dict[str, Any]] = []

    # These selectors are approximate and may need changes
    # as Product Hunt updates their layout.
    #
    # Strategy:
    # - Each product is in a container (e.g., article or div)
    # - We look for a title element and a link
    # - Then we try to find tagline, votes, comments nearby
    product_items = soup.select("article[data-test='post-item'], div[data-test='post-item']")

    if not product_items:
        # Fallback: try a more generic selector as a backup
        product_items = soup.select("article, div")

    rank = 0

    for item in product_items:
        try:
            # Title + link
            title_el = (
                item.select_one("[data-test='post-name']") or
                item.select_one("h3 a") or
                item.select_one("h3") or
                item.select_one("a[data-test='post-name']")
            )
            if not title_el:
                continue

            name = title_el.get_text(strip=True)
            link = title_el.get("href", "").strip()
            if link and link.startswith("/"):
                link = "https://www.producthunt.com" + link

            # Tagline
            tagline_el = (
                item.select_one("[data-test='post-tagline']") or
                item.select_one("p")
            )
            tagline: Optional[str] = None
            if tagline_el:
                tagline = tagline_el.get_text(strip=True)

            # Votes
            votes_el = (
                item.select_one("[data-test='post-vote-count']") or
                item.select_one("button span")  # very rough fallback
            )
            votes: Optional[int] = None
            if votes_el:
                # e.g. "123" or "123 votes"
                votes_text = votes_el.get_text(strip=True).split()[0]
                votes = safe_int(votes_text)

            # Comments
            comments_el = (
                item.select_one("[data-test='post-comments-count']") or
                item.find("a", string=lambda s: s and "comment" in s.lower())
            )
            comments: Optional[int] = None
            if comments_el:
                parts = comments_el.get_text(strip=True).split()
                if parts and parts[0].isdigit():
                    comments = safe_int(parts[0])

            rank += 1

            products.append(
                {
                    "name": name,
                    "tagline": tagline,
                    "link": link,
                    "votes": votes,
                    "comments": comments,
                    "rank": rank,
                }
            )

        except Exception:
            # Skip bad rows and move on
            continue

    return products[: max(0, limit)]
