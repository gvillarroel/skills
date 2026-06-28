import { spawn } from 'node:child_process'
import { mkdir } from 'node:fs/promises'
import net from 'node:net'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const __dirname = dirname(fileURLToPath(import.meta.url))
const exampleRoot = resolve(__dirname, '..')
const repoRoot = resolve(exampleRoot, '..', '..', '..', '..', '..', '..')
const outputDir = resolve(repoRoot, 'projects', 'threejs-animated-3d-validation', 'artifacts', 'screenshots')
const viteBin = resolve(exampleRoot, 'node_modules', 'vite', 'bin', 'vite.js')

await mkdir(outputDir, { recursive: true })

const port = await findOpenPort(4180)
const url = `http://127.0.0.1:${port}/`
const server = spawn(process.execPath, [
  viteBin,
  '--host',
  '127.0.0.1',
  '--port',
  String(port),
  '--strictPort',
], {
  cwd: exampleRoot,
  stdio: ['ignore', 'pipe', 'pipe'],
})

let serverLog = ''
server.stdout.on('data', (chunk) => {
  serverLog += chunk.toString()
})
server.stderr.on('data', (chunk) => {
  serverLog += chunk.toString()
})

const consoleIssues = []
const pageErrors = []
let browser

try {
  await waitForServer(url, server)
  browser = await chromium.launch()

  await verifyViewport({
    browser,
    url,
    label: 'desktop',
    viewport: { width: 1440, height: 1050 },
    screenshot: resolve(outputDir, 'gallery-desktop.png'),
    exerciseInteraction: true,
  })

  await verifyViewport({
    browser,
    url,
    label: 'mobile',
    viewport: { width: 390, height: 980 },
    screenshot: resolve(outputDir, 'gallery-mobile.png'),
    exerciseInteraction: false,
  })

  if (consoleIssues.length || pageErrors.length) {
    throw new Error([
      'Browser reported issues:',
      ...consoleIssues,
      ...pageErrors.map((message) => `pageerror: ${message}`),
    ].join('\n'))
  }

  console.log(JSON.stringify({
    ok: true,
    url,
    screenshots: [
      resolve(outputDir, 'gallery-desktop.png'),
      resolve(outputDir, 'gallery-mobile.png'),
    ],
  }, null, 2))
} finally {
  if (browser) await browser.close()
  server.kill()
}

