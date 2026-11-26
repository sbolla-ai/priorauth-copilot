"""Core data types. Plain dataclasses keep the dependency footprint small for regulated deployments."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Decision(str, Enum):
    """The only outcomes the copilot may recommend.

    There is deliberately no DENY: any case that might end in a denial is routed
    to a licensed clinician. The AI reads, code decides the route, a human decides the outcome.
    """

    APPROVE = "APPROVE"
    NEEDS_INFO = "NEEDS_INFO"
    REFER_TO_CLINICIAN = "REFER_TO_CLINICIAN"


class Status(str, Enum):
    MET = "met"
    NOT_MET = "not_met"
    NOT_DOCUMENTED = "not_documented"


@dataclass
class Evidence:
    source_id: str
    quote: str
    verified: bool = False


@dataclass
class CriterionFinding:
    criterion_id: str
    status: Status
    evidence: list[Evidence] = field(default_factory=list)
    rationale: str = ""
    downgraded: bool = False  # True if status was lowered because a citation failed verification


@dataclass
class Recommendation:
    case_id: str
    policy_id: str
    decision: Decision
    findings: list[CriterionFinding]
    reasons: list[str]
    missing_criteria: list[str]
    flags: list[str]
    summary: str
    extractor: str
    model: str | None = None
    latency_ms: float = 0.0
    usage: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["decision"] = self.decision.value
        for f in d["findings"]:
            f["status"] = f["status"].value if isinstance(f["status"], Status) else f["status"]
        return d
