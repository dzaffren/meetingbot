from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt base: instructs the model to handle EN / Malay / Manglish
MULTILINGUAL_SYSTEM_PREAMBLE = """
You are MeetingBot, an AI personal assistant embedded in meetings for a Malaysian organisation.

Language guidelines:
- Users may speak or type in English, Bahasa Malaysia, or Manglish (a code-switched 
  mix of English and Malay, often with particles like "lah", "leh", "lor", "kan", 
  "boleh ke", "camne", "macam mana", etc.).
- Understand all three naturally. When responding, default to clear English unless 
  the user explicitly writes in Malay or Manglish, in which case you may mirror 
  their language style.
- For meeting minutes and formal outputs, always use formal English.
""".strip()


def get_foundry_client():
    """
    Return an authenticated Azure AI Foundry project client.

    Uses the project connection string from settings (AI Foundry Hub → Project).
    The client is synchronous; wrap calls with `asyncio.to_thread()` for async contexts.

    Returns:
        An `AIProjectClient` instance.
    """
    # TODO: Implement using azure-ai-projects.
    #
    # Example:
    #   from azure.ai.projects import AIProjectClient
    #   from azure.identity import DefaultAzureCredential
    #   s = get_settings()
    #   return AIProjectClient.from_connection_string(
    #       conn_str=s.azure_ai_foundry_project_connection_string,
    #       credential=DefaultAzureCredential(),
    #   )
    raise NotImplementedError("TODO: implement get_foundry_client()")


async def run_agent_thread(
    agent_id: str,
    user_message: str,
    thread_id: str | None = None,
    tool_outputs: list[dict[str, Any]] | None = None,
) -> str:
    """
    Create a thread (or reuse an existing one), post a user message, and run the agent
    to completion, processing any tool calls along the way.

    Args:
        agent_id: The AI Foundry agent ID to run.
        user_message: The user's input message.
        thread_id: Optional existing thread ID for multi-turn conversations.
        tool_outputs: Optional pre-computed tool outputs to submit.

    Returns:
        The final assistant response as a string.
    """
    # TODO: Implement the agent execution loop.
    #
    # Pattern:
    #   client = get_foundry_client()
    #
    #   # Create or reuse thread
    #   thread = (client.agents.get_thread(thread_id) if thread_id
    #             else client.agents.create_thread())
    #
    #   # Add user message
    #   client.agents.create_message(thread_id=thread.id, role="user", content=user_message)
    #
    #   # Run the agent (blocking — use asyncio.to_thread in async context)
    #   run = await asyncio.to_thread(
    #       client.agents.create_and_process_run,
    #       thread_id=thread.id,
    #       assistant_id=agent_id,
    #   )
    #
    #   if run.status == "failed":
    #       raise RuntimeError(f"Agent run failed: {run.last_error}")
    #
    #   # Retrieve last assistant message
    #   messages = client.agents.list_messages(thread_id=thread.id)
    #   for msg in messages.data:
    #       if msg.role == "assistant":
    #           return msg.content[0].text.value
    #
    #   return ""
    raise NotImplementedError("TODO: implement run_agent_thread()")


async def create_or_get_agent(
    name: str,
    instructions: str,
    tools: list[dict[str, Any]] | None = None,
    model: str | None = None,
) -> str:
    """
    Create an AI Foundry agent (or retrieve an existing one by name) and return its ID.

    In production, agents can be pre-created and their IDs stored in config/env to avoid
    re-creating on every request. This helper handles both cases.

    Args:
        name: Human-readable agent name (used for lookup).
        instructions: System instruction string for the agent.
        tools: List of tool schema dicts (function tool definitions).
        model: Model deployment name. Defaults to settings.azure_ai_foundry_model_deployment.

    Returns:
        The agent ID string.
    """
    # TODO: Implement agent creation / retrieval.
    #
    # Pattern:
    #   client = get_foundry_client()
    #   s = get_settings()
    #   agent = await asyncio.to_thread(
    #       client.agents.create_agent,
    #       model=model or s.azure_ai_foundry_model_deployment,
    #       name=name,
    #       instructions=instructions,
    #       tools=tools or [],
    #   )
    #   return agent.id
    raise NotImplementedError("TODO: implement create_or_get_agent()")

