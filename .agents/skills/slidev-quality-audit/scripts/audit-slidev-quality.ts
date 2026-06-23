#!/usr/bin/env -S npx tsx
// Run: npx tsx ./.agents/skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck ./examples/slidev-echarts --out ./projects/slidev-quality-audits/artifacts/reports/slidev-echarts
// Dependencies: tsx, playwright in the target Slidev project, @slidev/cli in the target Slidev project.

import { spawn, spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync } from 'node:fs'
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { createServer } from 'node:net'
import { basename, isAbsolute, relative, resolve } from 'node:path'

type Severity = 'error' | 'warning' | 'info'
type WaitUntil = 'load' | 'domcontentloaded' | 'networkidle'

type Options = {
  deckDir: string
  slidesFile: string
  outDir: string
  name: string
  port: number
  width: number
  height: number
  dwellMs: number
  clickDwellMs: number
  timeoutMs: number
  waitUntil: WaitUntil
  channel: string | undefined
  headed: boolean
  strict: boolean
  range: string | undefined
  maxClicks: number | undefined
  defaultClicksForDynamic: number
  minFontSize: number
  minContrast: number
  largeTextContrast: number
  overflowTolerance: number
  safeMargin: number
  overlapRatio: number
  maxWords: number
  maxTextBlocks: number
  screenshots: 'issues' | 'all' | 'none'
  ignoreSelector: string
  allowOverflowSelector: string
  allowHiddenSelector: string
}

type SlidePlan = {
  no: number
  title: string
  clicks: number
  dynamicClicks: boolean
}

type Rect = {
  left: number
  top: number
  right: number
  bottom: number
  width: number
  height: number
}

type BrowserFinding = {
  ruleId: string
  severity: Severity
  target: string
  message: string
  critique: string
  improvement: string
  rect?: Rect
}

type Finding = BrowserFinding & {
  slide: number
  click: number
  title: string
  screenshot?: string
}

type StateInspection = {
  visualHash: string
  metrics: Record<string, number | boolean | string>
  findings: BrowserFinding[]
  hiddenTextFindings: BrowserFinding[]
}

const invocationCwd = process.cwd()

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error))
  process.exit(1)
})

