"""MkDocs hook: course-specific page design.

- Tags <body> with data-track (literacy / engineering / reference / home) so CSS can apply the
  track colour.
- Replaces each class page's "Class N · Title" heading and meta line with a class header:
  a large class number, the title, and a stepper linking every class in the track.
- Marks ```text code blocks as prompt cards (wrapped text) or diagrams (kept verbatim).
"""
from __future__ import annotations

import html as html_lib
import re

CLASS_PAGE = re.compile(r"^(literacy|engineering)/(c(\d)|prework)\.md$")
H1 = re.compile(
    r'<h1 id="([^"]*)">(?:Class (\d) · |Pre-work · )(.*?)(?:<a class="headerlink"[^>]*>.*?</a>)?</h1>\s*'
    r'(?:<div class="class-meta">(.*?)</div>)?',
    re.S,
)
SPAN = re.compile(r"<span>(.*?)</span>", re.S)
TEXT_BLOCK = re.compile(r'<div class="language-text highlight">(<pre[^>]*>.*?</pre>)', re.S)
DIAGRAM_CHARS = re.compile(r"[─│┌┐└┘├┤┬┴┼▶►▼◀→↓←↑]|-->|<--|\+-{3,}|\|\s{2,}\|")
TRACK_NAMES = {"AI Literacy", "AI Engineering"}

ARCH_IMG = re.compile(
    r'<div class="diagram">\s*<p><img alt="[^"]*" src="[^"]*?(reference-architecture[\w-]*\.svg)"\s*/?></p>\s*</div>'
)

# Filled from the nav: {"literacy": [(src_uri, url, title), ...], "engineering": [...]}
_tracks: dict[str, list[tuple[str, str, str]]] = {}
_img_dir = None  # content/assets/img, set in on_config


def track_for(src_uri: str) -> str:
    if src_uri == "index.md":
        return "home"
    for track in ("literacy", "engineering"):
        if src_uri.startswith(f"{track}/") or src_uri.startswith(f"instructor/{track}-"):
            return track
    return "reference"


def meta_items(spans: list[str]) -> list[str]:
    items = []
    for text in spans:
        text = text.strip()
        if text in TRACK_NAMES:
            continue
        items.append(re.sub(r"^~\s*", "About ", text))
    return items


def _stepper(src_uri: str, track: str, classes: list[tuple[str, str, str]]) -> str:
    items = []
    for uri, url, title in classes:
        m = CLASS_PAGE.match(uri)
        number = m.group(3) or "0"
        attrs = f'href="{url}" title="{html_lib.escape(title, quote=True)}" data-progress-for="{uri[:-3]}.html"'
        if uri == src_uri:
            attrs += ' aria-current="page"'
        items.append(f"<li><a {attrs}>{number}</a></li>")
    return f'<nav class="class-steps" aria-label="Classes in this course"><ol>{"".join(items)}</ol></nav>'


def class_header(page_html: str, src_uri: str, classes: list[tuple[str, str, str]], total: int = 8) -> str:
    m = CLASS_PAGE.match(src_uri)
    if not m:
        return page_html
    h1 = H1.search(page_html)
    if not h1:
        return page_html
    anchor, number, title, meta_html = h1.groups()
    number = number or "0"
    position = f"Class {number} of {total}" if number != "0" else "Before class 1"
    meta = [position] + meta_items(SPAN.findall(meta_html or ""))
    meta_html_out = "".join(f"<span>{item}</span>" for item in meta)
    label = f"Class {number}: " if number != "0" else "Pre-work: "
    header = (
        '<header class="class-head">'
        f'<div class="class-head__num" aria-hidden="true">{number}</div>'
        '<div class="class-head__text">'
        f'<h1 id="{anchor}"><span class="visually-hidden">{label}</span>{title.strip()}</h1>'
        f'<p class="class-head__meta">{meta_html_out}</p>'
        "</div>"
        f"{_stepper(src_uri, m.group(1), classes)}"
        "</header>\n"
    )
    return page_html[: h1.start()] + header + page_html[h1.end():]


LIST_START = re.compile(r"^\s*([-*•]|\d+[.)]|\"\"\"|<|\[|#)")
CODE_BODY = re.compile(r"(<code>)(.*?)(</code>)", re.S)


def reflow_prompt(text: str) -> str:
    """Join lines that were hard-wrapped in the source so prompts wrap naturally on screen
    (and paste into a chat tool as clean paragraphs). Lists, blank lines, short lines and
    delimiters keep their line breaks."""
    lines = text.split("\n")
    out = [lines[0]] if lines else []
    for line in lines[1:]:
        prev = out[-1]
        wrapped = (
            len(prev) >= 50
            and line.strip()
            and not prev.rstrip().endswith((":", '"""'))
            and not LIST_START.match(line)
            and not LIST_START.match(prev)
        )
        if wrapped:
            out[-1] = prev.rstrip() + " " + line.lstrip()
        else:
            out.append(line)
    return "\n".join(out)


def classify_text_blocks(page_html: str) -> str:
    def mark(match: re.Match) -> str:
        pre = match.group(1)
        text = html_lib.unescape(re.sub(r"<[^>]+>", "", pre))
        if DIAGRAM_CHARS.search(text):
            return f'<div class="language-text highlight is-diagram">{pre}'

        def reflow(code: re.Match) -> str:
            body = code.group(2)
            if "<" in body.replace("<span></span>", ""):
                return code.group(0)  # contains markup we shouldn't rewrite
            return code.group(1) + html_lib.escape(reflow_prompt(html_lib.unescape(body)), quote=False) + code.group(3)

        return f'<div class="language-text highlight is-prompt">{CODE_BODY.sub(reflow, pre, count=1)}'

    return TEXT_BLOCK.sub(mark, page_html)


def inline_architecture(page_html: str, img_dir) -> str:
    """Swap architecture <img> tags for the inline SVG so it follows the theme and track colour."""
    def swap(match: re.Match) -> str:
        path = img_dir / match.group(1)
        if not path.is_file():
            return match.group(0)
        return f'<figure class="figure figure--arch">{path.read_text(encoding="utf-8")}</figure>'

    return ARCH_IMG.sub(swap, page_html)


# ---- MkDocs events -------------------------------------------------------------------------

def on_config(config):
    global _img_dir
    from pathlib import Path
    _img_dir = Path(config["docs_dir"]) / "assets" / "img"
    return config


def on_nav(nav, config, files):
    _tracks.clear()
    for page in nav.pages:
        uri = page.file.src_uri
        m = CLASS_PAGE.match(uri)
        if m:
            title = re.sub(r"^\d+\.\s*|^Pre-work:\s*", "", page.title or "")
            _tracks.setdefault(m.group(1), []).append((uri, uri.split("/", 1)[1][:-3] + ".html", title))
    return nav


def on_page_content(html, page, config, files):
    uri = page.file.src_uri
    m = CLASS_PAGE.match(uri)
    if m:
        classes = _tracks.get(m.group(1), [])
        html = class_header(html, uri, classes, total=sum(1 for c in classes if "prework" not in c[0]))
    if _img_dir is not None:
        html = inline_architecture(html, _img_dir)
    return classify_text_blocks(html)


def on_post_page(output, page, config):
    return output.replace("<body ", f'<body data-track="{track_for(page.file.src_uri)}" ', 1)
