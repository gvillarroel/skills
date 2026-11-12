#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression cases for connected flow identity and mixed-chart wire boundaries."""
import copy
import unittest

from check_connected_spec import validate


class ConnectedRecipes(unittest.TestCase):
    def test_exact_label_flow(self):
        spec = {"preset": "sankey", "data": {"nodes": ["Queue", "Worker"], "links": [["Queue", "Worker", 9]]}}
        self.assertEqual(validate(spec), [])
        for endpoints in [[0, 1, 9], ["Queue", "Missing", 9], ["Queue", "Worker", -1], ["Queue", "Worker", True]]:
            changed = copy.deepcopy(spec)
            changed["data"]["links"] = [endpoints]
            self.assertTrue(validate(changed), endpoints)

    def test_real_mark_component_separation(self):
        spec = {"version": 1, "factory": "chart", "marks": [{"kind": "line", "args": [[0, 1], [4, 9]]}], "components": [{"kind": "legend", "kwargs": {"loc": "lower right"}}]}
        self.assertEqual(validate(spec), [])
        changed = copy.deepcopy(spec)
        changed["components"] = [{"type": "legend"}]
        self.assertTrue(validate(changed))
        changed["components"] = [{"kind": "line", "args": [[0, 1], [8, 8]]}]
        self.assertTrue(validate(changed))

    def test_paired_values_and_finite_boundaries(self):
        for x, y in [([0, 1], [9]), ([0, 1], [True, 9]), ([0, 1], [float("inf"), 9])]:
            self.assertTrue(validate({"preset": "line", "data": {"x": x, "y": y}}))
        self.assertEqual(validate({"preset": "line", "data": {"x": [0, 1], "y": [4, 9]}}), [])

    def test_preset_cannot_hide_a_mixed_chart(self):
        self.assertTrue(validate({"preset": "line", "data": {"x": [0, 1], "y": [4, 9]}, "components": [{"type": "line"}]}))


if __name__ == "__main__":
    unittest.main()
