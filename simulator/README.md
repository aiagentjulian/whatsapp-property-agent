# Pearlmont Simulator V1.6

Run the complete scenario suite from the repository root:

```sh
python3 simulator/runner/run.py
```

The runner evaluates Human Support and appointment-ready sales outcomes. `SUPPORT_REQUEST` obtains a scenario-fixture answer while the AI retains ownership and resumes selling. `HANDOFF` records an `APPOINTMENT_HANDOFF`; `MANDATORY_HANDOFF` records a `MANDATORY_OPERATIONAL_HANDOFF`. Both formal handoffs transfer ownership to HUMAN and end the AI session. The primary KPI remains appointment-ready AI success.

The four model roles are configured in `config.json`. The default provider is `codex_cli`, using the authenticated Codex CLI with `gpt-5.6-luna` and Medium reasoning. Each role has a required structured JSON schema. To use the OpenAI API provider instead, set `provider` to `openai_api`; that selectable alternative uses `OPENAI_API_KEY` and the model IDs configured for each role. No non-standard Python packages are required. `run_v1.py` preserves the original V1 runner for historical reproducibility.

Scenario `human_operations` support fixtures are synthetic simulator data, hidden from both the Sales Agent before support and the Customer Simulator. They are not Pearlmont factual Knowledge or claims about live inventory, pricing, CRM, or calendar capability. The runner does not modify Brain or Knowledge.

Run the operator path against fake provider transports before live execution:

```sh
python3 simulator/runner/run.py --dry-run
```

To run selected scenarios, add `--scenario PEA-001` (repeat the option for multiple IDs). Each invocation creates a directory under `reports/` with per-scenario transcript JSON, report JSON/Markdown, and aggregate JSON/Markdown. Run-level and scenario-level accounting records provider/model, calls by role, duration, retry count, and exact token counts when reported by the provider. Token values are left unavailable when the provider does not expose them. Rate limits, usage exhaustion, authentication failures, and unavailable models stop the run before another scenario starts.
