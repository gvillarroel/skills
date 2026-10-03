#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.52.0"]
# ///
"""Measure solid SVG text against local browser-painted backgrounds at rest."""

from __future__ import annotations

import io
import math
from typing import Any

from PIL import Image


def _luminance(rgb) -> float:
    channels = [float(v) / 255 for v in rgb]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(channel * weight for channel, weight in zip(linear, (.2126, .7152, .0722)))


def _contrast(first, second) -> float:
    a, b = _luminance(first), _luminance(second)
    return (max(a, b) + .05) / (min(a, b) + .05)


def _pixels(image):
    return getattr(image, "get_flattened_data", image.getdata)()


COLLECT = r"""() => {
  const texts = [...document.querySelectorAll('svg text')];
  const all = [...document.querySelectorAll('svg, svg *, html, body')];
  const styles = all.map(el => [el, el.getAttribute('style')]);
  const canvas = document.createElementNS('http://www.w3.org/1999/xhtml', 'canvas');
  canvas.width = canvas.height = 1;
  const ctx = canvas.getContext('2d', {willReadFrequently:true});
  const rgba = value => {
    if (!CSS.supports('color', value)) return null;
    ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = value; ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data];
  };
  const records = texts.map((el, index) => {
    const cs = getComputedStyle(el), box = el.getBoundingClientRect();
    const unsupported = [], hidden = [];
    let groupOpacity = 1;
    for (let node = el; node; node = node.parentElement) {
      const s = getComputedStyle(node);
      if (s.display === 'none') hidden.push('display-none');
      if (Number(s.opacity) === 0) hidden.push('zero-opacity');
      if (node !== el) groupOpacity *= Number(s.opacity);
      // A shadow outside a group does not change the interior foreground paint.
      if (s.filter !== 'none' && (!s.filter.startsWith('drop-shadow(') ||
          /(?:opacity|brightness|contrast|saturate|grayscale|invert|sepia|hue-rotate|blur|url)\(/.test(s.filter))) unsupported.push('filter');
      if (s.maskImage !== 'none') unsupported.push('mask');
      if (s.mixBlendMode !== 'normal') unsupported.push('blend-mode');
    }
    if (groupOpacity < .999) unsupported.push('group-opacity-compositing');
    if (cs.visibility !== 'visible') hidden.push('visibility');
    if (!el.textContent.trim() || !box.width || !box.height) hidden.push('empty');
    if (box.right <= 0 || box.bottom <= 0 || box.left >= innerWidth || box.top >= innerHeight) hidden.push('offscreen');
    if (el.closest('[aria-disabled="true"], [disabled]')) hidden.push('disabled-control');
    if (Number(cs.fillOpacity) === 0 || cs.fill === 'none') hidden.push('no-fill');
    if (cs.stroke !== 'none' && Number(cs.strokeOpacity) > 0 && Number.parseFloat(cs.strokeWidth) > 0) unsupported.push('text-stroke');
    const color = rgba(cs.fill);
    if (!color) unsupported.push('non-solid-text-paint');
    else if (color[3] === 0) hidden.push('transparent-fill');
    for (const child of el.querySelectorAll('tspan, textPath')) {
      const s = getComputedStyle(child);
      if (s.fill !== cs.fill || s.fillOpacity !== cs.fillOpacity || Number(s.opacity) !== 1 ||
          s.stroke !== cs.stroke || s.filter !== 'none' || s.visibility !== cs.visibility) {
        unsupported.push('mixed-text-run-paint');
      }
    }
    return {index, id:el.id || 'text-' + index, moduleId:el.closest('[data-module-id]')?.dataset.moduleId || null,
      text:el.textContent.trim(), color, alpha:Number(cs.opacity) * Number(cs.fillOpacity) * (color ? color[3]/255 : 1),
      box:{x:box.x,y:box.y,width:box.width,height:box.height},
      hidden:[...new Set(hidden)], unsupported:[...new Set(unsupported)]};
  });
  let maskIndex = 0;
  records.forEach(record => {
    if (!record.hidden.length && !record.unsupported.length) record.maskIndex = maskIndex++;
  });
  return {texts, styles, records};
}"""


