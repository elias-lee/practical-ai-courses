# Lab 1 — Thinking and models

Three small tools that turn Class 1's ideas into code you can run and test: a token and cost
estimator, a decomposition exercise for the SitRep process, and a variance experiment.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `tokens.py` | Token and cost estimator with a **pluggable tokenizer**; compares six widely used languages |
| `decomposition.py` | **Exercise:** assign each SitRep step to AI, code or a human; a validator checks the rules |
| `variance.py` | Sample the same prompt N times, normalise the answers, and decide by majority or escalate |
| `test_c1.py` | Tests using a pure-Python tokenizer and a scripted `FakeLLM` — **no API key needed** |
| `sample_reports.md` | Three messy, **fictional** field reports with a deliberate conflict (1,200 vs 1,450 households) |

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
pip install tiktoken               # optional: a real tokenizer for tokens.py
```

## Run the tests (no key needed)

```bash
pytest -q
```

## Run the tools

```bash
python tokens.py                   # six-language token table and a monthly cost estimate
python decomposition.py            # validates YOUR decomposition (edit MY_DECOMPOSITION first)
```

`tokens.py` uses `approx_tokenize`, a deliberately simple pure-Python approximation. To use a
real tokenizer, pass one in:

```python
from tokens import LANGUAGE_SAMPLE, language_table, tiktoken_tokenizer

for lang, n, ratio in language_table(LANGUAGE_SAMPLE, tokenizer=tiktoken_tokenizer("o200k_base")):
    print(f"{lang:<8} {n:>4} tokens  {ratio:.2f}x English")
```

`tiktoken` covers OpenAI-family tokenizers. Other providers use their own; for exact counts use
the provider's token-counting endpoint or the `usage` figures returned with every response.

## Run the variance experiment (needs a key)

Set `MODEL` plus your provider's variables (model names as of 2026 — check your provider):

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys
python variance.py
```

It asks "how many households are affected?" ten times at temperature 0 and ten times at 1.0.
The reports genuinely disagree (1,200 vs 1,450, plus 60 *families*), so watch for 1200, 1450
and 2650 — and notice that disagreement between samples is a signal about the *data*, not just
the model.

## Stretch challenges

1. **Measure the real ratios.** Install `tiktoken` and rerun the language table with
   `tiktoken_tokenizer("o200k_base")` and `tiktoken_tokenizer("cl100k_base")` (an older
   tokenizer). Which languages gained most from the newer tokenizer? Adjust
   `CHARS_PER_TOKEN` so the approximation lands within 15% of the real counts.
2. **Normalise better.** `normalize_number` takes the *first* number in a reply. Write a test
   where that is wrong ("Between 1,200 and 1,450 households") and decide what the right
   behaviour is — perhaps returning `None` so the answer counts as unparseable.
3. **Budget guard.** Write `check_budget(prompt, max_input_tokens, tokenizer)` that raises
   before a call if the prompt is too long, with a test. Where in the SitRep pipeline would you
   put it?
