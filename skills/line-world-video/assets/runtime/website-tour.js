/* Original website screenshots, measured semantic cues and one deterministic clock. */
(() => {
  'use strict';
  const S = WEBSITE_STORY, frame = {x: 96, y: 78, w: 1728, h: 924};
  const svg = document.querySelector('#stage'), ns = 'http://www.w3.org/2000/svg';
  const element = (tag, attrs, parent = svg) => {
    const e = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    parent.append(e); return e;
  };
  const defs = element('defs', {}), clip = element('clipPath', {id: 'screen'}, defs);
  element('rect', {x: frame.x, y: frame.y, width: frame.w, height: frame.h}, clip);
  const stage = element('g', {'clip-path': 'url(#screen)'}), layers = S.scenes.map((s, i) => {
    const c = element('clipPath', {id: 'source-' + i, clipPathUnits: 'userSpaceOnUse'}, defs);
    element('rect', {x: s.region[0], y: s.region[1], width: s.region[2] - s.region[0], height: s.region[3] - s.region[1]}, c);
    const g = element('g', {}, stage), image = element('g', {'clip-path': 'url(#source-' + i + ')'}, g);
    element('image', {href: s.capture, x: 0, y: 0, width: s.width, height: s.height, 'data-content-anchor': s.id}, image);
    return g;
  });
  const guide = element('circle', {id: 'guide', r: 11, fill: '#9e1b32', stroke: '#ffffff', 'stroke-width': 3, 'data-lw-guide': 'true'});
  const ease = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
  const mix = (a, b, u) => a + (b - a) * u;
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const obstacles = s => [...Object.values(s.targets).map(t => t.box), ...(s.avoid || [])].map(b => ({x0: b[0], y0: b[1], x1: b[0] + b[2], y1: b[1] + b[3]}));
  const routes = S.scenes.map(s => s.cues.map((cue, i) => {
    const a = s.targets[s.cues[Math.max(0, i - 1)].target].port, b = s.targets[cue.target].port;
    return LineWorldFocus.route({x: a[0], y: a[1]}, {x: b[0], y: b[1]}, obstacles(s), {x0: 0, y0: 0, x1: s.width, y1: s.height}, {radius: 10, gap: 2});
  }));
  const interpolate = (a, b, u) => ({x: mix(a.x, b.x, u), y: mix(a.y, b.y, u), k: mix(a.k, b.k, u)});
  function destination(scene, target, scale) {
    const b = target.box, region = scene.region, cx = b[0] + b[2] / 2, cy = b[1] + b[3] / 2;
    const halfW = frame.w / scale / 2, halfH = frame.h / scale / 2;
    const center = (value, a, z, half) => z - a <= 2 * half ? (a + z) / 2 : clamp(value, a + half, z - half);
    const x = center(cx, region[0], region[2], halfW), y = center(cy, region[1], region[3], halfH);
    return {x: frame.x + frame.w / 2 - x * scale, y: frame.y + frame.h / 2 - y * scale, k: scale};
  }
  const projected = (p, c) => ({x: p[0] * c.k + c.x, y: p[1] * c.k + c.y});
  function pose(i, seconds) {
    const s = S.scenes[i], time = clamp(seconds, 0, s.duration), cues = s.cues;
    let index = 0;
    for (let n = 1; n < cues.length; n++) if (time >= Math.max(0, cues[n].at - (s.panSeconds ?? 1.6))) index = n;
    const cue = cues[index], target = s.targets[cue.target], previous = s.targets[cues[Math.max(0, index - 1)].target];
    const travel = index === 0 ? 0 : Math.min(s.panSeconds ?? 1.6, (cue.at - cues[index - 1].at) * .55);
    const u = index === 0 ? 1 : ease((time - (cue.at - travel)) / travel);
    const camera = interpolate(destination(s, previous, s.scale), destination(s, target, s.scale), u);
    // A single calm entry. Subsequent source changes retain a fixed scene scale.
    if (i === 0 && time < 2.4) {
      const k = mix(s.scale * .92, s.scale, ease(time / 2.4));
      Object.assign(camera, destination(s, target, k));
    }
    const sourcePoint = LineWorldFocus.along(routes[i][index], u), p = projected([sourcePoint.x, sourcePoint.y], camera);
    const point = {x: p.x, y: p.y, r: 11 + 2 * Math.sin(Math.PI * u)};
    return {camera, point, target: cue.target};
  }
  function renderClip(i, seconds) {
    const s = S.scenes[i], current = pose(i, seconds), fade = i === 0 ? 1 : ease(seconds / .38);
    layers.forEach((layer, n) => {
      layer.style.display = n === i || (n === i - 1 && fade < 1) ? '' : 'none';
      if (n === i) { layer.setAttribute('transform', `translate(${current.camera.x} ${current.camera.y}) scale(${current.camera.k})`); layer.style.opacity = String(fade); }
      else if (n === i - 1 && fade < 1) { const p = pose(n, S.scenes[n].duration); layer.setAttribute('transform', `translate(${p.camera.x} ${p.camera.y}) scale(${p.camera.k})`); layer.style.opacity = '1'; }
    });
    let point = current.point;
    if (i > 0 && fade < 1) { const p = pose(i - 1, S.scenes[i - 1].duration).point; point = {x: mix(p.x, point.x, fade), y: mix(p.y, point.y, fade), r: mix(p.r, point.r, fade)}; }
    guide.setAttribute('cx', point.x); guide.setAttribute('cy', point.y); guide.setAttribute('r', point.r);
    const issues = [], b = s.targets[current.target].box, c = current.camera;
    const box = {x: b[0] * c.k + c.x, y: b[1] * c.k + c.y, w: b[2] * c.k, h: b[3] * c.k};
    if (seconds >= .4 && (point.x < 20 || point.x > 1900 || point.y < 20 || point.y > 1060)) issues.push('guide-outside-frame');
    if (seconds >= .4) for (const b of obstacles(s)) {
      if (point.x > b.x0 * c.k + c.x - point.r - 2 && point.x < b.x1 * c.k + c.x + point.r + 2 && point.y > b.y0 * c.k + c.y - point.r - 2 && point.y < b.y1 * c.k + c.y + point.r + 2) issues.push('guide-over-annotated-control');
    }
    // At each spoken arrival the complete annotated control must remain visible.
    for (const cue of s.cues) if (Math.abs(seconds - cue.at) < 1 / S.fps) {
      const t = s.targets[cue.target].box;
      if (t[0] * c.k + c.x < frame.x - 1 || (t[0] + t[2]) * c.k + c.x > frame.x + frame.w + 1 || t[1] * c.k + c.y < frame.y - 1 || (t[1] + t[3]) * c.k + c.y > frame.y + frame.h + 1) issues.push('clipped-spoken-control:' + cue.target);
    }
    return {scene: s.id, camera: current.camera, guide: point, target: current.target, blend: fade, issues};
  }
  window.renderClip = renderClip;
  window.renderAt = seconds => {
    let time = Math.max(0, seconds), i = 0;
    while (i < S.scenes.length - 1 && time >= S.scenes[i].duration) { time -= S.scenes[i].duration; i++; }
    return renderClip(i, time);
  };
  window.ready = Promise.all(S.scenes.map(s => new Promise((resolve, reject) => {
    const im = new Image(); im.onload = async () => { await im.decode(); resolve(); }; im.onerror = () => reject(Error('Screenshot failed to decode: ' + s.capture)); im.src = s.capture;
  }))).then(() => renderAt(0));
})();
