#!/usr/bin/env node
import { spawn, spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { createServer } from 'node:net'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const __dirname = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(__dirname, '..')
const repoRoot = resolve(projectRoot, '..', '..', '..', '..', '..', '..')

const defaults = {
  port: 3030,
  width: 1280,
  height: 720,
  dwellMs: 650,
  clickDwellMs: 900,
  outDir: resolve(repoRoot, 'projects', 'slidev-echarts-validation', 'artifacts', 'videos'),
  channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge',
  maxClicks: undefined,
  skipVideo: false,
  keepWebm: true,
}

const args = parseArgs(process.argv.slice(2))
const options = { ...defaults, ...args }
options.port = await findAvailablePort(options.port)
const baseUrl = `http://localhost:${options.port}`
const videoSize = { width: options.width, height: options.height }
const slides = await parseSlides(resolve(projectRoot, 'slides.md'))
const screenshotsDir = resolve(options.outDir, 'slides')
const rawVideoDir = resolve(options.outDir, 'raw')
const webmPath = resolve(options.outDir, 'slidev-echarts-auto.webm')
const mp4Path = resolve(options.outDir, 'slidev-echarts-auto.mp4')
const manifestPath = resolve(options.outDir, 'recording-manifest.json')

await mkdir(options.outDir, { recursive: true })
await rm(screenshotsDir, { recursive: true, force: true })
await rm(rawVideoDir, { recursive: true, force: true })
await mkdir(screenshotsDir, { recursive: true })
await mkdir(rawVideoDir, { recursive: true })

let server
let browser
let context
let page

try {
  server = await startSlidevServer(options.port)
  await waitForServer(baseUrl)

  browser = await launchBrowser(options.channel)
  context = await browser.newContext({
    viewport: videoSize,
    deviceScaleFactor: 1,
    recordVideo: options.skipVideo ? undefined : { dir: rawVideoDir, size: videoSize },
  })
  page = await context.newPage()

  const consoleIssues = []
  const consoleWarnings = []
  const pageErrors = []
  page.on('console', (message) => {
    if (message.type() === 'error')
      consoleIssues.push(message.text())
    else if ((message.type() === 'warning' || message.type() === 'warn') && !isIgnoredConsoleWarning(message.text()))
      consoleWarnings.push(message.text())
  })
  page.on('pageerror', (error) => pageErrors.push(error.message))

  const results = []

  for (const slide of slides) {
    const clicksToRun = Math.min(slide.clicks, options.maxClicks ?? slide.clicks)
    const slideUrl = `${baseUrl}/${slide.no}?embedded=true&clicks=0`

    await page.goto(slideUrl, { waitUntil: 'networkidle', timeout: 30000 })
    await waitForSlideReady(page)
    await page.waitForTimeout(options.dwellMs)

    const initial = await inspectSlide(page)

    for (let click = 0; click < clicksToRun; click++) {
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(options.clickDwellMs)
    }

    const final = await inspectSlide(page)
    const replay = await inspectReplay(page)
    await page.waitForTimeout(options.clickDwellMs)
    const screenshotPath = resolve(screenshotsDir, `slide-${String(slide.no).padStart(3, '0')}.png`)
    await page.screenshot({ path: screenshotPath, fullPage: false })

    results.push({
      slide: slide.no,
      title: slide.title,
      clicksAvailable: slide.clicks,
      clicksRecorded: clicksToRun,
      expectedCharts: slide.expectedCharts,
      expectedSvgCharts: slide.expectedSvgCharts,
      expectedGeneratedSvgs: slide.expectedGeneratedSvgs,
      visibleCharts: final.visibleCharts,
      nonblankCharts: final.nonblankCharts,
      svgCharts: final.svgCharts,
      svgReplayableCharts: final.svgReplayableCharts,
      svgMarkCount: final.svgMarkCount,
      svgTextCount: final.svgTextCount,
      svgEmptyPathCount: final.svgEmptyPathCount,
      generatedSvgDemos: final.generatedSvgDemos,
      generatedSvgReplayableDemos: final.generatedSvgReplayableDemos,
      generatedSvgMarkCount: final.generatedSvgMarkCount,
      generatedSvgTextCount: final.generatedSvgTextCount,
      generatedSvgEmptyPathCount: final.generatedSvgEmptyPathCount,
      changedAfterClicks: (slide.expectedCharts > 0 || slide.expectedGeneratedSvgs > 0) && clicksToRun > 0
        ? initial.surfaceHash !== final.surfaceHash
        : null,
      replay,
      overflowCount: final.overflow.length,
      horizontalOverflowCount: final.horizontalOverflow.length,
      verticalOverflowCount: final.verticalOverflow.length,
      viewportOverflow: final.viewportOverflow,
      contentMargins: final.contentMargins,
      screenshot: relativeOutputPath(screenshotPath),
      initialSurfaceHash: initial.surfaceHash,
      finalSurfaceHash: final.surfaceHash,
      overflow: final.overflow.slice(0, 8),
      horizontalOverflow: final.horizontalOverflow.slice(0, 8),
      verticalOverflow: final.verticalOverflow.slice(0, 8),
    })
  }

  const video = page.video()
  await context.close()
  context = undefined
  await browser.close()
  browser = undefined

  if (video && !options.skipVideo) {
    const recordedPath = await video.path()
    await rm(webmPath, { force: true })
    await moveFile(recordedPath, webmPath)
    await convertToMp4(webmPath, mp4Path)
    if (!options.keepWebm)
      await rm(webmPath, { force: true })
  }

  const failures = collectFailures(results, consoleIssues, consoleWarnings, pageErrors)
  const manifest = {
    generatedAt: new Date().toISOString(),
    baseUrl,
    viewport: videoSize,
    slideCount: slides.length,
    recordedStates: results.reduce((total, result) => total + 1 + result.clicksRecorded, 0),
    video: options.skipVideo
      ? null
      : {
          webm: options.keepWebm ? relativeOutputPath(webmPath) : null,
          mp4: existsSync(mp4Path) ? relativeOutputPath(mp4Path) : null,
        },
    failures,
    consoleIssues,
    consoleWarnings,
    pageErrors,
    results,
  }

  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8')
  console.log(`Recorded ${manifest.slideCount} slides and ${manifest.recordedStates} visual states.`)
  if (!options.skipVideo)
    console.log(`MP4 video: ${mp4Path}`)
  console.log(`Manifest: ${manifestPath}`)

  if (failures.length) {
    console.error(`Verification failed with ${failures.length} issue(s).`)
    for (const failure of failures.slice(0, 12))
      console.error(`- ${failure}`)
    process.exitCode = 1
  }
}
finally {
  await context?.close().catch(() => {})
  await browser?.close().catch(() => {})
  stopServer(server)
}

function parseArgs(argv) {
  const parsed = {}

  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index]
    const next = argv[index + 1]

    if (arg === '--skip-video') {
      parsed.skipVideo = true
    }
    else if (arg === '--no-webm') {
      parsed.keepWebm = false
    }
    else if (arg === '--port') {
      parsed.port = Number(next)
      index++
    }
    else if (arg === '--width') {
      parsed.width = Number(next)
      index++
    }
    else if (arg === '--height') {
      parsed.height = Number(next)
      index++
    }
    else if (arg === '--dwell') {
      parsed.dwellMs = Number(next)
      index++
    }
    else if (arg === '--click-dwell') {
      parsed.clickDwellMs = Number(next)
      index++
    }
    else if (arg === '--out') {
      parsed.outDir = resolve(projectRoot, next)
      index++
    }
    else if (arg === '--channel') {
      parsed.channel = next === 'none' ? undefined : next
      index++
    }
    else if (arg === '--max-clicks') {
      parsed.maxClicks = Number(next)
      index++
    }
    else {
      throw new Error(`Unknown argument: ${arg}`)
    }
  }

  return parsed
}

