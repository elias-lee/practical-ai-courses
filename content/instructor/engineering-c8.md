# Engineering Class 8 · Security, Governance and Production + Capstone — Instructor Guide

**Learner page:** [Class 8 · Security, Governance and Production + Capstone](../engineering/c8.md) ·
**Lab folder:** `labs/engineering/c8/` · **Quiz:** `quizzes/engineering/c8.yml`

This class has two parts. The **3-hour session** covers security, governance and production, and
ends with the red-team lab. The **capstone** runs as a separate session (recommended: a half day
one to two weeks later) in which teams present their extensions and red-team each other.
Announce the capstone at the end of Class 6, so teams can start their extension early.

The message to leave behind is: **assume the model will be fooled sometimes, and design so that
being fooled cannot do much harm.** Learners who arrive thinking security is a better system
prompt should leave thinking in terms of trifecta legs, allow-lists and approval gates.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 7 (case-by-case comparison, judge calibration, circuit breakers). Bridge: "Your evals include an injection case. What happens if it *passes* the eval but an attacker rewords it?" |
| 0:10–0:30 | Concept I: threat model, injection, trifecta | Sections 1–3. Field-office analogy; draw the data-flow diagram with trust boundaries; read `g12` aloud; draw the trifecta and fill in the SitRep table with the room. |
| 0:30–0:50 | Concept II: OWASP and defences | Sections 4–5. Go through OWASP quickly, pointing back to earlier classes; spend the time on the eight defences, and on why keyword filters are signals, not controls. |
| 0:50–1:05 | Concept III: data, governance, production | Sections 6–8. The classification table and the GPS-coordinates example; EU AI Act tiers in two minutes; the incident-response steps and the kill switch; model deprecation. |
| 1:05–1:25 | Live demo | See the script below: a lookalike domain beats a substring allow-list. |
| 1:25–1:35 | Break | |
| 1:35–2:30 | Lab (pairs) | Steps 1–5. Step 4 (improve both numbers and write two new attacks) is where the learning happens. |
| 2:30–2:40 | Capstone briefing | Section 9: extension options, rules of engagement, rubric. Confirm team pairings for red-teaming. |
| 2:40–2:55 | Check Your Understanding | Discuss the most-missed question (usually Q2 or Q6). |
| 2:55–3:00 | Exit ticket | |

### Capstone session (half day, suggested)

| Time | Block |
|---|---|
| 0:00–0:15 | Setup; each team hands its system, threat model and README to its assigned red team |
| 0:15–1:00 | Red-teaming (45 min). Facilitators circulate and enforce the rules of engagement |
| 1:00–1:20 | Teams write findings (exact input, impact, suggested fix) and share them with the owning team |
| 1:20–1:30 | Break; owning teams triage findings |
| 1:30–3:00 | Presentations, 10 min each plus 5 min questions, scored with the rubric |
| 3:00–3:15 | Wrap-up: the most instructive finding of the day, and what each person will do differently |

## Live-demo script (20 min)

**Goal:** show that an injection defence can look right and be wrong, and that a red-team suite
catches it.

1. **The naive pipeline (4 min).** In `labs/engineering/c8/`, run `python run_red_team_demo.py`.
   The naive pipeline: 9/9 attacks succeed. Open `naive_pipeline()` and read its four lines. Ask:
   "Which line is the vulnerability?" (All of them: the report goes straight into the prompt,
   the output is trusted, and every action runs.)

2. **Explain the gullible model (3 min).** Open `gullible_llm`. "This is a pessimistic model: it
   obeys everything it reads. If our defences hold against it, they don't depend on the model's
   good behaviour." Show the defended score: 1/9 attacks succeed (`a07`), 1/4 benign reports are
   wrongly blocked (`b04`).

3. **The deliberate failure: a plausible-looking allow-list (6 min).** In a Python shell, replace
   the domain check with the version most people write first:

    ```python
    import pipeline
    from pipeline import defended_pipeline
    from redteam import gullible_llm, load_suite, run_red_team

    suite = load_suite("injection_suite.jsonl")
    proper = pipeline._domain_allowed
    pipeline._domain_allowed = lambda domain, allowed: any(a in domain for a in allowed)

    r = run_red_team(lambda rep: defended_pipeline(gullible_llm, rep), suite)
    print(r.summary().splitlines()[0])      # Attacks: 2/9 succeeded ... ['a07', 'a08']
    ```

    Show `a08`'s report: a password-reset link to `veloria-relief.example.evil.example`. Ask:
    "Who controls that domain?" (Whoever owns `evil.example`. The allowed name is just a
    subdomain label.) This is a credential-phishing link that our "allow-list" approved.

