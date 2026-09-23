??? info "Know the Term: Pre-training, fine-tuning and human feedback"
    Chat models are built in stages. **Pre-training** is the huge first stage: the model reads an
    enormous amount of text (web pages, books, code) and learns to predict the next token. This
    takes weeks on thousands of specialised chips and produces a **base model** that can continue
    any text but doesn't reliably follow instructions. **Fine-tuning** (also called
    **instruction tuning** or **supervised fine-tuning**) then trains it further on a much
    smaller set of example conversations showing good, helpful answers. Finally, **learning from
    human feedback** (**RLHF**, reinforcement learning from human feedback, and related methods)
    has people, or AI graders following written guidelines, compare pairs of answers; the model
    is adjusted towards the preferred ones, which shapes its tone, helpfulness and refusals.

    **Analogy:** a new staff member who first reads the whole library (pre-training), then
    shadows experienced colleagues on real cases (fine-tuning), then gets regular feedback from a
    supervisor on which of their drafts were better (human feedback).

    **Why you care:** most of what a model "knows" comes from pre-training, fixed at a cut-off
    date. Its politeness, style and willingness to refuse come from the later stages. And the
    feedback stage rewards answers people *like*, which is one reason chatbots can sound
    confident and agreeable even when they are wrong.
