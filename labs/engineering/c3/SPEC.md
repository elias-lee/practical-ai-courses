# SPEC — SitRep Summarizer CLI (v1)

**Status:** agreed · **Owner:** your pair · **Data:** fictional only (Northern Veloria province)

This is the written contract for the app in this folder. It was written *before* the code.
Every requirement below has a test in `test_app.py` (see the table at the end). If you, or your
AI coding assistant, change behaviour, change this spec and the tests first.

## 1. Purpose

Duty officers paste messy field reports into a file and need a short, neutral summary they can
check in under a minute. The tool summarizes; a human still reads the reports and signs off.

## 2. Interface

```text
python app.py summarize <reports-file> [--max-words N] [--max-cost USD]
```

- Prints the summary to **stdout**.
- Prints one usage line to **stderr**, e.g.
  `calls=1 input_tokens=512 output_tokens=140 cost_usd=0.000161`.
- The model is chosen with the `MODEL` environment variable (for example
  `openai/gpt-4o-mini`, `azure/<deployment>`, `anthropic/<model>`).

| Exit code | Meaning |
|---|---|
| 0 | Summary printed |
| 1 | Configuration problem (e.g. `MODEL` not set) |
| 2 | Bad input (missing, empty or too large file) |
| 3 | Model unavailable after retries, or budget exceeded |

## 3. Requirements

**R1 · Input validation.** Reject a missing file, an empty (whitespace-only) file, or a file
longer than `MAX_INPUT_CHARS` (20,000 characters) *before* calling the model.

**R2 · Prompt.** Send exactly two messages: a fixed system prompt, and a user message that
contains the reports verbatim between `<reports>` and `</reports>` tags plus the word limit.
The system prompt must require: figures copied as written, conflicting figures flagged (never
silently resolved), `not stated` for missing information, no invented facts.

**R3 · Retries.** Retry **transient** errors (rate limits, timeouts, connection and 5xx
errors) up to `retries` times (default 3) with exponential backoff: 1 s, 2 s, 4 s … capped at
30 s, plus up to 10% random jitter. Never retry other errors (bad request, authentication,
content filter): they propagate immediately.

**R4 · Give up loudly.** When retries are exhausted, raise `RetryError` naming the number of
attempts and chaining the last error. The CLI prints the error and exits with code 3.

**R5 · Timeouts.** Every real model call has a timeout (default 60 s); a timeout counts as a
transient error.

**R6 · Cost tracking.** Accumulate, across all calls in a run: number of calls, input tokens,
output tokens and estimated cost in USD, using per-million-token prices from
`PRICE_IN_PER_MTOK` and `PRICE_OUT_PER_MTOK` (defaults 0.15 and 0.60, illustrative only). Use
the provider's reported token counts when available; otherwise estimate 1 token ≈ 4
characters.

**R7 · Budget.** If `--max-cost` is given and the accumulated cost has reached it, refuse the
next call with `BudgetExceeded` (exit code 3). No call is made after the budget is hit.

**R8 · Secrets.** API keys are read only from environment variables (or a local `.env` file
that is listed in `.gitignore`). Keys are never printed, logged or passed on the command line.

## 4. Non-goals (v1)

Streaming output, a web UI, saving summaries, multiple files per run, translation.

## 5. Acceptance tests

| Requirement | Test(s) in `test_app.py` |
|---|---|
| R1 | `test_summarize_rejects_empty_input`, `test_summarize_rejects_oversized_input`, `test_cli_bad_input_exit_code` |
| R2 | `test_summarize_sends_system_prompt_and_reports` |
| R3 | `test_retry_succeeds_after_transient_errors`, `test_backoff_is_exponential_and_capped`, `test_non_transient_error_is_not_retried`, `test_provider_style_errors_are_recognised` |
| R4 | `test_gives_up_after_n_retries`, `test_cli_exit_code_when_model_unavailable` |
| R5 | covered by `llm.litellm_llm(timeout=...)`; `test_provider_style_errors_are_recognised` checks a timeout is transient |
| R6 | `test_cost_accumulates_across_calls`, `test_tracked_llm_estimates_tokens`, `test_cli_prints_summary_and_usage` |
| R7 | `test_budget_blocks_the_next_call` |
| R8 | review checklist item; `.gitignore` in this folder |
