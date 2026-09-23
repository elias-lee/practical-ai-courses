# Pre-work · Setup

<div class="class-meta" markdown><span>AI Engineering</span><span>1–2 hours, self-paced</span><span>Python</span></div>

!!! abstract "By the end of this pre-work you will be able to"
    - Create an isolated **Python 3.11+** environment for the course labs.
    - Set up an editor with an **AI coding assistant** your organization has approved.
    - Obtain an **API key** through your organization's approved route and store it safely in
      **environment variables**, never in code or Git.
    - Call any provider (Azure OpenAI, OpenAI or Anthropic) through **LiteLLM** by changing one
      model string.
    - Run the **smoke test**: one real model call that prints the reply, token usage and latency,
      plus its tests, which need no key at all.

!!! note "Where we are"
    This is the starting line. Class 1 opens with how models work and how to break a task
    down for them; from Class 2 onwards every lab calls a model from Python. Do this setup
    before Class 1 so that class time goes on ideas, not installation problems.

## 1. What you are setting up, and why

Every lab in this course has the same shape: plain Python code that calls a large language model
(LLM) through one small interface, plus tests that run **without** a model. To do that you need
four things:

| Piece | What it is | Why |
|---|---|---|
| **Python 3.11+** | The language of the labs | Modern syntax and speed; most AI libraries target it (the lab code also runs on 3.9) |
| **A virtual environment** | A private folder of packages for this course | Keeps course packages away from your system Python and other projects |
| **An editor with an AI coding assistant** | Where you write code, with a model suggesting and explaining it | Class 3 is about working *with* a coding assistant; start building the habit now |
| **An API key and LiteLLM** | Your credential for a model provider, and one library that speaks to all of them | Labs are model-agnostic: you choose the provider, the code stays the same |

Budget 1–2 hours. Most of that is waiting: for installers, and for your organization to issue a
key. **Request the key first** (Section 4), then install software while you wait.

## 2. Install Python and create a virtual environment

Check what you have:

```bash
python3 --version        # Windows: py --version
```

If it prints 3.11 or later, you are set. If not, install a current version from python.org, your
organization's software portal, or a package manager (`brew install python@3.12` on macOS,
`winget install Python.Python.3.12` on Windows). On a managed laptop, use the software portal:
it avoids admin-rights problems.

Now get the course files (from the course zip or the repository) and create a **virtual
environment**, a self-contained folder with its own Python and packages:

```bash
cd labs/engineering/prework
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install litellm pytest
```

Your prompt now starts with `(.venv)`. Every time you open a new terminal for the course,
activate the environment again. You can reuse one environment for all the labs.

!!! tip "One environment per project"
    If you install packages without an active virtual environment, they go into your system
    Python. That is how "it works on my machine" problems start. If `pip install` complains
    about an "externally managed environment", that is Python protecting you: activate the
    venv first.

## 3. Editor and AI coding assistant

Any editor works. Visual Studio Code and the JetBrains IDEs (PyCharm) are the most common
choices, and both support the assistants below. Install the Python extension, then point the
editor at the course environment ("Python: Select Interpreter" → the `.venv` folder).

Add an **AI coding assistant**, a model built into the editor that completes code, explains
errors and can make multi-file changes when asked. As of 2026 common options include GitHub
Copilot, Claude Code, Cursor, and the assistants built into JetBrains IDEs. Use the one your
organization has approved and licensed, and check which data it may see: an assistant sends
your code, and sometimes open files, to its provider.

For now, practise three moves on the smoke-test code:

1. Select `check_environment` in `smoke_test.py` and ask the assistant to explain it.
2. Ask it to write one more test for `provider_of`, then read the test before you run it.
3. Break something on purpose, run `pytest`, and ask the assistant to explain the failure.

You will learn to *direct* and *review* these assistants properly in
[Class 3](c3.md). The rule from day one: **you are responsible for every line you commit,
whoever wrote it.**

## 4. Get an API key the right way

An **API key** is a long secret string that identifies you (or your project) to a model
provider. Anyone who has your key can spend your budget and, depending on the setup, see what
you send. Treat it like a password.

**Use your organization's approved route.** Do not sign up for a personal account and put it on
a personal credit card to "get started quickly". Approved routes typically give you:

- a key tied to an **enterprise agreement**, in which the provider does not train on your data
  and keeps it only for a limited period;
- **data residency** (for example, an Azure OpenAI resource in an approved region);
- **spending limits** and monitoring;
- someone to call when the key stops working.

