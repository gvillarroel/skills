/* Full-frame line atlas. All animation is a pure function of the shared clock. */
(() => {
'use strict';
const S=window.STORY, R=S.rows, stage=d3.select('#stage'), world=d3.select('#world');
const A=LineWorldAttention,M=A.settings(S.attention),pointUnit=A.unitFor(R.map(r=>r.after),M.unitPerPoint);
const category=id=>M.categoryColors[id]||C.ink;
const C=LineWorldTheme.colors();
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), ease=x=>{x=clamp(x);return x*x*(3-2*x)}, mix=(a,b,t)=>a+(b-a)*t;
const txt=(g,x,y,v,size=24)=>g.append('text').attr('x',x).attr('y',y).attr('font-size',size*LineWorldTheme.fontScale()).attr('fill',C.ink).attr('data-role','data-label').text(v);
const line=(g,x1,y1,x2,y2,color=C.ink,width=1.5)=>g.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',width*LineWorldTheme.lineWidth()/2);
const path=(g,d,color=C.ink,width=1.8)=>{const p=g.append('path').attr('d',d).attr('fill','none').attr('stroke',color).attr('stroke-width',width*LineWorldTheme.lineWidth()/2);p.attr('data-draw-length',p.node().getTotalLength());return p;};
const circle=(g,x,y,r,fill=C.white,stroke=C.ink)=>g.append('circle').attr('cx',x).attr('cy',y).attr('r',r).attr('fill',fill==='none'?C.white:fill===C.white?C.quiet:fill).attr('stroke',fill==='none'?C.line:'none').attr('stroke-width',fill==='none'?1.5:0).attr('data-lw-surface',fill==='none'?'group':'item');
const entity=(e,id)=>e.attr('data-entity-id',id).attr('data-base-stroke',e.attr('stroke')||'').attr('data-base-fill',e.attr('fill')||'').attr('data-base-width',e.attr('stroke-width')||1.5);
const eachRow=(g,fn)=>R.forEach((r,i)=>fn(r,i));
let seed=919; const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
const samples=Array.from({length:64},(_,i)=>({id:'sample-'+i,entity:R[i%4].id,x:clamp((i%4)/4+.1+(random()-.5)*.27,.025,.975),y:clamp(.5+Math.sin(i*.61)*.25+(random()-.5)*.25,.025,.975),latency:2+(i%4)*1.5+random()*7}));
const hierarchy=()=>d3.hierarchy({name:'Work',children:[{name:'Plan',children:R.slice(0,2).map(r=>({name:r.label,id:r.id,value:r.after}))},{name:'Deliver',children:R.slice(2).map(r=>({name:r.label,id:r.id,value:r.after}))}]}).sum(d=>d.value||0);
function axis(g,scale,orient,x,y,ticks=4){const a=g.append('g').attr('transform',`translate(${x} ${y})`).call((orient==='x'?d3.axisBottom(scale):d3.axisLeft(scale)).ticks(ticks).tickSize(5));a.selectAll('text').attr('font-size',21).attr('fill',C.muted);a.selectAll('path,line').attr('stroke',C.line);return a;}
function base(g,w,h,opts={}){const p=opts.padding||[68,58,62,76], [top,right,bottom,left]=p;return{x:left,y:top,w:w-left-right,h:h-top-bottom};}
function nodeText(g,x,y,label,id){circle(g,x,y,9,C.white);entity(txt(g,x+18,y+8,label,25),id);}
const handlers={};

handlers.network=(g,w,h)=>{
 const b=base(g,w,h), nodes=R.map((r,i)=>({...r,x:b.x+b.w*(.2+.6*(i%2)),y:b.y+b.h*(.2+.6*Math.floor(i/2))})), links=[[0,1],[1,2],[2,3],[0,3]].map(([a,b])=>({source:nodes[a],target:nodes[b]}));
 const sim=d3.forceSimulation(nodes).randomSource(d3.randomLcg(.41)).force('link',d3.forceLink(links).distance(Math.min(b.w,b.h)*.54).strength(.5)).force('charge',d3.forceManyBody().strength(-2000)).force('center',d3.forceCenter(w/2,h/2)).stop();sim.tick(150);
 links.forEach(d=>path(g,`M${d.source.x} ${d.source.y}L${d.target.x} ${d.target.y}`,C.line));
 nodes.forEach((r,i)=>{const node=g.append('g');entity(circle(node,r.x,r.y,28,C.white),r.id);entity(txt(node,r.x,r.y+63,r.label,27).attr('text-anchor','middle'),r.id);const icons=['database','workflow','chart-no-axes-combined','workflow'];if(S.icons[icons[i]])node.append('g').attr('data-lw-icon','monochrome').attr('transform',`translate(${r.x-16} ${r.y-16}) scale(1.33)`).html(S.icons[icons[i]])});
};
handlers.scatter=(g,w,h)=>{const b=base(g,w,h),x=d3.scaleLinear([0,64],[b.x,b.x+b.w]),y=d3.scaleLinear([0,15],[b.y+b.h,b.y]);axis(g,x,'x',0,b.y+b.h);axis(g,y,'y',b.x,0);txt(g,b.x,b.y-22,'ms',21);txt(g,b.x+b.w,b.y+b.h+49,'Request',21).attr('text-anchor','end');samples.forEach((d,i)=>entity(circle(g,x(i),y(d.latency),5,C.white),d.entity));};
handlers.histogram=(g,w,h)=>{const b=base(g,w,h,{padding:[45,58,65,76]}),bins=d3.bin().domain([0,15]).thresholds([0,3,6,9,12,15])(samples.map(d=>d.latency)),x=d3.scaleLinear([0,15],[b.x,b.x+b.w]),y=d3.scaleLinear([0,d3.max(bins,d=>d.length)],[b.y+b.h,b.y]);bins.forEach(d=>g.append('rect').attr('x',x(d.x0)+2).attr('y',y(d.length)).attr('width',Math.max(0,x(d.x1)-x(d.x0)-4)).attr('height',b.y+b.h-y(d.length)).attr('fill',C.quiet).attr('stroke','none'));axis(g,x,'x',0,b.y+b.h);txt(g,b.x,b.y-13,'Requests',21);txt(g,b.x+b.w,b.y+b.h+49,'ms',21).attr('text-anchor','end');};
handlers['stacked-area']=(g,w,h)=>{const b=base(g,w,h),data=d3.range(6).map(i=>Object.fromEntries(R.map(r=>[r.id,r.trend[i]]))),stack=d3.stack().keys(R.map(r=>r.id))(data),x=d3.scaleLinear([0,5],[b.x,b.x+b.w]),y=d3.scaleLinear([0,70],[b.y+b.h,b.y]),area=d3.area().x((d,i)=>x(i)).y0(d=>y(d[0])).y1(d=>y(d[1]));stack.forEach((d,i)=>entity(g.append('path').attr('d',area(d)).attr('fill',[C.quiet,C.white,'#cfcfcf','#f7f7f7'][i]).attr('stroke',C.ink),d.key));axis(g,x,'x',0,b.y+b.h,5);axis(g,y,'y',b.x,0);txt(g,b.x,b.y-20,S.unit,21);};
handlers['event-raster']=(g,w,h)=>{const b=base(g,w,h,{padding:[40,58,50,130]}),x=d3.scaleLinear([0,5],[b.x,b.x+b.w]);eachRow(g,(r,i)=>{const yy=b.y+(i+.5)*b.h/4;txt(g,30,yy+7,r.label,22);line(g,b.x,yy,b.x+b.w,yy,C.quiet);r.trend.forEach((v,j)=>entity(line(g,x(j),yy-10,x(j),yy+10,C.ink,2),r.id))});axis(g,x,'x',0,b.y+b.h,5);};
handlers['radial-tree']=(g,w,h)=>{const root=d3.tree().size([2*Math.PI,Math.min(w,h)*.32])(hierarchy()),cx=w/2,cy=h/2;const p=d=>[cx+Math.sin(d.x)*d.y,cy-Math.cos(d.x)*d.y];root.links().forEach(d=>{const a=p(d.source),b=p(d.target);path(g,`M${a}L${b}`,C.line)});root.descendants().forEach(d=>{const[x,y]=p(d);entity(circle(g,x,y,d.depth?7:12,C.white),d.data.id||'root');entity(txt(g,x,y+(y<cy?-20:31),d.data.name,24).attr('text-anchor','middle'),d.data.id||'root')});};
handlers['circle-pack']=(g,w,h)=>{const root=d3.pack().size([w-100,h-180]).padding(19)(hierarchy()),gg=g.append('g').attr('transform','translate(50 90)');root.descendants().forEach(d=>{const node=gg.append('g');const face=entity(circle(node,d.x,d.y,d.r,d.children?'none':C.white,d.children?C.line:C.ink),d.data.id||'root');if(!d.children){const label=node.append('g').attr('data-lw-content','').attr('data-lw-for','lw-pack-'+d.data.id);face.attr('id','lw-pack-'+d.data.id);entity(txt(d.r<50?node:label,d.x,d.r<50?d.y+d.r+30:d.y-5,d.data.name,d.r<50?20:24).attr('text-anchor','middle'),d.data.id);txt(label,d.x,d.r<50?d.y+10:d.y+31,d.value,28).attr('text-anchor','middle')}});txt(g,50,h-35,S.unit,21);};
handlers.sunburst=(g,w,h)=>{const radius=Math.min(w,h)*.43,root=d3.partition().size([2*Math.PI,radius])(hierarchy()),a=d3.arc().startAngle(d=>d.x0).endAngle(d=>d.x1).innerRadius(d=>Math.max(0,d.y0-12)).outerRadius(d=>d.y1-13),gg=g.append('g').attr('transform',`translate(${w/2} ${h/2})`);root.descendants().filter(d=>d.depth).forEach(d=>{entity(gg.append('path').attr('d',a(d)).attr('fill',d.depth===1?C.white:C.quiet).attr('stroke',d.depth===1?C.line:'none').attr('data-lw-surface',d.depth===1?'group':'item'),d.data.id||'root');const[x,y]=a.centroid(d);entity(txt(gg,x,y,d.data.name,22).attr('text-anchor','middle'),d.data.id||'root')});txt(gg,0,9,'42',32).attr('text-anchor','middle');txt(g,50,h-35,S.unit,21);};
handlers.treemap=(g,w,h)=>{const b=base(g,w,h,{padding:[45,30,55,30]}),root=d3.treemap().size([b.w,b.h]).paddingInner(5).paddingOuter(0)(hierarchy());root.leaves().forEach(d=>{const xx=b.x+d.x0,yy=b.y+d.y0;entity(g.append('rect').attr('x',xx).attr('y',yy).attr('width',d.x1-d.x0).attr('height',d.y1-d.y0).attr('fill',C.quiet).attr('stroke','none').attr('data-lw-surface','item'),d.data.id);entity(txt(g,xx+20,yy+42,d.data.name,25),d.data.id);txt(g,xx+20,yy+83,d.value,30)});txt(g,30,h-21,S.unit,21);};
handlers.chord=(g,w,h)=>{const radius=Math.min(w,h)*.34,gg=g.append('g').attr('transform',`translate(${w/2} ${h/2})`),ch=d3.chordDirected().padAngle(.08)(S.flows),arc=d3.arc().innerRadius(radius).outerRadius(radius+10);ch.groups.forEach((d,i)=>{entity(gg.append('path').attr('d',arc(d)).attr('fill',C.quiet).attr('stroke','none').attr('data-lw-surface','item'),R[i].id);const mid=(d.startAngle+d.endAngle)/2;entity(txt(gg,Math.sin(mid)*(radius+44),-Math.cos(mid)*(radius+44),R[i].label,23).attr('text-anchor','middle'),R[i].id)});ch.forEach(d=>entity(gg.append('path').attr('d',d3.ribbonArrow().radius(radius-3)(d)).attr('fill',C.quiet).attr('stroke','none').attr('opacity',.75),R[d.source.index].id));};
handlers.matrix=(g,w,h)=>{const size=Math.min(w-200,h-115),cell=size/4,x=(w-size)/2+45,y=53;R.forEach((r,i)=>{entity(txt(g,x-15,y+(i+.64)*cell,r.label,21).attr('text-anchor','end'),r.id);entity(txt(g,x+(i+.5)*cell,y-18,r.label.slice(0,3),21).attr('text-anchor','middle'),r.id);S.flows[i].forEach((v,j)=>{entity(g.append('rect').attr('x',x+j*cell).attr('y',y+i*cell).attr('width',cell).attr('height',cell).attr('fill',v?C.quiet:C.white).attr('stroke','none').attr('data-encoding','matrix'),r.id);txt(g,x+(j+.5)*cell,y+(i+.65)*cell,v,23).attr('text-anchor','middle')})});txt(g,w-25,h-17,'units',20).attr('text-anchor','end');};
handlers['table-bars']=(g,w,h)=>{const y0=105,gap=(h-140)/4,x=d3.scaleLinear([0,24],[w*.55,w-95]);txt(g,65,55,'Stage',23);txt(g,w*.32,55,'Before',23).attr('text-anchor','end');txt(g,w*.44,55,'After',23).attr('text-anchor','end');txt(g,w*.55,55,S.unit,23);line(g,50,75,w-50,75,C.line);axis(g,x,'x',0,h-33);eachRow(g,(r,i)=>{const y=y0+i*gap;entity(txt(g,65,y+8,r.label,27),r.id);entity(txt(g,w*.32,y+8,r.before,27).attr('text-anchor','end'),r.id).attr('class','atlas-before-value');entity(txt(g,w*.44,y+8,r.after,27).attr('text-anchor','end'),r.id).attr('class','atlas-after-value');entity(line(g,x(0),y-7,x(r.before),y-7,C.line,10),r.id).attr('class','atlas-before-mark');entity(line(g,x(0),y+9,x(r.after),y+9,C.ink,4),r.id).attr('class','atlas-after-mark');circle(g,x(r.after),y+9,5,C.white)});};
handlers.bump=(g,w,h)=>{const b=base(g,w,h,{padding:[50,150,60,65]}),x=d3.scaleLinear([0,5],[b.x,b.x+b.w]),y=d3.scalePoint([0,1,2,3],[b.y,b.y+b.h]);eachRow(g,(r,i)=>{const ranks=d3.range(6).map(j=>R.map(v=>({id:v.id,value:v.trend[j]})).sort((a,b)=>b.value-a.value).findIndex(v=>v.id===r.id));entity(path(g,d3.line().x((d,j)=>x(j)).y(d=>y(d)).curve(d3.curveMonotoneX)(ranks)),r.id);entity(txt(g,x(5)+20,y(ranks[5])+8,r.label,24),r.id)});axis(g,x,'x',0,b.y+b.h+13,5);txt(g,65,29,'Rank',21);};
handlers.intervals=(g,w,h)=>{const b=base(g,w,h,{padding:[55,55,65,160]}),x=d3.scaleLinear([0,12],[b.x,b.x+b.w]);eachRow(g,(r,i)=>{const y=b.y+(i+.5)*b.h/4,[a,z]=S.schedule[i];entity(txt(g,35,y+8,r.label,24),r.id);entity(line(g,x(a),y,x(z),y,C.ink,3),r.id);circle(g,x(a),y,6);circle(g,x(z),y,6)});axis(g,x,'x',0,b.y+b.h,4);txt(g,w-45,h-17,'Day',21).attr('text-anchor','end');};
handlers.lines=(g,w,h)=>{const b=base(g,w,h,{padding:[60,150,64,75]}),x=d3.scaleLinear([0,5],[b.x,b.x+b.w]),y=d3.scaleLinear([0,26],[b.y+b.h,b.y]);eachRow(g,(r,i)=>{entity(path(g,d3.line().x((d,j)=>x(j)).y(d=>y(d)).curve(d3.curveMonotoneX)(r.trend)),r.id);entity(txt(g,x(5)+18,y(r.after)+8,r.label,24),r.id)});axis(g,x,'x',0,b.y+b.h,5);axis(g,y,'y',b.x,0);txt(g,b.x,b.y-23,S.unit,21);};
handlers.streamgraph=(g,w,h)=>{const b=base(g,w,h),data=d3.range(6).map(i=>Object.fromEntries(R.map(r=>[r.id,r.trend[i]]))),ss=d3.stack().keys(R.map(r=>r.id)).offset(d3.stackOffsetWiggle)(data),ex=d3.extent(ss.flat().flat()),x=d3.scaleLinear([0,5],[b.x,b.x+b.w]),y=d3.scaleLinear(ex,[b.y+b.h,b.y]);ss.forEach((d,i)=>entity(g.append('path').attr('d',d3.area().x((d,j)=>x(j)).y0(d=>y(d[0])).y1(d=>y(d[1])).curve(d3.curveBasis)(d)).attr('fill',[C.quiet,C.white,'#cfcfcf','#f7f7f7'][i]).attr('stroke',C.ink),d.key));axis(g,x,'x',0,b.y+b.h,5);txt(g,b.x,b.y-20,'Thickness = days',21);};
handlers.parallel=(g,w,h)=>{const b=base(g,w,h,{padding:[80,80,70,80]}),keys=['Before','After','Change'],x=d3.scalePoint(keys,[b.x,b.x+b.w]),ys=[d3.scaleLinear([0,24],[b.y+b.h,b.y]),d3.scaleLinear([0,24],[b.y+b.h,b.y]),d3.scaleLinear([0,10],[b.y+b.h,b.y])];keys.forEach((k,i)=>{axis(g,ys[i],'y',x(k),0,3);txt(g,x(k),b.y-30,k,24).attr('text-anchor','middle')});eachRow(g,r=>entity(path(g,d3.line()([[x(keys[0]),ys[0](r.before)],[x(keys[1]),ys[1](r.after)],[x(keys[2]),ys[2](r.before-r.after)]])),r.id));};
handlers.boxplot=(g,w,h)=>{const b=base(g,w,h,{padding:[55,90,55,160]}),x=d3.scaleLinear([0,15],[b.x,b.x+b.w]);eachRow(g,(r,i)=>{const data=samples.filter(d=>d.entity===r.id).map(d=>d.latency).sort(d3.ascending),a=d3.min(data),z=d3.max(data),q1=d3.quantileSorted(data,.25),q2=d3.quantileSorted(data,.5),q3=d3.quantileSorted(data,.75),y=b.y+(i+.5)*b.h/4;entity(txt(g,35,y+7,r.label,23),r.id);entity(line(g,x(a),y,x(z),y),r.id);entity(g.append('rect').attr('x',x(q1)).attr('y',y-12).attr('width',x(q3)-x(q1)).attr('height',24).attr('fill',C.quiet).attr('stroke','none').attr('data-lw-surface','item'),r.id);line(g,x(q2),y-12,x(q2),y+12);line(g,x(a),y-7,x(a),y+7);line(g,x(z),y-7,x(z),y+7)});axis(g,x,'x',0,b.y+b.h,5);txt(g,w-45,h-16,'ms',21).attr('text-anchor','end');};
handlers.dumbbell=(g,w,h)=>{const b=base(g,w,h,{padding:[60,80,60,160]}),x=d3.scaleLinear([0,24],[b.x,b.x+b.w]);eachRow(g,(r,i)=>{const y=b.y+(i+.5)*b.h/4;entity(txt(g,35,y+8,r.label,24),r.id);entity(line(g,x(r.after),y,x(r.before),y,C.ink,2),r.id);entity(circle(g,x(r.before),y,7,C.white,C.muted),r.id);entity(circle(g,x(r.after),y,7,C.ink),r.id)});axis(g,x,'x',0,b.y+b.h);txt(g,w-45,30,'Before ○  After ● · '+S.unit,22).attr('text-anchor','end');};
handlers.globe=(g,w,h)=>{const b=base(g,w,h),projection=d3.geoOrthographic().rotate([32,-12]).translate([w/2,h/2]).scale(Math.min(b.w,b.h)*.46),geo=d3.geoPath(projection);path(g,geo({type:'Sphere'}),C.ink);path(g,geo(d3.geoGraticule10()),C.line,1);S.sites.forEach((d,i)=>{const[x,y]=projection([d.longitude,d.latitude]);entity(circle(g,x,y,7,C.white),d.id);entity(txt(g,x+(i===2?18:-18),y+(i===1?-23:i===2?27:10),d.label,24).attr('text-anchor',i===2?'start':'end'),d.id)});const coords=S.sites.map(d=>[d.longitude,d.latitude]);path(g,geo({type:'LineString',coordinates:coords}),C.muted,1.5);txt(g,w/2,h-40,'Synthetic deployment · real coordinates',21).attr('text-anchor','middle');};
handlers.donut=(g,w,h)=>{const r=Math.min(w,h)*.35,gg=g.append('g').attr('transform',`translate(${w/2} ${h/2})`),pie=d3.pie().value(d=>d.after).sort(null)(R),arc=d3.arc().innerRadius(r*.62).outerRadius(r);pie.forEach(d=>{entity(gg.append('path').attr('d',arc(d)).attr('fill',C.quiet).attr('stroke','none').attr('data-lw-surface','item'),d.data.id);const[a,b]=arc.centroid(d);entity(txt(gg,a,b,d.data.after,26).attr('text-anchor','middle'),d.data.id)});txt(gg,0,10,'42',36).attr('text-anchor','middle');R.forEach((d,i)=>entity(txt(g,45,100+i*38,d.label+' · '+d.after,25),d.id));txt(g,45,h-35,S.unit,21);};
handlers.lollipop=(g,w,h)=>{const b=base(g,w,h,{padding:[190,50,130,145]}),x=d3.scaleLinear([0,18],[b.x,b.x+b.w]);eachRow(g,(r,i)=>{const y=b.y+(i+.5)*b.h/4;entity(txt(g,30,y+8,r.label,24),r.id);entity(line(g,x(0),y,x(r.after),y,C.ink,2),r.id);entity(circle(g,x(r.after),y,8,C.white),r.id);txt(g,x(r.after)+20,y+8,r.after,25)});axis(g,x,'x',0,b.y+b.h);txt(g,30,h-55,S.unit,21);};
function spatial(g,w,h,kind){const b=base(g,w,h,{padding:[45,45,45,45]}),pts=samples.map(d=>[b.x+d.x*b.w,b.y+d.y*b.h]),del=d3.Delaunay.from(pts);if(kind==='voronoi')path(g,del.voronoi([b.x,b.y,b.x+b.w,b.y+b.h]).render(),C.line,1);if(kind==='delaunay')path(g,del.render(),C.line,1);if(kind==='contours'){const density=d3.contourDensity().x(d=>d[0]).y(d=>d[1]).size([w,h]).bandwidth(40).thresholds(7)(pts);density.forEach(d=>path(g,d3.geoPath()(d),C.line,1.3))}pts.forEach(([x,y],i)=>entity(circle(g,x,y,4,C.white),samples[i].entity));}
for(const kind of ['voronoi','delaunay','contours'])handlers[kind]=(g,w,h)=>spatial(g,w,h,kind);
handlers.beeswarm=(g,w,h)=>{const b=base(g,w,h,{padding:[65,60,70,65]}),x=d3.scaleLinear([0,1],[b.x,b.x+b.w]),nodes=samples.map(d=>({...d,targetX:x(d.x),x:x(d.x),y:h/2})),sim=d3.forceSimulation(nodes).randomSource(d3.randomLcg(.9)).force('x',d3.forceX(d=>d.targetX).strength(1)).force('y',d3.forceY(h/2).strength(.04)).force('collide',d3.forceCollide(7)).stop();sim.tick(140);nodes.forEach(d=>entity(circle(g,d.x,d.y,5,C.white),d.entity));axis(g,x,'x',0,b.y+b.h,4);txt(g,65,40,'x',21);};

const scenes=[];
S.scenePlan.forEach((s,i)=>{
 const beat=S.beats[i],cell=beat.cell,group=world.append('g').attr('class','atlas-cell').attr('data-scene-id',s.id).attr('transform',`translate(${cell[0]*1920} ${cell[1]*1080})`), panes=[];
 s.panels.forEach((p,j)=>{const[x,y,pw,ph]=p.rect,w=pw*1920,h=ph*1080,pg=group.append('g').attr('class','atlas-panel').attr('data-producer',p.producer).attr('data-kind',p.kind).attr('data-panel-id',s.id+'-'+j).attr('data-pattern-id','line-world-'+p.kind).attr('transform',`translate(${x*1920} ${y*1080})`);pg.append('rect').attr('class','panel-surface').attr('width',w).attr('height',h).attr('fill',C.white);const content=pg.append('g').attr('class','panel-content');
 if(p.producer==='mermaid'){
   if(!S.diagrams[p.kind])throw Error('Missing native Mermaid asset: '+p.kind);
   content.html(S.diagrams[p.kind]);content.selectAll('.node rect,.node circle,.node ellipse,.node polygon,.node path.node-bkg,rect.actor,rect.task,path.node-bkg,rect.treemapLeaf,.bar-plot-1 rect').attr('data-lw-surface','item');
   content.selectAll('.cluster>rect,rect.journey-section,rect.treemapSection,rect.section').attr('data-lw-surface','group');
   content.selectAll('[data-lw-surface="item"]').style('fill',C.quiet,'important').style('stroke','none','important');
   // Normalize native inline styles before any focus visit changes serialization.
   content.selectAll('[style]').each(function(){this.setAttribute('style',this.style.cssText)});
   const svg=content.select('svg'),pad=p.kind==='radar'?90:48;svg.attr('x',pad).attr('y',55).attr('width',w-pad*2).attr('height',h-110).attr('preserveAspectRatio','xMidYMid meet').style('max-width','none').style('width',(w-pad*2)+'px').style('height',(h-110)+'px').style('overflow','visible');
   content.selectAll('text,tspan').each(function(){const label=this.textContent.trim();const r=R.find(r=>label===r.label||new RegExp('^'+r.label+'[\\s\\d.\\[\\]()%·:-]*$').test(label));if(r){const fill=getComputedStyle(this).fill;d3.select(this).attr('data-entity-id',r.id).attr('data-base-fill',fill).style('fill',fill,'important');const a=this.getBoundingClientRect(),faces=[...content.node().querySelectorAll('[data-lw-surface=\"item\"]')].filter(e=>{const b=e.getBoundingClientRect();return a.width&&b.width&&a.left>=b.left-1&&a.right<=b.right+1&&a.top>=b.top-1&&a.bottom<=b.bottom+1}).sort((a,b)=>a.getBoundingClientRect().width*a.getBoundingClientRect().height-b.getBoundingClientRect().width*b.getBoundingClientRect().height);if(faces[0])entity(d3.select(faces[0]),r.id).attr('data-base-fill',C.quiet)}});
   if(p.kind==='xy')txt(content,w-52,h-16,'Before ─    After ▯',22).attr('text-anchor','end');
 }else handlers[p.kind](content,w,h);
 // A separator is a boundary of the complete frame partition, never an inset card.
 pg.append('rect').attr('class','panel-boundary').attr('width',w).attr('height',h).attr('fill','none').attr('stroke',C.line).attr('stroke-width',1.3);
 panes.push({p,pg,content,w,h});
 });
 scenes.push({s,beat,cell,group,panes});
});
const portCache=new Map(),maxGuideRadius=Math.max(M.focusRadius,M.emitRadius);
function worldBox(e){const b=e.getBBox(),inv=world.node().getScreenCTM().inverse(),m=e.getScreenCTM(),points=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m).matrixTransform(inv)),round=v=>Math.round(v*1e4)/1e4;return{x0:round(Math.min(...points.map(p=>p.x))),y0:round(Math.min(...points.map(p=>p.y))),x1:round(Math.max(...points.map(p=>p.x))),y1:round(Math.max(...points.map(p=>p.y)))};}
function port(sc,index,row){const key=sc.s.id+':'+index+':'+row.id;if(portCache.has(key))return portCache.get(key);const pane=sc.panes[index],rect=pane.p.rect,x=sc.cell[0]*1920+rect[0]*1920,y=sc.cell[1]*1080+rect[1]*1080,bounds={x0:x+5,y0:y+5,x1:x+pane.w-5,y1:y+pane.h-5},entries=[...pane.content.node().querySelectorAll('[data-entity-id]')].filter(e=>e.dataset.entityId===row.id),e=entries.find(e=>['text','tspan'].includes(e.tagName.toLowerCase()))||entries[0];
 const result=e?A.clearPort(worldBox(e),bounds,[...pane.pg.node().querySelectorAll('text')].filter(e=>e.getBoundingClientRect().width).map(worldBox),maxGuideRadius):{x:x+pane.w*.5,y:y+maxGuideRadius+12};if(document.fonts.status==='loaded')portCache.set(key,result);return result;}
