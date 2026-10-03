#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Cross-family color identity and rendered-paint failure controls."""

import copy
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
from audit_diagram import COLOR_AUDIT, launch_browser, run
from build_panels import Renderer
from compose_diagram import compose, plan
from test_composition import panel
from test_native_panels import DATA
from playwright.sync_api import sync_playwright


COLORS = {"engine": "#007298"}


class SharedColorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = launch_browser(cls.pw)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def inspect(self, content, panels=None):
        page = self.browser.new_page()
        try:
            page.set_content('<svg xmlns="http://www.w3.org/2000/svg" width="740" height="520">'
                             '<g data-panel-id="subject">' + content + '</g></svg>')
            return page.evaluate(COLOR_AUDIT, {"colors": COLORS,
                "panels": panels or [{"id": "subject", "concepts": ["engine"]}]})
        finally:
            page.close()

    @staticmethod
    def mark(extra="", color="#007298"):
        return ('<rect x="20" y="20" width="80" height="40" '
                'data-color-concept="engine" data-color-channel="fill" '
                f'fill="{color}" {extra}/>')

    def test_native_families_share_one_registry(self):
        for kind, original in DATA.items():
            with self.subTest(kind=kind):
                data = copy.deepcopy(original)
                target = {"hub": lambda: data["center"], "matrix": lambda: data["rows"][0],
                          "taxonomy": lambda: data["groups"][0], "cycle": lambda: data["steps"][0],
                          "boundary": lambda: data}[kind]()
                target["concept"] = "engine"
                target.pop("color", None)
                renderer = Renderer(720, 500, 15, Path.cwd(), colors=COLORS)
                getattr(renderer, kind)(data)
                result = self.inspect(ET.tostring(renderer.root, encoding="unicode"))
                self.assertEqual(result["issues"], [])
                self.assertEqual(result["coverage"]["subject"], ["engine"])

    def test_binding_overrides_and_unknown_ids_rejected(self):
        renderer = Renderer(720, 500, 15, Path.cwd(), colors=COLORS)
        for data in ({"concept":"engine","color":"#e8002a"}, {"concept":"missing"}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                renderer.concept_color(data)

    def test_rendered_css_wins_over_presentation_attribute(self):
        good = self.inspect(self.mark('style="fill:rgb(0, 114, 152)"'))
        self.assertEqual(good["issues"], [])
        bad = self.inspect(self.mark('style="fill:#9e1b32"'))
        self.assertIn("semantic-color-mismatch", {i["kind"] for i in bad["issues"]})

    def test_missing_annotations_and_other_panel_do_not_cover_occurrence(self):
        for content in ('<rect x="20" y="20" width="80" height="40" fill="#007298"/>',
                        '<g data-panel-id="other">' + self.mark() + '</g>'):
            result = self.inspect(content, [{"id":"subject","concepts":["engine"]},
                                           {"id":"other","concepts":["engine"]}])
            self.assertTrue(any(i["kind"]=="semantic-color-missing" and i["panel"]=="subject"
                                for i in result["issues"]))

    def test_hidden_transparent_or_off_canvas_accents_cannot_supply_coverage(self):
        for content in (self.mark('opacity="0"'), '<g opacity="0.5">'+self.mark()+'</g>',
                        '<g display="none">'+self.mark()+'</g>', '<defs>'+self.mark()+'</defs>',
                        '<g transform="translate(1000)">'+self.mark()+'</g>'):
            with self.subTest(content=content):
                result = self.inspect(content)
                self.assertIn("semantic-color-invisible-or-altered", {i["kind"] for i in result["issues"]})
                self.assertEqual(result["coverage"]["subject"], [])

    def test_invalid_channel_group_binding_and_undeclared_concept(self):
        for content in (self.mark().replace('channel="fill"', 'channel="background"'),
                        self.mark().replace('concept="engine"', 'concept="other"'),
                        '<g data-color-concept="engine" data-color-channel="fill">'+self.mark()+'</g>'):
            with self.subTest(content=content):
                self.assertIn("semantic-color-invalid-binding", {i["kind"] for i in self.inspect(content)["issues"]})

    def test_palette_validation(self):
        spec = json.loads((Path(__file__).parents[1]/"assets/templates/composition.json").read_text(encoding="utf-8"))
        for color in ("red", "#123", "#12345678", None):
            spec["concepts"][0]["color"] = color
            with self.subTest(color=color), self.assertRaisesRegex(ValueError, "#RRGGBB"):
                plan(spec)
        spec["concepts"][0]["color"] = "#cfcfcf"
        self.assertEqual(plan(spec)["semanticColors"], {"system":"#cfcfcf"})
        spec["concepts"].append({"id":"different","label":"Other meaning","color":"#cfcfcf"})
        with self.assertRaisesRegex(ValueError, "distinct colors"):
            plan(spec)


class ColorImportTests(unittest.TestCase):
    mark = staticmethod(SharedColorTests.mark)

    def test_compose_prepare_and_final_audit_preserve_bindings(self):
        with tempfile.TemporaryDirectory(prefix="color-contract-", dir=Path.cwd()) as tmp:
            directory = Path(tmp)
            source = directory/"source.svg"
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">'
                '<style>.accent{fill:#007298}</style>' + self.mark('class="accent"', '#e8002a') +
                '<text x="20" y="110" font-size="20">Engine</text></svg>', encoding="utf-8")
            prepared = directory/"ready.svg"
            run(SimpleNamespace(command="prepare", input=source, output=prepared, overwrite=False))
            p = panel("subject",1,1,1,1); p["source"]="ready.svg"
            spec = {"version":1,"title":"Shared color","thesis":"One binding survives import.",
                "canvas":{"width":500,"height":400,"displayWidth":500,"minTextPx":14,
                          "margin":20,"gap":20,"titleHeight":50,"footerHeight":20},
                "grid":{"columns":[1],"rows":[1]},"panels":[p],
                "concepts":[{"id":"engine","label":"Engine","color":"#007298"}]}
            svg, report = compose(spec, directory/"plan.json")
            self.assertEqual(report["semanticColors"], COLORS)
            target = directory/"figure.svg"; target.write_text(svg, encoding="utf-8")
            args = SimpleNamespace(command="audit", input=target, output=None,
                report=directory/"audit.json", screenshot=directory/"preview.png", overwrite=True)
            result = run(args)
            self.assertTrue(result["ok"], result["issues"])
            self.assertEqual(result["semanticColors"]["status"], "checked")
            root = ET.fromstring(svg)
            next(e for e in root.iter() if e.get("data-color-concept")).set("fill", "#e8002a")
            target.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
            result = run(args)
            self.assertFalse(result["ok"])
            self.assertIn("semantic-color-mismatch", {i["kind"] for i in result["issues"]})


if __name__ == "__main__":
    unittest.main()
