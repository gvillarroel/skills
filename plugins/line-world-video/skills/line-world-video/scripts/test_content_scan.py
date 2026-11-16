#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3", "Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Exercise guide-only gaps, narrow dividers, source anchors and reversible emphasis."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import content_scan as content
import review_video as review


class ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='content-coverage-',dir=Path.cwd());cls.root=Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def movie(self,name,gap=False):
        path=self.root/(name+'.mp4');enable=":enable='lt(t,1)+gte(t,2)'" if gap else ''
        vf='drawbox=x=200:y=100:w=240:h=120:color=gray:t=3'+enable+',drawbox=x=40:y=170:w=10:h=10:color=0x9e1b32:t=fill'
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=white:s=640x360:r=30:d=3','-vf',vf,'-an','-c:v','libx264','-pix_fmt','yuv420p',str(path)],check=True,capture_output=True)
        return path

    def test_dot_only_divider_only_and_uniform_color_are_not_content(self):
        image=np.full((360,640,3),255,np.uint8)
        self.assertTrue(content.measure(image)['insufficient']);image[170:180,40:50]=[158,27,50]
        self.assertTrue(content.measure(image)['insufficient']);image[:]=255;image[180:182,:]=130
        self.assertTrue(content.measure(image)['insufficient']);image[:]=[158,27,50]
        self.assertTrue(content.measure(image)['insufficient'])

    def test_sparse_legible_geometry_is_accepted(self):
        image=np.full((360,640,3),255,np.uint8);image[100:103,200:440]=130;image[217:220,200:440]=130;image[100:220,200:203]=130;image[100:220,437:440]=130
        self.assertFalse(content.measure(image)['insufficient'])

    def test_real_encoded_guide_only_interval_and_corrected_cache(self):
        video=self.movie('gap',True);report=content.scan(video,cache=self.root/'scan.json')
        self.assertFalse(report['ok']);self.assertEqual(report['frames'],90);self.assertEqual(report['insufficientFrames'],30)
        self.assertEqual([(i['firstFrame'],i['lastFrame']) for i in report['intervals']],[(30,59)])
        fixed=self.movie('fixed');positive=content.scan(fixed,cache=self.root/'scan.json');self.assertTrue(positive['ok']);self.assertFalse(positive['reused'])
        self.assertTrue(content.scan(fixed,cache=self.root/'scan.json')['reused'])
        raw=json.loads((self.root/'scan.json').read_text());raw['result']['frames']=0;(self.root/'scan.json').write_text(json.dumps(raw))
        self.assertFalse(content.scan(fixed,cache=self.root/'scan.json')['reused'])

    def test_source_guide_and_divider_fail_even_with_a_nonempty_movie(self):
        document=self.root/'empty.html';document.write_text('<svg id="stage" width="640" height="360"><rect class="panel-boundary" x="5" y="5" width="310" height="350" fill="none" stroke="#cfcfcf"/><line data-divider="true" x1="0" y1="180" x2="640" y2="180" stroke="#828282"/><g data-content-anchor="hidden-path"><path d="M200 100L400 200" fill="none" stroke="#696969" stroke-dasharray="224 224" stroke-dashoffset="224"/></g><circle id="guide" cx="50" cy="80" r="7" fill="#9e1b32"/></svg><script>renderAt=t=>({camera:{x:0,y:0},guide:{x:50,y:80}});snapshot=()=>renderAt(0)</script>')
        scenes=[{'id':'gap','index':0,'start':0,'duration':3,'sourceDuration':3,'cues':[]}]
        result=review.source_review(document,scenes,'global',30,640,360,self.root/'source-review',[])
        self.assertEqual(result['scenes'][0]['content']['minimumVisibleAnchors'],0)
        self.assertEqual(result['scenes'][0]['content']['emptyIntervals'][0]['frames'],90)

    def test_theme_focus_restores_geometry_and_preserves_quantity_color(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=review.browser_path(),headless=True);page=browser.new_page()
            page.set_content('<svg id="stage"><g id="one"><rect width="100" height="80" fill="white" stroke="var(--lw-line)"/><rect class="pixel" x="120" width="20" height="20" style="fill:#696969!important"/><text y="30" fill="#333e48">Object</text></g><g id="two"><rect data-encoding="quantity" width="120" height="30" fill="#696969"/><text y="60">26.2%</text></g></svg>')
            page.add_style_tag(path=str(review.SKILL/'assets/runtime/theme.css'));page.add_script_tag(path=str(review.SKILL/'assets/runtime/theme.js'))
            page.add_style_tag(content='#one rect{fill:white!important;stroke:#828282!important}')
            states=page.evaluate('''()=>{const root=document.querySelector('#stage'),a=document.querySelector('#one'),b=document.querySelector('#two'),shape=a.querySelector('rect'),bar=b.querySelector('rect');const before=shape.getAttribute('width');LineWorldTheme.focus(root,a);const pixelFill=getComputedStyle(a.querySelector('.pixel')).fill,active={fill:getComputedStyle(shape).fill,stroke:getComputedStyle(shape).stroke,width:getComputedStyle(shape).strokeWidth};LineWorldTheme.focus(root,b,'secondary');const secondary={fill:getComputedStyle(bar).fill,text:getComputedStyle(b.querySelector('text')).fill};LineWorldTheme.focus(root,null);return{active,secondary,pixelFill,cleared:getComputedStyle(shape).stroke,geometryUnchanged:before===shape.getAttribute('width'),marked:root.querySelectorAll('[data-lw-focus]').length}}''')
            browser.close()
        self.assertEqual(states['active'],{'fill':'rgb(158, 27, 50)','stroke':'none','width':'0px'})
        self.assertEqual(states['secondary'],{'fill':'rgb(105, 105, 105)','text':'rgb(105, 105, 105)'})
        self.assertEqual(states['pixelFill'],'rgb(105, 105, 105)')
        self.assertEqual(states['cleared'],'rgb(130, 130, 130)');self.assertTrue(states['geometryUnchanged']);self.assertEqual(states['marked'],0)


    def test_explicit_solid_focus_keeps_white_internal_text_and_restores(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=review.browser_path(),headless=True);page=browser.new_page()
            page.set_content('<svg id="stage"><g id="object"><rect id="face" data-focus-fill="solid" width="160" height="80" fill="white"/><text id="inside" data-focus-on-fill="true" x="10" y="40">CUDA</text><text id="outside" y="120">2007</text><rect id="data" data-focus-fill="solid" data-encoding="quantity" x="200" width="40" height="80" fill="#696969"/></g></svg>')
            page.add_style_tag(path=str(review.SKILL/'assets/runtime/theme.css'));page.add_script_tag(path=str(review.SKILL/'assets/runtime/theme.js'))
            result=page.evaluate('''()=>{const root=document.querySelector('#stage'),target=document.querySelector('#object'),ids=['face','inside','outside','data'],get=()=>ids.map(id=>getComputedStyle(document.getElementById(id)).fill);const before=get();LineWorldTheme.focus(root,target);const active=get();LineWorldTheme.focus(root,null);return{before,active,after:get()}}''');browser.close()
        self.assertEqual(result['active'],['rgb(158, 27, 50)','rgb(255, 255, 255)','rgb(158, 27, 50)','rgb(105, 105, 105)'])
        self.assertEqual(result['before'],result['after'])

    def test_combined_cli_serializes_both_real_gap_intervals(self):
        video=self.movie('combined-gap',True);document=self.root/'combined.html'
        document.write_text('<svg id="stage" width="640" height="360"><g id="object"><rect x="200" y="100" width="240" height="120" fill="white" stroke="#696969"/></g><circle id="guide" cx="45" cy="175" r="5" fill="#9e1b32"/></svg><script>renderAt=t=>{document.querySelector("#object").style.display=t>=1&&t<2?"none":"";return{camera:{x:0,y:0}}};snapshot=()=>({})</script>')
        story=self.root/'combined-story.json';story.write_text(json.dumps({'scenes':[{'id':'gap','clipSeconds':3}]}));output=self.root/'combined-review'
        result=subprocess.run([sys.executable,str(Path(review.__file__)),'--video',str(video),'--story',str(story),'--html',str(document),'--output',str(output)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,2,result.stdout+result.stderr);summary=review.read(output/'summary.json');self.assertEqual(summary['insufficientContentFrames'],30)
        finding=review.read(output/'findings.json')[0];self.assertEqual(finding['emptyEncodedIntervals'][0]['firstFrame'],30);self.assertEqual(finding['emptySourceIntervals'][0]['frames'],30)

if __name__=='__main__':unittest.main()
