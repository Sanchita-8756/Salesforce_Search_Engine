"""
FastMCP server exposing SalesforceAgent as HTTP MCP tools.

Usage:
    python mcp_servers/salesforce_agent_server.py

This starts a Starlette + Uvicorn server that exposes SalesforceAgent
methods as MCP-compatible tools over Server-Sent Events (SSE).
Your ADK Agent can then connect to: http://localhost:8002/sse
"""

import sys
import os
import yaml
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

# Ensure repo root on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.salesforce_client import SalesforceClient
from utils.salesforce_agent import SalesforceAgent

from fastmcp import FastMCP
from mcp.server.sse import SseServerTransport


CONFIG_PATH = os.path.join(os.path.dirname(__file__),"config", "config.yaml.example")
print(CONFIG_PATH)
try:
    with open(CONFIG_PATH, "r") as fh:
        cfg = yaml.safe_load(fh)
except FileNotFoundError:
    cfg = {}

scfg = cfg.get("settings", {}).get("salesforce", {})

username = scfg.get("username") or os.environ.get("SF_USERNAME")
print(username)
password = scfg.get("password") or os.environ.get("SF_PASSWORD")
print(password)
security_token = scfg.get("security_token") or os.environ.get("SF_SECURITY_TOKEN")
print(security_token)
domain = scfg.get("domain") or os.environ.get("SF_DOMAIN")
instance_url = scfg.get("instance_url") or os.environ.get("SF_INSTANCE_URL")

sf_client = SalesforceClient(username, password, security_token, domain, instance_url)
agent = SalesforceAgent(sf_client)


mcp = FastMCP(name=os.environ.get("MCP_NAME", "salesforce-action-agent"))


@mcp.tool()
def run_soql(soql: str) -> dict:
    """Run an arbitrary SOQL query. Returns raw Salesforce response."""
    return agent.run_soql(soql)


@mcp.tool()
def query_all(soql: str) -> dict:
    """Run SOQL and return all fetched records (handles nextRecordsUrl)."""
    records = agent.query_all(soql)
    return {"total": len(records), "records": records}


@mcp.tool()
def get_record(object_name: str, record_id: str) -> dict:
    return agent.get_record(object_name, record_id)


@mcp.tool()
def create_record(object_name: str, payload: dict) -> dict:
    return agent.create_record(object_name, payload)


@mcp.tool()
def update_record(object_name: str, record_id: str, payload: dict) -> dict:
    return agent.update_record(object_name, record_id, payload)


@mcp.tool()
def delete_record(object_name: str, record_id: str) -> dict:
    return agent.delete_record(object_name, record_id)


@mcp.tool()
def describe_object(object_name: str) -> dict:
    return agent.describe_object(object_name)


@mcp.tool()
def list_objects() -> dict:
    return agent.list_objects()


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


async def login_page(request: Request):
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "login.html"))


async def dashboard_page(request: Request):
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "dashboard.html"))


async def callback_handler(request: Request):
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "login.html"))


async def root_redirect(request: Request):
    return RedirectResponse(url="/login")


app = Starlette(
    debug=True,
    routes=[
        Route("/", endpoint=root_redirect, methods=["GET"]),
        Route("/login", endpoint=login_page, methods=["GET"]),
        Route("/dashboard", endpoint=dashboard_page, methods=["GET"]),
        Route("/callback", endpoint=callback_handler, methods=["GET"]),
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages", app=MessageHandler()),
        Mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static"),
    ],
)


if __name__ == "__main__":
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host=host, port=port, log_level="info")

