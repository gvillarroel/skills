#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise semantic edits, transactions, style validation and dependency-aware reuse."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import video_edit as edit

class EditingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path.cwd());self.root=Path(self.tmp.name).resolve()
  self.story={'language':'en','voice':'Nyla','scenes':[{'id':sid,'clipSeconds':8,'essentialAnimationSeconds':4,'script':'Explain '+sid} for sid in ['a','b','c']]}
  self.cues={'scenes':[{'id':sid,'cues':[{'id':'focus','target':sid+'-mark','at':2,'travelSeconds':.25}]} for sid in ['a','b','c']]}
  self.write('story.json',self.story);self.write('cues.json',self.cues);edit.setup(self.root,cues='cues.json')
 def tearDown(self):self.tmp.cleanup()
 def write(self,name,value):edit.atomic(self.root/name,edit.encode(value))
 def op(self,path,value,file='story',**extra):return {'changes':[{'file':file,'path':path,'value':value,**extra}]}
 def snapshots(self):return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
 def receipt(self,sid,first=None,last=None):
  current=next(s for s in edit.status(self.root,True)['scenes'] if s['id']==sid);i=['a','b','c'].index(sid)
  p=self.root/(sid+'.bin');p.write_bytes(('Rendered fixture '+sid).encode())
  return {'id':sid,'inputsSha256':current['inputsSha256'],'artifact':p.name,'firstPose':first or {'x':i},'lastPose':last or {'x':i+1}}
 def seed_cache(self):edit.record(self.root,[self.receipt(sid) for sid in ['a','b','c']])
 def test_stable_id_patch_preserves_other_scenes_and_order(self):
  edit.apply(self.root,self.op('scenes[id=b].clipSeconds',9));after=edit.read(self.root/'story.json')
  self.assertEqual(after['scenes'][0],self.story['scenes'][0]);self.assertEqual(after['scenes'][2],self.story['scenes'][2]);self.assertEqual([s['id'] for s in after['scenes']],['a','b','c'])
 def test_ambiguous_selector_unknown_field_and_id_change_fail_without_writes(self):
  before=self.snapshots()
  for path,value in [('scenes[clipSeconds=8].script','New'),('scenes[id=b].scrpt','New'),('scenes[id=b].id','renamed')]:
   with self.assertRaises(ValueError):edit.apply(self.root,self.op(path,value))
  self.assertEqual(before,self.snapshots())
 def test_expected_value_and_hash_guard(self):
  before=self.snapshots();p=self.op('scenes[id=b].clipSeconds',9,expect=7)
  with self.assertRaises(ValueError):edit.apply(self.root,p)
  p=self.op('scenes[id=b].clipSeconds',9);p['expectedSha256']={'story':'0'*64}
  with self.assertRaises(ValueError):edit.apply(self.root,p)
  self.assertEqual(before,self.snapshots())
 def test_dry_run_and_noop_preserve_exact_files_and_mtime(self):
  before=self.snapshots();stamp=(self.root/'story.json').stat().st_mtime_ns
  self.assertTrue(edit.apply(self.root,self.op('scenes[id=b].clipSeconds',9),True)['dryRun'])
  self.assertFalse(edit.apply(self.root,self.op('scenes[id=b].clipSeconds',8))['changed'])
  self.assertEqual(before,self.snapshots());self.assertEqual(stamp,(self.root/'story.json').stat().st_mtime_ns)
 def test_invalid_duration_animation_nan_and_palette_fail_before_writes(self):
  before=self.snapshots()
  for p in [self.op('scenes[id=b].clipSeconds',3),self.op('scenes[id=b].clipSeconds',float('nan')),self.op('colors.primary','#e8002a','theme'),self.op('fontScale',3,'theme')]:
   with self.assertRaises(ValueError):edit.apply(self.root,p)
  self.assertEqual(before,self.snapshots())
 def test_cue_budget_cross_file_validation(self):
  before=self.snapshots()
  with self.assertRaises(ValueError):edit.apply(self.root,self.op('scenes[id=b].cues[id=focus].at',9,'cues'))
  self.assertEqual(before,self.snapshots())
 def test_transaction_rolls_back_on_mid_write_failure(self):
  before=self.snapshots();original=edit.atomic;calls=0
  def fail_once(p,data):
   nonlocal calls
   calls+=1
   if calls==2:raise OSError('Injected write failure')
   return original(p,data)
  with patch.object(edit,'atomic',fail_once):
   with self.assertRaises(OSError):edit.apply(self.root,self.op('fontScale',1.1,'theme'))
  self.assertEqual(before,self.snapshots())
 def test_restore_exact_bytes_and_stale_restore_rejected(self):
  before=(self.root/'story.json').read_bytes();r=edit.apply(self.root,self.op('scenes[id=b].script','Changed'))
  edit.restore(self.root,r['revision']);self.assertEqual(before,(self.root/'story.json').read_bytes())
  r=edit.apply(self.root,self.op('scenes[id=b].script','Changed'));edit.apply(self.root,self.op('scenes[id=b].clipSeconds',9))
  with self.assertRaises(ValueError):edit.restore(self.root,r['revision'])
 def test_theme_compilation_places_project_overrides_last(self):
  edit.apply(self.root,self.op('fontScale',1.1,'theme'));css=(self.root/'theme.css').read_text(encoding='utf-8')
  self.assertGreater(css.rfind('--lw-font-scale:1.1'),css.find('--lw-font-scale:1;'));self.assertIn('--lw-primary:#9e1b32',css)
 def test_selected_inspection_is_bounded(self):
  r=edit.inspect(self.root,'cues','scenes[id=b].cues[id=focus]');self.assertEqual(r['value']['target'],'b-mark');self.assertLess(len(json.dumps(r)),500)
 def test_paths_and_existing_authored_css_are_protected(self):
  with self.assertRaises(ValueError):edit.inside(self.root,'../outside.json')
  other=self.root/'other';other.mkdir();(other/'story.json').write_bytes(edit.encode(self.story));(other/'theme.css').write_text('/* Authored CSS */',encoding='utf-8')
  with self.assertRaises(ValueError):edit.setup(other)
  self.assertFalse((other/'theme.json').exists());self.assertFalse((other/edit.META).exists())
 def test_cache_local_edit_waits_for_endpoint_then_reuses_successor(self):
  self.seed_cache();edit.apply(self.root,self.op('scenes[id=b].cues[id=focus].at',3,'cues'));s=edit.status(self.root)
  self.assertEqual(s['render'],['b']);self.assertEqual(s['checkJoin'],['c']);self.assertEqual(s['reuse'],['a'])
  edit.record(self.root,[self.receipt('b')]);self.assertEqual(edit.status(self.root)['reuse'],['a','b','c'])
 def test_changed_endpoint_propagates_until_a_stable_join(self):
  self.seed_cache();edit.apply(self.root,self.op('scenes[id=a].cues[id=focus].at',3,'cues'));edit.record(self.root,[self.receipt('a',last={'x':10})])
  s=edit.status(self.root);self.assertEqual(s['render'],['b']);self.assertEqual(s['checkJoin'],['c'])
  edit.record(self.root,[self.receipt('b',first={'x':10})]);self.assertEqual(edit.status(self.root)['reuse'],['a','b','c'])
 def test_bad_receipt_wrong_join_and_stale_predecessor_are_rejected(self):
  self.seed_cache();before=(self.root/'.line-world/render-state.json').read_bytes();r=self.receipt('b',first={'x':99})
  with self.assertRaises(ValueError):edit.record(self.root,[r])
  r=self.receipt('a');r['inputsSha256']='0'*64
  with self.assertRaises(ValueError):edit.record(self.root,[r])
  (self.root/'a.bin').write_bytes(b'Corrupted')
  with self.assertRaises(ValueError):edit.record(self.root,[self.receipt('c')])
  self.assertEqual(before,(self.root/'.line-world/render-state.json').read_bytes());self.assertEqual(edit.status(self.root)['checkJoin'],['b','c'])
 def test_theme_invalidates_all_scenes(self):
  self.seed_cache();edit.apply(self.root,self.op('fontScale',1.05,'theme'));self.assertEqual(edit.status(self.root)['render'],['a','b','c'])
 def test_global_clock_and_overview_dependencies(self):
  self.seed_cache();c=edit.read(self.root/edit.META);c['clock']='global';c['overviewIds']=['c'];self.write(edit.META,c);self.seed_cache()
  edit.apply(self.root,self.op('scenes[id=a].clipSeconds',9));self.assertEqual(edit.status(self.root)['render'],['a','b','c'])
 def test_declared_source_change_is_detected(self):
  (self.root/'figure.svg').write_text('<svg/>',encoding='utf-8');c=edit.read(self.root/edit.META);c['sceneInputs']={'b':['figure.svg']};self.write(edit.META,c);self.seed_cache()
  (self.root/'figure.svg').write_text('<svg><!-- changed --></svg>',encoding='utf-8');self.assertEqual(edit.status(self.root)['render'],['b'])
 def test_render_does_not_clear_narration_review(self):
  self.seed_cache();r=edit.apply(self.root,self.op('scenes[id=b].script','New spoken text'));self.assertTrue(r['narrationReview'])
  edit.record(self.root,[self.receipt('b')]);self.assertEqual(edit.status(self.root)['narrationReview'],['b']);self.assertIn('never confirms native',edit.status(self.root)['scope'])
 def test_cli_report_cannot_replace_inputs(self):
  p=self.root/'patch.json';p.write_bytes(edit.encode(self.op('scenes[id=b].clipSeconds',9)));before=(self.root/'story.json').read_bytes()
  r=subprocess.run([sys.executable,str(Path(edit.__file__)),'apply','--project',str(self.root),'--patch',str(p),'--report',str(self.root/'story.json')],capture_output=True,text=True)
  self.assertEqual(r.returncode,2);self.assertEqual(before,(self.root/'story.json').read_bytes())
 def test_project_relative_input_and_ambiguous_input(self):
  name='patch-'+self.root.name+'.json';p=self.root/name;self.write(name,self.op('scenes[id=b].clipSeconds',9))
  self.assertEqual(edit.input_path(self.root,name),p)
  other=Path.cwd()/name
  try:
   other.write_text('{}',encoding='utf-8')
   with self.assertRaises(ValueError):edit.input_path(self.root,name)
   self.assertEqual(edit.input_path(self.root,p),p)
  finally:other.unlink()

if __name__=='__main__':unittest.main()
