# The AI Map

Every useful AI system — from a single well-written prompt to a multi-agent platform — can be
described with the same layers. This map is the "big picture" for both courses.

<div class="diagram" markdown>
![Reference architecture of an agentic AI system](assets/img/reference-architecture.svg)
</div>

| Layer | What it does | Question it answers | Literacy class | Engineering class |
|---|---|---|---|---|
| **Interface** | Where people meet the system: chat, API, email, an approval screen | *How do people use it?* | 5 | 8 |
| **Orchestration layer** | Plans the work, routes it to agents, keeps state, enforces budgets and stop rules | *Who does what, in what order, and when do we stop?* | 7 | 6 |
| **Agents** | Specialized workers — each a model with its own instructions and tools | *Which specialist handles this step?* | 7 | 6 |
| **Harness** | Everything wrapped around a model call: system prompts, tools, guardrails, output formats, permissions | *What may the model see and do?* | 3 | 2, 5 |
| **Context & data** | Getting the right information into the model: retrieval (RAG), memory, document ingestion | *Does the model know what it needs to know?* | 4 | 4 |
| **Models** | The large language models themselves, and choosing which one to use | *Which brain, at what cost?* | 1, 2 | 1, 6 |
| **Cross-cutting** | Evals, observability, security and cost apply to every layer | *Does it work, can we see it, is it safe, can we afford it?* | 6, 8 | 7, 8 |

## Four kinds of "engineering"

The field's vocabulary grew in the same order as the layers above. Each new term answers the
question the previous one could not:

1. **Prompt engineering** — writing one excellent instruction. *"My prompt is great — why is the
   answer still wrong?"* Because the model lacks information…
2. **Context engineering** — deciding exactly what information the model sees. *"It has the right
   information — why can't it act?"* Because it has no hands…
3. **Harness engineering** — the tools, rules and structure around the model. *"It can act — how
   do I know it does the job well, and stops when it should?"*
4. **Loop engineering** — the **agent loop** (act, observe, repeat until a stop rule or a human
   says stop) and the **improvement loop** (measure with tests, change one thing, measure again).
