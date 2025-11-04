"""
FastMCP server exposing DynamicsCrmAgent as HTTP MCP tools.

Usage:
    python mcp_servers/dynamics_crm_agent_server.py

This starts a Starlette + Uvicorn server that exposes DynamicsCrmAgent
methods as MCP-compatible tools over Server-Sent Events (SSE).
Your ADK Agent can then connect to: http://localhost:8003/sse
"""

import sys
import os
import yaml
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

# Ensure repo root on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dynamics_crm_client import DynamicsCrmClient
from utils.dynamics_crm_agent import DynamicsCrmAgent

from fastmcp import FastMCP
from mcp.server.sse import SseServerTransport


CONFIG_PATH = os.path.join(os.path.dirname(__file__),"config", "config.yaml.example")
print(CONFIG_PATH)
try:
    with open(CONFIG_PATH, "r") as fh:
        cfg = yaml.safe_load(fh)
except FileNotFoundError:
    cfg = {}

crm_cfg = cfg.get("settings", {}).get("dynamics_crm", {})

server_url = crm_cfg.get("server_url") or os.environ.get("CRM_SERVER_URL")
print(server_url)
username = crm_cfg.get("username") or os.environ.get("CRM_USERNAME")
password = crm_cfg.get("password") or os.environ.get("CRM_PASSWORD")
domain = crm_cfg.get("domain") or os.environ.get("CRM_DOMAIN")
client_id = crm_cfg.get("client_id") or os.environ.get("CRM_CLIENT_ID")
client_secret = crm_cfg.get("client_secret") or os.environ.get("CRM_CLIENT_SECRET")
tenant_id = crm_cfg.get("tenant_id") or os.environ.get("CRM_TENANT_ID")

crm_client = DynamicsCrmClient(server_url, username, password, domain, client_id, client_secret, tenant_id)
agent = DynamicsCrmAgent(crm_client)


mcp = FastMCP(name=os.environ.get("MCP_NAME", "dynamics-crm-action-agent"))


@mcp.tool()
def run_odata_query(odata_query: str) -> dict:
    """Run an arbitrary OData query. Returns raw Dynamics CRM response."""
    return agent.run_odata_query(odata_query)


@mcp.tool()
def query_all(odata_query: str) -> dict:
    """Run OData query and return all fetched records (handles @odata.nextLink)."""
    records = agent.query_all(odata_query)
    return {"total": len(records), "records": records}


@mcp.tool()
def get_record(entity_name: str, record_id: str) -> dict:
    """Get a single record by entity name and ID."""
    return agent.get_record(entity_name, record_id)


@mcp.tool()
def create_record(entity_name: str, payload: dict) -> dict:
    """Create a new record in the specified entity."""
    return agent.create_record(entity_name, payload)


@mcp.tool()
def update_record(entity_name: str, record_id: str, payload: dict) -> dict:
    """Update an existing record."""
    return agent.update_record(entity_name, record_id, payload)


@mcp.tool()
def delete_record(entity_name: str, record_id: str) -> dict:
    """Delete a record by entity name and ID."""
    return agent.delete_record(entity_name, record_id)


@mcp.tool()
def get_entity_metadata(entity_name: str) -> dict:
    """Get metadata for a specific entity."""
    return agent.get_entity_metadata(entity_name)


@mcp.tool()
def list_entities() -> dict:
    """List all available entities in the CRM system."""
    return agent.list_entities()


@mcp.tool()
def get_contacts(filter_query: str = None) -> dict:
    """Get contacts with optional OData filter."""
    records = agent.get_contacts(filter_query)
    return {"total": len(records), "records": records}


@mcp.tool()
def get_accounts(filter_query: str = None) -> dict:
    """Get accounts with optional OData filter."""
    records = agent.get_accounts(filter_query)
    return {"total": len(records), "records": records}


@mcp.tool()
def get_opportunities(filter_query: str = None) -> dict:
    """Get opportunities with optional OData filter."""
    records = agent.get_opportunities(filter_query)
    return {"total": len(records), "records": records}


@mcp.tool()
def get_leads(filter_query: str = None) -> dict:
    """Get leads with optional OData filter."""
    records = agent.get_leads(filter_query)
    return {"total": len(records), "records": records}


sse = SseServerTransport("/messages")


async def handle_sse(request: Request):
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())


class MessageHandler:
    async def __call__(self, scope, receive, send):
        await sse.handle_post_message(scope, receive, send)


app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages", app=MessageHandler()),
    ],
)


if __name__ == "__main__":
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host=host, port=port, log_level="info")