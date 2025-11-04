from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams


def create_agent() -> LlmAgent:
	"""Constructs the ADK agent for Dynamics CRM operations."""
	return LlmAgent(
		model="gemini-2.5-flash",
		name="DynamicsCRM_Agent",
		instruction="""
			You are a Dynamics CRM operations assistant. Use MCP tools to run OData queries,
			read and modify CRM records, and describe entities. Prefer real
			data via tools; do not fabricate fields or entity names.
		""",
		tools=[
			MCPToolset(
				connection_params=SseServerParams(
					url="http://localhost:8003/sse",  # FastMCP Dynamics CRM server
				)
			)
		],
	)