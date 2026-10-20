"""Cost and isolation guarantees through the real operator CLI function."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .sales_lab import main, fingerprint


class SalesLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.args = ['--run-dir', str(self.root), '--trial', 'dry', '--scenario', 'own_stay', '--customer', 'Own stay from your ad']

    def test_fake_transport_loads_real_brain_and_context(self):
        main(self.args)
        state = json.loads((self.root / 'dry-own_stay.json').read_text())
        context = state['dry_run_context']
        self.assertIn('help an ordinary WhatsApp prospect genuinely want to arrange a property viewing', context['brain_and_skills'])
        self.assertEqual(context['recent_conversation'][0]['body'], 'Own stay from your ad')
        snapshot = context['sales_lab_test_context']
        self.assertEqual(snapshot['source_date'], '2026-08-14')
        self.assertEqual(snapshot['entry_reference']['base_price_myr'], 328000)
        self.assertEqual(snapshot['entry_reference']['indicative_net_on_base_myr'], 301760)
        self.assertIn('not a confirmed unit-level or all-in', ' '.join(snapshot['qualification']))
        self.assertNotIn('private_persona', context)
        self.assertFalse((self.root / 'ledger.json').exists())

    @patch('app.sales_lab.SalesAgent.decide')
    def test_pending_support_allows_natural_customer_continuation(self, decide):
        decide.return_value = ({'action': 'SUPPORT_REQUEST', 'reply': 'What is your comfortable range?',
                                'lead_updates': {}, 'support_request': {'support_type': 'PRICING'}}, {})
        main(self.args)
        main(self.args)
        state = json.loads((self.root / 'dry-own_stay.json').read_text())
        self.assertFalse(state['closed'])
        self.assertEqual(len(state['turns']), 2)
        self.assertEqual([row['direction'] for row in decide.call_args.args[2]][:3],
                         ['INBOUND', 'OUTBOUND', 'INBOUND'])
        self.assertEqual(decide.call_args.args[3][0]['status'], 'OPEN')
        self.assertEqual(decide.call_args.args[3], state['support_context'])

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-not-real'})
    @patch('app.provider.urllib.request.urlopen', side_effect=TimeoutError)
    def test_failed_live_reserves_once_and_stops_no_retry(self, transport):
        main(self.args)
        live = self.args + ['--live']
        live[live.index('dry')] = 'baseline'
        with self.assertRaises(SystemExit): main(live)
        ledger = json.loads((self.root / 'ledger.json').read_text())
        self.assertTrue(ledger['stopped'])
        self.assertEqual(len(ledger['attempts']), 1)
        with self.assertRaises(SystemExit): main(live)
        self.assertEqual(transport.call_count, 1)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-not-real'})
    @patch('app.provider.urllib.request.urlopen')
    def test_budget_and_dry_gate_block_before_transport(self, transport):
        with self.assertRaises(SystemExit): main(self.args + ['--live'])
        (self.root / 'dry_run.json').write_text(json.dumps({'source_sha256': fingerprint()}))
        (self.root / 'ledger.json').write_text(json.dumps({'limit': 1, 'attempts': [{}], 'stopped': False}))
        with self.assertRaises(SystemExit): main(self.args + ['--api-limit', '1', '--live'])
        transport.assert_not_called()

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-not-real'})
    @patch('app.sales_lab.SalesAgent.decide')
    def test_custom_call_limit_is_persisted_and_enforced(self, decide):
        decide.return_value = ({'action': 'REPLY', 'reply': 'A useful response.', 'lead_updates': {}}, {})
        main(self.args)
        live = self.args + ['--api-limit', '1', '--live']
        live[live.index('dry')] = 'baseline'
        main(live)
        ledger = json.loads((self.root / 'ledger.json').read_text())
        self.assertEqual(ledger['limit'], 1)
        self.assertEqual(len(ledger['attempts']), 1)
        self.assertFalse(ledger['stopped'])
        completed_calls = decide.call_count
        self.assertEqual(completed_calls, 2)  # one fake dry turn and one live turn

        second = self.args + ['--api-limit', '1', '--live']
        second[second.index('dry')] = 'candidate'
        with self.assertRaises(SystemExit): main(second)
        self.assertEqual(decide.call_count, completed_calls)
        self.assertEqual(len(json.loads((self.root / 'ledger.json').read_text())['attempts']), 1)
