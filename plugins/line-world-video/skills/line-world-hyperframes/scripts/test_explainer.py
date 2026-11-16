#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Run: uv run --script scripts/test_explainer.py --work-dir <project-artifacts>."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("explainer", Path(__file__).with_name("explainer.py"))
engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
STARTER = json.loads((engine.BUNDLE / "assets/templates/brief.json").read_text(encoding="utf-8"))


class ContractTests(unittest.TestCase):
    def setUp(self): self.brief = copy.deepcopy(STARTER)

    def assert_finding(self, code):
        report = engine.preflight(self.brief)
        self.assertFalse(report["ok"])
        self.assertIn(code, [e["code"] for e in report["findings"]])

    def test_starter_and_multi_view_closure(self):
        report = engine.preflight(self.brief)
        self.assertTrue(report["ok"], report["findings"])
        self.assertEqual(report["eventViews"]["open-valve"], ["history", "tank"])

    def test_initializer_creates_an_exact_sized_rate_integral_model(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            target=Path(folder)/"nested/scene.json"
            report=engine.initialize_brief(target,width=960,height=540,fps=12,duration=8,initial=2,maximum=5,target=5,at=2,ramp=2)
            self.assertTrue(report["ok"],report["findings"])
            brief=json.loads(target.read_text());self.assertEqual(brief["output"],{"width":960,"height":540,"fps":12,"duration":8})
            self.assertEqual(engine.evaluate(brief,8)[0]["volume"],31)
            self.assertEqual(engine.evaluate(brief,8,{"rate":5})[0]["volume"],40)
            self.assertEqual(report["eventViews"]["change-input"],["history","mechanism"])
            self.assertFalse(any(m["kind"] in ["rect","ellipse","circle"] for m in brief["marks"]))

    def test_initializer_generalizes_quantity_names_units_and_explicit_palette(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            target=Path(folder)/"vehicle.json"
            report=engine.initialize_brief(target,width=960,height=540,duration=8,maximum=6,target=4,at=2,ramp=2,
                                          source="speed",source_unit="m/s",quantity="distance",quantity_unit="m",palette="colorset2")
            self.assertTrue(report["ok"],report["findings"])
            brief=json.loads(target.read_text());self.assertEqual(engine.evaluate(brief,8)[0]["distance"],26)
            self.assertEqual(engine.evaluate(brief,8,{"speed":6})[0]["distance"],48)
            self.assertEqual(brief["entities"]["distance"],"secondary")

    def test_initializer_rejects_invalid_domains_and_events_without_files(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            for config in [{"maximum":-1},{"target":6},{"initial":-1},{"at":15,"ramp":2},{"duration":0},{"width":500},{"quantity":"rate"}]:
                target=Path(folder)/"missing.json"
                self.assertFalse(engine.initialize_brief(target,**config)["ok"]);self.assertFalse(target.exists())

    def test_initializer_preserves_existing_brief_and_the_skill_payload(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            target=Path(folder)/"scene.json";target.write_text("authored scene")
            self.assertFalse(engine.initialize_brief(target)["ok"]);self.assertEqual(target.read_text(),"authored scene")
            target=engine.BUNDLE/"never-created.json"
            self.assertFalse(engine.initialize_brief(target)["ok"]);self.assertFalse(target.exists())

    def test_initializer_cli_writes_the_requested_paths(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            target=Path(folder)/"deliverables/scene.json";report=Path(folder)/"deliverables/init.json"
            result=subprocess.run([sys.executable,str(engine.BUNDLE/"scripts/explainer.py"),"init","--brief",str(target),"--report",str(report),"--width","960","--height","540","--fps","12","--duration","8","--at","2","--ramp","2","--target","5"],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(report.read_text())["ok"])
            self.assertEqual(engine.evaluate(json.loads(target.read_text()),8)[0]["volume"],31)

    def test_analytic_ramp_integral(self):
        for time, expected in [(0, 0), (4, 8), (5, 10.5), (6, 14), (10, 30), (11, 33.25), (12, 35), (16, 39)]:
            self.assertAlmostEqual(engine.evaluate(self.brief, time)[0]["volume"], expected)

    def test_integral_is_not_current_rate_times_time(self):
        state = engine.evaluate(self.brief, 10)[0]
        self.assertEqual(state["rate"], 4)
        self.assertEqual(state["volume"], 30)
        self.assertNotEqual(state["volume"], state["rate"] * 10)

    def test_discrete_step_has_no_instantaneous_volume_jump(self):
        self.brief["events"] = [self.brief["events"][0]]
        self.brief["events"][0]["duration"] = 0
        self.assertEqual(engine.evaluate(self.brief, 4)[0]["rate"], 4)
        self.assertEqual(engine.evaluate(self.brief, 4)[0]["volume"], 8)
        self.assertEqual(engine.evaluate(self.brief, 16)[0]["volume"], 56)

    def test_input_override_recomputes_history(self):
        state = engine.evaluate(self.brief, 16, {"rate": 5})[0]
        self.assertEqual(state["rate"], 5); self.assertEqual(state["volume"], 80)

    def test_backward_and_repeated_seeks_are_pure(self):
        states = {t: engine.evaluate(self.brief, t)[0] for t in [0, 5, 16]}
        for t in [16, 0, 5, 5, 16, 0]: self.assertEqual(states[t], engine.evaluate(self.brief, t)[0])

    def test_overlap_rejected(self):
        self.brief["events"][1]["at"] = 5; self.assert_finding("event-overlap")

    def test_duplicate_instant_rejected(self):
        self.brief["events"][0]["duration"] = 0
        self.brief["events"][1]["at"] = 4; self.assert_finding("event-overlap")

    def test_out_of_domain_event(self):
        self.brief["events"][0]["changes"]["rate"] = 6; self.assert_finding("domain")

    def test_source_cannot_be_time(self):
        self.brief["sources"]["time"] = {"value": 0, "domain": [0, 1], "unit": "s"}; self.assert_finding("quantity")

    def test_derived_cycle(self):
        self.brief["derived"]["volume"]["expr"] = "volume"; self.assert_finding("cycle")

    def test_unknown_quantity(self):
        self.brief["derived"]["volume"]["expr"] = "imaginary"; self.assert_finding("expression")

    def test_operation_arity(self):
        self.brief["derived"]["volume"]["expr"] = {"div": [1]}; self.assert_finding("expression")

    def test_division_by_zero_in_legal_control_domain(self):
        self.brief["derived"]["volume"]["expr"] = {"div": [1, "rate"]}; self.assert_finding("model")

    def test_undefined_display_value(self):
        self.brief["marks"][6]["value"] = {"div": [1, 0]}; self.assert_finding("model")

    def test_derived_rate_cannot_use_source_integrator(self):
        self.brief["derived"]["volume"]["expr"] = {"integrate": ["volume", "time"]}; self.assert_finding("integrate")

    def test_integrator_rejects_non_name(self):
        self.brief["derived"]["volume"]["expr"] = {"integrate": [{"add": [1, 2]}, "time"]}; self.assert_finding("integrate")

    def test_conservation_failure(self):
        self.brief["invariants"] = [{"id": "invented-constant", "lhs": "volume", "rhs": 30}]; self.assert_finding("invariant")

    def test_palette_one_rejects_blue(self):
        self.brief["marks"][1]["stroke"] = "secondary"; self.assert_finding("paint")

    def test_palette_two_needs_decision(self):
        self.brief["palette"]["mode"] = "colorset2"; self.assert_finding("palette")

    def test_palette_two_without_extra_hue_falls_back(self):
        self.brief["palette"] = {"mode": "colorset2", "decision": "explicit", "reason": "Requested palette."}; self.assert_finding("palette")

    def test_palette_two_with_semantic_paint(self):
        self.brief["palette"] = {"mode": "colorset2", "decision": "explicit", "reason": "Requested blue inlet identity."}
        self.brief["marks"][1]["stroke"] = "secondary"
        self.assertTrue(engine.preflight(self.brief)["ok"])

    def test_overridden_unused_blue_cannot_justify_palette_two(self):
        self.brief["palette"] = {"mode": "colorset2", "decision": "explicit", "reason": "Requested blue water."}
        self.brief["marks"][2]["stroke"] = "secondary"
        self.assert_finding("palette")

    def test_language_tag_is_not_injected_markup(self):
        self.brief["language"] = 'en" onclick="x'; self.assert_finding("language")

    def test_common_canvas_groups_preserve_distinct_semantic_views(self):
        for view in self.brief["views"]: view["region"] = [0, 0, 1920, 1080]
        self.assertTrue(engine.preflight(self.brief)["ok"])
        self.assertEqual(len(engine.preflight(self.brief)["eventViews"]["open-valve"]), 2)

    def test_partial_panel_overlap_still_rejected(self):
        self.brief["views"][1]["region"] = [500, 200, 650, 730]
        self.assert_finding("layout")

    def test_text_anchor_alias_is_canonicalized_without_mutating_input(self):
        mark = next(m for m in self.brief["marks"] if m["kind"] == "text")
        mark.pop("anchor", None); mark["attrs"]["anchor"] = "end"
        normalized = engine.normalize_brief(self.brief)
        target = next(m for m in normalized["marks"] if m["id"] == mark["id"])
        self.assertEqual(target["anchor"], "end"); self.assertNotIn("anchor", target["attrs"])
        self.assertEqual(mark["attrs"]["anchor"], "end")
        self.assertTrue(engine.preflight(self.brief)["ok"])

    def test_unbound_control(self):
        self.brief["sources"]["unused"] = {"value": 1, "domain": [0, 2], "unit": "m"}; self.assert_finding("unbound-source")

    def test_one_view_is_not_synchronized_explanation(self):
        self.brief["marks"] = [m for m in self.brief["marks"] if m["view"] == "tank"]; self.assert_finding("synchronization")

    def test_clipped_regions(self):
        self.brief["views"][1]["region"][0] = 1900; self.assert_finding("layout")

    def test_plot_never_clamps_out_of_domain_quantity(self):
        next(m for m in self.brief["marks"] if m["kind"] == "plot")["yDomain"] = [0, 20]; self.assert_finding("plot-domain")

    def test_prose_does_not_enter_film(self):
        self.brief["marks"][6]["text"] = "This introductory headline has many words and explains all the information in prose."; self.assert_finding("text")

    def test_mojibake_is_an_actionable_text_finding(self):
        mark=next(m for m in self.brief["marks"] if m["kind"]=="text")
        mark["text"]="Stored \u00c2\u00b7 L"; self.assert_finding("text-encoding")
        mark["text"]="Stored - L"; self.assertTrue(engine.preflight(self.brief)["ok"])

    def test_path_markup_rejected(self):
        self.brief["marks"][0]["d"] = '<script>alert(1)</script>'; self.assert_finding("path")

    def test_invalid_json_is_an_authoring_finding(self):
        with tempfile.TemporaryDirectory(dir=WORK) as temp:
            root = Path(temp); source = root / "invalid.json"; report = root / "finding.json"
            source.write_text('{"sources": {broken}', encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("explainer.py")), "preflight", "--brief", str(source), "--report", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            finding = json.loads(report.read_text(encoding="utf-8"))
            self.assertFalse(finding["ok"]); self.assertEqual(finding["findings"][0]["code"], "json")

    def test_patch_selects_only_the_named_mark(self):
        with tempfile.TemporaryDirectory(dir=WORK) as temp:
            root = Path(temp); source = root / "brief.json"; changes = root / "patch.json"
            engine.write_json(source, self.brief)
            engine.write_json(changes, {"marks": {"rate-label": {"attrs": {"y": 190}}}})
            report = engine.patch_brief(source, changes); self.assertTrue(report["applied"])
            updated = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual(next(m for m in updated["marks"] if m["id"] == "rate-label")["attrs"]["y"], 190)
            self.assertEqual(updated["marks"][7], self.brief["marks"][7])

    def test_patch_replaces_expression_operator_atomically(self):
        with tempfile.TemporaryDirectory(dir=WORK) as temp:
            root = Path(temp); source = root / "brief.json"; changes = root / "patch.json"
            engine.write_json(source, self.brief)
            engine.write_json(changes, {"derived": {"volume": {"expr": {"add": [0, {"integrate": ["rate", "time"]}]}}}})
            self.assertTrue(engine.patch_brief(source, changes)["applied"])
            updated = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual(list(updated["derived"]["volume"]["expr"]), ["add"])
            self.assertEqual(engine.evaluate(updated, 16)[0]["volume"], 39)

    def test_bad_patch_preserves_source_bytes(self):
        with tempfile.TemporaryDirectory(dir=WORK) as temp:
            root = Path(temp); source = root / "brief.json"; changes = root / "patch.json"
            engine.write_json(source, self.brief); original = source.read_bytes()
            for patch in [{"marks": {"unknown-mark": {"attrs": {"y": 190}}}}, {"marks": {"stored": {"attrs": {"width": -1}}}}]:
                engine.write_json(changes, patch)
                self.assertFalse(engine.patch_brief(source, changes)["applied"])
                self.assertEqual(source.read_bytes(), original)

    def test_patch_cannot_write_skill(self):
        source = engine.BUNDLE / "assets/templates/brief.json"; original = source.read_bytes()
        self.assertFalse(engine.patch_brief(source, source)["applied"])
        self.assertEqual(source.read_bytes(), original)

    def test_exact_outputs_and_existing_project_protection(self):
        with tempfile.TemporaryDirectory(dir=WORK) as temp:
            root = Path(temp); source = root / "input.json"; engine.write_json(source, self.brief)
            project = root / "nested" / "requested-project"
            report = engine.build(source, project)
            self.assertTrue(report["ok"])
            self.assertEqual(project, Path(report["project"]))
            for file in report["outputs"]: self.assertTrue((project / file).is_file())
            written = json.loads((project / "brief.json").read_text(encoding="utf-8"))
            self.assertEqual(written["sources"]["rate"]["unit"], "L/s")
            self.assertIn('data-fps="30"', (project / "index.html").read_text(encoding="utf-8"))
            refused = engine.build(source, project)
            self.assertFalse(refused["ok"])
            self.assertEqual(refused["findings"][0]["code"], "project-exists")
            self.brief["sources"]["rate"]["value"] = 3
            engine.write_json(source, self.brief)
            self.assertTrue(engine.build(source, project, refresh=True)["ok"])
            self.assertEqual(json.loads((project / "brief.json").read_text(encoding="utf-8"))["sources"]["rate"]["value"], 3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--work-dir", required=True)
    args = parser.parse_args(); WORK = Path(args.work_dir).resolve(); WORK.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
