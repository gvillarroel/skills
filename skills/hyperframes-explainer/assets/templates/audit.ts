#!/usr/bin/env -S node --experimental-strip-types
// Node.js >=24: node scripts/audit.ts --report audit.json --screenshot preview.png.
import path from 'node:path';
import {readFileSync, writeFileSync, mkdirSync, existsSync} from 'node:fs';
import http from 'node:http';
import puppeteer from 'puppeteer-core';
const project = path.resolve(import.meta.dirname, '..');
const args = process.argv.slice(2);
const option = (name, fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const reportPath = path.resolve(option('--report', 'audit.json'));
const screenshotPath = path.resolve(option('--screenshot', 'preview.png'));
const brief = JSON.parse(readFileSync(path.join(project, 'brief.json'), 'utf8'));
const oracle = JSON.parse(readFileSync(path.join(project, 'oracle.json'), 'utf8'));
const browserPath = [process.env.HYPERFRAMES_BROWSER_PATH, 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium',
  '/usr/bin/chromium-browser', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'].filter(Boolean).find(p => existsSync(p!));
const findings = [], consoleErrors = [];
let browser;
const mime = {'.html': 'text/html', '.js': 'text/javascript', '.ttf': 'font/ttf', '.json': 'application/json'};
const server = http.createServer((req, res) => {
  const relative = decodeURIComponent(new URL(req.url!, 'http://localhost').pathname).slice(1) || 'index.html';
  const file = path.resolve(project, relative);
  if (!file.startsWith(project + path.sep) || !existsSync(file)) {res.writeHead(404).end(); return;}
  res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(readFileSync(file));
});
await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
try {
  if (!browserPath) throw Error('Chrome/Chromium is missing. Set HYPERFRAMES_BROWSER_PATH to an installed browser.');
  mkdirSync(path.join(project, '.cache/audit-browser'), {recursive: true});
  browser = await puppeteer.launch({executablePath: browserPath, headless: true, userDataDir: path.join(project, '.cache/audit-browser'),
    args: ['--no-sandbox', '--disable-dev-shm-usage']});
  const page = await browser.newPage();
  await page.setViewport({width: brief.output.width, height: brief.output.height, deviceScaleFactor: 1});
  page.on('pageerror', error => consoleErrors.push(error.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, {waitUntil: 'networkidle0'});
  await page.evaluate(async () => {await document.fonts.ready;});
  const scenarios = oracle.oracle;
  let checks = 0;
  for (const scenario of [...scenarios, ...scenarios.slice().reverse().filter(s => !Object.keys(s.overrides).length)]) {
    const result = await page.evaluate(async ({scenario, bindings}) => {
      const api = window.explainer;
      api.clearInputs(); api.seek(scenario.time);
      if (Object.keys(scenario.overrides).length) api.setInputs(scenario.overrides);
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const frame = api.snapshot(scenario.time, scenario.overrides);
      const errors = [];
      for (const [key, value] of Object.entries(scenario.state)) {
        if (Math.abs(frame.state[key] - value) > 1e-7) errors.push(`Oracle disagreement ${key} at ${scenario.time}`);
      }
      if (Math.abs(Number(document.getElementById('stage').dataset.time) - scenario.time) > 1e-7) errors.push('DOM uses a different time.');
      function rgb(paint) {
        const numbers = paint.match(/[\d.]+/g);
        return numbers ? numbers.slice(0, 3).map(Number) : [];
      }
      function lum(paint) {const a = rgb(paint).map(v => {v /= 255; return v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4;});
        return .2126*a[0] + .7152*a[1] + .0722*a[2];}
      const background = getComputedStyle(document.body).backgroundColor;
      const allowed = new Set(api.palette.allowed);
      for (const resolved of frame.marks) {
        const node = document.querySelector(`[data-mark="${resolved.id}"]`);
        for (const [key, value] of Object.entries(resolved.attrs)) {
          if (['translateX', 'translateY', 'rotation', 'pointX', 'pointY'].includes(key)) continue;
          const actual = Number(node.getAttribute(key === 'fontSize' ? 'font-size' : key));
          if (Math.abs(actual-value) > 1e-7) errors.push(`DOM binding ${resolved.id}.${key} differs from shared state.`);
        }
        if (resolved.kind === 'text' && node.textContent !== resolved.text) errors.push(`Detached value label: ${resolved.id}`);
        if (['path', 'plot'].includes(resolved.kind) && node.getAttribute('d') !== resolved.d) errors.push(`Stale path: ${resolved.id}`);
        if (resolved.kind === 'path' && node.getAttribute('transform') !== `translate(${resolved.attrs.translateX || 0} ${resolved.attrs.translateY || 0}) rotate(${resolved.attrs.rotation || 0})`)
          errors.push(`Stale transformed geometry: ${resolved.id}`);
        if (resolved.kind === 'plot') {
          const point = document.querySelector(`[data-point="${resolved.id}"]`);
          if (Math.abs(Number(point.getAttribute('cx'))-resolved.attrs.pointX)>1e-7 || Math.abs(Number(point.getAttribute('cy'))-resolved.attrs.pointY)>1e-7)
            errors.push(`Detached current point: ${resolved.id}`);
        }
        const style = getComputedStyle(node);
        for (const key of ['fill', 'stroke']) {
          if (node.getAttribute(key) !== resolved[key]) errors.push(`DOM paint binding differs: ${resolved.id}.${key}`);
          if (style[key] !== 'none') {
            const color = '#' + rgb(style[key]).map(v => v.toString(16).padStart(2, '0')).join('');
            if (!allowed.has(color)) errors.push(`Outside palette: ${resolved.id} ${color}`);
          }
        }
        const box = node.getBBox(), view = api.brief.views.find(v => v.id === bindings[resolved.id].view);
        const matrix = node.getCTM();
        const corners = [[box.x, box.y], [box.x+box.width, box.y], [box.x, box.y+box.height], [box.x+box.width, box.y+box.height]]
          .map(([x,y]) => new DOMPoint(x,y).matrixTransform(matrix));
        if (corners.some(p => p.x < view.region[0]-1 || p.y < view.region[1]-1 || p.x > view.region[0]+view.region[2]+1 || p.y > view.region[1]+view.region[3]+1))
          errors.push(`Mark leaves its view: ${resolved.id} at ${scenario.time}s inputs=${JSON.stringify(scenario.overrides)}; x=${Math.min(...corners.map(p=>p.x)).toFixed(1)}..${Math.max(...corners.map(p=>p.x)).toFixed(1)}, y=${Math.min(...corners.map(p=>p.y)).toFixed(1)}..${Math.max(...corners.map(p=>p.y)).toFixed(1)}; allowed=${view.region.join(',')}`);
        const screen = node.getBoundingClientRect();
        if (screen.left < -1 || screen.top < -1 || screen.right > api.brief.output.width+1 || screen.bottom > api.brief.output.height+1)
          errors.push(`Canvas clipping: ${resolved.id} at ${scenario.time}s inputs=${JSON.stringify(scenario.overrides)}; bounds=${[screen.left,screen.top,screen.right,screen.bottom].map(v=>v.toFixed(1)).join(',')}`);
        if (resolved.kind === 'text') {
          const fontSize = parseFloat(style.fontSize);
          if (fontSize < 24*api.brief.output.height/1080) errors.push(`Unreadable label size: ${resolved.id}`);
          let backdrop = background;
          const center = [screen.left+screen.width/2, screen.top+screen.height/2];
          for (const other of [...document.querySelectorAll('rect')].filter(n => n.compareDocumentPosition(node)&Node.DOCUMENT_POSITION_FOLLOWING)) {
            const b = other.getBoundingClientRect();
            if (center[0] >= b.left && center[0] <= b.right && center[1] >= b.top && center[1] <= b.bottom && getComputedStyle(other).fill !== 'none') backdrop = getComputedStyle(other).fill;
          }
          const a = lum(style.fill), b = lum(backdrop), ratio = (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
          if (ratio < (fontSize >= 24 ? 3 : 4.5)) errors.push(`Low text contrast: ${resolved.id} ${ratio.toFixed(2)}`);
        }
      }
      const labels = [...document.querySelectorAll('text')];
      for (let i=0; i<labels.length; i++) for (let j=i+1; j<labels.length; j++) {
        const a=labels[i].getBoundingClientRect(), b=labels[j].getBoundingClientRect();
        if (Math.min(a.right,b.right)-Math.max(a.left,b.left)>2 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2)
          errors.push(`Overlapping direct labels: ${labels[i].dataset.mark}, ${labels[j].dataset.mark} at ${scenario.time}`);
      }
      return {errors, state: frame.state};
    }, {scenario, bindings: oracle.bindings});
    for (const error of result.errors) if (!findings.includes(error)) findings.push(error);
    checks++;
  }
  const inputTests = await page.evaluate(() => {
    const api = window.explainer, result = [];
    const signature = node => node.outerHTML;
    for (const [name, source] of Object.entries(api.brief.sources)) {
      const time = api.brief.output.duration / 2;
      api.clearInputs(); api.seek(time);
      const before = new Map([...document.querySelectorAll('[data-mark]')].map(n => [n.dataset.mark, signature(n)]));
      const state = api.stateAt(time);
      const target = Math.abs(state[name]-source.domain[0]) > Math.abs(state[name]-source.domain[1]) ? source.domain[0] : source.domain[1];
      const after = api.setInputs({[name]: target});
      const changed = [...document.querySelectorAll('[data-mark]')].filter(n => signature(n) !== before.get(n.dataset.mark)).map(n => n.dataset.mark);
      result.push({source: name, value: target, changed, state: after.state});
    }
    api.clearInputs(); return result;
  });
  for (const test of inputTests) {
    const expected = Object.entries(oracle.bindings).filter(([, b]) => b.dependencies.includes(test.source)).map(([id]) => id);
    const unexpected = test.changed.filter(id => !expected.includes(id));
    const views = new Set(test.changed.map(id => oracle.bindings[id].view));
    if (!test.changed.length || unexpected.length) findings.push(`Input ${test.source} does not propagate exclusively through its dependencies.`);
    if (Object.values(oracle.eventViews).some(v => v.length >= 2) && expected.some(id => brief.marks.find(m => m.id===id).kind==='plot') && views.size < 2)
      findings.push(`Input ${test.source} did not change both mechanism and history.`);
  }
  // Exercise the actual preview control, outside the captured stage.
  await page.goto(`http://127.0.0.1:${server.address().port}/preview.html`, {waitUntil: 'networkidle0'});
  const previewTest = await page.evaluate(() => {
    const input = document.querySelector('[data-source]');
    const api = document.getElementById('film').contentWindow.explainer;
    const name = input.dataset.source;
    input.value = input.max; input.dispatchEvent(new Event('input', {bubbles: true}));
    const frame = api.renderAt(1);
    const ok = frame.state[name] === Number(input.max);
    document.getElementById('reset').click();
    return {ok, source: name, restored: api.renderAt(1).state[name] === api.stateAt(1)[name]};
  });
  if (!previewTest.ok || !previewTest.restored) findings.push('Interactive preview control did not update or restore the filmed stage.');
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, {waitUntil: 'networkidle0'});
  await page.evaluate(async seconds => {await document.fonts.ready; window.explainer.seek(seconds);
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));}, brief.output.duration*.65);
  mkdirSync(path.dirname(screenshotPath), {recursive: true}); await page.screenshot({path: screenshotPath});
  findings.push(...consoleErrors);
  mkdirSync(path.dirname(reportPath), {recursive: true});
  writeFileSync(reportPath, JSON.stringify({ok: !findings.length, findings, sampledFrames: checks,
    palette: oracle.palette, inputTests, previewTest, screenshot: screenshotPath}, null, 2));
  console.log(JSON.stringify({ok: !findings.length, report: reportPath, findings: findings.length, sampledFrames: checks}));
} catch (error) {
  mkdirSync(path.dirname(reportPath), {recursive: true});
  writeFileSync(reportPath, JSON.stringify({ok: false, findings: [String(error)]}, null, 2));
  console.error(String(error)); process.exitCode = 2;
} finally {if (browser) await browser.close(); await new Promise<void>(resolve => server.close(() => resolve()));}
