async (page) => {
  await page.setViewportSize({width:1440,height:1000});
  const reports=[];
  for(const width of [1440,900,360]){
    await page.setViewportSize({width,height:1000});
    for(const id of ['fidelity','models','variability']){
      await page.evaluate(id=>window.DECK.go(id),id);
      const clashes=await page.evaluate(()=>{
        const result=[];
        for(const axis of document.querySelectorAll('.x-axis,.y-axis')){
          const labels=[...axis.querySelectorAll('.tick text')].map(t=>({label:t.textContent,r:t.getBoundingClientRect()}));
          for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
            const a=labels[i],b=labels[j];if(a.r.left<b.r.right+3&&a.r.right+3>b.r.left&&a.r.top<b.r.bottom+3&&a.r.bottom+3>b.r.top)result.push([a.label,b.label]);
          }
        }
        return result;
      });
      if(clashes.length)throw Error(JSON.stringify({id,width,clashes}));
      reports.push({id,width,tickCollisions:0});
    }
  }
  await page.setViewportSize({width:1440,height:1000});
  await page.evaluate(()=>window.DECK.go('system'));
  const box=await page.locator('[data-chart-hit]').boundingBox();
  await page.mouse.move(box.x+box.width*.61,box.y+box.height*.7);
  if(!(await page.locator('.tooltip').isVisible()))throw Error('Cross-series tooltip did not appear');
  const before=await page.evaluate(()=>window.DECK.state.value);
  await page.mouse.click(box.x+box.width*.61,box.y+box.height*.7);
  const after=await page.evaluate(()=>window.DECK.state.value);
  if(before===after)throw Error('Click to inspect did not update the parameter');
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Export chart'}).click()]);
  await download.saveAs('projects/code-assist-costs/artifacts/decision-curves-v1/qa/exported-system.svg');
  await page.evaluate(()=>window.DECK.go('parameters'));
  const html=await page.content();
  const offlineContext=await page.context().browser().newContext({offline:true,viewport:{width:1280,height:900}});
  const offlinePage=await offlineContext.newPage();
  await offlinePage.setContent(html,{waitUntil:'load'});
  const offline=await offlinePage.evaluate(()=>{window.DECK.go('cap');window.DECK.set(156000);return window.DECK.state;});
  if(!offline.result.includes('$763,372'))throw Error('Offline cost oracle');
  await offlineContext.close();
  const result={ok:true,tickChecks:reports,tooltip:true,clickToInspect:true,svgDownload:true,offline:{ok:true,state:offline}};
  await page.evaluate(r=>window.DECK_FINAL_QA=r,result);
  return result;
}
