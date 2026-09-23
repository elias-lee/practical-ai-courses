"""The only thing the lab knows about a model: messages in, text out.

Keeping the model behind this tiny interface means the tests can swap in a scripted
fake, and you can swap providers by changing one string.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

# A chat message is {"role": "system" | "user" | "assistant", "content": "..."}.
LLM = Callable[[List[Dict[str, str]]], str]


def litellm_llm(model: str, **kwargs: Any) -> LLM:
    """Return an LLM function backed by LiteLLM, which speaks to any provider.

    Model strings (as of 2026; check your provider for current names):

    - Azure OpenAI: ``"azure/<your-deployment-name>"`` with ``AZURE_API_KEY``,
      ``AZURE_API_BASE`` and ``AZURE_API_VERSION`` set in the environment.
    - OpenAI:       ``"openai/gpt-4o-mini"`` with ``OPENAI_API_KEY`` set.
    - Anthropic:    ``"anthropic/claude-sonnet-4-5"`` with ``ANTHROPIC_API_KEY`` set.

    Extra keyword arguments (e.g. ``temperature=0``) are passed to every call.
    LiteLLM is imported lazily, so the tests never need it installed.
    """

    def call(messages: List[Dict[str, str]]) -> str:
        import litellm  # lazy: only needed when a real model is used

        response = litellm.completion(model=model, messages=messages, **kwargs)
        return response.choices[0].message.content or ""

    return call
