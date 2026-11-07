#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure rendered SVG labels in the browser coordinate system."""

_LAYOUT = r"""(svg, minFontPx) => {
    const boundary = svg.getBoundingClientRect();
    const ignored = 'defs, clipPath, mask, pattern, marker, symbol, [data-d3-export-ignore]';
    const labels = [];
    const issues = [];
    for (const node of svg.querySelectorAll('text')) {
        const value = node.textContent.trim().replace(/\s+/g, ' ');
        const style = getComputedStyle(node);
        if (!value || node.closest(ignored) || style.visibility !== 'visible' || style.display === 'none') continue;
        let opacity = Number(style.fillOpacity);
        if (style.fill === 'none' && style.stroke !== 'none') opacity = Number(style.strokeOpacity);
        for (let el = node; el && el !== svg.parentElement; el = el.parentElement) {
            opacity *= Number(getComputedStyle(el).opacity);
        }
        const box = node.getBoundingClientRect();
        if (opacity === 0 || box.width === 0 || box.height === 0) continue;
        const matrix = node.getScreenCTM();
        if (!matrix) continue;
        const font = parseFloat(style.fontSize) * Math.hypot(matrix.c, matrix.d);
        const index = labels.length;
        const exemption = node.getAttribute('data-d3-layout-overlap')?.trim();
        const x = box.left - boundary.left, y = box.top - boundary.top;
        labels.push({id: node.id || null, text: value, fontPx: font, box: [x, y, box.width, box.height],
                     overlapReason: exemption || null});
        if (x < -1 || y < -1 || x + box.width > boundary.width + 1 || y + box.height > boundary.height + 1) {
            issues.push({kind: 'clipped-label', labels: [index]});
        }
        if (font < minFontPx - 0.25) {
            issues.push({kind: 'small-label', labels: [index]});
        }
    }
    // Keep active labels sorted in x to avoid comparing disjoint columns.
    const order = labels.map((_, index) => index).sort((a, b) => labels[a].box[0] - labels[b].box[0]);
    for (const [position, a] of order.entries()) {
        const [ax, ay, aw, ah] = labels[a].box;
        for (let candidate = position + 1; candidate < order.length; candidate++) {
            const b = order[candidate];
            const [bx, by, bw, bh] = labels[b].box;
            if (bx >= ax + aw - 2) break;
            if (labels[a].overlapReason || labels[b].overlapReason) continue;
            const w = Math.min(ax + aw, bx + bw) - bx;
            const h = Math.min(ay + ah, by + bh) - Math.max(ay, by);
            if (w > 2 && h > 2 && w*h > 0.12 * Math.min(aw*ah, bw*bh)) {
                issues.push({kind: 'overlapping-labels', labels: [a, b], areaPx2: w*h});
            }
        }
    }
    return {schemaVersion: 1, viewport: [boundary.width, boundary.height], minFontPx, labels, issues};
}"""


def rendered_layout(locator, min_font_px):
    return locator.evaluate(_LAYOUT, min_font_px)
