#!/usr/bin/env python3
"""Isolated local evaluation for Laya -> Nano-Jev -> the existing Luna SalesAgent.

Run from the repository root in the separately created Python environment. Model
and Hugging Face caches are controlled by HF_HOME and must stay outside this repo.
"""
import argparse
import json
import os
import resource
import statistics
import time
from pathlib import Path

import laya
import nanojev

ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = Path(__file__).with_name("cases.json")
LAYA_REVISION = "1a793eb568e6718f15941d08f85432581df534e3"
NANOJEV_REVISION = "ffee345e97797bef0948561461ea54fe558588a0"
CHOICES = {
    "intent": {
        "asks_unverified_returns": "Requests a rental yield or future appreciation estimate that is not established by supplied evidence.",
        "requests_multiple_evidence_items": "Requests several facts and their sources, including facts not yet known.",
        "returns_to_unresolved_request": "Follows up on an unresolved part after a different part was answered.",
        "raises_safety_and_flood_concern": "Raises safety, infrastructure or flood-risk concerns.",
        "requests_recommendation_with_constraints": "Asks for a recommendation while stating competing requirements or budget constraints.",
        "continues_due_diligence": "Continues factual due diligence without showing appointment intent.",
        "confirms_hard_product_mismatch": "States that a confirmed product mismatch is a firm requirement.",
        "asks_for_space_after_overload": "Says the information load is too much and asks for time.",
        "neutral_acknowledgement": "Gives a brief neutral acknowledgement without a new buying signal.",
        "asks_specific_verified_fact": "Asks a direct factual question answerable from project knowledge."
    },
    "next_move": {
        "avoid_unsupported_claim_and_offer_verification": "Avoid unsupported returns or forecasts and offer to verify the necessary evidence.",
        "answer_known_parts_and_verify_missing_evidence": "Answer known parts, separate unknown facts and arrange verification for those gaps.",
        "continue_unresolved_item_without_repeating_resolved_item": "Continue the unresolved request and do not repeat the already supplied information.",
        "answer_with_limits_and_no_guarantee": "Answer from documented facts, state limits and avoid absolute safety guarantees.",
        "clarify_tradeoff_before_recommending": "Ask one useful question to resolve the stated tradeoff before recommending a unit.",
        "answer_due_diligence_without_pushing_viewing": "Continue due diligence without assuming readiness to view.",
        "acknowledge_mismatch_without_repitching": "Acknowledge the hard mismatch and avoid selling around it.",
        "brief_acknowledgement_and_give_space": "Briefly acknowledge and give the buyer time.",
        "do_not_infer_purchase_intent": "Do not treat a neutral acknowledgement as purchase intent.",
        "answer_direct_question_from_knowledge": "Answer the direct question from verified knowledge."
    }
}


def read_cases():
    return json.loads(CASE_FILE.read_text(encoding="utf-8"))


def load_passages(paths):
    from app.knowledge import _passages, KNOWLEDGE

    out = []
    for relative in paths:
        file_path = KNOWLEDGE / relative
        for heading, body in _passages(file_path.read_text(encoding="utf-8")):
            # Keep pairs short enough for the 512-token cross-encoder limit.
            content = (heading + "\n" + body)[:1500]
            out.append({"path": relative, "heading": heading, "content": content})
    return out


def laya_questions():
    return {
        name: {"type": "choice", "instructions": instructions, "criteria": CHOICES[name]}
        for name, instructions in (
            ("intent", "What is the customer's latest actionable intent in this conversation? Choose the most specific current intent."),
            ("next_move", "What should the salesperson do next to respond helpfully, accurately and without pressure?")
        )
    }


def run_decisions(agent, cases):
    rows, durations = [], []
    for case in cases["decision_cases"]:
        start = time.perf_counter()
        result = agent.predict(case["state"], laya_questions())
        duration = (time.perf_counter() - start) * 1000
        durations.append(duration)
        answers = result["answers"]
        rows.append({
            "id": case["id"], "source": case["source"], "expected": {"intent": case["intent"], "next_move": case["next_move"]},
            "predicted": {key: value.get("choice") for key, value in answers.items()},
            "probabilities": {key: value.get("probabilities", {}) for key, value in answers.items()},
            "confidence": {key: value.get("confidence") for key, value in answers.items()}, "latency_ms": round(duration, 2)
        })
    total = sum(1 for row in rows for key in ("intent", "next_move") if row["expected"][key] == row["predicted"][key])
    count = len(rows) * 2
    return {"model": "convaiinnovations/laya-typed-decisions", "revision": LAYA_REVISION,
            "cases": rows, "accuracy": total / count if count else None, "correct": total, "decisions": count,
            "median_warm_inference_ms": round(statistics.median(durations), 2),
            "omissions_or_misclassifications": [row["id"] for row in rows if any(row["expected"][k] != row["predicted"][k] for k in ("intent", "next_move"))]}


