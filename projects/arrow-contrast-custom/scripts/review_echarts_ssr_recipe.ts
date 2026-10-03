// Run: node --experimental-strip-types projects/arrow-contrast-custom/scripts/review_echarts_ssr_recipe.ts
// Dependencies: ECharts 6.1.0 and Playwright 1.60.0 from the owning fixture package.
// Independent, read-only review of the compact native SSR graph recipe.
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {prepareColorsetOption} from '../../../skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs';

const root = new URL('../../../', import.meta.url);
const require = createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json', root));
const echarts = require('echarts');
const {chromium} = require('playwright');
const artifacts = new URL('projects/arrow-contrast-custom/artifacts/reviews/echarts-native-ssr-recipe/', root);
mkdirSync(artifacts, {recursive: true});
const sourcePaths = ['skills/echarts-animated-svg/references/arrow-contrast.md', 'skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs'];
const hashes = () => Object.fromEntries(sourcePaths.map(path => [path, createHash('sha256').update(readFileSync(new URL(path, root))).digest('hex')]));
const beforeHashes = hashes();
const browser = await chromium.launch({headless: true});
const page = await browser.newPage({viewport: {width: 640, height: 360}, deviceScaleFactor: 1});
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
const states = [];

for (const colorset of ['colorset1', 'colorset2']) {
  // The recipe is recreated verbatim apart from its palette argument.
  const option = {
    animation: false, backgroundColor: '#ffffff',
    series: [{
      type: 'graph', layout: 'none', symbolSize: 60,
      edgeSymbol: ['none', 'arrow'], edgeSymbolSize: 16,
      label: {show: true, position: 'inside'},
      data: [{id: 'a', name: 'A', x: 100, y: 180},
             {id: 'b', name: 'B', x: 500, y: 180}],
      links: [{source: 'a', target: 'b'}],
      lineStyle: {color: '#cfcfcf', opacity: 0.25}
    }]
  };
  const baseline = JSON.parse(JSON.stringify(option));
  const returned = prepareColorsetOption(option, colorset);
  const chart = echarts.init(null, null, {
    renderer: 'svg', ssr: true, width: 640, height: 360
  });
  chart.setOption(option);
  const actualCoordinateSystem = chart.getModel().getSeriesByIndex(0).coordinateSystem.type;
  const svg = chart.renderToSVGString();
  chart.dispose();
  const svgUrl = new URL(colorset + '.svg', artifacts);
  writeFileSync(svgUrl, svg);
  await page.goto(svgUrl.href);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const measured = await page.evaluate(() => {
    const rootSvg = document.querySelector('svg');
    const rgb = value => value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
    const luminance = c => c.map(v => v / 255).map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)
      .reduce((sum, v, index) => sum + v * [0.2126, 0.7152, 0.0722][index], 0);
    const contrast = (a, b) => (Math.max(luminance(a), luminance(b)) + 0.05) / (Math.min(luminance(a), luminance(b)) + 0.05);
    const alpha = element => {let a = 1; for (let p = element; p; p = p.parentElement) a *= Number(getComputedStyle(p).opacity); return a;};
    const paths = [...rootSvg.querySelectorAll('path')].filter(element => !element.closest('defs'));
    const nodes = paths.filter(element => /[Aa]/.test(element.getAttribute('d')) && getComputedStyle(element).fill !== 'none');
    const heads = paths.filter(element => !nodes.includes(element) && getComputedStyle(element).fill !== 'none');
    const shafts = paths.filter(element => getComputedStyle(element).fill === 'none' && getComputedStyle(element).stroke !== 'none');
    const filled = [...rootSvg.querySelectorAll('path,rect,circle,polygon')].filter(element => !element.closest('defs') && getComputedStyle(element).fill !== 'none' && !heads.includes(element));
    const backing = (point, owner) => {
      let color = [255, 255, 255]; const coveredBy = [];
      for (const element of filled) {
        if (element === owner || !element.isPointInFill(point.matrixTransform(element.getScreenCTM().inverse()))) continue;
        if (owner.compareDocumentPosition(element) & Node.DOCUMENT_POSITION_FOLLOWING) continue;
        const css = getComputedStyle(element), paint = rgb(css.fill), a = alpha(element) * Number(css.fillOpacity);
        color = color.map((v, index) => v * (1 - a) + paint[index] * a);
        if (nodes.includes(element)) coveredBy.push('node');
      }
      return {color, coveredBy};
    };
    const occludedBy = (point, owner) => filled.filter(element => element !== owner
      && (owner.compareDocumentPosition(element) & Node.DOCUMENT_POSITION_FOLLOWING)
      && element.isPointInFill(point.matrixTransform(element.getScreenCTM().inverse()))
      && alpha(element) * Number(getComputedStyle(element).fillOpacity) === 1).map(element => nodes.includes(element) ? 'node' : element.tagName);
    const records = [];
    for (const [part, elements] of [['shaft', shafts], ['head', heads]]) {
      for (const element of elements) {
        const css = getComputedStyle(element), paint = rgb(css[part === 'shaft' ? 'stroke' : 'fill']);
        const opacity = alpha(element) * Number(css[part === 'shaft' ? 'strokeOpacity' : 'fillOpacity']);
        const samples = [];
        if (part === 'shaft') {
          const length = element.getTotalLength();
          for (let index = 0; index <= 126; index++) samples.push({point: element.getPointAtLength(length * index / 126).matrixTransform(element.getScreenCTM()), kind: 'shaft'});
        } else {
          const b = element.getBBox();
          for (let u = 0.05; u < 1; u += 0.05) for (let v = 0.05; v < 1; v += 0.05) {
            const point = new DOMPoint(b.x + b.width * u, b.y + b.height * v);
            if (element.isPointInFill(point)) samples.push({point: point.matrixTransform(element.getScreenCTM()), kind: 'interior'});
          }
          // Include actual native tip and terminal boundary points as well as interiors.
          for (let index = 0; index <= 80; index++) samples.push({point: element.getPointAtLength(element.getTotalLength() * index / 80).matrixTransform(element.getScreenCTM()), kind: 'boundary'});
        }
        const points = samples.map(({point, kind}) => {
          const under = backing(point, element), visible = paint.map((v, index) => v * opacity + under.color[index] * (1 - opacity));
          return {x: point.x, y: point.y, kind, occludedBy: occludedBy(point, element), backing: under.color, coveredBy: under.coveredBy, contrast: contrast(visible, under.color)};
        });
        const visiblePoints = points.filter(point => point.occludedBy.length === 0);
        const b = element.getBoundingClientRect();
        const matrix = element.getScreenCTM(), screenStrokeWidth = Number.parseFloat(css.strokeWidth) * Math.sqrt(Math.abs(matrix.a * matrix.d - matrix.b * matrix.c));
        records.push({part, d: element.getAttribute('d'), transform: element.getAttribute('transform'), paint: css[part === 'shaft' ? 'stroke' : 'fill'], opacity,
          strokeWidth: Number.parseFloat(css.strokeWidth), screenStrokeWidth, bounds: {x: b.x, y: b.y, width: b.width, height: b.height}, sampleCount: points.length,
          visibleSampleCount: visiblePoints.length, occludedSampleCount: points.length - visiblePoints.length,
          occludedInteriorCount: points.filter(p => p.kind === 'interior' && p.occludedBy.length > 0).length,
          minimumContrast: Math.min(...visiblePoints.map(p => p.contrast)), coveredSampleCount: visiblePoints.filter(p => p.coveredBy.length).length,
          xRange: [Math.min(...points.map(p => p.x)), Math.max(...points.map(p => p.x))]});
      }
    }
    const nodeRecords = nodes.map(element => {
      const css = getComputedStyle(element), b = element.getBoundingClientRect();
      return {fill: css.fill, opacity: alpha(element) * Number(css.fillOpacity), stroke: css.stroke, strokeWidth: Number.parseFloat(css.strokeWidth),
        bounds: {x: b.x, y: b.y, width: b.width, height: b.height}};
    });
    const labels = [...rootSvg.querySelectorAll('text')].map(element => {
      const b = element.getBoundingClientRect(), point = new DOMPoint(b.x + b.width / 2, b.y + b.height / 2), under = backing(point, element), css = getComputedStyle(element);
      const black = contrast([0, 0, 0], under.color), white = contrast([255, 255, 255], under.color), expected = black >= white ? 'rgb(0, 0, 0)' : 'rgb(255, 255, 255)';
      return {text: element.textContent, fill: css.fill, expected, actualBacking: under.color, passed: css.fill === expected};
    });
    const orderedNodes = nodeRecords.sort((a, b) => a.bounds.x - b.bounds.x);
    const head = records.find(record => record.part === 'head');
    const targetLeft = orderedNodes[1]?.bounds.x;
    return {nodes: nodeRecords, labels, shaftCount: shafts.length, headCount: heads.length, records,
      nativeTipClearance: targetLeft - head?.xRange[1], targetLeft, nativeTipX: head?.xRange[1]};
  });
  const screenshot = new URL(colorset + '.png', artifacts);
  await page.screenshot({path: fileURLToPath(screenshot)});
  const passed = actualCoordinateSystem === 'view' && returned === option && option.series[0].symbolSize === 60 && option.series[0].edgeSymbolSize === 16
    && measured.nodes.length === 2 && measured.nodes.every(n => Math.abs(n.bounds.width - 60) < 0.02 && Math.abs(n.bounds.height - 60) < 0.02 && n.opacity === 1 && (n.stroke === 'none' || n.strokeWidth === 0))
    && measured.shaftCount === 1 && measured.headCount === 1 && measured.records.every(r => r.visibleSampleCount > 0 && r.minimumContrast >= 3 && r.coveredSampleCount === 0 && r.opacity === 1 && r.occludedInteriorCount === 0)
    && measured.records.find(r => r.part === 'shaft').screenStrokeWidth >= 1.5 && measured.labels.every(label => label.passed) && measured.nativeTipClearance >= -0.02;
  states.push({colorset, actualCoordinateSystem, preparationReturnsSameObject: returned === option, baselineLineStyle: baseline.series[0].lineStyle,
    preparedLineStyle: option.series[0].lineStyle, preparedEdgeStyle: option.series[0].links[0].lineStyle,
    symbolSize: option.series[0].symbolSize, edgeSymbolSize: option.series[0].edgeSymbolSize,
    artifact: fileURLToPath(svgUrl).replace(fileURLToPath(root), '').replaceAll('\\', '/'), screenshot: fileURLToPath(screenshot).replace(fileURLToPath(root), '').replaceAll('\\', '/'),
    svgSha256: createHash('sha256').update(svg).digest('hex'), ...measured, passed});
}
await browser.close();
const afterHashes = hashes();
const sourceUnchanged = JSON.stringify(beforeHashes) === JSON.stringify(afterHashes);
const report = {date: '2026-10-03', skill: 'echarts-animated-svg', case: 'independent-native-ssr-graph-recipe', model: null, validationType: 'deterministic independent read-only artifact review',
  command: 'node --experimental-strip-types projects/arrow-contrast-custom/scripts/review_echarts_ssr_recipe.ts', echartsVersion: echarts.version,
  sourceHashes: afterHashes, sourceUnchanged, errors, states, passed: echarts.version === '6.1.0' && sourceUnchanged && errors.length === 0 && states.every(state => state.passed),
  scope: 'Exact compact SSR graph recipe with fresh nested options in both palettes. Actual view coordinates, solid borderless 60px circle nodes, native 16px arrow symbol, dense shaft/head interior and boundary backing probes respecting SVG paint order, and max black/white labels. Native source-end shaft geometry hidden behind the origin node and the tangent tip boundary are recorded separately from visible samples. No native source changes or Pi process. This fixture exercises static exported geometry; arbitrary crossed fills and custom arrows still require independent checks.',
  retainedProbeAttempt: 'evaluations/arrow-contrast/custom-native-ssr-recipe-review-attempt1-20261003.json',
  retainedProbeLimitation: 'Attempt 1 treated later-painted opaque nodes as underlays and required stroke-width zero even when stroke was none. Its false failures are retained as evaluator limitations; canonical recipe bytes did not change.'};
const reportUrl = new URL('evaluations/arrow-contrast/custom-native-ssr-recipe-review-20261003.json', root);
writeFileSync(reportUrl, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
