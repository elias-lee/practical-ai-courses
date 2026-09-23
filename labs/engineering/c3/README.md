# Lab 3 — SitRep Summarizer, built spec-first

Your first real LLM app: a command-line tool that summarizes messy field reports, with
retries, timeouts, cost tracking and a budget. It is small on purpose (about 150 lines) and it
was built **spec-first**: `SPEC.md` was written before the code, and `test_app.py` turns every
requirement into a check. In the lab you extend it with an AI coding assistant, using the spec
and tests as the contract the assistant must satisfy.

| File | What it is |
|---|---|
| `SPEC.md` | The written spec: interface, requirements R1–R8, non-goals, acceptance tests |
| `llm.py` | The model interface (`messages -> text`), a LiteLLM adapter with a timeout, error translation and usage reporting |
| `app.py` | `call_with_retry()`, `CostTracker`, `tracked()`, `summarize()` and the CLI |
| `test_app.py` | 15 tests using a scripted `FakeLLM` and a fake `sleep` — **no API key needed** |
| `sample_reports.md` | Three messy, **fictional** field reports from Northern Veloria province |
| `.gitignore` | Keeps `.env` and other secrets out of git |

## Setup

Python 3.11+ recommended (the code also runs on 3.9).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
pip freeze > requirements.lock     # pin exact versions once it works
```

## Run the tests (no key needed)

```bash
pytest -q
```

All tests should pass in well under a second. `FakeLLM` can be scripted to *raise* errors
(`TransientError("429")`) as well as return text, and `RecordingSleep` records the backoff
delays instead of waiting. That is why a test of "retry three times with 1 s, 2 s, 4 s waits"
takes milliseconds.

## Run it for real (needs a key)

Set `MODEL` plus your provider's variables (model names as of 2026 — check your provider):

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys; never paste them into a chat
python app.py summarize sample_reports.md --max-words 120 --max-cost 0.01
```

The summary goes to stdout and one usage line to stderr, for example
`calls=1 input_tokens=498 output_tokens=131 cost_usd=0.000153`. Set `PRICE_IN_PER_MTOK` and
`PRICE_OUT_PER_MTOK` to your model's real prices; the defaults are illustrative only.

To see a retry for real, set an impossible timeout: edit `main()` to pass `timeout=0.001` to
`litellm_llm`, run again, and watch the command give up with exit code 3 after four attempts.

Use only fictional data: do not paste real field reports into a lab.

## Stretch challenges

1. **Add a `--stream` flag.** Print tokens as they arrive (`litellm.completion(...,
   stream=True)` yields chunks whose `choices[0].delta.content` holds the new text). Update
   `SPEC.md` first, then write a test with a fake that yields chunks, then implement. Decide
   what happens if the stream fails half-way: retry from scratch, or keep the partial text?
2. **Honour `Retry-After`.** Some providers send a `Retry-After` header with a 429. Extend
   `call_with_retry` so that, if the exception carries a `retry_after` attribute, it waits that
   long (still capped) instead of the computed backoff. Test-first.
3. **Add a fallback model.** Add `--fallback-model`: if the primary model still fails after
   its retries, try the fallback once, and record which model answered in the usage line.
   Ask your coding assistant to implement it *from your updated spec*, then review its diff
   with the checklist on the class page before accepting it.
