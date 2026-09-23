??? info "Know the Term: Transformer and attention"
    The **transformer** is the design behind almost every modern large language model. It was
    introduced in the 2017 research paper *"Attention Is All You Need"*. Its key trick is
    **attention**: when the model processes a word, it looks at *all* the other words in the text
    and decides which ones matter most for understanding it. In *"The bank raised interest rates"*,
    attention links "bank" to "interest rates", so the model reads it as a financial bank, not a
    river bank.

    **Analogy:** a meeting where every participant can listen to everyone at once and decide
    whose input matters for the point being made.

    **Why you care:** the model can only "pay attention" to what is in the text you give it. That
    is why the context you provide matters so much.
