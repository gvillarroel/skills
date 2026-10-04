#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify transferred native boxplot medians in SVG SSR and browser Canvas."""
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
const require=createRequire(path.resolve('boxplot-test.cjs'));
const echarts=require(ECHARTS),{chromium}=require(PLAYWRIGHT);
const helper=await import(MODULE),{prepareColorsetOption,normalizeSvgPaints,qualifyBoxplotMedians:qualify}=helper;
fs.mkdirSync(OUTPUT,{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1100,height:900}}),rows=[];
const values=[[4,9,14,20,28],[4,9,9,20,28],[4,14,14,14,28],[4,9,14,20,40]];
const makeOption=(canvas,horizontal)=>({animation:false,backgroundColor:canvas,grid:{left:60,right:25,top:25,bottom:45},xAxis:horizontal?{type:'value',min:0,max:30}:{type:'category',data:['Normal','Boundary','Zero IQR','Clipped']},yAxis:horizontal?{type:'category',data:['Normal','Boundary','Zero IQR','Clipped']}:{type:'value',min:0,max:30},series:[{id:'boxes',type:'boxplot',data:values,emphasis:{itemStyle:{color:'#e7e7e7',opacity:1}},select:{itemStyle:{color:'#4f4f4f',opacity:1}},blur:{itemStyle:{opacity:.15}}}]});
const nativeSnapshot=chart=>{const rows=[];chart.getModel().eachSeriesByType('boxplot',series=>series.getData().eachItemGraphicEl((el,index)=>rows.push({index,points:el.shape.points.map(p=>[...p]),style:{...el.style},transform:[el.x,el.y,el.rotation,el.scaleX,el.scaleY]})));return rows};
for(const set of ['colorset1','colorset2'])for(const canvas of ['#ffffff','#1c1c1c'])for(const horizontal of [false,true]) {
  const id=[set,canvas.slice(1),horizontal?'horizontal':'vertical'].join('-'),chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360});
  chart.setOption(prepareColorsetOption(makeOption(canvas,horizontal),set));
  for(const state of ['normal','emphasis','select','blur','resize','update']) {
    chart.dispatchAction({type:'downplay',seriesIndex:0});chart.dispatchAction({type:'unselect',seriesIndex:0});
    if(state==='emphasis')chart.dispatchAction({type:'highlight',seriesIndex:0,dataIndex:0});
    if(state==='select')chart.dispatchAction({type:'select',seriesIndex:0,dataIndex:0});
    if(state==='blur') {const el=chart.getModel().getSeriesByIndex(0).getData().getItemGraphicEl(0);el.useState('blur');}
    if(state==='resize')chart.resize({width:960,height:540});
    if(state==='update')chart.setOption({series:[{id:'boxes',data:[values[0],values[2]]}]});
    chart.getZr().flush();
    const option=JSON.stringify(chart.getOption()),native=nativeSnapshot(chart),before=normalizeSvgPaints(chart.renderToSVGString(),set);
    const first=qualify(chart,echarts,set),after=normalizeSvgPaints(chart.renderToSVGString(),set),repeat=qualify(chart,echarts,set);
    assert.equal(repeat.newMedians,0);assert.equal(JSON.stringify(chart.getOption()),option);assert.deepEqual(nativeSnapshot(chart),native);
    assert.equal(first.qualifiedBoxes,state==='update'?2:4);
    fs.writeFileSync(path.join(OUTPUT,id+'-'+state+'.svg'),after);
    await page.setContent('<div>'+after+'</div>');
    const proof=await page.evaluate(medians=>{
      const numeric=/^M\s*([\d.+-]+)[ ,]([\d.+-]+)L\s*([\d.+-]+)[ ,]([\d.+-]+)$/;
      const L=paint=>(paint.startsWith('#')?[1,3,5].map(i=>parseInt(paint.slice(i,i+2),16)):paint.match(/[\d.]+/g).slice(0,3).map(Number)).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
      return medians.map(median=>{
        const paths=[...document.querySelectorAll('svg path[data-native-median="'+median.seriesIndex+':'+median.dataIndex+'"]')].filter(el=>{const match=el.getAttribute('d')?.match(numeric);return match&&match.slice(1).map(Number).every((v,i)=>Math.abs(v-median.ends.flat()[i])<=.051)&&el.getAttribute('stroke')===median.svgInk});
        const a=L(median.svgInk),b=L(median.svgBacking);
        return {matchingSegments:paths.length,ink:median.svgInk,contrast:(Math.max(a,b)+.05)/(Math.min(a,b)+.05),hasClip:paths[0]?.closest('[clip-path]')!==null};
      });
    },first.medians);
    for(const mark of proof){assert.equal(mark.matchingSegments,1,'native median must be transferred exactly once');assert(mark.contrast>=4.5);}
    if(state==='normal') {
      const face=first.medians[0].face;await page.mouse.move(face.x+face.width/2,face.y+face.height/2);
      const hovered=await page.evaluate(()=>{const median=document.querySelector('[data-native-median="0:0"]'),body=document.querySelector('[data-native-box="0:0"]');return {stroke:getComputedStyle(median).stroke,fill:getComputedStyle(body).fill}});
      assert.equal(hovered.stroke,first.medians[0].hoverSvgInk==='#ffffff'?'rgb(255, 255, 255)':'rgb(0, 0, 0)','exported native SSR hover median ink did not follow body');
      await page.mouse.move(1050,850);
    }
    for(const median of first.medians)assert.deepEqual(median.ends,native[median.dataIndex].points.slice(-2));
    rows.push({id,state,first,repeat,proof,optionAndNativeGeometryPaintPreserved:true});
    if(state==='normal'){fs.writeFileSync(path.join(OUTPUT,id+'.before.svg'),before);await page.screenshot({path:path.join(OUTPUT,id+'.png'),fullPage:true});}
  }
  chart.setOption({series:[]},{replaceMerge:['series']});const cleared=qualify(chart,echarts,set);assert.equal(cleared.qualifiedBoxes,0);assert.equal(cleared.removedMedians,2);chart.dispose();
}
await page.setContent('<div id="chart" style="width:640px;height:360px"></div>');
await page.addScriptTag({path:path.join(ECHARTS,'dist/echarts.js')});
await page.addScriptTag({content:fs.readFileSync(new URL(MODULE),'utf8').replace(/\bexport\s+/g,'')+'\nwindow.medianHelpers={prepareColorsetOption,qualifyBoxplotMedians,colorsets};'});
const canvasRows=[];
for(const set of ['colorset1','colorset2'])for(const canvas of ['#ffffff','#1c1c1c'])for(const horizontal of [false,true]) {
  const result=await page.evaluate(({set,option})=>{
    const chart=echarts.init(document.querySelector('#chart'),null,{renderer:'canvas',devicePixelRatio:1});chart.setOption(medianHelpers.prepareColorsetOption(option,set));
    const optionBefore=JSON.stringify(chart.getOption()),states=[];
    for(const state of ['normal','emphasis','select','resize','update']) {
      chart.dispatchAction({type:'downplay',seriesIndex:0});chart.dispatchAction({type:'unselect',seriesIndex:0});
      if(state==='emphasis')chart.dispatchAction({type:'highlight',seriesIndex:0,dataIndex:0});
      if(state==='select')chart.dispatchAction({type:'select',seriesIndex:0,dataIndex:0});
      if(state==='resize')chart.resize({width:960,height:540});
      if(state==='update')chart.setOption({series:[{id:'boxes',data:[[4,9,14,20,28]]}]});
      const currentOption=JSON.stringify(chart.getOption()),report=medianHelpers.qualifyBoxplotMedians(chart,echarts,set),repeat=medianHelpers.qualifyBoxplotMedians(chart,echarts,set);
      const surface=chart.getZr().painter.getRenderedCanvas({pixelRatio:1}),context=surface.getContext('2d');
      const L=channels=>channels.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
      const pixels=report.medians.map(mark=>{const center=mark.ends[0].map((v,i)=>(v+mark.ends[1][i])/2),x=Math.floor(center[0])-2,y=Math.floor(center[1])-2,bytes=context.getImageData(x,y,5,5).data,backing=L(mark.backing.match(/[\d.]+/g).slice(0,3).map(Number));let strongestPixelContrast=1;for(let i=0;i<bytes.length;i+=4){const px=x+i/4%5+.5,py=y+Math.floor(i/20)+.5;if(!mark.degenerateFace&&(px<mark.face.x||px>mark.face.x+mark.face.width||py<mark.face.y||py>mark.face.y+mark.face.height))continue;const ink=L([bytes[i],bytes[i+1],bytes[i+2]]);strongestPixelContrast=Math.max(strongestPixelContrast,(Math.max(ink,backing)+.05)/(Math.min(ink,backing)+.05));}return {dataIndex:mark.dataIndex,center,ink:mark.ink,strongestPixelContrast,degenerateFace:mark.degenerateFace}});
      states.push({state,report,repeat,pixels,optionPreserved:JSON.stringify(chart.getOption())===currentOption});
    }
    chart.dispose();return {states};
  },{set,option:makeOption(canvas,horizontal)});
  for(const state of result.states){assert(state.optionPreserved);assert.equal(state.repeat.newMedians,0);for(const pixel of state.pixels)assert(pixel.strongestPixelContrast>=3,'Canvas median is invisible: '+JSON.stringify({set,canvas,horizontal,state:state.state,...pixel}));}
  canvasRows.push({set,canvas,horizontal,...result});
}
const paletteBoundaryRows=await page.evaluate(()=>{
  const marks=[],L=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  for(const fill of medianHelpers.colorsets.colorset1)for(const canvas of ['#ffffff','#1c1c1c'])for(const horizontal of [false,true]) {
    const chart=echarts.init(document.querySelector('#chart'),null,{renderer:'canvas',devicePixelRatio:1}),categories=['Q1','Q3'],data=[[4,9.019,9.019,20.013,28],[4,9.019,20.013,20.013,28]];
    chart.setOption({animation:false,backgroundColor:canvas,grid:{left:60,right:25,top:25,bottom:45},xAxis:horizontal?{type:'value',min:0,max:30}:{type:'category',data:categories},yAxis:horizontal?{type:'category',data:categories}:{type:'value',min:0,max:30},series:[{type:'boxplot',data,itemStyle:{color:fill,borderColor:fill,borderWidth:1}}]});
    const report=medianHelpers.qualifyBoxplotMedians(chart,echarts,'colorset1'),context=chart.getZr().painter.getRenderedCanvas({pixelRatio:1}).getContext('2d');
    for(const mark of report.medians)for(const fraction of [.25,.5,.75]) {
      const center=mark.ends[0].map((v,i)=>v+(mark.ends[1][i]-v)*fraction),x=Math.floor(center[0])-2,y=Math.floor(center[1])-2,bytes=context.getImageData(x,y,5,5).data,backing=L(mark.backing.match(/[\d.]+/g).slice(0,3).map(Number));let strongestPixelContrast=1;
      for(let i=0;i<bytes.length;i+=4){const px=x+i/4%5+.5,py=y+Math.floor(i/20)+.5;if(px<mark.face.x||px>mark.face.x+mark.face.width||py<mark.face.y||py>mark.face.y+mark.face.height)continue;const ink=L([bytes[i],bytes[i+1],bytes[i+2]]);strongestPixelContrast=Math.max(strongestPixelContrast,(Math.max(ink,backing)+.05)/(Math.min(ink,backing)+.05));}
      marks.push({fill,canvas,horizontal,quartile:mark.dataIndex?'Q3':'Q1',fraction,strongestPixelContrast,ink:mark.ink});
    }
    chart.dispose();
  }
  return marks;
});
for(const mark of paletteBoundaryRows)assert(mark.strongestPixelContrast>=3,'palette-boundary median actual paint contrast failed: '+JSON.stringify(mark));
const nativeCrossoverRows=[];
for(const canvas of ['#ffffff','#1c1c1c'])for(const style of [{fill:'#757575',opacity:.996},{fill:'rgba(119,119,119,0.91)',opacity:.83}]) {
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360});chart.setOption(makeOption(canvas,false));
  const owner=chart.getModel().getSeriesByIndex(0).getData().getItemGraphicEl(0);owner.setStyle(style);
  const before=nativeSnapshot(chart),option=JSON.stringify(chart.getOption()),result=qualify(chart,echarts,'colorset1');
  assert.deepEqual(nativeSnapshot(chart),before);assert.equal(JSON.stringify(chart.getOption()),option);
  if(style.opacity===.996&&canvas==='#ffffff') {assert.equal(result.medians[0].ink,'#000000');assert.equal(result.medians[0].svgInk,'#ffffff');}
  nativeCrossoverRows.push({canvas,style,median:result.medians[0],actualNativePaintPreserved:true});chart.dispose();
}
for(const alteration of ['version','points','gradient']) {
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360});chart.setOption(makeOption('#ffffff',false));
  const owner=chart.getModel().getSeriesByIndex(0).getData().getItemGraphicEl(0);
  if(alteration==='points')owner.shape.points=owner.shape.points.slice(0,12);
  if(alteration==='gradient')owner.style.fill={type:'linear',x:0,y:0,x2:1,y2:0,colorStops:[{offset:0,color:'#000000'},{offset:1,color:'#ffffff'}]};
  const builder=owner.buildPath,option=JSON.stringify(chart.getOption());
  assert.throws(()=>qualify(chart,alteration==='version'?{...echarts,version:'unsupported'}:echarts,'colorset1'),/6.1.0|fourteen-end|known solid/);
  assert.equal(owner.buildPath,builder);assert.equal(JSON.stringify(chart.getOption()),option);chart.dispose();
}
await browser.close();
const report={ok:true,echartsVersion:echarts.version,ssrStates:rows.length,canvasStates:canvasRows.reduce((n,row)=>n+row.states.length,0),paletteBoundaryPixels:paletteBoundaryRows.length,medianSegmentsTransferredExactlyOnce:true,nativeEndsAndBodyWhiskerPaintPreserved:true,minimumMedianContrast:Math.min(...rows.flatMap(row=>row.proof.map(p=>p.contrast))),minimumBoundaryPixelContrast:Math.min(...paletteBoundaryRows.map(row=>row.strongestPixelContrast)),zeroIqrUsesCanvas:true,nativeClippingRetained:true,statesResizeUpdateCleanupAndRepeat:true,unroundedNativeAndDeliveredCrossover:true,unsupportedRejectedBeforeMutation:true,rows,canvasRows,paletteBoundaryRows,nativeCrossoverRows};
fs.writeFileSync(path.join(OUTPUT,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,rows:undefined,canvasRows:undefined,paletteBoundaryRows:undefined}));
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--echarts-package',type=Path,required=True)
    parser.add_argument('--playwright-package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    skill=Path(__file__).resolve().parents[1]
    values={'ECHARTS':str(args.echarts_package.resolve()),'PLAYWRIGHT':str(args.playwright_package.resolve()),'MODULE':(skill/'assets/templates/echarts-colorsets.mjs').as_uri(),'OUTPUT':str(args.output.resolve())}
    source=TEST
    for token,value in values.items():source=source.replace(token,json.dumps(value))
    result=subprocess.run(['node','--input-type=module','-e',source],capture_output=True,text=True,encoding='utf-8')
    print(result.stdout.strip())
    if result.returncode:print(result.stderr.strip())
    return result.returncode

if __name__=='__main__':raise SystemExit(main())
