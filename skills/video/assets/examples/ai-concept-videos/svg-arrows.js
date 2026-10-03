// Browser ES module: import {drawArrow, finishArrows} from './svg-arrows.js'.
// drawArrow accepts a native SVG element or a D3-style fluent selection.
// Keep source/target coordinates semantic; the finisher clips to clear ports and
// selects exact palette paint against actual composited backing regions.
let serial = 0;
export function svgSelection(node) {
  return {append(tag) {const child=document.createElementNS('http://www.w3.org/2000/svg',tag);node.appendChild(child);return svgSelection(child);},
    attr(name,value) {node.setAttribute(name,value);return this;},node() {return node;}};
}
export function drawArrow(g, from, to, color, opacity = 1, width = 3, head = 10) {
  if (g?.nodeType === 1) g=svgSelection(g);
  if (opacity <= .01 || Math.hypot(to.x-from.x,to.y-from.y) < 1) return;
  const group=g.append('g').attr('data-arrow-id','arrow-'+serial++).attr('data-arrow-color',color);
  // Readable arrows use opaque paint. Whole-scene reveal can still animate its
  // parent; alpha is not used as a permanent category hierarchy.
  group.append('path').attr('data-arrow-shaft','true').attr('fill','none')
    .attr('stroke',color).attr('stroke-width',width).attr('stroke-linecap','butt');
  group.append('path').attr('data-arrow-head','true').attr('fill',color).attr('stroke','none');
  group.node().__arrow={from:{...from},to:{...to},head,width};
  position(group.node(),[from,to]);
}
function position(group,points) {
 const {head,width}=group.__arrow,last=points.at(-1),previous=points.at(-2),angle=Math.atan2(last.y-previous.y,last.x-previous.x);
 const size=Math.min(head,Math.hypot(last.x-previous.x,last.y-previous.y)*.7);
 const base={x:last.x-Math.cos(angle)*size,y:last.y-Math.sin(angle)*size},wing=Math.max(3,size*.5);
 group.querySelector('[data-arrow-shaft]').setAttribute('d','M'+[...points.slice(0,-1),base].map(p=>`${p.x},${p.y}`).join('L'));
 group.querySelector('[data-arrow-head]').setAttribute('d',`M${last.x},${last.y}L${base.x-Math.sin(angle)*wing},${base.y+Math.cos(angle)*wing}L${base.x+Math.sin(angle)*wing},${base.y-Math.cos(angle)*wing}Z`);
 group.dataset.arrowPoints=JSON.stringify(points);
}
export function finishArrows(root, {allowed,canvas='#ffffff'}={}) {
 const ctx=document.createElementNS('http://www.w3.org/1999/xhtml','canvas').getContext('2d',{willReadFrequently:true});
 const rgba=value=>{if(!value||value==='none'||value.startsWith('url('))return null;ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);const p=ctx.getImageData(0,0,1,1).data;return [p[0],p[1],p[2],p[3]/255];};
 const lum=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
 const contrast=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
 const blend=(bg,c,a)=>bg.map((v,i)=>v*(1-a)+c[i]*a);
 const opacity=e=>{let value=1;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility!=='visible')return 0;value*=+s.opacity;}return value;};
 const cache=new Map(),surfaces=[];
 for(const e of root.querySelectorAll('rect,circle,ellipse,polygon,path')) {
  if(e.closest('defs,[data-arrow-id],[data-source-preserved]'))continue;
  const s=getComputedStyle(e),c=rgba(s.fill),a=opacity(e),m=e.getScreenCTM();
  if(!c||!a||!m||Math.abs(m.a*m.d-m.b*m.c)<1e-12)continue;
  cache.set(e,{color:c,alpha:c[3]*+s.fillOpacity*a,box:e.getBoundingClientRect(),inverse:m.inverse()});surfaces.push(e);
 }
 const at=(e,p)=>{const v=cache.get(e),b=v.box;return p.x>=b.left&&p.x<=b.right&&p.y>=b.top&&p.y<=b.bottom&&e.isPointInFill(new DOMPoint(p.x,p.y).matrixTransform(v.inverse));};
 const background=p=>{let bg=rgba(canvas).slice(0,3);for(const e of surfaces){if(!at(e,p))continue;const v=cache.get(e);bg=blend(bg,v.color,v.alpha);}return bg;};
 const hsv=c=>{const [r,g,b]=c.slice(0,3).map(v=>v/255),hi=Math.max(r,g,b),lo=Math.min(r,g,b),d=hi-lo;let h=!d?0:hi===r?((g-b)/d+6)%6:hi===g?(b-r)/d+2:(r-g)/d+4;return [h/6,hi?d/hi:0,hi];};
 const bounds=root.getBoundingClientRect();
 for(const group of root.querySelectorAll('[data-arrow-id]')) {
  if(!group.__arrow)continue;
  const m=group.getScreenCTM(),inverse=m.inverse(),screen=p=>new DOMPoint(p.x,p.y).matrixTransform(m),local=p=>new DOMPoint(p.x,p.y).matrixTransform(inverse);
  let start=screen(group.__arrow.from),end=screen(group.__arrow.to);
  const dx=end.x-start.x,dy=end.y-start.y,length=Math.hypot(dx,dy),ux=dx/length,uy=dy/length;
  const bodies=surfaces.filter(e=>{const b=cache.get(e).box;return b.width>12&&b.height>12&&b.width*b.height<bounds.width*bounds.height*.8&&!(at(e,start)&&at(e,end));});
  const source=bodies.filter(e=>at(e,start)),target=bodies.filter(e=>at(e,end));
  const gap=3+group.__arrow.head*.6*Math.hypot(m.a,m.b);
  for(let t=0;t<length*.45&&source.some(e=>at(e,start));t++)start={x:start.x+ux,y:start.y+uy};
  if(source.length)start={x:start.x+ux*gap,y:start.y+uy*gap};
  for(let t=0;t<length*.45&&target.some(e=>at(e,end));t++)end={x:end.x-ux,y:end.y-uy};
  if(target.length)end={x:end.x-ux*gap,y:end.y-uy*gap};
  const blocked=points=>points.slice(1).some((b,i)=>{const a=points[i],n=Math.max(2,Math.ceil(Math.hypot(b.x-a.x,b.y-a.y)/4));for(let j=0;j<=n;j++){const p={x:a.x+(b.x-a.x)*j/n,y:a.y+(b.y-a.y)*j/n};if(bodies.some(e=>at(e,p)))return true;}return false;});
  // Preserve the semantic arrival/departure bearing when detouring. A final
  // vertical elbow beside a horizontal target would point past its silhouette.
  const span=Math.hypot(end.x-start.x,end.y-start.y),stubDistance=Math.min(span/4,Math.max(12,group.__arrow.head*2*Math.hypot(m.a,m.b)));
  const sourceStub={x:start.x+ux*stubDistance,y:start.y+uy*stubDistance},targetStub={x:end.x-ux*stubDistance,y:end.y-uy*stubDistance};
  const join=middle=>[start,sourceStub,...middle,targetStub,end];
  const candidates=[[start,end],join([]),join([{x:sourceStub.x,y:targetStub.y}]),join([{x:targetStub.x,y:sourceStub.y}])];
  for(const body of bodies){const b=cache.get(body).box;for(const y of [b.top-10,b.bottom+10])candidates.push(join([{x:sourceStub.x,y},{x:targetStub.x,y}]));for(const x of [b.left-10,b.right+10])candidates.push(join([{x,y:sourceStub.y},{x,y:targetStub.y}]));}
  const route=candidates.find(p=>!blocked(p)&&p.every(q=>q.x>=bounds.left+2&&q.x<=bounds.right-2&&q.y>=bounds.top+2&&q.y<=bounds.bottom-2));
  if(!route){group.dataset.arrowIssue='No clear route preserves the endpoint bearing; expand its gutter';continue;}
  position(group,route.map(local));
  const samples=[];for(let i=1;i<route.length;i++){const a=route[i-1],b=route[i];for(let t=0;t<=1;t+=.1)samples.push(background({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t}));}
  const preferred=group.dataset.arrowColor,colors=allowed||[preferred,'#000000','#ffffff'];
  const viable=colors.filter(c=>samples.every(bg=>contrast(rgba(c),bg)>=3));
  if(!viable.length){group.dataset.arrowIssue='No paint contrasts with every backing; reroute this relationship';continue;}
  const [h,s,v]=hsv(rgba(preferred));
  const score=c=>{const [ch,cs,cv]=hsv(rgba(c));const hd=s>.12&&cs>.12?Math.min(Math.abs(h-ch),1-Math.abs(h-ch)):(s<=.12&&cs<=.12?0:1);return hd*100+Math.abs(s-cs)+Math.abs(v-cv)*.1;};
  const paint=viable.includes(preferred)?preferred:viable.sort((a,b)=>score(a)-score(b))[0];
  group.querySelector('[data-arrow-shaft]').setAttribute('stroke',paint);group.querySelector('[data-arrow-head]').setAttribute('fill',paint);
  group.dataset.arrowPaint=paint;group.dataset.arrowMinContrast=Math.min(...samples.map(bg=>contrast(rgba(paint),bg)));
 }
}
