/* Restore reviewed photographic color only inside semantic parent-clock focus. */
(() => {
  'use strict';
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  const ease = n => { n = Math.max(0, Math.min(1, n)); return n * n * (3 - 2 * n); };
  function intervals(windows) {
    if (!Array.isArray(windows) || !windows.length) throw Error('Declare photograph focus windows.');
    const ordered = windows.map(w => {
      if (!finite(w.start) || !finite(w.end) || w.start < 0 || w.end <= w.start) throw Error('Use finite positive photograph focus intervals.');
      return {start: w.start, end: w.end};
    }).sort((a, b) => a.start - b.start);
    const merged = [];
    for (const w of ordered) {
      const previous = merged.at(-1);
      if (previous && w.start <= previous.end) previous.end = Math.max(previous.end, w.end);
      else merged.push({...w});
    }
    return merged;
  }
  function state(binding, seconds) {
    if (!finite(seconds)) throw Error('Render photographs with a finite parent-clock time.');
    const transition = binding.transition ?? .35;
    if (!finite(transition) || transition < 0 || transition > 2) throw Error('Photograph transition must be between zero and two seconds.');
    let color = 0;
    for (const w of intervals(binding.windows)) {
      if (seconds < w.start || seconds >= w.end) continue;
      const fade = Math.min(transition, (w.end - w.start) / 2);
      color = fade === 0 ? 1 : ease(Math.min((seconds - w.start) / fade, (w.end - seconds) / fade));
    }
    return {id: binding.id, color, focused: color > 0};
  }
  function attach(root, bindings) {
    if (!Array.isArray(bindings) || !bindings.length) throw Error('Provide photograph bindings.');
    const ids = new Set(), elements = new Set();
    // Validate every binding before modifying any source element.
    const prepared = bindings.map(b => {
      state(b, 0);
      const matches = root.querySelectorAll(b.target);
      if (!b.id || ids.has(b.id) || matches.length !== 1 || matches[0].localName !== 'image' || !b.color) throw Error('Bind unique photograph IDs to one SVG image and its reviewed color source.');
      const source = matches[0];
      if (elements.has(source) || source.closest('[data-lw-photo-focus]')) throw Error('A photograph already has a color-focus controller.');
      ids.add(b.id); elements.add(source);
      if (b.neutral && new URL(source.getAttribute('href'), document.baseURI).href !== new URL(b.neutral, document.baseURI).href) throw Error('Neutral photograph differs from the prepared pair.');
      return {binding: b, source};
    });
    const bound = prepared.map(({binding, source}) => {
      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.dataset.lwPhotoFocus = binding.id;
      source.before(group); group.append(source);
      const color = source.cloneNode(false);
      for (const name of [...color.attributes].map(a => a.name)) if (name === 'id' || name.startsWith('data-')) color.removeAttribute(name);
      color.removeAttributeNS('http://www.w3.org/1999/xlink', 'href');
      color.setAttribute('href', binding.color); color.setAttribute('aria-hidden', 'true');
      color.dataset.lwPhotoColor = binding.id;
      color.style.setProperty('filter', 'none', 'important');
      color.style.setProperty('transition', 'none', 'important');
      color.style.setProperty('animation', 'none', 'important');
      color.style.pointerEvents = 'none'; color.style.opacity = '0'; group.append(color);
      const load = url => new Promise((resolve, reject) => {
        const image = new Image(); image.onload = async () => {
          try { await image.decode(); resolve([image.naturalWidth, image.naturalHeight]); }
          catch (error) { reject(error); }
        };
        image.onerror = () => reject(Error('Photographic source failed to load: ' + url)); image.src = url;
      });
      const ready = Promise.all([load(source.getAttribute('href')), load(binding.color)]).then(([neutral, original]) => {
        if (neutral[0] !== original[0] || neutral[1] !== original[1]) throw Error('Use aligned neutral/color photographs from the same prepared crop.');
      });
      return {binding, source, group, color, ready};
    });
    let destroyed = false;
    return {
      ready: Promise.all(bound.map(b => b.ready)),
      render(seconds) {
        if (destroyed) throw Error('Photograph controller was destroyed.');
        return bound.map(({binding, source, color}) => {
          const current = state(binding, seconds), paint = getComputedStyle(source);
          color.style.opacity = String(current.color * Number(paint.opacity));
          color.style.display = paint.display; color.style.visibility = paint.visibility;
          return current;
        });
      },
      destroy() {
        for (const {source, group} of bound) { group.before(source); group.remove(); }
        destroyed = true;
      }
    };
  }
  window.LineWorldPhotoFocus = {attach, state};
})();
