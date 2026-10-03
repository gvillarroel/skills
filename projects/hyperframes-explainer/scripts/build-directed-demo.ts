#!/usr/bin/env -S node --experimental-strip-types
// Run: node projects/hyperframes-explainer/scripts/build-directed-demo.ts
// Authoring dependencies: installed d3 skill's pinned D3 7.9.0; SVG and procedural skill guidance.
import path from 'node:path';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import vm from 'node:vm';
const root = process.cwd();
const base = path.join(root, 'projects/hyperframes-explainer/artifacts/directed');
const d3Exports = {};
vm.runInNewContext(readFileSync(path.join(root, '.agents/skills/d3/assets/vendor/d3.v7.9.0.min.js'), 'utf8'), {exports: d3Exports, module: {exports: d3Exports}});
const d3 = d3Exports as any;
const palettes = JSON.parse(readFileSync('skills/hyperframes-explainer/assets/palettes/colorsets.json', 'utf8')).colorsets;
function save(file, value) {mkdirSync(path.dirname(file), {recursive: true}); writeFileSync(file, typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');}
for (const mode of ['colorset1', 'colorset2']) {
  const dir = path.join(base, mode), p = palettes[mode].roles;
  const fluid = mode==='colorset2' ? p.secondary : p.primary;
  const fluidRole = mode==='colorset2' ? 'secondary' : 'primary';
  const prefix = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1030 920" data-colorset="${mode}" font-family="Explainer"><title>Controlled inlet and calibrated reservoir</title><desc>Illustrative ideal tank with a rotating valve, connected inlet and proportional stored-volume cutaway.</desc>`;
  const mechanism = `${prefix}
<path id="tank-shell" d="M640 312 V780 C640 832 940 832 940 780 V312" fill="${p.surface}" stroke="${p.ink}" stroke-width="5"/>
<ellipse id="tank-cap" cx="790" cy="312" rx="150" ry="38" fill="${p.surface}" stroke="${p.ink}" stroke-width="5"/>
<rect id="fluid" x="655" y="610" width="270" height="170" fill="${fluid}" stroke="none"/>
<line id="waterline" x1="655" x2="925" y1="610" y2="610" stroke="${fluid}" stroke-width="5"/>
<path id="tank-bottom" d="M640 780 C640 825 940 825 940 780" fill="none" stroke="${p.ink}" stroke-width="5"/>
<path id="tank-feet" d="M665 810 V850 H700 V820 M880 820 V850 H915 V810" fill="none" stroke="${p.ink}" stroke-width="5"/>
<path id="capacity-rail" d="M960 314 H973 V780 H960" fill="none" stroke="${p.muted}" stroke-width="2"/>
${[0,20,40,60,80].map((v,i)=>`<line id="capacity-${v}" x1="955" y1="${780-v*5.825}" x2="${v%40===0?979:967}" y2="${780-v*5.825}" stroke="${p.muted}" stroke-width="2"/>${v%40===0?`<text id="capacity-label-${v}" x="1020" y="${790-v*5.825}" text-anchor="end" font-size="26" fill="${p.ink}" stroke="none">${v}</text>`:''}`).join('')}
<rect id="pipe-shell" x="100" y="305" width="555" height="50" rx="25" fill="${p.quiet}" stroke="${p.ink}" stroke-width="3"/>
<rect id="pipe-channel" x="101" y="317" width="554" height="26" rx="13" fill="${p.surface}" stroke="none"/>
<path id="valve-body" d="M305 283 H405 L430 305 V355 L405 377 H305 L280 355 V305 Z" fill="${p.surface}" stroke="${p.ink}" stroke-width="5"/>
<path id="open-channel" d="M280 317 H430 M280 343 H430" fill="none" stroke="${p.line}" stroke-width="2"/>
<line id="valve-gate" x1="342" y1="306" x2="368" y2="354" stroke="${p.primary}" stroke-width="10"/>
<circle id="gate-bearing" cx="355" cy="330" r="5" fill="${p.ink}" stroke="none"/>
<line id="valve-stem" x1="355" y1="230" x2="355" y2="283" stroke="${p.ink}" stroke-width="6"/>
<circle id="wheel-rim" cx="355" cy="180" r="50" fill="none" stroke="${p.primary}" stroke-width="6"/>
<path id="wheel" d="M-50 0 H50 M0 -50 V50 M-35 -35 L35 35 M-35 35 L35 -35" transform="translate(355 180)" fill="none" stroke="${p.primary}" stroke-width="4"/>
<circle id="wheel-hub" cx="355" cy="180" r="9" fill="${p.primary}" stroke="none"/>
<path id="flow-direction" d="M130 405 H235 M225 395 L235 405 L225 415" fill="none" stroke="${p.ink}" stroke-width="3"/>
<text id="flow-label" x="485" y="252" font-size="40" fill="${p.primary}" stroke="none">Flow</text>
<text id="stored-label" x="640" y="905" font-size="40" fill="${fluid}" stroke="none">Stored</text>
</svg>`;
  save(path.join(dir,'assets/mechanism.svg'),mechanism);
  const particles = `${prefix}${d3.range(9).map(i=>`<circle id="tracer-${i}" cx="${110+i*58}" cy="330" r="5" fill="${fluid}" stroke="none"/>`).join('')}</svg>`;
  save(path.join(dir,'assets/transport.svg'),particles);
  const axes = (name,max,unit) => {
    const x=d3.scaleLinear().domain([0,16]).range([56,581]);
    const y=d3.scaleLinear().domain([0,max]).range([280,45]);
    const out=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 370" data-colorset="${mode}" font-family="Explainer"><title>${name} history scales</title><desc>Fixed linear domains. Geometry is authored with D3; live curves use the same canonical state.</desc>`];
    for(const v of [0,max/2,max]) {
      const grid=d3.path();grid.moveTo(56,y(v));grid.lineTo(581,y(v));
      out.push(`<path id="grid-${v===0?'zero':v===max?'max':'mid'}" d="${grid}" fill="none" stroke="${p.line}" stroke-width="2"/>`);
      out.push(`<text id="tick-${v===0?'zero':v===max?'max':'mid'}" x="39" y="${y(v)+9}" text-anchor="end" font-size="26" fill="${p.ink}" stroke="none">${v}</text>`);
    }
    for(const t of [0,8,16])out.push(`<line id="time-tick-${t}" x1="${x(t)}" x2="${x(t)}" y1="280" y2="288" stroke="${p.ink}" stroke-width="2"/><text id="time-${t}" x="${x(t)}" y="324" text-anchor="middle" font-size="26" fill="${p.ink}" stroke="none">${t}</text>`);
    out.push(`<text id="unit" x="56" y="31" font-size="28" fill="${p.ink}" stroke="none">${unit}</text><text id="seconds" x="621" y="324" text-anchor="end" font-size="28" fill="${p.ink}" stroke="none">s</text></svg>`);
    return out.join('');
  };
  save(path.join(dir,'assets/rate-scale.svg'),axes('Inlet rate',5,'L/s'));
  save(path.join(dir,'assets/volume-scale.svg'),axes('Stored volume',80,'L'));
  const brief = {
    schemaVersion:1,id:`hyperframes-inlet-${mode==='colorset1'?'cs1':'cs2'}`,language:'en',
    claim:'The valve changes the inlet rate; transport speed, reservoir filling speed and history slopes respond to that same change.',
    evidence:'Illustrative imposed inlet, no outflow, constant tank cross-section and capacity 80 L. Wheel/aperture motion represents the control, not a measured hydraulic law. Tracers qualitatively show transport; stored volume is the exact analytic integral. D3 authors fixed linear scales; no autonomous asset clock.',
    output:{width:1920,height:1080,fps:30,duration:16},
    palette:{mode,decision:mode==='colorset1'?'default':'explicit',reason:mode==='colorset1'?'One controlled fluid can be explained with red and neutral structure.':'Requested second palette demonstration: red denotes the actuator/rate and blue the transported/stored fluid.'},
    sources:{rate:{value:2,domain:[0,5],unit:'L/s'}},derived:{volume:{expr:{integrate:['rate','time']},unit:'L'},valveAngle:{expr:{mul:[{sub:[90,{mul:['rate',16]}]},Math.PI/180]},unit:'rad'}},
    events:[{id:'open-valve',at:4,duration:2,changes:{rate:4},cause:'The inlet control opens further.'},{id:'restrict-valve',at:10,duration:2,changes:{rate:1},cause:'The inlet control restricts the flow.'}],
    entities:{water:fluidRole},
    views:[{id:'mechanism',question:'How does the valve change transport and storage?',region:[65,55,1030,920],importance:'main'},
      {id:'rate',question:'How does the input rate change over time?',region:[1190,105,650,370],importance:'support'},
      {id:'volume',question:'How does input history determine the stored amount?',region:[1190,605,650,370],importance:'support'}],
    marks:[{id:'rate-history',view:'rate',kind:'plot',attrs:{x:56,y:45,width:525,height:235},xValue:'time',yValue:'rate',xDomain:[0,16],yDomain:[0,5],samples:240,fill:'none',stroke:'primary',strokeWidth:5},
      {id:'volume-history',view:'volume',kind:'plot',attrs:{x:56,y:45,width:525,height:235},xValue:'time',yValue:'volume',xDomain:[0,16],yDomain:[0,80],samples:240,fill:'none',stroke:fluidRole,strokeWidth:5}]
  };
  const level={sub:[780,{mul:['volume',5.825]}]};
  const vx={mul:[27,{cos:['valveAngle']}]},vy={mul:[27,{sin:['valveAngle']}]};
  const bindings={fluid:{attrs:{y:level,height:{mul:['volume',5.825]}}},waterline:{attrs:{y1:level,y2:level}},
    'valve-gate':{attrs:{x1:{sub:[355,vx]},y1:{sub:[330,vy]},x2:{add:[355,vx]},y2:{add:[330,vy]}}},wheel:{attrs:{rotation:{mul:['rate',30]}}},
    'flow-label':{value:'rate',unit:'L/s',digits:1},'stored-label':{value:'volume',unit:'L',digits:1}};
  const tracerBindings=Object.fromEntries(d3.range(9).map(i=>[`tracer-${i}`,{attrs:{cx:{add:[110,{mul:[530,{mod:[{add:[{mul:['volume',.09]},i/9]},1]}]}]},r:{mul:[5,{sqrt:{div:['rate',5]}}]}}}]));
  // Expressions have arrays of operands, including unary sqrt.
  for(const b of Object.values(tracerBindings) as any[]) b.attrs.r={mul:[6,{sqrt:[{div:['rate',5]}]}]};
  const allMoments=['establish','open-valve','restrict-valve','hold'];
  const plan={schemaVersion:1,assets:[
    {id:'inlet',path:'assets/mechanism.svg',producer:'svg-brief-design',purpose:'Recognizable valve, connected pipe and reservoir cutaway with truthful capacity ruler.',view:'mechanism',placement:[0,0],moments:allMoments,ports:{supply:[100,330],outlet:[655,330]},bindings},
    {id:'flow',path:'assets/transport.svg',producer:'procedural-svg-animation',purpose:'Show rate-dependent motion driven by integrated volume, with no phase reset at a rate change.',view:'mechanism',placement:[0,0],moments:allMoments,bindings:tracerBindings},
    {id:'rate-scale',path:'assets/rate-scale.svg',producer:'d3',purpose:'Fixed linear input-rate scales for the synchronized history curve.',view:'rate',placement:[0,0],moments:allMoments},
    {id:'volume-scale',path:'assets/volume-scale.svg',producer:'d3',purpose:'Fixed linear volume scales expose the integral and its changing slope.',view:'volume',placement:[0,0],moments:allMoments}
  ]};
  save(path.join(dir,'scene.json'),brief);save(path.join(dir,'asset-plan.json'),plan);
  console.log(JSON.stringify({mode,scene:path.join(dir,'scene.json'),assets:plan.assets.length}));
}
