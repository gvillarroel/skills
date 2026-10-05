---
name: slidev-quality-audit
description: "Audits Slidev decks for visual quality regressions with automated Playwright checks and actionable critiques. Use when Codex needs to verify Slidev presentations for off-screen elements, clipped or hidden information, text overlap, low contrast, tiny text, blank charts or media, broken assets, unchanged click states, unsafe margins, and excessive content density before delivering a deck, screenshot set, or video."
---

# Slidev Quality Audit

Read [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed. Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.

## Core Workflow

1. Locate the Slidev deck root, usually the directory containing `package.json` and `slides.md`. For a NEW scratch deck, run the preparation helper from the task workspace before writing the supplied slide:

   ```powershell
   uv run --script <skill-root>/scripts/prepare-audit-deck.py --deck ./deck
   ```

   It creates [the tested dependency package](assets/templates/package.json) only when absent, validates the actual package, and installs with the resolved deck prefix. It preserves an existing package and uses `npm ci` when a lock exists. Keep supplied decks on their existing setup workflow and dependencies unless a reproduced runtime failure requires repair.
2. Create or verify the deck's actual `package.json` before installing anything. Always pass its directory explicitly. For an existing unlocked deck, install declared dependencies with `npm install --prefix /path/to/deck`; retain its lock with `npm ci --prefix /path/to/deck` when present. Add a missing Playwright dependency only when needed with `npm install --prefix /path/to/deck --save-dev playwright`. After writing a new scratch slide, warm its build with `npm --prefix /path/to/deck run build` before the first native audit.

3. Run a diagnostic audit without `--strict`, capturing every native browser state. Preserve its output in a separate before directory; expected presentation findings are report data during diagnosis. Keep generated artifacts outside skill directories:

   ```powershell
   npx --prefix /path/to/deck tsx <skill-root>/scripts/audit-slidev-quality.ts --deck /path/to/deck --out /path/to/projects/<project-id>/artifacts/reports/deck-quality-before --screenshots all
   ```

4. Read `quality-report.md` first, then inspect `quality-report.json` for exact selectors, bounding boxes, thresholds and each `states[].screenshot` path. Open those recorded paths directly. The auditor launches real Chromium; its retained native screenshots are the browser verification surface for manual review. Capture clean states too, because an automated pass does not prove visual quality; DOM bounds can miss painted SVG text failures. Native image inspection and source geometry suffice for this review; do not add an ad hoc pixel probe or assume image-analysis dependencies are installed. Keep captures inside the task workspace; avoid Windows `/tmp` paths.
5. Fix findings that are real presentation problems. Mark intentional exceptions in the deck with attributes or classes instead of weakening global thresholds. For a connected explanatory diagram, perform [the actual readable compactness trial](references/audit-rules.md#readable-compactness-trial) before accepting the result: create and natively render at least one tighter geometry candidate with the same full labels and readable type/head/stroke dimensions. A hypothetical spacing change is not a trial.
6. Re-run the audit after fixes into a separate after directory with `--screenshots all`. Once findings are resolved, run the final gate with `--strict --screenshots all` at the requested report path. Preserve before and after screenshots, compare them at the same viewport, and retain the files referenced by delivered reports.

## Script

Use `scripts/audit-slidev-quality.ts` for the automated pass. It starts a local Slidev server, visits each selected slide, advances detected click states, samples DOM layout and rendered chart/media surfaces, and writes a Markdown and JSON report.

Common options:

```powershell
npx --prefix /path/to/deck tsx <skill-root>/scripts/audit-slidev-quality.ts `
  --deck /path/to/deck `
  --out /path/to/projects/<project-id>/artifacts/reports/deck-quality `
  --range 1,4-8 `
  --max-clicks 3 --screenshots all
```

Reserve `--strict` for a final audit that must exit nonzero on error-level findings; use normal reporting while diagnosing a supplied imperfect deck. `--screenshots all` is the default; `issues` and `none` are explicit alternatives for tasks that do not require complete visual evidence. Use `--allow-overflow-selector`, `--allow-hidden-selector`, and `--ignore-selector` for explicitly intentional exceptions.

## Quality Rules

Read [the marked SVG arrow audit](references/arrow-audit.md) for authored diagram connections. Use stable arrow attributes and inspect both shaft and referenced head at 3:1 against their actual local backing, including opacity and filled paths.

For connected explanatory diagrams, also review whether surplus padding,
rank gaps, empty wrappers or connector detours can be removed while retaining
the same facts and readable text/head/stroke sizes. Create and natively render at least one tighter local
candidate at the same slide scale and type/head/stroke dimensions; reject overlap, clipped labels, obscured
heads, ambiguous source/target attachment, merged unrelated routes or lost
motion clearance. Support every rejection with an observed defect in its native
capture or geometry; vague breathing room, occupancy or unchanged comprehension
is insufficient. Keep distinct lanes and inspect settled click states,
closest motion approaches and final exports. Stop when remaining space
protects reading or routing. Record this as a manual compactness review;
the automated audit does not prove shortest routes or optimal packing.
Preserve chart scales, axes, legends and useful data dimensions. Low whitespace
alone is neither a pass criterion nor a reason to report a defect.

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

## Pattern Promotion

When an audit finding, exception marker, threshold rule, false-positive case, or remediation pattern proves reusable, update `references/audit-rules.md` before finishing. Capture the symptom, detection signal, likely cause, accepted exception marker, fix pattern, and validation command. Keep deck-specific screenshots and reports in `projects/<project-id>/artifacts/reports/`, not in the skill.
