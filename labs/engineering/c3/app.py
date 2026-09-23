"""SitRep Summarizer: a small, tested command-line LLM app, built spec-first.

Read SPEC.md first. Every function here exists to satisfy a numbered requirement (R1-R8),
and every requirement has a test in test_app.py.

    export MODEL=openai/gpt-4o-mini       # or azure/<deployment>, anthropic/<model>
    python app.py summarize sample_reports.md --max-words 120
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from llm import LLM, TransientError, is_transient, litellm_llm

MAX_INPUT_CHARS = 20_000

SYSTEM_PROMPT = """You summarize humanitarian field reports for a duty officer.
Rules:
- Use only information in the reports. Never invent facts, figures, places or dates.
- Copy every figure exactly as written, with its unit (households, people, families).
- If sources give different figures for the same thing, report both and write CONFLICT.
- If something important is missing (for example deaths or access), write "not stated".
- Neutral tone. No advice, no speculation.
Format: a heading "Summary", then short bullet points, then a line "Gaps:" listing
what is not stated."""


class RetryError(Exception):
    """Raised when a call still fails after all retries (R4)."""

    def __init__(self, attempts: int, last_error: BaseException):
        super().__init__(f"model call failed after {attempts} attempts: {last_error}")
        self.attempts = attempts


class BudgetExceeded(Exception):
    """Raised instead of making a call once the cost budget is used up (R7)."""


# --- R3 / R4: retries with exponential backoff --------------------------------------

def call_with_retry(
    llm: LLM,
    messages: List[Dict[str, str]],
    retries: int = 3,
    backoff: float = 1.0,
    max_backoff: float = 30.0,
    jitter: float = 0.1,
    sleep: Optional[Callable[[float], None]] = None,
    rand: Callable[[], float] = random.random,
) -> str:
    """Call ``llm(messages)``, retrying transient errors up to ``retries`` times.

    Waits ``backoff * 2**n`` seconds before retry n (1 s, 2 s, 4 s ... by default),
    capped at ``max_backoff``, plus up to ``jitter`` (10%) random extra so that many
    clients do not all retry at the same instant. ``sleep`` and ``rand`` are injectable
    so tests run instantly and deterministically.
    """
    if retries < 0:
        raise ValueError("retries must be >= 0")
    sleep = sleep or time.sleep   # looked up at call time, so tests can patch time.sleep
    attempt = 0
    while True:
        try:
            return llm(messages)
        except Exception as exc:
            if not is_transient(exc):
                raise  # bad request, auth, content filter: retrying will not help
            if attempt >= retries:
                raise RetryError(attempt + 1, exc) from exc
            delay = min(max_backoff, backoff * (2 ** attempt))
            sleep(delay * (1 + jitter * rand()))
            attempt += 1


# --- R6 / R7: token and cost accounting --------------------------------------------

def estimate_tokens(text: str) -> int:
    """Rough token estimate: about 4 characters per token for English text.

    Good enough for budgets and dashboards; use the provider's reported usage for billing.
    Arabic, Chinese and Russian text usually needs more tokens per character.
    """
    return max(1, math.ceil(len(text) / 4)) if text else 0


@dataclass
class CostTracker:
    """Accumulates calls, tokens and cost across a run."""

    price_in_per_mtok: float = 0.15    # USD per million input tokens (illustrative)
    price_out_per_mtok: float = 0.60   # USD per million output tokens (illustrative)
    max_cost_usd: Optional[float] = None
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    def record(self, input_tokens: int, output_tokens: int) -> None:
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    @property
    def cost_usd(self) -> float:
        return (self.input_tokens * self.price_in_per_mtok
                + self.output_tokens * self.price_out_per_mtok) / 1_000_000

    def check_budget(self) -> None:
        if self.max_cost_usd is not None and self.cost_usd >= self.max_cost_usd:
            raise BudgetExceeded(
                f"cost ${self.cost_usd:.6f} has reached the budget ${self.max_cost_usd:.6f}"
            )

    def summary(self) -> str:
        return (f"calls={self.calls} input_tokens={self.input_tokens} "
                f"output_tokens={self.output_tokens} cost_usd={self.cost_usd:.6f}")


def tracked(llm: LLM, tracker: CostTracker) -> LLM:
    """Wrap an LLM so every successful call is recorded with *estimated* tokens.

    Use this for fakes or providers that report no usage. With ``litellm_llm`` pass
    ``on_usage=tracker.record`` instead, to record exact counts (and don't wrap twice).
    """

    def call(messages: List[Dict[str, str]]) -> str:
        reply = llm(messages)
        prompt_text = "".join(m["content"] for m in messages)
        tracker.record(estimate_tokens(prompt_text), estimate_tokens(reply))
        return reply

    return call


# --- R1 / R2: the summarize command ------------------------------------------------

def build_messages(reports: str, max_words: int) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Summarize these field reports in at most {max_words} words.\n\n"
            f"<reports>\n{reports}\n</reports>"
        )},
    ]


def summarize(
    llm: LLM,
    reports: str,
    max_words: int = 150,
    tracker: Optional[CostTracker] = None,
    sleep: Optional[Callable[[float], None]] = None,
) -> str:
    """Summarize field reports with one (retried) model call."""
    if not reports.strip():
        raise ValueError("the reports are empty")
    if len(reports) > MAX_INPUT_CHARS:
        raise ValueError(
            f"the reports are {len(reports):,} characters; the limit is {MAX_INPUT_CHARS:,}"
        )
    if tracker is not None:
        tracker.check_budget()
    return call_with_retry(llm, build_messages(reports, max_words), sleep=sleep).strip()


# --- CLI ------------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None, llm: Optional[LLM] = None) -> int:
    """Entry point. Tests pass ``llm``; real runs build one from the MODEL variable."""
    parser = argparse.ArgumentParser(prog="app.py", description="SitRep Summarizer")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("summarize", help="summarize a file of field reports")
    s.add_argument("file")
    s.add_argument("--max-words", type=int, default=150)
    s.add_argument("--max-cost", type=float, default=None, help="budget in USD")
    args = parser.parse_args(argv)

    tracker = CostTracker(
        price_in_per_mtok=float(os.environ.get("PRICE_IN_PER_MTOK", "0.15")),
        price_out_per_mtok=float(os.environ.get("PRICE_OUT_PER_MTOK", "0.60")),
        max_cost_usd=args.max_cost,
    )
    if llm is not None:
        model_llm = tracked(llm, tracker)
    else:
        model = os.environ.get("MODEL")
        if not model:
            print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).",
                  file=sys.stderr)
            return 1
        model_llm = litellm_llm(model, temperature=0, on_usage=tracker.record)

    path = Path(args.file)
    try:
        reports = path.read_text(encoding="utf-8")
        text = summarize(model_llm, reports, args.max_words, tracker)
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except (RetryError, BudgetExceeded) as exc:
        print(f"Model error: {exc}", file=sys.stderr)
        return 3
    finally:
        print(tracker.summary(), file=sys.stderr)

    print(text)
    return 0


__all__ = [
    "BudgetExceeded", "CostTracker", "RetryError", "TransientError", "call_with_retry",
    "estimate_tokens", "main", "summarize", "tracked",
]

if __name__ == "__main__":
    raise SystemExit(main())
