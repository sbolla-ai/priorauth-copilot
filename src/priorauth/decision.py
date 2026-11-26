"""Deterministic routing. The model extracts evidence; this code (reviewable, testable) picks the route."""
from __future__ import annotations

from .models import CriterionFinding, Decision, Status


def route(policy: dict, findings: list[CriterionFinding], flags: list[str]) -> tuple[Decision, list[str], list[str]]:
    """Return (decision, reasons, missing_criteria).

    - Any safety flag (e.g. prompt injection, unparseable model output) -> REFER_TO_CLINICIAN.
    - Some approval path fully MET with verified evidence -> APPROVE.
    - Every approval path contains a NOT_MET criterion -> REFER_TO_CLINICIAN (a possible
      denial, which only a clinician may decide).
    - Otherwise -> NEEDS_INFO, listing what to request from the provider.
    """
    status = {f.criterion_id: f.status for f in findings}
    paths: list[list[str]] = policy["approve_if_any"]

    if flags:
        return Decision.REFER_TO_CLINICIAN, [f"Safety flag: {f}" for f in flags], []

    for path in paths:
        if all(status.get(c) == Status.MET for c in path):
            return Decision.APPROVE, [f"All criteria met on approval path {'+'.join(path)}."], []

    if all(any(status.get(c) == Status.NOT_MET for c in path) for path in paths):
        not_met = sorted({c for p in paths for c in p if status.get(c) == Status.NOT_MET})
        return (
            Decision.REFER_TO_CLINICIAN,
            [f"Documentation indicates criteria not met: {', '.join(not_met)}. Clinician review required; the AI does not issue denials."],
            [],
        )

    # Request what's missing on the path(s) with no NOT_MET criteria.
    open_paths = [p for p in paths if not any(status.get(c) == Status.NOT_MET for c in p)]
    missing = sorted({c for p in open_paths for c in p if status.get(c) != Status.MET})
    return Decision.NEEDS_INFO, [f"Missing documentation for: {', '.join(missing)}."], missing