async function parseSlides(slidesPath) {
  const markdown = await readFile(slidesPath, 'utf8')
  const withoutFrontmatter = markdown.replace(/^---\n[\s\S]*?\n---\n/, '')
  const sections = withoutFrontmatter.split(/\n---\n/g)

  return sections.map((section, index) => ({
    no: index + 1,
    title: section.match(/^#\s+(.+)$/m)?.[1]?.trim() || `Slide ${index + 1}`,
    clicks: countVClicks(section),
    expectedCharts: expectedChartCount(section),
    expectedSvgCharts: section.includes('<ChartTypeSlide') ? 1 : 0,
    expectedGeneratedSvgs: section.includes('<GeneratedSvgMotion') ? 1 : 0,
  }))
}

function countVClicks(section) {
  const blocks = [...section.matchAll(/<v-clicks[\s\S]*?<\/v-clicks>/g)]
  return blocks.reduce((total, block) => {
    const bullets = block[0].split('\n').filter(line => /^\s*-\s+/.test(line)).length
    return total + bullets
  }, 0)
}

function expectedChartCount(section) {
  if (section.includes('<ExecutiveDashboard'))
    return 3
  if (section.includes('scene="comparison"'))
    return 2
  if (
    section.includes('<ChartTypeSlide')
    || section.includes('<RevenueStory')
    || section.includes('<MarketMixChart')
    || section.includes('scene="spotlight"')
  ) {
    return 1
  }
  return 0
}

async function startSlidevServer(port) {
  const command = process.platform === 'win32' ? 'cmd.exe' : 'npx'
  const args = process.platform === 'win32'
    ? ['/d', '/s', '/c', `npx slidev --port ${port} --log warn`]
    : ['slidev', '--port', String(port), '--log', 'warn']
  const child = spawn(command, args, {
    cwd: projectRoot,
    env: { ...process.env, FORCE_COLOR: '0' },
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  child.stdout.on('data', (chunk) => process.stdout.write(chunk))
  child.stderr.on('data', (chunk) => process.stderr.write(chunk))
  child.on('exit', (code) => {
    if (code && code !== 0 && !child.slidevStopping)
      console.error(`Slidev server exited with code ${code}.`)
  })

  return child
}

async function findAvailablePort(startPort) {
  for (let port = startPort; port < startPort + 50; port++) {
    if (await canBind(port))
      return port
  }

  throw new Error(`No available port found from ${startPort} to ${startPort + 49}.`)
}

async function canBind(port) {
  const ipv4 = await canBindHost(port, '127.0.0.1')
  const ipv6 = await canBindHost(port, '::1')
  return ipv4 && ipv6
}

async function canBindHost(port, host) {
  return await new Promise((resolvePromise) => {
    const server = createServer()
    server.once('error', () => resolvePromise(false))
    server.once('listening', () => {
      server.close(() => resolvePromise(true))
    })
    server.listen(port, host)
  })
}

async function waitForServer(url) {
  const started = Date.now()
  let lastError

  while (Date.now() - started < 30000) {
    try {
      const response = await fetch(url)
      if (response.ok)
        return
    }
    catch (error) {
      lastError = error
    }
    await delay(300)
  }

  throw new Error(`Timed out waiting for Slidev at ${url}. ${lastError?.message || ''}`)
}

async function launchBrowser(channel) {
  if (channel) {
    try {
      return await chromium.launch({ channel, headless: true })
    }
    catch (error) {
      console.warn(`Could not launch browser channel "${channel}": ${error.message}`)
    }
  }

  return await chromium.launch({ headless: true })
}

async function waitForSlideReady(page) {
  await page.waitForFunction(() => {
    const layout = [...document.querySelectorAll('.slidev-layout')].find((candidate) => {
      const style = getComputedStyle(candidate)
      const rect = candidate.getBoundingClientRect()
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 400 && rect.height > 300
    })
    if (!layout)
      return false
    return true
  }, null, { timeout: 30000 })
  await page.waitForTimeout(250)
}

async function inspectSlide(page) {
  return await page.evaluate(() => {
    const layout = [...document.querySelectorAll('.slidev-layout')]
      .filter((candidate) => {
        const rect = candidate.getBoundingClientRect()
        const style = getComputedStyle(candidate)
        return style.visibility !== 'hidden'
          && style.display !== 'none'
          && rect.width > 400
          && rect.height > 300
          && rect.bottom > 0
          && rect.right > 0
          && rect.top < innerHeight
          && rect.left < innerWidth
      })
      .sort((first, second) => {
        const firstRect = first.getBoundingClientRect()
        const secondRect = second.getBoundingClientRect()
        return (secondRect.width * secondRect.height) - (firstRect.width * firstRect.height)
      })[0]
    const layoutRect = layout?.getBoundingClientRect()
    const frames = [...document.querySelectorAll('.echart-frame')]
      .filter((frame) => {
        const rect = frame.getBoundingClientRect()
        return rect.width > 80 && rect.height > 80 && rect.bottom > 0 && rect.right > 0 && rect.top < innerHeight && rect.left < innerWidth
      })
    const generatedFrames = [...document.querySelectorAll('.generated-svg-frame')]
      .filter((frame) => {
        const rect = frame.getBoundingClientRect()
        return rect.width > 80 && rect.height > 80 && rect.bottom > 0 && rect.right > 0 && rect.top < innerHeight && rect.left < innerWidth
      })

    const surfaces = frames.map(surfaceState)
    const svgSurfaces = surfaces.filter((surface) => surface.tag === 'svg')
    const generatedSurfaces = generatedFrames.map(surfaceState)
    const generatedSvgSurfaces = generatedSurfaces.filter((surface) => surface.tag === 'svg')
    const overflow = [...document.querySelectorAll('.slidev-layout p, .slidev-layout li, .slidev-layout h1, .slidev-layout h2, .slidev-layout h3, .slidev-layout span, .slidev-layout strong, .slidev-layout code')]
      .filter((node) => {
        const rect = node.getBoundingClientRect()
        if (rect.width < 8 || rect.height < 8 || rect.bottom < 0 || rect.right < 0 || rect.top > innerHeight || rect.left > innerWidth)
          return false
        return node.scrollWidth > node.clientWidth + 8 || node.scrollHeight > node.clientHeight + 8
      })
      .map((node) => ({
        tag: node.tagName.toLowerCase(),
        text: (node.textContent || '').trim().slice(0, 90),
        client: [node.clientWidth, node.clientHeight],
        scroll: [node.scrollWidth, node.scrollHeight],
      }))
    const horizontalOverflow = layout && layoutRect
      ? [...layout.querySelectorAll('*')]
          .filter((node) => {
            const rect = node.getBoundingClientRect()
            if (rect.width < 2 || rect.height < 2 || rect.bottom < 0 || rect.right < 0 || rect.top > innerHeight || rect.left > innerWidth)
              return false
            return rect.right > layoutRect.right + 2 || rect.left < layoutRect.left - 2
          })
          .map((node) => {
            const rect = node.getBoundingClientRect()
            return {
              tag: node.tagName.toLowerCase(),
              className: typeof node.className === 'string' ? node.className.slice(0, 80) : '',
              text: (node.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90),
              leftOverflow: Math.max(0, Math.round(layoutRect.left - rect.left)),
              rightOverflow: Math.max(0, Math.round(rect.right - layoutRect.right)),
              width: Math.round(rect.width),
            }
          })
      : []
    const verticalOverflow = layout && layoutRect
      ? [...layout.querySelectorAll('*')]
          .filter((node) => {
            const rect = node.getBoundingClientRect()
            if (rect.width < 2 || rect.height < 2 || rect.bottom < 0 || rect.right < 0 || rect.top > innerHeight || rect.left > innerWidth)
              return false
            return rect.bottom > layoutRect.bottom + 2 || rect.top < layoutRect.top - 2
          })
          .map((node) => {
            const rect = node.getBoundingClientRect()
            return {
              tag: node.tagName.toLowerCase(),
              className: typeof node.className === 'string' ? node.className.slice(0, 80) : '',
              text: (node.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90),
              topOverflow: Math.max(0, Math.round(layoutRect.top - rect.top)),
              bottomOverflow: Math.max(0, Math.round(rect.bottom - layoutRect.bottom)),
              height: Math.round(rect.height),
            }
          })
      : []
    const visibleNodes = layout && layoutRect
      ? [...layout.querySelectorAll('*')]
          .map((node) => {
            const rect = node.getBoundingClientRect()
            const style = getComputedStyle(node)
            if (
              style.display === 'none'
              || style.visibility === 'hidden'
              || Number(style.opacity) === 0
              || rect.width < 2
              || rect.height < 2
              || rect.bottom < layoutRect.top
              || rect.top > layoutRect.bottom
              || rect.right < layoutRect.left
              || rect.left > layoutRect.right
            ) {
              return null
            }
            return rect
          })
          .filter(Boolean)
      : []
    const contentMargins = layoutRect && visibleNodes.length
      ? {
          left: Math.round(Math.min(...visibleNodes.map((rect) => rect.left)) - layoutRect.left),
          top: Math.round(Math.min(...visibleNodes.map((rect) => rect.top)) - layoutRect.top),
          right: Math.round(layoutRect.right - Math.max(...visibleNodes.map((rect) => rect.right))),
          bottom: Math.round(layoutRect.bottom - Math.max(...visibleNodes.map((rect) => rect.bottom))),
        }
      : null
    const viewportOverflow = Math.max(
      0,
      document.documentElement.scrollWidth - document.documentElement.clientWidth,
      document.body.scrollWidth - document.body.clientWidth,
    )

    return {
      visibleCharts: frames.length,
      nonblankCharts: surfaces.filter((surface) => surface.nonblank).length,
      svgCharts: svgSurfaces.length,
      svgReplayableCharts: surfaces.filter((surface) => surface.replayable).length,
      svgMarkCount: svgSurfaces.reduce((total, surface) => total + surface.svgMarkCount, 0),
      svgTextCount: svgSurfaces.reduce((total, surface) => total + surface.svgTextCount, 0),
      svgEmptyPathCount: svgSurfaces.reduce((total, surface) => total + surface.svgEmptyPathCount, 0),
      generatedSvgDemos: generatedSvgSurfaces.length,
      generatedSvgReplayableDemos: generatedSurfaces.filter((surface) => surface.replayable).length,
      generatedSvgMarkCount: generatedSvgSurfaces.reduce((total, surface) => total + surface.svgMarkCount, 0),
      generatedSvgTextCount: generatedSvgSurfaces.reduce((total, surface) => total + surface.svgTextCount, 0),
      generatedSvgEmptyPathCount: generatedSvgSurfaces.reduce((total, surface) => total + surface.svgEmptyPathCount, 0),
      surfaceHash: [...surfaces, ...generatedSurfaces].map((surface) => surface.hash).join('|') || 'no-surface',
      surfaces,
      overflow,
      horizontalOverflow,
      verticalOverflow,
      contentMargins,
      viewportOverflow,
    }

    function surfaceState(frame) {
      const canvases = [...frame.querySelectorAll('canvas')]
      const svg = frame.querySelector('svg')
      const rect = frame.getBoundingClientRect()
      const state = {
        tag: canvases.length ? 'canvas' : svg ? 'svg' : 'none',
        renderer: frame.dataset.renderer || 'unknown',
        replayable: frame.dataset.svgReplayable === 'true',
        rect: { width: Math.round(rect.width), height: Math.round(rect.height) },
        nonblank: false,
        hash: 'none',
        colored: 0,
        opaque: 0,
        svgMarkCount: 0,
        svgTextCount: 0,
        svgEmptyPathCount: 0,
        svgHasViewBox: false,
        svgHasSize: false,
      }

      if (canvases.length) {
        let hash = 2166136261

        for (const canvas of canvases) {
          const context = canvas.getContext('2d', { willReadFrequently: true })
          const { width, height } = canvas
          if (!context || width === 0 || height === 0)
            continue

          const data = context.getImageData(0, 0, width, height).data
          for (let index = 0; index < data.length; index += 24) {
            const r = data[index]
            const g = data[index + 1]
            const b = data[index + 2]
            const a = data[index + 3]
            hash ^= r + (g << 8) + (b << 16) + (a << 24)
            hash = Math.imul(hash, 16777619)
            if (a > 0)
              state.opaque++
            if (a > 0 && (Math.abs(r - 255) > 8 || Math.abs(g - 255) > 8 || Math.abs(b - 255) > 8))
              state.colored++
          }
        }

        state.hash = String(hash >>> 0)
        state.nonblank = state.opaque > 100 && state.colored > 80
      }
      else if (svg) {
        const serialized = new XMLSerializer().serializeToString(svg)
        let hash = 2166136261
        for (let index = 0; index < serialized.length; index++) {
          hash ^= serialized.charCodeAt(index)
          hash = Math.imul(hash, 16777619)
        }
        state.hash = String(hash >>> 0)
        state.svgMarkCount = svg.querySelectorAll('path,line,rect,circle,ellipse,text,polygon,polyline').length
        state.svgTextCount = svg.querySelectorAll('text').length
        state.svgEmptyPathCount = svg.querySelectorAll('path[d=""]').length
        state.svgHasViewBox = svg.hasAttribute('viewBox')
        state.svgHasSize = state.svgHasViewBox
          || (Number(svg.getAttribute('width')) > 0 && Number(svg.getAttribute('height')) > 0)
          || (rect.width > 80 && rect.height > 80)
        state.colored = state.svgMarkCount
        state.opaque = state.colored
        state.nonblank = state.colored > 5 && state.svgHasSize
      }

      return state
    }
  })
}

async function inspectReplay(page) {
  const before = await page.evaluate(() => {
    return replayState()

    function replayState() {
      const frames = visibleElements(document.querySelectorAll('.echart-frame[data-svg-replayable="true"], .generated-svg-frame[data-svg-replayable="true"]'))
        .map((frame) => ({
          renderer: frame.dataset.renderer || 'unknown',
          isReplaying: frame.classList.contains('is-replaying'),
          animatedMarks: [...frame.querySelectorAll('svg path, svg rect, svg circle, svg ellipse, svg line, svg polyline, svg polygon, svg text')]
            .filter((mark) => getComputedStyle(mark).animationName !== 'none').length,
        }))

      return {
        buttonCount: visibleElements(document.querySelectorAll('[data-svg-replay-button]')).length,
        frames,
      }
    }

    function visibleElements(nodes) {
      return [...nodes].filter((node) => {
        const rect = node.getBoundingClientRect()
        const style = getComputedStyle(node)
        return style.visibility !== 'hidden'
          && style.display !== 'none'
          && rect.width > 2
          && rect.height > 2
          && rect.bottom > 0
          && rect.right > 0
          && rect.top < innerHeight
          && rect.left < innerWidth
      })
    }
  })
  await page.evaluate(() => {
    function visibleElements(nodes) {
      return [...nodes].filter((node) => {
        const rect = node.getBoundingClientRect()
        const style = getComputedStyle(node)
        return style.visibility !== 'hidden'
          && style.display !== 'none'
          && rect.width > 2
          && rect.height > 2
          && rect.bottom > 0
          && rect.right > 0
          && rect.top < innerHeight
          && rect.left < innerWidth
      })
    }

    for (const button of visibleElements(document.querySelectorAll('[data-svg-replay-button]')))
      button.click()
  })
  await page.waitForTimeout(120)
  const after = await page.evaluate(() => {
    return replayState()

    function replayState() {
      const frames = visibleElements(document.querySelectorAll('.echart-frame[data-svg-replayable="true"], .generated-svg-frame[data-svg-replayable="true"]'))
        .map((frame) => ({
          renderer: frame.dataset.renderer || 'unknown',
          isReplaying: frame.classList.contains('is-replaying'),
          animatedMarks: [...frame.querySelectorAll('svg path, svg rect, svg circle, svg ellipse, svg line, svg polyline, svg polygon, svg text')]
            .filter((mark) => getComputedStyle(mark).animationName !== 'none').length,
        }))

      return {
        buttonCount: visibleElements(document.querySelectorAll('[data-svg-replay-button]')).length,
        frames,
      }
    }

    function visibleElements(nodes) {
      return [...nodes].filter((node) => {
        const rect = node.getBoundingClientRect()
        const style = getComputedStyle(node)
        return style.visibility !== 'hidden'
          && style.display !== 'none'
          && rect.width > 2
          && rect.height > 2
          && rect.bottom > 0
          && rect.right > 0
          && rect.top < innerHeight
          && rect.left < innerWidth
      })
    }
  })

  return {
    buttonCount: before.buttonCount,
    replayableFrames: after.frames.length,
    replayingFrames: after.frames.filter((frame) => frame.isReplaying).length,
    activeAnimatedFrames: after.frames.filter((frame) => frame.animatedMarks > 0).length,
    frames: after.frames,
  }
}

function collectFailures(results, consoleIssues, consoleWarnings, pageErrors) {
  const failures = []

  for (const result of results) {
    if (result.expectedCharts > result.visibleCharts) {
      failures.push(`Slide ${result.slide} expected ${result.expectedCharts} chart surface(s), saw ${result.visibleCharts}.`)
    }
    if (result.expectedCharts > result.nonblankCharts) {
      failures.push(`Slide ${result.slide} expected ${result.expectedCharts} nonblank chart surface(s), saw ${result.nonblankCharts}.`)
    }
    if (result.expectedSvgCharts > result.svgCharts) {
      failures.push(`Slide ${result.slide} expected ${result.expectedSvgCharts} SVG chart surface(s), saw ${result.svgCharts}.`)
    }
    if (result.expectedSvgCharts > result.svgReplayableCharts) {
      failures.push(`Slide ${result.slide} expected ${result.expectedSvgCharts} replayable SVG chart surface(s), saw ${result.svgReplayableCharts}.`)
    }
    if (result.expectedSvgCharts > 0 && result.svgMarkCount < 12) {
      failures.push(`Slide ${result.slide} SVG chart has too few drawable marks (${result.svgMarkCount}).`)
    }
    if (result.expectedSvgCharts > 0 && result.svgTextCount < 1) {
      failures.push(`Slide ${result.slide} SVG chart has no visible text nodes.`)
    }
    if (result.expectedSvgCharts > 0 && result.svgEmptyPathCount > 0) {
      failures.push(`Slide ${result.slide} SVG chart has ${result.svgEmptyPathCount} empty path(s); capture may have happened before ECharts settled.`)
    }
    if (result.expectedGeneratedSvgs > result.generatedSvgDemos) {
      failures.push(`Slide ${result.slide} expected ${result.expectedGeneratedSvgs} generated SVG demo(s), saw ${result.generatedSvgDemos}.`)
    }
    if (result.expectedGeneratedSvgs > result.generatedSvgReplayableDemos) {
      failures.push(`Slide ${result.slide} expected ${result.expectedGeneratedSvgs} replayable generated SVG demo(s), saw ${result.generatedSvgReplayableDemos}.`)
    }
    if (result.expectedGeneratedSvgs > 0 && result.generatedSvgMarkCount < 18) {
      failures.push(`Slide ${result.slide} generated SVG demo has too few drawable marks (${result.generatedSvgMarkCount}).`)
    }
    if (result.expectedGeneratedSvgs > 0 && result.generatedSvgTextCount < 2) {
      failures.push(`Slide ${result.slide} generated SVG demo has too few text labels (${result.generatedSvgTextCount}).`)
    }
    if (result.expectedGeneratedSvgs > 0 && result.generatedSvgEmptyPathCount > 0) {
      failures.push(`Slide ${result.slide} generated SVG demo has ${result.generatedSvgEmptyPathCount} empty path(s).`)
    }
    if (result.expectedSvgCharts > 0 && result.replay.buttonCount < result.expectedSvgCharts) {
      failures.push(`Slide ${result.slide} expected ${result.expectedSvgCharts} SVG replay button(s), saw ${result.replay.buttonCount}.`)
    }
    if (result.expectedSvgCharts > 0 && result.replay.activeAnimatedFrames < result.expectedSvgCharts) {
      failures.push(`Slide ${result.slide} SVG replay did not activate animations on every replayable chart.`)
    }
    if (result.expectedGeneratedSvgs > 0 && result.replay.buttonCount < result.expectedGeneratedSvgs) {
      failures.push(`Slide ${result.slide} expected ${result.expectedGeneratedSvgs} generated SVG replay button(s), saw ${result.replay.buttonCount}.`)
    }
    if (result.expectedGeneratedSvgs > 0 && result.replay.activeAnimatedFrames < result.expectedGeneratedSvgs) {
      failures.push(`Slide ${result.slide} generated SVG replay did not activate animations on every replayable demo.`)
    }
    if (result.changedAfterClicks === false) {
      failures.push(`Slide ${result.slide} chart surface did not change after recorded clicks.`)
    }
    if (result.overflowCount > 0) {
      failures.push(`Slide ${result.slide} has ${result.overflowCount} visible text overflow candidate(s).`)
    }
    if (result.horizontalOverflowCount > 0 || result.viewportOverflow > 1) {
      failures.push(`Slide ${result.slide} has visible horizontal overflow.`)
    }
    if (result.verticalOverflowCount > 0) {
      failures.push(`Slide ${result.slide} has visible vertical overflow.`)
    }
    if (result.contentMargins && result.contentMargins.bottom < 8) {
      failures.push(`Slide ${result.slide} has less than 8px of bottom margin.`)
    }
  }

  for (const issue of consoleIssues)
    failures.push(`Browser console error: ${issue}`)
  for (const warning of consoleWarnings) {
    if (/SVG render mode doesn't support/i.test(warning))
      failures.push(`Unsupported SVG renderer feature warning: ${warning}`)
  }
  for (const error of pageErrors)
    failures.push(`Page error: ${error}`)

  return failures
}

function isIgnoredConsoleWarning(text) {
  return /Canvas2D: Multiple readback operations using getImageData/i.test(text)
}

function stopServer(child) {
  if (!child?.pid)
    return

  if (process.platform === 'win32') {
    child.slidevStopping = true
    spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' })
    return
  }

  child.slidevStopping = true
  child.kill()
}

async function convertToMp4(input, output) {
  await rm(output, { force: true })
  await runCommand('ffmpeg', [
    '-y',
    '-i',
    input,
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
  ])
}

async function runCommand(command, args) {
  await new Promise((resolvePromise, reject) => {
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'] })
    let stderr = ''
    child.stderr.on('data', (chunk) => {
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

async function moveFile(source, target) {
  const data = await readFile(source)
  await writeFile(target, data)
  await rm(source, { force: true })
}

function relativeOutputPath(path) {
  return path.replace(`${repoRoot}\\`, '').replaceAll('\\', '/')
}

function delay(ms) {
  return new Promise(resolvePromise => setTimeout(resolvePromise, ms))
}
