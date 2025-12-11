"""
web_app.py

Simple web UI for the Web2API MCP project.

- Shows a form to enter `limit`
- Calls the `hn_get_top_posts_handler` under the hood
- Renders posts in a basic HTML table

Run with:
    python3 web_app.py

Then open:
    http://127.0.0.1:5000
"""

from typing import Any, Dict, List

from flask import Flask, render_template_string, request

from mcp_server.tools import hn_get_top_posts_handler


app = Flask(__name__)


TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Web2API MCP – Hacker News UI</title>
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
        align-items: center;
        gap: 0.5rem;
      }
      input[type="number"] {
        width: 80px;
        padding: 0.3rem 0.5rem;
      }
      button {
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        background: #2563eb;
        color: #fff;
        font-weight: 500;
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
    <h1>Web2API MCP – Hacker News</h1>
    <div class="subtitle">
      Fetch top posts from Hacker News via your Web2API tool.
    </div>

    <form method="get" action="/">
      <label for="limit">Posts:</label>
      <input
        type="number"
        id="limit"
        name="limit"
        min="1"
        max="50"
        value="{{ limit }}"
      />
      <button type="submit">Fetch</button>
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
            <th class="points">Points</th>
            <th class="comments">Comments</th>
          </tr>
        </thead>
        <tbody>
          {% for post in posts %}
            <tr>
              <td class="rank">{{ post.rank or "-" }}</td>
              <td>{{ post.title }}</td>
              <td>
                <a href="{{ post.link }}" target="_blank" rel="noopener noreferrer">
                  {{ post.link }}
                </a>
              </td>
              <td class="points">{{ post.points if post.points is not none else "-" }}</td>
              <td class="comments">{{ post.comments if post.comments is not none else "-" }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}

    <div class="footer">
      Backed by <code>hn_get_top_posts</code> in <code>mcp_server.tools</code>.
    </div>
  </body>
</html>
"""


@app.route("/", methods=["GET"])
def index() -> Any:
    # Read limit from query params, default 10
    raw_limit = request.args.get("limit", "10")
    error = None
    error_details = None
    posts: List[Dict[str, Any]] = []

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

    # Call your existing tool handler
    result = hn_get_top_posts_handler({"limit": limit})

    if isinstance(result, dict) and result.get("error"):
        error = result.get("error")
        error_details = result.get("details")
    else:
        posts = result  # type: ignore[assignment]

    return render_template_string(
        TEMPLATE,
        limit=limit,
        posts=posts,
        error=error,
        error_details=error_details,
    )


if __name__ == "__main__":
    app.run(debug=True)
