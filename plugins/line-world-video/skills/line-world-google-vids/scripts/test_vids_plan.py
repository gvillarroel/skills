#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test evidence gates and frame-contiguous native timing compilation."""
import copy
import tempfile
import unittest
from pathlib import Path
from vids_plan import prepare,compile_timing

def fixture():
    story={'projectTitle':'Test film','fps':30,'scenes':[{'id':'first','script':'A short explanation.','visual':'chart','clipSeconds':10,'essentialAnimationSeconds':3},{'id':'second','script':'A second explanation.','visual':'pipeline','clipSeconds':10,'essentialAnimationSeconds':3}]}
    observed={'voice':'Nyla','scenes':[{'id':'first','observed':True,'sceneSeconds':6.2,'voiceoverSeconds':5.5,'audioLeadSeconds':.2,'tailSeconds':.5},{'id':'second','observed':True,'sceneSeconds':7.1,'voiceoverSeconds':6.9,'tailSeconds':.2}]}
    return story,observed

class TimingTests(unittest.TestCase):
    def test_rendered_source_clip_needs_no_redundant_visual_brief(self):
        s,o=fixture()
        for scene in s['scenes']:
            scene.pop('visual');scene['sourceClip']='input.mp4'
        result=compile_timing(s,o);self.assertEqual(result['scenes'][0]['clip'],'input.mp4')
    def test_frame_continuity_and_source_order(self):
        s,o=fixture();o['scenes'].reverse();r=compile_timing(s,o)
        self.assertEqual(r['frames'],399);self.assertEqual(r['scenes'][0]['endFrame'],r['scenes'][1]['startFrame']);self.assertEqual(r['scenes'][0]['id'],'first')
    def test_unmeasured_rejected(self):
        s,o=fixture();o['scenes'][0]['observed']=False
        with self.assertRaises(ValueError):compile_timing(s,o)
    def test_speech_clipping_rejected(self):
        s,o=fixture();o['scenes'][0]['voiceoverSeconds']=7
        with self.assertRaises(ValueError):compile_timing(s,o)
    def test_essential_visual_clipping_rejected(self):
        s,o=fixture();s['scenes'][0]['essentialAnimationSeconds']=8
        with self.assertRaises(ValueError):compile_timing(s,o)
    def test_unverified_coverage_rejected(self):
        s,o=fixture();o['scenes'][0]['sceneSeconds']=12
        with self.assertRaises(ValueError):compile_timing(s,o)
        o['scenes'][0]['extendedVisualVerified']=True
        self.assertEqual(compile_timing(s,o)['scenes'][0]['duration'],12)
    def test_duplicate_observation_rejected(self):
        s,o=fixture();o['scenes'][1]['id']='first'
        with self.assertRaises(ValueError):compile_timing(s,o)
    def test_nonfinite_and_boolean_rejected(self):
        for value in [float('nan'),float('inf'),True,-1]:
            s,o=fixture();o['scenes'][0]['sceneSeconds']=value
            with self.assertRaises(ValueError):compile_timing(s,o)
    def test_prepare_preserves_observations(self):
        s,o=fixture()
        with tempfile.TemporaryDirectory() as td:
            prepare(s,td);p=Path(td)/'observed.json';before=p.read_bytes()
            with self.assertRaises(ValueError):prepare(s,td)
            self.assertEqual(p.read_bytes(),before)

if __name__=='__main__':unittest.main()
