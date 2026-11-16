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
  // Paint readable delivery states against a completed reveal without changing
  // the actual hidden/reveal clock. Semantic alpha retains its current meaning.
  function restingAlpha(node, property) {
    const style = getComputedStyle(node);
    if (node.closest('[data-opacity-role="semantic"]')) return Number(style[property]);
    const animation = node.querySelector(':scope > animate[attributeName="'+(property === 'fillOpacity' ? 'fill-opacity' : 'opacity')+'"]');
    if (animation && animation.getAttribute('fill') === 'freeze') {
      const final = (animation.getAttribute('values') || '').split(';').at(-1) || animation.getAttribute('to');
      if (final !== null && final !== '' && Number.isFinite(Number(final))) return Number(final);
    }
    const frames = node.getAnimations().flatMap(animation => animation.effect?.getKeyframes() || []).filter(frame => property in frame);
    return frames.length ? Number(frames.at(-1)[property]) : Number(style[property]);
  }
  function normalizeArrows(svg, palette) {
    if (!palette) return;
    const geometry = [...svg.querySelectorAll('rect,circle,ellipse,polygon,path')].filter(shape => !exempt(shape) && !shape.closest('defs') &&
      !(shape.localName === 'circle' && /pulse/.test(shape.getAttribute('class') || '') && [...shape.children].some(child => child.localName.toLowerCase() === 'animatemotion')));
    const order = [...svg.querySelectorAll('*')];
    const inside = (shape, point) => {
      const style = getComputedStyle(shape);
      if (!hex(style.fill) || style.display === 'none' || style.visibility === 'hidden' || restingAlpha(shape, 'opacity') === 0) return false;
      try { return shape.isPointInFill(point.matrixTransform(shape.getScreenCTM().inverse())); } catch { return false; }
    };
    const backing = (point, owner, ignored = []) => {
      let color = '#ffffff';
      const ancestors = [];
      for (let node = svg; node; node = node.parentElement) ancestors.unshift(node);
      ancestors.forEach(node => {
        const paint = getComputedStyle(node).backgroundColor, value = hex(paint);
        const alpha = paint.startsWith('rgba') ? Number(paint.match(/,\s*([\d.]+)\s*\)$/)?.[1] ?? 0) : 1;
        if (value && alpha > 0) color = composite(value, color, alpha);
      });
      let occluded = false;
      for (const shape of geometry) {
        if (shape === owner || ignored.includes(shape) || !inside(shape, point)) continue;
        const style = getComputedStyle(shape);
        let alpha = restingAlpha(shape, 'fillOpacity') * restingAlpha(shape, 'opacity');
        for (let parent = shape.parentElement; parent && parent !== svg; parent = parent.parentElement) alpha *= restingAlpha(parent, 'opacity');
        color = composite(hex(style.fill), color, alpha);
        if (order.indexOf(shape) > order.indexOf(owner)) occluded = true;
      }
      return { color, occluded };
    };
    // Explicit line/triangle direction glyphs retain their geometry and data
    // encoding. Scope their common paint against the actual local underlays.
    svg.querySelectorAll('[data-direction-role="glyph"]').forEach(glyph => {
      if (exempt(glyph)) return;
      const members = glyph.matches('line,path,polygon') ? [glyph] : [...glyph.querySelectorAll('line,path,polygon')];
      const grounds = [];
      members.forEach(member => {
        const box = member.getBBox(), points = member.localName === 'line' ?
          Array.from({length: 15}, (_, i) => member.getPointAtLength(member.getTotalLength() * (i + 1) / 16)) :
          [[.2,.5],[.6,.5],[.2,.3],[.2,.7]].map(([x,y]) => new DOMPoint(box.x+box.width*x,box.y+box.height*y)).filter(point => member.isPointInFill(point));
        points.forEach(point => grounds.push(backing(new DOMPoint(point.x,point.y).matrixTransform(member.getScreenCTM()), member, members).color));
      });
      if (!grounds.length || !members.length) return;
      const backingSelector = glyph.getAttribute('data-direction-backing');
      if (backingSelector) {
        const substrate = glyph.parentElement.querySelector(backingSelector);
        if (!substrate || !hex(getComputedStyle(substrate).fill)) { glyph.dataset.arrowUnresolved = 'The declared direction backing is missing or unpainted'; return; }
        // Equipment icons declare their enclosing solid face explicitly. This
        // avoids transient reveal hit testing choosing the distant canvas.
        const style = getComputedStyle(substrate);
        let alpha = restingAlpha(substrate, 'fillOpacity') * restingAlpha(substrate, 'opacity');
        for (let parent = substrate.parentElement; parent && parent !== svg; parent = parent.parentElement) alpha *= restingAlpha(parent, 'opacity');
        grounds.splice(0, grounds.length, composite(hex(style.fill), '#ffffff', alpha));
      }
      glyph.dataset.directionBackings = [...new Set(grounds)].join(',');
      const first = getComputedStyle(members[0]), original = hex(first.fill === 'none' || members[0].localName === 'line' ? first.stroke : first.fill) || palette.roles.ink;
      const level = paint => Math.min(...grounds.map(ground => (Math.max(luminance(paint),luminance(ground))+.05)/(Math.min(luminance(paint),luminance(ground))+.05)));
      const candidates = palette.allowed.filter(paint => level(paint) >= 3).sort((a,b) =>
        rgb(a).reduce((sum,v,i)=>sum+(v-rgb(original)[i])**2,0)-rgb(b).reduce((sum,v,i)=>sum+(v-rgb(original)[i])**2,0));
      if (!candidates.length) { glyph.dataset.arrowUnresolved = 'Direction glyph crosses incompatible backings; move it or scope its paint'; return; }
      const paint = candidates.includes(original) ? original : candidates[0];
      members.forEach(member => {
        const property = member.localName === 'line' || getComputedStyle(member).fill === 'none' ? 'stroke' : 'fill';
        member.setAttribute(property, paint);member.style.setProperty(property, paint);
      });
      glyph.dataset.directionContrast = level(paint).toFixed(3);delete glyph.dataset.arrowUnresolved;
    });
    const owners = [...svg.querySelectorAll('path,line,polyline')].filter(owner => !exempt(owner) && getComputedStyle(owner).markerEnd !== 'none');
    owners.forEach((owner, index) => {
      const style = getComputedStyle(owner);
      const current = style.markerEnd.match(/#([^"')]+)/)?.[1];
      if (!current || !owner.getTotalLength) return;
      const sourceId = owner.dataset.arrowMarkerSource || current;
      const source = svg.querySelector('#' + CSS.escape(sourceId));
      const sourcePaint = source?.querySelector('path,polygon,circle');
      if (!sourcePaint) return;
      const endpointDot = sourcePaint.localName === 'circle';
      owner.dataset.arrowMarkerSource = sourceId;
      const length = owner.getTotalLength();
      const at = distance => { const point = owner.getPointAtLength(Math.max(0, Math.min(length, distance))); return new DOMPoint(point.x, point.y).matrixTransform(owner.getScreenCTM()); };
      const endpoint = owner.getPointAtLength(length), previous = owner.getPointAtLength(Math.max(0, length - .5));
      const angle = Math.atan2(endpoint.y - previous.y, endpoint.x - previous.x);
      const end = at(length), area = Math.max(1, svg.viewBox.baseVal.width * svg.viewBox.baseVal.height);
      const targets = geometry.filter(shape => {
        if (shape === owner || !inside(shape, end)) return false;
        const bounds = shape.getBBox();
        return bounds.width * bounds.height < area * .2 && !/(?:panel|background|surface)/i.test(shape.getAttribute('class') || '');
      });
      let retreat = 0;
      if (targets.length && !endpointDot) {
        const terminalAt = offset => new DOMPoint(endpoint.x-Math.cos(angle)*offset,
          endpoint.y-Math.sin(angle)*offset).matrixTransform(owner.getScreenCTM());
        while (retreat < length && targets.some(shape => inside(shape, terminalAt(retreat)))) retreat += .5;
        retreat = Math.min(length, retreat + 4);
      }
      const box = sourcePaint.getBBox();
      const scale = source.markerWidth.baseVal.value / (source.viewBox.baseVal.width || box.width) * (source.getAttribute('markerUnits') === 'userSpaceOnUse' ? 1 : parseFloat(style.strokeWidth));
      if (!(scale > 0)) return;
      const projected = (x, y, offset) => {
        x = (x - (endpointDot ? source.refX.baseVal.value : box.x + box.width)) * scale - offset;
        y = (y - source.refY.baseVal.value) * scale;
        return new DOMPoint(endpoint.x + Math.cos(angle) * x - Math.sin(angle) * y,
          endpoint.y + Math.sin(angle) * x + Math.cos(angle) * y).matrixTransform(owner.getScreenCTM());
      };
      // A curved path's terminal marker follows its final tangent, not the arc.
      // Test the actual tip and wings, including nodes just beyond the endpoint.
      const silhouette = [[box.x + box.width, box.y + box.height * .5],
        [box.x + box.width * .12, box.y + box.height * .12],
        [box.x + box.width * .12, box.y + box.height * .88],
        [box.x + box.width * .55, box.y + box.height * .5]];
      // Do not retreat through the source node in a narrow gutter. The owning
      // route must leave room for the complete head plus the 4-unit clearance.
      const identity = (svg.id || svg.dataset.patternId || 'diagram') + '-direction-' + index;
      let marker = svg.querySelector('#' + CSS.escape(identity));
      if (!marker) { marker = source.cloneNode(true); marker.id = identity; source.parentElement.append(marker); }
      marker.setAttribute('refX', String(endpointDot ? source.refX.baseVal.value : box.x + box.width + retreat / scale));
      const backgrounds = [];
      for (const fraction of Array.from({length: 127}, (_, i) => (i + 1) / 128)) {
        const under = backing(at(length * fraction), owner);
        if (!under.occluded) backgrounds.push(under.color);
      }
      const headBackgrounds = silhouette.map(([x,y]) => backing(projected(x,y,retreat), owner).color);
      let alpha = Number(style.strokeOpacity);
      for (let node = owner; node && node !== svg; node = node.parentElement) {
        const animated = node.querySelector(':scope > animate[attributeName="opacity"]') ||
          node.getAnimations().some(animation => animation.effect?.getKeyframes().some(frame => 'opacity' in frame));
        if (!animated) alpha *= Number(getComputedStyle(node).opacity);
      }
      const level = (paint, grounds = backgrounds, opacity = alpha) => Math.min(...grounds.map(background => {
        const a = luminance(composite(paint, background, opacity)), b = luminance(background);
        return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      }));
      const original = hex(style.stroke) || palette.roles.ink;
      const distance = paint => rgb(paint).reduce((sum, channel, i) => sum + (channel - rgb(original)[i]) ** 2, 0);
      const combined = [...backgrounds, ...headBackgrounds];
      const shared = palette.allowed.filter(paint => level(paint, combined) >= 3).sort((a,b) => distance(a) - distance(b));
      const permitted = shared.length ? shared : palette.allowed.filter(paint => level(paint) >= 3).sort((a,b) => distance(a) - distance(b));
      const paint = permitted[0] || [...palette.allowed].sort((a,b) => level(b) - level(a))[0];
      const headPermitted = palette.allowed.filter(candidate => level(candidate, headBackgrounds, 1) >= 3).sort((a,b) => distance(a) - distance(b));
      const headPaint = level(paint, headBackgrounds, 1) >= 3 ? paint : headPermitted[0];
      if (!permitted.length) owner.dataset.arrowUnresolved = 'No allowed paint reaches 3:1 across the sampled local backings; reroute or scope terminal paint';
      else if (!headPaint) owner.dataset.arrowUnresolved = 'The head crosses incompatible local backings; give the route a clear terminal gutter';
      else delete owner.dataset.arrowUnresolved;
      owner.dataset.arrowTerminalPaint = headPaint || paint;
      owner.style.setProperty('stroke', paint);
      owner.setAttribute('stroke', paint);
      marker.querySelectorAll('path,polygon,circle').forEach((shape, i) => {
        const original = source.querySelectorAll('path,polygon,circle')[i];
        const open = getComputedStyle(original).fill === 'none';
        shape.setAttribute(open ? 'stroke' : 'fill', headPaint || paint);
        shape.style.setProperty(open ? 'stroke' : 'fill', headPaint || paint);
        shape.setAttribute(open ? 'fill' : 'stroke', 'none');
      });
      owner.setAttribute('marker-end', 'url(#' + identity + ')');
      owner.dataset.arrowClearance = String(retreat);
      owner.dataset.arrowContrast = level(paint).toFixed(3);
    });
    // Moving flow pulses retain their path and clock, but cannot obscure a
    // persistent tip. Clip only the exact triangular head silhouettes out of
    // pulse layers; this adds neither a halo nor a category-node outline.
    const pulseLayers = [...new Set([...svg.querySelectorAll('circle > animateMotion')].map(animation => animation.parentElement.parentElement))]
      .filter(layer => layer.localName === 'g' && !layer.hasAttribute('transform'));
    if (pulseLayers.length && owners.length) {
      const holes = [];
      owners.forEach(owner => {
        const id = getComputedStyle(owner).markerEnd.match(/#([^"')]+)/)?.[1];
        const marker = id && svg.querySelector('#' + CSS.escape(id)), glyph = marker?.querySelector('path,polygon');
        if (!glyph || (glyph.localName === 'path' && /[cCqQaAhHvVsStT]/.test(glyph.getAttribute('d') || ''))) return;
        const coordinates = (glyph.getAttribute(glyph.localName === 'polygon' ? 'points' : 'd') || '').match(/-?\d+(?:\.\d+)?/g)?.map(Number);
        if (!coordinates || coordinates.length !== 6) return;
        const length = owner.getTotalLength(), end = owner.getPointAtLength(length), before = owner.getPointAtLength(Math.max(0,length-.5));
        const angle = Math.atan2(end.y-before.y,end.x-before.x), bounds = glyph.getBBox();
        const scale = marker.markerWidth.baseVal.value / (marker.viewBox.baseVal.width || bounds.width) *
          (marker.getAttribute('markerUnits') === 'userSpaceOnUse' ? 1 : parseFloat(getComputedStyle(owner).strokeWidth));
        const points = [0,2,4].map(i => {
          const x = (coordinates[i]-marker.refX.baseVal.value)*scale, y=(coordinates[i+1]-marker.refY.baseVal.value)*scale;
          return new DOMPoint(end.x+Math.cos(angle)*x-Math.sin(angle)*y,end.y+Math.sin(angle)*x+Math.cos(angle)*y)
            .matrixTransform(owner.getScreenCTM()).matrixTransform(svg.getScreenCTM().inverse());
        });
        holes.push('M'+points.map(point=>point.x+','+point.y).join('L')+'Z');
      });
      svg.querySelectorAll('[data-direction-role="glyph"]').forEach(glyph => {
        const shapes = glyph.matches('path,polygon') ? [glyph] : [...glyph.querySelectorAll('path,polygon')];
        shapes.forEach(shape => {
          if (exempt(shape) || (shape.localName === 'path' && /[cCqQaAhHvVsStT]/.test(shape.getAttribute('d') || ''))) return;
          const coordinates = (shape.getAttribute(shape.localName === 'polygon' ? 'points' : 'd') || '').match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/gi)?.map(Number);
          if (!coordinates || coordinates.length !== 6) return;
          const points = [0,2,4].map(i => new DOMPoint(coordinates[i],coordinates[i+1]).matrixTransform(shape.getScreenCTM()).matrixTransform(svg.getScreenCTM().inverse()));
          holes.push('M'+points.map(point=>point.x+','+point.y).join('L')+'Z');
        });
      });
      const identity = (svg.id || 'diagram')+'-pulse-tip-clearance';
      let clip = svg.querySelector('#'+CSS.escape(identity));
      if (!clip) { clip=document.createElementNS(svg.namespaceURI,'clipPath');clip.id=identity;svg.querySelector('defs').append(clip); }
      clip.setAttribute('clipPathUnits','userSpaceOnUse');
      let path=clip.querySelector('path');
      if (!path) { path=document.createElementNS(svg.namespaceURI,'path');clip.append(path); }
      const box=svg.viewBox.baseVal;
      path.setAttribute('d',`M${box.x},${box.y}h${box.width}v${box.height}h${-box.width}Z `+holes.join(' '));
      path.setAttribute('clip-rule','evenodd');path.setAttribute('fill-rule','evenodd');
      pulseLayers.forEach(layer=>{layer.setAttribute('clip-path','url(#'+identity+')');layer.dataset.pulseHeadGuard='exact-silhouette';});
    }
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
    // Resolve labels against actual containing paint at its readable delivery
    // state; parent SMIL opacity changes do not trigger attribute observers.
    svg.querySelectorAll("text").forEach(text => {
      if (exempt(text)) return;
      // Letterforms within a logo are painted artwork rather than labels.
      if ((svg.dataset.patternId || "").startsWith("d3-logo-") && text.closest('[data-text-role]')) return;
      const textBox = text.getBoundingClientRect();
      if (!textBox.width || !textBox.height) return;
      const center = new DOMPoint(textBox.x + textBox.width / 2, textBox.y + textBox.height / 2);
      let background = "#ffffff";
      const textScope = text.closest('[data-text-backing]');
      const textBacking = textScope?.querySelector(textScope.dataset.textBacking);
      // Explicit enclosing faces remain the label substrate during a geometry
      // reveal too (for example an instrument circle growing from radius 5).
      const covering = textBacking && hex(getComputedStyle(textBacking).fill) ? [textBacking] : shapes.filter(shape => {
        const style = getComputedStyle(shape), fill = hex(style.fill);
        if (!fill || style.display === "none" || style.visibility === "hidden" || restingAlpha(shape, "opacity") === 0) return false;
        const bounds = shape.getBoundingClientRect();
        if (textBox.x < bounds.x - 2 || textBox.right > bounds.right + 2 || center.y < bounds.y || center.y > bounds.bottom) return false;
        try { return shape.isPointInFill(center.matrixTransform(shape.getScreenCTM().inverse())); } catch { return false; }
      });
      covering.forEach(shape => {
        const style = getComputedStyle(shape);
        let alpha = restingAlpha(shape, "fillOpacity") * restingAlpha(shape, "opacity");
        for (let ancestor = shape.parentElement; ancestor && ancestor !== svg; ancestor = ancestor.parentElement) alpha *= restingAlpha(ancestor, "opacity");
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
    normalizeArrows(svg, palette);
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
