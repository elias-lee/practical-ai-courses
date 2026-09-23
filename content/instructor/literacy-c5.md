# Instructor Guide · Literacy Class 5 · AI at Work

**Learner page:** [Class 5 · AI at Work](../literacy/c5.md)

**Big idea to land:** *AI speeds up the work; you still own the result.* Every task in this class
follows the same pattern: break it down, delegate the parts AI is good at, keep the judgment, and
check before anything leaves your hands. The SitRep workflow is the whole class in one exercise.

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine and zoom to 125–150%.
- Have the field note and distribution table from the Prompt Lab open in a text file.
- Print or display the "delegate vs keep" table (Section 9); you'll refer to it throughout.
- Check whether your tool has a calculation or "analysis" feature and whether it can record or
  transcribe meetings (as of 2026 this varies by tool and by organization). Know your
  organization's rules on recording meetings.
- If possible, recruit a colleague who reads French (or another language learners use) to support
  Exercise 3.
- Rehearse the SitRep demo once; it's the longest demo in the course.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 4 (the desk, grounding, knowledge cutoff) | Link forward: "You can brief it and feed it. Now let's use it for real work." |
| 0:10–0:20 | Concept: you are still the author | Section 1; the junior colleague image; break it down | Ask: "What would you never let a new junior colleague send without reading?" |
| 0:20–0:40 | Concept: the six tasks | Sections 2–7, one or two minutes each, pointing at the prompts | Focus on "what goes wrong" for each; the prompts are for the lab. |
| 0:40–1:00 | **Live demo** | SitRep workflow, script below, with a deliberate failure | This is the class's centrepiece. |
| 1:00–1:10 | Concept: delegate vs keep | Section 9 table and the "how bad if wrong?" test | Ask the room to add one task from their job to the table. |
| 1:10–1:20 | Break | | |
| 1:20–2:20 | **Prompt Lab** (pairs) | Exercises 1–4 (~10 min each), then Exercise 5 (~20 min) | Everyone should reach Exercise 5. Let fast pairs skip ahead. |
| 2:20–2:40 | Check Your Understanding + discussion | Learners answer on the page | Most-missed is usually Q3 (translation check) or Q5 (why the table). |
| 2:40–2:50 | Lab debrief | Pairs report: what they corrected by hand in Exercise 5, and time taken | Compare "time with AI" against "time from scratch". Both numbers matter. |
| 2:50–3:00 | Exit ticket + close | Preview Class 6 | "Today you checked informally. Next time: checking AI properly." |

## Live-demo script (20 minutes)

Narrate each step as *delegate* or *keep*. Learners should hear the decision, not only see the
prompt.

**Step 1: The shortcut (4 min).** In a fresh chat, paste the field note and ask:

```text
Write a SitRep from these notes for the country director.
```

**The deliberate failure:** this one-shot approach typically produces a polished SitRep with at
least one of these problems: "1,200 households" stated as fact, a total number of *people*
calculated from households, "04/05" turned into a definite date, the uncounted community hall
disappearing, or a "Response" section that adds activities not in the note.

Ask the room to hunt for problems for two minutes, with the note beside the draft. Count the
problems on a flipchart. Make the point: **it looks finished, which is exactly why errors
survive.**

!!! tip "If the failure doesn't happen"
    If the draft is clean, ask it to make the SitRep "more compelling for donors" in the same chat.
    Pressure towards persuasion usually strengthens claims ("urgent crisis affecting thousands")
    and drops hedges. Either way you have a failure to fix.

**Step 2: Extract (4 min).** In a **new chat**, run the step 2 prompt from Section 8. Show the
table. Point at the "Count, estimate or second-hand?" column: the uncertainty that the shortcut
hid is now visible.

**Step 3: Check (4 min).** Invite a volunteer to check three rows against the note aloud. Make at
least one correction in the chat, even a small one (e.g. confirm "04/05" means 4 May). Say:
**this is the human step, and it's fast because the table is short and structured.**

**Step 4: Draft and self-review (5 min).** Run the draft prompt, then the self-review prompt.
Compare the result with the shortcut version from Step 1: the labels ("estimate", "not stated")
survive, and the self-review lists anything that drifted.

