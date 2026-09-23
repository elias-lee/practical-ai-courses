# Glossary

Plain-English definitions of the terms used across both courses. Use the search box, or your
browser's find (Ctrl/Cmd + F), to jump to a term. The class where a term is introduced is shown
as **L** (AI Literacy) or **E** (AI Engineering) plus the class number.

## A

**A/B test, shadow mode, canary release** *(E7)*
: Ways to compare or roll out a new version safely on live traffic: split users between versions;
  run the new version silently alongside the old; release it to a small share first.

**A2A (Agent2Agent)** *(E6)*
: An open protocol that lets agents from different teams or vendors delegate tasks to each other.
  Each agent publishes an *Agent Card* describing what it can do.

**Agent** *(L7, E6)*
: A language model running in a loop that chooses its own next action (usually a tool call) until
  the job is done, a limit is hit or a person stops it.

**Agent-computer interface (ACI)** *(E5)*
: The names, descriptions, schemas, results and error messages through which a model uses a
  system. Good tool design is good ACI design.

**Agent framework** *(E6)*
: A library that provides agent loops, state, checkpoints, approval gates and tracing — e.g.
  LangGraph, OpenAI Agents SDK, Claude Agent SDK, Microsoft Agent Framework, CrewAI (as of 2026).

**Agent loop** *(E6)*
: The cycle an agent repeats: observe → think → act → observe again.

**Agentic RAG** *(E4)*
: A model that decides when and what to search, possibly searching several times.

**AI / code / human split** *(L1, E1)*
: Giving each step of a task one owner. AI proposes, code checks, humans decide.

**AI gateway** *(E3)*
: A central service between applications and model providers that handles keys, logging, quotas
  and cost.

**AI governance** *(L8, E8)*
: The laws, policies, standards and bodies that shape how AI is built and used.

**AI winter** *(L1)*
: A period when excitement and funding for AI research fell after promises weren't met.

**API key** *(E0)*
: A secret string that identifies you to a model provider. Treat it like a password.

**Artificial intelligence (AI)** *(L1)*
: The broad field of making computers do tasks that normally need human intelligence.

**Attention** *(L2, E1)*
: The transformer's way of working out which other parts of the text matter most for each token.

**Automation bias** *(L6)*
: The human tendency to over-trust a computer's output, especially when it sounds confident.

**Autoregressive generation** *(E1)*
: Producing text one token at a time, adding each chosen token before predicting the next.

## B

**Back-translation** *(L5)*
: Translating a translation back into the original language to check that the meaning survived.

**Base model** *(L2, E1)*
: A model after pre-training only — a text continuer, not yet a helpful assistant.

**Bias** *(L6)*
: A systematic skew in AI output for or against certain groups, places, languages or viewpoints.

**BM25** *(E4)*
: The standard method for scoring how well a document matches a query's keywords.

**Budget** *(E6)*
: A hard limit, enforced in code, on an AI system's steps, tokens, cost or time.

**Byte-pair encoding (BPE)** *(E1)*
: A common way to build a tokenizer's vocabulary by repeatedly merging frequent character pairs.

## C

**Cascade** *(E6)*
: Trying a cheap model first and escalating to a stronger one only when a check fails.

**Chain of thought** *(L3, E2)*
: Getting the AI to work through a problem in visible steps before giving its final answer.

**Checkpoint** *(E6)*
: A saved snapshot of a run's state after a step, so it can resume without redoing earlier work.

**Chunk, chunking, overlap** *(L4, E4)*
: A short piece of a document cut out so it can be searched; the act of cutting documents up;
  words repeated between neighbouring pieces so meaning isn't cut in half. Chunking can be
  *fixed-size*, *recursive* (following the document's structure) or *semantic* (where the
  meaning changes).

**Circuit breaker** *(E7)*
: Stops calling a failing service for a while and fails fast instead of waiting.

**Citation / citation accuracy** *(L4, E4)*
: A reference showing which source a statement came from / whether each cited source actually
  supports the claim attached to it.

**Closed (proprietary) model** *(L2, E1)*
: A model available only through its maker's service.

**Coding agent** *(E3)*
: An AI that plans, edits files and runs commands such as tests to complete a programming task.

