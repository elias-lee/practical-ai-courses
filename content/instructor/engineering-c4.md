# Engineering Class 4 · Context Engineering and RAG — Instructor Guide

**Learner page:** [Class 4 · Context Engineering and RAG](../engineering/c4.md) ·
**Lab folder:** `labs/engineering/c4/` · **Quiz:** `quizzes/engineering/c4.yml`

This class covers a lot of ground. Guard the core: context budgets, the pipeline, hybrid search,
citations with a not-found path, and measuring retrieval. Agentic RAG, GraphRAG, memory and
caching (Sections 10–12) can be taught as a quick tour with the sidebars if time is short. The
lab is pure Python, so every score can be printed and explained. Use that: learners who have
seen BM25 and cosine numbers side by side understand vector databases much better.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 3 (stateless API, transient errors, tests as contract). Bridge: "The model is stateless and knows only its training data. How does it answer about today's reports?" |
| 0:10–0:25 | Concept I: context engineering | Section 1. The briefing-folder analogy; build the budget table on the board with the room; lost in the middle; stable-first ordering. |
| 0:25–0:50 | Concept II: the pipeline | Sections 2–8. Draw the offline and online halves; chunking trade-offs; embeddings as coordinates; hybrid search with the three-line score printout; citations and the not-found gate. |
| 0:50–1:00 | Concept III: tour | Sections 9–14 at speed: multilingual table, agentic RAG vs GraphRAG, memory types, caching rule, the RAG/fine-tuning/long-context table, recall@k. |
| 1:00–1:20 | Live demo | See the script below: keyword fails a paraphrase, hybrid fixes it; then the deliberate hallucination and the gate. |
| 1:20–1:30 | Break | |
| 1:30–2:30 | Lab (pairs) | Steps 1–5; stretch challenges for fast pairs. |
| 2:30–2:45 | Check Your Understanding | Discuss the most-missed question (usually Q2 or Q4). |
| 2:45–2:55 | Debrief | Each pair shares one recall@k finding or one citation their real model got wrong. |
| 2:55–3:00 | Exit ticket | Collect; the "question keyword search gets wrong" answers are good golden-set seeds for Class 7. |

## Live-demo script (20 min)

**Goal:** make retrieval visible (scores, ranks, citations), show a hybrid search win, then
show the classic RAG failure, a fluent uncited answer to an unanswerable question, and fix it
in code.

1. **Tests (2 min).** In `labs/engineering/c4/`, run `pytest -q`: 14 passes, no key, no
   downloads.
2. **Look inside search (6 min).** In a Python shell:

    ```python
    from rag import Index, load_library, features
    index = Index.from_documents(load_library("library"))
    q = "Is the crossing to Kessan still standing?"
    for mode in ("keyword", "vector", "hybrid"):
        print(mode, [(h.chunk.cid, round(h.score, 2)) for h in index.search(q, k=3, mode=mode)])
    print(features(q))
    ```

    Ask the room to predict the keyword result before you run it. Point at the `~access` concept
    tag: "this is the toy version of what an embedding model learns."
3. **The deliberate failure: a hallucinated answer (6 min).** Show what happens *without* the
   not-found gate. With a real key:

    ```python
    import os
    from llm import litellm_llm
    llm = litellm_llm(os.environ["MODEL"], temperature=0)
    q = "What is the rainfall forecast for Aramu next month?"
    print(llm([{"role": "user", "content": q}]))
    ```

    Most models produce a fluent, plausible-sounding forecast, or generic climate information,
    with no source. Ask: "Would this end up in a SitRep? Who would notice?" (If you have no key,
    use a `FakeLLM` scripted with a plausible forecast; the point is the same.)
4. **The fix (4 min).**

    ```python
    from rag import answer
    r = answer(llm, q, index)
    print(r.found, r.text, r.sources)       # False NOT FOUND []
    ```

    Show the three lines in `answer()` that return before the model is called, and the test that
    proves it (`FakeLLM([])`). Worth pointing out: BM25 *did* match "Aramu" in the market report,
    but no chunk's cosine similarity reaches the 0.1 floor (the best is about 0.07), so nothing
    counts as relevant. A keyword hit on a place name is not an answer. Then ask a real question and show `r.citations` and
    `r.unknown_citations`.
