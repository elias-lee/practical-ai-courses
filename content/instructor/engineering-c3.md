# Engineering Class 3 · Building with Code and AI Pair Programming — Instructor Guide

**Learner page:** [Class 3 · Building with Code and AI Pair Programming](../engineering/c3.md) ·
**Lab folder:** `labs/engineering/c3/` · **Quiz:** `quizzes/engineering/c3.yml`

This class has two halves that learners often treat as separate topics: *calling models from
code robustly* and *working with AI coding agents*. Keep tying them together: the retry code is
the example of what a spec and tests look like, and the coding agent is the way learners extend
it. Before class, check that every learner can use an **approved** coding assistant, and have a
fallback (pairs share one machine) for anyone who can't.

## Timing plan (~3 hours)

| Time | Block | What to do |
|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 2 (system prompts, JSON schemas, validation). Bridge: "Your prompt returns valid JSON in a notebook. What else has to be true before colleagues can rely on it?" |
| 0:10–0:30 | Concept I: calling models from code | Sections 1–5. Show the messages list and a raw response; land "the API is stateless". Walk `call_with_retry` line by line; do the cost worked example on the board. |
| 0:30–0:50 | Concept II: working with coding agents | Sections 6–10. The spec-first loop, guard the contract, the review checklist. Have the room review the seven-finding `call_model` snippet *before* revealing the notes. |
| 0:50–1:10 | Live demo | See the script below: tests with fakes, the coding agent implementing R9, and a deliberate failure. |
| 1:10–1:20 | Break | |
| 1:20–2:30 | Lab (pairs) | Steps 1–6. Steps 4–5 (agent plus review) are the heart of it; protect that time. |
| 2:30–2:45 | Check Your Understanding | Discuss the most-missed question (usually Q3 or Q4). |
| 2:45–2:55 | Debrief | Two pairs show their R9 diffs and review findings. Which pair's agent tried to touch the tests? |
| 2:55–3:00 | Exit ticket | Collect answers; they seed Class 7's discussion of what to evaluate. |

## Live-demo script (20 min)

**Goal:** show that failure handling is testable without a network, then show a coding agent
working spec-first, including the moment it cheats and how you catch it.

1. **Tests with no key (3 min).** In `labs/engineering/c3/`, with no key set, run `pytest -q`:
   15 passes in milliseconds. Open `test_retry_succeeds_after_transient_errors` and point at
   `sleep.delays == [1.0, 2.0]`: "We tested a three-second backoff without waiting three seconds."
2. **Stateless in one minute (2 min).** In a Python shell with a real key, send
   `[{"role": "user", "content": "My name is Amina."}]`, then a separate call with
   `"What is my name?"`. The model doesn't know. Then send both turns in one list. Say "the
   conversation lives in *your* code."
3. **Spec-first with the agent (6 min).** Add R9 (length check) to `SPEC.md` live, then give the
   Exercise 1 prompt to your coding agent. Narrate what it does: which files it reads, whether
   it shows failing tests first. Run `pytest -q` yourself at the end.
4. **The deliberate failure: the agent weakens a test (5 min).** Prepare this in advance on a
   branch, so the demo is reliable: change `call_with_retry` so it makes one attempt *too few*
   (`if attempt >= retries - 1`), then "fix" the failing test the way agents sometimes do,
   by changing `match="4 attempts"` to `match="attempts"`, `assert len(llm.calls) == 4` to
   `assert len(llm.calls) >= 1` and `sleep.delays == [0.5, 1.0, 2.0]` to
   `len(sleep.delays) <= 3` in `test_gives_up_after_n_retries`. Check beforehand which other
   tests fail with the off-by-one (the CLI test expects "4 attempts" too) and "fix" those the
   same way. Show `pytest -q`: all green.
   Ask: "Ship it?" Then show `git diff test_app.py`. The room should spot it.
5. **The fix (4 min).** Restore the test (`git checkout test_app.py`), see it fail with the
   real reason (3 attempts instead of 4), fix the off-by-one in `app.py`, and see it pass. Add
   to the agent instructions on screen: *"Do not modify or delete any existing test. If you
   believe a test is wrong, stop and tell me why."* Point out that reviewing **test diffs first**
   is the one-line habit that catches this.

If the live agent is slow or unavailable, skip step 3 and spend the time on steps 4–5, which
need no network.

