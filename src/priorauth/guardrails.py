"""Guardrails that run outside the model, so they hold even when the model is wrong or manipulated."""
from __future__ import annotations

import re

from .models import CriterionFinding, Evidence, Status

INJECTION_PATTERNS = [
    r"ignore (?:all |any )?(?:previous|prior|above) instructions",
    r"disregard (?:the |all )?(?:policy|instructions|rules)",
    r"(?:note|message|instruction)s? (?:to|for) the (?:ai|model|assistant|reviewer bot|ai reviewer)",
    r"you are now",
    r"system prompt",
    r"mark (?:every|all) criteri(?:a|on) as met",
    # Deliberately NOT matching "please approve this request": providers write that legitimately,
    # and a false positive here sends a valid case to manual review.
]
_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.I)

MIN_QUOTE_CHARS = 8


def screen_for_injection(texts: list[str]) -> list[str]:
    """Return suspicious spans. Clinical notes are data; text addressing the AI is a red flag."""
    hits = []
    for text in texts:
        hits += [m.group(0) for m in _INJECTION_RE.finditer(text)]
    return hits


def _norm(s: str) -> str:
    s = s.strip().strip("\"'“”‘’").rstrip(".;,")
    return re.sub(r"\s+", " ", s).lower()


def verify_evidence(evidence: Evidence, sources: dict[str, str]) -> bool:
    """A quote counts only if it appears verbatim in the source it claims to come from."""
    source = sources.get(evidence.source_id)
    quote = _norm(evidence.quote)
    if source is None or len(quote) < MIN_QUOTE_CHARS:
        return False
    return quote in _norm(source)


def enforce_citations(finding: CriterionFinding, sources: dict[str, str]) -> CriterionFinding:
    """Verify every quote. A MET or NOT_MET finding with no verified quote is downgraded to
    NOT_DOCUMENTED: the system never acts on a claim it cannot point to."""
    for ev in finding.evidence:
        ev.verified = verify_evidence(ev, sources)
    if finding.status != Status.NOT_DOCUMENTED and not any(ev.verified for ev in finding.evidence):
        finding.status = Status.NOT_DOCUMENTED
        finding.downgraded = True
        finding.rationale = (finding.rationale + " [downgraded: no verifiable citation]").strip()
    return finding