async function main() {
  const options = normalizeOptions(parseArgs(process.argv.slice(2)))
  const screenshotsDir = resolve(options.outDir, 'screenshots')
  const jsonPath = resolve(options.outDir, 'quality-report.json')
  const markdownPath = resolve(options.outDir, 'quality-report.md')

  await mkdir(options.outDir, { recursive: true })
  await rm(screenshotsDir, { recursive: true, force: true })
  if (options.screenshots !== 'none')
    await mkdir(screenshotsDir, { recursive: true })

  const slides = applyRange(await parseSlides(options.slidesFile, options.defaultClicksForDynamic), options.range)
  if (!slides.length)
    throw new Error('No slides selected for quality audit.')

  const playwright = loadPlaywright(options.deckDir)
  options.port = await findAvailablePort(options.port)
  const baseUrl = `http://localhost:${options.port}`

  let server: ChildProcess | undefined
  let browser: any
  let context: any
  let page: any

  const consoleIssues: string[] = []
  const pageErrors: string[] = []
  const states: any[] = []
  const findings: Finding[] = []

  try {
    server = startSlidevServer(options)
    await waitForServer(baseUrl, options.timeoutMs, server)

    browser = await launchBrowser(playwright.chromium, options)
    context = await browser.newContext({
      viewport: { width: options.width, height: options.height },
      deviceScaleFactor: 1,
    })
    page = await context.newPage()
    await page.addInitScript(() => {
      ;(globalThis as any).__name = (value: any) => value
    })

    page.on('console', (message: any) => {
      if (message.type() === 'error' && !isIgnoredRuntimeIssue(message.text()))
        consoleIssues.push(message.text())
    })
    page.on('pageerror', (error: Error) => {
      if (!isIgnoredRuntimeIssue(error.message))
        pageErrors.push(error.message)
    })

    for (const slide of slides)
      await auditSlide(page, baseUrl, slide, options, screenshotsDir, states, findings)
  }
  finally {
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    stopServer(server)
  }

  for (const issue of consoleIssues)
    findings.push(runtimeFinding('browser-console-error', issue))
  for (const error of pageErrors)
    findings.push(runtimeFinding('page-error', error))

  const report = {
    generatedAt: new Date().toISOString(),
    deck: relativeToCwd(options.deckDir),
    slides: relativeToCwd(options.slidesFile),
    baseUrl,
    viewport: { width: options.width, height: options.height },
    thresholds: {
      minFontSize: options.minFontSize,
      minContrast: options.minContrast,
      largeTextContrast: options.largeTextContrast,
      overflowTolerance: options.overflowTolerance,
      safeMargin: options.safeMargin,
      overlapRatio: options.overlapRatio,
      maxWords: options.maxWords,
      maxTextBlocks: options.maxTextBlocks,
    },
    slideCount: slides.length,
    stateCount: states.length,
    findingCount: findings.length,
    severityCounts: countBy(findings, (finding) => finding.severity),
    ruleCounts: countBy(findings, (finding) => finding.ruleId),
    findings,
    states,
  }

  await writeFile(jsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8')
  await writeFile(markdownPath, renderMarkdown(report), 'utf8')

  console.log(`Audited ${report.slideCount} slide(s) and ${report.stateCount} visual state(s).`)
  console.log(`Findings: ${report.findingCount} (${formatSeverityCounts(report.severityCounts)})`)
  console.log(`Markdown report: ${markdownPath}`)
  console.log(`JSON report: ${jsonPath}`)

  if (options.strict && findings.some((finding) => finding.severity === 'error'))
    process.exitCode = 1
}

async function auditSlide(
  page: any,
  baseUrl: string,
  slide: SlidePlan,
  options: Options,
  screenshotsDir: string,
  states: any[],
  findings: Finding[],
) {
  const clicksToRun = Math.min(slide.clicks, options.maxClicks ?? slide.clicks)
  const stateHashes: string[] = []
  const firstFindingIndex = findings.length

  await gotoSlide(page, baseUrl, slide, options)

  for (let click = 0; click <= clicksToRun; click++) {
    if (click > 0) {
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(options.clickDwellMs)
    }
    else {
      await page.waitForTimeout(options.dwellMs)
    }

    const inspection = await inspectState(page, options)
    const isFinalClickState = click === slide.clicks
    const browserFindings = [
      ...inspection.findings,
      ...(isFinalClickState ? inspection.hiddenTextFindings : []),
    ]
    stateHashes.push(inspection.visualHash)

    let screenshot: string | undefined
    if (options.screenshots === 'all' || (options.screenshots === 'issues' && browserFindings.length)) {
      const screenshotPath = resolve(
        screenshotsDir,
        `slide-${String(slide.no).padStart(3, '0')}-click-${String(click).padStart(2, '0')}.png`,
      )
      await page.screenshot({ path: screenshotPath, fullPage: false })
      screenshot = relativeToCwd(screenshotPath)
    }

    for (const finding of browserFindings)
      findings.push({ ...finding, slide: slide.no, click, title: slide.title, screenshot })

    states.push({
      slide: slide.no,
      click,
      title: slide.title,
      visualHash: inspection.visualHash,
      screenshot,
      metrics: inspection.metrics,
      findingCount: browserFindings.length,
    })
  }

  if (clicksToRun > 0 && new Set(stateHashes).size === 1) {
    findings.push({
      ruleId: 'unchanged-click-state',
      severity: 'warning',
      slide: slide.no,
      click: clicksToRun,
      title: slide.title,
      target: 'slide',
      message: `Slide has ${clicksToRun} detected click state(s), but the visual signature did not change.`,
      critique: 'Click instructions imply progressive disclosure, but the rendered slide appears unchanged.',
      improvement: 'Bind the visual state to `$clicks`, fix the `<v-clicks>` structure, or remove click steps that do not change what the audience sees.',
    })
  }

  if (findings.length > firstFindingIndex)
    console.log(`Slide ${slide.no}: ${findings.length - firstFindingIndex} finding(s)`)
}

function runtimeFinding(ruleId: 'browser-console-error' | 'page-error', message: string): Finding {
  return {
    ruleId,
    severity: 'error',
    slide: 0,
    click: 0,
    title: 'Browser runtime',
    target: ruleId === 'browser-console-error' ? 'console' : 'page',
    message,
    critique: ruleId === 'browser-console-error'
      ? 'The deck emitted a browser console error during automated traversal.'
      : 'The deck threw an uncaught browser error during automated traversal.',
    improvement: ruleId === 'browser-console-error'
      ? 'Fix the runtime error before treating the deck as visually validated.'
      : 'Fix the exception and rerun the audit so visual checks are trustworthy.',
  }
}

function parseArgs(argv: string[]) {
  const parsed: Record<string, string | boolean> = {}

  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index]
    const next = argv[index + 1]

    if (arg === '--help' || arg === '-h') {
      printHelp()
      process.exit(0)
    }
    else if (arg === '--deck') {
      parsed.deck = requireValue(arg, next)
      index++
    }
    else if (arg === '--slides') {
      parsed.slides = requireValue(arg, next)
      index++
    }
    else if (arg === '--out') {
      parsed.out = requireValue(arg, next)
      index++
    }
    else if (arg === '--name') {
      parsed.name = requireValue(arg, next)
      index++
    }
    else if (arg === '--port') {
      parsed.port = requireValue(arg, next)
      index++
    }
    else if (arg === '--width') {
      parsed.width = requireValue(arg, next)
      index++
    }
    else if (arg === '--height') {
      parsed.height = requireValue(arg, next)
      index++
    }
    else if (arg === '--dwell') {
      parsed.dwell = requireValue(arg, next)
      index++
    }
    else if (arg === '--click-dwell') {
      parsed.clickDwell = requireValue(arg, next)
      index++
    }
    else if (arg === '--timeout') {
      parsed.timeout = requireValue(arg, next)
      index++
    }
    else if (arg === '--wait-until') {
      parsed.waitUntil = requireValue(arg, next)
      index++
    }
    else if (arg === '--channel') {
      parsed.channel = requireValue(arg, next)
      index++
    }
    else if (arg === '--range') {
      parsed.range = requireValue(arg, next)
      index++
    }
    else if (arg === '--max-clicks') {
      parsed.maxClicks = requireValue(arg, next)
      index++
    }
    else if (arg === '--default-clicks-for-dynamic') {
      parsed.defaultClicksForDynamic = requireValue(arg, next)
      index++
    }
    else if (arg === '--min-font-size') {
      parsed.minFontSize = requireValue(arg, next)
      index++
    }
    else if (arg === '--min-contrast') {
      parsed.minContrast = requireValue(arg, next)
      index++
    }
    else if (arg === '--large-text-contrast') {
      parsed.largeTextContrast = requireValue(arg, next)
      index++
    }
    else if (arg === '--overflow-tolerance') {
      parsed.overflowTolerance = requireValue(arg, next)
      index++
    }
    else if (arg === '--safe-margin') {
      parsed.safeMargin = requireValue(arg, next)
      index++
    }
    else if (arg === '--overlap-ratio') {
      parsed.overlapRatio = requireValue(arg, next)
      index++
    }
    else if (arg === '--max-words') {
      parsed.maxWords = requireValue(arg, next)
      index++
    }
    else if (arg === '--max-text-blocks') {
      parsed.maxTextBlocks = requireValue(arg, next)
      index++
    }
    else if (arg === '--screenshots') {
      parsed.screenshots = requireValue(arg, next)
      index++
    }
    else if (arg === '--ignore-selector') {
      parsed.ignoreSelector = requireValue(arg, next)
      index++
    }
    else if (arg === '--allow-overflow-selector') {
      parsed.allowOverflowSelector = requireValue(arg, next)
      index++
    }
    else if (arg === '--allow-hidden-selector') {
      parsed.allowHiddenSelector = requireValue(arg, next)
      index++
    }
    else if (arg === '--headed') {
      parsed.headed = true
    }
    else if (arg === '--strict') {
      parsed.strict = true
    }
    else {
      throw new Error(`Unknown argument: ${arg}`)
    }
  }

  return parsed
}

