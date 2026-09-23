"""MkDocs hook: turn `<!-- quiz: course/cN -->` markers into interactive quizzes.

Quiz data lives in `quizzes/<course>/<cN>.yml`. Interactivity is added in the
browser by `content/assets/js/quiz.js`, which relies on the HTML produced here.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import yaml

MARKER = re.compile(r"<!--\s*quiz:\s*([\w\-/]+)\s*-->")
BACKTICKS = re.compile(r"`([^`]+)`")


class QuizError(Exception):
    pass


def validate_quiz(questions: list, source: str) -> None:
    if not isinstance(questions, list) or not questions:
        raise QuizError(f"{source}: quiz must be a non-empty list of questions")
    seen = set()
    for q in questions:
        qid = q.get("id", "<missing id>")
        where = f"{source} [{qid}]"
        if "id" not in q or not q.get("question"):
            raise QuizError(f"{where}: every question needs an id and question text")
        if qid in seen:
            raise QuizError(f"{where}: duplicate question id")
        seen.add(qid)
        options = q.get("options") or []
        if len(options) < 2:
            raise QuizError(f"{where}: needs at least 2 options")
        for opt in options:
            if not opt.get("text") or not opt.get("why"):
                raise QuizError(f"{where}: every option needs text and why")
        if sum(1 for opt in options if opt.get("correct") is True) != 1:
            raise QuizError(f"{where}: needs exactly one correct option")


def load_quiz(path: Path) -> list[dict]:
    questions = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    validate_quiz(questions, str(path))
    return questions


def _inline(text: str) -> str:
    """Escape text, then render `backtick` spans as <code>."""
    return BACKTICKS.sub(r"<code>\1</code>", html.escape(str(text).strip()))


def render_quiz(questions: list[dict], quiz_id: str) -> str:
    parts = [f'<div class="quiz" data-quiz-id="{html.escape(quiz_id)}">']
    for n, q in enumerate(questions, 1):
        parts.append(f'<div class="quiz-q" data-qid="{html.escape(q["id"])}">')
        parts.append(
            f'<p class="quiz-question"><span class="quiz-num">{n}</span> {_inline(q["question"])}</p>'
        )
        parts.append('<ol class="quiz-options">')
        for opt in q["options"]:
            correct = "true" if opt.get("correct") is True else "false"
            parts.append(
                f'<li><button type="button" class="quiz-option" data-correct="{correct}">'
                f'{_inline(opt["text"])}</button>'
                f'<div class="quiz-why" hidden>{_inline(opt["why"])}</div></li>'
            )
        parts.append("</ol></div>")
    parts.append('<p class="quiz-score" aria-live="polite"></p></div>')
    return "\n".join(parts)


def expand_quiz_markers(markdown: str, quizzes_dir: Path) -> str:
    def replace(match: re.Match) -> str:
        quiz_id = match.group(1)
        path = Path(quizzes_dir) / f"{quiz_id}.yml"
        if not path.is_file():
            raise QuizError(f"quiz '{quiz_id}' not found at {path}")
        return render_quiz(load_quiz(path), quiz_id)

    return MARKER.sub(replace, markdown)


def on_page_markdown(markdown, page, config, files):
    quizzes_dir = Path(config.config_file_path).parent / "quizzes"
    return expand_quiz_markers(markdown, quizzes_dir)