**Coding assistant** *(E3)*
: An AI tool that suggests or drafts code while you work.

**Cohen's kappa** *(E7)*
: A measure of agreement between two graders that corrects for agreement expected by chance.

**Computational thinking** *(L1, E1)*
: Breaking a problem down so that people and machines can carry it out reliably: decomposition,
  pattern recognition, abstraction and writing clear steps.

**Context** *(L4)*
: Everything the model can see when it answers: instructions, conversation, pasted text, files
  and search results.

**Context engineering** *(E4)*
: Deciding what goes into the model's context window, in what order and within what budget.

**Context isolation** *(E6)*
: Giving each sub-agent only the information its own step needs.

**Context rot / lost in the middle** *(L4, E4)*
: Answers get worse as context grows; information buried in the middle of a long context is used
  less reliably than information at the start or end.

**Context window** *(L2, E1)*
: The maximum amount of text, measured in tokens, a model can take into account at once.

**Cosine similarity** *(E1, E4)*
: A measure of how closely two embeddings point in the same direction — i.e. how similar in
  meaning two texts are.

**Cost tracking** *(E3)*
: Counting input and output tokens, pricing them, and refusing further calls past a budget.

**Custom instructions** *(L3)*
: Your own standing instructions (or project settings) that apply to every chat in that space.

## D

**Data classification** *(L8, E8)*
: Labelling information by sensitivity (e.g. public, internal, confidential, strictly
  confidential) to decide who and which tools may use it.

**Data minimisation** *(L8)*
: Using only the personal data strictly needed for the purpose.

**Data sovereignty** *(L8, E8)*
: The principle that data is subject to the laws and control of where it comes from or whom it
  describes.

**Deep learning** *(L1)*
: Machine learning that uses large neural networks with many layers.

**Defence in depth** *(E8)*
: Several independent defences, so one failure does not become a breach.

**Delimiters** *(E2)*
: Markers such as `<report>…</report>` that separate data from instructions in a prompt.

**Demographically identifiable information** *(E8)*
: Group-level data that can put a community at risk even without names.

**Diffusion model** *(E8)*
: The kind of model behind AI image generation; it builds an image by removing noise step by step.

**Distillation** *(E8)*
: Training a small model to copy a large model's answers on a particular task.

## E

**Embedding** *(L2, E1, E4)*
: A list of numbers that represents the meaning of a piece of text, so similar meanings sit close
  together. Used to search by meaning.

**Energy use (of AI)** *(L8)*
: The electricity — and often cooling water — that data centres use to train and run models.

**Environment variable** *(E0, E3)*
: A named value set outside the code; the safe place for secrets such as API keys.

**Error analysis** *(E7)*
: Reading failures and grouping them into categories before choosing what to measure.

**Error compounding** *(E6)*
: Small per-step error rates multiplying across a chain: ten steps that are each 95% reliable
  succeed together only about 60% of the time.

**EU AI Act** *(L8, E8)*
: The European Union's AI law, which sets rules by risk tier: unacceptable, high, limited and
  minimal risk, plus rules for general-purpose models.

**Eval** *(E7)*
: A repeatable test of an AI system on a fixed set of cases, producing a score.

**Evaluator-optimizer** *(E6)*
: One model call drafts, another critiques against criteria, and the loop repeats until approved
  or out of rounds.

**Example leakage** *(E2)*
: A model copying content from a few-shot example into a real answer.

**Exfiltration** *(E8)*
: Getting data out of a system without permission — for example through a link or image address.

**Expert system** *(L1)*
: An early form of AI built from many hand-written "if… then…" rules.

**Exponential backoff and jitter** *(E3, E5)*
: Retrying after increasingly long waits (1 s, 2 s, 4 s…) plus a small random delay, so many
  clients don't retry at the same moment.

## F

**Fact-checking routine** *(L6)*
: Mark the claims, trace them to sources, compare meaning, look for gaps, record what you checked.

**FakeLLM** *(E0)*
: A scripted stand-in for a model, so tests run without an API key or network.

**Fallback** *(E5, E7)*
: A planned alternative — another model, a reduced mode or a human — when the main path fails.

**Few-shot prompting** *(L3, E2)*
: Including a few examples of the output you want so the AI copies their pattern.

