"""The dated Sales Lab price snapshot must never enter normal Runtime prompts."""
import json
import unittest

from .agent import SalesAgent


class CapturingProvider:
    def __init__(self):
        self.user_prompt = None

    def decide(self, system_prompt, user_prompt):
        self.user_prompt = user_prompt
        return ({'action': 'REPLY', 'sales_move': 'ANSWER', 'buyer_signal': 'QUESTION',
                 'reply': 'The available starting reference is indicative.',
                 'lead_updates': {}, 'support_request': None,
                 'handoff_reason': None, 'handoff_details': None}, {})


class SalesAgentContextTests(unittest.TestCase):
    def test_normal_agent_call_does_not_receive_sales_lab_snapshot(self):
        provider = CapturingProvider()
        agent = SalesAgent({'model': 'gpt-6-luna', 'reasoning': 'high'}, provider=provider)
        agent.decide('How much is it?', {'purchase_purpose': 'UNKNOWN'},
                     [{'direction': 'INBOUND', 'body': 'How much is it?'}], [])
        prompt = json.loads(provider.user_prompt)
        self.assertNotIn('sales_lab_test_context', prompt)
