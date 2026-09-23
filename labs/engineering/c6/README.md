# Lab 6 — Build the SitRep orchestrator

A multi-agent SitRep pipeline in about 150 lines of plain Python — no agent framework — so you
can see every moving part of an orchestration layer. The class page then shows the same design
in LangGraph.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `agents.py` | `Agent(name, system_prompt)` and the four SitRep specialists |
| `orchestrator.py` | `plan()` (validated JSON plan), `run_plan()` (dependency order), `review_loop()` (evaluator-optimizer) |
| `test_orchestrator.py` | Tests using a scripted `FakeLLM` — **no API key needed** |
| `run_demo.py` | Runs the whole pipeline against a real model |
| `sample_reports.md` | Three messy, **fictional** field reports from Northern Veloria province |

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

All tests should pass. They use `FakeLLM`, which returns scripted replies and records every
message it receives, so you can assert on *what the orchestrator sent*, not just what came back.

## Run the demo (needs a key)

Set `MODEL` plus your provider's variables (model names as of 2026 — check your provider):

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys
python run_demo.py
```

You will see the plan, one trace line per model call, the number of review rounds, and the
final SitRep. Use only fictional data: do not paste real field reports into a lab.

## Stretch challenges

1. **Add a router step.** Before planning, call a cheap model with a classifier prompt that
   labels the request `sitrep`, `update_existing`, `translation` or `out_of_scope`, and only
   call `plan()` for `sitrep`. Write a test with `FakeLLM` for each label.
2. **Run independent steps in parallel.** Steps whose dependencies are all complete can run at
   the same time. Change `run_plan()` to execute each "ready layer" with
   `concurrent.futures.ThreadPoolExecutor`. Test that outputs are identical to the sequential
   version (hint: make `FakeLLM` return a reply keyed on the system prompt, not on call order).
3. **Add a human-approval gate before the Writer.** Pause after the Analyst step, print the
   key figures, and ask `Approve figures? [y/N]`. On "no", stop and save the partial state to a
   JSON file so the run can be resumed later without re-running the Researcher and Analyst.
