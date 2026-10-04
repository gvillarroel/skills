#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Verify genuine D3, responsive complete tiles, capacity, caller labels and actual SVG export."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from playwright.sync_api import sync_playwright

SKILL_ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(SKILL_ROOT/'scripts'))
import build_category_grid
import check_self_contained_html

ORDER=['#9e1b32','#333e48','#4f4f4f','#696969','#828282','#9c9c9c','#b5b5b5','#cfcfcf','#e7e7e7','#363636','#f7f7f7','#1c1c1c','#000000','#ffffff','#6d1222','#e8002a','#ffccd5']
ARTIFACTS: Path
INSPECT=r'''() => {
const svg=document.querySelector('svg'),box=svg.getBoundingClientRect(),hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):value;};
const tiles=[...svg.querySelectorAll('rect[data-category-index]')];
const bounds=node=>{const b=node.getBoundingClientRect(),style=getComputedStyle(node),half=parseFloat(style.strokeWidth)/2;return {x:b.x-half,y:b.y-half,right:b.right+half,bottom:b.bottom+half,width:b.width,height:b.height};};
const marks=tiles.map(node=>{const style=getComputedStyle(node),text=node.parentElement.querySelector('text'),label=getComputedStyle(text),b=bounds(node),t=bounds(text);
return {index:+node.dataset.categoryIndex,id:node.dataset.categoryId,label:text.textContent,extra:node.__data__?.extra??null,fill:hex(style.fill),text:hex(label.fill),stroke:hex(style.stroke),strokeWidth:parseFloat(style.strokeWidth),opacity:+style.opacity,tier:node.parentElement.dataset.outlineTier,bounds:b,textBounds:t,fontSize:parseFloat(label.fontSize),
outside:b.x<box.x-.1||b.y<box.y-.1||b.right>box.right+.1||b.bottom>box.bottom+.1,
labelOutside:t.x<b.x||t.y<b.y||t.right>b.right||t.bottom>b.bottom};});
return {version:window.d3?.version,desc:svg.querySelector('desc')?.textContent,title:svg.querySelector('title')?.textContent,
indexCount:svg.querySelectorAll('[data-category-index]').length,marks,scroll:document.documentElement.scrollWidth>innerWidth,
runtime:document.querySelector('#d3-runtime')?.textContent};
}'''


def luminance(paint: str) -> float:
    channels=[int(paint[index:index+2],16)/255 for index in (1,3,5)]
    return sum((channel/12.92 if channel<=.04045 else ((channel+.055)/1.055)**2.4)*weight for channel,weight in zip(channels,[.2126,.7152,.0722]))


