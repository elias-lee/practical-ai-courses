"""Generate the reference-architecture diagrams used across the site.

Writes content/assets/img/reference-architecture.svg (no highlight) and one
reference-architecture-<key>.svg per layer with that layer highlighted, so each
class page can show "where we are".

The SVGs are included inline in pages (e.g. content/ai-map.md), so they use the site's
diagram classes (dg-box, dg-label, ...) instead of fixed colours and follow light/dark
mode and the course's track colour.

Run: python scripts/make_architecture_svg.py
"""
from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "assets" / "img"

LAYERS = [
    ("interface", "Interface", "chat, API, email, human approval screen"),
    ("orchestration", "Orchestration layer", "planner and router, workflow engine, state, checkpoints, budgets, stop rules"),
    ("agents", "Agents", "Intake, Researcher, Analyst, Writer, Reviewer"),
    ("harness", "Harness", "system prompts, tools (MCP), guardrails, structured outputs, permissions"),
    ("context", "Context & data", "RAG pipeline, vector store, memory, multilingual ingestion"),
    ("models", "Models", "model router; large, small and reasoning models"),
]
CROSS = ["Evals", "Observability", "Security", "Cost"]
NAMES = dict({key: title for key, title, _ in LAYERS}, cross="the cross-cutting concerns")

W, LAYER_H, GAP, TOP, LEFT, MAIN_W = 700, 58, 10, 4, 4, 530


def svg(highlight: str | None = None) -> str:
    height = TOP * 2 + len(LAYERS) * LAYER_H + (len(LAYERS) - 1) * GAP
    title = "Reference architecture of an agentic AI system"
    if highlight:
        title += f", with {NAMES[highlight]} highlighted"
    tid = f"arch-{highlight or 'all'}-t"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" role="img" aria-labelledby="{tid}">',
        f'<title id="{tid}">{escape(title)}</title>',
    ]
    for i, (key, name, detail) in enumerate(LAYERS):
        y = TOP + i * (LAYER_H + GAP)
        box = "dg-box dg-box--accent" if key == highlight else "dg-box"
        label = "dg-accent-text" if key == highlight else "dg-label"
        parts.append(f'<rect class="{box}" x="{LEFT}" y="{y}" width="{MAIN_W}" height="{LAYER_H}" rx="7"/>')
        parts.append(f'<text class="{label}" x="{LEFT + 16}" y="{y + 23}" style="font-size:15px">{escape(name)}</text>')
        parts.append(f'<text class="dg-note" x="{LEFT + 16}" y="{y + 43}" style="font-size:12.5px">{escape(detail)}</text>')
    cross_x = LEFT + MAIN_W + 14
    cross_w = W - cross_x - LEFT
    cross_h = height - 2 * TOP
    box = "dg-box dg-box--accent" if highlight == "cross" else "dg-box dg-box--muted"
    label = "dg-accent-text" if highlight == "cross" else "dg-label"
    parts.append(f'<rect class="{box}" x="{cross_x}" y="{TOP}" width="{cross_w}" height="{cross_h}" rx="7"/>')
    parts.append(f'<text class="{label}" x="{cross_x + cross_w / 2}" y="{TOP + 26}" text-anchor="middle">Cross-cutting</text>')
    step = (cross_h - 60) / len(CROSS)
    for n, name in enumerate(CROSS):
        parts.append(
            f'<text class="dg-note" x="{cross_x + cross_w / 2}" y="{TOP + 72 + n * step}" '
            f'text-anchor="middle" style="font-size:13px">{name}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reference-architecture.svg").write_text(svg(), encoding="utf-8")
    for key in [k for k, *_ in LAYERS] + ["cross"]:
        (OUT / f"reference-architecture-{key}.svg").write_text(svg(key), encoding="utf-8")


if __name__ == "__main__":
    main()
