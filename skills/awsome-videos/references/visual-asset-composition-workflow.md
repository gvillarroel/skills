# Visual Asset and Composition Workflow

Use this for finished videos. Preserve one source-to-reviewed-MP4 artifact chain; specialists are collaborators, not runtime dependencies.

## Ownership and routing

Keep one owner per decision:

- `awsome-videos` owns promise, beats, voiceover, style, audio, and final acceptance.
- Prefer `source-to-video-director` to freeze source facts, storyboard, and shot contracts for source-backed or finished work.
- Prefer `scene-composition-director` for scene framing, focal hierarchy, safe areas, depth, asset roles, and motion phases. Prefer `scene-transition-director` for every multi-scene transition chain.
- Route each asset to one producer: `imagegen` for raster work; `mermaid` for conventional diagrams; `d3` for bespoke geometry/data motion; ECharts for charts; Three.js only when depth carries meaning.
- Select exactly one renderer owner. Prefer `html-d3-anime-video-workflow` for complex browser animation, Slidev plus its animation/chart skills for slide-first work, or `manim-svg-video` for an SVG mosaic or Manim-native sequence. Do not let two renderer skills encode competing finals.
- Run renderer checks, the applicable visual audit, and the final MP4/style/readiness/package gates.

Finished work requires source, composition, transition, and renderer owners; route asset specialists only when needed.

Record `skillRouting` with `stage`, `skill`, `reason`, `output`, `outputPaths`, `proof`, and `status`. Completed proofs bind every output SHA-256; the source route also freezes URL-backed facts and fact-to-shot mappings. Skips need `fallbackReason`. Keep one renderer route.

## Required artifact chain

Create and consume these files in this exact order:

1. `source/source-package.json` and `source/shot-contract.json`
2. `source/asset-manifest.json`
3. `source/composition-plan.json` and `source/transition-plan.json`
4. Rendered frames, capture evidence, and candidate MP4
5. `artifacts/reviews/visual-review.json`
6. `artifacts/reviews/asset-composition-validation.json`

Do not author the composition plan before asset paths and provenance are known. Do not finalize the review from source code or a scaffold preview; inspect rendered pixels. Generate the validation report last and regenerate it after every corrected render.

### Asset manifest

Give every asset a stable lowercase `id` and include the exact contract fields:

- `kind`, concrete `claim`, project-relative `output`, and file `sha256`;
- `origin: { type, uri, rightsStatus, attribution }`, with a real URL for captured/external work;
- `producer: { skill, method, report }`; a ready asset's schema-v1 report must match its identity and SHA-256 and include at least three substantive passing checks with method and finding;
- `technical: { targetWidth, targetHeight, aspectRatio, maxUpscale, crop }`;
- one or more `uses: [{ sceneId, beatId, role, fit }]`;
- `status` (`planned`, `ready`, `verified`, or `approved`) and at least three concrete `qualityChecks`.

Every declared asset must exist, match its hash, and appear in a scene. Raster/SVG work must decode; video must pass ffprobe; GLTF/GLB must have valid 2.x scene/node/mesh structure. Reject placeholder media, broken paths, unverifiable provenance, generic stock, watermarks, private data, illegible screenshots, and rights violations.

Prefer source-bound UI, code, docs, diagrams, and captures. Generate imagery only for a claim or deliberate metaphor. Inspect the final crop; reject malformed objects, garbled text, noisy edges, inconsistent perspective, halos, or style drift. Supply enough resolution for the largest zoom; prefer vectors for diagrams and icons.

### Composition plan

Create exactly one entry per rendered `sceneId` in the `scenes` array. Bind each entry through `beatIds` and `assetIds`. Record:

- canvas/aspect ratio, title and caption safe areas, and any platform crop zones;
- composition armature, primary focal point, secondary support, reading path, visual balance, and intended eye landing point;
- at least two rejected alternatives, two concrete `armatureAnchors`, and a structured `validationContract` for alignment, safe zones, edge policy, box spacing, grayscale hierarchy, focal hierarchy, and expected proof artifacts;
- foreground, subject, support, and background layers with explicit asset roles;
- text region, maximum line measure, contrast treatment, and collision/clearance constraints;
- entrance, readable hold, emphasis, and exit phases; camera or object motion; and reduced-motion/static intent when relevant;
- normalized `objectBounds` including one `role: focal` object that occupies enough frame area;
- structured `validationChecks` with method, target, and pass criterion;
- outgoing `seamId`, persistent element, attention handoff, and expected before/after state.

