"""Tests for the tool harness. No API key needed: a scripted FakeLLM stands in for the model."""
from __future__ import annotations

import json
from typing import Dict, List

import pytest

import sitrep_tools
from harness import (LoopResult, ToolArgumentError, ToolRegistry, allow_list, redact_pii,
                     run_tool_loop, tool, with_fallback, with_retry)
from sitrep_tools import ALL_TOOLS, READ_ONLY_TOOLS, format_sitrep, get_population, search_reports


class FakeLLM:
    """Returns queued responses in order and records every message list it receives."""

    def __init__(self, responses: List[str]):
        self.responses = list(responses)
        self.calls: List[List[Dict[str, str]]] = []

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        self.calls.append([dict(m) for m in messages])
        if not self.responses:
            raise AssertionError("FakeLLM ran out of scripted responses")
        return self.responses.pop(0)


def call(name: str, **arguments) -> str:
    return json.dumps({"tool": name, "arguments": arguments})


def final(text: str) -> str:
    return json.dumps({"final": text})


def last_observation(llm: FakeLLM, call_index: int) -> dict:
    """The tool result the harness sent to the model just before call number `call_index`."""
    return json.loads(llm.calls[call_index][-1]["content"])


ASK = [{"role": "user", "content": "What is the population of Kessan district?"}]


@pytest.fixture(autouse=True)
def empty_outbox():
    sitrep_tools.OUTBOX.clear()
    yield
    sitrep_tools.OUTBOX.clear()


# --- schema generation -----------------------------------------------------------------

def test_schema_is_generated_from_signature_and_docstring():
    schema = search_reports.schema
    assert schema["name"] == "search_reports"
    assert schema["description"].startswith("Search this week's field reports")
    params = schema["parameters"]
    assert params["required"] == ["query"]
    assert params["additionalProperties"] is False
    assert params["properties"]["query"]["type"] == "string"
    assert params["properties"]["limit"] == {"type": "integer", "description": "Results per page, 1-5.",
                                             "default": 3}
    assert params["properties"]["district"]["type"] == "string"  # Optional[str] -> string


def test_list_arguments_become_arrays():
    items = format_sitrep.schema["parameters"]["properties"]["key_figures"]
    assert items["type"] == "array" and items["items"] == {"type": "string"}


def test_tool_without_docstring_is_rejected():
    with pytest.raises(ValueError, match="docstring"):
        @tool
        def mystery(x: int) -> int:
            return x


def test_registry_validates_arguments_with_actionable_messages():
    reg = ToolRegistry(READ_ONLY_TOOLS)
    with pytest.raises(ToolArgumentError, match="missing required"):
        reg.call("get_population", {})
    with pytest.raises(ToolArgumentError, match="must be of type integer"):
        reg.call("search_reports", {"query": "shelter", "limit": "3"})
    with pytest.raises(ToolArgumentError, match="Available tools"):
        reg.call("delete_reports", {})


# --- the loop ---------------------------------------------------------------------------

def test_tool_call_roundtrip():
    llm = FakeLLM([call("get_population", district="Kessan"),
                   final("Kessan has about 84,300 people (2025 projection).")])
    result = run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK)

    assert isinstance(result, LoopResult)
    assert result.status == "final"
    assert result.answer.startswith("Kessan has about 84,300")
    assert result.steps == 2
    # The system prompt carries the protocol and the tool schemas.
    assert "get_population" in llm.calls[0][0]["content"]
    # The tool result was fed back before the second model call.
    obs = last_observation(llm, 1)
    assert obs["tool"] == "get_population" and obs["ok"] is True
    assert "84300" in obs["result"]
    assert [r.tool for r in result.tool_calls] == ["get_population"]


def test_tool_error_is_fed_back_and_model_recovers():
    llm = FakeLLM([call("get_population", district="Tamsi"),
                   call("get_population", district="Kessan"),
                   final("Tamsi is in Kessan district, population about 84,300.")])
    result = run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK)

    assert result.status == "final"
    err = last_observation(llm, 1)
    assert err["ok"] is False
    # The error names the known districts and the village's district: something to act on.
    assert "Known districts" in err["result"] and "Kessan" in err["result"]
    assert [r.ok for r in result.tool_calls] == [False, True]


