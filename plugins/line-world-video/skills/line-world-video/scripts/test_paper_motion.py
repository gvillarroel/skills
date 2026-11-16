#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check continuous paper camera geometry and unobscuring margin emphasis."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path


class MotionTests(unittest.TestCase):
    def run_js(self, code):
        if not shutil.which('node'): self.skipTest('Node is required for the pure geometry contract.')
        resource = Path(__file__).resolve().parent.parent / 'assets/paper-video/paper-motion.js'
        setup = "const p=require(process.argv[1]);const input={scene:{layout:'paper',duration:18},source:{x:80,y:300,w:1760,h:400},targets:{left:{x:140,y:400,w:180,h:180},right:{x:1500,y:400,w:180,h:180}},cues:[{target:'left',at:4,port:{x:230,y:370}},{target:'right',at:11,port:{x:1590,y:370}}]};"
        result = subprocess.run(['node', '-e', setup + code, str(resource)], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_single_entry_then_constant_scale_and_lateral_pan(self):
        result = self.run_js("let c=p.cameraPlan(input);console.log(JSON.stringify({mode:c.mode,start:c.at(0),a:c.at(4),b:c.at(11),end:c.at(18),moves:c.moves}));")
        self.assertEqual(result['mode'], 'pan'); self.assertEqual(result['start']['k'], 1)
        self.assertGreater(result['a']['k'], 1); self.assertEqual(result['a']['k'], result['b']['k'])
        self.assertEqual(result['b'], result['end']); self.assertNotEqual(result['a']['x'], result['b']['x'])
        self.assertEqual(result['a']['y'], result['b']['y'])

    def test_no_zoom_out_or_teleport_at_any_frame(self):
        result = self.run_js("const c=p.cameraPlan(input);let zoomOut=0,speed=0,last=c.at(0);for(let n=1;n<540;n++){let a=c.at(n/30);if(a.k<last.k-1e-9)zoomOut++;speed=Math.max(speed,Math.hypot(a.x-last.x,a.y-last.y)*30);last=a;}console.log(JSON.stringify({zoomOut,speed}));")
        self.assertEqual(result['zoomOut'], 0); self.assertLessEqual(result['speed'], 541)

    def test_legacy_static_flag_and_short_readings_keep_context(self):
        result = self.run_js("input.scene.cameraZoom=false;let a=p.cameraPlan(input);delete input.scene.cameraZoom;input.scene.duration=4;let b=p.cameraPlan(input);console.log(JSON.stringify([a.at(3),b.at(3)]));")
        self.assertEqual(result, [{'k': 1, 'x': 0, 'y': 0}] * 2)

    def test_dense_far_apart_cues_fall_back_instead_of_accelerating(self):
        result = self.run_js("input.cues[1].at=4.4;const c=p.cameraPlan(input);console.log(JSON.stringify({mode:c.mode,a:c.at(5),b:c.at(15)}));")
        self.assertEqual(result['mode'], 'static-dense-cues'); self.assertEqual(result['a'], result['b'])

    def test_repeated_target_does_not_restart_zoom(self):
        result = self.run_js("input.cues[1]={...input.cues[0],at:11};const c=p.cameraPlan(input);console.log(JSON.stringify({a:c.at(5),b:c.at(12),moves:c.moves.length}));")
        self.assertEqual(result['a'], result['b']); self.assertEqual(result['moves'], 1)

    def test_seeking_is_independent_of_history(self):
        result = self.run_js("const c=p.cameraPlan(input),a=c.at(9);c.at(18);c.at(0);console.log(JSON.stringify([a,c.at(9)]));")
        self.assertEqual(*result)

    def test_word_boxes_expand_a_partial_text_selection(self):
        result = self.run_js("console.log(JSON.stringify(p.expandWords({x:20,y:20,w:40,h:10},[{x:10,y:18,w:35,h:15},{x:46,y:18,w:50,h:15}])));")
        self.assertEqual(result, {'x': 10, 'y': 18, 'w': 86, 'h': 15})

    def test_emphasis_uses_only_margin_segments(self):
        result = self.run_js("let f={x:400,y:300,w:500,h:180};console.log(JSON.stringify(p.marginMarks(f,[f])));")
        self.assertTrue(result)
        for mark in result: self.assertTrue(mark['w'] == 0 or mark['h'] == 0)

    def test_raster_rejection_omits_ink_instead_of_covering_connectors(self):
        result = self.run_js("console.log(JSON.stringify(p.marginMarks({x:400,y:300,w:500,h:180},[], 'margin',()=>false)));")
        self.assertEqual(result, [])

    def test_explicit_no_emphasis_preserves_guide_only(self):
        result = self.run_js("console.log(JSON.stringify(p.marginMarks({x:400,y:300,w:500,h:180},[], 'none')));")
        self.assertEqual(result, [])


if __name__ == '__main__': unittest.main()
