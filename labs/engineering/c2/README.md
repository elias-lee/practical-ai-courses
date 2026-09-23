# Lab 2 — A SitRep extractor with validated, structured output

`extract_sitrep(llm, report) -> SitRep` turns a messy field report into data your code can
trust: a versioned prompt, JSON parsing that tolerates ```json fences, schema validation, and a
retry loop that feeds the exact validation errors back to the model (at most 3 attempts).

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `sitrep_schema.py` | The data contract: `SitRep` and `Figure` dataclasses, hand-written validation, and the same contract as a JSON Schema |
| `sitrep_prompts.py` | The prompt as code: `PROMPT_VERSION`, system/user templates, a few-shot example, the repair message |
| `extractor.py` | `strip_fences`, `parse_json`, `extract_sitrep` (the retry loop), `ExtractionError` |
| `test_extractor.py` | Tests using a scripted `FakeLLM` — **no API key and no Pydantic needed** |
| `run_extract.py` | Runs the extractor against a real model |
| `sample_report.md` | A messy, **fictional** field note from Aramu district |

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
pip install pydantic               # optional: for the Pydantic version below
```

## Run the tests (no key needed)

```bash
pytest -q
```

The tests cover a valid reply, a fenced reply, a malformed reply that is fixed on retry (and
check that the error text reached the model), retries exhausted, "not stated" handling, schema
errors with paths, and the prompt itself.

## Run with a real model (needs a key)

Set `MODEL` plus your provider's variables (model names as of 2026 — check your provider):

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini
export OPENAI_API_KEY=...          # never commit keys
python run_extract.py
```

Check the output against the report by hand: is `report_date` "not stated" (the note only
says "Thurs")? Are the 1,200 *households* and ~600 *people* kept as separate figures with
different units? Is Dorra listed under `gaps`?

## The same schema in Pydantic

The lab validates in plain Python so the tests need no packages. In a real project you would
write the contract with Pydantic (v2), which generates the checks, the error messages and the
JSON Schema for you:

```python
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

class Figure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    location: str = Field(min_length=1)
    value: str = Field(min_length=1, description='As written, e.g. "approx 1,200"')
    unit: Literal["households", "people", "families", "not stated"]
    source: str = Field(min_length=1, description="Words quoted from the report")


class SitRep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    district: str = Field(min_length=1)
    report_date: str = Field(pattern=r"^(\d{4}-\d{2}-\d{2}|not stated)$")
    hazard: str = Field(min_length=1)
    severity: Literal["low", "medium", "high", "critical", "not stated"]
    affected: List[Figure]
    priority_needs: List[str]
    response: List[str]
    gaps: List[str]


# Validate a reply (after strip_fences):
try:
    sitrep = SitRep.model_validate_json(text)
except ValidationError as exc:
    errors = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
    # ...feed `errors` back to the model, exactly as extractor.py does

# The JSON Schema for the prompt or a provider's structured-output mode:
schema = SitRep.model_json_schema()
```

With LiteLLM you can also pass the model class to a provider's structured-output mode (as of
2026; support varies by provider and model, so check the LiteLLM docs):

```python
import litellm

response = litellm.completion(model="openai/gpt-4o-mini", messages=messages,
                              response_format=SitRep)
sitrep = SitRep.model_validate_json(response.choices[0].message.content)
```

Keep validating even with a structured-output mode: it guarantees the *shape*, not that the
figures are in the report.

## Stretch challenges

1. **Swap in Pydantic.** Replace `parse_sitrep` with the Pydantic model above, keeping every
   test green. Which error messages got better, and which got worse for the model to act on?
2. **Check figures against the source.** Add a validation rule that every `Figure.source`
   appears verbatim (ignoring case and whitespace) in the report. Write a test with a
   hallucinated figure and make sure the retry loop reports it.
3. **A prompt regression test.** Save three fictional reports and their expected JSON in a
   `cases/` folder. Write a test that runs `extract_sitrep` on each with a `FakeLLM` that
   replays recorded model outputs, then re-record the outputs whenever you bump
   `PROMPT_VERSION`. This is the seed of Class 7's evals.
