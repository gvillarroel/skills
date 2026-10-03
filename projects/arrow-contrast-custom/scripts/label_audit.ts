// Browser evaluator only. Required package: Playwright; invoke through the owning
// uv Python browser probe. Syntax: node --experimental-strip-types --check
// projects/arrow-contrast-custom/scripts/label_audit.ts.
window.auditInstrumentLabels = () => {
  const luminance = rgb => rgb.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
    .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
  return [...document.querySelectorAll('[data-instrument-id]')].flatMap(group => {
    const face = group.querySelector('circle');
    if (!face) return [];
    const fill = getComputedStyle(face).fill;
    const channels = fill.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/)?.slice(1).map(Number);
    if (!channels) throw new Error('Instrument face needs an actual solid RGB fill');
    const light = luminance(channels), black = (light + .05) / .05, white = 1.05 / (light + .05);
    const expected = black >= white ? 'rgb(0, 0, 0)' : 'rgb(255, 255, 255)';
    let alpha = Number(getComputedStyle(face).fillOpacity);
    for (let node = face; node && node.localName !== 'svg'; node = node.parentElement) alpha *= Number(getComputedStyle(node).opacity);
    return [...group.querySelectorAll('text')].map(label => ({
      instrumentId: group.dataset.instrumentId, text: label.textContent, faceFill: fill,
      actual: getComputedStyle(label).fill, expected, alpha, contrast: Math.max(black, white),
      passed: getComputedStyle(label).fill === expected
    }));
  });
};
window.auditCalloutLabels = () => {
  const luminance = rgb => rgb.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
    .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
  return [...document.querySelectorAll('[data-gap-id]')].flatMap(group => {
    const face = group.querySelector('rect'),bounds = face.getBoundingClientRect(),fill = getComputedStyle(face).fill;
    const channels = fill.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/)?.slice(1).map(Number);
    if (!channels) throw new Error('Callout face needs actual solid RGB fill');
    const light = luminance(channels),black = (light + .05) / .05,white = 1.05 / (light + .05);
    const expected = black >= white ? 'rgb(0, 0, 0)' : 'rgb(255, 255, 255)';
    return [...group.querySelectorAll('text')].map(label => {
      const box = label.getBoundingClientRect(),contained = box.x >= bounds.x-.5 && box.right <= bounds.right+.5 && box.y >= bounds.y-.5 && box.bottom <= bounds.bottom+.5;
      return {calloutId:group.dataset.gapId,text:label.textContent,faceFill:fill,actual:getComputedStyle(label).fill,expected,fontSize:getComputedStyle(label).fontSize,textBounds:box.toJSON(),faceBounds:bounds.toJSON(),contained,contrast:Math.max(black,white),passed:contained&&getComputedStyle(label).fill===expected};
    });
  });
};
