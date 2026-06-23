#!/usr/bin/env -S npx tsx
// Run: npx tsx ./.agents/skills/slidev-video/scripts/record-slidev-video.ts --deck ./examples/slidev-echarts --out ./output/slidev-video/slidev-echarts
// Dependencies: tsx, playwright in the target Slidev project, @slidev/cli in the target Slidev project, optional ffmpeg on PATH.

import { spawn, spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync } from 'node:fs'
import { copyFile, mkdir, readFile, rename, rm, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { createServer } from 'node:net'
import { basename, isAbsolute, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

type WaitUntil = 'load' | 'domcontentloaded' | 'networkidle'
type NavigationMode = 'native' | 'direct'

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
  transitionMs: number
  trimStartMs: number | 'auto'
  timeoutMs: number
  waitUntil: WaitUntil
  navigationMode: NavigationMode
  channel: string | undefined
  headed: boolean
  skipVideo: boolean
  keepWebm: boolean
  webmOnly: boolean
  strict: boolean
  strictOverflow: boolean
  requireClickChange: boolean
  defaultClicksForDynamic: number
  maxClicks: number | undefined
  range: string | undefined
}

type SlidePlan = {
  no: number
  title: string
  clicks: number
  dynamicClicks: boolean
}

type SlideInspection = {
  hasLayout: boolean
  hasVisibleContent: boolean
  visibleElementCount: number
  textLength: number
  canvasCount: number
  nonblankCanvasCount: number
  svgCount: number
  mediaCount: number
  overflowCount: number
  horizontalOverflowCount: number
  viewportOverflow: number
  visualHash: string
  warnings: string[]
}

const invocationCwd = process.cwd()

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error))
  process.exit(1)
})

