#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise real media caching, stale evidence and isolated native-UI text parsing."""
import copy,json,math,shutil,subprocess,tempfile,unittest
from pathlib import Path
from batch_clips import sha,inside,atomic_json
from vids_batch import init,build,observe,patch_story,load,queue,confirm,announcements,deliver,delivery_status

class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise unittest.SkipTest('FFmpeg is required for real media tests.')
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path.cwd());self.root=Path(self.tmp.name).resolve();self.assertTrue(self.root.is_relative_to(Path.cwd().resolve()))
        self.source=self.root/'source.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=white:s=320x180:r=30:d=2','-vf','drawbox=x=40:y=40:w=240:h=1:color=gray,drawbox=x=100:y=90:w=12:h=12:color=0x9e1b32','-an','-c:v','libx264','-pix_fmt','yuv420p',str(self.source)],check=True,capture_output=True)
        self.story={'projectTitle':'Fixture production','voice':'Nyla','language':'en','fps':30,'width':320,'height':180,'scenes':[{'id':sid,'script':'Explain '+sid+'.','sourceClip':'source.mp4','visual':'A synthetic static red mark.','clipSeconds':2,'essentialAnimationSeconds':.5,'staticHoldAfterSeconds':.5} for sid in ['prepare','compare','evaluate']]}
        self.path=self.root/'input.json';atomic_json(self.path,self.story);self.project=self.root/'film';init(self.project,self.path)
        self.measured={'voice':'Nyla','scenes':[{'id':sid,'observed':True,'voiceoverSeconds':seconds-.05,'sceneSeconds':seconds} for sid,seconds in zip(['prepare','compare','evaluate'],[.91,1.01,1.5])]}
        self.measure=self.root/'measured.json';atomic_json(self.measure,self.measured)
    def tearDown(self):
        self.assertTrue(self.root.is_relative_to(Path.cwd().resolve()));self.tmp.cleanup()
    def ready(self):observe(self.project,self.measure);return build(self.project)
    def approve_fixture(self):
        root,story,state=load(self.project);tasks=queue(root,story,state)
        return confirm(root,[{'taskId':t['taskId'],'observed':True,'evidence':'Synthetic test fixture: simulated native placement/order.'} for t in tasks])
    def test_draft_has_pending_voices_without_timing(self):
        r=build(self.project);self.assertTrue(r['bulkVoiceEligible']);self.assertEqual(len(r['pendingVoiceovers']),3);self.assertFalse((self.project/'handoff/timing.json').exists())
    def test_delivery_requires_completed_native_queue(self):
        with self.assertRaisesRegex(ValueError,'pending native queue'):deliver(self.project,self.source)
    def test_empty_upload_queue_still_needs_observed_delivery(self):
        self.ready();self.approve_fixture();self.assertEqual(delivery_status(self.project)['status'],'awaiting-delivery')
        result=deliver(self.project,self.source);self.assertFalse(result['ok']);self.assertEqual(result['status'],'collect-observations')
        evidence=Path(result['evidence']);before=evidence.read_bytes();second=deliver(self.project,self.source)
        self.assertFalse(second['ok']);self.assertEqual(evidence.read_bytes(),before);self.assertFalse(second['checks']['nativeProjectSaved'])
    def test_batch_ceil_and_second_build_zero_encodes(self):
        a=self.ready();self.assertEqual(a['encodedClips'],3)
        timing=json.loads((self.project/'handoff/timing.json').read_text());self.assertEqual(timing['frames'],28+31+45)
        b=build(self.project);self.assertEqual(b['encodedClips'],0);self.assertEqual(b['reusedClips'],3)
        self.assertEqual(a['duration'],b['duration'])
    def test_one_narration_change_only_retimes_one_clip(self):
        self.ready();self.approve_fixture();patch_story(self.project,{'scenes':[{'id':'compare','script':'A longer comparison.'}]})
        a=build(self.project);self.assertEqual(a['pendingVoiceovers'],['compare']);self.assertFalse(a['timingReady'])
        new={'voice':'Nyla','scenes':[{'id':'compare','observed':True,'voiceoverSeconds':1.05,'sceneSeconds':1.12}]};atomic_json(self.measure,new);observe(self.project,self.measure)
        b=build(self.project);self.assertEqual(b['encodedClips'],1);self.assertEqual(b['reusedClips'],2)
        root,story,state=load(self.project);tasks=queue(root,story,state);self.assertEqual([(t['kind'],t['sceneId']) for t in tasks],[('upload','compare')])
    def test_reorder_reuses_all_media_and_only_verifies_order(self):
        self.ready();self.approve_fixture();patch_story(self.project,{'order':['evaluate','prepare','compare']});r=build(self.project)
        self.assertEqual(r['encodedClips'],0);self.assertEqual(r['reusedClips'],3)
        root,story,state=load(self.project);self.assertEqual([t['kind'] for t in queue(root,story,state)],['verify-order'])
    def test_invalid_patch_is_atomic(self):
        original=(self.project/'story.json').read_bytes()
        with self.assertRaises(ValueError):patch_story(self.project,{'scenes':[{'id':'prepare','script':''}]})
        self.assertEqual((self.project/'story.json').read_bytes(),original)
    def test_noop_edit_and_history(self):
        self.assertFalse(patch_story(self.project,{'projectTitle':'Fixture production'})['changed'])
        patch_story(self.project,{'projectTitle':'New fixture name'});self.assertEqual(len(list((self.project/'.vids/history').glob('*.json'))),1)
    def test_voice_change_invalidates_every_measurement(self):
        self.ready();patch_story(self.project,{'voice':'Alba'});r=build(self.project);self.assertEqual(len(r['pendingVoiceovers']),3);self.assertFalse(r['timingReady'])
    def test_old_measurement_file_cannot_be_rebound_to_new_script(self):
        self.ready();patch_story(self.project,{'scenes':[{'id':'prepare','script':'A new script.'}]})
        with self.assertRaisesRegex(ValueError,'older narration'):observe(self.project,self.measure)
    def test_deleted_upload_is_restored_from_cache(self):
        self.ready();root,story,state=load(self.project);Path(state['clips']['prepare']['target']).unlink()
        self.assertFalse(build(root,False)['timingReady']);r=build(root);self.assertEqual(r['encodedClips'],0);self.assertEqual(r['reusedClips'],3)
    def test_malformed_observation_batch_does_not_partially_import(self):
        a=load(self.project)[2];bad=copy.deepcopy(self.measured);bad['scenes'][2]['sceneSeconds']=-1;atomic_json(self.measure,bad)
        with self.assertRaises(ValueError):observe(self.project,self.measure)
        self.assertEqual(load(self.project)[2],a)
    def test_unmeasured_observation_rejected(self):
        bad=copy.deepcopy(self.measured);bad['scenes'][0]['observed']=False;atomic_json(self.measure,bad)
        with self.assertRaises(ValueError):observe(self.project,self.measure)
    def test_retime_requires_declared_hold(self):
        observe(self.project,self.measure);patch_story(self.project,{'scenes':[{'id':'prepare','staticHoldAfterSeconds':None}]})
        with self.assertRaisesRegex(ValueError,'Declare staticHoldAfterSeconds'):build(self.project)
        self.assertFalse((self.project/'media').exists())
    def test_essential_motion_cut_rejected_before_any_encode(self):
        observe(self.project,self.measure);patch_story(self.project,{'scenes':[{'id':'evaluate','essentialAnimationSeconds':1.8}]})
        with self.assertRaisesRegex(ValueError,'Essential animation'):build(self.project)
        self.assertFalse((self.project/'media').exists())
    def test_corrupt_cache_is_rebuilt(self):
        self.ready();root,story,state=load(self.project);p=root/'.vids/cache'/state['clips']['prepare']['key']/'clip.mp4';p.write_bytes(b'corrupt')
        r=build(root);self.assertEqual(r['encodedClips'],1);self.assertEqual(r['reusedClips'],2)
    def test_false_and_stale_ui_receipts_rejected(self):
        self.ready();root,story,state=load(self.project);task=next(t for t in queue(root,story,state) if t['kind']=='upload')
        with self.assertRaises(ValueError):confirm(root,[{'taskId':task['taskId'],'observed':False,'evidence':'Not observed.'}])
        patch_story(root,{'scenes':[{'id':task['sceneId'],'script':'Changed.'}]})
        with self.assertRaises(ValueError):confirm(root,[{'taskId':task['taskId'],'observed':True,'evidence':'Old fixture receipt.'}])
    def test_source_and_native_files_are_preserved(self):
        digest=sha(self.source);self.ready();build(self.project);self.assertEqual(sha(self.source),digest)
    def test_source_collision_uses_separate_upload(self):
        original=self.project/'media/prepare.mp4';original.parent.mkdir();shutil.copyfile(self.source,original);before=sha(original)
        patch_story(self.project,{'scenes':[{'id':'prepare','sourceClip':str(original)}]});self.ready()
        self.assertEqual(sha(original),before);state=load(self.project)[2];self.assertEqual(Path(state['clips']['prepare']['target']),self.project/'media/prepared/prepare.mp4')
    def test_announcement_import_uses_precise_ms_and_requires_attestation(self):
        text='100 text Scene 1 of 3, duration 1 second 40 milliseconds\n101 text Scene 2 of 3, duration 1 second 200 milliseconds\n102 text Scene 3 of 3, duration 1 second 500 milliseconds'
        f=self.root/'native.txt';f.write_text(text)
        with self.assertRaises(ValueError):observe(self.project,f,'Nyla',True)
        observe(self.project,f,'Nyla',True,True,True);r=build(self.project);self.assertAlmostEqual(r['duration'],32/30+1.2+1.5)
    def test_conflicting_and_wrong_count_announcements_rejected(self):
        for text in ['Scene 1 of 99, duration 2 seconds','Scene 1 of 3, duration 1 second\nScene 1 of 3, duration 2 seconds']:
            with self.assertRaises(ValueError):announcements(text,self.story)
    def test_output_escape_rejected(self):
        with self.assertRaises(ValueError):inside(self.project,'../outside.mp4')
    def test_plan_only_retains_unchanged_measured_timing(self):
        self.ready();before=(self.project/'handoff/timing.json').read_bytes();r=build(self.project,False)
        self.assertTrue(r['timingReady']);self.assertEqual((self.project/'handoff/timing.json').read_bytes(),before)
    def test_dimensions_preflight(self):
        observe(self.project,self.measure);p=self.project/'story.json';s=json.loads(p.read_text());s['width']=640;atomic_json(p,s)
        with self.assertRaisesRegex(ValueError,'dimensions'):build(self.project)
        self.assertFalse((self.project/'media').exists())