Ask your IT or data team which of these the organization offers (as of 2026, commonly one or
more of Azure OpenAI, OpenAI or Anthropic), and request access for "an internal training
course, fictional data only, low volume". What you receive depends on the provider:

| Provider | What you receive | LiteLLM model string |
|---|---|---|
| **Azure OpenAI** | A key, an **endpoint** URL, an **API version**, and the name of a **deployment** (Azure's name for a model you have enabled) | `azure/<your-deployment-name>` |
| **OpenAI** | A key (ideally a project key with a spending limit) | `openai/gpt-4o-mini` |
| **Anthropic** | A key (ideally in a workspace with a spending limit) | `anthropic/claude-sonnet-4-5` |

Model names are as of 2026 and change often; use whatever small, inexpensive model your
provider recommends for development. For Azure the model string contains *your deployment
name*, not the model's name.

!!! danger "Course data rule"
    Labs use **fictional data only**. Never paste real field reports, names or case data into a
    lab, even with an approved key. See the [data rules on the About page](../about.md#data).

## 5. Environment variables, and never committing keys

Code must never contain a key. Instead, put the key in an **environment variable**, a named
value your shell passes to every program it starts, and have the code read it from there.
LiteLLM reads the standard names automatically.

=== "macOS / Linux"

    ```bash
    export MODEL=openai/gpt-4o-mini
    export OPENAI_API_KEY=sk-...          # paste your key; this stays in this terminal only
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:MODEL = "openai/gpt-4o-mini"
    $env:OPENAI_API_KEY = "sk-..."
    ```

The variables for each provider:

| Provider | Variables |
|---|---|
| Azure OpenAI | `MODEL=azure/<deployment>`, `AZURE_API_KEY`, `AZURE_API_BASE` (the endpoint URL), `AZURE_API_VERSION` |
| OpenAI | `MODEL=openai/<model>`, `OPENAI_API_KEY` |
| Anthropic | `MODEL=anthropic/<model>`, `ANTHROPIC_API_KEY` |

Typing these in every terminal gets old. The usual alternative is a **`.env` file**: a local
text file of `NAME=value` lines that you load before running. The lab folder includes
`.env.example` (a template with no secrets) and a `.gitignore` that excludes `.env`:

```bash
cp .env.example .env                  # then edit .env and fill in one provider block
set -a; source .env; set +a           # macOS/Linux: load it into this terminal
git status                            # .env must NOT appear in the list
```

!!! warning "Never commit a key"
    Keys pushed to a repository, even a private one and even for a minute, should be treated as
    leaked: automated scanners find them within minutes, and Git history keeps them after you
    delete the file. If it happens: **revoke the key immediately** in the provider's console or
    through your IT team, issue a new one, and then clean the history. Revoking comes first;
    cleaning history does not un-leak a key.

Habits that prevent leaks:

- Keep `.env` in `.gitignore` *before* you create it.
- Never paste a key into a notebook cell, a chat with an AI assistant, a screenshot or a ticket.
- Use one key per project, with a spending limit, so a leak is contained and easy to revoke.
- In production, keys live in a **secrets manager** (for example Azure Key Vault), not in files.
  Class 8 covers this.

## 6. LiteLLM: one interface, any provider

Each provider has its own software development kit (SDK) with slightly different request and
response shapes. **LiteLLM** is an open-source library that puts one OpenAI-style interface in
front of all of them. You change the model string; the calling code stays the same:

```python
import litellm

response = litellm.completion(
    model="anthropic/claude-sonnet-4-5",   # or "azure/sitrep-gpt", "openai/gpt-4o-mini"
    messages=[{"role": "user", "content": "Say hello in French."}],
)
print(response.choices[0].message.content)
print(response.usage)                      # prompt_tokens, completion_tokens, total_tokens
```

The labs go one step further. They hide even LiteLLM behind a single type in `llm.py`:

```python
LLM = Callable[[List[Dict[str, str]]], str]   # messages in, text out
```

Any function with that shape can stand in for a model: a LiteLLM call, a cached wrapper, or a
**`FakeLLM`** that returns scripted replies in tests. That is why every lab's tests run with no
key, no network and no cost, and why switching provider is a one-line change. The pre-work's
`llm.py` also has `UsageTrackingLLM`, which keeps the `LLM` shape but remembers the token
usage of its last call.

## 7. Run the smoke test

A **smoke test** is the smallest check that the whole path works: your code, your environment
variables, the network route to the provider, your key and the model. The lab is
`labs/engineering/prework/`:

| File | Role |
|---|---|
| `llm.py` | The `LLM` type, a LiteLLM adapter, and `UsageTrackingLLM` |
| `smoke_test.py` | Checks your variables, makes one call, prints reply, tokens and latency |
| `test_smoke_test.py` | 9 tests using a scripted `FakeLLM`: no key needed |
| `.env.example`, `.gitignore` | Safe configuration template, and the rule that keeps `.env` out of Git |

**Step 1: tests first, no key.**

```bash
pytest -q
```

All nine tests should pass. Open `test_smoke_test.py` and read `FakeLLM`: it returns replies
from a list and records every message it was sent. It also carries a fake `last_usage`, and
the tests inject a fake clock, so even latency is deterministic.

**Step 2: the real call.** With your variables set:

```bash
python smoke_test.py
```

```text
Model:    openai/gpt-4o-mini
Reply:    SitRep Assistant online.
Tokens:   33 in + 6 out = 39
Latency:  0.84 s
```

Before calling, `check_environment()` checks that `MODEL` has a known provider prefix and that
every variable that provider needs is set. It reports *all* missing variables at once instead of
failing on the first. The core of the smoke test is five lines:

```python
def run_smoke_test(llm, clock=time.perf_counter):
    start = clock()
    reply = llm(SMOKE_MESSAGES)
    latency = clock() - start
    usage = getattr(llm, "last_usage", None)   # reported by the provider, if available
    ...
```

Three numbers matter from now on, and they will reappear throughout the course:

- **Tokens in and out.** Providers bill per **token** (a chunk of text of roughly
  three-quarters of an English word), and output tokens usually cost several times more than
  input tokens. [Class 1](c1.md) explains tokens properly.
- **Latency.** Even a one-line reply takes a noticeable fraction of a second, often more.
  Multiply by the number of calls in a multi-agent pipeline (Class 6) and latency becomes a
  design constraint.
- **The reply itself.** Did the model follow "Reply with exactly…"? Run the smoke test three
  times. Is the reply identical each time? Class 1 explains why it may not be.

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'litellm'` | Virtual environment not active, or packages installed elsewhere | `source .venv/bin/activate`, then `pip install litellm pytest`; check `which python` points into `.venv` |
| `error: externally-managed-environment` | Installing into the system Python | Create and activate a venv first (Section 2) |
| `Not ready yet: MODEL is not set` | Variables set in a different terminal, or `.env` not loaded | Set them in *this* terminal, or `set -a; source .env; set +a` |
| `MODEL ... has no known provider prefix` | Model string without `azure/`, `openai/` or `anthropic/` | Use the full LiteLLM string, e.g. `openai/gpt-4o-mini` |
| `AuthenticationError` / HTTP 401 | Wrong, expired or revoked key; key for a different provider; stray spaces or quotes | Re-copy the key; check the variable name matches the provider; ask IT whether it is active |
| `NotFoundError` / HTTP 404 (Azure) | Deployment name wrong, or endpoint/version mismatch | `MODEL=azure/<deployment name>` exactly as in the Azure portal; check `AZURE_API_BASE` and `AZURE_API_VERSION` |
| `NotFoundError` (OpenAI/Anthropic) | Model name misspelt or retired, or not enabled for your project | Use a model your console lists as available |
| `RateLimitError` / HTTP 429 | Too many requests, or quota or spending limit reached | Wait and retry; check quota with your administrator |
| Timeout, `APIConnectionError`, SSL errors | Corporate proxy or firewall blocking the provider | Set `HTTPS_PROXY` as your IT team advises; try off VPN only if policy allows; ask IT to allow the endpoint |
| `Tokens: ... (estimated: provider reported no usage)` | Provider or proxy did not return usage | Harmless for the smoke test; the count is a rough four-characters-per-token estimate |
| Tests fail with `ModuleNotFoundError: llm` | Running pytest from another folder without the lab's `conftest.py` | Run `pytest` inside `labs/engineering/prework/`, or pass the folder path |

If you are still stuck, bring the exact error message (with the key removed) to Class 1. Never
share a key while asking for help, including with an AI assistant.

## Before Class 1

!!! success "Checklist"
    - `python --version` shows 3.11 or later inside the activated `.venv`.
    - `pytest -q` in `labs/engineering/prework/` shows 9 passed.
    - `python smoke_test.py` prints a reply, token counts and latency.
    - `git status` does not list `.env`, and no key appears in any file you might share.
    - Your AI coding assistant can explain `smoke_test.py` to you.

Optional reading: skim the [AI Map](../ai-map.md) to see the architecture the course builds,
and the [Glossary](../glossary.md) for terms you have not met yet.

<div class="complete-toggle"></div>
