"""Generate the reference-architecture diagrams used across the site.

Writes content/assets/img/reference-architecture.svg (no highlight) and one
reference-architecture-<key>.svg per layer with that layer highlighted, so each
class page can show "where we are".

Run: python scripts/make_architecture_svg.py
"""
from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "assets" / "img"

LAYERS = [
    ("interface", "Interface", "chat · API · email / Teams · human approval screen"),
    ("orchestration", "Orchestration layer", "planner / router · workflow engine · state & checkpoints · budgets & stop rules"),
    ("agents", "Agents", "Intake · Researcher · Analyst · Writer · Reviewer"),
    ("harness", "Harness", "system prompts · tools (MCP) · guardrails · structured outputs · permissions"),
    ("context", "Context & data", "RAG pipeline · vector store · memory · multilingual ingestion"),
    ("models", "Models", "model router · large, small and reasoning models"),
]
CROSS = ["Evals", "Observability", "Security", "Cost"]

W, LAYER_H, GAP, TOP, LEFT, MAIN_W = 780, 58, 10, 20, 20, 560
BG, INK, MUTED = "#ffffff", "#1d2733", "#4b5a6a"
FILL, STROKE = "#eef3f8", "#b9c8d8"
HI_FILL, HI_STROKE = "#1c5d99", "#123f6b"


def layer_rect(i: int, key: str, title: str, detail: str, highlight: str | None) -> str:
    y = TOP + i * (LAYER_H + GAP)
    hi = key == highlight
    fill, stroke = (HI_FILL, HI_STROKE) if hi else (FILL, STROKE)
    title_color, detail_color = ("#ffffff", "#dce9f6") if hi else (INK, MUTED)
    return (
        f'<rect x="{LEFT}" y="{y}" width="{MAIN_W}" height="{LAYER_H}" rx="8" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{2 if hi else 1}"/>'
        f'<text x="{LEFT + 16}" y="{y + 24}" font-size="16" font-weight="700" fill="{title_color}">{escape(title)}</text>'
        f'<text x="{LEFT + 16}" y="{y + 44}" font-size="12.5" fill="{detail_color}">{escape(detail)}</text>'
    )


def svg(highlight: str | None = None) -> str:
    height = TOP * 2 + len(LAYERS) * LAYER_H + (len(LAYERS) - 1) * GAP
    cross_x = LEFT + MAIN_W + 16
    cross_w = W - cross_x - LEFT
    cross_h = height - 2 * TOP
    hi = highlight == "cross"
    cfill, cstroke = (HI_FILL, HI_STROKE) if hi else (FILL, STROKE)
    ccolor = "#ffffff" if hi else INK
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
        f'font-family="-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" role="img">',
        f"<title>Reference architecture of an agentic AI system</title>",
        f'<rect width="{W}" height="{height}" rx="12" fill="{BG}"/>',
    ]
    for i, (key, title, detail) in enumerate(LAYERS):
        parts.append(layer_rect(i, key, title, detail, highlight))
    parts.append(
        f'<rect x="{cross_x}" y="{TOP}" width="{cross_w}" height="{cross_h}" rx="8" '
        f'fill="{cfill}" stroke="{cstroke}" stroke-width="{2 if hi else 1}"/>'
    )
    parts.append(
        f'<text x="{cross_x + cross_w / 2}" y="{TOP + 28}" text-anchor="middle" font-size="13" '
        f'font-weight="700" fill="{ccolor}">Cross-cutting</text>'
    )
    step = (cross_h - 60) / len(CROSS)
    for n, name in enumerate(CROSS):
        y = TOP + 70 + n * step
        parts.append(
            f'<text x="{cross_x + cross_w / 2}" y="{y}" text-anchor="middle" font-size="14" fill="{ccolor}">{name}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reference-architecture.svg").write_text(svg(), encoding="utf-8")
    for key, *_ in LAYERS:
        (OUT / f"reference-architecture-{key}.svg").write_text(svg(key), encoding="utf-8")
    (OUT / "reference-architecture-cross.svg").write_text(svg("cross"), encoding="utf-8")


if __name__ == "__main__":
    main()
