#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-layout-templates/scripts/test-layouts.ts
// Node 24+, native APIs only. Do not write into skill bundles.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { categoryPaints, extendCategoryOrder, layoutTheme, planSlideLayout, relativeLuminance, textOnFill } from '../../../skills/slidev-echarts/assets/templates/slidev-layouts/lib/slidev-layouts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
let passed = 0;
function check(name: string, run: () => void) { run(); passed++; console.log(`PASS ${name}`); }
function items(count: number) { return Array.from({ length: count }, (_, i) => ({ id: `component-${i + 1}`, title: `Component ${i + 1}`, category: `category-${i + 1}` })); }
function overlap(a: any, b: any) { return Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x) > 0.5 && Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y) > 0.5; }

for (const file of ['components/SlidevLayout.vue', 'components/SlidevCollection.vue', 'lib/slidev-layouts.mjs']) {
  assert.deepEqual(await fs.readFile(path.join(root, 'skills/slidev-echarts/assets/templates/slidev-layouts', file)), await fs.readFile(path.join(root, 'skills/slidev-animejs/assets/templates/slidev-layouts', file)));
}
check('both runtime bundles are byte-identical', () => {});
const canonical = JSON.parse(await fs.readFile(path.join(root, 'skills/slidev-echarts/assets/palettes/colorsets.json'), 'utf8'));
for (const colorset of ['colorset1', 'colorset2']) {
  check(`${colorset} exact solid order and white-canvas exclusion`, () => {
    const expected = canonical.colorsets[colorset].solidSequence.filter((fill: string) => fill !== '#ffffff');
    const paints = [...categoryPaints(items(expected.length), { colorset }).values()];
    assert.deepEqual(paints.map(paint => paint.fill), expected);
    assert(paints.every(paint => paint.borderWidth === 0 && paint.overflowTier === 0));
  });
  check(`${colorset} overflow begins after every usable solid`, () => {
    const capacity = canonical.colorsets[colorset].solidSequence.length - 1;
    const paints = [...categoryPaints(items(capacity + 10), { colorset }).values()];
    assert(paints.slice(0, capacity).every(paint => paint.borderWidth === 0));
    assert(paints.slice(capacity).every(paint => paint.borderWidth >= 1 && paint.borderWidth <= 3 && paint.overflowTier > 0));
    assert.equal(paints[capacity].fill, '#9e1b32');
  });
  check(`${colorset} maximum black/white text contrast`, () => {
    for (const paint of categoryPaints(items(50), { colorset }).values()) {
      const luminance = relativeLuminance(paint.fill);
      const black = (luminance + .05) / .05;
      const white = 1.05 / (luminance + .05);
      assert.equal(paint.ink, black >= white ? '#000000' : '#ffffff');
      assert(Math.max(black, white) >= 4.5);
    }
  });
}
check('default tokens preserve palette and Open Sans', () => {
  assert.equal(layoutTheme().colorset, 'colorset1');
  assert.equal(layoutTheme().primary, '#9e1b32');
  assert.equal(layoutTheme().canvas, '#ffffff');
  assert.match(layoutTheme().font, /Open Sans/);
  assert.throws(() => layoutTheme('invented'), /Unknown colorset/);
});
check('first-seen registry survives reorder, hide and reveal', () => {
  const all = items(6);
  let order = extendCategoryOrder([], all.slice(0, 3));
  const initial = categoryPaints(all.slice(0, 3), { categoryOrder: order });
  order = extendCategoryOrder(order, [all[5], all[1], all[0]]);
  order = extendCategoryOrder(order, [...all].reverse());
  const final = categoryPaints([...all].reverse(), { categoryOrder: order });
  for (const [id, paint] of initial) assert.deepEqual(final.get(id), paint);
  assert.deepEqual(order.slice(0, 4), ['category-1', 'category-2', 'category-3', 'category-6']);
});
check('explicit identity manifest reserves positions before visible pages', () => {
  const all = items(12);
  const manifest = all.map(item => item.category);
  const first = planSlideLayout({ items: all, pageSize: 6, page: 1, categoryOrder: manifest });
  const last = planSlideLayout({ items: all, pageSize: 6, page: 2, categoryOrder: manifest });
  const reversed = planSlideLayout({ items: [...all].reverse(), pageSize: 6, categoryOrder: manifest });
  const map = new Map([...first.items, ...last.items].map(item => [item.id, item.fill]));
  for (const item of reversed.items) assert.equal(item.fill, map.get(item.id));
});
check('columns use balanced contiguous vertical stacks', () => {
  const plan = planSlideLayout({ items: items(7), mode: 'columns', columns: 3, height: 400 });
  assert.deepEqual(plan.items.map(item => item.column), [0, 0, 0, 1, 1, 2, 2]);
  assert.deepEqual(plan.items.map(item => item.row), [0, 1, 2, 0, 1, 0, 1]);
  assert.equal(plan.fits, true);
});
check('grid has equal width and equal measured maximum height', () => {
  const plan = planSlideLayout({ items: items(7), columns: 3, rows: 3, height: 400, measurements: { 'component-1': { height: 130 }, 'component-5': { height: 180 } } });
  assert.equal(new Set(plan.items.map(item => item.width)).size, 1);
  assert.equal(new Set(plan.items.map(item => item.height)).size, 1);
  assert.equal(plan.items[0].height, 180);
  assert.equal(plan.fits, false);
  assert(plan.reasons.includes('frame-height'));
});
check('component content budgets exclude padding and overflow borders', () => {
  const plan = planSlideLayout({ items: items(17), pageSize: 1, page: 17 });
  const box = plan.items[0];
  assert.equal(box.borderWidth, 1);
  assert.equal(box.contentWidth, box.width - 30);
  assert.equal(box.contentHeight, box.height - 30);
});
check('traditional masonry chooses the actual shortest column', () => {
  const all = items(6);
  const heights = [160, 120, 100, 110, 130, 100];
  const measurements = Object.fromEntries(all.map((item, i) => [item.id, { height: heights[i] }]));
  const plan = planSlideLayout({ items: all, mode: 'masonry-columns', measurements, height: 400, gap: 16 });
  assert.deepEqual(plan.items.map(item => item.column), [0, 1, 2, 2, 1, 0]);
  assert.deepEqual(plan.items.slice(3).map(item => item.y), [116, 136, 176]);
  assert.equal(plan.fits, true);
});
check('horizontal masonry uses exactly three configured tracks', () => {
  const all = items(7).map((item, index) => ({ ...item, width: [160, 210, 180, 260, 190, 170, 160][index] }));
  const plan = planSlideLayout({ items: all, mode: 'masonry-rows', rows: 3, height: 400 });
  assert.equal(plan.configuredRows, 3);
  assert.equal(plan.occupiedRows, 3);
  assert.deepEqual(plan.items.map(item => item.row), [0, 1, 2, 0, 2, 1, 2]);
  assert.equal(plan.fits, true);
  assert.equal(planSlideLayout({ items: all.slice(0, 2), mode: 'masonry-rows', rows: 3 }).occupiedRows, 2);
});
check('all modes preserve identity and geometry without rectangle overlap', () => {
  for (const mode of ['columns', 'grid', 'masonry-columns', 'masonry-rows']) {
    for (let n = 0; n <= 30; n++) {
      const plan = planSlideLayout({ items: items(n), mode, columns: 3, rows: 3 });
      assert.deepEqual(plan.visibleIds, items(n).map(item => item.id));
      assert(plan.items.every(item => item.width > 0 && item.height > 0 && item.x >= 0 && item.y >= 0));
      for (let i = 0; i < plan.items.length; i++) for (let j = i + 1; j < plan.items.length; j++) assert.equal(overlap(plan.items[i], plan.items[j]), false, `${mode}/${n}/${i}/${j}`);
    }
  }
});
check('explicit pageSize covers every item without omissions or paint shifts', () => {
  const all = items(22);
  const first = planSlideLayout({ items: all, pageSize: 9 });
  assert.equal(first.pages, 3);
  const pages = [1, 2, 3].map(page => planSlideLayout({ items: all, pageSize: 9, page }));
  assert.deepEqual(pages.flatMap(page => page.visibleIds), all.map(item => item.id));
  assert(pages.every(page => page.totalItems === 22 && page.pageSize === 9));
});
check('narrow frames report width capacity rather than shrinking cards', () => {
  const plan = planSlideLayout({ items: items(3), width: 250, columns: 3, minItemWidth: 140 });
  assert.equal(plan.fits, false);
  assert.equal(plan.items[0].width, 140);
  assert.equal(plan.requiredWidth, 452);
  assert.deepEqual(plan.reasons, ['frame-width']);
});
check('oversized natural content remains measured and reports capacity', () => {
  const plan = planSlideLayout({ items: items(1), height: 390, measurements: { 'component-1': { height: 600 } } });
  assert.equal(plan.items[0].height, 600);
  assert.equal(plan.requiredHeight, 600);
  assert.equal(plan.fits, false);
  assert.deepEqual(plan.overflowIds, ['component-1']);
});
check('content wider than its own box fails even inside the frame', () => {
  const plan = planSlideLayout({ items: items(3), measurements: { 'component-1': { width: 450 } } });
  assert.equal(plan.fits, false);
  assert(plan.reasons.includes('item-width'));
  assert(plan.overflowIds.includes('component-1'));
});
check('inputs, measurements and caller manifests are not mutated', () => {
  const input = { items: items(7), categoryOrder: ['reserved'], measurements: { 'component-1': { height: 120 } } };
  const snapshot = JSON.stringify(input);
  planSlideLayout(input);
  assert.equal(JSON.stringify(input), snapshot);
});
check('invalid geometry, pages, identities and colors are rejected', () => {
  for (const options of [{ columns: 0 }, { rows: -1 }, { columns: 1.5 }, { gap: -1 }, { gap: NaN }, { width: Infinity }, { height: 0 }, { page: 0 }, { page: 2 }, { pageSize: 0 }, { minItemWidth: -1 }, { mode: 'experimental-masonry' }, { colorset: 'forest' }, { items: [{ id: '' }] }, { items: [{ id: 'duplicate' }, { id: 'duplicate' }] }, { categoryOrder: ['duplicate', 'duplicate'] }, { measurements: { 'component-1': { height: 0 } } }, { measurements: { 'component-1': { width: Infinity } } }]) {
    assert.throws(() => planSlideLayout({ items: items(1), ...options }));
  }
  assert.throws(() => categoryPaints(items(1), { canvas: '#123456' }));
  assert.throws(() => textOnFill('red'));
});
console.log(JSON.stringify({ passed, status: 'pass', matrix: '4 modes × 31 item counts plus exact palette, identity, pagination and capacity boundaries' }));
