"""
Basic tests for the Hacker News adapter / tool.

Run with:
    python3 -m unittest tests.test_hn_adapter
"""

import unittest

from mcp_server.tools import hn_get_top_posts_handler


class TestHackerNewsAdapter(unittest.TestCase):
    def test_returns_list_of_posts(self) -> None:
        # Ask for a small number of posts
        args = {"limit": 3}
        result = hn_get_top_posts_handler(args)

        # Should be a list
        self.assertIsInstance(result, list)

        # Should not return more than requested
        self.assertLessEqual(len(result), 3)

        if result:
            first = result[0]
            # Check basic fields exist
            self.assertIn("title", first)
            self.assertIn("link", first)
            self.assertIn("rank", first)
            self.assertIn("points", first)
            self.assertIn("comments", first)

            # Types sanity check
            self.assertIsInstance(first["title"], str)
            self.assertIsInstance(first["link"], str)


if __name__ == "__main__":
    unittest.main()
