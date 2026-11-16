#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Run: uv run --script scripts/test_composition.py --work-dir <project-artifacts>."""
import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
import compose_mechanism as composer
import explainer as engine
import import_assets as importer


class CompositionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=WORK); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def generate(self, kind="inlet", palette="colorset1", width=960, height=540, **kwargs):
        source, quantity, source_unit, quantity_unit = ("rate","volume","L/s","L") if kind == "inlet" else ("speed","distance","m/s","m")
        options = dict(width=width,height=height,fps=12,duration=8,initial=2,maximum=5 if kind == "inlet" else 6,
                       target=5 if kind == "inlet" else 4,at=2,ramp=2,source=source,quantity=quantity,
                       source_unit=source_unit,quantity_unit=quantity_unit,palette=palette)
        options.update(kwargs)
        self.model = self.root/"model.json"; self.scene = self.root/"scene.json"
        self.svg = self.root/"assets/mechanism.svg"; self.plan = self.root/"asset-plan.json"
        self.assertTrue(engine.initialize_brief(self.model,**options)["ok"])
        result = composer.compose(self.model,self.scene,self.svg,self.plan,kind=kind)
        self.assertTrue(result["ok"],result["findings"])
        result = importer.assemble(self.scene,self.plan,self.root/"assembled.json")
        self.assertTrue(result["ok"],result["findings"])
        self.brief = json.loads((self.root/"assembled.json").read_text(encoding="utf-8"))
        return result

    def mark(self, identity, time, overrides=None):
        state, evaluate = engine.evaluate(self.brief,time,overrides)
        mark = copy.deepcopy(next(m for m in self.brief["marks"] if m["id"] == identity))
        mark["attrs"] = {key:evaluate(value) for key,value in mark["attrs"].items()}
        if "value" in mark: mark["value"] = evaluate(mark["value"])
        return mark

    def test_inlet_preserves_model_and_aligns_fill_with_capacity_ruler(self):
        self.generate()
        model = json.loads(self.model.read_text()); scene = json.loads(self.scene.read_text())
        for field in ["output","palette","sources","derived","events","invariants"]:
            self.assertEqual(scene.get(field),model.get(field))
        calibration = scene["composition"]["calibration"]
        fill = self.mark("mechanism-fluid",8)["attrs"]
        self.assertAlmostEqual(fill["height"],31*calibration["pixelsPerUnit"])
        self.assertAlmostEqual(fill["y"]+fill["height"],calibration["zeroY"])
        full = self.mark("mechanism-fluid",8,{"rate":5})["attrs"]
        self.assertAlmostEqual(full["y"],calibration["capacityY"])
        self.assertEqual(len(scene["views"]),3)

    def test_tracers_remain_continuous_through_rate_change_and_stop_at_zero(self):
        self.generate()
        before = self.mark("mechanism-tracer-0",2-1e-6)["attrs"]
        after = self.mark("mechanism-tracer-0",2+1e-6)["attrs"]
        self.assertLess(abs(before["cx"]-after["cx"]),.001)
        self.assertEqual(self.mark("mechanism-tracer-0",8,{"rate":0})["attrs"]["r"],0)
        self.assertEqual(self.mark("mechanism-fluid",8,{"rate":0})["attrs"]["height"],0)

    def test_low_frame_rate_transport_does_not_alias_backwards(self):
        self.generate()
        before = self.mark("mechanism-tracer-0",6,{"rate":5})["attrs"]["cx"]
        after = self.mark("mechanism-tracer-0",6+1/12,{"rate":5})["attrs"]["cx"]
        self.assertGreater(after-before,0)
        self.assertLessEqual(after-before,530*.5/(4*9)+1e-9)

    def test_full_hd_transport_preserves_the_sol_reference_pacing(self):
        self.generate(width=1920,height=1080,fps=30,duration=16)
        calibration = self.brief["composition"]["calibration"]
        self.assertAlmostEqual(calibration["tracerCyclesPerUnit"],6/80)
        self.assertLess(calibration["maximumPhaseAdvancePerFrame"],1/(4*9))

    def test_vehicle_distance_anchor_wheel_contact_and_clockwise_rotation_agree(self):
        self.generate(kind="vehicle",palette="colorset2")
        calibration = self.brief["composition"]["calibration"]
        rear = self.mark("mechanism-rear-tyre",8)["attrs"]
        pointer = self.mark("mechanism-position-pointer",8)["attrs"]
        self.assertAlmostEqual(pointer["translateX"],rear["cx"])
        self.assertAlmostEqual(rear["cy"]+rear["r"],calibration["roadY"])
        spokes = self.mark("mechanism-rear-spokes",8)["attrs"]
        self.assertAlmostEqual(spokes["rotation"],26*calibration["pixelsPerUnit"]/calibration["wheelRadius"]*180/composer.math.pi)
        self.assertGreater(spokes["rotation"],0)
        for t in [0,8]:
            for value in [0,6]:
                car = self.mark("mechanism-car-body",t,{"speed":value})["attrs"]
                self.assertGreaterEqual(car["translateX"],0)
                self.assertLessEqual(car["translateX"]+385*.5,1030*.5-35*.5)

    def test_nonbinary_scale_native_viewbox_round_trips_without_fit_error(self):
        self.generate(width=1280,height=720)
        result = importer.assemble(self.scene,self.plan,self.root/"roundtrip.json")
        self.assertTrue(result["ok"],result["findings"])

    def test_custom_quantity_ids_and_source_events_are_not_replaced(self):
        self.generate(source="inflow",quantity="stored-water")
        self.assertEqual(engine.evaluate(self.brief,8)[0]["stored-water"],31)
        self.assertEqual(self.mark("mechanism-input-value",8)["value"],5)

    def test_explicit_extended_palette_reaches_real_semantic_geometry(self):
        self.generate(palette="colorset2")
        self.assertEqual(next(m for m in self.brief["marks"] if m["id"] == "mechanism-fluid")["fill"],"secondary")
        self.assertEqual(next(m for m in self.brief["marks"] if m["id"] == "mechanism-valve-gate")["stroke"],"primary")

    def test_palette_assertion_accepts_matching_input_and_preserves_conflicting_input(self):
        self.generate(kind="vehicle",palette="colorset2")
        before = self.model.read_bytes()
        result = composer.compose(self.model,self.root/"asserted.json",self.root/"asserted.svg",self.root/"asserted-plan.json",kind="vehicle",expected_palette="colorset2")
        self.assertTrue(result["ok"])
        with self.assertRaisesRegex(ValueError,"palette assertion"):
            composer.compose(self.model,self.root/"conflict.json",self.root/"conflict.svg",self.root/"conflict-plan.json",kind="vehicle",expected_palette="colorset1")
        self.assertEqual(before,self.model.read_bytes())
        self.assertFalse((self.root/"conflict.svg").exists())

    def test_existing_outputs_are_preserved_and_capacity_overflow_is_rejected(self):
        self.generate()
        files = [self.scene,self.svg,self.plan]; before = [p.read_bytes() for p in files]
        with self.assertRaisesRegex(ValueError,"already exist"):
            composer.compose(self.model,self.scene,self.svg,self.plan,kind="inlet")
        self.assertEqual(before,[p.read_bytes() for p in files])
        with self.assertRaisesRegex(ValueError,"Capacity"):
            composer.compose(self.model,self.root/"bad.json",self.root/"bad.svg",self.root/"bad-plan.json",kind="inlet",capacity=20)
        self.assertFalse((self.root/"bad.svg").exists())

    def test_incompatible_model_is_rejected_before_output_writes(self):
        self.generate()
        model = json.loads(self.model.read_text()); model["derived"]["volume"]["expr"] = {"mul":["rate","time"]}
        engine.write_json(self.model,model)
        with self.assertRaisesRegex(ValueError,"accumulated quantity"):
            composer.compose(self.model,self.root/"invalid.json",self.root/"invalid.svg",self.root/"invalid-plan.json",kind="inlet")
        self.assertFalse((self.root/"invalid.json").exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--work-dir",required=True)
    args,remaining = parser.parse_known_args(); WORK = Path(args.work_dir).resolve(); WORK.mkdir(parents=True,exist_ok=True)
    unittest.main(argv=[sys.argv[0],*remaining])
