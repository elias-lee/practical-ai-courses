# Instructor Guide · Literacy Class 3 · Prompting Well

**Learner page:** [Class 3 · Prompting Well](../literacy/c3.md)

**Big idea to land:** *the AI can only use what you give it.* Prompting is briefing, a skill
learners already have from writing terms of reference and briefing consultants. Keep coming back
to the "smart new colleague on day one" analogy.

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine and check the screen is readable
  from the back of the room (zoom to 125–150%).
- Have the fictional field report (from the Prompt Lab) open in a text file, ready to paste.
- Open two browser tabs or chats side by side for the weak vs strong comparison.
- Answers vary from run to run. Rehearse the demo once, but don't promise learners the exact
  wording they'll see.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 2 (tokens, prediction, why chatbots make things up) | Link the last one forward: "If it predicts from what it's given, what we give it matters." |
| 0:10–0:20 | Concept: why prompts matter | Day-one colleague analogy; the one-sentence version | Ask: "What do you tell a new consultant on day one?" Write answers on a flipchart. You'll map them to the six blocks next. |
| 0:20–0:40 | Concept: anatomy of a prompt | The six blocks, the table, weak vs strong | Map the flipchart answers onto the six blocks. Nearly every group reinvents them. |
| 0:40–1:00 | **Live demo** | Script below, including a deliberate failure | Keep the pace brisk; learners will practise all of it in the lab. |
| 1:00–1:10 | Concept: iterating, few-shot, step by step | Sections 3–5, quickly, pointing at the snippets | Keep it short; the lab exercises teach these better than slides. |
| 1:10–1:20 | Break | | |
| 1:20–2:20 | **Prompt Lab** (pairs) | Exercises 1–4 (~12 min each), Exercise 5 as a stretch or homework | Circulate. Collect 2–3 good or surprising outputs to show in the debrief. |
| 2:20–2:40 | Check Your Understanding + discussion | Learners answer on the page; discuss the most-missed question | Usually Q2 (context) or Q3 (memory). Use the rationale table below. |
| 2:40–2:50 | Lab debrief | Show the collected examples; common mistakes table | Ask pairs which building block made the biggest difference. |
| 2:50–3:00 | Exit ticket + close | Exit ticket prompt; preview Class 4 | "Today: how to ask. Next time: what information to give it." |

## Live-demo script (20 minutes)

Narrate what you are doing and *why*, and think aloud. Learners copy the habit, not the prompt.

**Step 1: The vague prompt (3 min).** In a fresh chat, type:

```text
Write a sitrep about the floods in Veloria.
```

Ask the room: *"Is this good?"* Let them notice that it looks professional. Then ask: *"Where did
these numbers come from?"* Point at any specific figure, agency or date. Veloria is fictional,
so every specific detail is invented. That's the key moment: **fluent is not the same as
true**.

**Step 2: The deliberate failure (5 min).** Now paste the field report with a half-improved
prompt that has a task and format but **no constraint about missing information**:

```text
Turn these field notes into a SitRep with headings: Affected population /
Needs / Response. Include the total number of displaced people.

[paste field report]
```

The report gives *households* (1,200) and only one partial *people* figure (~600 at the school).
The community hall count is missing. The AI will very often produce a confident "total displaced
people" figure, for example by multiplying households by an assumed family size, or state "600
people" as if it were the total. It may also turn "04/05" into a definite date.

Stop and ask: *"Is that number in the notes?"* Have someone search the report for it. Make the
point: **we asked for a number that doesn't exist, so it made one up to please us.** Part of
the problem was our prompt.

!!! tip "If the failure doesn't happen"
    Sometimes the model behaves well and flags the gap. Praise it, then show it's not
    guaranteed: open a new chat and ask *"Just give me one number for total displaced people for
    the headline."* Pressure for a single neat number usually produces a guess. Either way,
    you've got your teaching point.

**Step 3: The fix (5 min).** Continue in the same chat (this is also a demo of iteration):

```text
The notes do not give a total number of people. Redo the SitRep:
- Use only figures that appear in the notes, with their units
  (households vs people).
- Where a figure is missing, write "not stated".
- Add a heading "Gaps and unknowns" listing what we still need to find
  out, including any ambiguous dates.
```

Point out the improvement: "not stated" for the community hall, Dorra listed as a gap, "04/05"
flagged. Then say: **the fix was one sentence of constraint.** It's also worth adding to every
reporting template.

**Step 4: Few-shot in 60 seconds (3 min).** Paste the donor-update prompt from Section 4 of the
learner page. Show that the output copies the pattern of the examples (people first, then
significance) without any instruction to do so.

