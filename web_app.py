"""
web_app.py

Simple web UI for the Web2API MCP project.

- Shows a form to select `source` (Hacker News, Product Hunt, Reddit)
- Shows a `limit` field
- Calls the corresponding *_handler under the hood
- Renders items in a basic HTML table

Run with:
    python3 web_app.py

Then open:
    http://127.0.0.1:5000
"""

from typing import Any, Dict, List

from flask import Flask, render_template_string, request

from mcp_server.tools import (
    hn_get_top_posts_handler,
    ph_get_top_products_handler,
    reddit_get_top_posts_handler,
)

app = Flask(__name__)


TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Web2API MCP – Aggregator</title>
    <style>
      body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 2rem;
        background: #f5f5f5;
      }
      h1 {
        margin-bottom: 0.5rem;
      }
      .subtitle {
        margin-bottom: 1.5rem;
        color: #555;
      }
      form {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem;
      }
      label {
        font-size: 0.85rem;
        color: #333;
      }
      select,
      input[type="number"] {
        padding: 0.3rem 0.5rem;
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 0.9rem;
      }
      input[type="number"] {
        width: 80px;
      }
      button {
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        background: #2563eb;
        color: #fff;
        font-weight: 500;
        font-size: 0.9rem;
      }
      button:hover {
        background: #1d4ed8;
      }
      table {
        border-collapse: collapse;
        width: 100%;
        background: #fff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      }
      th, td {
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid #eee;
        text-align: left;
        vertical-align: top;
        font-size: 0.9rem;
      }
      th {
        background: #f9fafb;
        font-weight: 600;
      }
      tr:last-child td {
        border-bottom: none;
      }
      .rank {
        width: 40px;
      }
      .points, .comments {
        width: 90px;
        text-align: right;
      }
      .source-col {
        width: 110px;
        white-space: nowrap;
      }
      .error {
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        background: #fef2f2;
        color: #b91c1c;
      }
      .footer {
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #777;
      }
      a {
        color: #2563eb;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
      }
    </style>
  </head>
  <body>
    <h1>Web2API MCP – Aggregator</h1>
    <div class="subtitle">
      Fetch top items from Hacker News, Product Hunt, or Reddit via your Web2API tools.
    </div>

    <form method="get" action="/">
      <div>
        <label for="source">Source</label><br>
        <select id="source" name="source">
          <option value="hackernews" {{ 'selected' if selected_source == 'hackernews' else '' }}>
            Hacker News
          </option>
          <option value="producthunt" {{ 'selected' if selected_source == 'producthunt' else '' }}>
            Product Hunt
          </option>
          <option value="reddit" {{ 'selected' if selected_source == 'reddit' else '' }}>
            Reddit (r/all)
          </option>
        </select>
      </div>

      <div>
        <label for="limit">Items</label><br>
        <input
          type="number"
          id="limit"
          name="limit"
          min="1"
          max="50"
          value="{{ limit }}"
        />
      </div>

      <div>
        <button type="submit">Fetch</button>
      </div>
    </form>

    {% if error %}
      <div class="error">
        {{ error }}
        {% if error_details %}
          <div style="margin-top: 0.25rem; font-size: 0.8rem;">{{ error_details }}</div>
        {% endif %}
      </div>
    {% endif %}

    {% if posts %}
      <table>
        <thead>
          <tr>
            <th class="rank">#</th>
            <th>Title</th>
            <th>Link</th>
            <th class="source-col">Source</th>
            <th class="points">Points / Votes</th>
            <th class="comments">Comments</th>
          </tr>
        </thead>
        <tbody>
          {% for post in posts %}
            <tr>
              <td class="rank">{{ post.rank or "-" }}</td>
              <td>{{ post.title }}</td>
              <td>
                {% if post.link %}
                  <a href="{{ post.link }}" target="_blank" rel="noopener noreferrer">
                    {{ post.link }}
                  </a>
                {% else %}
                  -
                {% endif %}
              </td>
              <td class="source-col">
                {{ post.source or "-" }}
              </td>
              <td class="points">
                {% if post.points is not none %}
                  {{ post.points }}
                {% else %}
                  -
                {% endif %}
              </td>
              <td class="comments">
                {% if post.comments is not none %}
                  {{ post.comments }}
                {% else %}
                  -
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}

    <div class="footer">
      Backed by <code>hn_get_top_posts</code>, <code>ph_get_top_products</code>,
      and <code>reddit_get_top_posts</code> in <code>mcp_server.tools</code>.
    </div>
  </body>
</html>
"""


@app.route("/", methods=["GET"])
def index() -> Any:
    # Read query params with defaults
    raw_limit = request.args.get("limit", "10")
    source = request.args.get("source", "hackernews")

    error = None
    error_details = None
    posts: List[Dict[str, Any]] = []

    # Parse + clamp limit
    try:
        limit = int(raw_limit)
        if limit <= 0:
            raise ValueError("limit must be positive")
        if limit > 50:
            limit = 50
    except ValueError as exc:
        error = "Invalid 'limit' value. Using default of 10."
        error_details = str(exc)
        limit = 10

    # Choose handler based on source
    handler = None
    if source == "hackernews":
        handler = hn_get_top_posts_handler
    elif source == "producthunt":
        handler = ph_get_top_products_handler
    elif source == "reddit":
        handler = reddit_get_top_posts_handler
    else:
        if not error:
            error = f"Unknown source: {source}"

    # Call handler if we have one and no previous error
    if handler and not error:
        result = handler({"limit": limit})

        # If handler returned an error-like dict
        if isinstance(result, dict) and result.get("error"):
            error = result.get("error")
            error_details = result.get("details")
        else:
            # Normalize result items into a common shape
            normalized: List[Dict[str, Any]] = []
            rank_counter = 1
            for item in result:  # type: ignore[assignment]
                # Safely probe multiple key names
                title = (
                    item.get("title")
                    or item.get("name")
                    or "(no title)"
                )
                link = (
                    item.get("link")
                    or item.get("url")
                    or item.get("discussion_url")
                    or ""
                )
                points = (
                    item.get("points")
                    or item.get("score")
                    or item.get("votes")
                    or item.get("votes_count")
                )
                comments = (
                    item.get("comments")
                    or item.get("num_comments")
                    or item.get("comments_count")
                )

                normalized.append(
                    {
                        "rank": item.get("rank", rank_counter),
                        "title": title,
                        "link": link,
                        "points": points,
                        "comments": comments,
                        "source": source.capitalize(),
                    }
                )
                rank_counter += 1

            posts = normalized

    return render_template_string(
    TEMPLATE,
    limit=limit,
    posts=posts,
    error=error,
    error_details=error_details,
    selected_source=source,
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
