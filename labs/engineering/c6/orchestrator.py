"""A framework-free orchestrator: plan -> validate -> execute in dependency order -> review.

Three responsibilities of an orchestration layer are visible here in plain Python:
1. Planning:   the model proposes a plan; *code* validates it before anything runs.
2. Execution:  steps run in topological order; each gets only its dependencies' outputs.
3. Stopping:   hard budgets (max_steps, max_rounds) that do not depend on the model.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence, Tuple

from agents import Agent
from llm import LLM


class PlanError(Exception):
    """The model's plan is malformed or unsafe to execute."""


@dataclass
class Step:
    id: str
    agent: str
    input: str
    depends_on: List[str] = field(default_factory=list)


ORCHESTRATOR_PROMPT = """You are the orchestrator of a situation-report (SitRep) team.
Break the user's request into steps, each assigned to exactly one agent.

Available agents:
{agents}

Rules:
- Use at most {max_steps} steps. Fewer is better.
- Each step has a short unique "id", an "agent" (one of the names above), an "input"
  (a precise instruction for that agent), and "depends_on" (ids of earlier steps whose
  output this step needs; [] if none).
- Do not create circular dependencies.
- If the request is not about producing or improving a situation report from field
  information, reply with {{"status": "out_of_scope"}} and nothing else.

Reply with JSON only, in this shape:
{{"steps": [{{"id": "facts", "agent": "Researcher", "input": "...", "depends_on": []}}]}}"""

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(text: str) -> dict:
    """Parse JSON from a model reply, tolerating ```json fences and surrounding prose."""
    match = _FENCE.search(text)
    candidate = match.group(1) if match else text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start:end + 1])
            except json.JSONDecodeError:
                pass
    raise PlanError(f"plan is not valid JSON: {text[:200]!r}")


def _topological_order(steps: Sequence[Step]) -> List[Step]:
    """Kahn's algorithm. Keeps the listed order among ready steps; raises on a cycle."""
    by_id = {s.id: s for s in steps}
    remaining = {s.id: set(s.depends_on) for s in steps}
    ordered: List[Step] = []
    while remaining:
        ready = [s.id for s in steps if s.id in remaining and not remaining[s.id]]
        if not ready:
            raise PlanError(f"plan contains a cycle among steps: {sorted(remaining)}")
        for sid in ready:
            ordered.append(by_id[sid])
            del remaining[sid]
        for deps in remaining.values():
            deps.difference_update(ready)
    return ordered


def validate_plan(steps: Sequence[Step], agent_names: Sequence[str], max_steps: int = 8) -> None:
    """Raise PlanError unless the plan is safe to execute."""
    if len(steps) > max_steps:
        raise PlanError(f"plan has {len(steps)} steps; the budget is {max_steps} steps")
    ids = [s.id for s in steps]
    if len(set(ids)) != len(ids):
        raise PlanError(f"plan has duplicate step ids: {ids}")
    for s in steps:
        if s.agent not in agent_names:
            raise PlanError(f"step {s.id!r} uses unknown agent {s.agent!r}")
        for dep in s.depends_on:
            if dep not in ids:
                raise PlanError(f"step {s.id!r} depends on unknown step {dep!r}")
    _topological_order(steps)  # raises on a cycle


def plan(llm: LLM, request: str, agent_names: Sequence[str], max_steps: int = 8) -> List[Step]:
    """Ask the model for a plan, then validate it in code. Out-of-scope requests -> []."""
    system = ORCHESTRATOR_PROMPT.format(
        agents="\n".join(f"- {name}" for name in agent_names), max_steps=max_steps
    )
    reply = llm([
        {"role": "system", "content": system},
        {"role": "user", "content": request},
    ])
    data = _extract_json(reply)
    if not isinstance(data, dict):
        raise PlanError("plan must be a JSON object")
    if data.get("status") == "out_of_scope":
        return []
    raw_steps = data.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise PlanError("plan must contain a non-empty 'steps' list")
    try:
        steps = [
            Step(id=str(r["id"]), agent=str(r["agent"]), input=str(r["input"]),
                 depends_on=[str(d) for d in r.get("depends_on", [])])
            for r in raw_steps
        ]
    except (KeyError, TypeError) as exc:
        raise PlanError(f"malformed step in plan: {exc}") from exc
    validate_plan(steps, agent_names, max_steps)
    return steps


def run_plan(llm: LLM, agents: Mapping[str, Agent], steps: Sequence[Step]) -> Dict[str, str]:
    """Execute steps in dependency order. Each step sees its input plus its dependencies' outputs."""
    outputs: Dict[str, str] = {}
    for step in _topological_order(steps):
        task = step.input
        for dep in step.depends_on:
            task += f"\n\n--- Output of step '{dep}' ---\n{outputs[dep]}"
        outputs[step.id] = agents[step.agent].run(llm, task)
    return outputs


def _approved(review: str) -> bool:
    return review.strip().lstrip("*#> ").startswith("APPROVED")


def review_loop(llm: LLM, writer: Agent, reviewer: Agent, task: str,
                max_rounds: int = 3) -> Tuple[str, int]:
    """Evaluator-optimizer: write, review, revise until APPROVED or the round budget runs out.

    Returns (final_draft, rounds_used). Hitting the budget returns the last draft; the
    caller decides whether an unapproved draft goes to a human.
    """
    draft = writer.run(llm, task)
    for round_no in range(1, max_rounds + 1):
        review = reviewer.run(llm, f"Task given to the writer:\n{task}\n\nDraft:\n{draft}")
        if _approved(review) or round_no == max_rounds:
            return draft, round_no
        draft = writer.run(
            llm,
            f"{task}\n\n--- Your previous draft ---\n{draft}\n\n"
            f"--- Reviewer feedback: fix every numbered point ---\n{review}",
        )
    return draft, 0  # only reached if max_rounds < 1: no review happened
