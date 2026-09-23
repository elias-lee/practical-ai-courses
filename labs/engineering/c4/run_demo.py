"""Ask the document library questions with a real model.

    export MODEL="openai/gpt-4o-mini"      # or azure/<deployment>, anthropic/<model>
    python run_demo.py                                  # runs the sample questions
    python run_demo.py "Is the Bara well water safe?"   # or your own question

Prints the retrieved chunks with their scores, then the grounded answer and its citations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from llm import litellm_llm
from rag import Index, answer, load_library, search_multilingual

HERE = Path(__file__).resolve().parent

SAMPLE_QUESTIONS = [
    "Is the Tamsi health post working?",
    "Is the crossing to Kessan still standing?",
    "How many households are affected? Do the sources agree?",
    "How many days of food do the families in the Bara mosque have?",
    "What is the average rainfall forecast for next month?",   # should be NOT FOUND
]


def main() -> int:
    if "MODEL" not in os.environ:
        print("Set MODEL first, e.g. export MODEL=openai/gpt-4o-mini (see README.md).")
        return 1
    llm = litellm_llm(os.environ["MODEL"], temperature=0)
    index = Index.from_documents(load_library(HERE / "library"), size=60, overlap=15)
    print(f"Indexed {len(index.chunks)} chunks from {HERE / 'library'}\n")

    for question in sys.argv[1:] or SAMPLE_QUESTIONS:
        print("=" * 78)
        print("Q:", question)
        for h in index.search(question, k=4):
            print(f"   {h.chunk.cid:<32} hybrid={h.score:.2f} bm25={h.keyword_score:.2f} "
                  f"cos={h.vector_score:.2f}")
        multi = search_multilingual(llm, question, index, languages=["fr"], k=4)
        print("   with French query translation, top:", multi[0].chunk.cid if multi else "-")
        result = answer(llm, question, index)
        print("\nA:", result.text)
        print("   citations:", result.citations or "none")
        if result.unknown_citations:
            print("   WARNING - cited but not retrieved:", result.unknown_citations)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
