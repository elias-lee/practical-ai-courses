# Engineering Class 2 · Prompting and Structured Outputs — Instructor Guide

**Learner page:** [Class 2 · Prompting and Structured Outputs](../engineering/c2.md) ·
**Lab folder:** `labs/engineering/c2/` · **Quiz:** `quizzes/engineering/c2.yml`

Many learners arrive thinking of prompting as a chat skill. The shift this class makes is from
*"write a good prompt"* to *"build a contract, and a harness that enforces it"*. Keep the
prompt-writing half (Sections 2–4) brisk, since the Literacy course covers the basics, and
spend your time on schemas, validation and the retry loop (Sections 5–7). The lab is the class.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 1: who owns arithmetic, does temperature 0 make output deterministic, what should happen when 5 samples disagree. Show one good exit-ticket decomposition and circle its "extract facts" step: "today we build this." |
| 0:10–0:35 | Concept I: prompts for systems | Sections 1–4. The SOP analogy; system vs user; delimiters; the lab's system prompt read aloud rule by rule ("which failure is each rule for?"). Few-shot leakage and reasoning patterns briefly. |
| 0:35–0:55 | Live demo | See the script below: naive `json.loads` fails, the validator catches an invented date, the retry loop fixes it. |
| 0:55–1:20 | Concept II: structured outputs | Section 5: JSON Schema, Pydantic, schema design, the three enforcement levels and the provider table. Section 6's four design decisions. |
| 1:20–1:30 | Break | |
| 1:30–1:40 | Concept III: prompts as code | Section 7: templates, versions, the three layers of prompt tests. |
| 1:40–2:40 | Lab (pairs) | Steps 1–5. Step 4's "Try it" (source check) is the most valuable; make sure every pair attempts it. |
| 2:40–2:55 | Check Your Understanding | Discuss the most-missed question (usually Q2 or Q4). |
| 2:55–3:00 | Exit ticket | Collect answers; the best field lists make good Class 3 examples. |

## Live-demo script (20 min)

**Goal:** show that "reply in JSON" is not a contract, that a well-formed reply can still be
wrong, and that validation plus a retry with feedback fixes both.

1. **The naive version (5 min).** In a Python shell in `labs/engineering/c2/` with a key set:

    ```python
    import json, os
    from llm import litellm_llm
    llm = litellm_llm(os.environ["MODEL"])
    report = open("sample_report.md").read()
    reply = llm([{"role": "user", "content":
        "Extract district, report_date (YYYY-MM-DD), hazard and households_affected "
        "from this report as JSON.\n\n" + report}])
    print(reply)
    json.loads(reply)
    ```

