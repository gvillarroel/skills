#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-diagram-defaults/scripts/inspect-contrast.ts <verification.json>
// Dependencies: Node >=24 only.
import { readFile } from 'node:fs/promises'
const report = JSON.parse(await readFile(process.argv[2], 'utf8'))
for (const item of report.cases)
  console.log(item.id, JSON.stringify(item.textContrasts.filter((text: any) => text.inside && text.fill !== text.best)))
