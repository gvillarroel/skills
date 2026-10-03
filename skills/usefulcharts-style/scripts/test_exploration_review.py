#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reject coverage-only and unsupported discovery claims independently of scores."""
import copy
import hashlib
import json
import unittest
import test_illustrated_review as coverage_tests
from assess_exploration_review import assess


class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = coverage_tests.ReviewTests()
        self.fixture.setUp()
        self.base = self.fixture.base
        (self.base / "coverage.json").write_text(json.dumps(self.fixture.review), encoding="utf-8")
        (self.base / "poster.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><g id="a" data-record-id="a1"><text>A</text></g><g id="b" data-record-id="b1"><text>B</text></g><path id="ab" d="M0 0L10 10"/></svg>', encoding="utf-8")
        self.data = dict(schema_version=1, illustrated_review="coverage.json", svg=self.evidence("poster.svg"), actual_pixel_review=True,
            reference=dict(source_url="https://example.org/reference", whole=self.evidence("whole.png"), detail=self.evidence("detail.png"), reviewed_images=True, comparison_basis="same-width-whole-and-relative-detail", comparisons={k:"Fixture observation; not a visual claim." for k in ("structure", "image_ownership", "color_continuity", "reading_rhythm")}, convincing_family_resemblance=True, remaining_differences=[]),
            discovery_routes=[dict(id=str(i), anchors=["a1","b1"], question="Fixture comparison", answer="Fixture answer", operation="trace" if i==0 else "compare", region="upper" if i==0 else "lower", reviewed_at_reading_size=True, requires_detached_lookup=False, detail=self.evidence("detail.png"), steps=[dict(element_ids=["a","ab"],observation="Follow the printed path."),dict(element_ids=["b"],observation="Read the destination.")]) for i in range(3)], unresolved_composition_defects=[])

    def evidence(self, name):
        return dict(path=name, sha256=hashlib.sha256((self.base/name).read_bytes()).hexdigest())

    def tearDown(self):
        self.fixture.tearDown()

    def reject(self, code):
        result=assess(self.data,self.base)
        self.assertFalse(result["declared_exploratory_composition_pass"])
        self.assertIn(code,result["failures"])

    def test_pending_density_never_becomes_reference_pass(self):
        result=assess(self.data,self.base)
        self.assertTrue(result["declared_exploratory_composition_pass"])
        self.assertFalse(result["declared_reference_target_pass"])

    def test_remaining_difference_prevents_reference_pass(self):
        self.fixture.review["reference_density_status"]="verified"
        (self.base/"coverage.json").write_text(json.dumps(self.fixture.review),encoding="utf-8")
        self.data["reference"]["remaining_differences"]=["Picture rail remains."]
        result=assess(self.data,self.base)
        self.assertTrue(result["declared_exploratory_composition_pass"])
        self.assertFalse(result["declared_reference_target_pass"])

    def test_coverage_does_not_supply_routes(self):
        self.data["discovery_routes"]=[];self.reject("insufficient-discovery-routes")

    def test_distant_code_lookup_is_not_integration(self):
        self.data["discovery_routes"][0]["requires_detached_lookup"]=True;self.reject("detached-discovery")

    def test_prompt_without_graphical_steps_fails(self):
        self.data["discovery_routes"][0]["steps"]=[];self.reject("missing-visible-steps")

    def test_invented_svg_anchor_fails(self):
        self.data["discovery_routes"][0]["steps"][0]["element_ids"]=["absent"];self.reject("missing-printed-element")

    def test_stale_svg_fails(self):
        (self.base/"poster.svg").write_text("<svg/>");self.reject("stale-svg")

    def test_missing_reference_comparison_fails(self):
        self.data["reference"]["comparisons"]["image_ownership"]="";self.reject("unexplained-reference-image_ownership")

    def test_repeated_single_operation_fails(self):
        for route in self.data["discovery_routes"]:route["operation"]="trace"
        self.reject("single-reading-operation")

    def test_concentrated_examples_fail(self):
        for route in self.data["discovery_routes"]:route["region"]="upper"
        self.reject("concentrated-discovery")

    def test_no_direct_review_fails(self):
        self.data["actual_pixel_review"]=False;self.reject("no-pixel-review")

    def test_material_composition_issue_fails(self):
        self.data["unresolved_composition_defects"]=["Main branch requires a distant lookup."];self.reject("unresolved-composition")

    def test_duplicate_routes_fail(self):
        self.data["discovery_routes"][1]=copy.deepcopy(self.data["discovery_routes"][0]);self.reject("duplicate-or-missing-route")

    def test_missing_actual_record_fails(self):
        text=(self.base/"poster.svg").read_text().replace('data-record-id="b1"','data-record-id="wrong"')
        (self.base/"poster.svg").write_text(text);self.data["svg"]=self.evidence("poster.svg");self.reject("missing-printed-record")


if __name__ == "__main__":
    unittest.main()
