#!/usr/bin/env python3
"""Isolated paired V2/V3 sales evaluation through fake or OpenAI transports."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "simulator"
sys.path.insert(0, str(ROOT))
from app.agent import SalesAgent
from app.config import get_config, load_env_file
from app.db import support_equivalent
from app.knowledge import KNOWLEDGE
from app.provider import PROFILE_FIELDS, agent_schema
from app.sales_core_v3 import SalesCoreV3
from app.service import support_customer_reply, support_signature

MODEL = "gpt-6-luna"
INPUT_RATE, CACHED_RATE, OUTPUT_RATE = 0.10, 0.01, 0.50
WEIGHTS = {"customer_insight": 25, "meaningful_sales_actions": 25,
           "observation_and_adaptation": 20, "natural_continuity": 20, "progression_and_pacing": 10}
CUSTOMER_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "message": {"type": "string"}, "state": {"type": "string", "enum": ["CONTINUE", "WAITING", "END"]},
    "reason": {"type": "string"}, "interest_change": {"type": "string", "enum": ["INCREASED", "UNCHANGED", "DECREASED"]}},
    "required": ["message", "state", "reason", "interest_change"]}
JUDGE_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "winner": {"type": "string", "enum": ["A", "B", "TIE"]},
    "scores": {"type": "object", "additionalProperties": False, "properties": {
        side: {"type": "object", "additionalProperties": False,
               "properties": {key: {"type": "integer", "minimum": 1, "maximum": 5} for key in WEIGHTS},
               "required": list(WEIGHTS)} for side in ("A", "B")}, "required": ["A", "B"]},
    "examples": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {"side": {"type": "string", "enum": ["A", "B"]}, "turn": {"type": "integer"},
                       "evidence": {"type": "string"}, "assessment": {"type": "string"},
                       "better_response": {"type": "string"}},
        "required": ["side", "turn", "evidence", "assessment", "better_response"]}},
    "material_errors": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {"side": {"type": "string", "enum": ["A", "B"]}, "turn": {"type": "integer"},
                       "kind": {"type": "string"}, "evidence": {"type": "string"}},
        "required": ["side", "turn", "kind", "evidence"]}},
    "simulator_quality": {"type": "string"}, "summary": {"type": "string"}},
    "required": ["winner", "scores", "examples", "material_errors", "simulator_quality", "summary"]}


def atomic_json(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


class API:
    def __init__(self, config, dry=False):
        self.config, self.dry = config, dry
        self.records = []
        self.journal = None

    def request(self, role, system, user, schema, name, max_tokens, reasoning=None):
        start = time.monotonic()
        effort = reasoning or self.config["reasoning"]
        if self.dry:
            payload = self.fake(role, user)
            usage = {"input_tokens": 12, "output_tokens": 6, "total_tokens": 18, "cached_tokens": 0}
            status, detail = "COMPLETED", None
        else:
            body = {"model": MODEL, "reasoning": {"effort": effort},
                "input": [{"role": "system", "content": [{"type": "input_text", "text": system}]},
                          {"role": "user", "content": [{"type": "input_text", "text": user}]}],
                "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
                "max_output_tokens": max_tokens, "store": False}
            req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + self.config["api_key"], "Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=180) as response:
                    result = json.load(response)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:1000]
                self.record(role, effort, {}, time.monotonic() - start, "FAILED", detail)
                raise RuntimeError("HTTP %s: %s" % (exc.code, detail))
            except (urllib.error.URLError, TimeoutError) as exc:
                self.record(role, effort, {}, time.monotonic() - start, "FAILED", str(exc))
                raise
            raw_usage = result.get("usage") or {}
            usage = {"input_tokens": raw_usage.get("input_tokens"), "output_tokens": raw_usage.get("output_tokens"),
                     "total_tokens": raw_usage.get("total_tokens"),
                     "cached_tokens": (raw_usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                     "reasoning_tokens": (raw_usage.get("output_tokens_details") or {}).get("reasoning_tokens")}
            status = result.get("status")
            if status != "completed":
                detail = str(result.get("incomplete_details"))
                self.record(role, effort, usage, time.monotonic() - start, "INCOMPLETE", detail)
                raise RuntimeError("Responses API %s: %s" % (status, detail))
            raw = result.get("output_text") or next((x.get("text") for row in result.get("output", [])
                for x in row.get("content", []) if x.get("type") == "output_text"), None)
            if not raw:
                self.record(role, effort, usage, time.monotonic() - start, "INCOMPLETE", "no output_text")
                raise RuntimeError("Responses API returned no structured output")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                self.record(role, effort, usage, time.monotonic() - start, "INVALID_JSON", str(exc))
                raise
        self.record(role, effort, usage, time.monotonic() - start, "COMPLETED", None)
        return payload, usage, round(time.monotonic() - start, 3)

    def record(self, role, effort, usage, duration, outcome, detail):
        row = {"role": role, "transport": "fake" if self.dry else "responses_api", "model": MODEL,
               "reasoning": effort, "usage": usage, "latency_seconds": round(duration, 3),
               "outcome": outcome, "detail": detail}
        self.records.append(row)
        if self.journal:
            with self.journal.open("a") as file:
                file.write(json.dumps(row, ensure_ascii=False) + "\n")
                file.flush()
                os.fsync(file.fileno())

    @staticmethod
    def fake(role, user):
        if role == "sales_strategy":
            from app.sales_core_v3 import PROGRESS_FIELDS
            progress = {key: [] for key in PROGRESS_FIELDS[:-1]}
            progress["next_opportunity"] = {"action": "answer", "why": "customer asked", "feedback_to_watch": "next reply"}
            return {"progress": progress, "buyer_signal": "QUESTION", "reaction_to_previous_action": "unknown",
                    "immediate_objective": "Answer accurately", "knowledge_query": None}
        if role in ("sales_v2", "sales_v3"):
            return {"action": "REPLY", "sales_move": "ANSWER", "buyer_signal": "QUESTION",
                    "reply": "Thanks for asking. I can share the verified details.",
                    "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                    "handoff_reason": None, "handoff_details": None}
        if role == "customer_simulator":
            return {"message": "Thanks, I will think about it.", "state": "END", "reason": "natural pause after answer",
                    "interest_change": "UNCHANGED"}
        return {"winner": "TIE", "scores": {s: {k: 3 for k in WEIGHTS} for s in ("A", "B")},
                "examples": [], "material_errors": [], "simulator_quality": "Fake transport only", "summary": "Dry run"}


class V3EvalProvider:
    def __init__(self, api): self.api = api
    def request(self, name, schema, system, user, max_output_tokens):
        role = "sales_strategy" if name == "sales_strategy_v3" else "sales_v3"
        return self.api.request(role, system, user, schema, name, max_output_tokens, "high")


class V2EvalProvider:
    def __init__(self, api): self.api = api
    def decide(self, system, user):
        decision, usage, _ = self.api.request("sales_v2", system, user, agent_schema(),
                                               "property_agent_decision", 5500, "high")
        return decision, usage


class FakeOperations:
    """Stateful offline adapter; fixture resolution is explicit and never a live operation."""
    def __init__(self, state=None):
        self.requests = (state or {}).get("requests", [])
        self.handoff = (state or {}).get("handoff")

    def context(self):
        return [{"request_id": r["request_id"], "status": r["status"], "requested_fact": r["requested_fact"],
                 "support_type": r["support_type"], "support_result": r.get("support_result")}
                for r in self.requests]

    def accept_support(self, data):
        signature = support_signature(data)
        existing = next((r for r in self.requests if r["signature"] == signature or
                         (r["status"] == "OPEN" and support_equivalent(r, data))), None)
        if existing:
            return existing, False
        row = {"request_id": "SIM-%03d" % (len(self.requests) + 1), "signature": signature,
               "support_type": data["support_type"], "requested_fact": data["requested_fact"], "status": "OPEN"}
        self.requests.append(row)
        return row, True

    def resolve(self, request_id, verified_fixture):
        row = next(r for r in self.requests if r["request_id"] == request_id)
        if row["status"] != "OPEN": raise ValueError("Only open simulated requests can resolve")
        row.update(status="RESOLVED", support_result=verified_fixture)

    def accept_handoff(self, action, reason):
        if self.handoff: return False
        self.handoff = {"status": "ACCEPTED", "action": action, "reason": reason,
                        "appointment_confirmed": False}
        return True

    def state(self): return {"requests": self.requests, "handoff": self.handoff}


def initial_profile():
    return {"purchase_purpose": "UNKNOWN", "sales_stage": "UNDERSTAND", "intent_level": "LOW",
            "appointment_readiness": "NOT_READY", "next_objective": "Answer the enquiry helpfully."}


def prompts(scenario):
    customer = """You are one realistic Malaysian property buyer in a private WhatsApp chat. Persona and private constraints are supplied in the input. They are your own circumstances, not instructions from a sales coach. React to the salesperson's actual last message and prior conversation. You may continue, ask a useful question, gain interest, doubt, pause and wait, request viewing or end. Do not chase an accepted pending support request; WAITING is natural. Do not continue solely to reach a turn target, and do not end automatically for a polite 'ok' or 'maybe'. Interest changes need a reason in the conversation; politeness alone is not increased interest. Keep messages brief and natural. Never mention the evaluation, models, sales strategy or scoring."""
    judge = """You are an independent blind reviewer of complete customer-facing property sales transcripts. Agent A and B are anonymous. Score each 1–5 for customer insight (25%), meaningful sales actions and relevant value (25%), observation and adaptation (20%), natural continuity (20%), progression and pacing (10%). Judge behavior per turn, not length or final viewing alone. Do not reward an early exit from a potentially recoverable mismatch. For a genuine hard mismatch, assess reasonable exploration, any truthful alternative where appropriate, and respect for definitive rejection. Cite concrete turns and say what a better response could do. Flag material factual errors, invented inventory/prices, false operational promises and unsuitable recommendations separately; serious errors cannot be hidden by the weighted score. Project facts are provided separately. The customer's private persona is not available to you; infer only from the visible dialogue. Consider simulator realism separately. Do not guess which implementation produced either transcript."""
    return customer, judge