2. **The deliberate failure (5 min).** Usually `json.loads` raises, because the reply is wrapped
   in a ```` ```json ```` fence or has a sentence before it. Even if it parses, point at
   `report_date`: the note says only "sent Thurs eve", so any concrete date is **invented**,
   and the schema *demanded* a date. Ask: "How many SitReps would ship with that date before
   anyone noticed?" If the live model happens to behave, use the fake for the fence:

    ```python
    from test_extractor import FakeLLM, valid_json
    fenced = "Here you go:\n```json\n" + valid_json() + "\n```"
    json.loads(fenced)        # JSONDecodeError
    ```

3. **The validator catches it (4 min).**

    ```python
    from sitrep_schema import parse_sitrep
    bad = dict(json.loads(valid_json()), report_date=None, severity="severe")
    parse_sitrep(bad)
    ```

    Read the `ValidationError` aloud. Every error has a path, and the `null` error tells the
    model what to do instead. "These messages are now part of our prompt."

4. **The fix: the real extractor (6 min).**

    ```python
    from extractor import extract_sitrep
    calls = []
    def traced(messages):
        calls.append(len(messages))
        return llm(messages)
    sitrep = extract_sitrep(traced, report)
    print(calls, sitrep.report_date, [(f.value, f.unit) for f in sitrep.affected])
    ```

    `calls` shows the number of messages per attempt (2, then 4 if a retry happened). Check
    `report_date == "not stated"` and that households and people are separate figures. Then run
    `pytest -q`: 13 passes, no key. "The loop you just watched is tested without a model."

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "Structured-output mode means I don't need validation." | Shape is not content. Show a schema-valid reply with an invented Dorra figure. |
| "If it's in the schema, it's required, so the model must fill it." | That is exactly what makes it invent. Make "not stated" legitimate. |
| "Retry means send the same thing again." | A blind retry is another sample. Show the difference in Prompt Lab Exercise 3. |
| "More retries = more reliable." | After three specific repairs, the input is the problem. Budget, then escalate. |
| "The system prompt is secret and secure." | It shapes behaviour; it is not a security boundary. Delimiters reduce injection, not eliminate it (Class 8). |
| "Few-shot examples should look like the real inputs." | Leads to example leakage. Same pattern, different content. |
| "Think step by step always helps." | Breaks parsing with standard models, and is redundant with reasoning models. Use a reasoning field or a reasoning model. |
| "Prompts are config; they don't need tests." | Two of the three test layers need no model and run in milliseconds. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | C | System vs user, delimiters | B: "one user message; models understand context". Works in demos, fails on hostile or odd inputs. |
| 2 | A | Enforcement vs validation | B: "strict mode makes validation redundant". The single most common production shortcut. |
| 3 | D | "Not stated" as a first-class value | A: "make it optional / null". Reasonable instinct; null is ambiguous and inconsistently used. |
| 4 | B | Retry with error feedback | C: "map it in code". Pragmatic for one alias; a slippery slope into silent guessing. |
| 5 | A | Few-shot leakage | D: "add more Aramu examples". Intuitive and exactly backwards. |
| 6 | C | Tolerating fences | B: "general JSON repair". Sounds robust; hides real errors. |
| 7 | B | Prompts as code, versioning | D: "pin the model". Good practice, wrong culprit. |
| 8 | D | Reasoning with structured output | A: "they can't be combined". Learners who hit the parsing error once often conclude this. |

## Discussion prompts

- "Which fields in your exit-ticket document would you store 'as written' rather than
  converted, and why?"
- "When extraction fails after three attempts, who in your team should receive the report, and
  what should they see?"
- "Is a hand-written validator ever better than Pydantic? When would you choose it?"
- "Who should be allowed to change a production prompt, and what evidence should they bring?"

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: sitrep_schema`**: running pytest outside the lab folder without its
  `conftest.py`. Run from `labs/engineering/c2/`.
- **`FakeLLM ran out of scripted responses`**: their change makes an extra call (often a retry
  that should not have happened because their new validation rule rejects the valid fixture).
  Print the validation errors from the first reply.
- **New `Figure` field breaks every test**: expected in Step 2's "Try it". The fixture `VALID`
  in the tests, the example in `sitrep_prompts.py`, the JSON Schema and the validator all need
  the field. That is the point: the contract lives in several places, which is why Pydantic
  generates the schema.
- **`KeyError` from `Template.substitute`**: a `$` in new prompt text (for example "USD $5").
  Escape it as `$$` or use `safe_substitute` knowingly.
- **Source check fails on valid replies**: whitespace, line breaks and case differ between the
  quote and the report. Normalise both (lowercase, collapse whitespace) before comparing.
- **Real model returns `null` despite the rules**: common with some models. The retry fixes it;
  if it recurs, check that the few-shot example uses "not stated" and consider a
  structured-output mode.
- **Strict schema rejected by the provider**: some modes (as of 2026) require every property in
  `required` and `additionalProperties: false` at every level, and don't support every JSON
  Schema keyword. The lab's schema is written to satisfy strict mode; learners' additions may not.
- **Anthropic or Azure differences with `response_format`**: support depends on the model and
  API version. If it errors, drop the argument: the prompt plus validator still works, which is
  exactly why the validator exists.
