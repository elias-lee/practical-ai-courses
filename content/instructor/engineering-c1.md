# Engineering Class 1 · Foundations: Thinking and Models — Instructor Guide

**Learner page:** [Class 1 · Foundations: Thinking and Models](../engineering/c1.md) ·
**Lab folder:** `labs/engineering/c1/` · **Quiz:** `quizzes/engineering/c1.yml`

This class sets two habits the rest of the course relies on: decomposing a task into AI, code
and human steps, and treating model output as variable and unverified. The model internals
(Sections 3–8) are broad; teach them as *engineering consequences*, not as machine-learning
theory. If time is short, compress Section 2 (AI family) and Section 6 (internals) to the
sidebars and protect Sections 1, 3 and 9.

**Before class:** check that learners completed the [pre-work](../engineering/prework.md).
Expect 10–20% of learners to arrive without a working key. Pair them with someone whose key
works; every test in the lab runs without one.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up | No previous class, so use three pre-work questions instead: "What does `FakeLLM` let you do?", "Where does your key live?", "What were your token count and latency?" Collect latency numbers on the board. |
| 0:10–0:35 | Concept I: computational thinking | Section 1. Tell the duty-officer story, then build the SitRep decomposition *with the room* on the board before showing the page's table. Land the slogan: AI proposes, code checks, humans decide. |
| 0:35–0:55 | Concept II: tokens, prediction, sampling | Sections 3–4. Run `python tokens.py` live for the six-language table. Show the next-token probability table and explain temperature with it. |
| 0:55–1:10 | Live demo | See the script below: a model asked to do arithmetic, then the fix. |
| 1:10–1:25 | Concept III: context, internals, training, model types | Sections 5–8 at speed: one engineering consequence per idea. Use the model-selection table as the summary. |
| 1:25–1:35 | Break | |
| 1:35–1:45 | Concept IV: non-determinism | Section 9. Run Prompt Lab Exercise 2 as a whole-room poll: everyone sends the prompt once and calls out their number. |
| 1:45–2:40 | Lab (pairs) | Steps 1–5. Stretch challenges for fast pairs. |
| 2:40–2:55 | Check Your Understanding | Discuss the most-missed question (usually Q3 or Q7). |
| 2:55–3:00 | Exit ticket | Collect answers. Keep three good decompositions for the Class 2 warm-up. |

## Live-demo script (15 min)

**Goal:** show that a model asked to do arithmetic across messy reports gets it wrong in a
plausible way, then fix it by decomposing: the model extracts, code adds, a human resolves.

1. **Setup (2 min).** In a Python shell in `labs/engineering/c1/`, with a key set:

    ```python
    import os
    from llm import litellm_llm
    llm = litellm_llm(os.environ["MODEL"], temperature=0)
    reports = open("sample_reports.md").read()
    ```

2. **The deliberate failure: one big prompt (5 min).**

    ```python
    print(llm([{"role": "user", "content":
        "From these reports, give the total number of households affected. "
        "Reply with one number.\n\n" + reports}]))
    ```

    Typical answers are 2,650 (1,200 + 1,450 added, although the areas overlap), 2,710 (60
    *families* added to households) or 1,450. Any single number is wrong, because the reports
    overlap and use different units. Ask the room: "Which step of our decomposition did this
    one prompt skip?" (Extraction with units, code arithmetic, and the human conflict step.)
    If the model happens to answer carefully, run it three more times, or at temperature 1.
    Variation between runs makes the same point.

