from __future__ import annotations

import logging
from typing import Any

from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt base: instructs the model to handle EN / Malay / Manglish
MULTILINGUAL_SYSTEM_PREAMBLE = """
You are MeetingBot, an AI assistant embedded in meetings for a Malaysian organisation.

Language guidelines:
- Users may speak or type in English, Bahasa Malaysia, or Manglish (a code-switched 
  mix of English and Malay, often with particles like "lah", "leh", "lor", "kan", 
  "boleh ke", "camne", "macam mana", etc.).
- Understand all three naturally. When responding, default to clear English unless 
  the user explicitly writes in Malay or Manglish, in which case you may mirror 
  their language style.
- For meeting minutes and formal outputs, always use formal English.
""".strip()


def _build_client() -> AsyncAzureOpenAI:
    s = get_settings()
    return AsyncAzureOpenAI(
        azure_endpoint=s.azure_openai_endpoint,
        api_key=s.azure_openai_api_key,
        api_version=s.azure_openai_api_version,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def chat_completion(
    messages: list[ChatCompletionMessageParam],
    response_format: dict[str, Any] | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Call Azure OpenAI chat completion with retry.
    Returns the assistant message content as a string.
    """
    s = get_settings()
    client = _build_client()

    kwargs: dict[str, Any] = {
        "model": s.azure_openai_deployment,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = await client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content or ""
    return content


def system_message(extra: str = "") -> ChatCompletionMessageParam:
    """Build a system message combining the multilingual preamble with any extra instruction."""
    content = MULTILINGUAL_SYSTEM_PREAMBLE
    if extra:
        content = f"{content}\n\n{extra}"
    return {"role": "system", "content": content}
