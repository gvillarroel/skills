#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2", "numpy>=2,<3"]
# ///
"""Exercise transit-only defects, real video decoding, cache reuse and source safety."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_video as review


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="line-world-review-test-", dir=Path.cwd())
        cls.root = Path(cls.temp.name)
        cls.video = cls.root / "fixture.mp4"
        command = ['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=white:s=640x360:r=30:d=11','-vf','drawbox=x=200:y=100:w=240:h=100:color=gray:t=2,drawbox=x=20:y=20:w=30:h=30:color=red:t=fill','-an','-c:v','libx264','-pix_fmt','yuv420p',str(cls.video)]
        subprocess.run(command, check=True, capture_output=True)
        (cls.root/'story.json').write_text(json.dumps({'scenes':[{'id':'fixture','clipSeconds':11}]}),encoding='utf-8')
        cues = [{'target':'step-'+str(i),'at':1+i*.05,'travelSeconds':.28} for i in range(150)]
        (cls.root/'cues.json').write_text(json.dumps({'scenes':[{'id':'fixture','cues':cues}]}),encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def invoke(self, output, document=None):
        args=[sys.executable,str(Path(review.__file__)),'--video',str(self.video),'--story',str(self.root/'story.json'),'--cues',str(self.root/'cues.json'),'--output',str(output)]
        if document:args.extend(['--html',str(document)])
        return subprocess.run(args,capture_output=True,text=True,encoding='utf-8')

    def document(self, name, collision):
        if collision:
            contents='<rect id="block" x="280" y="130" width="140" height="80" fill="white" stroke="#696969"/><text x="290" y="170" font-size="24">Obstacle</text>'
            y=160
        else:
            contents='<text x="200" y="120" font-size="28">Readable</text>'
            y=260
        path=self.root/(name+'.html')
        tail='<circle id="guide" cx="20" cy="__Y__" r="7" fill="#9e1b32"/></svg><script>window.renderAt=t=>{document.querySelector("#guide").setAttribute("cx",20+600*t/11);return{guide:{x:20+600*t/11,y:__Y__}}};window.snapshot=()=>({x:+document.querySelector("#guide").getAttribute("cx")});</script>'
        path.write_text('<style>body{margin:0}</style><svg id="stage" width="640" height="360">'+contents+tail.replace('__Y__',str(y)),encoding='utf-8')
        return path

    def test_real_transit_collision_is_detected_between_safe_endpoints(self):
        path=self.document('collision',True);result=self.invoke(self.root/'collision-review',path)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        report=review.read(self.root/'collision-review/report.json')
        self.assertEqual(report['encoded']['frames'],330)
        issues=report['source']['scenes'][0]['guideIssues']
        self.assertTrue(any(i['kind']=='guide-over-text' and i['frames']>1 for i in issues))
        self.assertTrue(any(i['kind']=='guide-over-mark' and i['intervals'] for i in issues))

    def test_large_sample_plan_cache_and_corrupt_thumbnail_recovery(self):
        output=self.root/'clean-review';path=self.document('clean',False)
        first=self.invoke(output,path);self.assertEqual(first.returncode,0,first.stdout+first.stderr)
        summary=review.read(output/'summary.json');self.assertGreater(summary['cache']['capturedFrames'],200)
        second=self.invoke(output,path);self.assertEqual(second.returncode,0,second.stdout+second.stderr)
        cached=review.read(output/'summary.json');self.assertEqual(cached['cache']['capturedFrames'],0);self.assertTrue(cached['sourceReused'])
        record=next(iter(review.read(output/'cache.json')['frames'].values()));(output/record['path']).write_bytes(b'corrupt')
        third=self.invoke(output,path);self.assertEqual(third.returncode,0,third.stdout+third.stderr)
        self.assertEqual(review.read(output/'summary.json')['cache']['capturedFrames'],1)

    def test_review_cannot_overwrite_the_authored_source(self):
        path=self.document('source-safe',False);before=path.read_bytes();result=self.invoke(self.root,path)
        self.assertEqual(result.returncode,2);self.assertIn('separate review directory',result.stderr);self.assertEqual(path.read_bytes(),before)

    def test_unsafe_or_duplicate_scene_identifiers_are_rejected(self):
        for scenes in [[{'id':'../escape','clipSeconds':11}],[{'id':'same','clipSeconds':5.5},{'id':'same','clipSeconds':5.5}]]:
            with self.subTest(scenes=scenes),self.assertRaisesRegex(ValueError,'scene IDs'):
                review.plan({'scenes':scenes},None,None,30,330)

    def test_visual_attestation_is_bound_to_the_exact_artifacts(self):
        path=self.root/'operator.json';path.write_text(json.dumps({'videoSha256':'movie','sourceSha256':'source','scenes':[{'id':'fixture','reviewed':True,'notes':'Inspected the fixture contact sheet.'}]}),encoding='utf-8')
        self.assertEqual(review.manual_review(path,'movie',{'sourceSha256':'source'},[{'id':'fixture'}]),'recorded')
        with self.assertRaisesRegex(ValueError,'different movie/source'):
            review.manual_review(path,'changed',{'sourceSha256':'source'},[{'id':'fixture'}])
        with self.assertRaisesRegex(ValueError,'every current scene'):
            review.manual_review(path,'movie',{'sourceSha256':'source'},[{'id':'another'}])


if __name__ == '__main__':
    unittest.main()
