"""Run the full SitRep pipeline against a real model.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    python run_demo.py                      # uses sample_reports.md
    python run_demo.py my_reports.md        # or your own (fictional!) reports

Pipeline: orchestrator plans -> agents execute the plan -> Writer/Reviewer loop polishes.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from agents import SITREP_AGENTS
from llm import LLM, litellm_llm
from orchestrator import PlanError, plan, review_loop, run_plan

HERE = Path(__file__).resolve().parent


def traced(llm: LLM) -> LLM:
    """Wrap an LLM to print one line per call: a poor man's trace (Class 7 does it properly)."""
    counter = {"n": 0}

    def call(messages):
        counter["n"] += 1
        role = messages[0]["content"].splitlines()[0][:60]
        start = time.time()
        reply = llm(messages)
        print(f"  [call {counter['n']}] {role!r} -> {len(reply)} chars in {time.time() - start:.1f}s")
        return reply

    return call


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    reports_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "sample_reports.md"
    reports = reports_path.read_text(encoding="utf-8")
    llm = traced(litellm_llm(os.environ["MODEL"], temperature=0))

    request = (
        "Produce a situation report for the flooding in Northern Veloria province from the "
        "field reports below. The final step should be a Writer draft.\n\n" + reports
    )

    print("1) Planning...")
    try:
        steps = plan(llm, request, list(SITREP_AGENTS))
    except PlanError as exc:
        print(f"Plan rejected: {exc}")
        return 2
    if not steps:
        print("The orchestrator judged this request out of scope.")
        return 0
    for s in steps:
        print(f"   {s.id:<12} {s.agent:<10} depends_on={s.depends_on}")

    print("2) Executing plan...")
    # Every step needs the raw reports, so we append them to each step's instruction.
    for s in steps:
        s.input = f"{s.input}\n\n--- Field reports ---\n{reports}"
    outputs = run_plan(llm, SITREP_AGENTS, steps)

    print("3) Review loop...")
    context = "\n\n".join(f"--- {sid} ---\n{out}" for sid, out in outputs.items())
    final, rounds = review_loop(
        llm, SITREP_AGENTS["Writer"], SITREP_AGENTS["Reviewer"],
        "Write the final SitRep using this material:\n\n" + context, max_rounds=3,
    )
    print(f"   finished after {rounds} review round(s)\n")
    print(final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
