async (page) => {
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const reports=[],scenes=await page.evaluate(()=>window.DECK.scenes);
 for(const width of [1600,900,360]){
  await page.setViewportSize({width,height:900});
  for(const scene of scenes){
   await page.evaluate(id=>window.DECK.go(id),scene.id);
   const r=await page.evaluate(()=>{
    const out=[...document.querySelectorAll('#chart svg text')].filter(t=>{const r=t.getBoundingClientRect(),s=t.closest('svg').getBoundingClientRect();return t.textContent.trim()&&(r.left<s.left-2||r.right>s.right+2||r.top<s.top-2||r.bottom>s.bottom+2);}).map(t=>t.textContent);
    return {scene:window.DECK.state.scene,overflow:document.documentElement.scrollWidth>innerWidth,vertical:document.documentElement.scrollHeight>innerHeight+2,labels:out,result:window.DECK.state.result};
   });
   reports.push({width,...r});
   if(scene.min!==undefined){
    for(const n of [scene.min,scene.max,scene.initial])await page.locator('#parameter').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input',{bubbles:true}));},n);
    const v=await page.evaluate(()=>window.DECK.state.value);if(Math.abs(v-scene.initial)>1e-8)throw Error('Slider failed: '+scene.id);
   }
   if(width===1600||['parameters','system','models','fidelity'].includes(scene.id))await page.screenshot({path:`projects/code-assist-costs/artifacts/decision-budget-v2/qa/${scene.id}-${width}.png`,fullPage:true});
  }
 }
 await page.setViewportSize({width:1600,height:900});
 for(const [id,main,delta] of [['system','5,397',-52],['tools','5,597',148],['output','6,571',1122],['cache','5,215',-234],['cap','252',103]]){
  await page.locator('#scene-picker').selectOption(id);const s=await page.evaluate(()=>window.DECK.state);
  if(s.account.main!==main||s.account.ledger.delta!==delta)throw Error('Account oracle: '+JSON.stringify(s));
 }
 await page.locator('#scene-picker').selectOption('fidelity');
 for(const [value,preferred] of [[.95,'No summaries'],[.99,'Summaries']]){
  await page.locator('#parameter').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));},value);
  const s=await page.evaluate(()=>window.DECK.state.account);if(s.impact[2][1]!==preferred)throw Error('Quality reversal');
 }
 await page.locator('#scene-picker').selectOption('models');
 await page.locator('#parameter').evaluate(el=>{el.value=.95;el.dispatchEvent(new Event('input',{bubbles:true}));});
 if((await page.locator('#result strong').innerText())!=='No match')throw Error('Missing-model state');
 await page.getByRole('button',{name:'How is this calculated?'}).click();
 if(!(await page.locator('#detail').isVisible()))throw Error('Missing calculation dialog');
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Download data & budget method'}).click();const dataDownload=await downloadPromise;
 await dataDownload.saveAs('projects/code-assist-costs/artifacts/decision-budget-v2/qa/downloaded-data.json');
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await page.locator('#scene-picker').selectOption('system');
 await page.getByRole('button',{name:'Play change'}).click();await page.waitForTimeout(400);
 if(!(await page.evaluate(()=>window.DECK.state.playing&&window.DECK.state.value>0)))throw Error('Replay did not advance');
 await page.getByRole('button',{name:'Pause',exact:true}).click();
 await page.emulateMedia({reducedMotion:'reduce'});await page.getByRole('button',{name:'Play change'}).click();
 if(!(await page.evaluate(()=>!window.DECK.state.playing&&window.DECK.state.value===10000)))throw Error('Reduced-motion state');
 await page.emulateMedia({reducedMotion:'no-preference'});
 const exported=page.waitForEvent('download');await page.getByRole('button',{name:'Export chart',exact:true}).click();const chartDownload=await exported;
 await chartDownload.saveAs('projects/code-assist-costs/artifacts/decision-budget-v2/qa/exported-system.svg');
 await page.locator('#scene-picker').selectOption('parameters');
 const failures=reports.filter(r=>r.overflow||r.labels.length||(r.width===1600&&r.vertical));
 const result={ok:failures.length===0&&errors.length===0,scenes:scenes.length,widths:[1600,900,360],reports,failures,errors,checks:['all slider extrema','whole-run oracles','quality reversal','missing-model state','replay','reduced motion','source download','SVG export','layout bounds']};
 return result;
}
