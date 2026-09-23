??? info "Know the Term: Knowledge cutoff"
    A model learns from a huge collection of text gathered up to a certain date, and then its
    training stops. That date is its **knowledge cutoff**. Anything that happened afterwards, such
    as a new policy, a changed ceasefire line, last week's flood figures or a newly appointed head
    of agency, is simply not in the model's memory. Some tools add a web search or a document
    search on top, which can bring in newer information, but the model underneath still has a
    fixed cutoff. Worse, the model doesn't always *know* what it doesn't know: asked about recent
    events, it may answer confidently from older information as if it were current.

    **Analogy:** a well-read colleague just back from a year at a remote field post with no
    internet. They know a lot, but nothing from the past year, and they may not realise how much
    has changed.

    **Why you care:** for anything recent or fast-moving, don't rely on the model's memory. Give it
    the current documents yourself, and check the date on any fact that matters.
