??? info "Know the Term: Vector database"
    A **vector database** stores pieces of text together with their **embeddings**: long lists of
    numbers that capture what each piece *means*. When a question arrives, it is turned into the
    same kind of list, and the database quickly finds the stored pieces whose numbers are closest,
    that is, the passages most similar in meaning, even if they use different words. Most also
    store **metadata** such as date, language or source, so a search can be limited to, say,
    French documents from last week. Examples as of 2026 include Chroma, pgvector (an add-on for
    the PostgreSQL database), Qdrant, Weaviate, Pinecone and the vector search built into cloud
    platforms.

    **Analogy:** a library where books are shelved by topic rather than by title, so everything
    about water safety sits together whatever words the authors used.

    **Why you care:** it is the search engine behind most "chat with your documents" tools. How
    well it finds the right passages sets a ceiling on how good the answers can be.
