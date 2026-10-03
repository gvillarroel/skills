#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Rendered object, connector, color-application, and text-contrast checks."""

QUALITY = r"""({report}) => {
 const root=document.querySelector('svg'), issues=[], contacts=[], internalContacts=[], openTerminals=[], contrasts=[], colorOwners=[];
 const all=[...root.querySelectorAll('*')], order=new Map(all.map((e,i)=>[e,i]));
 const outside=e=>!!e.closest('defs,clipPath,mask,marker,pattern,symbol');
 const canvas=document.createElement('canvas');canvas.width=canvas.height=1;
 const ctx=canvas.getContext('2d',{willReadFrequently:true});
 function rgba(value) {
   if(!value||value==='none'||value.startsWith('url('))return null;
   ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);
   const p=ctx.getImageData(0,0,1,1).data;return [p[0],p[1],p[2],p[3]/255];
 }
 function opacity(e) {
   let result=1;
   for(let n=e;n&&n instanceof SVGElement;n=n.parentElement){
     const s=getComputedStyle(n);if(s.display==='none'||s.visibility!=='visible')return 0;
     result*=+s.opacity;
   }return result;
 }
 const geometry=all.filter(e=>e instanceof SVGGeometryElement&&!outside(e)&&opacity(e)>0);
 function local(e,p){return new DOMPoint(p.x,p.y).matrixTransform(e.getScreenCTM().inverse());}
 function paints(e,p,channel='fill') {
   const s=getComputedStyle(e), color=rgba(s.getPropertyValue(channel));
   if(!color||color[3]===0)return false;
   if(channel==='stroke'&&parseFloat(s.strokeWidth)<=0)return false;
   const b=e.getBoundingClientRect();
   if(p.x<b.left-4||p.x>b.right+4||p.y<b.top-4||p.y>b.bottom+4)return false;
   const q=local(e,p);
   return channel==='fill'?e.isPointInFill(q):e.isPointInStroke(q);
 }
 function occluded(e,p) {
   return geometry.some(g=>order.get(g)>order.get(e)&&opacity(g)>.999&&
     +getComputedStyle(g).fillOpacity>.999&&rgba(getComputedStyle(g).fill)?.[3]>.999&&paints(g,p));
 }
 function samples(e,channel) {
   const b=e.getBBox(),m=e.getScreenCTM(),out=[];
   if(channel==='stroke'&&e.getTotalLength){
     const length=e.getTotalLength();
     for(let i=0;i<32;i++){const p=e.getPointAtLength(length*(i+.25)/32);out.push(new DOMPoint(p.x,p.y).matrixTransform(m));}
   } else for(const u of [.15,.35,.5,.65,.85])for(const v of [.15,.35,.5,.65,.85])
     out.push(new DOMPoint(b.x+b.width*u,b.y+b.height*v).matrixTransform(m));
   return out.filter(p=>paints(e,p,channel));
 }
 const marks=[...root.querySelectorAll('[data-color-concept][data-color-channel]')].filter(e=>e instanceof SVGGeometryElement);
 for(const e of marks) {
   const channel=e.dataset.colorChannel;
   if(!['fill','stroke'].includes(channel)||outside(e)||opacity(e)===0)continue;
   const points=samples(e,channel),visible=points.filter(p=>!occluded(e,p)).length;
   if(!visible)issues.push({kind:'semantic-color-occluded',concept:e.dataset.colorConcept,panel:e.closest('[data-panel-id]')?.dataset.panelId||null});
 }
 const nodes=[...root.querySelectorAll('[data-node-id]')].filter(e=>e instanceof SVGGeometryElement&&!outside(e));
 function nodeKey(e){return (e.closest('[data-panel-id]')?.dataset.panelId||'')+'.'+e.dataset.nodeId;}
 const byNode=new Map(nodes.map(e=>[nodeKey(e),e]));
 if(byNode.size!==nodes.length)issues.push({kind:'duplicate-object-id'});
 const rootMatrix=root.getScreenCTM();
 const toScreen=p=>new DOMPoint(p[0],p[1]).matrixTransform(rootMatrix);
 for(const p of report.panels||[])for(const [id,obj] of Object.entries(p.mappedObjects||{})) {
   const node=byNode.get(p.id+'.'+id);
   if(!node){issues.push({kind:'object-geometry-missing',object:p.id+'.'+id});continue;}
   const b=node.getBoundingClientRect(),[x,y,w,h]=obj.box,a=toScreen([x,y]),z=toScreen([x+w,y+h]);
   if(Math.max(Math.abs(b.left-a.x),Math.abs(b.top-a.y),Math.abs(b.right-z.x),Math.abs(b.bottom-z.y))>1.5)
     issues.push({kind:'object-geometry-mismatch',object:p.id+'.'+id});
 }
 const neutral=c=>Math.max(...c.slice(0,3))-Math.min(...c.slice(0,3))<=20;
 function tint(actual,base) {
   // Canonical colorset2 highlight pairs are finite tokens, not arbitrary RGB blends.
   const highlights={'#9e1b32':'#ffccd5','#007298':'#cdf3ff','#e77204':'#ffe5cc','#45842a':'#dbffcc','#652f6c':'#f9ccff','#f1c319':'#fff4cc'};
   const hex=c=>'#'+c.slice(0,3).map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
   if(highlights[hex(base)]===hex(actual))return true;
   const delta=base.slice(0,3).map(v=>255-v),den=delta.reduce((s,v)=>s+v*v,0);
   const t=den?delta.reduce((s,v,i)=>s+v*(255-actual[i]),0)/den:0;
   if(t>=0&&t<=1.001&&actual.slice(0,3).every((v,i)=>Math.abs(v-(255-t*delta[i]))<=5))return true;
   const denDark=base.slice(0,3).reduce((s,v)=>s+v*v,0);
   const shade=denDark?base.slice(0,3).reduce((s,v,i)=>s+v*actual[i],0)/denDark:0;
   return shade>=0&&shade<=1.001&&actual.slice(0,3).every((v,i)=>Math.abs(v-shade*base[i])<=5);
 }
 for(const node of nodes) {
   const cid=node.dataset.conceptId,expected=report.semanticColors?.[cid];
   if(!cid||!expected)continue;
   const s=getComputedStyle(node),fill=rgba(s.fill),base=rgba(expected);
   const own=marks.filter(e=>e.closest('[data-panel-id]')===node.closest('[data-panel-id]')&&
       e.dataset.colorConcept===cid&&(e===node||e.dataset.colorOwner===node.dataset.nodeId));
   if(!own.length)issues.push({kind:'semantic-color-owner-missing',object:nodeKey(node),concept:cid});
   if(fill&&fill[3]>0&&!neutral(fill)&&!tint(fill,base))
     issues.push({kind:'semantic-color-conflicting-fill',object:nodeKey(node),concept:cid,fill:s.fill,expected});
   colorOwners.push({object:nodeKey(node),concept:cid,fill:s.fill,accentCount:own.length});
 }
 const paths=[...root.querySelectorAll('[data-relation-id] path,[data-connector]')]
   .filter(e=>e instanceof SVGGeometryElement&&!outside(e)&&opacity(e)>0);
 const labels=[...root.querySelectorAll('text')].filter(e=>!outside(e)&&opacity(e)>0).map(e=>({e,box:e.getBoundingClientRect()}));
 function strictlyInside(node,p) {
   const q=local(node,p),b=node.getBBox(),m=node.getScreenCTM(),pad=2.5/Math.max(.01,Math.hypot(m.a,m.b));
   return q.x>b.x+pad&&q.x<b.x+b.width-pad&&q.y>b.y+pad&&q.y<b.y+b.height-pad&&node.isPointInFill(q);
 }
 const contours=new Map();
 function contour(node) {
   if(contours.has(node))return contours.get(node);
   const length=node.getTotalLength(),m=node.getScreenCTM(),count=Math.max(8,Math.ceil(length*Math.hypot(m.a,m.b)/2)),points=[];
   for(let i=0;i<=count;i++){const p=node.getPointAtLength(length*i/count);points.push(new DOMPoint(p.x,p.y).matrixTransform(m));}
   contours.set(node,points);return points;
 }
 function boundaryDistance(node,q) {
   const points=contour(node);let best=Infinity;
   for(let j=1;j<points.length;j++){
     const a=points[j-1],b=points[j],dx=b.x-a.x,dy=b.y-a.y,den=dx*dx+dy*dy;
     const t=den?Math.max(0,Math.min(1,((q.x-a.x)*dx+(q.y-a.y)*dy)/den)):0;
     best=Math.min(best,Math.hypot(q.x-a.x-t*dx,q.y-a.y-t*dy));
   }return best;
 }
 function checkInternalContact(path,id,length,m) {
   const panel=path.closest('[data-panel-id]'),scope=nodes.filter(n=>n.closest('[data-panel-id]')===panel);
   const screenAt=t=>{const p=path.getPointAtLength(t);return new DOMPoint(p.x,p.y).matrixTransform(m);};
   for(let end=0;end<2;end++) {
     const explicit=path.getAttribute(end?'data-to-node':'data-from-node');
     const open=path.getAttribute(end?'data-open-end':'data-open-start');
     if(open?.trim()&&!explicit){openTerminals.push({relation:id,end,reason:open.trim()});continue;}
     // A background center-to-center edge is acceptable only when its visible
     // portion actually emerges at a real opaque node surface.
     let t=end?length:0,q=screenAt(t),step=1/Math.max(.01,Math.hypot(m.a,m.b));
     while(occluded(path,q)&&t>=0&&t<=length){t+=end?-step:step;q=screenAt(Math.max(0,Math.min(length,t)));}
     if(t<0||t>length){issues.push({kind:'connector-entirely-obscured',relation:id,end});continue;}
     const z=screenAt(Math.max(0,Math.min(length,t+(end?-1:1)*5*step)));
     let candidates=scope.filter(n=>!explicit||n.dataset.nodeId===explicit).map(n=>({n,error:boundaryDistance(n,q)}));
     let touching=candidates.filter(c=>c.error<=1.5);
     if(!explicit&&touching.some(c=>c.n.dataset.nodeKind!=='container'))touching=touching.filter(c=>c.n.dataset.nodeKind!=='container');
     if(touching.length!==1){issues.push({kind:touching.length?'connector-ambiguous-contact':'connector-floating-endpoint',relation:id,end,
       expected:explicit||null,nearestError:candidates.length?Math.min(...candidates.map(c=>c.error)):null});continue;}
     const {n,error}=touching[0],outside=!n.isPointInFill(local(n,z))&&boundaryDistance(n,z)>.2;
     internalContacts.push({relation:id,end,object:nodeKey(n),error,outside});
     if(!outside)issues.push({kind:'connector-wrong-side-contact',relation:id,end,object:nodeKey(n)});
   }
 }
 const sampled=[];
 for(const path of paths) {
   const length=path.getTotalLength(),m=path.getScreenCTM(),id=path.closest('[data-relation-id]')?.dataset.relationId||
     (path.closest('[data-panel-id]')?.dataset.panelId||'source')+':'+(path.id||'wire-'+paths.indexOf(path));
   const hits=new Set(),textHits=new Set(),points=[];
   const steps=Math.max(1,Math.ceil(length*Math.hypot(m.a,m.b)/2));
   for(let i=0;i<=steps;i++) {
     const p=path.getPointAtLength(length*i/steps),q=new DOMPoint(p.x,p.y).matrixTransform(m);
     if(i%5===0||i===steps)points.push(q);
     for(const node of nodes)if(node.dataset.nodeKind!=='container'&&strictlyInside(node,q)&&!occluded(path,q))hits.add(nodeKey(node));
     for(const t of labels)if(q.x>t.box.left+2&&q.x<t.box.right-2&&q.y>t.box.top+2&&q.y<t.box.bottom-2&&!occluded(path,q))textHits.add(t.e.textContent.trim());
   }
   for(const object of hits)issues.push({kind:'connector-object-intrusion',relation:id,object});
   for(const label of textHits)issues.push({kind:'connector-text-interference',relation:id,label});
   sampled.push({path,points,id});
   const group=path.closest('[data-relation-id]');
   if(!group||!group.hasAttribute('data-endpoints')){checkInternalContact(path,id,length,m);continue;}
   const endpoints=JSON.parse(group.dataset.endpoints);
   for(let i=0;i<2;i++) {
     const binding=endpoints[i];
     if(!binding){issues.push({kind:'connector-unbound-endpoint',relation:id,end:i});continue;}
     const node=byNode.get(binding.object);
     if(!node){issues.push({kind:'connector-endpoint-object-missing',relation:id,object:binding.object});continue;}
     const t=i?length:0,p=path.getPointAtLength(t),q=new DOMPoint(p.x,p.y).matrixTransform(m);
     const near=path.getPointAtLength(i?Math.max(0,length-5):Math.min(length,5)),z=new DOMPoint(near.x,near.y).matrixTransform(m);
     const b=node.getBoundingClientRect(), normals={left:[-1,0],right:[1,0],top:[0,-1],bottom:[0,1]},normal=normals[binding.side];
     const target={left:[b.left,(b.top+b.bottom)/2],right:[b.right,(b.top+b.bottom)/2],top:[(b.left+b.right)/2,b.top],bottom:[(b.left+b.right)/2,b.bottom]}[binding.side];
     const error=Math.hypot(q.x-target[0],q.y-target[1]),outward=(z.x-q.x)*normal[0]+(z.y-q.y)*normal[1];
     contacts.push({relation:id,end:i,object:binding.object,side:binding.side,error,outward});
     if(error>1.5||outward<=0)issues.push({kind:'connector-bad-contact',relation:id,end:i,object:binding.object,error,outward});
   }
 }
 function segments(points) {
   const clean=[];
   for(const p of points){
     if(clean.length>=2){const a=clean.at(-2),b=clean.at(-1);
       if(Math.abs((b.x-a.x)*(p.y-b.y)-(b.y-a.y)*(p.x-b.x))<.001)clean.pop();}
     clean.push(p);
   }return clean.slice(1).map((p,i)=>[clean[i],p]);
 }
 function crossing(a,b,c,d) {
   const x=b.x-a.x,y=b.y-a.y,u=d.x-c.x,v=d.y-c.y,den=x*v-y*u;
   if(Math.abs(den)<.001) {
     if(Math.abs((c.x-a.x)*y-(c.y-a.y)*x)>.1)return null;
     const axis=Math.abs(x)>Math.abs(y)?'x':'y';
     const overlap=Math.min(Math.max(a[axis],b[axis]),Math.max(c[axis],d[axis]))-Math.max(Math.min(a[axis],b[axis]),Math.min(c[axis],d[axis]));
     return overlap>12?'overlap':null;
   }
   const t=((c.x-a.x)*v-(c.y-a.y)*u)/den,s=((c.x-a.x)*y-(c.y-a.y)*x)/den;
   return t>.01&&t<.99&&s>.01&&s<.99?'crossing':null;
 }
 for(let i=0;i<sampled.length;i++)for(let j=i+1;j<sampled.length;j++) {
   const a=sampled[i],b=sampled[j],kinds=new Set();
   for(const [p,q] of segments(a.points))for(const [r,s] of segments(b.points)){
     const kind=crossing(p,q,r,s);if(kind)kinds.add(kind);
   }
   for(const kind of kinds)issues.push({kind:'connector-'+kind,relations:[a.id,b.id]});
 }
 // Evaluate actual background paint under text, excluding the text glyph itself.
 function luminance(c){return c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
 for(const text of root.querySelectorAll('text')) {
   if(outside(text)||opacity(text)===0||text.closest('[data-brand-artwork]'))continue;
   const s=getComputedStyle(text),ink=rgba(s.fill);
   if(!ink){issues.push({kind:'contrast-complex-paint',label:text.textContent.trim()});continue;}
   const b=text.getBoundingClientRect(),p={x:(b.left+b.right)/2,y:(b.top+b.bottom)/2};
   if([.2,.5,.8].every(u=>occluded(text,{x:b.left+b.width*u,y:p.y})))
     issues.push({kind:'text-obscured',label:text.textContent.trim()});
   let bg=[255,255,255];
   for(const g of geometry) {
     if(order.get(g)>=order.get(text))continue;
     const gs=getComputedStyle(g);
     if(gs.fill.startsWith('url(')&&g.isPointInFill(local(g,p)))
       issues.push({kind:'contrast-complex-background',label:text.textContent.trim()});
     if(!paints(g,p))continue;
     const c=rgba(gs.fill),alpha=c[3]*+gs.fillOpacity*opacity(g);
     bg=bg.map((v,i)=>c[i]*alpha+v*(1-alpha));
   }
   const alpha=ink[3]*+s.fillOpacity*opacity(text),fg=bg.map((v,i)=>ink[i]*alpha+v*(1-alpha));
   const a=luminance(fg),z=luminance(bg),ratio=(Math.max(a,z)+.05)/(Math.min(a,z)+.05);
   const m=text.getScreenCTM(),size=parseFloat(s.fontSize)*Math.hypot(m.c,m.d);
   const threshold=size>=24||(size>=56/3&&parseInt(s.fontWeight)>=700)?3:4.5;
   const record={label:text.textContent.trim(),ratio,threshold};contrasts.push(record);
   if(ratio+1e-9<threshold)issues.push({kind:'text-low-contrast',...record});
 }
 return {issues,connectorCount:paths.length,contacts,internalContacts,openTerminals,colorOwners,contrasts};
}"""


