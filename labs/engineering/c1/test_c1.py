"""Tests for Class 1. No API key and no packages beyond pytest: the tokenizer is a pure-Python
approximation and a scripted FakeLLM stands in for the model."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

import pytest

from decomposition import (MY_DECOMPOSITION, REFERENCE_DECOMPOSITION, Task,
                           validate_decomposition)
from tokens import (LANGUAGE_SAMPLE, Price, approx_tokenize, count_tokens, estimate_cost,
                    language_table)
from variance import analyse, majority_answer, normalize_number, sample


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


# --- tokens.py ------------------------------------------------------------

def test_short_english_words_are_one_token_and_keep_their_space():
    assert approx_tokenize("clean water is urgent") == ["clean", " water", " is", " urgent"]


def test_long_words_split_into_pieces():
    assert approx_tokenize("households") == ["househ", "olds"]


def test_numbers_split_into_groups_of_three_digits():
    assert approx_tokenize("1,200") == ["1", ",", "200"]
    assert approx_tokenize("1450") == ["145", "0"]


def test_chinese_is_about_one_token_per_character():
    assert approx_tokenize("清洁饮用水") == ["清", "洁", "饮", "用", "水"]


def test_russian_and_arabic_split_into_shorter_pieces():
    assert approx_tokenize("вода") == ["вод", "а"]
    assert len(approx_tokenize("الفيضانات")) == 3


def test_empty_text_has_no_tokens():
    assert approx_tokenize("") == []
    assert count_tokens("   ") == 0


def test_tokenizer_is_pluggable():
    def one_token_per_word(text: str) -> List[str]:
        return text.split()

    assert count_tokens("a b c", tokenizer=one_token_per_word) == 3
    est = estimate_cost("a b c d", 0, Price(1_000_000, 0), tokenizer=one_token_per_word)
    assert est.input_tokens == 4 and est.cost_usd == pytest.approx(4.0)


def test_cost_counts_input_and_output_at_different_prices():
    price = Price(input_per_million=2.0, output_per_million=10.0)
    est = estimate_cost("x" * 12, expected_output_tokens=500, price=price,
                        tokenizer=lambda t: list(t))  # one token per character: 12 in
    assert est.input_tokens == 12
    assert est.cost_usd == pytest.approx((12 * 2.0 + 500 * 10.0) / 1_000_000)
    month = est.times(1000)
    assert month.output_tokens == 500_000
    assert month.cost_usd == pytest.approx(est.cost_usd * 1000)


def test_same_message_costs_more_tokens_in_non_latin_scripts():
    rows = {lang: (tokens, ratio) for lang, tokens, ratio in language_table(LANGUAGE_SAMPLE)}
    assert set(rows) == {"English", "French", "Spanish", "Russian", "Arabic", "Chinese"}
    assert rows["English"][1] == 1.0
    for lang in ("Russian", "Arabic", "Chinese"):
        assert rows[lang][1] > 1.2, lang


# --- decomposition.py -----------------------------------------------------

def test_reference_decomposition_passes():
    assert validate_decomposition(REFERENCE_DECOMPOSITION) == []


def test_unfilled_exercise_reports_every_missing_owner():
    problems = validate_decomposition(MY_DECOMPOSITION)
    assert len(problems) == len(MY_DECOMPOSITION)
    assert all("owner must be" in p for p in problems)


def _with(task_id: str, **changes) -> List[Task]:
    return [replace(t, **changes) if t.id == task_id else t for t in REFERENCE_DECOMPOSITION]


def test_arithmetic_by_ai_is_rejected():
    problems = validate_decomposition(_with("totals", owner="AI", checked_by="conflicts"))
    assert any("arithmetic belongs to code" in p for p in problems)


def test_ai_step_without_a_check_is_rejected():
    problems = validate_decomposition(_with("draft", checked_by=""))
    assert any("draft: AI step needs checked_by" in p for p in problems)


def test_ai_step_checked_by_an_earlier_step_is_rejected():
    problems = validate_decomposition(_with("draft", checked_by="validate"))
    assert any("must come after" in p for p in problems)


def test_ai_checking_ai_is_rejected():
    problems = validate_decomposition(_with("extract", checked_by="draft"))
    assert any("owned by code or a human" in p for p in problems)


def test_approval_by_ai_is_rejected_and_blocks_publishing():
    problems = validate_decomposition(_with("approve", owner="AI", checked_by="publish"))
    assert any("only a human" in p for p in problems)
    assert any("publish: nothing is published" in p for p in problems)


# --- variance.py ----------------------------------------------------------

def test_sample_sends_identical_messages_n_times():
    llm = FakeLLM(["1200", "1,200", "1450"])
    messages = [{"role": "user", "content": "How many households?"}]
    replies = sample(llm, messages, n=3)
    assert replies == ["1200", "1,200", "1450"]
    assert llm.calls == [messages] * 3


def test_normalize_number():
    assert normalize_number("About 1,200 households.") == "1200"
    assert normalize_number("1450") == "1450"
    assert normalize_number("I cannot tell from the reports.") is None


def test_analyse_counts_normalised_answers():
    replies = ["1200", "1,200 households", "1450", "1200.", "unclear"]
    report = analyse(replies)
    assert report.counts == {"1200": 3, "1450": 1}
    assert report.distinct == 2
    assert report.unparseable == 1
    assert report.majority == "1200"
    assert report.agreement == pytest.approx(0.6)


def test_majority_answer_requires_enough_agreement():
    assert majority_answer(["1200"] * 8 + ["1450"] * 2) == "1200"
    # 60% agreement is below the default 70% threshold: escalate instead of guessing.
    assert majority_answer(["1200"] * 6 + ["1450"] * 4) is None
    assert majority_answer(["no idea"] * 3) is None
