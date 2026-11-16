# Real portraits and circular logos

## Contents

- [Research and select](#research-and-select)
- [Build once, reuse locally](#build-once-reuse-locally)
- [Place and synchronize](#place-and-synchronize)

Use this workflow when an explanation benefits from showing who contributed,
or when a company mark must be usable in a video and in a graph. It does not
replace ordinary icons or require portraits in unrelated videos.

## Research and select

1. Identify contributors by stage from original papers, institutional biographies
   or the person's own page. Distinguish inventor, coauthor, project leader and
   organization. Show a useful selection; do not imply sole authorship or an
   exhaustive historical ranking. Keep affiliations accurate to the story's date.
2. Search public image sources. Prefer a verified institutional portrait or an
   appropriately licensed Commons image. The bounded helper can search Commons:

   `uv run --script <skill-root>/scripts/media_assets.py search --query '"person name"' --output candidates.json`

   Candidates are unreviewed. Inspect the source page and actual photograph;
   confirm the named subject and contribution separately. A search thumbnail,
   filename or automated face match is insufficient. If Commons lacks a useful
   result, use web/image search and record the selected official source URL.
   Never generate a substitute face and present it as documentary photography.
   Check namesakes against profession, institution and the historical paper;
   public profile aggregators can merge different people with the same name.
3. Prefer exact vector brand artwork from an available `technical-logo-assets`
   companion or the brand's official media kit. Export only selected files and
   provenance into the project. Keep a local SVG/PNG fallback usable without
   that companion; do not import its catalog or depend on its installation path.

## Build once, reuse locally

Create a project-owned JSON request with an `assets` array. Every entry needs
`id`, `kind` (`portrait` or `logo`), `label`, `sourcePage`, `identityEvidence`,
`contributionEvidence`, `reviewed: true`, and `rights` with `creator`, `license`
and `credit`. Set `licenseUrl` when available. State unknown reuse terms plainly;
do not label an institutional photograph as Creative Commons without evidence.
Add either `downloadUrl` or `sourceFile` relative to the request. Optional fields
are `role`, `stage`, `focus: [0.5, 0.3]`, `zoom: 1.5` (1–4), and `sourceSha256`
for a pinned source. Use zoom for a full-body photograph; inspect the resulting
headroom and chin rather than relying on the default center.
For a logo, contribution evidence can explain the organization/stage association.

```json
{"assets":[{"id":"example-company","kind":"logo","label":"Example company",
"sourceFile":"original.svg","sourcePage":"https://example.com/brand",
"identityEvidence":"Official brand kit","contributionEvidence":"Company behind the narrated product",
"reviewed":true,"rights":{"creator":"Example company","license":"Brand-kit terms",
"credit":"Example company; official brand artwork"}}]}
```

Run `uv run --script <skill-root>/scripts/media_assets.py build --request media.json --output media --png`.
Omit `--png` when only SVGs are needed. No network is needed for local files.
Identical downloaded bytes and requests reuse cached outputs. `--refresh` checks
the remote source again; it does not silently change a pinned digest. Inspect
the compact report, `manifest.json`, `credits.md` and `graph-nodes.json`.
Rasterization needs local Playwright Chromium; acquisition and SVG output do not.
Run the helper through `uv run --script`: its Pillow and Playwright dependencies
are declared there, so a separate import probe in system Python is unnecessary.
For adjacent Python image work, use a uv environment with the needed packages
or the standard library rather than assuming those dependencies are global.

The output uses 256 by 256 viewports and transparent corners. Portraits use an
explicit circular viewport over the real photo; adjust `focus` after inspecting
the face at delivery resolution. This is a raster photograph inside an SVG,
not a vectorized face. Logos remain fully visible with `meet` scaling inside a
white circular support. Never circle-crop a wordmark, distort, trace, recolor or
remove the original mark's required clear space. Prefer vector SVG; identify a
PNG fallback as raster. The helper rejects active or externally dependent SVG.
Keep the complete original, source digest, attribution, license and changes.

## Place and synchronize

Plan each portrait as a sourced explanation. At the first meaningful appearance,
say the person's name and what they contributed to the process being explained.
Show the full name and one or two short contribution lines next to the face.
Measure caption size after the final fit; prefer at least 24 screen pixels in
1080p reading states. When increasing type, remeasure the line gap and nearby
divider clearance. Two individually readable lines can still overlap each other.
An affiliation or present-day executive title alone does not explain a historical
contribution. Use the role at the story's date. Preserve team/coauthor credit;
do not invent individual responsibilities that the evidence does not establish.
For example, a CUDA software leader belongs beside CUDA because of that work,
not merely because the person currently works for the hardware company.

Keep these bindings in `story.json` under each scene's `people` array:

```json
{"id":"contributor-id","name":"Person Name","caption":["Relevant contribution"],"narrationRole":"the exact contribution phrase spoken nearby","target":"person-contributor-id","sources":["https://example.org/original-paper"]}
```

Use `spokenName` only for an intentional different spoken form; otherwise the
name is the spoken form. Include a scene cue whose phrase is that name. Keep
the contribution near it in the narration. The source fields are evidence links,
not automated factual verification; read the actual primary sources first.

Run the compact preflight before paying for narration or rendering:

```text
uv run --script <skill-root>/scripts/people_context.py --story story.json --media media/manifest.json --output review/people-plan.json
```

It rejects unintroduced portrait assets, missing spoken names/contributions,
missing captions/sources and missing semantic person cues. Pending observations
remain explicit. Update the script when a new portrait lacks context; preserve
an existing recording only when it already names and explains every shown person.
Re-measure changed audio and realign downstream scene starts and cue times.

For an SVG source, mark its actual portrait group `data-person-id`, optionally
`data-person-scene`, its full name `data-person-name`, and each role line
`data-person-caption`. Retain the ordinary `data-media-id` and focus target.
The actual source must expose `#stage` and `renderClip(index,localSeconds)`.
The browser inspector checks loaded names/captions against the plan, delivery
legibility and clearance from the photo. Complete the gate using the measured
`aligned-to-audio` cue output from actual narration word timestamps:

```text
uv run --script <skill-root>/scripts/people_context.py --story story.json --media media/manifest.json --html composition/index.html --cues cues.json --require-observed --output review/people-final.json
```

For a renderer outside this SVG contract, supply `--visible observations.json`
instead of `--html`. Record `observed: true`, concrete `evidence`, and
`scenes: [{id,people:[{id,name,caption:[...],legible:true}]}]` only after viewing
the actual result. This is an observation receipt, not an expected-data manifest.
Add `--screenshot review/people.png` to save the last inspected reading pose
without another browser script. ASR timing is approximate; inspect the encoded guide beside the correct person
and listen to their name/contribution. Captions are essential figure labels,
not permission to add unrequested chapter titles or biography panels.

Use each graph node's `image` as a local SVG/PNG asset; it is already circular.
Preserve stable node IDs and relative file paths. SVG `<image>` supports these
assets in D3; Mermaid node-image support is renderer-dependent, so use an adjacent
D3 portrait/brand layer when it cannot preserve the asset. Do not fake support.
For a standalone SVG, embed the local bytes as a data URL rather than a remote URL.

Allocate room before rendering: a 180–240 px portrait is a useful starting point
at 1080p. Keep the name and short factual role outside the circular image. Reserve
the entire circle, label and nearby connector envelope as obstacles. Move the red
guide beside the person when named, never over the eyes, logo or text. Bind each
speaker reference to its own semantic target and measured voice time. Retain
unchanged narration when it already provides the portrait's context. Full-frame dividers
and adequate reading space still apply. Inspect the actual encoded result and
keep attribution accessible with the delivered film and editable sources.
