import os
import sys

# Always add this file's directory to sys.path so Python can find `mcp_server`
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcp_server.mcp_server import main  # type: ignore[import]

if __name__ == "__main__":
    main()

