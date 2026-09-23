# Instructor Guide · Literacy Class 1 · What AI Is

**Learner page:** [Class 1 · What AI Is](../literacy/c1.md)

**Big idea to land:** *"AI" is a family of very different things, and generative AI is strong at
transforming material you give it but weak at supplying facts from memory. Fluent is not the
same as true.* The second big idea is the three-way question for any task: **AI, a normal
program or a human?** Everything else in the course builds on these two.

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine and check the screen is readable
  from the back of the room (zoom to 125–150%).
- Check that every learner has access to the approved tool before the lab. This is the first
  class, so expect a few login problems. Have a support contact ready, or plan for learners
  without access to pair with someone who has it.
- Have the fictional field report (from the Prompt Lab) open in a text file, ready to paste.
- Find out whether your tool has web search switched on. The demo works either way, but you
  need to know which you're showing.
- Draw the four nested circles (AI ⊃ ML ⊃ deep learning ⊃ generative AI) on a flipchart before
  learners arrive.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:15 | Welcome and introductions | Course format, the SitRep Assistant case study, data rules | Ask each person: "One way you've used AI, or one worry you have about it." Note the worries; you'll return to them in the hype section. |
| 0:15–0:25 | Warm-up poll (no previous class) | Three quick hands-up questions: Is a spam filter AI? Does the chatbot look things up on the internet? Can it be wrong while sounding sure? | Don't give answers yet. "We'll find out today." |
| 0:25–0:45 | Concept: the family tree; rules vs learning | Nested circles; the urgent-note example | Ask learners to place things they use (spell-check, translation, Copilot) on the flipchart circles. |
| 0:45–1:05 | **Live demo** | Script below, including a deliberate failure | The key moment is the invented SitRep. |
| 1:05–1:20 | Concept: timeline, good/bad at, hype vs reality | Sections 3–5, briskly | Return to the worries from the introductions and sort them into "real" and "hype". |
| 1:20–1:30 | Break | | |
| 1:30–1:45 | Concept: computational thinking | Section 6: the SitRep broken into steps, AI / program / human | Build the table live with the room before showing the page version. |
| 1:45–2:35 | **Prompt Lab** (pairs) | Exercises 1–4 (~10–12 min each), Exercise 5 as a stretch or homework | Circulate. Collect one invented "fact" from Exercise 3 for the debrief. |
| 2:35–2:50 | Check Your Understanding + discussion | Learners answer on the page; discuss the most-missed question | Usually Q1 (family tree) or Q6 (spreadsheet vs AI). Use the rationale table below. |
| 2:50–3:00 | Exit ticket + close | Exit ticket prompt; preview Class 2 | "Today: what AI is. Next time: how the chatbot actually produces its answers, and why it makes things up." |

## Live-demo script (20 minutes)

Narrate what you are doing and *why*. Learners copy your habit of asking "How do we know that's
true?"

**Step 1: A strength (4 min).** Paste the field report with:

```text
Summarize the field note below in five bullet points for a country
director. Use only information in the note.
```

Let the room admire it. Then read one bullet aloud and ask someone to find it in the note. It
should be there. Point out: **we supplied the material and it transformed it.** That's the sweet
spot.

**Step 2: The deliberate failure (6 min).** Open a **new chat** and type, with no notes:

```text
Write a short situation report on the current floods in Aramu district,
Northern Veloria, including the number of people affected and the
organizations responding.
```

It will very likely produce a professional-looking report with figures, organization names and
perhaps dates. Ask the room: *"Is this good?"* Let them say yes. Then reveal: **Veloria is
fictional. Every specific figure and name in this report was invented.** Pause on this; it's
the most important moment of the class.

