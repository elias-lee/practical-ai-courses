# Engineering Class 6 · Agents & Orchestration — Instructor Guide

**Learner page:** [Class 6 · Agents & Orchestration](../engineering/c6.md) ·
**Lab folder:** `labs/engineering/c6/` · **Quiz:** `quizzes/engineering/c6.yml`

This is the course's flagship class and its densest. The concept block is deliberately
longer than the standard 30 minutes; the lab is framework-free so that learners understand the
mechanics before meeting LangGraph. Expect some pairs not to finish the stretch challenges —
see [Follow-up](#follow-up) below.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 5 (tools, MCP, guardrails). Ask: "What is the difference between a tool and an agent?" as a bridge. |
| 0:10–0:25 | Concept I: the agent loop | Sections 1–2. Walk the 20-line loop line by line; stop on `max_steps`, `except`, `BudgetExceeded`. Run the workflow-vs-agent table against 2–3 learner processes. |
| 0:25–0:50 | Concept II: patterns and topologies | Sections 3–4. Draw each pattern on the board as it is introduced; have pairs name a SitRep use for each before reading the page's example. Land 0.95¹⁰ ≈ 0.60. |
| 0:50–1:05 | Concept III: orchestration layer | Sections 5–7: budgets, state, gates, handoff contracts, cascades. Keep frameworks (Section 8) for after the lab. |
| 1:05–1:25 | Live demo | See the script below — tests with `FakeLLM`, then a runaway loop and its fix. |
| 1:25–1:35 | Break | |
| 1:35–2:30 | Lab (pairs) | Steps 1–5 of the lab; stretch challenges for fast pairs. |
| 2:30–2:40 | Frameworks debrief | Section 8: map the lab onto the LangGraph snippet using the concept table; MCP vs A2A in two minutes. |
| 2:40–2:55 | Check Your Understanding | Discuss the most-missed question (usually Q2 or Q5). |
| 2:55–3:00 | Exit ticket | Collect three answers to read out next class. |

## Live-demo script (20 min)

**Goal:** show that orchestration logic is testable without a model, and that a loop without a
budget is a real hazard — then fix it.

1. **Tests with no key (4 min).** In `labs/engineering/c6/`, with no API key set, run
   `pytest -q` and show 14 passes. Open `test_orchestrator.py`, show `FakeLLM`, and point out
   the assertion that the Analyst's task contains `FACTS-OUT` — "we are testing *what the
   orchestrator sent*, not what the model said."
2. **Break a plan on purpose (4 min).** In a Python shell:

    ```python
    from test_orchestrator import FakeLLM
    from orchestrator import plan
    import json
    bad = {"steps": [{"id": "a", "agent": "Researcher", "input": "x", "depends_on": ["b"]},
                     {"id": "b", "agent": "Analyst", "input": "y", "depends_on": ["a"]}]}
    plan(FakeLLM([json.dumps(bad)]), "req", ["Researcher", "Analyst"])
    ```

    Show the `PlanError: plan contains a cycle`. Ask: "Without this check, what would
    `run_plan` have done?" (Hang, or crash after spending money on the steps before.)

3. **The deliberate failure: a runaway loop (6 min).** Paste a naive review loop that "stops when
   the reviewer approves", with a reviewer that never does:

    ```python
    from itertools import cycle
    from agents import SITREP_AGENTS
    replies = cycle(["draft", "1. Add more detail on Bara."])
    calls = {"n": 0}
    def llm(messages):
        calls["n"] += 1
        return next(replies)

    W, R = SITREP_AGENTS["Writer"], SITREP_AGENTS["Reviewer"]
    draft = W.run(llm, "Write the SitRep")
    while not R.run(llm, draft).startswith("APPROVED"):
        draft = W.run(llm, "Write the SitRep")
        if calls["n"] >= 500:            # demo safety net only
            break
    print(calls["n"], "calls; at ~USD 0.01 per call that is", calls["n"] * 0.01, "USD")
    ```

    Pause on the number. Ask: "Where should the stop rule live — in the prompt or in the code?"

4. **The fix (4 min).** Replace the loop with the lab's function:

    ```python
    from orchestrator import review_loop
    calls["n"] = 0
    final, rounds = review_loop(llm, W, R, "Write the SitRep", max_rounds=3)
    print(rounds, "rounds,", calls["n"], "calls")   # 3 rounds, 6 calls
    ```

    Emphasise that `rounds == max_rounds` is a *distinct outcome*: the draft goes to a human.

5. **Optional real run (2 min).** If you have a key, `python run_demo.py` and read the trace
   lines aloud. If the live model fails or is slow, that is a teaching moment about fallbacks.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "Agents are always better than workflows." | Autonomy is a cost. Ask for the specific failure the agent fixes; if there isn't one, it's a workflow. |
| "More agents = more accuracy." | Do 0.95¹⁰ on the board. Agents add steps; steps compound errors. |
| "A bigger context window fixes coordination." | It lets you pass giant transcripts; it doesn't stop agents being distracted by irrelevant content, and cost scales with every hop. |
| "The model will stop when it's done." | The runaway-loop demo. Budgets live in code. |
| "The LLM reviewer means we don't need a human." | A reviewer improves drafts; accountability for publication stays with a person. |
| "Frameworks do the design for me." | Frameworks provide checkpoints and edges; they don't choose the pattern, the validation or the gate position. |
| "MCP and A2A are competing standards." | Different jobs: agent-to-tool vs agent-to-agent. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | B | Workflows vs agents | A — "agents are smarter". Unlearning this is the main goal of Section 2. |
| 2 | B | Error compounding | A — "as good as the average step". Intuitive but wrong; probabilities multiply. |
| 3 | C | Budgets and stop rules | A — "tell it in the prompt". Useful, but not a guarantee. |
| 4 | C | Orchestrator-workers | B — sectioning. The discriminator is whether sub-tasks are known in advance. |
| 5 | B | Context isolation / handoffs | A — bigger window. Tempting because it sounds like a capacity problem. |
| 6 | D | Plan validation | B — silently drop the step. Looks pragmatic; hides failure. |
| 7 | B | Human approval gates | A — gate everything. Sounds safe; causes approval fatigue. |
| 8 | C | MCP vs A2A | A — MCP for both. Reasonable for a simple partner API, but wrong for a partner *agent*. |

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: agents`** — running `pytest` from the repository root without the
  folder's `conftest.py`, or copying files elsewhere. Run from `labs/engineering/c6/` or keep
  `conftest.py` alongside.
- **`FakeLLM ran out of scripted responses`** — their change makes more model calls than the
  test scripted. This is a *feature*: the test caught an unexpected extra call. Have them count
  calls per path.
- **Parallel stretch tests flaky** — `FakeLLM` returns replies in call order, which is
  non-deterministic under threads. Key the fake's replies on the system prompt instead.
- **Plan parsing fails on real models** — prose around the JSON, trailing commas, or single
  quotes. The parser tolerates fences and surrounding prose, not invalid JSON; suggest a repair
  retry that feeds the `PlanError` back to the model, or the provider's JSON mode.
- **Reviewer says "Approved." or "**APPROVED**"** — the check strips leading `*#>` and
  whitespace but is case-sensitive. Lab Step 4 asks them to decide and test; there is no single
  right answer, only a tested one.
- **Missing environment variables** — Azure needs `AZURE_API_BASE` and `AZURE_API_VERSION`
  as well as the key; `MODEL` must include the provider prefix (`azure/…`).
- **Dependency outputs not reaching steps** — learners who rewrite `run_plan` sometimes iterate
  over `steps` in listed order rather than topological order. The ordering test catches it.

## Follow-up

This class carries the most new material in the course. **Schedule an optional follow-up lab
or office hours (60–90 min) within the week**, focused on the stretch challenges (router,
parallel execution, human gate with a JSON checkpoint) and on porting the pipeline to LangGraph
using the snippet in Section 8. Learners who complete the port arrive at Class 7 (evals and
tracing) with a much richer system to measure.
