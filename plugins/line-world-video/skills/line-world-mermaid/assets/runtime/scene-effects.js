/* Scene-local effects bridge. Render the authored figure first, then call frame(). */
(() => {
'use strict';
function attach(root, plan) {
  if (!root || !Array.isArray(plan.scenes) || !plan.scenes.length) throw Error('Declare the ordered scene clock.');
  let cursor = 0;
  const ids = new Set();
  const scenes = plan.scenes.map(scene => {
    const duration = Number(scene.clipSeconds ?? scene.duration);
    if (!scene.id || ids.has(scene.id) || !Number.isFinite(duration) || duration <= 0) throw Error('Scene IDs and positive durations are required.');
    ids.add(scene.id);
    const item = {id:scene.id, start:cursor, duration}; cursor += duration; return item;
  });
  const interval = item => {
    const scene = scenes.find(s => s.id === item.sceneId);
    if (!scene || !Number.isFinite(item.start) || !Number.isFinite(item.end) || item.start < 0 || item.end <= item.start || item.end > scene.duration + 1e-6) throw Error('Effect bounds must fit their declared scene.');
    return {start:scene.start + item.start, end:scene.start + item.end};
  };
  const windows = (plan.motion || []).map(item => ({...item, ...interval(item)}));
  const photos = (plan.photos || []).map(item => ({...item, windows:item.windows.map(w => interval({...w, sceneId:item.sceneId}))}));
  if (windows.length && !window.LineWorldFocusMotion) throw Error('Load focus-motion.js before the bridge.');
  if (photos.length && !window.LineWorldPhotoFocus) throw Error('Load photo-focus.js before the bridge.');
  const motion = windows.length ? LineWorldFocusMotion.attach(root, windows) : null;
  const photograph = photos.length ? LineWorldPhotoFocus.attach(root, photos) : null;
  let last = null;
  return {
    scenes, windows, photos,
    ready: photograph?.ready || Promise.resolve(),
    frame(index, seconds, authoredState) {
      if (!Number.isInteger(index) || !scenes[index] || !Number.isFinite(seconds)) throw Error('Use a valid scene index and local time.');
      const scene = scenes[index], time = scene.start + Math.max(0, Math.min(scene.duration, seconds));
      const moving = (motion?.render(time) || []).filter(s => s.active && s.eligible);
      const colored = (photograph?.render(time) || []).filter(s => s.color > 0);
      // This identity is consumed by PNG hold caches. Inactive effects must not
      // invalidate a static hold; active phases and photo fades must invalidate it.
      last = {...authoredState, effects:{motion:moving, photos:colored}};
      return structuredClone(last);
    },
    locate(seconds) {
      if (!Number.isFinite(seconds)) throw Error('Use a finite parent time.');
      const time = Math.max(0, Math.min(cursor, seconds));
      const index = scenes.findIndex((s, i) => time < s.start + s.duration || i === scenes.length - 1);
      return {index, seconds:time - scenes[index].start};
    },
    snapshot: () => structuredClone(last),
    destroy() { motion?.destroy(); photograph?.destroy(); }
  };
}
window.LineWorldSceneEffects = {attach};
})();
