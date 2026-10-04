#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regress category priority, opacity and native directional inheritance."""
import json
from pathlib import Path
import subprocess

SKILL = Path(__file__).resolve().parents[1]
MODULE = (SKILL / "assets/templates/echarts-colorsets.mjs").as_uri()
TEST = r'''
import assert from 'node:assert/strict';
const {colorsets,solidColors,solidCategoryStyle,contrastSafeArrowStyle:safe,prepareColorsetOption:prepare,colorsetTheme,insetCartesianArrowRoutes:inset}=await import(MODULE);
const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const L=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
const ratio=(a,b)=>(Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05);
let cases=0;
// Category ordering must agree with the standalone contract and survive native options.
const contract=CONTRACT;
for(const set of ['colorset1','colorset2'])for(const canvas of ['#ffffff','#f7f7f7','#000000','#9e1b32']){
 const expected=contract[set].solidSequence.filter(fill=>fill!==canvas);
 assert.deepEqual(solidColors(set,canvas),expected);
 const data=expected.map((_,index)=>({id:`node-${String(index).padStart(2,'0')}`,name:`node-${String(index).padStart(2,'0')}`}));
 const rendered=prepare({backgroundColor:canvas,series:[{type:'graph',data}]},set,data.map(node=>node.id)).series[0].data;
 for(let index=0;index<expected.length;index++){
  const item=rendered[index],style=solidCategoryStyle(index,set,canvas);
  assert.equal(item.itemStyle.color,expected[index]);assert.equal(item.itemStyle.borderWidth,0);
  assert.equal(item.label.color,contract[set].textOnFill[expected[index]]);
  assert.equal(style.color,expected[index]);assert.equal(style.overflow,false);
 }
assert.equal(solidCategoryStyle(expected.length,set,canvas).overflow,true);
}
const boxes=prepare({series:[{type:'boxplot',data:[[1,2,3,4,5]]},{type:'boxplot',data:[[2,3,4,5,6]]}]},'colorset1').series;
assert.equal(boxes[0].itemStyle.color,'#9e1b32');assert.equal(boxes[1].itemStyle.color,'#333e48');
assert.equal(prepare({series:[{type:'boxplot',data:[[1,2,3,4,5]]}]},'colorset2').series[0].itemStyle.color,'#007298');
assert.equal(prepare({series:[{type:'boxplot',itemStyle:{color:'#4f4f4f'},data:[[1,2,3,4,5]]}]},'colorset1').series[0].itemStyle.color,'#4f4f4f');
for(const set of ['colorset1','colorset2'])for(const bg of colorsets[set])for(const color of ['#cfcfcf','#9e1b32','#ffffff','#000000']){
 const style=safe({color,opacity:.25,width:.2},set,bg),raw=rgb(style.color),back=rgb(bg),paint=raw.map((v,i)=>v*style.opacity+back[i]*(1-style.opacity));
 assert(ratio(paint,back)>=3);assert(colorsets[set].includes(style.color));assert(style.width>=1.5);cases++;
}
// A just-failing ratio must not pass after rounding the composite to 8-bit hex.
let low=0,high=1;
for(let i=0;i<60;i++){const mid=(low+high)/2;if(ratio([255*(1-mid),255*(1-mid),255*(1-mid)],[255,255,255])<3)low=mid;else high=mid;}
assert.equal(safe({color:'#000000',opacity:low-1e-8},'colorset1').opacity,1);
assert.equal(safe({color:'rgba(0,0,0,25%)'},'colorset1').color,'#000000');
assert.equal(safe({color:'rgba(0,0,0,25%)'},'colorset1').opacity,1);
assert.equal(safe({color:'rgba(0,0,0,125%)'},'colorset1').opacity,1);
assert.equal(safe({color:'transparent'},'colorset1').opacity,1);
assert.throws(()=>safe({color:{type:'linear',colorStops:[]}},'colorset1'),/known solid color/);
assert.throws(()=>safe({color:'var(--arrow-color)'},'colorset1'),/known solid color/);
assert.throws(()=>safe({color:'#000000'},'colorset1',{type:'linear',colorStops:[]}),/known solid color/);
assert.throws(()=>prepare({backgroundColor:{type:'linear',colorStops:[]},series:[{type:'graph',edgeSymbol:['none','arrow'],data:[]}]},'colorset1'),/known solid color/);
assert.throws(()=>prepare({backgroundColor:'var(--canvas)',series:[{type:'graph',edgeSymbol:['none','arrow'],data:[]}]},'colorset1'),/known solid color/);
for(const set of ['colorset1','colorset2']){
 const graph=prepare({series:[{type:'graph',edgeSymbol:['none','arrow'],lineStyle:{color:'#cfcfcf',opacity:.25},blur:{lineStyle:{opacity:.1}},
 data:[{id:'A',name:'A'},{id:'B',name:'B'}],links:[{source:'A',target:'B',lineStyle:{color:'source',opacity:.2}}]}]},set);
 const edge=graph.series[0].links[0];assert(edge.lineStyle.opacity===1);assert(edge.blur.lineStyle.opacity===1);assert(graph.series[0].data.every(n=>n.itemStyle.borderWidth===0));
 const routes=prepare({series:[{type:'lines',effect:{show:true,symbol:'arrow',color:'#cfcfcf'},lineStyle:{opacity:.2},data:[{coords:[[0,0],[1,1]]}]},
 {type:'line',markLine:{lineStyle:{color:'#cfcfcf',opacity:.25},data:[{xAxis:1}]}}]},set);
 assert(ratio(rgb(routes.series[0].effect.color),[255,255,255])>=3);assert(routes.series[0].lineStyle.opacity===1);assert(routes.series[1].markLine.lineStyle.opacity===1);
 const individual=prepare({series:[{type:'lines',symbol:'none',effect:{show:true,symbol:'circle'},lineStyle:{color:'#cfcfcf',opacity:.25},data:[{coords:[[0,0],[1,1]],effect:{symbol:'arrow',color:'#cfcfcf'}}]}]},set).series[0].data[0];
 assert(individual.lineStyle.opacity===1);assert(ratio(rgb(individual.effect.color),[255,255,255])>=3);
 const disabledEdge=prepare({series:[{type:'lines',effect:{show:true,symbol:'arrow'},data:[{coords:[[0,0],[1,1]],effect:{show:false,color:'#cfcfcf'}}]}]},set).series[0].data[0];
 assert.equal(disabledEdge.effect.show,false);assert(ratio(rgb(disabledEdge.effect.color),[255,255,255])>=3);
 const nativeAlpha=prepare({series:[{type:'lines',effect:{show:true,symbol:'arrow',color:'#000000',opacity:.1},data:[{coords:[[0,0],[1,1]],effect:{color:'#000000',opacity:.1}}]}]},set).series[0];
 assert.equal(nativeAlpha.effect.opacity,1);assert.equal(nativeAlpha.data[0].effect.opacity,1);
 const terminal=prepare({series:[{type:'line',markLine:{symbol:'none',lineStyle:{color:'#cfcfcf',opacity:.25},data:[[{coord:[0,0],symbol:'none'},{coord:[1,1],symbol:'arrow'}]]}}]},set).series[0].markLine;
 assert.equal(terminal.symbol,'none');assert.equal(terminal.lineStyle.opacity,1);assert.equal(terminal.data[0][1].symbol,'arrow');assert(ratio(rgb(terminal.data[0][1].lineStyle.color),[255,255,255])>=3);
 const source=prepare({colorsetPresentation:'source',series:[{type:'graph',edgeSymbol:['none','arrow'],lineStyle:{color:'#cfcfcf',opacity:.25},data:[]}]},set);
 assert.equal(source.series[0].lineStyle.opacity,.25);
 for(const type of ['graph','tree','lines'])assert(ratio(rgb(colorsetTheme(set)[type].lineStyle.color),[255,255,255])>=3);
}
const original={series:[{type:'lines',coordinateSystem:'cartesian2d',symbol:['none','arrow'],lineStyle:{curveness:.18},data:[{coords:[[0,0],[20,10]]}]}]};
const chart={getOption:()=>({xAxis:[{type:'value'}],yAxis:[{type:'value'}]}),convertToPixel:(_,p)=>p.map(v=>v*10),convertFromPixel:(_,p)=>p.map(v=>v/10)};
const trimmed=inset(original,chart,7),end=trimmed.series[0].data[0].coords[1];
assert.deepEqual(original.series[0].data[0].coords,[[0,0],[20,10]]);
assert(Math.abs(Math.hypot((20-end[0])*10,(10-end[1])*10)-7)<1e-10);
assert.deepEqual(inset(original,chart,7),trimmed);
assert.throws(()=>inset(original,{...chart,getOption:()=>({xAxis:[{type:'category'}]})},7),/continuous/);
assert.throws(()=>inset(original,chart,100),/too short/);
console.log(JSON.stringify({passed:true,categoryPriority:true,canvasExclusion:true,solidCapacityBeforeOutline:true,paletteBackingCases:cases,thresholdUnrounded:true,edgeStates:true,movingEffects:true,defaultMarkLine:true,sourcePreserved:true,terminalPixels:true,originalCoordinatesPreserved:true,resizeIdempotent:true,unsupportedGeometryRejected:true}));
'''


def main():
    source = TEST.replace("import(MODULE)", "import(" + json.dumps(MODULE) + ")")
    contract = json.loads((SKILL / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    source = source.replace("CONTRACT", json.dumps(contract))
    result = subprocess.run(["node", "--input-type=module", "-e", source],
                            capture_output=True, text=True, encoding="utf-8")
    print(result.stdout.strip())
    if result.returncode:
        print(result.stderr.strip())
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
