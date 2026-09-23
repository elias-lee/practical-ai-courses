"""Tests for the SitRep orchestrator. No API key needed: a scripted FakeLLM stands in
for the model, so every test is fast and deterministic."""
from __future__ import annotations

import json
from typing import Dict, List

import pytest

from agents import SITREP_AGENTS, Agent
from orchestrator import PlanError, Step, plan, review_loop, run_plan


class FakeLLM:
    """Returns queued responses in order and records every message list it receives."""

    def __init__(self, responses: List[str]):
        self.responses = list(responses)
        self.calls: List[List[Dict[str, str]]] = []

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("FakeLLM ran out of scripted responses")
        return self.responses.pop(0)


AGENT_NAMES = list(SITREP_AGENTS)


def plan_json(steps: List[dict]) -> str:
    return json.dumps({"steps": steps})


VALID_STEPS = [
    {"id": "facts", "agent": "Researcher", "input": "Extract facts", "depends_on": []},
    {"id": "trends", "agent": "Analyst", "input": "Find trends", "depends_on": ["facts"]},
    {"id": "draft", "agent": "Writer", "input": "Draft the SitRep", "depends_on": ["facts", "trends"]},
]


# --- plan() ---------------------------------------------------------------

def test_valid_plan_is_parsed_into_steps():
    llm = FakeLLM([plan_json(VALID_STEPS)])
    steps = plan(llm, "Write a SitRep for Northern Veloria", AGENT_NAMES)
    assert [s.id for s in steps] == ["facts", "trends", "draft"]
    assert steps[2] == Step(id="draft", agent="Writer", input="Draft the SitRep",
                            depends_on=["facts", "trends"])
    # The orchestrator prompt goes in as a system message and names the agents.
    system = llm.calls[0][0]
    assert system["role"] == "system"
    assert "Researcher" in system["content"]


def test_fenced_json_is_parsed():
    llm = FakeLLM(["Here is the plan:\n```json\n" + plan_json(VALID_STEPS) + "\n```"])
    steps = plan(llm, "Write a SitRep", AGENT_NAMES)
    assert len(steps) == 3


def test_out_of_scope_returns_empty_plan():
    llm = FakeLLM([json.dumps({"status": "out_of_scope"})])
    assert plan(llm, "Book me a flight to Geneva", AGENT_NAMES) == []


def test_unknown_agent_raises():
    bad = [{"id": "a", "agent": "Translator", "input": "x", "depends_on": []}]
    with pytest.raises(PlanError, match="Translator"):
        plan(FakeLLM([plan_json(bad)]), "req", AGENT_NAMES)


def test_cycle_raises():
    cyclic = [
        {"id": "a", "agent": "Researcher", "input": "x", "depends_on": ["b"]},
        {"id": "b", "agent": "Analyst", "input": "y", "depends_on": ["a"]},
    ]
    with pytest.raises(PlanError, match="cycle"):
        plan(FakeLLM([plan_json(cyclic)]), "req", AGENT_NAMES)


def test_too_many_steps_raises():
    many = [{"id": f"s{i}", "agent": "Researcher", "input": "x", "depends_on": []}
            for i in range(9)]
    with pytest.raises(PlanError, match="steps"):
        plan(FakeLLM([plan_json(many)]), "req", AGENT_NAMES, max_steps=8)


def test_unknown_dependency_raises():
    bad = [{"id": "a", "agent": "Researcher", "input": "x", "depends_on": ["ghost"]}]
    with pytest.raises(PlanError, match="ghost"):
        plan(FakeLLM([plan_json(bad)]), "req", AGENT_NAMES)


def test_duplicate_ids_raise():
    dup = [
        {"id": "a", "agent": "Researcher", "input": "x", "depends_on": []},
        {"id": "a", "agent": "Analyst", "input": "y", "depends_on": []},
    ]
    with pytest.raises(PlanError, match="duplicate"):
        plan(FakeLLM([plan_json(dup)]), "req", AGENT_NAMES)


def test_invalid_json_raises():
    with pytest.raises(PlanError):
        plan(FakeLLM(["I think we should start with research."]), "req", AGENT_NAMES)


# --- run_plan() -----------------------------------------------------------

def test_run_plan_executes_in_dependency_order_and_passes_outputs():
    # Listed out of order on purpose: run_plan must sort topologically.
    steps = [
        Step(id="draft", agent="Writer", input="Draft the SitRep", depends_on=["facts", "trends"]),
        Step(id="trends", agent="Analyst", input="Find trends", depends_on=["facts"]),
        Step(id="facts", agent="Researcher", input="Extract facts", depends_on=[]),
    ]
    llm = FakeLLM(["FACTS-OUT", "TRENDS-OUT", "DRAFT-OUT"])
    outputs = run_plan(llm, SITREP_AGENTS, steps)

    assert outputs == {"facts": "FACTS-OUT", "trends": "TRENDS-OUT", "draft": "DRAFT-OUT"}
    systems = [call[0]["content"] for call in llm.calls]
    assert systems == [SITREP_AGENTS[n].system_prompt for n in ("Researcher", "Analyst", "Writer")]

    trends_task = llm.calls[1][-1]["content"]
    draft_task = llm.calls[2][-1]["content"]
    assert "Find trends" in trends_task and "FACTS-OUT" in trends_task
    assert "FACTS-OUT" in draft_task and "TRENDS-OUT" in draft_task
    # Independent steps do not see outputs they did not ask for.
    assert "TRENDS-OUT" not in llm.calls[0][-1]["content"]


# --- review_loop() --------------------------------------------------------

WRITER = SITREP_AGENTS["Writer"]
REVIEWER = SITREP_AGENTS["Reviewer"]


def test_review_loop_stops_early_on_approved():
    llm = FakeLLM(["draft v1", "1. Add the date of the flooding.", "draft v2", "APPROVED"])
    final, rounds = review_loop(llm, WRITER, REVIEWER, "Write the SitRep", max_rounds=3)
    assert final == "draft v2"
    assert rounds == 2
    assert len(llm.calls) == 4
    # The reviewer's fixes are fed back to the writer.
    assert "Add the date of the flooding" in llm.calls[2][-1]["content"]


def test_review_loop_stops_at_budget():
    llm = FakeLLM(["d1", "1. fix", "d2", "1. fix", "d3", "1. still wrong"])
    final, rounds = review_loop(llm, WRITER, REVIEWER, "Write the SitRep", max_rounds=3)
    assert final == "d3"
    assert rounds == 3
    assert len(llm.calls) == 6


def test_agent_run_sends_system_and_user_messages():
    llm = FakeLLM(["ok"])
    agent = Agent(name="Echo", system_prompt="You echo.")
    assert agent.run(llm, "hello") == "ok"
    assert llm.calls[0] == [
        {"role": "system", "content": "You echo."},
        {"role": "user", "content": "hello"},
    ]


def test_sitrep_agents_roster():
    assert set(SITREP_AGENTS) == {"Researcher", "Analyst", "Writer", "Reviewer"}
    assert "APPROVED" in SITREP_AGENTS["Reviewer"].system_prompt
