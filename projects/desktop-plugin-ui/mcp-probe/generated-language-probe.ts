// Run from this directory: npx --no-install tsx generated-language-probe.ts
// Uses the already installed playwright/tsx dependencies in package.json.
// Reads immutable generated previews; writes browser evidence only to project artifacts.
import { chromium, type Page } from 'playwright';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const output = path.join(repo, 'projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser');
await mkdir(output, { recursive: true });
const digest = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
const variants = [
  { run: 1, search: '#search', priority: '#priority', save: '#save', cancel: '#cancel', refresh: '#refresh', status: '#status', export: '#export', failure: '#refresh-failure', clear: '#clear-search', select: 'input[name="ticket"][value="T-104"]', tooltip: null },
  { run: 2, search: '#queue-search', priority: '#priority-select', save: '#save-button', cancel: '#cancel-button', refresh: '#refresh-button', status: '#status-region', export: '#export-button', failure: '#fail-refresh', clear: '#clear-search-button', select: 'button[aria-label^="Select T-104,"]', tooltip: '#export-tooltip' },
  { run: 3, search: '#search', priority: '#priority', save: '#save', cancel: '#cancel', refresh: '#refresh', status: '#status', export: '#export', failure: '#failure', clear: '#clear-search', select: 'button[data-id="T-104"]', tooltip: '#export-tip' },
];
// Quoted Spanish strings are source/test fixtures for leakage detection, never authored UI copy.
const legacy = ['Cola de soporte', 'Buscar solicitudes', 'Escribe un ID o un asunto', 'Prioridad', 'Guardar prioridad', 'Cancelar edición', 'Actualizar cola', 'Explicar selección', 'Exportar CSV', 'Actualizando la cola', 'Selecciona una prioridad válida', 'No se pudo actualizar', 'Edición cancelada', 'No hay solicitudes', 'Prioridad guardada', 'Exporta únicamente', 'Panel de solicitudes', 'No puedo acceder a mi cuenta', 'Alta', 'Pendiente'];
const viewports = [{ name: 'desktop', width: 1100, height: 820 }, { name: 'narrow', width: 360, height: 780 }];
const results: any[] = [];
const browser = await chromium.launch({ headless: true, channel: 'msedge', args: ['--disable-background-networking'] });
const browserVersion = browser.version();

async function ensureDetails(page: Page) {
  for (const detail of await page.locator('details').all()) {
    if (!await detail.getAttribute('open').then(value => value !== null)) {
      await detail.locator('summary').focus();
      await page.keyboard.press('Enter');
    }
  }
}

