# Pearlmont Simulator V1

Run the complete scenario suite from the repository root:

```sh
python3 simulator/runner/run.py
```

The runner uses the explicit roles/models in `config.json`, reads the existing Brain and Skills, and retrieves at most four matching Pearlmont Knowledge files for each Agent turn. It needs `OPENAI_API_KEY` for live model calls. No non-standard Python packages are required.

Run the same operator path against a fake transport before a live run:

```sh
python3 simulator/runner/run.py --dry-run
```

To run one or more scenarios, add `--scenario PEA-001` (repeat the option for multiple IDs). Each invocation creates a new timestamped directory under `reports/` with JSON transcripts, per-scenario JSON/Markdown reports, and aggregate JSON/Markdown reports. `RUN-*` directories are live results; `DRYRUN-*` directories are transport validation artifacts.

The customer model receives hidden scenario details; the Sales Agent does not. The Judge sees the complete transcript, action/retrieval traces, and the actual retrieved source text. The runner only reads `brain/` and `knowledge/` and never updates them.

After a transient failed scenario, rerun only that case with `--scenario PEA-009`, then merge it into the full run with `python3 simulator/runner/finalize.py --run RUN-DIRECTORY --retry RETRY-DIRECTORY`. To rescore saved transcripts with the retrieved source text after changing Judge guidance, use `python3 simulator/runner/rejudge.py --run RUN-DIRECTORY`; this does not call the Sales Agent or Customer Simulator.
