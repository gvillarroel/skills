/* Pure paper camera and margin-mark geometry. No DOM, network or mutable clock. */
(function(root){
  "use strict";
  const W=1920,H=1080,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const smooth=t=>(t=clamp(t,0,1))*t*t*(t*(t*6-15)+10);
  const intersects=(a,b,p=0)=>a.x-p<b.x+b.w&&a.x+a.w+p>b.x&&a.y-p<b.y+b.h&&a.y+a.h+p>b.y;
  const union=(a,b)=>({x:Math.min(a.x,b.x),y:Math.min(a.y,b.y),w:Math.max(a.x+a.w,b.x+b.w)-Math.min(a.x,b.x),h:Math.max(a.y+a.h,b.y+b.h)-Math.min(a.y,b.y)});
  function expandWords(rect,words){
    let result={...rect};
    for(let n=0;n<4;n++){let before=JSON.stringify(result);for(const word of words)if(intersects(result,word))result=union(result,word);if(JSON.stringify(result)===before)break;}
    return result;
  }
  function marginMarks(f,obstacles,style="margin",clearRaster=()=>true){
    if(style==="none")return [];
    const marks=[];
    for(const gap of [14,22,34,50,72]){
      const len=Math.min(30,Math.max(14,f.h*.4)),cy=f.y+f.h/2,cx=f.x+f.w/2;
      const candidates=[{x:f.x-gap,y:cy-len/2,w:0,h:len},{x:f.x+f.w+gap,y:cy-len/2,w:0,h:len},
        {x:cx-15,y:f.y-gap,w:30,h:0},{x:cx-15,y:f.y+f.h+gap,w:30,h:0}];
      for(const line of candidates){let ink={x:line.x-2,y:line.y-2,w:line.w+4,h:line.h+4};
        if(ink.x<18||ink.y<18||ink.x+ink.w>W-18||ink.y+ink.h>H-45||obstacles.some(b=>intersects(ink,b,4))||!clearRaster(ink))continue;
        if(!marks.length||Math.abs(line.x-marks[0].x)>f.w/2){marks.push({...line,ink});if(marks.length===2)return marks;}
      }
      if(marks.length)return marks;
    }
    return marks; // A guide alone is preferable when no clear margin exists.
  }
  function cameraPlan(input){
    const s=input.scene,config={zoom:1.3,enterSeconds:2.6,travelSeconds:2,minTravelSeconds:1.4,minHoldSeconds:1.1,safeInset:58,maxPanSpeed:540,...(s.camera||{})};
    const identity={k:1,x:0,y:0};
    if(s.layout!=="paper"||s.cameraZoom===false||config.mode==="static"||s.duration<6)return {mode:"static",at:()=>({...identity}),moves:[],zoom:1};
    const inset=config.safeInset,focus=input.cues.map(c=>({at:c.at,box:union(input.targets[c.target],{x:c.port.x-14,y:c.port.y-14,w:28,h:28})}));
    let k=Math.max(1,Math.min(config.zoom,...focus.map(f=>Math.min((W-2*inset)/f.box.w,(H-2*inset)/f.box.h))));
    const source=input.source;
    function target(box){
      let x=W/2-k*(box.x+box.w/2),y=H/2-k*(box.y+box.h/2);
      for(const axis of [{key:"x",size:"w",full:W},{key:"y",size:"h",full:H}]){
        const {key,size,full}=axis,span=source[size]*k;
        let value=key==="x"?x:y;
        value=span>full-160?clamp(value,full-80-k*(source[key]+source[size]),80-k*source[key]):full/2-k*(source[key]+source[size]/2);
        value=clamp(value,inset-k*box[key],full-inset-k*(box[key]+box[size]));
        if(key==="x")x=value;else y=value;
      }
      return {k,x,y};
    }
    function visible(box,cam){return box.x*k+cam.x>=inset-1&&box.y*k+cam.y>=inset-1&&(box.x+box.w)*k+cam.x<=W-inset+1&&(box.y+box.h)*k+cam.y<=H-inset+1;}
    let start=s.entry?6.4:.6,end=start+config.enterSeconds,current=target(focus[0].box),moves=[{start,end,from:identity,to:current,kind:"enter"}],lastAt=focus[0].at;
    for(const f of focus.slice(1)){
      let next=target(f.box),distance=Math.hypot(next.x-current.x,next.y-current.y);
      if(distance<90){lastAt=f.at;continue;}
      const duration=Math.max(config.travelSeconds,distance*1.875/config.maxPanSpeed);
      let begin=Math.max(end+config.minHoldSeconds,lastAt+config.minHoldSeconds,f.at-duration);
      if(f.at-begin<Math.max(config.minTravelSeconds,distance*1.875/config.maxPanSpeed)){
        if(visible(f.box,current)){lastAt=f.at;continue;}
        return {mode:"static-dense-cues",at:()=>({...identity}),moves:[],zoom:1};
      }
      moves.push({start:begin,end:f.at,from:current,to:next,kind:"pan",cueAt:f.at});current=next;end=f.at;lastAt=f.at;
    }
    return {mode:"pan",zoom:k,moves,at(t){let current=identity;for(const move of moves){if(t<move.start)break;const u=smooth((t-move.start)/(move.end-move.start));current={k:move.from.k+(move.to.k-move.from.k)*u,x:move.from.x+(move.to.x-move.from.x)*u,y:move.from.y+(move.to.y-move.from.y)*u};if(t<move.end)break;}return current;}};
  }
  root.PaperMotion={expandWords,marginMarks,cameraPlan};
  if(typeof module!=="undefined")module.exports=root.PaperMotion;
})(globalThis);
