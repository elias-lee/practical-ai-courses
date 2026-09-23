# AI Engineering

**For technical colleagues. Working knowledge of Python is required.**

By the end of this course you will be able to design a multi-agent architecture with an
orchestration layer, build a working prototype of it with an AI coding assistant, and
evaluate, trace and secure it.

**Format:** self-paced pre-work plus 8 classes of about 3 hours.
**You need:** Python 3.11+, an editor with an AI coding assistant, and an API key for any
LLM provider (Azure OpenAI, OpenAI or Anthropic). Labs are model-agnostic, and every lab's
tests run without an API key. Lab code is in the `labs/` folder of the course zip.

## The target architecture

Each class builds one layer of this reference architecture — see the full [AI Map](../ai-map.md).

<div class="diagram" markdown>
![Reference architecture: interface, orchestration, agents, harness, context and data, models, with cross-cutting evals, observability, security and cost](../assets/img/reference-architecture.svg)
</div>

## Classes

| # | Class | Layer | Lab output | Progress |
|---|---|---|---|---|
| 0 | [Pre-work: setup](prework.md) | — | Working environment and first API call | <span data-progress-for="engineering/prework.html"></span> |
| 1 | [Foundations: thinking and models](c1.md) | Models | SitRep task breakdown, token and cost estimator | <span data-progress-for="engineering/c1.html"></span> |
| 2 | [Prompting and structured outputs](c2.md) | Harness | Validated, structured SitRep extractor | <span data-progress-for="engineering/c2.html"></span> |
| 3 | [Building with code and AI pair programming](c3.md) | Interface | Spec-first CLI app with retries and cost tracking | <span data-progress-for="engineering/c3.html"></span> |
| 4 | [Context engineering and RAG](c4.md) | Context & data | Hybrid-search RAG with citations | <span data-progress-for="engineering/c4.html"></span> |
| 5 | [Harness and tools](c5.md) | Harness | Tool loop with guardrails | <span data-progress-for="engineering/c5.html"></span> |
| 6 | [Agents and orchestration](c6.md) | Orchestration + agents | Multi-agent SitRep with an orchestrator | <span data-progress-for="engineering/c6.html"></span> |
| 7 | [Evals, observability and reliability](c7.md) | Cross-cutting | Golden test set, LLM grader, traces | <span data-progress-for="engineering/c7.html"></span> |
| 8 | [Security, governance and production](c8.md) | Cross-cutting | Red-team harness and capstone | <span data-progress-for="engineering/c8.html"></span> |
