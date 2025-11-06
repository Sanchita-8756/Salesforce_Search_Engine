import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncIterable, List

import httpx
import nest_asyncio
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    AgentCapabilities, 
    AgentSkill,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .salesforce_tools import (
    query_salesforce_records,
    create_salesforce_record,
    update_salesforce_record,
    describe_salesforce_object,
)
from .remote_agent_connection import RemoteAgentConnections

load_dotenv()
nest_asyncio.apply()


class HostAgent:
    """The Salesforce Host agent."""

    def __init__(
        self,
    ):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ""
        self._agent = self.create_agent()
        self._user_id = "host_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def _async_init_components(self, remote_agent_addresses: List[str]):
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(f"ERROR: Failed to get agent card from {address}: {e}")
                except Exception as e:
                    print(f"ERROR: Failed to initialize connection for {address}: {e}")

        agent_info = [
            json.dumps({"name": card.name, "description": card.description})
            for card in self.cards.values()
        ]
        if not agent_info:
            agentt_name = "Salesforce Agent"
            agentt_url = "http://salesforce-agent:10003"
            agentt_name = "Salesforce Agent"
            card = AgentCard(
                name=agentt_name,
                description="Salesforce agent.",
                url="http://salesforce-agent:10003",
                version="1.0.0",
                capabilities=AgentCapabilities(
                    chat=True,
                    task=True,
                    code_execution=False,
                    data_access=False
                ),
                skills=[
                    AgentSkill(
                        id="query_records",
                        name="query_records",
                        description="Queries Salesforce records.",
                        tags=["salesforce", "query"]
                    ),
                    AgentSkill(
                        id="create_record",
                        name="create_record",
                        description="Creates a new Salesforce record.",
                        tags=["salesforce", "create"]
                    ),
                    AgentSkill(
                        id="update_record",
                        name="update_record",
                        description="Updates an existing Salesforce record.",
                        tags=["salesforce", "update"]
                    ),
                ],
                defaultInputModes=["text"],
                defaultOutputModes=["text"],
            )
            remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=agentt_url
                    )
            self.remote_agent_connections[card.name] = remote_connection
            self.cards[card.name] = card
            agent_info = [json.dumps({"name": agentt_name, "description": "Manually registered Salesforce agent."})]
        
        print("agent_info:", agent_info)
        self.agents = "\n".join(agent_info) if agent_info else "No friends found"

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: List[str],
    ):
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-2.5-flash",
            name="host",
            instruction=self.root_instruction,
            description="This Host agent orchestrates Salesforce operations with specialized agents.",
            tools=[
                self.send_message,
                # query_salesforce_records,
                # create_salesforce_record,
                # update_salesforce_record,
                # describe_salesforce_object,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        return f"""
         **Role:** You are the Host Agent, an expert coordinator for Salesforce operations. Your primary function is to delegate requests to specialized Salesforce agents and provide clear summaries.

        **Core Directives:**

        *   **Delegate to Agents:** When users ask for Salesforce information (records, queries, objects), use the send_message tool to communicate with the appropriate agent.
        *   **Agent Communication:** Use send_message with agent_name "Salesforce Agent" for all Salesforce-related requests.
        *   **Summarize Results:** When agents return data, provide clear, concise summaries.
        *   **Handle Errors:** If agents return errors, explain the issue clearly to the user.
        *   **Tool Usage:** Always use the send_message tool to get information from Salesforce agents. Do not generate Salesforce data on your own.

        **Available Tools:**
        - send_message(agent_name, task, tool_context): Send requests to specialized agents

        **Today's Date (YYYY-MM-DD):** {datetime.now().strftime("%Y-%m-%d")}

        <Available Agents>
        {self.agents}
        </Available Agents>

        **Example Usage:**
        User: "get me all accounts"
        You should: send_message("Salesforce Agent", "get me all accounts", tool_context)
        """

    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a remote friend agent."""
        print(" Available agents:", list(self.agents))
        print(" Available agents:", list(self.remote_agent_connections))
        print(" Available agents:", list(self.remote_agent_connections.keys()))
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f"Client not available for {agent_name}")

        # Generate unique message ID for this request
        message_id = str(uuid.uuid4())
        
        # FIXED: Don't include taskId and contextId - let the remote agent create them
        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                # Removed: "taskId" and "contextId"
            },
        }

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        
        try:
            send_response: SendMessageResponse = await client.send_message(message_request)
            print(f"send_response root type: {type(send_response.root)}")
            print(f"send_response: {send_response}")

            if not isinstance(send_response.root, SendMessageSuccessResponse):
                error_msg = f"Received a non-success response: {send_response.root}"
                print(error_msg)
                return [{"error": error_msg}]

            if not isinstance(send_response.root.result, Task):
                error_msg = f"Response result is not a Task: {type(send_response.root.result)}"
                print(error_msg)
                return [{"error": error_msg}]

            task_result = send_response.root.result
            response_content = task_result.model_dump_json(exclude_none=True)
            json_content = json.loads(response_content)
            print(f"json_content after task result: {json_content}")
            resp = []
            if json_content.get("artifacts"):
                for artifact in json_content["artifacts"]:
                    if artifact.get("parts"):
                        for part in artifact["parts"]:
                            if part.get("text"):
                                resp.append({"text": part["text"]})
                            else:
                                resp.append(part)
            
            return resp if resp else [{"message": "Task completed successfully but no content returned"}]
            
        except Exception as e:
            error_msg = f"Error sending message to {agent_name}: {str(e)}"
            print(error_msg)
            return [{"error": error_msg}]


def _get_initialized_host_agent_sync():
    """Synchronously creates and initializes the HostAgent."""

    async def _async_main():
        # Hardcoded URLs for the Salesforce agents
        salesforce_agent_urls = [
            "http://salesforce-agent:10003" #docker urls
            # "http://localhost:10003",  # Salesforce Agent
        ]

        print("initializing host agent")
        hosting_agent_instance = await HostAgent.create(
            remote_agent_addresses=salesforce_agent_urls
        )
        print("HostAgent initialized")
        return hosting_agent_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print(
                f"Warning: Could not initialize HostAgent with asyncio.run(): {e}. "
                "This can happen if an event loop is already running (e.g., in Jupyter). "
                "Consider initializing HostAgent within an async function in your application."
            )
        else:
            raise


root_agent = _get_initialized_host_agent_sync()