**Step 5: Sign-off (3 min).** Read the final draft aloud as the country director. Ask the room:
*"Would you send this? What would you change by hand?"* Make one human edit live. End on:
**same tool, same notes; the difference was breaking the task down and keeping the checks.**

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "If it reads well, it's right." | Fluent writing usually signals a careful writer | Step 1 of the demo. Polished prose hides errors; the table makes them visible. |
| "AI saves time on everything." | Marketing; early impressive demos | Time saved on drafting can be lost on checking. Compare total time in the debrief. The biggest gains are on drafting, restructuring and first-pass summaries. |
| "Computers can't get arithmetic wrong." | Calculators and spreadsheets | A chat model predicts text; a number can be predicted, not calculated. Use Exercise 4's calculator check. |
| "A good translation reads smoothly." | Fluency is what we notice | Smooth translations can shift numbers, conditions and official terms. Show a back-translation. |
| "Summaries are neutral." | Summaries feel like compression, not editing | Every summary chooses what to drop. Caveats and minority views go first. Exercise 2 makes this visible. |
| "Asking the AI to check itself is enough." | The self-review step works well in the demo | Self-review catches a lot, but it can miss things or be wrong. It supports human review; it doesn't replace it. |
| "If it's in the enterprise tool, I can use it for any task." | "Approved tool" sounds like "approved use" | Approval covers kinds of data, not kinds of decisions. Decisions about people stay in the "keep" column. |
| "Using AI for my work is cheating." | Uncertainty about norms | Using AI is a tool choice, like a spell-checker or a template, provided you follow your organization's policy, check the result and take responsibility. Transparency norms vary; follow local guidance. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Missing date in donor email | **C** (placeholders) | B (estimate a realistic date) | "Realistic" sounds responsible. It is still an invented date that can become a commitment. |
| 2 | Estimates became facts in summary | **A** (uncertainty lost) | B (simplifying is fine) | Shortening is the point of summaries, so losses feel acceptable. But changing an estimate to a fact changes the meaning. |
| 3 | Smooth French translation | **D** (check key items + independent comparison) | B (ask the same chat) | It's quick. But the same chat tends to confirm its own work. An independent check is more reliable. |
| 4 | Kits per household figures | **B** (check totals, recalculate one) | A (computers are good at arithmetic) | Deep-seated trust in computers. A chat model can predict a number instead of calculating it. |
| 5 | Why draft from the checked table | **C** (human-verified facts; drift visible) | B (fewer tokens) | Learners from Class 4 know tokens matter. Here the reason is checkability, not cost. |
| 6 | Conflicting figures | **A** (keep the decision) | C (listing figures) | Listing sounds like "deciding". But extracting is checkable; choosing between sources is a judgment. |
| 7 | Eligibility decisions | **D** (keep with people) | C (use AI, spot-check) | Spot-checking works for low-stakes tasks, so it sounds balanced. High stakes and personal data put this in "keep". |

## Discussion prompts

1. Which task in your job takes the most time but needs the least judgment? Is it a good
   candidate for AI? What would you check?
2. In Exercise 5, how long did the full workflow take compared with writing a SitRep from
   scratch? Would it be faster next time, with a saved project?
3. Should colleagues say when a document was drafted with AI? When does it matter, and to whom?
4. The "delegate vs keep" table puts "decisions about people" in "keep". Can you think of a small,
   safe part of such a task that AI could help with?
5. What would a team-wide prompt library look like for your office? Who would maintain it?

## Lab facilitation tips

- **Pairs, one keyboard, clear roles.** One partner operates the AI, the other plays the
  accountable reviewer. Swap after Exercise 3. In Exercise 5 the reviewer does steps 3 and 6.
- **Exercise 1:** the placeholders are the point. If a pair's draft has no placeholders, ask them
  where the reallocation amount came from.
- **Exercise 2:** encourage pairs to write down the losses *before* running the audit prompt, then
  compare with what the AI found. Humans and AI often catch different things.
- **Exercise 3:** if no one in a pair reads French, let them swap to Spanish or another
  language they know, adjusting the fixed terms. The back-check in a new chat still works for
  numbers and names without reading the language well.
- **Exercise 4:** hand out calculators or tell learners to use their phone. The Dorra row is the
  key test; celebrate pairs who spot the AI treating "not visited" as zero.
- **Exercise 5:** protect the time; it's the capstone of the class. If a pair falls behind,
  let them skip Exercises 3 and 4 and come back to them as homework.
- **Keep it fictional.** Learners will be tempted to try their own real reports. Redirect them to
  the exit ticket and remind them of the data rules.
- **Collect for the debrief:** the most interesting correction made in step 3 of Exercise 5, and
  each pair's time estimate (with AI vs from scratch).
