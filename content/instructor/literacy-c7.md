# Instructor Guide · Literacy Class 7 · Agents and Automation

**Learner page:** [Class 7 · Agents and Automation](../literacy/c7.md)

**Big idea to land:** *an agent is a model in a loop, using tools, and the more it can do, the
more its mistakes matter.* The practical skill is **commissioning**: describing a system clearly
enough, with success criteria, test cases and approval points, that someone else can build it and
you can judge it. Keep returning to "asking a question vs delegating a task".

**Prepare before class:**

- Log in to the approved AI chat tool on the presenter machine; zoom to 125–150%.
- If your approved tool has an agent-style feature (deep research, web browsing, actions), test it
  beforehand and decide whether to show it. If not, the demo below works in plain chat.
- Print the one-page spec template (section 7) for each pair; learners like writing on paper
  before typing.
- Have the Class 6 field note (with follow-up) ready to paste.
- Prepare a flipchart with two columns: **Workflow** and **Agent**.

## Timing plan (~3 hours)

| Time | Block | What happens | Notes |
|---|---|---|---|
| 0:00–0:10 | Warm-up quiz | 3 questions from Class 6 (fact-checking routine, automation bias, traffic lights) | Link forward: "Last time you were the checker. What if the AI acts before you check?" |
| 0:10–0:25 | Concept: from answering to doing | Delegating analogy; the agent loop; agents learners may already use | Ask: "What would you delegate to a new assistant, and what would you never let them do alone?" |
| 0:25–0:40 | Concept: workflows vs agents; what agents do and where they fail | Sections 2–3 | Sort 4–5 room-suggested tasks onto the Workflow / Agent flipchart. |
| 0:40–1:00 | **Live demo** | Script below, with a deliberate failure | |
| 1:00–1:15 | Concept: tools, MCP, multi-agent, orchestration | Sections 4–6 | Use the coordination-cell analogy; most learners have worked in or with one. |
| 1:15–1:25 | Break | | |
| 1:25–1:35 | Concept: commissioning and the spec template | Section 7 | Walk through the template headings; spend the most time on test cases. |
| 1:35–2:35 | **Prompt Lab** (pairs) | Exercises 1–4 (~15 min each); Exercise 5 as stretch or homework | Circulate. Collect one weak success criterion and one excellent awkward test case. |
| 2:35–2:50 | Check Your Understanding + discussion | Learners answer; discuss most-missed | Usually Q2 (workflow vs agent) or Q7 (test cases). |
| 2:50–3:00 | Exit ticket + close | Preview Class 8 and the final project | "Your final project uses this spec template on a workflow from your own job. Start thinking about which one." |

## Live-demo script (20 minutes)

This demo simulates an agent in plain chat, so it works with any tool. Narrate each step as
"look, decide, act, observe".

**Step 1: Play the loop by hand (5 min).** Tell the AI:

```text
You are an agent producing a weekly SitRep. You have three tools:
READ_NOTES (returns field notes), SEARCH_PAST_REPORTS(query) and
SEND_EMAIL(to, text). At each turn, say which ONE tool you want to use
and why, then wait for me to give you the result. Begin.
```

You play the tools. When it asks for READ_NOTES, paste the field note. When it searches past
reports, invent a short plausible result ("Last week: Dorra 80 households, unconfirmed"). Point at
the screen each turn: *look, decide, act, observe*. That's the agent loop.

**Step 2: The deliberate failure (5 min).** Keep going until it has a draft. Many models will
proceed to SEND_EMAIL to the country director without being asked to wait. If it does, stop and
ask the room: *"Who approved that?"* Nobody did. We gave it a send tool and no approval rule.

!!! tip "If it doesn't send on its own"
    Some models ask first. Praise it, then add: *"Be efficient and finish the task without
    checking with me."* It will usually send. The point stands: politeness in the model isn't a
    control; a missing permission is.

**Step 3: The fix (4 min).** Start a new chat with a better design:

```text
You are an agent producing a weekly SitRep. Tools: READ_NOTES,
SEARCH_PAST_REPORTS(query), SAVE_DRAFT(text). You cannot send email.
Rules: at most 8 tool uses; if a note mentions a security incident,
stop and say "ALERT: human needed". When the draft is saved, stop and
say "Ready for human review". Use one tool per turn and wait for me.
```

Run a few turns. Show the difference: **the send tool is gone, there's a budget, a stop rule and
a hand-back.** Say: *"We didn't make the AI smarter. We designed the limits."*

