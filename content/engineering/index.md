# AI Engineering

For people who write Python. By the end of this course you can design a multi-agent system with
an orchestration layer, build a working prototype with an AI coding assistant, and evaluate,
trace and secure it.

There is a self-paced pre-work session, then eight classes of about three hours. You need Python
3.11 or later, an editor with an AI coding assistant, and an API key for any model provider
(Azure OpenAI, OpenAI or Anthropic). Every lab's tests run without a key, and the lab code is in
the `labs/` folder of the course download.

## What you will build

Each class builds one layer of this architecture. The [AI map](../ai-map.md) explains every layer.

<div class="diagram" markdown>
![Reference architecture: interface, orchestration, agents, harness, context and data, models, with cross-cutting evals, observability, security and cost](../assets/img/reference-architecture.svg)
</div>

## Classes

<ol class="hub-classes" start="0">
<li><a href="prework.html">Pre-work: setup</a><span>A working environment and your first API call.</span><span data-progress-for="engineering/prework.html"></span></li>
<li><a href="c1.html">Foundations: thinking and models</a><span>Break the task down; estimate tokens and cost. Layer: models.</span><span data-progress-for="engineering/c1.html"></span></li>
<li><a href="c2.html">Prompting and structured outputs</a><span>A SitRep extractor that returns validated data. Layer: harness.</span><span data-progress-for="engineering/c2.html"></span></li>
<li><a href="c3.html">Building with code and AI pair programming</a><span>A spec-first app with retries and cost tracking. Layer: interface.</span><span data-progress-for="engineering/c3.html"></span></li>
<li><a href="c4.html">Context engineering and RAG</a><span>Hybrid search with citations across languages. Layer: context and data.</span><span data-progress-for="engineering/c4.html"></span></li>
<li><a href="c5.html">Harness and tools</a><span>A tool loop with guardrails and a step budget. Layer: harness.</span><span data-progress-for="engineering/c5.html"></span></li>
<li><a href="c6.html">Agents and orchestration</a><span>A multi-agent SitRep with an orchestrator. Layers: orchestration and agents.</span><span data-progress-for="engineering/c6.html"></span></li>
<li><a href="c7.html">Evals, observability and reliability</a><span>A golden test set, an LLM grader and traces. Cross-cutting.</span><span data-progress-for="engineering/c7.html"></span></li>
<li><a href="c8.html">Security, governance and production</a><span>A red-team harness and the capstone. Cross-cutting.</span><span data-progress-for="engineering/c8.html"></span></li>
</ol>
