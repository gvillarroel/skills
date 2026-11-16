/* Editable, balanced composition. Visible context is explicitly requested only. */
(() => {
const C=LineWorldTheme.colors();
const S=window.STORY,rows=S.rows,stage=d3.select('#stage'),world=d3.select('#world');
const A=LineWorldAttention,M=A.settings(S.attention);
const O={diagram:{x:1920,y:0},data:{x:1920,y:1080},categories:{x:0,y:1080}};
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),ease=v=>{v=clamp(v);return v*v*(3-2*v)},mix=(a,b,t)=>a+(b-a)*t;
const at=id=>S.beats.find(b=>b.id===id),local=(t,id)=>t-at(id).start;
const klass=cls=>cls.split(' ').map(c=>['label','small','note','number','quiet'].includes(c)?'world-'+c:c).join(' ');
const text=(g,x,y,value,cls='label')=>g.append('text').attr('x',x).attr('y',y).attr('class',klass(cls)).attr('data-role','data-label').text(value);
const line=(g,x1,y1,x2,y2,color=C.ink)=>g.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',LineWorldTheme.lineWidth());
const path=(g,d,cls='ink-line')=>g.append('path').attr('d',d).attr('class',cls);
const shifted=(g,o)=>g.attr('transform',`translate(${o.x} ${o.y})`);
function reveal(p,q){const length=p.node().getTotalLength();p.attr('stroke-dasharray',length+' '+length).attr('stroke-dashoffset',length*(1-clamp(q)));}
function icon(g,id,x,y,size=48){if(S.icons[id])g.append('g').attr('data-lw-icon','monochrome').attr('transform',`translate(${x} ${y}) scale(${size/24})`).html(S.icons[id]);}
function along(points,q){const value=clamp(q)*(points.length-1),i=Math.min(points.length-2,Math.floor(value)),u=ease(value-i);return{x:mix(points[i].x,points[i+1].x,u),y:mix(points[i].y,points[i+1].y,u)};}
function curve(a,b,q){const u=ease(q);return{x:mix(a.x,b.x,u),y:mix(a.y,b.y,u)+Math.sin(u*Math.PI)*100};}
let seed=431;function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}

const cloud=world.append('g').attr('id','observations').attr('data-content-anchor','observation-field').attr('data-pattern-id','line-world-guided-relations');
const nodes=[{x:340,y:540,label:'Observe',icon:'database'},{x:730,y:245,label:'Select'},{x:1160,y:345,label:'Relate',icon:'chart-no-axes-combined'},{x:1550,y:650,label:'Explain',icon:'workflow'},{x:950,y:845,label:'Compare'}];
const edges=[[0,1],[1,2],[2,3],[3,4],[4,0],[1,4]];
const cloudEdges=cloud.append('g').selectAll('path').data(edges).join('path').attr('class','ink-line').attr('d',d=>`M${nodes[d[0]].x} ${nodes[d[0]].y} Q960 535 ${nodes[d[1]].x} ${nodes[d[1]].y}`);
const particles=Array.from({length:90},(_,i)=>{const a=random()*Math.PI*2,r=110+random()*330;return{i,x:960+Math.cos(a)*r*1.72,y:540+Math.sin(a)*r*.85,r:2+random()*4,target:nodes[i%5]}});
const dots=cloud.selectAll('.particle').data(particles).join('circle').attr('class','particle').attr('fill',C.muted).attr('stroke','none');
const nodeMarks=cloud.selectAll('.concept').data(nodes).join('g').attr('class','concept').attr('transform',d=>`translate(${d.x} ${d.y})`);
nodeMarks.each(function(d){const g=d3.select(this);if(d.icon)icon(g,d.icon,-24,-24);else g.append('circle').attr('r',12).attr('fill',C.ink);text(g,0,-42,d.label).attr('text-anchor','middle')});

