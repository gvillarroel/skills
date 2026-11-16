/* Scene effects use measured cues and reviewed original photograph pairs. */
(() => {
const authoredReady = window.ready;
window.ready = authoredReady.then(async () => {
  const scenes=PRODUCTION.scenes, motion=[], photos=[];
  const at=(i,target)=>NARRATION_CUES.scenes.find(s=>s.id===scenes[i].id).cues.find(c=>c.target===target).at;
  const add=(i,name,selector,start,end,mode='trace',kind='diagram')=>{
    const scope='#scene-'+scenes[i].id, source=document.querySelector(scope).querySelector(selector);
    if(!source)throw Error('Missing reviewed motion geometry: '+name);
    source.id='cuda-motion-'+name;motion.push({id:name,sceneId:scenes[i].id,source:'#'+source.id,scope,start,end,mode,kind});
  };
  add(0,'convergence','path[marker-end]',1,scenes[0].clipSeconds-.4);
  add(1,'engineered-features','path.flowchart-link',1,at(1,'learned'));
  add(1,'learned-features','g[transform="translate(120 660)"] path.flowchart-link',at(1,'learned'),scenes[1].clipSeconds-.4);
  add(3,'parallel-input','path[marker-end]',1,scenes[3].clipSeconds-.4);
  add(5,'learned-layers','path[d="M520 540H600"]',at(5,'conv-layers'),scenes[5].clipSeconds-.4);
  add(6,'model-partition','[data-focus-id="model-split"] line',at(6,'model-split'),scenes[6].clipSeconds-.4);
  add(7,'relu','[data-focus-id="relu"] path',at(7,'relu'),at(7,'augmentation'),'trace','chart');
  add(7,'dropout','[data-focus-id="dropout"] line',at(7,'dropout'),scenes[7].clipSeconds-.4);
  add(8,'winning-error','[data-focus-id="winner"] rect',at(8,'winner'),at(8,'runner-up'),'pulse','chart');
  add(8,'comparison-error','[data-focus-id="runner-up"] rect',at(8,'runner-up'),scenes[8].clipSeconds-.4,'pulse','chart');
  add(9,'historical-convergence','path[marker-end]',1,scenes[9].clipSeconds-.4);
  const photo=(i,id,start,end)=>{
    const target=`#scene-${scenes[i].id} [data-object-id="${id}"] image[data-documentary-id]`, image=document.querySelector(target);
    if(!image)throw Error('Missing reviewed photograph: '+id);
    const asset=DOCUMENTARY_ASSETS[image.dataset.documentaryId];
    photos.push({id:'photo-'+i+'-'+id,sceneId:scenes[i].id,target,neutral:asset.variants.gray.image,color:asset.original,transition:.35,windows:[{start,end}]});
  };
  photo(2,'cpu-photo',at(2,'cpu'),at(2,'gpu'));
  photo(2,'gpu-photo',at(2,'gpu'),scenes[2].clipSeconds-.4);
  for(let r=0;r<5;r++)for(let c=0;c<6;c++)photo(4,`imagenet-photo-${r}-${c}`,at(4,'labels'),at(4,'challenge'));
  photo(5,'pixels-photo',at(5,'pixels'),at(5,'categories'));
  for(const id of ['gtx-left','gtx-right'])photo(6,id,at(6,'gpu-pair'),at(6,'model-split'));
  for(let i=0;i<4;i++)photo(7,'augmentation-photo-'+i,at(7,'augmentation'),at(7,'dropout'));
  const authored=window.renderClip,bridge=LineWorldSceneEffects.attach(document.querySelector('#stage'),{scenes,motion,photos});
  window.FOCUS_PLAN={windows:bridge.windows};window.PHOTO_FOCUS_PLAN={bindings:bridge.photos};
  await bridge.ready;
  window.renderClip=(i,t)=>bridge.frame(i,t,authored(i,t));
  window.renderAt=t=>{const p=bridge.locate(t);return renderClip(p.index,p.seconds)};
  window.snapshot=bridge.snapshot;
  return renderClip(0,0);
});
})();
