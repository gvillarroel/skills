/* Project-specific Spanish educational figure; all data marks use measured DATA. */
const R='#9e1b32',G='#b5b5b5',D='#696969',L='#e7e7e7',I='#333e48',W='#ffffff';
const svg=d3.select('#stage').attr('font-family','Space Grotesk').attr('fill',I);
svg.append('rect').attr('width',1920).attr('height',1080).attr('fill',W);
const world=svg.append('g');
const cells=[[0,0],[1920,0],[3840,0],[5760,0],[5760,1080],[3840,1080],[1920,1080],[0,1080],[0,2160],[1920,2160],[3840,2160],[5760,2160]];
const groups=cells.map(([x,y],i)=>world.append('g').attr('transform',`translate(${x},${y})`).attr('data-scene',i));
const clamp=x=>Math.max(0,Math.min(1,x));const ease=x=>{x=clamp(x);return x*x*(3-2*x)};
function line(g,x1,y1,x2,y2,c=G,w=2){return g.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',c).attr('stroke-width',w)}
function text(g,x,y,t,size=30,c=I,anchor='start'){return g.append('text').attr('x',x).attr('y',y).attr('font-size',size).attr('fill',c).attr('text-anchor',anchor).text(t)}
function dot(g,x,y,r=7,c=R){return g.append('circle').attr('cx',x).attr('cy',y).attr('r',r).attr('fill',c)}
function box(g,x,y,w,h,c=G,fill=W){return g.append('rect').attr('x',x).attr('y',y).attr('width',w).attr('height',h).attr('rx',18).attr('fill',fill).attr('stroke',c).attr('stroke-width',2).attr('data-lw-surface',w>500&&h>400?'group':'item')}
function arrow(g,x,y,xx,yy,c=G){line(g,x,y,xx,yy,c,2.5);const a=Math.atan2(yy-y,xx-x);g.append('path').attr('d',`M${xx-13*Math.cos(a-.45)},${yy-13*Math.sin(a-.45)}L${xx},${yy}L${xx-13*Math.cos(a+.45)},${yy-13*Math.sin(a+.45)}`).attr('fill','none').attr('stroke',c).attr('stroke-width',2.5)}
function chart(g,x,y,w,h,xd,yd,xLabel,yLabel){const xx=d3.scaleLinear().domain(xd).range([x,x+w]),yy=d3.scaleLinear().domain(yd).range([y+h,y]);for(let v of yy.ticks(4)){line(g,x,yy(v),x+w,yy(v),L,1);text(g,x-18,yy(v)+7,d3.format('.2~f')(v),24,D,'end')}if(xLabel)for(let v of xx.ticks(4))text(g,xx(v),y+h+36,d3.format('.2~f')(v),24,D,'middle');line(g,x,y+h,x+w,y+h);text(g,x+w,y+h+78,xLabel,26,I,'end');text(g,x,y-65,yLabel,26,I);return{xx,yy,w,h,x,y}}
function path(g,points,c,w=4){return g.append('path').attr('d',d3.line()(points)).attr('fill','none').attr('stroke',c).attr('stroke-width',w).attr('stroke-linecap','round').attr('stroke-linejoin','round')}
const animated=[];function reveal(node,start=1.8,duration=1){animated.push({node,start,duration})}
const plots=[];
// 1: data, flexible fit and a smoother model share exactly one coordinate system.
{
let g=groups[0],p=chart(g,150,160,1600,670,[-1,1],[-1.8,1.8],'x','y');
const train=DATA.samplesXY.filter(d=>d[2]==='train');train.forEach(d=>dot(g,p.xx(d[0]),p.yy(d[1]),4.5,G));
const clip=g.append('defs').append('clipPath').attr('id','fit-clip');clip.append('rect').attr('x',150).attr('y',160).attr('width',1600).attr('height',670);
DATA.fits.forEach((f,i)=>{let q=g.append('g').attr('clip-path','url(#fit-clip)');reveal(path(q,DATA.gridX.map((x,j)=>[p.xx(x),p.yy(f.prediction[j])]),i===1?R:G,i===1?5:2.3),2+i*1.8,1.8)});
text(g,180,990,'Sintéticos · ajuste: 144 · total: 240 · 120 entidades',27,G);text(g,1000,990,'Capacidad controlada',30,R);line(g,944,980,984,980,R,5);
}
// 2: full-frame three-column data contract and quality gates.
{
let g=groups[1];line(g,640,0,640,1080);line(g,1280,0,1280,1080);
const labels=[['Entrada disponible','x','momento de predecir'],['Objetivo','y','valor observado'],['Error cuadrático','(y − ŷ)²','menor es mejor']];
labels.forEach((a,j)=>{let q=g.append('g');reveal(q,2+j*1.5);dot(q,320+640*j,250,35);text(q,320+640*j,430,a[1],88,R,'middle');text(q,320+640*j,545,a[0],34,I,'middle');text(q,320+640*j,603,a[2],28,G,'middle')});
['Procedencia','Etiquetas','Duplicados','Ausentes','Cobertura real'].forEach((a,j)=>{const x=[150,470,820,1110,1580][j];dot(g,x,835,9,j===2?R:G);text(g,x,900,a,28,I,'middle')});
}
// 3: grouped split; each vertical pair stays together.
{
let g=groups[2];let parts=[['Entrenamiento',60,144,R],['Validación',20,48,G],['Prueba',20,48,G]],x=0;
parts.forEach(([label,pct,n,c],k)=>{let w=1920*pct/100;let q=g.append('g');if(k)line(g,x,0,x,1080);text(q,x+w/2,165,`${pct}%`,70,c,'middle');text(q,x+w/2,245,label,31,I,'middle');text(q,x+w/2,298,`${n} observaciones`,27,G,'middle');for(let j=0;j<n/2;j++){let cols=Math.floor((w-110)/44),cx=x+65+(j%cols)*44,cy=400+Math.floor(j/cols)*95;line(q,cx,cy,cx,cy+22,c,2);dot(q,cx,cy,6,c);dot(q,cx,cy+22,6,c)}reveal(q,2+k*1.7);x+=w});text(g,90,1000,'Una entidad → un único conjunto',32,R);text(g,1728,1000,'Prueba reservada',28,I,'middle');
}
// 4: semantic flow expressed as a sparse pipeline; fold-local fit is explicit.
{
let g=groups[3];line(g,0,540,1920,540);const names=['Imputar','Escalar','Seleccionar','Modelo'];
names.forEach((a,j)=>{let x=130+j*455;let q=g.append('g');box(q,x,285,295,150,j===3?R:G);text(q,x+147,375,a,34,I,'middle');if(j<3)arrow(q,x+295,360,x+445,360);reveal(q,2+j*1.2);box(q,x,695,295,150,G);text(q,x+147,785,a,34,I,'middle');if(j<3)arrow(q,x+295,770,x+445,770)});
// Shared transfer lane stays to the right of both row labels and all boxes.
line(g,1790,435,1870,435,R);line(g,1870,435,1870,770,R);arrow(g,1870,770,1790,770,R);
text(g,115,145,'Ajustar · solo entrenamiento de cada fold',34,R);text(g,115,625,'Aplicar · validación / prueba',34,I);text(g,1470,980,'Sin volver a ajustar',28,G);
}
// 5: baseline and selected model measured on the same validation sample.
{
let g=groups[4];line(g,960,0,960,1080);let p=chart(g,150,200,650,570,[0,1],[0,1],'','MSE · validación');
[[.25,DATA.baselineValidationMSE,'Media',D],[.75,DATA.chosenValidationMSE,'Pipeline',R]].forEach(([x,v,label,c],j)=>{let q=g.append('g');q.append('rect').attr('x',p.xx(x)-70).attr('y',p.yy(v)).attr('width',140).attr('height',p.yy(0)-p.yy(v)).attr('fill',c).attr('data-color-role',j===0?'secondary-highlight':'primary-highlight');text(q,p.xx(x),p.yy(v)-25,v.toFixed(3),38,c,'middle');text(q,p.xx(x),845,label,32,I,'middle');reveal(q,2+j*2)});
let p2=chart(g,1110,200,650,570,[1,17],[0,.3],'Grado','MSE · CV');const a=DATA.candidates.filter(d=>d.alpha===.3);reveal(path(g,a.map(d=>[p2.xx(d.degree),p2.yy(d.cvMSE)]),R,4),4,2);a.forEach(d=>dot(g,p2.xx(d.degree),p2.yy(d.cvMSE),8,R));text(g,1110,965,'Elegir por datos no usados en el ajuste',29,I);
}
// 6: folds, linked selected row and error with variability.
{
let g=groups[5];line(g,960,0,960,1080);for(let row=0;row<5;row++){text(g,90,210+row*115,`${row+1}`,30,G);for(let col=0;col<5;col++)box(g,160+col*132,150+row*115,108,78,row===col?R:G,row===col?R:L).attr('data-encoding','fold-role')}text(g,160,845,'Reservado',30,R);text(g,395,845,'Ajuste',30,G);
let rows=DATA.candidates.filter(d=>d.alpha===.3);text(g,1050,155,'Grado',28,G);text(g,1300,155,'MSE CV',28,G);text(g,1590,155,'± desviación',28,G);rows.forEach((d,j)=>{let y=260+j*122,c=d.degree===3?R:I;line(g,1030,y+45,1810,y+45,L);text(g,1080,y,d.degree,37,c);text(g,1300,y,d.cvMSE.toFixed(3),37,c);text(g,1630,y,d.cvSD.toFixed(3),37,c)});text(g,1040,970,'5 folds por grupos · α = 0.3',29,G);
}
// 7: real coefficient norms, logarithmic scale clearly marked.
{
let g=groups[6],p=chart(g,180,200,1550,610,[-6,1],[0,2.6],'log₁₀ α','log₁₀ (1 + ‖coeficientes‖₂)');
let data=DATA.regularization;reveal(path(g,data.map(d=>[p.xx(Math.log10(d.alpha)),p.yy(Math.log10(1+d.coefficientNorm))]),R,5),2,3);data.forEach((d,j)=>{let q=g.append('g');dot(q,p.xx(Math.log10(d.alpha)),p.yy(Math.log10(1+d.coefficientNorm)),12,R);text(q,p.xx(Math.log10(d.alpha)),p.yy(Math.log10(1+d.coefficientNorm))-35,d.coefficientNorm.toFixed(1),31,I,'middle');reveal(q,2+j*1.5)});text(g,180,1000,'Mismo grado 17 · cambia solo la penalización L2',30,G);
}
// 8: explicitly schematic early stopping, never attributed to Ridge.
{
let g=groups[7],e=DATA.earlyStopping,p=chart(g,180,180,1550,620,[0,30],[0,1],'Época','Error · esquema');
reveal(path(g,e.epoch.map((x,j)=>[p.xx(x),p.yy(e.trainLoss[j])]),G,4),2,4);reveal(path(g,e.epoch.map((x,j)=>[p.xx(x),p.yy(e.validationLoss[j])]),R,5),2,5);let best=d3.minIndex(e.validationLoss);line(g,p.xx(best),180,p.xx(best),800,R,2).attr('stroke-dasharray','8 10');dot(g,p.xx(best),p.yy(e.validationLoss[best]),15,R);text(g,p.xx(best)+25,220,'Recuperar este estado',32,R);text(g,180,990,'Entrenamiento',29,G);text(g,600,990,'Validación',29,R);text(g,1080,990,'Esquema · no es una curva de Ridge',28,G);
}
// 9: measured grouped learning curves and their gaps.
{
let g=groups[8],p=chart(g,180,180,1550,630,[35,120],[0,.22],'Ejemplos de entrenamiento por fold','MSE');
['trainMSE','cvMSE'].forEach((key,j)=>{let c=j?R:G;reveal(path(g,DATA.learning.map(d=>[p.xx(d.samples),p.yy(d[key])]),c,5),2+j*1.6,2);DATA.learning.forEach(d=>dot(g,p.xx(d.samples),p.yy(d[key]),10,c))});text(g,180,990,'Entrenamiento',30,G);text(g,640,990,'CV por grupos',30,R);text(g,1190,990,'Grado 3 · α = 0.3',30,I);
}
// 10: freeze configuration before one final independent evaluation.
{
let g=groups[9];line(g,960,0,960,1080);box(g,180,190,600,650);text(g,480,315,'Pipeline congelado',36,I,'middle');['PolynomialFeatures · grado 3','StandardScaler','Ridge · α = 0.3','Desarrollo · 192 observaciones'].forEach((s,j)=>text(g,245,450+j*85,s,29,j===2?R:I));
let q=g.append('g');reveal(q,5,2);dot(q,1440,360,75,R);text(q,1440,560,DATA.finalTestMSE.toFixed(3),100,R,'middle');text(q,1440,630,'MSE · prueba independiente',31,I,'middle');text(q,1440,740,`IC 95%: ${DATA.testMSEInterval95.map(d=>d.toFixed(3)).join(' – ')}`,34,I,'middle');text(q,1440,812,'Bootstrap por entidad · modelo fijo',27,G,'middle');text(q,1440,905,'48 observaciones · 24 entidades',27,G,'middle');arrow(g,780,540,1100,540,R);
}
// 11: production loop, schematic because no deployment has been performed.
{
let g=groups[10],nodes=[[330,290,'Datos'],[1330,290,'Predicciones'],[1330,790,'Error real'],[330,790,'Evaluar de nuevo']];nodes.forEach(([x,y,s],j)=>{let q=g.append('g');box(q,x-180,y-75,360,150,j===2?R:G);text(q,x,y+12,s,32,I,'middle');reveal(q,2+j*1.2);let [xx,yy]=nodes[(j+1)%4];if(x===xx)arrow(g,x,y+(yy>y?90:-90),xx,yy+(yy>y?-90:90),G);else arrow(g,x+(xx>x?200:-200),y,xx+(xx>x?-200:200),yy,G)});text(g,1720,540,'Versionar',31,R,'middle');text(g,1720,595,'datos / código',27,G,'middle');text(g,1720,640,'pipeline / modelo',27,G,'middle');text(g,90,1000,'Esquema de seguimiento · etiquetas nuevas para medir el error',28,G);
}
// 12 stays empty; it is a camera zoom to the complete connected world.
const route=world.append('path').attr('d',d3.line()(cells.slice(0,11).map(([x,y])=>[x+960,y+540]))).attr('stroke',R).attr('stroke-width',3).attr('stroke-dasharray','8 20').attr('fill','none').lower();
const guide=svg.append('circle').attr('fill',R).attr('stroke',W).attr('stroke-width',4).attr('id','guide');
const bindings=[
 {},
 {'input':['Entrada disponible'],'objective':['Objetivo'],'error':['Error cuadrático'],'provenance':['Procedencia'],'labels':['Etiquetas'],'missing':['Ausentes'],'duplicates':['Duplicados'],'coverage':['Cobertura real']},
 {'train-label':['Entrenamiento'],'validation-label':['Validación'],'test-label':['Prueba'],'split-train':['60%'],'split-validation':['20%',0],'split-test':['20%',1],'grouped':['Una entidad → un único conjunto'],'sealed':['Prueba reservada']},
 {'impute':['Imputar',0],'scale':['Escalar',0],'select':['Seleccionar',0],'fit-only':['Ajustar · solo entrenamiento de cada fold'],'apply-only':['Aplicar · validación / prueba'],'apply-model':['Modelo',1],'no-refit':['Sin volver a ajustar']},
 {'baseline-value':[DATA.baselineValidationMSE.toFixed(3)],'baseline-bar':['Media'],'selected-bar':['Pipeline'],'unseen':['Elegir por datos no usados en el ajuste']},
 {'folds':['1',0],'held-fold':['Reservado'],'cv-mean':['MSE CV'],'cv-sd':['± desviación'],'selected-degree':['3',1]},
 {'large-coefficient':[DATA.regularization[0].coefficientNorm.toFixed(1)],'small-coefficient':[DATA.regularization.at(-1).coefficientNorm.toFixed(1)],'penalty':['Mismo grado 17 · cambia solo la penalización L2']},
 {'restore':['Recuperar este estado'],'schematic':['Esquema · no es una curva de Ridge']},
 {'group-cv':['CV por grupos']},
 {'frozen':['Pipeline congelado'],'hyperparameters':['Ridge · α = 0.3'],'development':['Desarrollo · 192 observaciones'],'test-score':[DATA.finalTestMSE.toFixed(3)],'uncertainty':[`IC 95%: ${DATA.testMSEInterval95.map(d=>d.toFixed(3)).join(' – ')}`],'independent':['MSE · prueba independiente']},
 {'versions':['Versionar'],'input-data':['Datos'],'predictions':['Predicciones'],'real-error':['Error real'],'reevaluate':['Evaluar de nuevo']}
];
groups[4].selectAll('[data-color-role]').attr('data-encoding','quantity').attr('data-value',function(){return this.dataset.colorRole==='secondary-highlight'?DATA.baselineValidationMSE:DATA.chosenValidationMSE});
// Place value labels inside dedicated reading lanes, away from axes and points.
groups[4].selectAll('text').filter(function(){return this.textContent===DATA.baselineValidationMSE.toFixed(3)}).attr('y',180);
groups[4].selectAll('text').filter(function(){return this.textContent==='MSE · validación'}).attr('y',115);
groups[6].selectAll('text').filter(function(){return this.textContent===DATA.regularization[0].coefficientNorm.toFixed(1)}).attr('x',255).attr('y',270);
groups.forEach(g=>g.selectAll('text').filter(function(){return this.getAttribute('text-anchor')==='end'&&this.getAttribute('fill')===D}).attr('x',function(){return +this.getAttribute('x')-16}));
// Interrupt only grid rules at measured label envelopes. Keep complete dividers.
groups.forEach(g=>{const labels=g.selectAll('text').nodes().filter(n=>n.textContent).map(n=>n.getBBox());for(const node of g.selectAll('line').nodes()){if(node.getAttribute('stroke')!==L||+node.getAttribute('y1')!==+node.getAttribute('y2'))continue;const y=+node.getAttribute('y1'),a=+node.getAttribute('x1'),b=+node.getAttribute('x2'),cuts=labels.filter(q=>y>q.y-7&&y<q.y+q.height+7&&q.x<b&&q.x+q.width>a).map(q=>[Math.max(a,q.x-9),Math.min(b,q.x+q.width+9)]).sort((p,q)=>p[0]-q[0]);if(!cuts.length)continue;let x=a;for(const [lo,hi] of cuts){if(lo>x)line(g,x,y,lo,y,L,1);x=Math.max(x,hi)}if(x<b)line(g,x,y,b,y,L,1);node.remove();}});
// Use the same secondary ink for quiet labels throughout the film.
groups.forEach(g=>g.selectAll('text').filter(function(){return this.getAttribute('fill')===G}).attr('fill',D));
function bindText(g,id,label,n=0){const nodes=g.selectAll('text').nodes().filter(e=>e.textContent===label),node=nodes[n];if(!node)throw Error('Missing focus entity '+id+': '+label);node.setAttribute('data-focus-id',id);}
bindings.forEach((map,i)=>Object.entries(map).forEach(([id,[label,n]])=>bindText(groups[i],id,label,n||0)));
// Node targets reserve space outside the complete node, including its outline.
for(const [i,map] of [[3,{'impute':0,'scale':2,'select':4,'apply-model':7}],[10,{'input-data':0,'predictions':1,'real-error':2,'reevaluate':3}]])for(const [id,k] of Object.entries(map)){groups[i].select(`[data-focus-id="${id}"]`).attr('data-focus-id',null);groups[i].selectAll('rect').nodes()[k].setAttribute('data-focus-id',id);}
function markFocus(i,id,x,y){dot(groups[i],x,y,7,i===0?G:R).attr('data-focus-id',id)}
let gp=DATA.gridX.findIndex(x=>x>=.18),fit=DATA.fits[0];markFocus(0,'flexible-fit',150+(DATA.gridX[gp]+1)*800,830-(fit.prediction[gp]+1.8)/3.6*670);
markFocus(0,'controlled-fit',150+(DATA.gridX[gp]+1)*800,830-(DATA.fits[1].prediction[gp]+1.8)/3.6*670);
let sample=DATA.samplesXY.filter(d=>d[2]==='train')[25];markFocus(0,'samples',150+(sample[0]+1)*800,830-(sample[1]+1.8)/3.6*670);
let cv=DATA.candidates.filter(d=>d.alpha===.3);for(const [id,k] of [['cv-small',0],['cv-selected',1],['cv-large',cv.length-1]])markFocus(4,id,1110+(cv[k].degree-1)/16*650,770-cv[k].cvMSE/.3*570);
let e=DATA.earlyStopping,best=d3.minIndex(e.validationLoss);markFocus(7,'best-state',180+best/30*1550,800-e.validationLoss[best]*620);markFocus(7,'validation-curve',180+20/30*1550,800-e.validationLoss[20]*620);markFocus(7,'training-curve',180+24/30*1550,800-e.trainLoss[24]*620);
for(const [id,k,key] of [['train-error',0,'trainMSE'],['cv-error',0,'cvMSE'],['more-data',DATA.learning.length-1,'cvMSE'],['error-gap',1,'cvMSE']])markFocus(8,id,180+(DATA.learning[k].samples-35)/85*1550,810-DATA.learning[k][key]/.22*630);
const focusPlans=[],panRoutes=[],worldBlocks=[];let focusReady=false;
const overviewNames=['Objetivo','Datos','Separación','Preparación','Comparación','Validación','Regularización','Parada','Diagnóstico','Prueba','Producción'];
const overviewLabels=svg.insert('g','#guide').attr('opacity',0);
overviewNames.forEach((name,i)=>text(overviewLabels,cells[i][0]*.25+40,(cells[i][1]+540)*.25+32,name,28,I).attr('data-overview-index',i));
window.prepareFocus=()=>{
 if(focusReady)return focusPlans;
 LineWorldTheme.finish(svg.node());
 world.attr('transform','translate(0,0)');animated.forEach(a=>a.node.attr('opacity',1));
 const bounds={x0:30,y0:30,x1:1890,y1:1050};let origin={x:90,y:90};
 for(let i=0;i<12;i++){
  let obstacles=[],ports={};
  if(i<11){
   // getBBox is local to each text; the scene's world transform is not included.
   obstacles=groups[i].selectAll('text').nodes().filter(n=>n.textContent).map(n=>{const b=n.getBBox();return{x0:b.x,y0:b.y,x1:b.x+b.width,y1:b.y+b.height}});
   const marks=[];for(const node of groups[i].selectAll('path,line,rect,circle').nodes()){if(node.closest('defs'))continue;const fill=node.getAttribute('fill'),stroke=node.getAttribute('stroke');if(node.tagName==='circle'||node.tagName==='rect'){const b=node.getBBox();marks.push({x0:b.x,y0:b.y,x1:b.x+b.width,y1:b.y+b.height});}if(stroke&&stroke!=='none'&&stroke!==L&&typeof node.getTotalLength==='function'){const length=node.getTotalLength();for(let d=0;d<=length;d+=6){const p=node.getPointAtLength(d);marks.push({x0:p.x-2,y0:p.y-2,x1:p.x+2,y1:p.y+2});}}}
   for(const node of groups[i].selectAll('[data-focus-id]').nodes()){let b=node.getBBox(),box={x0:b.x,y0:b.y,x1:b.x+b.width,y1:b.y+b.height};const id=node.dataset.focusId;let candidates=[];if(i===9&&['frozen','hyperparameters','development'].includes(id)){const shell=groups[i].select('rect[data-lw-surface=\"group\"]').node().getBBox();box.x0=shell.x;box.x1=shell.x+shell.width;}
    if(i===0&&['controlled-fit','flexible-fit'].includes(id)){const fit=DATA.fits[id==='controlled-fit'?1:0];candidates=DATA.gridX.map((x,k)=>[150+(x+1)*800,830-(fit.prediction[k]+1.8)/3.6*670]).filter((p,k)=>k%18===0&&p[1]>180&&p[1]<810);}
    if(i===0&&id==='samples')candidates=DATA.samplesXY.filter(d=>d[2]==='train').map(d=>[150+(d[0]+1)*800,830-(d[1]+1.8)/3.6*670]);
    const choices=[null,...candidates];for(const candidate of choices){if(candidate)box={x0:candidate[0]-7,x1:candidate[0]+7,y0:candidate[1]-7,y1:candidate[1]+7};try{ports[id]=LineWorldFocus.port(box,bounds,[...obstacles,...marks],{gap:i===10&&id==='reevaluate'?58:18,side:'left'});if(candidate){node.setAttribute('cx',candidate[0]);node.setAttribute('cy',candidate[1]);}break}catch(error){if(candidate===choices.at(-1))throw Error(PRODUCTION.scenes[i].id+'/'+id+': '+error.message)}}
   }
   // Every landed port clears the maximum guide plus its keyline and marks.
   for(const [id,p] of Object.entries(ports))if(marks.some(b=>LineWorldFocus.overlap({x0:p.x-17,x1:p.x+17,y0:p.y-17,y1:p.y+17},b,3)))throw Error('Guide covers an important mark at '+id);
  }else{
   // The overview uses legible concept labels instead of unreadable miniature copy.
   groups.slice(0,11).forEach((g,j)=>{const [ox,oy]=cells[j];for(const n of g.selectAll('rect,circle').nodes()){if(n.closest('defs'))continue;const b=n.getBBox();obstacles.push({x0:(ox+b.x)*.25,x1:(ox+b.x+b.width)*.25,y0:(oy+b.y+540)*.25,y1:(oy+b.y+b.height+540)*.25});}});
   for(const n of overviewLabels.selectAll('text').nodes()){const b=n.getBBox();obstacles.push({x0:b.x,x1:b.x+b.width,y0:b.y,y1:b.y+b.height});}
   for(const [id,j] of Object.entries({'world-data':1,'world-split':2,'world-pipeline':3,'world-capacity':4,'world-validation':5,'world-test':9,'world-production':10,'world-all':5})){const n=overviewLabels.select('[data-overview-index="'+j+'"]').node(),b=n.getBBox(),box=id==='world-all'?{x0:0,y0:135,x1:1920,y1:945}:{x0:b.x,y0:b.y,x1:b.x+b.width,y1:b.y+b.height};ports[id]=LineWorldFocus.port(box,bounds,obstacles,{gap:18,side:'above'});}
   const last=focusPlans[10].cues.at(-1);origin={x:(cells[10][0]+last.x)*.25,y:(cells[10][1]+last.y+540)*.25};
  }
  if(i<11){const bodies=groups[i].selectAll('rect,circle').nodes().filter(n=>!n.closest('defs')).map(n=>{const b=n.getBBox();return{x0:b.x,y0:b.y,x1:b.x+b.width,y1:b.y+b.height}}),all=[...obstacles,...bodies];obstacles=all.filter((a,j)=>!all.some((b,k)=>k!==j&&(b.x1-b.x0)*(b.y1-b.y0)>(a.x1-a.x0)*(a.y1-a.y0)&&b.x0<=a.x0&&b.y0<=a.y0&&b.x1>=a.x1&&b.y1>=a.y1));worldBlocks.push(obstacles);}
  const cues=NARRATION_CUES.scenes[i].cues.map(c=>({...c,at:Math.max(i===11?PRODUCTION.motion.overviewSeconds:PRODUCTION.motion.panSeconds,c.at),...ports[c.target]}));
  if(i>0&&i<11)origin={x:cues[0].x,y:cues[0].y,target:cues[0].target};
  let from=origin;for(const c of cues){if(!Number.isFinite(c.x))throw Error('Unbound semantic cue '+c.target);c.path=LineWorldFocus.route(from,c,obstacles,bounds,{radius:10,gap:7});from=c;}
  focusPlans.push({cues,origin,obstacles});origin={x:from.x,y:from.y,target:from.target};
 }
 for(let i=1;i<11;i++){const a=cells[i-1],b=cells[i],old=focusPlans[i-1].cues.at(-1),first=focusPlans[i].origin,from={x:a[0]+old.x,y:a[1]+old.y},to={x:b[0]+first.x,y:b[1]+first.y},blocks=[...worldBlocks[i-1].map(q=>({x0:q.x0+a[0],x1:q.x1+a[0],y0:q.y0+a[1],y1:q.y1+a[1]})),...worldBlocks[i].map(q=>({x0:q.x0+b[0],x1:q.x1+b[0],y0:q.y0+b[1],y1:q.y1+b[1]}))];panRoutes[i]=LineWorldFocus.route(from,to,blocks,{x0:Math.min(a[0],b[0])+30,x1:Math.max(a[0],b[0])+1890,y0:Math.min(a[1],b[1])+30,y1:Math.max(a[1],b[1])+1050},{radius:10,gap:7});}
 focusReady=true;return focusPlans;
};
window.renderAt=(index,t)=>{
 const motion=window.PRODUCTION?.motion||{},pan=motion.panSeconds||.65,overview=motion.overviewSeconds||7;
 const move=ease(t/pan),prev=index?cells[index-1]:cells[0],target=cells[index];let cx=prev[0]+(target[0]-prev[0])*move,cy=prev[1]+(target[1]-prev[1])*move,scale=1;
 if(index===11){const q=ease(t/overview);scale=1-.75*q;cx=3840*(1-q)/scale;cy=(2160*(1-q)-135*q)/scale;}
 world.attr('transform',`scale(${scale}) translate(${-cx},${-cy})`);
 groups.forEach((g,i)=>{g.attr('opacity',i===11?0:1);g.selectAll('text').attr('opacity',index===11?1-ease(t/.5):1)});overviewLabels.attr('opacity',index===11?ease((t-overview)/.2):0);
 animated.forEach(a=>a.node.attr('opacity',1));
 route.attr('opacity',index===11?ease(t/5):0);
 const plan=focusReady?focusPlans[index]:null;let p=plan?LineWorldFocus.pose(plan.cues,t,plan.origin):{x:90,y:90,radius:10,target:null,moving:false};
 if(focusReady&&index>0&&index<11&&t<pan){const old=focusPlans[index-1].cues.at(-1),point=LineWorldFocus.visibleAlong(panRoutes[index],move,{x0:cx+30,x1:cx+1890,y0:cy+30,y1:cy+1050});p={x:point.x-cx,y:point.y-cy,radius:10-4*Math.sin(move*Math.PI),target:t===0?old.target:null,moving:true};}
 if(focusReady&&index===11&&t<overview){const old=focusPlans[10].cues.at(-1);p={x:(cells[10][0]+old.x-cx)*scale,y:(cells[10][1]+old.y-cy)*scale,radius:10*scale,target:old.target,moving:true};}
 guide.attr('stroke-width',index===11&&t<overview?4*scale:4);
 overviewLabels.selectAll('text').attr('fill',function(){return index===11&&p.target&&({'world-data':1,'world-split':2,'world-pipeline':3,'world-capacity':4,'world-validation':5,'world-test':9,'world-production':10}[p.target])===+this.dataset.overviewIndex?R:I});
 guide.attr('cx',p.x).attr('cy',p.y).attr('r',p.radius);
 const activeIndex=index===11?10:index&&t<pan?index-1:index,activeTarget=focusReady&&(index===11||index&&t<pan)?focusPlans[activeIndex].cues.at(-1).target:p.target;const key=activeIndex+':'+activeTarget;if(key!==window.lastPaint){const target=activeTarget?[...groups[activeIndex].node().querySelectorAll('[data-focus-id]')].find(e=>e.dataset.focusId===activeTarget):null;LineWorldTheme.focus(svg.node(),target,['baseline-bar','baseline-value'].includes(activeTarget)?'secondary':'primary');window.lastPaint=key;}
 window.state={camera:{x:cx,y:cy,scale},index,scale,cx,cy,guideColor:R,guideRadius:p.radius,guideX:p.x,guideY:p.y,target:p.target,moving:p.moving};return window.state;
};window.renderClip=window.renderAt;
window.snapshot=()=>structuredClone(window.state);
window.ready=document.fonts.ready.then(()=>{prepareFocus();return renderClip(0,0)});
window.renderAt(0,0);