const diagram=shifted(world.append('g').attr('id','diagram'),O.diagram);
const diagramAsset=diagram.append('g').attr('id','producer-diagram').attr('transform','translate(200 270)');
let diagramPorts=[],diagramFocus=-2;
if(S.diagramSvg){
  diagramAsset.html(S.diagramSvg);diagramAsset.selectAll('.node rect,.node circle,.node ellipse,.node polygon').attr('data-lw-surface','item');LineWorldTheme.finish(diagramAsset.node());diagramAsset.select('svg').attr('width',1520).attr('height',540).style('width','1520px').style('height','540px').style('overflow','visible');
  const inverse=stage.node().getScreenCTM().inverse();
  diagramAsset.selectAll('.node').each(function(){const circle=this.querySelector('circle'),radius=circle?+circle.getAttribute('r'):0;const point=new DOMPoint(0,-radius).matrixTransform(this.getScreenCTM()).matrixTransform(inverse);diagramPorts.push({x:point.x,y:point.y})});
}else{
  ['Observe','Select','Compare','Explain'].forEach((name,i)=>{const x=100+i*440;diagramAsset.append('circle').attr('cx',x).attr('cy',270).attr('r',12).attr('fill',C.ink);text(diagramAsset,x,330,name).attr('text-anchor','middle');if(i<3)path(diagramAsset,`M${x+24} 270L${x+410} 270`,'guide-line').attr('marker-end','url(#arrow)');diagramPorts.push({x:O.diagram.x+200+x,y:540})});
}
if(diagramPorts.length<2)diagramPorts=[{x:2220,y:540},{x:3540,y:540}];

const data=shifted(world.append('g').attr('id','data-island').attr('data-pattern-id','line-world-table-focus'),O.data);
line(data,920,0,920,1080,C.line).attr('class','full-frame-divider');
const tableX=130,tableY=205,rowGap=Math.min(150,600/rows.length);
const table=data.append('g').attr('id','table').attr('transform',`translate(${tableX} ${tableY})`);
text(table,0,0,S.copy.entity,'small quiet');text(table,390,0,'Before','small quiet').attr('text-anchor','end');text(table,590,0,'After','small quiet').attr('text-anchor','end');
line(table,0,30,650,30,C.line);
const tableRows=table.selectAll('.table-row').data(rows).join('g').attr('class','table-row').attr('data-row-id',d=>d.id).attr('transform',(d,i)=>`translate(0 ${78+i*rowGap})`);
tableRows.append('text').attr('class','world-label row-label').text(d=>d.label);
tableRows.append('text').attr('x',390).attr('class','world-number before-value').attr('text-anchor','end').text(d=>d.before);
tableRows.append('text').attr('x',590).attr('class','world-number after-value').attr('text-anchor','end').text(d=>d.after);
tableRows.append('line').attr('x1',0).attr('x2',650).attr('y1',30).attr('y2',30).attr('stroke',C.quiet).attr('stroke-width',1);
const focusLine=line(table,-25,108,650,108,C.red).attr('id','row-focus').attr('stroke-width',2.5);
const unitNote=S.unit+(S.dataStatus==='synthetic'?' · illustrative':'');
text(table,0,rows.length*rowGap+90,unitNote,'small quiet');
const chart=data.append('g').attr('id','paired-chart').attr('transform','translate(1040 205)');
line(chart,0,-8,36,-8,C.line);text(chart,48,0,'Before','small quiet');line(chart,190,-8,226,-8,C.ink);text(chart,238,0,'After','small quiet');
const maximum=d3.max(rows,d=>Math.max(d.before,d.after))||1,x=d3.scaleLinear().domain([0,maximum*1.1]).range([0,690]);
const pairs=chart.selectAll('.pair').data(rows).join('g').attr('class','pair').attr('data-row-id',d=>d.id).attr('transform',(d,i)=>`translate(0 ${58+i*rowGap})`);
pairs.append('rect').attr('class','before-bar').attr('height',8).attr('fill',C.line).attr('width',d=>x(d.before));
pairs.append('rect').attr('class','after-bar').attr('y',20).attr('height',8).attr('fill',C.secondary).attr('width',d=>x(d.after));
pairs.append('text').attr('class','world-small chart-value').attr('x',d=>x(d.after)+16).attr('y',32).text(d=>d.after);
line(chart,0,rows.length*rowGap+56,690,rows.length*rowGap+56,C.line);
[0,maximum/2,maximum].forEach(v=>{const px=x(v);line(chart,px,rows.length*rowGap+56,px,rows.length*rowGap+65,C.line);text(chart,px,rows.length*rowGap+102,d3.format('~g')(v),'small quiet').attr('text-anchor','middle')});
const delta=text(data,1040,995,'','small').attr('id','data-delta').attr('data-role','data-value');

