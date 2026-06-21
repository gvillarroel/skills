---
name: slidev-quality-audit
description: Audit Slidev decks for visual quality regressions with automated Playwright checks and actionable critiques. Use when Codex needs to verify Slidev presentations for off-screen elements, clipped or hidden information, text overlap, low contrast, tiny text, blank charts or media, broken assets, unchanged click states, unsafe margins, and excessive content density before delivering a deck, screenshot set, or video.
---

# Slidev Quality Audit

## Core Workflow

1. Locate the Slidev deck root, usually the directory containing `package.json` and `slides.md`.
2. Install missing deck-local dependencies before auditing:

   ```powershell
   npm install --save-dev playwright
   ```

3. Run the bundled quality audit. Keep generated artifacts outside skill directories:

   ```powershell
   npx tsx /path/to/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck /path/to/deck --out /path/to/output/deck-quality
   ```

4. Read `quality-report.md` first, then inspect `quality-report.json` for exact selectors, bounding boxes, and thresholds.
5. Fix findings that are real presentation problems. Mark intentional exceptions in the deck with attributes or classes instead of weakening global thresholds.
6. Re-run the audit after every fix and compare the finding counts, screenshots, and affected slide states.

## Script

Use `scripts/audit-slidev-quality.ts` for the automated pass. It starts a local Slidev server, visits each selected slide, advances detected click states, samples DOM layout and rendered chart/media surfaces, and writes a Markdown and JSON report.

Common options:

```powershell
npx tsx /path/to/slidev-quality-audit/scripts/audit-slidev-quality.ts `
  --deck /path/to/deck `
  --out /path/to/output/deck-quality `
  --range 1,4-8 `
  --max-clicks 3
```

Use `--strict` when the audit should exit nonzero on error-level findings. Use `--allow-overflow-selector`, `--allow-hidden-selector`, and `--ignore-selector` for explicitly intentional exceptions.

## Quality Rules

The script currently checks these issue families:

- Missing or blank visible Slidev layout.
- Document or slide overflow outside the viewport.
- Visible elements outside the slide frame.
- Text clipped by fixed-size containers.
- Text or content hidden in the final click state.
- Text blocks that overlap each other.
- Visible text covered by another element.
- Text contrast below WCAG-style thresholds.
- Text smaller than the configured minimum size.
- Broken, zero-size, blank, or distorted media/chart surfaces.
- Click-driven slides that do not visibly change.
- Excessive word count or too many text blocks for a single slide.
- Text too close to the slide edge.
- Browser console and page errors.

## Exception Markers

Prefer local markers over broad threshold changes:

```html
<div data-allow-overflow>intentional bleed art</div>
<div class="allow-overflow">intentional crop</div>
<h2 data-allow-overflow>intentional split-text clipping</h2>
<div data-allow-hidden>alternate animation state</div>
<div data-slidev-audit-ignore>decorative test fixture</div>
```

## References

Read `references/audit-rules.md` when deciding whether a finding is a real defect, tuning thresholds for a deck style, or explaining a recommendation to a user.