function normalizeOptions(parsed: Record<string, string | boolean>): Options {
  const deckDir = resolve(invocationCwd, String(parsed.deck ?? '.'))
  const slidesValue = parsed.slides === undefined ? resolve(deckDir, 'slides.md') : String(parsed.slides)
  const slidesFile = isAbsolute(slidesValue) ? slidesValue : resolve(deckDir, slidesValue)
  const name = sanitizeName(String(parsed.name ?? (basename(deckDir) || 'slidev-deck')))
  const outDir = resolve(invocationCwd, String(parsed.out ?? resolve('projects', 'slidev-quality-audits', 'artifacts', 'reports', name)))
  const waitUntil = String(parsed.waitUntil ?? 'networkidle') as WaitUntil
  const screenshots = String(parsed.screenshots ?? 'issues') as Options['screenshots']

  if (!existsSync(deckDir))
    throw new Error(`Deck directory does not exist: ${deckDir}`)
  if (!existsSync(slidesFile))
    throw new Error(`Slides file does not exist: ${slidesFile}`)
  if (!['load', 'domcontentloaded', 'networkidle'].includes(waitUntil))
    throw new Error('--wait-until must be one of: load, domcontentloaded, networkidle')
  if (!['issues', 'all', 'none'].includes(screenshots))
    throw new Error('--screenshots must be one of: issues, all, none')

  return {
    deckDir,
    slidesFile,
    outDir,
    name,
    port: numberOption(parsed.port, defaultPort(), '--port'),
    width: numberOption(parsed.width, 1280, '--width'),
    height: numberOption(parsed.height, 720, '--height'),
    dwellMs: numberOption(parsed.dwell, 700, '--dwell'),
    clickDwellMs: numberOption(parsed.clickDwell, 750, '--click-dwell'),
    timeoutMs: numberOption(parsed.timeout, 30000, '--timeout'),
    waitUntil,
    channel: parsed.channel === 'none' ? undefined : String(parsed.channel ?? process.env.PLAYWRIGHT_CHANNEL ?? 'msedge'),
    headed: Boolean(parsed.headed),
    strict: Boolean(parsed.strict),
    range: parsed.range === undefined ? undefined : String(parsed.range),
    maxClicks: parsed.maxClicks === undefined ? undefined : numberOption(parsed.maxClicks, 0, '--max-clicks'),
    defaultClicksForDynamic: numberOption(parsed.defaultClicksForDynamic, 0, '--default-clicks-for-dynamic'),
    minFontSize: numberOption(parsed.minFontSize, 12, '--min-font-size'),
    minContrast: numberOption(parsed.minContrast, 4.5, '--min-contrast'),
    largeTextContrast: numberOption(parsed.largeTextContrast, 3, '--large-text-contrast'),
    overflowTolerance: numberOption(parsed.overflowTolerance, 4, '--overflow-tolerance'),
    safeMargin: numberOption(parsed.safeMargin, 18, '--safe-margin'),
    overlapRatio: numberOption(parsed.overlapRatio, 0.18, '--overlap-ratio'),
    maxWords: numberOption(parsed.maxWords, 115, '--max-words'),
    maxTextBlocks: numberOption(parsed.maxTextBlocks, 24, '--max-text-blocks'),
    screenshots,
    ignoreSelector: String(parsed.ignoreSelector ?? '[data-slidev-audit-ignore], [data-audit-ignore], .slidev-audit-ignore'),
    allowOverflowSelector: String(parsed.allowOverflowSelector ?? '[data-allow-overflow], .allow-overflow, .intentional-overflow'),
    allowHiddenSelector: String(parsed.allowHiddenSelector ?? '[data-allow-hidden], .allow-hidden, .intentional-hidden, [aria-hidden="true"]'),
  }
}

function requireValue(flag: string, value: string | undefined) {
  if (!value || value.startsWith('--'))
    throw new Error(`${flag} requires a value.`)
  return value
}

function numberOption(value: string | boolean | undefined, fallback: number, flag: string) {
  if (value === undefined)
    return fallback
  const number = Number(value)
  if (!Number.isFinite(number) || number < 0)
    throw new Error(`${flag} must be a non-negative number.`)
  return number
}

function printHelp() {
  console.log(`Audit a Slidev deck for layout and visual-quality issues.

Usage:
  npx tsx audit-slidev-quality.ts --deck <deck-dir> --out <output-dir>

Common options:
  --slides <file>                       Slidev markdown entry file
  --range <spec>                        Slides to audit, for example 1,4-6
  --max-clicks <n>                      Cap detected click states per slide
  --screenshots <issues|all|none>       Screenshot capture mode, default issues
  --strict                              Exit nonzero on error-level findings
  --min-font-size <px>                  Minimum visible text size, default 12
  --min-contrast <ratio>                Minimum normal text contrast, default 4.5
  --overflow-tolerance <px>             Allowed off-frame tolerance, default 4
  --safe-margin <px>                    Minimum text margin from frame, default 18
  --allow-overflow-selector <selector>  Mark intentional bleed or crop elements
  --allow-hidden-selector <selector>    Mark intentional hidden final-state text
  --ignore-selector <selector>          Exclude decorative or known-noisy nodes
  --channel <name|none>                 Preferred Chromium channel, default msedge
  --headed                              Show browser while auditing
`)
}

function defaultPort() {
  return 3030 + (process.pid % 1000)
}

function isIgnoredRuntimeIssue(message: string) {
  return /wake lock permission request denied/i.test(message)
    || (/NotAllowedError/i.test(message) && /Wake Lock/i.test(message))
}

async function gotoSlide(page: any, baseUrl: string, slide: SlidePlan, options: Options) {
  await page.goto(`${baseUrl}/${slide.no}?embedded=true&clicks=0`, {
    waitUntil: 'domcontentloaded',
    timeout: options.timeoutMs,
  })
  await waitForSlideReady(page, options.timeoutMs)
  if (options.waitUntil !== 'domcontentloaded')
    await page.waitForLoadState(options.waitUntil, { timeout: options.timeoutMs })
}

