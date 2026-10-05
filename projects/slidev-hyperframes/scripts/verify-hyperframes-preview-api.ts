#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes-preview-api.ts
// Uses the owning fixture's qualified dependencies; tests normal public Vue refs in an isolated generated deck.
import { createRequire } from 'node:module'
import { resolve, join, extname } from 'node:path'
import { mkdir, mkdtemp, readFile, writeFile, symlink } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { createServer } from 'node:http'
import assert from 'node:assert/strict'

const root=resolve(import.meta.dirname,'../../..'), output=join(root,'projects/slidev-hyperframes/artifacts/preview-api')
await mkdir(output,{recursive:true})
const run=await mkdtemp(join(output,'run-')),deck=join(run,'deck'),owner=join(root,'skills/slidev-echarts')
const dependencies=join(owner,'assets/examples/slidev-echarts/node_modules'),execute=promisify(execFile)
const {chromium}=createRequire(join(dependencies,'../package.json'))('playwright')
await execute('uv',['run','--script',join(owner,'scripts/scaffold_hyperframes_deck.py'),'--deck',deck],{cwd:root,maxBuffer:1_000_000})
await symlink(dependencies,join(deck,'node_modules'),'junction')
await writeFile(join(deck,'components/PreviewApiDiagnostic.vue'),`<script setup lang="ts">
import { ref } from 'vue'
import HyperframePreview from './HyperframePreview.vue'
const preview=ref<InstanceType<typeof HyperframePreview>>()
</script>
<template><div data-public-api-probe><HyperframePreview ref="preview" :controls="false" :height="330" />
<button data-public-play @click="preview?.play()">External play</button>
<button data-public-pause @click="preview?.pause()">External pause</button>
<button data-public-seek @click="preview?.seek(9)">External seek</button></div></template>
`)
await writeFile(join(deck,'slides.md'),(await readFile(join(deck,'slides.md'),'utf8'))+'\n---\nlayout: default\n---\n\n<PreviewApiDiagnostic />\n')
const build=await execute(process.execPath,[join(dependencies,'@slidev/cli/bin/slidev.mjs'),'build','--base','./'],{cwd:deck,maxBuffer:30_000_000})
await writeFile(join(run,'build.log'),build.stdout+build.stderr)
const server=createServer(async(req,res)=>{try{const file=join(deck,'dist',decodeURIComponent(new URL(req.url,'http://localhost').pathname));const bytes=await readFile(extname(file)?file:join(deck,'dist/index.html'));res.writeHead(200,{'Content-Type':({'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.json':'application/json'})[extname(file)]||'text/html'});res.end(bytes)}catch{res.writeHead(404);res.end()}})
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve))
const browser=await chromium.launch({headless:true}),page=await browser.newPage(),errors=[]
page.on('pageerror',error=>errors.push(error.message))
try{
  await page.goto('http://127.0.0.1:'+server.address().port+'/4')
  const probe=page.locator('[data-public-api-probe]:visible')
  await probe.locator('.hyperframe-slide[data-ready="true"][data-time="0"]').waitFor()
  assert.equal(await probe.locator('.hyperframe-preview-control').count(),0)
  await probe.locator('[data-public-play]').click()
  await page.waitForFunction(()=>[...document.querySelectorAll('[data-public-api-probe]')].some(p=>p.getBoundingClientRect().width>0&&Number(p.querySelector('.hyperframe-slide').dataset.time)>.2))
  const played=Number(await probe.locator('.hyperframe-slide').getAttribute('data-time'))
  await probe.locator('[data-public-pause]').click();await page.waitForTimeout(100)
  const stopped=Number(await probe.locator('.hyperframe-slide').getAttribute('data-time'));await page.waitForTimeout(200)
  const stable=Number(await probe.locator('.hyperframe-slide').getAttribute('data-time'));assert.equal(stopped,stable)
  await probe.locator('[data-public-seek]').click();await probe.locator('.hyperframe-slide[data-ready="true"][data-time="9"]').waitFor()
  const iframe=await probe.locator('iframe').elementHandle(),frame=await iframe.contentFrame()
  const level=await frame.locator('[data-scene-mark="level-readout"]').textContent();assert.equal(level,'70%');assert.deepEqual(errors,[])
  const sourceSha256=createHash('sha256').update(await readFile(join(deck,'components/HyperframePreview.vue'))).digest('hex')
  const report={passed:true,run,sourceSha256,controls:false,actualPlayedTime:played,pausedTime:stopped,stableTime:stable,seekTime:9,actualLevel:level,errors,freshInstall:false}
  await writeFile(join(output,'verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2))
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
