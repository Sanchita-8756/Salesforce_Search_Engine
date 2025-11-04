from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams


def create_agent() -> LlmAgent:
	"""Constructs the ADK agent for Salesforce operations."""
	return LlmAgent(
		model="gemini-2.5-flash",
		name="Salesforce_Agent",
		instruction="""
			You are a Salesforce operations assistant. Use MCP tools to run SOQL,
			read and modify Salesforce records, and describe objects. Prefer real
			data via tools; do not fabricate fields or object names.
		""",
		tools=[
			MCPToolset(
				connection_params=SseServerParams(
					url="http://localhost:8002/sse",  # FastMCP Salesforce server
				)
			)
		],
	)


