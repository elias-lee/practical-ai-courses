# Lab 5 — Give the SitRep Assistant tools

A tool harness in about 250 lines of plain Python — no SDK tool-calling helpers — so you can see
every moving part: JSON-schema generation, argument validation, the tool-call loop, errors fed
back to the model, a step budget, an allow-list guardrail, PII redaction, retries and fallbacks.

| File | What it is |
|---|---|
| `llm.py` | The model interface (`messages -> text`) and a LiteLLM adapter |
| `harness.py` | `@tool`, `ToolRegistry`, `run_tool_loop()`, `allow_list()`, `redact_pii()`, `with_retry()`, `with_fallback()` |
| `sitrep_tools.py` | Five SitRep tools over **fictional** Northern Veloria data: `search_reports`, `get_report`, `get_population`, `format_sitrep`, and the dangerous `send_sitrep_email` |
| `test_harness.py` | Tests using a scripted `FakeLLM` — **no API key needed** |
| `run_demo.py` | Runs the loop against a real model |

## Setup

Python 3.11+ recommended (the code also runs on 3.9).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install litellm pytest
```

## Run the tests (no key needed)

```bash
pytest -q
```

All tests should pass. `FakeLLM` returns scripted replies (tool calls as JSON) and records every
message list it receives, so the tests assert on *what the harness sent back to the model*: the
tool result, the error message, the "BLOCKED" notice.

## Run the demo (needs a key)

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<your-deployment-name>`, `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/gpt-4o-mini`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/claude-sonnet-4-5`, `ANTHROPIC_API_KEY` |

```bash
export MODEL=openai/gpt-4o-mini    # model names as of 2026 — check your provider
export OPENAI_API_KEY=...          # never commit keys
python run_demo.py
```

The default request asks the assistant to email the SitRep. The email tool is registered but
blocked by the allow-list, so you should see a `BLOCKED` step and `Emails sent: 0`.

## Native tool calling

The lab uses a tiny JSON protocol so that `FakeLLM` stays a plain `messages -> text` function.
Production code normally uses the provider's native tool calling, where the schemas go in a
`tools=` parameter and the model returns structured `tool_calls`. `Tool.schema` is already in
the right shape:

```python
import litellm
from sitrep_tools import READ_ONLY_TOOLS

tools = [{"type": "function", "function": t.schema} for t in READ_ONLY_TOOLS]
response = litellm.completion(model="openai/gpt-4o-mini", messages=messages, tools=tools)
calls = response.choices[0].message.tool_calls     # list of {id, function: {name, arguments}}
```

## Stretch challenges

1. **Native tool calling.** Write `run_native_tool_loop()` that uses the snippet above instead of
   the JSON protocol, feeding results back as `{"role": "tool", "tool_call_id": ..., "content": ...}`
   messages. Keep the same guardrails, budget and error handling, and compare the two loops on the
   same request.
2. **Human approval instead of a hard block.** Replace the allow-list for `send_sitrep_email`
   with an `approval_gate(tools=["send_sitrep_email"], ask=input)` guardrail that shows the
   recipient and subject and asks a person. Test it by injecting a fake `ask` function.
3. **Expose the tools over MCP.** Using the official MCP Python SDK (`pip install mcp`), wrap
   `search_reports`, `get_report` and `get_population` as an MCP server, and connect to it from
   an MCP-capable client. Which of your docstrings needed rewriting once a different client was
   reading them?
