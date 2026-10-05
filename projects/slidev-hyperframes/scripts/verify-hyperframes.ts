#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes.ts
// Dependencies: the confined artifacts/probe/package.json pins Vue, Vite, player,
// @vitejs/plugin-vue, playwright, @vue/compiler-sfc and vite-plugin-singlefile.
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
import { cp, readFile, writeFile, readdir, stat } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import assert from 'node:assert/strict'

const root = resolve(import.meta.dirname, '../../..')
const project = resolve(root, 'projects/slidev-hyperframes/artifacts/probe')
const pack = resolve(root, 'skills/slidev-echarts/assets/templates/slidev-hyperframes')
const require = createRequire(resolve(project, 'package.json'))
const { chromium } = require('playwright')
const { createServer, build } = await import(pathToFileURL(resolve(project, 'node_modules/vite/dist/node/index.js')).href)
const vue = (await import(pathToFileURL(resolve(project, 'node_modules/@vitejs/plugin-vue/dist/index.mjs')).href)).default
const { viteSingleFile } = await import(pathToFileURL(resolve(project, 'node_modules/vite-plugin-singlefile/dist/esm/index.js')).href)
const hashes = {}
async function inventory(directory, prefix = '') {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const name = `${prefix}${entry.name}`
    if (entry.isDirectory()) await inventory(resolve(directory, entry.name), `${name}/`)
    else hashes[name] = createHash('sha256').update(await readFile(resolve(directory, entry.name))).digest('hex')
  }
}
await inventory(pack)
for (const [name, digest] of Object.entries(hashes)) assert.equal(createHash('sha256').update(await readFile(resolve(root, 'skills/slidev-animejs/assets/templates/slidev-hyperframes', name))).digest('hex'), digest, name)
await cp(pack, project, { recursive: true })
await writeFile(resolve(project, 'index.html'), '<html><head><meta charset="utf-8"></head><body><div id="app"></div><script type="module" src="/main.js"></script></body></html>')
await writeFile(resolve(project, 'slidev-stub.js'), "import {ref} from 'vue';export const active=ref(true),context=ref('slide');export const useIsSlideActive=()=>active;export const useSlideContext=()=>({$renderContext:context});")
await writeFile(resolve(project, 'main.js'), `import{createApp,ref,h}from'vue';import H from'./components/HyperframeSlide.vue';import{active,context}from'./slidev-stub.js';const c={step:ref(0),playing:ref(false),src:ref('hyperframes/starter.html'),palette:ref('colorset1'),show:ref(true),static:ref(false),exportTime:ref(9),api:ref(),active,context};window.controls=c;const file=location.protocol==='file:';createApp({setup:()=>()=>h('div',{id:'stage',style:{width:'720px'}},[c.show.value?h(H,{ref:c.api,src:file?'hyperframes/starter.html?compact=1':c.src.value,step:c.step.value,cueTimes:[0,4,9],playing:c.playing.value,colorset:c.palette.value,static:file||c.static.value,exportTime:c.exportTime.value}):null,file?h(H,{src:'hyperframes/starter.html?compact=1',static:true,exportTime:0,height:330}):null])}).mount('#app');`)
const config = { root: project, configFile: false, plugins: [vue()], resolve: { alias: { '@slidev/client': resolve(project, 'slidev-stub.js') } }, server: { host: '127.0.0.1', port: 0 } }
const server = await createServer(config)
await server.listen()
const url = server.resolvedUrls.local[0]
const helper = await server.ssrLoadModule('/lib/hyperframes.js')
const checks = [], errors = [], requests = []
function check(name, condition, detail = {}) { assert.ok(condition, `${name}: ${JSON.stringify(detail)}`); checks.push({ name, ...detail }) }
check('cue clamp', helper.cueTime(-2, [0, 4, 9]) === 0 && helper.cueTime(100, [0, 4, 9], 5) === 5)
for (const bad of [[], [NaN], [-1], [Infinity]]) assert.throws(() => helper.cueTime(0, bad))
check('nested Pages URL', helper.assetUrl('hyperframes/starter.html', '/skills/examples/deck/', 'https://example.test/skills/examples/deck/2') === 'https://example.test/skills/examples/deck/hyperframes/starter.html')
check('relative base URL', helper.compositionDocument('<head><base href="../assets/"></head>', 'https://example.test/deck/scene/index.html').includes('https://example.test/deck/assets/'))
check('custom query preserved', helper.starterUrl('custom/index.html?name=Ship%20it', 'colorset2', './', 'https://example.test/deck/index.html').endsWith('custom/index.html?name=Ship%20it'))
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1000, height: 800 } })
page.on('pageerror', error => errors.push(error.message))
page.on('request', request => requests.push(request.url()))
async function settled(seconds) { await page.waitForSelector(`.hyperframe-slide[data-ready="true"][data-time="${seconds}"]`, { timeout: 15000 }) }
async function scene() {
  const frame = page.frames().find(frame => frame !== page.mainFrame())
  return frame.evaluate(() => {
    const root = document.querySelector('[data-composition-id]'), tank = document.querySelector('#tank'), fill = document.querySelector('#tank-fill'), text = document.querySelector('#level-readout')
    return { time: Number(root.dataset.sceneTime), fraction: Number(fill.getAttribute('height')) / Number(tank.getAttribute('height')), readout: text.textContent, fill: fill.getAttribute('fill'), font: getComputedStyle(text).fontFamily, loaded: document.fonts.check('600 24px "Open Sans"') }
  })
}
try {
  await page.goto(url)
  for (const selected of ['colorset1', 'colorset2']) {
    await page.evaluate(selected => { window.controls.palette.value = selected }, selected)
    for (const [step, seconds, fraction] of [[0, 0, 0], [1, 4, .2], [2, 9, .7], [1, 4, .2], [0, 0, 0]]) {
      await page.evaluate(step => { window.controls.step.value = step }, step)
      await settled(seconds)
      const actual = await scene()
      check(`actual ${selected} cue ${seconds}`, actual.time === seconds && Math.abs(actual.fraction - fraction) < 1e-8 && actual.loaded && actual.fill === (selected === 'colorset1' ? '#9e1b32' : '#007298'), actual)
    }
  }
  await page.evaluate(() => { window.controls.step.value = 1; window.controls.playing.value = true })
  await page.waitForFunction(() => Number(document.querySelector('.hyperframe-slide').dataset.time) > 4.2)
  await page.evaluate(() => { window.controls.playing.value = false })
  const pausedAt = (await scene()).time
  await page.waitForTimeout(260)
  check('Pause freezes current time', pausedAt > 4 && Math.abs((await scene()).time - pausedAt) < .01)
  await page.evaluate(() => { window.controls.playing.value = true })
  await page.waitForTimeout(180)
  await page.evaluate(() => { window.controls.active.value = false })
  const inactiveAt = (await scene()).time
  await page.waitForTimeout(300)
  check('inactive playback stable', Math.abs((await scene()).time - inactiveAt) < .01)
  await page.evaluate(() => { window.controls.playing.value = false; window.controls.active.value = true })
  await settled(4)
  check('reentry canonical cue', (await scene()).time === 4)
  await page.evaluate(async () => { await window.controls.api.value.seek(9) })
  await settled(9)
  check('public seek painted', (await scene()).time === 9)
  for (const width of [420, 304, 245]) {
    await page.evaluate(width => { window.controls.src.value = 'hyperframes/starter.html?compact=1'; document.querySelector('#stage').style.width = `${width}px` }, width)
    await settled(4)
    const scale = await page.locator('hyperframes-player').evaluate(player => player.iframeElement.getBoundingClientRect().width / 420)
    check(`compact font at ${width}`, 24 * scale >= 14 - .01 && (await scene()).loaded, { effectiveFontSize: 24 * scale })
  }
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.evaluate(() => { window.controls.playing.value = true })
  await page.waitForTimeout(240)
  const reducedState = await scene()
  check('reduced motion paused', Math.abs(reducedState.time - 4) < .01, reducedState)
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.evaluate(() => { window.controls.playing.value = false; window.controls.static.value = true; window.controls.exportTime.value = 9 })
  await settled(9)
  check('explicit static actual frame', Math.abs((await scene()).fraction - .7) < 1e-8)
  await page.screenshot({ path: resolve(project, '../native-static-9.png') })
  await page.evaluate(() => { window.controls.src.value = 'missing-scene.html' })
  await page.waitForSelector('[data-status="error"]')
  check('failed fetch visible error', await page.locator('[role="alert"]').isVisible())
  await page.evaluate(() => { window.controls.src.value = 'hyperframes/starter.html'; window.controls.show.value = false })
  await page.waitForTimeout(150)
  check('unmount removes player', await page.locator('hyperframes-player').count() === 0)
  await page.evaluate(() => { window.controls.show.value = true })
  await settled(9)
  check('remount initialized', (await scene()).time === 9)
  await build({ ...config, base: './', plugins: [vue(), viteSingleFile()], build: { outDir: 'file-dist', emptyOutDir: true } })
  const filePage = await browser.newPage()
  filePage.on('pageerror', error => errors.push(error.message))
  const fileRequests = []
  filePage.on('request', request => fileRequests.push(request.url()))
  await filePage.goto(pathToFileURL(resolve(project, 'file-dist/index.html')).href)
  await filePage.waitForFunction(() => document.querySelectorAll('[data-ready="true"][data-source-kind="fallback"]').length === 2)
  const fileState = await filePage.evaluate(() => {
    const roots = [...document.querySelectorAll('.hyperframe-slide')]
    const ids = [...document.querySelectorAll('[id]')].map(el => el.id)
    return { unique: new Set(ids).size === ids.length, loaded: document.fonts.check('600 24px "Open Sans"'), states: roots.map(root => ({ time: Number(root.dataset.time), text: root.querySelector('[data-scene-mark="level-readout"]').textContent, title: root.querySelector('svg').getAttribute('aria-labelledby').split(' ').map(id => document.getElementById(id)?.textContent).join(' ') })) }
  })
  check('file same-model fonts/IDs', fileState.unique && fileState.loaded && fileState.states[0].text === '70%' && fileState.states[1].text === '0%' && fileState.states[0].title.includes('9.00') && fileState.states[1].title.includes('0.00'), fileState)
  await filePage.evaluate(async () => { await window.controls.api.value.seek(4) })
  check('file public seek updates actual SVG', await filePage.locator('[data-scene-mark="level-readout"]').first().textContent() === '20%')
  await filePage.evaluate(() => { window.controls.exportTime.value = 99 })
  await filePage.waitForSelector('[data-ready="true"][data-time="12"]')
  check('file duration clamp', await filePage.locator('[data-scene-mark="level-readout"]').first().textContent() === '80%')
  check('file no live resources', fileRequests.every(url => url.startsWith('file:') || url.startsWith('data:')) && await filePage.locator('hyperframes-player').count() === 0, { fileRequests })
  await filePage.screenshot({ path: resolve(project, '../native-file-fallback.png') })
  check('no browser errors', errors.length === 0, { errors })
  check('no external HTTP requests', requests.every(request => request.startsWith(url)), { external: requests.filter(request => !request.startsWith(url)) })
  const report = { accepted: true, checks: checks.length, cases: checks, hashes, errors }
  await writeFile(resolve(project, '../runtime-verification.json'), JSON.stringify(report, null, 2))
  console.log(JSON.stringify({ accepted: true, checks: checks.length, report: resolve(project, '../runtime-verification.json') }, null, 2))
} finally { await browser.close(); await server.close() }
