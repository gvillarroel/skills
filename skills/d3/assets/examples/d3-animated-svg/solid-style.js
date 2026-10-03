/* Finalize authored SVG paint while preserving connectors and open line geometry.
   Supply the bundled colorsets contract through D3_SOLID_PALETTES. */
(function () {
  const palettes = window.D3_SOLID_PALETTES || {};
  const hex = value => {
    if (/^#[0-9a-f]{6}$/i.test(value || "")) return value.toLowerCase();
    const channels = (value || "").match(/^rgba?\(\s*(\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)/i);
    return channels ? "#" + channels.slice(1).map(v => Number(v).toString(16).padStart(2, "0")).join("") : null;
  };
  const rgb = value => [1, 3, 5].map(i => parseInt(value.slice(i, i + 2), 16));
  const luminance = value => rgb(value).map(v => v / 255).map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)
    .reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
  const textOn = value => (luminance(value) + 0.05) / 0.05 >= 1.05 / (luminance(value) + 0.05) ? "#000000" : "#ffffff";
  const composite = (front, back, alpha) => "#" + rgb(front).map((v, i) => Math.round(v * alpha + rgb(back)[i] * (1 - alpha)).toString(16).padStart(2, "0")).join("");
  function categoryStyle(index, colorset = "colorset1", canvas = "#ffffff") {
    const palette = palettes[colorset];
    if (!palette || !Number.isInteger(index) || index < 0) throw new Error("Use a nonnegative category index and a bundled colorset");
    const solids = [...new Set(palette.solidSequence)].filter(value => value.toLowerCase() !== canvas.toLowerCase());
    if (!solids.length) throw new Error("The canvas leaves no category colors");
    const fill = solids[index % solids.length];
    const variant = Math.floor(index / solids.length) - 1;
    const base = { fill, text: palette.textOnFill[fill], stroke: "none", strokeWidth: 0, strokeDasharray: null, tier: "solid", cue: null };
    if (variant < 0) return base;
    const borders = [...new Set(palette.allowed)].filter(value => value !== fill &&
      (Math.max(luminance(value), luminance(fill)) + .05) / (Math.min(luminance(value), luminance(fill)) + .05) >= 3);
    if (variant >= borders.length * 9) return { ...base, tier: "structural", cue: "label-symbol-or-split" };
    const pattern = Math.floor(variant / borders.length) % 3;
    return { ...base, stroke: borders[variant % borders.length], strokeWidth: 1 + Math.floor(variant / (borders.length * 3)),
      strokeDasharray: [null, "6 4", "1 3"][pattern], tier: "overflow" };
  }
  function exempt(element) {
    return !!element.closest('defs, mask, clipPath, pattern, [data-paint-mode="source"], [data-paint-mode="line-art"]');
  }
  const forcedAlpha = new WeakMap();
  function opaque(element, property) {
    let saved = forcedAlpha.get(element);
    if (!saved) { saved = {}; forcedAlpha.set(element, saved); }
    if (!(property in saved)) saved[property] = { value: element.style.getPropertyValue(property), priority: element.style.getPropertyPriority(property) };
    if (element.style.getPropertyValue(property) !== "1") element.style.setProperty(property, "1");
  }
  function restoreFocusAlpha(element) {
    const saved = forcedAlpha.get(element);
    if (!saved) return;
    for (const [property, original] of Object.entries(saved)) {
      if (original.value) element.style.setProperty(property, original.value, original.priority);
      else element.style.removeProperty(property);
    }
    forcedAlpha.delete(element);
  }
  function normalize(svg) {
    if (exempt(svg)) return;
    const active = svg.dataset.colorset || document.body.dataset.colorset || document.body.dataset.colorSet || "colorset1";
    const palette = palettes[active];
    const permitted = new Set(palette?.allowed || []);
    const box = svg.viewBox.baseVal;
    const area = Math.max(1, box.width * box.height);
    const shapes = [...svg.querySelectorAll("rect,circle,ellipse,polygon,path")].filter(element => !exempt(element));
    shapes.forEach(element => {
      const focused = !!element.closest(":focus, :focus-visible");
      if (focused) restoreFocusAlpha(element);
      const style = getComputedStyle(element), fill = hex(style.fill), stroke = hex(style.stroke);
      if (!fill || style.fill === "none" || style.display === "none") return;
      // An unclosed path is a curve, connector, signal trace or handwritten stroke.
      if (element.localName === "path" && !/[zZ]\s*$/.test(element.getAttribute("d") || "")) return;
      let bounds;
      try { bounds = element.getBBox(); } catch { return; }
      const panel = bounds.width * bounds.height > area * 0.35 || /(?:^|[-_ ])(?:panel|frame|background|surface)(?:$|[-_ ])/i.test(element.getAttribute("class") || "");
      const overflow = !!element.closest('[data-outline-tier="overflow"]');
      if (!overflow && !panel && stroke && permitted.has(stroke) && luminance(fill) > 0.6 && luminance(stroke) < 0.5) {
        element.style.setProperty("fill", stroke);
      }
      if (!overflow && element.style.stroke !== "none") element.style.setProperty("stroke", "none");
      // Static translucency is decorative unless the author names its meaning.
      // Explicit overlap/data opacity and reveal animation retain their alpha.
      const semanticAlpha = !!element.closest('[data-opacity-role="semantic"], [data-opacity-role="reveal"]');
      const keyframes = element.getAnimations().flatMap(animation => animation.effect?.getKeyframes() || []);
      const fillReveal = !!element.querySelector('animate[attributeName="fill-opacity"]') || keyframes.some(frame => "fillOpacity" in frame);
      const opacityReveal = !!element.querySelector('animate[attributeName="opacity"]') || keyframes.some(frame => "opacity" in frame);
      if (!semanticAlpha && !focused && !fillReveal && Number(style.fillOpacity) > 0) opaque(element, "fill-opacity");
      if (!semanticAlpha && !focused && !opacityReveal && Number(style.opacity) > 0) opaque(element, "opacity");
      if (element.dataset.fillStyle !== "solid") element.dataset.fillStyle = "solid";
    });
    // Resolve labels against the actual containing mark and composited opacity.
    svg.querySelectorAll("text").forEach(text => {
      if (exempt(text)) return;
      // Letterforms within a logo are painted artwork rather than labels.
      if ((svg.dataset.patternId || "").startsWith("d3-logo-") && text.closest('[data-text-role]')) return;
      const textBox = text.getBoundingClientRect();
      if (!textBox.width || !textBox.height) return;
      const center = new DOMPoint(textBox.x + textBox.width / 2, textBox.y + textBox.height / 2);
      let background = "#ffffff";
      const covering = shapes.filter(shape => {
        const style = getComputedStyle(shape), fill = hex(style.fill);
        if (!fill || style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
        const bounds = shape.getBoundingClientRect();
        if (textBox.x < bounds.x - 2 || textBox.right > bounds.right + 2 || center.y < bounds.y || center.y > bounds.bottom) return false;
        try { return shape.isPointInFill(center.matrixTransform(shape.getScreenCTM().inverse())); } catch { return false; }
      });
      covering.forEach(shape => {
        const style = getComputedStyle(shape);
        let alpha = Number(style.fillOpacity) * Number(style.opacity);
        for (let ancestor = shape.parentElement; ancestor && ancestor !== svg; ancestor = ancestor.parentElement) alpha *= Number(getComputedStyle(ancestor).opacity);
        background = composite(hex(style.fill), background, alpha);
      });
      // SMIL paint overrides inline CSS. Keep animated labels in black/white
      // and synchronize their contrast to the containing mark's paint timeline.
      text.querySelectorAll('animate[attributeName="fill"]').forEach(animation => {
        const mark = covering.at(-1);
        const markAnimation = mark?.querySelector('animate[attributeName="fill"]');
        const values = animation.getAttribute("values");
        if (!values) return;
        const marks = markAnimation?.getAttribute("values")?.split(";");
        const labels = values.split(";");
        const paint = labels.map((value, index) => {
          const fill = hex(marks?.length === labels.length ? marks[index] : "");
          return fill ? textOn(fill) : (luminance(hex(value) || "#000000") > 0.5 ? "#ffffff" : "#000000");
        }).join(";");
        if (values !== paint) animation.setAttribute("values", paint);
        if (animation.getAttribute("calcMode") !== "discrete") animation.setAttribute("calcMode", "discrete");
        if (marks?.length === labels.length && markAnimation.getAttribute("calcMode") !== "discrete") markAnimation.setAttribute("calcMode", "discrete");
      });
      const paint = textOn(background);
      if (text.style.fill !== paint) text.style.setProperty("fill", paint);
      if (text.style.stroke !== "none") text.style.setProperty("stroke", "none");
    });
    svg.dataset.fillStyle = "solid-first";
  }
  let scheduled = false;
  const dirty = new Set();
  const observer = new MutationObserver(records => {
    records.forEach(record => {
      const element = record.target.nodeType === 1 ? record.target : record.target.parentElement;
      const svg = element?.closest("svg");
      if (svg) dirty.add(svg);
      record.addedNodes.forEach(node => { if (node.nodeType === 1) { if (node.matches("svg")) dirty.add(node); node.querySelectorAll?.("svg").forEach(svg => dirty.add(svg)); } });
    });
    schedule();
  });
  function schedule() {
    if (scheduled || !dirty.size) return;
    scheduled = true;
    requestAnimationFrame(() => {
      observer.disconnect();
      dirty.forEach(normalize); dirty.clear(); scheduled = false;
      observer.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ["fill", "fill-opacity", "stroke", "style", "class", "opacity", "transform", "data-opacity-role"] });
    });
  }
  function start() {
    document.querySelectorAll("svg").forEach(svg => dirty.add(svg));
    schedule();
    observer.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ["fill", "fill-opacity", "stroke", "style", "class", "opacity", "transform", "data-opacity-role"] });
    for (const eventName of ["focusin", "focusout"]) document.addEventListener(eventName, event => { const svg = event.target.closest?.("svg"); if (svg) { dirty.add(svg); schedule(); } });
  }
  window.D3SolidStyle = { categoryStyle, normalize, textOn, luminance };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
})();