**Fine-tuning** *(L2, E8)*
: Further training a model on a smaller, targeted set of examples to change its style or narrow
  skills.

**Function calling (tool use)** *(E5)*
: The model requests a named function with structured arguments; your code checks it, runs it and
  returns the result.

## G

**Generative AI** *(L1)*
: AI that creates new content such as text, images, audio or code.

**GDPR (General Data Protection Regulation)** *(L8, E8)*
: The European Union's data-protection law, a common reference point for handling personal data.

**Global Dialogue on AI Governance** *(L8)*
: A forum set up by the UN General Assembly for governments and stakeholders to discuss
  international cooperation on AI
  (established 2025).

**Global Digital Compact** *(L8, E8)*
: The UN Member States' 2024 agreement on digital cooperation, including AI governance.

**Golden dataset (golden set)** *(E4, E7)*
: A versioned set of realistic inputs with known correct answers or expectations, used for
  evaluation.

**Graceful degradation** *(E7)*
: Delivering a reduced but clearly labelled result instead of nothing.

**GraphRAG** *(E4)*
: RAG over a knowledge graph of entities and relationships extracted from a document library.

**Grounding / grounded answer** *(L4, E4)*
: Making the AI answer only from specific trusted sources; an answer whose every claim is
  supported by them.

**Guardrail** *(E5)*
: A check in code on inputs, tool calls or outputs that holds whatever the model does.

## H

**Hallucination** *(L2, E1)*
: A confident, fluent statement from an AI that is false or invented. A *hallucinated citation*
  is a reference that looks real but doesn't exist or doesn't say what is claimed.

**Handoff / swarm** *(E6)*
: A multi-agent design where agents pass control directly to each other, with no central
  coordinator.

**Handoff contract** *(E6)*
: A validated, structured format for what one agent passes to the next.

**Harness** *(E5)*
: Everything wrapped around a model call — instructions, tools, the loop, validation,
  guardrails, permissions and reliability wrappers — that controls what the model sees and does.

**Human approval point (gate)** *(L7, E6)*
: A step where a named person must approve before an AI system takes an irreversible or
  high-stakes action.

**Human in the loop** *(L6, E7)*
: A person who reviews and approves AI work at agreed points before it has real effects. A
  *rubber stamp* is a checkpoint that approves without really checking.

**Human sign-off** *(L5)*
: The final review and approval by an accountable person before anything is sent or published.

**Hybrid search** *(E4)*
: Combining keyword (BM25) and meaning-based (vector) scores to rank search results.

## I

**ISO/IEC 42001** *(L8, E8)*
: An international standard (2023) for an organization's AI management system.

**Idempotent** *(E3, E5)*
: Safe to repeat: doing it twice has the same effect as doing it once.

**Improvement loop** *(E7)*
: Run the eval, analyse the errors, change one thing, measure again.

**Independent International Scientific Panel on AI** *(L8)*
: A panel of 40 experts, established by the UN General Assembly in 2025, that assesses AI's
  opportunities, risks and impacts.

**Inference** *(L8)*
: Running a trained model to produce an answer; it uses energy each time.

**Ingestion** *(E4)*
: Turning raw files into clean text with metadata, ready to be indexed for search.

**Iteration** *(L3)*
: Improving an AI's answer through specific follow-up messages in the same conversation.

## J

**Jagged frontier** *(L1)*
: The uneven pattern of AI ability: strong at some tasks, weak at similar-looking ones.

**Jailbreak** *(L8, E8)*
: A user's attempt to trick an AI into breaking its own safety rules.

**JSON / JSON Schema** *(L3, E2)*
: A plain-text data format of labelled fields that programs can read / a standard description of
  the shape JSON data must have.

**JSON mode vs structured-output (strict) mode** *(E2)*
: API settings that guarantee syntactically valid JSON / output that matches a given JSON Schema.

## K

**Kill switch** *(E8)*
: A configuration flag that turns off an AI feature or tool immediately.

**Knowledge base / project** *(L4)*
: A saved space in an AI tool that holds documents and standing instructions reused across chats.

**Knowledge cutoff** *(L2, L4, E1)*
: The date after which a model's training data contains no information.

## L

**Language coverage** *(L6)*
: How well an AI tool performs in a given language, which depends on how much of that language it
  learned from.

