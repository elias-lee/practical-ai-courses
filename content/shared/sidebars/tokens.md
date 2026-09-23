??? info "Know the Term: Tokens"
    A **token** is the unit of text a language model reads and writes. It is often a whole
    common word ("water"), sometimes part of a word ("purific" + "ation"), a space, or a
    punctuation mark. Before the model sees your text, a **tokenizer** chops it into tokens and
    turns each one into a number. A rough rule for English: 1 token ≈ ¾ of a word, so 100 words
    ≈ 130 tokens. Tokenizers are built mostly from English-heavy text, so the same sentence often
    needs **more tokens** in languages such as Arabic or Russian, and scripts such as Chinese
    are counted differently again. Model limits (the **context window**) and prices are measured
    in tokens, not words.

    **Analogy:** Lego bricks. The model never sees your sentence as a whole; it sees the bricks
    it has been broken into, and it builds its answer one brick at a time.

    **Why you care:** tokens explain why long documents hit a limit, why costs can differ between
    the languages you work in, and why chatbots sometimes stumble on tasks like counting the letters
    in a word: they never saw the individual letters.
