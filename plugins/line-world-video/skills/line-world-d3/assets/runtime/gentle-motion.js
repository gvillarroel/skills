/* Small parent-clock float and image-detail motions. No autonomous timers. */
(() => {'use strict';
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},round=x=>Math.round(x*1e7)/1e7;
const number=(v,label)=>{if(!Number.isFinite(v))throw Error(label+' must be finite.');return v;};
function phase(id){let h=2166136261;for(const c of id)h=Math.imul(h^c.charCodeAt(0),16777619);return(h>>>0)/4294967296*Math.PI*2;}
function compile(input,{reducedMotion=false}={}){
 const s={...input};
 if(!s.id||typeof s.id!=='string')throw Error('Use a stable motion ID.');
 number(s.start,'start');number(s.end,'end');if(s.start<0||s.end<=s.start)throw Error('Declare a positive parent-clock window.');
 if(s.type==='float'){
  s.amplitudeX=s.amplitudeX??3;s.amplitudeY=s.amplitudeY??8;s.period=s.period??10;s.settleSeconds=s.settleSeconds??1.5;s.phase=s.phase??phase(s.id);
  for(const key of ['amplitudeX','amplitudeY','period','settleSeconds','phase'])number(s[key],key);
  if(s.amplitudeX<0||s.amplitudeX>8||s.amplitudeY<0||s.amplitudeY>12||s.period<8||s.settleSeconds<1)throw Error('Keep float amplitudes within 8/12 units, period at least 8 s and settling at least 1 s.');
  if(s.end-s.start<2*s.settleSeconds)throw Error('Reserve both float settling windows.');
 }else if(s.type==='detail'){
  s.zoom=s.zoom??1.10;s.inSeconds=s.inSeconds??4;s.holdSeconds=s.holdSeconds??3;s.outSeconds=s.outSeconds??4;
  for(const key of ['zoom','inSeconds','holdSeconds','outSeconds','width','height'])number(s[key],key);
  if(s.zoom<=1||s.zoom>1.2||s.inSeconds<3||s.outSeconds<3||s.holdSeconds<3||s.width<=0||s.height<=0)throw Error('Use zoom up to 1.2, at least 3 s each way, and a reading hold of at least 3 s.');
  if(s.end-s.start+1e-6<s.inSeconds+s.holdSeconds+s.outSeconds)throw Error('Do not compress a detail cycle into a short scene.');
  if(!Array.isArray(s.focus)||s.focus.length!==4||s.focus.some(v=>!Number.isFinite(v)||v<0||v>1)||s.focus[0]>=s.focus[2]||s.focus[1]>=s.focus[3])throw Error('Use a reviewed normalized focus rectangle.');
 }else throw Error('Use type float or detail.');
 const envelope=s.type==='float'?{x:s.amplitudeX,y:s.amplitudeY}:{x:0,y:0};
 function at(t){
  number(t,'parent time');const identity={id:s.id,type:s.type,active:false,x:0,y:0,scale:1,sourceX:0,sourceY:0};
  if(reducedMotion||t<=s.start||t>=s.end)return identity;
  let x=0,y=0,scale=1,sourceX=0,sourceY=0;
  if(s.type==='float'){
   const fade=Math.min(ease((t-s.start)/s.settleSeconds),ease((s.end-t)/s.settleSeconds)),a=(t-s.start)/s.period*Math.PI*2;
   x=Math.sin(a+s.phase)*s.amplitudeX*fade;y=Math.sin(a+s.phase+Math.PI/2)*s.amplitudeY*fade;
  }else{
   const enter=ease((t-s.start)/s.inSeconds),leave=ease((t-s.start-s.inSeconds-s.holdSeconds)/s.outSeconds),p=enter*(1-leave);
   scale=1+(s.zoom-1)*p;
   sourceX=Math.max(0,Math.min(s.width-s.width/scale,(s.focus[0]+s.focus[2])/2*s.width-s.width/(2*scale)));
   sourceY=Math.max(0,Math.min(s.height-s.height/scale,(s.focus[1]+s.focus[3])/2*s.height-s.height/(2*scale)));
   x=-sourceX*scale;y=-sourceY*scale;
  }
  return {...identity,active:Math.abs(x)+Math.abs(y)+Math.abs(scale-1)>1e-8,x:round(x),y:round(y),scale:round(scale),sourceX:round(sourceX),sourceY:round(sourceY)};
 }
 return Object.freeze({spec:Object.freeze(s),envelope:Object.freeze(envelope),at});
}
function attach(root,inputs,options={}){
 if(!root||!Array.isArray(inputs))throw Error('Supply an SVG root and motion windows.');
 const ids=new Set(),entries=inputs.map(input=>{
  if(ids.has(input.id))throw Error('Motion IDs must be unique.');ids.add(input.id);
  const controller=compile(input,options),matches=root.querySelectorAll(input.target||'');
  if(matches.length!==1||matches[0].tagName.toLowerCase()!=='g')throw Error('Target one project-owned SVG g wrapper.');
  const element=matches[0],transform=element.getAttribute('transform');
  if(transform?.trim()||getComputedStyle(element).transform!=='none')throw Error('Keep authored transforms inside the motion wrapper.');
  if(input.type==='detail'&&!element.querySelector('image'))throw Error('A detail wrapper must contain the original source image inside a fixed clipped viewport.');
  return {controller,element,transform};
 });
 let last=[];
 return {
  ready:document.fonts?.ready||Promise.resolve(),
  render(t){last=entries.map(({controller,element})=>{const state=controller.at(t);element.setAttribute('transform',`matrix(${state.scale} 0 0 ${state.scale} ${state.x} ${state.y})`);return state;});return structuredClone(last);},
  snapshot:()=>structuredClone(last),
  destroy(){for(const {element,transform} of entries){if(transform===null)element.removeAttribute('transform');else element.setAttribute('transform',transform);}last=[];}
 };
}
globalThis.LineWorldGentleMotion=Object.freeze({compile,attach});
})();
