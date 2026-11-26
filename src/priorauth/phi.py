"""PHI minimization: strip direct identifiers before anything reaches a model, a log, or a trace.

Coverage decisions need clinical facts, not identities. Redacting up front means a
prompt-injection or a verbose trace can't leak what the model never saw.
"""
from __future__ import annotations

import re

GENERIC_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "[EMAIL]"),
    (re.compile(r"\(?\b\d{3}\)?[ -]\d{3}-\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b555-\d{4}\b"), "[PHONE]"),
    (re.compile(r"\bMRN[:\s]*[A-Z0-9-]+\b", re.I), "[MRN]"),
    (re.compile(r"\bDOB[:\s]*\d{4}-\d{2}-\d{2}\b", re.I), "[DOB]"),
]


def identifiers_for(patient: dict) -> list[tuple[str, str]]:
    """Patient-specific values to scrub, longest first so full names go before name parts."""
    pairs: list[tuple[str, str]] = []
    name = patient.get("name", "")
    if name:
        pairs.append((name, "[PATIENT]"))
        pairs += [(part, "[PATIENT]") for part in name.split() if len(part) > 2]
    for key, token in (("identifier", "[MRN]"), ("birthDate", "[DOB]"), ("telecom", "[PHONE]")):
        if patient.get(key):
            pairs.append((patient[key], token))
    return sorted(pairs, key=lambda p: len(p[0]), reverse=True)


def redact(text: str, patient: dict | None = None) -> str:
    if patient:
        for value, token in identifiers_for(patient):
            text = re.sub(rf"\b{re.escape(value)}\b", token, text, flags=re.I)
    for pattern, token in GENERIC_PATTERNS:
        text = pattern.sub(token, text)
    return text


def find_leaks(text: str, patient: dict) -> list[str]:
    """Return any direct identifiers that survived into `text` (used by tests and evals)."""
    leaks = [value for value, _ in identifiers_for(patient) if re.search(rf"\b{re.escape(value)}\b", text, re.I)]
    leaks += [m.group(0) for m in re.finditer(r"\b\d{3}-\d{2}-\d{4}\b", text)]
    return leaks
