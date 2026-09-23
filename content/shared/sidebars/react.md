??? info "Know the Term: ReAct (Reason + Act)"
    **ReAct** is the pattern behind most tool-using agents, named in a 2022 research paper
    (*"ReAct: Synergizing Reasoning and Acting in Language Models"*). The model alternates between
    a **thought** ("I need last week's displacement figures"), an **action** (call the
    `search_reports` tool), and an **observation** (the tool's result), then thinks again with
    the new information. Interleaving reasoning with real observations keeps the model anchored
    to facts instead of reasoning in a vacuum.

    **Analogy:** a field assessor who says "let me check the clinic register", checks it, and
    updates their assessment — rather than writing the whole report from memory.

    **Why you care:** the thought–action–observation trace is also your debugging record. When an
    agent goes wrong, the trace shows the exact step where its reasoning left the facts.