5. **Multilingual (2 min).** Run `search_multilingual` with the real model on "How many
   families were displaced to the mosque?" and show the French Bara report jump to the top.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "A bigger context window makes RAG unnecessary." | Lost in the middle, distractors, cost per call, per-user access control. Q2 and Q3. |
| "Vector search understands everything; keywords are obsolete." | Ask for "SR-2026-014" or "1,450". Exact terms need keyword search: that's why hybrid is the default. |
| "Fine-tune the model on our documents so it knows them." | Fine-tuning changes behaviour, not an updatable, citable, permission-aware store of facts. |
| "Telling the model not to hallucinate is enough." | The demo. Gate in code before the model; check citations after. |
| "A citation means the claim is supported." | Only if the cited chunk was retrieved *and* says that. Exercise 3's families/households trap. |
| "Translate the answer and multilingual is done." | The failure is in retrieval: the French report never reaches the model. |
| "Chunk size is a detail." | It is one of the biggest levers on recall. Measure it; don't guess. |
| "Memory is always helpful." | Memories go stale, can be wrong, and are personal data. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | C | Hybrid search | B: paste everything. It works on six documents, which is exactly why it's tempting. |
| 2 | A | Context rot / lost in the middle | C: "longer is always better, fix the prompt". A strong intuition that the class has to unlearn. |
| 3 | D | RAG vs fine-tuning vs long context | A: weekly fine-tuning. Sounds thorough; fails freshness, citations and access control. |
| 4 | B | Multilingual retrieval | D: raise k to 50. Partly works, which makes it attractive, but hides the real problem. |
| 5 | D | Not-found path | A: "do not hallucinate". Feels like the obvious fix; it is a request, not a guarantee. |
| 6 | B | Citation checking | D: look up the id and add it. Well-meant, but the model never saw that source. |
| 7 | A | Prompt caching | C: fine-tune on the style guide. Solves the wrong problem at great cost. |
| 8 | C | Evaluating retrieval | A: "smaller is always more precise". Half-true, which is what makes it dangerous. |

## Discussion prompts

- "Which document collection in your office would you index first? What metadata is missing
  from it today?"
- "Who may see which documents? How would you carry those permissions into the index?"
- "In your context, which languages matter most, and which approach from the multilingual
  table would you pilot?"
- "When should the assistant say NOT FOUND, and how should the interface present that so users
  don't just rephrase until it guesses?"

## Lab facilitation tips

- **Print scores, always.** Encourage pairs to print `keyword_score` and `vector_score` for
  every hit. Most "why did it pick that?" questions answer themselves.
- **Be honest about the toy embedding.** The concept-tag table is hand-made. Learners who notice
  that adding a word to `CONCEPTS` "fixes" a query have understood something real: a real model
  learns those associations from data, and fails where its training data was thin, often on
  local place names and less-resourced languages.
- **Step 3's date filter** opens a design discussion (extend `where` with operators vs a
  dedicated parameter). Both are fine if tested.
- **Real runs:** have pairs check *every* citation by hand against the printed chunk. This is
  where they find citation drift, a real sentence attached to the wrong source.

## Common lab bugs

- **`ModuleNotFoundError: rag`**: running from outside the folder without `conftest.py`.
- **`FileNotFoundError` or zero documents**: `load_library("library")` is relative to the
  current directory; run from `labs/engineering/c4/` or pass an absolute path.
- **`ValueError: overlap must be … smaller than size`**: learners try `overlap == size` to
  "maximise context". Good moment to ask what the step size would be (zero: an infinite loop).
- **Hybrid test fails after edits**: changing `STOPWORDS`, `CONCEPTS` or the default chunk
  size shifts the scores. That's expected: retrieval is sensitive to these choices, which is why
  they must be measured. Revert, or update the test deliberately with a reason.
- **Multilingual test fails**: the `FakeLLM` translation was changed to include quotes or an
  explanation. `translate_query` strips whitespace only; real models need the "translation
  only" instruction, and sometimes a clean-up step.
- **Real model ignores the citation format** (e.g. writes "(Source 1)"): tighten the rules with
  one example sentence, or post-process. `parse_citations` accepts only `[id#n]`.
- **`NOT FOUND` for a question the library does answer**: `min_similarity` is too high for
  the query, or the question uses only stopwords and rare words. Print `vector_score` for the
  top hits and adjust with a test.
