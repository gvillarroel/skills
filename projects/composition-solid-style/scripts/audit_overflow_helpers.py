#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify all five local helper copies with independent WCAG calculations."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,(.2126,.7152,.0722)))
def contrast(a,b):
    first,second=sorted((luminance(a),luminance(b)))
    return (second+.05)/(first+.05)
rows=[]
for skill in ['compose-synchronized-svg','diagram-composition','usefulcharts-style','video','manim-svg-video']:
    spec=importlib.util.spec_from_file_location(skill.replace('-','_'),ROOT/'skills'/skill/'scripts/palette_contract.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    checked=0
    for colorset in helper.COLORSETS:
        for canvas in ['#ffffff','#000000','#9e1b32']:
            colors=helper.solid_colors(colorset,canvas);capacity=len(colors)
            assert len(set(colors))==capacity
            assert set(colors)==set(helper.COLORSETS[colorset]['allowed'])-{canvas}
            for cycle in [0,1,2,10,30,100,219,10000]:
                for slot in range(capacity):
                    style=helper.category_style(cycle*capacity+slot,colorset,canvas)
                    checked+=1
                    expected=max(['#000000','#ffffff'],key=lambda color:contrast(color,style['fill']))
                    assert style['text']==expected,(skill,colorset,canvas,cycle,slot,style)
                    if not cycle:
                        assert style['stroke']=='none' and style['strokeWidth']==0
                    else:
                        assert style['stroke']!=style['fill']
                        assert contrast(style['stroke'],style['fill'])>=3
                        assert style['strokeWidth'] in [1,2,3]
                        assert style['dash'] in ['', '6 3','2 3']
                    if cycle==10000:assert style['overflowExhausted']
    rows.append({'skill':skill,'checkedStyles':checked,'passed':True})
report={'passed':True,'copies':rows,'totalStyles':sum(r['checkedStyles'] for r in rows)}
out=ROOT/'projects/composition-solid-style/artifacts/overflow-helpers-final.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
