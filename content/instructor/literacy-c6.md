# Instructor Guide · Literacy Class 6 · Checking AI

**Learner page:** [Class 6 · Checking AI](../literacy/c6.md)

**Big idea to land:** *fluent is not the same as true.* The AI produces plausible answers; the
learner decides whether they are correct, and is accountable for what goes out. Keep returning
to the "fast assistant who sometimes invents things in the same calm voice" analogy.

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine; zoom to 125–150%.
- Have the fictional field note **with the follow-up** (from the Prompt Lab) open in a text
  file, ready to paste.
- Have a library catalogue or scholarly search engine open in another tab for the citation demo.
- Print or display the traffic-light table; you'll use it for the closing discussion.
- Rehearse the demo once. Outputs vary; don't promise specific wording.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 5 (SitRep workflow, translation checks, summarizing) | End with: "Last time we produced a SitRep. Today: would you sign it?" |
| 0:10–0:25 | Concept: why checking is your job | The assistant analogy; accountability; where errors cluster | Ask: "Who has seen an AI answer that was confidently wrong?" Collect two stories. |
| 0:25–0:40 | Concept: the fact-checking routine and hallucinated citations | Sections 2–3 | Put the five-step routine on a flipchart and leave it up all session. |
| 0:40–1:00 | **Live demo** | Script below, with a deliberate failure | |
| 1:00–1:15 | Concept: bias, automation bias, self-checks | Sections 4–6 | Use the "who got the credit?" example; it lands better than abstract definitions. |
| 1:15–1:25 | Break | | |
| 1:25–2:25 | **Prompt Lab** (pairs) | Exercises 1–4 (~13 min each); Exercise 5 as stretch or homework | Circulate. Collect one invented figure, one fake citation and one bias example. |
| 2:25–2:45 | Check Your Understanding + discussion | Learners answer; discuss most-missed | Usually Q4 (self-check) or Q7 (rubber stamp). |
| 2:45–2:52 | Traffic lights and human in the loop | Sections 7–8 | Ask each table to classify two tasks from their own jobs. |
| 2:52–3:00 | Exit ticket + close | Preview Class 7 | "Today the AI drafts and we check. Next time it starts *doing* things." |

## Live-demo script (20 minutes)

Think aloud. Learners should copy your checking habit, not your prompts.

**Step 1: A confident SitRep (4 min).** In a fresh chat, paste the field note (without the
follow-up) and this prompt:

```text
Write a one-page situation report for the country director. Include the
total number of people displaced, the number of disease cases, and the
expected date of the next delivery.
```

Read it aloud. Ask the room: *"Would you send this?"* Most will say it looks good.

**Step 2: Run the routine live (6 min).** Mark every number, date and name on screen (highlight
or bold). Ask a volunteer to search the note for each one with Ctrl+F. Typical finds: a "total
people displaced" figure that isn't in the note (households multiplied by an assumed family
size, or 600 presented as the total), "04/05" turned into a definite date, "approx" dropped,
Dorra silently missing. Tally them on the flipchart.

**Step 3: The deliberate failure: trusting the self-check (4 min).** Type:

```text
Is everything in your report accurate and supported by the notes?
```

The model will very often reply that the report is accurate, or fix only one issue. Point at the
flipchart tally: *"We found four problems. It found (none / one)."* This is the moment:
**asking the AI "are you sure?" is not verification.**

!!! tip "If the self-check catches everything"
    Occasionally it does. Praise it, then show it isn't reliable: ask *"Quote the exact sentence
    in the notes that gives the total number of people displaced."* Models often produce a
    "quote" that isn't in the note. Have a volunteer search for it. Either way, you have your point.

**Step 4: The fix (3 min).** Replace the vague self-check with a specific, evidence-based one,
and then verify its output:

```text
For every number, date and name in your report, quote the exact words in
the notes that support it. If there are none, write "NOT IN NOTE". Then
rewrite the report using only supported figures, with "not stated" for
anything missing and a "Gaps and unknowns" section.
```

Check two of its "quotes" against the note live. Make the point: **specific self-checks help;
human tracing is still the final step.**

