#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect an authored poster with Chromium and export a full-resolution preview."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Support both direct execution and evaluator-owned importlib loading.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_timeline_annotations import check_annotations

AUDIT = r"""() => {
  const svg = document.querySelector('svg');
  const meta = JSON.parse(svg.querySelector('#chart-data').textContent);
  const view = svg.viewBox.baseVal;
  const findings = [];
  const bounds = el => {
    const b=el.getBBox(),m=svg.getScreenCTM().inverse().multiply(el.getScreenCTM());
    const p=[[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
    const xs=p.map(v=>v.x),ys=p.map(v=>v.y);
    return {x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};
  };
  const viewport = el => {
    if(!el.viewBox)return null;
    const b=el.viewBox.baseVal,m=svg.getScreenCTM().inverse().multiply(el.getScreenCTM());
    const a=new DOMPoint(b.x,b.y).matrixTransform(m),z=new DOMPoint(b.x+b.width,b.y+b.height).matrixTransform(m);
    return {x:a.x,y:a.y,w:z.x-a.x,h:z.y-a.y};
  };
  const textOrigin=el=>new DOMPoint(el.x.baseVal[0]?.value||0,el.y.baseVal[0]?.value||0).matrixTransform(svg.getScreenCTM().inverse().multiply(el.getScreenCTM()));
  const glyphPoint=(el,end=false)=>{
    const count=el.getNumberOfChars();if(!count)return null;
    const p=end?el.getEndPositionOfChar(count-1):el.getStartPositionOfChar(0);
    const v=new DOMPoint(p.x,p.y).matrixTransform(svg.getScreenCTM().inverse().multiply(el.getScreenCTM()));
    return {x:v.x,y:v.y};
  };
  const intersect=(a,b,p=0)=>a.x<b.x+b.w-p && a.x+a.w>b.x+p && a.y<b.y+b.h-p && a.y+a.h>b.y+p;
  const contained=(a,b,p=0)=>a.x>=b.x-p && a.y>=b.y-p && a.x+a.w<=b.x+b.w+p && a.y+a.h<=b.y+b.h+p;
  const lum=color=>{
    const rgb=color.startsWith('#')?[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)):color.match(/[\d.]+/g).slice(0,3).map(Number);
    return rgb.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  };
  const contrast=(a,b)=>{const [lo,hi]=[lum(a),lum(b)].sort((x,y)=>x-y);return (hi+.05)/(lo+.05)};
  const painted=el=>{
    if(!el)return null;
    const style=getComputedStyle(el);let opacity=Number(style.fillOpacity),visible=true;
    for(let current=el;current;current=current.parentElement){const css=getComputedStyle(current);opacity*=Number(css.opacity);visible&&=css.display!=='none'&&css.visibility==='visible';}
    return {box:bounds(el),fill:style.fill,opacity,visible};
  };
  const nodes=[...svg.querySelectorAll('[data-node-id]')].map(el=>{
    const body=el.querySelector('[data-node-box]'),label=el.querySelector('[data-label-box]'),stem=el.querySelector('[data-period-stem]');
    return {id:el.dataset.nodeId,box:bounds(body),label_box:label?bounds(label):null,
      period_stem:painted(stem),period_label:painted(el.querySelector('[data-period-label]')),
      parts:stem?[bounds(stem),...(label?[bounds(label)]:[])]:[bounds(body)]};
  });
  const byId=Object.fromEntries(nodes.map(n=>[n.id,n]));
  const edges=[...svg.querySelectorAll('[data-edge-id]')].map(el=>({id:el.dataset.edgeId,source:el.dataset.source,target:el.dataset.target,kind:el.dataset.kind,source_port:el.dataset.sourcePort||'bottom',target_port:el.dataset.targetPort||'top',d:el.getAttribute('d'),curved:el.dataset.routeStyle==='rounded'}));
  const events=[...svg.querySelectorAll('[data-event-id]')].map(el=>({id:el.dataset.eventId,year:Number(el.dataset.year),origin_y:Number(el.dataset.originY),text:el.textContent}));
  const unions=[...svg.querySelectorAll('[data-union-id]')].map(el=>({id:el.dataset.unionId,d:el.getAttribute('d')}));
  const texts=[...svg.querySelectorAll('text')].map(el=>({text:el.textContent,owner:el.dataset.owner,event:el.closest('[data-event-id]')?.dataset.eventId,role:el.dataset.eventTextRole||null,origin:{x:textOrigin(el).x,y:textOrigin(el).y},box:bounds(el),font:parseFloat(getComputedStyle(el).fontSize),contrast:contrast(getComputedStyle(el).fill,el.dataset.background),runs:[...el.querySelectorAll('tspan')].map(run=>({text:run.textContent,role:run.dataset.eventRunRole||null,font:parseFloat(getComputedStyle(run).fontSize),weight:Number(getComputedStyle(run).fontWeight),origin:glyphPoint(run),end:glyphPoint(run,true),contrast:contrast(getComputedStyle(run).fill,el.dataset.background),...painted(run)}))}));
  const illustrations=[...svg.querySelectorAll('[data-event-id] [data-artwork]')].map(el=>({event:el.closest('[data-event-id]').dataset.eventId,kind:el.dataset.artwork,illustration_id:el.dataset.illustrationId||null,use_href:el.querySelector('use')?.getAttribute('href')||null,viewport:viewport(el),...painted(el)}));
  const landmarks=[...svg.querySelectorAll('[data-annotation-kind="landmark"]')].map(el=>({id:el.dataset.annotationId,node:el.dataset.contextNode,group:el.dataset.contextGroup,field:el.dataset.sourceField,value:el.dataset.sourceValue,box:bounds(el.querySelector('[data-annotation-box]')),heraldry_fill:el.querySelector('[data-artwork="heraldry"]>path')?getComputedStyle(el.querySelector('[data-artwork="heraldry"]>path')).fill:null,label:[...el.querySelectorAll('[data-content-role="landmark-label"]')].map(t=>t.textContent).join(' ')}));
  const setEqual=(a,b)=>a.length===b.length && [...a].sort().join('\n')===[...b].sort().join('\n');
  if(!setEqual(nodes.map(n=>n.id),meta.node_ids))findings.push({type:'node-inventory'});
  if(!setEqual(edges.map(e=>e.id),meta.edge_ids))findings.push({type:'edge-inventory'});
  if(texts.map(t=>t.text).join('\n')!==meta.expected_text.join('\n'))findings.push({type:'text-inventory'});
  for(const n of nodes)if(!contained(n.box,{x:0,y:0,w:view.width,h:view.height}))findings.push({type:'node-outside-page',id:n.id});
  for(const t of texts){
    if(!contained(t.box,{x:24,y:0,w:view.width-48,h:view.height-24},.5))findings.push({type:'text-outside-page',text:t.text});
    if(t.owner!=='page' && (!byId[t.owner] || !contained(t.box,byId[t.owner].label_box||byId[t.owner].box,-2)))findings.push({type:'label-outside-node',id:t.owner,text:t.text,box:t.box});
    if(t.contrast<4.5-.01)findings.push({type:'text-contrast',text:t.text,ratio:t.contrast});
    if(t.box.w<.1||t.box.h<.1)findings.push({type:'empty-text-geometry',text:t.text});
  }
  for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(intersect(texts[i].box,texts[j].box,1.2))findings.push({type:'text-overlap',a:texts[i].text,b:texts[j].text});
  for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++)if(nodes[i].parts.some(a=>nodes[j].parts.some(b=>intersect(a,b,.5))))findings.push({type:'node-overlap',a:nodes[i].id,b:nodes[j].id});
  for(const t of texts)for(const n of nodes)if(t.owner!==n.id && n.parts.some(part=>intersect(t.box,part,.5)))findings.push({type:'text-other-node',text:t.text,node:n.id});
  for(const art of illustrations){
    if(!contained(art.box,{x:24,y:0,w:view.width-48,h:view.height-24},.5))findings.push({type:'illustration-outside-page',event:art.event});
    for(const n of nodes)if(n.parts.some(part=>intersect(art.box,part,.5)))findings.push({type:'illustration-node-collision',event:art.event,node:n.id});
    for(const t of texts)if(intersect(art.box,t.box,.5))findings.push({type:'illustration-text-collision',event:art.event,text:t.text});
  }
  for(const heading of svg.querySelectorAll('[data-annotation-kind="heading"]')){
    for(const art of heading.querySelectorAll('[data-artwork]')){
      const b=bounds(art);
      if(!contained(b,{x:34,y:118,w:view.width-68,h:view.height-152},.5))findings.push({type:'heading-art-outside-paper',id:heading.dataset.annotationId});
      for(const t of texts)if(intersect(b,t.box,.5))findings.push({type:'heading-art-text-collision',id:heading.dataset.annotationId,text:t.text});
    }
  }
  for(let i=0;i<illustrations.length;i++)for(let j=i+1;j<illustrations.length;j++)if(intersect(illustrations[i].box,illustrations[j].box,.5))findings.push({type:'illustration-overlap',a:illustrations[i].event,b:illustrations[j].event});
  for(const landmark of landmarks){
    const el=svg.querySelector(`[data-annotation-id="${CSS.escape(landmark.id)}"]`);
    if(!contained(landmark.box,{x:48,y:130,w:view.width-96,h:view.height-215},.5))findings.push({type:'landmark-outside-paper',id:landmark.id});
    for(const child of el.querySelectorAll('text,[data-artwork]'))if(!contained(bounds(child),landmark.box,.5))findings.push({type:'landmark-content-overflow',id:landmark.id});
    for(const node of nodes)if(intersect(landmark.box,node.box))findings.push({type:'landmark-node-collision',id:landmark.id,node:node.id});
    for(const other of svg.querySelectorAll('[data-annotation-id]'))if(other!==el&&intersect(landmark.box,bounds(other),.5))findings.push({type:'landmark-annotation-collision',id:landmark.id,other:other.dataset.annotationId});
    for(const path of svg.querySelectorAll('[data-edge-id],[data-union-id]')){
      const length=path.getTotalLength(),r=landmark.box;
      for(let at=0;at<=length;at+=2){
        const p=path.getPointAtLength(at);
        if(p.x>r.x&&p.x<r.x+r.w&&p.y>r.y&&p.y<r.y+r.h){findings.push({type:'landmark-path-collision',id:landmark.id,path:path.dataset.edgeId||path.dataset.unionId});break;}
      }
    }
  }
  for(const rule of svg.querySelectorAll('[data-era-rule]')){
    const b=bounds(rule),r={x:b.x,y:b.y-1,w:b.w,h:2};
    for(const t of texts)if(t.owner==='page'&&intersect(r,t.box,.1))findings.push({type:'era-rule-text-collision',year:rule.dataset.eraRule,text:t.text});
  }
  const points=d=>(d.match(/-?\d+(?:\.\d+)?/g)||[]).map(Number).reduce((a,n,i,all)=>{if(i%2===0)a.push([n,all[i+1]]);return a},[]);
  const attached=(point,box,side)=>{
    if(!box)return false;
    if(side==='top'||side==='bottom')return point[0]>=box.x+5&&point[0]<=box.x+box.w-5&&Math.abs(point[1]-box.y-(side==='bottom'?box.h:0))<=.1;
    if(side==='left'||side==='right')return point[1]>=box.y+5&&point[1]<=box.y+box.h-5&&Math.abs(point[0]-box.x-(side==='right'?box.w:0))<=.1;
    return false;
  };
  for(const e of edges){
    const el=svg.querySelector(`[data-edge-id="${CSS.escape(e.id)}"]`);
    const length=el.getTotalLength();
    const p=e.curved?Array.from({length:Math.ceil(length/2)+1},(_,i)=>{const p=el.getPointAtLength(Math.min(length,i*2));return [p.x,p.y]}):points(e.d);
    if(e.curved){const end=el.getPointAtLength(length);p.push([end.x,end.y]);}
    const inside=(point,r)=>point[0]>r.x+.25&&point[0]<r.x+r.w-.25&&point[1]>r.y+.25&&point[1]<r.y+r.h-.25;
    for(const t of texts)if(t.event&&p.some(point=>inside(point,t.box)))findings.push({type:'edge-event-text-collision',edge:e.id,event:t.event,text:t.text});
    for(const art of illustrations)if(p.some(point=>inside(point,art.box)))findings.push({type:'edge-event-illustration-collision',edge:e.id,event:art.event});
    for(let i=0;i<p.length-1;i++){
      const [a,b]=[p[i],p[i+1]];
      if(!e.curved&&a[0]!==b[0]&&a[1]!==b[1])findings.push({type:'non-orthogonal-edge',id:e.id});
      for(const n of nodes)for(const r of n.parts){
        const hit=e.curved?a[0]>r.x+.6&&a[0]<r.x+r.w-.6&&a[1]>r.y+.6&&a[1]<r.y+r.h-.6:a[0]===b[0]?a[0]>r.x+.1&&a[0]<r.x+r.w-.1&&Math.max(Math.min(a[1],b[1]),r.y)<Math.min(Math.max(a[1],b[1]),r.y+r.h)-.1:a[1]>r.y+.1&&a[1]<r.y+r.h-.1&&Math.max(Math.min(a[0],b[0]),r.x)<Math.min(Math.max(a[0],b[0]),r.x+r.w)-.1;
        if(hit)findings.push({type:'edge-node-collision',edge:e.id,node:n.id});
      }
    }
    const target=byId[e.target]?.box,last=p.at(-1);
    if(!attached(last,target,e.target_port))findings.push({type:'detached-target',id:e.id});
    const origin=byId[e.source]?.box,first=p[0];
    if(origin&&!attached(first,origin,e.source_port))findings.push({type:'detached-source',id:e.id});
    if((e.source_port!=='bottom'||e.target_port!=='top')&&(meta.mode!=='lineage'||e.kind!=='influence'))findings.push({type:'invalid-lateral-relation',id:e.id});
  }
  const composition_warnings=[];
  if(meta.mode==='lineage'){
    const straights=e=>{
      const element=svg.querySelector(`[data-edge-id="${CSS.escape(e.id)}"]`);
      const matrix=svg.getScreenCTM().inverse().multiply(element.getScreenCTM());
      const converted=p=>{const v=new DOMPoint(...p).matrixTransform(matrix);return [v.x,v.y]};
      let at=null;const result=[];
      for(const match of e.d.matchAll(/([MLQ])([^MLQ]*)/g)){
        const values=points(match[2]);
        if(match[1]==='L')for(const point of values){if(at)result.push([converted(at),converted(point)]);at=point;}
        else at=values.at(-1);
      }
      return result;
    };
    const strokes=edges.map(e=>({edge:e,segments:straights(e)}));
    for(let i=0;i<strokes.length;i++)for(let j=i+1;j<strokes.length;j++){
      const a=strokes[i],b=strokes[j];
      if([a.edge.source,a.edge.target].some(id=>[b.edge.source,b.edge.target].includes(id)))continue;
      let longest=0;
      for(const [p,q] of a.segments)for(const [r,s] of b.segments)for(const axis of [0,1]){
        if(Math.max(p[axis],q[axis],r[axis],s[axis])-Math.min(p[axis],q[axis],r[axis],s[axis])>.02)continue;
        const k=1-axis;longest=Math.max(longest,Math.min(Math.max(p[k],q[k]),Math.max(r[k],s[k]))-Math.max(Math.min(p[k],q[k]),Math.min(r[k],s[k])));
      }
      if(longest>4)composition_warnings.push({type:'unrelated-shared-run',first:a.edge.id,second:b.edge.id,length:longest});
    }
  }
  const clippedArea=(poly,r)=>{
    let out=poly;
    for(const [axis,bound,greater] of [[0,r.x,true],[0,r.x+r.w,false],[1,r.y,true],[1,r.y+r.h,false]]){
      const input=out;out=[];if(!input.length)break;
      const inside=p=>greater?p[axis]>=bound:p[axis]<=bound;
      for(let i=0;i<input.length;i++){
        const a=input[i],b=input[(i+1)%input.length],ai=inside(a),bi=inside(b);
        if(ai)out.push(a);
        if(ai!==bi){const t=(bound-a[axis])/(b[axis]-a[axis]);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}
      }
    }
    return Math.abs(out.reduce((sum,p,i)=>{const q=out[(i+1)%out.length];return sum+p[0]*q[1]-q[0]*p[1]},0))/2;
  };
  for(const fill of svg.querySelectorAll('[data-transition-fill]')){
    const poly=points(fill.getAttribute('d'));
    for(const n of nodes)if(n.parts.some(part=>clippedArea(poly,part)>1))findings.push({type:'transition-fill-node-collision',edge:fill.dataset.transitionFill,node:n.id});
    for(const t of texts)if(t.owner==='page'&&clippedArea(poly,t.box)>1)findings.push({type:'transition-fill-text-collision',edge:fill.dataset.transitionFill,text:t.text});
    for(const art of illustrations)if(clippedArea(poly,art.box)>1)findings.push({type:'transition-fill-illustration-collision',edge:fill.dataset.transitionFill,event:art.event});
  }
  return {status:findings.length?'fail':'pass',id:meta.id,mode:meta.mode,canvas:[view.width,view.height],node_count:nodes.length,edge_count:edges.length,event_count:events.length,text_count:texts.length,min_contrast:Math.min(...texts.map(t=>t.contrast)),findings,composition_warnings,nodes,edges,events,unions,texts,illustrations,landmarks,metadata:meta};
}"""


