#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-logical-sizing.ts
// Uses the retained clean-guide-deck Slidev dependencies and probe's pinned Playwright.
// Preserves isolated outputs; changed copies live only in ignored diagnostic artifacts.
import { createRequire } from 'node:module'
import { resolve, join, relative, sep } from 'node:path'
import { readFile, writeFile, cp, symlink, mkdir, stat } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { createServer } from 'node:http'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import assert from 'node:assert/strict'

const root = resolve(import.meta.dirname, '../../..')
const run = '20261005-slidev-hyperframes-animejs-sol-contract'
const original = resolve(root, 'evaluations/runs', run, 'workspace/deck')
const initialBuild = resolve(root, 'projects/slidev-hyperframes/artifacts/pi-final', run, 'build-source/dist')
const artifacts = resolve(root, 'projects/slidev-hyperframes/artifacts/logical-sizing')
const deck = join(artifacts, 'deck')
const dependencies = resolve(root, 'projects/slidev-hyperframes/artifacts/clean-guide-deck/node_modules')
const require = createRequire(resolve(root, 'projects/slidev-hyperframes/artifacts/probe/package.json'))
const { chromium } = require('playwright')
const execute = promisify(execFile)
const digest = (buffer) => createHash('sha256').update(buffer).digest('hex')
const originalAdapter = await readFile(join(original, 'components/HyperframeStory.vue'), 'utf8')
const originalHash = digest(originalAdapter)
assert.equal(originalHash, '80efb890f47982fabc63b61f6a858bc5bdcb0b7c91ed212ee5e1f81b55cfa9a0')
await mkdir(artifacts, { recursive: true })
await cp(original, deck, { recursive: true, filter: source => !['node_modules', 'dist'].includes(relative(original, source).split(sep)[0]) })
await symlink(dependencies, join(deck, 'node_modules'), 'junction').catch(async error => {
  if (error.code !== 'EEXIST') throw error
  assert.equal(await stat(join(deck, 'node_modules')).then(s => s.isDirectory()), true)
})
const safeAdapter = originalAdapter.replace('const rect = box.getBoundingClientRect()', 'const rect = { width: box.clientWidth, height: box.clientHeight }')
assert.notEqual(safeAdapter, originalAdapter)
await writeFile(join(deck, 'components/HyperframeStory.vue'), safeAdapter)
await writeFile(join(deck, 'components/LogicalSizingRecipe.vue'), `<script setup lang="ts">
import {ref} from 'vue'
import {onSlideLeave} from '@slidev/client'
import HyperframeSlide from './HyperframeSlide.vue'
const playing=ref(false)
defineProps<{step:number}>()
onSlideLeave(()=>{playing.value=false})
</script>
<template>
<div data-logical-recipe style="display:grid;grid-template-rows:330px 38px;gap:10px">
<HyperframeSlide :step="step" :cue-times="[0,4,9]" :height="330" :playing="playing" />
<button :aria-label="playing?'Pause animation':'Play animation'" @click="playing=!playing">{{playing?'Pause animation':'Play animation'}}</button>
</div>
</template>`)
const slides = await readFile(join(deck, 'slides.md'), 'utf8')
await writeFile(join(deck, 'slides.md'), slides+'\n---\nlayout: default\nclicks: 2\n---\n\n<h1 style="font-size:28px">Fixed logical player and control rows</h1>\n\n<LogicalSizingRecipe :step="$clicks" />\n')
const command = [join(dependencies, '@slidev/cli/bin/slidev.mjs'), 'build', '--base', './']
const build = await execute(process.execPath, command, { cwd: deck, maxBuffer: 30_000_000 })
await writeFile(join(artifacts, 'build.log'), build.stdout+'\n'+build.stderr)
for (const name of ['components/HyperframeSlide.vue', 'lib/hyperframes.js', 'lib/hyperframes-vite.ts']) assert.equal(digest(await readFile(join(deck, name))), digest(await readFile(join(original, name))))
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json', '.svg': 'image/svg+xml' }
async function serve(directory) {
  const server = createServer(async (req, res) => {
    try {
      let file = resolve(directory, '.'+decodeURIComponent(new URL(req.url, 'http://localhost').pathname))
      if (relative(directory, file).startsWith('..')) throw Error('Outside serve root')
      if (!(await stat(file).catch(()=>null))?.isFile()) file = join(directory, 'index.html')
      const ext = file.slice(file.lastIndexOf('.'))
      res.writeHead(200, {'Content-Type': mime[ext] || 'application/octet-stream'})
      res.end(await readFile(file))
    } catch { res.writeHead(404); res.end('Not found') }
  })
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  return { server, url: 'http://127.0.0.1:'+server.address().port }
}
const oldServer = await serve(initialBuild), newServer = await serve(join(deck, 'dist'))
const browser = await chromium.launch({headless: true})
const page = await browser.newPage({viewport: {width: 1280, height: 800}})
const errors = [], checks = []
page.on('pageerror', error => errors.push(error.message))
async function open(base, slide) {
  await page.goto(base+'/'+slide+'?clicks=0')
  await page.waitForSelector('.hyperframe-slide:visible[data-ready="true"]')
  await page.waitForTimeout(120)
}
async function geometry() {
  return page.locator('.hyperframe-slide:visible').first().evaluate(player => {
    const story = player.closest('.hyperframe-story') || player.closest('[data-logical-recipe]')
    const button = story.querySelector('button'), box = story.querySelector('.player-measure')
    const pr = player.getBoundingClientRect(), br = button.getBoundingClientRect(), mr = box?.getBoundingClientRect()
    const center = document.elementFromPoint(br.x+br.width/2, br.y+br.height/2)
    return {
      logicalPlayerWidth: player.clientWidth, logicalPlayerHeight: player.clientHeight,
      playerBounds: {x: pr.x, y: pr.y, width: pr.width, height: pr.height, bottom: pr.bottom},
      buttonBounds: {x: br.x, y: br.y, width: br.width, height: br.height, top: br.top},
      scale: pr.width/player.clientWidth, logicalBoxWidth: box?.clientWidth, logicalBoxHeight: box?.clientHeight,
      measuredBoxWidth: mr?.width, measuredBoxHeight: mr?.height,
      buttonHit: button === center || button.contains(center),
    }
  })
}
async function nativeScene() {
  const iframe = await page.locator('hyperframes-player:visible').first().locator('iframe').elementHandle()
  const frame = await iframe.contentFrame()
  const bounds = await iframe.boundingBox()
  const state = await frame.evaluate(() => {
    const text = document.querySelector('[data-scene-mark="level-readout"]')
    return {time:Number(document.querySelector('[data-composition-id]').dataset.sceneTime),readout:text.textContent,font:getComputedStyle(text).fontFamily,fontSize:Number.parseFloat(getComputedStyle(text).fontSize),loaded:document.fonts.check('600 24px "Open Sans"'),width:innerWidth}
  })
  return {...state,effectiveFontSize:state.fontSize*bounds.width/state.width}
}
try {
  await open(oldServer.url, 1)
  const old = await geometry()
  assert.equal(old.buttonHit, false)
  assert.ok(old.logicalPlayerHeight > old.logicalBoxHeight+50)
  await page.screenshot({path: join(artifacts, 'original-scaled-overlay.png')})
  checks.push({id: 'retained-original-failure-reproduced', ...old})
  for (const viewport of [{width:1280,height:800}, {width:1920,height:1080}, {width:980,height:700}]) {
    await page.setViewportSize(viewport)
    for (const slide of [1, 2, 4]) {
      await open(newServer.url, slide)
      const current = await geometry()
      assert.ok(current.buttonHit, JSON.stringify(current))
      assert.ok(current.playerBounds.bottom <= current.buttonBounds.top+.5, JSON.stringify(current))
      if (slide !== 4) assert.ok(current.logicalPlayerHeight <= current.logicalBoxHeight, JSON.stringify(current))
      else assert.equal(current.logicalPlayerHeight, 330)
      const scene = await nativeScene()
      assert.ok(scene.loaded && scene.font.includes('Open Sans') && scene.effectiveFontSize >= 14, JSON.stringify(scene))
      await page.getByRole('button', {name: 'Play animation', exact: true}).first().click({timeout:3000})
      await page.waitForFunction(() => [...document.querySelectorAll('.hyperframe-slide')].some(el => Number(el.dataset.time)>.1 && el.dataset.paused==='false'))
      await page.getByRole('button', {name: 'Pause animation', exact: true}).first().click({timeout:3000})
      await page.waitForFunction(() => [...document.querySelectorAll('.hyperframe-slide')].every(el => el.dataset.paused==='true'))
      if (slide === 4) {
        await page.evaluate(() => document.activeElement?.blur())
        for (const [key,seconds] of [['ArrowRight',4],['ArrowRight',9],['ArrowLeft',4],['ArrowLeft',0]]) {
          await page.keyboard.press(key)
          await page.waitForSelector('.hyperframe-slide:visible[data-ready="true"][data-time="'+seconds+'"]')
          const seeked = await nativeScene()
          assert.equal(seeked.time, seconds)
          assert.equal(seeked.readout, seconds === 0 ? '0%' : seconds === 4 ? '20%' : '70%')
        }
      }
      checks.push({id: 'logical-sizing-'+viewport.width+'-slide-'+slide, ...current, scene})
      await page.screenshot({path: join(artifacts, 'logical-'+viewport.width+'-slide-'+slide+'.png')})
    }
  }
  assert.equal(errors.length, 0, JSON.stringify(errors))
  assert.equal(digest(await readFile(join(original, 'components/HyperframeStory.vue'))), originalHash)
  const report = {
    passed: true, checks: checks.length, cases: checks, errors,
    originalAdapter: {path: join(original, 'components/HyperframeStory.vue'), sha256: originalHash, unchanged: true},
    diagnosticAdapter: {path: join(deck, 'components/HyperframeStory.vue'), sha256: digest(safeAdapter), onlyRepair: 'getBoundingClientRect() replaced by padding-free clientWidth/clientHeight'},
    build: {command: [process.execPath, ...command], log: join(artifacts, 'build.log')},
    fixedGuideRecipe: {height:330, controlHeight:38, gap:10, totalBudget:378}, runtimeUnchanged: true,
  }
  await writeFile(join(artifacts, 'verification.json'), JSON.stringify(report, null, 2)+'\n')
  console.log(JSON.stringify({passed: true, checks: checks.length, report: join(artifacts, 'verification.json')}, null, 2))
} finally {
  await browser.close()
  await Promise.all([new Promise(resolve => oldServer.server.close(resolve)), new Promise(resolve => newServer.server.close(resolve))])
}