class UiParserTests(unittest.TestCase):
    def test_compact_parser_drops_private_lists_and_disabled_controls(self):
        runtime=Path(__file__).resolve().parent.parent/'assets/runtime/vids-ui.js'
        raw='0 document Fixture - Google Vids Value: https://docs.google.com/videos/d/fixture/edit\n1 button Document status: Saved to Drive.\n2 button Insert voiceover\n3 button (disabled) Update voiceover\n4 text Scene 2 of 3, duration 1 second 200 milliseconds\n5 text 00:02.0\n6 text 00:03.0\n7 group Description: compare.mp4\n8 button Scene 2 of 3\n9 tab item (selectable) All scenes\n'+''.join(f'{100+i} list item option unrelated-private-file-{i}\n' for i in range(1000))
        js="const p=require(process.argv[1]);let s=p.summarize(require('node:fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(s))"
        result=subprocess.run(['node','-e',js,str(runtime)],input=raw,capture_output=True,text=True,check=True);out=json.loads(result.stdout)
        self.assertTrue(out['recognized']);self.assertNotIn('unrelated-private',result.stdout);self.assertEqual(out['controls']['Insert voiceover'],2);self.assertNotIn('Update voiceover',out['controls']);self.assertLess(len(result.stdout),len(raw)/20)
        self.assertEqual(out['scenes'][0]['index'],8);self.assertEqual(out['tabs']['All scenes'],9)
        other=subprocess.run(['node','-e',js,str(runtime)],input='0 document Downloads Value: chrome://downloads/',capture_output=True,text=True,check=True)
        self.assertFalse(json.loads(other.stdout)['recognized'])

if __name__=='__main__':unittest.main()
