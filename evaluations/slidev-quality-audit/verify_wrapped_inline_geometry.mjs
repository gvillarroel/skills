#!/usr/bin/env node
// Usage: node verify_wrapped_inline_geometry.mjs --fixture <deck> --url <slide-url> --out <report.json>

import assert from 'node:assert/strict'
import { writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { resolve } from 'node:path'

const args = new Map()
for (let index = 2; index < process.argv.length; index += 2)
  args.set(process.argv[index], process.argv[index + 1])

const fixture = resolve(args.get('--fixture') || 'evaluations/slidev-quality-audit/fixture')
const url = args.get('--url')
const out = resolve(args.get('--out') || 'evaluations/runs/slidev-quality-audit-wrapped-inline-local/geometry-report.json')
assert(url, '--url is required')

const requireFromFixture = createRequire(resolve(fixture, 'package.json'))
const { chromium } = requireFromFixture('playwright')
const browser = await chromium.launch({ headless: true })

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } })
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.waitForSelector('[data-testid="wrapped-inline"]')

  const geometry = await page.$eval('[data-testid="wrapped-inline"]', (node) => {
    const rect = node.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const centerNode = document.elementFromPoint(centerX, centerY)
    const isOwnTextSurface = (candidate) => candidate === node
      || (candidate !== null && node.contains(candidate))
      || (candidate !== null && candidate.contains(node))
    const fragments = [...node.getClientRects()]
      .filter(fragment => fragment.width > 1 && fragment.height > 1)
      .map((fragment) => {
        const x = fragment.left + fragment.width / 2
        const y = fragment.top + fragment.height / 2
        const top = document.elementFromPoint(x, y)
        return {
          x: fragment.x,
          y: fragment.y,
          width: fragment.width,
          height: fragment.height,
          topTestId: top?.getAttribute('data-testid') || null,
          ownTextSurface: isOwnTextSurface(top),
        }
      })

    return {
      unionRect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
      legacyUnionCenter: {
        x: centerX,
        y: centerY,
        topTestId: centerNode?.getAttribute('data-testid') || null,
        ownTextSurface: isOwnTextSurface(centerNode),
      },
      fragments,
    }
  })

  assert.equal(geometry.legacyUnionCenter.topTestId, 'neighbor-token')
  assert.equal(geometry.legacyUnionCenter.ownTextSurface, false)
  assert(geometry.fragments.length >= 2)
  assert(geometry.fragments.every(fragment => fragment.ownTextSurface))

  await writeFile(out, `${JSON.stringify({ status: 'pass', ...geometry }, null, 2)}\n`, 'utf8')
  console.log(`PASS: legacy union center lands on neighbor-token while all ${geometry.fragments.length} fragment centers resolve to the wrapped inline text.`)
}
finally {
  await browser.close()
}
