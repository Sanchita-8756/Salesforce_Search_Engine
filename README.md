# salesforce-mcp-server

Expose Salesforce operations as MCP tools via SSE.

## Quickstart

1. Copy `.env.example` to `.env` and fill credentials.
2. Create `config/config.yaml` from `config/config.yaml.example` or rely on env vars.
3. Install dependencies:

```bash
~python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt~
```

4. Run server:

```bash
python mcp_servers/salesforce_agent_server.py
```

5. Connect your ADK agent to `http://localhost:8002/sse` and call tools like `run_soql`, `create_record`.

