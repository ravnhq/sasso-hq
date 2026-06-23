---
name: bot-safety
description: Make a public Claude bot safe with deterministic guardrails — block prompt-injection on input, redact PII (email/phone/SSN/card) on input and output, and short-circuit blocked messages with a canned reply. Use when hardening a bot for public traffic, adding input/output screening, or filling the chatbot-toolkit Guardrails seam.
---

# Bot Safety

A public bot takes untrusted input and emits model output to real people. The
`Guardrails` seam screens both ends. `HeuristicGuardrails` (in `app/guardrails.py`)
is the real implementation that replaces `NoOpGuardrails`.

## What it does

`screen_input(text) -> GuardResult` and `screen_output(text) -> GuardResult`, both
synchronous. `GuardResult(allowed, text)` carries either possibly-redacted text or,
when blocked, a safe canned reply.

| Stage | Threat | Action |
|-------|--------|--------|
| input | prompt-injection ("ignore previous instructions", "reveal your system prompt", "developer mode", "you are now…") | `allowed=False`, text = canned refusal |
| input | PII (email, phone, US SSN, card-like digits) | `allowed=True`, text redacted with `[REDACTED_*]` |
| output | PII leaking from the model | `allowed=True`, text redacted |

The PII regex/redaction is one shared helper used by both methods — one source of truth.

## How the webhook uses it

Flow: `parse → screen_input → load → brain → screen_output → append → send`.

- Blocked input short-circuits: the canned `guard_in.text` is sent back and the
  **Brain never sees it**. No history is written.
- Allowed input passes its *redacted* `guard_in.text` to the Brain, so the model
  never receives raw PII.
- `guard_out.text` (redacted) is what gets stored and sent — PII can't leak out.

## Why deterministic

Screening is pure heuristics/regex: no network, no LLM-moderation API. That makes it
fast, free, and testable — `tests/test_guardrails.py` asserts exact behavior over
known-bad and known-good inputs. An LLM-moderation layer is a real upgrade for fuzzy
cases (toxicity, nuanced policy), but it adds latency, cost, and nondeterminism. Slot
it in behind the same `Guardrails` protocol when you need it; keep the deterministic
checks as a cheap first line.

## Extending

Add injection phrases to `INJECTION_PATTERNS` and PII shapes to `_PII_RULES`. Keep
SSN before the generic phone rule so `XXX-XX-XXXX` isn't mislabeled. Add a test case
for every new pattern.
