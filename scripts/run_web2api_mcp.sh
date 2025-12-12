#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/amittomar-air/Desktop/projects/web2api-mcp-agent"
cd "$REPO_DIR"

# Force src-layout imports to work
export PYTHONPATH="$REPO_DIR/src"

# If you have env vars for web2api, load them here (optional)
if [[ -f "$HOME/.web2api_mcp.env" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.web2api_mcp.env"
fi

# IMPORTANT: run via the repo venv python, not a console script
exec "$REPO_DIR/.venv/bin/python" -m web2api_mcp.run_mcp
