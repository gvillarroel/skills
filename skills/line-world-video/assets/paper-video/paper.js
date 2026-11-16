/* Original source captures remain intact. One scene-local clock owns every overlay. */
"use strict";
const ORIGINAL=window.PAPER_STORY,P=window.PAPER_PAGES,NS="http://www.w3.org/2000/svg",RED="#9e1b32";
const ranges=[],expanded=[];
for(let s of ORIGINAL.scenes){let parts=[{at:0},...(s.shots||[])],range=[];for(let j=0;j<parts.length;j++){let part=parts[j],end=parts[j+1]?.at??s.duration,cues=s.cues.filter(c=>c.at>=part.at&&c.at<end).map(c=>({...c,at:c.at-part.at})),ids=new Set(cues.map(c=>c.target));let segment={...s,...part,id:s.id+"-"+j,duration:end-part.at,cues,targets:Object.fromEntries(Object.entries(s.targets).filter(([id])=>ids.has(id)))};if(j>0)delete segment.entry;range.push({index:expanded.length,start:part.at,end});expanded.push(segment)}ranges.push(range)}
const S={...ORIGINAL,scenes:expanded};
const pages=new Map(P.pages.map(p=>[p.page,p])),clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),ease=v=>(v=clamp(v))*v*(3-2*v);
function el(tag,attrs={},parent){let n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(parent)parent.append(n);return n}
function label(parent,value,x,y,size=28,attrs={}){let n=el("text",{x,y,"font-size":size,fill:"#444",...attrs},parent);n.textContent=value;return n}
function fit(r,b){let z=Math.min(b.w/(r[2]-r[0]),b.h/(r[3]-r[1]));return{z,x:b.x+(b.w-(r[2]-r[0])*z)/2-r[0]*z,y:b.y+(b.h-(r[3]-r[1])*z)/2-r[1]*z}}
function mapped(r,m){return{x:r[0]*m.z+m.x,y:r[1]*m.z+m.y,w:(r[2]-r[0])*m.z,h:(r[3]-r[1])*m.z}}
function overlap(a,b,p=0){return a.x-p<b.x+b.w&&a.x+a.w+p>b.x&&a.y-p<b.y+b.h&&a.y+a.h+p>b.y}
function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y)}
function port(r,obstacles,bounds){
 const d=32,c=[{x:r.x+r.w/2,y:r.y-d},{x:r.x-d,y:r.y+r.h/2},{x:r.x+r.w+d,y:r.y+r.h/2},{x:r.x+r.w/2,y:r.y+r.h+d}];
 for(let v of c)if(v.x>15&&v.x<1905&&v.y>15&&v.y<1065&&!obstacles.some(b=>overlap({x:v.x-10,y:v.y-10,w:20,h:20},b,2)))return v;
 for(let d=35;d<150;d+=15)for(let x of [r.x-d,r.x+r.w+d]){let v={x,y:r.y+r.h/2};if(v.x>15&&v.x<1905&&v.y>15&&v.y<1065&&!obstacles.some(b=>overlap({x:v.x-10,y:v.y-10,w:20,h:20},b,2)))return v}
 return{x:Math.max(20,bounds.x-24),y:Math.max(24,r.y-24)};
}
function route(a,b,obstacles){
 if(distance(a,b)<1)return[a,b];const grid=12,W=160,H=90,key=(x,y)=>y*W+x,cell=p=>[Math.round(p.x/grid),Math.round(p.y/grid)];
 let [sx,sy]=cell(a),[ex,ey]=cell(b),start=key(sx,sy),end=key(ex,ey),open=[start],cost=new Map([[start,0]]),came=new Map(),done=new Set();
 let blocked=new Set();for(let r of obstacles){let x0=Math.max(1,Math.ceil((r.x-12)/grid)),x1=Math.min(W-1,Math.floor((r.x+r.w+12)/grid)),y0=Math.max(1,Math.ceil((r.y-12)/grid)),y1=Math.min(H-1,Math.floor((r.y+r.h+12)/grid));for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)blocked.add(key(x,y))}blocked.delete(start);blocked.delete(end);
 const score=k=>(cost.get(k)||0)+Math.abs(k%W-ex)+Math.abs(Math.floor(k/W)-ey);
 while(open.length){open.sort((a,b)=>score(a)-score(b));let n=open.shift();if(n===end){let path=[b];while(n!==start){path.push({x:n%W*grid,y:Math.floor(n/W)*grid});n=came.get(n)}path.push(a);path.reverse();return path}if(done.has(n))continue;done.add(n);let x=n%W,y=Math.floor(n/W);for(let [dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){let X=x+dx,Y=y+dy,k=key(X,Y);if(X<1||X>=W||Y<1||Y>=H||blocked.has(k)||done.has(k))continue;let c=cost.get(n)+1;if(c<(cost.get(k)??Infinity)){cost.set(k,c);came.set(k,n);open.push(k)}}}
 return[a,{x:a.x,y:35},{x:b.x,y:35},b];
}
function along(path,t){let ds=path.slice(1).map((p,i)=>distance(p,path[i])),d=ds.reduce((a,b)=>a+b,0)*clamp(t);for(let i=0;i<ds.length;i++){if(d<=ds[i]){let u=ds[i]?d/ds[i]:0;return{x:path[i].x+(path[i+1].x-path[i].x)*u,y:path[i].y+(path[i+1].y-path[i].y)*u}}d-=ds[i]}return path.at(-1)}
const cache=new Map();
const rasterCache=new Map();
function clearRasterInk(page,m,source,ink){
 let data=rasterCache.get(page.page);if(!data){let bitmap=page.bitmap,canvas=document.createElement("canvas");canvas.width=bitmap.naturalWidth;canvas.height=bitmap.naturalHeight;let ctx=canvas.getContext("2d",{willReadFrequently:true});ctx.drawImage(bitmap,0,0);data={ctx,w:canvas.width,h:canvas.height};rasterCache.set(page.page,data)}
 const x1=Math.max(ink.x-3,source.x),y1=Math.max(ink.y-3,source.y),x2=Math.min(ink.x+ink.w+3,source.x+source.w),y2=Math.min(ink.y+ink.h+3,source.y+source.h);if(x2<=x1||y2<=y1)return true;
 const px=Math.max(0,Math.floor((x1-m.x)/m.z/page.size[0]*data.w)),py=Math.max(0,Math.floor((y1-m.y)/m.z/page.size[1]*data.h)),w=Math.min(data.w-px,Math.ceil((x2-x1)/m.z/page.size[0]*data.w)+2),h=Math.min(data.h-py,Math.ceil((y2-y1)/m.z/page.size[1]*data.h)+2);
 const pixels=data.ctx.getImageData(px,py,w,h).data;for(let n=0;n<pixels.length;n+=4)if(Math.min(pixels[n],pixels[n+1],pixels[n+2])<220)return false;return true;
}
function plan(i){
 if(cache.has(i))return cache.get(i);let s=S.scenes[i],bounds=s.layout==="table-side"?{x:55,y:150,w:950,h:720}:s.layout==="table-stack"?{x:110,y:70,w:1700,h:430}:{x:80,y:100,w:1760,h:860};
 let pageWords=pages.get(s.page).words,vr=PaperMotion.expandWords({x:s.view[0],y:s.view[1],w:s.view[2]-s.view[0],h:s.view[3]-s.view[1]},pageWords.map(w=>({x:w[0],y:w[1],w:w[2]-w[0],h:w[3]-w[1]}))),view=[vr.x,vr.y,vr.x+vr.w,vr.y+vr.h];
 let m=fit(view,bounds),source=mapped(view,m),words=pageWords.map(w=>mapped(w,m)).filter(r=>overlap(r,source)),regions=[...Object.values(s.targets),...(s.avoid||[])].map(r=>mapped(r,m)),obstacles=[...words,...regions],ports={},chart=null;
 for(let [id,r]of Object.entries(s.targets))ports[id]=port(mapped(r,m),obstacles,bounds);
 if(s.chart){let side=s.layout==="table-side",b=side?{x:1095,y:160,w:740,h:720}:{x:110,y:580,w:1700,h:430};chart={bounds:b,rowHeight:side?126:62,left:side?30:270,barWidth:side?650:1350,top:side?120:90};}
 let cues=s.cues.map(c=>{let p=ports[c.target];if(c.guide==="chart"&&chart){let ri=s.chart.rows.findIndex(r=>r.id===(c.row||c.target));if(ri<0)ri=0;let v=s.chart.rows[ri].values[c.column||0];p={x:chart.bounds.x+chart.left+v/100*chart.barWidth+25,y:chart.bounds.y+chart.top+ri*chart.rowHeight+15}}return{...c,port:p}});
 let previous=ports[s.cues[0]?.target]||{x:60,y:60};for(let c of cues){c.path=route(previous,c.port,obstacles);previous=c.port}
 const targets=Object.fromEntries(Object.entries(s.targets).map(([id,r])=>[id,PaperMotion.expandWords(mapped(r,m),words)]));
 const marks=Object.fromEntries(Object.entries(targets).map(([id,r])=>[id,PaperMotion.marginMarks(r,obstacles,s.emphasis||"margin",ink=>clearRasterInk(pages.get(s.page),m,source,ink))]));
 const camera=PaperMotion.cameraPlan({scene:s,source,targets,cues});
 let result={s,view,bounds,m,source,words,regions,ports,cues,chart,targets,marks,camera};cache.set(i,result);return result;
}
function chartDraw(group,p,c){let s=p.s,ch=s.chart,b=p.chart.bounds,side=s.layout==="table-side",col=c.column||0,row=c.row||c.target;
 el("line",side?{x1:1050,x2:1050,y1:0,y2:1080,stroke:"#c9c9c9","stroke-width":2}:{x1:0,x2:1920,y1:540,y2:540,stroke:"#c9c9c9","stroke-width":2},group);
 label(group,ch.columns[col],b.x+(side?25:270),b.y+25,side?27:30);label(group,ch.unit,b.x+(side?25:270),b.y+61,23,{fill:"#696969"});
 for(let [i,r]of ch.rows.entries()){let y=b.y+p.chart.top+i*p.chart.rowHeight,v=r.values[col],active=r.id===row,fill=active?RED:r.id==="gpt"||r.id==="oracle"?"#696969":"#bcbcbc",x=b.x+p.chart.left,w=v/100*p.chart.barWidth;
 if(side)label(group,r.label,b.x+30,y-18,26);else label(group,r.label,b.x+40,y+25,27);
 if(v>0)el("rect",{x,y,width:w,height:side?42:35,fill,stroke:"none"},group);else el("circle",{cx:x,cy:y+17,r:5,fill},group);
 let inside=w>70,ink=inside&&(active||r.id==="gpt"||r.id==="oracle")?"white":"#444";label(group,String(v).replace(".",","),inside?x+w-14:x+20,y+(side?30:26),side?28:26,{fill:ink,"text-anchor":inside?"end":"start"});}
}
function pose(i,t){let p=plan(i),s=p.s,t1=clamp(t,0,s.duration),ci=-1;const flight=c=>{const move=p.camera.moves.find(m=>m.kind==="pan"&&m.cueAt===c.at);return move?move.end-move.start:.28};for(let j=0;j<p.cues.length;j++)if(t1>=p.cues[j].at-flight(p.cues[j]))ci=j;let c=p.cues[Math.max(0,ci)]||{target:Object.keys(s.targets)[0],port:{x:60,y:60},path:[]},moving=ci>=0&&t1<c.at,progress=ci<0?1:ease((t1-c.at+flight(c))/flight(c)),guide=moving?along(c.path,progress):c.port;
 let camera=p.camera.at(t1);
 return{p,c,ci,t:t1,guide,r:moving?7:9+2*Math.exp(-Math.max(0,t1-c.at)*3),moving,camera};}
