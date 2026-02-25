from __future__ import annotations

import logging
from typing import Literal

from app.agents.base import MULTILINGUAL_SYSTEM_PREAMBLE
from app.models.minutes import MeetingMinutes
from app.models.session import MeetingSession
from app.transcription.transcript_buffer import TranscriptBuffer

logger = logging.getLogger(__name__)

# Intent labels the orchestrator resolves before routing
Intent = Literal["generate_minutes", "answer_question", "assign_tasks", "unknown"]


async def resolve_intent(
    user_input: str,
    context: dict | None = None,
) -> Intent:
    """
    Use an LLM call (or rule-based heuristic) to classify the intent of an incoming request.

    Args:
        user_input: The raw user message or trigger event description.
        context: Optional context dict (e.g. {"trigger": "meeting_end"}).

    Returns:
        An Intent literal.
    """
    # TODO: Implement intent classification.
    #
    # Simple rule-based approach for Phase 1:
    #   trigger = (context or {}).get("trigger", "")
    #   if trigger == "meeting_end": return "generate_minutes"
    #   if trigger == "task_assignment": return "assign_tasks"
    #   keywords = ["what", "who", "when", "how", "explain", "tell me", "apa", "siapa", "macam mana"]
    #   if any(k in user_input.lower() for k in keywords): return "answer_question"
    #   return "unknown"
    #
    # LLM-based approach (more robust):
    #   Use a fast model call with a classification prompt returning one of the Intent labels.
    raise NotImplementedError("TODO: implement resolve_intent()")


async def run(
    user_input: str,
    session: MeetingSession,
    buffer: TranscriptBuffer | None = None,
    context: dict | None = None,
) -> dict:
    """
    Main orchestrator entry point. Resolves intent and delegates to the correct sub-agent.

    Args:
        user_input: The user's message or a system trigger description (e.g. "Meeting ended").
        session: The active MeetingSession.
        buffer: The live transcript buffer (if available).
        context: Optional context hints — e.g. {"trigger": "meeting_end", "conversation_id": "..."}

    Returns:
        A result dict. Shape depends on intent:
          - generate_minutes: {"minutes": MeetingMinutes, "sharepoint_url": str | None}
          - answer_question:  {"answer": str, "conversation_id": str}
          - assign_tasks:     {"tasks_created": int, "action_items": list}
          - unknown:          {"message": "I'm not sure how to help with that."}
    """
    # TODO: Implement orchestration routing.
    #
    # Pattern:
    #   intent = await resolve_intent(user_input, context)
    #   logger.info("Orchestrator resolved intent=%s for meeting=%s", intent, session.id)
    #
    #   if intent == "generate_minutes":
    #       from app.agents import minutes_agent, task_agent
    #       minutes = await minutes_agent.generate_minutes(session=session, buffer=buffer)
    #       minutes = await task_agent.assign_tasks(minutes)
    #       return {"minutes": minutes}
    #
    #   elif intent == "answer_question":
    #       from app.agents import qa_agent
    #       conversation_id = (context or {}).get("conversation_id", session.id)
    #       answer = await qa_agent.answer(
    #           question=user_input,
    #           meeting_id=session.id,
    #           conversation_id=conversation_id,
    #           buffer=buffer,
    #       )
    #       return {"answer": answer, "conversation_id": conversation_id}
    #
    #   elif intent == "assign_tasks":
    #       from app.agents import task_agent
    #       from app.storage.cosmos_client import CONTAINER_MINUTES, get_cosmos_store
    #       store = get_cosmos_store()
    #       doc = await store.get(CONTAINER_MINUTES, session.id)
    #       if not doc: return {"error": "No minutes found to assign tasks from."}
    #       minutes = MeetingMinutes(**doc)
    #       minutes = await task_agent.assign_tasks(minutes)
    #       return {"tasks_created": len(minutes.action_items), "action_items": [...]}
    #
    #   return {"message": "I'm not sure how to help with that."}
    raise NotImplementedError("TODO: implement orchestrator.run()")