def test_bad_arguments_and_malformed_replies_do_not_crash_the_loop():
    llm = FakeLLM(["Sure! Let me look that up.",                      # not JSON
                   call("search_reports", query="shelter", limit=50),  # out of range
                   final("done")])
    result = run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK)
    assert result.status == "final"
    assert "Could not parse" in last_observation(llm, 1)["error"]
    assert "limit must be between 1 and 5" in last_observation(llm, 2)["result"]


def test_step_budget_is_enforced():
    llm = FakeLLM([call("search_reports", query="water")] * 10)
    result = run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK, max_steps=3)
    assert result.status == "budget_exceeded"
    assert result.answer is None
    assert len(llm.calls) == 3          # exactly the budget, not one call more


def test_disallowed_tool_is_blocked_and_never_runs():
    llm = FakeLLM([call("send_sitrep_email", to="all@partners.example", subject="SitRep", body="..."),
                   final("I cannot send email; here is the draft instead.")])
    guard = allow_list([t.name for t in READ_ONLY_TOOLS])
    result = run_tool_loop(llm, ToolRegistry(ALL_TOOLS), ASK, guardrails=[guard])

    assert result.status == "final"
    assert sitrep_tools.OUTBOX == []                 # the side effect never happened
    obs = last_observation(llm, 1)
    assert obs["ok"] is False and "BLOCKED" in obs["result"]


def test_pii_is_redacted_from_tool_results():
    llm = FakeLLM([call("search_reports", query="mobile clinic"), final("ok")])
    run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK)
    seen = last_observation(llm, 1)["result"]
    assert "k.ondela@kessan-health.example" not in seen
    assert "+000 555 0147" not in seen
    assert "[EMAIL REDACTED]" in seen
    assert "2026-03-15" in seen                      # dates are not mistaken for phone numbers


def test_long_results_are_truncated_with_a_hint():
    llm = FakeLLM([call("search_reports", query="kessan", limit=5), final("ok")])
    run_tool_loop(llm, ToolRegistry(READ_ONLY_TOOLS), ASK, max_result_chars=200)
    assert "truncated" in last_observation(llm, 1)["result"]


# --- the tools themselves -----------------------------------------------------------------

def test_search_reports_pages_results():
    first = search_reports(query="kessan", limit=2)
    assert first["total"] >= 3 and len(first["results"]) == 2 and first["next_offset"] == 2
    rest = search_reports(query="kessan", limit=5, offset=first["next_offset"])
    ids = {r["id"] for r in first["results"]} | {r["id"] for r in rest["results"]}
    assert len(ids) == first["total"]
    assert rest["next_offset"] is None


def test_get_report_returns_full_text_or_a_useful_error():
    reg = ToolRegistry(READ_ONLY_TOOLS)
    assert "1,450 households" in reg.call("get_report", {"report_id": "r2"})["text"]
    with pytest.raises(Exception, match="get them from search_reports"):
        reg.call("get_report", {"report_id": "Report 9"})


def test_format_sitrep_requires_sourced_figures():
    reg = ToolRegistry(READ_ONLY_TOOLS)
    args = dict(title="T", overview="O", key_figures=["1,200 households affected"], needs=["water"],
                response="R", gaps="G")
    with pytest.raises(Exception, match="no source"):
        reg.call("format_sitrep", args)
    args["key_figures"] = ["1,200 households affected (R1)"]
    text = reg.call("format_sitrep", args)
    for heading in ["Situation overview", "Key figures", "Humanitarian needs", "Response to date",
                    "Gaps and constraints"]:
        assert f"## {heading}" in text


# --- guardrail and reliability helpers ----------------------------------------------------

def test_redact_pii_keeps_ordinary_numbers():
    assert redact_pii("1,450 households; call +41 22 555 0100") == "1,450 households; call [PHONE REDACTED]"


def test_retry_then_fallback():
    attempts = {"n": 0}

    def flaky(messages):
        attempts["n"] += 1
        raise TimeoutError("provider timed out")

    sleeps: List[float] = []
    primary = with_retry(flaky, attempts=3, sleep=sleeps.append)
    llm = with_fallback(primary, lambda messages: "fallback answer")
    assert llm([{"role": "user", "content": "hi"}]) == "fallback answer"
    assert attempts["n"] == 3
    assert sleeps == [0.5, 1.0]          # exponential backoff between attempts
