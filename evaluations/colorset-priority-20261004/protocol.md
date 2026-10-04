# Colorset 1 Priority Release Protocol

This evaluation isolates the user's 2026-10-04 correction: primary red,
then grays, then black, then white, then the remaining colors. It does not
change allowed tokens, Colorset 2, semantic opacity, native line art,
black/white text selection, or arrow contrast and clearance acceptance.

The independent literal order is:

```text
#9e1b32
#333e48 #4f4f4f #696969 #828282 #9c9c9c #b5b5b5 #cfcfcf #e7e7e7 #363636 #f7f7f7
#1c1c1c #000000
#ffffff
#6d1222 #e8002a #ffccd5
```

The steel-gray token `#333e48` belongs to the gray group. The near-black
token `#1c1c1c` belongs to the black group. Exclude only the exact actual
canvas token from categorical solids. An explicit existing semantic role
can reserve a slot, such as the primary red hub in the Three.js orbit.
Interior labels must select exact black or white by maximum contrast against
the actual solid body. Distinct first-cycle fills remain opaque and have no
decorative outlines. A remaining red variant or pink must not be allocated
before a usable gray, black, or white slot.

## Scope and Consumer Inventory

Runtime allocation consumers are D3 (`categoryStyle`, palette adapters and
builders), Mermaid (`solid_style` and native indexed presentation), PlantUML
(family defaults and role-specific native finishing), ECharts and Slidev
ECharts (prepared-option category assignment), Three.js (solid material
allocation), procedural SVG (`category_style`), vectorization (solid palette
allocation), and synchronized SVG composition (theme and category marks).

The sequence-only copies in diagram composition, UsefulCharts, video, and
Manim SVG video are passive for this correction: their production callers
use paint qualification or text contrast, without allocating categorical
fills from `solidSequence`. Their whole runtime payloads still receive
static identity and palette-copy checks. The Harbor report consolidator's
sequence consumer explicitly selects Colorset 2 and is unchanged by this
Colorset 1 correction. Other palette copies that expose only allowed paints,
roles, or source-artwork mappings receive the same static coverage.

## Frozen Forward Tests

Do not dispatch a forward run until the coordinator confirms the complete
source candidate is frozen. Use the runtime payload, strict JSON mode,
exact output paths, no ambient discovery, and unchanged copied resources.
Save every attempt and infrastructure failure. Use the mandated Spark model
unless the owning backlog row records an applicable deliberate exception.
D3, Mermaid, PlantUML, and Three.js have recorded `openai-codex/gpt-5.6-luna`
exceptions after Spark rejection. The default for ECharts and Slidev ECharts
remains Spark unless the coordinator records an own-skill exception.

Run nine deterministic command contracts for the real allocation consumers,
including actual native SVG, D3 HTML, or WebGL output where supported. Add
three independent naturalistic repetitions for D3, Mermaid, and PlantUML,
the directly observed diagram routes. This yields eighteen planned runs.
Require at least two joint passes out of three for each naturalistic case.
Use the contract alone for the additional narrow allocation consumers.
No failed sampled
attempt is silently replaced in the numerator or denominator.

The allocator contract layer verifies both white and dark canvas sequences, the
first overflow index, all first-cycle opacity/border/text styles, and the
owning renderer's normal output route. ECharts contracts render both actual
canvases through native SVG SSR. Three.js observes native hub and token
materials through its WebGL inspection API. Procedural and synchronized
SVG contracts also generate their normal bundled pattern or composition.
Vectorization preserves its perceptual source mapping, rights, and contours;
an order-only change must not force index-based brand allocation over source
artwork. Naturalistic cases use new category
data and do not reveal the suspected bug or the internal implementation.

## Independent Gates

1. Run the repository helper with `--mode json --strict` and an exact
   `--expect-output` flag for every artifact.
2. Recompute all returned fills against the independent literal order above;
   do not accept an agent-written `passed` field as the oracle.
3. Inspect actual SVG bodies or Three.js material objects in the browser,
   including body paint, opacity, outline width, complete inside labels,
   preserved source labels/relationships, and actual arrow heads and shafts.
4. Capture desktop/mobile resting-state views and inspect them directly.
5. Summarize events with the requested model assertion, valid JSON,
   zero tool errors, required prompt-first read, and no example/sibling reads.
6. Require identical pre/post copied-payload digests. Retain exact commands,
   prompt and output identities, concise findings, and all failures.

Keep raw runs, browser media and generated outputs under ignored
`evaluations/runs/`. Keep only compact controls and results here. Repository
validation and public Pages verification are coordinated separately.
