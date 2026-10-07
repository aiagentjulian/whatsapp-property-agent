# Pearlmont Simulator V1.3

Run the complete scenario suite from the repository root:

```sh
python3 simulator/runner/run.py
```

The default runner evaluates the Human Support Loop as well as appointment-ready sales outcomes. `SUPPORT_REQUEST` obtains a scenario-fixture answer while the AI keeps ownership and resumes the customer conversation. Only formal `HANDOFF` sets the owner to HUMAN and pauses AI. The primary KPI remains appointment-ready AI success; support-enabled paths count when AI uses the verified answer, continues selling, reaches readiness, and performs the appropriate appointment handoff.

The runner uses the model roles in `config.json`, reads the existing Brain and Skills, and retrieves at most four matching Pearlmont Knowledge files per Agent turn. It needs `OPENAI_API_KEY` for live model calls. No non-standard Python packages are required. `run_v1.py` preserves the original V1 runner for historical reproducibility.

Scenario `human_operations` support fixtures are synthetic simulator data, hidden from both the Sales Agent before support and the Customer Simulator. They are not Pearlmont factual Knowledge or claims about live inventory, pricing, CRM, or calendar capability. The runner does not modify Brain or Knowledge.

Run the operator path against fake provider transports before live execution:

```sh
python3 simulator/runner/run.py --dry-run
```

To run selected scenarios, add `--scenario PEA-001` (repeat the option for multiple IDs). Each invocation creates a new timestamped directory under `reports/` with per-scenario transcript JSON, report JSON/Markdown, and aggregate JSON/Markdown. `RUN-V13-*` directories are live results; `DRYRUN-V13-*` directories are transport-validation artifacts. The aggregate directly compares against `RUN-V12-20261007T015000Z`.
