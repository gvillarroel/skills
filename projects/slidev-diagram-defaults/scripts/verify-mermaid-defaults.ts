#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-diagram-defaults/scripts/verify-mermaid-defaults.ts --template skills/slidev-echarts/assets/templates/slidev-diagram-style --palette colorset1 --scheme light
// Dependencies: Node >=24; @slidev/cli, @slidev/theme-default and playwright from --dependencies (existing fixture by default).
// This evaluator owns its inputs and checks actual Chromium SVG/shadow-root paint.
import { readFile, writeFile, mkdir, cp, symlink, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import http from 'node:http'

const args = process.argv.slice(2)
function arg(name: string, fallback = '') {
  const index = args.indexOf(name)
  return index >= 0 ? args[index + 1] : fallback
}
const root = process.cwd()
const palette = arg('--palette', 'colorset1')
const scheme = arg('--scheme', 'light')
if (!['colorset1', 'colorset2'].includes(palette) || !['light', 'dark'].includes(scheme))
  throw new Error('Use --palette colorset1|colorset2 and --scheme light|dark.')
const deps = path.resolve(arg('--dependencies', 'skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const template = path.resolve(arg('--template', 'skills/slidev-echarts/assets/templates/slidev-diagram-style'))
const output = path.resolve(arg('--output', `projects/slidev-diagram-defaults/artifacts/${palette}-${scheme}`))
const deck = path.resolve(arg('--deck', path.join(output, 'deck')))
const paletteSource = path.resolve(arg('--palette-source', 'skills/slidev-echarts/assets/palettes/colorsets.json'))
const existing = args.includes('--existing')
const onlySlide = Number(arg('--slide', '0'))
const sourceMode = args.includes('--source')
const cases = [
  { id: 'flowchart', labels: ['Intake', 'Review', 'Publish', 'checks', 'releases'], code: 'flowchart LR\n  Intake -->|checks| Review\n  Review -->|releases| Publish' },
  { id: 'sequence', labels: ['Client', 'Service', 'request', 'response'], code: 'sequenceDiagram\n  participant Client\n  participant Service\n  Client->>Service: request\n  Service-->>Client: response' },
  { id: 'class', labels: ['Request', 'Service', 'uses', 'id', 'handle'], code: 'classDiagram\n  class Request {\n    +String id\n  }\n  class Service {\n    +handle() void\n  }\n  Request ..> Service : uses' },
  { id: 'state', labels: ['Intake', 'Review', 'Publish', 'checks', 'releases'], code: 'stateDiagram-v2\n  [*] --> Intake\n  Intake --> Review: checks\n  Review --> Publish: releases\n  Publish --> [*]' },
  { id: 'er', labels: ['REQUEST', 'SERVICE', 'handles', 'id', 'name'], code: 'erDiagram\n  REQUEST {\n    string id PK\n  }\n  SERVICE {\n    string name\n  }\n  SERVICE ||--o{ REQUEST : handles' },
  { id: 'pie', labels: ['Intake', 'Review', 'Publish'], code: 'pie showData\n  title Review stages\n  "Intake" : 30\n  "Review" : 45\n  "Publish" : 25' },
]
if (args.includes('--extended')) {
  cases.splice(0, cases.length,
    { id: 'mindmap', labels: ['Delivery', 'Intake', 'Review', 'Publish'], code: 'mindmap\n  root((Delivery))\n    Intake\n    Review\n    Publish' },
    { id: 'gantt', labels: ['Intake', 'Review', 'Publish'], code: 'gantt\n  title Release schedule\n  dateFormat YYYY-MM-DD\n  axisFormat %m-%d\n  section Delivery\n    Intake :a, 2026-10-01, 2d\n    Review :b, after a, 2d\n    Publish :c, after b, 1d' },
    { id: 'gitgraph', labels: ['Intake', 'Review', 'Publish', 'main', 'review'], code: 'gitGraph\n  commit id: "Intake"\n  branch review\n  checkout review\n  commit id: "Review"\n  checkout main\n  merge review id: "Publish"' },
    { id: 'timeline', labels: ['Release stages', 'Intake', 'Review', 'Publish'], code: 'timeline\n  title Release stages\n  2026-10 : Intake : Review : Publish' },
  )
}
await mkdir(output, { recursive: true })
await mkdir(deck, { recursive: true })
if (!existing) {
  await cp(template, deck, { recursive: true })
  const setupPath = path.join(deck, 'setup', 'mermaid.ts')
  const setupSource = await readFile(setupPath, 'utf8')
  await writeFile(setupPath, setupSource.replace(/mermaidColorsetConfig\('colorset1'\)/, `mermaidColorsetConfig('${palette}')`))
  await writeFile(path.join(deck, 'package.json'), JSON.stringify({ name: 'mermaid-default-evaluator', private: true, type: 'module', scripts: { build: 'slidev build --base ./' }, dependencies: { '@slidev/cli': '52.16.0', '@slidev/theme-default': '0.25.0' } }, null, 2))
  const frontmatter = `---\ntheme: default\ncolorSchema: ${scheme}\nfonts:\n  sans: Open Sans\n---\n\n`
  const deckCases = sourceMode ? cases.slice(0, 1) : cases
  const slides = deckCases.map((item) => `# ${item.id}\n\n\`\`\`mermaid${sourceMode ? " {colorsetPresentation: 'source', theme: 'forest'}" : item.id === 'timeline' ? ' {scale: 0.65}' : ''}\n${item.code}\n\`\`\`\n`).join('\n---\n\n')
  await writeFile(path.join(deck, 'slides.md'), frontmatter + slides)
}
const source = await readFile(path.join(deck, 'slides.md'), 'utf8')
const helperPath = path.resolve(arg('--helper-path', path.join(deck, 'diagram-style.mjs')))
const helperSha256 = existsSync(helperPath) ? createHash('sha256').update(await readFile(helperPath)).digest('hex') : null
const expectedHelperSha = arg('--expect-helper-sha')
if (expectedHelperSha && helperSha256 !== expectedHelperSha)
  throw new Error(`Copied runtime helper SHA-256 mismatch: expected ${expectedHelperSha}, observed ${helperSha256}.`)
if (!sourceMode && !onlySlide && /classDef\b|^\s*style\s|%%\{\s*init\b|```mermaid\s+\{[^}]*theme/m.test(source))
  throw new Error('Evaluator source must use plain Mermaid without styling directives.')
const nodeModules = path.join(deck, 'node_modules')
if (!existsSync(nodeModules)) await symlink(deps, nodeModules, 'junction')
const require = createRequire(path.join(deps, 'playwright', 'package.json'))
const { chromium } = require('playwright')

function run(command: string, commandArgs: string[], cwd: string) {
  return new Promise<void>((resolve, reject) => {
    const child = spawn(command, commandArgs, { cwd, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true })
    let output = ''
    child.stdout.on('data', chunk => { output += chunk })
    child.stderr.on('data', chunk => { output += chunk })
    child.on('error', reject)
    child.on('close', async code => {
      await writeFile(path.join(outputDir, 'build.log'), output)
      if (code === 0) resolve()
      else reject(new Error(`Slidev build failed (${code}). Inspect ${path.join(outputDir, 'build.log')}.`))
    })
  })
}
const outputDir = output
if (!args.includes('--skip-build'))
  await run(process.execPath, [path.join(deps, '@slidev/cli/bin/slidev.mjs'), 'build', 'slides.md', '--out', path.join(output, 'html'), '--base', './'], deck)
const html = path.resolve(arg('--html', path.join(output, 'html')))
const mime: Record<string, string> = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' }
const server = http.createServer(async (request, response) => {
  try {
    let candidate = path.resolve(html, `.${decodeURIComponent(new URL(request.url || '/', 'http://local').pathname)}`)
    if (!candidate.startsWith(html + path.sep) && candidate !== html) { response.writeHead(403).end(); return }
    if (!existsSync(candidate) || (await stat(candidate)).isDirectory()) candidate = path.join(html, 'index.html')
    const body = await readFile(candidate)
    response.writeHead(200, { 'content-type': mime[path.extname(candidate)] || 'application/octet-stream' }).end(body)
  }
  catch (error) { response.writeHead(500).end(String(error)) }
})
await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve))
const address = server.address() as { port: number }
const base = `http://127.0.0.1:${address.port}`
const declared = JSON.parse(await readFile(paletteSource, 'utf8')).colorsets[palette]
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 })
const consoleErrors: string[] = []
const ignoredConsoleErrors: string[] = []
page.on('pageerror', (error: Error) => {
  const message = String(error)
  if (message === 'NotAllowedError: Wake Lock permission request denied') ignoredConsoleErrors.push(message)
  else consoleErrors.push(message)
})
const results: any[] = []
try {
  const slideCases = onlySlide ? [{ id: `slide-${onlySlide}`, labels: arg('--labels').split('|').filter(Boolean), code: '' }] : sourceMode ? cases.slice(0, 1) : existing ? cases.slice(0, 3) : cases
  for (let index = 0; index < slideCases.length; index++) {
    const item = slideCases[index]
    await page.goto(`${base}/${args.includes('--hash-route') ? '#/' : ''}${onlySlide || index + 1}`, { waitUntil: 'networkidle' })
    await page.waitForFunction((label: string) => {
      const roots = [...document.querySelectorAll('*')].map((element: any) => element.shadowRoot).filter(Boolean)
      return roots.some((root: any) => [...root.querySelectorAll('svg')].some((svg: any) => svg.getBoundingClientRect().width > 0 && (!label || svg.textContent.includes(label))))
    }, item.labels[0] || '', { timeout: 30000 })
    await page.waitForTimeout(200)
    const audit = await page.evaluate(({ allowed, expected, family, preserveSource }: { allowed: string[], expected: string[], family: string, preserveSource: boolean }) => {
      function hex(value: string) {
        if (!value || value === 'none' || value === 'transparent' || value.startsWith('url(')) return null
        const numbers = value.match(/[\d.]+/g)?.map(Number)
        if (value.startsWith('rgb') && numbers && numbers.length >= 3) {
          if (numbers.length > 3 && numbers[3] === 0) return null
          return '#' + numbers.slice(0, 3).map(number => Math.round(number).toString(16).padStart(2, '0')).join('')
        }
        return value.toLowerCase()
      }
      function luminance(value: string) {
        const channels = value.slice(1).match(/../g)!.map(value => parseInt(value, 16) / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4)
        return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722
      }
      function contrast(a: string, b: string) { const x = luminance(a); const y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05) }
      const roots: ShadowRoot[] = [...document.querySelectorAll('*')].map((element: any) => element.shadowRoot).filter(Boolean)
      const svgs: SVGSVGElement[] = roots.flatMap(root => [...root.querySelectorAll<SVGSVGElement>('svg')]).filter(svg => svg.getBoundingClientRect().width > 0)
      const svg = svgs.find(svg => svg.textContent?.includes(expected[0])) || svgs[0]
      if (!svg) return { passed: false, failures: ['No rendered Mermaid SVG.'] }
      const rect = svg.getBoundingClientRect()
      const surface = hex(getComputedStyle(svg).backgroundColor) || '#ffffff'
      const paint: any[] = []
      const outside: any[] = []
      for (const element of svg.querySelectorAll('*')) {
        if (element.closest('defs,clipPath,mask,style')) continue
        const box = element.getBoundingClientRect()
        if (box.width === 0 && box.height === 0) continue
        const css = getComputedStyle(element)
        for (const property of ['fill', 'stroke', 'color', 'background-color']) {
          const value = hex(css.getPropertyValue(property))
          if (!value) continue
          if ((property === 'color' || property === 'background-color') && element instanceof SVGElement) continue
          const record = { tag: element.tagName, classes: element.getAttribute('class'), property, value, text: element.textContent?.trim().slice(0, 80) }
          paint.push(record)
          if (!allowed.includes(value)) outside.push(record)
        }
      }
      const visibleText = [...svg.querySelectorAll('text,tspan,foreignObject')].map(element => element.textContent || '').join(' ')
      const missing = expected.filter(label => !visibleText.includes(label))
      const clippedText: any[] = []
      for (const foreignObject of svg.querySelectorAll('foreignObject')) {
        const backing = foreignObject.getBoundingClientRect()
        if (!backing.width || !backing.height) continue
        const walker = document.createTreeWalker(foreignObject, NodeFilter.SHOW_TEXT)
        let node = walker.nextNode()
        while (node) {
          if (node.textContent?.trim()) {
            const range = document.createRange()
            range.selectNodeContents(node)
            for (const glyphs of range.getClientRects()) {
              if (glyphs.left < backing.left - 1.5 || glyphs.right > backing.right + 1.5 || glyphs.top < backing.top - 1.5 || glyphs.bottom > backing.bottom + 1.5)
                clippedText.push({ text: node.textContent, backing: { x: backing.x, y: backing.y, width: backing.width, height: backing.height }, glyphs: { x: glyphs.x, y: glyphs.y, width: glyphs.width, height: glyphs.height } })
            }
          }
          node = walker.nextNode()
        }
      }
      const textContrasts: any[] = []
      const backingShapes = [...svg.querySelectorAll<SVGGeometryElement>('rect,circle,ellipse,polygon,path')].filter(element => !element.closest('defs,clipPath,mask') && hex(getComputedStyle(element).fill))
      for (const element of svg.querySelectorAll('text,tspan,foreignObject span')) {
        if (element.tagName.toLowerCase() === 'text' && element.querySelector('tspan')) continue
        const box = element.getBoundingClientRect()
        if (!element.textContent?.trim() || !box.width || !box.height) continue
        const center = { x: box.x + box.width / 2, y: box.y + box.height / 2 }
        const fill = hex(element instanceof SVGElement ? getComputedStyle(element).fill : getComputedStyle(element).color)
        if (!fill) continue
        const contained = backingShapes.filter(shape => {
          try {
            const matrix = shape.getScreenCTM()
            if (!matrix) return false
            const point = new DOMPoint(center.x, center.y).matrixTransform(matrix.inverse())
            return shape.isPointInFill(point)
          } catch { return false }
        }).sort((a, b) => { const x = a.getBoundingClientRect(); const y = b.getBoundingClientRect(); return x.width*x.height-y.width*y.height })
        const background = contained.length ? hex(getComputedStyle(contained[0]).fill)! : surface
        const ratio = contrast(fill, background)
        const best = contrast('#000000', background) > contrast('#ffffff', background) ? '#000000' : '#ffffff'
        textContrasts.push({ text: element.textContent.trim(), fill, background, ratio, best, inside: contained.length > 0 })
      }
      const failures: string[] = []
      if (outside.length && !preserveSource) failures.push(`${outside.length} rendered paints outside declared palette.`)
      if (missing.length) failures.push(`Missing labels: ${missing.join(', ')}.`)
      if (clippedText.length) failures.push(`${clippedText.length} text ranges extend beyond their foreignObject clipping bounds.`)
      if (rect.width < 20 || rect.height < 20) failures.push('Blank or tiny SVG.')
      const badInside = textContrasts.filter(item => item.inside && item.fill !== item.best)
      if (badInside.length && !preserveSource) failures.push(`${badInside.length} inside labels do not use the maximum black/white contrast.`)
      const lowText = textContrasts.filter(item => item.ratio < 4.5)
      if (lowText.length) failures.push(`${lowText.length} text labels have contrast below 4.5:1.`)
      const classDividers: any[] = []
      if (family === 'class') {
        for (const divider of svg.querySelectorAll<SVGGeometryElement>('.divider path,.divider line')) {
          const matrix = divider.getScreenCTM()
          const midpoint = divider.getPointAtLength(divider.getTotalLength() / 2)
          const screenPoint = new DOMPoint(midpoint.x, midpoint.y).matrixTransform(matrix!)
          const contained = backingShapes.filter(shape => {
            if (shape === divider) return false
            const transform = shape.getScreenCTM()
            return transform ? shape.isPointInFill(screenPoint.matrixTransform(transform.inverse())) : false
          }).sort((a, b) => { const x = a.getBoundingClientRect(); const y = b.getBoundingClientRect(); return x.width*x.height-y.width*y.height })
          const css = getComputedStyle(divider)
          const stroke = hex(css.stroke)
          const background = contained.length ? hex(getComputedStyle(contained[0]).fill) : null
          const width = Number.parseFloat(css.strokeWidth)
          const ratio = stroke && background ? contrast(stroke, background) : 0
          classDividers.push({ stroke, background, width, ratio })
        }
        if (!classDividers.length) failures.push('Missing native class compartment separators.')
        const weakDividers = classDividers.filter(item => !item.width || item.ratio < 3)
        if (weakDividers.length) failures.push(`${weakDividers.length} class compartment separators have contrast below 3:1 against their actual node backing.`)
      }
      const clipped = rect.left < 0 || rect.top < 0 || rect.right > innerWidth + 1 || rect.bottom > innerHeight + 1
      if (clipped) failures.push('Diagram SVG falls outside the viewport.')
      const connectorPaint = paint.filter(item => item.property === 'stroke' && /edge|message|relation|transition|flowchart-link|actor-line/i.test(item.classes || ''))
      const markerPaint: any[] = []
      for (const element of svg.querySelectorAll('[marker-start],[marker-end]')) {
        for (const attribute of ['marker-start', 'marker-end']) {
          const reference = element.getAttribute(attribute)?.match(/#([^)]+)/)?.[1]
          if (!reference) continue
          const marker = svg.querySelector(`[id="${reference}"]`)
          for (const shape of marker?.querySelectorAll('path,polygon,circle,line') || []) {
            const css = getComputedStyle(shape)
            for (const property of ['fill', 'stroke']) {
              const color = hex(css.getPropertyValue(property))
              if (color) markerPaint.push({ property, color, ratio: contrast(color, surface) })
            }
          }
        }
      }
      const weakConnectors = connectorPaint.filter(item => contrast(item.value, surface) < 3)
      const weakMarkers = markerPaint.filter(item => item.ratio < 3 && !(item.property === 'fill' && item.color === surface))
      if (weakConnectors.length) failures.push(`${weakConnectors.length} connector strokes have contrast below 3:1.`)
      if (weakMarkers.length) failures.push(`${weakMarkers.length} arrow or relation marker paints have contrast below 3:1.`)
      if (!['pie', 'gantt', 'gitgraph', 'timeline', 'mindmap'].includes(family) && !family.startsWith('slide-') && !connectorPaint.length) failures.push('Missing rendered connector strokes.')
      if (!preserveSource && markerPaint.some(item => !allowed.includes(item.color))) failures.push('Referenced marker paint falls outside declared palette.')
      const sourceOutlines = [...svg.querySelectorAll('.node rect,.node path,.node polygon')].map(element => ({ stroke: hex(getComputedStyle(element).stroke), width: Number.parseFloat(getComputedStyle(element).strokeWidth) })).filter(item => item.stroke && item.width > 0)
      if (preserveSource && !paint.some(item => item.property === 'fill' && item.value === '#cde498')) failures.push('Requested native forest node fill was not preserved.')
      if (preserveSource && !sourceOutlines.length) failures.push('Requested native source outlines were not preserved.')
      const dataAttributes = Object.fromEntries([...svg.attributes].filter(attribute => attribute.name.startsWith('data-')).map(attribute => [attribute.name, attribute.value]))
      return { passed: failures.length === 0, failures, bounds: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }, surface, missing, clippedText, paints: [...new Set(paint.map(item => item.value))], outside, textContrasts, connectorPaint, markerPaint, classDividers, sourceOutlines, dataAttributes, svg: svg.outerHTML }
    }, { allowed: declared.allowed, expected: item.labels, family: item.id, preserveSource: sourceMode })
    await writeFile(path.join(output, `${item.id}.svg`), audit.svg || '')
    delete audit.svg
    await page.screenshot({ path: path.join(output, `${item.id}.png`), fullPage: true })
    results.push({ id: item.id, ...audit })
  }
}
finally {
  await browser.close()
  await new Promise<void>(resolve => server.close(() => resolve()))
}
const report = { palette, scheme, sourcePreservation: sourceMode, deck, template: existing ? null : template, helperPath: helperSha256 ? helperPath : null, helperSha256, passed: results.every(item => item.passed) && consoleErrors.length === 0, consoleErrors, ignoredConsoleErrors, cases: results }
await writeFile(path.join(output, 'verification.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify({ palette, scheme, passed: report.passed, cases: results.map(({ id, passed, failures, paints }) => ({ id, passed, failures, paints })), report: path.join(output, 'verification.json') }, null, 2))
if (!report.passed) process.exitCode = 1