function draw(group,i,t,clipId){
 group.replaceChildren();let root=group,q=pose(i,t),{p,c,guide}=q,s=p.s,m=p.m,view=p.view,page=s.page;group=el("g",{transform:`matrix(${q.camera.k},0,0,${q.camera.k},${q.camera.x},${q.camera.y})`},root);
 let r=mapped(view,m),clip=document.querySelector(`#${clipId} rect`);for(let[k,v]of Object.entries({x:r.x,y:r.y,width:r.w,height:r.h}))clip.setAttribute(k,v);
 let container=el("g",{"clip-path":`url(#${clipId})`},group),image=pages.get(page);
 el("image",{href:image.image,x:m.x,y:m.y,width:image.size[0]*m.z,height:image.size[1]*m.z,"preserveAspectRatio":"none"},container);
 if(s.chart)chartDraw(group,p,c);
 const holdEnd=p.cues[q.ci+1]?.at??s.duration,activeMotion=t>=c.at&&holdEnd-c.at>2;q.emphasisPhase=activeMotion?+(((t-c.at)/3.2)%1).toFixed(6):null;
 if(!q.cover){for(const mark of p.marks[c.target]){const attrs={x1:mark.x,y1:mark.y,x2:mark.x+mark.w,y2:mark.y+mark.h,"stroke-linecap":"round","data-role":"paper-emphasis"};el("line",{...attrs,stroke:activeMotion?"#b5b5b5":RED,"stroke-width":activeMotion?1.5:2.5},group);if(activeMotion){const length=Math.hypot(mark.w,mark.h);el("line",{...attrs,stroke:RED,"stroke-width":2.5,"stroke-dasharray":`${length*.35} ${length*.65}`,"stroke-dashoffset":-length*q.emphasisPhase,"data-role":"paper-emphasis-motion"},group);}}el("circle",{cx:guide.x,cy:guide.y,r:q.r,fill:RED,stroke:"none"},group)}
 if(i===0&&s.entry&&t<6.4){let u=ease((t-4)/2.4),a=fit(s.entry.view,{x:260,y:50,w:1400,h:960}),b=mapped(s.entry.view,a),entry=el("g",{opacity:1-u},group),cp=document.querySelector("#clipEntry rect");for(let[k,v]of Object.entries({x:b.x,y:b.y,width:b.w,height:b.h}))cp.setAttribute(k,v);el("rect",{width:1920,height:1080,fill:"white"},entry);let im=pages.get(s.entry.page);el("image",{href:im.image,x:a.x,y:a.y,width:im.size[0]*a.z,height:im.size[1]*a.z,"clip-path":"url(#clipEntry)"},entry);q.cover=true;page=s.entry.page;}
 const attrib=`${S.source.version} · p. ${page} · ${S.source.license}`;label(root,attrib,1860,1036,24,{fill:"#777","text-anchor":"end"});
 return q;
}
function renderShot(i,t){i=clamp(Math.floor(i),0,S.scenes.length-1);t=clamp(t,0,S.scenes[i].duration);let current=document.getElementById("current"),previous=document.getElementById("previous"),q=draw(current,i,t,"clipA"),fade=i>0?ease(t/.65):1;current.setAttribute("opacity",fade);if(i>0&&fade<1){draw(previous,i-1,S.scenes[i-1].duration,"clipB");previous.setAttribute("opacity",1-fade)}else previous.replaceChildren();let issues=[];
 if(!q.cover&&fade===1){let g={x:q.guide.x-q.r,y:q.guide.y-q.r,w:q.r*2,h:q.r*2},cam=q.camera;if(g.x*cam.k+cam.x<0||g.y*cam.k+cam.y<0||(g.x+g.w)*cam.k+cam.x>1920||(g.y+g.h)*cam.k+cam.y>1080)issues.push("Guide is outside the frame.");for(let w of q.p.words)if(overlap(g,w,1)){issues.push("Guide intersects original paper text.");break}for(let b of q.p.regions)if(overlap(g,b)){issues.push("Guide intersects an annotated source body.");break}}
 if(!q.cover&&fade===1){for(const mark of q.p.marks[q.c.target])if([...q.p.words,...q.p.regions].some(b=>overlap(mark.ink,b,2)))issues.push("Emphasis ink intersects original content.");
  if(!q.moving){const f=q.p.targets[q.c.target],cam=q.camera;if(f.x*cam.k+cam.x<18||f.y*cam.k+cam.y<18||(f.x+f.w)*cam.k+cam.x>1902||(f.y+f.h)*cam.k+cam.y>1035)issues.push("Active source region is cropped by the frame.");}}
 let result={shot:S.scenes[i].id,page:q.cover?1:S.scenes[i].page,target:q.c.target,guide:{x:+(q.guide.x*q.camera.k+q.camera.x).toFixed(3),y:+(q.guide.y*q.camera.k+q.camera.y).toFixed(3),r:+(q.r*q.camera.k).toFixed(3)},camera:Object.fromEntries(Object.entries(q.camera).map(([k,v])=>[k,+v.toFixed(5)])),cameraMode:q.p.camera.mode,emphasisMarks:q.cover?0:q.p.marks[q.c.target].length,emphasisPhase:q.cover?null:q.emphasisPhase,fade:+fade.toFixed(4),cover:!!q.cover,column:q.c.column||0,issues};window.lastState=result;return result;}
