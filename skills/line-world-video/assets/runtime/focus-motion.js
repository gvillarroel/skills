/* Meaningful motion during long focus holds, driven only by the parent clock. */
(() => {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg', PRIMARY = '#9e1b32';
  const clamp = x => Math.max(0, Math.min(1, x));
  const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
  function validate(windows) {
    const ids = new Set();
    for (const w of windows) {
      if (!w.id || ids.has(w.id)) throw Error('Focus motion needs unique window IDs.');
      ids.add(w.id);
      if (!Number.isFinite(w.start) || !Number.isFinite(w.end) || w.start < 0 || w.end <= w.start) throw Error('Use a positive focus interval on the parent clock.');
      if (!['chart', 'diagram'].includes(w.kind)) throw Error('Declare chart or diagram focus.');
      if (!['trace', 'pulse'].includes(w.mode || 'trace')) throw Error('Use trace or pulse motion.');
      if (w.period !== undefined && (!Number.isFinite(w.period) || w.period < 2.4)) throw Error('Keep a calm motion period of at least 2.4 seconds.');
    }
  }
  function state(window, time) {
    const duration = window.end - window.start, active = duration > 2 && time >= window.start && time < window.end;
    const elapsed = time - window.start, phase = ((elapsed / (window.period || 3.2)) % 1 + 1) % 1;
    const opacity = active ? ease(elapsed / .22) * ease((window.end - time) / .22) : 0;
    return {id: window.id, eligible: duration > 2, active, phase, opacity, mode: window.mode || 'trace'};
  }
  function attach(root, windows) {
    validate(windows);
    const lengths = new WeakMap();
    const bindings = windows.map(w => {
      const matches = typeof w.source === 'string' ? root.querySelectorAll(w.source) : [w.source];
      if (matches.length !== 1 || !matches[0] || typeof matches[0].getTotalLength !== 'function') throw Error('Bind each focus source to one real SVG geometry element.');
      const source = matches[0], overlay = document.createElementNS(NS, source.tagName);
      if ((w.mode || 'trace') === 'trace' && source.tagName.toLowerCase() === 'path' && (source.getAttribute('d')?.match(/[Mm]/g) || []).length > 1) throw Error('Trace one continuous SVG path; bind separate edges or use pulse for multiple subpaths.');
      overlay.setAttribute('data-lw-motion-overlay', w.id); overlay.setAttribute('aria-hidden', 'true');
      overlay.style.pointerEvents = 'none'; overlay.style.fill = 'none'; overlay.style.stroke = PRIMARY;
      overlay.style.strokeWidth = '3'; overlay.style.strokeLinecap = 'round'; overlay.style.vectorEffect = 'non-scaling-stroke';
      source.parentNode.appendChild(overlay);
      return {window: w, source, overlay};
    });
    let current = [];
    function render(time) {
      if (!Number.isFinite(time)) throw Error('Render motion at a finite parent-clock time.');
      current = bindings.map(({window: w, source, overlay}) => {
        const s = state(w, time);
        if (!s.active) { overlay.style.display = 'none'; return s; }
        const geometry = [];
        for (const key of ['d', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'width', 'height', 'rx', 'ry', 'cx', 'cy', 'r', 'points', 'transform', 'clip-path']) {
          const value = source.getAttribute(key); geometry.push(value);
          if (value !== null) overlay.setAttribute(key, value); else overlay.removeAttribute(key);
        }
        const key = JSON.stringify(geometry), previous = lengths.get(source);
        if (previous?.key !== key) lengths.set(source, {key, length: source.getTotalLength()});
        const length = lengths.get(source).length, paint = getComputedStyle(source);
        overlay.style.strokeWidth = String(Math.min(6, Math.max(3, (parseFloat(paint.strokeWidth) || 1) + 2)));
        overlay.style.clipPath = paint.clipPath;
        overlay.style.display = s.active && length > 0 && paint.display !== 'none' && paint.visibility !== 'hidden' && +paint.opacity > 0 ? '' : 'none';
        overlay.style.opacity = String(s.opacity * (s.mode === 'pulse' ? .45 + .4 * (.5 - .5 * Math.cos(s.phase * Math.PI * 2)) : .9));
        overlay.style.strokeDasharray = s.mode === 'trace' ? `${length * .13} ${length * .87}` : 'none';
        overlay.style.strokeDashoffset = String(-length * s.phase);
        return s;
      });
      return current.map(s => ({...s}));
    }
    render(-1);
    return {render, snapshot: () => current.map(s => ({...s})), destroy: () => bindings.forEach(b => b.overlay.remove())};
  }
  globalThis.LineWorldFocusMotion = Object.freeze({attach, state, validate, thresholdSeconds: 2});
})();
