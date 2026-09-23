# Instructor Guide · Literacy Class 2 · How Chatbots Work

**Learner page:** [Class 2 · How Chatbots Work](../literacy/c2.md)

**Big idea to land:** *a chatbot predicts plausible text, one token at a time, from what is in
front of it.* Almost every behaviour learners will meet (making things up, varying between runs,
forgetting old chats, stumbling over letters) follows from that one sentence. Keep bringing
surprises back to it: "What would a next-word predictor do here?"

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine and check the screen is readable
  from the back of the room (zoom to 125–150%).
- Know your tool: does it have search switched on, a memory feature, a reasoning or "thinking"
  mode, file or image upload? Learners will ask.
- Optional but effective: open a public **tokenizer** web page from a model provider in a browser
  tab (several providers publish one) to show how a sentence splits into tokens in English,
  French and Arabic. Use only the fictional sentence from Exercise 5. Check your organization
  allows the site; if not, skip it and use the illustration in Section 10.
- Prepare a flipchart with the sentence *"After the floods, the most urgent need in Lomi village
  is clean…"* for the opening game.
- Answers vary from run to run. Rehearse the demo, but don't promise exact wording.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 1 (family tree, fluent vs true, AI / program / human) | Link the "fluent vs true" question forward: "Today we find out *why*." |
| 0:10–0:20 | Opening game: be the model | Room predicts the next word on the flipchart; tally the answers | The tally *is* a probability table. Say so: "You just did what the model does." |
| 0:20–0:45 | Concept: prediction, tokens, training, attention, context window | Sections 1–5 | Use the desk analogy for the context window. Keep the transformer to two minutes. |
| 0:45–1:05 | **Live demo** | Script below, including a deliberate failure | The variation and hallucination moments are the ones people remember. |
| 1:05–1:20 | Concept: hallucination, variation, model types, languages | Sections 6–10 | Ask the room which languages they work in; connect to Section 10. |
| 1:20–1:30 | Break | | |
| 1:30–2:30 | **Prompt Lab** (pairs) | Exercises 1–5 (~11 min each); Exercise 3 can run longer | Exercise 3 ("break the model") is the heart of the lab. Protect time for it. |
| 2:30–2:45 | Check Your Understanding + discussion | Learners answer on the page; discuss the most-missed question | Usually Q3 (variation) or Q7 (open vs closed). Use the rationale table below. |
| 2:45–2:55 | Lab debrief: best "breaks" | Each pair shares their best failure and explains it with a concept from today | Write the explanations up: tokens, no fact check, context, randomness. |
| 2:55–3:00 | Exit ticket + close | Exit ticket prompt; preview Class 3 | "Now you know it predicts from what you give it. Next time: how to give it the right instructions." |

## Live-demo script (20 minutes)

Narrate what you're doing and *why*. The goal is for learners to be able to predict the tool's
behaviour from how it works.

**Step 1: Prediction made visible (3 min).** Type:

```text
Continue this sentence with the next five words only:
"After the floods, the most urgent need in Lomi village is"
```

Compare with the flipchart tally from the opening game. Usually "clean water" wins in both. Say:
*"It doesn't know anything about Lomi. It knows what usually follows sentences like this."*

**Step 2: Variation (4 min).** Open **three new chats** side by side (or one after another) and
send the same prompt in each:

```text
Write a one-sentence headline for a situation report about floods in
Aramu district, where 1,200 households are displaced.
```

Read them aloud. Ask: *"Which one is the real answer?"* There isn't one. Explain the weighted
dice and temperature.

**Step 3: The deliberate failure (6 min).** In a new chat:

```text
Give me three published reports on the 2025 Tula river floods in
Northern Veloria, with authors, titles, publishers and dates.
```

It will often produce convincing references: realistic titles, plausible agency names, even
report numbers. Ask the room: *"Would you put these in a briefing note?"* Then reveal the whole
place is fictional. **These references were predicted, not found.** Connect it to the five
causes in Section 6: plausible not true, no fact check, training rewarded answering.

!!! tip "If the failure doesn't happen"
    Many tools now say they can't find such reports, especially with search on. Praise the tool,
    then follow up in the same chat: *"Understood. Just give me your best guess at what such
    reports would be called and who would publish them."* Then ask the room: "What happens if
    a busy colleague copies this list into a document?" Or try the false-assumption question:
    *"Why did the Veloria Relief Coalition close its Aramu office in 2021?"* Models often
    explain events that never happened.

**Step 4: The fix (4 min).** New chat. Paste the field report from Class 1 and ask:

```text
Using only the field note below, what are the main needs in Lomi and
Tavet? For each need, quote the sentence from the note that supports
it. If the note doesn't say, write "not stated".

[paste field report]
```

Show that with the source on its "desk" and an instruction to quote it, the answer is grounded
and easy to check. **The fix is to give it the text and ask it to point to it**, which is the
theme of Classes 3 and 4.

