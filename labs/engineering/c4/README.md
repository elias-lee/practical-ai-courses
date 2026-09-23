# Lab 4 — A SitRep that answers from documents, with citations

A complete retrieval-augmented generation (RAG) pipeline in about 300 lines of plain Python:
chunking, a toy embedding, BM25 keyword search, hybrid scoring, metadata filters, query
translation, grounded answers with citations and a "not found" path, and a retrieval metric.
No vector database and no embedding model are needed for the tests; the section
[The real version](#the-real-version-chroma-and-an-embedding-model) shows the same pipeline
with Chroma and a multilingual embedding model.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `rag.py` | `chunk()`, `Index` (BM25 + vectors + hybrid `search()`), `search_multilingual()`, `answer()`, `recall_at_k()` |
| `test_rag.py` | 14 tests using a scripted `FakeLLM` — **no API key needed** |
| `run_demo.py` | Asks the library questions with a real model and prints scores and citations |
| `library/` | Six short, **fictional** documents from Northern Veloria province (one in French) |

## Setup

Python 3.11+ recommended (the code also runs on 3.9).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
```

## Run the tests (no key needed)

```bash
pytest -q
```

Read the tests before the code; they are the specification. Four of them carry the main
lessons of the class:

- `test_chunk_overlap_is_correct`: neighbouring chunks share exactly `overlap` words.
- `test_hybrid_beats_keyword_on_a_paraphrased_query`: "Is the crossing to Kessan still
  standing?" never mentions a *bridge* or a *collapse*, so keyword search alone misses the
  logistics update. The vector side catches the paraphrase.
- `test_query_translation_finds_the_french_report`: an English question only reaches the
  French community report from Bara once it is also searched in French.
- `test_not_found_without_calling_the_model`: if nothing relevant is retrieved, the model is
  never asked. There is nothing to ground an answer in.

## Run it for real (needs a key)

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

Model names are as of 2026; check your provider.

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys
python run_demo.py
python run_demo.py "How many households are affected? Do the sources agree?"
```

For each question you will see the retrieved chunks with their hybrid, BM25 and cosine
scores, then the answer with its citations. Check every citation against the chunk it names.
Use only fictional documents: do not put real reports into a lab.

## The real version: Chroma and an embedding model

In production you replace the toy parts, not the shape. The snippet below is illustrative and
reflects the libraries as of 2026; check their documentation for current names.

```bash
pip install chromadb sentence-transformers rank-bm25
```

```python
import chromadb
from chromadb.utils import embedding_functions
from rag import chunk, load_library

# A multilingual embedding model maps text in many languages into one shared vector space,
# so an English question can match a French or Arabic passage directly.
embed = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-small")          # or BAAI/bge-m3, or a hosted API

client = chromadb.PersistentClient(path="./chroma")       # a folder on disk
col = client.get_or_create_collection("sitrep-library", embedding_function=embed)

for doc in load_library("library"):
    pieces = chunk(doc.text, size=200, overlap=40)
    col.upsert(
        ids=[f"{doc.id}#{i}" for i in range(len(pieces))],
        documents=pieces,
        metadatas=[{**doc.metadata, "doc_id": doc.id, "title": doc.title}] * len(pieces),
    )

res = col.query(query_texts=["Is the crossing to Kessan still standing?"],
                n_results=4, where={"lang": "en"})        # metadata filter, as in the lab
for cid, text, dist in zip(res["ids"][0], res["documents"][0], res["distances"][0]):
    print(cid, round(dist, 3), text[:80])
```

For the keyword half of hybrid search, `rank_bm25.BM25Okapi` does what `Index.keyword_scores`
does. For re-ranking, score the top 20 hybrid hits with a cross-encoder such as
`sentence_transformers.CrossEncoder("BAAI/bge-reranker-v2-m3")` and keep the best 4. With
pgvector (PostgreSQL) or a hosted vector store the steps are identical: embed, store with
metadata, query with a filter, fuse with keyword scores, re-rank, cite.

## Stretch challenges

1. **Re-ranking.** Add `rerank(llm, question, hits, keep=3)` that asks the model to score each
   retrieved chunk 0–10 for relevance (one call, JSON output) and reorders them. Test it with
   `FakeLLM`. When does re-ranking fix the top result, and what does it cost?
2. **Sentence-aware chunking.** Write `chunk_sentences(text, max_words, overlap_sentences)`
   that never splits a sentence, then compare `recall_at_k` for both chunkers on a set of ten
   questions you write yourself (your first golden test set; Class 7 builds on it).
3. **Multilingual answers.** Let `answer()` take a `retriever` argument so it can use
   `search_multilingual`, add an Arabic or Spanish document to `library/`, and check that the
   answer cites it and quotes its figures exactly.