async function verifyViewport({ browser, url, label, viewport, screenshot, exerciseInteraction }) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 })
  page.on('console', (message) => {
    if (['error', 'warning'].includes(message.type())) {
      const text = message.text()
      if (!isTransientWebGLMessage(text)) {
        consoleIssues.push(`${label} ${message.type()}: ${text}`)
      }
    }
  })
  page.on('pageerror', (error) => pageErrors.push(`${label}: ${error.stack || error.message}`))

  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.waitForFunction(() => window.__threeGalleryReady === true)
  await page.waitForSelector('canvas.three-canvas')
  await page.waitForTimeout(1500)

  const initial = await page.evaluate(() => {
    const shell = document.querySelector('.page-shell')
    const expected = Number(shell?.dataset.expectedExamples || 0)
    const cards = [...document.querySelectorAll('.example-card')]
    const canvases = [...document.querySelectorAll('canvas.three-canvas')]
    return {
      expected,
      cards: cards.length,
      canvases: canvases.length,
      replayButtons: document.querySelectorAll('.card-replay-button').length,
      replayIcons: document.querySelectorAll('.material-symbols-rounded').length,
      fontFamily: getComputedStyle(document.body).fontFamily,
      headings: cards.map((card) => card.querySelector('h2')?.textContent?.trim()),
      invalidExampleIds: cards
        .map((card) => card.dataset.exampleId || '')
        .filter((id) => !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id)),
      duplicateExampleIds: cards.length - new Set(cards.map((card) => card.dataset.exampleId || '')).size,
      cardsWithoutDomId: cards
        .filter((card) => card.id !== `example-${card.dataset.exampleId}`)
        .map((card) => card.dataset.sceneId),
      mismatchedSceneIds: cards
        .filter((card) => card.dataset.exampleId !== card.dataset.sceneId)
        .map((card) => card.dataset.sceneId),
      duplicateSceneIds: canvases.length - new Set(canvases.map((canvas) => canvas.dataset.sceneId)).size,
      smallFrames: canvases
        .filter((canvas) => {
          const box = canvas.getBoundingClientRect()
          return box.width < 260 || box.height < 210
        })
        .map((canvas) => canvas.dataset.sceneId),
    }
  })

  if (initial.expected !== 24)
    throw new Error(`${label}: expected page metadata to declare 24 examples, saw ${initial.expected}.`)
  if (initial.cards !== initial.expected || initial.canvases !== initial.expected)
    throw new Error(`${label}: expected ${initial.expected} cards and canvases, saw ${initial.cards} cards and ${initial.canvases} canvases.`)
  if (initial.replayButtons !== initial.expected)
    throw new Error(`${label}: expected one replay button per scene, saw ${initial.replayButtons}.`)
  if (initial.replayIcons < initial.expected + 1)
    throw new Error(`${label}: expected Material Symbols icons on every replay control, saw ${initial.replayIcons}.`)
  if (!initial.fontFamily.includes('Open Sans'))
    throw new Error(`${label}: expected Open Sans as the page font, saw ${initial.fontFamily}.`)
  if (initial.invalidExampleIds.length)
    throw new Error(`${label}: invalid example ids: ${initial.invalidExampleIds.join(', ')}.`)
  if (initial.duplicateExampleIds)
    throw new Error(`${label}: found duplicate example ids.`)
  if (initial.cardsWithoutDomId.length)
    throw new Error(`${label}: cards without matching DOM ids: ${initial.cardsWithoutDomId.join(', ')}.`)
  if (initial.mismatchedSceneIds.length)
    throw new Error(`${label}: cards with mismatched scene ids: ${initial.mismatchedSceneIds.join(', ')}.`)
  if (initial.duplicateSceneIds)
    throw new Error(`${label}: found duplicate scene canvas ids.`)
  if (initial.smallFrames.length)
    throw new Error(`${label}: scene frames are too small: ${initial.smallFrames.join(', ')}.`)

  const beforeStats = await collectCanvasStats(page)
  assertCanvasStats(beforeStats, label)

  await page.waitForTimeout(760)
  const afterStats = await collectCanvasStats(page)
  const moved = afterStats.filter((stat, index) => stat.hash !== beforeStats[index].hash)

  if (moved.length < initial.expected - 1)
    throw new Error(`${label}: expected most canvases to animate, saw ${moved.length}/${initial.expected} changed hashes.`)

  await page.click('#replay-all')
  await page.waitForTimeout(140)
  const replayed = await page.evaluate(() => [...document.querySelectorAll('.example-card')]
    .filter((card) => Number(card.dataset.replayCount || 0) >= 1).length)
  if (replayed !== initial.expected)
    throw new Error(`${label}: replay-all did not reset every scene, saw ${replayed}/${initial.expected}.`)

  if (exerciseInteraction) {
    const firstCanvas = page.locator('canvas.three-canvas').first()
    const box = await firstCanvas.boundingBox()
    if (!box) throw new Error(`${label}: first canvas has no bounding box.`)
    await page.mouse.move(box.x + box.width * 0.52, box.y + box.height * 0.5)
    await page.mouse.down()
    await page.mouse.move(box.x + box.width * 0.72, box.y + box.height * 0.58, { steps: 8 })
    await page.mouse.up()
    const dragCount = await page.locator('.example-card').first().evaluate((card) => Number(card.dataset.dragCount || 0))
    if (dragCount < 1)
      throw new Error(`${label}: pointer drag did not update interaction state.`)
  }

  await page.screenshot({ path: screenshot, fullPage: true })
  await page.close()
}

