"""A small, framework-free evaluation harness for the SitRep Assistant.

    dataset = load_dataset("sitrep_golden.jsonl")
    report  = run_eval(system, dataset, checks=DEFAULT_CHECKS + [judge_check(judge_llm)])
    print(report.summary())
    compare(baseline_report, report)       # did anything get worse?

A *system* is any function ``input text -> output text``. A *check* is any function
``(case, output) -> CheckResult`` that returns None when it does not apply to the case.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from llm import LLM

# --------------------------------------------------------------------------------------
# Dataset
# --------------------------------------------------------------------------------------


class DatasetError(Exception):
    pass


@dataclass
class Case:
    id: str
    input: str
    expected: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


def load_dataset(path: Union[str, Path]) -> List[Case]:
    """Load a JSONL golden dataset: one JSON object per line with id, input, expected, tags."""
    cases: List[Case] = []
    seen = set()
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetError(f"{path}:{lineno}: invalid JSON ({exc})") from exc
        if not raw.get("id") or not isinstance(raw.get("input"), str):
            raise DatasetError(f"{path}:{lineno}: every case needs an 'id' and an 'input' string")
        if raw["id"] in seen:
            raise DatasetError(f"{path}:{lineno}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])
        cases.append(Case(raw["id"], raw["input"], raw.get("expected", {}), raw.get("tags", [])))
    return cases


# --------------------------------------------------------------------------------------
# Rule-based checks: cheap, deterministic, run on every commit
# --------------------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


Check = Callable[[Case, str], Optional[CheckResult]]

HEADINGS = ["Situation overview", "Key figures", "Humanitarian needs", "Response to date",
            "Gaps and constraints"]
OUT_OF_SCOPE_MARKER = "OUT_OF_SCOPE"
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
_CONFLICT_WORDS = ("conflict", "discrepan", "inconsistent", "differ", "contradict", "vary", "varies")


def _numbers(text: str) -> List[str]:
    return [n.replace(",", "").rstrip(".") for n in _NUMBER.findall(text)]


def check_headings(case: Case, output: str) -> Optional[CheckResult]:
    if not case.expected.get("headings"):
        return None
    missing = [h for h in HEADINGS if h.lower() not in output.lower()]
    return CheckResult("headings", not missing, f"missing: {missing}" if missing else "")


def check_max_words(case: Case, output: str) -> Optional[CheckResult]:
    limit = case.expected.get("max_words")
    if not limit:
        return None
    n = len(output.split())
    return CheckResult("max_words", n <= limit, f"{n} words (limit {limit})")


def check_must_include(case: Case, output: str) -> Optional[CheckResult]:
    needed = case.expected.get("must_include")
    if not needed:
        return None
    missing = [s for s in needed if s.lower() not in output.lower()]
    return CheckResult("must_include", not missing, f"missing: {missing}" if missing else "")


def check_must_not_include(case: Case, output: str) -> Optional[CheckResult]:
    banned = case.expected.get("must_not_include")
    if not banned:
        return None
    found = [s for s in banned if s.lower() in output.lower()]
    return CheckResult("must_not_include", not found, f"found: {found}" if found else "")


def check_no_invented_numbers(case: Case, output: str) -> Optional[CheckResult]:
    """Every number in the output must appear in the input (or be explicitly allowed).
    Catches the most dangerous SitRep failure: a plausible figure with no source."""
    if case.expected.get("out_of_scope"):
        return None
    allowed = set(_numbers(case.input)) | {str(n).replace(",", "") for n in case.expected.get("allowed_numbers", [])}
    invented = sorted(set(n for n in _numbers(output) if n not in allowed))
    return CheckResult("no_invented_numbers", not invented, f"not in source: {invented}" if invented else "")


def check_flags_conflict(case: Case, output: str) -> Optional[CheckResult]:
    """Heuristic: a case with conflicting sources must say so. The LLM judge checks the nuance."""
    if not case.expected.get("conflict"):
        return None
    ok = any(w in output.lower() for w in _CONFLICT_WORDS)
    return CheckResult("flags_conflict", ok, "" if ok else "no conflict wording found")


def check_out_of_scope(case: Case, output: str) -> Optional[CheckResult]:
    if "out_of_scope" not in case.expected:
        return None
    said = OUT_OF_SCOPE_MARKER in output
    ok = said == bool(case.expected["out_of_scope"])
    detail = "" if ok else ("should have refused" if not said else "refused an in-scope request")
    return CheckResult("out_of_scope", ok, detail)


DEFAULT_CHECKS: List[Check] = [
    check_headings, check_max_words, check_must_include, check_must_not_include,
    check_no_invented_numbers, check_flags_conflict, check_out_of_scope,
]

# --------------------------------------------------------------------------------------
# LLM as a judge: for qualities code cannot check
# --------------------------------------------------------------------------------------

DEFAULT_RUBRIC = """\
5 - Every figure traceable to a source; conflicts flagged, not resolved; neutral; nothing important missing.
4 - Accurate and neutral, with one minor omission or awkward phrasing.
3 - One material problem: a missing key need, an unflagged conflict, or mildly non-neutral tone.
2 - Several material problems, or one figure that is not in the source.
1 - Misleading: invented figures, followed instructions found inside the reports, or unusable."""

JUDGE_PROMPT = """You are grading a humanitarian situation report (SitRep) written from field reports.
Grade ONLY against the rubric. Length and writing style do not earn points. Do not reward
confident tone. Check every figure in the SitRep against the source.

