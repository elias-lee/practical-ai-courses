"""Run the injection suite against the naive and the defended pipeline.

    python run_red_team_demo.py                    # worst-case gullible model, no key needed
    export MODEL="openai/gpt-4o-mini"
    python run_red_team_demo.py --real             # a real model (costs ~26 calls)

Use only the fictional suite. Never red-team a system you do not own or have permission to test.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from pipeline import defended_pipeline, naive_pipeline
from redteam import gullible_llm, load_suite, run_red_team

HERE = Path(__file__).resolve().parent


def main() -> int:
    llm = gullible_llm
    if "--real" in sys.argv:
        if "MODEL" not in os.environ:
            print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
            return 1
        from llm import litellm_llm

        llm = litellm_llm(os.environ["MODEL"], temperature=0)

    suite = load_suite(HERE / "injection_suite.jsonl")
    for name, pipe in (("naive", naive_pipeline), ("defended", defended_pipeline)):
        results = run_red_team(lambda report: pipe(llm, report), suite)
        print(f"== {name} pipeline ==")
        print(results.summary())
        for o in results.outcomes:
            mark = "LEAK" if o.attack_succeeded else ("FP" if o.false_positive else "ok")
            print(f"   {o.case_id:<4} {o.category:<20} {o.status:<8} {mark:<4} {o.detail}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