const history=data.append('g').attr('id','history-chart').attr('transform','translate(1040 205)').attr('data-pattern-id','line-world-linked-history');
const hmax=(d3.max(rows.flatMap(d=>d.trend))||1)*1.13,hx=d3.scaleLinear().domain([0,rows[0].trend.length-1]).range([0,650]),hy=d3.scaleLinear().domain([0,hmax]).range([610,45]);
line(history,0,610,690,610,C.line);line(history,0,45,0,610,C.line);
[0,hmax/2,hmax].forEach(v=>text(history,-20,hy(v)+8,d3.format('.0f')(v),'small quiet').attr('text-anchor','end'));
text(history,0,665,'1','small quiet');text(history,650,665,''+rows[0].trend.length,'small quiet').attr('text-anchor','end');text(history,325,715,S.copy.observations,'small quiet').attr('text-anchor','middle');text(history,-20,10,S.unit,'small quiet').attr('text-anchor','end');
const lineGen=d3.line().x((d,i)=>hx(i)).y(d=>hy(d)).curve(d3.curveMonotoneX);
const histories=history.selectAll('.history-path').data(rows).join('path').attr('class','ink-line history-path').attr('data-row-id',d=>d.id).attr('d',d=>lineGen(d.trend));
const historyLabel=text(history,670,100,'','small');
const historyPoint=history.append('circle').attr('r',7).attr('fill',C.red);

const categories=shifted(world.append('g').attr('id','categories').attr('data-pattern-id','line-world-category-expansion'),O.categories);
const colors=S.colorSequence;
const positive=rows.filter(d=>d.after>0),root=d3.hierarchy({children:positive.map(d=>({name:d.label,value:d.after,id:d.id}))}).sum(d=>d.value||0);d3.treemap().size([1920,1080]).paddingInner(0).round(true)(root);
const leaves=positive.length?root.leaves():[];
const cells=categories.append('g').selectAll('.cell').data(leaves).join('g').attr('class','cell').attr('data-row-id',d=>d.data.id).attr('transform',d=>`translate(${d.x0} ${d.y0})`);
cells.append('rect').attr('width',d=>d.x1-d.x0).attr('height',d=>d.y1-d.y0).attr('fill',(d,i)=>colors[i]);
cells.append('text').attr('x',28).attr('y',48).attr('class','world-label').style('fill',(d,i)=>S.textOnFill[colors[i]]).text(d=>d.data.name);
cells.append('text').attr('x',28).attr('y',99).attr('class','world-number').style('fill',(d,i)=>S.textOnFill[colors[i]]).text(d=>d.value);
if(!leaves.length)text(categories,960,540,'0 '+S.unit,'number').attr('text-anchor','middle');
cells.append('text').attr('x',28).attr('y',d=>d.y1-d.y0-28).attr('class','world-small').style('fill',(d,i)=>S.textOnFill[colors[i]]).text(unitNote);
const categoryTarget=leaves.length?{x:O.categories.x+(leaves.at(-1).x0+leaves.at(-1).x1)/2,y:O.categories.y+(leaves.at(-1).y0+leaves.at(-1).y1)/2}:{x:960,y:1620};
const firstTablePort={x:O.data.x+tableX-40,y:O.data.y+tableY+78};
const bridge=path(world,`M${nodes.at(-1).x} ${nodes.at(-1).y}C1680 1050 1820 480 ${diagramPorts[0].x} ${diagramPorts[0].y}M${diagramPorts.at(-1).x} ${diagramPorts.at(-1).y}C3900 860 2370 940 ${firstTablePort.x} ${firstTablePort.y}M${O.data.x+90} 1910C1850 2130 1820 2120 1730 1860`,'guide-line').attr('stroke-dasharray','3 13').attr('data-layout-allow-overlap','');
const guide=world.append('g').attr('id','attention-dot');guide.append('circle').attr('r',M.baseRadius+3).attr('fill',C.white);guide.append('circle').attr('r',M.baseRadius).attr('fill',A.PRIMARY_RED);
const context=text(stage,130,84,'','note').attr('id','context-label').attr('data-role','requested-context');
let currentState=null;
const motionWindows=[];
const registerMotion=(element,id,start,end,kind,mode,scope)=>{if(!element)return;element.setAttribute('data-focus-motion-source',id);motionWindows.push({id,source:`[data-focus-motion-source="${id}"]`,scope,kind,start,end,mode});};
registerMotion(diagramAsset.node().querySelector('path.flowchart-link,.edgePath path,path.guide-line'),'linked-flow',at('relations').start+2.7,at('relations').end,'diagram','trace','#producer-diagram');
pairs.select('.after-bar').each(function(d,i){const span=(at('compare').duration-2)/rows.length;registerMotion(this,'linked-bar-'+d.id,at('compare').start+2+i*span,at('compare').start+2+(i+1)*span,'chart','pulse','#paired-chart');});
histories.each(function(d,i){if(!i)return;const span=at('history').duration/rows.length;registerMotion(this,'linked-history-'+d.id,at('history').start+i*span,at('history').start+(i+1)*span,'chart','trace','#history-chart');});
window.FOCUS_PLAN={windows:motionWindows};
const focusMotion=LineWorldFocusMotion.attach(stage.node(),motionWindows);

