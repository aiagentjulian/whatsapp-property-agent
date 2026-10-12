#!/usr/bin/env python3
"""Paired, offline-from-WhatsApp Sales Core V2/V3 conversation experiment."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "simulator"
sys.path.insert(0, str(ROOT))
from app.agent import SalesAgent  # noqa: E402
from app.config import get_config, load_env_file  # noqa: E402
from app.provider import PROFILE_FIELDS, OpenAIProvider  # noqa: E402
from app.sales_core_v3 import SalesCoreV3  # noqa: E402

MODEL = "gpt-6-luna"
INPUT_RATE = 0.10
CACHED_RATE = 0.01
OUTPUT_RATE = 0.50
SCORE_DIMENSIONS = [
    "customer_understanding", "contextual_continuity", "sales_judgment", "value_relevance",
    "question_quality", "objection_handling", "repetition_control", "factual_accuracy",
    "viewing_timing", "interest_without_pressure", "naturalness",
]

CUSTOMER_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "message": {"type": "string"}, "done": {"type": "boolean"},
    "ending_reason": {"type": ["string", "null"]},
}, "required": ["message", "done", "ending_reason"]}
JUDGE_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "winner": {"type": "string", "enum": ["A", "B", "TIE"]},
    "scores": {"type": "object", "additionalProperties": False,
               "properties": {side: {"type": "object", "additionalProperties": False,
                                     "properties": {key: {"type": "integer", "minimum": 1, "maximum": 5}
                                                    for key in SCORE_DIMENSIONS},
                                     "required": SCORE_DIMENSIONS} for side in ("A", "B")},
               "required": ["A", "B"]},
    "stronger_examples": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {"side": {"type": "string", "enum": ["A", "B"]}, "turn": {"type": "integer"},
                       "evidence": {"type": "string"}, "why_better": {"type": "string"}},
        "required": ["side", "turn", "evidence", "why_better"]}},
    "weaker_examples": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {"side": {"type": "string", "enum": ["A", "B"]}, "turn": {"type": "integer"},
                       "evidence": {"type": "string"}, "why_worse": {"type": "string"}},
        "required": ["side", "turn", "evidence", "why_worse"]}},
    "simulator_quality": {"type": "string"},
    "factuality_findings": {"type": "array", "items": {"type": "string"}},
    "summary": {"type": "string"},
}, "required": ["winner", "scores", "stronger_examples", "weaker_examples", "simulator_quality", "factuality_findings", "summary"]}


class API:
    def __init__(self, config, dry=False):
        self.config = config
        self.dry = dry
        self.records = []

    def request(self, role, system, user, schema, name, max_tokens=1200):
        start = time.monotonic()
        if self.dry:
            payload = self.fake(role, name, user, schema)
            usage = {"input_tokens": 12, "output_tokens": 6, "total_tokens": 18, "cached_tokens": 0}
        else:
            config = self.config
            body = {"model": config["model"], "reasoning": {"effort": config["reasoning"]},
                    "input": [{"role": "system", "content": [{"type": "input_text", "text": system}]},
                              {"role": "user", "content": [{"type": "input_text", "text": user}]}],
                    "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
                    "max_output_tokens": max_tokens, "store": False}
            req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(),
                    headers={"Authorization": "Bearer " + config["api_key"], "Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=180) as response:
                    result = json.load(response)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")
                self._record(role, {}, time.monotonic() - start, "FAILED")
                raise RuntimeError("HTTP %s: %s" % (exc.code, detail[:1000]))
            usage = self._usage(result.get("usage") or {})
            if result.get("status") not in (None, "completed"):
                self._record(role, usage, time.monotonic() - start, "INCOMPLETE")
                raise RuntimeError("Responses API returned incomplete output: %s (%s)" %
                                   (result.get("status"), (result.get("incomplete_details") or {}).get("reason", "no reason reported")))
            raw = result.get("output_text")
            if not raw:
                raw = next((x.get("text") for item in result.get("output", []) for x in item.get("content", [])
                            if x.get("type") == "output_text"), None)
            if not raw:
                self._record(role, usage, time.monotonic() - start, "FAILED")
                raise RuntimeError("No structured output returned")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                self._record(role, usage, time.monotonic() - start, "INVALID_JSON")
                raise
        duration = round(time.monotonic() - start, 3)
        self._record(role, usage, duration, "COMPLETED")
        return payload, usage, duration

    @staticmethod
    def _usage(usage):
        details = usage.get("input_tokens_details") or {}
        return {"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                "total_tokens": usage.get("total_tokens"), "cached_tokens": details.get("cached_tokens", 0)}

    def _record(self, role, usage, duration, outcome):
        self.records.append({"role": role, "transport": "fake" if self.dry else "responses_api", "model": MODEL,
                             "reasoning": self.config["reasoning"], "usage": usage,
                             "latency_seconds": round(duration, 3), "outcome": outcome})

    @staticmethod
    def fake(role, name, user, schema):
        if role == "sales_strategy":
            return {"customer_intent": "The customer is exploring.", "known_customer_context": [],
                    "unresolved_items": [], "buyer_signal": "QUESTION", "immediate_objective": "Answer clearly.", "knowledge_query": None}
        if role == "sales_v2" or role == "sales_v3":
            return {"action": "REPLY", "sales_move": "ANSWER", "buyer_signal": "QUESTION",
                    "reply": "Thanks for asking. I can share verified details and check anything current that is not confirmed.",
                    "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                    "handoff_reason": None, "handoff_details": None}
        if role == "customer_simulator":
            try:
                state = json.loads(user)
                count = len([m for m in state["history"] if m["speaker"] == "customer"])
            except Exception:
                count = 0
            return {"message": "Thanks, that helps. I will think about it.", "done": True, "ending_reason": "dry-run transport check"}
        return {"winner": "TIE", "scores": {side: {key: 3 for key in SCORE_DIMENSIONS} for side in ("A", "B")},
                "stronger_examples": [], "weaker_examples": [], "simulator_quality": "Transport smoke only; not a quality result.",
                "factuality_findings": [], "summary": "dry-run transport check"}


class V3EvalProvider:
    def __init__(self, api): self.api = api
    def request(self, name, schema, system, user, max_output_tokens):
        if name == "sales_strategy_v3":
            return self.api.request("sales_strategy", system, user, schema, name, max_output_tokens)
        return self.api.request("sales_v3", system, user, schema, name, max_output_tokens)


class V2EvalProvider:
    def __init__(self, config, api): self.inner = None if api.dry else OpenAIProvider(config); self.api = api
    def decide(self, system, user):
        start = time.monotonic()
        if self.api.dry:
            decision = self.api.fake("sales_v2", "property_agent_decision", user, self.inner_schema())
            usage = {"input_tokens": 12, "output_tokens": 6, "total_tokens": 18, "cached_tokens": 0}
        else:
            try:
                decision, usage = self.inner.decide(system, user)
            except Exception:
                self.api.records.append({"role": "sales_v2", "transport": "responses_api", "model": MODEL,
                                         "reasoning": self.api.config["reasoning"], "usage": {},
                                         "latency_seconds": round(time.monotonic() - start, 3), "outcome": "FAILED"})
                raise
            usage = dict(usage)
            usage["cached_tokens"] = ((usage.get("input_tokens_details") or {}).get("cached_tokens", 0))
        self.api.records.append({"role": "sales_v2", "transport": "fake" if self.api.dry else "responses_api", "model": MODEL, "reasoning": self.api.config["reasoning"],
                                 "usage": usage, "latency_seconds": round(time.monotonic() - start, 3), "outcome": "COMPLETED"})
        return decision, usage

    @staticmethod
    def inner_schema():
        from app.provider import agent_schema
        return agent_schema()


class CapturingV3(V3EvalProvider):
    pass


def initial_profile():
    return {"purchase_purpose": "UNKNOWN", "sales_stage": "UNDERSTAND", "intent_level": "LOW",
            "appointment_readiness": "NOT_READY", "next_objective": "Answer the enquiry helpfully."}


def prompts(scenario, side):
    customer = """Act as this buyer in a Malaysian WhatsApp conversation. Persona: %s\nPrivate motives and known facts: %s\n\nReact to the actual last Agent message. Reveal personal details progressively, only when natural. Do not give the sales agent this hidden persona or motives in your messages. Keep language realistic and concise; use informal English or code-switching only when it fits. Good answers can increase trust; ignoring a direct question, repeating facts, inventing claims or pressuring should reduce it. Do not automatically accept every polite answer. Do not terminate after 'ok', 'maybe' or 'I guess so'. Aim for 6–10 customer turns; end earlier only for clear disengagement, a genuine hard mismatch, or a natural completed sales journey. After 6 turns, decide naturally whether to continue or finish. Output a realistic next customer message and whether the conversation is actually over.""" % (scenario["persona"], scenario["facts"])
    judge = """You are a blind sales-quality reviewer. The two transcripts are anonymized as Agent A and Agent B; do not infer or guess which system produced either. Compare the complete conversations against the hidden buyer truth. Score each 1–5 on: customer understanding, contextual continuity, judgment, value relevance, question necessity, objection handling, repetition control, factual accuracy, viewing timing, interest without pressure, and naturalness. Cite specific turn numbers and short transcript evidence. Reward honest recognition of uncertainty and mismatch. Check if the simulator behaved realistically rather than being automatically cooperative or satisfied. State comparative winner as A, B or TIE. Do not overvalue appointment conversion where it would be inappropriate."""
    return customer, judge


def run_conversation(scenario, architecture, api, config, checkpoint):
    if checkpoint and checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if saved.get("status") == "COMPLETED":
            return saved
    prior_records = []
    if checkpoint and checkpoint.exists() and saved.get("transcript"):
        history = saved["transcript"]
        profile = saved.get("final_profile") or initial_profile()
        supports = saved.get("unresolved_offline_support", [])
        actions = saved.get("agent_actions", [])
        customer_turns = saved.get("customer_turns", 1)
        prior_records = saved.get("provider_calls", [])
    else:
        history = [{"turn": 0, "speaker": "customer", "message": scenario["opening"]}]
        profile = initial_profile()
        supports = []
        actions = []
        customer_turns = 1
    metrics_start = len(api.records)
    system, _ = prompts(scenario, "")
    core = SalesAgent(config, provider=V2EvalProvider(config, api)) if architecture == "V2" else SalesCoreV3(config, provider=CapturingV3(api))
    status, ending = "COMPLETED", None
    max_turns = 10
    try:
        while customer_turns <= max_turns:
            latest = next(x["message"] for x in reversed(history) if x["speaker"] == "customer")
            latest_customer_record = next(x for x in reversed(history) if x["speaker"] == "customer")
            context_history = [{"direction": "INBOUND" if x["speaker"] == "customer" else "OUTBOUND", "body": x["message"]}
                               for x in history if x["speaker"] in ("customer", "agent")]
            decision, usage = core.decide(latest, profile, context_history, supports)
            actions.append({"turn": customer_turns, "action": decision["action"], "sales_move": decision.get("sales_move"),
                            "buyer_signal": decision.get("buyer_signal"), "reply": decision["reply"]})
            updates = {key: value for key, value in decision["lead_updates"].items() if key in PROFILE_FIELDS and value is not None}
            profile.update(updates)
            if decision["action"] == "SUPPORT_REQUEST":
                supports.append({"status": "UNRESOLVED_OFFLINE", "request": decision.get("support_request"),
                                 "note": "No human, live inventory, price, calendar, CRM or WhatsApp connection exists in this offline simulation."})
                # Retry the same customer turn with the unresolved request visible; this models support continuity without an external lookup.
                decision, usage = core.decide(latest, profile, context_history, supports)
                actions.append({"turn": customer_turns, "action": decision["action"], "sales_move": decision.get("sales_move"),
                                "buyer_signal": decision.get("buyer_signal"), "reply": decision["reply"], "after_support_request": True})
            reply = str(decision.get("reply", "")).strip()
            if reply:
                history.append({"turn": customer_turns, "speaker": "agent", "message": reply})
            if latest_customer_record.get("simulator_done"):
                ending = latest_customer_record.get("simulator_ending_reason") or "customer chose to end naturally"
                break
            if decision["action"] in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
                ending = "agent requested " + decision["action"] + "; no operational handoff executed"
                break
            if not reply:
                ending = "agent produced no customer-facing reply"
                break
            if customer_turns >= max_turns:
                ending = "10 customer turns reached"
                break
            customer_user = json.dumps({"scenario_persona": scenario["persona"], "private_facts": scenario["facts"],
                                        "motives": scenario["motives"], "history": history,
                                        "completed_customer_turns": customer_turns, "target_turn_range": [6, 10]}, ensure_ascii=False)
            next_customer, _, _ = api.request("customer_simulator", system, customer_user, CUSTOMER_SCHEMA,
                                               "simulated_customer_turn", 700)
            message = next_customer["message"].strip()
            if not message:
                status, ending = "INCOMPLETE", "customer simulator returned an empty message"
                break
            customer_turns += 1
            history.append({"turn": customer_turns, "speaker": "customer", "message": message,
                            "simulator_done": next_customer["done"], "simulator_ending_reason": next_customer["ending_reason"]})
        if ending is None:
            ending = "conversation ended"
    except Exception as exc:
        status, ending = "INCOMPLETE", "%s: %s" % (type(exc).__name__, str(exc)[:500])
    report = {"architecture": architecture, "status": status, "customer_turns": customer_turns,
              "natural_ending_reason": ending, "transcript": history, "agent_actions": actions,
              "final_profile": profile, "unresolved_offline_support": supports,
              "model": MODEL, "reasoning": config["reasoning"], "provider_calls": prior_records + api.records[metrics_start:]}
    if checkpoint:
        checkpoint.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def report_metrics(records):
    usage = {key: 0 for key in ("input_tokens", "cached_tokens", "output_tokens", "total_tokens")}
    available = {key: False for key in usage}
    for record in records:
        for key in usage:
            raw_usage = record.get("usage") or {}
            value = raw_usage.get(key)
            if key == "cached_tokens" and not isinstance(value, int):
                value = (raw_usage.get("input_tokens_details") or {}).get("cached_tokens")
            if isinstance(value, int):
                usage[key] += value
                available[key] = True
    if not available["total_tokens"] and available["input_tokens"] and available["output_tokens"]:
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        available["total_tokens"] = True
    uncached = max(0, usage["input_tokens"] - usage["cached_tokens"])
    fake_only = bool(records) and all(r.get("transport") == "fake" for r in records)
    cost = (uncached * INPUT_RATE + usage["cached_tokens"] * CACHED_RATE + usage["output_tokens"] * OUTPUT_RATE) / 1_000_000 if available["input_tokens"] and available["output_tokens"] and not fake_only else None
    return {"model_calls": len(records), "calls_by_role": _counts(r["role"] for r in records),
            "failed_or_incomplete_calls": sum(r.get("outcome") not in (None, "COMPLETED") for r in records),
            "latency_seconds_total": round(sum(r["latency_seconds"] for r in records), 3),
            "latency_seconds_mean": round(sum(r["latency_seconds"] for r in records) / len(records), 3) if records else None,
            "tokens": {k: usage[k] if available[k] else None for k in usage},
            "estimated_standard_usd": round(cost, 6) if cost is not None else None,
            "cost_basis": "Dry-run synthetic usage; no charges." if fake_only else "Standard GPT-6 Luna text token rates, short-context tier; cached input separated. Estimate excludes any unreported cache writes, taxes, and account-level adjustments."}


def _counts(values):
    result = {}
    for value in values: result[value] = result.get(value, 0) + 1
    return result


def run_pair(scenario, api, config, outdir, dry=False):
    pair_path = outdir / (scenario["id"] + ".pair.json")
    failure_path = outdir / (scenario["id"] + ".failure.json")
    pair = json.loads(pair_path.read_text()) if pair_path.exists() else {"scenario_id": scenario["id"], "title": scenario["title"], "status": "INCOMPLETE"}
    if pair.get("status") == "COMPLETED":
        failure_path.unlink(missing_ok=True)
        return pair
    for arch in ("V2", "V3"):
        if pair.get(arch, {}).get("status") == "COMPLETED":
            continue
        cp = outdir / (scenario["id"] + "." + arch.lower() + ".json")
        metrics_start = len(api.records)
        result = run_conversation(scenario, arch, api, config, cp)
        pair[arch] = result
        pair.setdefault("metrics", {})[arch] = report_metrics(result.get("provider_calls", api.records[metrics_start:]))
        pair["status"] = "INCOMPLETE"
        pair_path.write_text(json.dumps(pair, ensure_ascii=False, indent=2) + "\n")
        if result["status"] != "COMPLETED":
            return pair
    if not all(pair.get(arch, {}).get("status") == "COMPLETED" for arch in ("V2", "V3")):
        return pair
    label_map = {"V2": "A", "V3": "B"} if int(hashlib.sha256(scenario["id"].encode()).hexdigest(), 16) % 2 else {"V2": "B", "V3": "A"}
    _, judge_system = prompts(scenario, "")
    blind = {label_map[arch]: {"transcript": pair[arch]["transcript"], "customer_turns": pair[arch]["customer_turns"],
                               "ending_reason": pair[arch]["natural_ending_reason"]} for arch in ("V2", "V3")}
    judge_user = json.dumps({"buyer_truth": {"persona": scenario["persona"], "motives": scenario["motives"], "facts": scenario["facts"]},
                             "scenario": scenario["title"], "Agent A": blind["A"], "Agent B": blind["B"]}, ensure_ascii=False)
    judge_records_start = len(api.records)
    judge, _, _ = api.request("blind_judge", judge_system, judge_user, JUDGE_SCHEMA, "blind_sales_comparison", 6000)
    pair["blind_judge_provider_calls"] = api.records[judge_records_start:]
    pair["blind_label_map"] = label_map  # Kept in artifacts, omitted from judge input.
    pair["blind_judge"] = judge
    pair["paired_winner"] = "TIE" if judge["winner"] == "TIE" else next(arch for arch, label in label_map.items() if label == judge["winner"])
    pair["metrics"]["blind_judge"] = report_metrics(pair["blind_judge_provider_calls"])
    pair["status"] = "COMPLETED"
    pair["pair_judged_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    pair_path.write_text(json.dumps(pair, ensure_ascii=False, indent=2) + "\n")
    failure_path.unlink(missing_ok=True)
    return pair


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run 10 paired, offline-from-WhatsApp Sales Core V2/V3 dialogs")
    parser.add_argument("--dry-run", action="store_true", help="exercise the same paired operator path with fake model transports")
    parser.add_argument("--output", help="new or existing report directory name; existing completed pairs are skipped")
    parser.add_argument("--scenario", action="append", help="scenario ID; default evaluates all 10")
    parser.add_argument("--env-file", help="load existing local API/model configuration without copying secrets")
    args = parser.parse_args(argv)
    if args.env_file:
        load_env_file(args.env_file)
    config = get_config()
    if config["model"] != MODEL:
        raise SystemExit("A/B comparison requires GPT-6 Luna for the existing runtime")
    if not args.dry_run and not config["api_key"]:
        raise SystemExit("OPENAI_API_KEY is required for paid evaluation; no fallback provider is used")
    scenarios = json.loads((SIM / "sales_core_v3_scenarios.json").read_text())
    selected = set(args.scenario or [s["id"] for s in scenarios])
    scenarios = [s for s in scenarios if s["id"] in selected]
    if selected != {s["id"] for s in scenarios}:
        raise SystemExit("Unknown scenario id")
    stamp = args.output or (("DRYRUN-" if args.dry_run else "RUN-") + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    outdir = SIM / "reports" / stamp
    outdir.mkdir(parents=True, exist_ok=bool(args.output))
    run_start, api = time.monotonic(), API(config, args.dry_run)
    pairs = []
    for scenario in scenarios:
        try:
            pairs.append(run_pair(scenario, api, config, outdir, args.dry_run))
            if not args.dry_run and pairs[-1].get("status") != "COMPLETED":
                break
        except Exception as exc:
            failure = {"scenario_id": scenario["id"], "status": "INCOMPLETE", "error": "%s: %s" % (type(exc).__name__, str(exc)[:800])}
            (outdir / (scenario["id"] + ".failure.json")).write_text(json.dumps(failure, indent=2) + "\n")
            pairs.append(failure)
            if not args.dry_run:
                break
    complete = [p for p in pairs if p.get("status") == "COMPLETED"]
    aggregates = {arch: {"mean_scores": {}, "wins": 0, "completed_conversations": sum(p.get(arch, {}).get("status") == "COMPLETED" for p in pairs),
                         "metrics": report_metrics([c for p in pairs for c in p.get(arch, {}).get("provider_calls", [])])}
                  for arch in ("V2", "V3")}
    for p in complete:
        for arch in ("V2", "V3"):
            for dim in SCORE_DIMENSIONS:
                label = p["blind_label_map"][arch]
                bucket = aggregates[arch]["mean_scores"].setdefault(dim, [])
                bucket.append(p["blind_judge"]["scores"][label][dim])
        if p["paired_winner"] != "TIE": aggregates[p["paired_winner"]]["wins"] += 1
    for arch in aggregates:
        aggregates[arch]["mean_scores"] = {k: round(sum(v) / len(v), 2) for k, v in aggregates[arch]["mean_scores"].items()}
    all_records = [c for p in pairs for arch in ("V2", "V3") for c in p.get(arch, {}).get("provider_calls", [])]
    all_records.extend(c for p in pairs for c in p.get("blind_judge_provider_calls", []))
    roles = ("sales_v2", "sales_strategy", "sales_v3", "customer_simulator", "blind_judge")
    role_metrics = {role: report_metrics([record for record in all_records if record.get("role") == role])
                    for role in roles}
    judge_times = [dt.datetime.fromisoformat(p["pair_judged_at_utc"]) for p in complete if p.get("pair_judged_at_utc")]
    judged_span_seconds = round((max(judge_times) - min(judge_times)).total_seconds(), 3) if len(judge_times) > 1 else None
    report = {"run_id": stamp, "status": "COMPLETED" if len(complete) == 10 else "INCOMPLETE",
              "scenario_count": len(scenarios), "completed_pairs": len(complete),
              "failed_or_incomplete_pairs": [p["scenario_id"] for p in pairs if p.get("status") != "COMPLETED"],
              "model": MODEL, "reasoning": config["reasoning"], "dry_run": args.dry_run,
              "aggregate": aggregates, "pair_results": [{"scenario_id": p["scenario_id"], "title": p.get("title"),
                   "status": p.get("status"), "winner": p.get("paired_winner"),
                   "customer_turns": {a: p.get(a, {}).get("customer_turns") for a in ("V2", "V3")},
                   "ending_reasons": {a: p.get(a, {}).get("natural_ending_reason") for a in ("V2", "V3")}}
                   for p in pairs], "provider_metrics": report_metrics(all_records), "api_usage_by_role": role_metrics,
              "first_to_last_pair_judgment_seconds": judged_span_seconds,
              "duration_seconds": round(time.monotonic() - run_start, 3),
              "limits": ["Ten pairs are descriptive and not statistically significant.",
                         "Estimated charges use standard short-context text rates and retained provider-reported tokens.",
                         "During earlier resumes, one partial five-turn V3 attempt and three incomplete API responses were overwritten before their usage could be retained; the final token and cost totals therefore understate actual experiment usage by an unknown amount.",
                         "No CRM, SQLite, WhatsApp, live inventory, calendar or human-support transport is invoked."]}
    (outdir / "aggregate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (outdir / "aggregate.md").write_text(render(report, pairs))
    print(json.dumps({"report_dir": str(outdir), "completed_pairs": len(complete),
                      "status": report["status"], "provider_metrics": report["provider_metrics"]}, ensure_ascii=False, indent=2))
    return 0 if args.dry_run or report["status"] == "COMPLETED" else 2


def render(report, pairs):
    lines = ["# Sales Core V2/V3 paired evaluation", "", f"- Run: {report['run_id']}",
             f"- Status: {report['status']} ({report['completed_pairs']}/{report['scenario_count']} pairs)",
             f"- Model: {report['model']} / {report['reasoning']}", "", "## Scenario outcomes", "",
             "| Scenario | Pair | V2 turns | V3 turns | Winner |", "|---|---|---:|---:|---|"]
    for row in report["pair_results"]:
        lines.append(f"| {row['scenario_id']} {row.get('title') or ''} | {row['status']} | {row['customer_turns']['V2']} | {row['customer_turns']['V3']} | {row['winner'] or '—'} |")
    lines += ["", "## Paired blind scores", "", "| Dimension | V2 | V3 |", "|---|---:|---:|"]
    for dim in SCORE_DIMENSIONS:
        lines.append(f"| {dim} | {report['aggregate']['V2']['mean_scores'].get(dim, '—')} | {report['aggregate']['V3']['mean_scores'].get(dim, '—')} |")
    lines += ["", "## Usage", "", "```json", json.dumps(report["provider_metrics"], ensure_ascii=False, indent=2), "```", "", "## Transcript evidence", ""]
    for p in pairs:
        if p.get("status") != "COMPLETED":
            lines += [f"### {p['scenario_id']}: incomplete", ""]
            continue
        judge = p["blind_judge"]
        lines += [f"### {p['scenario_id']} — {p['title']} ({p['paired_winner']})", "", judge["summary"], ""]
        for label in ("stronger_examples", "weaker_examples"):
            for example in judge[label]:
                arch = next(a for a, side in p["blind_label_map"].items() if side == example["side"])
                reason = example.get("why_better", example.get("why_worse", ""))
                lines.append(f"- {label.replace('_', ' ').title()}: {arch}, turn {example['turn']}: “{example['evidence']}” — {reason}")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
