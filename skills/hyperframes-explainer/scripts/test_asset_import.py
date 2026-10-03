#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Run: uv run --script scripts/test_asset_import.py --work-dir <project-artifacts>."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
import explainer as engine
import import_assets as importer
STARTER = json.loads((engine.BUNDLE / "assets/templates/brief.json").read_text(encoding="utf-8"))
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><title>Valve</title><g transform="translate(10 12)" stroke="#333e48" fill="none"><ellipse id="body" cx="30" cy="30" rx="16" ry="10"/><path id="gate" d="M0 -8 L0 8"/><text id="readout" x="4" y="80" fill="#333e48" stroke="none" font-size="26">Q</text></g></svg>'


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.brief = copy.deepcopy(STARTER)
        self.svg = self.root / "valve.svg"; self.svg.write_text(SVG, encoding="utf-8")
        self.plan = {"schemaVersion": 1, "assets": [{"id": "valve", "path": "valve.svg", "producer": "svg-brief-design",
                     "purpose": "Expose the moving gate.", "view": "tank", "moments": ["establish", "hold"],
                     "placement": [20, 30], "ports": {"inlet": [0, 30]},
                     "bindings": {"gate": {"attrs": {"rotation": {"mul": ["rate", 18]}}}, "readout": {"value": "rate", "unit": "L/s"}}}]}

    def run_import(self):
        engine.write_json(self.root / "brief.json", self.brief); engine.write_json(self.root / "plan.json", self.plan)
        return importer.assemble(self.root / "brief.json", self.root / "plan.json", self.root / "assembled.json")

    def test_translated_assets_keep_geometry_and_bound_ids(self):
        report = self.run_import(); self.assertTrue(report["ok"], report["findings"])
        brief = json.loads((self.root / "assembled.json").read_text())
        body = next(m for m in brief["marks"] if m["id"] == "valve-body")
        self.assertEqual(body["attrs"], {"cx": 60, "cy": 72, "rx": 16, "ry": 10})
        self.assertEqual(report["bindings"]["valve-gate"]["dependencies"], ["rate"])
        self.assertEqual(report["assets"][0]["hooks"], ["gate", "readout"])

    def test_original_asset_is_copied_with_matching_hash(self):
        self.run_import(); self.assertTrue(engine.build(self.root / "assembled.json", self.root / "project")["ok"])
        asset = json.loads((self.root / "project/manifest.json").read_text())["assets"][0]
        self.assertEqual((self.root / "project" / asset["projectSource"]).read_bytes(), self.svg.read_bytes())
        self.assertEqual(asset["sha256"], engine.hashlib.sha256(self.svg.read_bytes()).hexdigest())

    def test_asset_change_requires_reassembly(self):
        self.run_import(); self.svg.write_text(SVG.replace('rx="16"', 'rx="17"'))
        report = engine.build(self.root / "assembled.json", self.root / "project")
        self.assertFalse(report["ok"]); self.assertEqual(report["findings"][0]["code"], "asset-source-changed")
        self.assertFalse((self.root / "project").exists())

    def test_unknown_hook_rejected_without_replacing_output(self):
        target = self.root / "assembled.json"; target.write_text("previous artifact")
        self.plan["assets"][0]["bindings"]["imaginary"] = {"value": "rate"}
        with self.assertRaisesRegex(ValueError, "actual shape IDs"): self.run_import()
        self.assertEqual(target.read_text(), "previous artifact")

    def test_palette_two_colors_cannot_enter_palette_one(self):
        self.svg.write_text(SVG.replace('#333e48', '#007298'))
        with self.assertRaisesRegex(ValueError, "outside the active palette"): self.run_import()

    def test_missing_source_explains_plan_relative_paths(self):
        self.plan["assets"][0]["path"] = "duplicate/valve.svg"
        with self.assertRaisesRegex(ValueError, "relative to the asset-plan JSON"): self.run_import()

    def test_nested_plan_does_not_duplicate_workspace_prefix(self):
        self.root = self.root / "deliverables"; self.root.mkdir()
        self.svg = self.root / "valve.svg"; self.svg.write_text(SVG, encoding="utf-8")
        self.assertTrue(self.run_import()["ok"])

    def test_scaffold_uses_view_size_and_plan_relative_path(self):
        engine.write_json(self.root / "brief.json", self.brief)
        target=self.root / "deliverables/assets/mechanism.svg"; plan=self.root / "deliverables/asset-plan.json"
        report=importer.scaffold(self.root / "brief.json", plan, target)
        self.assertTrue(report["ok"])
        self.assertIn('viewBox="0 0 1020 920"',target.read_text())
        self.assertEqual(json.loads(plan.read_text())["assets"][0]["path"],"assets/mechanism.svg")
        with self.assertRaisesRegex(ValueError,"already exists"): importer.scaffold(self.root / "brief.json",plan,target)

    def test_scaffold_preserves_an_existing_matching_asset_plan(self):
        engine.write_json(self.root / "brief.json", self.brief)
        plan=self.root / "deliverables/asset-plan.json"; target=self.root / "deliverables/assets/mechanism.svg"
        self.plan["assets"][0].update(path="assets/mechanism.svg", placement=[0,0])
        engine.write_json(plan,self.plan); original=plan.read_bytes()
        report=importer.scaffold(self.root / "brief.json",plan,target,"tank")
        self.assertTrue(report["ok"]); self.assertTrue(report["planPreserved"])
        self.assertEqual(plan.read_bytes(),original); self.assertTrue(target.is_file())

    def test_scaffold_refuses_a_mismatched_existing_plan_without_side_effects(self):
        engine.write_json(self.root / "brief.json",self.brief)
        plan=self.root / "plan.json"; target=self.root / "missing.svg"
        engine.write_json(plan,self.plan); original=plan.read_bytes()
        with self.assertRaisesRegex(ValueError,"exact SVG path"):
            importer.scaffold(self.root / "brief.json",plan,target,"tank")
        self.assertFalse(target.exists()); self.assertEqual(plan.read_bytes(),original)

    def test_scaffold_rejects_a_plan_with_the_wrong_view(self):
        engine.write_json(self.root / "brief.json",self.brief)
        plan=self.root / "plan.json"; target=self.root / "missing.svg"
        self.plan["assets"][0].update(path="missing.svg",view="history")
        engine.write_json(plan,self.plan)
        with self.assertRaisesRegex(ValueError,"selected view"):
            importer.scaffold(self.root / "brief.json",plan,target,"tank")
        self.assertFalse(target.exists())

    def test_empty_scaffold_is_not_accepted_as_artwork(self):
        engine.write_json(self.root / "brief.json",self.brief)
        plan=self.root / "plan.json";target=self.root / "blank.svg"
        importer.scaffold(self.root / "brief.json",plan,target)
        with self.assertRaisesRegex(ValueError,"visible editable geometry"): importer.assemble(self.root / "brief.json",plan,self.root / "assembled.json")

    def test_external_and_active_svg_are_rejected(self):
        for element in ['<script/>', '<image href="https://example.com/a.png"/>', '<animate/>', '<use href="#body"/>']:
            with self.subTest(element=element):
                self.svg.write_text(SVG.replace('</svg>', element + '</svg>'))
                with self.assertRaisesRegex(ValueError, "Unsupported SVG"): self.run_import()

    def test_unsupported_transform_cannot_be_silently_dropped(self):
        self.svg.write_text(SVG.replace('translate(10 12)', 'rotate(20)'))
        with self.assertRaisesRegex(ValueError, "Bake scale"): self.run_import()

    def test_geometry_ids_cannot_collide(self):
        self.brief["marks"][0]["id"] = "valve-body"
        with self.assertRaisesRegex(ValueError, "collides"): self.run_import()

    def test_asset_bounds_and_ports_are_checked(self):
        self.plan["assets"][0]["ports"]["inlet"] = [101, 10]
        with self.assertRaisesRegex(ValueError, "inside the native SVG"): self.run_import()
        self.plan["assets"][0]["ports"] = {}; self.plan["assets"][0]["placement"] = [10000, 0]
        with self.assertRaisesRegex(ValueError, "must fit"): self.run_import()

    def test_group_and_leaf_opacity_multiply(self):
        self.svg.write_text(SVG.replace('<g transform', '<g opacity="0.5" transform').replace('id="body"', 'id="body" opacity="0.6"'))
        self.run_import(); brief = json.loads((self.root / "assembled.json").read_text())
        self.assertAlmostEqual(brief["marks"][0]["opacity"], .3)

    def test_group_motion_preserves_initial_pose_and_moves_all_parts(self):
        self.svg.write_text(SVG.replace('<g transform','<g id="car" transform'))
        self.plan["assets"][0]["bindings"] = {"car": {"offset": [{"mul": ["rate", 10]}, 3]}}
        report=self.run_import(); self.assertTrue(report["ok"], report["findings"])
        b=json.loads((self.root / "assembled.json").read_text())
        state, expr=engine.evaluate(b,0)
        marks={m["id"]:m for m in b["marks"]}
        self.assertEqual(expr(marks["valve-body"]["attrs"]["cx"]),80)
        self.assertEqual(expr(marks["valve-body"]["attrs"]["cy"]),75)
        self.assertEqual(expr(marks["valve-gate"]["attrs"]["translateX"]),50)
        self.assertEqual(expr(marks["valve-readout"]["attrs"]["x"]),54)
        self.assertEqual(len(report["assets"][0]["selectors"]["car"]),3)

    def test_group_geometry_is_not_ambiguously_applied_to_children(self):
        self.svg.write_text(SVG.replace('<g transform','<g id="car" transform'))
        self.plan["assets"][0]["bindings"] = {"car": {"attrs": {"rotation": "rate"}}}
        with self.assertRaisesRegex(ValueError,"relative offset only"): self.run_import()

    def test_group_hook_must_not_collide_with_a_shape_id(self):
        self.svg.write_text(SVG.replace('<g transform','<g id="body" transform'))
        with self.assertRaisesRegex(ValueError,"unique lowercase"): self.run_import()

    def test_modulo_transport_is_continuous_when_rate_changes(self):
        self.brief["derived"]["phase"] = {"expr": {"mod": [{"mul": ["volume", .01]}, 1]}, "unit": ""}
        a = engine.evaluate(self.brief, 4 - 1e-5)[0]["phase"]; b = engine.evaluate(self.brief, 4 + 1e-5)[0]["phase"]
        self.assertAlmostEqual(a, b, places=5)
        self.assertEqual(engine.evaluate(self.brief, 16, {"rate": 0})[0]["phase"], 0)

    def test_nonpositive_modulus_is_a_model_finding(self):
        self.brief["derived"]["phase"] = {"expr": {"mod": [1, 0]}, "unit": ""}
        self.assertFalse(engine.preflight(self.brief)["ok"])

    def test_python_and_javascript_agree_for_modulo_and_ellipse(self):
        self.brief["derived"]["phase"] = {"expr": {"mod": [{"sub": ["volume", 50]}, 7]}, "unit": ""}; self.run_import()
        code = "const fs=require('node:fs');require(process.argv[1]);const b=JSON.parse(fs.readFileSync(process.argv[2]));const p=JSON.parse(fs.readFileSync(process.argv[3])).colorsets.colorset1;const k=ExplainerKernel.create(b,p);console.log(JSON.stringify([0,4,5,16].map(t=>k.snapshot(t))));"
        result = subprocess.run(["node", "-e", code, str(engine.BUNDLE / "assets/templates/kernel.js"), str(self.root / "assembled.json"), str(engine.BUNDLE / "assets/palettes/colorsets.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for frame in json.loads(result.stdout):
            self.assertAlmostEqual(frame["state"]["phase"], engine.evaluate(self.brief, frame["time"])[0]["phase"])
            self.assertEqual(next(m for m in frame["marks"] if m["id"] == "valve-body")["attrs"]["rx"], 16)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--work-dir", required=True); args = parser.parse_args()
    WORK = Path(args.work_dir).resolve()
    if WORK.is_relative_to(engine.BUNDLE): parser.error("Tests must write outside the skill bundle.")
    WORK.mkdir(parents=True, exist_ok=True); unittest.main(argv=[sys.argv[0]])
