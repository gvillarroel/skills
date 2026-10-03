---
name: hyperframes-explainer
description: "Creates minimal, synchronized explanatory videos with HyperFrames, selecting specialist skills and editable assets for each explanatory moment. Use for educational animations and interactive previews where one event changes a recognizable mechanism and related measurements together, with sparse labels, colorset1 by default and justified colorset2. Use when linked visual motion should explain the subject."
---

# HyperFrames Explainer

Explain by showing what changes, why it changes, and what remains consistent.
Build one canonical state and one seekable clock for the whole composition.

## Shape the explanation

1. Preserve the requested subject, dimensions, duration, units, language and exact
   output paths. Treat illustrative assumptions as assumptions in the project
   manifest. Do not invent product claims or present a model as measured evidence.
2. Name the initiating event and its causal chain. Choose two or more related
   representations when the topic calls for them: mechanism, trajectory, amount,
   force, comparison, queue, conservation or signal. Give each a distinct viewer
   question. Repeating a number in several boxes is not a multi-view explanation.
3. Keep the mechanism dominant and the representations close to the objects they
   explain. Prefer one continuous scene; keep anchors and entity identities stable.
   Read [explanation-design.md](references/explanation-design.md) before laying out
   a scene, especially for multiple simultaneous effects.
4. Start with **colorset1**. Read [palette-policy.md](references/palette-policy.md).
Read [solid-surfaces.md](references/solid-surfaces.md) for solid-first category fills, black/white text on the actual fill, and palette exhaustion before border variants.
   Try direct labels, grouping, position and semantic shape before additional hue. Filled category surfaces start without decorative strokes; meaningful mechanism paths remain visible.
   Use colorset2 for an explicit request or a documented semantic-separation need;
   never for decoration or simply because more objects exist.
5. Default to no headline, chapter banner, brand lockup, frame metadata or closing
   slogan inside the film. Use short direct labels, exact values and units. Add one
   brief context label or event annotation only when it removes a real ambiguity.
   Preserve necessary facts instead of satisfying a word quota by omitting meaning.

## Choose assets for each moment

Before authoring scene geometry, read [asset-direction.md](references/asset-direction.md).
Inspect the available installed skill descriptions, select by the relationship
being explained, and read the selected skill's actual `SKILL.md`. Follow its
generation and validation workflow. Do not assume a skill is installed or invoke
every possible specialist. Record each asset's purpose, producer, event IDs,
state hooks, ports, bounds and provenance in a project-owned asset plan.

