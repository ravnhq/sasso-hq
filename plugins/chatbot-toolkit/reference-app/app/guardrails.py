import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    text: str  # possibly-redacted text, or a safe response when blocked


class Guardrails(Protocol):
    def screen_input(self, text: str) -> GuardResult: ...
    def screen_output(self, text: str) -> GuardResult: ...


class NoOpGuardrails:
    """Pass-through seam. Slice #4 (bot-safety) replaces this with real screening."""

    def screen_input(self, text: str) -> GuardResult:
        return GuardResult(allowed=True, text=text)

    def screen_output(self, text: str) -> GuardResult:
        return GuardResult(allowed=True, text=text)


CANNED_REFUSAL = "Sorry, I can't help with that request."

INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore (all )?(the )?(previous|prior|above) (instructions|rules)",
        r"disregard (the )?(above|previous|prior)",
        r"forget (all )?(your )?(previous|prior) (instructions|rules)",
        r"you are now\b",
        r"reveal your system prompt",
        r"system prompt",
        r"developer mode",
        r"jailbreak",
    ]
]

# (pattern, placeholder) — order matters: SSN before phone so XXX-XX-XXXX wins.
_PII_RULES = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "[REDACTED_CARD]"),
    (re.compile(r"\+?\d[\d\s().-]{7,}\d"), "[REDACTED_PHONE]"),
]


def _redact_pii(text: str) -> str:
    for pattern, placeholder in _PII_RULES:
        text = pattern.sub(placeholder, text)
    return text


class HeuristicGuardrails:
    """Deterministic, network-free screening: prompt-injection blocking + PII redaction."""

    def screen_input(self, text: str) -> GuardResult:
        if any(p.search(text) for p in INJECTION_PATTERNS):
            return GuardResult(allowed=False, text=CANNED_REFUSAL)
        return GuardResult(allowed=True, text=_redact_pii(text))

    def screen_output(self, text: str) -> GuardResult:
        return GuardResult(allowed=True, text=_redact_pii(text))
