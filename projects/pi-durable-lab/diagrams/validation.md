# Diagram validation

Validated on 2026-10-19 against the lab's pinned Pi Durable 1.3.0 API. These diagrams explain tested runtime concepts; they do not add coverage for live providers or remote hosts.

## Outputs

| Source | Rendered output | Browser preview | Structure |
|---|---|---|---|
| [runtime-flow.mmd](runtime-flow.mmd) | `artifacts/svgs/runtime-flow.svg` | `artifacts/screenshots/runtime-flow.png` | 10 nodes, 12 directed relations; 826.84 x 714 viewBox |
| [decision-guide.mmd](decision-guide.mmd) | `artifacts/svgs/decision-guide.svg` | `artifacts/screenshots/decision-guide.png` | 11 nodes, 10 directed relations; 1019.20 x 534 viewBox |

The authored sources are retained under this directory. Output paths in the table are relative to `projects/pi-durable-lab/`. SVGs, screenshots, comparison sources, and JSON verification output are local artifacts under the ignored `artifacts/` tree.

## Commands and results

Commands ran from the repository root unless stated otherwise. The existing repository-local Mermaid skill supplied deterministic styling and rendering; no skill bundle was modified.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'projects/pi-durable-lab/artifacts/cache'

uv run --script .agents/skills/mermaid/scripts/style_mermaid_directory.py projects/pi-durable-lab/diagrams --write --report projects/pi-durable-lab/artifacts/manifests/mermaid-style.json

uv run --script .agents/skills/mermaid/scripts/style_mermaid_directory.py projects/pi-durable-lab/diagrams --check --require-accessibility --report projects/pi-durable-lab/artifacts/manifests/mermaid-check.json

uv run --script .agents/skills/mermaid/scripts/animate_mermaid_svg.py projects/pi-durable-lab/diagrams/runtime-flow.mmd -o projects/pi-durable-lab/artifacts/svgs/runtime-flow.svg --animation none --require-accessibility

uv run --script .agents/skills/mermaid/scripts/animate_mermaid_svg.py projects/pi-durable-lab/diagrams/decision-guide.mmd -o projects/pi-durable-lab/artifacts/svgs/decision-guide.svg --animation none --require-accessibility

git diff --check -- projects/pi-durable-lab/diagrams
```

All commands exited successfully. Final styler results: `diagramCount: 2`, `declarationsSeen: [flowchart]`, `colorset: colorset1`, `changedFileCount: 0`, `missingStyleCount: 0`, and `missingAccessibilityCount: 0`. Both SVG render gates verified referenced accessible title and description metadata and rejected Mermaid error markers.

Browser inspection used the already installed Playwright module from `@playwright/cli` and an existing Chromium headless-shell executable (`chromium_headless_shell-1243`), with temporary files under `artifacts/cache/playwright`. The inspection ran as `node --input-type=module -e $piInspectScript` from `projects/pi-durable-lab`, reading each SVG, inserting it into a blank browser document with XML namespaces preserved, and capturing `page.locator('svg').screenshot(...)`.

The essential insertion operation was:

```javascript
const xml = new DOMParser().parseFromString(source, 'image/svg+xml');
document.body.appendChild(document.importNode(xml.documentElement, true));
```

Using `setContent()` to concatenate the serialized SVG into HTML loses the meaning of prefixed XHTML line breaks; that preview was rejected. Direct full-page screenshots of an SVG document timed out in the installed browser. XML-preserving insertion followed by an SVG-element screenshot completed successfully. No browser download or global installation was needed.

Local browser observations in `artifacts/manifests/diagrams-browser.json` confirm that both outputs have referenced nonempty titles/descriptions, zero error markers, zero SVG animation elements, and `data-colorset="colorset1"`. Visible node fills are exactly `#9e1b32`, `#000000`, and `#828282`. Both final screenshots were opened and visually inspected: complete labels, readable black/white text, visible arrowheads, independent routes, no text clipping, and no misleading relation through an unrelated node.

## Meaning and composition review

Primary runtime contract: committed admission, committed effect intent, external execution, committed result, then an answer. Restart routes visibly distinguish generation, a safe replay, and an unsafe tool's interrupted result. The external-effect node states that idempotency is required. Storage commits and external work have separate labels and roles.

Primary selection contract: choose the finished coding product for local terminal work, or the embedded durable runtime for an application that owns recovery/client state; then choose storage, composition, and lifetime deliberately. A quiet, borderless application group keeps Durable's configuration branches away from the Coding Agent card.

Composition comparison retained locally under `artifacts/diagram-comparison/`:

- Runtime: reordered the final-answer branch before the tool branch, removing the crossing between the answer route and tool execution. Simplified the host call to the real signature `root.submit(input, context)` and stated the stable `input.requestId` separately. Bounds decreased from 932.13 x 738 to 826.84 x 714 without reducing the 16 px type.
- Decision guide: replaced the oversized question diamond with a rectangular question card. An initial tighter 734.30 x 500 layout was rejected because a configuration connector passed through the Coding Agent region. Grouping the Durable branch increases width to 1019.20 while keeping every relation independently traceable; this was preferred to a smaller misleading layout.

## Fidelity ledger

Detail: balanced; 10 runtime nodes and 11 selection nodes. Audience: developer building a first application. Destination: local Markdown guide and standalone static SVG. Palette: colorset1. Motion: none.

- Kept: stable request ID, atomic admission, generation, committed tool intent, external execution, committed result, final answer, wait settlement, restart/checkpoints, safe/unsafe tool recovery, and external idempotency.
- Kept: Coding Agent versus Durable 1.3.0, SQLite default, Memory tests, JSONL readability, direct-tools default, code mode composition, and foreground/background lifetime choice.
- Merged: model-response processing into `pi.generation`; individual storage records into admission/intent/result/answer cards; each configuration's related alternatives into one card.
- Moved to guide text: exact tool replay opt-in, live-provider limitations, queue/error policies, document semantics, compaction thresholds, usage, hooks, extension selection, power-loss guarantees, and the one-owner storage rule.
- Adapted explanatory wording: "JSONL readable archive" becomes "JSONL: readable small logs" because the documented backend retains its full history in memory and is best presented as a small inspectable-log option. No retention or archival guarantee is added.
- Omitted from these overviews: development-only `sleepUntil`, `wake`, telemetry, crash parking, and other APIs absent from 1.3.0. They are covered as version differences in the source review and guide.

The accessible metadata gate verifies a useful SVG title and description, not complete structural navigation of every relation for screen readers. The visual review establishes these two diagrams' local presentation, not universal browser compatibility.
