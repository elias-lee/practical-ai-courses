"""Run the golden dataset against a real model: baseline prompt vs improved prompt.

    export MODEL="openai/gpt-4o-mini"            # system under test
    export JUDGE_MODEL="openai/gpt-4o"           # optional: adds the LLM-judge check
    python run_eval_demo.py

Writes results/v1.json, results/v2.json and results/trace_v2.json, and prints both summaries
and the case-by-case comparison. Every run costs money: check the token totals it prints.
"""
from __future__ import annotations

import os
from pathlib import Path

from evals import DEFAULT_CHECKS, compare, judge_check, load_dataset, run_eval
from llm import litellm_llm
from sitrep_system import PROMPT_V1, PROMPT_V2, make_system
from tracer import Tracer, traced_llm

HERE = Path(__file__).resolve().parent


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    dataset = load_dataset(HERE / "sitrep_golden.jsonl")
    checks = list(DEFAULT_CHECKS)
    if "JUDGE_MODEL" in os.environ:
        checks.append(judge_check(litellm_llm(os.environ["JUDGE_MODEL"], temperature=0)))

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    reports = {}
    for label, prompt in (("v1", PROMPT_V1), ("v2", PROMPT_V2)):
        tracer = Tracer()
        llm = traced_llm(litellm_llm(os.environ["MODEL"], temperature=0), tracer, os.environ["MODEL"])
        with tracer.span("eval_run", label=label, cases=len(dataset)):
            reports[label] = run_eval(make_system(llm, prompt, tracer), dataset, checks, label=label)
        reports[label].save_json(out / f"{label}.json")
        tracer.export_json(out / f"trace_{label}.json")
        print(reports[label].summary())
        print(f"   usage: {tracer.totals()}\n")

    print(compare(reports["v1"], reports["v2"]).summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
