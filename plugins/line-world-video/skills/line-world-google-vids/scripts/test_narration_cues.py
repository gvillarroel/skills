#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test audio identity, repeated values and evidence failures."""
import copy,unittest
from narration_cues import align
def fixture():
 words=[{'word':w,'start':s,'end':e} for w,s,e in [('60,',10.4,11),('20',11.3,11.7),('y',11.7,11.9),('20%.',11.9,12.8)]]
 return {'segments':[{'words':words}]},{'scenes':[{'id':'split','start':3,'end':23,'duration':20}]},{'scenes':[{'id':'split','cues':[{'target':'train','phrase':'sesenta'},{'target':'validation','phrase':'veinte'},{'target':'test','phrase':'veinte','occurrence':2}]}]}
class CueTests(unittest.TestCase):
 def test_repeated_values_keep_distinct_identity_and_scene_clock(self):
  cues=align(*fixture())['scenes'][0]['cues'];self.assertEqual([c['target'] for c in cues],['train','validation','test']);self.assertAlmostEqual(cues[0]['at'],7.4);self.assertAlmostEqual(cues[2]['at'],8.9);self.assertIn('approximate',cues[0]['evidence'])
 def test_missing_audio_fails(self):
  a,t,s=fixture();a['segments']=[]
  with self.assertRaisesRegex(ValueError,'Unmatched'):align(a,t,s)
 def test_unmatched_phrase_fails(self):
  a,t,s=fixture();s['scenes'][0]['cues'][0]['phrase']='unspoken'
  with self.assertRaisesRegex(ValueError,'Unmatched'):align(a,t,s)
 def test_wrong_speech_order_fails(self):
  a,t,s=fixture();s['scenes'][0]['cues'].reverse()
  with self.assertRaisesRegex(ValueError,'speech order'):align(a,t,s)
 def test_invalid_word_times_fail(self):
  a,t,s=fixture();a['segments'][0]['words'][0]['start']=float('nan')
  with self.assertRaisesRegex(ValueError,'finite'):align(a,t,s)
 def test_duplicate_scene_id_fails(self):
  a,t,s=fixture();t['scenes']*=2
  with self.assertRaisesRegex(ValueError,'unique'):align(a,t,s)
 def test_invalid_travel_fails(self):
  a,t,s=fixture();s['scenes'][0]['cues'][0]['travelSeconds']=False
  with self.assertRaisesRegex(ValueError,'travelSeconds'):align(a,t,s)
 def test_reviewed_asr_alternative_is_explicit(self):
  a,t,s=fixture();s['scenes'][0]['cues'][0].update(phrase='sixty',alternatives=['sesenta']);self.assertAlmostEqual(align(a,t,s)['scenes'][0]['cues'][0]['at'],7.4)
if __name__=='__main__':unittest.main()
