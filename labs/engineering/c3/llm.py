"""The only thing the app knows about a model: messages in, text out.

Keeping the model behind this tiny interface means the tests can swap in a scripted
fake, and you can swap providers by changing one string.

Compared with the Class 6 version, this adapter adds two things a real app needs:

- it turns the provider's "try again later" errors (rate limits, timeouts, server errors)
  into one exception type, ``TransientError``, so the retry logic in ``app.py`` does not
  need to know which provider you use;
- it reports the real token counts of every call to an optional ``on_usage`` callback,
  so cost tracking can use exact numbers instead of estimates.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

# A chat message is {"role": "system" | "user" | "assistant", "content": "..."}.
LLM = Callable[[List[Dict[str, str]]], str]

# on_usage(input_tokens, output_tokens) is called after every successful real call.
UsageCallback = Callable[[int, int], None]


class TransientError(Exception):
    """A failure that may succeed if you wait and try again (429, timeout, 5xx)."""


# Exception class names LiteLLM uses for retryable failures (as of 2026). Matching on
# names keeps this module importable without LiteLLM installed.
_TRANSIENT_NAMES = {
    "RateLimitError",
    "Timeout",
    "APITimeoutError",
    "APIConnectionError",
    "InternalServerError",
    "ServiceUnavailableError",
}
_TRANSIENT_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


def is_transient(exc: BaseException) -> bool:
    """True if ``exc`` looks like a temporary provider problem worth retrying."""
    if isinstance(exc, TransientError):
        return True
    if type(exc).__name__ in _TRANSIENT_NAMES:
        return True
    return getattr(exc, "status_code", None) in _TRANSIENT_STATUS


def litellm_llm(
    model: str,
    timeout: float = 60.0,
    on_usage: Optional[UsageCallback] = None,
    **kwargs: Any,
) -> LLM:
    """Return an LLM function backed by LiteLLM, which speaks to any provider.

    Model strings (as of 2026; check your provider for current names):

    - Azure OpenAI: ``"azure/<your-deployment-name>"`` with ``AZURE_API_KEY``,
      ``AZURE_API_BASE`` and ``AZURE_API_VERSION`` set in the environment.
    - OpenAI:       ``"openai/gpt-4o-mini"`` with ``OPENAI_API_KEY`` set.
    - Anthropic:    ``"anthropic/claude-sonnet-4-5"`` with ``ANTHROPIC_API_KEY`` set.

    ``timeout`` (seconds) bounds every call: a hung connection becomes a
    ``TransientError`` instead of freezing the app. Extra keyword arguments
    (e.g. ``temperature=0``) are passed to every call. LiteLLM is imported lazily,
    so the tests never need it installed.
    """

    def call(messages: List[Dict[str, str]]) -> str:
        import litellm  # lazy: only needed when a real model is used

        try:
            response = litellm.completion(
                model=model, messages=messages, timeout=timeout, **kwargs
            )
        except Exception as exc:  # translate provider errors into our two categories
            if is_transient(exc):
                raise TransientError(f"{type(exc).__name__}: {exc}") from exc
            raise
        usage = getattr(response, "usage", None)
        if on_usage is not None and usage is not None:
            on_usage(int(usage.prompt_tokens or 0), int(usage.completion_tokens or 0))
        return response.choices[0].message.content or ""

    return call