**Step 5: A citation in 3 minutes (3 min).** Ask for "two published studies on disease after
flooding, with full references". Pick one and search for the exact title in the catalogue. If
it doesn't exist, say so calmly: this is normal. If it exists, open it and check whether it
supports the claim. Frequently it's real but says something different.

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "If it's detailed and specific, it must be real." | In human writing, detail signals research | Show a fabricated citation with page numbers. Detail is what AI generates most easily. |
| "It told me it was confident, so it's right." | We read confidence as a signal in people | The confidence statement is generated text, not a measurement. Check the claim, not the tone. |
| "If I ask it to check itself, that's verification." | It *does* often catch errors | Step 3 of the demo. Same model, same blind spots, and it can invent supporting quotes. |
| "Tools with web search don't hallucinate." | Links look like proof | Search reduces invented references, but summaries of real pages can still be wrong. Click through. |
| "Bias means offensive content." | Public stories about offensive outputs | Most bias is quiet: who gets credit, who's missing, which language gets a worse summary. Use the Exercise 3 example. |
| "A human reviewer makes it safe." | "Human in the loop" sounds reassuring | Only if they have time, sources, expertise and authority to say no. Otherwise it's a rubber stamp. |
| "AI is either safe or unsafe to use." | Wanting a single rule | The traffic-light rule depends on the task and the data. The same task can move from green to red when personal data is added. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Households became people | **B** (units and qualifier lost) | A (helpful conversion) | Converting looks like the AI doing extra work. But the assumption is hidden and the estimate becomes a "fact". |
| 2 | Perfect-looking reference | **D** (resolve it yourself) | B (ask the AI if it's real) | It feels like asking the source. The model will often confirm its own invention. |
| 3 | Stopped checking after six weeks | **A** (automation bias) | B (sensible efficiency) | Efficiency is a real value. But hallucinations are unpredictable and past accuracy doesn't protect the next answer. |
| 4 | "All figures are supported" | **C** (first pass only) | A (verified, send it) | The AI's statement sounds like a verification. It's the same model with the same blind spots. |
| 5 | Women's group lost the credit | **B** (correct the output bias) | A (broadly right, accept) | No single sentence is false. Bias often lives in emphasis and omission, not errors. |
| 6 | Which task is red | **D** (eligibility decisions) | B (SitRep) | SitReps feel high-stakes. They are amber: fine with the checking routine and a named checker. Decisions about named people are red. |
| 7 | Real check vs rubber stamp | **C** (reviewer with sources and authority) | B (AI reviews again) | It sounds like a second layer. It's a self-check, not human review. |

## Discussion prompts

1. Where in your team's work does a figure travel furthest from its source? How many hands
   does a number pass through before a donor reads it, and who checks it at each step?
2. Have you ever been the rubber stamp, approving something you didn't really check? What
   would have made it a real check?
3. In Exercise 3, was the bias in the AI or in the field note? Can AI make bias that's already
   in our reporting worse?
4. Which tasks in your job are clearly red? Are there any where colleagues are already using AI
   anyway? What would you say to them?
5. For material in local languages, who in your office could check an AI translation? What
   happens if nobody can?

## Lab facilitation tips

- **Two roles in each pair.** The driver prompts; the reviewer's only job is to say "show me
  where that comes from". Swap every exercise. This builds the habit better than any slide.
- **Exercise 1:** make sure pairs use the prompt *without* a "not stated" rule, so there are
  errors to find. If the AI behaves perfectly, ask them to add "Give one headline number for
  total displaced people."
- **Exercise 2:** learners need a real search tool outside the AI. If your network blocks
  scholarly search, use the organization's library portal or a general search engine with the
  exact title in quotation marks.
- **Exercise 3:** the follow-up paragraph matters. Check that pairs pasted it. The swap test
  (women's group vs youth group) works best when both chats are visible side by side.
- **Exercise 4:** ask pairs to count "caught by me", "caught by AI" and "caught by both". Collect
  the numbers on the flipchart; the pattern is usually instructive.
- **Exercise 5:** learners should describe tasks in general terms. If anyone starts pasting real
  case files or names, stop them kindly and point to the red row.
- **Struggling pairs:** give them the five-step routine as a checklist and have them do Step 1
  (mark the claims) with a pen on a printout.
- **Fast pairs:** ask them to write a "checking instruction" for a reviewer of the SitRep: three
  specific things to confirm, and what to do if one fails.
- **Collect for the debrief:** one invented figure, one fake or misquoted citation, one bias
  example, and the Exercise 4 tally.
