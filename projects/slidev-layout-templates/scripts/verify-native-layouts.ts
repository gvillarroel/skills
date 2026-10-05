#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-native-layouts.ts --template skills/slidev-echarts/assets/templates/slidev-layouts
// Dependencies: Node >=24; @slidev/cli, @slidev/theme-default and playwright from --dependencies (existing fixture by default).
// Evaluator-owned native Vue/Slidev cases; no acceptance fixtures are exposed to isolated authoring agents.
import { readFile, writeFile, mkdir, cp, symlink, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import http from 'node:http'

const args = process.argv.slice(2)
function arg(name: string, fallback = '') {
  const index = args.indexOf(name)
  return index >= 0 ? args[index + 1] : fallback
}
const root = process.cwd()
const template = path.resolve(arg('--template', 'skills/slidev-echarts/assets/templates/slidev-layouts'))
const dependencies = path.resolve(arg('--dependencies', 'skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const output = path.resolve(arg('--output', 'projects/slidev-layout-templates/artifacts/native-matrix'))
const deck = path.join(output, 'deck')
const html = path.join(output, 'html')
const paletteSource = path.resolve(arg('--palette-source', 'skills/slidev-echarts/assets/palettes/colorsets.json'))
const require = createRequire(path.join(dependencies, '../package.json'))
const { chromium } = require('playwright')
const palettes = JSON.parse(await readFile(paletteSource, 'utf8')).colorsets
const modes = ['columns', 'grid', 'masonry-columns', 'masonry-rows']
const titles = ['Intake', 'Scope', 'Research', 'Draft', 'Diagram', 'Review', 'Revise', 'Check', 'Approve', 'Publish', 'Archive']
const cards = titles.map((title, index) => ({
  id: `card-${String(index + 1).padStart(2, '0')}`, title,
  body: index % 3 === 0 ? 'Keep scope clear.' : index % 3 === 1 ? 'Record. Share.' : 'Check. Confirm. Save.',
  width: [150, 190, 160, 220, 170, 180, 200, 150, 210, 170, 160][index],
}))
await mkdir(path.join(deck, 'components'), { recursive: true })
await mkdir(path.join(deck, 'lib'), { recursive: true })
await cp(path.join(template, 'components/SlidevLayout.vue'), path.join(deck, 'components/SlidevLayout.vue'))
await cp(path.join(template, 'lib/slidev-layouts.mjs'), path.join(deck, 'lib/slidev-layouts.mjs'))
const sourceHashes = Object.fromEntries(await Promise.all(['components/SlidevLayout.vue', 'lib/slidev-layouts.mjs'].map(async file => [file, createHash('sha256').update(await readFile(path.join(template, file))).digest('hex')])))
const expectedHelperSha = arg('--expect-helper-sha')
if (expectedHelperSha && sourceHashes['lib/slidev-layouts.mjs'] !== expectedHelperSha) throw new Error('Runtime helper digest differs from the frozen release digest.')
await writeFile(path.join(deck, 'package.json'), JSON.stringify({ private: true, type: 'module', dependencies: { '@slidev/cli': '52.16.0', '@slidev/theme-default': '0.25.0', vue: '3.5.38' } }, null, 2))
await writeFile(path.join(deck, 'slides.md'), `---\ntheme: default\nlayout: none\nfonts:\n  sans: Open Sans\n---\n\n<NativeLayoutCase />\n`)
await writeFile(path.join(deck, 'components/NativeLayoutCase.vue'), `<script setup>
import { reactive, onMounted, nextTick } from 'vue'
import SlidevLayout from './SlidevLayout.vue'
const source = ${JSON.stringify(cards)}
const state = reactive({ mode: 'columns', count: 3, columns: 2, rows: 3, width: 880, height: 390, colorset: 'colorset1', page: 1, pageSize: 11, reverse: false, filtered: false, manifest: true, custom: false, smallSlot: false, fixedGeometry: false, feedback: false, longCopy: false, ready: false })
const capacity = reactive({ value: null, emissions: 0 })
function receiveCapacity(value) { capacity.emissions++; capacity.value = value }
const active = () => { let items = source.slice(0, state.count).map((item, index) => state.longCopy ? { ...item, width: 320, body: index % 3 === 0 ? 'Keep the request clear.' : index % 3 === 1 ? 'Record the decision. Share the next step.' : 'Check the evidence. Confirm the result. Save the decision.' } : item); if (state.feedback && capacity.value) items = items.map(item => ({ ...item, width: Math.max(140, Math.floor((capacity.value.width - 32) / 3)) })); if (state.filtered) items = items.filter((_, i) => i % 2 === 0); return state.reverse ? [...items].reverse() : items }
onMounted(async () => {
  window.__layoutCase = { state, source, capacity, active, async set(change) { state.ready = false; Object.assign(state, change); await nextTick(); await document.fonts.ready; await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))); await new Promise(resolve => setTimeout(resolve, 120)); state.ready = true; return true } }
  await window.__layoutCase.set({})
})
</script>
<template>
  <div id="native-layout-case" :style="{ width: state.width + 'px' }">
    <div class="case-caption">{{ state.mode }} · {{ state.count }} items · {{ state.colorset }} · page {{ state.page }}</div>
    <SlidevLayout :items="active()" :mode="state.mode" :columns="state.columns" :rows="state.rows" :height="state.height" :gap="16" :min-item-width="140" :colorset="state.colorset" :category-order="state.manifest ? source.map(item => item.id) : undefined" :page="state.page" :page-size="state.pageSize" @capacity="receiveCapacity">
      <template v-if="state.custom" #item="{ item, color, box }">
        <div v-if="state.fixedGeometry" data-fixed-geometry="true" :style="{ width: box.contentWidth + 'px', height: box.contentHeight + 'px', lineHeight: '0' }"><svg :width="box.contentWidth" :height="box.contentHeight" style="display:block"><text x="0" y="22" :fill="color.ink" style="font-size:20px;line-height:1.2">{{ item.title }}</text><text x="0" y="49" :fill="color.ink" style="font-size:18px;line-height:1.35">{{ item.body }}</text></svg></div>
        <template v-else>
        <h3 style="font-size:20px;line-height:1.2;margin:0 0 8px">{{ item.title }}</h3>
        <p :data-intentional-font="state.smallSlot ? '14' : undefined" :style="{ fontSize: state.smallSlot ? '14px' : '18px', lineHeight: '1.35', margin: '0', opacity: '1' }">{{ item.body }}</p>
        <div class="custom-slot-panel" data-custom-slot="true"><strong>Evidence</strong><svg viewBox="0 0 90 20" aria-label="Step relationship"><rect x="0" y="2" width="25" height="16" :fill="color.fill"/><path d="M30 10H58m-5-4 5 4-5 4" fill="none" stroke="#696969" stroke-width="2"/><rect x="64" y="2" width="25" height="16" :fill="color.fill"/></svg></div>
        </template>
      </template>
    </SlidevLayout>
  </div>
</template>
<style scoped>
#native-layout-case { position:absolute; left:40px; top:24px; color:#000000; background:#ffffff; font-family:'Open Sans',sans-serif; }
.case-caption { height:36px; font-size:18px; line-height:24px; }
.custom-slot-panel { margin-top:8px; padding:4px; background:#ffffff; color:#000000; display:flex; align-items:center; gap:8px; font-size:18px; }
.custom-slot-panel svg { width:90px; height:20px; }
</style>
`)
if (!existsSync(path.join(deck, 'node_modules'))) await symlink(dependencies, path.join(deck, 'node_modules'), 'junction')
if (!args.includes('--skip-build')) {
  const cli = require.resolve('@slidev/cli/bin/slidev.mjs')
  const built = await new Promise<{ code: number, stdout: string }>(resolve => {
    const child = spawn(process.execPath, [cli, 'build', 'slides.md', '--base', './', '--out', html], { cwd: deck, windowsHide: true, env: { ...process.env, NODE_ENV: 'production' } })
    let stdout = ''
    child.stdout.on('data', data => stdout += data)
    child.stderr.on('data', data => stdout += data)
    child.on('close', code => resolve({ code: code ?? 1, stdout }))
  })
  await writeFile(path.join(output, 'build.log'), built.stdout)
  if (built.code) throw new Error(`Native fixture build failed; inspect ${path.join(output, 'build.log')}`)
}
const mime: Record<string, string> = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' }
const server = http.createServer(async (request, response) => {
  try {
    let candidate = path.resolve(html, `.${decodeURIComponent(new URL(request.url || '/', 'http://local').pathname)}`)
    if (!candidate.startsWith(html + path.sep) && candidate !== html) { response.writeHead(403).end(); return }
    if (!existsSync(candidate) || (await stat(candidate)).isDirectory()) candidate = path.join(html, 'index.html')
    response.writeHead(200, { 'content-type': mime[path.extname(candidate)] || 'application/octet-stream' }).end(await readFile(candidate))
  } catch (error) { response.writeHead(500).end(String(error)) }
})
await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve))
const port = (server.address() as { port: number }).port
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
const errors: string[] = []
page.on('pageerror', (error: Error) => { if (!String(error).includes('Wake Lock permission request denied')) errors.push(String(error)) })
const results: any[] = []

async function auditCase(id: string, change: any, negative = false, screenshot = false) {
  await page.evaluate(change => (window as any).__layoutCase.set(change), change)
  const palette = palettes[change.colorset || await page.evaluate(() => (window as any).__layoutCase.state.colorset)]
  const audit = await page.evaluate(({ allowed, negative }) => {
    function hex(value: string) {
      if (!value || value === 'transparent' || value === 'none') return null
      const numbers = value.match(/[\d.]+/g)?.map(Number)
      if (value.startsWith('rgb') && numbers && numbers.length >= 3) {
        if (numbers.length > 3 && numbers[3] === 0) return null
        return '#' + numbers.slice(0, 3).map(n => Math.round(n).toString(16).padStart(2, '0')).join('')
      }
      return value.toLowerCase()
    }
    function luminance(value: string) {
      const c = value.slice(1).match(/../g)!.map(v => parseInt(v, 16) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
      return c[0] * .2126 + c[1] * .7152 + c[2] * .0722
    }
    function contrast(a: string, b: string) { const x = luminance(a), y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05) }
    const owner = (window as any).__layoutCase
    const state = { ...owner.state }
    const surface = document.querySelector<HTMLElement>('#native-layout-case [data-layout-mode]')!
    const bounds = surface.getBoundingClientRect()
    const scale = bounds.width / surface.clientWidth
    const active = owner.active()
    const pages = Math.max(1, Math.ceil(active.length / state.pageSize))
    const pageNumber = Math.min(pages, Math.max(1, state.page))
    const expected = active.slice((pageNumber - 1) * state.pageSize, pageNumber * state.pageSize).map((item: any) => item.id)
    const failures: string[] = []
    const clipped: any[] = []
    const paints: any[] = []
    const cards = [...surface.querySelectorAll<HTMLElement>('[data-item-id]')].map(element => {
      const r = element.getBoundingClientRect(), css = getComputedStyle(element)
      const fill = hex(css.backgroundColor), ink = hex(css.color)
      const id = element.dataset.itemId!
      const sourceItem = active.find((item:any) => item.id === id)
      if (!sourceItem || !element.textContent?.includes(sourceItem.title) || !element.textContent?.includes(sourceItem.body)) failures.push(`${id}: requested full title/body is missing`)
      if (fill && !allowed.includes(fill)) failures.push(`${id}: undeclared fill ${fill}`)
      if (ink && !allowed.includes(ink)) failures.push(`${id}: undeclared text ${ink}`)
      const best = fill && contrast('#000000', fill) >= contrast('#ffffff', fill) ? '#000000' : '#ffffff'
      if (ink !== best) failures.push(`${id}: text is not maximum black/white contrast`)
      if (fill && ink && contrast(fill, ink) < 4.5) failures.push(`${id}: inside text contrast below 4.5:1`)
      if (!negative && (r.left < bounds.left - 1 || r.top < bounds.top - 1 || r.right > bounds.right + 1 || r.bottom > bounds.bottom + 1)) failures.push(`${id}: card outside layout frame`)
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT)
      let node = walker.nextNode()
      while (node) {
        if (node.textContent?.trim()) {
          const parent = node.parentElement!
          const style = getComputedStyle(parent)
          let opacity=1; for (let ancestor:Element|null=parent; ancestor; ancestor=ancestor.parentElement) { opacity*=Number(getComputedStyle(ancestor).opacity); if (ancestor===surface) break }
          if (Math.abs(opacity-1)>0.0001) failures.push(`${id}: label effective opacity ${opacity} is not opaque`)
          const color = hex(style.color)
          const panel = parent.closest<HTMLElement>('[data-custom-slot]')
          const backing = panel ? hex(getComputedStyle(panel).backgroundColor) : fill
          if (color && !allowed.includes(color)) failures.push(`${id}: undeclared descendant ink ${color}`)
          if (backing && color && color !== (contrast('#000000', backing) >= contrast('#ffffff', backing) ? '#000000' : '#ffffff')) failures.push(`${id}: descendant text contrast does not match its backing`)
          if (parent.dataset.intentionalFont === '14') { if (parseFloat(style.fontSize) !== 14) failures.push(`${id}: explicit 14px slot typography was overridden`) }
          else if (parseFloat(style.fontSize) < 18) failures.push(`${id}: text shrunk below 18px`)
          const range = document.createRange(); range.selectNodeContents(node)
          for (const glyph of range.getClientRects()) {
            if (glyph.left < r.left - 1 || glyph.top < r.top - 1 || glyph.right > r.right + 1 || glyph.bottom > r.bottom + 1) clipped.push({ id, text: node.textContent, glyph: { x: glyph.x, y: glyph.y, width: glyph.width, height: glyph.height } })
          }
        }
        node = walker.nextNode()
      }
      for (const property of ['backgroundColor', 'color', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor']) {
        const value = hex(css[property as any])
        if (value && !allowed.includes(value)) failures.push(`${id}: undeclared ${property} ${value}`)
        if (value) paints.push(value)
      }
      return { id, category: element.dataset.categoryId, row: Number(element.dataset.row), column: Number(element.dataset.column), fill, ink, borderWidth: parseFloat(css.borderTopWidth), title: element.querySelector('h3')?.textContent, body: element.querySelector('p')?.textContent, bodyFont: element.querySelector('p') ? getComputedStyle(element.querySelector('p')!).fontSize : null, x: (r.left-bounds.left)/scale, y: (r.top-bounds.top)/scale, width: r.width/scale, height: r.height/scale }
    })
    if (JSON.stringify(cards.map(card => card.id)) !== JSON.stringify(expected)) failures.push('Rendered IDs or source order differ from the requested page.')
    if (cards.some(card => card.borderWidth !== 0)) failures.push('A decorative border appears before unique solid capacity is exhausted.')
    if (clipped.length && !negative) failures.push(`${clipped.length} text ranges cross their card bounds.`)
    const overlap: any[] = []
    for (let i = 0; i < cards.length; i++) for (let j = i+1; j < cards.length; j++) {
      const a = cards[i], b = cards[j]
      if (Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x) > .5 && Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y) > .5) overlap.push([a.id,b.id])
    }
    if (overlap.length) failures.push(`${overlap.length} card pairs overlap.`)
    if (surface.dataset.layoutMode !== state.mode || surface.dataset.colorset !== state.colorset) failures.push('Native layout mode or palette is stale after update.')
    if (Number(surface.dataset.page) !== pageNumber || Number(surface.dataset.pages) !== pages) failures.push('Native page metadata is stale after update.')
    const fits = surface.dataset.layoutFits === 'true'
    if (owner.capacity.value?.fits !== fits) failures.push('Emitted capacity report disagrees with rendered metadata.')
    if (negative ? fits : !fits) failures.push(negative ? 'Impossible capacity was reported as fitting.' : 'Publication state was reported as not fitting.')
    if (!negative && (bounds.left < 0 || bounds.top < 0 || bounds.right > innerWidth+1 || bounds.bottom > innerHeight+1)) failures.push('Layout frame crosses the browser viewport.')
    if (state.mode === 'masonry-rows' && cards.length >= state.rows) {
      const rows = [...new Set(cards.map(card => card.row))]
      if (rows.length !== state.rows) failures.push(`Horizontal masonry uses ${rows.length} rows instead of ${state.rows}.`)
      for (const row of rows) {
        const members = cards.filter(card => card.row === row)
        if (Math.max(...members.map(card => card.y))-Math.min(...members.map(card => card.y)) > .5) failures.push(`Row ${row} is not a literal horizontal row.`)
      }
    }
    if (state.mode === 'grid') {
      for (const row of [...new Set(cards.map(card => card.row))]) {
        const members = cards.filter(card => card.row === row)
        if (Math.max(...members.map(card => card.y))-Math.min(...members.map(card => card.y)) > .5 || Math.max(...members.map(card => card.height))-Math.min(...members.map(card => card.height)) > .5) failures.push(`Grid row ${row} is not aligned with equal cells.`)
      }
    }
    const animations = surface.getAnimations({ subtree: true }).map(animation => ({ playState: animation.playState, timing: animation.effect?.getComputedTiming() }))
    return { passed: !failures.length, failures, state, expected, fits, width: surface.clientWidth, height: surface.clientHeight, page: surface.dataset.page, capacity: owner.capacity.value, capacityEmissions: owner.capacity.emissions, cards, clipped, overlap, paints: [...new Set(paints)], animations, customSlots: surface.querySelectorAll('[data-custom-slot]').length }
  }, { allowed: palette.allowed, negative })
  if (screenshot || !audit.passed) await page.screenshot({ path: path.join(output, `${id}.png`), fullPage: true })
  Object.assign(audit, { id, negativeCapacity: negative }); results.push(audit)
  return audit
}

