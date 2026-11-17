/* Project-owned composition. Spanish entity labels are required video source text. */
(()=>{'use strict';
const S=window.STORY, W=1920,H=1080, RED='#9e1b32',GRAY='#696969',QUIET='#e7e7e7',INK='#333e48';
const svg=document.querySelector('#stage'),media=document.querySelector('#media'),prior=document.querySelector('#prior');
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const DOCK={x:960,y:1040},bounds={x0:0,y0:0,x1:1920,y1:1080};
const box=(x,y,w,h)=>({x0:x,y0:y,x1:x+w,y1:y+h});
const text=(x,y,content,size=30,fill=INK,anchor='middle')=>`<text x="${x}" y="${y}" font-family="Space Grotesk" font-size="${size}" fill="${fill}" text-anchor="${anchor}" dominant-baseline="middle">${escape(content)}</text>`;
const rect=(x,y,w,h,fill)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}"/>`;
const floats=new Map(),cameras=new Map();
function floatFor(scene){if(!floats.has(scene.id))floats.set(scene.id,LineWorldGentleMotion.compile({id:scene.id+'-concepts',type:'float',start:scene.panSeconds+.2,end:scene.duration-.8,...S.motion.float}));return floats.get(scene.id);}
function cameraFor(scene){
 if(scene.kind!=='communication')return null;
 if(!cameras.has(scene.id)){const at=scene.cues.find(c=>c.target==='media-tv').at,c=S.motion.detail;cameras.set(scene.id,LineWorldGentleMotion.compile({id:scene.id+'-television',type:'detail',start:at-c.inSeconds,end:at+c.holdSeconds+c.outSeconds,width:S.layout.television.w,height:S.layout.television.h,...c}));}
 return cameras.get(scene.id);
}
function layout(scene){
 if(scene.kind==='overview')return scene.overview.map((item,i)=>({id:item.id,...S.layout.overview[i],label:item.label,file:`../artifacts/panels/${scene.id}-${i}.mp4`}));
 const items=[{id:'media-main',...S.layout.main,label:scene.context,file:`../artifacts/panels/${scene.id}-main.mp4`}];
 if(scene.kind==='communication')items.push({id:'media-tv',...S.layout.television,label:'Televisión',file:`../artifacts/panels/${scene.id}-tv.mp4`,camera:cameraFor(scene).spec});
 return items;
}
function nodes(scene){
 const maps={street:[['mobility','Movilidad'],['shops','Comercios'],['meeting','Encuentro']],fashion:[['day','Día'],['night','Noche'],['aspiration','Aspiración']],cinema:[['films','Películas'],['fashion','Moda'],['conversation','Conversación']],rights:[['rights','Derechos civiles'],['public-space','Espacio público'],['equality','Igualdad']]};
 if(scene.kind==='overview')return [];
 if(scene.kind==='communication')return [{id:'calls',label:'Llamadas',x:1345,y:830,w:230,h:88},{id:'coordination',label:'Coordinación',x:1690,y:830,w:230,h:88}];
 const positions=[[1370,310],[1695,535],[1370,760]];
 return maps[scene.kind].map(([id,label],i)=>({id,label,x:positions[i][0],y:positions[i][1],w:250,h:90}));
}
function endpoint(a,b){const dx=b.x-a.x,dy=b.y-a.y,k=Math.min((a.w/2)/Math.max(.001,Math.abs(dx)),(a.h/2)/Math.max(.001,Math.abs(dy)));return{x:a.x+dx*k,y:a.y+dy*k};}
function obstacles(scene){
 const a=layout(scene).flatMap(p=>[box(p.x,p.y,p.w,p.h),box(p.x,p.y+p.h+23,p.w,44)]);
 if(scene.kind!=='overview')a.push(box(126,982,710,30));
 const envelope=scene.kind==='overview'?{x:0,y:0}:floatFor(scene).envelope;
 return a.concat(nodes(scene).map(n=>box(n.x-n.w/2-envelope.x,n.y-n.h/2-envelope.y,n.w+2*envelope.x,n.h+2*envelope.y)));
}
const plans=new Map();
function plan(scene){
 if(plans.has(scene.id))return plans.get(scene.id);
 const obstaclesForScene=obstacles(scene),targets={};
 for(const p of layout(scene))targets[p.id]=box(p.x,p.y,p.w,p.h);
 for(const n of nodes(scene))targets[n.id]=box(n.x-n.w/2,n.y-n.h/2,n.w,n.h);
 const cues=[];let previous=DOCK;
 const first=scene.cues[0],firstAt=scene.panSeconds?scene.panSeconds+.52:0;
 const firstPort=LineWorldFocus.port(targets[first.target],bounds,obstaclesForScene.filter(b=>b!==targets[first.target]),{radius:18,gap:24,side:'left'});
 const events=[{...first,at:firstAt,travelSeconds:scene.panSeconds?.5:.01},...scene.cues];
 for(const cue of events){
  const p=cue===events[0]?firstPort:LineWorldFocus.port(targets[cue.target],bounds,obstaclesForScene,{radius:18,gap:24,side:'left'});
  const path=LineWorldFocus.route(previous,p,obstaclesForScene,bounds,{radius:18,gap:8});
  cues.push({...cue,x:p.x,y:p.y,path});previous=p;
 }
 const dockAt=scene.duration-.06, dockStart=scene.duration-.78;
 cues.push({target:'dock',at:dockAt,travelSeconds:dockAt-dockStart,x:DOCK.x,y:DOCK.y,path:LineWorldFocus.route(previous,DOCK,obstaclesForScene,bounds,{radius:18,gap:8})});
 const result={cues,obstacles:obstaclesForScene};plans.set(scene.id,result);return result;
}
function visual(scene,t,{guide=true}={}){
 const shift=scene.panSeconds?W*(1-ease(t/scene.panSeconds)):0;
 const motion=scene.kind==='overview'?{x:0,y:0,active:false}:floatFor(scene).at(t);
 let focus=LineWorldFocus.pose(plan(scene).cues,t,DOCK,{radius:9,focusRadius:16});
 const baseNodes=nodes(scene),nodeIds=new Set(baseNodes.map(n=>n.id));let blend=nodeIds.has(focus.target)?1:0;
 const cues=plan(scene).cues;
 for(let i=0;i<cues.length;i++){const cue=cues[i],travel=Math.max(.1,Math.min(.45,cue.travelSeconds||.28)),start=Math.max(0,cue.at-travel);if(t>=start&&t<cue.at){const u=ease((t-start)/Math.max(.001,cue.at-start)),from=i&&nodeIds.has(cues[i-1].target)?1:0,to=nodeIds.has(cue.target)?1:0;blend=from+(to-from)*u;break;}}
 focus={...focus,x:focus.x+motion.x*blend,y:focus.y+motion.y*blend};
 const ns=baseNodes.map(n=>({...n,x:n.x+motion.x,y:n.y+motion.y}));let ink='';
 const pairs=ns.length===3?[[0,1],[1,2],[2,0]]:ns.length===2?[[0,1]]:[];
 for(const [i,j] of pairs){
  const a=endpoint(ns[i],ns[j]),b=endpoint(ns[j],ns[i]),d=`M ${a.x} ${a.y} L ${b.x} ${b.y}`;
  ink+=`<path d="${d}" fill="none" stroke="${QUIET}" stroke-width="3"/>`;
  if(ns[i].id===focus.target||ns[j].id===focus.target)ink+=`<path d="${d}" fill="none" stroke="${RED}" stroke-width="3" stroke-dasharray="26 160" stroke-dashoffset="${-(t*42)%186}"/>`;
 }
 for(const n of ns){const active=n.id===focus.target;ink+=`<g data-focus-id="${n.id}">${rect(n.x-n.w/2,n.y-n.h/2,n.w,n.h,active?RED:QUIET)}${text(n.x,n.y,n.label,30,active?'#ffffff':INK)}</g>`;}
 for(const p of layout(scene)){
  const labelY=scene.kind==='overview'?p.y+p.h+42:p.id==='media-tv'?p.y+p.h+42:948;
  ink+=text(scene.kind==='overview'?p.x+p.w/2:p.id==='media-tv'?p.x+p.w/2:128,labelY,p.label,30,INK,scene.kind==='overview'||p.id==='media-tv'?'middle':'start');
 }
 if(scene.kind!=='overview')ink+=text(128,996,scene.kind==='street'?'NASA / NARA · Destockd':'NARA · Destockd',24,GRAY,'start');
 if(scene.kind==='communication'){
  const d=`M 1250 590 L 1205 590 L 1205 700 L ${1345+motion.x} 700 L ${1345+motion.x} ${786+motion.y}`;
  ink+=`<path d="${d}" fill="none" stroke="${QUIET}" stroke-width="3"/>`;
  if(focus.target==='calls'||focus.target==='media-tv')ink+=`<path d="${d}" fill="none" stroke="${RED}" stroke-width="3" stroke-dasharray="24 150" stroke-dashoffset="${-(t*40)%174}"/>`;
 }
 const transformed=`<g transform="translate(${shift} 0)">${ink}</g>`;
 const dot=guide?`<circle id="guide" cx="${focus.x}" cy="${focus.y}" r="${focus.radius}" fill="${RED}" stroke="#ffffff" stroke-width="3"/>`:'';
 return {markup:transformed+dot,focus,shift,sceneId:scene.id,t,placements:layout(scene),gentle:{float:motion,camera:cameraFor(scene)?.at(t)||null}};
}
function locate(seconds){const at=Math.max(0,Math.min(S.duration-1/S.fps,seconds));const index=S.scenes.findIndex(s=>at<s.end);return{scene:S.scenes[index],index,t:at-S.scenes[index].start,seconds:at};}
function renderAt(seconds,options={}){
 const state=locate(seconds),v=visual(state.scene,state.t,options);svg.innerHTML=v.markup;
 return{...state,...v,obstacles:plan(state.scene).obstacles};
}
const elements=new Map();let shownScene=null;
function syncMedia(state,{exact=false}={}){
 const loads=[];const active=new Set();
 for(const p of state.placements){
  const key=state.scene.id+'-'+p.id;active.add(key);
  let e=elements.get(key);
  if(!e){const holder=document.createElement('div');holder.style.position='absolute';holder.style.overflow='hidden';e=document.createElement('video');e.src=p.file;e.muted=true;e.playsInline=true;e.preload='auto';e.dataset.id=key;holder.append(e);media.append(holder);elements.set(key,e);}
  const holder=e.parentElement;holder.style.display='block';holder.style.left=(p.x+state.shift)+'px';holder.style.top=p.y+'px';holder.style.width=p.w+'px';holder.style.height=p.h+'px';
  e.style.display='block';e.style.left='0';e.style.top='0';e.style.width=p.w+'px';e.style.height=p.h+'px';
  const camera=p.camera?cameraFor(state.scene).at(state.t):{scale:1,x:0,y:0};e.style.transformOrigin='0 0';e.style.transform=`matrix(${camera.scale},0,0,${camera.scale},${camera.x},${camera.y})`;
  const set=()=>{const target=Math.min(Math.max(0,state.t),Math.max(0,e.duration-1/S.fps));if(Math.abs(e.currentTime-target)>.012)e.currentTime=target;};
  if(exact)loads.push((async()=>{
    if(e.readyState<1)await new Promise((ok,bad)=>{e.addEventListener('loadedmetadata',ok,{once:true});e.addEventListener('error',bad,{once:true});});
    const target=Math.min(Math.max(0,state.t),Math.max(0,e.duration-1/S.fps));
    if(Math.abs(e.currentTime-target)>.012)await new Promise((ok,bad)=>{e.addEventListener('seeked',ok,{once:true});e.addEventListener('error',bad,{once:true});e.currentTime=target;});
    if(Math.abs(e.currentTime-target)>.05)throw Error('The media seek did not reach its requested frame.');
  })());
  else if(e.readyState>=1)set();else loads.push(new Promise((ok,bad)=>{e.addEventListener('loadedmetadata',()=>{set();ok();},{once:true});e.addEventListener('error',bad,{once:true});}));
 }
 for(const [id,e] of elements)if(!active.has(id)){e.pause();e.style.display='none';e.parentElement.style.display='none';}
 if(state.index&&state.t<state.scene.panSeconds){
  const source=`../artifacts/stills/${S.scenes[state.index-1].id}-outgoing.jpg`;
  if(!prior.src.endsWith(source.replace('../','')))prior.src=source;
  prior.style.display='block';prior.style.transform=`translateX(${-W*ease(state.t/state.scene.panSeconds)}px)`;
 }else prior.style.display='none';
 shownScene=state.scene.id;return loads;
}
window.renderAt=renderAt;window.layoutFor=layout;window.scenePlan=scene=>plan(scene);window.locate=locate;
window.overlaySvg=(seconds,options={})=>{const v=renderAt(seconds,options);return`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">${v.markup}</svg>`;};
window.seekMedia=async seconds=>{const state=renderAt(seconds),pending=syncMedia(state,{exact:true});await Promise.all(pending);await new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok)));return{scene:state.scene.id,t:state.t,focus:state.focus,shift:state.shift};};
window.snapshot=()=>({scene:shownScene,svg:svg.innerHTML});
window.ready=document.fonts.ready.then(()=>{S.scenes.forEach(plan);const state=renderAt(0);if(!new URLSearchParams(location.search).has('graphics'))syncMedia(state);});
const audio=document.querySelector('#voice'),seek=document.querySelector('#seek'),play=document.querySelector('#play');seek.max=S.duration;
function resize(){document.querySelector('#canvas').style.transform=`scale(${innerWidth/1920})`;};addEventListener('resize',resize);resize();
function tick(){if(!audio.paused){const state=renderAt(audio.currentTime);syncMedia(state);seek.value=audio.currentTime;document.querySelector('#time').textContent=Math.floor(audio.currentTime/60)+':'+String(Math.floor(audio.currentTime%60)).padStart(2,'0');}requestAnimationFrame(tick);}requestAnimationFrame(tick);
play.onclick=()=>{if(audio.paused){audio.play();play.textContent='Pausar';}else{audio.pause();play.textContent='Reproducir';}};
seek.oninput=()=>{audio.currentTime=Number(seek.value);window.seekMedia(Number(seek.value));};audio.onended=()=>{play.textContent='Reproducir';};
})();
