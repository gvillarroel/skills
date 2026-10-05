// Place existing native Line captions, including their full protected envelopes.
// Call after native arrow insetting; no replacement marks or overlays are added.
export class ConceptCaptionLayoutRejection extends Error {
  constructor(message) { super(message); this.name='ConceptCaptionLayoutRejection'; this.gate='caption-clearance'; }
}
const clearance=3;
const bounds=element=>{const b=element.getBoundingRect().clone();b.applyTransform(element.getComputedTransform());return b;};
const corners=rect=>[[rect.x,rect.y],[rect.x+rect.width,rect.y],[rect.x+rect.width,rect.y+rect.height],[rect.x,rect.y+rect.height]];
function envelope(points) {
  const x=Math.min(...points.map(p=>p[0])),y=Math.min(...points.map(p=>p[1]));
  return {x,y,width:Math.max(...points.map(p=>p[0]))-x,height:Math.max(...points.map(p=>p[1]))-y};
}
function paintEnvelope(chart,text) {
  const rect=text.getBoundingRect().clone(),matrix=text.getComputedTransform()||[1,0,0,1,0,0];
  const svg=chart.getDom()?.querySelector('svg');
  if(!svg)return {rect,measurement:'native-ssr'};
  const inverse=svg.getScreenCTM()?.inverse();
  if(!inverse)throw new Error('Native SVG caption measurement requires an invertible viewport');
  const glyphs=[...svg.querySelectorAll('text')],used=new Set(),points=corners(rect);
  for(const span of text.childrenRef().filter(child=>child.type==='tspan'&&child.style.text)) {
    const expected=bounds(span),center=[expected.x+expected.width/2,expected.y+expected.height/2];
    const matching=glyphs.filter(el=>!used.has(el)&&el.textContent===String(span.style.text)).map(el=>{
      const box=el.getBBox(),m=inverse.multiply(el.getScreenCTM());
      const quad=corners(box).map(([x,y])=>[m.a*x+m.c*y+m.e,m.b*x+m.d*y+m.f]);
      const b=envelope(quad);return {el,quad,score:(b.x+b.width/2-center[0])**2+(b.y+b.height/2-center[1])**2};
    }).sort((a,b)=>a.score-b.score);
    if(!matching.length)throw new Error(`Native SVG glyph measurement missing ${String(span.style.text)}`);
    const glyph=matching[0];used.add(glyph.el);
    points.push(...glyph.quad.map(point=>localPoint(point,matrix)));
  }
  // DOM getBBox protects emitted baseline/side bearings as well as native backing.
  return {rect:envelope(points),measurement:'native-and-dom-glyphs'};
}
const overlap=(a,b,p=0)=>a.x<b.x+b.width+p&&a.x+a.width>b.x-p&&a.y<b.y+b.height+p&&a.y+a.height>b.y-p;
function segmentHits(a,b,rect,pad=0) {
  const x=rect.x-pad,y=rect.y-pad,w=rect.width+2*pad,h=rect.height+2*pad;
  let lo=0,hi=1;
  for(const [start,delta,min,max] of [[a[0],b[0]-a[0],x,x+w],[a[1],b[1]-a[1],y,y+h]]) {
    if(Math.abs(delta)<1e-9) {if(start<min||start>max)return false;continue;}
    let first=(min-start)/delta,last=(max-start)/delta;
    if(first>last)[first,last]=[last,first];
    lo=Math.max(lo,first);hi=Math.min(hi,last);if(lo>hi)return false;
  }
  return true;
}
function localPoint(point,matrix) {
  const [a,b,c,d,e,f]=matrix,det=a*d-b*c,x=point[0]-e,y=point[1]-f;
  if(!Number.isFinite(det)||Math.abs(det)<1e-9)throw new Error('Native caption transform must be invertible');
  return [(d*x-c*y)/det,(-b*x+a*y)/det];
}
export function settleConceptGraphCaptions(chart) {
  const nodes=[],heads=[],routes=[],captions=[];
  chart.getModel().eachSeriesByType('graph',series=>{
    const graph=series.getGraph();
    graph.eachNode(node=>nodes.push(bounds(node.getGraphicEl().getSymbolPath())));
    graph.eachEdge(edge=>{
      const element=edge.getGraphicEl(),line=element.childOfName('line'),head=element.childOfName('toSymbol');
      const points=[];for(let i=0;i<=120;i++)points.push(line.pointAt(i/120));
      routes.push({edge,line,points,width:Number(line.style.lineWidth)||2});
      if(head)heads.push(bounds(head));
      const text=element.getTextContent();if(text&&!text.ignore)captions.push({edge,line,text});
    });
  });
  for(const {text} of captions){text.setStyle({align:'center',verticalAlign:'middle'});text.dirtyStyle();}
  chart.getZr().refreshImmediately();
  const placed=[],report={checkedCaptions:captions.length,clearancePx:clearance,placements:[]};
  for(const {edge,line,text} of captions) {
    const painted=paintEnvelope(chart,text);
    const source=bounds(edge.node1.getGraphicEl().getSymbolPath());
    let visibleStart=0;
    for(let t=0;t<=1;t+=.005){const p=line.pointAt(t);if(!segmentHits(p,p,source,4)){visibleStart=t;break;}}
    const middleT=(visibleStart+1)/2,original=line.pointAt(middleT),start=line.pointAt(0),end=line.pointAt(1);
    const fractions=[middleT,...[-.05,.05,-.1,.1,-.15,.15,-.2,.2].map(delta=>middleT+delta)].filter(t=>t>visibleStart+.03&&t<.94);
    const candidates=[];
    for(const t of fractions) {
      const p=line.pointAt(t),tangent=line.tangentAt(t),length=Math.hypot(...tangent);
      if(!length)continue;
      const nx=-tangent[1]/length,ny=tangent[0]/length;
      for(const offset of [-12,12,-16,16,-20,20,-24,24,-28,28,-36,36,-44,44,-56,56]) {
        const x=p[0]+nx*offset,y=p[1]+ny*offset;
        candidates.push({t,offset,x,y,rotation:-Math.atan2(tangent[1],tangent[0])+(end[0]<start[0]?Math.PI:0),score:(x-original[0])**2+(y-(original[1]-8))**2});
      }
    }
    candidates.sort((a,b)=>a.score-b.score);
    let selected;
    for(const candidate of candidates) {
      text.x=candidate.x;text.y=candidate.y;text.originX=text.originY=0;
      text.rotation=candidate.rotation;text.scaleX=text.scaleY=1;
      text.setStyle({align:'center',verticalAlign:'middle'});
      text.dirtyStyle();
      const rect=painted.rect,matrix=text.getComputedTransform()||[1,0,0,1,0,0];
      const box=envelope(corners(rect).map(([x,y])=>[matrix[0]*x+matrix[2]*y+matrix[4],matrix[1]*x+matrix[3]*y+matrix[5]]));
      if(box.x<clearance||box.y<clearance||box.x+box.width>chart.getWidth()-clearance||box.y+box.height>chart.getHeight()-clearance)continue;
      if([...nodes,...heads,...placed].some(other=>overlap(box,other,clearance)))continue;
      // Protect the whole native rectangle, not only its white backing or midpoint.
      if(routes.some(route=>route.points.slice(1).some((point,i)=>segmentHits(localPoint(route.points[i],matrix),localPoint(point,matrix),rect,clearance+route.width/2))))continue;
      selected={...candidate,bounds:{x:box.x,y:box.y,width:box.width,height:box.height}};break;
    }
    if(!selected)throw new ConceptCaptionLayoutRejection(`No clear native placement for caption ${String(text.style.text)}; protect full glyphs, nodes, heads and all shafts`);
    placed.push(selected.bounds);text.markRedraw();
    report.placements.push({label:String(text.style.text),position:selected.t,offset:selected.offset,anchor:[selected.x,selected.y],bounds:selected.bounds,measurement:painted.measurement});
  }
  chart.getZr().refreshImmediately();
  // Re-read actual painted glyphs after the selected transforms are emitted.
  for(const {text} of captions) {
    const {rect}=paintEnvelope(chart,text),matrix=text.getComputedTransform()||[1,0,0,1,0,0];
    if(routes.some(route=>route.points.slice(1).some((point,i)=>segmentHits(localPoint(route.points[i],matrix),localPoint(point,matrix),rect,clearance+route.width/2))))
      throw new ConceptCaptionLayoutRejection(`Settled native glyph envelope meets a shaft for caption ${String(text.style.text)}`);
  }
  return report;
}