class CategoryGridTests(unittest.TestCase):
    def test_input_and_output_boundaries(self):
        for bad in [[],{},[{}],[123],[{'label':'a','id':'x'},{'label':'b','id':'x'}]]:
            with self.assertRaises(ValueError):build_category_grid.build_document(bad)
        with self.assertRaises(ValueError):build_category_grid.build_document(['a'],canvas='white')
        with self.assertRaises(ValueError):build_category_grid.build_document(['a'],canvas='#007298')
        path=ARTIFACTS/'boundary-data.json';path.write_text('["a"]',encoding='utf-8')
        command=[sys.executable,str(SKILL_ROOT/'scripts/build_category_grid.py'),'--data',str(path),'--output',str(SKILL_ROOT/'illegal-grid.html')]
        result=subprocess.run(command,text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('read-only skill',result.stderr)
        self.assertFalse((SKILL_ROOT/'illegal-grid.html').exists())

    def test_native_canvases_mobile_bounds_labels_and_portable_export(self):
        data=[{'id':f'unit-{index}','label':f'Category {index+1:02}','extra':{'value':index}} for index in range(26)]
        data[3]['label']='Long descriptive category label'
        data[7]['label']='IdentifierWithoutAnyWordSeparators123456789'
        data[11]['label']='Literal </script> & #ffccd5'
        vendor=(SKILL_ROOT/'assets/vendor/d3.v7.9.0.min.js').read_text(encoding='utf-8')
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {'channel':'msedge'}))
            errors=[]
            for canvas in ['#ffffff','#000000']:
                name='white' if canvas=='#ffffff' else 'dark'
                html=ARTIFACTS/f'{name}.html'
                html.write_text(build_category_grid.build_document(data,canvas=canvas,title='Delivery catalogue',description='Complete equal tiles in caller order.'),encoding='utf-8')
                self.assertEqual(check_self_contained_html.check_file(html),[])
                page=browser.new_page(viewport={'width':1440,'height':1000})
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(html.as_uri());page.wait_for_function('window.categoryGridReady===true')
                for width in [1440,390]:
                    page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(120)
                    state=page.evaluate(INSPECT);marks=state['marks'];solids=[paint for paint in ORDER if paint!=canvas]
                    self.assertEqual(state['version'],'7.9.0')
                    self.assertEqual(hashlib.sha256(state['runtime'].encode()).digest(),hashlib.sha256(vendor.encode()).digest())
                    self.assertEqual(state['indexCount'],len(data))
                    self.assertEqual([mark['index'] for mark in marks],list(range(len(data))))
                    self.assertEqual([mark['id'] for mark in marks],[record['id'] for record in data])
                    self.assertEqual([mark['label'] for mark in marks],[record['label'] for record in data])
                    self.assertEqual([mark['extra'] for mark in marks],[record['extra'] for record in data])
                    self.assertEqual([mark['fill'] for mark in marks],[solids[index%len(solids)] for index in range(len(data))])
                    self.assertEqual(state['desc'],'Complete equal tiles in caller order.')
                    self.assertFalse(state['scroll'])
                    self.assertTrue(all(mark['fontSize']>=14 for mark in marks))
                    self.assertTrue(all(not mark['outside'] and not mark['labelOutside'] for mark in marks),marks)
                    self.assertTrue(all(abs(mark['bounds']['width']-marks[0]['bounds']['width'])<.01 and abs(mark['bounds']['height']-marks[0]['bounds']['height'])<.01 for mark in marks))
                    for index,mark in enumerate(marks):
                        expected_text='#000000' if (luminance(mark['fill'])+.05)/.05>=1.05/(luminance(mark['fill'])+.05) else '#ffffff'
                        self.assertEqual(mark['text'],expected_text)
                        self.assertEqual(mark['opacity'],1)
                        if index<len(solids):
                            self.assertEqual((mark['stroke'],mark['strokeWidth'],mark['tier']),('none',0,'solid'))
                        else:
                            self.assertEqual(mark['tier'],'overflow');self.assertGreater(mark['strokeWidth'],0)
                            self.assertGreaterEqual((max(luminance(mark['stroke']),luminance(mark['fill']))+.05)/(min(luminance(mark['stroke']),luminance(mark['fill']))+.05),3)
                    capture=page.locator('svg').evaluate(build_category_grid.CAPTURE)
                    svg=ARTIFACTS/f'{name}-{width}.svg';svg.write_text(capture['markup'],encoding='utf-8')
                    (ARTIFACTS/f'{name}-{width}-allocation.json').write_text(json.dumps(capture['allocation'],indent=2)+'\n',encoding='utf-8')
                    self.assertEqual(capture['allocation']['labels'],[record['label'] for record in data])
                    self.assertEqual([style['fill'] for style in capture['allocation']['styles']],[mark['fill'] for mark in marks])
                    exported=browser.new_page(viewport={'width':width,'height':1000});exported.goto(svg.as_uri())
                    export_state=exported.evaluate(INSPECT)
                    self.assertTrue(all(not mark['outside'] and not mark['labelOutside'] for mark in export_state['marks']))
                    self.assertEqual([(mark['label'],mark['fill'],mark['text'],mark['stroke'],mark['strokeWidth']) for mark in export_state['marks']],[(mark['label'],mark['fill'],mark['text'],mark['stroke'],mark['strokeWidth']) for mark in marks])
                    exported.close();page.locator('svg').screenshot(path=str(ARTIFACTS/f'{name}-{width}.png'))
                page.close()
            self.assertEqual(errors,[])
            browser.close()

    def test_exact_cli_paths_and_cs2(self):
        data=ARTIFACTS/'caller-data.json';data.write_text(json.dumps(['One','Two','Three','Four','Five','Six','Seven']),encoding='utf-8')
        html=ARTIFACTS/'exact.catalogue.html';svg=ARTIFACTS/'exact.catalogue.svg';allocation=ARTIFACTS/'exact.allocation.json'
        result=subprocess.run([sys.executable,str(SKILL_ROOT/'scripts/build_category_grid.py'),'--data',str(data),'--output',str(html),'--svg-output',str(svg),'--allocation-output',str(allocation),'--colorset','colorset2','--force'],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertTrue(html.exists() and svg.exists() and allocation.exists())
        self.assertEqual(check_self_contained_html.check_file(html),[])
        record=json.loads(allocation.read_text(encoding='utf-8'))
        self.assertEqual(record['labels'],['One','Two','Three','Four','Five','Six','Seven'])
        self.assertTrue(any(style['fill']=='#007298' for style in record['styles']))
        self.assertIn('<desc',svg.read_text(encoding='utf-8'))


def main() -> int:
    global ARTIFACTS
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--artifacts',type=Path,required=True);args=parser.parse_args()
    ARTIFACTS=args.artifacts.resolve()
    if ARTIFACTS.is_relative_to(SKILL_ROOT):parser.error('Artifacts must be outside the skill resource')
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CategoryGridTests))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
