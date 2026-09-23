"""Tests for the mini RAG pipeline. No API key and no packages beyond pytest: the
"embedding" is pure Python and a scripted FakeLLM stands in for the model."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from rag import (
    GROUNDING_RULES,
    NOT_FOUND,
    Index,
    answer,
    chunk,
    cosine,
    load_library,
    parse_citations,
    recall_at_k,
    search_multilingual,
)

LIBRARY = Path(__file__).resolve().parent / "library"


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


@pytest.fixture(scope="module")
def index() -> Index:
    return Index.from_documents(load_library(LIBRARY), size=60, overlap=15)


def top_doc(hits) -> str:
    return hits[0].chunk.doc_id


# --- chunking -----------------------------------------------------------------------

def test_chunk_overlap_is_correct():
    words = [f"w{i}" for i in range(25)]
    chunks = chunk(" ".join(words), size=10, overlap=3)
    assert [c.split() for c in chunks] == [words[0:10], words[7:17], words[14:24], words[21:25]]
    for a, b in zip(chunks, chunks[1:]):
        assert a.split()[-3:] == b.split()[:3]      # neighbours share exactly 3 words
    assert chunks[-1].split()[-1] == "w24"           # nothing lost at the end


def test_chunk_edge_cases():
    assert chunk("only five words in here", size=10, overlap=3) == ["only five words in here"]
    assert chunk("   ", size=10, overlap=3) == []
    with pytest.raises(ValueError):
        chunk("a b c", size=5, overlap=5)            # overlap must be smaller than size
    with pytest.raises(ValueError):
        chunk("a b c", size=0, overlap=0)


# --- vectors ------------------------------------------------------------------------

def test_cosine_similarity():
    assert cosine({"flood": 1.0, "bridge": 2.0}, {"flood": 2.0, "bridge": 4.0}) == pytest.approx(1.0)
    assert cosine({"flood": 1.0}, {"cholera": 1.0}) == 0.0
    assert cosine({}, {"flood": 1.0}) == 0.0


def test_library_loads_with_metadata(index):
    docs = load_library(LIBRARY)
    assert len(docs) == 6
    langs = {d.id: d.metadata["lang"] for d in docs}
    assert langs["bara-fr-2026-03-16"] == "fr"
    assert all(c.cid.startswith(c.doc_id + "#") for c in index.chunks)


# --- retrieval ------------------------------------------------------------------------

def test_retrieval_finds_the_right_document(index):
    hits = index.search("Is the Tamsi health post working?", k=3)
    assert top_doc(hits) == "health-kessan-2026-03-15"
    assert top_doc(index.search("Is the well water safe to drink?", k=3)) == "wash-2026-03-17"


def test_hybrid_beats_keyword_on_a_paraphrased_query(index):
    # The logistics update says the *bridge collapsed*; the question says *crossing* and
    # *standing*. Keyword search only matches "Kessan", which is everywhere.
    question = "Is the crossing to Kessan still standing?"
    keyword = index.search(question, k=3, mode="keyword")
    hybrid = index.search(question, k=3, mode="hybrid")
    assert top_doc(keyword) != "logistics-2026-03-16"
    assert top_doc(hybrid) == "logistics-2026-03-16"


def test_metadata_filter(index):
    hits = index.search("families mosque food", k=5, where={"lang": "fr"})
    assert hits and all(h.chunk.metadata["lang"] == "fr" for h in hits)


def test_query_translation_finds_the_french_report(index):
    question = "How many families were displaced to the mosque?"
    assert top_doc(index.search(question, k=3)) != "bara-fr-2026-03-16"
    llm = FakeLLM(["Combien de familles déplacées sont hébergées dans la mosquée ?"])
    hits = search_multilingual(llm, question, index, languages=["fr"], k=3)
    assert top_doc(hits) == "bara-fr-2026-03-16"
    assert "French" in llm.calls[0][-1]["content"]


def test_recall_at_k(index):
    cases = [
        ("Is the Tamsi health post working?", "health-kessan-2026-03-15"),
        ("How many latrines are there at the school shelter?", "wash-2026-03-17"),
        ("Is the crossing to Kessan still standing?", "logistics-2026-03-16"),
    ]
    assert recall_at_k(index, cases, k=1, mode="hybrid") == 1.0
    assert recall_at_k(index, cases, k=1, mode="keyword") == pytest.approx(2 / 3)


# --- answers --------------------------------------------------------------------------

def test_answer_cites_sources(index):
    reply = ("The Tamsi health post has been non-functional since 15 March and the cold "
             "chain was lost [health-kessan-2026-03-15#0].")
    llm = FakeLLM([reply])
    result = answer(llm, "Is the Tamsi health post working?", index)
    assert result.found
    assert result.citations == ["health-kessan-2026-03-15#0"]
    assert result.unknown_citations == []
    system, user = llm.calls[0]
    assert system["content"] == GROUNDING_RULES
    assert "[health-kessan-2026-03-15#0]" in user["content"]      # the source is labelled
    assert "cold chain was lost" in user["content"]               # and its text is included
    assert user["content"].rstrip().endswith("Question: Is the Tamsi health post working?")


def test_answer_flags_citations_that_were_not_retrieved(index):
    llm = FakeLLM(["The health post is closed [health-kessan-2026-03-15#0]. "
                   "A new hospital opened in Aramu [aramu-hospital#3]."])
    result = answer(llm, "Is the Tamsi health post working?", index)
    assert result.citations == ["health-kessan-2026-03-15#0"]
    assert result.unknown_citations == ["aramu-hospital#3"]


def test_not_found_without_calling_the_model(index):
    llm = FakeLLM([])                                  # any call would fail the test
    result = answer(llm, "What is the average rainfall forecast for next month?", index)
    assert not result.found
    assert result.text == NOT_FOUND
    assert llm.calls == []


def test_model_can_say_not_found(index):
    llm = FakeLLM(["NOT FOUND"])
    result = answer(llm, "How many measles cases were confirmed in Tamsi?", index)
    assert not result.found and result.citations == []
    assert len(llm.calls) == 1


def test_parse_citations():
    text = "A [x#0]. B [y#1; z#2]. C [x#0, w#4]. Not a citation [see annex]."
    assert parse_citations(text) == ["x#0", "y#1", "z#2", "w#4"]
