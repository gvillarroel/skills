// Runtime implementation for render_concept_graph.py; requires ECharts 6.1.0.
// Native graph symbols, edges and edge captions are retained throughout.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {prepareColorsetOption, insetGraphArrowRoutes, normalizeSvgPaints} from './echarts-colorsets.mjs';
import {settleConceptGraphCaptions} from './concept-graph-labels.mjs';

const require = createRequire(path.resolve('concept-graph-runtime.cjs'));
const echarts = require('echarts');
if (echarts.version !== '6.1.0') throw new Error('Native conceptual graphs require ECharts 6.1.0');
const [inputPath, svgPath, optionPath, reviewPath, mode] = process.argv.slice(2);
if (!reviewPath) throw new Error('Pass input JSON, output SVG, option JSON and review JSON');
class LayoutRejection extends Error {
  constructor(gate,reason) {super(reason);this.gate=gate;}
}
const reject=(gate,reason)=>{throw new LayoutRejection(gate,reason);};
if(mode==='--probe') process.once('uncaughtException',error=>{
  if(!(error instanceof LayoutRejection)){console.error(error.stack??error);process.exit(1);}
  const result={ok:true,accepted:false,gate:error.gate,reason:error.message,svgDelivered:false,optionDelivered:false};
  fs.mkdirSync(path.dirname(reviewPath),{recursive:true});fs.writeFileSync(reviewPath,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));process.exit(0);
});
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const fail = message => { throw new Error(message); };
const finite = (v, fallback) => v === undefined ? fallback : Number.isFinite(v) ? v : fail('Geometry must be finite');
const fontSize = Math.max(16, finite(input.fontSize, 18)), captionSize = Math.max(14, finite(input.captionSize, 14));
const headSize = Math.max(14, finite(input.headSize, 14)), strokeWidth = Math.max(2, finite(input.strokeWidth, 2));
const fontFamily = 'Open Sans, Arial, sans-serif';
const measure = (text, size, bold = false) => new echarts.graphic.Text({style:{text, font:`${bold ? '600 ' : ''}${size}px ${fontFamily}`}}).getBoundingRect().width;
const wrap = (label, size, limit) => label.split('\n').flatMap(paragraph => {
  const words = paragraph.split(/\s+/), lines = []; let line = '';
  for (const word of words) {const next = line ? line+' '+word : word; if (line && measure(next,size,true)>limit) {lines.push(line);line=word;} else line=next;}
  lines.push(line);return lines;
}).join('\n');
if (!Array.isArray(input.nodes) || !input.nodes.length || input.nodes.length > 40) fail('Provide 1–40 named nodes; split larger conceptual graphs');
if (!Array.isArray(input.edges) || input.edges.length > 80) fail('Provide up to 80 directed edges');
const ids = new Set();
const nodes = input.nodes.map(node => {
  if (typeof node.id !== 'string' || !node.id || ids.has(node.id) || typeof node.label !== 'string' || !node.label.trim()) fail('Node IDs must be unique strings and full labels must be nonempty');
  ids.add(node.id);
  const label = wrap(node.label, fontSize, finite(input.labelWidth,220));
  const width = Math.ceil(Math.max(...label.split('\n').map(line=>measure(line,fontSize,true)))*1.12+28);
  const height = Math.ceil(label.split('\n').length*(fontSize+5)+24);
  return {...node, label, fullLabel:node.label, width, height};
});
const byId = new Map(nodes.map(node=>[node.id,node]));
const edges = input.edges.map((edge,index) => {
  if (!ids.has(edge.source) || !ids.has(edge.target) || edge.source===edge.target) fail('Every edge needs distinct existing source/target IDs; self loops require a specialist layout');
  if (edge.label !== undefined && typeof edge.label !== 'string') fail('Edge labels must be strings');
  if (edge.kind !== undefined && !['forward','return'].includes(edge.kind)) fail('Edge kind must be forward or return');
  return {...edge,id:edge.id??`edge-${index}`,label:edge.label??''};
});
if (new Set(edges.map(edge=>edge.id)).size!==edges.length) fail('Edge IDs must be unique');
const positioned = nodes.some(node=>node.x!==undefined || node.y!==undefined);
if (positioned && nodes.some(node=>!Number.isFinite(node.x)||!Number.isFinite(node.y))) fail('Supply x/y for every node or let the helper compute all positions');
if (!positioned) {
  if (nodes.some(node=>node.rank!==undefined)) {
    if (nodes.some(node=>!Number.isInteger(node.rank)||node.rank<0||node.rank>40)) fail('Supply a nonnegative integer rank for every node');
  } else {
    const incoming = new Map(nodes.map(node=>[node.id,0])), ranks = new Map(nodes.map(node=>[node.id,0]));
    for (const edge of edges.filter(edge=>edge.kind!=='return')) incoming.set(edge.target,incoming.get(edge.target)+1);
    const ready = nodes.filter(node=>incoming.get(node.id)===0).map(node=>node.id); let seen=0;
    while (ready.length) {const id=ready.shift();seen++;for (const edge of edges.filter(edge=>edge.kind!=='return'&&edge.source===id)) {ranks.set(edge.target,Math.max(ranks.get(edge.target),ranks.get(id)+1));incoming.set(edge.target,incoming.get(edge.target)-1);if (!incoming.get(edge.target)) ready.push(edge.target);}}
    if (seen!==nodes.length) fail('Mark cycle-closing edges kind:return or provide explicit ranks');
    for (const node of nodes) node.rank=ranks.get(node.id);
  }
  const ranks = [...new Set(nodes.map(node=>node.rank))].sort((a,b)=>a-b);
  let x=0;
  for (const rank of ranks) {
    const members=nodes.filter(node=>node.rank===rank), column=Math.max(...members.map(node=>node.width));
    let y=0;
    for (const node of members) {node.x=x+column/2;node.y=y+node.height/2;y+=node.height+captionSize+headSize+8;}
    const next=ranks[ranks.indexOf(rank)+1];
    const local=edges.filter(edge=>Math.min(byId.get(edge.source).rank,byId.get(edge.target).rank)===rank&&Math.max(byId.get(edge.source).rank,byId.get(edge.target).rank)===next);
    const gap=Math.max(headSize*2+16,...local.map(edge=>edge.label?measure(edge.label,captionSize)+headSize*2+28:0));
    x+=column+gap;
  }
  // Align the first member of every rank on the same reading row.
  const firstY=Math.max(...ranks.map(rank=>nodes.find(node=>node.rank===rank).height/2));
  for (const rank of ranks) {const members=nodes.filter(node=>node.rank===rank), delta=firstY-members[0].y;for (const node of members)node.y+=delta;}
}
const counts = new Map();
for (const edge of edges) {
  const a=byId.get(edge.source),b=byId.get(edge.target),dx=b.x-a.x;
  const key=[edge.source,edge.target].join('\0'), lane=counts.get(key)??0;counts.set(key,lane+1);
  const returning=edge.kind==='return'||(!positioned&&b.rank<=a.rank);
  const skipping=!positioned&&b.rank>a.rank+1;
  if (edge.curveness!==undefined) edge.curveness=finite(edge.curveness,0);
  else if (returning || skipping || lane) {
    if (Math.abs(dx)<1) fail('Vertical parallel/return routes need explicit curveness and positions');
    const rise=Math.max(a.height,b.height)/2+headSize+captionSize+24+lane*36;
    edge.curveness=(skipping?-1:1)*Math.sign(dx)*2*rise/Math.abs(dx);
  } else edge.curveness=0;
}
const point = (a,b,c,t) => c ? [(1-t)**2*a.x+2*(1-t)*t*((a.x+b.x)/2+(b.y-a.y)*c)+t*t*b.x,(1-t)**2*a.y+2*(1-t)*t*((a.y+b.y)/2-(b.x-a.x)*c)+t*t*b.y] : [a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t];
const overlaps=(a,b,gap=0)=>a.x<b.x+b.width+gap&&a.x+a.width>b.x-gap&&a.y<b.y+b.height+gap&&a.y+a.height>b.y-gap;
const body=node=>({x:node.x-node.width/2,y:node.y-node.height/2,width:node.width,height:node.height});
for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++)if(overlaps(body(nodes[i]),body(nodes[j]),8))reject('node-overlap','Node envelopes overlap; provide wider positions or split the graph');
for (const edge of edges) for (let t=0;t<=1;t+=.005) {
  const [x,y]=point(byId.get(edge.source),byId.get(edge.target),edge.curveness,t);
  for (const node of nodes) if (node.id!==edge.source&&node.id!==edge.target&&overlaps({x,y,width:.01,height:.01},body(node),4)) reject('route-crosses-node',`Route ${edge.id} crosses unrelated node ${node.id}; use explicit ranks/curveness or split the graph`);
}
const rects=nodes.map(body), pad=18, title=input.title??'';
for (const edge of edges) {const a=byId.get(edge.source),b=byId.get(edge.target);for(let t=0;t<=1;t+=.01){const [x,y]=point(a,b,edge.curveness,t);rects.push({x:x-headSize,y:y-headSize,width:headSize*2,height:headSize*2});}
  if(edge.label){const [x,y]=point(a,b,edge.curveness,.5),w=measure(edge.label,captionSize)*1.12+20;rects.push({x:x-w/2,y:y-captionSize*2,width:w,height:captionSize*4});}}
