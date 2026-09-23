# Lab 8 — Red-team the SitRep intake

A prompt-injection red-team harness in plain Python. You will attack a naive report-summarising
pipeline, watch every attack succeed, then measure how far a defended pipeline gets — and where
it still fails. The same harness is what you point at another team's system in the capstone.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `pipeline.py` | `naive_pipeline()` and `defended_pipeline()`: untrusted-content separation, action allow-list, exfiltration filter, injection flags |
| `redteam.py` | `load_suite()`, `run_red_team() -> RedTeamResults`, and `gullible_llm`, a worst-case model that obeys every instruction it reads |
| `injection_suite.jsonl` | 13 **fictional** reports: 4 benign, 9 attacks across 8 categories |
| `test_redteam.py` | Tests — **no API key needed** |
| `run_red_team_demo.py` | Scores both pipelines, with the gullible model or a real one |

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

## Run the red team

```bash
python run_red_team_demo.py                    # gullible model: no key, fully deterministic
```

Expected: the naive pipeline loses 9/9 attacks; the defended pipeline loses 1/9 (the obfuscated
address in `a07`) and wrongly blocks 1/4 benign reports (the partner link in `b04`). Both
imperfections are deliberate: they are the discussion.

Then against a real model:

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini                # model names as of 2026 — check your provider
python run_red_team_demo.py --real
```

A real model usually resists some attacks on its own, so the naive pipeline scores better than
against the gullible model. That is exactly why you should not rely on it: the model's resistance
changes with every model version and every rephrased attack; the code defences do not.

## Rules of engagement

- Attack only systems you own, or that another team has explicitly handed you for the capstone.
- Use only fictional data. Never put real names, real locations or real credentials in a payload.
- Report findings to the owning team first, with the exact input that worked.

## Stretch challenges

1. **Close the a07 gap without breaking b04.** Add a check for obfuscated addresses (`(at)`,
   `[dot]`, spelled-out "at"/"dot") and for bare domains without `https://`. Then decide what to
   do about `b04`: add the partner to the allow-list, or route non-allow-listed links to a human
   instead of blocking. Re-run the suite and report both numbers.
2. **Write five new attacks** your pipeline does not catch — for example, a payload split across
   two reports, instructions in Arabic or Chinese, or a request to encode data in the summary's
   first letters. Add them to the suite with a `canary`, and fix what you can.
3. **Add a human approval gate.** Change `defended_pipeline` so that any allow-listed action
   marked irreversible (add `publish_sitrep`) is queued for approval instead of executed, and
   write a test that the queue — not the executor — receives it.