Use one dominant reading task per moment. Keep proof primary and labels subordinate. Reserve clear margins, avoid tangencies/overlaps, and protect crop zones. Vary actual `objectBounds` geometry across scenes—not only armature names—with at least three material spatial layouts in a six-plus-scene sequence. Motion must reveal, compare, transform, or hand off attention.

Before renderer handoff, mute narration/captions and view each hold for three seconds. Name its familiar object, state-changing action, and result. Fail anonymous boxes/lines, motion that only relocates geometry, or a small semantic inset under an abstract dominant background. Enlarge/replace the asset, add functional local labels, and retest.

## Seam IDs and binding

Use the same stable IDs and timing across every contract and report. Visible media itself carries matching `data-asset-id`, `data-asset-src`, and `data-asset-sha256` and must load that exact file; inline SVG/canvas/3D needs an instrumented resource load. Composition objects carry `data-object-id`. Do not repair a seam by renaming one artifact.

For each adjacent pair, use a deterministic seam ID such as `scene-02__scene-03`, plus `fromSceneId`, `toSceneId`, cut time, transition type, persistent element, and before/after proof frame IDs. A sequence of `N` scenes must have `N-1` seams unless an intentional discontinuity is recorded. The persistent element named in the plan must be visible in both rendered seam states.

## Scaffold is a wireframe

A scaffold proves directories and timing hooks only. Its generic cards, gradients, labels, charts, and motion are wireframe material. Replace them with manifest-bound assets and scene-specific compositions; final validation detects both the explicit marker and markerless near-copies by starter signatures and template similarity.

## Pixel review and correction loop

Review first/hold/emphasis/final for every scene and before/midpoint/after for every seam. Timestamps must be ordered, lie inside their scene, and straddle the exact seam; paths and hashes must be globally unique. The validator uses ffmpeg to re-extract every frame from the candidate MP4 and enforces normalized mean pixel difference at most `0.04`. Record:

- `candidateVideo: { path, sha256 }` for the exact delivered MP4;
- one scene review per ID with `compositionId`, exact `assetIds`, evidence-frame timestamps/paths/SHA-256 values, eight passing checks, a concrete `silentTest` (`durationSeconds`, `object`, `action`, `result`), substantive finding/correction text, and `status: approved`;
- `N-1` transition reviews with from/to IDs, evidence-frame path/SHA-256, substantive finding, and passing status;
- checks for asset binding, focal hierarchy, legibility, safe areas, crop, contrast, silent comprehension, visual continuity, transition persistence, motion purpose, and source fidelity;
- `pass`, `warn`, or `fail`, with concrete observations, correction owner, and rerender requirement;
- caveats and the reviewer method (`automated`, `manual`, or both).

When a check fails, fix the lowest owning layer: asset producer for bad media, composition plan for hierarchy/layout, transition plan for continuity, or renderer for implementation/capture defects. Rerender the affected range, then the final encode when timing or shared state changed. Rebuild the contact sheet and capture evidence, repeat pixel review, and replace stale hashes. Never turn a failure into a pass by editing review prose without inspecting the corrected render.

Generate `artifacts/reviews/asset-composition-validation.json` only after the review passes. `check_visual_contract.py` binds SHA-256 values for the asset manifest, composition plan, visual review, and final MP4; reports asset/scene/seam coverage and file inspection; and fails stale hashes, unused assets, missing composition evidence, missing transition proof, or a reviewed MP4 that differs from delivery.

The renderer report also binds current `assetManifestSha256` and `compositionPlanSha256`. Final package validation reruns it in a browser, checks decoded resource loads and geometry, compares fresh browser frames to the candidate MP4, recomputes readiness, and rejects fabricated or stale reports.

## Isolated fallback

When a preferred skill or tool is unavailable, continue with a local equivalent inside the project; do not read sibling skill directories or assume their files exist. Use `producer.skill: "repo-native"` with a concrete `fallbackReason`. Use provided/captured media, self-authored SVG/HTML, or a static replacement whose limitations are explicit. Never omit the artifact chain, stable IDs, provenance, pixel review, correction loop, or hash bindings merely because a specialist is unavailable.
