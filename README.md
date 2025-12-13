# Web2API MCP Tool  

---

## ✨ Features

- 🔌 **Local MCP Server** compatible with Claude Desktop  
- ⚡ **Fetch top posts** from:
  - Hacker News  
  - Reddit
  - Product Hunt (next tool - TODO)
- 🧩 Tools implemented in Python with clean handlers  
- 🔒 Secure, local execution  
- 🎯 Deterministic responses (no hallucination about API data)  

---

## 🏗️ Architecture

Below is the high-level request/response flow between Claude ↔ MCP Layer ↔ External APIs:

![Architecture Diagram](./architecture.png)

*(Replace `architecture.png` with your generated PNG:  
`A_flowchart_digital_diagram_illustrates_the_archit.png`)*

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/<yourname>/web2api-mcp-tool.git
cd web2api-mcp-tool

### 2. Create VIrtual environment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 3. Run the server manually 

python -m mcp_server.mcp_server

### 4. Add this to your Claude_dekstop_config.json

{
  "mcpServers": {
    "web2api": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "mcp_server.mcp_server"]
    }
  }
}


### 5. You should see 
web2api  ✓ connected


### 6. Once connected to Claude, use
Show me today's top HackerNews or Reddit posts using web2api.



🧠 Why This Tool Exists (the “Why MCP?” section)

Claude could hallucinate API data if asked directly.
Claude cannot safely call external URLs on its own.

This MCP tool fills the gap:

Fresh data from APIs

No hallucinations

Local control & security

Deterministic behavior

Composable with any future tools you add

This is the emerging pattern for AI-native apps:
LLMs + Tooling + Real-world APIs
