/* Runs inside the shared pixel explorer closure. All explanations stay outside the canvas. */
if (decision) {
  const openingPolicy=structuredClone(data.pixels.config);
  let draft=structuredClone(openingPolicy), timer=null;
  const css=document.createElement('style');
  css.textContent='.composer{width:min(660px,calc(100% - 32px));margin:0 auto;padding:10px 0;color:#bac4d0;font-size:11px}.playback{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.playback button{font-size:11px;min-height:32px;padding:5px 10px}.playback label{margin-left:auto}.composer input[type=range]{width:100%;accent-color:#acd9d3;min-height:26px}.composer p{margin:5px 0;overflow-wrap:anywhere}.decision-title{color:#e6e8e9}.rule-order{display:grid;gap:4px;padding:0;list-style:none}.rule-order li{display:flex;align-items:center;gap:5px}.rule-order span{flex:1}.rule-order button{min-height:25px;padding:0 8px}.drawer .weight-row{display:grid;grid-template-columns:1fr 30px;align-items:center;column-gap:12px}.weight-row output{text-align:right}.weight-row input{grid-column:1/3}.trace-table{width:100%;font-size:11px;text-align:left;font-variant-numeric:tabular-nums;border-collapse:collapse}.trace-table th,.trace-table td{padding:3px 5px}.trace-table th:first-child{width:40%}.rule-note{border-left:2px solid #acd9d3;padding-left:9px}';
  document.head.append(css);
  const panel=document.createElement('section'); panel.className='composer chrome'; panel.setAttribute('aria-label','Composition playback');
  panel.innerHTML='<div class="playback"><button id="decision-play">Replay</button><button id="decision-back" aria-label="Previous placement">←</button><button id="decision-next" aria-label="Next placement">→</button><button id="decision-finish">Show all</button><button id="decision-rules">Composition rules</button><label>Speed <select id="decision-speed" aria-label="Placements per second"><option value="10">10/s</option><option value="60" selected>60/s</option><option value="240">240/s</option></select></label></div><input id="decision-step" type="range" min="1" step="1" aria-label="Number of placed records"><p id="decision-status" class="decision-title"></p><p id="decision-reason"></p><p id="composition-summary"></p>';
  $('stage').after(panel);
  const rules=document.createElement('section'); rules.id='composition-controls';
  rules.innerHTML='<h2>Composition rules</h2><p>Choose who enters next, then how each vacant cell is scored. Apply rules to build a new layout. Color lenses keep the current layout.</p><label>Placement priority<select id="priority-key"></select></label><label id="priority-direction-row">Numeric order<select id="priority-direction"><option value="descending">Highest first</option><option value="ascending">Lowest first</option></select></label><p id="priority-order-label">Earlier categories enter first. Move them to define the priority.</p><ol id="priority-order" class="rule-order"></ol><label>Eligibility<select id="eligibility"><option value="generation">Complete each generation first</option><option value="parent">Parent placed first; then any ready record</option></select></label><label>Bring similar records together<select id="affinity-key"></select></label><div id="placement-weights"></div><label>Growth allowance · cells<input id="frontier-window" type="range" min="1" max="8" step="1"><output id="frontier-value"></output></label><p>Only connected, empty cells within this distance of the nearest frontier are considered. Enclosed holes are rejected.</p><div class="controls"><button id="compose-apply">Apply rules</button><button id="compose-restore">Restore rules</button></div><p id="compose-message" role="status"></p><h2>Current placement</h2><div id="decision-explanation" class="rule-note"></div><button id="decision-export">Download decision log</button>';
  $('drawer').append(rules);
  const weightLabels={parent:'Closeness to parent',affinity:'Attribute affinity',compactness:'Contact with occupied cells',radial:'Closeness to center'};
  for (const d of data.dimensions) {
    const option=document.createElement('option'); option.value=d.key; option.textContent=d.label; $('priority-key').append(option);
    if (d.type==='categorical') $('affinity-key').append(option.cloneNode(true));
  }
  const none=document.createElement('option'); none.value=''; none.textContent='No attribute affinity'; $('affinity-key').prepend(none);
  for (const [name,label] of Object.entries(weightLabels)) {
    const row=document.createElement('label'); row.className='weight-row';
    row.innerHTML=`<span>${label}</span><output id="weight-value-${name}"></output><input id="weight-${name}" type="range" min="0" max="10" step="0.5" aria-label="${label}">`;
    $('placement-weights').append(row);
    $('weight-'+name).addEventListener('input',e=>{$('weight-value-'+name).textContent=e.target.value;});
  }
  function categoryOrder() {
    const dim=data.dimensions.find(d=>d.key===draft.priority.key), numeric=dim.type==='numeric';
    $('priority-direction-row').hidden=!numeric; $('priority-order').hidden=numeric; $('priority-order-label').hidden=numeric;
    $('priority-order').replaceChildren();
    if (!numeric) draft.priority.order.forEach((value,i)=>{
      const row=document.createElement('li'), label=document.createElement('span'); label.textContent=value; row.append(label);
      for (const [delta,glyph] of [[-1,'↑'],[1,'↓']]) {
        const b=button(glyph,()=>{const j=i+delta;[draft.priority.order[i],draft.priority.order[j]]=[draft.priority.order[j],draft.priority.order[i]];categoryOrder();});
        b.disabled=i+delta<0||i+delta>=draft.priority.order.length; b.setAttribute('aria-label',`Move ${value} ${delta<0?'earlier':'later'}`); row.append(b);
      }
      $('priority-order').append(row);
    });
  }
  function fillRules(policy) {
    draft=structuredClone(policy); $('priority-key').value=draft.priority.key; $('priority-direction').value=draft.priority.direction||'descending';
    $('affinity-key').value=draft.affinity||''; $('eligibility').value=draft.eligibility;
    for (const [name,value] of Object.entries(draft.weights)) { $('weight-'+name).value=value; $('weight-value-'+name).textContent=value; }
    $('frontier-window').value=draft.frontierWindow; $('frontier-value').textContent=draft.frontierWindow; categoryOrder();
  }
  function pause() { if(timer!==null) clearInterval(timer); timer=null; $('decision-play').textContent=state.step>=data.nodes.length?'Replay':'Play'; }
  function explain() {
    const config=data.pixels.config, record=data.pixels.decisions[state.step-1], n=data.nodes[record.node];
    const label=data.dimensions.find(d=>d.key===config.priority.key).label;
    $('decision-step').value=state.step;
    $('decision-status').textContent=`${fmt(state.step)} / ${fmt(data.nodes.length)} placed · ${n.label}`;
    $('decision-reason').textContent=state.step===1?'The root anchors the center.':`${record.eligible} eligible · ${label}: ${record.priorityValue===null?'No observation (last)':record.priorityValue} · best allowed vacancy score ${record.score.toFixed(3)} of ${record.candidates} candidates`;
    const affinity=config.affinity===null?'none':data.dimensions.find(d=>d.key===config.affinity).label;
    $('composition-summary').textContent=`Order: ${label} · Affinity: ${affinity} · ${config.eligibility==='generation'?'Generation order':'Parent before child'} · Colors preserve this composition`;
    const box=$('decision-explanation'); box.replaceChildren();
    for (const value of [n.label,`Position (${record.x}, ${record.y}). Parent: ${n.parentId===null?'Root':byId.get(n.parentId).label}.`,state.step===1?'Root placement is mandatory.':`Highest priority among ${record.eligible} eligible records; equal priorities use record ID. Missing priority values enter last.`,`${record.rejectedHoles} hole-forming candidates skipped before retaining the best three allowed candidates.`]) { const p=document.createElement('p');p.textContent=value;box.append(p); }
    const table=document.createElement('table'); table.className='trace-table';
    const head=table.createTHead().insertRow(); for(const title of ['Term','Value','Weight','Contribution']){const th=document.createElement('th');th.textContent=title;head.append(th);}
    for (const [name,value] of Object.entries(record.terms)) {const row=table.insertRow();for(const text of [weightLabels[name],value.toFixed(3),config.weights[name],(value*config.weights[name]).toFixed(3)])row.insertCell().textContent=text;}
    box.append(table);
    for(const alt of record.alternatives){const p=document.createElement('p');p.textContent=`Alternative (${alt.x}, ${alt.y}): ${alt.score.toFixed(3)}`;box.append(p);}
    $('decision-back').disabled=state.step<=1; $('decision-next').disabled=state.step>=data.nodes.length;
  }
  function setStep(value) {state.step=Math.max(1,Math.min(data.nodes.length,Math.floor(value)));paint();explain();}
  function play() {
    if(timer!==null){pause();return;}
    if(state.step>=data.nodes.length)setStep(1);
    $('decision-play').textContent='Pause';let previous=performance.now(),remainder=0;
    timer=setInterval(()=>{const now=performance.now();remainder+=(now-previous)*Number($('decision-speed').value)/1000;previous=now;const count=Math.floor(remainder);remainder-=count;if(count)setStep(state.step+count);if(state.step===data.nodes.length)pause();},30);
  }
  function recompose(policy) {
    pause();
    const layout=HierarchyDecisionEngine.compose(data,policy,data.pixels.cellPixels,data.pixels.seed);
    data.pixels=layout;N=layout.size;art.width=art.height=N;owners=new Int32Array(N*N).fill(-1);pixels=ctx.createImageData(N,N);
    for(const [y,row]of layout.rows.entries())for(const[x,width,index]of row)owners.fill(index,y*N+x,y*N+x+width);
    state.step=data.nodes.length;state.selected=data.rootId;state.x=state.y=0;state.zoom=1;state.category=undefined;
    $('grid-note').textContent=`${N} × ${N} native grid; ${data.nodes.length} records, ${layout.cellPixels**2} pixels per record. This policy was recomposed; color lenses keep it fixed.`;
    fit();paint();explain();pause();
  }
  $('priority-key').addEventListener('change',e=>{const d=data.dimensions.find(d=>d.key===e.target.value);draft.priority=d.type==='numeric'?{key:d.key,direction:'descending'}:{key:d.key,order:d.categories.slice()};categoryOrder();});
  $('frontier-window').addEventListener('input',e=>$('frontier-value').textContent=e.target.value);
  $('compose-apply').addEventListener('click',()=>{
    const policy=structuredClone(draft); if(!policy.priority.order)policy.priority.direction=$('priority-direction').value;
    policy.affinity=$('affinity-key').value||null;policy.eligibility=$('eligibility').value;policy.frontierWindow=Number($('frontier-window').value);
    for(const name of Object.keys(weightLabels))policy.weights[name]=Number($('weight-'+name).value);
    $('compose-message').textContent='Composing…';
    setTimeout(()=>{try{recompose(policy);draft=structuredClone(policy);$('compose-message').textContent='Composition rebuilt. Replay to inspect its decisions.';}catch(error){$('compose-message').textContent=error.message;}},10);
  });
  $('compose-restore').addEventListener('click',()=>{fillRules(openingPolicy);recompose(openingPolicy);$('compose-message').textContent='Opening policy restored.';});
  $('decision-play').addEventListener('click',play);
  $('decision-back').addEventListener('click',()=>{pause();setStep(state.step-1);});
  $('decision-next').addEventListener('click',()=>{pause();setStep(state.step+1);});
  $('decision-finish').addEventListener('click',()=>{pause();setStep(data.nodes.length);pause();});
  $('decision-step').max=data.nodes.length;$('decision-step').addEventListener('input',e=>{pause();setStep(Number(e.target.value));});
  $('decision-rules').addEventListener('click',()=>{pause();drawer(true);rules.scrollIntoView({block:'start'});});
  $('decision-export').addEventListener('click',()=>download(new Blob([JSON.stringify({title:data.title,patternId:data.patternId,config:data.pixels.config,seed:data.pixels.seed,cellPixels:data.pixels.cellPixels,records:data.nodes.map(n=>({id:n.id,parentId:n.parentId,values:n.values})),decisions:data.pixels.decisions},null,2)],{type:'application/json'}),'hierarchy-decisions.json'));
  $('brand').textContent='Hierarchy Lens / Decision growth';document.title=data.title+' · Decision growth';
  $('geometry-key').textContent='The root starts in the center. A priority rule chooses the next eligible record. A weighted vacancy score chooses its position. Replay or advance one placement to inspect each decision.';
  $('area-key').textContent=`One ${data.pixels.cellPixels} × ${data.pixels.cellPixels} square is one record. Every placement stays connected and avoids holes. Position reflects composition rules; cell contact is not a reporting edge. Exact parents remain in record details.`;
  $('export-note').textContent='PNG/SVG capture the current replay step and colors. SVG includes the active policy and complete decision log. HTML keeps the interactive engine.';
  art.setAttribute('aria-label','Text-free hierarchy composed by explicit placement priorities and weighted spatial rules. Use playback and the outside decision explanation.');
  fillRules(openingPolicy);explain();
  window.hierarchyDecisions=Object.freeze({snapshot:()=>({step:state.step,config:structuredClone(data.pixels.config),cells:structuredClone(data.pixels.cells),decisions:structuredClone(data.pixels.decisions)}),setStep,recompose});
}