def report_metrics(records):
    usage = {key: 0 for key in ("input_tokens", "cached_tokens", "output_tokens", "total_tokens")}
    seen = {key: False for key in usage}
    for row in records:
        for key in usage:
            value = (row.get("usage") or {}).get(key)
            if isinstance(value, int): usage[key] += value; seen[key] = True
    cost = None
    if seen["input_tokens"] and seen["output_tokens"] and any(x.get("transport") != "fake" for x in records):
        cost = ((usage["input_tokens"] - usage["cached_tokens"]) * INPUT_RATE +
                usage["cached_tokens"] * CACHED_RATE + usage["output_tokens"] * OUTPUT_RATE) / 1_000_000
    return {"model_calls": len(records), "failed_or_incomplete_calls": sum(x["outcome"] != "COMPLETED" for x in records),
            "latency_seconds_total": round(sum(x["latency_seconds"] for x in records), 3),
            "tokens": {key: usage[key] if seen[key] else None for key in usage},
            "estimated_standard_usd": round(cost, 6) if cost is not None else None}


def deterministic_checks(report):
    actions, operations = report["agent_actions"], report["operations"]
    requests = operations["requests"]
    return {"duplicate_support_requests": sum(a.get("operation_outcome") == "REUSED" for a in actions),
            "pending_requests": sum(r["status"] == "OPEN" for r in requests),
            "handoff_without_acceptance": sum(a["action"] in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF")
                and a.get("operation_outcome") != "ACCEPTED" for a in actions),
            "false_confirmation_phrase": [a["turn"] for a in actions if "appointment is confirmed" in a["reply"].lower()
                and not (operations.get("handoff") or {}).get("appointment_confirmed")],
            "invented_four_bedroom": [a["turn"] for a in actions if "we have a 4-bedroom" in a["reply"].lower()
                or "we have four bedrooms" in a["reply"].lower()]}