async function inspectState(page: any, options: Options): Promise<StateInspection> {
  return await page.evaluate((auditOptions: any) => {
    const findings: BrowserFinding[] = []
    const hiddenTextFindings: BrowserFinding[] = []
    const capCounts = new Map<string, number>()

    const add = (
      list: BrowserFinding[],
      ruleId: string,
      severity: Severity,
      target: string,
      message: string,
      critique: string,
      improvement: string,
      rect?: DOMRect,
      cap = 14,
    ) => {
      const count = capCounts.get(ruleId) || 0
      if (count >= cap)
        return
      capCounts.set(ruleId, count + 1)
      list.push({
        ruleId,
        severity,
        target,
        message,
        critique,
        improvement,
        rect: rect ? serializeRect(rect) : undefined,
      })
    }

    const layouts = [...document.querySelectorAll('.slidev-layout')]
      .filter((node) => isVisible(node, true))
      .sort((first, second) => area(second.getBoundingClientRect()) - area(first.getBoundingClientRect()))
    const layout = layouts[0] as HTMLElement | undefined

    if (!layout) {
      add(
        findings,
        'layout-missing',
        'error',
        '.slidev-layout',
        'No visible Slidev layout was found.',
        'The active route did not expose a visible Slidev slide, so visual quality cannot be trusted.',
        'Fix Slidev routing, server startup, or runtime errors before auditing slide quality.',
      )
      return {
        visualHash: 'layout-missing',
        metrics: { hasLayout: false, visibleElementCount: 0, textLength: 0 },
        findings,
        hiddenTextFindings,
      }
    }

    const layoutRect = layout.getBoundingClientRect()
    const allElements = [...layout.querySelectorAll('*')].filter((node) => !matchesClosest(node, auditOptions.ignoreSelector))
    const visibleElements = allElements.filter((node) => isVisible(node, false))
    const textElements = allElements.filter((node) => hasMeaningfulText(node))
    const visibleTextElements = textElements.filter((node) => isVisible(node, false))
    const textBlocks = visibleTextElements.filter((node) => isTextBlock(node))
    const textLength = normalizeText(layout.innerText || layout.textContent || '').length
    const words = wordCountOf(layout.innerText || layout.textContent || '')
    const viewportOverflowX = Math.max(
      0,
      document.documentElement.scrollWidth - document.documentElement.clientWidth,
      document.body.scrollWidth - document.body.clientWidth,
    )
    const viewportOverflowY = Math.max(
      0,
      document.documentElement.scrollHeight - document.documentElement.clientHeight,
      document.body.scrollHeight - document.body.clientHeight,
    )

    if (textLength < 4 && !visibleElements.some((node) => isMediaElement(node))) {
      add(
        findings,
        'blank-slide',
        'error',
        describeElement(layout),
        'Slide has almost no visible text, chart, media, or SVG content.',
        'The slide appears blank or functionally empty in the browser.',
        'Restore the missing component or remove the empty slide from the deck.',
        layoutRect,
      )
    }

    if (viewportOverflowX > auditOptions.overflowTolerance || viewportOverflowY > auditOptions.overflowTolerance) {
      add(
        findings,
        'viewport-overflow',
        'error',
        'document',
        `Document overflows viewport by ${Math.round(viewportOverflowX)}px horizontally and ${Math.round(viewportOverflowY)}px vertically.`,
        'The exported slide can be cropped, shifted, or show scrollbars in screenshots and videos.',
        'Constrain slide containers with max-width, min-width: 0, stable grid tracks, and explicit heights.',
      )
    }

    const offSlide = visibleElements
      .map((node) => ({ node, rect: node.getBoundingClientRect(), overage: offSlideOverage(node.getBoundingClientRect(), layoutRect, auditOptions.overflowTolerance) }))
      .filter((item) => item.overage > 0 && !hasScrollableAncestor(item.node) && !matchesClosest(item.node, auditOptions.allowOverflowSelector))
      .sort((first, second) => second.overage - first.overage)
      .slice(0, 14)
    for (const item of offSlide) {
      add(
        findings,
        'off-slide-element',
        'error',
        describeElement(item.node),
        `Visible element extends ${Math.round(item.overage)}px beyond the slide frame.`,
        'The audience may lose content in screenshots, video exports, or embedded playback.',
        'Resize, wrap, or reposition the element; mark only intentional bleed art with data-allow-overflow.',
        item.rect,
      )
    }

    for (const node of textBlocks) {
      const element = node as HTMLElement
      const rect = element.getBoundingClientRect()
      const allowsIntentionalClip = matchesClosest(node, auditOptions.allowOverflowSelector)
      const style = getComputedStyle(element)
      const fontSize = Number.parseFloat(style.fontSize || '0')
      const horizontalClip = element.scrollWidth > element.clientWidth + 4
      const verticalClip = element.scrollHeight > element.clientHeight + Math.max(6, fontSize * 0.3)
      if (!allowsIntentionalClip && (horizontalClip || verticalClip)) {
        add(
          findings,
          'clipped-text',
          'error',
          describeElement(node),
          'Text box has hidden overflow or clipped wrapping content.',
          'Important words can be cut off even when the slide looks mostly complete.',
          'Increase the container size, reduce copy, lower the local font size, or allow wrapping.',
          rect,
        )
      }

      const overflowText = `${style.overflow} ${style.overflowX} ${style.overflowY}`
      if (!allowsIntentionalClip && /(hidden|clip|scroll|auto)/.test(overflowText) && (verticalClip || horizontalClip)) {
        add(
          findings,
          'clipped-text',
          'error',
          describeElement(node),
          'Text container requires clipping or scrolling to reveal all content.',
          'Slide viewers and video exports normally cannot recover hidden text.',
          'Avoid scrollable text on slides; split the content or expand the layout.',
          rect,
        )
      }
    }

    for (const node of textElements) {
      if (!isVisible(node, false) && !matchesClosest(node, auditOptions.allowHiddenSelector)) {
        const rect = node.getBoundingClientRect()
        add(
          hiddenTextFindings,
          'hidden-final-text',
          'warning',
          describeElement(node),
          `Text remains hidden: "${previewText(node)}"`,
          'The final click state still contains hidden textual information that may be stale or unintentionally unreachable.',
          'Remove stale hidden content, add the missing click state, or mark intentional alternates with data-allow-hidden.',
          rect,
          10,
        )
      }
    }

    findTextOverlaps(textBlocks, auditOptions.overlapRatio).forEach((pair) => {
      add(
        findings,
        'overlapping-text',
        'error',
        `${describeElement(pair.first)} + ${describeElement(pair.second)}`,
        `Text blocks overlap by ${Math.round(pair.ratio * 100)}% of the smaller block.`,
        'Overlapping copy makes the slide hard to read and often signals unstable grid or absolute positioning.',
        'Add gap, change grid tracks, reduce copy, or move absolute elements away from text.',
        pair.rect,
        10,
      )
    })

    for (const node of textBlocks.slice(0, 120)) {
      const rect = node.getBoundingClientRect()
      const centerX = clamp(rect.left + rect.width / 2, 0, innerWidth - 1)
      const centerY = clamp(rect.top + rect.height / 2, 0, innerHeight - 1)
      const topNode = document.elementFromPoint(centerX, centerY)
      if (topNode && layout.contains(topNode) && topNode !== node && !node.contains(topNode) && !topNode.contains(node) && !matchesClosest(node, auditOptions.allowOverflowSelector) && !matchesClosest(topNode, auditOptions.ignoreSelector)) {
        add(
          findings,
          'covered-content',
          'warning',
          describeElement(node),
          `Text center is covered by ${describeElement(topNode)}.`,
          'A visible overlay can hide important text at export time even if the DOM element itself is visible.',
          'Move the overlay, lower z-index, add padding, or make the overlay non-covering.',
          rect,
          10,
        )
      }
    }

    for (const node of textBlocks) {
      const element = node as HTMLElement
      const style = getComputedStyle(element)
      const fontSize = Number.parseFloat(style.fontSize || '0')
      const rect = element.getBoundingClientRect()
      if (fontSize > 0 && fontSize < auditOptions.minFontSize) {
        add(
          findings,
          'tiny-text',
          'warning',
          describeElement(node),
          `Text is ${fontSize.toFixed(1)}px, below the ${auditOptions.minFontSize}px threshold.`,
          'Small text is difficult to read in exported videos, thumbnails, and mobile embeds.',
          'Use larger type, reduce copy, or split the material across slides.',
          rect,
        )
      }

      const fg = parseCssColor(style.color)
      const bg = findBackgroundColor(element, layout)
      if (fg && bg) {
        const contrast = contrastRatio(fg, bg)
        const required = fontSize >= 18 || (fontSize >= 14 && Number.parseFloat(style.fontWeight || '400') >= 700)
          ? auditOptions.largeTextContrast
          : auditOptions.minContrast
        if (contrast < required) {
          add(
            findings,
            'low-contrast-text',
            'warning',
            describeElement(node),
            `Text contrast is ${contrast.toFixed(2)}:1, below the ${required}:1 threshold.`,
            'Low contrast reduces readability and can disappear after compression in video exports.',
            'Darken the text, lighten the background, or place text on a solid backing.',
            rect,
          )
        }
      }

      const nearestEdge = Math.min(
        Math.abs(rect.left - layoutRect.left),
        Math.abs(layoutRect.right - rect.right),
        Math.abs(rect.top - layoutRect.top),
        Math.abs(layoutRect.bottom - rect.bottom),
      )
      if (nearestEdge < auditOptions.safeMargin && !matchesClosest(node, auditOptions.allowOverflowSelector)) {
        add(
          findings,
          'unsafe-margin',
          'info',
          describeElement(node),
          `Text is ${Math.round(nearestEdge)}px from the slide frame edge.`,
          'Text near the edge can feel cropped and is vulnerable to export or player framing differences.',
          'Move important text inward or add slide padding.',
          rect,
          8,
        )
      }
    }

    for (const node of visibleElements.filter((element) => isMediaElement(element))) {
      const rect = node.getBoundingClientRect()
      if (rect.width < 8 || rect.height < 8) {
        add(
          findings,
          'zero-size-media',
          'error',
          describeElement(node),
          'Visible media or chart surface is effectively zero-size.',
          'The component mounted but did not receive usable layout dimensions.',
          'Give the container stable width and height, and resize charts after the slide becomes visible.',
          rect,
        )
      }

      if (node instanceof HTMLImageElement && (node.complete === false || node.naturalWidth === 0 || node.naturalHeight === 0)) {
        add(
          findings,
          'broken-media',
          'error',
          describeElement(node),
          'Image failed to load intrinsic dimensions.',
          'Broken image assets leave holes in the slide and can invalidate visual review.',
          'Fix the asset path, bundler import, public directory location, or network dependency.',
          rect,
        )
      }

      if (node instanceof HTMLVideoElement && node.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) {
        add(
          findings,
          'broken-media',
          'error',
          describeElement(node),
          'Video element has no playable source.',
          'Missing video sources leave an empty playback surface in the presentation.',
          'Fix the video source path or provide a supported fallback format.',
          rect,
        )
      }

      if (node instanceof HTMLImageElement && node.naturalWidth > 0 && node.naturalHeight > 0 && rect.width > 8 && rect.height > 8) {
        const naturalRatio = node.naturalWidth / node.naturalHeight
        const renderedRatio = rect.width / rect.height
        const ratioDelta = Math.abs(Math.log(renderedRatio / naturalRatio))
        if (ratioDelta > 0.22 && !matchesClosest(node, auditOptions.allowOverflowSelector)) {
          add(
            findings,
            'distorted-media',
            'warning',
            describeElement(node),
            'Rendered image aspect ratio differs from its intrinsic ratio.',
            'Unintentional stretching makes images and screenshots look low quality.',
            'Preserve aspect ratio with width/height constraints or use object-fit for intentional crops.',
            rect,
          )
        }
      }

      if (node instanceof HTMLCanvasElement && !canvasIsNonBlank(node) && !hasNonBlankCanvasSibling(node)) {
        add(
          findings,
          'blank-canvas',
          'error',
          describeElement(node),
          'Canvas samples as blank or nearly blank.',
          'Charts or canvas visuals can silently fail while the slide still appears structurally present.',
          'Wait for chart initialization, verify data and renderer setup, and resize after activation.',
          rect,
        )
      }

      if (node instanceof SVGSVGElement && svgLooksBlank(node)) {
        add(
          findings,
          'blank-svg',
          'error',
          describeElement(node),
          'SVG surface has no meaningful graphic or text content.',
          'An empty SVG usually means generation, viewBox, or component conditions failed.',
          'Fix SVG generation, viewBox, child elements, or conditional rendering.',
          rect,
        )
      }
    }

    if (words > auditOptions.maxWords || textBlocks.length > auditOptions.maxTextBlocks) {
      add(
        findings,
        'dense-slide',
        'warning',
        describeElement(layout),
        `Slide has ${words} words and ${textBlocks.length} text blocks.`,
        'Dense slides are harder to scan and more likely to hide overflow after responsive changes.',
        'Split the content, replace prose with a diagram, or move details to speaker notes.',
        layoutRect,
      )
    }

    const canvasHashes = visibleElements
      .filter((node) => node instanceof HTMLCanvasElement)
      .map((node) => hashText(sampleCanvasSignature(node as HTMLCanvasElement)))
    const svgHashes = visibleElements
      .filter((node) => node instanceof SVGSVGElement)
      .map((node) => hashText(new XMLSerializer().serializeToString(node).slice(0, 120000)))
    const motionSignature = visibleElements.slice(0, 260).map((node) => {
      const rect = node.getBoundingClientRect()
      const style = getComputedStyle(node)
      return [
        node.tagName,
        typeof (node as HTMLElement).className === 'string' ? (node as HTMLElement).className : '',
        Math.round(rect.left),
        Math.round(rect.top),
        Math.round(rect.width),
        Math.round(rect.height),
        style.transform,
        style.opacity,
      ].join(':')
    }).join('|')
    const visualHash = hashText([
      normalizeText(layout.innerText || layout.textContent || ''),
      motionSignature,
      canvasHashes.join(','),
      svgHashes.join(','),
    ].join('|'))

    return {
      visualHash,
      metrics: {
        hasLayout: true,
        visibleElementCount: visibleElements.length,
        textLength,
        wordCount: words,
        textBlockCount: textBlocks.length,
        viewportOverflowX,
        viewportOverflowY,
        canvasCount: visibleElements.filter((node) => node instanceof HTMLCanvasElement).length,
        svgCount: visibleElements.filter((node) => node instanceof SVGSVGElement).length,
        mediaCount: visibleElements.filter((node) => isMediaElement(node)).length,
      },
      findings,
      hiddenTextFindings,
    }

    function isVisible(node: Element, _allowPartial: boolean) {
      const rect = node.getBoundingClientRect()
      const style = getComputedStyle(node)
      return style.visibility !== 'hidden'
        && style.display !== 'none'
        && Number(style.opacity) > 0.01
        && rect.width > 1
        && rect.height > 1
        && rect.bottom > 0
        && rect.right > 0
        && rect.top < innerHeight
        && rect.left < innerWidth
    }

    function hasMeaningfulText(node: Element) {
      const tag = node.tagName.toLowerCase()
      if (['script', 'style', 'title', 'meta', 'link'].includes(tag))
        return false
      return normalizeText((node as HTMLElement).innerText || node.textContent || '').length >= 2
    }

    function isTextBlock(node: Element) {
      const tag = node.tagName.toLowerCase()
      const textTags = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span', 'strong', 'em', 'code', 'pre', 'a', 'button', 'td', 'th', 'label'])
      if (!textTags.has(tag) && !node.getAttribute('role')?.includes('heading'))
        return false

      const visibleTextChildren = [...node.children].filter((child) => isVisible(child, false) && hasMeaningfulText(child))
      if (visibleTextChildren.length === 0)
        return true

      const ownText = [...node.childNodes]
        .filter((child) => child.nodeType === Node.TEXT_NODE)
        .map((child) => child.textContent || '')
        .join(' ')
      return normalizeText(ownText).length >= 12
    }

    function normalizeText(value: string) {
      return value.replace(/\s+/g, ' ').trim()
    }

    function wordCountOf(value: string) {
      const text = normalizeText(value)
      return text ? text.split(/\s+/).length : 0
    }

    function previewText(node: Element) {
      const text = normalizeText((node as HTMLElement).innerText || node.textContent || '')
      return text.length > 80 ? `${text.slice(0, 77)}...` : text
    }

    function matchesClosest(node: Element, selector: string) {
      if (!selector)
        return false
      try {
        return Boolean(node.closest(selector))
      }
      catch {
        return false
      }
    }

    function isMediaElement(node: Element) {
      return ['canvas', 'svg', 'img', 'video', 'iframe', 'object', 'embed'].includes(node.tagName.toLowerCase())
    }

    function serializeRect(rect: DOMRect): Rect {
      return {
        left: round(rect.left),
        top: round(rect.top),
        right: round(rect.right),
        bottom: round(rect.bottom),
        width: round(rect.width),
        height: round(rect.height),
      }
    }

    function round(value: number) {
      return Math.round(value * 10) / 10
    }

    function area(rect: DOMRect | Rect) {
      return Math.max(0, rect.width) * Math.max(0, rect.height)
    }

    function offSlideOverage(rect: DOMRect, frame: DOMRect, tolerance: number) {
      const left = Math.max(0, frame.left - rect.left - tolerance)
      const right = Math.max(0, rect.right - frame.right - tolerance)
      const top = Math.max(0, frame.top - rect.top - tolerance)
      const bottom = Math.max(0, rect.bottom - frame.bottom - tolerance)
      return Math.max(left, right, top, bottom)
    }

    function findTextOverlaps(nodes: Element[], minRatio: number) {
      const pairs: Array<{ first: Element, second: Element, ratio: number, rect: DOMRect }> = []
      const items = nodes
        .map((node) => ({ node, rect: node.getBoundingClientRect() }))
        .filter((item) => item.rect.width > 4 && item.rect.height > 4)
        .slice(0, 90)

      for (let firstIndex = 0; firstIndex < items.length; firstIndex++) {
        for (let secondIndex = firstIndex + 1; secondIndex < items.length; secondIndex++) {
          const first = items[firstIndex]
          const second = items[secondIndex]
          if (first.node.contains(second.node) || second.node.contains(first.node))
            continue
          if (first.node.closest('pre, code') || second.node.closest('pre, code'))
            continue
          if (hasTransformedAncestor(first.node) || hasTransformedAncestor(second.node))
            continue
          if (normalizeText(first.node.textContent || '') === normalizeText(second.node.textContent || '') && sameRect(first.rect, second.rect))
            continue
          const intersection = intersectRect(first.rect, second.rect)
          if (!intersection)
            continue
          const ratio = area(intersection) / Math.max(1, Math.min(area(first.rect), area(second.rect)))
          if (ratio >= minRatio)
            pairs.push({ first: first.node, second: second.node, ratio, rect: intersection as DOMRect })
        }
      }

      return pairs.sort((first, second) => second.ratio - first.ratio).slice(0, 10)
    }

    function sameRect(first: DOMRect, second: DOMRect) {
      return Math.abs(first.left - second.left) < 1
        && Math.abs(first.top - second.top) < 1
        && Math.abs(first.width - second.width) < 1
        && Math.abs(first.height - second.height) < 1
    }

    function hasTransformedAncestor(node: Element) {
      let current: Element | null = node
      while (current && current !== layout) {
        const transform = getComputedStyle(current).transform
        if (transform && transform !== 'none')
          return true
        current = current.parentElement
      }
      return false
    }

    function hasScrollableAncestor(node: Element) {
      let current = node.parentElement
      while (current && current !== layout) {
        const style = getComputedStyle(current)
        if (/(auto|scroll)/.test(`${style.overflow} ${style.overflowX} ${style.overflowY}`))
          return true
        current = current.parentElement
      }
      return false
    }

    function hasNonBlankCanvasSibling(canvas: HTMLCanvasElement) {
      const parent = canvas.parentElement
      if (!parent)
        return false
      return [...parent.querySelectorAll('canvas')]
        .some((candidate) => candidate !== canvas && isVisible(candidate, false) && canvasIsNonBlank(candidate as HTMLCanvasElement))
    }

    function intersectRect(first: DOMRect, second: DOMRect) {
      const left = Math.max(first.left, second.left)
      const right = Math.min(first.right, second.right)
      const top = Math.max(first.top, second.top)
      const bottom = Math.min(first.bottom, second.bottom)
      if (right <= left || bottom <= top)
        return null
      return {
        left,
        top,
        right,
        bottom,
        width: right - left,
        height: bottom - top,
      } as DOMRect
    }

    function clamp(value: number, min: number, max: number) {
      return Math.max(min, Math.min(max, value))
    }

    function parseCssColor(value: string) {
      const match = value.match(/rgba?\(([^)]+)\)/)
      if (!match)
        return null
      const parts = match[1].split(',').map((part) => Number.parseFloat(part.trim()))
      if (parts.length < 3 || parts.some((part) => Number.isNaN(part)))
        return null
      return { r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 }
    }

    function findBackgroundColor(node: HTMLElement, fallbackRoot: HTMLElement) {
      let current: HTMLElement | null = node
      while (current) {
        const style = getComputedStyle(current)
        const color = parseCssColor(style.backgroundColor)
        if (color && color.a > 0.2)
          return color
        if (style.backgroundImage && style.backgroundImage !== 'none')
          return null
        if (current === fallbackRoot)
          break
        current = current.parentElement
      }
      return { r: 255, g: 255, b: 255, a: 1 }
    }

    function contrastRatio(foreground: any, background: any) {
      const fg = foreground.a < 1 ? blend(foreground, background) : foreground
      const fgLum = luminance(fg)
      const bgLum = luminance(background)
      const light = Math.max(fgLum, bgLum)
      const dark = Math.min(fgLum, bgLum)
      return (light + 0.05) / (dark + 0.05)
    }

    function blend(foreground: any, background: any) {
      const alpha = foreground.a
      return {
        r: foreground.r * alpha + background.r * (1 - alpha),
        g: foreground.g * alpha + background.g * (1 - alpha),
        b: foreground.b * alpha + background.b * (1 - alpha),
        a: 1,
      }
    }

    function luminance(color: any) {
      const values = [color.r, color.g, color.b].map((channel) => {
        const value = channel / 255
        return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4
      })
      return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]
    }

    function canvasIsNonBlank(canvas: HTMLCanvasElement) {
      const signature = sampleCanvasSignature(canvas)
      if (signature === 'empty-canvas' || signature === 'tainted-canvas')
        return signature === 'tainted-canvas'
      return !signature.startsWith('blank:')
    }

    function sampleCanvasSignature(canvas: HTMLCanvasElement) {
      if (canvas.width === 0 || canvas.height === 0)
        return 'empty-canvas'
      const context = canvas.getContext('2d', { willReadFrequently: true })
      if (!context)
        return 'empty-canvas'

      try {
        const data = context.getImageData(0, 0, canvas.width, canvas.height).data
        let colored = 0
        let opaque = 0
        let sample = ''
        const stride = Math.max(4, Math.floor(data.length / 7000))
        const alignedStride = stride - (stride % 4) || 4
        for (let index = 0; index < data.length; index += alignedStride) {
          const r = data[index]
          const g = data[index + 1]
          const b = data[index + 2]
          const a = data[index + 3]
          if (a > 0)
            opaque++
          if (a > 0 && (Math.abs(r - 255) > 8 || Math.abs(g - 255) > 8 || Math.abs(b - 255) > 8))
            colored++
          sample += `${r},${g},${b},${a};`
        }
        if (opaque <= 20 || colored <= 10)
          return `blank:${opaque}:${colored}:${hashText(sample)}`
        return sample
      }
      catch {
        return 'tainted-canvas'
      }
    }

    function svgLooksBlank(svg: SVGSVGElement) {
      const meaningful = svg.querySelectorAll('path, circle, rect, line, polyline, polygon, ellipse, text, image, use')
      if (meaningful.length === 0)
        return true
      try {
        const box = svg.getBBox()
        return box.width <= 1 || box.height <= 1
      }
      catch {
        return false
      }
    }

    function hashText(text: string) {
      let hash = 2166136261
      for (let index = 0; index < text.length; index++) {
        hash ^= text.charCodeAt(index)
        hash = Math.imul(hash, 16777619)
      }
      return String(hash >>> 0)
    }

    function describeElement(node: Element) {
      const element = node as HTMLElement
      const tag = element.tagName.toLowerCase()
      const id = element.id ? `#${element.id}` : ''
      const classes = typeof element.className === 'string'
        ? element.className.split(/\s+/).filter(Boolean).slice(0, 3).map((name) => `.${name}`).join('')
        : ''
      const data = element.getAttribute('data-testid') || element.getAttribute('aria-label')
      return `${tag}${id}${classes}${data ? `[${data}]` : ''}`
    }
  }, {
    minFontSize: options.minFontSize,
    minContrast: options.minContrast,
    largeTextContrast: options.largeTextContrast,
    overflowTolerance: options.overflowTolerance,
    safeMargin: options.safeMargin,
    overlapRatio: options.overlapRatio,
    maxWords: options.maxWords,
    maxTextBlocks: options.maxTextBlocks,
    ignoreSelector: options.ignoreSelector,
    allowOverflowSelector: options.allowOverflowSelector,
    allowHiddenSelector: options.allowHiddenSelector,
  })
}

