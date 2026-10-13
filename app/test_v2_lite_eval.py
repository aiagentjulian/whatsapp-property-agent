import json
import unittest
from pathlib import Path

from .config import get_config
from .v2_lite_eval import (
    SCENARIO_IDS, Usage, load_prompts, project_knowledge, run_dialogue,
)


class PromptOnlyEvaluationTests(unittest.TestCase):
    def test_exactly_one_source_difference_and_distinct_prompt_loads(self):
        prompts = load_prompts()
        self.assertNotEqual(prompts["A_V2"], prompts["B_V2_LITE"])
        self.assertEqual(set(prompts), {"A_V2", "B_V2_LITE"})

    def test_fake_agent_runs_both_prompt_arms_without_network(self):
        prompts = load_prompts()
        config = get_config()
        config.update({"model": "gpt-6-luna", "reasoning": "high"})
        scenario = next(row for row in json.loads(
            (Path(__file__).resolve().parents[1] / "simulator/evaluation/scenarios.json").read_text()
        ) if row["id"] == SCENARIO_IDS[0])
        seen = []
        for arm in ("A_V2", "B_V2_LITE"):
            row = run_dialogue(arm, prompts[arm], scenario, config, Usage(""),
                              project_knowledge(), seen, mock=True)
            self.assertEqual(row["end_reason"], "customer_ended")
            self.assertEqual(row["customer_turn_count"], 2)
            self.assertTrue(any(turn.get("agent_reply") for turn in row["turns"]))
        self.assertEqual([item["arm"] for item in seen], ["A_V2", "A_V2", "B_V2_LITE", "B_V2_LITE"])
        self.assertEqual(seen[0]["sha256"], seen[1]["sha256"])
        self.assertEqual(seen[2]["sha256"], seen[3]["sha256"])
        self.assertNotEqual(seen[0]["sha256"], seen[2]["sha256"])


if __name__ == "__main__":
    unittest.main()