def check_source(report, data):
    import re
    import hashlib
    source_hash=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if report['metadata'].get('data_sha256')!=source_hash:
        report['findings'].append({'type':'source-revision-mismatch','expected_sha256':source_hash,'rendered_sha256':report['metadata'].get('data_sha256')})
    nodes = data.get("periods", []) if data["mode"] == "timeline" else data.get("nodes", [])
    contexts={f'annotation-{i}':a for i,a in enumerate(data.get('annotations',[])) if a.get('kind')=='landmark'}
    actual_contexts={a['id']:a for a in report.get('landmarks',[])}
    if sorted(contexts)!=sorted(actual_contexts):report['findings'].append({'type':'source-landmark-inventory'})
    by_id={n['id']:n for n in nodes}
    for aid,annotation in contexts.items():
        actual=actual_contexts.get(aid)
        if not actual:continue
        source_node=by_id.get(annotation.get('node'),{});value=source_node.get(annotation.get('field'))
        expected=(annotation.get('node'),source_node.get('group'),annotation.get('field'),value)
        if (actual['node'],actual['group'],actual['field'],actual['value'])!=expected:
            report['findings'].append({'type':'source-landmark-binding','id':aid})
        if ' '.join(actual['label'].split())!=' '.join(str(value).split()):
            report['findings'].append({'type':'source-landmark-label','id':aid})
        if annotation.get('icon')=='heraldry':
            paint=next((g['color'] for g in data['groups'] if g['id']==source_node.get('group')),'#000000')
            expected_rgb=tuple(int(paint[i:i+2],16) for i in (1,3,5))
            if tuple(int(v) for v in re.findall(r'\d+',actual.get('heraldry_fill') or ''))!=expected_rgb:
                report['findings'].append({'type':'source-landmark-color','id':aid})
        drawn=next((n['box'] for n in report['nodes'] if n['id']==annotation.get('node')),None)
        if drawn:
            x=drawn['x']+drawn['w']/2+annotation.get('dx',0);y=drawn['y']+drawn['h']/2+annotation.get('dy',0)
            if abs(actual['box']['x']+actual['box']['w']/2-x)>.1 or abs(actual['box']['y']+actual['box']['h']/2-y)>.1:
                report['findings'].append({'type':'source-landmark-position','id':aid})
    if sorted(n["id"] for n in nodes) != sorted(n["id"] for n in report["nodes"]):
        report["findings"].append({"type": "source-node-inventory"})
    relations = list(data.get("edges", [])) + list(data.get("transitions", []))
    for union in data.get("unions", []):
        relations.extend({"id": f'{union["id"]}-{child}', "source": union["id"], "target": child, "kind": "descent"} for child in union.get("children", []))
        partner_boxes=sorted((n["box"] for n in report["nodes"] if n["id"] in union["partners"]),key=lambda b:b["x"])
        drawn=[p for p in report["unions"] if p["id"]==union["id"]]
        if len(partner_boxes)!=2 or len(drawn)!=2:
            report["findings"].append({"type":"source-union-inventory","id":union["id"]})
            continue
        a,b=partner_boxes
        for path in drawn:
            values=[float(v) for v in re.findall(r"-?\d+(?:\.\d+)?",path["d"])]
            if len(values)!=4 or abs(values[0]-a["x"]-a["w"])>.1 or abs(values[2]-b["x"])>.1:
                report["findings"].append({"type":"source-union-endpoint","id":union["id"]})
        midpoint=((a["x"]+a["w"]+b["x"])/2,a["y"]+a["h"]/2)
        for edge in report["edges"]:
            if edge["source"]==union["id"]:
                values=[float(v) for v in re.findall(r"-?\d+(?:\.\d+)?",edge["d"])]
                if abs(values[0]-midpoint[0])>.1 or abs(values[1]-midpoint[1])>.1:
                    report["findings"].append({"type":"source-union-origin","edge":edge["id"]})
    fields = ("id", "source", "target", "kind")
    if sorted(tuple(e[k] for k in fields) for e in relations) != sorted(tuple(e[k] for k in fields) for e in report["edges"]):
        report["findings"].append({"type": "source-relation-inventory"})
    actual_edges={edge['id']:edge for edge in report['edges']}
    for edge in relations if data['mode']!='timeline' else []:
        actual=actual_edges.get(edge['id'])
        if actual and any(actual.get(key,default)!=edge.get(key,default) for key,default in (('source_port','bottom'),('target_port','top'))):
            report['findings'].append({'type':'source-relation-port','id':edge['id']})
    # Text may wrap across lines; retain word order when checking node labels.
    for node in nodes:
        actual = " ".join(t["text"] for t in report["texts"] if t["owner"] == node["id"])
        for field in ('label','detail','date_label'):
            if node.get(field) is not None and " ".join(str(node[field]).split()) not in actual:
                report["findings"].append({"type": f"source-{field.replace('_','-')}-missing", "id": node["id"]})
    if data["mode"] == "timeline":
        y0, y1 = report["metadata"]["time_y"]
        start, end = data["time"]["start"], data["time"]["end"]
        actual_events={e['id']:e for e in report.get('events',[])}
        expected_ids=[e.get('id',f'event-{i}') for i,e in enumerate(data.get('events',[]))]
        if sorted(actual_events)!=sorted(expected_ids):report['findings'].append({'type':'source-event-inventory'})
        for i,event in enumerate(data.get('events',[])):
            actual=actual_events.get(event.get('id',f'event-{i}'))
            if not actual:continue
            expected_y=y0+(event['year']-start)/(end-start)*(y1-y0)
            if abs(actual['year']-event['year'])>.001 or abs(actual['origin_y']-expected_y)>.1:report['findings'].append({'type':'event-time-mismatch','id':actual['id']})
        boxes = {n["id"]: n["box"] for n in report["nodes"]}
        rendered_nodes={n['id']:n for n in report['nodes']}
        weights=[lane.get('weight',1) for lane in data['lanes']]
        lane_widths=[(report['canvas'][0]-175)*weight/sum(weights) for weight in weights]
        lane_origins={lane['id']:110+sum(lane_widths[:index]) for index,lane in enumerate(data['lanes'])}
        if data.get('design')=='editorial' and data.get('layout')!='compact':
            check_annotations(report,data,lane_origins,(y0,y1))
        for node in nodes:
            box = boxes.get(node["id"])
            if not box:
                continue
            expected_y = y0 + (node["start"] - start)/(end - start)*(y1-y0)
            expected_h = (node["end"]-node["start"])/(end-start)*(y1-y0)
            if abs(box["y"]-expected_y)>.1 or abs(box["h"]-expected_h)>.1:
                report["findings"].append({"type": "numeric-time-mismatch", "id": node["id"]})
            actual=rendered_nodes[node['id']];stem=actual.get('period_stem');label=actual.get('label_box')
            if data.get('design')=='editorial' and data.get('layout')!='compact':
                expected_x=lane_origins[node['lane']]+node.get('offset',18)
                if abs(box['x']-expected_x)>.1 or abs(box['w']-node.get('bar_width',32))>.1:
                    report['findings'].append({'type':'source-period-lane-position','id':node['id']})
            if bool(stem)!=(node.get('treatment')=='stem'):
                report['findings'].append({'type':'source-period-treatment','id':node['id']})
            if node.get('treatment')=='stem' and stem:
                sb=stem['box'];sw=node.get('stem_width',5)
                expected_color=next(group['color'] for group in data['groups'] if group['id']==node['group'])
                rgb='rgb('+', '.join(str(int(expected_color[i:i+2],16)) for i in (1,3,5))+')'
                if any(abs(sb[key]-value)>.1 for key,value in dict(x=box['x']+(box['w']-sw)/2,y=expected_y,w=sw,h=expected_h).items()) or not stem['visible'] or stem['opacity']<.99 or stem['fill']!=rgb:
                    report['findings'].append({'type':'source-period-stem-geometry','id':node['id']})
                if not label or any([label['x']<box['x']-.1,label['x']+label['w']>box['x']+box['w']+.1,label['y']<expected_y-.1,label['y']+label['h']>expected_y+expected_h+.1]) or abs(label['y']-(expected_y+(expected_h-label['h'])*node.get('label_position',.5)))>.1:
                    report['findings'].append({'type':'source-period-label-geometry','id':node['id']})
                label_paint=actual.get('period_label')
                if not label_paint or label_paint['fill']!=rgb or not label_paint['visible'] or label_paint['opacity']<.99:
                    report['findings'].append({'type':'source-period-label-treatment','id':node['id']})
        if data.get('design')=='editorial':
            for edge in relations:
                actual=actual_edges.get(edge['id'])
                if not actual:continue
                coords=[float(value) for value in re.findall(r'-?\d+(?:\.\d+)?',actual['d'])]
                for node_id,fraction,point,bottom in ((edge['source'],edge.get('source_port',.5),coords[:2],True),(edge['target'],edge.get('target_port',.5),coords[-2:],False)):
                    box=boxes.get(node_id)
                    if box and (abs(point[0]-(box['x']+box['w']*fraction))>.1 or abs(point[1]-(box['y']+(box['h'] if bottom else 0)))>.1):
                        report['findings'].append({'type':'source-timeline-port','id':edge['id']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--png", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--browser-executable", type=Path)
    args = parser.parse_args()
    try:
        outputs = [p.resolve() for p in (args.svg,args.report,args.png,args.source) if p]
        if len(outputs) != len(set(outputs)):
            raise ValueError("Input and output paths must be distinct.")
        with sync_playwright() as p:
            browser = None
            attempts = [{"executable_path": str(args.browser_executable)}] if args.browser_executable else [{},{"channel":"chrome"},{"channel":"msedge"}]
            for options in attempts:
                try:
                    browser = p.chromium.launch(headless=True, **options)
                    break
                except Exception:
                    continue
            if browser is None:
                raise RuntimeError("No Chromium browser available; install Playwright Chromium or use --browser-executable.")
            page = browser.new_page(viewport={"width":1600,"height":1000},device_scale_factor=1)
            page.goto(args.svg.resolve().as_uri())
            page.evaluate("document.fonts.ready")
            report = page.evaluate(AUDIT)
            report["browser"] = browser.version
            if args.source:
                check_source(report,json.loads(args.source.read_text(encoding="utf-8-sig")))
            report["status"] = "fail" if report["findings"] else "pass"
            if args.png:
                args.png.parent.mkdir(parents=True,exist_ok=True)
                w,h = report["canvas"]
                page.set_viewport_size({"width":int(w),"height":min(int(h),1200)})
                page.locator("svg").first.screenshot(path=str(args.png.resolve()))
            browser.close()
        report["visual_review"] = "Inspect the preview separately; these checks do not rate stylistic resemblance."
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        summary={k:report[k] for k in ("status","id","node_count","edge_count","text_count","min_contrast","findings")}
        summary['composition_warnings']=report.get('composition_warnings',[])
        print(json.dumps(summary))
        return 0 if report["status"] == "pass" else 1
    except Exception as error:
        print(f"Browser audit could not complete: {error}",file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
