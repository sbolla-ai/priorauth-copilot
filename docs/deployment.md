# Deploying in a customer environment

_The default topology for a health plan that requires data to stay in its own cloud account._

## Topology
```
Customer VPC
 ├─ UM intake (portal / fax-OCR / EHR feed) ──► queue
 ├─ priorauth-copilot (container, private subnet, no public ingress)
 │    ├─ PHI redaction + injection screen   (in-process)
 │    ├─ Model endpoint                     (private link to the model provider or a cloud-hosted model)
 │    └─ OTel collector ──► customer's observability stack (redacted attributes only)
 └─ Reviewer UI ◄── recommendations + verified evidence
```

## Checklist
- **Contracts:** BAA in place with the model provider and cloud vendor; zero-data-retention settings confirmed in writing.
- **Secrets:** API keys from the cloud secret manager, injected as env vars; never in code or images.
- **Network:** private subnet, egress allow-listed to the model endpoint only.
- **Logging:** application logs carry case IDs, decisions and flags, never note text. Verify by running `pytest -q` (PHI leak tests) against the deployed image.
- **Release gate:** CI runs `evals/run_evals.py` on the customer's labeled set; a failed safety gate blocks the deploy.
- **Rollout:** shadow mode → assistive mode for a pilot group → wider rollout, with a weekly metrics readout.
- **Rollback:** recommendations are advisory, so turning the copilot off returns reviewers to today's workflow with no data migration.

## Configuration
| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | Model credentials |
| `PRIORAUTH_MODEL` | Model id to use and evaluate |
| `PRIORAUTH_OTEL` | `console` or `otlp` to export traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector endpoint when using `otlp` |
