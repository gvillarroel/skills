#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-diagram-defaults/scripts/test-render-queue-browser.ts
// Requires Node.js 24+ and Playwright with Chromium from the existing Slidev
// ECharts fixture's node_modules. No builds, network services, or artifacts.

import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'

const helperPaths = ['slidev-echarts', 'slidev-animejs'].map(skill =>
  new URL(`../../../skills/${skill}/assets/templates/slidev-diagram-style/diagram-style.mjs`, import.meta.url),
)
const [echartsHelper, animejsHelper] = await Promise.all(helperPaths.map(file => readFile(file)))
assert.ok(echartsHelper.equals(animejsHelper), 'The two shipped diagram helpers differ.')
const helperSha256 = createHash('sha256').update(echartsHelper).digest('hex')

const require = createRequire(new URL('../../../skills/slidev-echarts/assets/examples/slidev-echarts/node_modules/playwright/package.json', import.meta.url))
const { chromium } = require('playwright')
const browser = await chromium.launch({ headless: true })
let report: any
try {
  const page = await browser.newPage()
  report = await page.evaluate(async (source: string) => {
    const helper = await import(`data:text/javascript;base64,${btoa(source)}`)
    let active: any
    const events: any[] = []
    // Only the native global-state interleaving is mocked. Font readiness,
    // DOMParser, style mutation, and XML serialization use real Chromium APIs.
    const native = {
      initialize(config: any) {
        active = config
        events.push({ action: 'initialize', secondary: config.themeVariables?.secondaryColor, theme: config.theme })
      },
      mermaidAPI: { getConfig() { return active } },
      async render(_id: string, code: string) {
        await new Promise(resolve => setTimeout(resolve, 10))
        if (code === 'invalid')
          throw new Error('Expected default parse failure')
        const secondary = active.themeVariables.secondaryColor
        events.push({ action: 'render', code, secondary, theme: active.theme })
        return {
          svg: `<svg xmlns="http://www.w3.org/2000/svg" data-code="${code}" data-secondary="${secondary}" data-theme="${active.theme}"><rect fill="${secondary}"/></svg>`,
        }
      },
    }
    const first = helper.createColorsetRenderer(native, () => helper.mermaidColorsetConfig('colorset1'))
    const second = helper.createColorsetRenderer(native, () => helper.mermaidColorsetConfig('colorset2'))
    const output = await Promise.all([
      first('first', { theme: 'dark' }),
      second('second', { theme: 'dark' }),
    ])
    let failure = ''
    try {
      await first('invalid', { theme: 'dark' })
    }
    catch (error) {
      failure = (error as Error).message
    }
    const recovered = await second('recovered', { theme: 'dark' })
    function facts(svg: string) {
      const root = new DOMParser().parseFromString(svg, 'image/svg+xml').documentElement
      return {
        code: root.getAttribute('data-code'),
        secondary: root.getAttribute('data-secondary'),
        theme: root.getAttribute('data-theme'),
        background: root.style.backgroundColor,
      }
    }
    return { results: output.map(facts), failure, recovered: facts(recovered), events }
  }, echartsHelper.toString('utf8'))
}
finally {
  await browser.close()
}

assert.deepEqual(report.results, [
  { code: 'first', secondary: '#000000', theme: 'base', background: 'rgb(255, 255, 255)' },
  { code: 'second', secondary: '#007298', theme: 'base', background: 'rgb(255, 255, 255)' },
])
assert.equal(report.failure, 'Expected default parse failure')
assert.deepEqual(report.recovered, {
  code: 'recovered', secondary: '#007298', theme: 'base', background: 'rgb(255, 255, 255)',
})
assert.deepEqual(report.events.slice(0, 4), [
  { action: 'initialize', secondary: '#000000', theme: 'base' },
  { action: 'render', code: 'first', secondary: '#000000', theme: 'base' },
  { action: 'initialize', secondary: '#007298', theme: 'base' },
  { action: 'render', code: 'second', secondary: '#007298', theme: 'base' },
])
const finalHelpers = await Promise.all(helperPaths.map(file => readFile(file)))
assert.ok(finalHelpers.every(helper => helper.equals(echartsHelper)), 'A shipped helper changed during the browser smoke.')
console.log(JSON.stringify({ passed: true, helperSha256, checks: ['identical shipped helpers', 'concurrent default colorset1/colorset2', 'automatic dark theme coercion', 'native SVG canvas and serialization', 'default parse failure recovery'] }, null, 2))
