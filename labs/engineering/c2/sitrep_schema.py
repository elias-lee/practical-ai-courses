"""The SitRep data contract: dataclasses plus validation written in plain Python.

In production you would normally use Pydantic (see README.md for the same schema as Pydantic
models). Writing the checks by hand once shows exactly what a validation library does for you:
check types, check allowed values, and collect *every* error with its path so the model can be
told precisely what to fix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, fields
from typing import Any, Dict, List

NOT_STATED = "not stated"
UNITS = ("households", "people", "families", NOT_STATED)
SEVERITIES = ("low", "medium", "high", "critical", NOT_STATED)
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(ValueError):
    """The data does not match the schema. ``errors`` lists every problem, with its path."""

    def __init__(self, errors: List[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


@dataclass
class Figure:
    location: str   # village or district, as named in the report
    value: str      # the number as written: "approx 1,200", "~600"
    unit: str       # one of UNITS; never convert families to people
    source: str     # the words in the report the figure comes from


@dataclass
class SitRep:
    district: str
    report_date: str         # YYYY-MM-DD, or "not stated"
    hazard: str
    severity: str            # one of SEVERITIES
    affected: List[Figure]
    priority_needs: List[str]
    response: List[str]
    gaps: List[str]          # what is unknown or unreachable


# The same contract as a JSON Schema: sent to the model in the prompt, and usable with a
# provider's structured-output mode. test_extractor.py checks it stays in sync with the
# dataclasses above.
SITREP_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["district", "report_date", "hazard", "severity", "affected",
                 "priority_needs", "response", "gaps"],
    "properties": {
        "district": {"type": "string"},
        "report_date": {"type": "string", "description": 'YYYY-MM-DD or "not stated"'},
        "hazard": {"type": "string"},
        "severity": {"type": "string", "enum": list(SEVERITIES)},
        "affected": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["location", "value", "unit", "source"],
                "properties": {
                    "location": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": "string", "enum": list(UNITS)},
                    "source": {"type": "string"},
                },
            },
        },
        "priority_needs": {"type": "array", "items": {"type": "string"}},
        "response": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
    },
}


def _check_keys(obj: Dict[str, Any], expected: List[str], path: str, errors: List[str]) -> None:
    for key in expected:
        if key not in obj:
            errors.append(f"{path}{key}: field required")
    for key in obj:
        if key not in expected:
            errors.append(f"{path}{key}: unexpected field")


def _check_str(value: Any, path: str, errors: List[str]) -> bool:
    if value is None:
        errors.append(f'{path}: must be a string, not null; write "{NOT_STATED}" if the report '
                      "does not say")
        return False
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: must be a non-empty string")
        return False
    return True


def _check_str_list(value: Any, path: str, errors: List[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: must be a list of strings")
        return
    for i, item in enumerate(value):
        _check_str(item, f"{path}[{i}]", errors)


def parse_sitrep(data: Any) -> SitRep:
    """Validate decoded JSON and build a SitRep, or raise ValidationError listing every problem."""
    if not isinstance(data, dict):
        raise ValidationError([f"top level: must be a JSON object, got {type(data).__name__}"])
    errors: List[str] = []
    _check_keys(data, [f.name for f in fields(SitRep)], "", errors)

    for key in ("district", "hazard"):
        if key in data:
            _check_str(data[key], key, errors)
    if "report_date" in data and _check_str(data["report_date"], "report_date", errors):
        date = data["report_date"].strip()
        if date != NOT_STATED and not _ISO_DATE.match(date):
            errors.append(f'report_date: {date!r} must be YYYY-MM-DD or "{NOT_STATED}"')
    if "severity" in data and _check_str(data["severity"], "severity", errors):
        if data["severity"] not in SEVERITIES:
            errors.append(f"severity: {data['severity']!r} must be one of {list(SEVERITIES)}")
    for key in ("priority_needs", "response", "gaps"):
        if key in data:
            _check_str_list(data[key], key, errors)

    figures: List[Figure] = []
    if "affected" in data:
        if not isinstance(data["affected"], list):
            errors.append("affected: must be a list of objects")
        else:
            for i, item in enumerate(data["affected"]):
                path = f"affected[{i}]"
                if not isinstance(item, dict):
                    errors.append(f"{path}: must be an object")
                    continue
                before = len(errors)
                _check_keys(item, [f.name for f in fields(Figure)], f"{path}.", errors)
                for key in ("location", "value", "source"):
                    if key in item:
                        _check_str(item[key], f"{path}.{key}", errors)
                if "unit" in item and item["unit"] not in UNITS:
                    errors.append(f"{path}.unit: {item['unit']!r} must be one of {list(UNITS)}")
                if len(errors) == before:
                    figures.append(Figure(**item))

    if errors:
        raise ValidationError(errors)
    return SitRep(
        district=data["district"], report_date=data["report_date"].strip(),
        hazard=data["hazard"], severity=data["severity"], affected=figures,
        priority_needs=list(data["priority_needs"]), response=list(data["response"]),
        gaps=list(data["gaps"]),
    )
