??? info "Know the Term: GraphRAG"
    **GraphRAG** is a variant of retrieval-augmented generation that first uses an AI model to
    read a whole document collection and build a **knowledge graph**: a network of the people,
    places, organizations and events mentioned, and how they are connected. Questions are then
    answered by following those connections, often using summaries of whole groups of related
    items, instead of only fetching passages that look similar to the question. It is better at
    "big picture" questions ("What are the main themes across 300 reports?") and at questions
    that need several facts joined together. It is also slower and more costly to build and to
    keep up to date.

    **Analogy:** ordinary RAG hands you the five most relevant pages; GraphRAG hands you the
    investigator's wall of photos and strings showing who is linked to what.

    **Why you care:** if people mostly ask about connections and trends across many documents,
    plain search may not be enough. For most look-up questions it is.