**LangGraph** *(E6)*
: An agent framework in which you define the workflow explicitly as a graph of nodes, edges and
  shared state.

**Large language model (LLM)** *(L1, E1)*
: A generative AI model trained on huge amounts of text to predict the next token — the engine
  behind chat tools such as ChatGPT, Copilot and Claude.

**Least privilege** *(E5, E8)*
: Each component gets only the permissions its job needs.

**Lethal trifecta** *(L8, E8)*
: The dangerous combination of access to private data, exposure to untrusted content, and the
  ability to send information out. Together they allow data theft. (Term coined by Simon
  Willison, 2025.)

**LiteLLM** *(E0, E3)*
: An open-source Python library that calls many model providers through one interface.

**LLM as a judge (grader)** *(E7)*
: A model that grades outputs against a rubric — trusted only after checking it against human
  grades.

## M

**Machine learning (ML)** *(L1)*
: A branch of AI where systems learn patterns from examples instead of following rules a person
  wrote.

**MCP (Model Context Protocol)** *(L7, E5)*
: An open standard for connecting AI assistants to tools and data sources — a "USB port" for AI.

**Memory (short-term, long-term, episodic, semantic)** *(E4)*
: Context kept within a session; kept across sessions; records of past events; distilled stable
  facts and preferences.

**Messages API** *(E3)*
: The standard request format for calling a model: a list of messages, each with a role (system,
  user, assistant) and content.

**Metadata filter** *(E4)*
: Limiting a search to documents with given attributes such as language, date, district or
  permissions.

**Model** *(L1)*
: The trained system that is then used on new inputs.

**Model deprecation** *(E8)*
: A provider retiring a model version. Handle it by pinning versions, tracking retirement dates
  and re-running evals.

**Model routing** *(E6)*
: Choosing a different model for each step based on its difficulty and cost.

**Multi-agent system** *(L7, E6)*
: A job split across several specialised agents, coordinated by an orchestrator or supervisor.

**Multilingual embedding model** *(E4)*
: An embedding model that places text in many languages in one shared space, so a question in one
  language can find documents in another.

**Multimodal model** *(L2, E1)*
: A model that handles more than one kind of input or output, such as text, images and audio.

## N

**Neural network** *(L1)*
: A model made of many simple connected units whose adjustable weights are tuned during training.

**Next-token prediction** *(L2, E1)*
: How a language model writes: give a probability to every possible next token, pick one, add it,
  repeat.

**NIST AI Risk Management Framework** *(L8, E8)*
: A voluntary US framework (2023) for identifying and managing AI risks, widely used worldwide.

**Non-determinism** *(E1)*
: Getting different outputs from the same input.

**"Not stated"** *(L3, E2)*
: The explicit value used when a source doesn't give a piece of information, instead of guessing.

## O

**Observability** *(E7)*
: Being able to see what a system did and why, through traces, logs and metrics.

**OECD AI Principles** *(L8, E8)*
: Intergovernmental principles for trustworthy AI, adopted in 2019 and updated in 2024.

**Omission** *(L6)*
: An important fact, group or caveat from the source that an AI's output left out.

**Open-weight model** *(L2, E1)*
: A model whose trained weights are published, so organizations can run it themselves.

**OpenTelemetry** *(E7)*
: The open standard for recording traces and metrics.

**Orchestration layer** *(L7, E6)*
: The part of an AI system that plans the work, routes it to agents or tools, keeps state and
  enforces budgets, stop rules and human approval.

**Orchestrator-workers** *(E6)*
: A central model decides the sub-tasks at run time, hands them to worker models and combines the
  results.

**OWASP Top 10 for LLM Applications** *(E8)*
: The standard checklist of security risks for applications built on language models.

## P

**p95 latency** *(E7)*
: The time within which 95% of requests finish.

**Parallelization** *(E6)*
: Running several model calls at once — on different sub-tasks (*sectioning*) or on the same task
  to compare answers (*voting*).

**Parameters (weights)** *(L1)*
: The billions of numbers inside a model that are adjusted during training.

**pass@k / pass^k** *(E7)*
: Succeeds at least once in k tries / succeeds all k times.

**Personal data** *(L8)*
: Any information that relates to an identified or identifiable person.

