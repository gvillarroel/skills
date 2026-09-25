#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise semantic invariants and invalid-input boundaries."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from build_explorer import build, demo, normalize


def fixture():
    return {"title": "Research groups", "provenance": "Synthetic acceptance data.",
            "dimensions": [{"key": "kind", "label": "Kind", "type": "categorical"},
                           {"key": "tokens", "label": "Tokens", "type": "numeric", "unit": "tokens", "period": "June 2026", "aggregation": "sum"}],
            "nodes": [{"id": "r", "parentId": None, "label": "Root", "values": {"kind": "Leader", "tokens": 10}},
                      {"id": "a", "parentId": "r", "label": "Team", "values": {"kind": "Leader", "tokens": 20}},
                      {"id": "b", "parentId": "a", "label": "Missing", "values": {"tokens": None}},
                      {"id": "c", "parentId": "r", "label": "Zero", "values": {"kind": "Member", "tokens": 0}}]}


class ExplorerTests(unittest.TestCase):
    def test_aggregate_without_double_counting(self):
        data = normalize(fixture())
        self.assertEqual(data["nodes"][0]["aggregates"]["tokens"], {"value": 30, "known": 3})
        self.assertEqual(data["nodes"][0]["count"], 4)

    def test_null_is_not_zero(self):
        nodes = {n["id"]: n for n in normalize(fixture())["nodes"]}
        self.assertEqual(nodes["b"]["aggregates"]["tokens"], {"value": None, "known": 0})
        self.assertEqual(nodes["c"]["aggregates"]["tokens"], {"value": 0, "known": 1})

    def test_angles_reserve_each_managers_own_share(self):
        nodes = {n["id"]: n for n in normalize(fixture())["nodes"]}
        self.assertAlmostEqual(nodes["a"]["x1"]-nodes["a"]["x0"], math.pi)
        self.assertAlmostEqual(nodes["c"]["x1"], math.tau*3/4)
        self.assertAlmostEqual(nodes["b"]["x1"]-nodes["b"]["x0"], math.tau/4)

    def test_input_order_and_leadership_independent_of_depth(self):
        data = normalize(fixture())
        self.assertEqual(data["nodes"][0]["children"], ["a", "c"])
        self.assertEqual(data["dimensions"][0]["categories"], ["Leader", "Member"])

    def test_invalid_tree_cases(self):
        for kind in ["duplicate", "missing-parent", "forest", "cycle", "no-root", "missing-parent-key"]:
            with self.subTest(kind=kind):
                f = fixture()
                if kind == "duplicate": f["nodes"].append(copy.deepcopy(f["nodes"][1]))
                if kind == "missing-parent": f["nodes"][1]["parentId"] = "absent"
                if kind == "forest": f["nodes"][1]["parentId"] = None
                if kind == "cycle": f["nodes"][1]["parentId"] = "b"
                if kind == "no-root": f["nodes"][0]["parentId"] = "b"
                if kind == "missing-parent-key": del f["nodes"][0]["parentId"]
                with self.assertRaises(ValueError): normalize(f)

    def test_invalid_numeric_cases(self):
        for val in [-1, float("nan"), float("inf"), True, "100", 2**54]:
            with self.subTest(value=val):
                f = fixture()
                f["nodes"][0]["values"]["tokens"] = val
                with self.assertRaises(ValueError): normalize(f)

    def test_numeric_period_and_aggregation(self):
        f = fixture()
        del f["dimensions"][1]["period"]
        with self.assertRaises(ValueError): normalize(f)
        f = fixture()
        f["dimensions"][1]["aggregation"] = "average"
        with self.assertRaises(ValueError): normalize(f)

    def test_explicit_categories_cannot_hide_values(self):
        f = fixture()
        f["dimensions"][0]["categories"] = ["Leader"]
        with self.assertRaises(ValueError): normalize(f)
        f["dimensions"][0]["categories"] = ["Leader", "Member"] + list("abcdefg")
        with self.assertRaises(ValueError): normalize(f)

    def test_all_missing_numeric_domain(self):
        f = fixture()
        for n in f["nodes"]: n["values"]["tokens"] = None
        data = normalize(f)
        self.assertEqual(data["dimensions"][1]["maxIndividual"], 0)
        self.assertEqual(data["dimensions"][1]["maxSubtree"], 0)

    def test_singleton_and_nonadditive_metric(self):
        f = fixture()
        f["nodes"] = f["nodes"][:1]
        f["dimensions"][1]["aggregation"] = "none"
        data = normalize(f)
        self.assertEqual(data["maxDepth"], 0)
        self.assertEqual(data["nodes"][0]["aggregates"], {})

    def test_html_closing_tokens_remain_data(self):
        f = fixture()
        f["nodes"][0]["label"] = '</script><script>alert("bad")</script>'
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            destination = Path(directory)/"artifact.html"
            build(f, destination)
            result = destination.read_text(encoding="utf-8")
            self.assertNotIn(f["nodes"][0]["label"], result)
            self.assertIn('\\u003c/script>', result)

    def test_demo_is_exact_and_deterministic(self):
        for count in [2, 45, 1200, 5000]:
            with self.subTest(count=count):
                source = demo(count)
                self.assertEqual(len(normalize(source)["nodes"]), count)
                self.assertEqual(json.dumps(source), json.dumps(demo(count)))

    def test_depth_bound(self):
        f = fixture()
        f["nodes"] = [{"id": str(i), "parentId": str(i-1) if i else None, "label": str(i)} for i in range(66)]
        with self.assertRaises(ValueError): normalize(f)


if __name__ == "__main__":
    unittest.main()
