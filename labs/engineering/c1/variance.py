"""Experiment: ask the same question N times and measure how much the answers vary.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    python variance.py                      # 10 samples at temperature 0, then at 1.0

LLM output is not a function of the input alone: sampling, provider-side batching and model
updates all introduce variation. Engineering consequences: never assume two runs agree,
normalise answers before comparing them, and decide in code what happens when they do not.
"""
from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from llm import LLM

HERE = Path(__file__).resolve().parent

QUESTION = ("How many households are affected by the flooding, according to these reports? "
            "Reply with a single number only.")

_NUMBER = re.compile(r"\d[\d,.\s]*\d|\d")


def sample(llm: LLM, messages: List[Dict[str, str]], n: int) -> List[str]:
    """Send the identical messages n times and collect the replies."""
    return [llm([dict(m) for m in messages]) for _ in range(n)]


def normalize_number(text: str) -> Optional[str]:
    """'About 1,200 households.' -> '1200'. Returns None if the reply has no number."""
    match = _NUMBER.search(text)
    if not match:
        return None
    return re.sub(r"[,.\s]", "", match.group(0))


@dataclass
class VarianceReport:
    n: int
    counts: Dict[str, int]      # normalised answer -> how many times it appeared
    unparseable: int            # replies with no usable answer
    majority: Optional[str]     # most common normalised answer (None if nothing parsed)
    agreement: float            # share of all n replies that gave the majority answer

    @property
    def distinct(self) -> int:
        return len(self.counts)


def analyse(replies: List[str],
            normalize: Callable[[str], Optional[str]] = normalize_number) -> VarianceReport:
    normalised = [normalize(r) for r in replies]
    counts = Counter(v for v in normalised if v is not None)
    unparseable = sum(1 for v in normalised if v is None)
    if not counts:
        return VarianceReport(len(replies), {}, unparseable, None, 0.0)
    majority, hits = counts.most_common(1)[0]
    return VarianceReport(len(replies), dict(counts), unparseable, majority,
                          hits / len(replies))


def majority_answer(replies: List[str], min_agreement: float = 0.7,
                    normalize: Callable[[str], Optional[str]] = normalize_number
                    ) -> Optional[str]:
    """Return the majority answer if enough samples agree; otherwise None (send to a human).

    This is 'self-consistency' voting: it costs n calls, so keep it for short, high-stakes
    answers. Disagreement is itself useful information: it often means the source is ambiguous.
    """
    report = analyse(replies, normalize)
    return report.majority if report.agreement >= min_agreement else None


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    from llm import litellm_llm

    reports = (HERE / "sample_reports.md").read_text(encoding="utf-8")
    messages = [{"role": "user", "content": f"{QUESTION}\n\n<reports>\n{reports}\n</reports>"}]
    for temperature in (0.0, 1.0):
        llm = litellm_llm(os.environ["MODEL"], temperature=temperature)
        replies = sample(llm, messages, n=10)
        report = analyse(replies)
        print(f"temperature={temperature}: {report.counts}  unparseable={report.unparseable}"
              f"  majority={report.majority}  agreement={report.agreement:.0%}")
        print(f"  decision: {majority_answer(replies) or 'no consensus -> human review'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