async function collectCanvasStats(page) {
  return page.evaluate(async () => {
    async function imageFromCanvas(canvas) {
      const image = new Image()
      image.src = canvas.toDataURL('image/png')
      await image.decode()
      return image
    }

    return Promise.all([...document.querySelectorAll('canvas.three-canvas')].map(async (canvas) => {
      const image = await imageFromCanvas(canvas)
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
      const width = 96
      const height = Math.max(48, Math.round(width * image.height / image.width))
      const probe = document.createElement('canvas')
      probe.width = width
      probe.height = height
      const context = probe.getContext('2d', { willReadFrequently: true })
      context.drawImage(image, 0, 0, width, height)
      const data = context.getImageData(0, 0, width, height).data
      let nonWhite = 0
      let colored = 0
      let hash = 2166136261
      const buckets = new Set()

      for (let i = 0; i < data.length; i += 4) {
        const r = data[i]
        const g = data[i + 1]
        const b = data[i + 2]
        const a = data[i + 3]
        const white = r > 248 && g > 248 && b > 248
        const gray = Math.abs(r - g) < 5 && Math.abs(g - b) < 5
        if (a > 20 && !white) nonWhite += 1
        if (a > 20 && !white && !gray) colored += 1
        if (a > 20 && !white) buckets.add(`${r >> 4}-${g >> 4}-${b >> 4}`)
        hash = Math.imul(hash ^ r, 16777619)
        hash = Math.imul(hash ^ g, 16777619)
        hash = Math.imul(hash ^ b, 16777619)
      }

      const box = canvas.getBoundingClientRect()
      return {
        id: canvas.dataset.sceneId,
        width: Math.round(box.width),
        height: Math.round(box.height),
        nonWhite,
        colored,
        uniqueBuckets: buckets.size,
        hash: hash >>> 0,
        lost: Boolean(gl?.isContextLost?.()),
      }
    }))
  })
}

function assertCanvasStats(stats, label) {
  for (const stat of stats) {
    if (stat.lost)
      throw new Error(`${label}: ${stat.id} WebGL context is lost after stabilization.`)
    if (stat.width < 260 || stat.height < 210)
      throw new Error(`${label}: ${stat.id} canvas is too small (${stat.width}x${stat.height}).`)
    if (stat.nonWhite < 260)
      throw new Error(`${label}: ${stat.id} appears blank; nonwhite sample count was ${stat.nonWhite}.`)
    if (stat.colored < 90)
      throw new Error(`${label}: ${stat.id} has too few colored pixels; sample count was ${stat.colored}.`)
    if (stat.uniqueBuckets < 8)
      throw new Error(`${label}: ${stat.id} has too little color diversity; bucket count was ${stat.uniqueBuckets}.`)
  }
}

function isTransientWebGLMessage(text) {
  return text.includes('CONTEXT_LOST_WEBGL: loseContext: context lost')
    || text.includes('GPU stall due to ReadPixels')
}

async function findOpenPort(start) {
  for (let port = start; port < start + 40; port += 1) {
    if (await canListen(port)) return port
  }
  throw new Error(`No open port found from ${start} to ${start + 39}.`)
}

function canListen(port) {
  return new Promise((resolveCanListen) => {
    const tester = net.createServer()
    tester.once('error', () => resolveCanListen(false))
    tester.once('listening', () => {
      tester.close(() => resolveCanListen(true))
    })
    tester.listen(port, '127.0.0.1')
  })
}

async function waitForServer(url, processHandle) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (processHandle.exitCode !== null)
      throw new Error(`Vite exited before serving ${url}.\n${serverLog}`)

    try {
      const response = await fetch(url)
      if (response.ok) return
    } catch {
      await new Promise((resolveWait) => setTimeout(resolveWait, 150))
    }
  }

  throw new Error(`Timed out waiting for ${url}.\n${serverLog}`)
}