**Step 4: Commission it (6 min).** Open the spec template. Ask the room to call out one line each
for Problem, Success criteria and Human approval points. Type them in. Then paste into the AI:
*"Suggest five awkward test cases for this spec."* Pick one good one and one weak one, and ask the
room to say why the weak one is weak (usually: no clear description of the correct result).

## Common misconceptions and how to address them

| Misconception | Where it comes from | How to address it |
|---|---|---|
| "Agents are a smarter kind of AI." | Marketing language | Same models; different arrangement. The loop and tools make an agent. Demo Step 1 shows this. |
| "Agents are always better than workflows." | Novelty; hype | Use the recipe vs chef analogy. For fixed-step tasks, a workflow is cheaper, more predictable and easier to test. |
| "If you tell the agent to be careful, it will be." | We rely on instructions with people | Instructions help but are not controls. Remove dangerous tools; require approval for irreversible actions. |
| "More agents means better results." | "Team" sounds good | Each hand-off can lose information and pass on errors. Use several agents only for genuinely distinct parts. |
| "Commissioning is IT's job." | Technical projects feel technical | Problem, success criteria, test cases, risks and approval points are business decisions. Builders can't guess them. |
| "The spec should say which model and framework to use." | Wanting to be concrete | Specify the *what* and *how we'll know*; let builders propose the *how*. |
| "Test cases are for testers." | Unfamiliar vocabulary | A test case is just "for this input, a good result looks like this". Programme staff are the best people to write them. |

## Quiz answer rationale

| Q | Topic | Correct | Most tempting wrong answer | Why it's tempting, and why it's wrong |
|---|---|---|---|---|
| 1 | Agent vs chat | **C** (loop with tools) | A (bigger model) | "Agent" sounds more advanced. The same model can be a chatbot or an agent. |
| 2 | Fixed-step SitRep | **A** (workflow) | B (agents are newest) | Newness feels like quality. Predictability and testability matter more for a fixed process. |
| 3 | Agent sent unreviewed draft | **D** (approval point, no send tool) | A (better system prompt) | Instructions feel like control. They aren't; permissions and approval are. |
| 4 | MCP connection | **B** (read vs change) | A (which model) | People focus on the model. Risk sits in what the connection can reach and do. |
| 5 | Nine agents | **C** (hand-offs and cost) | A (more specialists better) | Specialization sounds efficient. Beyond genuine need, it adds error and cost. |
| 6 | Vague success criteria | **D** (measurable) | B (builders will know) | It feels like trusting experts. Builders can't know your reporting standards. |
| 7 | Most useful test case | **B** (personal data case) | A (clean note) | The typical case feels representative. Systems fail on awkward cases, so tests must include them. |

## Discussion prompts

1. What's something you would delegate to a human assistant but not to an AI agent? What's the
   difference in your mind: skill, judgement or accountability?
2. Think of a system your organization bought or built that disappointed. Which section of the
   spec template was missing from the original request?
3. In the demo, the agent sent the email. Whose fault would that be in real life: the model, the
   builders, or the person who commissioned it?
4. Which steps in the SitRep process should *never* be done by AI, even with a perfect system?
5. Your spec says "reviewers accept 8 of 10 drafts". Is that a good bar? What if the two
   rejected ones contain a wrong casualty figure?

## Lab facilitation tips

- **Paper first for the spec.** Have pairs fill in the Problem, Users and Human approval points on
  the printed template *before* Exercise 2. The AI's questions are much more useful when learners
  have already thought about the answers.
- **Exercise 1:** watch for task 4 (cash eligibility). If the AI suggests an agent, make sure the
  pair pushes back. Link to the red light in Class 6.
- **Exercise 2:** the AI's clarifying questions are the real value. Ask pairs to note which
  question they found hardest to answer.
- **Exercise 3:** push for specificity. "Handles ambiguity well" is not a test; "flags 04/05 as
  ambiguous and does not convert it to a date" is. Challenge pairs with: "Could two people
  disagree about whether this passed?"
- **Exercise 4:** the red-team output is often generic. Ask pairs to pick the *one* criticism
  that would change the design most, and fix it in the spec.
- **Exercise 5:** insist on learners' own answers before asking the AI. The comparison is the
  learning.
- **Keep it fictional.** Some learners will want to write a spec for a real system in their
  office. Encourage it as homework and as a head start on the Class 8 final project, but use
  only fictional or non-sensitive details in class.
- **Struggling pairs:** give them the test-case table from section 7 and ask them to add three
  rows.
- **Fast pairs:** ask them to write the orchestration decisions for a *multi-agent* version and
  say which agent gets which tools and why.
- **Collect for the debrief:** one vague success criterion rewritten to be measurable, one great
  awkward test case, and one criticism from Exercise 4 that changed a spec.
