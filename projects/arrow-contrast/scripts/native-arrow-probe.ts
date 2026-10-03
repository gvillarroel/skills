// Browser evaluation helper for this project's native ECharts evidence.
// Used with Node 24 --experimental-strip-types and Playwright.
export function measureNativeArrows(svg, family) {
  const color=s=>{const c=s.match(/[\d.]+/g)?.map(Number);return c?.length>=3?c.slice(0,3):null;};
  const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const alpha=e=>{let a=1;for(let p=e;p;p=p.parentElement)a*=Number(getComputedStyle(p).opacity);return a;};
  const all=[...svg.querySelectorAll('path')].filter(e=>!e.closest('defs'));
  const heads=all.filter(e=>/^M0 0L/.test(e.getAttribute('d'))&&color(getComputedStyle(e).fill));
  const shafts=all.filter(e=>getComputedStyle(e).fill==='none'&&getComputedStyle(e).stroke!=='none'&&
    (family==='graph'?e.getAttribute('ecmeta_series_index')==='0':/[Qq]/.test(e.getAttribute('d'))));
  const bodies=[...svg.querySelectorAll('path,rect,circle,polygon')].filter(e=>!e.closest('defs')&&!heads.includes(e)&&color(getComputedStyle(e).fill));
  const surface=(p,owner)=>{let bg=[255,255,255],covered=[];for(const body of bodies){if(body===owner||!body.isPointInFill(p.matrixTransform(body.getScreenCTM().inverse())))continue;const s=getComputedStyle(body),c=color(s.fill),a=alpha(body)*Number(s.fillOpacity);bg=bg.map((v,i)=>v*(1-a)+c[i]*a);if(body.tagName!=='rect')covered.push(body.tagName);}return {bg,covered};};
  const records=[];
  for(const [kind,elements] of [['shaft',shafts],['head',heads]])for(const e of elements){const css=getComputedStyle(e),paint=color(css[kind==='shaft'?'stroke':'fill']),a=alpha(e)*Number(css[kind==='shaft'?'strokeOpacity':'fillOpacity']),samples=[];
    if(kind==='shaft'){const length=e.getTotalLength();for(const f of [.12,.32,.5,.68,.88])samples.push(e.getPointAtLength(length*f).matrixTransform(e.getScreenCTM()));}
    else{const b=e.getBBox();for(const u of [.2,.4,.6,.8])for(const v of [.2,.4,.6,.8]){const p=new DOMPoint(b.x+b.width*u,b.y+b.height*v);if(e.isPointInFill(p))samples.push(p.matrixTransform(e.getScreenCTM()));}}
    const points=samples.map(p=>{const b=surface(p,e);return {contrast:ratio(paint.map((v,i)=>v*a+b.bg[i]*(1-a)),b.bg),...b};});
    records.push({kind,paint:css[kind==='shaft'?'stroke':'fill'],effectiveOpacity:a,width:css.strokeWidth,minimumContrast:Math.min(...points.map(p=>p.contrast)),points});
  }
  return {shaftCount:shafts.length,headCount:heads.length,records};
}