def run_conversation(scenario, architecture, api, config, checkpoint):
    saved = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    if saved.get("status") == "COMPLETED": return saved
    history = saved.get("transcript") or [{"turn": 1, "speaker": "customer", "message": scenario["opening"]}]
    profile = saved.get("final_profile") or initial_profile()
    operations = FakeOperations(saved.get("operations"))
    actions = saved.get("agent_actions") or []
    states = saved.get("customer_state_transitions") or []
    phase = saved.get("phase", "agent")
    journal = checkpoint.with_suffix(".calls.jsonl")
    api.journal = journal
    core = SalesAgent(config, provider=V2EvalProvider(api)) if architecture == "V2" else SalesCoreV3(config, provider=V3EvalProvider(api))
    status, ending = "IN_PROGRESS", None
    customer_turn = len([x for x in history if x["speaker"] == "customer"])

    def save(phase_value):
        atomic_json(checkpoint, {"architecture": architecture, "status": "IN_PROGRESS", "phase": phase_value,
            "customer_turns": customer_turn, "transcript": history, "agent_actions": actions,
            "customer_state_transitions": states, "final_profile": profile, "operations": operations.state()})

    try:
        while customer_turn <= 10:
            if phase == "agent":
                latest = next(x["message"] for x in reversed(history) if x["speaker"] == "customer")
                context_history = [{"direction": "INBOUND" if x["speaker"] == "customer" else "OUTBOUND", "body": x["message"]}
                                   for x in history if x["speaker"] in ("customer", "agent")]
                decision, _ = core.decide(latest, profile, context_history, operations.context())
                progress = decision.pop("_conversation_progress", None)
                if progress is not None: profile["conversation_progress"] = progress
                profile.update({k: v for k, v in decision["lead_updates"].items() if k in PROFILE_FIELDS and v is not None})
                action = {"turn": customer_turn, "action": decision["action"], "sales_move": decision["sales_move"],
                          "buyer_signal": decision["buyer_signal"], "reply": decision["reply"]}
                if decision["action"] == "SUPPORT_REQUEST":
                    request, created = operations.accept_support(decision["support_request"])
                    action["operation_outcome"] = "ACCEPTED" if created else "REUSED"
                    action["request_id"] = request["request_id"]
                    if architecture == "V3":
                        decision["reply"] = support_customer_reply(request, created)
                        action["reply"] = decision["reply"]
                elif decision["action"] in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
                    action["operation_outcome"] = "ACCEPTED" if operations.accept_handoff(decision["action"], decision["handoff_reason"]) else "REUSED"
                actions.append(action)
                reply = decision["reply"].strip()
                if reply: history.append({"turn": customer_turn, "speaker": "agent", "message": reply})
                phase = "customer"
                save(phase)
                if decision["action"] in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
                    status, ending = "COMPLETED", "accepted formal handoff; appointment not confirmed"
                    break
                if not reply:
                    status, ending = "INCOMPLETE", "empty agent reply"
                    break
                if customer_turn >= 10:
                    status, ending = "COMPLETED", "10 customer turns reached"
                    break
            customer_system, _ = prompts(scenario)
            customer_input = json.dumps({"persona": scenario["persona"], "private_needs": scenario["facts"],
                "private_motivations": scenario["motives"], "conversation": history,
                "operational_status": operations.context()}, ensure_ascii=False)
            customer, _, _ = api.request("customer_simulator", customer_system, customer_input, CUSTOMER_SCHEMA,
                                           "simulated_customer_turn", 1200, "medium")
            states.append({"after_agent_turn": customer_turn, **customer})
            if customer["message"].strip():
                customer_turn += 1
                history.append({"turn": customer_turn, "speaker": "customer", "message": customer["message"].strip()})
            phase = "agent"
            save(phase)
            if customer["state"] in ("WAITING", "END"):
                if customer["state"] == "WAITING" and scenario.get("simulated_support_result") and operations.requests:
                    operations.resolve(operations.requests[0]["request_id"], scenario["simulated_support_result"])
                    history.append({"turn": customer_turn + 1, "speaker": "customer", "message": "Any verified update on that?"})
                    customer_turn += 1
                    states.append({"after_agent_turn": customer_turn, "state": "RESUMED", "reason": "explicit simulated support event"})
                    save(phase)
                    continue
                status, ending = "COMPLETED", "customer " + customer["state"].lower() + ": " + customer["reason"]
                break
            if not customer["message"].strip():
                status, ending = "INCOMPLETE", "CONTINUE without customer message"
                break
    except Exception as exc:
        status, ending = "INCOMPLETE", "%s: %s" % (type(exc).__name__, str(exc)[:600])
    records = [json.loads(line) for line in journal.read_text().splitlines()] if journal.exists() else []
    report = {"architecture": architecture, "status": status, "phase": phase, "customer_turns": customer_turn,
        "natural_ending_reason": ending, "transcript": history, "agent_actions": actions,
        "customer_state_transitions": states, "final_profile": profile, "operations": operations.state(),
        "provider_calls": records}
    report["deterministic_checks"] = deterministic_checks(report)
    atomic_json(checkpoint, report)
    api.journal = None
    return report


