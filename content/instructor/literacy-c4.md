# Instructor Guide · Literacy Class 4 · Giving AI the Right Information

**Learner page:** [Class 4 · Giving AI the Right Information](../literacy/c4.md)

**Big idea to land:** *the model only knows what it can see.* If the facts aren't on the desk, it
answers from memory, and memory is old, generic and sometimes invented. Keep returning to two
images: the **analyst's desk** (the context window) and the **open-book exam** (RAG).

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine and zoom to 125–150%.
- Have Doc A and Doc B from the Prompt Lab open in a text file, ready to paste.
- Find out what your tool actually offers (as of 2026 this varies a lot): file upload limits,
  whether projects or knowledge bases are enabled, whether web search is on by default, and what
  the documentation says about the model's knowledge cutoff. Learners will ask.
- If your tool has a project feature, create a demo project in advance holding Doc A, Doc B and
  two or three unrelated fictional documents (for example a travel policy and a workshop agenda),
  so you can show retrieval picking sources.
- Rehearse the demo once. Answers vary; don't promise exact wording.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 3 (context block, few-shot, iterating) | Link forward: "Context was the block people leave out most. Today is all about context." |
| 0:10–0:20 | Concept: the desk | Section 1, the two sources of knowledge | Ask: "What does the AI know about our office?" Collect answers, then show that it knows nothing you haven't given it. |
| 0:20–0:40 | Concept: context window, three methods, RAG | Sections 2–4; the pipeline table | Draw the desk on a flipchart. Add sticky notes as "documents" until they fall off. Then draw the open-book exam. |
| 0:40–1:00 | **Live demo** | Script below, including a deliberate failure | The grounding moment is the core of the class. Don't rush it. |
| 1:00–1:10 | Concept: cutoff, messy context, languages | Sections 6–8, briskly | Use the "colleague back from a year at a remote post" image for the cutoff. |
| 1:10–1:20 | Break | | |
| 1:20–2:20 | **Prompt Lab** (pairs) | Exercises 1–3 (~15 min each), then 4 or 5 by choice | Everyone must do Exercise 2. Collect the most convincing invented answer. |
| 2:20–2:40 | Check Your Understanding + discussion | Learners answer on the page | Most-missed is usually Q4 (RAG doesn't read everything) or Q6 (the conflict). |
| 2:40–2:50 | Lab debrief | Show the invented answers from Exercise 2 without the rule | Ask: "Would you have caught this in a real SitRep?" |
| 2:50–3:00 | Exit ticket + close | Preview Class 5 | "Now you can brief it and feed it. Next time: using it for real work." |

## Live-demo script (20 minutes)

**Step 1: The empty desk (3 min).** In a fresh chat with no documents, type:

```text
How many households are displaced in Aramu district, and when does
water trucking to Lomi start?
```

The model will either invent specific figures or give a generic "I don't have information about
this" answer. Either way, ask the room: *"What was on the desk?"* Answer: nothing but the
question. Point out that any specific figure is invented.

**Step 2: Paste the documents, but don't ground (4 min).** Paste Doc A and Doc B and ask
exactly this, with **no rules**:

```text
Based on these documents, how many households are displaced in Aramu
district and Dorra combined, and which agency leads the health
response?
```

**The deliberate failure:** neither document gives a Dorra figure or a health lead. The AI will
very often produce a combined total (an estimate for Dorra added on, or one of the two district
figures presented as "the" figure) and name VRC as health lead because VRC appears in both
documents. It may also silently choose 1,450 or 1,150, or average them.

Stop and ask someone to find the answer in the documents. They can't. Make the point: **having
the documents on the desk isn't enough. Without a rule, the model blends the desk with guessing.**

!!! tip "If the failure doesn't happen"
    If the model correctly says the documents don't contain it, praise it, then push: *"I need a
    single combined number for the headline, just give me your best figure."* Pressure for a neat
    answer usually produces a guess. You can also demonstrate the conflict alone: *"One number for
    displaced households, please."*

**Step 3: The fix (5 min).** In a **new chat**, paste the grounded prompt from Section 5 of the
learner page, with both documents and the same question. Show:

- "Not found in the documents provided" for Dorra and the health lead.
- Both displacement figures shown with sources and the conflict flagged.
- Citations in square brackets. Ask a learner to check one quote against the source aloud.

Say: **the fix was three rules: only these documents, an exact "not found" phrase, and a conflict
rule.**

**Step 4: Retrieval in a project (5 min, if your tool supports it).** In your demo project, ask a
specific question ("When is the next coordination meeting?") and show the source link to Doc B.
Then ask a whole-collection question ("Summarize everything in this project") and show that the
answer leans on a few documents. Connect this to the open-book exam: it only reads the pages it
flips to.

**Step 5: The cutoff (3 min).** Ask "What is your knowledge cutoff?" and compare the answer with
your tool's documentation. Then ask about something that changed recently in your field. If web
search is available, toggle it and show the difference in sources.

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "The AI can see our shared drive / my inbox." | Integrated tools in office software; marketing | It sees only what you give it or what the tool is set up and permitted to search. Ask learners what *their* tool is connected to; many don't know. |
| "A bigger context window means I can dump everything in." | Headline numbers ("a million tokens!") | Show the messy-context table. More material means more distraction, lost-in-the-middle and conflicting versions. Curate. |
| "If I upload a file, the AI reads all of it." | It feels like handing over a document | Long files may be truncated or searched in parts. Demo asking about a detail near the end of a long document. |
| "With RAG the AI can't make things up." | "Grounded" sounds like "guaranteed" | RAG reduces invention a lot but doesn't eliminate it: wrong chunks, misattributed citations, filling gaps. Check citations. |
| "A citation means the claim is correct." | Academic habit: citations signal rigour | Citations are claims too. Show a case where the cited passage says something slightly different. Ask for word-for-word quotes. |
| "The AI knows today's news." | Web search in consumer tools | Training stops at a cutoff. Search can add recent information, but only if it's on and used, and results need checking. |
| "The AI will tell me if it doesn't know." | Human conversational norms | Models often answer confidently from out-of-date or missing knowledge. You have to give them permission, and a phrase, to say "not found". |
| "Translation is the only language issue." | Thinking of language as output only | Cross-language retrieval can miss documents, names get transliterated differently, and official terms get paraphrased. Ask for original-language quotes. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Figure with no documents | **B** (invented from memory) | C (from the internet) | People assume AI "looks things up". Without search on and sources shown, it didn't, and internal figures aren't online anyway. |
| 2 | Early instruction forgotten | **D** (crowded context) | A (AI overriding you) | It *feels* deliberate. It's a context effect: older instructions get dropped, compressed or diluted. |
| 3 | Pasting the same material weekly | **A** (project) | C (upload five years of reports) | "More examples must help." But old material distracts and dates the format. Curate a small current set. |
| 4 | Thin summary of 400 documents | **C** (only a few chunks retrieved) | A (read all, chose to be brief) | People picture the AI reading everything. Retrieval brings back a handful of passages; the rest never reaches the desk. |
| 5 | Dorra not in documents | **B** ("not found" + relevant fact) | C (1,150 with a citation) | A citation looks rigorous. But it's attached to the wrong claim: that figure isn't about Dorra. |
| 6 | Two conflicting figures | **D** (show both, flag, note agreement) | A (average) | Averaging feels fair and neutral. It creates a number neither source contains and hides the disagreement. |
| 7 | Current guidelines from memory | **A** (knowledge cutoff) | C ("it would say I don't know") | Human norms: a confident colleague usually knows. Models are often confident when wrong or out of date. |

## Discussion prompts

1. Which documents does your team re-explain to new colleagues every time? Would they make a good
   project or knowledge base? Who would keep it up to date?
2. In Exercise 3, Doc B says partners *agreed* to use the district figure. Should the AI decide
   which figure goes in the headline, or only lay out the options? Who owns that judgment?
3. Is "Not found in the documents provided" a useful answer to a country director? How would you
   turn it into a useful gap in a SitRep?
4. Your office works in French and English. What could go wrong if the AI searched only English
   documents? How would you notice?
5. When is it fine to rely on the model's general knowledge without giving it documents? When is
   it never fine?

## Lab facilitation tips

- **Pairs, one keyboard.** One types, the other checks every claim against Doc A and Doc B aloud:
  "Where does it say that?"
- **Exercise 2 is non-negotiable.** Everyone should see an ungrounded answer invent something.
  Make sure pairs use a **new chat** for the no-rules version, or the earlier rules will still be
  in context.
- **Exercise 3:** the averaging (1,300) is the prize find. If a pair gets it, show the room.
  Ask them to write the conflict rule into their prompt template from Class 3.
- **Exercise 4:** learners need a real, fast-moving topic for question 2. Have two ready (a recent
  change in a well-known global framework or funding mechanism in your field). Stress that this is
  the one exercise using real-world topics, and still no internal or sensitive data.
- **Exercise 5:** pair a learner who reads French, Spanish, Arabic, Chinese or Russian with one who
  doesn't. The reader judges quality; the other checks the numbers and names against the English
  source.
- **Struggling pairs:** give them the three rules on a card: *only these documents; exact "not
  found" phrase; show conflicts.*
- **Fast pairs:** ask them to add a third fictional document that is irrelevant (e.g. a workshop
  agenda) and a duplicate of Doc A with one figure changed, then see whether answers get worse.
- **Collect for the debrief:** the most convincing invented answer from Exercise 2, and the best
  honest headline wording from Exercise 3.
