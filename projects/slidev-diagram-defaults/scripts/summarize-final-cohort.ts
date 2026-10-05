#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-diagram-defaults/scripts/summarize-final-cohort.ts
// Dependencies: Node >=24 and installed @slidev/parser from the read-only ECharts fixture dependencies.
import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const root = process.cwd()
const require = createRequire(path.resolve(root, 'skills/slidev-echarts/assets/examples/slidev-echarts/node_modules/@slidev/parser/package.json'))
const { parseSync } = require('@slidev/parser/core')
const expected = 'b16f9f5cade2898beead219b0c451636e8608d16dc162dcb26043dd5c122b8da'
const rows: any[] = []
for (const skill of ['echarts', 'animejs']) {
  for (const caseName of ['contract', 'natural-1', 'natural-2', 'natural-3']) {
    const id = `20261005-slidev-mermaid-${skill}-sol-final-${caseName}`
    const slidePath = path.resolve(root, 'evaluations/runs', id, 'workspace/deck/slides.md')
    const source = await readFile(slidePath, 'utf8')
    const parsed = parseSync(source, slidePath)
    const mermaidCounts = parsed.slides.map((slide: any) => [...slide.content.matchAll(/^\s*```mermaid\b[^\n]*\n([\s\S]*?)^\s*```\s*$/gm)].length)
    const plain = !/classDef\b|^\s*style\s|%%\{\s*init\b|```mermaid\s+\{[^}]*theme/m.test(source)
    const report = JSON.parse(await readFile(path.resolve(root, 'projects/slidev-diagram-defaults/artifacts/pi-final', id, 'verification.json'), 'utf8'))
    const passed = parsed.slides.length === 3 && mermaidCounts.every((count: number) => count === 1) && plain && report.passed && report.helperSha256 === expected
    rows.push({ id, skill, case: caseName, slideCount: parsed.slides.length, mermaidCounts, plain, nativePasses: report.cases.filter((item: any) => item.passed).length, helperSha256: report.helperSha256, passed })
  }
}
const summary = { passed: rows.every(row => row.passed), deckCount: rows.length, nativeCaseCount: rows.reduce((sum, row) => sum + row.nativePasses, 0), rows }
const destination = path.resolve(root, 'projects/slidev-diagram-defaults/artifacts/pi-final/final-cohort-summary.json')
await writeFile(destination, JSON.stringify(summary, null, 2))
console.log(JSON.stringify(summary, null, 2))
if (!summary.passed) process.exitCode = 1
