??? info "Know the Term: Chunking"
    **Chunking** means cutting long documents into smaller pieces, called **chunks**, before
    they are stored for search. A search system retrieves chunks, not whole documents, so the
    way you cut matters. Cut too small and a chunk loses its context ("it was closed on Monday":
    *what* was?). Cut too large and a chunk mixes several topics, so it matches many questions
    weakly. Common approaches cut every few hundred words (**fixed-size**), follow the document's
    own headings, paragraphs and sentences (**recursive**), or start a new chunk where the topic
    changes (**semantic**). Neighbouring chunks usually **overlap** a little so that a sentence
    split at a boundary still appears whole in one of them.

    **Analogy:** cutting a long report into index cards. Each card must make sense on its own,
    and a little repetition between cards is better than a key sentence torn in half.

    **Why you care:** when a document assistant misses something that is clearly in the file,
    poor chunking is one of the first things to check.