try {
  await page.goto(`http://127.0.0.1:${port}/1`, { waitUntil: 'networkidle' })
  await page.waitForFunction(() => (window as any).__layoutCase?.state.ready, { timeout: 30000 })
  for (const scheme of ['light', 'dark']) {
    await page.emulateMedia({ colorScheme: scheme, reducedMotion: 'no-preference' })
    for (const colorset of ['colorset1', 'colorset2']) for (const mode of modes) for (const count of [3, 7, 11]) for (const width of [880, 480]) {
      const columns = count === 3 ? 2 : count === 7 ? 3 : 4
      const pageSize = width === 480 ? 3 : 11
      await auditCase(`${colorset}-${scheme}-${mode}-${count}-${width}`, { mode, count, columns, width, height:390, colorset, pageSize, page:1, reverse:false, filtered:false, manifest:true, custom:false }, false, count === 11 && scheme === 'light')
    }
  }
  // Traverse every narrow page and compare identity colors before/after reorder and filtering.
  for (const colorset of ['colorset1', 'colorset2']) for (const mode of modes) {
    const colors = new Map<string,string>()
    const visited: string[] = []
    for (const pageNumber of [1,2,3,4]) {
      const value = await auditCase(`${colorset}-${mode}-page-${pageNumber}`, { colorset, mode, count:11, columns:3, width:480, height:390, pageSize:3, page:pageNumber, reverse:false, filtered:false, manifest:true, custom:false })
      for (const card of value.cards) { colors.set(card.id,card.fill); visited.push(card.id) }
    }
    if (visited.length !== cards.length || new Set(visited).size !== cards.length) results.push({ id:`${colorset}-${mode}-complete-pagination`, passed:false, failures:['Pagination did not reach every active card exactly once.'], visited })
    for (const pageNumber of [1,2,3,4]) {
      const value = await auditCase(`${colorset}-${mode}-reverse-${pageNumber}`, { page:pageNumber, reverse:true })
      const changed = value.cards.filter((card:any) => colors.get(card.id) !== card.fill)
      if (changed.length) { value.passed=false; value.failures.push('Reordering/pagination changed existing identity colors.') }
    }
    const filtered = await auditCase(`${colorset}-${mode}-filtered`, { page:1, reverse:false, filtered:true })
    if (filtered.cards.some((card:any) => colors.get(card.id) !== card.fill)) { filtered.passed=false; filtered.failures.push('Filtering changed existing identity colors.') }
  }
  // First-seen registry: growing, hiding and reversing within one mounted instance.
  const registryBaseline = await auditCase('registry-initial', { colorset:'colorset1', mode:'masonry-columns', count:3, columns:2, width:880, height:390, pageSize:11, page:1, manifest:false, filtered:false, reverse:false })
  const registryColors = new Map(registryBaseline.cards.map((card:any) => [card.id,card.fill]))
  for (const [id, change] of [['grow',{count:11,columns:4}],['filter',{filtered:true}],['reverse',{filtered:false,reverse:true}],['restore',{count:3,columns:2,reverse:false}]] as any) {
    const value = await auditCase(`registry-${id}`, change)
    if (value.cards.some((card:any) => registryColors.has(card.id) && registryColors.get(card.id) !== card.fill)) { value.passed=false; value.failures.push('First-seen registry reassigned an existing category.') }
  }
  await page.emulateMedia({ colorScheme:'light', reducedMotion:'reduce' })
  for (const colorset of ['colorset1','colorset2']) for (const mode of modes) await auditCase(`${colorset}-${mode}-reduced-motion`, { colorset, mode, count:7, columns:3, width:880, height:390, pageSize:11, page:1, reverse:false, filtered:false, manifest:true, custom:false })
  await auditCase('custom-item-slot', { mode:'grid', count:3, columns:3, width:880, height:390, pageSize:11, page:1, custom:true }, false, true)
  await auditCase('custom-slot-14px', { mode:'grid', count:3, columns:3, width:880, height:390, pageSize:11, page:1, custom:true, smallSlot:true }, false, true)
  await auditCase('custom-slot-14px-resize', { width:480 }, false, true)
  await auditCase('custom-slot-14px-count', { count:7, columns:3, pageSize:3 }, false, true)
  for (const mode of modes) {
    const visited:string[]=[]
    for (const pageNumber of [1,2,3,4]) {
      const value=await auditCase(`long-copy-${mode}-page-${pageNumber}`, { mode, count:11, columns:3, width:880, height:390, pageSize:3, page:pageNumber, custom:false, smallSlot:false, longCopy:true, filtered:false, reverse:false })
      visited.push(...value.cards.map((card:any)=>card.id))
    }
    if (visited.length !== 11 || new Set(visited).size !== 11) results.push({id:`long-copy-${mode}-complete`,passed:false,failures:['Pagination recovery did not preserve all eleven full-text cards.'],visited})
  }
  const fixed = await auditCase('fixed-slot-initial', { mode:'grid', count:3, columns:3, width:880, height:390, pageSize:3, page:1, custom:true, fixedGeometry:true, longCopy:false, smallSlot:false }, false, true)
  for (let tick=1; tick<=4; tick++) {
    const value=await auditCase(`fixed-slot-settle-${tick}`, {})
    if (value.cards.some((card:any,index:number)=>Math.abs(card.height-fixed.cards[index].height)>.5)) { value.passed=false; value.failures.push('Fixed slot dimensions grew during repeated native settling.') }
  }
  await auditCase('fixed-slot-resize', { width:780 }, false, true)
  const feedback = await auditCase('capacity-parent-feedback', { mode:'masonry-rows', count:7, columns:3, rows:3, width:880, height:390, pageSize:6, page:1, custom:false, fixedGeometry:false, feedback:true, longCopy:false }, false, true)
  for (let tick=1;tick<=3;tick++) {
    const value=await auditCase(`capacity-parent-feedback-settle-${tick}`, {})
    if (value.capacityEmissions-feedback.capacityEmissions>3) { value.passed=false; value.failures.push('Public capacity feedback continued emitting equivalent settled reports.') }
  }
  await auditCase('capacity-parent-feedback-resize', { width:760 }, false, true)
  await auditCase('negative-capacity', { mode:'grid', count:11, columns:4, width:220, height:80, pageSize:11, page:1, custom:false, fixedGeometry:false, feedback:false, longCopy:false }, true, true)
} finally {
  await browser.close()
  await new Promise<void>(resolve => server.close(() => resolve()))
}
const report = { passed: results.every(result=>result.passed) && !errors.length, template, dependencies, sourceHashes, cases:results, errors }
await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2))
console.log(JSON.stringify({ passed:report.passed, cases:results.length, failed:results.filter(result=>!result.passed).map(({id,failures})=>({id,failures})), errors, sourceHashes, report:path.join(output,'verification.json') },null,2))
if (!report.passed) process.exitCode=1
