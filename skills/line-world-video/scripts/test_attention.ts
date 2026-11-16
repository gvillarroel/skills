#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types scripts/test_attention.ts
// Dependencies: Node.js >=24; built-in modules only.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import assert from 'node:assert/strict';
const ctx:any={};vm.runInNewContext(fs.readFileSync(path.join(import.meta.dirname,'../assets/runtime/attention.js'),'utf8'),ctx);const A=ctx.LineWorldAttention,M=A.settings();
assert.equal(A.PRIMARY_RED,'#9e1b32');
const radii=[A.radius(M,{travel:0}),A.radius(M,{travel:1}),A.radius(M,{phase:.9}),A.radius(M,{phase:.31,hold:2.05,panes:2,emitting:true})];
assert(Math.min(...radii)<=6&&Math.max(...radii)>28);
for(const v of [0,.25,6,8,12,16,1e9]){const unit=A.unitFor([v]),t=A.tokens(v,unit);assert(t.length<=16);assert(Math.abs(t.reduce((n,p)=>n+p.quantity,0)-v)<1e-6);assert(t.every(p=>p.weight>0&&p.weight<=1));}
const input={time:1,birth:.2,flight:.5,origin:{x:0,y:0},target:{x:100,y:60},radius:4.5,weight:.25};
const landed=A.sample(input);assert(landed.landed);assert.equal(landed.radius,2.25);assert.equal(landed.x,100);assert.equal(landed.y,60);assert.equal(JSON.stringify(landed),JSON.stringify(A.sample(input)));assert.equal(A.sample({...input,time:0}).opacity,0);
const label={x0:100,y0:100,x1:200,y1:125},port=A.clearPort(label,{x0:0,y0:0,x1:500,y1:400},[label],32);assert(port.y+32<label.y0||port.y-32>label.y1||port.x+32<label.x0||port.x-32>label.x1);
console.log('Attention runtime checks passed: primary red, size range, conserved quantities, weighted area, deterministic seek and label clearance.');
