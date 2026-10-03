#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic geometry, import, semantic-reference, and output-boundary checks."""

import copy
import base64
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
from compose_diagram import compose, namespace, parse_svg, plan, tag


def spec():
    return {"version": 1, "title": "A shared system", "thesis": "Two views combine.",
        "canvas": {"width": 800, "height": 600, "displayWidth": 800, "minTextPx": 14,
                   "margin": 20, "gap": 20, "titleHeight": 50, "footerHeight": 30},
        "grid": {"columns": [1, 1, 1, 1], "rows": [1, 1]},
        "concepts": [{"id": "engine", "label": "Engine"}],
        "panels": [panel("a", 1, 1, 1, 2), panel("b", 2, 1, 1, 2), panel("c", 1, 3, 2, 2)],
        "links": [{"id": "a-c", "from": "a.out", "to": "c.in", "relation": "informs"}]}


def panel(pid, row, column, rows, columns):
    return {"id": pid, "title": pid.upper(), "question": "What belongs here?",
            "claim": "One shared object.", "family": "containment", "reason": "Explicit ownership.",
            "alternative": "A flow invents order.", "source": f"{pid}.svg", "concepts": ["engine"],
            "span": {"row": row, "column": column, "rows": rows, "columns": columns},
            "ports": {"in": [0, 0.5], "out": [1, 0.5]}}


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="diagram-composition-", dir=Path.cwd())
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def svg(self, content='', attrs=''):
        path = self.root / "input.svg"
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 20 100 50" {attrs}>{content}</svg>', encoding="utf-8")
        return path

    def test_grid_spans_and_gutters(self):
        result = plan(spec())
        a, b, c = result["panels"]
        self.assertEqual(a["panel"], [20, 70, 370, 230])
        self.assertEqual(b["panel"], [20, 320, 370, 230])
        self.assertEqual(c["panel"], [410, 70, 370, 480])

    def test_weighted_tracks(self):
        s = spec(); s["grid"]["columns"] = [1, 1, 2, 2]
        self.assertGreater(plan(s)["panels"][2]["body"][2], plan(s)["panels"][0]["body"][2])

    def test_overlap_rejected(self):
        s = spec(); s["panels"][1]["span"]["row"] = 1
        with self.assertRaisesRegex(ValueError, "overlaps"):
            plan(s)

    def test_outside_grid_rejected(self):
        s = spec(); s["panels"][0]["span"]["columns"] = 5
        with self.assertRaisesRegex(ValueError, "exceeds"):
            plan(s)

    def test_invalid_spans_and_numbers(self):
        for bad in (0, -1, 1.5, True):
            s = spec(); s["panels"][0]["span"]["row"] = bad
            with self.assertRaises(ValueError): plan(s)
        for bad in (float("nan"), float("inf"), -1):
            s = spec(); s["canvas"]["width"] = bad
            with self.assertRaises(ValueError): plan(s)

    def test_unknown_concepts(self):
        s = spec(); s["panels"][0]["concepts"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "unknown concept"): plan(s)

    def test_missing_semantic_choice(self):
        s = spec(); s["panels"][0]["alternative"] = ""
        with self.assertRaisesRegex(ValueError, "alternative"): plan(s)

    def test_unknown_ports(self):
        s = spec(); s["links"][0]["to"] = "c.missing"
        with self.assertRaisesRegex(ValueError, "endpoint"): plan(s)

    def test_geometry_can_defer_unbuilt_ports(self):
        s = spec()
        for panel in s["panels"]:
            panel["ports"] = {}
        result = plan(s, defer_ports=True)
        self.assertEqual(result["panels"][0]["panel"], [20, 70, 370, 230])
        self.assertEqual(len(result["warnings"]), 2)
        with self.assertRaisesRegex(ValueError, "Unknown endpoint"):
            plan(s)

    def test_deferred_ports_do_not_accept_unknown_panels(self):
        s = spec(); s["links"][0]["to"] = "missing.in"
        with self.assertRaisesRegex(ValueError, "endpoint panel"):
            plan(s, defer_ports=True)

    def test_layout_cli_accepts_pending_ports_but_compose_rejects(self):
        s = spec()
        for panel in s["panels"]:
            panel["ports"] = {}
        source = self.root / "brief.json"
        source.write_text(json.dumps(s), encoding="utf-8")
        script = Path(__file__).with_name("compose_diagram.py")
        result = subprocess.run([sys.executable, str(script), "layout", "--spec", str(source),
                                 "--output", str(self.root / "layout.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = subprocess.run([sys.executable, str(script), "compose", "--spec", str(source),
                                 "--output", str(self.root / "figure.svg"), "--report", str(self.root / "report.json")],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown endpoint", result.stdout)
        self.assertFalse((self.root / "figure.svg").exists())

    def test_port_range(self):
        s = spec(); s["panels"][0]["ports"]["in"] = [1.2, 0.5]
        with self.assertRaisesRegex(ValueError, "normalized"): plan(s)

    def test_waypoint_range(self):
        s = spec(); s["links"][0]["via"] = [[900, 20]]
        with self.assertRaisesRegex(ValueError, "outside canvas"): plan(s)

    def test_empty_body(self):
        s = spec(); s["panels"][0]["padding"] = 300
        with self.assertRaisesRegex(ValueError, "body space"): plan(s)

    def test_duplicate_ids(self):
        s = spec(); s["panels"][1]["id"] = "a"
        with self.assertRaisesRegex(ValueError, "Duplicate panel"): plan(s)
        with self.assertRaisesRegex(ValueError, "Duplicate source"):
            parse_svg(self.svg('<g id="x"/><g id="x"/>'))

    def test_reference_namespace(self):
        path = self.svg('<title id="title">Hello</title><defs><linearGradient id="paint"/><path id="shape" d="M0 0L1 1"/></defs><use href="#shape" fill="url(#paint)" aria-labelledby="title"/>')
        root, _, _ = parse_svg(path)
        namespace(root, "a-")
        use = root.find(tag("use"))
        self.assertEqual(use.get("href"), "#a-shape")
        self.assertEqual(use.get("fill"), "url(#a-paint)")
        self.assertEqual(use.get("aria-labelledby"), "a-title")

    def test_unresolved_reference(self):
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            parse_svg(self.svg('<path fill="url(#missing)"/>'))

    def test_unsafe_or_nonportable_inputs(self):
        for content in ('<script/>', '<foreignObject/>', '<image href="data:image/png;base64,AA"/>',
                        '<animate/>', '<use href="https://example.com/x.svg#id"/>',
                        '<path onclick="alert(1)"/>', '<path fill="url(https://example.com/x)"/>'):
            with self.subTest(content=content), self.assertRaises(ValueError): parse_svg(self.svg(content))

    def test_css_requires_prepare(self):
        with self.assertRaisesRegex(ValueError, "prepare"):
            parse_svg(self.svg('<style>text{fill:red}</style>'))
        parse_svg(self.svg('<style>text{fill:red}</style>'), allow_style=True)

    def test_embedded_vector_logo(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><defs><path id="mark" d="M0 0L24 24"/></defs><use href="#mark"/></svg>'
        encoded = base64.b64encode(raw).decode()
        root, _, _ = parse_svg(self.svg(f'<image x="4" y="5" width="48" height="48" href="data:image/svg+xml;base64,{encoded}"/>'))
        self.assertIsNone(root.find('.//' + tag('image')))
        use = root.find('.//' + tag('use'))
        ids = {el.get('id') for el in root.iter() if el.get('id')}
        self.assertIn(use.get('href')[1:], ids)

    def test_embedded_svg_cannot_hide_script(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><script/></svg>'
        encoded = base64.b64encode(raw).decode()
        with self.assertRaisesRegex(ValueError, 'script'):
            parse_svg(self.svg(f'<image width="24" height="24" href="data:image/svg+xml;base64,{encoded}"/>'))

    def test_css_external_rejected_before_browser(self):
        with self.assertRaises(ValueError):
            parse_svg(self.svg('<style>@import "https://example.com/a.css";</style>'), allow_style=True)

    def test_source_origin_and_port_transform(self):
        s = spec()
        for panel_data in s["panels"]:
            (self.root / panel_data["source"]).write_text(self.svg('<text x="20" y="40" font-size="16">Engine</text>').read_text(), encoding="utf-8")
        svg, report = compose(s, self.root / "spec.json")
        a = report["panels"][0]
        self.assertAlmostEqual(a["mappedPorts"]["out"][0], a["fitted"][0] + a["fitted"][2])
        self.assertAlmostEqual(a["mappedPorts"]["out"][1], a["fitted"][1] + a["fitted"][3] / 2)
        parsed = ET.fromstring(svg)
        ids = [el.get("id") for el in parsed.iter() if el.get("id")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(parsed.find(tag("metadata")).get("id"), "composition-report")
        self.assertIn('viewBox="10 20 100 50"', svg)

    def test_explicit_route_and_no_invented_arrow(self):
        s = spec(); s["links"][0]["via"] = [[400, 190], [400, 300]]
        for p in s["panels"]:
            (self.root / p["source"]).write_text(self.svg().read_text(), encoding="utf-8")
        svg, report = compose(s, self.root / "spec.json")
        self.assertEqual(report["links"][0]["points"][1:-1], [[400, 190], [400, 300]])
        self.assertNotIn('marker-end=', svg)


if __name__ == "__main__":
    unittest.main()