def run_pair(scenario, api, config, outdir):
    path = outdir / (scenario["id"] + ".pair.json")
    pair = json.loads(path.read_text()) if path.exists() else {"scenario_id": scenario["id"],
        "title": scenario["title"], "status": "INCOMPLETE"}
    if pair["status"] == "COMPLETED": return pair
    for arch in ("V2", "V3"):
        if pair.get(arch, {}).get("status") == "COMPLETED": continue
        result = run_conversation(scenario, arch, api, config, outdir / (scenario["id"] + "." + arch.lower() + ".json"))
        pair[arch] = result
        pair["status"] = "INCOMPLETE"
        atomic_json(path, pair)
        if result["status"] != "COMPLETED": return pair
    label_map = {"V2": "A", "V3": "B"} if int(hashlib.sha256(scenario["id"].encode()).hexdigest(), 16) % 2 else {"V2": "B", "V3": "A"}
    _, judge_system = prompts(scenario)
    blind = {label_map[a]: {"transcript": pair[a]["transcript"], "ending_reason": pair[a]["natural_ending_reason"]}
             for a in ("V2", "V3")}
    verified_facts = {str(path.relative_to(KNOWLEDGE)): path.read_text(encoding="utf-8")
                      for folder in ("01_facts", "02_commercial")
                      for path in sorted((KNOWLEDGE / folder).glob("*.md"))}
    judge_input = json.dumps({"verified_project_facts": verified_facts,
        "customer_facing_name_policy": "Pearl Residences is the authorized customer-facing sales alias for SkyWorld Pearlmont. Using that alias in an ordinary introduction is correct. If the customer directly asks the real identity, answer truthfully. Do not flag the alias itself as an invented project.",
        "scenario": scenario["title"],
                              "Agent A": blind["A"], "Agent B": blind["B"]}, ensure_ascii=False)
    judge_journal = outdir / (scenario["id"] + ".judge.calls.jsonl")
    api.journal = judge_journal
    try:
        judge, _, _ = api.request("blind_judge", judge_system, judge_input, JUDGE_SCHEMA,
                                   "blind_sales_comparison", 9000, "xhigh")
    except RuntimeError as exc:
        if "reasoning" in str(exc).lower() and ("unsupported" in str(exc).lower() or "invalid" in str(exc).lower()):
            pair["judge_xhigh_error"] = str(exc)
            atomic_json(path, pair)
            judge, _, _ = api.request("blind_judge", judge_system, judge_input, JUDGE_SCHEMA,
                                       "blind_sales_comparison", 9000, "high")
        else: raise
    pair["blind_label_map"] = label_map
    pair["blind_judge"] = judge
    pair["paired_winner"] = "TIE" if judge["winner"] == "TIE" else next(a for a, label in label_map.items() if label == judge["winner"])
    pair["blind_judge_provider_calls"] = [json.loads(line) for line in judge_journal.read_text().splitlines()]
    pair["status"] = "COMPLETED"
    atomic_json(path, pair)
    api.journal = None
    return pair


