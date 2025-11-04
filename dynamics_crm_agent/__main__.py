import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
	AgentCapabilities,
	AgentCard,
	AgentSkill,
)
from agent import create_agent
from agent_executor import DynamicsCrmAgentExecutor
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
	"""Exception for missing API key."""

	pass


def main():
	"""Starts the Dynamics CRM agent server."""
	host = "localhost"
	port = 10006
	try:
		# Check for API key only if Vertex AI is not configured
		if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
			if not os.getenv("GOOGLE_API_KEY"):
				raise MissingAPIKeyError(
					"GOOGLE_API_KEY environment variable not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
				)

		capabilities = AgentCapabilities(streaming=True)
		skill = AgentSkill(
			id="dynamics_crm_operations",
			name="Dynamics CRM Operations",
			description="Manages Dynamics CRM records, queries, and entity metadata via MCP tools.",
			tags=["dynamics", "crm", "microsoft", "automation"],
			examples=[
				"Run OData query: contacts?$select=fullname,emailaddress1&$top=5",
				"Create a Contact with first and last name",
				"Describe the Account entity",
			],
		)
		agent_card = AgentCard(
			name="Dynamics CRM Agent",
			description="An agent that works with Dynamics CRM via MCP tools (query, CRUD, describe).",
			url=f"http://{host}:{port}/",
			version="1.0.0",
			defaultInputModes=["text/plain"],
			defaultOutputModes=["text/plain"],
			capabilities=capabilities,
			skills=[skill],
		)

		adk_agent = create_agent()
		runner = Runner(
			app_name=agent_card.name,
			agent=adk_agent,
			artifact_service=InMemoryArtifactService(),
			session_service=InMemorySessionService(),
			memory_service=InMemoryMemoryService(),
		)
		agent_executor = DynamicsCrmAgentExecutor(runner)

		request_handler = DefaultRequestHandler(
			agent_executor=agent_executor,
			task_store=InMemoryTaskStore(),
		)
		server = A2AStarletteApplication(
			agent_card=agent_card, http_handler=request_handler
		)

		uvicorn.run(server.build(), host=host, port=port)
	except MissingAPIKeyError as e:
		logger.error(f"Error: {e}")
		exit(1)
	except Exception as e:
		logger.error(f"An error occurred during server startup: {e}")
		exit(1)


if __name__ == "__main__":
	main()