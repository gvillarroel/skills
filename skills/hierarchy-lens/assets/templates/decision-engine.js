/* Shared deterministic engine: embedded offline in HTML and called by the Python builder through Node. */
const HierarchyDecisionEngine = (() => {
  'use strict';
  const directions = [[1,0],[0,1],[-1,0],[0,-1]];
  const key = (x,y) => `${x},${y}`;
  const around = (x,y) => directions.map(([dx,dy]) => [x+dx,y+dy]);
  const lexical = (a,b) => a < b ? -1 : a > b ? 1 : 0;

  function validate(data, raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw Error('Decision view requires an explicit composition object.');
    const config = JSON.parse(JSON.stringify(raw));
    const dimension = data.dimensions.find(d => d.key === config.priority?.key);
    if (!dimension) throw Error('composition.priority.key must name a dimension.');
    if (dimension.type === 'categorical') {
      const order = config.priority.order;
      if (!Array.isArray(order) || new Set(order).size !== order.length || order.length !== dimension.categories.length || dimension.categories.some(c => !order.includes(c))) throw Error('Categorical priority requires an explicit order containing every declared category exactly once.');
    } else if (!['ascending','descending'].includes(config.priority.direction)) throw Error('Numeric priority requires ascending or descending direction.');
    if (config.affinity !== null && !data.dimensions.some(d => d.key === config.affinity && d.type === 'categorical')) throw Error('composition.affinity must be a categorical key or null.');
    if (!['generation','parent'].includes(config.eligibility)) throw Error('composition.eligibility must be generation or parent.');
    if (!config.weights || ['parent','affinity','compactness','radial'].some(k => typeof config.weights[k] !== 'number' || !Number.isFinite(config.weights[k]) || config.weights[k] < 0 || config.weights[k] > 10)) throw Error('All four composition weights must be finite numbers from 0 to 10.');
    if (!Number.isInteger(config.frontierWindow) || config.frontierWindow < 1 || config.frontierWindow > 8) throw Error('composition.frontierWindow must be an integer from 1 to 8.');
    if (data.nodes.length > 5000) throw Error('The interactive decision engine supports at most 5000 records.');
    return config;
  }

  function compareRecords(data, config, a, b) {
    const dim = data.dimensions.find(d => d.key === config.priority.key);
    const av = a.values[dim.key], bv = b.values[dim.key];
    if (config.eligibility === 'generation' && a.depth !== b.depth) return a.depth-b.depth;
    if (av === null && bv !== null) return 1;
    if (bv === null && av !== null) return -1;
    if (av !== null && bv !== null) {
      const delta = dim.type === 'categorical' ? config.priority.order.indexOf(av)-config.priority.order.indexOf(bv) : (av-bv)*(config.priority.direction === 'descending' ? -1 : 1);
      if (delta) return delta;
    }
    return lexical(a.id,b.id);
  }

  function noNewHole(x,y,occupied,bounds) {
    const targets = around(x,y).filter(([a,b]) => !occupied.has(key(a,b)));
    if (targets.length < 2) return true;
    const reachable = (local) => {
      const pending = new Set(targets.map(([a,b]) => key(a,b)));
      const queue = [targets[0]], seen = new Set([key(...targets[0])]);
      pending.delete(key(...targets[0]));
      for (let i=0;i<queue.length && pending.size;i++) {
        for (const [a,b] of around(...queue[i])) {
          if (a===x && b===y || occupied.has(key(a,b)) || seen.has(key(a,b))) continue;
          if (local ? Math.abs(a-x)>1 || Math.abs(b-y)>1 : a<bounds[0]-2 || a>bounds[2]+2 || b<bounds[1]-2 || b>bounds[3]+2) continue;
          seen.add(key(a,b)); pending.delete(key(a,b)); queue.push([a,b]);
        }
      }
      return pending.size === 0;
    };
    return reachable(true) || reachable(false);
  }

  function tie(seed,x,y) {
    let value = (seed ^ Math.imul(x,374761393) ^ Math.imul(y,668265263)) >>> 0;
    value = Math.imul(value ^ value>>>13,1274126177);
    return (value ^ value>>>16) >>> 0;
  }

  function compose(data, policy, cellPixels=2, seed=73021) {
    const config = validate(data,policy);
    if (!Number.isInteger(cellPixels) || cellPixels < 1 || cellPixels > 4) throw Error('cell-pixels must be an integer from 1 to 4.');
    if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw Error('seed must be an unsigned 32-bit integer.');
    const nodes=data.nodes, byId=new Map(nodes.map((n,i)=>[n.id,{node:n,index:i}]));
    const occupied=new Map(), frontier=new Map(), positions=new Map(), groups=new Map();
    const cells=Array(nodes.length), decisions=[], bounds=[0,0,0,0];
    let ready=[byId.get(data.rootId)];
    function place(record,x,y,decision) {
      const {node,index}=record, birth=decisions.length;
      occupied.set(key(x,y),index); frontier.delete(key(x,y)); positions.set(node.id,[x,y]);
      for (const [a,b] of around(x,y)) if (!occupied.has(key(a,b))) frontier.set(key(a,b),[a,b]);
      bounds[0]=Math.min(bounds[0],x); bounds[1]=Math.min(bounds[1],y); bounds[2]=Math.max(bounds[2],x); bounds[3]=Math.max(bounds[3],y);
      if (config.affinity !== null && node.values[config.affinity] !== null) {
        const value=node.values[config.affinity], group=groups.get(value)||{x:0,y:0,count:0};
        group.x+=x; group.y+=y; group.count++; groups.set(value,group);
      }
      cells[index]={node:index,tileX:x,tileY:y,birth,arrival:birth};
      decisions.push({step:birth+1,node:index,x,y,...decision});
      ready=ready.filter(r=>r.index!==index);
      for (const id of node.children) ready.push(byId.get(id));
    }
    place(ready[0],0,0,{eligible:1,priorityValue:nodes[0].values[config.priority.key],candidates:1,rejectedHoles:0,score:0,terms:{parent:0,affinity:0,compactness:0,radial:0},alternatives:[]});
    while (decisions.length < nodes.length) {
      ready.sort((a,b)=>compareRecords(data,config,a.node,b.node));
      const record=ready[0], node=record.node, parent=positions.get(node.parentId);
      const eligible=config.eligibility==='generation' ? ready.filter(r=>r.node.depth===node.depth).length : ready.length;
      const group=config.affinity===null ? null : groups.get(node.values[config.affinity]);
      const vacancies=[...frontier.values()], minimum=Math.min(...vacancies.map(([x,y])=>Math.hypot(x,y)));
      const candidates=vacancies.filter(([x,y])=>Math.hypot(x,y)<=minimum+config.frontierWindow).map(([x,y])=>{
        const neighbors=around(x,y).map(([a,b])=>occupied.get(key(a,b))).filter(i=>i!==undefined);
        const matching=group ? neighbors.filter(i=>nodes[i].values[config.affinity]===node.values[config.affinity]).length : 0;
        const terms={parent:1/(1+Math.abs(x-parent[0])+Math.abs(y-parent[1])),affinity:group ? .65/(1+Math.abs(x-group.x/group.count)+Math.abs(y-group.y/group.count))+.35*matching/4 : 0,compactness:neighbors.length/4,radial:1/(1+Math.hypot(x,y))};
        const score=Object.entries(terms).reduce((total,[name,value])=>total+value*config.weights[name],0);
        return {x,y,score,terms,tie:tie(seed,x,y)};
      }).sort((a,b)=>b.score-a.score || a.tie-b.tie || a.y-b.y || a.x-b.x);
      const accepted=[]; let rejectedHoles=0;
      for (const candidate of candidates) {
        if (noNewHole(candidate.x,candidate.y,occupied,bounds)) accepted.push(candidate);
        else rejectedHoles++;
        if (accepted.length===3) break;
      }
      if (!accepted.length) throw Error('No connected, hole-free vacancy fits the growth window.');
      const chosen=accepted[0];
      place(record,chosen.x,chosen.y,{eligible,priorityValue:node.values[config.priority.key],candidates:candidates.length,rejectedHoles,score:chosen.score,terms:chosen.terms,alternatives:accepted.slice(1).map(({x,y,score,terms})=>({x,y,score,terms}))});
    }
    const radius=Math.max(...bounds.map(Math.abs));
    const size=2**Math.ceil(Math.log2(Math.max(32,2*(radius+3)*cellPixels))), origin=size/2-Math.floor(cellPixels/2);
    const rows=Array.from({length:size},()=>[]);
    for (const cell of cells) {
      cell.x=origin+cell.tileX*cellPixels; cell.y=origin+cell.tileY*cellPixels;
      for (let dy=0;dy<cellPixels;dy++) rows[cell.y+dy].push([cell.x,cellPixels,cell.node]);
    }
    rows.forEach(row=>row.sort((a,b)=>a[0]-b[0]));
    return {mode:'organic',engine:'priority-frontier-v1',size,rows,coverage:cells.map(()=>cellPixels**2),cellPixels,seed,cells,connected:true,holes:0,rootCenter:[origin+cellPixels/2,origin+cellPixels/2],displayScale:3,bounds:[origin+bounds[0]*cellPixels,origin+bounds[1]*cellPixels,origin+(bounds[2]+1)*cellPixels,origin+(bounds[3]+1)*cellPixels],config,decisions};
  }
  return Object.freeze({compose,validate,compareRecords});
})();
if (typeof module !== 'undefined') module.exports=HierarchyDecisionEngine;