3. **The fix: decompose (6 min).**

    ```python
    import json
    facts = llm([{"role": "user", "content":
        "List every figure of affected people, households or families in these reports as a "
        "JSON list of objects with keys report, area, value, unit. Copy values as written; "
        "do not add anything up. JSON only.\n\n" + reports}])
    facts = json.loads(facts.strip().strip("`").removeprefix("json"))
    by_unit = {}
    for f in facts:
        by_unit.setdefault(f["unit"], []).append(f)
    for unit, items in by_unit.items():
        print(unit, [(i["report"], i["area"], i["value"]) for i in items])
    ```

    Now the conflict is *visible*: two household figures covering overlapping areas, one
    figure in families and one in people. Point out that the code refuses to add across units,
    and the overlap goes to a human. If the JSON parse fails, don't hide it: "that is exactly
    the problem Class 2 solves."

4. **Close (2 min).** Map the demo to the slogan on the board: the model *proposed* the facts,
   code *checked and grouped* them, a human *decides* the figure.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "The model looks facts up." | There is no database, only weights. Show Prompt Lab Exercise 3: confident answers past the cutoff. |
| "Tokens are words." | Run `approx_tokenize("Aramu 1,450")` and the six-language table. Numbers and rare names split. |
| "Temperature 0 means deterministic, so we don't need tests." | It reduces variation, doesn't eliminate it, and doesn't make answers correct. Point to Section 9's table. |
| "A bigger context window means I don't need to choose what to send." | Cost per call, latency, and the lost-in-the-middle effect. Preview Class 4. |
| "Use the biggest model everywhere to be safe." | Cost and latency multiply across pipeline steps; small models plus validation often match. Ask "what failure would the big model fix?" |
| "More AI steps means a smarter system." | Most of a good decomposition is code. Every AI step needs a check after it. |
| "Open-weight means free and safe." | Weights are free; running, securing and updating them is not. Data control is the real benefit. |
| "The model will say when it doesn't know." | Preference training rewards confident answers. Make "not stated" an accepted output and check sources in code. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | B | AI / code / human split | A: "it already read the reports". Feels efficient; ignores that models are poor at arithmetic. |
| 2 | D | Tokens across languages | C: "translate to English first". Sounds thrifty; it adds a call and risks meaning. |
| 3 | A | Temperature and non-determinism | B: "temperature 0 is deterministic". Nearly true in theory, dangerous in design. |
| 4 | C | Context window | A: "if it fits, it's used". The most common long-context assumption. |
| 5 | B | Knowledge cutoff, hallucination | C: "it would say if it didn't know". Trained helpfulness makes this false. |
| 6 | A | Small vs large, model choice | B: "largest reasoning model for safety". Ignores cost at volume. |
| 7 | D | Self-consistency, escalation | B: "pick the majority". Learners miss that 40% is not a majority, and that disagreement is information. |
| 8 | C | Next-token prediction, "not stated" | D: "tell it not to hallucinate". Prompts help; only checks guarantee. |

## Discussion prompts

- "Which step in your own team's reporting process would you *never* give to a model? Is that
  because of accuracy, accountability or data sensitivity?"
- "Our decomposition gives the model four of eleven steps. Would you give it more or fewer?
  What would change your mind?"
- "If Arabic reports cost 40% more tokens than English, is it fair to charge offices by usage?
  What would you tell a budget holder?"
- "A partner asks you to guarantee the SitRep pipeline gives the same output every time. What
  can you honestly promise instead?"

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: tokens` (or `llm`)**: running pytest from the repository root
  without the lab's `conftest.py`, or copying files elsewhere. Run from `labs/engineering/c1/`.
- **"My decomposition passes but looks wrong"**: the validator enforces minimum rules only.
  That is intentional. Push pairs to defend their choices against the reference, not just to
  get a clean run.
- **`checked_by` names an earlier step**: learners often write `extract` checked by `collect`.
  The error message ("must come after the AI step") is the teaching point: a check has to see
  the output.
- **Everything assigned to "human"**: passes the rules but is not a system. Ask what it would
  cost at 40 reports a day.
- **`tiktoken` install fails behind a proxy**: it downloads encoding files on first use. It is
  optional; the approximate tokenizer covers the lab.
- **Variance experiment returns identical answers at temperature 0**: that is a valid result.
  Ask them to run at 1.0, or to change the question so it is more ambiguous, and discuss why
  temperature 0 agreement still doesn't mean correct.
- **Reasoning model rejects `temperature`**: some reasoning models only accept default
  sampling (as of 2026). Remove the argument, or use a standard model for the experiment.
- **Rate limits during `variance.py`**: 20 calls in quick succession can hit low trial quotas.
  Reduce `n` or add a short `time.sleep` between samples.
