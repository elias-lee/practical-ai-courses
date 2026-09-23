# Engineering Class 5 · Harness and Tools — Instructor Guide

**Learner page:** [Class 5 · Harness and Tools](../engineering/c5.md) ·
**Lab folder:** `labs/engineering/c5/` · **Quiz:** `quizzes/engineering/c5.yml`

This class turns the SitRep Assistant from a text generator into a system that acts. The main
idea to get across is that **the model proposes and the code disposes**: every tool call is a
request that the harness validates, permits, runs, and reports back on. Section 3 (designing
tools for agents) is the part most learners have never met. Protect time for it, even if MCP
has to be shortened.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 4 (chunking, citations, context budgets). Bridge: "Retrieval gives the model information. What would it need in order to *act*?" |
| 0:10–0:25 | Concept I: harness and function calling | Sections 1–2. Horse and harness analogy; the four-step contract; walk the native round trip; then the loop, stopping on budget, errors and "budget_exceeded". |
| 0:25–0:50 | Concept II: designing tools for agents | Section 3. Show the weak/better tables. Have pairs rewrite one bad tool description from their own work, then swap and critique. |
| 0:50–1:05 | Concept III: MCP, Skills, guardrails, permissions, retries | Sections 4–8 at speed. Put the guardrail flow diagram and the permission table on screen; ask "which of these is a control and which is a wish?" |
| 1:05–1:25 | Live demo | See the script below: a vague error causes a stuck loop; an actionable error fixes it. |
| 1:25–1:35 | Break | |
| 1:35–2:30 | Lab (pairs) | Steps 1–5; the "Try it" tasks are the core of the lab; stretch challenges for fast pairs. |
| 2:30–2:40 | Prompt Lab debrief | Exercise 2 (error recovery) results across pairs: how often did version A lead to an invented figure? |
| 2:40–2:55 | Check Your Understanding | Discuss the most-missed question (usually Q4 or Q6). |
| 2:55–3:00 | Exit ticket | Collect three tool descriptions to critique at the start of Class 6. |

## Live-demo script (20 min)

**Goal:** show that tool design, and especially the error message, changes model behaviour, and
that the harness makes this testable without a live model.

1. **Schemas from code (3 min).** In `labs/engineering/c5/`, run `pytest -q` with no API key
   (16 passes). Then:

    ```python
    import json
    from sitrep_tools import get_population
    print(json.dumps(get_population.schema, indent=2))
    ```

    Point at `"description"` and `"required"`: "The docstring is the user interface. The user is
    a model."

2. **A deterministic stand-in model (3 min).** Paste this rule-based fake. It behaves like a
   reasonable model: it asks for Tamsi first, corrects itself *if the error tells it how*, and
   answers once it has the figure.

    ```python
    import json
    import sitrep_tools
    from harness import ToolError, ToolRegistry, run_tool_loop
    from sitrep_tools import READ_ONLY_TOOLS

    def model(messages):
        last = messages[-1]["content"]
        if "84300" in last:
            return json.dumps({"final": "Tamsi is in Kessan district (pop. ~84,300, 2025 projection)."})
        if "village in Kessan" in last:
            return json.dumps({"tool": "get_population", "arguments": {"district": "Kessan"}})
        return json.dumps({"tool": "get_population", "arguments": {"district": "Tamsi"}})

    ask = [{"role": "user", "content": "What is the population around Tamsi?"}]
    ```

3. **The deliberate failure: a vague error (6 min).** Replace the helpful error with the kind of
   error most APIs return:

    ```python
    original = sitrep_tools._district
    def vague(name):
        if name.strip().lower() != "kessan":
            raise ToolError("404")
        return "Kessan"
    sitrep_tools._district = vague

    r = run_tool_loop(model, ToolRegistry(READ_ONLY_TOOLS), ask, max_steps=5)
    print(r.status, r.steps, [c.arguments for c in r.tool_calls])
    ```

    Output: `budget_exceeded 5` and five identical `{'district': 'Tamsi'}` calls. Pause. Ask:
    "What would a real model do after the third 404?" (Common answers: retry, apologise, or
    *estimate a population from memory*, which is the worst outcome for a SitRep.) Note that the
    budget turned an infinite loop into a recorded failure.

