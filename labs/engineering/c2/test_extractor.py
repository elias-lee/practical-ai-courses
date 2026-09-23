"""Tests for the SitRep extractor. No API key and no Pydantic: a scripted FakeLLM stands in for
the model, and validation is plain Python."""
from __future__ import annotations

import json
from dataclasses import fields
from typing import Dict, List

import pytest

from extractor import ExtractionError, extract_sitrep, parse_json, strip_fences
from sitrep_prompts import PROMPT_VERSION, build_messages
from sitrep_schema import (NOT_STATED, SITREP_JSON_SCHEMA, Figure, SitRep, ValidationError,
                           parse_sitrep)


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


REPORT = "heavy rain since the weekend in Aramu district. approx 1,200 households displaced."

VALID = {
    "district": "Aramu",
    "report_date": NOT_STATED,
    "hazard": "flooding",
    "severity": "high",
    "affected": [{"location": "Aramu district", "value": "approx 1,200",
                  "unit": "households", "source": "approx 1,200 households displaced"}],
    "priority_needs": ["clean water"],
    "response": [NOT_STATED],
    "gaps": ["Dorra not reached"],
}


def valid_json(**changes) -> str:
    return json.dumps({**VALID, **changes})


# --- the happy path -------------------------------------------------------

def test_valid_output_returns_a_sitrep_in_one_call():
    llm = FakeLLM([valid_json()])
    sitrep = extract_sitrep(llm, REPORT)
    assert isinstance(sitrep, SitRep)
    assert sitrep.district == "Aramu"
    assert sitrep.affected == [Figure("Aramu district", "approx 1,200", "households",
                                      "approx 1,200 households displaced")]
    assert len(llm.calls) == 1


def test_not_stated_is_a_valid_answer():
    sitrep = extract_sitrep(FakeLLM([valid_json()]), REPORT)
    assert sitrep.report_date == NOT_STATED
    assert sitrep.response == [NOT_STATED]


def test_json_fence_is_stripped():
    llm = FakeLLM(["Here is the data:\n```json\n" + valid_json() + "\n```"])
    assert extract_sitrep(llm, REPORT).hazard == "flooding"


def test_strip_fences_leaves_plain_json_alone():
    assert strip_fences('  {"a": 1}\n') == '{"a": 1}'
    assert strip_fences('```\n{"a": 1}\n```') == '{"a": 1}'


# --- retry with error feedback --------------------------------------------

def test_malformed_then_fixed_retries_with_the_error():
    llm = FakeLLM(["Sure! The district is Aramu and about 1,200 households...", valid_json()])
    sitrep = extract_sitrep(llm, REPORT)
    assert sitrep.district == "Aramu"
    assert len(llm.calls) == 2
    retry = llm.calls[1]
    # The model sees its own bad reply, then the exact problem.
    assert retry[-2] == {"role": "assistant",
                         "content": "Sure! The district is Aramu and about 1,200 households..."}
    assert retry[-1]["role"] == "user"
    assert "not valid JSON" in retry[-1]["content"]


def test_schema_error_is_fed_back_verbatim():
    llm = FakeLLM([valid_json(severity="severe", report_date=None), valid_json()])
    extract_sitrep(llm, REPORT)
    feedback = llm.calls[1][-1]["content"]
    assert "severity: 'severe' must be one of" in feedback
    assert "report_date: must be a string, not null" in feedback
    assert f'write "{NOT_STATED}"' in feedback


def test_retries_exhausted_raises_with_evidence():
    llm = FakeLLM(["not json", "still not json", valid_json(unit_typo=True)])
    with pytest.raises(ExtractionError) as info:
        extract_sitrep(llm, REPORT, max_attempts=3)
    assert len(llm.calls) == 3
    assert info.value.attempts == 3
    assert info.value.replies[0] == "not json"
    assert info.value.errors == ["unit_typo: unexpected field"]


# --- validation (the schema) ----------------------------------------------

def test_validation_collects_every_error_with_its_path():
    bad = dict(VALID, report_date="14/03", affected=[{"location": "Tamsi", "value": "400",
                                                      "unit": "persons", "source": "~400 ppl"}])
    del bad["gaps"]
    with pytest.raises(ValidationError) as info:
        parse_sitrep(bad)
    errors = info.value.errors
    assert "gaps: field required" in errors
    assert any(e.startswith("report_date: '14/03' must be YYYY-MM-DD") for e in errors)
    assert any(e.startswith("affected[0].unit: 'persons'") for e in errors)
    assert len(errors) == 3


def test_top_level_must_be_an_object():
    with pytest.raises(ValidationError, match="JSON object"):
        parse_sitrep(parse_json("[1, 2, 3]"))


def test_iso_date_is_accepted():
    assert parse_sitrep(dict(VALID, report_date="2026-03-14")).report_date == "2026-03-14"


def test_json_schema_matches_the_dataclasses():
    assert SITREP_JSON_SCHEMA["required"] == [f.name for f in fields(SitRep)]
    figure_schema = SITREP_JSON_SCHEMA["properties"]["affected"]["items"]
    assert figure_schema["required"] == [f.name for f in fields(Figure)]


# --- prompt tests ---------------------------------------------------------

def test_prompt_separates_instructions_from_data():
    system, user = build_messages(REPORT)
    assert system["role"] == "system" and user["role"] == "user"
    assert REPORT not in system["content"]
    assert f"<report>\n{REPORT}\n</report>" in user["content"]


def test_prompt_states_the_rules_that_matter():
    system = build_messages(REPORT)[0]["content"]
    assert f'"{NOT_STATED}"' in system
    assert "Never use null" in system
    assert "Never convert units" in system
    assert '"priority_needs"' in system          # the schema is included
    assert PROMPT_VERSION.startswith("sitrep-extract/")
