/* Audio-clock focus ports and SVG reading-frame diagnostics. No independent timer. */
(()=>{'use strict';
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},mix=(a,b,u)=>a+(b-a)*u;
function overlap(a,b,p=0){return a.x0-p<b.x1&&a.x1+p>b.x0&&a.y0-p<b.y1&&a.y1+p>b.y0;}
function port(box,bounds,obstacles=[],{radius=14,gap=16,side='left'}={}){
 const candidates=[],sides=[side,...['left','right','above','below','above-left','above-right','below-left','below-right'].filter(v=>v!==side)];
 for(const pad of [gap,gap+18,gap+42])for(const direction of sides)for(const f of [.5,.25,.75]){
  const p=direction==='left'?{x:box.x0-radius-pad,y:mix(box.y0,box.y1,f)}:direction==='right'?{x:box.x1+radius+pad,y:mix(box.y0,box.y1,f)}:direction==='above'?{x:mix(box.x0,box.x1,f),y:box.y0-radius-pad}:direction==='below'?{x:mix(box.x0,box.x1,f),y:box.y1+radius+pad}:{x:direction.endsWith('left')?box.x0-radius-pad:box.x1+radius+pad,y:direction.startsWith('above')?box.y0-radius-pad:box.y1+radius+pad};
  const b={x0:p.x-radius-4,x1:p.x+radius+4,y0:p.y-radius-4,y1:p.y+radius+4};
  if(b.x0>=bounds.x0&&b.y0>=bounds.y0&&b.x1<=bounds.x1&&b.y1<=bounds.y1&&!obstacles.some(o=>overlap(b,o,4))&&!overlap(b,box,4))candidates.push({...p,side:direction});
 }
 if(!candidates.length)throw Error('No unobstructed focus port; recompose the target area.');
 return candidates[0];
}
function pose(cues,t,origin,{radius=10,focusRadius=14}={}){
 if(!Array.isArray(cues)||!origin)throw Error('Provide cue ports and an initial pose.');
 let previous=origin;
 for(const cue of cues){
  if(!Number.isFinite(cue.at)||!Number.isFinite(cue.x)||!Number.isFinite(cue.y))throw Error('Cues need finite times and resolved semantic ports.');
  const travel=Math.max(.10,Math.min(.45,cue.travelSeconds||.28)),start=Math.max(0,cue.at-travel);
  if(t<start)return {...previous,radius,target:previous.target||null,moving:false};
  if(t<cue.at){const u=ease((t-start)/Math.max(.001,cue.at-start)),p=along(cue.path||[previous,cue],u);return {...p,radius:6,target:cue.target,moving:true};}
  previous={x:cue.x,y:cue.y,target:cue.target};
  const next=cues[cues.indexOf(cue)+1];
  if(!next||t<Math.max(0,next.at-(next.travelSeconds||.28))){const p=clamp((t-cue.at)/.24);return {...previous,radius:mix(focusRadius,radius,ease(p)),moving:false};}
 }
 return {...previous,radius,moving:false};
}
function along(points,u){const lengths=points.slice(1).map((p,i)=>Math.hypot(p.x-points[i].x,p.y-points[i].y)),total=lengths.reduce((a,b)=>a+b,0);let d=clamp(u)*total;for(let i=0;i<lengths.length;i++){if(d<=lengths[i]||i===lengths.length-1){const f=lengths[i]?d/lengths[i]:1;return{x:mix(points[i].x,points[i+1].x,f),y:mix(points[i].y,points[i+1].y,f)}}d-=lengths[i]}return{...points[0]};}
function visibleAlong(points,u,bounds){
 const lengths=points.slice(1).map((p,i)=>Math.hypot(p.x-points[i].x,p.y-points[i].y)),total=lengths.reduce((a,b)=>a+b,0);let walked=0,best=null;
 for(let i=0;i<lengths.length;i++){
  const a=points[i],b=points[i+1];let lo=0,hi=1;
  for(const [axis,min,max]of [['x','x0','x1'],['y','y0','y1']]){const delta=b[axis]-a[axis];if(Math.abs(delta)<1e-9){if(a[axis]<bounds[min]||a[axis]>bounds[max]){lo=2;break}}else{let left=(bounds[min]-a[axis])/delta,right=(bounds[max]-a[axis])/delta;if(left>right)[left,right]=[right,left];lo=Math.max(lo,left);hi=Math.min(hi,right);}}
  if(lo<=hi){const lower=total?(walked+lo*lengths[i])/total:0,upper=total?(walked+hi*lengths[i])/total:1,progress=Math.max(lower,Math.min(clamp(u),upper)),distance=Math.abs(progress-clamp(u));if(!best||distance<best.distance)best={progress,distance};}
  walked+=lengths[i];
 }
 if(!best){if(points.length===1&&points[0].x>=bounds.x0&&points[0].x<=bounds.x1&&points[0].y>=bounds.y0&&points[0].y<=bounds.y1)return{...points[0],progress:0,limited:false};throw Error('The camera contains no point on the clear guide route; recompose the pan.');}
 return{...along(points,best.progress),progress:best.progress,limited:best.distance>1e-8};
}
function segmentHits(a,b,box){let lo=0,hi=1;for(const [key,min,max] of [['x','x0','x1'],['y','y0','y1']]){const d=b[key]-a[key];if(Math.abs(d)<1e-8){if(a[key]<=box[min]||a[key]>=box[max])return false;}else{let v=(box[min]-a[key])/d,w=(box[max]-a[key])/d;if(v>w)[v,w]=[w,v];lo=Math.max(lo,v);hi=Math.min(hi,w);if(lo>=hi)return false}}return true;}
function route(a,b,obstacles,bounds,{radius=10,gap=6}={}){
 const pad=radius+gap,blocks=obstacles.map(o=>({x0:o.x0-pad,x1:o.x1+pad,y0:o.y0-pad,y1:o.y1+pad}));
 const safe=points=>points.every(p=>p.x>=bounds.x0+radius&&p.x<=bounds.x1-radius&&p.y>=bounds.y0+radius&&p.y<=bounds.y1-radius)&&points.slice(1).every((p,i)=>!blocks.some(o=>segmentHits(points[i],p,o)));
 const choices=[[a,b],[a,{x:a.x,y:b.y},b],[a,{x:b.x,y:a.y},b]];
 for(const o of blocks){for(const y of [o.y0-1,o.y1+1])choices.push([a,{x:a.x,y}, {x:b.x,y},b]);for(const x of [o.x0-1,o.x1+1])choices.push([a,{x,y:a.y},{x,y:b.y},b]);}
 const length=p=>p.slice(1).reduce((v,q,i)=>v+Math.hypot(q.x-p[i].x,q.y-p[i].y),0),valid=choices.filter(safe).sort((p,q)=>length(p)-length(q));
 if(valid.length)return valid[0].map(p=>({x:p.x,y:p.y}));
 // Visibility-graph fallback is computed once, outside the frame loop.
 const nodes=[a,b];for(const o of blocks)for(const x of [o.x0-1,o.x1+1])for(const y of [o.y0-1,o.y1+1]){const p={x,y};if(safe([p]))nodes.push(p);}
 const distances=nodes.map(()=>Infinity),parents=nodes.map(()=>-1),done=new Set();distances[0]=0;
 for(let count=0;count<nodes.length;count++){let k=-1;for(let j=0;j<nodes.length;j++)if(!done.has(j)&&(k<0||distances[j]<distances[k]))k=j;if(k<0||!Number.isFinite(distances[k]))break;if(k===1){const result=[];for(let j=1;j>=0;j=parents[j])result.unshift({x:nodes[j].x,y:nodes[j].y});return result;}done.add(k);for(let j=0;j<nodes.length;j++)if(!done.has(j)&&safe([nodes[k],nodes[j]])){const distance=distances[k]+Math.hypot(nodes[j].x-nodes[k].x,nodes[j].y-nodes[k].y);if(distance<distances[j]){distances[j]=distance;parents[j]=k;}}}
 throw Error('No clear focus route; reserve a travel lane or recompose.');
}
function rect(element){const b=element.getBoundingClientRect();return{x0:b.left,y0:b.top,x1:b.right,y1:b.bottom};}
function visible(element,root){for(let p=element;p&&p!==root.parentElement;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<.95)return false}return true;}
function inClips(mark,point,root){for(let node=mark;node&&node!==root.parentElement;node=node.parentElement){const id=(getComputedStyle(node).clipPath||'').match(/#([^)"]+)/)?.[1];if(!id)continue;const clip=document.getElementById(id);if(!clip||clip.getAttribute('clipPathUnits')==='objectBoundingBox')continue;const matrix=node.getScreenCTM();if(!matrix)continue;const p=new DOMPoint(point.x,point.y).matrixTransform(matrix.inverse()),shapes=[...clip.children].filter(e=>typeof e.isPointInFill==='function');if(shapes.length&&!shapes.some(e=>e.isPointInFill(p)))return false;}return true;}
function audit(root,{checkMarks=true,padding=5}={}){
 const frame=rect(root),texts=[...root.querySelectorAll('text')].filter(e=>e.textContent.trim()&&visible(e,root)).map(e=>({element:e,text:e.textContent.trim(),box:rect(e)})).filter(e=>e.box.x1>frame.x0&&e.box.x0<frame.x1&&e.box.y1>frame.y0&&e.box.y0<frame.y1),issues=[];
 for(const a of texts)if(a.box.x0<frame.x0-1||a.box.x1>frame.x1+1||a.box.y0<frame.y0-1||a.box.y1>frame.y1+1)issues.push({kind:'clipped-text',text:a.text});
 for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(overlap(texts[i].box,texts[j].box,padding))issues.push({kind:'text-overlap',a:texts[i].text,b:texts[j].text});
 if(checkMarks){
  const marks=[...root.querySelectorAll('path,line,polyline,polygon,rect,circle')].filter(e=>!e.closest('defs')&&!e.closest('[data-audit-ignore="true"]')&&e.id!=='guide'&&visible(e,root)&&getComputedStyle(e).stroke!=='none'&&typeof e.getTotalLength==='function');
  for(const mark of marks){const b=rect(mark),near=texts.filter(t=>overlap(t.box,b,2));if(!near.length)continue;const len=mark.getTotalLength(),matrix=mark.getScreenCTM();if(!matrix)continue;
   for(const a of near){let hit=false;for(let d=0;d<=len;d+=Math.max(3,len/1600)){const q=mark.getPointAtLength(d),p=new DOMPoint(q.x,q.y).matrixTransform(matrix);if(p.x>a.box.x0-2&&p.x<a.box.x1+2&&p.y>a.box.y0-2&&p.y<a.box.y1+2&&inClips(mark,p,root)){hit=true;break}}
    if(hit)issues.push({kind:'stroke-through-text',text:a.text,mark:mark.getAttribute('data-focus-id')||mark.id||mark.tagName});
   }
  }
 }
 const style=globalThis.LineWorldTheme?.audit?.(root);if(style)issues.push(...style.violations);
 return {ok:!issues.length,issues,textCount:texts.length};
}
globalThis.LineWorldFocus=Object.freeze({port,pose,route,along,visibleAlong,overlap,audit});
})();