def rank_candidates(decider, query, candidates):
    scores = decider.relevance(query, [item["content"] for item in candidates])
    ranked = []
    for item, probabilities in zip(candidates, scores):
        ranked.append({**item, "probabilities": probabilities,
                       "rank_score": probabilities.get("directly answers", 0.0) + 0.35 * probabilities.get("partially relevant", 0.0)})
    ranked.sort(key=lambda x: x["rank_score"], reverse=True)
    return ranked


def retrieval_metrics(rows, k=3):
    hits = 0
    recalls = []
    for row in rows:
        expected = set(row["gold_paths"])
        chosen = [item["path"] for item in row["ranked"][:k]]
        found = expected.intersection(chosen)
        hits += bool(found)
        recalls.append(len(found) / max(len(expected), 1))
    return {"top_1_path_hit_rate": sum(bool(set(r["gold_paths"]).intersection([x["path"] for x in r["ranked"][:1]])) for r in rows) / max(len(rows), 1),
            "top_3_path_hit_rate": hits / max(len(rows), 1), "mean_gold_path_recall_at_3": sum(recalls) / max(len(recalls), 1)}


def run_retrieval(decider, cases):
    from app.knowledge import retrieve

    rows, durations, sufficient, grounded = [], [], [], []
    for case in cases["retrieval_cases"]:
        candidates = load_passages(case["candidate_paths"])
        start = time.perf_counter()
        ranked = rank_candidates(decider, case["query"], candidates)
        durations.append((time.perf_counter() - start) * 1000)
        baseline = retrieve(case["query"], {})
        rows.append({"id": case["id"], "query": case["query"], "gold_paths": case["gold_paths"],
                     "baseline_top_paths": [item["path"] for item in baseline], "ranked": ranked,
                     "selected_paths": list(dict.fromkeys(item["path"] for item in ranked[:8]))[:4]})

    for case in cases["sufficiency_cases"]:
        material = load_passages(case["paths"])
        context = "\n\n".join(item["content"] for item in material)
        start = time.perf_counter()
        score = decider.sufficient(case["query"], [context])
        durations.append((time.perf_counter() - start) * 1000)
        sufficient.append({"id": case["id"], "expected_sufficient": case["sufficient"], "probabilities": score,
                           "predicted_sufficient": score.get("yes", 0.0) >= 0.5})

    for case in cases["grounding_cases"]:
        material = load_passages(case["paths"])
        context = "\n\n".join(item["content"] for item in material)
        start = time.perf_counter()
        score = decider.grounded(case["claim"], context)
        durations.append((time.perf_counter() - start) * 1000)
        grounded.append({"id": case["id"], "expected_grounded": case["grounded"], "probabilities": score,
                         "predicted_grounded": score.get("yes", 0.0) >= 0.5})

    rel = retrieval_metrics(rows)
    base_rows = [{"gold_paths": row["gold_paths"], "ranked": [{"path": path} for path in row["baseline_top_paths"]]} for row in rows]
    base = retrieval_metrics(base_rows)
    suff_correct = sum(x["expected_sufficient"] == x["predicted_sufficient"] for x in sufficient)
    ground_correct = sum(x["expected_grounded"] == x["predicted_grounded"] for x in grounded)
    return {"model": "sdmlai/nano-jev@v1.0", "cases": rows, "ranking_metrics": rel,
            "existing_retrieval_baseline_metrics": base, "sufficiency": sufficient,
            "sufficiency_accuracy": suff_correct / max(len(sufficient), 1), "groundedness": grounded,
            "groundedness_accuracy": ground_correct / max(len(grounded), 1),
            "median_warm_inference_ms": round(statistics.median(durations), 2),
            "mistakes": {"sufficiency": [x["id"] for x in sufficient if x["expected_sufficient"] != x["predicted_sufficient"]],
                         "groundedness": [x["id"] for x in grounded if x["expected_grounded"] != x["predicted_grounded"]]}}


def laya_hint(agent, case):
    result = agent.predict(case["history"], laya_questions())
    return {"choices": {name: answer.get("choice") for name, answer in result["answers"].items()},
            "probabilities": {name: answer.get("probabilities", {}) for name, answer in result["answers"].items()},
            "confidence": {name: answer.get("confidence") for name, answer in result["answers"].items()}}