MEASURE = r"""() => {
 const root=document.querySelector('svg'),r=root.getBoundingClientRect(),objects={},ports={};
 for(const e of root.querySelectorAll('[data-node-id]')) {
   if(e.closest('defs,clipPath,mask,marker,pattern,symbol'))continue;
   const id=e.dataset.nodeId;
   if(!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id)||id.length>64||objects[id])throw new Error('Invalid or duplicate data-node-id: '+id);
   if(!['rect','circle','ellipse'].includes(e.tagName))throw new Error('Use a rect/circle/ellipse connector enclosure for '+id);
   const m=e.getScreenCTM();
   if(Math.abs(m.b)>.00001||Math.abs(m.c)>.00001||m.a<=0||m.d<=0)throw new Error('Use an axis-aligned connector enclosure for '+id);
   const b=e.getBoundingClientRect(),box=[(b.x-r.x)/r.width,(b.y-r.y)/r.height,b.width/r.width,b.height/r.height];
   if(box[2]<=0||box[3]<=0||box[0]<-.00001||box[1]<-.00001||box[0]+box[2]>1.00001||box[1]+box[3]>1.00001)throw new Error('Object leaves its viewBox: '+id);
   const kind=e.dataset.nodeKind||'node';
   if(!['node','container'].includes(kind))throw new Error('Invalid node kind: '+id);
   objects[id]={box,kind,shape:e.tagName==='rect'?'rect':'ellipse'};
   for(const side of ['left','right','top','bottom'])ports[id+'-'+side]={object:id,side};
 }
 if(!Object.keys(objects).length)throw new Error('Tag semantic shapes with data-node-id before measuring');
 const routingObstacles=[];
 for(const e of root.querySelectorAll('text,[data-connector]')) {
   if(e.closest('defs,clipPath,mask,marker,pattern,symbol'))continue;
   const b=e.getBoundingClientRect(),left=Math.max(r.left,b.left-1),top=Math.max(r.top,b.top-1),
     right=Math.min(r.right,b.right+1),bottom=Math.min(r.bottom,b.bottom+1);
   if(right>left&&bottom>top)routingObstacles.push([(left-r.left)/r.width,(top-r.top)/r.height,(right-left)/r.width,(bottom-top)/r.height]);
 }
 return {objects,ports,routingObstacles};
}"""
