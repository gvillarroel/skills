const { test, expect } = require('@playwright/test');

const ids = [
  'procedural-svg-alpha-persistence',
  'procedural-svg-join-tree',
  'procedural-svg-optimal-transport',
  'procedural-svg-fast-marching-front',
  'procedural-svg-physarum-network',
  'procedural-svg-stable-fluid',
];

const invariantCounts = new Map([
  ['procedural-svg-alpha-persistence', '4/4'],
  ['procedural-svg-join-tree', '4/4'],
  ['procedural-svg-optimal-transport', '5/5'],
  ['procedural-svg-fast-marching-front', '4/4'],
  ['procedural-svg-physarum-network', '4/4'],
  ['procedural-svg-stable-fluid', '5/5'],
]);

const rootUrl = 'http://127.0.0.1:4173/projects/procedural-svg-animation-mastery/artifacts/svgs';
const screenshotRoot = 'projects/procedural-svg-animation-mastery/artifacts/screenshots';

for (const id of ids) {
  test(`${id} closes, changes, and exposes a static fallback`, async ({ page }) => {
    const consoleErrors = [];
    page.on('console', message => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });
    page.on('pageerror', error => consoleErrors.push(error.message));

    await page.goto(`${rootUrl}/${id}.full.svg`, { waitUntil: 'load' });
    const root = page.locator('svg');
    await expect(root).toHaveAttribute('data-invariants-status', invariantCounts.get(id));
    await expect(root).toHaveAttribute('data-loop-contract', 'palindromic-snapshots');
    await expect(page.locator('[data-motion-layer="animated"] > * [data-stratum], [data-motion-layer="animated"] [data-stratum]')).toHaveCount(6);
    await expect(page.locator('[data-motion-layer="reduced"] > * [data-stratum], [data-motion-layer="reduced"] [data-stratum]')).toHaveCount(6);

    if (id === 'procedural-svg-optimal-transport') {
      const evidence = await page.evaluate(() => {
        const animated = document.querySelector('[data-motion-layer="animated"]');
        const parameters = JSON.parse(document.documentElement.dataset.parameterValues);
        const values = selector => [...animated.querySelectorAll(selector)]
          .map(node => Number(node.getAttribute(selector.includes('kernel')
            ? 'data-kernel-value'
            : selector.includes('scaling')
              ? 'data-scaling-value'
              : 'data-plan-mass')));
        return {
          siteCount: parameters.site_count,
          frameCount: parameters.frame_count,
          kernelValues: values('[data-kernel-value]'),
          scalingValues: values('[data-scaling-value]'),
          planMasses: values('[data-plan-mass]'),
          movingEntries: animated.querySelectorAll('[data-plan-entry]').length,
        };
      });
      expect(evidence.kernelValues).toHaveLength(evidence.siteCount ** 2);
      expect(evidence.planMasses).toHaveLength(evidence.siteCount ** 2);
      expect(evidence.scalingValues).toHaveLength(2 * evidence.siteCount * evidence.frameCount);
      expect(evidence.movingEntries).toBe(evidence.siteCount ** 2 * evidence.frameCount);
      expect(evidence.kernelValues.every(value => Number.isFinite(value) && value >= 0)).toBeTruthy();
      expect(evidence.scalingValues.every(value => Number.isFinite(value) && value > 0)).toBeTruthy();
      expect(evidence.planMasses.every(value => Number.isFinite(value) && value >= 0)).toBeTruthy();
    }

    if (id === 'procedural-svg-fast-marching-front') {
      const trialAudit = await page.evaluate(() => [...document.querySelectorAll(
        '[data-motion-layer="animated"] [data-stratum="accepted-front"] [data-trial-cell-ids]',
      )].map(node => {
        const ids = node.dataset.trialCellIds ? node.dataset.trialCellIds.split(',') : [];
        const times = node.dataset.trialArrivalTimes ? node.dataset.trialArrivalTimes.split(',') : [];
        return {
          count: Number(node.dataset.trialCount),
          ids,
          times: times.map(Number),
          heap: Number(node.dataset.trialHeapEntryCount),
          stale: Number(node.dataset.trialStaleEntryCount),
        };
      }));
      expect(trialAudit).toHaveLength(7);
      expect(trialAudit.some(frame => frame.count > 0)).toBeTruthy();
      expect(trialAudit.every(frame => (
        frame.ids.length === frame.count
        && frame.times.length === frame.count
        && frame.times.every(Number.isFinite)
        && frame.heap === frame.count + frame.stale
      ))).toBeTruthy();
    }

    if (id === 'procedural-svg-physarum-network') {
      expect(await page.locator(
        '[data-motion-layer="animated"] [data-stratum="network"] [data-network-root="true"]',
      ).count()).toBeGreaterThan(0);
    }

    if (id === 'procedural-svg-stable-fluid') {
      for (const stratum of ['velocity', 'projection', 'dye', 'streamlines']) {
        await expect(page.locator(
          `[data-motion-layer="animated"] [data-stratum="${stratum}"] [data-frame-index]`,
        )).toHaveCount(7);
      }
    }

    const seek = async time => page.evaluate(async value => {
      document.documentElement.pauseAnimations();
      document.documentElement.setCurrentTime(value);
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return [...document.querySelectorAll('[data-motion-layer="animated"] [data-frame-index]')]
        .map(group => [group.getAttribute('data-frame-index'), getComputedStyle(group).opacity]);
    }, time);
    const initialState = await seek(0);
    const initial = await page.screenshot({ path: `${screenshotRoot}/${id}-initial.png` });
    await seek(3);
    const middle = await page.screenshot({ path: `${screenshotRoot}/${id}-middle.png` });
    const seamState = await seek(6);
    await page.screenshot({ path: `${screenshotRoot}/${id}-seam.png` });
    expect(middle.equals(initial), 'middle frame should visibly differ').toBeFalsy();
    expect(seamState, 'master-loop endpoint must activate the same snapshots').toEqual(initialState);

    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.reload({ waitUntil: 'load' });
    await expect(page.locator('[data-motion-layer="animated"]')).toHaveCSS('display', 'none');
    await expect(page.locator('[data-motion-layer="reduced"]')).not.toHaveCSS('display', 'none');
    await page.screenshot({ path: `${screenshotRoot}/${id}-media-reduced.png` });
    expect(consoleErrors).toEqual([]);
  });

  test(`${id} direct reduced artifact is static`, async ({ page }) => {
    await page.goto(`${rootUrl}/${id}.reduced.svg`, { waitUntil: 'load' });
    await expect(page.locator('svg')).toHaveAttribute('data-motion', 'reduced');
    await expect(page.locator('svg')).toHaveAttribute('data-loop', 'false');
    await expect(page.locator('[data-stratum]')).toHaveCount(6);
    await expect(page.locator('animate, animateMotion, animateTransform, set')).toHaveCount(0);
  });
}