const emissionGroups=[];
scenes.forEach(sc=>{
 const pane=sc.panes.find(p=>M.emissionViews.includes(p.p.kind)&&p.p.producer==='d3');
 if(pane){const tokens=R.flatMap((r,ri)=>A.tokens(r.after,pointUnit).map(d=>({...d,row:r,rowIndex:ri,id:sc.s.id+'-'+r.id+'-'+d.index}))),group=world.append('g').attr('class','quantity-points').attr('data-scene-id',sc.s.id).attr('data-view',pane.p.kind).attr('data-unit-per-point',pointUnit).attr('data-layout-allow-overlap','');
 const marks=group.selectAll('circle').data(tokens,d=>d.id).join('circle').attr('data-entity-id',d=>d.row.id).attr('data-quantity',d=>d.quantity).attr('fill',d=>category(d.row.id)).attr('stroke',C.white).attr('stroke-width',1);
 emissionGroups.push({sc,pane,tokens,group,marks});}
 if(pane){pane.content.selectAll('text').filter(function(){return this.textContent===S.unit}).remove();const singular={days:'day',hours:'hour',items:'item'};txt(pane.pg,48,pane.h-30,`After · 1 dot = ${pointUnit} ${pointUnit===1?(singular[S.unit]||S.unit):S.unit}`,20).attr('class','point-legend');}
 if(sc.s.id==='space'&&Object.keys(M.categoryColors).length){const legend=sc.panes[0].pg.append('g').attr('class','point-legend').attr('transform','translate(48 26)');R.forEach((r,i)=>{circle(legend,i*145, -6,4.5,category(r.id),'none');txt(legend,i*145+14,0,r.label,20)});txt(legend,600,0,'1 dot = 1 observation',18);}
 sc.panes.filter(p=>['scatter','voronoi','delaunay','contours','beeswarm'].includes(p.p.kind)).forEach(p=>p.content.selectAll('circle[data-entity-id]').classed('semantic-point',true));
 sc.group.selectAll('.semantic-point').attr('fill',function(){return M.categoryColors[this.dataset.entityId]||C.quiet}).attr('stroke','none');
 sc.group.selectAll('svg').attr('data-colorset',S.palette);
 if(sc.s.id==='shares'&&Object.keys(M.categoryColors).length){sc.panes[0].content.selectAll('g.legend').each(function(d,i){if(R[i])d3.select(this).select('rect').style('fill',category(R[i].id),'important')});}
});
scenes.forEach(sc=>LineWorldTheme.finish(sc.group.node()));
const targetCache=new Map();
function targetFor(pool,d){if(targetCache.has(d.id))return targetCache.get(d.id);const pane=pool.pane,sc=pool.sc,offset={x:sc.cell[0]*1920+pane.p.rect[0]*1920,y:sc.cell[1]*1080+pane.p.rect[1]*1080};let result;
 if(pane.p.kind==='donut'){const total=d3.sum(R,r=>r.after),before=d3.sum(R.slice(0,d.rowIndex),r=>r.after),angle=(before+d.index*pointUnit+d.quantity*.5)/total*2*Math.PI-Math.PI/2,r=Math.min(pane.w,pane.h)*.35*.94;result={x:offset.x+pane.w/2+Math.cos(angle)*r,y:offset.y+pane.h/2+Math.sin(angle)*r};}
 else{const mark=[...pane.content.node().querySelectorAll('circle[data-entity-id]')].find(e=>e.dataset.entityId===d.row.id),b=worldBox(mark),cx=(b.x0+b.x1)/2,cy=(b.y0+b.y1)/2,rad=pane.p.kind==='network'?76:Math.min(b.x1-b.x0,b.y1-b.y0)*.5*.78,n=A.tokens(d.row.after,pointUnit).length,angle=Math.PI*(1.18+.64*(d.index+.5)/Math.max(1,n));result={x:cx+Math.cos(angle)*rad,y:cy+Math.sin(angle)*rad};}
 if(document.fonts.status==='loaded')targetCache.set(d.id,result);return result;}
