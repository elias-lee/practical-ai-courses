"""Tests for the smoke test. No API key needed: a scripted FakeLLM stands in for the model."""
from __future__ import annotations

from typing import Dict, List, Optional

from smoke_test import (SMOKE_MESSAGES, check_environment, format_result, main,
                        provider_of, rough_token_count, run_smoke_test)


class FakeLLM:
    """Returns queued responses in order and records every message list it receives."""

    def __init__(self, responses: List[str], usage: Optional[Dict[str, int]] = None):
        self.responses = list(responses)
        self.calls: List[List[Dict[str, str]]] = []
        self.last_usage = usage

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("FakeLLM ran out of scripted responses")
        return self.responses.pop(0)


def fake_clock(*times: float):
    """A clock that returns the given times in order, so latency is deterministic."""
    values = list(times)
    return lambda: values.pop(0)


def test_smoke_test_reports_reply_usage_and_latency():
    llm = FakeLLM(["SitRep Assistant online."],
                  usage={"prompt_tokens": 31, "completion_tokens": 5, "total_tokens": 36})
    result = run_smoke_test(llm, clock=fake_clock(10.0, 10.75))
    assert result.reply == "SitRep Assistant online."
    assert (result.prompt_tokens, result.completion_tokens, result.total_tokens) == (31, 5, 36)
    assert result.latency_s == 0.75
    assert result.usage_is_estimate is False
    # Exactly one call, with a system and a user message.
    assert llm.calls == [SMOKE_MESSAGES]


def test_usage_is_estimated_when_provider_reports_none():
    llm = FakeLLM(["SitRep Assistant online."])  # no last_usage
    result = run_smoke_test(llm, clock=fake_clock(0.0, 1.0))
    assert result.usage_is_estimate is True
    assert result.prompt_tokens > 0 and result.completion_tokens > 0


def test_format_result_mentions_every_number():
    llm = FakeLLM(["ok"], usage={"prompt_tokens": 20, "completion_tokens": 1})
    text = format_result("openai/gpt-4o-mini", run_smoke_test(llm, clock=fake_clock(0.0, 0.5)))
    assert "openai/gpt-4o-mini" in text
    assert "20 in + 1 out = 21" in text
    assert "0.50 s" in text


def test_rough_token_count():
    assert rough_token_count("") == 0
    assert rough_token_count("abcd" * 10) == 10


def test_provider_prefix():
    assert provider_of("azure/sitrep-gpt") == "azure"
    assert provider_of("anthropic/claude-sonnet-4-5") == "anthropic"
    assert provider_of("gpt-4o-mini") == ""


def test_check_environment_openai_ready():
    assert check_environment("openai/gpt-4o-mini", {"OPENAI_API_KEY": "sk-test"}) == []


def test_check_environment_lists_every_missing_azure_variable():
    problems = check_environment("azure/sitrep-gpt", {"AZURE_API_KEY": "x"})
    assert len(problems) == 2
    assert any("AZURE_API_BASE" in p for p in problems)
    assert any("AZURE_API_VERSION" in p for p in problems)


def test_check_environment_rejects_missing_or_unprefixed_model():
    assert "MODEL is not set" in check_environment("", {})[0]
    assert "provider prefix" in check_environment("gpt-4o-mini", {"OPENAI_API_KEY": "x"})[0]


def test_main_stops_before_calling_when_not_configured(capsys):
    assert main({}) == 1
    assert "Not ready yet" in capsys.readouterr().out
