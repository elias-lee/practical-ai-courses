"""The courses are audience-agnostic and must not read as written for one employer.

International bodies may be named only as world context, alongside the governance item
being described (e.g. the Global Digital Compact). Any other mention fails this test.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNED = ["content", "quizzes", "labs", "hooks", "scripts", "README.md", "mkdocs.yml", "mkdocs.instructor.yml"]
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".mjs", ".js", ".jsonl", ".json", ".txt", ".sh", ".svg", ".css", ".html"}

UN_MENTION = re.compile(r"\bUN\b|United Nations|\bU\.N\.|UNTERM")
GOVERNANCE_CONTEXT = re.compile(
    r"Global Digital Compact|Member States|General Assembly|Scientific Panel|Global Dialogue|UNESCO"
)


def scanned_files():
    for entry in SCANNED:
        path = ROOT / entry
        if path.is_file():
            yield path
        else:
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in TEXT_SUFFIXES and "__pycache__" not in f.parts:
                    yield f


def test_un_appears_only_as_governance_context():
    offending = []
    for f in scanned_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if UN_MENTION.search(line) and ("UNTERM" in line or not GOVERNANCE_CONTEXT.search(line)):
                offending.append(f"{f.relative_to(ROOT)}:{n}: {line.strip()[:120]}")
    assert not offending, "Audience-specific UN references:\n" + "\n".join(offending)