async function parseSlides(slidesPath: string, defaultClicksForDynamic: number): Promise<SlidePlan[]> {
  const markdown = await readFile(slidesPath, 'utf8')
  const sections = splitSlides(stripFrontmatter(markdown))
  return sections.map((section, index) => {
    const dynamicClicks = section.includes('$clicks')
    const detectedClicks = countClicks(section)
    return {
      no: index + 1,
      title: section.match(/^#\s+(.+)$/m)?.[1]?.trim() || `Slide ${index + 1}`,
      clicks: detectedClicks || (dynamicClicks ? defaultClicksForDynamic : 0),
      dynamicClicks,
    }
  })
}

function stripFrontmatter(markdown: string) {
  const normalized = markdown.replace(/\r\n/g, '\n')
  if (!normalized.startsWith('---\n'))
    return normalized

  const end = normalized.indexOf('\n---\n', 4)
  return end === -1 ? normalized : normalized.slice(end + 5)
}

function splitSlides(markdown: string) {
  const sections: string[] = []
  const current: string[] = []
  let inFence = false
  let fenceMarker = ''

  for (const line of markdown.split('\n')) {
    const trimmed = line.trim()
    const fenceMatch = trimmed.match(/^(```+|~~~+)/)
    if (fenceMatch) {
      const marker = fenceMatch[1][0]
      if (!inFence) {
        inFence = true
        fenceMarker = marker
      }
      else if (marker === fenceMarker) {
        inFence = false
        fenceMarker = ''
      }
    }

    if (!inFence && /^---\s*$/.test(line)) {
      sections.push(current.join('\n'))
      current.length = 0
    }
    else {
      current.push(line)
    }
  }

  sections.push(current.join('\n'))
  if (sections.length > 1 && !sections[sections.length - 1].trim())
    sections.pop()
  return sections
}

function countClicks(section: string) {
  let count = 0
  let remainder = section
  const vClicksBlocks = [...section.matchAll(/<v-clicks\b[\s\S]*?<\/v-clicks>/gi)]

  for (const block of vClicksBlocks) {
    count += block[0].split('\n').filter((line) => /^\s*[-*+]\s+/.test(line)).length
    remainder = remainder.replace(block[0], '')
  }

  const explicitVClicks = remainder.match(/<v-click(?:\s|>|\/|\.)/gi) || []
  count += explicitVClicks.length
  remainder = remainder.replace(/<v-click\b[\s\S]*?<\/v-click>/gi, '')
  remainder = remainder.replace(/<v-click\b[^>]*\/?>/gi, '')
  count += (remainder.match(/\bv-click(?:\.\w+)?\b/gi) || []).length

  const atValues = [...section.matchAll(/\bat=["']?(\d+)/gi)].map((match) => Number(match[1]))
  if (atValues.length)
    count = Math.max(count, Math.max(...atValues))

  return count
}

function applyRange(slides: SlidePlan[], range: string | undefined) {
  if (!range)
    return slides

  const selected = new Set<number>()
  for (const part of range.split(',')) {
    const trimmed = part.trim()
    if (!trimmed)
      continue
    const rangeMatch = trimmed.match(/^(\d+)-(\d+)$/)
    if (rangeMatch) {
      const start = Number(rangeMatch[1])
      const end = Number(rangeMatch[2])
      for (let value = Math.min(start, end); value <= Math.max(start, end); value++)
        selected.add(value)
    }
    else {
      selected.add(Number(trimmed))
    }
  }

  return slides.filter((slide) => selected.has(slide.no))
}

function loadPlaywright(deckDir: string) {
  try {
    const requireFromDeck = createRequire(resolve(deckDir, 'package.json'))
    return requireFromDeck('playwright')
  }
  catch (error) {
    throw new Error(`Could not load Playwright from the deck. Run "npm install --save-dev playwright" in ${deckDir}. ${(error as Error).message}`)
  }
}

function startSlidevServer(options: Options) {
  const relativeSlidesFile = relative(options.deckDir, options.slidesFile)
  const slidevEntry = relativeSlidesFile && !relativeSlidesFile.startsWith('..') && !isAbsolute(relativeSlidesFile)
    ? relativeSlidesFile
    : options.slidesFile
  const slidevArgs = [
    'slidev',
    slidevEntry,
    '--port',
    String(options.port),
    '--log',
    'warn',
  ]
  const command = process.platform === 'win32' ? 'cmd.exe' : 'npx'
  const args = process.platform === 'win32'
    ? ['/d', '/s', '/c', ['npx', ...slidevArgs].map(quoteForCmd).join(' ')]
    : slidevArgs
  const child = spawn(command, args, {
    cwd: options.deckDir,
    env: { ...process.env, FORCE_COLOR: '0' },
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  child.stdout?.on('data', (chunk) => process.stdout.write(chunk))
  child.stderr?.on('data', (chunk) => process.stderr.write(chunk))
  child.on('exit', (code) => {
    ;(child as any).slidevExited = true
    ;(child as any).slidevExitCode = code
    if (code && code !== 0 && !(child as any).slidevStopping)
      console.error(`Slidev server exited with code ${code}.`)
  })

  return child
}

function quoteForCmd(value: string) {
  if (/^[A-Za-z0-9._/:=-]+$/.test(value))
    return value
  return `"${value.replaceAll('"', '""')}"`
}

async function launchBrowser(chromium: any, options: Options) {
  if (options.channel) {
    try {
      return await chromium.launch({ channel: options.channel, headless: !options.headed })
    }
    catch (error) {
      console.warn(`Could not launch browser channel "${options.channel}": ${(error as Error).message}`)
    }
  }

  return await chromium.launch({ headless: !options.headed })
}

async function waitForServer(url: string, timeoutMs: number, server?: ChildProcess) {
  const started = Date.now()
  let lastError: Error | undefined

  while (Date.now() - started < timeoutMs) {
    if ((server as any)?.slidevExited && (server as any)?.slidevExitCode)
      throw new Error(`Slidev server exited before it became ready with code ${(server as any).slidevExitCode}.`)

    try {
      const response = await fetch(url)
      if (response.ok) {
        await delay(800)
        if ((server as any)?.slidevExited && (server as any)?.slidevExitCode)
          throw new Error(`Slidev server exited before it became ready with code ${(server as any).slidevExitCode}.`)
        return
      }
    }
    catch (error) {
      lastError = error as Error
    }
    await delay(250)
  }

  throw new Error(`Timed out waiting for Slidev at ${url}. ${lastError?.message || ''}`)
}

async function waitForSlideReady(page: any, timeoutMs: number) {
  await page.waitForFunction(() => {
    const layouts = [...document.querySelectorAll('.slidev-layout')]
    return layouts.some((candidate) => {
      const rect = candidate.getBoundingClientRect()
      const style = getComputedStyle(candidate)
      return style.visibility !== 'hidden'
        && style.display !== 'none'
        && rect.width > 200
        && rect.height > 150
        && rect.bottom > 0
        && rect.right > 0
        && rect.top < innerHeight
        && rect.left < innerWidth
    })
  }, null, { timeout: timeoutMs })
}

async function findAvailablePort(startPort: number) {
  for (let port = startPort; port < startPort + 50; port++) {
    if (await canBind(port, '127.0.0.1') && await canBind(port, '::1'))
      return port
  }

  throw new Error(`No available port found from ${startPort} to ${startPort + 49}.`)
}

async function canBind(port: number, host: string) {
  return await new Promise<boolean>((resolvePromise) => {
    const server = createServer()
    server.once('error', () => resolvePromise(false))
    server.once('listening', () => server.close(() => resolvePromise(true)))
    server.listen(port, host)
  })
}

function stopServer(child: ChildProcess | undefined) {
  if (!child?.pid)
    return

  ;(child as any).slidevStopping = true
  if (process.platform === 'win32') {
    spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' })
    return
  }

  child.kill()
}

function renderMarkdown(report: any) {
  const lines: string[] = []
  lines.push('# Slidev Quality Audit')
  lines.push('')
  lines.push(`- Generated: ${report.generatedAt}`)
  lines.push(`- Deck: ${report.deck}`)
  lines.push(`- Slides audited: ${report.slideCount}`)
  lines.push(`- Visual states audited: ${report.stateCount}`)
  lines.push(`- Findings: ${report.findingCount} (${formatSeverityCounts(report.severityCounts)})`)
  lines.push('')
  lines.push('## Rule Counts')
  lines.push('')
  const ruleEntries = Object.entries(report.ruleCounts).sort((a: any, b: any) => b[1] - a[1])
  if (ruleEntries.length) {
    for (const [rule, count] of ruleEntries)
      lines.push(`- \`${rule}\`: ${count}`)
  }
  else {
    lines.push('- No findings.')
  }
  lines.push('')
  lines.push('## Findings')
  lines.push('')
  if (!report.findings.length) {
    lines.push('No findings were detected.')
  }
  else {
    for (const finding of report.findings.slice(0, 200)) {
      const location = finding.slide > 0 ? `Slide ${finding.slide}, click ${finding.click}` : finding.title
      lines.push(`### [${finding.severity.toUpperCase()}] ${finding.ruleId} - ${location}`)
      lines.push('')
      lines.push(`- Target: \`${finding.target}\``)
      lines.push(`- Message: ${finding.message}`)
      lines.push(`- Critique: ${finding.critique}`)
      lines.push(`- Improvement: ${finding.improvement}`)
      if (finding.screenshot)
        lines.push(`- Screenshot: ${finding.screenshot}`)
      lines.push('')
    }
    if (report.findings.length > 200)
      lines.push(`Report truncated after 200 findings. See quality-report.json for all ${report.findings.length} findings.`)
  }
  lines.push('')
  lines.push('## Rule Coverage')
  lines.push('')
  for (const rule of [
    'layout-missing',
    'blank-slide',
    'viewport-overflow',
    'off-slide-element',
    'clipped-text',
    'hidden-final-text',
    'overlapping-text',
    'covered-content',
    'low-contrast-text',
    'tiny-text',
    'zero-size-media',
    'broken-media',
    'blank-canvas',
    'blank-svg',
    'distorted-media',
    'unchanged-click-state',
    'dense-slide',
    'unsafe-margin',
    'browser-console-error',
    'page-error',
  ])
    lines.push(`- \`${rule}\``)
  lines.push('')
  return `${lines.join('\n')}\n`
}

function countBy<T>(items: T[], keyFn: (item: T) => string) {
  const result: Record<string, number> = {}
  for (const item of items) {
    const key = keyFn(item)
    result[key] = (result[key] || 0) + 1
  }
  return result
}

function formatSeverityCounts(counts: Record<string, number>) {
  const error = counts.error || 0
  const warning = counts.warning || 0
  const info = counts.info || 0
  return `${error} error, ${warning} warning, ${info} info`
}

function sanitizeName(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'slidev-deck'
}

function relativeToCwd(path: string) {
  return relative(invocationCwd, path).replaceAll('\\', '/')
}

function delay(ms: number) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, ms))
}
