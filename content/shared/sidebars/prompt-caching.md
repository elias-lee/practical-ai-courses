??? info "Know the Term: Prompt caching"
    Many AI systems send the same long opening text with every request: the same instructions,
    the same style guide, the same reference documents. **Prompt caching** lets the provider keep
    the processed version of that repeated opening for a few minutes (sometimes longer), so the
    next request that starts the same way is cheaper and faster. As of 2026 the major providers
    (OpenAI, Azure OpenAI, Anthropic, Google) offer it, some automatically and some when you mark
    the part to cache, with discounts that can be large on the cached part. It only works if the
    repeated part comes *first* and is *exactly* the same each time.

    **Analogy:** a meeting where everyone has already read the background pack, so the briefing
    can skip straight to today's update.

    **Why you care:** put fixed instructions and documents at the start of a prompt and the
    changing question at the end. It can cut the cost and waiting time of a busy AI tool
    substantially without changing its answers.
