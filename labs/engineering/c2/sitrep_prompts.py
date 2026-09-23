"""Prompts as code: versioned, templated, reviewed and tested like any other source file.

Change the prompt -> bump PROMPT_VERSION -> run the tests (and, from Class 7, the evals).
Log PROMPT_VERSION with every call so any output can be traced to the prompt that made it.
"""
from __future__ import annotations

import json
from string import Template
from typing import Dict, List

from sitrep_schema import NOT_STATED, SITREP_JSON_SCHEMA

PROMPT_VERSION = "sitrep-extract/1.0.0"

# One short worked example (few-shot). It is deliberately about a different place and hazard,
# so the model copies the *pattern*, not the content.
EXAMPLE_REPORT = """landslide in Kopa hills sat night, 2026-02-07. 35 families lost houses,
staying in Kopa church. road to Kopa blocked. need tarps + blankets. no one from our team
has visited the upper village yet."""

EXAMPLE_OUTPUT = {
    "district": "Kopa",
    "report_date": "2026-02-07",
    "hazard": "landslide",
    "severity": "medium",
    "affected": [
        {"location": "Kopa", "value": "35", "unit": "families",
         "source": "35 families lost houses"},
    ],
    "priority_needs": ["tarpaulins", "blankets"],
    "response": [NOT_STATED],
    "gaps": ["upper village not yet visited", "road to Kopa blocked"],
}

SYSTEM_TEMPLATE = Template("""You extract structured data from humanitarian field reports for
a situation report (SitRep). You are careful and literal.

Rules:
1. Use only information in the report. Never estimate, infer or add figures.
2. If the report does not state something, write "$not_stated". Never use null.
3. Copy every figure exactly as written ("approx 1,200", "~600"). Never convert units:
   households, people and families are different units.
4. For each figure, "source" quotes the words in the report it comes from.
5. report_date is YYYY-MM-DD only if the report gives an unambiguous date; otherwise
   "$not_stated".
6. severity is your assessment from the report's content: one of low, medium, high,
   critical, or "$not_stated" if there is too little information.
7. Reply with one JSON object that matches the schema below. No prose, no markdown.

JSON schema:
$schema

Example report:
<report>
$example_report
</report>

Example output:
$example_output""")

USER_TEMPLATE = Template("""Extract the SitRep data from this report.

<report>
$report
</report>""")

REPAIR_TEMPLATE = Template("""Your previous reply could not be used. Problems found:
$errors

Reply again with the complete corrected JSON object only.""")


def build_messages(report: str) -> List[Dict[str, str]]:
    """The system prompt carries the stable instructions; the user message carries the data,
    fenced in <report> tags so the model can tell instructions from material."""
    system = SYSTEM_TEMPLATE.substitute(
        not_stated=NOT_STATED,
        schema=json.dumps(SITREP_JSON_SCHEMA, indent=2),
        example_report=EXAMPLE_REPORT,
        example_output=json.dumps(EXAMPLE_OUTPUT, indent=2),
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": USER_TEMPLATE.substitute(report=report.strip())},
    ]


def repair_message(errors: List[str]) -> Dict[str, str]:
    """The follow-up message for a retry: the exact validation errors, one per line."""
    lines = "\n".join(f"- {e}" for e in errors)
    return {"role": "user", "content": REPAIR_TEMPLATE.substitute(errors=lines)}