**Step 5: The desk (3 min).** In the same chat, ask: *"What did I ask you in my other chat a
few minutes ago?"* It can't know. Say: *"Each chat is a separate desk."*

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "It looks up answers in a database." | Search engines; how we expect computers to work | Demo Step 3. A database can't return a report that doesn't exist; a predictor can write one. |
| "It learns from my conversations." | It adapts within a chat, so it feels like learning | Training happens before release. Corrections apply only in the current chat (unless a memory feature is on). Demo Step 5. |
| "If it gives a different answer, one of them is broken." | Computers are usually consistent | Weighted dice. Variation is built in; disagreement between runs on a fact is a warning sign worth using. |
| "Hallucinations are rare glitches that will soon be fixed." | "Glitch" framing in news | They follow from how the model works. Newer models do it less, but no model is free of it, so verification stays necessary. |
| "It's lying." | Human words for human behaviour | Lying needs knowing the truth. It produces plausible text without checking. The practical response is the same: verify. |
| "Bigger context window means it reads everything carefully." | Marketing of large context windows | Long contexts get patchy, especially in the middle. Put key instructions at the start or end, and restate them in long chats. |
| "All languages work equally well and cost the same." | The tool answers fluently in many languages | Tokens: the same text can need more tokens in some languages, and quality varies. Check important translations with a fluent speaker. |
| "Open model means the data is open to everyone." | The word "open" | "Open" refers to the model's published weights. An open-weight model run in-house can actually keep data *more* private. |
| "Reasoning models don't make mistakes." | Visible "thinking" looks rigorous | Reasoning reduces some errors, not all. A long, tidy chain of thought can still end in a wrong answer. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Core mechanism | **C** (predict next token, repeat) | A (searches a database of facts) | It's how we expect computers to work, and some tools add search. The model itself predicts. |
| 2 | Invented population figure | **A** (plausible, no fact check) | B (lying on purpose) | Human language for human behaviour. It doesn't know the truth to hide it. |
| 3 | Different answers to same prompt | **D** (randomness / temperature) | A (learned from first chat) | Feels like it "improved". But it doesn't learn from chats, and a new chat can't see the old one. |
| 4 | Correction forgotten in new chat | **B** (trained before release; correction only in that chat) | C (needs days to absorb) | Suggests learning is slow but real. Your chats don't retrain the model. |
| 5 | Instruction fades in long chat | **D** (context window / uneven attention) | C (decided it knows better) | Chatbots feel like people with opinions. The cause is mechanical. |
| 6 | Arabic costs more | **A** (more tokens per sentence) | B (surcharge for non-English) | A plausible business policy. Pricing is per token; the difference is in tokenization. |
| 7 | Keep sensitive data in-house | **C** (approved open-weight model on own servers) | D (closed model keeps data closed) | "Closed" sounds secure. It means the weights are private, not your data; closed models run on the provider's service. |

## Discussion prompts

Use one or two in the quiz discussion or the lab debrief.

1. Now that you know a chatbot predicts plausible text, which of your current uses of AI feel
   safer, and which feel riskier?
2. Is variation between answers a bug or a feature? For which of your tasks is it each?
3. A colleague says, "It gave me the same figure twice, so it must be right." What would you
   say to them?
4. Your office works in French and Arabic as well as English. What would you check before
   relying on AI output in each language?
5. If you were choosing between a large closed model and a smaller model run on your
   organization's own servers, what questions would you ask?

## Lab facilitation tips

- **Pairs, one keyboard.** One types; the other keeps a list of surprises. Swap every exercise.
- **New chats matter.** Exercises 2, 3 and 4 depend on opening new chats at the right moment. If
  a pair's results look odd, check that they did.
- **Exercise 1:** the model's list of "alternatives it considered" is itself a prediction, not a
  readout of its internals. If a learner asks, that's a great catch; say so to the room.
- **Exercise 3 is the heart of the lab.** Encourage creativity and keep it good-humoured: the
  aim is to understand failures, not to "win". Useful extra probes: a question with a false
  premise, a long list to sort alphabetically, a very specific quotation from a real public
  document, a riddle with a twist. Keep everything fictional or public; no real sensitive data.
- **Prompt 3 answer:** 48,317 × 7,926 = 382,960,542. Have a calculator handy.
- **Prompt 4:** the best answers note that Tavet may be counted twice and a total can't be
  known. Celebrate any pair whose model spotted it, and any pair that spotted it when the model
  didn't.
- **Exercise 4:** if your tool has a memory feature switched on, the new chat may "remember".
  Use that to explain the difference between the context window and a tool's memory feature.
- **Exercise 5:** the model's token estimates are usually unreliable; that's part of the lesson.
  If you have a tokenizer page open, show real counts for English, French and Arabic.
- **Struggling pairs:** give them one prompt from Exercise 3 and ask, "Before you send it, what
  do you predict will happen, and why?"
- **Fast pairs:** ask them to turn one of their "breaks" into a rule for colleagues, e.g. "Never
  ask the chatbot to recall references; ask it to extract them from a document you provide."
- **Collect examples** for the debrief: the most convincing hallucination, the most surprising
  variation, and one failure explained by tokens.