function camera(t){
  let c={x:960,y:540,z:1};
  const move=(id,target,duration)=>{if(t>=at(id).start){const q=ease(local(t,id)/duration);c={x:mix(c.x,target.x,q),y:mix(c.y,target.y,q),z:mix(c.z,target.z,q)}}};
  move('relations',{x:2880,y:540,z:1},2.6*Math.min(1,at('relations').duration/8));
  move('travel',{x:2880,y:1620,z:1},at('travel').duration);
  move('categories',{x:960,y:1620,z:1},2.7*Math.min(1,at('categories').duration/8));
  move('overview',{x:1920,y:1080,z:.5},3.6*Math.min(1,at('overview').duration/6));return c;
}
window.renderAt=function(seconds,options={}){
  const t=clamp(+seconds||0,0,S.duration-.000001),c=camera(t),pan=options.pan||[0,0],beat=S.beats.find(b=>t>=b.start&&t<b.end)?.id;
  world.attr('transform',`translate(${960-c.x*c.z+pan[0]} ${540-c.y*c.z+pan[1]}) scale(${c.z})`);
  const cloudT=t*(7/at('cloud').duration),formation=ease((cloudT-3.2)/2.3),particleReveal=.35+.65*ease((cloudT-.2)/1.2);
  dots.attr('cx',d=>mix(d.x+Math.sin(t*.5+d.i)*9,d.target.x,formation)).attr('cy',d=>mix(d.y+Math.cos(t*.6+d.i)*8,d.target.y,formation)).attr('r',d=>d.r*(1-formation*.8)).attr('opacity',particleReveal*(1-formation));
  nodeMarks.attr('opacity',formation);cloudEdges.each(function(d,i){reveal(d3.select(this),(cloudT-4.6-i*.13)/1.3)});
  const relationT=local(t,'relations')*(8/at('relations').duration);diagram.attr('opacity',ease(relationT/.9));diagramAsset.attr('opacity',ease((relationT-.5)/.9));
  const nativeNodes=diagramAsset.selectAll('g.node').nodes(),nativeIndex=beat==='relations'?Math.min(nativeNodes.length-1,Math.max(0,Math.floor((relationT-2.2)/Math.max(1,5.8/nativeNodes.length)))):-1;if(nativeIndex!==diagramFocus){LineWorldTheme.focus(diagramAsset.node(),nativeNodes[nativeIndex]||null);diagramFocus=nativeIndex;}
  const compareT=local(t,'compare'),span=(at('compare').duration-2)/rows.length;data.attr('opacity',ease((local(t,'travel')-.6)/1.1));
  let selected=clamp(Math.floor((compareT-2)/span),0,rows.length-1),mode='compare';
  if(t>=at('history').start){selected=clamp(Math.floor(local(t,'history')/(at('history').duration/rows.length)),0,rows.length-1);mode='history'}
  const row=rows[selected],rowY=78+selected*rowGap;
  focusLine.attr('y1',rowY+30).attr('y2',rowY+30).attr('opacity',ease((compareT-.5)/.5));
  tableRows.select('.row-label').style('fill',(d,i)=>i===selected?C.red:C.ink);
  const barReveal=ease((t-at('compare').start+1.4)/1.4);pairs.select('.before-bar').attr('width',d=>x(d.before)*barReveal);pairs.select('.after-bar').attr('width',d=>x(d.after)*barReveal).attr('fill',(d,i)=>i===selected?C.red:C.secondary);pairs.attr('opacity',(d,i)=>i===selected?1:.6);
  const historyT=local(t,'history');chart.attr('opacity',1-ease(historyT/.45));history.attr('opacity',ease(historyT/.45));
  histories.style('stroke',(d,i)=>i===selected?C.red:C.line).style('stroke-width',(d,i)=>i===selected?3:2).each(function(){reveal(d3.select(this),historyT/2)});
  historyLabel.attr('y',hy(row.trend.at(-1))+7).text(row.label);historyPoint.attr('cx',650).attr('cy',hy(row.trend.at(-1)));
  const change=row.after-row.before;delta.text(`${change>0?'+':''}${d3.format('~g')(change)} ${S.unit}`).style('fill',C.red).attr('opacity',mode==='compare'?ease((compareT-1.5)/.5):0);
  const catActual=local(t,'categories'),catT=catActual*(8/at('categories').duration);categories.attr('opacity',ease(catT/.7));cells.attr('opacity',(d,i)=>ease((catT-.25-i*.18)/.8));
  const moving=(beat==='relations'&&local(t,'relations')<2.6*Math.min(1,at('relations').duration/8))||beat==='travel'||(beat==='categories'&&catActual<2.7*Math.min(1,at('categories').duration/8))||beat==='overview';bridge.attr('opacity',moving?.4:0);
  let dot={x:mix(360,nodes[0].x,ease(cloudT/3)),y:mix(360,nodes[0].y,ease(cloudT/3))};
  if(cloudT>=4)dot=along(nodes,(cloudT-4)/3);
  if(t>=at('relations').start)dot=relationT<2.2?curve(nodes.at(-1),diagramPorts[0],relationT/2.2):along(diagramPorts,(relationT-2.2)/5.8);
  if(t>=at('travel').start)dot=curve(diagramPorts.at(-1),firstTablePort,local(t,'travel')/at('travel').duration);
  if(compareT>=0)dot={x:O.data.x+tableX-40,y:O.data.y+tableY+rowY};
  if(t>=at('categories').start){const q=catActual/(2.7*Math.min(1,at('categories').duration/8));dot=curve({x:O.data.x+tableX-40,y:O.data.y+tableY+rowY},categoryTarget,q);}
  if(t>=at('overview').start)dot=curve(categoryTarget,{x:1920,y:1080},local(t,'overview')/(3.6*Math.min(1,at('overview').duration/6)));
  const activeBeat=at(beat),phase=((t-activeBeat.start)/activeBeat.duration*rows.length)%1,guideRadius=A.radius(M,{phase,travel:moving?clamp((t-activeBeat.start)/Math.min(2,activeBeat.duration)):null});
  if(beat==='cloud')dot.x-=guideRadius+24;
  guide.attr('transform',`translate(${dot.x} ${dot.y})`);guide.select('circle:first-child').attr('r',guideRadius+3);guide.select('circle:last-child').attr('r',guideRadius).attr('fill',A.PRIMARY_RED);
  const requestedContext=S.presentation?.contextLabels?.[beat]||'';context.text(requestedContext).attr('opacity',requestedContext?ease(local(t,beat)/.35):0);
  const figureMotion=focusMotion.render(t).filter(s=>s.active);
  currentState={seconds:t,beat,selectedRowId:row.id,before:row.before,after:row.after,mode,camera:c,dot,palette:S.palette,contextLabel:requestedContext,layout:'balanced-four-islands',guideRadius,guideColor:A.PRIMARY_RED,figureMotion};return currentState;
};
window.snapshot=()=>({...currentState});window.renderAt(0);
})();
