from pathlib import Path

import pytest

from quiz import QuizError, expand_quiz_markers, load_quiz, render_quiz, validate_quiz

FIXTURES = Path(__file__).parent / "fixtures" / "quizzes"


def question(**overrides):
    q = {
        "id": "q1",
        "question": "Pick one",
        "options": [
            {"text": "A", "correct": True, "why": "Because A."},
            {"text": "B", "correct": False, "why": "Not B."},
        ],
    }
    q.update(overrides)
    return q


def test_load_valid_quiz():
    questions = load_quiz(FIXTURES / "demo" / "c1.yml")
    assert questions[0]["id"] == "demo-c1-q1"
    assert len(questions[0]["options"]) == 2


def test_missing_why_is_rejected():
    q = question()
    del q["options"][1]["why"]
    with pytest.raises(QuizError, match="q1"):
        validate_quiz([q], "demo/c1")


def test_no_correct_option_is_rejected():
    q = question()
    q["options"][0]["correct"] = False
    with pytest.raises(QuizError, match="exactly one correct"):
        validate_quiz([q], "demo/c1")


def test_two_correct_options_are_rejected():
    q = question()
    q["options"][1]["correct"] = True
    with pytest.raises(QuizError, match="exactly one correct"):
        validate_quiz([q], "demo/c1")


def test_single_option_is_rejected():
    q = question()
    q["options"] = q["options"][:1]
    with pytest.raises(QuizError, match="at least 2 options"):
        validate_quiz([q], "demo/c1")


def test_duplicate_ids_are_rejected():
    with pytest.raises(QuizError, match="duplicate"):
        validate_quiz([question(), question()], "demo/c1")


def test_render_escapes_html():
    html = render_quiz([question(question="<script>x</script>")], "demo/c1")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_render_converts_backticks_to_code():
    html = render_quiz([question(question="What does `max_steps` do?")], "demo/c1")
    assert "<code>max_steps</code>" in html


def test_render_contract():
    html = render_quiz([question()], "demo/c1")
    assert 'data-quiz-id="demo/c1"' in html
    assert 'data-qid="q1"' in html
    assert html.count('class="quiz-option"') == 2
    assert 'data-correct="true"' in html
    assert html.count('class="quiz-why" hidden') == 2
    assert 'class="quiz-score"' in html


def test_marker_expansion():
    md = "Intro\n\n<!-- quiz: demo/c1 -->\n\nOutro"
    out = expand_quiz_markers(md, FIXTURES)
    assert 'data-quiz-id="demo/c1"' in out
    assert "<!-- quiz:" not in out
    assert out.startswith("Intro") and out.endswith("Outro")


def test_unknown_quiz_is_an_error():
    with pytest.raises(QuizError, match="nope/c9"):
        expand_quiz_markers("<!-- quiz: nope/c9 -->", FIXTURES)
