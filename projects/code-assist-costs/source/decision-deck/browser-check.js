async (page) => {
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://127.0.0.1:8842/');
  await page.setViewportSize({width:1440,height:1000});
  const scenes=await page.evaluate(()=>window.DECK.scenes);
  const reports=[];
  for(const scene of scenes){
    await page.evaluate(id=>window.DECK.go(id),scene.id);
    const report=await page.evaluate(()=>{
      const bad=[...document.querySelectorAll('#chart svg text')].filter(t=>{
        if(!t.textContent.trim())return false;
        const r=t.getBoundingClientRect(),s=t.closest('svg').getBoundingClientRect();
        return r.left<s.left-2||r.right>s.right+2||r.top<s.top-2||r.bottom>s.bottom+2;
      }).map(t=>t.textContent);
      return {state:window.DECK.state,svgCount:document.querySelectorAll('#chart svg').length,overflow:document.documentElement.scrollWidth>innerWidth,labelsOutside:bad};
    });
    if(report.overflow||report.labelsOutside.length)throw Error(JSON.stringify(report));
    await page.screenshot({path:`projects/code-assist-costs/artifacts/decision-curves-v1/qa/${scene.id}-1440.png`,fullPage:true});
    if(scene.min!==undefined){
      for(const v of [scene.min,scene.max,scene.initial])await page.locator('#parameter').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input',{bubbles:true}));},v);
      const state=await page.evaluate(()=>window.DECK.state);
      if(Math.abs(state.value-scene.initial)>1e-8)throw Error('Slider state failed: '+scene.id);
    }
    reports.push(report);
  }
  await page.evaluate(()=>window.DECK.go('system'));
  await page.locator('#volume').selectOption('1000');
  const system=await page.locator('#result').innerText();
  if(!system.includes('$0.35'))throw Error('Monthly scale oracle: '+system);
  await page.locator('#volume').selectOption('1000000');
  await page.evaluate(()=>window.DECK.go('fidelity'));
  await page.locator('#parameter').evaluate(el=>{el.value=.95;el.dispatchEvent(new Event('input',{bubbles:true}));});
  if(!(await page.locator('#result strong').innerText()).includes('No cap'))throw Error('Fidelity lower-side decision');
  await page.locator('#parameter').evaluate(el=>{el.value=.99;el.dispatchEvent(new Event('input',{bubbles:true}));});
  if(!(await page.locator('#result strong').innerText()).includes('180k cap'))throw Error('Fidelity upper-side decision');
  await page.evaluate(()=>window.DECK.go('models'));
  await page.locator('#parameter').evaluate(el=>{el.value=.95;el.dispatchEvent(new Event('input',{bubbles:true}));});
  if(!(await page.locator('#result strong').innerText()).includes('No qualifying'))throw Error('Missing-model case');
  await page.getByRole('button',{name:'Assumptions & sources'}).click();
  if(!(await page.locator('#detail').isVisible()))throw Error('Notes dialog');
  await page.getByRole('button',{name:'Close',exact:true}).click();
  await page.evaluate(()=>window.DECK.go('system'));
  await page.getByRole('button',{name:'Play sweep'}).click();
  await page.waitForTimeout(500);
  const playing=await page.evaluate(()=>window.DECK.state);
  if(!playing.playing||playing.value<=0)throw Error('Replay animation did not advance');
  await page.getByRole('button',{name:'Pause',exact:true}).click();
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.getByRole('button',{name:'Play sweep'}).click();
  const reduced=await page.evaluate(()=>window.DECK.state);
  if(reduced.playing||reduced.value!==10000)throw Error('Reduced-motion final state');
  await page.emulateMedia({reducedMotion:'no-preference'});
  for(const width of [900,360]){
    await page.setViewportSize({width,height:1000});
    for(const scene of scenes){
      await page.evaluate(id=>window.DECK.go(id),scene.id);
      const issues=await page.evaluate(()=>{
        const overflow=document.documentElement.scrollWidth>innerWidth;
        const labels=[...document.querySelectorAll('#chart svg text')].filter(t=>{
          const r=t.getBoundingClientRect(),s=t.closest('svg').getBoundingClientRect();
          return t.textContent.trim()&&(r.left<s.left-2||r.right>s.right+2||r.top<s.top-2||r.bottom>s.bottom+2);
        }).map(t=>t.textContent);
        return {overflow,labels};
      });
      if(issues.overflow||issues.labels.length)throw Error(JSON.stringify({scene:scene.id,width,...issues}));
      await page.screenshot({path:`projects/code-assist-costs/artifacts/decision-curves-v1/qa/${scene.id}-${width}.png`,fullPage:true});
    }
  }
  await page.setViewportSize({width:1440,height:1000});
  await page.evaluate(()=>window.DECK.go('parameters'));
  if(errors.length)throw Error(errors.join('\n'));
  const result={ok:true,scenes:reports.length,widths:[1440,900,360],checks:['sliders','monthly scale','fidelity reversal','missing model','notes','replay','reduced motion','horizontal overflow','SVG label bounds'],reports,errors};
  await page.evaluate(r=>window.DECK_QA=r,result);
  return result;
}
