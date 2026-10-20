import unittest
from .knowledge import retrieve, focused_sales_context


class SalesEvidenceTests(unittest.TestCase):
    def test_ad_filler_does_not_retrieve_random_facilities(self):
        self.assertEqual(retrieve('Hi, I’m enquiring from your Pearl Residences ad. I’m looking for a place for my own stay. Could you share more details?'), [])

    def test_office_gets_layout_evidence_not_skypark(self):
        q = 'My partner and I need space for a home office'
        evidence = focused_sales_context(q, {}, [])
        self.assertTrue(any('Layout' in p['angle'] for p in evidence['optional_sales_angles']))
        self.assertFalse(any('SkyPark' in p['angle'] for p in evidence['optional_sales_angles']))
        self.assertIn('Layout and room arrangement', [p['heading'] for p in retrieve(q)])

    def test_multi_part_price_layout_and_completion_are_not_lost(self):
        data = retrieve('What is the price range, floor plan and completion?')
        self.assertEqual(len(data), 3)
        text = '\n'.join(p['content'] for p in data)
        for fact in ('RM328k', 'car-park premium', '14 August 2026', 'Do not determine rebate only', 'current unit/base-price structure', 'Q4 2029', 'outward-facing windows'):
            self.assertIn(fact, text)

    def test_investment_gets_holding_costs_without_returns_or_identity(self):
        text = '\n'.join(p['content'] for p in retrieve('I am considering it as an investment'))
        for fact in ('RM0.18', 'Q4 2029', 'Freehold'):
            self.assertIn(fact, text)
        self.assertNotIn('Project name: SkyWorld', text)

    def test_everyday_shops_wording_retrieves_location_sales_angle(self):
        q = 'What is the area like for getting to shops and things?'
        evidence = focused_sales_context(q, {}, [])
        location = next((p for p in evidence['optional_sales_angles'] if 'Location' in p['angle']), None)
        self.assertIsNotNone(location)
        self.assertIn('Sunway Carnival Mall', location['verified_evidence'])

    def test_combined_price_and_location_question_keeps_both_fact_groups(self):
        data = retrieve('Could you share roughly where Pearl Residences is and the starting price?')
        text = '\n'.join(p['content'] for p in data)
        self.assertIn('RM328k', text)
        self.assertIn('Seberang Jaya', text)
        self.assertIn('Sunway Carnival Mall', text)

    def test_area_or_nearest_landmark_question_retrieves_location_facts(self):
        data = retrieve('Could you share the area or nearest landmark so we can check the commute?')
        text = '\n'.join(p['content'] for p in data)
        self.assertIn('Seberang Jaya', text)
        self.assertIn('Butterworth', text)
