#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26,<2", "playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Exercise PDF identity, cache invalidation, data bounds and actual browser seeking."""
import copy,json,tempfile,unittest
from pathlib import Path
import pymupdf
from paper_video import prepare,build,validate,read,run_browser,inspect_page

class PaperVideoTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='.paper-video-tests-',dir=Path.cwd())
  self.root=Path(self.tmp.name);self.project=self.root/'film';self.pdf=self.root/'input.pdf'
  with pymupdf.open() as doc:
   for i in range(2):
    p=doc.new_page(width=300,height=400);p.insert_text((30,60),'Source evidence '+str(i+1),fontsize=14)
    p.insert_text((30,100),'Baseline 20    Method 50',fontsize=12)
   doc.save(self.pdf)
  prepare(self.pdf,self.project,[1,2],150)
  self.story={'source':{'url':'https://example.org/paper','version':'v1','license':'CC BY 4.0'},'fps':30,'scenes':[{'id':'method','script':'Explain the actual evidence.','duration':2.2,'page':1,'layout':'paper','cameraZoom':False,'view':[20,35,280,120],'targets':{'evidence':[28,42,172,64]},'cues':[{'target':'evidence','phrase':'evidence','at':.8}]}]}
 def tearDown(self):self.tmp.cleanup()
 def test_cached_pages_reuse_verified_bytes(self):
  self.assertEqual(prepare(self.pdf,self.project,[1,2],150)['reused'],2)
 def test_corrupt_image_is_recaptured(self):
  (self.project/'pages/page-001.png').write_bytes(b'broken')
  self.assertEqual(prepare(self.pdf,self.project,[1,2],150)['reused'],1)
  self.assertGreater((self.project/'pages/page-001.png').stat().st_size,100)
 def test_changed_source_invalidates_all_pages(self):
  with pymupdf.open(self.pdf) as doc:
   doc[0].insert_text((30,180),'Changed evidence');doc.save(self.root/'changed.pdf')
  self.assertEqual(prepare(self.root/'changed.pdf',self.project,[1,2],150)['reused'],0)
 def test_out_of_page_region_is_rejected(self):
  self.story['scenes'][0]['view'][2]=301
  with self.assertRaisesRegex(ValueError,'exceeds'):validate(self.story,read(self.project/'paper.json'))
 def test_stale_late_cue_is_rejected(self):
  self.story['scenes'][0]['cues'][0]['at']=2.3
  with self.assertRaisesRegex(ValueError,'inside'):validate(self.story,read(self.project/'paper.json'))
 def test_missing_rights_is_rejected(self):
  del self.story['source']['license']
  with self.assertRaisesRegex(ValueError,'license'):validate(self.story,read(self.project/'paper.json'))
 def test_abrupt_camera_settings_are_rejected(self):
  self.story['scenes'][0]['camera']={'zoom':2,'enterSeconds':1.8}
  with self.assertRaisesRegex(ValueError,'Slow the camera'):validate(self.story,read(self.project/'paper.json'))
 def test_rectangular_emphasis_is_not_a_supported_default(self):
  self.story['scenes'][0]['emphasis']='rectangle'
  with self.assertRaisesRegex(ValueError,'margin emphasis'):validate(self.story,read(self.project/'paper.json'))
 def test_compact_inspection_uses_original_page_coordinates(self):
  value=inspect_page(self.project,2,100)
  self.assertEqual(value['page'],2);self.assertEqual(value['size'],[300,400])
  self.assertIn('Source evidence 2',value['blocks'][0]['text'])
  self.assertLessEqual(sum(len(v['text']) for v in value['blocks']),100)
 def test_large_inspection_request_is_bounded_without_a_failed_call(self):
  value=inspect_page(self.project,1,14000)
  self.assertEqual(value['requestedMaxChars'],14000);self.assertEqual(value['maxChars'],12000)
 def test_percentages_do_not_accept_invented_range(self):
  self.story['scenes'][0]['chart']={'columns':['A'],'rows':[{'id':'a','values':[101]}]}
  with self.assertRaisesRegex(ValueError,'0-100'):validate(self.story,read(self.project/'paper.json'))
 def test_empty_shot_is_rejected_before_render(self):
  self.story['scenes'][0]['shots']=[{'at':1,'page':2,'view':[20,35,280,120]}]
  with self.assertRaisesRegex(ValueError,'Every paper shot'):validate(self.story,read(self.project/'paper.json'))
 def test_build_preserves_values_and_frame_clock(self):
  self.story['scenes'][0]['chart']={'unit':'%','columns':['A','B'],'rows':[{'id':'a','label':'A','values':[20,25.5]}]}
  story=self.root/'story.json';story.write_text(json.dumps(self.story),encoding='utf-8');result=build(self.project,story)
  self.assertEqual(read(self.project/'story.json')['scenes'][0]['chart']['rows'][0]['values'],[20,25.5])
  self.assertEqual(read(self.project/'timing.json')['scenes'][0]['frames'],66);self.assertAlmostEqual(result['duration'],2.2)
 def test_real_browser_can_seek_page_changes_without_collisions(self):
  s=self.story['scenes'][0];s['duration']=3.2;s['cues'].append({'target':'evidence','phrase':'second page','at':2.0});s['shots']=[{'at':1.3,'page':2,'view':s['view']}]
  story=self.root/'story.json';story.write_text(json.dumps(self.story),encoding='utf-8');build(self.project,story)
  report=self.root/'audit.json';poster=self.root/'review/exact-poster.png';result=run_browser(self.project,self.root/'clips',report,None,False,poster,'method',2.1)
  self.assertTrue(result['ok'],result);self.assertEqual(read(report)['scenes'][0]['trajectoryFrames'],96)
  from PIL import Image
  with Image.open(poster) as im:self.assertEqual(im.size,(1920,1080))

if __name__=='__main__':unittest.main()
