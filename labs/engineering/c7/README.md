# Lab 7 — Measure the SitRep Assistant

An evaluation harness and a tracer in plain Python — no eval framework — so you can see exactly
what tools such as Langfuse, promptfoo or OpenTelemetry do for you. You will run a 20-case
golden dataset, read the report, make **one measured improvement**, and prove it did not break
anything else.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `evals.py` | `load_dataset()`, rule-based checks, `llm_judge()` / `judge_check()`, `run_eval() -> Report`, `compare()`, `cohens_kappa()` |
| `tracer.py` | `Tracer` with nested spans (duration, tokens, cost), JSON export, and `traced_llm()` |
| `sitrep_system.py` | The system under test: a one-call SitRep writer with `PROMPT_V1` and `PROMPT_V2` |
| `sitrep_golden.jsonl` | 20 **fictional** golden cases: core, edge, multilingual, adversarial, out-of-scope |
| `test_evals.py` | Tests using a scripted `FakeLLM` — **no API key needed** |
| `run_eval_demo.py` | Runs v1 and v2 against a real model and compares them |

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

## Run the eval (needs a key)

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini            # model names as of 2026 — check your provider
export JUDGE_MODEL=anthropic/claude-sonnet-4-5   # optional; ideally a different family
python run_eval_demo.py
```

40 model calls (plus 40 judge calls if `JUDGE_MODEL` is set). Results and traces are written
to `results/`. Do not commit `results/` if you ever run it on real data — and in this course,
never do.

## From the toy tracer to a real one

`tracer.py` has the same shape as a real trace: one trace per request, nested spans, attributes,
token usage and cost. The OpenTelemetry equivalent (API as of 2026; check the current docs):

```python
from opentelemetry import trace

tracer = trace.get_tracer("sitrep")
with tracer.start_as_current_span("sitrep_run") as span:
    span.set_attribute("case_id", "g01")
    with tracer.start_as_current_span("llm.call") as call:
        call.set_attribute("gen_ai.request.model", "gpt-4o-mini")
        call.set_attribute("gen_ai.usage.input_tokens", 812)
        call.set_attribute("gen_ai.usage.output_tokens", 240)
```

Langfuse, Arize Phoenix, LangSmith and similar tools accept OpenTelemetry traces and add
dashboards, dataset management and human annotation on top.

## Stretch challenges

1. **Calibrate the judge.** Label 10 outputs yourself (pass/fail) before looking at the judge's
   verdicts, then compute `cohens_kappa(judge, you)`. Below 0.6? Rewrite the rubric (more
   concrete anchors, one example per score) and measure again.
2. **Trajectory eval.** Run your Class 5 tool loop on five cases and write checks over
   `result.tool_calls`: called `search_reports` before `format_sitrep`; never called a blocked
   tool; used at most 6 steps; never called the same tool with the same arguments twice.
3. **A CI gate.** Write `ci_eval.py` that runs the rule-based checks on the golden set, loads
   `results/baseline.json`, and exits non-zero if `compare()` finds a regression. Add it to a
   GitHub Actions workflow that runs on pull requests that touch a prompt.
