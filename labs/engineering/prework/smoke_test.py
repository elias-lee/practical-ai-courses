"""Pre-work smoke test: one real model call, with the reply, token usage and latency.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    export OPENAI_API_KEY=...              # never commit keys; see README.md
    python smoke_test.py

If this prints a reply, your environment, key and network route to the provider all work.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional

from llm import LLM

# Environment variables each provider needs (as of 2026; LiteLLM's names).
PROVIDER_ENV_VARS: Dict[str, List[str]] = {
    "azure": ["AZURE_API_KEY", "AZURE_API_BASE", "AZURE_API_VERSION"],
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
}

SMOKE_MESSAGES: List[Dict[str, str]] = [
    {"role": "system", "content": "You are a terse assistant used to test an API connection."},
    {"role": "user", "content": "Reply with exactly: SitRep Assistant online."},
]


@dataclass
class SmokeResult:
    reply: str
    latency_s: float
    prompt_tokens: int
    completion_tokens: int
    usage_is_estimate: bool  # True when the provider did not report usage

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def provider_of(model: str) -> str:
    """'azure/my-deployment' -> 'azure'. A model string without a prefix -> ''."""
    return model.split("/", 1)[0] if "/" in model else ""


def check_environment(model: str, environ: Mapping[str, str]) -> List[str]:
    """Return a list of problems with the configuration; an empty list means ready to call."""
    if not model:
        return ["MODEL is not set, e.g. export MODEL=openai/gpt-4o-mini"]
    provider = provider_of(model)
    if provider not in PROVIDER_ENV_VARS:
        known = ", ".join(sorted(PROVIDER_ENV_VARS))
        return [f"MODEL {model!r} has no known provider prefix (expected one of: {known})"]
    return [f"{name} is not set (needed for {provider}/ models)"
            for name in PROVIDER_ENV_VARS[provider] if not environ.get(name)]


def rough_token_count(text: str) -> int:
    """About four characters per token for English: good enough to sanity-check a bill."""
    return max(1, round(len(text) / 4)) if text else 0


def run_smoke_test(llm: LLM, clock: Callable[[], float] = time.perf_counter) -> SmokeResult:
    """Send one short request, time it, and collect token usage."""
    start = clock()
    reply = llm(SMOKE_MESSAGES)
    latency = clock() - start

    usage: Optional[Dict[str, int]] = getattr(llm, "last_usage", None)
    if usage:
        return SmokeResult(reply, latency, usage.get("prompt_tokens", 0),
                           usage.get("completion_tokens", 0), usage_is_estimate=False)
    prompt_text = " ".join(m["content"] for m in SMOKE_MESSAGES)
    return SmokeResult(reply, latency, rough_token_count(prompt_text),
                       rough_token_count(reply), usage_is_estimate=True)


def format_result(model: str, result: SmokeResult) -> str:
    note = " (estimated: provider reported no usage)" if result.usage_is_estimate else ""
    return "\n".join([
        f"Model:    {model}",
        f"Reply:    {result.reply.strip()}",
        f"Tokens:   {result.prompt_tokens} in + {result.completion_tokens} out"
        f" = {result.total_tokens}{note}",
        f"Latency:  {result.latency_s:.2f} s",
    ])


def main(environ: Mapping[str, str] = os.environ) -> int:
    model = environ.get("MODEL", "")
    problems = check_environment(model, environ)
    if problems:
        print("Not ready yet:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    from llm import UsageTrackingLLM  # needs litellm installed

    try:
        result = run_smoke_test(UsageTrackingLLM(model, temperature=0))
    except Exception as exc:  # show the provider's message; see the troubleshooting table
        print(f"The call failed: {type(exc).__name__}: {exc}")
        return 2
    print(format_result(model, result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