async function main() {
  const options = normalizeOptions(parseArgs(process.argv.slice(2)))
  const videoSize = { width: options.width, height: options.height }
  const screenshotsDir = resolve(options.outDir, 'slides')
  const rawVideoDir = resolve(options.outDir, 'raw')
  const webmPath = resolve(options.outDir, `${options.name}.webm`)
  const mp4Path = resolve(options.outDir, `${options.name}.mp4`)
  const contactSheetPath = resolve(options.outDir, 'slide-contact-sheet.png')
  const manifestPath = resolve(options.outDir, 'recording-manifest.json')

  await mkdir(options.outDir, { recursive: true })
  await rm(screenshotsDir, { recursive: true, force: true })
  await rm(rawVideoDir, { recursive: true, force: true })
  await mkdir(screenshotsDir, { recursive: true })
  await mkdir(rawVideoDir, { recursive: true })

  const slides = applyRange(
    await parseSlides(options.slidesFile, options.defaultClicksForDynamic),
    options.range,
  )
  if (!slides.length)
    throw new Error('No slides selected for recording.')

  const playwright = loadPlaywright(options.deckDir)
  options.port = await findAvailablePort(options.port)
  const baseUrl = `http://localhost:${options.port}`

  let server: ChildProcess | undefined
  let browser: any
  let context: any
  let page: any
  let video: any
  let recordingStartedAt = 0
  let firstSlideReadyAt = 0

  const consoleIssues: string[] = []
  const pageErrors: string[] = []
  const warnings: string[] = []
  const results: any[] = []

  try {
    server = startSlidevServer(options)
    await waitForServer(baseUrl, options.timeoutMs, server)

    browser = await launchBrowser(playwright.chromium, options)
    context = await browser.newContext({
      viewport: videoSize,
      deviceScaleFactor: 1,
      recordVideo: options.skipVideo ? undefined : { dir: rawVideoDir, size: videoSize },
    })
    recordingStartedAt = Date.now()
    page = await context.newPage()
    await page.addInitScript(() => {
      ;(globalThis as any).__name = (value: any) => value
    })
    await page.evaluate(() => {
      ;(globalThis as any).__name = (value: any) => value
    })

    page.on('console', (message: any) => {
      if (message.type() === 'error')
        consoleIssues.push(message.text())
    })
    page.on('pageerror', (error: Error) => pageErrors.push(error.message))

    for (let index = 0; index < slides.length; index++) {
      const slide = slides[index]
      const previous = slides[index - 1]
      const next = slides[index + 1]
      const directNavigation = options.navigationMode === 'direct'
        || !previous
        || slide.no !== previous.no + 1

      if (directNavigation) {
        const readyAt = await gotoSlide(page, baseUrl, slide, options)
        if (!firstSlideReadyAt)
          firstSlideReadyAt = readyAt
      }

      results.push(await recordCurrentSlide(page, slide, options, screenshotsDir))

      if (next && options.navigationMode === 'native' && next.no === slide.no + 1)
        await navigateToNextSlide(page, baseUrl, next, options, warnings)
    }

    video = page.video?.()
  }
  finally {
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    stopServer(server)
  }

  if (video && !options.skipVideo) {
    const recordedPath = await video.path()
    await rm(webmPath, { force: true })
    await moveFile(recordedPath, webmPath)
  }

  const trimStartMs = resolveTrimStartMs(options, recordingStartedAt, firstSlideReadyAt)

  if (!options.skipVideo && existsSync(webmPath) && !options.webmOnly) {
    if (commandExists('ffmpeg')) {
      await convertToMp4(webmPath, mp4Path, options, trimStartMs)
    }
    else {
      warnings.push('ffmpeg was not found on PATH; MP4 conversion was skipped.')
    }
  }

  if (commandExists('ffmpeg'))
    await createContactSheet(screenshotsDir, contactSheetPath, slides.length).catch((error) => {
      warnings.push(`Contact sheet generation failed: ${error.message}`)
    })

  if (!options.keepWebm && existsSync(mp4Path))
    await rm(webmPath, { force: true })

  const failures = collectFailures(results, consoleIssues, pageErrors, options)
  const manifest = {
    generatedAt: new Date().toISOString(),
    deck: relativeToCwd(options.deckDir),
    slides: relativeToCwd(options.slidesFile),
    baseUrl,
    viewport: videoSize,
    navigationMode: options.navigationMode,
    transitionDwellMs: options.transitionMs,
    trimStartMs,
    slideCount: slides.length,
    recordedStates: results.reduce((total, result) => total + 1 + result.clicksRecorded, 0),
    video: options.skipVideo
      ? null
      : {
          webm: existsSync(webmPath) ? relativeToCwd(webmPath) : null,
          mp4: existsSync(mp4Path) ? relativeToCwd(mp4Path) : null,
        },
    contactSheet: existsSync(contactSheetPath) ? relativeToCwd(contactSheetPath) : null,
    warnings,
    failures,
    consoleIssues,
    pageErrors,
    results,
  }

  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8')

  console.log(`Recorded ${manifest.slideCount} slide(s) and ${manifest.recordedStates} visual state(s).`)
  if (manifest.video?.mp4)
    console.log(`MP4 video: ${resolve(invocationCwd, manifest.video.mp4)}`)
  if (manifest.video?.webm)
    console.log(`WebM video: ${resolve(invocationCwd, manifest.video.webm)}`)
  console.log(`Manifest: ${manifestPath}`)

  if (failures.length) {
    console.error(`Recording verification failed with ${failures.length} issue(s).`)
    for (const failure of failures.slice(0, 20))
      console.error(`- ${failure}`)
    if (options.strict)
      process.exitCode = 1
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
    else if (arg === '--transition-dwell') {
      parsed.transitionDwell = requireValue(arg, next)
      index++
    }
    else if (arg === '--trim-start') {
      parsed.trimStart = requireValue(arg, next)
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
    else if (arg === '--navigation') {
      parsed.navigation = requireValue(arg, next)
      index++
    }
    else if (arg === '--channel') {
      parsed.channel = requireValue(arg, next)
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
    else if (arg === '--range') {
      parsed.range = requireValue(arg, next)
      index++
    }
    else if (arg === '--skip-video') {
      parsed.skipVideo = true
    }
    else if (arg === '--no-webm') {
      parsed.keepWebm = false
    }
    else if (arg === '--webm-only') {
      parsed.webmOnly = true
    }
    else if (arg === '--direct-jumps') {
      parsed.navigation = 'direct'
    }
    else if (arg === '--no-trim-start') {
      parsed.trimStart = 'none'
    }
    else if (arg === '--no-strict') {
      parsed.strict = false
    }
    else if (arg === '--strict-overflow') {
      parsed.strictOverflow = true
    }
    else if (arg === '--require-click-change') {
      parsed.requireClickChange = true
    }
    else if (arg === '--headed') {
      parsed.headed = true
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
  const outDir = resolve(invocationCwd, String(parsed.out ?? resolve('output', 'slidev-video', name)))
  const waitUntil = String(parsed.waitUntil ?? 'networkidle') as WaitUntil
  const navigationMode = String(parsed.navigation ?? 'native') as NavigationMode
  const trimStartMs = parseTrimStart(parsed.trimStart)

  if (!existsSync(deckDir))
    throw new Error(`Deck directory does not exist: ${deckDir}`)
  if (!existsSync(slidesFile))
    throw new Error(`Slides file does not exist: ${slidesFile}`)
  if (!['load', 'domcontentloaded', 'networkidle'].includes(waitUntil))
    throw new Error('--wait-until must be one of: load, domcontentloaded, networkidle')
  if (!['native', 'direct'].includes(navigationMode))
    throw new Error('--navigation must be one of: native, direct')

  return {
    deckDir,
    slidesFile,
    outDir,
    name,
    port: numberOption(parsed.port, 3030, '--port'),
    width: numberOption(parsed.width, 1280, '--width'),
    height: numberOption(parsed.height, 720, '--height'),
    dwellMs: numberOption(parsed.dwell, 800, '--dwell'),
    clickDwellMs: numberOption(parsed.clickDwell, 900, '--click-dwell'),
    transitionMs: numberOption(parsed.transitionDwell, 700, '--transition-dwell'),
    trimStartMs,
    timeoutMs: numberOption(parsed.timeout, 30000, '--timeout'),
    waitUntil,
    navigationMode,
    channel: parsed.channel === 'none' ? undefined : String(parsed.channel ?? process.env.PLAYWRIGHT_CHANNEL ?? 'msedge'),
    headed: Boolean(parsed.headed),
    skipVideo: Boolean(parsed.skipVideo),
    keepWebm: parsed.keepWebm === false ? false : true,
    webmOnly: Boolean(parsed.webmOnly),
    strict: parsed.strict === false ? false : true,
    strictOverflow: Boolean(parsed.strictOverflow),
    requireClickChange: Boolean(parsed.requireClickChange),
    defaultClicksForDynamic: numberOption(parsed.defaultClicksForDynamic, 0, '--default-clicks-for-dynamic'),
    maxClicks: parsed.maxClicks === undefined ? undefined : numberOption(parsed.maxClicks, 0, '--max-clicks'),
    range: parsed.range === undefined ? undefined : String(parsed.range),
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

function parseTrimStart(value: string | boolean | undefined) {
  if (value === undefined || value === 'auto')
    return 'auto'
  if (value === 'none')
    return 0

  return numberOption(value, 0, '--trim-start')
}

function resolveTrimStartMs(options: Options, recordingStartedAt: number, firstSlideReadyAt: number) {
  if (options.skipVideo || options.webmOnly)
    return 0
  if (options.trimStartMs !== 'auto')
    return options.trimStartMs
  if (!recordingStartedAt || !firstSlideReadyAt)
    return 0

  return Math.max(0, firstSlideReadyAt - recordingStartedAt - 120)
}

function printHelp() {
  console.log(`Record a Slidev deck to WebM and optional MP4.

Usage:
  npx tsx record-slidev-video.ts --deck <deck-dir> --out <output-dir>

Common options:
  --slides <file>                       Slidev markdown entry file
  --range <spec>                        Slides to record, for example 1,4-6
  --skip-video                          Validate and screenshot without recording video
  --navigation <native|direct>          Use Slidev transitions or direct route jumps
  --transition-dwell <ms>               Wait after native slide transitions, default 700
  --trim-start <auto|none|ms>           Trim browser load lead-in from MP4, default auto
  --default-clicks-for-dynamic <n>      Fallback clicks for slides using $clicks
  --max-clicks <n>                      Cap clicks per slide
  --require-click-change                Fail if clicked slides do not visibly change
  --strict-overflow                     Fail on detected text or horizontal overflow
  --channel <name|none>                 Preferred Chromium channel, default msedge
  --headed                              Show browser while recording
  --direct-jumps                        Alias for --navigation direct
  --no-trim-start                       Alias for --trim-start none
`)
}

async function gotoSlide(page: any, baseUrl: string, slide: SlidePlan, options: Options) {
  const slideUrl = `${baseUrl}/${slide.no}?embedded=true&clicks=0`
  await page.goto(slideUrl, { waitUntil: 'domcontentloaded', timeout: options.timeoutMs })
  await waitForSlideReady(page, options.timeoutMs)
  const readyAt = Date.now()

  if (options.waitUntil !== 'domcontentloaded')
    await page.waitForLoadState(options.waitUntil, { timeout: options.timeoutMs })

  return readyAt
}

async function recordCurrentSlide(page: any, slide: SlidePlan, options: Options, screenshotsDir: string) {
  const clicksToRun = Math.min(slide.clicks, options.maxClicks ?? slide.clicks)
  const stateHashes: string[] = []
  const inspections: SlideInspection[] = []

  await page.waitForTimeout(options.dwellMs)

  const initial = await inspectSlide(page)
  inspections.push(initial)
  stateHashes.push(initial.visualHash)

  for (let click = 0; click < clicksToRun; click++) {
    await page.keyboard.press('ArrowRight')
    await page.waitForTimeout(options.clickDwellMs)
    const state = await inspectSlide(page)
    inspections.push(state)
    stateHashes.push(state.visualHash)
  }

  const final = inspections[inspections.length - 1]
  const screenshotPath = resolve(screenshotsDir, `slide-${String(slide.no).padStart(3, '0')}.png`)
  await page.screenshot({ path: screenshotPath, fullPage: false })

  return {
    slide: slide.no,
    title: slide.title,
    dynamicClicks: slide.dynamicClicks,
    clicksAvailable: slide.clicks,
    clicksRecorded: clicksToRun,
    visibleElementCount: final.visibleElementCount,
    textLength: final.textLength,
    canvasCount: final.canvasCount,
    nonblankCanvasCount: final.nonblankCanvasCount,
    svgCount: final.svgCount,
    mediaCount: final.mediaCount,
    overflowCount: final.overflowCount,
    horizontalOverflowCount: final.horizontalOverflowCount,
    viewportOverflow: final.viewportOverflow,
    changedAfterClicks: clicksToRun > 0 ? new Set(stateHashes).size > 1 : null,
    visualHashes: stateHashes,
    screenshot: relativeToCwd(screenshotPath),
    warnings: final.warnings,
  }
}

async function navigateToNextSlide(page: any, baseUrl: string, next: SlidePlan, options: Options, warnings: string[]) {
  await page.keyboard.press('ArrowRight')

  try {
    await waitForSlideRoute(page, next.no, Math.min(options.timeoutMs, 6000))
    await page.waitForTimeout(options.transitionMs)
    await waitForSlideReady(page, options.timeoutMs)
  }
  catch (error) {
    warnings.push(`Could not reach slide ${next.no} with one native ArrowRight transition; fell back to direct navigation. ${(error as Error).message}`)
    await gotoSlide(page, baseUrl, next, options)
  }
}

async function waitForSlideRoute(page: any, slideNo: number, timeoutMs: number) {
  await page.waitForFunction((expectedSlideNo: number) => {
    const path = window.location.pathname.replace(/\/+$/, '')
    const hash = window.location.hash
    const candidates = [
      path.match(/\/(\d+)$/)?.[1],
      hash.match(/#\/?(\d+)/)?.[1],
      new URLSearchParams(window.location.search).get('slide'),
    ].filter(Boolean)

    return candidates.includes(String(expectedSlideNo))
      || (expectedSlideNo === 1 && (path === '' || path === '/'))
  }, slideNo, { timeout: timeoutMs })
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
      if (response.ok)
        return
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

async function inspectSlide(page: any): Promise<SlideInspection> {
  return await page.evaluate(() => {
    const visible = (node: Element) => {
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
    const hashText = (text: string) => {
      let hash = 2166136261
      for (let index = 0; index < text.length; index++) {
        hash ^= text.charCodeAt(index)
        hash = Math.imul(hash, 16777619)
      }
      return String(hash >>> 0)
    }
    const layouts = [...document.querySelectorAll('.slidev-layout')]
      .filter(visible)
      .sort((first, second) => {
        const firstRect = first.getBoundingClientRect()
        const secondRect = second.getBoundingClientRect()
        return (secondRect.width * secondRect.height) - (firstRect.width * firstRect.height)
      })
    const layout = layouts[0]
    const warnings: string[] = []

    if (!layout) {
      return {
        hasLayout: false,
        hasVisibleContent: false,
        visibleElementCount: 0,
        textLength: 0,
        canvasCount: 0,
        nonblankCanvasCount: 0,
        svgCount: 0,
        mediaCount: 0,
        overflowCount: 0,
        horizontalOverflowCount: 0,
        viewportOverflow: 0,
        visualHash: 'no-layout',
        warnings,
      }
    }

    const layoutRect = layout.getBoundingClientRect()
    const visibleElements = [...layout.querySelectorAll('*')].filter(visible)
    const textLength = (layout.textContent || '').replace(/\s+/g, ' ').trim().length
    const canvases = [...layout.querySelectorAll('canvas')].filter(visible) as HTMLCanvasElement[]
    const svgs = [...layout.querySelectorAll('svg')].filter(visible)
    const media = [...layout.querySelectorAll('img,video,iframe,object,embed')].filter(visible)
    const canvasStates = canvases.map((canvas) => sampleCanvas(canvas, hashText, warnings))
    const svgHashes = svgs.map((svg) => hashText(new XMLSerializer().serializeToString(svg).slice(0, 200000)))
    const motionSignature = visibleElements.slice(0, 240).map((node) => {
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
        style.clipPath,
      ].join(':')
    }).join('|')
    const overflow = [...layout.querySelectorAll('p, li, h1, h2, h3, h4, span, strong, code, pre')]
      .filter((node) => visible(node) && (node.scrollWidth > (node as HTMLElement).clientWidth + 8 || node.scrollHeight > (node as HTMLElement).clientHeight + 8))
    const horizontalOverflow = visibleElements.filter((node) => {
      const rect = node.getBoundingClientRect()
      return rect.right > layoutRect.right + 2 || rect.left < layoutRect.left - 2
    })
    const viewportOverflow = Math.max(
      0,
      document.documentElement.scrollWidth - document.documentElement.clientWidth,
      document.body.scrollWidth - document.body.clientWidth,
    )
    const nonblankCanvasCount = canvasStates.filter((state) => state.nonblank).length
    const hasVisibleContent = textLength > 4 || media.length > 0 || svgs.length > 0 || nonblankCanvasCount > 0 || visibleElements.length > 5
    const visualHash = hashText([
      textLength,
      layout.innerText,
      motionSignature,
      canvasStates.map((state) => state.hash).join(','),
      svgHashes.join(','),
      media.length,
    ].join('|'))

    return {
      hasLayout: true,
      hasVisibleContent,
      visibleElementCount: visibleElements.length,
      textLength,
      canvasCount: canvases.length,
      nonblankCanvasCount,
      svgCount: svgs.length,
      mediaCount: media.length,
      overflowCount: overflow.length,
      horizontalOverflowCount: horizontalOverflow.length,
      viewportOverflow,
      visualHash,
      warnings,
    }

    function sampleCanvas(canvas: HTMLCanvasElement, hashTextFn: (text: string) => string, warningList: string[]) {
      const context = canvas.getContext('2d', { willReadFrequently: true })
      if (!context || canvas.width === 0 || canvas.height === 0)
        return { nonblank: false, hash: 'empty-canvas' }

      try {
        const data = context.getImageData(0, 0, canvas.width, canvas.height).data
        let colored = 0
        let opaque = 0
        let sample = ''
        const stride = Math.max(4, Math.floor(data.length / 6000))
        for (let index = 0; index < data.length; index += stride - (stride % 4)) {
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
        return { nonblank: opaque > 20 && colored > 10, hash: hashTextFn(sample) }
      }
      catch (error) {
        warningList.push(`Canvas could not be sampled: ${(error as Error).message}`)
        return { nonblank: true, hash: 'tainted-canvas' }
      }
    }
  })
}

function collectFailures(results: any[], consoleIssues: string[], pageErrors: string[], options: Options) {
  const failures: string[] = []

  for (const result of results) {
    if (!result.visibleElementCount)
      failures.push(`Slide ${result.slide}: no visible Slidev layout was found.`)
    if (!result.textLength && result.mediaCount === 0 && result.svgCount === 0 && result.nonblankCanvasCount === 0)
      failures.push(`Slide ${result.slide}: slide has no visible content.`)
    if (options.requireClickChange && result.clicksRecorded > 0 && result.changedAfterClicks === false)
      failures.push(`Slide ${result.slide}: did not visibly change after recorded clicks.`)
    if (options.strictOverflow && (result.overflowCount > 0 || result.horizontalOverflowCount > 0 || result.viewportOverflow > 1))
      failures.push(`Slide ${result.slide}: detected text or horizontal overflow.`)
  }

  for (const issue of consoleIssues)
    failures.push(`Browser console error: ${issue}`)
  for (const error of pageErrors)
    failures.push(`Page error: ${error}`)

  return failures
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

async function convertToMp4(input: string, output: string, options: Options, trimStartMs: number) {
  await rm(output, { force: true })
  const args = [
    '-y',
    '-i',
    input,
  ]

  if (trimStartMs > 0)
    args.push('-ss', seconds(trimStartMs))

  args.push(
    '-vf',
    `scale=${options.width}:${options.height}:flags=lanczos,fps=30`,
    '-pix_fmt',
    'yuv420p',
    '-c:v',
    'libx264',
    '-preset',
    'veryfast',
    '-crf',
    '18',
    '-movflags',
    '+faststart',
    output,
  )

  await runCommand('ffmpeg', args)
}

async function createContactSheet(inputDir: string, output: string, slideCount: number) {
  if (slideCount <= 0)
    return

  const columns = Math.min(5, Math.ceil(Math.sqrt(slideCount)))
  const rows = Math.ceil(slideCount / columns)
  await rm(output, { force: true })
  await runCommand('ffmpeg', [
    '-y',
    '-framerate',
    '1',
    '-i',
    resolve(inputDir, 'slide-%03d.png'),
    '-vf',
    `scale=320:-1,tile=${columns}x${rows}:padding=8:margin=8:color=white`,
    '-frames:v',
    '1',
    output,
  ])
}

async function runCommand(command: string, args: string[]) {
  await new Promise<void>((resolvePromise, reject) => {
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'] })
    let stderr = ''
    child.stderr?.on('data', (chunk) => {
      stderr += chunk
    })
    child.on('exit', (code) => {
      if (code === 0)
        resolvePromise()
      else
        reject(new Error(`${command} exited with code ${code}: ${stderr}`))
    })
  })
}

function commandExists(command: string) {
  const result = spawnSync(command, ['-version'], { stdio: 'ignore' })
  return result.status === 0
}

async function moveFile(source: string, target: string) {
  try {
    await rename(source, target)
  }
  catch {
    await copyFile(source, target)
    await rm(source, { force: true })
  }
}

function sanitizeName(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'slidev-deck'
}

function seconds(ms: number) {
  return (ms / 1000).toFixed(3)
}

function relativeToCwd(path: string) {
  return relative(invocationCwd, path).replaceAll('\\', '/')
}

function delay(ms: number) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, ms))
}
