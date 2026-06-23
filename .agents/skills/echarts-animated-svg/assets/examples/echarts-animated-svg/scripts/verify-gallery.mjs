import { mkdir } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { chromium } from 'playwright'

const __dirname = dirname(fileURLToPath(import.meta.url))
const exampleRoot = resolve(__dirname, '..')
const repoRoot = resolve(exampleRoot, '..', '..', '..', '..')
const indexPath = resolve(exampleRoot, 'index.html')
const screenshotPath = resolve(repoRoot, 'output', 'echarts-animated-svg', 'gallery.png')

await mkdir(dirname(screenshotPath), { recursive: true })

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 }, deviceScaleFactor: 1 })
const consoleErrors = []
const pageErrors = []

page.on('console', (message) => {
  if (['error', 'warning'].includes(message.type()))
    consoleErrors.push(`${message.type()}: ${message.text()}`)
})
page.on('pageerror', (error) => pageErrors.push(error.message))

await page.goto(pathToFileURL(indexPath).href, { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.chart-card svg')

const initial = await page.evaluate(() => {
  const cards = [...document.querySelectorAll('.chart-card')]
  const expectedCards = Number(document.querySelector('.page-shell')?.dataset.expectedCards || 0)
  const coreChartCount = Number(document.querySelector('.page-shell')?.dataset.coreChartCount || 0)
  const extraExampleCount = Number(document.querySelector('.page-shell')?.dataset.extraExampleCount || 0)
  return {
    expectedCards,
    coreChartCount,
    extraExampleCount,
    cards: cards.length,
    svgs: document.querySelectorAll('.chart-card svg').length,
    fontFamily: getComputedStyle(document.documentElement).fontFamily,
    replayIconCount: document.querySelectorAll('.material-symbols-rounded').length,
    oldPaletteHits: [...document.documentElement.outerHTML.matchAll(/#(?:2563eb|0f766e|f59e0b|be123c|7c3aed|64748b|475569|0f172a|334155|e2e8f0|dbeafe|f8fafc)/gi)].length,
    missingMarks: cards
      .filter((card) => !card.querySelector('svg .easv-mark'))
      .map((card) => card.dataset.chartType),
    smallSvgs: cards
      .filter((card) => {
        const box = card.querySelector('svg')?.getBoundingClientRect()
        return !box || box.width < 200 || box.height < 140
      })
      .map((card) => card.dataset.chartType),
  }
})

if (initial.coreChartCount < 23)
  throw new Error(`Expected at least 23 core chart profiles, saw ${initial.coreChartCount}.`)
if (initial.extraExampleCount < 20)
  throw new Error(`Expected at least 20 extra animated SVG examples, saw ${initial.extraExampleCount}.`)
if (initial.cards !== initial.expectedCards || initial.svgs !== initial.expectedCards)
  throw new Error(`Expected ${initial.expectedCards} chart cards and SVGs, saw ${initial.cards} cards and ${initial.svgs} SVGs.`)
if (!initial.fontFamily.includes('Open Sans'))
  throw new Error(`Expected Open Sans as the primary page font, saw: ${initial.fontFamily}`)
if (initial.replayIconCount < initial.expectedCards + 1)
  throw new Error(`Expected Material Symbols replay icons for every replay control, saw ${initial.replayIconCount}.`)
if (initial.oldPaletteHits)
  throw new Error(`Found ${initial.oldPaletteHits} old palette token(s) in the generated page.`)
if (initial.missingMarks.length)
  throw new Error(`Charts missing animated marks: ${initial.missingMarks.join(', ')}`)
if (initial.smallSvgs.length)
  throw new Error(`Charts with too-small SVG bounds: ${initial.smallSvgs.join(', ')}`)

await page.click('#replay-all')
await page.waitForTimeout(80)

const replay = await page.evaluate(() => {
  const cards = [...document.querySelectorAll('.chart-card')]
  const animated = cards.filter((card) => {
    const mark = card.querySelector('svg .easv-mark')
    return mark && getComputedStyle(mark).animationName !== 'none'
  })
  return {
    replayed: cards.filter((card) => Number(card.dataset.replayCount || 0) >= 1).length,
    animated: animated.length,
  }
})

if (replay.replayed !== initial.expectedCards)
  throw new Error(`Replay-all did not mark every card as replayed: ${replay.replayed}/${initial.expectedCards}.`)
if (replay.animated < Math.max(20, initial.expectedCards - 4))
  throw new Error(`Expected most cards to have active animation immediately after replay, saw ${replay.animated}.`)

await page.waitForTimeout(1100)
await page.screenshot({ path: screenshotPath, fullPage: true })

await browser.close()

if (consoleErrors.length || pageErrors.length) {
  throw new Error([
    'Browser reported issues:',
    ...consoleErrors,
    ...pageErrors.map((message) => `pageerror: ${message}`),
  ].join('\n'))
}

console.log(JSON.stringify({ ok: true, cards: initial.cards, svgs: initial.svgs, screenshot: screenshotPath }, null, 2))
