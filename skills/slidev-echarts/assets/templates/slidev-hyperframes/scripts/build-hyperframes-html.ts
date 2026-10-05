#!/usr/bin/env -S node --experimental-strip-types
// Run from the deck root: node --experimental-strip-types scripts/build-hyperframes-html.ts
// Node 24; @slidev/cli and vite-plugin-singlefile are declared in the deck package.
import { spawnSync } from 'node:child_process'
import { createRequire } from 'node:module'
import { copyFile, readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const require = createRequire(import.meta.url)
const cli = require.resolve('@slidev/cli/bin/slidev.mjs')
const result = spawnSync(process.execPath, [cli, 'build', '--base', './', '--router-mode', 'hash', '--out', 'dist'], {
  cwd: process.cwd(), env: { ...process.env, SLIDEV_SINGLE_FILE: '1' }, stdio: 'inherit',
})
if (result.error) throw result.error
if (result.status !== 0) process.exit(result.status || 1)
const html = await readFile(resolve('dist/index.html'), 'utf8')
const scripts = [...html.matchAll(/<script\b([^>]*)>[\s\S]*?<\/script\s*>/gi)]
const markup = html.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '')
if (scripts.some(match => /\bsrc\s*=/i.test(match[1])) || /<link\b[^>]*\brel=["']stylesheet/i.test(markup)) throw new Error('HTML still has external scripts/styles; enable hyperframesBuildPlugins in vite.config.ts')
await copyFile(resolve('dist/index.html'), resolve('dist/slidev.html'))
console.log('Created dist/slidev.html with deterministic direct-open HyperFrames fallback.')