4. **The fix (3 min).** Restore the proper check and re-run:

    ```python
    pipeline._domain_allowed = proper
    r = run_red_team(lambda rep: defended_pipeline(gullible_llm, rep), suite)
    print(r.summary().splitlines()[0])      # Attacks: 1/9 succeeded ... ['a07']
    ```

    Read `_domain_allowed()`: exact match or ending with `"." + allowed`. Emphasise that the suite
    caught a bug that code review might miss. This is why the red-team suite belongs in CI next to
    the evals.

5. **The honest ending (4 min).** Show `a07` ("archive (at) evil-mail (dot) example") and `b04`
   (a legitimate partner link, blocked). "Every filter trades missed attacks against false
   alarms. The job is to measure both, not to claim zero." Hand this over as the lab's Step 4.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "A strong system prompt prevents prompt injection." | One channel for code and data; no general fix as of 2026. Q2. Design for limited damage. |
| "Injection is only a problem with malicious users." | Indirect injection: the user is innocent and the attack is in the document. Q1. |
| "Our keyword filter blocks injections." | Run `injection_flags()` over the suite: `a02` (a markdown image) and `a03` (which just says "Assistant:") are not flagged, and widening the list soon flags benign corrections like `b03` ("Please ignore the earlier figure"). Signals, not controls. |
| "No names means no sensitive data." | The GPS-coordinates example (Q6): group data can endanger people. |
| "The EU AI Act doesn't apply to us, so governance doesn't either." | Data-protection law, your organisation's own AI and data policies, and frameworks it has adopted (NIST AI RMF, ISO/IEC 42001) apply regardless; vendors and partners may fall under the Act. |
| "Our provider handles security." | The provider secures the model service. Your harness decides tools, permissions, data flows and output handling. That is where most incidents come from. |
| "We'll deal with model retirement when it happens." | Retirement notices are often short; without pinned versions and evals, a switch is an untested change. Q8. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | A | Indirect injection | D, "it came from a partner". Trust in the source is exactly what indirect injection exploits. |
| 2 | C | Prompts can't fix injection | A, "models follow system prompts reliably". Most learners' starting belief. |
| 3 | B | Lethal trifecta | D, the internal retrieval assistant. It has private data, but no external channel if rendering is off. |
| 4 | D | Allow-list implementation | A, "too strict". Learners notice subdomains before they notice lookalikes. |
| 5 | C | Secrets management | B, private repositories. A common and costly habit. |
| 6 | A | Group data and data responsibility | B, "no personal data". The personal-data framing hides group harm. |
| 7 | D | EU AI Act risk tiers | C, the drafting assistant. "AI in a humanitarian setting" sounds high risk; the test is the decision it makes about people. |
| 8 | B | Model deprecation | A, "use latest". Sounds low-maintenance; it gives up control of behaviour. |

## Discussion prompts

- Which leg of the trifecta is cheapest to break in the system you would most like to build?
  Which leg would the business owner most resist breaking, and why?
- A partner asks to plug their own MCP server into your SitRep agents. What do you need from them
  before you say yes?
- A wrong figure has gone out in a published SitRep to 40 partners. Walk through the five
  incident-response steps. Who is phoned first?
- When is a self-hosted, quantized small model the *right* choice for field work, despite
  lower quality?
- Which widely shared AI principle (fairness, transparency, human oversight, privacy,
  accountability) does your capstone extension put most under strain?

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: pipeline`**: running `pytest` from the repository root without the lab's
  `conftest.py`. Run from `labs/engineering/c8/` or pass the folder path.
- **`test_defended_pipeline_scores` fails after an improvement**: this is expected. The test
  pins the current numbers. Learners should update the assertions to their *better* numbers,
  not delete the test.
- **New attack "doesn't work" against the gullible model**: `gullible_llm` only obeys links,
  emails, `ACTION:` lines and `Say:` lines. An attack in another form needs either a `Say:` line
  or a real model (`--real`).
- **Obfuscation fix blocks benign reports**: a pattern for " at " or " dot " fires on ordinary
  English ("at the school"). Require the full pattern (word, at, word, dot, word) and re-run the
  benign cases.
- **Regex catastrophes**: learners who write very general URL patterns can make the filter slow or
  match whole paragraphs. Test with `find_exfiltration()` directly on small strings first.
- **Real-model runs vary**: a real model's resistance changes between runs. Run twice before
  comparing, as in Class 7.
- **Azure variables**: `AZURE_API_BASE` and `AZURE_API_VERSION` are needed as well as the key;
  `MODEL` must include the `azure/` prefix.