**Step 5: "Interview me" (4 min).** Paste Exercise 4's prompt and answer two of the AI's
questions live, asking the room to supply plausible answers. Stop after two questions. Learners
will complete it themselves in the lab.

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "Being polite gets better answers." | We're polite to people; social media tips | Politeness is fine but it isn't a technique. Show two prompts that differ only by "please". The results are indistinguishable. Content is what changes answers. |
| "Longer prompts are always better." | The strong prompt is longer than the weak one | The strong prompt wins because each sentence adds information. Show a padded prompt where the key instruction is buried in the middle and gets ignored. Aim for *complete*, not *long*. |
| "The AI remembers my previous chats." | Tools that feel like a person; some tools *do* have memory features | Explain that the AI sees the current conversation, plus any memory or project feature your tool offers and that has been switched on. Demo: new chat, ask "what did I tell you yesterday?" |
| "Capital letters and '!!!' make it obey." | Frustration when instructions are ignored | Ignored instructions are usually unclear, contradictory or buried. Move the instruction to the end, state it plainly and give the reason. |
| "'You are an expert' makes it an expert." | Popular "magic prompt" lists | Role sets tone and vocabulary, not knowledge. It can't know your floods however expert it is told to be. |
| "If the first answer is bad, AI can't do this." | Vending-machine expectations | Show iteration in the demo. The second or third message is often where the value is. |
| "The enterprise tool is safe for anything." | "Enterprise" sounds like "approved for everything" | Each tool is approved for particular data classifications. Point to the data rules; Class 8 goes deeper. |
| "Step-by-step reasoning means the answer is correct." | Tidy explanations look authoritative | The steps make errors easier to find; they don't prevent them. Read the working and check the key numbers. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Generic report with invented figures | **B** (no context) | A (tool is broken) | People blame the tool when output disappoints. But the tool answered the question it was given; the brief was empty. |
| 2 | Most-omitted building block | **C** (context) | A (role) | "You are an expert…" is the most widely shared prompting tip, so people think it matters most. It adds tone, not facts. |
| 3 | New chat, "the usual summary" | **A** (starts from zero) | B (AI learns from each chat) | Chat tools feel like a person who remembers you, and some tools have memory features. By default, a new chat has no knowledge of earlier ones. |
| 4 | Wrong tone in donor updates | **D** (few-shot examples) | A (longer tone description) | "More detail is better" feels right. But tone is easier to show than describe, and long descriptions bury instructions. |
| 5 | Totalling overlapping figures | **B** (spell out the steps) | D ("be 100% accurate") | It feels like asking for accuracy should help. The AI can't be accurate on command; it needs a method. |
| 6 | 70%-right first draft | **C** (specific changes) | B ("That's wrong, try again") | It's quick and natural. But without saying *what* is wrong, the AI may change the good parts and keep the bad. |
| 7 | Performance review with personal data | **A** (check approval, anonymise) | C ("Keep this confidential") | It sounds responsible. But a prompt instruction can't control how the tool stores or logs data. |

## Discussion prompts

Use one or two in the quiz discussion or the lab debrief.

1. Think of the best briefing you ever received from a manager. Which of the six building
   blocks did it contain? Which did it leave out?
2. In Exercise 1, the weak prompt still produced *something*. When is a "good enough" generic
   answer actually fine, and when is it dangerous?
3. The AI says "not stated" for a missing figure. Is that more or less useful to a country
   director than a reasonable estimate? Who should make the estimate, and how should it be
   labelled?
4. If your whole team used the same SitRep template, what would you gain? What might you lose?
5. What's one task in your job where you would *not* use a prompt template, and why?

## Lab facilitation tips

- **Pairs, one keyboard.** One partner types, the other reads the output critically. Swap every
  exercise. The reader should ask "Is that in the notes?" aloud.
- **Keep the report fictional.** If someone wants to paste their own real field report, redirect
  them to Exercise 5 and remind them of the data rules. Real sensitive data should never be used
  in class.
- **Exercise 1:** make sure pairs use a **new chat** for the strong prompt. Otherwise the AI
  already has the report and the comparison is unfair.
- **Exercise 2:** the most common error is the AI mixing *households* and *people*. If a pair
  spots it, ask them to show the room. It's a real-world reporting error, not just an AI one.
- **Exercise 3:** fast pairs should rerun the task without examples and compare. This is the
  clearest demonstration of few-shot prompting.
- **Exercise 4:** the partner answering questions can invent plausible fictional details
  (budget, donor, deadline). Tell them to keep answers short; the point is the questions, not
  the answers.
- **Exercise 5:** if time runs short, set it as homework and ask learners to bring their
  finished template to Class 4. Some groups like to start the next class by sharing one.
- **Struggling pairs:** point them at the common mistakes table. Ask: "Which block is missing
  from your prompt?"
- **Fast pairs:** ask them to make the AI critique its own output against the source ("List any
  figure in your answer that is not in the notes") and see what it catches.
- **Collect examples** for the debrief: one great output, one instructive failure and one
  surprising question from Exercise 4.
