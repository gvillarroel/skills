/* Project-owned D3 world. All motion follows the supplied audio clock. */
(()=>{'use strict';
const S=PRODUCTION,F=LineWorldFocus,C=LineWorldTheme.colors(),stage=d3.select('#stage');
const W=1920,H=1080,world=stage.append('g').attr('id','world');
const cells=S.scenes.map((s,i)=>({x:(i<5?i:9-i)*W,y:i<5?0:H,id:s.id}));
const groups=cells.map(c=>world.append('g').attr('id','scene-'+c.id).attr('transform',`translate(${c.x} ${c.y})`));
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},mix=(a,b,u)=>a+(b-a)*u;
const mark=(e,id)=>e.attr('data-focus-id',id);
const obstacle=e=>e.attr('data-focus-obstacle','true');
const label=(g,x,y,v,size=30,id=null,anchor='start')=>{const t=g.append('text').attr('x',x).attr('y',y).attr('font-size',size*LineWorldTheme.fontScale()).attr('text-anchor',anchor).attr('fill',C.ink).text(v);if(id)mark(t,id);return t;};
const line=(g,x1,y1,x2,y2,color=C.line,width=2)=>g.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',width);
const path=(g,d,color=C.line,width=2)=>g.append('path').attr('d',d).attr('stroke',color).attr('stroke-width',width).attr('fill','none');
const rect=(g,x,y,w,h,fill=C.white,stroke=C.line)=>g.append('rect').attr('x',x).attr('y',y).attr('width',w).attr('height',h).attr('fill',fill).attr('stroke',stroke).attr('stroke-width',2).attr('data-lw-surface','item');
const dot=(g,x,y,r,fill=C.white,stroke=C.line)=>g.append('circle').attr('cx',x).attr('cy',y).attr('r',r).attr('fill',fill).attr('stroke',stroke).attr('stroke-width',2).attr('data-lw-surface','item');
const hdiv=(g,y)=>line(g,0,y,W,y).attr('data-divider','true');
const vdiv=(g,x,y0=0,y1=H)=>line(g,x,y0,x,y1).attr('data-divider','true');
const arrow=(g,d)=>path(g,d).attr('marker-end','url(#tip)');
const node=(g,x,y,w,h,v,id)=>{const n=mark(g.append('g'),id);obstacle(rect(n,x,y,w,h));label(n,x+w/2,y+h/2+10,v,30,null,'middle');return n;};
function photo(g,id,variant,x,y,w,h,objectId){const sceneId=g.node().closest('[id^="scene-"]')?.id.slice(6),policy=S.scenes.find(s=>s.id===sceneId)?.objects?.find(o=>o.id===objectId);id=policy?.asset||id;variant=policy?.variant||variant;const asset=DOCUMENTARY_ASSETS[id]?.variants[variant];if(!asset)throw Error('Missing reviewed photographic treatment '+id+'/'+variant);const n=g.append('g').attr('data-object-id',objectId);obstacle(n.append('image').attr('data-documentary-id',id).attr('x',x).attr('y',y).attr('width',w).attr('height',h).attr('href',asset.image).attr('preserveAspectRatio','xMidYMid meet'));return n;}
function media(g,id,x,y,size,focusId=null){const asset=MEDIA_ASSETS[id],context=S.scenes.flatMap(s=>s.people||[]).find(p=>p.id===id),n=g.append('g').attr('data-media-id',id);if(!asset)throw Error('Missing reviewed media '+id);if(asset.kind==='portrait'&&!context)throw Error('A visible portrait needs spoken identity and contribution: '+id);if(context)n.attr('data-person-id',id).attr('data-person-role',context.caption.join(' · '));if(context?.target||focusId)mark(n,[context?.target,focusId].filter(Boolean).join(' '));obstacle(n.append('image').attr('x',x-size/2).attr('y',y-size/2).attr('width',size).attr('height',size).attr('href',asset.image).attr('preserveAspectRatio','xMidYMid meet'));dot(n,x,y,size/2+2,'none',C.line).attr('data-lw-surface',null);label(n,x,y+size/2+40,context?.name||asset.label,30,null,'middle').attr('data-person-name',context?'true':null);for(const [i,line]of (context?.caption||[]).entries())label(n,x,y+size/2+86+i*38,line,23,null,'middle').attr('data-person-caption','true');return n;}
function native(g,name,x,y,w,h,ids){let svg=NATIVE_DIAGRAMS[name];const doc=new DOMParser().parseFromString(svg,'image/svg+xml'),root=doc.documentElement;const boxes=Object.values(NATIVE_DIAGRAMS).map(s=>new DOMParser().parseFromString(s,'image/svg+xml').documentElement.getAttribute('viewBox').split(/\s+/).map(Number)),box=root.getAttribute('viewBox').split(/\s+/).map(Number),scale=Math.min(w/Math.max(...boxes.map(b=>b[2])),h/Math.max(...boxes.map(b=>b[3])));const prefix=name+'-native-';for(const e of [root,...root.querySelectorAll('[id]')])if(e.id){const old=e.id;svg=svg.replaceAll('id="'+old+'"','id="'+prefix+old+'"').replaceAll('#'+old,'#'+prefix+old);}const wrap=g.append('g').attr('transform',`translate(${x} ${y})`);wrap.html(svg);const el=wrap.select('svg').attr('x',(w-box[2]*scale)/2).attr('y',(h-box[3]*scale)/2).attr('width',box[2]*scale).attr('height',box[3]*scale).style('max-width','none');el.selectAll('g.node rect,g.node circle,g.node ellipse,g.node polygon').attr('data-lw-surface','item');el.selectAll('text').attr('data-review-font-group','feature-lanes');el.selectAll('path.flowchart-link').attr('data-port-obstacle','true');for(const [source,target]of Object.entries(ids)){const n=el.selectAll('g.node').filter(function(){return this.id.includes('flowchart-'+source+'-')});if(n.empty())throw Error('Native Mermaid node missing: '+source);mark(n,target);n.selectAll('rect,polygon,path').attr('data-focus-obstacle','true').attr('data-lw-surface','item');}return wrap;}
stage.append('defs').html('<marker id="tip" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1L9 5L1 9" fill="none" stroke="#cfcfcf" stroke-width="1.8"/></marker>');

// The opening connects the same three entities used in the closing view.
{
 const g=groups[0];label(g,960,205,'2012',76,'year-2012','middle');line(g,960,245,960,330);
 node(g,715,365,490,165,'AlexNet','alexnet');
 const items=[{x:360,name:'Datos',id:'data'},{x:960,name:'Algoritmos',id:'algorithm'},{x:1560,name:'Cómputo',id:'compute'}];
 items.forEach((d,i)=>{const n=mark(g.append('g'),d.id);n.attr('data-lw-focus-mode','group');dot(n,d.x,795,72).attr('id','opening-face-'+i).attr('data-lw-surface','group');label(n,d.x,935,d.name,36,null,'middle');const glyph=n.append('g').attr('data-lw-icon','monochrome').attr('data-lw-content','').attr('data-lw-for','opening-face-'+i);if(i===0)for(let k=0;k<3;k++)rect(glyph,d.x-32+k*16,767+k*8,44,35).attr('fill','none');if(i===1){line(glyph,d.x-28,795,d.x+28,795);line(glyph,d.x,766,d.x-28,795);line(glyph,d.x,766,d.x+28,795);dot(glyph,d.x-28,795,9,C.white,C.muted);dot(glyph,d.x+28,795,9,C.white,C.muted);dot(glyph,d.x,766,9,C.white,C.muted);}if(i===2)rect(glyph,d.x-35,760,70,70).attr('fill','none');glyph.selectAll('[data-lw-surface]').attr('data-lw-surface',null);arrow(g,`M${d.x} 720V625H${[800,960,1120][i]}V535`);});
}
{
 const g=groups[1];hdiv(g,540);
 native(g,'engineered',120,120,1680,300,{edges:'edges',descriptors:'descriptors',classifier:'classifier'});
 native(g,'learned',120,660,1680,260,{learned:'learned'});
 label(g,1540,1015,'datos · cómputo',28,'resources','middle');
}
{
 const g=groups[2];hdiv(g,380);vdiv(g,960,380);
 const a=mark(g.append('g'),'cuda-2006');label(a,270,110,'2006',56,null,'middle');label(a,270,180,'CUDA',32,null,'middle');
 const b=mark(g.append('g'),'cuda-2007');label(b,700,110,'2007',56,null,'middle');label(b,700,180,'beta pública',32,null,'middle');line(g,140,245,850,245);line(g,270,208,270,245);line(g,700,208,700,245);
 media(g,'ian-buck',1220,135,170);media(g,'nvidia',1620,135,170);
 const cpu=mark(photo(g,'cpu','one-bit',285,520,340,360,'cpu-photo'),'cpu');label(cpu,455,470,'CPU',36,null,'middle');label(g,455,950,'control',30,null,'middle');
 const gpu=mark(photo(g,'gtx580','one-bit',1175,520,550,360,'gpu-photo'),'gpu');label(gpu,1450,470,'GPU',36,null,'middle');label(g,1450,950,'paralelo',32,'parallel','middle');
}
{
 const g=groups[3];vdiv(g,600);vdiv(g,1320);
 label(g,300,215,'datos',32,null,'middle');const input=mark(g.append('g'),'input');
 for(let r=0;r<4;r++)for(let c=0;c<4;c++){rect(input,130+c*82,355+r*82,66,66);label(input,163+c*82,398+r*82,String(r*4+c),26,null,'middle');}
 node(g,735,165,450,110,'kernel','kernel');
 const blocks=mark(g.append('g'),'blocks');for(let r=0;r<2;r++)for(let c=0;c<2;c++){const n=blocks.append('g');rect(n,700+c*275,415+r*250,225,200).attr('data-lw-surface','group');if(r===0&&c===0)mark(n,'threads');for(let tr=0;tr<2;tr++)for(let tc=0;tc<2;tc++)dot(n,765+c*275+tc*85,475+r*250+tr*80,18,C.quiet);}
 label(g,960,985,'bloques de hilos',30,null,'middle');line(g,960,280,960,350);path(g,'M810 405V350H1110V405');
 label(g,1620,215,'resultados',32,null,'middle');const output=mark(g.append('g'),'output');for(let r=0;r<4;r++)for(let c=0;c<4;c++){rect(output,1440+c*82,355+r*82,66,66);label(output,1473+c*82,398+r*82,String((r*4+c)*2),26,null,'middle');}
 arrow(g,'M480 900H680');arrow(g,'M1230 900H1410');label(g,300,970,'i',30,null,'middle');label(g,1620,970,'2 × i',30,null,'middle');
}
{
 const g=groups[4];vdiv(g,1080);node(g,135,95,420,90,'ImageNet · 2009','imagenet-2009');
 media(g,'fei-fei-li',300,295,190);media(g,'jia-deng',760,295,190);
 const field=mark(g.append('g'),'image-examples'),categories=['flower','elephant','sailboat','pumpkin','dog'];for(let r=0;r<5;r++)for(let c=0;c<6;c++)photo(field,`imagenet-${categories[r]}-${c+1}`,'gray',140+c*145,515+r*72,112,64,`imagenet-photo-${r}-${c}`);
 label(g,355,950,'etiquetas',32,'labels','middle');node(g,665,900,290,85,'concurso','challenge');label(g,140,1015,'ImageNet · muestras publicadas',26);
 const count=mark(g.append('g'),'images-count');label(count,1490,390,'1,2 millones',76,null,'middle');label(count,1490,460,'imágenes de entrenamiento',29,null,'middle');
 const classes=mark(g.append('g'),'classes-count');label(classes,1490,745,'1000',84,null,'middle');label(classes,1490,815,'categorías',32,null,'middle');
}
{
 const g=groups[5];hdiv(g,350);media(g,'alex-krizhevsky',350,150,190,'author-alex');media(g,'ilya-sutskever',960,150,190,'author-ilya');media(g,'geoffrey-hinton',1550,150,190,'author-hinton');
 const px=mark(photo(g,'leopard','pixel',110,420,170,170,'pixels-photo'),'pixels');label(px,190,735,'píxeles',30,null,'middle');
 const conv=mark(g.append('g'),'conv-layers');for(let i=0;i<5;i++){const x=420+i*190,h=320-i*36;rect(conv,x,540-h/2,92,h,C.white,C.muted);label(conv,x+46,735,'C'+(i+1),29,null,'middle');if(i<4)arrow(g,`M${x+100} 540H${x+180}`);}label(conv,850,900,'5 convolucionales',32,null,'middle');arrow(g,'M300 540H410');
 const dense=mark(g.append('g'),'dense-layers');for(let i=0;i<3;i++){const x=1480+i*145;for(let r=0;r<4;r++)dot(dense,x,415+r*80,17,C.white,C.muted);label(dense,x,735,'F'+(i+1),28,null,'middle');if(i<2)arrow(g,`M${x+28} 540H${x+116}`);}arrow(g,'M1280 540H1445');label(dense,1625,900,'3 conectadas',32,null,'middle');label(g,1745,1010,'categorías',30,'categories','middle');
}
{
 const g=groups[6];hdiv(g,790);vdiv(g,800,0,790);vdiv(g,1120,0,790);
 const pair=mark(g.append('g'),'gpu-pair');const one=mark(photo(pair,'gtx580','one-bit',135,250,540,354,'gtx-left'),'gpu-one');const two=mark(photo(pair,'gtx580','one-bit',1245,250,540,354,'gtx-right'),'gpu-two');label(one,405,185,'GTX 580',36,null,'middle');label(two,1515,185,'GTX 580',36,null,'middle');
 label(g,405,735,'3 GB',48,'memory','middle');label(g,1515,735,'3 GB',48,'capacity','middle');
 const split=mark(g.append('g'),'model-split');label(split,960,155,'red',30,null,'middle');for(let r=0;r<3;r++){dot(split,900,300+r*110,15,C.white,C.muted);dot(split,1020,355+r*110,15,C.white,C.muted);line(split,915,300+r*110,1005,355+r*110);}
 arrow(g,'M690 430H850');arrow(g,'M1070 430H1220');
 label(g,960,945,'5–6 días',64,'training-days','middle');label(g,960,1020,'entrenamiento de un modelo',27,null,'middle');
}
{
 const g=groups[7];vdiv(g,640);vdiv(g,1280);
 const relu=mark(g.append('g'),'relu');label(relu,320,260,'ReLU',34,null,'middle');line(relu,165,680,545,680,C.muted);line(relu,320,730,320,360,C.muted);path(relu,'M170 680H320L530 415',C.red,3);label(relu,565,690,'x',24);label(relu,290,760,'0',24);label(relu,320,900,'max(0, x)',32,null,'middle');
 const aug=mark(g.append('g'),'augmentation recipe');label(aug,960,260,'aumentación',32,null,'middle');const examples=['leopard','leopard-flip','leopard-crop','leopard-crop-flip'];for(let r=0;r<2;r++)for(let c=0;c<2;c++)photo(aug,examples[r*2+c],'gray',735+c*240,390+r*255,200,170,`augmentation-photo-${r*2+c}`);
 const drop=mark(g.append('g'),'dropout');label(drop,1600,260,'dropout',34,null,'middle');for(let c=0;c<2;c++)for(let r=0;r<3;r++)for(let k=0;k<3;k++)line(drop,1390+c*205+17,390+r*130,1390+(c+1)*205-17,390+k*130,C.quiet,1.4);for(let c=0;c<3;c++)for(let r=0;r<3;r++){const n=dot(drop,1390+c*205,390+r*130,17,(r+c)%3===1?C.quiet:C.white,C.muted);if((r+c)%3===1)n.attr('stroke-dasharray','4 5');}
 label(g,1600,900,'entrenamiento',29,null,'middle');label(g,1600,990,'sobreajuste',28,'generalization','middle');
}
{
 const g=groups[8];vdiv(g,1180);label(g,170,165,'Error top-5 · %',30);
 const ensemble=mark(g.append('g'),'ensemble');for(let i=0;i<7;i++)dot(ensemble,195+i*53,240,12,C.white,C.muted);label(ensemble,170,335,'AlexNet · 7 redes',32);
 const scale=d3.scaleLinear().domain([0,30]).range([0,780]);
 const winner=mark(g.append('g'),'winner');rect(winner,170,390,scale(15.3),50,C.red,C.red).attr('data-color-role','primary-highlight').attr('data-encoding','quantity').attr('data-value',15.3);label(winner,170+scale(15.3)+32,432,'15,3 %',46);
 label(g,170,590,'2.º puesto',32);const second=mark(g.append('g'),'runner-up');rect(second,170,640,scale(26.2),50,C.secondary,C.secondary).attr('data-color-role','secondary-highlight').attr('data-encoding','quantity').attr('data-value',26.2);label(second,170+scale(26.2)+32,682,'26,2 %',46);
 line(g,170,800,950,800,C.muted);for(const v of [0,10,20,30]){const x=170+scale(v);line(g,x,800,x,815,C.muted);label(g,x,855,String(v),25,null,'middle');}
 const gap=mark(g.append('g'),'gap');path(gap,`M${170+scale(15.3)} 910V930H${170+scale(26.2)}V910`,C.muted);label(gap,710,1020,'10,9 pp',56,null,'middle');
 const top=mark(g.append('g'),'top-five');label(top,1550,200,'5 opciones',32,null,'middle');for(let i=0;i<5;i++){const row=top.append('g'),y=315+i*105;rect(row,1350,y,390,66,C.white,i===2?C.red:C.line).attr('data-lw-align','preserve');
  const cell=(j,x,w)=>{const id=`top-five-cell-${i}-${j}`;row.append('rect').attr('id',id).attr('x',x).attr('y',y).attr('width',w).attr('height',66).attr('fill','none').attr('stroke','none');return row.append('g').attr('data-lw-content','').attr('data-lw-for',id);};
  label(cell(0,1350,100),1390,y+45,String(i+1),27);label(cell(1,1450,200),1530,y+45,String.fromCharCode(65+i),29);if(i===2)path(cell(2,1650,90),`M1660 ${y+28}L1673 ${y+41}L1700 ${y+15}`,C.red,3).attr('data-lw-icon','monochrome');}
 label(g,1550,955,'ejemplo esquemático',25,null,'middle');
}
{
 const g=groups[9];const entries=[{x:330,id:'legacy-cuda',name:'CUDA',date:'2006 / 2007'},{x:960,id:'legacy-data',name:'Datos',date:'ImageNet · 2009'},{x:1590,id:'legacy-model',name:'Redes',date:'AlexNet · 2012'}];
 entries.forEach((d,i)=>{const n=mark(g.append('g'),d.id);n.attr('data-lw-focus-mode','group');dot(n,d.x,365,90).attr('data-lw-surface','group');label(n,d.x,540,d.name,36,null,'middle');label(n,d.x,610,d.date,29,null,'middle');if(i===0)rect(n,d.x-34,331,68,68);if(i===1)for(let k=0;k<3;k++)rect(n,d.x-38+k*12,337+k*7,52,42,'none',C.muted).attr('data-lw-surface',null);if(i===2){for(let k=0;k<3;k++)dot(n,d.x-40+k*40,365,9,C.white,C.muted);line(n,d.x-30,365,d.x+30,365);}arrow(g,`M${d.x} 655V715H${[790,960,1130][i]}V775`);});
 node(g,700,785,520,120,'AlexNet','legacy-alexnet legacy-convergence');label(g,960,1000,'2012',48,'legacy-2012','middle');
}

const guide=world.append('circle').attr('id','guide').attr('fill','#9e1b32').attr('stroke','#ffffff').attr('stroke-width',3).attr('r',10);
let planned=[],poses=[],panRoutes=[],previousPaint='',lastState=null;
function bbox(el){const q=el.getBoundingClientRect(),r=stage.node().getBoundingClientRect(),sx=W/r.width,sy=H/r.height;return{x0:(q.left-r.left)*sx,y0:(q.top-r.top)*sy,x1:(q.right-r.left)*sx,y1:(q.bottom-r.top)*sy};}
function paint(i,target){const key=i+':'+target;if(key===previousPaint)return;const selected=i>=0&&target?[...groups[i].node().querySelectorAll('[data-focus-id]')].find(e=>e.dataset.focusId.split(/\s+/).includes(target)):null;LineWorldTheme.focus(stage.node(),selected,selected?.querySelector('[data-color-role="secondary-highlight"]')?'secondary':'primary');previousPaint=key;}
window.prepareFocus=function(){
 LineWorldTheme.finish(stage.node());
 const bounds={x0:45,y0:45,x1:1875,y1:1035},allBlocks=[];planned=[];poses=[];panRoutes=[];
 for(let i=0;i<groups.length;i++){
  groups.forEach((g,k)=>g.attr('display',k===i?null:'none'));world.attr('transform',`translate(${-cells[i].x} ${-cells[i].y})`);guide.attr('display','none');
  const texts=[...groups[i].node().querySelectorAll('text')].filter(e=>e.textContent.trim()).map(bbox),marks=[...groups[i].node().querySelectorAll('rect,circle,image,[data-focus-obstacle]')].filter(e=>!e.closest('defs')).map(bbox),dividers=[...groups[i].node().querySelectorAll('[data-divider],[data-port-obstacle]')].map(bbox);
  const boxes=[...texts,...marks],blocks=boxes.filter((a,j)=>!boxes.some((b,k)=>k!==j&&(b.x1-b.x0)*(b.y1-b.y0)>(a.x1-a.x0)*(a.y1-a.y0)&&b.x0<=a.x0&&b.x1>=a.x1&&b.y0<=a.y0&&b.y1>=a.y1));allBlocks.push(blocks);
  const source=(NARRATION_CUES.scenes||[]).find(s=>s.id===S.scenes[i].id)?.cues||S.scenes[i].cues.map((c,j)=>({...c,at:2+j*(S.scenes[i].clipSeconds-4)/S.scenes[i].cues.length,travelSeconds:.28,draft:true}));
  const targets=[...groups[i].node().querySelectorAll('[data-focus-id]')],ports=source.map(c=>{const el=targets.find(e=>e.dataset.focusId.split(/\s+/).includes(c.target));if(!el)throw Error('Missing target '+S.scenes[i].id+'/'+c.target);const p=F.port(bbox(el),bounds,[...texts,...marks,...dividers],{radius:14,gap:18,side:c.target==='authors'?'above':'left'});return{...c,...p};});
  let prior=ports[0];for(const cue of ports){cue.path=F.route(prior,cue,blocks,bounds,{radius:8,gap:6});prior=cue;}
  planned.push(ports);poses.push({first:ports[0],last:ports.at(-1),transition:i?Math.max(.25,Math.min(.9,ports[0].at-.10)):0});
 }
 for(let i=1;i<groups.length;i++){const a=cells[i-1],b=cells[i],from={x:a.x+poses[i-1].last.x,y:a.y+poses[i-1].last.y},to={x:b.x+poses[i].first.x,y:b.y+poses[i].first.y},obstacles=[...allBlocks[i-1].map(q=>({x0:q.x0+a.x,x1:q.x1+a.x,y0:q.y0+a.y,y1:q.y1+a.y})),...allBlocks[i].map(q=>({x0:q.x0+b.x,x1:q.x1+b.x,y0:q.y0+b.y,y1:q.y1+b.y}))],area={x0:Math.min(a.x,b.x)+45,x1:Math.max(a.x,b.x)+1875,y0:Math.min(a.y,b.y)+45,y1:Math.max(a.y,b.y)+1035};panRoutes[i]=F.route(from,to,obstacles,area,{radius:8,gap:8});}
 guide.attr('display',null);window.RESOLVED_CUES=planned;window.renderClip(0,0);return planned.map((c,i)=>({id:S.scenes[i].id,count:c.length,transition:poses[i].transition,draft:c.some(x=>x.draft)}));
};
window.renderClip=function(i,t){
 if(!planned.length)return null;const duration=S.scenes[i].clipSeconds;t=clamp(t,0,duration);const current=cells[i],previous=cells[Math.max(0,i-1)],pan=poses[i].transition,u=pan?ease(t/pan):1;
 const camera={x:mix(previous.x,current.x,u),y:mix(previous.y,current.y,u),scale:1};if(i===0){camera.x=current.x;camera.y=current.y;}
 groups.forEach((g,k)=>g.attr('display',k===i&&(!i||t>0)||i&&k===i-1&&t<pan?null:'none'));
 world.attr('transform',`translate(${-camera.x} ${-camera.y})`);
 let p,activeScene=i;if(i&&t<pan){const old=poses[i-1].last,point=F.visibleAlong(panRoutes[i],u,{x0:camera.x+45,x1:camera.x+W-45,y0:camera.y+45,y1:camera.y+H-45}),endRadius=F.pose(planned[i],pan,poses[i].first).radius;p={x:point.x,y:point.y,radius:Math.max(6,mix(10,endRadius,u)-4*Math.sin(u*Math.PI)),target:t===0?old.target:null};activeScene=t===0?i-1:i;}
 else{const local=F.pose(planned[i],t,poses[i].first);p={...local,x:current.x+local.x,y:current.y+local.y};}
 guide.attr('cx',p.x).attr('cy',p.y).attr('r',p.radius).attr('fill','#9e1b32');paint(activeScene,p.target);
 lastState={camera,guide:{x:p.x,y:p.y,radius:p.radius,target:p.target||null},visibleScene:activeScene};return structuredClone(lastState);
};
window.renderAt=function(seconds){let remaining=clamp(seconds,0,S.scenes.reduce((a,s)=>a+s.clipSeconds,0));for(let i=0;i<S.scenes.length;i++){if(remaining<=S.scenes[i].clipSeconds||i===S.scenes.length-1)return renderClip(i,remaining);remaining-=S.scenes[i].clipSeconds;}};
window.snapshot=()=>structuredClone(lastState);
window.auditScene=function(i){renderClip(i,S.scenes[i].clipSeconds);const base=F.audit(stage.node()),obstacles=[...groups[i].node().querySelectorAll('text,[data-focus-obstacle]')].map(bbox),hits=[];for(const c of planned[i]){const b={x0:c.x-18,x1:c.x+18,y0:c.y-18,y1:c.y+18};if(obstacles.some(o=>F.overlap(b,o,3)))hits.push(c.target);}return{...base,guidePortCollisions:hits,ok:base.ok&&!hits.length};};
window.ready=Promise.all([document.fonts.ready,...Object.values(MEDIA_ASSETS).map(a=>new Promise((ok,bad)=>{const i=new Image();i.onload=ok;i.onerror=()=>bad(Error('Media failed to load: '+a.image));i.src=a.image}))]).then(()=>prepareFocus());
})();
