import json
import unittest
from pathlib import Path

from .config import get_config
from .v2_lite_eval import (
    BASE_SHA, MAIN_ROOT, ROOT, SCENARIO_IDS, Usage, customer_simulator_profile, load_runtimes,
    runtime_evidence, run_dialogue,
)


class MissionLedEvaluationTests(unittest.TestCase):
    def test_both_complete_runtime_bundles_load_distinct_brains(self):
        runtimes = load_runtimes()
        brains, manifest = runtime_evidence(runtimes)
        self.assertEqual(manifest["A_V2"]["runtime_commit"], BASE_SHA)
        self.assertNotEqual(brains["A_V2"], brains["B_V2_LITE"])
        self.assertNotEqual(runtimes["A_V2"].SYSTEM_PROMPT, runtimes["B_V2_LITE"].SYSTEM_PROMPT)
        self.assertEqual(set(manifest["A_V2"]["knowledge_files_sha256"]),
                         set(manifest["B_V2_LITE"]["knowledge_files_sha256"]))
        self.assertEqual(set(SCENARIO_IDS), {
            "P3-family-four-bedroom-budget", "E05-layout-four-bedrooms", "P3-too-expensive-ambiguous",
            "E02-first-home-unsure", "P3-short-oh-okay", "P3-pricing-rebates-maintenance",
            "E30-ready-but-no-pressure", "P3-explicit-no-contact"})

    def test_fake_agent_runs_both_prompt_arms_without_network(self):
        runtimes = load_runtimes()
        brains, _ = runtime_evidence(runtimes)
        config = get_config()
        config.update({"model": "gpt-6-luna", "reasoning": "high"})
        scenario = next(row for row in json.loads(
            (Path(__file__).resolve().parents[1] / "simulator/evaluation/scenarios.json").read_text()
        ) if row["id"] == SCENARIO_IDS[0])
        seen = []
        captures = []
        for arm in ("A_V2", "B_V2_LITE"):
            row = run_dialogue(arm, runtimes[arm], brains[arm], scenario, config, Usage(""),
                              seen, captures, mock=True)
            self.assertEqual(row["end_reason"], "customer_ended")
            self.assertEqual(row["customer_turn_count"], 2)
            self.assertTrue(any(turn.get("agent_reply") for turn in row["turns"]))
        self.assertEqual([item["arm"] for item in seen], ["A_V2", "A_V2", "B_V2_LITE", "B_V2_LITE"])
        self.assertEqual(seen[0]["sha256"], seen[1]["sha256"])
        self.assertEqual(seen[2]["sha256"], seen[3]["sha256"])
        self.assertNotEqual(seen[0]["sha256"], seen[2]["sha256"])
        self.assertEqual([row["arm"] for row in captures], ["A_V2", "A_V2", "B_V2_LITE", "B_V2_LITE"])
        self.assertNotEqual(captures[0]["system_prompt"], captures[2]["system_prompt"])
        self.assertIn("relevant_project_knowledge", captures[0]["available_context"])

    def test_ambiguous_price_seed_uses_only_a_caveated_recorded_range(self):
        rows = json.loads((ROOT / "simulator/evaluation/scenarios.json").read_text())
        scenario = next(row for row in rows if row["id"] == "P3-too-expensive-ambiguous")
        prior_price_message = scenario["seeded_history"][1]["body"]
        self.assertIn("RM3xxk", prior_price_message)
        self.assertIn("confirm current validity", prior_price_message)
        self.assertNotIn("RM558,000", prior_price_message)

    def test_customer_simulator_does_not_receive_evaluator_expectations(self):
        rows = json.loads((ROOT / "simulator/evaluation/scenarios.json").read_text())
        scenario = next(row for row in rows if row["id"] == SCENARIO_IDS[0])
        self.assertNotIn("acceptable_behavior", customer_simulator_profile(scenario))


if __name__ == "__main__":
    unittest.main()
