# Engineering Class 7 · Evals, Observability and Reliability — Instructor Guide

**Learner page:** [Class 7 · Evals, Observability and Reliability](../engineering/c7.md) ·
**Lab folder:** `labs/engineering/c7/` · **Quiz:** `quizzes/engineering/c7.yml`

The message of this class is that **you cannot improve what you cannot measure**, and that
measurement itself can be wrong. Learners arrive from Class 6 with a pipeline that looks good in
demos. They should leave able to say how good it is, with numbers, where it fails, and how they
would notice if it got worse. The live demo is the centre of the class: an eval that gives 50% to
a system that does nothing at all.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 6 (budgets, handoff contracts, 0.95¹⁰). Bridge: "Your pipeline ran. Was the SitRep right? How do you know?" |
| 0:10–0:25 | Concept I: why evals, error analysis, golden sets | Sections 1–2. District nurse analogy; draw the improvement loop; show one golden-set line and the "every bug becomes a test" idea. |
| 0:25–0:50 | Concept II: metrics and judges | Section 3. Build the "choosing checks" table with the room. Work the calibration table on the board: 80% agreement, kappa ≈ 0.57, and why the false-pass cell matters. |
| 0:50–1:05 | Concept III: trajectories, CI, online evaluation, observability, reliability | Sections 4–8 at speed. Put the sample trace on screen and ask "where did the time go? where did the money go?" Then the circuit breaker's three states. |
| 1:05–1:25 | Live demo | See the script below: the "copy the input" system that scores 50%. |
| 1:25–1:35 | Break | |
| 1:35–2:35 | Lab (pairs) | Steps 1–5. Step 5 (one measured improvement) is the required output; pairs without a key do Steps 1–4 and the Prompt Lab. |
| 2:35–2:45 | Share results | Two or three pairs report their before and after numbers, cost, and any newly failing case. |
| 2:45–2:57 | Check Your Understanding | Discuss the most-missed question (usually Q4 or Q6). |
| 2:57–3:00 | Exit ticket | |

## Live-demo script (20 min)

**Goal:** show that an eval can be fooled, that checks measure only what they check, and that
case-by-case comparison exposes what averages hide.

1. **Tests with no key (3 min).** In `labs/engineering/c7/`, run `pytest -q` (21 passes). Read
   three test names aloud: "a crash is a failed case", "an unparseable judge is a failed check,
   not a pass", "a regression is detected even when the overall score improves". "These are the
   rules of an honest eval."

2. **The deliberate failure: a system that does nothing (6 min).** In a Python shell:

    ```python
    from evals import DEFAULT_CHECKS, HEADINGS, CheckResult, load_dataset, run_eval, compare
    data = load_dataset("sitrep_golden.jsonl")
    echo = lambda text: "\n".join(HEADINGS) + "\n" + text    # headings + the input, copied
    r = run_eval(echo, data, label="echo")
    print(r.summary())
    ```

    Output starts `== echo: 10/20 cases passed (50%)`, with `no_invented_numbers` at 100% and
    `must_include` at 94%. Pause and ask: "We have not written a single SitRep. Why does our eval
    give us 50%?" Draw out the answer: every check we wrote tests a *necessary* condition (the
    figures are there, nothing is invented, the headings exist), and copying the input satisfies
    all of them. The checks never ask whether this *is a summary*.

3. **Read the failures (3 min).** Point at what the echo system *did* fail: the injected
   "under control" line (g12), the patient's name (g14), "corrupt" (g17). The adversarial cases
   are the ones doing the real work. "This is why a golden set without adversarial cases is
   decoration."

4. **The fix (5 min).** Add a cheap check for the property we forgot, and compare:

    ```python
    def check_not_a_copy(case, output):
        if case.expected.get("out_of_scope"):
            return None
        long_lines = [l for l in case.input.splitlines() if len(l) > 60]
        copied = [l for l in long_lines if l in output]
        return CheckResult("not_a_copy", not copied, f"{len(copied)} line(s) copied verbatim")

    r2 = run_eval(echo, data, DEFAULT_CHECKS + [check_not_a_copy], label="echo+copycheck")
    print(r2.summary().splitlines()[0])      # 0/20
    print(compare(r, r2).summary())          # REGRESSION ... newly failing [...]
    ```

    Two lessons: the fix was one small rule, and the judge (Section 3.4) exists precisely for the
    qualities, "is this a good summary?", that rules keep missing. Then note that `compare()`
    calls this a regression. Here that is *correct* behaviour of a stricter eval, and a reminder
    that when you change the eval, you must re-baseline.

