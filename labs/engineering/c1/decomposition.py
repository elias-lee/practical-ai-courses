"""Exercise: decompose the SitRep process and decide who does each step: AI, code or a human.

1. Fill in ``owner`` (and ``checked_by`` for AI steps) in ``MY_DECOMPOSITION`` below.
2. Run ``python decomposition.py`` and fix every problem it reports.
3. Compare with ``REFERENCE_DECOMPOSITION`` at the bottom, and argue with it: the rules
   below are the minimum, not the only defensible answer.

The rules encode computational thinking for AI systems:
- Every step has exactly one owner.
- Arithmetic, counting, lookups, file handling and format checks belong to code: they are
  deterministic, cheap and testable.
- Every AI step is checked by a *later* step owned by code or a human.
- Nothing is published until a human has approved it.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import List

OWNERS = ("AI", "code", "human")

# What kind of work a step is. This is the "pattern recognition" part of the exercise.
KINDS = {
    "io":         "moving data in or out (read mailbox, save file, send email)",
    "language":   "reading or writing natural language (extract, summarise, translate, draft)",
    "judgement":  "a decision that needs context or discretion",
    "arithmetic": "adding, counting, comparing numbers",
    "verify":     "checking another step's output against rules or sources",
    "approval":   "accepting accountability for a decision",
    "publish":    "releasing something outside the team",
}


@dataclass(frozen=True)
class Task:
    id: str
    description: str
    kind: str
    owner: str = "?"       # "AI", "code" or "human"; "?" while you are still deciding
    checked_by: str = ""   # for AI steps: the id of a later code/human step that checks it


def validate_decomposition(tasks: List[Task]) -> List[str]:
    """Return a list of problems. An empty list means the decomposition passes the rules."""
    problems: List[str] = []
    position = {t.id: i for i, t in enumerate(tasks)}
    if len(position) != len(tasks):
        problems.append("task ids must be unique")

    human_approval_seen = False
    for i, t in enumerate(tasks):
        if t.kind not in KINDS:
            problems.append(f"{t.id}: unknown kind {t.kind!r}")
        if t.owner not in OWNERS:
            problems.append(f"{t.id}: owner must be one of {OWNERS}, not {t.owner!r}")
            continue
        if t.kind == "arithmetic" and t.owner != "code":
            problems.append(f"{t.id}: arithmetic belongs to code (deterministic and testable)")
        if t.kind == "approval" and t.owner != "human":
            problems.append(f"{t.id}: approval means accountability, which only a human can hold")
        if t.owner == "AI":
            checker = t.checked_by
            if checker not in position:
                problems.append(f"{t.id}: AI step needs checked_by naming a later step")
            elif position[checker] <= i:
                problems.append(f"{t.id}: checker {checker!r} must come after the AI step")
            elif tasks[position[checker]].owner not in ("code", "human"):
                problems.append(f"{t.id}: checker {checker!r} must be owned by code or a human")
        if t.kind == "approval" and t.owner == "human":
            human_approval_seen = True
        if t.kind == "publish" and not human_approval_seen:
            problems.append(f"{t.id}: nothing is published before a human approval step")
    return problems


# ---------------------------------------------------------------------------
# YOUR TURN: set every owner ("AI", "code" or "human") and checked_by for AI steps.
# You may add, split or reorder steps; keep the ids unique.
# ---------------------------------------------------------------------------
MY_DECOMPOSITION: List[Task] = [
    Task("collect", "Collect today's field reports from the mailbox and shared folder", "io"),
    Task("translate", "Make English working copies of reports in French or Arabic", "language"),
    Task("extract", "Extract facts (what, where, when, figure as written, source) into a "
                    "fixed schema", "language"),
    Task("validate", "Check each fact against the schema; check each figure appears "
                     "verbatim in its source report", "verify"),
    Task("same_incident", "Decide whether two reports describe the same incident", "judgement"),
    Task("totals", "Add up figures per district, keeping households and people separate",
         "arithmetic"),
    Task("conflicts", "Resolve conflicting figures (e.g. 1,200 vs 1,450 households)",
         "judgement"),
    Task("draft", "Draft the narrative sections to the SitRep template", "language"),
    Task("format_check", "Check headings, word limit, and that every figure in the draft "
                         "is in the totals table", "verify"),
    Task("approve", "Duty officer reads and approves the SitRep", "approval"),
    Task("publish", "Send the SitRep to the distribution list", "publish"),
]


# ---------------------------------------------------------------------------
# One reasonable answer. Look at it only after trying your own.
# ---------------------------------------------------------------------------
_OWNERS = {
    "collect": ("code", ""),
    "translate": ("AI", "conflicts"),       # a bilingual colleague spot-checks flagged figures
    "extract": ("AI", "validate"),
    "validate": ("code", ""),
    "same_incident": ("AI", "conflicts"),
    "totals": ("code", ""),
    "conflicts": ("human", ""),
    "draft": ("AI", "format_check"),
    "format_check": ("code", ""),
    "approve": ("human", ""),
    "publish": ("code", ""),
}
REFERENCE_DECOMPOSITION: List[Task] = [
    replace(t, owner=_OWNERS[t.id][0], checked_by=_OWNERS[t.id][1]) for t in MY_DECOMPOSITION
]


def main() -> None:
    problems = validate_decomposition(MY_DECOMPOSITION)
    for t in MY_DECOMPOSITION:
        print(f"{t.owner:>6}  {t.id:<14} {t.description}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
    else:
        print("\nPasses the rules. Now compare with REFERENCE_DECOMPOSITION and discuss.")


if __name__ == "__main__":
    main()