window.renderClip=function(i,t){i=clamp(Math.floor(i),0,ORIGINAL.scenes.length-1);t=clamp(t,0,ORIGINAL.scenes[i].duration);let part=ranges[i].find(r=>t<r.end)||ranges[i].at(-1),result=renderShot(part.index,t-part.start);result.scene=ORIGINAL.scenes[i].id;window.lastState=result;return result};
window.renderAt=function(t){let start=0;for(let i=0;i<ORIGINAL.scenes.length;i++){if(t<start+ORIGINAL.scenes[i].duration||i===ORIGINAL.scenes.length-1)return window.renderClip(i,t-start);start+=ORIGINAL.scenes[i].duration}};
window.snapshot=()=>window.lastState;
window.ready=Promise.all(P.pages.map(p=>new Promise((resolve,reject)=>{let im=new Image();im.onload=()=>{p.bitmap=im;resolve()};im.onerror=()=>reject(Error("PDF page image failed"));im.src=p.image}))).then(()=>{window.renderAt(0);return true});
if(new URLSearchParams(location.search).has("capture"))document.body.classList.add("capture");
const slider=document.getElementById("seek"),total=ORIGINAL.scenes.reduce((a,s)=>a+s.duration,0);slider.max=total;let playing=false,last=0,clock=0;
function seek(t){clock=clamp(t,0,total);slider.value=clock;document.getElementById("time").value=`${clock.toFixed(1)} / ${total.toFixed(1)} s`;renderAt(clock)}slider.oninput=()=>seek(+slider.value);document.getElementById("play").onclick=()=>{playing=!playing;document.getElementById("play").textContent=playing?"Pause":"Play";last=performance.now()};function tick(now){if(playing){seek(clock+(now-last)/1000);if(clock>=total)playing=false}last=now;requestAnimationFrame(tick)}requestAnimationFrame(tick);
