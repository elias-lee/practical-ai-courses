"""extract_sitrep(llm, report) -> SitRep: prompt, parse, validate, and retry with feedback.

The loop in one sentence: ask; strip any ```json fence; parse; validate; if anything fails,
show the model its own reply plus the exact errors and ask again, at most ``max_attempts``
times; then fail loudly.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from llm import LLM
from sitrep_prompts import build_messages, repair_message
from sitrep_schema import SitRep, ValidationError, parse_sitrep

_FENCE = re.compile(r"```[a-zA-Z]*[ \t]*\n?(.*?)```", re.DOTALL)


class ExtractionError(Exception):
    """No valid SitRep after every attempt. Keeps the evidence for debugging."""

    def __init__(self, attempts: int, errors: List[str], replies: List[str]):
        self.attempts = attempts
        self.errors = errors      # validation errors from the last attempt
        self.replies = replies    # every raw reply, in order
        super().__init__(f"no valid SitRep after {attempts} attempts; last errors: "
                         + "; ".join(errors))


def strip_fences(text: str) -> str:
    """Keep only the inside of a ```json ... ``` fence (models add fences, and sometimes a line
    of prose around them, even when told not to). Text without a fence is returned as is."""
    match = _FENCE.search(text)
    return match.group(1).strip() if match else text.strip()


def parse_json(text: str) -> Any:
    try:
        return json.loads(strip_fences(text))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"reply is not valid JSON ({exc.msg} at line {exc.lineno}, "
                               f"column {exc.colno}); reply with a JSON object only"]) from exc


def extract_sitrep(llm: LLM, report: str, max_attempts: int = 3) -> SitRep:
    """Turn one field report into a validated SitRep, or raise ExtractionError."""
    messages: List[Dict[str, str]] = build_messages(report)
    replies: List[str] = []
    errors: List[str] = []
    for _ in range(max_attempts):
        reply = llm(messages)
        replies.append(reply)
        try:
            return parse_sitrep(parse_json(reply))
        except ValidationError as exc:
            errors = exc.errors
            # Keep the conversation: the model sees what it said and exactly what was wrong.
            messages = messages + [{"role": "assistant", "content": reply},
                                   repair_message(errors)]
    raise ExtractionError(max_attempts, errors, replies)