## Common misconceptions

| Misconception | How to address it |
|---|---|
| "The model remembers our conversation." | Demo step 2. The API is stateless; history is resent and paid for on every call. |
| "Retry everything; models are random anyway." | Randomness affects the text, not whether a bad key is accepted. Walk the transient/permanent table. |
| "More retries = more reliable." | Stacked retries: 4 × 4 × 4 = 64. Retries are a loop and need a budget and one owner. |
| "Tokens are tokens; cost is total × price." | Input and output are priced differently; do Q4's arithmetic on the board. |
| "If the tests pass, the code is right." | Only if nobody weakened the tests. Demo steps 4–5. |
| "The AI reviewed it, so it's reviewed." | An AI review adds to human review; it doesn't replace it. It shares blind spots with the AI that wrote the code. |
| "Deleting the commit removes a leaked key." | Git history, clones and caches keep it. Rotate. |
| "Vibe coding is always bad." | It is fine for throwaway prototypes on fictional data. The question is where the code ends up. |

## Quiz rationale

| Q | Correct | Concept | The tempting wrong answer, and why |
|---|---|---|---|
| 1 | B | Transient vs permanent errors | A: "retry everything, models are random". Conflates output randomness with request validity. |
| 2 | D | Stateless API | C: bigger window. Sounds like a capacity problem, but nothing is being sent. |
| 3 | A | Stacked retries | B: 9. Learners count retries (3) instead of attempts (4) and forget the third layer. |
| 4 | C | Input vs output pricing | A: all tokens at the input price, the most common spreadsheet mistake. |
| 5 | B | Tests as the contract | C: ask the agent to confirm. Feels diligent but is self-report, not review. |
| 6 | A | Dependencies and slopsquatting | D: ask the assistant if it's safe. The model that invented the name will vouch for it. |
| 7 | D | Vibe coding vs spec-driven | C: "only 40 lines". Size feels like the criterion; the stakes (personal data) are. |
| 8 | C | Secrets hygiene | A: remove it in a new commit. Very common belief; history keeps the key. |

## Discussion prompts

- "Where in your team's current code would a stacked-retry problem hide?" (SDK defaults are
  the usual answer.)
- "What would you put in an `AGENTS.md` for your main repository? Name three lines."
- "Who is the author of record of code an agent wrote and you merged?" Push towards: you are.
- "Your manager asks for 'a quick AI tool' by Friday. How do you decide between vibe coding and
  spec-first, and how do you explain the choice to them?"

## Lab facilitation tips

- **Pair roles.** One learner "drives" the agent; the other holds `SPEC.md` and the review
  checklist and must approve every change. Swap at Step 5.
- **Push "show me the failing test first".** Many agents skip it. If one does, have the pair
  point it out to the agent and ask it to redo the step properly. This is an important lesson.
- **Timebox Step 4 to 20 minutes.** If the agent is going in circles, the pair should stop,
  make the spec more precise (usually what counts as a "word"), and restart the agent.
- **Watch for real keys in prompts.** If a learner pastes a key into the agent or a chat, have
  them rotate it: the exercise then teaches the lesson for real.

## Common lab bugs

- **`ModuleNotFoundError: app`**: running `pytest` from elsewhere without `conftest.py`. Run
  from `labs/engineering/c3/` or keep `conftest.py` alongside.
- **Tests hang for seconds**: a learner passed `sleep=time.sleep` or removed the injectable
  sleep. The whole suite should take well under a second.
- **`FakeLLM ran out of scripted responses`**: the change makes more calls than scripted
  (often a retry on a non-transient error). The test caught an unexpected call; count them.
- **R9 word count disagreements**: `"1,200"`, `"Tamsi-Bara"` and bullet markers. There is no
  single right answer; the spec must say which, and the test must encode it.
- **Real run returns exit code 1**: `MODEL` not set, or missing the provider prefix
  (`azure/…`). Azure also needs `AZURE_API_BASE` and `AZURE_API_VERSION`.
- **Usage line shows zero tokens on a real run**: some providers or proxies don't return
  usage; the adapter only calls `on_usage` when it's present. Wrap with `tracked()` instead to
  estimate.
- **Agent adds a dependency** (`tenacity`, `backoff`, `python-dotenv`): a good discussion,
  not a disaster. The spec says no new dependencies; revert, or update the spec deliberately
  and pin it.