Use original SVG illustration for recognizable objects, procedural systems for
transport or fields, D3/ECharts for quantitative geometry, notation renderers for
typed relationships, and 3D when depth or camera perspective carries meaning.
The routing table explains the tradeoffs and a standalone fallback for each.
These companion skills are optional; never require sibling paths or their
fixtures. In an isolated skill workspace, author subject-specific vector assets
using the construction recipe in that reference.
For a matching controlled inlet or moving vehicle, read
[calibrated-mechanisms.md](references/calibrated-mechanisms.md) and use its bundled
composer. It creates recognizable editable SVG, calibrated rulers, transport or
rolling hooks, two fixed-domain histories and the asset plan from the actual
numerical model. Preserve requested facts and exact paths; use custom assets for
other mechanisms. This route replaces the blank scaffold and never invents a
companion-skill invocation.
For a nonnegative rate and its accumulated quantity, **initialize the model first**
with the `init` command in [scene-contract.md](references/scene-contract.md#initialize-a-rateaccumulation-scene).
It writes valid project-owned JSON, numerical bindings and an adaptive layout;
then compose a supported mechanism or scaffold custom assets. Do not scaffold
against a brief that has not been created. The initializer supplies no
mechanism illustration; choose the actual subject deliberately.
For hand-authored SVGs, first create the view-sized blank scaffold described in
[asset-contract.md](references/asset-contract.md); then draw and bind the actual
subject. This prevents canvas/view coordinate confusion and wrong source paths.
The scaffold can preserve a matching existing plan. Inspect its report before
reading a newly requested file; do not probe paths whose creation was refused.
Use structured JSON serialization for nested expressions and parsed edits.
For travelling objects, bind a named group's relative `offset` to preserve its
authored pose and keep every part together. Budget the full silhouette at control
extremes. Use explicit UTF-8 writes and repair any text-encoding findings.

Minimalism removes redundant words and decoration, not the features that make a
mechanism understandable. Reject an asset if its silhouette, moving part, contact
point or visual encoding cannot communicate its assigned question at playback
size. Build and inspect a composed still before animating it. Correct the asset,
scale or composition when that still resembles generic boxes or a dashboard.

## Build a linked scene

Read [scene-contract.md](references/scene-contract.md). Write a project-owned JSON
brief using [brief.json](assets/templates/brief.json) as a small starting shape.
Use the initializer for a rate/integral instead of hand-balancing nested JSON.
For other models, replace the template's illustrative mechanism with the actual subject. The source variables,
derived expressions, timed input events and visual bindings define the explanation.
For iterative edits, use the bundled `patch` command described in the scene
contract. It selects marks by ID and validates the candidate before replacing the
brief. Do not substring-replace repeated geometry keys or normalized JSON.

Treat the bundled primitive builder as an assembly and synchronization layer,
not the default art direction. Import flattened editable specialist SVGs with
`import_assets.py`; see [asset-contract.md](references/asset-contract.md) for the
supported subset, placement, ID bindings and the exact command. It expands assets
into audited marks, preserving numeric state bindings and producer/file hashes.
Keep the copied skill read-only and all outputs outside it. Substitute the actual
bundle path for `<skill-root>`:

```text
uv run --script <skill-root>/scripts/explainer.py preflight --brief brief.json --report preflight.json
uv run --script <skill-root>/scripts/explainer.py build --brief brief.json --project project --report build.json
```

Expected authoring findings exit zero; inspect `ok`. Repair the brief before build.
Run one gate per tool call and inspect its report before the next gate. Do not
chain import and build: a refused import intentionally exits zero without an
assembled output. After changing an SVG, reimport from the original brief. After
changing an owned generated project, rebuild with `--refresh`; do not reuse a
stale assembled brief or omit that flag on a second build.
The builder never installs packages or reads sibling skills. To repair a generated
scene, edit the project-owned brief and rebuild with `--refresh`; this intentionally
regenerates the HTML and kernel. Preserve custom project edits before refreshing,
or update those custom bindings directly and validate them again. The index embeds
the brief, so editing JSON alone does not update the filmed stage.
For a mechanism beyond
the primitive vocabulary, adapt the generated project while retaining its pure
state function, public seek/input API, exact palette, event identities and tests.
Read [hyperframes-runtime.md](references/hyperframes-runtime.md) for that extension
and the pinned, verified rendering contract. Keep selected specialist assets local;
the bundled path remains usable without them.

## Verify and render

Read [validation.md](references/validation.md). Setup requires Node.js 24+, Chrome
or Chromium and FFmpeg. Run the following from the workspace root using the actual
project and artifact paths. The scripts locate their project from their own file:

```text
npm install --prefix <project> --cache <project>/.cache/npm --no-audit --no-fund
node <project>/scripts/audit.ts --report <audit.json> --screenshot <preview.png>
node <project>/scripts/hf.ts check
node <project>/scripts/hf.ts render --output <exact-video.mp4> --fps <requested-fps> --quality delivery --workers 2 --no-best-effort
uv run --script <skill-root>/scripts/explainer.py verify-media --video <exact-video.mp4> --brief <project>/brief.json --report <media.json> --contact-sheet <contact-sheet.jpg>
```

Inspect the browser audit's `ok` and repair findings before running the native
check. Relative artifact paths resolve against the command's working directory.
Use the supplied audit instead of adding ad hoc servers or probing uninstalled
browser packages. Read its small JSON report once; parse fields rather than guessing
pagination offsets. The builder normalizes JSON whitespace;
compare parsed quantities/units, never raw brief bytes.

Do the rendered-video work when the user requested a video; a request to create it
already authorizes local rendering. Do not introduce another approval pause.
For preview-only work, deliver the requested preview and omit encoding.

Verify actual input changes and backward/forward seeks. A source event must update
its derived values and every dependent mark at the same sampled time; independent
quantities must stay unchanged. Inspect stable states, event midpoints, causally
important arrivals and full-resolution frames. Repair detached labels, incorrect
directions, hidden marks, clipping, excessive prose and unreadable supporting views.
Keep controls and verification reports outside the filmed stage.

Deliver the requested artifact plus its editable brief/project and concise evidence.
Report actual limits: a passing structural audit cannot prove that the mechanism is
scientifically correct or that the viewer understood it. Keep source-backed claims
and illustrative models distinct.