def run_combo(laya_agent, decider, cases):
    from app.agent import SalesAgent
    from app.config import get_config
    from app.knowledge import retrieve

    sales_agent = SalesAgent(get_config())
    output = []
    for case in cases["combo_cases"]:
        latest = case["history"][-1]["body"]
        laya_start = time.perf_counter()
        hint = laya_hint(laya_agent, case)
        laya_ms = (time.perf_counter() - laya_start) * 1000

        # Use the real Sales Core V2 retriever's candidates as Nano-Jev's input.
        # This measures the intended reranking/filter step, not a slow full-corpus scan.
        candidate_chunks = retrieve(latest, case["profile"], limit=8)
        nano_start = time.perf_counter()
        ranked = rank_candidates(decider, latest, candidate_chunks)
        nano_ms = (time.perf_counter() - nano_start) * 1000
        # Apply Nano-Jev's documented irrelevance probability threshold to each
        # candidate; a rejected set remains empty and Luna sees that context gap.
        selected = [item for item in ranked if item["probabilities"].get("irrelevant", 1.0) < 0.5]
        chosen_paths = list(dict.fromkeys(item["path"] for item in selected))
        sufficiency = decider.sufficient(latest, ["\n\n".join(item["content"] for item in selected)]) if selected else {"yes": 0.0, "no": 1.0}
        route_context = {"local_laya_hint": hint, "local_nanojev": {"selected_knowledge_paths": chosen_paths,
                         "candidate_scores": [{"path": item["path"], "heading": item["heading"],
                                               "irrelevant": round(item["probabilities"].get("irrelevant", 0.0), 4),
                                               "directly_answers": round(item["probabilities"].get("directly answers", 0.0), 4)}
                                              for item in ranked],
                         "passages_sufficient_probability": sufficiency.get("yes", 0.0)}}

        baseline_start = time.perf_counter()
        baseline, baseline_usage = sales_agent.decide(latest, case["profile"], case["history"], [])
        baseline_ms = (time.perf_counter() - baseline_start) * 1000
        combo_start = time.perf_counter()
        combo, combo_usage = sales_agent.decide(latest, case["profile"], case["history"], [],
                                                knowledge_paths=chosen_paths, routing_context=route_context)
        combo_ms = (time.perf_counter() - combo_start) * 1000
        output.append({"id": case["id"], "source": case["source"], "latest_customer_message": latest,
                       "nano_candidate_scores": route_context["local_nanojev"]["candidate_scores"],
                       "selected_knowledge_paths": chosen_paths, "nano_sufficiency": sufficiency,
                       "laya_hint": hint, "baseline_sales_core_v2": {"reply": baseline["reply"], "buyer_signal": baseline["buyer_signal"], "sales_move": baseline["sales_move"], "latency_ms": round(baseline_ms, 2), "usage": baseline_usage},
                       "laya_nanojev_luna": {"reply": combo["reply"], "buyer_signal": combo["buyer_signal"], "sales_move": combo["sales_move"], "latency_ms": round(combo_ms, 2), "usage": combo_usage},
                       "local_stage_latency_ms": {"laya": round(laya_ms, 2), "nanojev": round(nano_ms, 2)}})
    return {"cases": output}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("decisions", "retrieval", "local", "combo", "all"), default="local")
    parser.add_argument("--env-file", type=Path, help="private local env file with OPENAI_API_KEY; never copied to the branch")
    parser.add_argument("--output", type=Path, default=Path("/tmp/laya-nanojev-results.json"))
    args = parser.parse_args()
    if args.env_file:
        from app.config import load_env_file
        load_env_file(args.env_file)
    cases = read_cases()
    report = {"versions": {"python": os.sys.version.split()[0], "laya": "0.4.6", "nano_jev": "1.0.0",
                           "laya_checkpoint": "convaiinnovations/laya-typed-decisions@" + LAYA_REVISION,
                           "nano_jev_checkpoint": "sdmlai/nano-jev@" + NANOJEV_REVISION},
              "measurements": {"max_rss_bytes": None, "laya_device": "mps"}}
    laya_agent = None
    decider = None
    if args.phase in ("decisions", "local", "combo", "all"):
        started = time.perf_counter()
        laya_agent = laya.load("typed-decisions", device="mps", revision="reviewed")
        report["laya_load_seconds"] = round(time.perf_counter() - started, 2)
    if args.phase in ("retrieval", "local", "combo", "all"):
        started = time.perf_counter()
        decider = nanojev.load("sdmlai/nano-jev@" + NANOJEV_REVISION)
        report["nanojev_load_seconds"] = round(time.perf_counter() - started, 2)
        report["nanojev_device"] = str(getattr(decider, "device", "cpu"))
    if args.phase in ("decisions", "local", "all"):
        report["laya_decisions"] = run_decisions(laya_agent, cases)
    if args.phase in ("retrieval", "local", "all"):
        report["nanojev_retrieval"] = run_retrieval(decider, cases)
    if args.phase in ("combo", "all"):
        report["combo"] = run_combo(laya_agent, decider, cases)
    report["measurements"]["max_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"phase": args.phase, "output": str(args.output), "max_rss_bytes": report["measurements"]["max_rss_bytes"],
                      "laya_accuracy": report.get("laya_decisions", {}).get("accuracy"),
                      "nanojev_ranking": report.get("nanojev_retrieval", {}).get("ranking_metrics"),
                      "combo_cases": len(report.get("combo", {}).get("cases", []))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
