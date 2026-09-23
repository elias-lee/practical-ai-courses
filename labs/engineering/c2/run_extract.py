"""Run the SitRep extractor against a real model.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    python run_extract.py                   # uses sample_report.md
    python run_extract.py my_report.md      # or your own (fictional!) report
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from extractor import ExtractionError, extract_sitrep
from llm import LLM, litellm_llm
from sitrep_prompts import PROMPT_VERSION

HERE = Path(__file__).resolve().parent


def traced(llm: LLM) -> LLM:
    """Print one line per call, so you can see retries happen."""
    counter = {"n": 0}

    def call(messages):
        counter["n"] += 1
        reply = llm(messages)
        print(f"  [attempt {counter['n']}] {len(messages)} messages in -> {len(reply)} chars out")
        return reply

    return call


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "sample_report.md"
    report = path.read_text(encoding="utf-8")
    llm = traced(litellm_llm(os.environ["MODEL"], temperature=0))

    print(f"Prompt {PROMPT_VERSION}, model {os.environ['MODEL']}")
    try:
        sitrep = extract_sitrep(llm, report)
    except ExtractionError as exc:
        print(f"FAILED: {exc}")
        return 2
    print(json.dumps(asdict(sitrep), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