Ask: *"If this were a real district, how would you tell the invented numbers from real ones?"*
(Answer: you can't, just by reading. They look identical.)

!!! tip "If the failure doesn't happen"
    Some tools will say they have no information about Aramu, especially with search switched
    on. Praise the tool, then push: *"I understand. Please write an illustrative example
    anyway, as realistic as possible, with specific figures."* Then ask the room what would
    happen if someone copied that "example" into a real report. Either way, you have your
    teaching point: without a source, specifics are made up.

**Step 3: The fix (4 min).** Go back to the first chat (the one with the notes) and ask:

```text
List every figure in your summary and quote the exact words in the
field note it came from. If a figure is not in the note, say so.
```

Show that grounding in a source, plus a request to point back to it, makes checking easy. **The
fix was to give it the material and ask it to show where each fact came from.**

**Step 4: A weak spot that isn't about facts (3 min).** In the same chat:

```text
Add up every number that appears in the field note.
```

Check the answer on a calculator or phone in front of the room. It may be right or wrong; either
way ask, *"Would you trust this in a report without checking? What's the better tool for this
step?"* (A spreadsheet.) This sets up the computational thinking section.

**Step 5: Bridge (3 min).** Ask: *"So which parts of writing a SitRep should AI do?"* Take three
answers and move straight into Section 6.

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "AI, machine learning and ChatGPT are the same thing." | Media use "AI" to mean chatbots | Use the nested circles. Ask for an example of AI that isn't a chatbot (spam filter, satellite mapping). |
| "AI follows rules someone programmed." | That's how most software works | Contrast the urgent-note example: rules written by a person vs patterns learned from examples. Nobody wrote the model's rules, so nobody can read them. |
| "AI is objective because it's a machine." | Computers feel neutral | Models learn from human-made data, gaps and biases included. The district example in the urgent-note box shows how. Class 6 goes deeper. |
| "If it's well written, it's probably right." | We judge human writing that way | The invented SitRep in the demo. Fluency and accuracy are unrelated in a chat tool. |
| "It looks everything up online." | Search engines; some tools do have search | Only if search is switched on in your tool. Show what your tool does, and note that search results can also be misread. |
| "AI is new; it appeared with ChatGPT." | ChatGPT was many people's first contact | The timeline: 70 years of research, several hype cycles and "AI winters". |
| "AI will do the whole job." | Vendor marketing; enthusiastic news | The SitRep table: AI speeds up two or three steps; programs and people do the rest. |
| "Computational thinking means coding." | The word "computational" | It's planning: break it down, notice patterns, keep what matters, write clear steps. Learners already do it when they write procedures. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Family tree | **B** (nested; most AI not generative) | C (ML is newest and contains the others) | ML sounds technical and advanced. But it is the older, wider group; generative AI is the newer, narrower part. |
| 2 | Learned bias | **D** (learned from under-rated examples) | A (someone wrote a rule) | Learners think of all software as rules. Machine learning has no hand-written rules; patterns, including biased ones, come from the examples. |
| 3 | Why progress sped up | **A** (data, chips, better designs) | C (ChatGPT invented AI) | ChatGPT was the public's first sight of AI. It built on decades of work. |
| 4 | Best SitRep task for AI | **C** (restructure pasted notes) | B (exact addition) | Computers are "good at maths", so people assume chat tools are too. A chat tool isn't a calculator; a spreadsheet is. |
| 5 | Vendor claim of 100% accuracy | **B** (ask the four questions) | D (accept if demo looks professional) | A polished demo is persuasive. But fluency says nothing about accuracy on your data. |
| 6 | Adding up households | **D** (normal program + human check) | A (generative AI, most advanced) | "Use the newest tool" feels modern. The best worker for exact arithmetic is a spreadsheet. |
| 7 | SitRep with no notes | **A** (details invented) | B (it found the information online) | People assume tools search the web. Without search, and with a fictional place, it can only invent. |

## Discussion prompts

Use one or two in the quiz discussion or the lab debrief.

1. Think of a system in your office that everyone calls "AI". Where does it sit on the family
   tree? What would go wrong if it made a mistake, and who would notice?
2. The rules approach missed "people drinking from the river"; the learning approach learned a
   bias. Which failure would worry you more in your work, and why?
3. What is one claim about AI you've heard at work that you now think is hype? One you now think
   is real?
4. In the SitRep table, which step would you be *most* reluctant to hand to AI? Why?
5. If AI makes drafting much faster, where should the time saved go?

## Lab facilitation tips

- **Pairs, one keyboard.** One partner types, the other reads critically and asks "How do we know
  that's true?" aloud. Swap every exercise.
- **Access problems.** In the first class, some learners won't have working access. Pair them
  with someone who does, and make sure they type for at least one exercise.
- **Exercise 1:** models are sometimes wrong about their own features (for example, whether they
  can search). If a pair finds this, share it with the room; it's a good early lesson.
- **Exercise 2:** item 6 (voice to text) is genuinely borderline. Let pairs argue; there's no
  single right answer. The point is to use the vocabulary.
- **Exercise 3:** Request B is the key one. Collect any invented Veloria figures for the debrief.
  If the tool refuses to invent, ask the pair to push ("give your best estimate") and see what
  happens.
- **Exercise 4:** pairs often find the AI is a good sceptic. Ask why that might be (it has read a
  lot of criticism of AI claims) and whether that means it's reliable on everything.
- **Exercise 5:** remind learners to describe tasks in general terms, with no confidential
  details. If time runs short, set it as homework; it feeds into Classes 5 and 8.
- **Struggling pairs:** point them at the "good at / weak at" table and ask them to predict which
  column each request falls into before they send it.
- **Fast pairs:** ask them to repeat Exercise 3, Request B in a new chat and compare the invented
  figures. Are they the same? (Usually not, a preview of Class 2.)
- **Collect examples** for the debrief: one convincing invented fact, one good sceptical
  question from Exercise 4, and one interesting AI / program / human table from Exercise 5.
