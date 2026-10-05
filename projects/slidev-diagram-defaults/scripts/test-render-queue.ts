#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-diagram-defaults/scripts/test-render-queue.ts
// Requires Node.js 24+; uses native TypeScript stripping and no npm packages.

import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createColorsetRenderer, mermaidColorsetConfig } from '../../../skills/slidev-echarts/assets/templates/slidev-diagram-style/diagram-style.mjs'

const paletteUrl = new URL('../../../skills/slidev-echarts/assets/palettes/colorsets.json', import.meta.url)
const palettes = JSON.parse(await readFile(paletteUrl, 'utf8')).colorsets

function authoredColors(value: unknown): string[] {
  if (typeof value === 'string')
    return [...value.matchAll(/#[0-9a-f]{6}/gi)].map(match => match[0].toLowerCase())
  if (value && typeof value === 'object')
    return Object.values(value).flatMap(authoredColors)
  return []
}

for (const selected of ['colorset1', 'colorset2']) {
  const config = mermaidColorsetConfig(selected)
  const outside = [...new Set(authoredColors(config))].filter(color => !palettes[selected].allowed.includes(color))
  assert.deepEqual(outside, [], `${selected} contains colors outside its exact palette`)
}

// The native renderer stores shared configuration and resolves asynchronously.
// Two independently created hooks must retain their own requested native theme.
let activeTheme: string | undefined
const nativeMock = {
  initialize(config: { theme?: string }) {
    activeTheme = config.theme
  },
  async render(_id: string, code: string) {
    await new Promise(resolve => setTimeout(resolve, 5))
    if (code === 'invalid')
      throw new Error('Expected native parse failure')
    return { svg: `<svg data-code="${code}" data-theme="${activeTheme}"/>` }
  },
}

const first = createColorsetRenderer(nativeMock, () => mermaidColorsetConfig())
const second = createColorsetRenderer(nativeMock, () => mermaidColorsetConfig())
const output = await Promise.all([
  first('first', { colorsetPresentation: 'source', theme: 'forest' }),
  second('second', { colorsetPresentation: 'source', theme: 'neutral' }),
])
assert.deepEqual(output, [
  '<svg data-code="first" data-theme="forest"/>',
  '<svg data-code="second" data-theme="neutral"/>',
])
await assert.rejects(
  first('invalid', { colorsetPresentation: 'source', theme: 'dark' }),
  /Expected native parse failure/,
)
assert.equal(
  await second('recovered', { colorsetPresentation: 'source', theme: 'base' }),
  '<svg data-code="recovered" data-theme="base"/>',
)
console.log('Passed: exact palette configurations, shared native render serialization, source style preservation, and recovery after a native parse failure.')
