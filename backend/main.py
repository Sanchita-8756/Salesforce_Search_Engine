# backend/main.py
"""
FastAPI backend - lightweight bridge between frontend and Salesforce MCP server.
Routes:
  POST /query  -> execute SOQL queries and data retrieval
  POST /action -> create/update/delete Salesforce records
  GET  /history -> returns recent operations
"""

import os, json, time, requests, sys
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Attempt to import Salesforce components for direct invocation fallback
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "salesforce-mcp-server"))
    from utils.salesforce_client import SalesforceClient
    from utils.salesforce_agent import SalesforceAgent
    DIRECT_AGENT_AVAILABLE = True
except Exception:
    DIRECT_AGENT_AVAILABLE = False

app = FastAPI(title="Salesforce MCP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# configuration: Salesforce MCP server port
SALESFORCE_MCP_PORT = os.getenv("SALESFORCE_MCP_PORT", "8002")

# Simple request models
class CommandPayload(BaseModel):
    command: str
    payload: Optional[Dict[str, Any]] = None

def _call_salesforce_mcp(tool: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Call Salesforce MCP server over SSE/HTTP.
    Note: This is a simplified HTTP interface - in production you'd use proper MCP protocol.
    """
    # For now, fall back to direct agent call since SSE requires more complex setup
    raise Exception("MCP HTTP not implemented - using direct agent fallback")

def _direct_salesforce_call(operation: str, payload: Optional[Dict[str, Any]] = None):
    """
    Fallback: call Salesforce agent directly.
    """
    if not DIRECT_AGENT_AVAILABLE:
        raise RuntimeError("Direct Salesforce agent not available.")
    
    client = SalesforceClient()
    agent = SalesforceAgent(client)
    
    # Parse operation and call appropriate method
    if operation.startswith("soql:"):
        soql = operation[5:].strip()
        return agent.run_soql(soql)
    elif operation.startswith("get:"):
        parts = operation[4:].strip().split("/")
        if len(parts) == 2:
            return agent.get_record(parts[0], parts[1])
    elif operation.startswith("create:"):
        object_name = operation[7:].strip()
        return agent.create_record(object_name, payload or {})
    elif operation.startswith("update:"):
        parts = operation[7:].strip().split("/")
        if len(parts) == 2:
            return agent.update_record(parts[0], parts[1], payload or {})
    elif operation.startswith("delete:"):
        parts = operation[7:].strip().split("/")
        if len(parts) == 2:
            return agent.delete_record(parts[0], parts[1])
    elif operation == "list_objects":
        return agent.list_objects()
    elif operation.startswith("describe:"):
        object_name = operation[9:].strip()
        return agent.describe_object(object_name)
    
    raise ValueError(f"Unrecognized operation: {operation}")


@app.on_event("startup")
def startup_event():
    print("Salesforce MCP Backend starting...")


@app.post("/query")
async def query_route(cmd: CommandPayload):
    """
    Execute Salesforce queries (SOQL, describe, get records).
    """
    try:
        # Try MCP first, fallback to direct agent
        try:
            resp = _call_salesforce_mcp("run_soql", {"soql": cmd.command})
            return resp
        except Exception:
            # Direct agent fallback
            resp = _direct_salesforce_call(cmd.command, cmd.payload)
            return {"success": True, "data": resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/action")
async def action_route(cmd: CommandPayload):
    """
    Execute Salesforce actions (create, update, delete records).
    """
    try:
        # Try MCP first, fallback to direct agent
        try:
            resp = _call_salesforce_mcp("create_record", {"command": cmd.command, "payload": cmd.payload})
            return resp
        except Exception:
            # Direct agent fallback
            resp = _direct_salesforce_call(cmd.command, cmd.payload)
            return {"success": True, "data": resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def history(limit: int = 20):
    # Simple in-memory history for now
    return {"count": 0, "items": []}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "salesforce-mcp-backend"}
