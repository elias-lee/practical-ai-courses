# Pre-work — Set up and smoke-test your environment

One real model call, through the same `llm.py` interface every later lab uses, printing the
reply, the token usage and the latency. If this works, you are ready for Class 1.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`), a LiteLLM adapter, and `UsageTrackingLLM`, which also records token usage |
| `smoke_test.py` | Checks your environment variables, makes one call, prints reply, tokens and latency |
| `test_smoke_test.py` | Tests using a scripted `FakeLLM` — **no API key needed** |
| `.env.example` | Template for your environment variables (copy to `.env`, never commit) |
| `.gitignore` | Keeps `.env` out of Git |

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
```

## Run the tests (no key needed)

```bash
pytest -q
```

## Run the smoke test (needs a key)

Get a key through your organization's approved route, then set `MODEL` plus your provider's
variables (model names as of 2026 — check your provider):

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys
python smoke_test.py
```

Expected output (your numbers will differ):

```text
Model:    openai/gpt-4o-mini
Reply:    SitRep Assistant online.
Tokens:   33 in + 6 out = 39
Latency:  0.84 s
```

If you prefer a `.env` file: `cp .env.example .env`, fill it in, and load it with
`set -a; source .env; set +a` (macOS/Linux) before running. Check `git status` shows no `.env`.

## Stretch challenges

1. **Compare providers.** If you have access to two providers, run the smoke test against both
   and compare latency and token counts for the same prompt. Why might the token counts differ?
2. **Time it properly.** Latency varies. Change `main()` to run the call five times and print the
   minimum, median and maximum. What does the spread tell you about timeouts you will need?
3. **Load `.env` in Python.** Install `python-dotenv` and call `load_dotenv()` at the top of
   `main()`. Then write a test proving that `check_environment` still reports a missing key
   when `.env` is absent.
