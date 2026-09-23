??? info "Know the Term: Agent frameworks"
    An **agent framework** is a software library that supplies the plumbing every agent system
    needs — the loop, tool calling, passing state between steps, saving progress
    (checkpoints), pausing for human approval, and tracing. Popular options as of 2026 include
    **LangGraph**, the **OpenAI Agents SDK**, the **Claude Agent SDK**, **Microsoft Agent
    Framework** and **CrewAI**. They differ mainly in how much control they give you: some make
    you draw the workflow explicitly as a graph, others let you describe a team of agents and
    handle coordination for you.

    **Analogy:** a framework is scaffolding on a building site — it speeds up construction, but
    you still need an architect's plan.

    **Why you care:** the concepts (loop, state, budgets, stop rules, approval gates) are the
    same in every framework. Learn them once, then pick the framework that fits your team's
    stack and hosting constraints; frameworks change fast, the concepts do not.
