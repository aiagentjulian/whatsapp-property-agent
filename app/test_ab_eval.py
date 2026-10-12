import unittest

from app.ab_eval import (
    BudgetStop,
    Ledger,
    _bootstrap_cluster_ci,
    _is_clef_quota_exhausted,
    _load_scenarios,
    _valid_for_expansion,
    summarize_dialogues,
)
from app.agent import SalesAgent
from app.knowledge import retrieve


class SalesCoreClefEvaluationTests(unittest.TestCase):
    def test_v2_prompt_stays_unchanged_and_clef_hypotheses_are_optional_hints(self):
        class RecordingProvider:
            def __init__(self):
                self.calls = []

            def decide(self, system, user):
                import json
                self.calls.append((system, json.loads(user)))
                return {"action": "REPLY", "sales_move": "ANSWER", "buyer_signal": "QUESTION",
                        "reply": "Hello.", "lead_updates": {}}, {"input_tokens": 1, "output_tokens": 1}

        provider = RecordingProvider()
        agent = SalesAgent({"model": "gpt-6-luna", "reasoning": "high", "api_key": "unused"}, provider=provider)
        args = ("Hi, tell me more?", {"purchase_purpose": "UNKNOWN"},
                [{"direction": "INBOUND", "body": "Hi, tell me more?"}], [])
        agent.decide(*args)
        baseline_system, baseline_user = provider.calls[-1]
        self.assertNotIn("clef_routing_hypotheses", baseline_user)

        agent.decide(*args, knowledge_paths=["01_facts/overview.md"],
                     routing_context={"intent_level": "LOW", "buyer_signal": "NEUTRAL"})
        routed_system, routed_user = provider.calls[-1]
        self.assertEqual(routed_user["clef_routing_hypotheses"]["intent_level"], "LOW")
        self.assertIn("fallible", routed_system)
        self.assertNotIn("clef_routing_hypotheses", baseline_user)
        self.assertNotEqual(baseline_system, routed_system)

    def test_dataset_has_thirty_distinct_buyer_contexts_and_openers(self):
        scenarios = _load_scenarios()
        self.assertGreaterEqual(len(scenarios), 30)
        self.assertEqual(len(scenarios), len({row["id"] for row in scenarios}))
        self.assertGreaterEqual(len({row["opening_message"] for row in scenarios}), 30)
        for scenario in scenarios:
            for key in ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior"):
                self.assertTrue(scenario[key])

    def test_clef_retrieval_is_limited_to_selected_knowledge_paths(self):
        routed = retrieve("What is the maintenance fee?", {}, allowed_paths=["01_facts/overview.md"])
        self.assertTrue(routed)
        self.assertTrue(all(row["path"] == "01_facts/overview.md" for row in routed))
        empty = retrieve("What is the maintenance fee?", {}, allowed_paths=[])
        self.assertEqual(empty, [])

    def test_combined_usage_budget_blocks_next_request(self):
        ledger = Ledger(max_usd=0.00015, max_neurons=100, secrets=())
        reserve = ledger.reserve_openai("x" * 100, max_output_tokens=200)
        ledger.finish_openai(reserve, {"input_tokens": 100, "output_tokens": 100}, 1, "test")
        with self.assertRaises(BudgetStop):
            ledger.reserve_openai("y" * 100, max_output_tokens=200)

    def test_clef_daily_neuron_quota_is_a_stop_condition(self):
        body = {"errors": [{"code": 4006, "message": "you have used up your daily free allocation of 10,000 neurons"}]}
        self.assertTrue(_is_clef_quota_exhausted(429, body))
        self.assertFalse(_is_clef_quota_exhausted(500, {"errors": [{"code": 5000, "message": "temporary failure"}]}))

    def test_pilot_expansion_requires_complete_blind_reviews_and_real_clef(self):
        rows = []
        for scenario_id in ("1", "2", "3", "4", "5"):
            for arm in ("A_SALES_CORE_V2", "B_CLEF_ROUTED"):
                rows.append({"scenario_id": scenario_id, "arm": arm, "end_reason": "customer_ended",
                             "transcript": [{"speaker": "customer", "text": "Hi"}, {"speaker": "agent", "text": "Hello"}],
                             "blind_judgment": "complete", "turns": [{"clef": {"model": "@cf/cloudflare/clef"},
                                 "customer_next_stance": "interested" if scenario_id in ("1", "2") else "doubtful"}]})
        self.assertTrue(_valid_for_expansion(rows)[0])
        rows[-1]["blind_judgment"] = "failed"
        self.assertFalse(_valid_for_expansion(rows)[0])

    def test_cluster_bootstrap_reports_uncertainty_without_overclaiming(self):
        pairs = [{"scenario_id": str(i), "A_score": 3.0, "B_score": 3.1} for i in range(30)]
        result = _bootstrap_cluster_ci(pairs, samples=1000)
        self.assertEqual(result["n_scenarios"], 30)
        self.assertEqual(result["ci95"], [0.1, 0.1])
        self.assertIn("B higher", result["statistical_signal"])

    def test_summary_keeps_failures_out_of_quality_means(self):
        score = {key: 4 for key in ("intent_understanding", "natural_continuation", "valuable_questions",
                                    "relevant_advantages", "customer_interest", "non_repetition",
                                    "factual_accuracy", "appropriate_pacing")}
        dialogues = [{"arm": "A_SALES_CORE_V2", "customer_turn_count": 2, "end_reason": "customer_ended",
                      "judgment": {"scores": score}},
                     {"arm": "B_CLEF_ROUTED", "customer_turn_count": 2, "end_reason": "agent_error", "judgment": None}]
        summary = summarize_dialogues(dialogues, [])
        self.assertEqual(summary["arms"]["A_SALES_CORE_V2"]["composite_mean_1_to_5"], 4.0)
        self.assertIsNone(summary["arms"]["B_CLEF_ROUTED"]["composite_mean_1_to_5"])


if __name__ == "__main__":
    unittest.main()