4. **The fix (4 min).** Restore the actionable message and run again:

    ```python
    sitrep_tools._district = original
    r = run_tool_loop(model, ToolRegistry(READ_ONLY_TOOLS), ask, max_steps=5)
    print(r.status, r.steps, r.answer)       # final 3 ...
    ```

    Show `r.tool_calls[0].result`: the error names the known districts and the village's district.
    "Same model, same tools. We changed one string."

5. **Blocked tool (4 min).** Run `test_disallowed_tool_is_blocked_and_never_runs` with `-v`, open
   it, and show that `OUTBOX` stays empty. Ask: "Why register the email tool at all if we block
   it?" (We shouldn't in production: least privilege. The test registers it to prove the second
   line of defence works.)

If you have a key, finish with `python run_demo.py` and read the step log aloud. The default
request asks for an email, so the `BLOCKED` step usually appears live.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "The model runs the tools." | Draw the four-step contract. The model emits JSON; your code executes it with your credentials. |
| "Tool descriptions are documentation for developers." | They are prompts for the model. The demo shows behaviour changing from one error string. |
| "Return everything; the model will pick what it needs." | Tokens cost money and attention. Paginate, search then read, and truncate visibly. |
| "A tool error should crash the run so we notice." | Log it, and return it to the model. Crashing throws away work the model could have recovered. |
| "Putting the rule in the system prompt is a guardrail." | A prompt is a wish; an allow-list in code is a control. Use both, rely on the code. |
| "MCP makes tools secure / MCP is a security risk, avoid it." | MCP is plumbing. Security comes from vetting servers, scoping credentials and least privilege. |
| "Retries make things more reliable." | Only for transient failures and idempotent operations. Retrying a non-idempotent write creates duplicates. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | B | Who executes tools | C, "MCP runs it". Learners who have used MCP clients often think the protocol executes calls. |
| 2 | D | Actionable error messages | C, "add a prompt rule". Feels like the fix, but the model still lacks the information to recover. |
| 3 | A | Pagination, search then read | B, a bigger context window. The capacity framing is intuitive; attention and cost are the real problems. |
| 4 | C | Idempotency | A, a longer timeout. It treats the symptom; timeouts will always happen sometimes. |
| 5 | B | When MCP pays off | D, "direct DB access without a harness". A misreading of what MCP connects. |
| 6 | D | Guardrails in code, least privilege | C, a bigger model. Better instruction-following lowers the rate but never to zero. |
| 7 | A | Retry classification | B, retrying the model's bad argument. Learners conflate "error" with "transient error". |
| 8 | C | Skills and progressive disclosure | A, "just a system prompt". The difference is *when* it is loaded. |

## Discussion prompts

- Think of an API your team already has. If you exposed it to an assistant endpoint by endpoint,
  what would go wrong first? What *task-shaped* tool would you design instead?
- Your assistant can read personal data about affected people (to de-duplicate beneficiary
  lists). Where would you place PII redaction, and where must you *not* redact because a human
  needs the data?
- An MCP server published by a trusted vendor updates overnight and a tool description changes.
  Who in your organisation should notice, and how?
- Which of the SitRep tools would you put behind a human approval step, and what exactly should
  the approver see?

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: harness`**: running `pytest` from the wrong folder without the lab's
  `conftest.py`. Run from `labs/engineering/c5/`, or pass the folder path.
- **`FakeLLM ran out of scripted responses`**: their change makes an extra model call (often a new
  guardrail feeding back a message and continuing). This is a test catching a behaviour change;
  count the steps.
- **Schema test fails after adding a parameter**: missing type hint (the decorator raises), or
  an `Args:` line indented with a tab or a single space, so the description is not picked up.
- **`TypeError` about `Literal`** on older Pythons: `from typing import Literal` (3.8+). The lab
  runs on 3.9 and later.
- **PII test fails after editing R2**: `search_reports` returns 240-character snippets. Contact
  details moved past the snippet are simply not returned, so there is nothing to redact.
- **Real model replies in prose or with several JSON objects**: the parser takes the first `{`
  to the last `}`. Two objects in one reply fail to parse and are fed back as an error. Point
  learners at native tool calling (stretch 1) as the production answer.
- **Azure variables**: `AZURE_API_BASE` and `AZURE_API_VERSION` are needed as well as the key;
  `MODEL` must include the `azure/` prefix.