5. **Traces (3 min).** Wrap `FakeLLM` or a real model with `traced_llm`, run three cases, and
   print `tracer.tree()` and `tracer.totals()`. Ask: "Which number would you put on a dashboard
   first?"

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "I tried it on a few examples; it works." | Outputs vary and failures are silent. Show the improvement loop; a vibe check is one sample. |
| "More test cases is always better." | Twenty cases you have read beat 2,000 unreviewed synthetic ones. Grow the set from real failures. |
| "The LLM judge is objective." | It has verbosity, position and self-preference biases, and it needs calibration against people. Show the kappa arithmetic. |
| "80% agreement means the judge is good." | Not if 80% of outputs pass anyway. Chance-corrected agreement, and the false-pass cell. |
| "If the average goes up, ship it." | Compare case by case. The demo's `compare()` output and Q6. |
| "Evals are a pre-launch activity." | Online signals, sampled judging and new cases from production failures keep the eval honest after launch. |
| "Log everything, just in case." | Never secrets; minimise personal data; traces need classification and retention like any data. |
| "Retries make it reliable." | Against an outage, retries make things worse. Circuit breakers and visible degradation. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | C | The improvement loop | A, "try three more". It feels like diligence but is still a vibe check. |
| 2 | A | Golden-set composition | C, 2,000 synthetic cases. "Statistical power" sounds rigorous. |
| 3 | D | Code checks before judges | A, an LLM judge. Learners reach for the fashionable tool before the cheap, exact one. |
| 4 | B | Judge calibration and chance agreement | A, "85% is high". Base rates are counter-intuitive; do the arithmetic. |
| 5 | C | Trajectory evals | D, a latency dashboard. It would show slowness but not the forbidden attempt. |
| 6 | A | Case-by-case regression detection | B, "ship, the average went up". The central trap of the class. |
| 7 | D | What not to log | C, tool results. Some learners worry about volume; the real rule is about secrets and personal data. |
| 8 | B | Circuit breaker and graceful degradation | C, more retries. Intuitive and exactly wrong during an outage. |

## Discussion prompts

- Which quality of a SitRep would you *never* delegate to an LLM judge, even a well-calibrated
  one? Who should check it instead?
- Your golden set is built from real field reports. Who may see it? Where may it be stored? What
  happens when a report in it is later reclassified?
- A partner asks for your "accuracy percentage". What would you tell them, and what would you
  refuse to summarise in one number?
- You have 20 SitReps a day. Is an A/B test realistic? What would you do instead?

## Lab facilitation: bugs learners commonly hit

- **`ModuleNotFoundError: evals`**: running `pytest` from the repository root without the lab's
  `conftest.py`. Run from `labs/engineering/c7/` or pass the folder path.
- **`DatasetError ... invalid JSON`** after editing `sitrep_golden.jsonl`: JSONL is one object per
  line. A pretty-printed, multi-line object breaks it, and so do trailing commas. The error gives
  the line number.
- **New check never runs**: it returns `None` because the case lacks the `expected` key it looks
  for. Check the per-check counts in `summary()`: "0/0" means not applicable, not passing.
- **`no_invented_numbers` fails on good outputs**: a real model writes "SitRep #1", "5 headings"
  or a computed total. Decide deliberately: add to `allowed_numbers` for that case, or tighten the
  prompt. Don't delete the check.
- **Judge always fails with "judge error"**: the judge model wraps JSON in prose *and* adds a
  second JSON object, or uses single quotes. Print the raw reply; tighten the prompt or use the
  provider's JSON mode.
- **Costs higher than expected**: with `JUDGE_MODEL` set, each run makes 80 calls. Remind pairs to
  run the judge on a subset while iterating (`dataset[:5]`).
- **Scores change between identical runs**: non-determinism. Run twice and compare before
  claiming an improvement smaller than the run-to-run noise.
