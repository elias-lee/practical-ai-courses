??? info "Know the Term: MCP (Model Context Protocol)"
    **MCP** is an open standard, introduced by Anthropic in late 2024 and now widely supported,
    for connecting AI assistants to other systems — a document library, a calendar, a database,
    a mapping service. Each system is wrapped once as an **MCP server** that describes what it
    offers ("search reports", "look up a district's population"). Any AI application that
    speaks MCP can then use it, without custom code for every pairing of AI tool and data
    source.

    **Analogy:** a universal power adapter — plug any device into any socket, instead of needing a
    different cable for every combination.

    **Why you care:** MCP is how an assistant gains safe, controlled access to your
    organization's systems. Whoever sets up an MCP connection decides what the AI can read or
    change — so ask what a connection allows before you switch it on.