try {
  for (const variant of variants) {
    const runId = `20261025-desktop-ui-english-components-v1-luna-${variant.run}`;
    const source = path.join(repo, 'evaluations/runs', runId, 'workspace/ui/status-panel.html');
    const metadata = path.join(path.dirname(source), 'component-copy.json');
    const original = { html: digest(await readFile(source)), json: digest(await readFile(metadata)) };
    const metadataText = await readFile(metadata, 'utf8');
    const runResult: any = {
      runId, source: path.relative(repo, source).replaceAll('\\', '/'), originalHashes: original,
      metadataIdentifiers: Object.fromEntries(['T-104', 'high', 'pending', 'queue_update_priority', 'E_INVALID_PRIORITY'].map(value => [value, metadataText.includes(value)])),
      viewports: [], limits: [],
    };

    for (const viewport of viewports) {
      const artifactDir = path.join(output, `run-${variant.run}`, viewport.name);
      await mkdir(artifactDir, { recursive: true });
      const context = await browser.newContext({ viewport, offline: true, locale: 'en-US', acceptDownloads: true });
      const page = await context.newPage();
      const errors: string[] = [], blockedNetwork: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await context.route('**/*', async route => {
        if (/^https?:/i.test(route.request().url())) {
          blockedNetwork.push(route.request().url());
          await route.abort('internetdisconnected');
        } else await route.continue();
      });
      const captures: any[] = [], operations: any[] = [];
      const capture = async (name: string, expected: RegExp, notes?: string) => {
        const visibleText = await page.locator('body').innerText();
        const accessibleTree = await page.locator('body').ariaSnapshot();
        const attributes = await page.locator('[aria-label], [aria-description], [aria-describedby], [title], [placeholder], option').evaluateAll(elements => elements.map(element => ({
          tag: element.tagName.toLowerCase(), id: element.id, text: element.tagName === 'OPTION' ? element.textContent : null,
          ariaLabel: element.getAttribute('aria-label'), ariaDescription: element.getAttribute('aria-description'),
          describedBy: element.getAttribute('aria-describedby'), title: element.getAttribute('title'), placeholder: element.getAttribute('placeholder'),
          value: (element as HTMLOptionElement).value ?? null,
        })));
        const geometry = await page.evaluate(() => ({
          viewportWidth: innerWidth, documentWidth: document.documentElement.scrollWidth,
          overflowContainers: [...document.querySelectorAll('body *')].filter(element => {
            const style = getComputedStyle(element);
            return ['auto', 'scroll'].includes(style.overflowX) && element.scrollWidth > element.clientWidth + 2;
          }).map(element => ({ tag: element.tagName.toLowerCase(), className: element.className, width: element.clientWidth, scrollWidth: element.scrollWidth })),
        }));
        const combined = `${visibleText}\n${accessibleTree}\n${JSON.stringify(attributes)}`;
        const legacyMatches = legacy.filter(text => new RegExp(`(?:^|[^A-Za-z])${text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:$|[^A-Za-z])`, 'i').test(combined));
        const record = { name, expectedEnglish: expected.source, expectedEnglishPresent: expected.test(visibleText), legacyMatches,
          documentLanguage: await page.locator('html').getAttribute('lang'), visibleText, accessibleTree, attributes, geometry, notes,
          screenshot: path.relative(output, path.join(artifactDir, `${name}.png`)).replaceAll('\\', '/') };
        await page.screenshot({ path: path.join(artifactDir, `${name}.png`), fullPage: true });
        captures.push(record);
        return record;
      };
      const operation = async (name: string, action: () => Promise<void>) => {
        try { await action(); operations.push({ name, passed: true }); }
        catch (error) { operations.push({ name, passed: false, error: String(error) }); }
      };
      const waitStatus = async (expression: RegExp) => {
        await page.waitForFunction(({ selector, source, flags }) => new RegExp(source, flags).test(document.querySelector(selector)?.textContent ?? ''), { selector: variant.status, source: expression.source, flags: expression.flags });
      };
      await page.goto(pathToFileURL(source).href);
      await capture('default', /Support queue/);
      await operation('select-source-ticket', async () => {
        await page.locator(variant.select).click();
        await capture('selected', /T-104/);
      });
      await operation('refresh-busy-success', async () => {
        await page.locator(variant.refresh).click();
        await capture('busy', /Refreshing|Updating/i);
        await waitStatus(/Queue refreshed/i);
        await capture('refresh-success', /Queue refreshed/i);
      });
      await operation('invalid-priority', async () => {
        await page.locator(variant.priority).selectOption('');
        await page.locator(variant.save).click();
        await capture('invalid', /valid priority/i);
      });
      await operation('cancel-staged-edit', async () => {
        const prior = await page.locator(variant.priority).inputValue();
        await page.locator(variant.priority).selectOption('low');
        await page.locator(variant.cancel).click();
        const result = await capture('cancelled', /cancelled/i);
        Object.assign(result, { priorInvalidDraft: prior, afterCancelValue: await page.locator(variant.priority).inputValue(), restoredOriginalHigh: await page.locator(variant.priority).inputValue() === 'high' });
      });
      await operation('refresh-error-retains-data', async () => {
        await ensureDetails(page);
        if (variant.run === 3) await page.locator(variant.failure).click();
        else { await page.locator(variant.failure).check(); await page.locator(variant.refresh).click(); }
        await waitStatus(/failed|could not|Unable/i);
        const result = await capture('refresh-error', /failed|could not|Unable/i);
        Object.assign(result, { retainedSourceTicket: /T-104/.test(result.visibleText) });
      });
      await operation('retry-after-error', async () => {
        await page.locator(variant.refresh).click();
        await waitStatus(/Queue refreshed/i);
        await capture('retry-success', /Queue refreshed/i);
      });
      await operation('empty-and-recovery', async () => {
        await page.locator(variant.search).fill('no-match-browser-audit');
        await capture('empty', /No matching requests|No requests match/i);
        await page.locator(variant.clear).click();
        const result = await capture('empty-recovery', /T-104/);
        Object.assign(result, { focusReturnedToSearch: await page.locator(variant.search).evaluate(element => element === document.activeElement) });
      });
      await operation('save-success', async () => {
        await page.locator(variant.priority).selectOption('low');
        await page.locator(variant.save).click();
        if (variant.run !== 3) await capture('save-busy', /Saving priority|Updating/i);
        await waitStatus(/Priority saved/i);
        await capture('save-success', /Priority saved/i);
      });
      await operation('help-and-keyboard-disclosure', async () => {
        await ensureDetails(page);
        const result = await capture('help-fallback', /Search|Text fallback|Text-only fallback/i);
        Object.assign(result, { expandedDetails: await page.locator('details[open]').count() });
      });
      await operation('tooltip-hover-and-focus', async () => {
        await page.locator(variant.export).hover();
        if (variant.tooltip) await page.waitForFunction(selector => Number(getComputedStyle(document.querySelector(selector)!).opacity) > 0.9, variant.tooltip);
        await page.locator(variant.export).focus();
        const result = await capture('tooltip', /Export CSV/);
        const tooltipCopy = variant.tooltip ? await page.locator(variant.tooltip).innerText() : await page.locator(variant.export).getAttribute('title');
        Object.assign(result, { tooltipCopy, tooltipEnglish: tooltipCopy === 'Exports only the current selection.',
          tooltipKind: variant.tooltip ? 'authored CSS tooltip, hovered and keyboard focused' : 'native title attribute; headless native popup paint unverified',
          describedBy: await page.locator(variant.export).getAttribute('aria-describedby') });
      });
      await operation('export-local-csv', async () => {
        const downloadEvent = page.waitForEvent('download', { timeout: 5000 });
        await page.locator(variant.export).click();
        const download = await downloadEvent;
        const destination = path.join(artifactDir, 'selection.csv');
        await download.saveAs(destination);
        const csv = await readFile(destination, 'utf8');
        const result = await capture('export-success', /CSV prepared/i);
        Object.assign(result, { csv, sourceTicketPreserved: csv.includes('T-104'), enumCodePreserved: /pending/.test(csv), localBrowserDownloadOnly: true });
      });
      if (await page.locator('#explain').count()) await operation('explain-selection', async () => {
        await page.locator('#explain').click();
        await capture('explain-selection', /T-104/);
      });
      else operations.push({ name: 'explain-selection', passed: false, limitation: 'No Explain selection control exists in this generated component.' });
      const finalCopy = captures.map(item => `${item.visibleText}\n${item.accessibleTree}`).join('\n');
      const viewportResult = { viewport, operations, captures, pageErrors: errors, blockedNetwork,
        documentLanguagePass: captures.every(item => item.documentLanguage === 'en'),
        legacyCopyAbsent: captures.every(item => item.legacyMatches.length === 0),
        expectedEnglishStateCopyPass: captures.every(item => item.expectedEnglishPresent),
        sourceTicketVisibleAndAccessible: captures.some(item => /T-104/.test(item.visibleText) && /T-104/.test(item.accessibleTree)),
        englishSemanticAnchors: Object.fromEntries(['Support queue', 'Search requests', 'Priority', 'Save priority', 'Cancel edit', 'Refresh queue', 'Export CSV'].map(copy => [copy, finalCopy.includes(copy)])),
      };
      runResult.viewports.push(viewportResult);
      await writeFile(path.join(artifactDir, 'states.json'), JSON.stringify(viewportResult, null, 2) + '\n');
      await context.close();
    }
    runResult.finalHashes = { html: digest(await readFile(source)), json: digest(await readFile(metadata)) };
    runResult.generatedSourcesUnchanged = JSON.stringify(runResult.originalHashes) === JSON.stringify(runResult.finalHashes);
    runResult.languageChecksPass = runResult.viewports.every((item: any) => item.documentLanguagePass && item.legacyCopyAbsent && item.expectedEnglishStateCopyPass && item.sourceTicketVisibleAndAccessible && Object.values(item.englishSemanticAnchors).every(Boolean));
    runResult.hostAcceptanceVerified = false;
    runResult.userTestingPerformed = false;
    results.push(runResult);
  }
} finally { await browser.close(); }

const report = { timestampUtc: new Date().toISOString(), scope: 'Local generated HTML browser previews with synthetic state changes; not installed assistant hosts or representative-user testing.',
  browser: { channel: 'msedge', version: browserVersion, playwright: '1.64.1' }, node: process.version,
  networkPolicy: 'New offline contexts; all HTTP(S) routes aborted. No server, provider, account, assistant application, or installation used.',
  results, hostAcceptanceVerified: false, userTestingPerformed: false };
await writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, browser: report.browser, runs: results.map(item => ({ runId: item.runId, languageChecksPass: item.languageChecksPass, generatedSourcesUnchanged: item.generatedSourcesUnchanged,
  viewports: item.viewports.map((entry: any) => ({ name: entry.viewport.name, stateCount: entry.captures.length, failedOperations: entry.operations.filter((operation: any) => !operation.passed), pageErrors: entry.pageErrors, blockedNetwork: entry.blockedNetwork })) })) }, null, 2));
