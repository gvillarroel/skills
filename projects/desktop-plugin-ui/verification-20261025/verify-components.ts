// Run from the repository root, using existing project dependencies only:
// node projects/desktop-plugin-ui/mcp-probe/node_modules/tsx/dist/cli.mjs projects/desktop-plugin-ui/verification-20261025/verify-components.ts
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');
const require = createRequire(path.resolve(here, '../mcp-probe/package.json'));
const { chromium } = require('playwright');
const runName = process.env.UI_VERIFICATION_RUN || 'run-002';
if (!/^run-\d{3}$/.test(runName)) throw new Error('UI_VERIFICATION_RUN must use run-NNN format');
const output = path.resolve(repo, 'projects/desktop-plugin-ui/artifacts/verification-closure-20261025', runName);
await mkdir(output, { recursive: true });
const sha = (value: Buffer) => createHash('sha256').update(value).digest('hex');
const provenance = JSON.parse(await readFile(path.join(here, 'provenance.json'), 'utf8'));
const paletteText = await readFile(path.join(repo, 'skills/desktop-plugin-ui/assets/palettes/colorset1.yml'), 'utf8');
const allowed = new Set([...paletteText.matchAll(/value:\s*"(#[\da-f]{6})"/gi)].map(item => item[1].toLowerCase()));
function scalarPaths(text: string) {
  const values = new Map<string, string>();
  const stack: Array<{ indent: number; key: string }> = [];
  for (const line of text.split('\n')) {
    const match = /^(\s*)("[^"]+"|[^:#]+):(?:\s*"([^"]*)")?\s*$/.exec(line);
    if (!match) continue;
    const indent = match[1].length, key = match[2].trim().replace(/^"|"$/g, '');
    while (stack.length && stack.at(-1)!.indent >= indent) stack.pop();
    const address = [...stack.map(item => item.key), key].join('.');
    if (match[3] !== undefined) values.set(address, match[3]);
    else stack.push({ indent, key });
  }
  return values;
}
const tokenPaths = scalarPaths(paletteText);
const variants = [
  { number: 1, search: '#search', priority: '#priority', save: '#save', cancel: '#cancel', refresh: '#refresh', status: '#status', export: '#export', failure: '#refresh-failure', clear: '#clear-search', tooltip: '#export-tip' },
  { number: 2, search: '#queue-search', priority: '#priority-select', save: '#save-button', cancel: '#cancel-button', refresh: '#refresh-button', status: '#status-region', export: '#export-button', failure: '#fail-refresh', clear: '#clear-search-button', tooltip: '#export-tooltip' },
  { number: 3, search: '#search', priority: '#priority', save: '#save', cancel: '#cancel', refresh: '#refresh', status: '#status', export: '#export', failure: '#failure', clear: '#clear-search', tooltip: '#export-tip' },
];
const viewports = [{ name: 'desktop', width: 1100, height: 820 }, { name: 'narrow', width: 360, height: 780 }, { name: 'minimum', width: 320, height: 780 }];
const results: any[] = [];
const browser = await chromium.launch({ headless: true, channel: 'msedge', args: ['--disable-background-networking'] });

function ratio(first: string, second: string) {
  const luminance = (value: string) => {
    const components = value.match(/[\da-f]{2}/gi)!.map(part => parseInt(part, 16) / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
    return components[0] * .2126 + components[1] * .7152 + components[2] * .0722;
  };
  const [light, dark] = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (light + .05) / (dark + .05);
}

try {
  for (const variant of variants) {
    const folder = path.join(here, `component-${variant.number}`);
    const source = path.join(folder, 'status-panel.html');
    const metadataPath = path.join(folder, 'component-copy.json');
    const html = await readFile(source, 'utf8');
    const metadata = JSON.parse(await readFile(metadataPath, 'utf8'));
    const original = { html: sha(await readFile(source)), json: sha(await readFile(metadataPath)) };
    const component: any = { component: variant.number, source: path.relative(repo, source).replaceAll('\\', '/'), originalHashes: original, checks: [], viewports: [] };
    const recordStatic = (name: string, passed: boolean, details?: any) => component.checks.push({ name, passed, details });
    recordStatic('all-authored-hex-values-are-exact-CS1', [...html.matchAll(/#[\da-f]{6}\b/gi)].every(item => allowed.has(item[0].toLowerCase())));
    recordStatic('no-authored-alpha-shadow-or-opacity-paint', !/rgba\(|box-shadow\s*:|opacity\s*:/i.test(html));
    recordStatic('all-CSS-source-token-paths-and-values-match', metadata.palette_bindings.tokens.every((item: any) => tokenPaths.get(item.source_token_path) === item.value), metadata.palette_bindings.tokens);
    recordStatic('reported-contrast-is-independently-reproducible', metadata.palette_bindings.contrast_measurements.every((item: any) => Math.abs(ratio(item.foreground, item.background) - item.ratio_unrounded) < 1e-12 && item.ratio_unrounded >= item.minimum));
    if (variant.number === 1) recordStatic('original-contrast-claims-corrected', metadata.styling_contract.contrast_checks.every((item: any) => Math.abs(ratio(item.foreground, item.background) - item.ratio_unrounded) < 1e-12 && item.ratio_approx === `${item.ratio_unrounded.toFixed(6)}:1`));
    recordStatic('source-identifiers-preserved', ['T-104', 'high', 'pending', 'queue_update_priority', 'E_INVALID_PRIORITY'].every(value => JSON.stringify(metadata).includes(value)));
    for (const viewport of viewports) {
      const artifactDir = path.join(output, `component-${variant.number}`, viewport.name);
      await mkdir(artifactDir, { recursive: true });
      const context = await browser.newContext({ viewport, offline: true, locale: 'en-US', acceptDownloads: true });
      const page = await context.newPage();
      page.setDefaultTimeout(5000);
      const pageErrors: string[] = [], network: string[] = [], checks: any[] = [], states: any[] = [];
      page.on('pageerror', (error: Error) => pageErrors.push(error.message));
      await context.route('**/*', async (route: any) => {
        if (/^https?:/i.test(route.request().url())) { network.push(route.request().url()); await route.abort('internetdisconnected'); }
        else await route.continue();
      });
      const check = async (name: string, action: () => Promise<any>) => {
        try { const detail = await action(); checks.push({ name, passed: true, detail }); }
        catch (error) { checks.push({ name, passed: false, error: String(error) }); }
      };
      const waitStatus = async (expression: RegExp) => page.waitForFunction(({ selector, source, flags }: any) => new RegExp(source, flags).test(document.querySelector(selector)?.textContent ?? ''), { selector: variant.status, source: expression.source, flags: expression.flags });
      const capture = async (name: string, screenshot = false) => {
        const visibleText = await page.locator('body').innerText();
        const accessibility = await page.locator('body').ariaSnapshot();
        const layout = await page.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth,
          scrollers: [...document.querySelectorAll('*')].filter(element => {
            const rect = element.getBoundingClientRect(), style = getComputedStyle(element);
            return rect.width && rect.height && ['auto', 'scroll'].includes(style.overflowX) && element.scrollWidth > element.clientWidth + 1;
          }).map(element => ({ tag: element.tagName, className: element.className, width: element.clientWidth, content: element.scrollWidth })) }));
        states.push({ name, visibleText, accessibility, layout, language: await page.locator('html').getAttribute('lang') });
        assert.equal(layout.page <= layout.viewport + 1, true, `${name}: page overflow`);
        assert.equal(layout.scrollers.length, 0, `${name}: nested horizontal scrolling`);
        assert.equal(await page.locator('html').getAttribute('lang'), 'en');
        assert.equal(/Cola de soporte|Buscar solicitudes|Guardar prioridad|Cancelar edición|Explicar selección|Exportar CSV|Prioridad guardada|No puedo acceder|Pendiente/.test(visibleText + accessibility), false, `${name}: legacy display copy leaked`);
        if (screenshot) await page.screenshot({ path: path.join(artifactDir, `${name}.png`), fullPage: true });
      };
      const openDetails = async () => { for (const detail of await page.locator('details').all()) if (await detail.getAttribute('open') === null) { await detail.locator('summary').focus(); await page.keyboard.press('Enter'); } };
      const selectSource = async () => {
        if (variant.number === 1 && viewport.width > 650) await page.getByRole('radio', { name: /^Select T-104:/ }).click();
        else if (variant.number === 1) await page.locator('button[data-ticket-id="T-104"]').click();
        else if (variant.number === 2) await page.getByRole('button', { name: /^Select T-104,/ }).click();
        else await page.locator('button[data-id="T-104"]').click();
      };
      await page.goto(pathToFileURL(source).href);
      await check('default-English-layout', async () => { await capture('default', true); assert.match(await page.locator('body').innerText(), /Support queue/); });
      await check('select-request-and-accessible-responsive-representation', async () => {
        await selectSource();
        assert.equal(await page.locator(variant.priority).inputValue(), 'high');
        if (variant.number === 1 && viewport.width <= 650) {
          assert.equal(await page.getByRole('table').count(), 0);
          const selected = page.getByRole('button', { name: /Select T-104:.*Priority: High.*Status: Pending/ });
          assert.equal(await selected.getAttribute('aria-pressed'), 'true');
          assert.equal(await selected.evaluate((element: Element) => element === document.activeElement), true);
        }
        if (variant.number === 3) { assert.equal(await page.getByRole('listbox').count(), 0); assert.equal(await page.locator('button[role="option"]').count(), 0); assert.equal(await page.getByRole('list', { name: 'Support requests' }).count(), 1); }
        await capture('selected', true);
      });
      await check('refresh-busy-success', async () => {
        await page.locator(variant.refresh).click();
        assert.equal(await page.locator(variant.refresh).isDisabled(), true);
        await capture('refresh-busy');
        await waitStatus(/Queue refreshed/i); await capture('refresh-success');
      });
      await check('invalid-save-and-cancel-preserve-data-focus', async () => {
        await page.locator(variant.priority).selectOption(''); await page.locator(variant.save).click();
        await waitStatus(/valid priority/i);
        assert.equal(await page.locator(variant.priority).evaluate((element: Element) => element === document.activeElement), true);
        await capture('invalid', true);
        await page.locator(variant.priority).selectOption('low'); await page.locator(variant.cancel).click();
        await waitStatus(/cancelled/i); assert.equal(await page.locator(variant.priority).inputValue(), 'high'); await capture('cancelled');
      });
      await check('refresh-failure-retains-last-success-and-retry', async () => {
        await openDetails();
        if (variant.number === 3) await page.locator(variant.failure).click();
        else { await page.locator(variant.failure).check(); await page.locator(variant.refresh).click(); }
        await waitStatus(/failed|could not|Unable/i);
        assert.match(await page.locator('body').innerText(), /T-104/);
        await capture('refresh-error', true);
        await page.locator(variant.refresh).click(); await waitStatus(/Queue refreshed/i); await capture('retry');
      });
      await check('empty-recovery-and-search-focus', async () => {
        await page.locator(variant.search).fill('no-match-verification'); await capture('empty');
        assert.match(await page.locator('body').innerText(), /No matching requests|No requests match/i);
        await page.locator(variant.clear).click();
        assert.equal(await page.locator(variant.search).evaluate((element: Element) => element === document.activeElement), true);
        await capture('empty-recovery');
      });
      await check('save-priority-and-cancel-later-draft', async () => {
        await page.locator(variant.priority).selectOption('low'); await page.locator(variant.save).click();
        await waitStatus(/Priority saved/i); assert.equal(await page.locator(variant.priority).inputValue(), 'low');
        await capture('saved', true);
        await page.locator(variant.priority).selectOption('high'); await page.locator(variant.cancel).click();
        assert.equal(await page.locator(variant.priority).inputValue(), 'low'); await capture('saved-then-cancelled');
      });
      await check('tooltip-accessible-description-focus-Escape-and-geometry', async () => {
        const exporter = page.locator(variant.export), tooltip = page.locator(variant.tooltip);
        assert.equal(await exporter.getAttribute('aria-describedby'), variant.tooltip.slice(1));
        assert.equal(await tooltip.getAttribute('role'), 'tooltip');
        assert.equal(await tooltip.textContent(), 'Exports only the current selection.');
        await exporter.focus();
        assert.equal(await tooltip.evaluate((element: Element) => getComputedStyle(element).visibility), 'visible');
        assert.equal(await tooltip.evaluate((element: Element) => getComputedStyle(element).pointerEvents), 'none');
        const box = await tooltip.boundingBox(); assert.ok(box && box.x >= 0 && box.x + box.width <= viewport.width + 1);
        await capture('tooltip', true);
        await page.keyboard.press('Escape');
        assert.equal(await tooltip.evaluate((element: Element) => getComputedStyle(element).visibility), 'hidden');
        assert.equal(await exporter.evaluate((element: Element) => element === document.activeElement), true);
      });
      await check('pointer-export-then-explain-without-forcing', async () => {
        await page.locator(variant.export).hover();
        const event = page.waitForEvent('download'); await page.locator(variant.export).click();
        const download = await event; const file = path.join(artifactDir, 'selection.csv'); await download.saveAs(file);
        const csv = await readFile(file, 'utf8'); assert.match(csv, /T-104/); assert.match(csv, /pending/); assert.match(csv, /low/);
        await capture('exported');
        await page.locator('#explain').click();
        assert.match(await page.locator(variant.status).innerText(), /T-104/);
        assert.match(await page.locator(variant.status).innerText(), /low/i);
        await capture('explained', true);
        return { csv, forcedClick: false, browserDownloadOnly: true };
      });
      await check('keyboard-explain-and-visible-focus', async () => {
        await page.locator('#explain').focus(); await page.keyboard.press('Enter');
        assert.match(await page.locator(variant.status).innerText(), /T-104/);
        const focus = await page.locator('#explain').evaluate((element: Element) => { const style = getComputedStyle(element); return { outline: style.outlineStyle, width: parseFloat(style.outlineWidth) }; });
        assert.notEqual(focus.outline, 'none'); assert.ok(focus.width >= 2); return focus;
      });
      await check('actual-visible-text-and-essential-boundary-contrast', async () => {
        const entries = await page.evaluate(String.raw`(() => {
          const rgb = (value) => { const values = value.match(/[\d.]+/g).map(Number); return { hex: '#' + values.slice(0, 3).map(channel => channel.toString(16).padStart(2, '0')).join(''), alpha: values.length === 4 ? values[3] : 1 }; };
          const back = (element) => {
            let node = element;
            while (node) { const value = rgb(getComputedStyle(node).backgroundColor); if (value.alpha > .99) return value.hex; node = node.parentElement; }
            return '#ffffff';
          };
          return [...document.querySelectorAll('body *')].filter(element => {
            const bounds = element.getBoundingClientRect(), style = getComputedStyle(element);
            return bounds.width && bounds.height && style.visibility !== 'hidden' && !element.closest('[aria-hidden="true"],script,style') && !element.disabled && element.tagName !== 'OPTION' && [...element.childNodes].some(node => node.nodeType === Node.TEXT_NODE && node.textContent?.trim());
          }).map(element => { const style = getComputedStyle(element), weight = parseInt(style.fontWeight), size = parseFloat(style.fontSize); return { tag: element.tagName, id: element.id, className: element.className, text: [...element.childNodes].filter(node => node.nodeType === Node.TEXT_NODE).map(node => node.textContent).join('').trim(), foreground: rgb(style.color).hex, background: back(element), minimum: size >= 24 || (size >= 18.6667 && weight >= 700) ? 3 : 4.5 }; });
        })()`);
        const measured = entries.map((item: any) => ({ ...item, ratio: ratio(item.foreground, item.background) }));
        const failing = measured.filter((item: any) => item.ratio < item.minimum);
        await writeFile(path.join(artifactDir, 'contrast.json'), JSON.stringify({ measured, failing }, null, 2) + '\n');
        assert.deepEqual(failing, []);
        const border = await page.locator(variant.search).evaluate((element: Element) => { const style = getComputedStyle(element); return { color: style.borderTopColor, background: style.backgroundColor }; });
        const asHex = (value: string) => '#' + value.match(/\d+/g)!.slice(0, 3).map(part => Number(part).toString(16).padStart(2, '0')).join('');
        const boundaryRatio = ratio(asHex(border.color), asHex(border.background)); assert.ok(boundaryRatio >= 3);
        return { visibleTextPairs: measured.length, minimumMeasuredTextRatio: Math.min(...measured.map((item: any) => item.ratio)), boundaryRatio };
      });
      await check('no-page-errors-or-network', async () => { assert.deepEqual(pageErrors, []); assert.deepEqual(network, []); });
      const result = { viewport, checks, states, pageErrors, network, passed: checks.every(item => item.passed) };
      component.viewports.push(result);
      await writeFile(path.join(artifactDir, 'states.json'), JSON.stringify(result, null, 2) + '\n');
      await context.close();
    }
    const sourceRun = provenance.components.find((item: any) => item.component === variant.number);
    const historicalRoot = path.join(repo, `evaluations/runs/${sourceRun.source_run}/workspace/ui`);
    const historicalHashes: Record<string, string> = {};
    for (const [name, expected] of Object.entries(sourceRun.historical_hashes)) {
      historicalHashes[name] = sha(await readFile(path.join(historicalRoot, name)));
      assert.equal(historicalHashes[name], expected);
    }
    recordStatic('historical-artifacts-unchanged', JSON.stringify(historicalHashes) === JSON.stringify(sourceRun.historical_hashes), historicalHashes);
    component.finalHashes = { html: sha(await readFile(source)), json: sha(await readFile(metadataPath)) };
    recordStatic('corrected-sources-unchanged-during-verification', JSON.stringify(component.finalHashes) === JSON.stringify(original));
    component.passed = component.checks.every((item: any) => item.passed) && component.viewports.every((item: any) => item.passed);
    results.push(component);
  }
} finally { await browser.close(); }
const report = { timestampUtc: new Date().toISOString(), browser: { channel: 'msedge', version: browser.version(), playwright: require('playwright/package.json').version },
  scope: 'Corrected local browser copies and independent project validation; no assistant host, account, backend or representative-user test.',
  hostAcceptanceVerified: false, representativeUserTestingPerformed: false, results, passed: results.every(item => item.passed) };
await writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, passed: report.passed, components: results.map(item => ({ number: item.component, staticFailures: item.checks.filter((check: any) => !check.passed), viewports: item.viewports.map((view: any) => ({ name: view.viewport.name, states: view.states.length, failed: view.checks.filter((check: any) => !check.passed) })) })) }, null, 2));
process.exitCode = report.passed ? 0 : 1;