**PII redaction** *(E5)*
: Masking personal data such as names, phone numbers and email addresses.

**Pinned dependencies / lock file** *(E3)*
: Recording exact package versions so every install is identical.

**Placeholder** *(L5)*
: A marker in [square brackets] where information is missing, used instead of letting the AI
  invent it.

**Pre-training** *(L2, E1)*
: The first and largest training stage, in which a model learns to predict text from an enormous
  collection of documents.

**Prompt** *(L3)*
: Everything you give an AI tool: instructions, questions, pasted material and follow-ups.

**Prompt caching** *(E4)*
: The provider reusing an identical prompt beginning, for lower cost and faster replies.

**Prompt chaining** *(E6)*
: Fixed steps run in sequence, each using the previous step's output, often with a check between.

**Prompt engineering** *(L3)*
: The skill of writing instructions that get useful output from an AI.

**Prompt injection** *(L8, E8)*
: Hiding instructions in content an AI will read so it follows them as if they came from its
  user. *Indirect* injection hides them in documents, emails or web pages the system processes.

**Prompt template / version / test** *(L3, E2)*
: A saved prompt with named slots / an identifier for a prompt's wording, logged with every call /
  an automated test of how a prompt is built or the logic around the model.

**Pydantic** *(E2)*
: A Python library that declares data shapes as classes, validates data and generates JSON Schema.

## Q

**Quantization** *(E8)*
: Storing a model's numbers with less precision so it is smaller and faster.

**Query translation** *(E4)*
: Searching with translations of the question into other languages and merging the results.

## R

**RAG (Retrieval-Augmented Generation)** *(L4, E4)*
: Searching a document collection first, then giving the most relevant passages to the model so
  it answers from them, with citations — an "open-book exam".

**Rate limit** *(E3)*
: A provider's cap on requests or tokens per minute; exceeding it returns error 429.

**ReAct** *(E6)*
: A pattern where the model alternates short reasoning ("thought") with tool use ("action") and
  reads each result ("observation").

**Reasoning model** *(L2, E1)*
: A model trained to work through a problem internally before giving its answer.

**Recall@k** *(E4)*
: The share of questions whose correct document appears in the top k search results.

**Reciprocal rank fusion (RRF)** *(E4)*
: Merging ranked lists by adding 1 ÷ (60 + rank) from each list.

**Red-teaming** *(E8)*
: Attacking your own system — or one you are authorised to test — to find weaknesses first.

**Regression test** *(E7)*
: An eval run automatically to catch things that used to work and no longer do.

**Re-identification** *(L8)*
: Working out who a person is from data that had names removed.

**Repair retry** *(E2)*
: Re-asking the model with its invalid reply and the exact validation errors.

**Re-ranking (cross-encoder)** *(E4)*
: Rescoring the top search results with a slower model that reads question and passage together.

**RLHF (reinforcement learning from human feedback)** *(L2, E1)*
: Adjusting a model towards answers that people rate as better.

**Routing** *(E6)*
: A first step that classifies a request and sends it to the right specialised path.

**Rubric** *(L8, E7)*
: A scoring guide with a concrete description for each level.

## S

**Sampling, temperature, top-p** *(L2, E1)*
: Picking the next token from the model's probabilities; a setting for how focused (low) or
  varied (high) those choices are; sampling only among the most likely tokens whose
  probabilities add up to p.

**Sandbox** *(E8)*
: An isolated environment with no network, credentials or broad file access, for running
  untrusted code.

**Secrets manager** *(E3, E8)*
: A secure service that stores keys and passwords and hands them to applications.

**Self-check / self-review** *(L5, L6)*
: Asking the AI to review its own output against the source. Useful, but not a substitute for
  human verification.

**Self-consistency (voting)** *(E1)*
: Asking several times and accepting the majority answer only if enough answers agree.

**Semantic check** *(E2)*
: Checking the content of output against the source — e.g. that a quoted figure is really in the
  report.

**SitRep (situation report)** *(L1, E1)*
: A short, structured update on a crisis for decision-makers: what happened, where, who is
  affected, urgent needs and open questions. The running case study of both courses.

**Skill** *(E5)*
: Packaged instructions and resources that an assistant loads only when a task needs them.

