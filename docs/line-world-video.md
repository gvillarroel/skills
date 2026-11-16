# Line World Video plugin

Release **0.23.0**, November 16, 2026. Create explanatory videos with a guiding
dot, a larger continuous world, full-frame sections, sourced photographs,
D3/Mermaid diagrams and measured narration. The plugin contains six standalone
skills: the main orchestrator, dedicated D3, Mermaid, icon and HyperFrames
producers, and the Google Vids adapter.

## Build and install

Run from the repository root with uv, Node, a supported browser, FFmpeg,
FFprobe and the Codex CLI available:

```text
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

The builder reads the version from `projects/line-world-video/package-spec.json`
and writes immutable portable and marketplace ZIPs below that project's ignored
`artifacts/packages/` folder. Select a new release version before rebuilding an
existing package. The verifiers extract actual bytes, validate the manifests,
install into a task-local Codex home, discover all six native skills and execute
the installed runtime tests. They do not change a global host configuration.

The `Build Line World plugin` GitHub Actions workflow also builds the installable
ZIPs on relevant main-branch changes. Download its versioned artifact to obtain
both packages and a digest receipt without rebuilding locally. The CI artifact
is retained for 30 days; source and local build commands remain permanent.

To install the extracted marketplace in your own Codex configuration:

```text
codex plugin marketplace add <extracted-marketplace-root>
codex plugin add line-world-video@line-world-local
```

Use `$line-world-video` for a new film. Discover the installed skill paths and
run their bundled utilities through uv. A source checkout is also usable by
loading `skills/line-world-video/SKILL.md`. Required runtime resources live
inside each skill; optional companions exchange project-owned assets.

## Defaults learned from the films

Keep the complete composition predominantly white, with grays for structure
and primary red `#9e1b32` for attention. Use dark gray `#696969` for secondary
comparison emphasis. Additional colors come from colorset2 when distinct
entities or independent series require them. No pixel-percentage quotas or pink
object fills apply. Small solid objects are borderless; groups retain white
interiors and discreet outlines. Red faces use white text and monochrome icons,
centered horizontally and vertically by measured bounds.

Visible titles are opt-in. Keep essential names, values, units, axes and legends.
Divide the entire frame into related sections. Move the guide beside the thing
being explained, with separate destinations for repeated values. Preserve
reading holds, unclipped text and continuity across scene joins.

When a chart or diagram holds focus for more than two seconds, keep meaningful
motion in that figure: a trace on its actual curve, flow on an actual connection
or restrained emphasis on the active mark. Keep fixed data, labels and camera
stable. The parent-clock runtime handles calm trace/pulse overlays, and the
target-pixel audit rejects an otherwise static graphic even when its guide
moves. See [long-focus motion](../skills/line-world-video/references/focus-motion.md).

Use researched photographs for documented physical objects and diagrams for
mechanisms, relations and quantities. Retain originals, identity/variant
checks, credits and transformation lineage. Compare original, grayscale, edge,
pixel and one-bit options at actual delivery size. Introduce people by spoken
name and contribution plus a short visible role caption.

Explain the subject, evidence and consequences in narration. Keep substantive
scientific limits; avoid spending the script describing the animation or its
visual simplifications. For paper tours, use pinned original pages, one gradual
camera entry and fixed-scale pans. Keep emphasis clear of actual words,
figures and table values.

## Choose a repeated-work utility

| Task | Bundled primary utility |
| --- | --- |
| Scaffold a linked story or full-frame atlas | `line_world.py init`, `build`, `update` |
| Inspect or change a few fields and select rerenders | `video_edit.py inspect`, `plan`, `apply`, `status` |
| Cache real-object images and compare treatments | `documentary_assets.py fetch`, `prepare`, `audit --screenshot` |
| Prepare portraits, circular logos and credits | `media_assets.py` and `people_context.py` |
| Review subject-focused narration | `narration_review.py` |
| Inspect icon/text contrast, alignment or guide clearance | `inspect_items.py`, `inspect_focus.py` |
| Animate and verify long chart/diagram focus holds | `assets/runtime/focus-motion.js`, `inspect_focus_motion.py` |
| Capture and navigate an original paper | `paper_video.py` |
| Assemble rendered clips with measured audio and package inputs | `project_delivery.py prepare`, `assemble`, `bundle` |
| Check the actual complete film and record visual decisions | `review_video.py` |

The [incremental workflow](../skills/line-world-video/references/incremental-editing.md)
uses stable IDs, guarded patches, shared themes and dependency fingerprints.
The [project-delivery contract](../skills/line-world-video/references/project-delivery.md)
turns ordered voice observations and clips into a reusable JSON request. It
preserves speech, holds a nonzero short audio tail, validates actual media and
reuses matching outputs. Its portable archive includes the real inputs,
self-contained helper, rebuild entry point and digest manifest. Reassembly is
separate from generating new visuals; include their renderer and dependencies
when further authoring is required.

Read only the selected reference and compact result. Avoid reading large vendor
files, repeating unchanged voice generation or rebuilding all scenes for a
small edit. Final visual inspection and actual audio measurements remain
necessary evidence.

## Google Vids and delivery status

Use the [native adapter](../skills/line-world-google-vids/SKILL.md) when Google
Vids is requested. Its helpers prepare exact scripts, measured timing, semantic
cues, current scene inventory and resumable upload/export queues. Operate the
supported interface, verify current script focus, retain approved voices during
visual-only changes and recheck actual scene lengths after clip insertion.

A local assembly is labelled local. Native completion requires actual visual
replacement, full export, observed playback/download and a verified cloud movie
link. A blocked upload, voice-only document or machine-local file is not a
complete native/cloud delivery. Preserve completed work and the exact queue
when a permission or account barrier occurs; resume after the real blocker is
resolved. No native action or account permission is inferred by local tools.

## Validation and source boundaries

The [0.23.0 motion evidence](../evaluations/line-world-video/focus-motion-20261116.md)
records the long-hold runtime, target-pixel checks and browser tests.
The earlier [0.22.1 release evidence](../evaluations/line-world-video/reusable-delivery-20261116.md)
records installed tests, isolated forwards, real CUDA/AlexNet assembly, clean
bundle rebuilding and publication checks. Historical evidence remains under
`evaluations/line-world-video/` and `evaluations/line-world-google-vids/`.
The main skill retains its recorded broader generation limitations in
[SKILLS.md](../SKILLS.md); a passing utility check is not a universal visual
quality claim.

Generated videos, downloaded original media, private editor state, large
screenshots and native receipts remain in ignored project artifacts. This
repository publishes reusable skill/plugin sources, tests and summarized
evidence. Build packages locally; do not treat historical local artifact paths
as public downloads.