Rubric:
{rubric}

Source (field reports and request):
<source>
{source}
</source>

SitRep to grade:
<sitrep>
{output}
</sitrep>

First list your reasons, then give the score. Reply with JSON only:
{{"reasons": "<one or two sentences>", "score": <integer 1-5>}}"""


class JudgeParseError(ValueError):
    pass


@dataclass
class JudgeResult:
    score: int
    reasons: str
    passed: bool


def parse_judge_output(text: str, threshold: int = 4) -> JudgeResult:
    """Parse the judge's JSON. Tolerates a ```json fence and surrounding prose; nothing else."""
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    body = fence.group(1) if fence else text
    start, end = body.find("{"), body.rfind("}")
    if start == -1 or end == -1:
        raise JudgeParseError(f"no JSON object in judge output: {text[:80]!r}")
    try:
        data = json.loads(body[start : end + 1])
    except json.JSONDecodeError as exc:
        raise JudgeParseError(f"invalid JSON from judge: {exc}") from exc
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        raise JudgeParseError(f"score must be an integer 1-5, got {score!r}")
    return JudgeResult(score=score, reasons=str(data.get("reasons", "")), passed=score >= threshold)


def llm_judge(llm: LLM, source: str, output: str, rubric: str = DEFAULT_RUBRIC,
              threshold: int = 4) -> JudgeResult:
    prompt = JUDGE_PROMPT.format(rubric=rubric, source=source, output=output)
    return parse_judge_output(llm([{"role": "user", "content": prompt}]), threshold)


def judge_check(llm: LLM, threshold: int = 4, rubric: str = DEFAULT_RUBRIC) -> Check:
    """Wrap the judge as a check. An unparseable verdict is a failed check, never a silent pass."""

    def check(case: Case, output: str) -> Optional[CheckResult]:
        if case.expected.get("out_of_scope"):
            return None
        try:
            verdict = llm_judge(llm, case.input, output, rubric, threshold)
        except JudgeParseError as exc:
            return CheckResult("judge", False, f"judge error: {exc}")
        return CheckResult("judge", verdict.passed, f"score {verdict.score}: {verdict.reasons}")

    return check


def cohens_kappa(a: Sequence[bool], b: Sequence[bool]) -> float:
    """Agreement between two raters (e.g. judge vs human) beyond what chance would give.
    1.0 = perfect, 0 = chance level. Aim for 0.6+ before trusting a judge unsupervised."""
    if len(a) != len(b) or not a:
        raise ValueError("need two equal-length, non-empty label lists")
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


# --------------------------------------------------------------------------------------
# Running an eval and reading the report
# --------------------------------------------------------------------------------------


@dataclass
class CaseResult:
    case_id: str
    tags: List[str]
    output: str
    checks: List[CheckResult]
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.error is None and all(c.passed for c in self.checks)


