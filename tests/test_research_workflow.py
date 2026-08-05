import unittest
from _support import candidate, itb

class ResearchWorkflowTests(unittest.TestCase):
    def test_high_match_adopt_directly(self):
        result = itb.decide_research({"network_available": True, "candidates": [candidate(score=.95)]})
        self.assertEqual(result["decision"], "ADOPT_DIRECTLY")
    def test_partial_match_configure(self):
        result = itb.decide_research({"network_available": True, "candidates": [candidate(score=.75, configurable=True)]})
        self.assertEqual(result["decision"], "ADOPT_WITH_CONFIGURATION")
    def test_combine_multiple_tools(self):
        result = itb.decide_research({"network_available": True, "combination_required": True, "candidates": [candidate("A", .62), candidate("B", .60)]})
        self.assertEqual(result["decision"], "COMBINE_EXISTING_TOOLS")
    def test_extend_open_source(self):
        result = itb.decide_research({"network_available": True, "candidates": [candidate(score=.58, open_source=True)]})
        self.assertEqual(result["decision"], "EXTEND_OPEN_SOURCE")
    def test_offline_never_claims_gap(self):
        result = itb.decide_research({"network_available": False, "candidates": []})
        self.assertEqual(result["decision"], "INSUFFICIENT_RESEARCH"); self.assertFalse(result["candidate_gap"])
    def test_conflicting_results_are_insufficient(self):
        result = itb.decide_research({"network_available": True, "conflicting_evidence": True, "candidates": [candidate(score=.9)]})
        self.assertEqual(result["decision"], "INSUFFICIENT_RESEARCH")
    def test_custom_build_is_only_candidate_gap(self):
        result = itb.decide_research({"network_available": True, "candidates": [candidate(score=.2)]})
        self.assertEqual(result["decision"], "BUILD_CUSTOM"); self.assertTrue(result["candidate_gap"]); self.assertIn("not a proven market opportunity", result["reason"])
    def test_score_rejects_fake_precision_input(self):
        bad = candidate(); bad["functional_fit"] = 12
        with self.assertRaises(itb.IdeaToBuildError): itb.score_candidate(bad)

    def test_online_search_without_candidates_is_insufficient(self):
        result = itb.decide_research({"network_available": True, "candidates": []})
        self.assertEqual(result["decision"], "INSUFFICIENT_RESEARCH"); self.assertFalse(result["candidate_gap"])
    def test_not_recommended_candidate_cannot_be_adopted(self):
        result = itb.decide_research({"network_available": True, "candidates": [candidate(score=.99, not_recommended=True)]})
        self.assertEqual(result["decision"], "NOT_RECOMMENDED")
    def test_report_escapes_markdown_cells(self):
        report, _ = itb.render_research_report({"network_available": True, "candidates": [candidate(name="A|B", score=.7)]})
        self.assertIn("A\\|B", report)
if __name__ == "__main__": unittest.main()