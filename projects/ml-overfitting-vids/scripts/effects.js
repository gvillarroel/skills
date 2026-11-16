/* Reviewed semantic motion bindings. Preserve values and the approved voice. */
(() => {
const authoredReady = window.ready;
window.ready = authoredReady.then(async () => {
  const scenes = PRODUCTION.scenes, motion = [];
  const add = (index, name, selector, start, end, mode='trace', kind='chart') => {
    const scope = `[data-scene="${index}"]`, source = document.querySelector(scope).querySelector(selector);
    if (!source) throw Error('Missing reviewed motion geometry: ' + name);
    source.id = 'ml-motion-' + name;
    motion.push({id:name, sceneId:scenes[index].id, source:'#'+source.id, scope, start, end, mode, kind});
  };
  const cues = i => NARRATION_CUES.scenes.find(s => s.id === scenes[i].id).cues;
  const at = (i, id) => cues(i).find(c => c.target === id).at;
  add(0,'controlled-fit','g[clip-path] + g[clip-path] path',at(0,'controlled-fit'),scenes[0].clipSeconds-.4);
  add(3,'training-flow','line[x1="425"][y1="360"]',at(3,'impute'),at(3,'apply-only'), 'trace','diagram');
  add(3,'application-flow','line[x1="425"][y1="770"]',at(3,'apply-only'),scenes[3].clipSeconds-.4,'trace','diagram');
  add(4,'capacity','path',at(4,'cv-small'),scenes[4].clipSeconds-.4);
  add(5,'reserved-fold','rect',at(5,'folds'),at(5,'cv-mean'),'pulse','diagram');
  add(6,'regularization','path',1,scenes[6].clipSeconds-.4);
  add(7,'training-curve','path',at(7,'training-curve'),at(7,'validation-curve'));
  add(7,'validation-curve','path:nth-of-type(2)',at(7,'validation-curve'),scenes[7].clipSeconds-.4);
  add(8,'group-validation','path:nth-of-type(2)',1,scenes[8].clipSeconds-.4);
  add(9,'frozen-transfer','line[x1="780"]',at(9,'frozen'),at(9,'test-score'),'trace','diagram');
  add(10,'production-feedback','line[x1="1330"][y1="380"]',at(10,'predictions'),scenes[10].clipSeconds-.4,'trace','diagram');
  const authored = window.renderClip, bridge = LineWorldSceneEffects.attach(document.querySelector('#stage'), {scenes, motion});
  window.FOCUS_PLAN = {windows:bridge.windows};
  await bridge.ready;
  window.renderClip = (i,t) => bridge.frame(i,t,authored(i,t));
  window.renderAt = (first,second) => {const p=second===undefined?bridge.locate(first):{index:first,seconds:second};return renderClip(p.index,p.seconds)};
  window.snapshot = bridge.snapshot;
  return renderClip(0,0);
});
})();
