??? info "Know the Term: Distillation"
    **Distillation** is a way of making a small, cheap model behave like a large, expensive one on
    a particular task. The large model (the "teacher") answers many example questions; the small
    model (the "student") is then trained to give the same answers. The student ends up much
    faster and cheaper to run, and nearly as good *on that task*, though usually weaker
    everywhere else. Many of the small, fast models offered by providers as of 2026 were produced
    partly this way.

    **Analogy:** an experienced officer writes model answers for the thirty questions the help
    desk gets most often, and a new colleague learns to handle those questions just as well,
    without the officer's twenty years of general experience.

    **Why you care:** distillation is one reason a small model can be good enough for a
    high-volume, narrow job such as routing or classifying reports, at a fraction of the cost.
    Check the provider's terms first: some forbid using their outputs to train other models.