**Slopsquatting** *(E3)*
: Publishing malicious packages under names that AI tools tend to invent.

**Small language model** *(L2, E1)*
: A model with relatively few parameters — faster and cheaper, sometimes able to run on a laptop
  or phone.

**Smoke test** *(E0)*
: The smallest check that a whole path — code, key, network, model — works.

**Spec (specification)** *(L7, E3)*
: A short document describing what a system must do, must not do, and how you'll know it works.
  *Spec-first development* means writing the spec and tests before the code.

**State** *(E6)*
: Everything a run needs to continue, explain or resume: inputs, plan, step outputs, decisions,
  counters and errors.

**Stateless (API)** *(E3)*
: The model remembers nothing between calls; your code resends the conversation each time.

**Stop reason (finish_reason)** *(E3)*
: Why the model stopped writing: finished, hit the length limit, called a tool, or was filtered.

**Stop rule** *(E6)*
: The condition that ends a run: success, an exhausted budget, or a human saying stop.

**Streaming** *(E3)*
: Receiving a model's answer in pieces as it is generated.

**Structured output** *(L3, E2)*
: An AI answer in a fixed, predictable shape such as a table, form or JSON.

**Success criteria** *(L7)*
: Measurable statements of what "working" means for a system.

**Supervisor / hierarchical** *(E6)*
: Multi-agent designs where one coordinating agent calls specialists and merges their results /
  supervisors manage other supervisors.

**System prompt** *(L3, E2)*
: Standing instructions given to the AI before the conversation starts, usually set by the
  tool's owners and hidden from users.

## T

**Test case** *(L7, E3)*
: A realistic input plus a description of the correct result. *Tests as the contract* means the
  automated tests define when a change is finished.

**Threat model** *(E8)*
: A structured review of what a system protects, who might attack it, how, and what you'll do
  about it.

**Timeout** *(E3)*
: The longest your code will wait for a reply before treating the call as failed.

**Token / tokenizer** *(L2, E1)*
: A chunk of text — word, part of a word or punctuation — that a model reads and writes / the
  component that splits text into tokens. Limits and costs are counted in tokens, and some
  languages need more tokens for the same meaning.

**Tool** *(L7, E5)*
: A specific action an AI system is allowed to request, such as searching a folder or drafting an
  email. *Tool poisoning* hides malicious instructions in a tool's description or output.

**Tool-call loop** *(E5)*
: Ask the model, run the tool it requests, feed back the result or error, and repeat until a final
  answer or the step budget runs out.

**Trace / span** *(E7)*
: The record of one request from start to finish / one timed step within it.

**Traffic-light rule** *(L6)*
: Green (go, with a normal check), amber (care and a named checker), red (don't use a general AI
  tool).

**Training** *(L1)*
: Adjusting a model using many examples until it performs a task well.

**Trajectory eval** *(E7)*
: Checking the path of tool calls an agent took, not only its final answer.

**Transformer** *(L2, E1)*
: The model design (2017) behind almost all modern large language models, built around attention.

**Transient vs permanent error** *(E3)*
: A failure worth retrying after a wait vs one that will fail the same way again.

**Trust boundary** *(E8)*
: The point where data crosses from a less trusted to a more trusted part of a system.

## U – Z

**UNESCO Recommendation on the Ethics of AI** *(L8, E8)*
: A global standard on AI ethics adopted by UNESCO's member states in 2021.

**Terminology list** *(L5)*
: Agreed translations of key terms that the AI must use, checked against your organization's list
  or an official terminology database.

**Validation** *(E2)*
: Checking output against a schema before code uses it.

**Vector store / vector database** *(E4)*
: A store that holds chunks with their embeddings and metadata and quickly finds the most similar.
  Fast search uses an *approximate nearest neighbour (ANN)* index.

**Vibe coding** *(E3)*
: Building software by accepting AI-generated code because it seems to work, without close review.

**Virtual environment (venv)** *(E0)*
: A private folder of Python packages for one project.

**Workflow** *(L7, E6)*
: Several model calls connected along a path your code defines in advance — as opposed to an
  agent, which chooses its own path.

**Zero-shot prompting** *(L3, E2)*
: Asking the AI to do a task with instructions only, no examples.
