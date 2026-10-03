#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent allocation/contrast and renderer regression checks."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

class SolidStyle(unittest.TestCase):
    def test_python_capacity_and_text(self):
        for skill in ['mermaid','plantuml-colorset-renderer','echarts-animated-svg']:
            m=load(skill,ROOT/'skills'/skill/'scripts/palette_paints.py')
            for colorset in ['colorset1','colorset2']:
                for canvas in ['#ffffff','#f7f7f7','#9e1b32']:
                    colors=m.solid_colors(colorset,canvas)
                    self.assertEqual(colors,[c for c in m.COLORSETS[colorset]['solidSequence'] if c!=canvas])
                    self.assertEqual(set(colors),set(m.COLORSETS[colorset]['allowed'])-{canvas})
                    styles=[m.solid_style(i,colorset,canvas) for i in range(len(colors)+5)]
                    self.assertTrue(all(s['strokeWidth']==0 and s['stroke']=='none' for s in styles[:len(colors)]))
                    self.assertTrue(all(s['strokeWidth']>0 and s['overflow'] for s in styles[len(colors):]))
                    for s in styles:self.assertEqual(s['text'],m.COLORSETS[colorset]['textOnFill'][s['fill']])
            for colorset in ['colorset1','colorset2']:
                for index in [len(m.solid_colors(colorset)),256,1296,5000]:
                    paint=m.solid_style(index,colorset)
                    left,right=m.relative_luminance(paint['fill']),m.relative_luminance(paint['stroke'])
                    self.assertGreaterEqual((max(left,right)+.05)/(min(left,right)+.05),3)
                    self.assertIn(paint['strokeWidth'],[1,2,3])
            self.assertEqual(m.readable_text('#e77204'),'#000000')
            self.assertEqual(m.readable_text('#45842a'),'#000000')
            self.assertEqual(m.readable_text('#007298'),'#ffffff')

    def test_mermaid_class_definitions(self):
        sys.path.insert(0,str(ROOT/'skills/mermaid/scripts'))
        m=load('mermaid_styler',ROOT/'skills/mermaid/scripts/style_mermaid_directory.py')
        for colorset in ['colorset1','colorset2']:
            fills=[]
            for c in m.COLOR_CLASS_ORDER:
                style=m.class_style(colorset,c)
                self.assertIn('stroke:none',style);self.assertIn('stroke-width:0px',style)
                fills.append(style.split('fill:')[1].split(',')[0])
            self.assertEqual(len(fills),len(set(fills)))

    def test_native_kanban_sections_and_animation_opacity(self):
        import xml.etree.ElementTree as ET
        sys.path.insert(0,str(ROOT/'skills/mermaid/scripts'))
        from mermaid_animation.solid import native_solid_presentation
        from palette_paints import solid_colors, readable_text
        for colorset in ['colorset1','colorset2']:
            colors=solid_colors(colorset)
            root=ET.Element('svg',{'aria-roledescription':'kanban'})
            connector=ET.SubElement(root,'path',{'class':'edge','fill':'none','stroke':'#696969','stroke-width':'2'})
            original=dict(connector.attrib)
            for i in range(len(colors)+1):
                section=ET.SubElement(root,'g',{'class':f'cluster section-{i+1}'})
                ET.SubElement(section,'rect')
                card=ET.SubElement(root,'g',{'class':'node','id':f'card-{i}'})
                ET.SubElement(card,'rect',{'style':'opacity:0.7'})
                ET.SubElement(card,'text').text=f'Card {i}'
            native_solid_presentation(root,colorset)
            native_solid_presentation(root,colorset)
            self.assertEqual(connector.attrib,original)
            for role in ['node','cluster']:
                groups=[g for g in root if role in g.get('class','').split()]
                for i,g in enumerate(groups):
                    paint=g[0].get('style','')
                    self.assertIn(f'fill:{colors[i%len(colors)]} !important',paint)
                    self.assertNotIn(';opacity:1 !important',paint)
                    self.assertEqual(paint.count('fill-opacity:'),1)
                    if i<len(colors):self.assertIn('stroke:none !important',paint)
                    else:self.assertEqual(g[0].get('data-colorset-overflow'),'true')
                    if role=='node':self.assertIn(readable_text(colors[i%len(colors)]),g[1].get('style',''))

    def test_javascript_templates_and_meaningful_lines(self):
        for skill in ['echarts-animated-svg','slidev-echarts']:
            script='''import {solidColors,solidCategoryStyle,prepareColorsetOption,readableText} from './skills/SKILL/assets/templates/echarts-colorsets.mjs';
import assert from 'node:assert/strict';
for (const cs of ['colorset1','colorset2']) {
 const colors=solidColors(cs), styles=Array.from({length:colors.length+2},(_,i)=>solidCategoryStyle(i,cs));
 assert.equal(new Set(styles.slice(0,colors.length).map(s=>s.color)).size,colors.length);
 assert(styles.slice(0,colors.length).every(s=>s.borderWidth===0));assert(styles.slice(colors.length).every(s=>s.borderWidth>0&&s.overflow));
}
for (const cs of ['colorset1','colorset2']) for (const canvas of ['#ffffff','#f7f7f7','#9e1b32']) {
 const colors=solidColors(cs,canvas);
 const prepared=prepareColorsetOption({backgroundColor:canvas,series:[{name:'Relationship series',type:'graph',label:{position:'inside'},data:Array.from({length:colors.length+1},(_,i)=>({id:`node-${i}`}))}]},cs);
 assert.deepEqual(prepared.color,colors);assert(prepared.series[0].data.every(n=>n.itemStyle.color!==canvas));
 assert.deepEqual(prepared.series[0].data.slice(0,colors.length).map(n=>n.itemStyle.color),colors);
 assert(prepared.series[0].data.slice(0,colors.length).every(n=>n.itemStyle.borderWidth===0));
 assert(prepared.series[0].data.at(-1).itemStyle.borderWidth>0);
}
assert.equal(readableText('#e77204'),'#000000'); assert.equal(readableText('#007298'),'#ffffff');
const option=prepareColorsetOption({series:[{type:'graph',label:{position:'inside',show:true},lineStyle:{color:'#696969',width:3},data:[{name:'A'},{name:'B'},{name:'C'}],links:[{source:'A',target:'B'}]}]},'colorset2');
assert.equal(option.series[0].lineStyle.width,3);assert.equal(option.series[0].data[0].itemStyle.color,'#9e1b32'); assert.equal(option.series[0].data[1].itemStyle.color,'#007298');
assert(option.series[0].data.every(n=>n.itemStyle.borderWidth===0));
const explicit=prepareColorsetOption({colorsetPresentation:'source',series:[{type:'bar',itemStyle:{color:'#cdf3ff',borderWidth:3}}]},'colorset2');assert.equal(explicit.series[0].itemStyle.borderWidth,3);
console.log('JavaScript allocation and semantic lines pass');'''.replace('SKILL',skill)
            result=subprocess.run(['node','--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