def render(report, pairs):
    lines = ["# Sales Brain V3 完整 A/B 评估", "", f"运行：{report['run_id']}；完成 {report['completed_pairs']}/{report['scenario_count']} 对。", "",
             "| 场景 | V2轮数 | V3轮数 | 判定 |", "|---|---:|---:|---|"]
    for p in pairs:
        lines.append(f"| {p['scenario_id']} {p.get('title','')} | {p.get('V2',{}).get('customer_turns','—')} | {p.get('V3',{}).get('customer_turns','—')} | {p.get('paired_winner','—')} |")
    lines += ["", "## 加权评分", "", "| 维度 | 权重 | V2 | V3 |", "|---|---:|---:|---:|"]
    for key, weight in WEIGHTS.items():
        lines.append(f"| {key} | {weight}% | {report['aggregate']['V2']['mean_scores'].get(key,'—')} | {report['aggregate']['V3']['mean_scores'].get(key,'—')} |")
    lines += ["", "## Token、费用、延迟", "", "```json", json.dumps(report["provider_metrics"], ensure_ascii=False, indent=2), "```", ""]
    for p in pairs:
        if p.get("status") != "COMPLETED": continue
        lines += [f"## {p['scenario_id']} {p['title']}", "", p["blind_judge"]["summary"], ""]
        for arch in ("V2", "V3"):
            lines.append(f"### {arch} 对话及状态")
            for turn in p[arch]["transcript"]: lines.append(f"- {turn['turn']} {turn['speaker']}: {turn['message']}")
            lines.append("- 运营动作与客户状态：" + json.dumps({"actions": p[arch]["agent_actions"],
                "operations": p[arch]["operations"], "states": p[arch]["customer_state_transitions"]}, ensure_ascii=False))
            lines.append("")
        for example in p["blind_judge"]["examples"]:
            arch = next(a for a, label in p["blind_label_map"].items() if label == example["side"])
            lines.append(f"- 评审 {arch} 第{example['turn']}轮：{example['evidence']}；{example['assessment']}；更好做法：{example['better_response']}")
        for error in p["blind_judge"]["material_errors"]: lines.append("- 严重问题：" + json.dumps(error, ensure_ascii=False))
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run isolated paired Sales Core V2/V3 conversations")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", help="new or resumable report directory under simulator/reports")
    parser.add_argument("--scenario", action="append")
    parser.add_argument("--env-file")
    args = parser.parse_args(argv)
    if args.env_file: load_env_file(args.env_file)
    config = get_config()
    if config["model"] != MODEL or (not args.dry_run and not config["api_key"]):
        raise SystemExit("GPT-6 Luna and an existing OPENAI_API_KEY are required for paid evaluation")
    scenarios = json.loads((SIM / "sales_core_v3_scenarios.json").read_text())
    selected = set(args.scenario or [s["id"] for s in scenarios])
    scenarios = [s for s in scenarios if s["id"] in selected]
    if selected != {s["id"] for s in scenarios}: raise SystemExit("Unknown scenario ID")
    stamp = args.output or (("DRYRUN-" if args.dry_run else "RUN-") + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    outdir = SIM / "reports" / stamp
    outdir.mkdir(parents=True, exist_ok=bool(args.output))
    api, started = API(config, args.dry_run), time.monotonic()
    pairs = []
    for scenario in scenarios:
        try:
            pair = run_pair(scenario, api, config, outdir)
        except Exception as exc:
            pair = {"scenario_id": scenario["id"], "status": "INCOMPLETE", "error": "%s: %s" % (type(exc).__name__, str(exc)[:1000])}
            atomic_json(outdir / (scenario["id"] + ".failure.json"), pair)
        pairs.append(pair)
        if pair["status"] != "COMPLETED" and not args.dry_run: break
    completed = [p for p in pairs if p["status"] == "COMPLETED"]
    aggregates = {a: {"wins": sum(p["paired_winner"] == a for p in completed), "mean_scores": {}} for a in ("V2", "V3")}
    for arch in ("V2", "V3"):
        for key in WEIGHTS:
            scores = [p["blind_judge"]["scores"][p["blind_label_map"][arch]][key] for p in completed]
            aggregates[arch]["mean_scores"][key] = round(sum(scores) / len(scores), 2) if scores else None
    records = [row for p in pairs for arch in ("V2", "V3") for row in p.get(arch, {}).get("provider_calls", [])]
    records.extend(row for p in pairs for row in p.get("blind_judge_provider_calls", []))
    report = {"run_id": stamp, "status": "COMPLETED" if len(completed) == len(scenarios) else "INCOMPLETE",
        "scenario_count": len(scenarios), "completed_pairs": len(completed), "dry_run": args.dry_run,
        "aggregate": aggregates, "provider_metrics": report_metrics(records),
        "api_usage_by_role": {role: report_metrics([r for r in records if r["role"] == role])
            for role in ("sales_v2", "sales_strategy", "sales_v3", "customer_simulator", "blind_judge")},
        "duration_seconds": round(time.monotonic() - started, 3),
        "pair_results": [{"scenario_id": p["scenario_id"], "status": p["status"], "winner": p.get("paired_winner")}
                         for p in pairs]}
    atomic_json(outdir / "aggregate.json", report)
    (outdir / "aggregate.md").write_text(render(report, pairs))
    print(json.dumps({"report_dir": str(outdir), "completed_pairs": len(completed),
        "status": report["status"], "provider_metrics": report["provider_metrics"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "COMPLETED" else 2

if __name__ == "__main__": raise SystemExit(main())
