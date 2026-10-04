#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify real native graph head clearance without changing nodes or options."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


TEST = r'''
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(path.resolve('graph-arrow-test.cjs'));
const echarts=require(ECHARTS),{chromium}=require(PLAYWRIGHT);
const {prepareColorsetOption,normalizeSvgPaints,insetGraphArrowRoutes:inset}=await import(MODULE);
const output=OUTPUT;fs.mkdirSync(output,{recursive:true});
const stableSvg=svg=>{const names=new Map();return svg.replace(/\bzr\d+-cls-\d+\b/g,name=>{if(!names.has(name))names.set(name,'native-cls-'+names.size);return names.get(name)});};
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1100,height:1300}});
const rows=[];
for (const set of ['colorset1','colorset2']) for (const canvas of ['#ffffff','#1c1c1c'])
for (const symbol of ['rect','roundRect','circle']) for (const curved of [false,true]) for (const both of [false,true]) {
  const id=[set,canvas.slice(1),symbol,curved?'curve':'straight',both?'both':'end'].join('-');
  const option=prepareColorsetOption({animation:false,backgroundColor:canvas,series:[{
    type:'graph',layout:'none',symbol,symbolSize:[72,32],edgeSymbol:both?['arrow','arrow']:['none','arrow'],edgeSymbolSize:14,
    label:{show:true,position:'inside'},
    edgeLabel:{show:true,formatter:'Route',position:both?'start':'middle'},
    data:[{id:'a',name:'Source',x:80,y:100},{id:'b',name:'Target',x:270,y:curved?180:100},{id:'c',name:'Other',x:440,y:280}],
    links:[{source:'a',target:'b'}],lineStyle:{color:'#696969',opacity:.25,curveness:curved?.22:0}
  }]},set,['a','b','c']);
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360});
  chart.setOption(option);
  for (const [frame,size] of [[640,360],[960,540],[640,360]].entries()) {
    if (frame===2) chart.setOption({...option,series:[{...option.series[0],data:option.series[0].data.map((node,index)=>({...node,x:node.x+(index===1?30:0),y:node.y+(index===1?12:0)}))}]});
    chart.resize({width:size[0],height:size[1]});
    const optionBefore=JSON.stringify(chart.getOption()),before=normalizeSvgPaints(chart.renderToSVGString(),set);
    const first=inset(chart,3),after=normalizeSvgPaints(chart.renderToSVGString(),set),second=inset(chart,3);
    assert.equal(second.adjustedEdges,0,id+' repeated call must not move glyphs');
    assert.equal(stableSvg(normalizeSvgPaints(chart.renderToSVGString(),set)),stableSvg(after),id+' repeated geometry and paint must be byte-stable after normalizing native generated class IDs');
    assert.equal(JSON.stringify(chart.getOption()),optionBefore,id+' native option and data must be unchanged');
    const stem=id+'-'+size.join('x')+(frame===2?'-updated':'');
    fs.writeFileSync(path.join(output,stem+'.before.svg'),before);fs.writeFileSync(path.join(output,stem+'.after.svg'),after);
    await page.setContent('<div id="before">'+before+'</div><div id="after">'+after+'</div>');
    const proof=await page.evaluate(({canvas})=>{
      const snapshot=id=>{
        const svg=document.querySelector('#'+id+' svg');
        const bounds=element=>{const b=element.getBBox(),m=element.getCTM(),points=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f}));const x=Math.min(...points.map(p=>p.x)),y=Math.min(...points.map(p=>p.y));return {x,y,width:Math.max(...points.map(p=>p.x))-x,height:Math.max(...points.map(p=>p.y))-y}};
        const nodes=[...svg.querySelectorAll('[ecmeta_series_index="0"][ecmeta_data_index]')].filter(el=>['path','circle','ellipse','rect'].includes(el.tagName)&&getComputedStyle(el).fill!=='none'&&!el.getAttribute('d')?.startsWith('M0 0L'));
        const heads=[...svg.querySelectorAll('path[d^="M0 0L"]')];
        const gap=(a,b)=>Math.hypot(Math.max(b.x-a.x-a.width,a.x-b.x-b.width,0),Math.max(b.y-a.y-a.height,a.y-b.y-b.height,0));
        const L=channels=>channels.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
        const bg=L([1,3,5].map(i=>parseInt(canvas.slice(i,i+2),16)));
        const source=el=>[...el.attributes].filter(a=>a.name!=='class').map(a=>[a.name,a.value]);
        return {nodes:nodes.map(el=>({index:el.getAttribute('ecmeta_data_index'),source:source(el),bounds:bounds(el),fill:getComputedStyle(el).fill,stroke:getComputedStyle(el).stroke})),
          labels:[...svg.querySelectorAll('text')].map(el=>({text:el.textContent,source:source(el),bounds:bounds(el),fill:getComputedStyle(el).fill})),
          heads:heads.map(el=>{const fill=getComputedStyle(el).fill,value=L(fill.match(/[\d.]+/g).slice(0,3).map(Number));return {bounds:bounds(el),fill,minimumNodeGap:Math.min(...nodes.map(node=>gap(bounds(el),bounds(node)))),contrast:(Math.max(value,bg)+.05)/(Math.min(value,bg)+.05)}})};
      };
      return {before:snapshot('before'),after:snapshot('after')};
    },{canvas});
    assert.deepEqual(proof.after.nodes,proof.before.nodes,id+' actual node paint and bounds changed');
    assert.deepEqual(proof.after.labels,proof.before.labels,id+' labels or positions changed');
    assert.equal(proof.after.heads.length,both?2:1);
    assert.deepEqual(proof.after.heads.map(h=>h.fill),proof.before.heads.map(h=>h.fill),id+' arrow paint changed');
    for (const head of proof.after.heads) {assert(head.minimumNodeGap>=2,id+' full head envelope is not clear: '+JSON.stringify(head));assert(head.contrast>=3,id+' head contrast failed');}
    rows.push({id,size,updatedOption:frame===2,first,repeat:second,proof});
    if (symbol==='rect'&&!curved&&!both&&frame===0) await page.screenshot({path:path.join(output,id+'.png'),fullPage:true});
  }
  chart.dispose();
}
for (const alteration of [{symbol:'diamond'},{symbolRotate:15},{layout:'circular'},{symbolSize:[800,240]}]) {
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360});
  chart.setOption({animation:false,series:[{type:'graph',layout:'none',symbol:'rect',symbolSize:[72,32],edgeSymbol:['none','arrow'],data:[{id:'a',x:0,y:0},{id:'b',x:100,y:0}],links:[{source:'a',target:'b'}],...alteration}]});
  const before=chart.renderToSVGString(),option=JSON.stringify(chart.getOption());
  assert.throws(()=>inset(chart,3),/supports native|axis-aligned|fixed layout|too short|blocked/);
  assert.equal(stableSvg(chart.renderToSVGString()),stableSvg(before),'rejected native graph was changed');
  assert.equal(JSON.stringify(chart.getOption()),option,'rejected option was changed');
  chart.dispose();
}
await browser.close();
const report={ok:true,echartsVersion:echarts.version,cases:rows.length,minimumHeadClearance:Math.min(...rows.flatMap(row=>row.proof.after.heads.map(head=>head.minimumNodeGap))),minimumHeadContrast:Math.min(...rows.flatMap(row=>row.proof.after.heads.map(head=>head.contrast))),nodeDataGeometryPaintPreserved:true,nodeAndEdgeLabelsPreserved:true,repeatGeometryPaintStable:true,generatedClassIdsNormalized:true,resizeAndOptionUpdateRecomputed:true,rejectedGeometryUnchanged:true,rows};
fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,rows:undefined}));
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--echarts-package', type=Path, required=True)
    parser.add_argument('--playwright-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    values = {'ECHARTS': str(args.echarts_package.resolve()),
              'PLAYWRIGHT': str(args.playwright_package.resolve()),
              'MODULE': (skill/'assets/templates/echarts-colorsets.mjs').as_uri(),
              'OUTPUT': str(args.output.resolve())}
    source = TEST
    for token, value in values.items():
        source = source.replace(token, json.dumps(value))
    result = subprocess.run(['node', '--input-type=module', '-e', source],
                            capture_output=True, text=True, encoding='utf-8')
    print(result.stdout.strip())
    if result.returncode:
        print(result.stderr.strip())
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