const minX=Math.min(...rects.map(r=>r.x)),maxX=Math.max(...rects.map(r=>r.x+r.width)),minY=Math.min(...rects.map(r=>r.y)),maxY=Math.max(...rects.map(r=>r.y+r.height));
const titleBand=title?42:0;
const naturalWidth=Math.ceil(Math.max(maxX-minX+pad*2,title?measure(title,24,true)*1.12+pad*2:0));
const naturalHeight=Math.ceil(maxY-minY+pad*2+titleBand);
const width=finite(input.width,naturalWidth),height=finite(input.height,naturalHeight);
if(width>16384||height>16384)fail('Canvas dimensions must be at most 16384 pixels');
if(width<naturalWidth||height<naturalHeight)reject('canvas-too-small',`Canvas must accommodate ${naturalWidth}×${naturalHeight} readable content without scaling`);
const shiftX=pad-minX+(width-naturalWidth)/2,shiftY=pad+titleBand-minY+(height-naturalHeight)/2;
for(const node of nodes){node.x+=shiftX;node.y+=shiftY;}
const xs=nodes.map(n=>n.x),ys=nodes.map(n=>n.y),spanX=Math.max(...xs)-Math.min(...xs),spanY=Math.max(...ys)-Math.min(...ys);
const option={animation:false,backgroundColor:'#ffffff',graphic:title?[{type:'text',left:pad,top:pad,style:{text:title,font:`600 24px ${fontFamily}`,fill:'#333e48'}}]:[],series:[{
  id:'concepts',type:'graph',layout:'none',coordinateSystem:'view',roam:false,
  left:Math.min(...xs)-(spanX?0:1),top:Math.min(...ys)-(spanY?0:1),width:spanX||2,height:spanY||2,
  symbol:'roundRect',edgeSymbol:['none','arrow'],edgeSymbolSize:headSize,
  label:{show:true,position:'inside',fontFamily,fontSize,fontWeight:600,lineHeight:fontSize+5},
  edgeLabel:{show:true,fontFamily,fontSize:captionSize,color:'#333e48',position:'middle',distance:8,backgroundColor:'#ffffff',padding:[3,6]},
  lineStyle:{width:strokeWidth,color:'#696969',opacity:1},
  data:nodes.map(node=>({id:node.id,name:node.label,x:node.x,y:node.y,symbolSize:[node.width,node.height]})),
  links:edges.map(edge=>({id:edge.id,source:edge.source,target:edge.target,name:edge.label,value:edge.label,label:{show:!!edge.label,formatter:'{c}'},lineStyle:{curveness:edge.curveness,type:edge.kind==='return'?'dashed':'solid'}}))
}]};
prepareColorsetOption(option,input.colorset??'colorset1',nodes.map(node=>node.id));
const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width,height});
chart.setOption(option);
// SSR does not run the normal browser frame. Settle native Line captions
// before the arrow helper protects their existing layout.
chart.getZr().flush();
chart.renderToSVGString();
chart.getModel().eachSeriesByType('graph',series=>series.getGraph().eachEdge(edge=>{const element=edge.getGraphicEl();element.markRedraw();element.childOfName('line').dirtyShape();element.beforeUpdate();}));
chart.getZr().flush();
const qualify=()=>{try{return insetGraphArrowRoutes(chart,3);}catch(error){
  const expected=['Graph route is too short for the complete arrowhead; increase the native node gutter','Graph route is too short for its complete terminal glyphs','Graph arrowhead is blocked by a node; author a clear native route gutter'];
  if(expected.includes(error.message))reject('arrow-clearance',error.message);
  throw error;
}};
const clearance=qualify();
settleConceptGraphCaptions(chart);
chart.renderToSVGString();
const repeat=qualify();
settleConceptGraphCaptions(chart);
let svg=normalizeSvgPaints(chart.renderToSVGString(),input.colorset??'colorset1');
const bounds=element=>{const b=element.getBoundingRect().clone();b.applyTransform(element.getComputedTransform());return {x:b.x,y:b.y,width:b.width,height:b.height};};
const geometry={nodes:[],captions:[],heads:[]};
chart.getModel().eachSeriesByType('graph',series=>{
  const graph=series.getGraph();
  graph.eachNode(node=>geometry.nodes.push({id:node.id,fullLabel:byId.get(node.id).fullLabel,bounds:bounds(node.getGraphicEl().getSymbolPath())}));
  graph.eachEdge(edge=>{const element=edge.getGraphicEl(),text=element.getTextContent();if(text&&!text.ignore)geometry.captions.push({id:edges[edge.dataIndex].id,label:edges[edge.dataIndex].label,bounds:bounds(text),anchor:[text.x,text.y]});const head=element.childOfName('toSymbol');if(head)geometry.heads.push({id:edges[edge.dataIndex].id,bounds:bounds(head)});});
});
for(const record of [...geometry.nodes,...geometry.captions,...geometry.heads]){const b=record.bounds;if(b.x<-.1||b.y<titleBand-.1||b.x+b.width>width+.1||b.y+b.height>height+.1)reject('outside-canvas',`Rendered ${record.id} is outside the protected canvas; increase explicit clearances`);}
for(const caption of geometry.captions){for(const node of geometry.nodes)if(overlaps(caption.bounds,node.bounds,3))reject('caption-node-overlap',`Caption ${caption.id} overlaps node ${node.id}; protect full captions`);}
for(let i=0;i<geometry.captions.length;i++)for(let j=i+1;j<geometry.captions.length;j++)if(overlaps(geometry.captions[i].bounds,geometry.captions[j].bounds,3))reject('caption-overlap','Native edge captions overlap; provide separate lanes');
const xml=text=>String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
svg=svg.replace('<svg ','<svg role="img" aria-labelledby="concept-title concept-desc" ').replace('>',`><title id="concept-title">${xml(title||'Concept graph')}</title><desc id="concept-desc">${xml(nodes.map(n=>n.fullLabel).join('; ')+'. '+edges.map(e=>`${byId.get(e.source).fullLabel} to ${byId.get(e.target).fullLabel}${e.label?': '+e.label:''}`).join('; '))}</desc>`);
chart.dispose();
const review={ok:true,accepted:true,echartsVersion:echarts.version,width,height,naturalWidth,naturalHeight,fontSize,captionSize,headSize,strokeWidth,clearance,repeat,geometry,nodes: nodes.map(({id,fullLabel,rank,x,y,width,height})=>({id,fullLabel,rank,x,y,width,height})),edges:edges.map(({id,source,target,label,kind,curveness})=>({id,source,target,label,kind,curveness})),checks:['native view transform remains 1:1','complete node/head/caption envelopes inside canvas','node and caption separation','routes avoid unrelated nodes','native repeated insetting is stable'],limitation:'Simple ranked conceptual graphs only; inspect Chromium at final size. The native preservation checks do not certify global optimal packing or all curve crossings.'};
for(const [filename,content] of [[svgPath,svg],[optionPath,JSON.stringify(option,null,2)+'\n'],[reviewPath,JSON.stringify(review,null,2)+'\n']]){fs.mkdirSync(path.dirname(filename),{recursive:true});fs.writeFileSync(filename,content);}
console.log(JSON.stringify({ok:true,width,height,nodes:nodes.length,edges:edges.length,svg:svgPath,option:optionPath,review:reviewPath}));
