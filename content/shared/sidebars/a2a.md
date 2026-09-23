??? info "Know the Term: A2A (Agent2Agent protocol)"
    **A2A** is an open protocol, introduced by Google in 2025 and now hosted by the Linux
    Foundation, that lets agents built by *different* teams, vendors or frameworks talk to each
    other. Each agent publishes an **Agent Card** — a small JSON document describing what it can
    do and how to reach it — and other agents send it **tasks** over standard web requests,
    receiving status updates and results (**artifacts**) back. The calling agent never sees the
    other agent's prompts, tools or memory: it delegates, it does not control.

    **Analogy:** sending a formal request to a partner agency's desk — you know what service they
    offer and how to ask, not how they organize their office.

    **Why you care:** where MCP connects an agent to *tools and data*, A2A connects an agent to
    *other agents*. It matters when your SitRep system needs a capability another organization
    runs as its own agent (as of 2026, adoption is growing but still uneven).
