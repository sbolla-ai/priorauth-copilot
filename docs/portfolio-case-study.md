# Portfolio case study text for sbolla.dev

_Paste into the "Selected deployments" card and the full case-study page. Replace [brackets] with numbers from your own eval runs. Leave any line out until you have its number._

**Card**

> **Prior-Authorization Copilot** · Side project · Healthcare
> An evidence copilot for health-plan reviewers that checks every claim against the source note and never issues a denial.
> Stack: Python, Claude API, OpenTelemetry GenAI, pytest eval gates, GitHub Actions
> Result: 0 unsafe approvals and 0 PHI leaks across [N] synthetic cases, including prompt-injection and hallucinated-citation tests; Claude at [X]% decision agreement.

**Full case study**

- **Problem:** Prior-auth reviewers spend most of their time hunting for evidence, and the biggest AI risk is a confident wrong answer, especially a wrong denial.
- **What I built:** A pipeline that removes patient identifiers before the model call, screens notes for prompt injection, has the model extract per-criterion evidence, verifies every quote verbatim against the source, and routes cases with deterministic, unit-tested rules. There is no denial path in the code.
- **How it ships:** Eval-gated CI (safety gates are absolute), OpenTelemetry GenAI traces with redacted attributes only, a VPC deployment guide, and a customer scoping doc.
- **Outcome:** [Claude decision agreement]% vs. a [baseline]% regex baseline on [N] cases; [held-out results when available]; [median latency] ms and [$cost] per case.
- **What I'd do next:** A held-out set written by someone else, a reviewer UI where overrides feed the eval set, and Synthea-generated FHIR patients.

**Interview story (30 seconds)**
"I didn't trust the model to be right, so I designed the system so being wrong is safe. The model can only point at evidence. If its quote isn't in the note, the claim doesn't count. And the code can't express a denial at all. I proved that with tests where a fake model invents evidence and obeys an injected instruction, and neither can get an approval through."
