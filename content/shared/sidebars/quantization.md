??? info "Know the Term: Quantization"
    **Quantization** makes a model smaller and faster by storing its billions of internal numbers
    with less precision, for example using 8 or 4 bits for each number instead of 16. The model
    needs far less memory, so it can run on a single server, a laptop or even a phone, and it
    answers faster, usually with only a small loss of quality. Quantization is common for
    open-weight models that an organisation runs on its own hardware.

    **Analogy:** saving a high-resolution photo as a smaller file. It loads faster and takes less
    space; most people cannot tell the difference, but fine detail can suffer.

    **Why you care:** quantization is what makes it practical to run a capable model on your own
    infrastructure, which can matter when data must not leave the organisation. Test the
    quantized model on your own evals: the loss of quality is small on average but can be larger on
    specific tasks or less common languages.
