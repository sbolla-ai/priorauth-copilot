# Engagement scoping: prior-authorization evidence copilot

_A one-page scoping document written the way I'd bring it to a health-plan customer in week one. The customer and every number below are hypothetical placeholders to replace with discovery data._

## 1. Problem (in the customer's words)
Nurse reviewers spend most of each prior-auth case searching notes for evidence against policy criteria. Turnaround times are under regulatory and provider pressure, and leadership will not accept AI that issues or influences denials without a clinician.

## 2. Scope of the pilot
| In scope | Out of scope (for now) |
|---|---|
| 2–3 high-volume, criteria-driven services (e.g. advanced imaging, DME) | Any automated denial |
| Evidence extraction + routing recommendation for nurse reviewers | Medical-necessity judgment calls without written criteria |
| Read-only access to submitted documentation | Writes to the UM system of record (phase 2) |

## 3. Success criteria (agreed before building)
- **Safety (hard gates):** 0 unsafe approvals and 0 PHI leaks on the eval set; 100% of injection tests routed to a human.
- **Quality:** decision agreement with nurse reviewers ≥ [X]% on a held-out set of [N] real, de-identified historical cases.
- **Efficiency:** median reviewer handling time from [baseline] to [target] minutes, measured in shadow mode.
- **Adoption:** ≥ [X]% of pilot reviewers use the evidence panel daily by week 6.

## 4. Discovery questions
1. Which services have the highest volume and the most objective written criteria?
2. Where do notes come from (fax/OCR, EHR integration, portal) and how clean is the text?
3. What counts as "pended for information" today, and who contacts the provider?
4. Data residency, BAA, and model-hosting constraints (cloud region, VPC, zero data retention)?
5. Who signs off on go-live: medical director, compliance, IT security?

## 5. Plan
| Week | Milestone |
|---|---|
| 1–2 | Discovery, criteria digitization, label 100 historical cases with reviewers |
| 3–4 | Build in customer VPC; eval gate in their CI; red-team review with security |
| 5–6 | Shadow mode: copilot runs silently, outputs compared to reviewer decisions |
| 7–8 | Assistive mode for pilot reviewers; weekly metrics readout to sponsor |

## 6. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Model asserts evidence that isn't there | Verbatim citation check; unverified → not documented |
| Prompt injection via submitted documents | Pre-model screen + data-only prompt framing + human routing |
| PHI exposure in logs or traces | Redaction before model call; trace attributes contain IDs and decisions only |
| Reviewer over-reliance | No approve-without-evidence UI; sampled audits; override tracking |
| Policy drift | Criteria versioned as data; eval suite rerun on every policy change |
