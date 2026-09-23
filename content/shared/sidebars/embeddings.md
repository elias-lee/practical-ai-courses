??? info "Know the Term: Embeddings"
    An **embedding** is a list of numbers (a **vector**, often hundreds or thousands of numbers
    long) that represents the *meaning* of a word, sentence or document. A model learns to
    produce embeddings so that things with similar meanings get similar numbers, and so sit
    close together in this "meaning space". "Flood", "inundation" and *inondation* (French) end
    up near each other; "flood" and "invoice" end up far apart. Inside a language model, every
    token is turned into an embedding before the model works on it. Separately, embeddings are
    used to **search by meaning**: to find the documents closest to a question even when they
    don't share any of its exact words.

    **Analogy:** a map where every idea has coordinates. Related ideas are neighbours, so to find
    documents about your question you look at what is nearby on the map.

    **Why you care:** embeddings are how AI tools find the relevant pages in a large document
    library (see RAG in Class 4) and how search can work across languages.
