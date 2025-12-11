"""
Quick local test for the Hacker News adapter.

Run with:
    python3 test_hn_local.py
"""

from mcp_server.tools import hn_get_top_posts_handler


def main() -> None:
    # Ask for top 5 posts from HN
    args = {"limit": 5}
    result = hn_get_top_posts_handler(args)

    print(f"Returned {len(result)} posts")
    for i, post in enumerate(result, start=1):
        print(f"{i}. {post['title']} ({post['link']}) - points={post['points']}, comments={post['comments']}")


if __name__ == "__main__":
    main()
