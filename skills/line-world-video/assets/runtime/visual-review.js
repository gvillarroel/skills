/* Read-only diagnostics for a rendered SVG. The parent controls the clock. */
(()=>{'use strict';
const rect=e=>{const b=e.getBoundingClientRect();return{x0:b.left,y0:b.top,x1:b.right,y1:b.bottom}};
const shown=(e,root)=>{for(let n=e;n&&n!==root.parentElement;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<.05)return false}return true};
const intersects=(a,b)=>a.x0<b.x1&&a.x1>b.x0&&a.y0<b.y1&&a.y1>b.y0;
const label=e=>e.getAttribute('data-review-id')||e.closest('[data-focus-id]')?.getAttribute('data-focus-id')||e.closest('[data-media-id]')?.getAttribute('data-media-id')||e.id||e.textContent.trim().slice(0,90)||e.tagName;
const circleRect=(p,r,b)=>Math.hypot(p.x-Math.max(b.x0,Math.min(p.x,b.x1)),p.y-Math.max(b.y0,Math.min(p.y,b.y1)))<r;
const hiddenPath=(e,s)=>e.tagName.toLowerCase()==='path'&&s.fill==='none'&&s.strokeDasharray!=='none'&&Math.abs(parseFloat(s.strokeDashoffset)||0)>=e.getTotalLength()-.01;
function guide(root,{selector='#guide',gap=3}={}){
 const e=root.querySelector(selector);if(!e)return{issues:[{kind:'missing-guide',target:selector}],visible:false};
 if(!shown(e,root))return{issues:[],visible:false};
 const b=rect(e),s=getComputedStyle(e),r=Math.max(b.x1-b.x0,b.y1-b.y0)/2+(parseFloat(s.strokeWidth)||0)/2+gap,p={x:(b.x0+b.x1)/2,y:(b.y0+b.y1)/2},frame=rect(root),issues=[];
 if(p.x-r<frame.x0||p.x+r>frame.x1||p.y-r<frame.y0||p.y+r>frame.y1)issues.push({kind:'clipped-guide',target:selector,x:p.x,y:p.y,radius:r});
 for(const item of root.querySelectorAll('text,rect,circle,[data-focus-obstacle],image')){
  if(item===e||item.closest('defs')||item.closest('[data-review-ignore="true"]')||!shown(item,root))continue;
  const q=rect(item);if(q.x1<=q.x0||q.y1<=q.y0||!intersects(q,frame))continue;
  if(item.tagName.toLowerCase()!=='text'&&(q.x1-q.x0)*(q.y1-q.y0)>(frame.x1-frame.x0)*(frame.y1-frame.y0)*.8)continue;
  const visibleBox={x0:Math.max(q.x0,frame.x0),x1:Math.min(q.x1,frame.x1),y0:Math.max(q.y0,frame.y0),y1:Math.min(q.y1,frame.y1)};
  const hit=item.tagName.toLowerCase()==='circle'?Math.hypot(p.x-(q.x0+q.x1)/2,p.y-(q.y0+q.y1)/2)<r+Math.max(q.x1-q.x0,q.y1-q.y0)/2:circleRect(p,r,visibleBox);
  if(hit)issues.push({kind:item.tagName.toLowerCase()==='text'?'guide-over-text':item.tagName.toLowerCase()==='image'?'guide-over-image':'guide-over-mark',target:label(item)});
 }
 return{issues,visible:true,x:p.x,y:p.y,radius:r-gap};
}
function reading(root,{inset=36,minFont=24,fontRatio=1.12,dividerGap=12}={}){
 const frame=rect(root),issues=[],fonts=[],groups=new Map(),bounds=[];
 for(const e of root.querySelectorAll('text')){
  if(!e.textContent.trim()||!shown(e,root))continue;const b=rect(e);if(!intersects(b,frame))continue;
  const m=e.getScreenCTM(),s=getComputedStyle(e),px=(parseFloat(s.fontSize)||0)*(m?Math.hypot(m.c,m.d):1),name=label(e);fonts.push({target:name,pixels:+px.toFixed(2)});
  if(px<minFont)issues.push({kind:'small-text',target:name,pixels:+px.toFixed(2),minimum:minFont,severity:'advisory'});
  if(b.x0<frame.x0+inset||b.x1>frame.x1-inset||b.y0<frame.y0+inset||b.y1>frame.y1-inset)issues.push({kind:'text-near-edge',target:name,severity:'advisory'});
  const id=e.getAttribute('data-review-font-group');if(id){if(!groups.has(id))groups.set(id,[]);groups.get(id).push(px)}
  bounds.push({target:name,box:b});
 }
 for(const [name,values] of groups){const ratio=Math.max(...values)/Math.min(...values);if(ratio>fontRatio)issues.push({kind:'inconsistent-peer-fonts',target:name,ratio:+ratio.toFixed(3),severity:'advisory'});}
 const dividers=[...root.querySelectorAll('[data-divider]')].filter(e=>shown(e,root)).map(rect);
 for(const e of root.querySelectorAll('rect,circle,[data-focus-obstacle],image')){
  if(!shown(e,root)||e.closest('[data-review-ignore="true"]'))continue;const b=rect(e);if(!intersects(b,frame))continue;
  if(e.tagName.toLowerCase()==='image'&&(b.x0<frame.x0+inset||b.x1>frame.x1-inset||b.y0<frame.y0+inset||b.y1>frame.y1-inset))issues.push({kind:'image-near-edge',target:label(e),severity:'advisory'});
  for(const d of dividers){let distance=Infinity;if(d.y1-d.y0<3&&b.x0<d.x1&&b.x1>d.x0)distance=Math.min(Math.abs(b.y0-d.y0),Math.abs(b.y1-d.y0));if(d.x1-d.x0<3&&b.y0<d.y1&&b.y1>d.y0)distance=Math.min(Math.abs(b.x0-d.x0),Math.abs(b.x1-d.x0));if(distance<dividerGap)issues.push({kind:'mark-near-divider',target:label(e),gap:+distance.toFixed(2),minimum:dividerGap,severity:'advisory'});}
 }
 const ordinary=LineWorldFocus.audit(root);return{issues:[...ordinary.issues,...issues],fontMinimum:fonts.length?Math.min(...fonts.map(f=>f.pixels)):null,fontMaximum:fonts.length?Math.max(...fonts.map(f=>f.pixels)):null,textCount:fonts.length,fonts};
}
function content(root){
 const frame=rect(root),fw=frame.x1-frame.x0,fh=frame.y1-frame.y0;
 const items=[...root.querySelectorAll('[data-content-anchor],text,rect,circle,ellipse,polygon,path,image')],small=[];let anchors=0;
 for(const e of items){
  if(e.closest('#guide,#guide-dot,#attention-dot,defs,[data-divider],[data-content-ignore="true"],[data-content-role="background"]')||e.matches('.panel-surface,.panel-boundary,.guide-line,[data-port-obstacle]'))continue;
  const b=rect(e),w=b.x1-b.x0,h=b.y1-b.y0;if(!intersects(b,frame)||w<=0||h<=0||w*h>fw*fh*.8)continue;
  if(!shown(e,root))continue;
  let opacity=1;for(let n=e;n&&n!==root.parentElement;n=n.parentElement)opacity*=+getComputedStyle(n).opacity;if(opacity<.25)continue;
  const fraction=Math.max(0,Math.min(b.x1,frame.x1)-Math.max(b.x0,frame.x0))*Math.max(0,Math.min(b.y1,frame.y1)-Math.max(b.y0,frame.y0))/(w*h);
  const s=getComputedStyle(e),tag=e.tagName.toLowerCase(),text=tag==='text';
  if(w<fw*.008||h<fh*.008){if(['circle','ellipse','rect'].includes(tag)&&w>1&&h>1&&((s.stroke!=='none'&&+s.strokeOpacity>0)||(s.fill!=='none'&&s.fill!=='rgb(255, 255, 255)'&&+s.fillOpacity>0)))small.push(b);continue;}
  if(hiddenPath(e,s))continue;
  if(fraction<(text?.85:.5)||text&&!e.textContent.trim())continue;
  const explicit=e.hasAttribute('data-content-anchor');
  if(explicit&&!['text','rect','circle','ellipse','polygon','path','image'].includes(tag)){
   const painted=[...e.querySelectorAll('text,rect,circle,path,image')].some(child=>{if(!shown(child,root)||!intersects(rect(child),frame)||hiddenPath(child,getComputedStyle(child)))return false;let a=1;for(let n=child;n&&n!==root.parentElement;n=n.parentElement)a*=+getComputedStyle(n).opacity;return a>=.25});if(!painted)continue;
  }
  if(!explicit&&tag!=='image'&&!text&&(s.stroke==='none'||+s.strokeOpacity===0)&&(s.fill==='none'||s.fill==='rgb(255, 255, 255)'||+s.fillOpacity===0))continue;
  return{visibleAnchors:1,empty:false,capped:true,anchor:label(e)};
 }
 if(small.length>=8&&Math.max(...small.map(b=>b.x1))-Math.min(...small.map(b=>b.x0))>=fw*.1&&Math.max(...small.map(b=>b.y1))-Math.min(...small.map(b=>b.y0))>=fh*.1)return{visibleAnchors:1,empty:false,capped:true,anchor:'visible-observation-field'};
 return{visibleAnchors:anchors,empty:anchors===0,capped:true};
}
window.LineWorldVisualReview=Object.freeze({guide,reading,content});
})();