@dataclass
class Report:
    label: str
    results: List[CaseResult]

    @property
    def pass_rate(self) -> float:
        return sum(r.passed for r in self.results) / len(self.results) if self.results else 0.0

    def check_pass_rates(self) -> Dict[str, Tuple[int, int, float]]:
        """{check name: (passed, applicable, rate)}. Checks that did not apply are not counted."""
        counts: Dict[str, List[int]] = {}
        for r in self.results:
            for c in r.checks:
                counts.setdefault(c.name, [0, 0])
                counts[c.name][0] += int(c.passed)
                counts[c.name][1] += 1
        return {name: (p, n, p / n) for name, (p, n) in counts.items()}

    def tag_pass_rates(self) -> Dict[str, float]:
        by_tag: Dict[str, List[bool]] = {}
        for r in self.results:
            for t in r.tags:
                by_tag.setdefault(t, []).append(r.passed)
        return {t: sum(v) / len(v) for t, v in sorted(by_tag.items())}

    def failures(self) -> List[CaseResult]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        lines = [f"== {self.label}: {sum(r.passed for r in self.results)}/{len(self.results)} cases passed "
                 f"({self.pass_rate:.0%})"]
        for name, (p, n, rate) in sorted(self.check_pass_rates().items()):
            lines.append(f"   {name:<22} {p:>3}/{n:<3} {rate:6.0%}")
        for r in self.failures():
            why = r.error or "; ".join(f"{c.name}: {c.detail}" for c in r.checks if not c.passed)
            lines.append(f"   FAIL {r.case_id}: {why}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "results": [asdict(r) for r in self.results]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Report":
        results = [CaseResult(r["case_id"], r["tags"], r["output"],
                              [CheckResult(**c) for c in r["checks"]], r.get("error"))
                   for r in data["results"]]
        return cls(data["label"], results)

    def save_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=1, ensure_ascii=False), encoding="utf-8")


def run_eval(system: Callable[[str], str], dataset: Sequence[Case],
             checks: Sequence[Check] = DEFAULT_CHECKS, label: str = "run") -> Report:
    """Run every case through the system and every applicable check over the output.
    A crash is recorded as a failed case, never skipped: skipped failures hide regressions."""
    results: List[CaseResult] = []
    for case in dataset:
        try:
            output = system(case.input)
        except Exception as exc:
            results.append(CaseResult(case.id, case.tags, "", [], error=f"{type(exc).__name__}: {exc}"))
            continue
        applied = [r for r in (check(case, output) for check in checks) if r is not None]
        results.append(CaseResult(case.id, case.tags, output, applied))
    return Report(label, results)


# --------------------------------------------------------------------------------------
# Regression detection
# --------------------------------------------------------------------------------------


@dataclass
class Comparison:
    newly_failing: List[str]
    newly_passing: List[str]
    check_deltas: Dict[str, float]
    pass_rate_delta: float

    @property
    def is_regression(self) -> bool:
        return bool(self.newly_failing)

    def summary(self) -> str:
        verdict = "REGRESSION" if self.is_regression else "no regression"
        return (f"{verdict}: pass rate {self.pass_rate_delta:+.0%}; "
                f"newly failing {self.newly_failing}; newly passing {self.newly_passing}")


def compare(baseline: Report, candidate: Report) -> Comparison:
    """Case-by-case comparison. A higher overall score can still hide a regression: an
    improvement on five cases does not excuse breaking the one that matters."""
    before = {r.case_id: r.passed for r in baseline.results}
    after = {r.case_id: r.passed for r in candidate.results}
    common = [cid for cid in before if cid in after]
    newly_failing = [cid for cid in common if before[cid] and not after[cid]]
    newly_passing = [cid for cid in common if not before[cid] and after[cid]]
    b_rates, c_rates = baseline.check_pass_rates(), candidate.check_pass_rates()
    deltas = {name: c_rates[name][2] - b_rates[name][2] for name in b_rates if name in c_rates}
    return Comparison(newly_failing, newly_passing, deltas, candidate.pass_rate - baseline.pass_rate)
