??? info "Know the Term: Observability and tracing"
    **Observability** is the ability to see what an AI system actually did, after the fact. The
    main tool is a **trace**: a record of one request from start to finish, broken into **spans**,
    one per step, such as a model call, a document search or a tool call. Each span records what
    went in, what came out, how long it took, how many tokens it used and what it cost. With
    traces you can answer "why did the SitRep say 900 people?" by finding the exact step where the
    number appeared. Common tools as of 2026 include OpenTelemetry (an open standard), Langfuse,
    Arize Phoenix and LangSmith.

    **Analogy:** a flight data recorder. You hope never to need it, but when something goes wrong
    it is the only way to find out what happened.

    **Why you care:** without traces, AI errors cannot be explained, fixed or defended in an
    audit. Traces also contain the data people typed in, so they need the same protection and
    retention rules as the data itself.