def audit_text_contrast(page: Any) -> dict[str, Any]:
    """Compare author foregrounds with pixels under glyphs, excluding antialiasing.

    Use at a paused scenario or camera state. Two temporary captures provide the actual
    background and a glyph mask. Never replace a variable background with its majority
    color. Mixed text paints, text strokes, masks, and group alpha remain incomplete.
    All inline styles are restored, including when capture fails; the semantic state
    is never changed. Device-pixel scaling is normalized by CSS-scale screenshots.
    """
    state = page.evaluate_handle(COLLECT)
    records = state.evaluate("state => state.records")
    result = {"ok": False, "threshold": 4.5, "checked": 0, "skipped": 0,
              "incomplete": 0, "failed": 0, "findings": [], "skippedReasons": {}}
    active = []
    for record in records:
        if record["hidden"]:
            result["skipped"] += 1
            for reason in record["hidden"]:
                result["skippedReasons"][reason] = result["skippedReasons"].get(reason, 0) + 1
        elif record["unsupported"]:
            result["incomplete"] += 1
            result["findings"].append({**record, "status": "inconclusive", "reason": ", ".join(record["unsupported"])})
        else:
            active.append(record)
    try:
        if active:
            state.evaluate("""state => state.texts.forEach(el => [el, ...el.querySelectorAll('tspan,textPath')].forEach(
              node => node.style.setProperty('visibility','hidden','important')))""")
            background = Image.open(io.BytesIO(page.screenshot(scale="css"))).convert("RGB")
            state.evaluate(r"""state => {
              for (const [el] of state.styles) {
                if (el.closest('defs')) continue;
                el.style.setProperty('transition','none','important');
                if (el.matches('svg,html,body')) el.style.setProperty('background','#000000','important');
                if (el.matches('path,rect,circle,ellipse,line,polygon,polyline,image,use,foreignObject')) {
                  const prior = getComputedStyle(el).filter;
                  el.style.setProperty('filter','brightness(0)' + (prior === 'none' ? '' : ' ' + prior),'important');
                } else el.style.setProperty('filter','none','important');
              }
              for (const record of state.records) {
                const el = state.texts[record.index];
                for (const node of [el, ...el.querySelectorAll('tspan,textPath')]) {
                  node.style.setProperty('visibility', record.hidden.length || record.unsupported.length ? 'hidden' : 'visible','important');
                  const color = 'rgb(255,' + (7 + (record.maskIndex % 31) * 8) + ',' + (7 + Math.floor(record.maskIndex / 31) * 8) + ')';
                  node.style.setProperty('fill',color,'important');
                  node.style.setProperty('fill-opacity','1','important');
                  node.style.setProperty('opacity','1','important');
                  node.style.setProperty('stroke','none','important');
                }
              }
            }""")
            mask = Image.open(io.BytesIO(page.screenshot(scale="css"))).convert("RGB")
            if background.size != mask.size:
                raise ValueError("text/background captures changed dimensions")
            for item in active:
                box = item["box"]
                bounds = (max(0, math.floor(box["x"])), max(0, math.floor(box["y"])),
                          min(mask.width, math.ceil(box["x"] + box["width"])),
                          min(mask.height, math.ceil(box["y"] + box["height"])))
                if item["maskIndex"] >= 961:
                    result["incomplete"] += 1
                    result["findings"].append({**item, "status": "inconclusive", "reason": "more than 961 text nodes; audit a smaller view"})
                    continue
                target_green, target_blue = 7 + item["maskIndex"] % 31 * 8, 7 + item["maskIndex"] // 31 * 8
                candidates = [(r, color) for (r, g, b), color in zip(_pixels(mask.crop(bounds)), _pixels(background.crop(bounds)))
                              if r >= 32 and abs(g * 255 / r - target_green) <= 3 and abs(b * 255 / r - target_blue) <= 3]
                peak = max((coverage for coverage, _ in candidates), default=0)
                # Encoded glyph colors exclude adjacent or overlapping text. Blackened
                # graphics retain paint order and alpha, so opaque occluders stay masked.
                colors = {color for coverage, color in candidates if coverage >= max(32, peak * .8)}
                if not colors:
                    result["skipped"] += 1
                    reason = "not-painted-at-this-view"
                    result["skippedReasons"][reason] = result["skippedReasons"].get(reason, 0) + 1
                    continue
                foreground, alpha = item["color"][:3], item["alpha"]
                def ratio(bg):
                    paint = [foreground[i] * alpha + bg[i] * (1 - alpha) for i in range(3)]
                    return _contrast(paint, bg)
                worst = min(colors, key=ratio)
                contrast = ratio(worst)
                status = "pass" if contrast >= 4.5 else "fail"
                result["checked"] += 1
                result["failed"] += status == "fail"
                result["findings"].append({**item, "status": status, "ratio": contrast,
                                           "background": list(worst), "backgroundSamples": len(colors)})
    finally:
        try:
            state.evaluate("""state => {
              const restore = () => state.styles.forEach(([el, style]) => {
                if (style === null) {
                  const attribute = el.getAttributeNode('style');
                  if (attribute) el.removeAttributeNode(attribute);
                } else el.setAttribute('style', style);
              });
              restore();
              state.styles.forEach(([el]) => el.style.setProperty('transition','none','important'));
              void document.documentElement.getBoundingClientRect();
              restore();
            }""")
        finally:
            state.dispose()
    result["ok"] = result["checked"] > 0 and result["failed"] == 0 and result["incomplete"] == 0
    return result
