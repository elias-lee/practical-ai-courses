"""Tests for the SitRep Summarizer: the executable version of SPEC.md.

No API key needed: a scripted FakeLLM stands in for the model, and a fake ``sleep``
records the backoff delays instead of waiting, so every test runs in milliseconds.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

import pytest

from app import (
    MAX_INPUT_CHARS,
    SYSTEM_PROMPT,
    BudgetExceeded,
    CostTracker,
    RetryError,
    TransientError,
    call_with_retry,
    estimate_tokens,
    main,
    summarize,
    tracked,
)
from llm import is_transient

HERE = Path(__file__).resolve().parent
MESSAGES = [{"role": "user", "content": "hello"}]


class FakeLLM:
    """Returns (or raises) scripted responses in order and records every call.

    A response that is an Exception instance is raised instead of returned, which is how
    we simulate rate limits and outages.
    """

    def __init__(self, responses: List[Union[str, Exception]]):
        self.responses = list(responses)
        self.calls: List[List[Dict[str, str]]] = []

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("FakeLLM ran out of scripted responses")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class RecordingSleep:
    def __init__(self):
        self.delays: List[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


# --- R3 / R4: retries -------------------------------------------------------------

def test_retry_succeeds_after_transient_errors():
    llm = FakeLLM([TransientError("429 rate limit"), TransientError("503"), "ok"])
    sleep = RecordingSleep()
    assert call_with_retry(llm, MESSAGES, retries=3, backoff=1.0, jitter=0, sleep=sleep) == "ok"
    assert len(llm.calls) == 3
    assert sleep.delays == [1.0, 2.0]


def test_gives_up_after_n_retries():
    llm = FakeLLM([TransientError(f"503 #{i}") for i in range(4)])
    sleep = RecordingSleep()
    with pytest.raises(RetryError, match="4 attempts") as info:
        call_with_retry(llm, MESSAGES, retries=3, backoff=0.5, jitter=0, sleep=sleep)
    assert len(llm.calls) == 4                      # 1 attempt + 3 retries, then stop
    assert sleep.delays == [0.5, 1.0, 2.0]          # no sleep after the final failure
    assert isinstance(info.value.__cause__, TransientError)   # last error is chained


def test_backoff_is_exponential_and_capped():
    llm = FakeLLM([TransientError("timeout")] * 6 + ["ok"])
    sleep = RecordingSleep()
    call_with_retry(llm, MESSAGES, retries=6, backoff=1.0, max_backoff=10.0,
                    jitter=0.1, sleep=sleep, rand=lambda: 1.0)
    # 1, 2, 4, 8, then capped at 10 - each plus the maximum 10% jitter.
    assert sleep.delays == pytest.approx([1.1, 2.2, 4.4, 8.8, 11.0, 11.0])


def test_non_transient_error_is_not_retried():
    llm = FakeLLM([ValueError("400 bad request: messages must not be empty")])
    sleep = RecordingSleep()
    with pytest.raises(ValueError):
        call_with_retry(llm, MESSAGES, retries=3, sleep=sleep)
    assert len(llm.calls) == 1
    assert sleep.delays == []


class RateLimitError(Exception):
    """Same class name as LiteLLM's, to check detection by name."""


class HTTPError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


def test_provider_style_errors_are_recognised():
    assert is_transient(RateLimitError("slow down"))
    assert is_transient(HTTPError(503))
    assert is_transient(HTTPError(408))             # request timeout
    assert not is_transient(HTTPError(401))         # bad key: retrying won't help
    assert not is_transient(HTTPError(400))
    assert not is_transient(KeyError("x"))


# --- R6 / R7: cost ------------------------------------------------------------------

def test_cost_accumulates_across_calls():
    tracker = CostTracker(price_in_per_mtok=1.0, price_out_per_mtok=4.0)
    tracker.record(1_000, 200)
    tracker.record(3_000, 300)
    assert tracker.calls == 2
    assert tracker.input_tokens == 4_000
    assert tracker.output_tokens == 500
    # (4,000 x 1.0 + 500 x 4.0) / 1,000,000 = 0.006
    assert tracker.cost_usd == pytest.approx(0.006)
    assert "calls=2" in tracker.summary()


def test_tracked_llm_estimates_tokens():
    tracker = CostTracker()
    llm = tracked(FakeLLM(["x" * 40]), tracker)
    llm([{"role": "user", "content": "y" * 400}])
    assert (tracker.calls, tracker.input_tokens, tracker.output_tokens) == (1, 100, 10)
    assert estimate_tokens("") == 0
    assert estimate_tokens("abc") == 1


def test_budget_blocks_the_next_call():
    tracker = CostTracker(price_in_per_mtok=1.0, price_out_per_mtok=1.0, max_cost_usd=0.001)
    tracker.record(1_000, 0)                         # exactly $0.001 spent
    llm = FakeLLM([])                                # would fail loudly if called
    with pytest.raises(BudgetExceeded):
        summarize(llm, "Report 1: flooding in Tamsi.", tracker=tracker)
    assert llm.calls == []


# --- R1 / R2: summarize -------------------------------------------------------------

def test_summarize_sends_system_prompt_and_reports():
    reports = "Report 1: approx 1,200 households affected in Tamsi."
    llm = FakeLLM(["Summary\n- 1,200 households affected (Report 1)\nGaps: deaths not stated"])
    out = summarize(llm, reports, max_words=80)
    assert out.startswith("Summary")
    messages = llm.calls[0]
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert "CONFLICT" in SYSTEM_PROMPT and "not stated" in SYSTEM_PROMPT
    assert f"<reports>\n{reports}\n</reports>" in messages[1]["content"]
    assert "80 words" in messages[1]["content"]


def test_summarize_retries_through_a_rate_limit():
    llm = FakeLLM([TransientError("429"), "Summary\n- ok"])
    assert summarize(llm, "Report", sleep=RecordingSleep()) == "Summary\n- ok"


def test_summarize_rejects_empty_input():
    llm = FakeLLM([])
    with pytest.raises(ValueError, match="empty"):
        summarize(llm, "   \n  ")
    assert llm.calls == []


def test_summarize_rejects_oversized_input():
    llm = FakeLLM([])
    with pytest.raises(ValueError, match="limit"):
        summarize(llm, "x" * (MAX_INPUT_CHARS + 1))
    assert llm.calls == []


# --- CLI ------------------------------------------------------------------------------

def test_cli_prints_summary_and_usage(capsys):
    code = main(["summarize", str(HERE / "sample_reports.md"), "--max-words", "100"],
                llm=FakeLLM(["Summary\n- Flooding in Tamsi since 11 March."]))
    out, err = capsys.readouterr()
    assert code == 0
    assert "Flooding in Tamsi" in out
    assert "calls=1" in err and "cost_usd=" in err


def test_cli_bad_input_exit_code(tmp_path, capsys):
    empty = tmp_path / "empty.md"
    empty.write_text("  ", encoding="utf-8")
    assert main(["summarize", str(empty)], llm=FakeLLM([])) == 2
    assert main(["summarize", str(tmp_path / "missing.md")], llm=FakeLLM([])) == 2
    assert "Input error" in capsys.readouterr().err


def test_cli_exit_code_when_model_unavailable(capsys, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)   # don't really wait in the CLI path
    llm = FakeLLM([TransientError("503")] * 4)
    assert main(["summarize", str(HERE / "sample_reports.md")], llm=llm) == 3
    assert "failed after 4 attempts" in capsys.readouterr().err
