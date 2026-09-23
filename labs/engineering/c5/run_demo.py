"""Run the SitRep tool loop against a real model.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    python run_demo.py
    python run_demo.py "How many people are in the Kessan school shelter now?"

The model may use the read-only tools. send_sitrep_email is registered (as it might be on a
real MCP server) but blocked by the allow-list guardrail: watch what happens if it tries.
"""
from __future__ import annotations

import os
import sys

from harness import ToolRegistry, allow_list, run_tool_loop, with_retry
from llm import litellm_llm
from sitrep_tools import ALL_TOOLS, OUTBOX, READ_ONLY_TOOLS

DEFAULT_REQUEST = (
    "Draft today's SitRep for the flooding in Kessan district, Northern Veloria. Use the field "
    "reports, put the affected numbers in context of the district population, flag conflicting "
    "figures, format it with format_sitrep, and email it to partners@veloria-relief.example."
)


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    request = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REQUEST
    llm = with_retry(litellm_llm(os.environ["MODEL"], temperature=0))
    guard = allow_list([t.name for t in READ_ONLY_TOOLS])

    result = run_tool_loop(llm, ToolRegistry(ALL_TOOLS), [{"role": "user", "content": request}],
                           max_steps=10, guardrails=[guard])

    for rec in result.tool_calls:
        flag = "ok " if rec.ok else "ERR"
        print(f"[step {rec.step}] {flag} {rec.tool}({rec.arguments}) -> {rec.result[:90]}")
    print(f"\nStatus: {result.status} after {result.steps} model call(s). Emails sent: {len(OUTBOX)}\n")
    print(result.answer or "(no final answer: the step budget ran out)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
