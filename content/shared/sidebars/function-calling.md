??? info "Know the Term: Function calling (tool use)"
    **Function calling**, also called **tool use**, is how a language model asks for something to
    be *done* rather than only writing text. The application tells the model which tools exist
    (for example "search field reports" or "look up a district's population"), each with a name,
    a description and a list of inputs. When the model decides a tool would help, it replies with
    a structured request such as *call `get_population` with district = "Kessan"*. The model never
    runs anything itself: the application checks the request, runs the tool, and hands the result
    back so the model can continue.

    **Analogy:** a researcher who cannot leave the library fills in request slips for the
    archive desk. The desk decides whether to fetch the file, fetches it, and passes it back.

    **Why you care:** tools are what let an assistant work with live, real data instead of guessing
    from memory. The application, not the model, decides which tools exist and what they are
    allowed to touch.
