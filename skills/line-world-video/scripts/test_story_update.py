#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check validated story updates, exact no-ops and generated-file rollback."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
import line_world as lw
class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path.cwd());self.root=Path(self.tmp.name).resolve();self.project=self.root/'film'
        subprocess.run([sys.executable,str(Path(lw.__file__)),'init','--project',str(self.project)],check=True,capture_output=True)
    def tearDown(self):
        self.assertTrue(self.root.is_relative_to(Path.cwd().resolve()));self.tmp.cleanup()
    def test_timing_patch_rebuilds_and_preserves_unrelated_values(self):
        before=json.loads((self.project/'story.json').read_text());r=lw.update(self.project,{'timing':{'cloud':9}})
        self.assertTrue(r['rebuilt']);after=json.loads((self.project/'story.json').read_text());self.assertEqual(after['rows'],before['rows']);self.assertEqual(r['duration'],58)
        self.assertEqual(json.loads((self.project/'timing.json').read_text())['beats'][1]['start'],9)
    def test_noop_skips_build(self):
        p=self.project/'story.js';before=p.stat().st_mtime_ns;self.assertFalse(lw.update(self.project,{'timing':{'cloud':7}})['rebuilt']);self.assertEqual(p.stat().st_mtime_ns,before)
    def test_invalid_and_missing_asset_preserve_all_outputs(self):
        names=['story.json','story.js','index.html','timing.json','selection.json'];before={n:(self.project/n).read_bytes() for n in names}
        for patch in [{'timing':{'cloud':-1}},{'assets':{'mermaid':'missing.svg'}}]:
            with self.assertRaises((ValueError,OSError)):lw.update(self.project,patch)
            self.assertEqual({n:(self.project/n).read_bytes() for n in names},before)
    def test_copied_editor_and_builder_operate_inside_generated_project(self):
        patch=self.project/'edit.json';patch.write_text(json.dumps({'changes':[{'file':'theme','path':'fontScale','value':1.05}]}),encoding='utf-8')
        for script,args in [('video_edit.py',['apply','--patch',str(patch)]),('story.py',['build'])]:
            result=subprocess.run([sys.executable,str(self.project/'scripts'/script),args[0],'--project',str(self.project),*args[1:]],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('--lw-font-scale:1.05',(self.project/'theme.css').read_text(encoding='utf-8'))
if __name__=='__main__':unittest.main()
