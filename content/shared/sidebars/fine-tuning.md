??? info "Know the Term: Fine-tuning"
    **Fine-tuning** means continuing to train an existing model on a smaller set of your own
    examples, so that it permanently picks up a style, format or narrow skill, for example
    always writing SitReps in a particular house style or classifying reports into your sector
    codes. It changes the model's internal settings (its weights), unlike a prompt, which only
    changes what the model reads for one request. Fine-tuning is good at teaching *how* to
    respond; it is a poor way to teach *facts*, which go stale and are better supplied through
    retrieval (RAG).

    **Analogy:** sending a capable new colleague on a two-week course in your organisation's
    writing style. They come back writing differently, but they still need this week's briefing
    notes to know what is happening.

    **Why you care:** fine-tuning costs money, needs hundreds or thousands of good examples, and
    must be repeated when the base model is retired. Try better prompts and retrieval first, and
    measure with evals before deciding it is needed.
