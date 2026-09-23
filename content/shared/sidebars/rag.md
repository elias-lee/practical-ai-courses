??? info "Know the Term: RAG (Retrieval-Augmented Generation)"
    Instead of relying only on what the model memorized during training, a RAG system first
    **searches** a collection of documents for passages relevant to your question, then **hands
    the best matches** to the model together with your question. The model writes its answer from
    those passages and can cite them.

    **Analogy:** an open-book exam instead of answering from memory.

    **Why you care:** RAG is the main way to make AI answer from *your organization's* documents —
    current, specific and citable — without retraining a model.
