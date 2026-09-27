from design import class_header, classify_text_blocks, meta_items, track_for

LIT = [("literacy/c1.md", "c1.html", "What AI Is"), ("literacy/c2.md", "c2.html", "How Chatbots Work"),
       ("literacy/c3.md", "c3.html", "Prompting Well")]
ENG = [("engineering/prework.md", "prework.html", "Setup"), ("engineering/c1.md", "c1.html", "Foundations")]

PAGE_HTML = (
    '<h1 id="class-3-prompting-well">Class 3 · Prompting Well<a class="headerlink" href="#x">¶</a></h1>\n'
    '<div class="class-meta"><p><span>AI Literacy</span><span>~3 hours</span><span>No coding</span></p></div>\n'
    "<p>Body</p>"
)


def test_track_for():
    assert track_for("literacy/c3.md") == "literacy"
    assert track_for("instructor/engineering-c6.md") == "engineering"
    assert track_for("glossary.md") == "reference"
    assert track_for("index.md") == "home"


def test_meta_items_drop_track_name_and_humanize_duration():
    spans = ["AI Literacy", "~3 hours", "No coding"]
    assert meta_items(spans) == ["About 3 hours", "No coding"]


def test_class_header_replaces_h1_and_meta():
    html = class_header(PAGE_HTML, "literacy/c3.md", LIT, total=8)
    assert 'class="class-head"' in html
    assert '<div class="class-head__num" aria-hidden="true">3</div>' in html
    assert '<h1 id="class-3-prompting-well"><span class="visually-hidden">Class 3: </span>Prompting Well</h1>' in html
    assert "Class 3 of 8" in html and "About 3 hours" in html
    assert "class-meta" not in html and "AI Literacy</span>" not in html
    assert html.endswith("<p>Body</p>")


def test_stepper_marks_current_and_tracks_progress():
    html = class_header(PAGE_HTML, "literacy/c3.md", LIT, total=8)
    assert '<a href="c1.html" title="What AI Is" data-progress-for="literacy/c1.html">1</a>' in html
    assert 'aria-current="page"' in html and 'data-progress-for="literacy/c3.html"' in html


def test_prework_is_class_zero():
    page = ('<h1 id="pre-work-setup">Pre-work · Setup</h1>\n'
            '<div class="class-meta"><p><span>AI Engineering</span><span>1–2 hours, self-paced</span></p></div>')
    html = class_header(page, "engineering/prework.md", ENG, total=8)
    assert '<div class="class-head__num" aria-hidden="true">0</div>' in html
    assert "Before class 1" in html
    assert ">0</a>" in html


def test_non_class_pages_are_untouched():
    assert class_header("<h1>Glossary</h1>", "glossary.md", LIT, total=8) == "<h1>Glossary</h1>"


def test_classify_text_blocks():
    prompt = '<div class="language-text highlight"><pre><span></span><code>Summarize this report.</code></pre></div>'
    diagram = '<div class="language-text highlight"><pre><span></span><code>A ──&gt; B\n│\nC</code></pre></div>'
    out = classify_text_blocks(prompt + diagram)
    assert '<div class="language-text highlight is-prompt">' in out
    assert '<div class="language-text highlight is-diagram">' in out


def test_reflow_joins_hard_wrapped_prompt_lines():
    from design import reflow_prompt
    text = (
        "You are a humanitarian reporting officer. Turn the field note below into\n"
        "a short situation update for our country director.\n"
        "\n"
        "Format: a one-line headline, then four headings: Affected population /\n"
        "Priority needs / Gaps.\n"
        "\n"
        "Field note:\n"
        '"""\n'
        "[paste the field report here]\n"
        '"""'
    )
    assert reflow_prompt(text) == (
        "You are a humanitarian reporting officer. Turn the field note below into a short situation "
        "update for our country director.\n"
        "\n"
        "Format: a one-line headline, then four headings: Affected population / Priority needs / Gaps.\n"
        "\n"
        "Field note:\n"
        '"""\n'
        "[paste the field report here]\n"
        '"""'
    )


def test_reflow_keeps_lists_and_short_lines():
    from design import reflow_prompt
    text = "Include:\n- the headline, which must be short and specific to the district\n- needs\n1. First item\nShort line\nAnother"
    assert reflow_prompt(text) == text


def test_inline_architecture(tmp_path):
    from design import inline_architecture
    (tmp_path / "reference-architecture-harness.svg").write_text("<svg>ok</svg>")
    page = ('<div class="diagram">\n<p><img alt="Arch" src="../assets/img/reference-architecture-harness.svg" />'
            "</p>\n</div>")
    assert inline_architecture(page, tmp_path) == '<figure class="figure figure--arch"><svg>ok</svg></figure>'


def test_classify_text_blocks_with_pre_attributes():
    block = '<div class="language-text highlight"><pre id="__code_3"><span></span><code>Hi</code></pre></div>'
    assert "is-prompt" in classify_text_blocks(block)
