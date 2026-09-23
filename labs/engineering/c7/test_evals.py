"""Tests for the eval harness and tracer. No API key needed: FakeLLM stands in for the model."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, List

import pytest

from evals import (Case, CheckResult, DatasetError, JudgeParseError, Report, cohens_kappa, compare,
                   check_no_invented_numbers, judge_check, llm_judge, load_dataset,
                   parse_judge_output, run_eval)
from sitrep_system import PROMPT_V2, make_system
from tracer import Tracer, traced_llm

HERE = Path(__file__).resolve().parent


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


GOOD_SITREP = """Situation overview: flooding in Tamsi since 11 March (R1).
Key figures: 1,200 households (R1) vs 1,450 households (R2) - conflicting figures.
Humanitarian needs: clean water. Response to date: mobile clinic requested.
Gaps and constraints: east side unreachable."""

CASE = Case("t1", "[R1] 1,200 households, 11 March. [R2] 1,450 households.",
            {"headings": True, "max_words": 400, "must_include": ["1,200", "1,450"], "conflict": True},
            ["core", "conflict"])


# --- dataset --------------------------------------------------------------------------

def test_golden_dataset_is_well_formed():
    cases = load_dataset(HERE / "sitrep_golden.jsonl")
    assert len(cases) >= 20
    tags = [t for c in cases for t in c.tags]
    assert tags.count("adversarial") >= 4          # adversarial cases are part of the set
    assert "out_of_scope" in tags and "multilingual" in tags
    assert all(c.expected for c in cases)          # every case says what "good" means


def test_loader_points_at_the_bad_line(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"id": "a", "input": "x"}\n{"id": "a", "input": "y"}\n', encoding="utf-8")
    with pytest.raises(DatasetError, match=r":2: duplicate"):
        load_dataset(path)


# --- rule-based checks ------------------------------------------------------------------

def test_rule_checks_on_a_good_output():
    report = run_eval(lambda text: GOOD_SITREP, [CASE])
    assert report.pass_rate == 1.0, report.summary()


def test_invented_number_is_caught():
    result = check_no_invented_numbers(CASE, GOOD_SITREP + " About 5,000 people are affected.")
    assert result == CheckResult("no_invented_numbers", False, "not in source: ['5000']")


# --- LLM judge ----------------------------------------------------------------------------

def test_judge_parses_clean_and_fenced_json():
    assert parse_judge_output('{"reasons": "All figures sourced.", "score": 5}').passed is True
    fenced = 'Here is my grade:\n```json\n{"reasons": "Conflict not flagged.", "score": 3}\n```'
    verdict = parse_judge_output(fenced, threshold=4)
    assert verdict.score == 3 and verdict.passed is False
    assert "Conflict" in verdict.reasons


@pytest.mark.parametrize("bad", [
    "Score: 4/5, looks good",                      # prose, no JSON
    '{"reasons": "fine", "score": 7}',              # out of range
    '{"reasons": "fine", "score": "4"}',            # string, not integer
    '{"reasons": "fine", "score": true}',           # bool is not a score
    '{"reasons": "fine", "score": 4',               # truncated JSON
])
def test_judge_rejects_malformed_verdicts(bad):
    with pytest.raises(JudgeParseError):
        parse_judge_output(bad)


def test_judge_prompt_contains_rubric_source_and_output():
    llm = FakeLLM(['{"reasons": "ok", "score": 4}'])
    llm_judge(llm, source="SOURCE-TEXT", output="SITREP-TEXT", rubric="RUBRIC-TEXT")
    prompt = llm.calls[0][0]["content"]
    assert "SOURCE-TEXT" in prompt and "SITREP-TEXT" in prompt and "RUBRIC-TEXT" in prompt


def test_unparseable_judge_is_a_failed_check_not_a_pass():
    check = judge_check(FakeLLM(["I'd say it's pretty good!"]))
    result = check(CASE, GOOD_SITREP)
    assert result.passed is False and "judge error" in result.detail


def test_cohens_kappa():
    human = [True, True, False, False, True, False]
    assert cohens_kappa(human, human) == 1.0
    # A judge that says "pass" to everything agrees 50% of the time here, but kappa is 0.
    assert cohens_kappa([True] * 6, human) == pytest.approx(0.0)


# --- report aggregation --------------------------------------------------------------------

def _dataset() -> List[Case]:
    return [
        Case("a", "[R1] 60 families", {"must_include": ["60 families"]}, ["core"]),
        Case("b", "[R1] 400 people", {"must_include": ["400 people"], "max_words": 5}, ["core", "edge"]),
        Case("c", "Write a poem", {"out_of_scope": True}, ["out_of_scope"]),
    ]


def test_report_aggregates_per_check_and_per_tag():
    outputs = {"[R1] 60 families": "60 families in Bara.",
               "[R1] 400 people": "About 400 people are in the Kessan school shelter today.",
               "Write a poem": "OUT_OF_SCOPE"}
    report = run_eval(lambda text: outputs[text], _dataset(), label="v1")

    rates = report.check_pass_rates()
    assert rates["must_include"] == (2, 2, 1.0)
    assert rates["max_words"] == (0, 1, 0.0)        # only case b has a word limit
    assert rates["out_of_scope"] == (1, 1, 1.0)     # checks that don't apply aren't counted
    assert [r.case_id for r in report.failures()] == ["b"]
    assert report.pass_rate == pytest.approx(2 / 3)
    assert report.tag_pass_rates() == {"core": 0.5, "edge": 0.0, "out_of_scope": 1.0}
    assert "FAIL b: max_words" in report.summary()


def test_a_crash_is_a_failed_case():
    def system(text: str) -> str:
        raise TimeoutError("model timed out")

    report = run_eval(system, _dataset()[:1])
    assert report.pass_rate == 0.0
    assert report.results[0].error == "TimeoutError: model timed out"


def test_report_json_roundtrip(tmp_path):
    report = run_eval(lambda text: "60 families", _dataset()[:1], label="v1")
    path = tmp_path / "v1.json"
    report.save_json(path)
    again = Report.from_dict(json.loads(path.read_text(encoding="utf-8")))
    assert again.pass_rate == report.pass_rate and again.label == "v1"


# --- regression detection ---------------------------------------------------------------

def test_regression_is_detected_even_when_the_overall_score_improves():
    data = _dataset()
    v1 = run_eval(lambda t: {"[R1] 60 families": "60 families", "[R1] 400 people": "long " * 10,
                             "Write a poem": "a poem"}[t], data, label="v1")
    v2 = run_eval(lambda t: {"[R1] 60 families": "sixty households", "[R1] 400 people": "400 people",
                             "Write a poem": "OUT_OF_SCOPE"}[t], data, label="v2")
    assert v2.pass_rate > v1.pass_rate               # looks like progress...
    cmp = compare(v1, v2)
    assert cmp.newly_failing == ["a"]                # ...but case a broke
    assert sorted(cmp.newly_passing) == ["b", "c"]
    assert cmp.is_regression
    assert cmp.check_deltas["must_include"] == pytest.approx(0.0)
    assert "REGRESSION" in cmp.summary()


def test_no_regression_when_nothing_breaks():
    data = _dataset()
    run = run_eval(lambda t: "OUT_OF_SCOPE", data)
    assert compare(run, run).is_regression is False


# --- tracing ------------------------------------------------------------------------------

def fake_clock(step: float = 0.01):
    counter = itertools.count()
    return lambda: next(counter) * step


def test_spans_nest_and_record_duration_tokens_and_cost():
    tracer = Tracer(clock=fake_clock())
    with tracer.span("sitrep_run", case_id="g01") as root:
        with tracer.span("llm.call", model="small") as a:
            a.record_usage(input_tokens=800, output_tokens=200, cost_usd=0.0003)
        with tracer.span("llm.call", model="small") as b:
            b.record_usage(input_tokens=900, output_tokens=150, cost_usd=0.0002)

    assert [s.name for s in tracer.children(root)] == ["llm.call", "llm.call"]
    assert a.parent_id == root.span_id and b.parent_id == root.span_id
    assert root.parent_id is None
    assert root.duration_ms > a.duration_ms > 0
    assert tracer.totals() == {"input_tokens": 1700, "output_tokens": 350, "cost_usd": 0.0005,
                               "llm_calls": 2, "errors": 0}
    exported = json.loads(tracer.to_json())
    assert len(exported["spans"]) == 3 and exported["spans"][0]["attributes"] == {"case_id": "g01"}
    assert tracer.tree().splitlines()[1].startswith("  llm.call")


def test_a_failing_span_is_recorded_and_the_error_propagates():
    tracer = Tracer(clock=fake_clock())
    with pytest.raises(TimeoutError):
        with tracer.span("sitrep_run"):
            with tracer.span("llm.call"):
                raise TimeoutError("provider timed out")
    assert [s.status for s in tracer.spans] == ["error", "error"]
    assert tracer.totals()["errors"] == 2
    assert all(s.end is not None for s in tracer.spans)


def test_traced_system_produces_a_trace_per_case():
    tracer = Tracer(clock=fake_clock())
    llm = traced_llm(FakeLLM(["OUT_OF_SCOPE"]), tracer, model="fake")
    system = make_system(llm, PROMPT_V2, tracer=tracer)
    report = run_eval(system, _dataset()[2:])
    assert report.pass_rate == 1.0
    assert [s.name for s in tracer.spans] == ["sitrep.system", "llm.call"]
    assert tracer.spans[1].input_tokens > 0 and tracer.spans[1].cost_usd > 0
