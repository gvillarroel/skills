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

from build_explorer import build, demo, normalize, pixel_layout
from organic_layout import organic_layout, flood_shape, shape_quality


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

    def test_pixel_layout_coverage_and_determinism(self):
        data = normalize(fixture())
        pixels = pixel_layout(data, 64)
        self.assertEqual(pixels, pixel_layout(data, 64))
        self.assertTrue(all(count > 0 for count in pixels["coverage"]))
        self.assertEqual(sum(pixels["coverage"]), sum(run[1] for row in pixels["rows"] for run in row))
        center = pixels["size"]//2
        self.assertTrue(any(x <= center < x+w and owner == 0 for x, w, owner in pixels["rows"][center]))

    def test_grid_refines_instead_of_dropping_records(self):
        data = normalize(demo(1200))
        pixels = pixel_layout(data, 64)
        self.assertGreater(pixels["size"], 64)
        self.assertEqual(len(pixels["coverage"]), 1200)
        self.assertTrue(all(pixels["coverage"]))

    def test_pixel_bundle_and_options(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            a, b = Path(directory)/"a.html", Path(directory)/"b.html"
            report = build(fixture(), a, view="pixel", pixel_grid=64, initial_lens="kind")
            build(fixture(), b, view="pixel", pixel_grid=64, initial_lens="kind")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(report["patternId"], "hierarchy-radial-pixels")
            self.assertIn('<canvas id="art"', a.read_text(encoding="utf-8"))
            for args in [{"view": "unknown"}, {"view": "pixel", "pixel_grid": 63},
                         {"view": "pixel", "initial_lens": "absent"}]:
                with self.subTest(args=args), self.assertRaises(ValueError):
                    build(fixture(), a, **args)

    def test_organic_equal_squares_and_root(self):
        data = normalize(demo(1200))
        layout = organic_layout(data)
        self.assertEqual(layout["size"],128)
        self.assertEqual(layout["coverage"],[4]*1200)
        self.assertEqual(len({(c["x"],c["y"]) for c in layout["cells"]}),1200)
        self.assertEqual(layout["cells"][0]["tileX"],0)
        self.assertEqual(layout["cells"][0]["tileY"],0)
        self.assertEqual(sum(run[1] for row in layout["rows"] for run in row),4800)

    def test_organic_geometry_independent_of_values(self):
        a = normalize(fixture())
        b = copy.deepcopy(a)
        for n in b["nodes"]:
            n["values"] = {"kind":"Changed","tokens":900}
        self.assertEqual(organic_layout(a),organic_layout(b))
        self.assertEqual(organic_layout(a,seed=42),organic_layout(a,seed=42))
        self.assertNotEqual(organic_layout(normalize(demo(120)),seed=42)["cells"],organic_layout(normalize(demo(120)),seed=43)["cells"])

    def test_organic_front_is_solid_across_counts_and_seeds(self):
        for count in [1,7,120,1200,5000]:
            for seed in [0,1,42,73021]:
                with self.subTest(count=count,seed=seed):
                    sites = flood_shape(count,seed)
                    self.assertEqual(shape_quality((x,y) for x,y,_ in sites),(True,0))
                    self.assertEqual([s[2] for s in sites],sorted(s[2] for s in sites))

    def test_organic_generation_order_and_pathological_trees(self):
        for kind in ['chain','star','uneven']:
            with self.subTest(kind=kind):
                source = fixture()
                source['nodes'] = [{'id':str(i),'parentId':None if i==0 else str(i-1) if kind=='chain' else '0' if kind=='star' or i<5 else '1','label':str(i)} for i in range(60)]
                data=normalize(source)
                layout=organic_layout(data)
                ordered=sorted(layout['cells'],key=lambda c:c['birth'])
                self.assertEqual([data['nodes'][c['node']]['depth'] for c in ordered],sorted(n['depth'] for n in data['nodes']))
                for size in [1,3,4]:
                    scaled=organic_layout(data,cell_pixels=size)
                    self.assertEqual(scaled['coverage'],[size**2]*60)
                    root=scaled['cells'][0]
                    self.assertTrue(root['x'] <= scaled['size']//2 < root['x']+size)
                    self.assertTrue(root['y'] <= scaled['size']//2 < root['y']+size)

    def test_organic_option_validation_and_bundle(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            target=Path(directory)/'organic.html'
            report=build(fixture(),target,view='organic')
            self.assertEqual(report['patternId'],'hierarchy-organic-pixels')
            self.assertEqual(report['minPixelsPerRecord'],4)
            self.assertIn('id="hierarchy-organic-pixels"',target.read_text(encoding='utf-8'))
            for options in [{'cell_pixels':0},{'cell_pixels':True},{'cell_pixels':2.0},{'cell_pixels':5},{'seed':True},{'seed':-1},{'seed':2**32}]:
                with self.subTest(options=options),self.assertRaises(ValueError):
                    build(fixture(),target,view='organic',**options)


if __name__ == "__main__":
    unittest.main()
