"""Both editions build strictly; instructor pages appear only in the instructor edition."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def build(config: str, out: Path) -> Path:
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "-q", "-f", config, "-d", str(out)],
        cwd=ROOT,
        check=True,
    )
    return out


@pytest.fixture(scope="module")
def learner(tmp_path_factory):
    return build("mkdocs.yml", tmp_path_factory.mktemp("learner"))


@pytest.fixture(scope="module")
def instructor(tmp_path_factory):
    return build("mkdocs.instructor.yml", tmp_path_factory.mktemp("instructor"))


def test_learner_edition_has_no_instructor_pages(learner):
    assert (learner / "index.html").is_file()
    assert not (learner / "instructor").exists()


def test_instructor_edition_has_instructor_pages(instructor):
    assert (instructor / "instructor" / "index.html").is_file()
    assert (instructor / "instructor" / "literacy-c3.html").is_file()


def test_snippet_sources_are_not_built(learner):
    assert not (learner / "shared").exists()


def test_quizzes_are_rendered(learner):
    page = (learner / "literacy" / "c3.html").read_text(encoding="utf-8")
    assert 'class="quiz"' in page
    assert "<!-- quiz:" not in page


def test_no_external_urls_in_assets(learner):
    """Offline requirement: no CDN scripts or web fonts."""
    for page in learner.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        assert "fonts.googleapis.com" not in text, page
        assert 'src="https://' not in text, page
