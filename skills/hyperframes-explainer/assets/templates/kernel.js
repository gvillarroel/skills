// Pure declarative scene kernel. The film has no browser-clock or pointer inputs.
(function (global) {
  'use strict';
  function create(brief, palette) {
    const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
    const events = [...brief.events].sort((a, b) => a.at - b.at);
    const duration = brief.output.duration;
    function integral(name, seconds, overrides) {
      if (Object.hasOwn(overrides, name)) return overrides[name] * seconds;
      let total = 0, cursor = 0, value = brief.sources[name].value;
      for (const event of events.filter(e => Object.hasOwn(e.changes, name))) {
        if (seconds <= event.at) break;
        total += value * (event.at - cursor);
        const target = event.changes[name];
        if (event.duration > 0) {
          const elapsed = Math.min(seconds - event.at, event.duration);
          total += value * elapsed + (target - value) * elapsed * elapsed / (2 * event.duration);
          if (seconds < event.at + event.duration) return total;
        }
        value = target; cursor = event.at + event.duration;
      }
      return total + value * (seconds - cursor);
    }
    function stateAt(seconds, overrides = {}) {
      const time = clamp(seconds, 0, duration);
      const state = {time};
      for (const [name, source] of Object.entries(brief.sources)) {
        let value = source.value;
        for (const event of events.filter(e => Object.hasOwn(e.changes, name))) {
          if (time < event.at) break;
          const fraction = event.duration ? clamp((time - event.at) / event.duration, 0, 1) : 1;
          value += (event.changes[name] - value) * fraction;
          if (fraction < 1) break;
        }
        state[name] = Object.hasOwn(overrides, name) ? overrides[name] : value;
      }
      const visiting = new Set();
      function expr(x) {
        if (typeof x === 'number') return x;
        if (typeof x === 'string') {
          if (Object.hasOwn(state, x)) return state[x];
          if (visiting.has(x)) throw Error(`Cyclic quantity: ${x}`);
          visiting.add(x); state[x] = expr(brief.derived[x].expr); visiting.delete(x); return state[x];
        }
        const [op, args] = Object.entries(x)[0];
        if (op === 'integrate') return integral(args[0], expr(args[1]), overrides);
        const a = args.map(expr);
        const ops = {
          add: () => a.reduce((s, v) => s + v, 0), sub: () => a[0] - a[1],
          mul: () => a.reduce((s, v) => s * v, 1), div: () => a[0] / a[1],
          min: () => Math.min(...a), max: () => Math.max(...a), pow: () => a[0] ** a[1],
          clamp: () => clamp(...a), abs: () => Math.abs(a[0]), sqrt: () => Math.sqrt(a[0]),
          sin: () => Math.sin(a[0]), cos: () => Math.cos(a[0]),
          mod: () => a[1] > 0 ? ((a[0] % a[1]) + a[1]) % a[1] : NaN,
        };
        const value = ops[op]();
        if (!Number.isFinite(value)) throw Error(`Undefined ${op} at ${time}`);
        return value;
      }
      for (const name of Object.keys(brief.derived)) expr(name);
      return {state, expr};
    }
    function snapshot(seconds, overrides = {}) {
      const {state, expr} = stateAt(seconds, overrides);
      const marks = brief.marks.map(mark => {
        const attrs = Object.fromEntries(Object.entries(mark.attrs || {}).map(([k, v]) => [k, expr(v)]));
        let text = mark.text || '', d = mark.d || '';
        if (mark.kind === 'text' && Object.hasOwn(mark, 'value')) {
          text = `${text}${text ? '  ' : ''}${expr(mark.value).toFixed(mark.digits ?? 1)}${mark.unit ? ' ' + mark.unit : ''}`;
        }
        if (mark.kind === 'plot') {
          const count = mark.samples || 100;
          const points = [];
          for (let i = 0; i <= count; i++) {
            const sample = stateAt(state.time * i / count, overrides);
            const xv = sample.expr(mark.xValue), yv = sample.expr(mark.yValue);
            const px = attrs.x + (xv - mark.xDomain[0]) / (mark.xDomain[1] - mark.xDomain[0]) * attrs.width;
            const py = attrs.y + attrs.height - (yv - mark.yDomain[0]) / (mark.yDomain[1] - mark.yDomain[0]) * attrs.height;
            points.push([px, py]);
          }
          d = points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(4)} ${y.toFixed(4)}`).join(' ');
          attrs.pointX = points.at(-1)[0]; attrs.pointY = points.at(-1)[1];
        }
        const role = (brief.entities || {})[mark.entity];
        const fill = mark.kind === 'text' || !role || ['line', 'path', 'plot'].includes(mark.kind) ? mark.fill : role;
        const stroke = role && ['line', 'path', 'plot'].includes(mark.kind) ? role : mark.stroke;
        return {id: mark.id, kind: mark.kind, attrs, text, d,
          fill: fill && fill !== 'none' ? palette.roles[fill] : 'none',
          stroke: stroke && stroke !== 'none' ? palette.roles[stroke] : 'none'};
      });
      return {time: state.time, state, marks};
    }
    return {stateAt: (t, o) => stateAt(t, o).state, snapshot};
  }
  global.ExplainerKernel = {create};
})(globalThis);
