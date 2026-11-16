/* Shared, deterministic attention and quantity-point choreography. No timer. */
(() => {
'use strict';
const PRIMARY_RED='#9e1b32';
const defaults={guideColor:PRIMARY_RED,baseRadius:9,travelRadius:6,focusRadius:22,emitRadius:32,pointRadius:4.5,emissionSeconds:.34,flightSeconds:.55,unitPerPoint:null,categoryColors:{},emissionViews:['network','circle-pack','donut']};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},mix=(a,b,u)=>a+(b-a)*u;
function settings(value={}){return {...defaults,...value,guideColor:PRIMARY_RED,categoryColors:{...(value.categoryColors||{})}};}
function unitFor(values,explicit){if(explicit)return explicit;const max=Math.max(...values,0);if(!max)return 1;const target=max/16,m=Math.pow(10,Math.floor(Math.log10(target)));return [1,2,5,10].map(v=>v*m).find(v=>v>=target-1e-12)||10*m;}
function tokens(value,unit){if(!Number.isFinite(value)||value<0||!Number.isFinite(unit)||unit<=0)throw Error('Invalid quantity-point value or unit.');const n=Math.ceil(value/unit-1e-10);if(n>64)throw Error('Use a larger unit per point; at most 64 points per entity.');return Array.from({length:Math.max(0,n)},(_,i)=>({index:i,quantity:Math.min(unit,Math.max(0,value-i*unit)),weight:Math.min(1,Math.max(0,value/unit-i))}));}
function windowFor(config,hold,panes){const start=.38/panes+.035,span=Math.min(config.emissionSeconds,hold*Math.max(.04,1/panes-start-.025)),flight=Math.min(config.flightSeconds,hold*.35);return {startPhase:start,span,flight};}
function radius(config,{phase=0,travel=null,hold=2,panes=2,emitting=false}={}){
 if(travel!==null)return mix(config.travelRadius,config.focusRadius,ease((travel-.6)/.4));
 let r=mix(config.baseRadius,config.focusRadius,1-ease(phase/.18));
 if(emitting){const w=windowFor(config,hold,panes),p=(phase*hold-w.startPhase*hold)/w.span;if(p>=0&&p<=1)r=Math.max(r,mix(config.baseRadius,config.emitRadius,Math.sin(Math.PI*p)**2));}
 return r;
}
function sample({time,birth,flight,origin,target,radius,weight=1}){const active=time>=birth,p=clamp((time-birth)/flight),u=ease(p),bend=Math.min(90,Math.hypot(target.x-origin.x,target.y-origin.y)*.12),round=v=>Math.round(v*1e6)/1e6;return {x:round(mix(origin.x,target.x,u)),y:round(mix(origin.y,target.y,u)-Math.sin(Math.PI*u)*bend),radius:active?radius*Math.sqrt(weight)*mix(.3,1,ease(p/.5)):0,opacity:active?1:0,landed:active&&p>=1};}
function clearPort(label,bounds,obstacles,r){const cx=(label.x0+label.x1)/2,cy=(label.y0+label.y1)/2,candidates=[];for(const pad of [12,34,64])candidates.push({x:cx,y:label.y0-r-pad},{x:label.x0-r-pad,y:cy},{x:label.x1+r+pad,y:cy},{x:cx,y:label.y1+r+pad});
 const score=p=>{const outside=Math.max(0,bounds.x0+r-p.x)+Math.max(0,p.x+r-bounds.x1)+Math.max(0,bounds.y0+r-p.y)+Math.max(0,p.y+r-bounds.y1);let overlap=0;for(const b of obstacles)overlap+=Math.max(0,Math.min(p.x+r+6,b.x1)-Math.max(p.x-r-6,b.x0))*Math.max(0,Math.min(p.y+r+6,b.y1)-Math.max(p.y-r-6,b.y0));return outside*1e6+overlap*1e3+Math.hypot(p.x-cx,p.y-cy);};
 return candidates.sort((a,b)=>score(a)-score(b))[0];
}
globalThis.LineWorldAttention=Object.freeze({PRIMARY_RED,defaults,settings,unitFor,tokens,windowFor,radius,sample,clearPort});
})();