function renderPoints(time){const result=[];for(const pool of emissionGroups){const {sc}=pool,hold=(sc.beat.duration-S.camera.transitionSeconds)/4,w=A.windowFor(M,hold,sc.panes.length),active=time>=sc.beat.start+S.camera.transitionSeconds;pool.group.attr('opacity',active?1:0);pool.marks.each(function(d){let p={x:0,y:0,radius:0,opacity:0,landed:false};if(active){const rowStart=sc.beat.start+S.camera.transitionSeconds+d.rowIndex*hold,n=A.tokens(d.row.after,pointUnit).length,birth=rowStart+w.startPhase*hold+w.span*d.index/Math.max(1,n-1);p=A.sample({time,birth,flight:w.flight,origin:port(sc,0,d.row),target:targetFor(pool,d),radius:M.pointRadius,weight:d.weight});}d3.select(this).attr('cx',p.x).attr('cy',p.y).attr('r',p.radius).attr('opacity',p.opacity);result.push({view:pool.pane.p.kind,rowId:d.row.id,quantity:d.quantity,color:category(d.row.id),...p});});}return result;}
const guide=world.append('circle').attr('id','guide-dot').attr('r',M.baseRadius).attr('fill',A.PRIMARY_RED).attr('stroke',C.white).attr('stroke-width',3);
const context=stage.append('text').attr('id','context-label').attr('x',60).attr('y',48).attr('font-size',26).attr('fill',C.ink);
let state={},lastFocusKey='';
const motionWindows=[];
scenes.forEach(sc=>R.forEach((row,rowIndex)=>sc.panes.forEach((pane,paneIndex)=>{
 const source=[...pane.content.node().querySelectorAll('path[data-entity-id],line[data-entity-id],rect[data-entity-id],circle[data-entity-id],ellipse[data-entity-id],polygon[data-entity-id]')].find(e=>e.dataset.entityId===row.id);
 if(!source||typeof source.getTotalLength!=='function')return;
 const slot=(sc.beat.duration-S.camera.transitionSeconds)/(R.length*sc.panes.length),start=sc.beat.start+S.camera.transitionSeconds+(rowIndex*sc.panes.length+paneIndex)*slot,id=`atlas-${sc.s.id}-${row.id}-${paneIndex}`;
 const trace=['path','line'].includes(source.tagName.toLowerCase())&&(source.getAttribute('d')?.match(/[Mm]/g)||[]).length<=1;
 source.setAttribute('data-focus-motion-source',id);motionWindows.push({id,source:`[data-focus-motion-source="${id}"]`,scope:`[data-panel-id="${sc.s.id}-${paneIndex}"]`,kind:pane.p.producer==='mermaid'?'diagram':'chart',start,end:start+slot,mode:trace?'trace':'pulse'});
})));
window.FOCUS_PLAN={windows:motionWindows};
const focusMotion=LineWorldFocusMotion.attach(stage.node(),motionWindows);
const drawStates=new Map();
const center=c=>({x:c[0]*1920+960,y:c[1]*1080+540,z:1});
function overview(){const cells=scenes.map(s=>s.cell),cols=d3.max(cells,c=>c[0])+1,rows=d3.max(cells,c=>c[1])+1;return{x:cols*960,y:rows*540,z:Math.min(1/cols,1/rows)};}
function blend(a,b,u){return{x:mix(a.x,b.x,u),y:mix(a.y,b.y,u),z:mix(a.z,b.z,u)}}
window.renderAt=(seconds,options={})=>{
 const t=clamp(+seconds||0,0,S.duration-1e-7),beat=S.beats.find(b=>t>=b.start&&t<b.end)||S.beats.at(-1),overviewing=beat.id==='overview',index=overviewing?scenes.length-1:S.beats.indexOf(beat),sc=scenes[index],local=t-beat.start,transition=S.camera.transitionSeconds,u=index===0&&!overviewing?1:ease(local/transition),dest=overviewing?overview():center(sc.cell),from=overviewing?center(sc.cell):center(scenes[Math.max(0,index-1)].cell),cam=blend(from,dest,u),pan=options.pan||[0,0];
 world.attr('transform',`translate(${960-cam.x*cam.z+pan[0]} ${540-cam.y*cam.z+pan[1]}) scale(${cam.z})`);
 const read=clamp((local-transition)/Math.max(.001,beat.duration-transition)),selected=R[Math.min(3,Math.floor(read*4))],previous=R[Math.max(0,Math.min(3,Math.floor(read*4)-1))],focusKey=beat.id+':'+selected.id,focusChanged=focusKey!==lastFocusKey;
 scenes.forEach((s,i)=>{
   s.group.attr('opacity',1);
   const isCurrent=i===index&&!overviewing;
   if(focusChanged)s.group.selectAll('[data-entity-id]').each(function(){const e=d3.select(this),active=isCurrent&&this.dataset.entityId===selected.id,tag=this.tagName.toLowerCase(),bs=this.dataset.baseStroke,bf=this.dataset.baseFill;
     if(tag==='text'||tag==='tspan')e.style('fill',active?C.red:(bf||C.ink),'important');
     else if(['rect','circle','ellipse','polygon'].includes(tag)&&this.dataset.lwSurface!=='group'&&!this.hasAttribute('data-encoding'))e.style('fill',active?C.red:(bf&&bf!==C.white&&bf!=='none'?bf:C.quiet),'important').style('stroke','none','important');
     else if(bs&&bs!=='none')e.attr('stroke',active?C.red:bs).attr('stroke-width',+this.dataset.baseWidth+(active?1:0));
   });
   if(focusChanged)LineWorldTheme.contrast(s.group.node());
   // Draw paths after arrival; retain all objects in the world for the final overview.
   const q=isCurrent?ease((local-transition*.55)/1.6):1;
   if(drawStates.get(i)!==q){
     s.group.selectAll('.panel-content').attr('opacity',1);
     s.group.selectAll('[data-draw-length]').attr('stroke-dasharray',function(){const len=this.dataset.drawLength;return len+' '+len}).attr('stroke-dashoffset',function(){return +this.dataset.drawLength*(1-q)});
     drawStates.set(i,q);
   }
 });
 lastFocusKey=focusKey;
 let dot={x:dest.x,y:dest.y};
 if(!overviewing&&local>=transition){const phase=(read*4)%1,pos=phase*sc.panes.length,paneIndex=Math.min(sc.panes.length-1,Math.floor(pos));
   const end=port(sc,paneIndex,selected),start=paneIndex?port(sc,paneIndex-1,selected):port(sc,sc.panes.length-1,previous),hop=ease((pos-paneIndex)/.38);
   dot={x:mix(start.x,end.x,hop),y:mix(start.y,end.y,hop)-Math.sin(hop*Math.PI)*26};
 }else if(!overviewing)dot={x:mix(from.x,dest.x,u),y:mix(from.y,dest.y,u)};
 const packets=renderPoints(t),hold=(beat.duration-transition)/4,phase=(read*4)%1,emitting=emissionGroups.some(p=>p.sc===sc),guideRadius=A.radius(M,{phase,hold,panes:sc.panes.length,emitting,travel:local<transition?local/transition:null});
 guide.attr('cx',dot.x).attr('cy',dot.y).attr('r',guideRadius).attr('fill',A.PRIMARY_RED).attr('opacity',overviewing?0:1);
 const label=S.presentation?.contextLabels?.[beat.id]||'';context.text(label).attr('opacity',label?1:0);
 const figureMotion=focusMotion.render(t).filter(s=>s.active);
 state={seconds:t,beat:beat.id,selectedRowId:selected.id,before:selected.before,after:selected.after,mode:'atlas',camera:cam,dot,palette:S.palette,contextLabel:label,layout:'full-frame-partitions',panelCount:overviewing?0:sc.panes.length,guideColor:A.PRIMARY_RED,guideRadius,points:packets,figureMotion};return state;
};
window.snapshot=()=>structuredClone(state);
window.ATLAS={scenes:scenes.map(s=>({id:s.s.id,cell:s.cell,panels:s.s.panels})),sampleCount:samples.length};
window.renderAt(0);
window.ready=document.fonts.ready.then(()=>{scenes.forEach(sc=>LineWorldTheme.finish(sc.group.node()));portCache.clear();targetCache.clear();return window.renderAt(state.seconds);});
})();
