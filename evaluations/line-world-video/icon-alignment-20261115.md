# Background-aware icons and centered content, release 0.18.0

Date: November 15, 2026 (local production date). Owners: line-world-video and
its dedicated line-world-icons producer. Primary status remains `validating`.

## Change and reusable behavior

The previous contrast helper handled text but left hard-coded icon strokes gray
on red faces. Some glyphs used nominal coordinates instead of their actual
visible bounds. The runtime now applies an alpha-preserving foreground filter
to explicitly marked monochrome inline groups, symbol uses and external SVG
images. White foreground is mandatory on the primary-red face. Inactive light
gray faces recover dark ink; secondary dark gray uses white. Real brand/photo
assets remain outside this monochrome contract.

The theme centers the complete loaded icon/label block in both axes, including
nonuniformly transformed parents. Simple items adopt direct internal content;
explicit `data-lw-content`/`data-lw-for` wrappers support deliberate layouts.
Quantitative coordinates, external labels, column alignment and complete group
layouts retain their own geometry. The audit rejects unverified/incorrect icon
ink, displacement over two CSS pixels and content overflow. Focus audits include
these findings. `inspect_items.py` reviews all authored cue/reading poses in one
local browser run without changing or repairing the source.

The primary instructions, compact `icons-and-alignment.md`, shared producer
contract and dedicated icon producer now carry the rules. General D3, Mermaid
and Iconify source skills are unchanged. Each plugin producer receives identical
theme/focus runtime bytes. No Pages source or catalog changed.

## Deterministic and native package validation

Commands, from the repository root:

```text
uv run --script skills/line-world-video/scripts/test_item_contrast.py
uv run --script skills/line-world-video/scripts/test_theme.py
uv run --script skills/line-world-video/scripts/test_focus.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

All 12 new icon/alignment tests, 12 existing theme tests and 11 focus tests pass.
New tests inspect actual screenshot pixels, transformed centering, combined
content, focus reversal, symbol/external SVGs, flat minus strokes, negative
contrast/centering tampering, quantitative exceptions and untinted brands.
The first pixel test caught a real cropped `<use>` filter; switching non-flat
glyphs to object-bounding-box filter regions fixed it before release.

The actual archives contain 310 declared files. Extraction, schema validation,
task-local native Codex install, six-skill app-server discovery and 175 installed
utility tests across 15 suites pass. This does not claim a global installation
or account publication. Evidence:
`projects/line-world-video/artifacts/host-checks/openai-0.18.0/verification.json`.
Canonical/local sync validates 126 primary files and 22 adapter files.

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| line-world-video-0.18.0.zip | 1,869,952 | fd2a435b3af4afaf88fb21a87f5e96cb503b119d8f18e53221dcdc201f560560 |
| line-world-video-0.18.0-marketplace.zip | 1,875,320 | 39b4cb08e2f0983f592038e1e2859c58baba7adc82fec355b983b74a4766dcec |

## Isolated forward evidence and limits

Use the recorded model exception `openai-codex/gpt-6.1-sol`, medium, because the
account previously rejected Spark. Strict mode retained exact output paths,
observed-model verification, valid JSON, no tool errors, restricted read surface
and unchanged runtime-only payload requirements.

The command contract passes in
`evaluations/runs/20261115-line-world-icons-center-contract-sol/`, using
`evaluations/pi-prompts/line-world-icons-center-contract.md`. It executes all
three exact test commands and writes `review/contract.json`.

Three naturalistic trials use
`evaluations/pi-prompts/line-world-icons-center-natural.md` and run IDs
`20261115-line-world-icons-center-natural-sol-1`, `-2`, `-3`. Every run creates
all five exact artifacts and correct final figures. Trial 1 passes strict mode.
Trials 2 and 3 fail strict mode because bare-Python dependency probes raise tool
errors; their later corrected verification does not erase those failures.

The dedicated icon-profile forward uses
`evaluations/pi-prompts/line-world-profile-icon-center.md` and
`projects/line-world-video/scripts/run_profile_eval.py`, cohort
`line-world-icons-center-0180`, case `attention`. It creates all four exact
artifacts and the final figure passes, but strict execution fails on its initial
browser-path assumption and an intermediate custom-verifier assertion. Preserve
the complete trace under that cohort; do not report a strict profile pass.

An evaluator-owned browser/pixel check independently passes all four final
figures. It measures actual content/face bounds, checks white and dark glyph
pixels, text foreground, containment and byte-identical return-seek screenshots:

```text
uv run --script evaluations/contracts/verify-line-world-icons-center.py --workspace evaluations/runs/20261115-line-world-icons-center-natural-sol-1/workspace --workspace evaluations/runs/20261115-line-world-icons-center-natural-sol-2/workspace --workspace evaluations/runs/20261115-line-world-icons-center-natural-sol-3/workspace --workspace evaluations/runs/line-world-icons-center-0180/evaluations/runs/20261114-line-world-icons-attention-sol-1/workspace --output projects/line-world-video/artifacts/reviews/independent-icon-center.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261115-line-world-icons-center-contract-sol/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

The instruction/runtime scope has usable passing evidence; the broader primary
and strict profile reliability questions remain open. Geometric centering and
marked icon paint checks do not establish universal optical balance or certify
unmarked imported assets.

## Regenerated examples and actual movies

The one-call item inspector passes 28 linked, 68 atlas, 83 CUDA/AlexNet and 116
ML poses: 295 total. It samples scene cues or four reading poses per beat, not
every encoded frame. Browser errors and item findings are zero. The atlas also
waits for fonts before its final alignment pass. The bubble chart uses separate
node wrappers and external names for undersized bubbles; the original Release/6
overlap and subsequent width-overflow diagnostic are retained as development
findings. Complete render/focus audits pass.

Both direct-browser demonstration movies were regenerated at 1920x1080/30 fps:
`line-world-aligned-linked.mp4` (56 seconds/1,680 frames) and
`line-world-aligned-atlas.mp4` (185 seconds/5,550 frames). The encoded content
scanner checks every frame and reports zero insufficient-content intervals.
Both versioned editable source archives extract and rebuild successfully.

Seven CUDA/AlexNet scenes and four ML scenes, including their changed continuity
dependencies, were replaced through the actual Vids Replace video > Upload flow.
Fresh changed-scene announcements verify one visual object and retained native
audio at the original scene extents. The top-five table uses separate column
alignment cells: centering the success glyph must not shift rank/class columns.
It was visually corrected, rerendered and replaced again before the final export.

Both native projects were exported through File > Export to Drive. Their
completed Open now links identify the actual new MP4s. Playback progress and
duration were observed; both files were downloaded through Drive and match the
connector metadata byte sizes. CUDA initially showed Drive's processing notice;
later refresh and native playback confirmed progress at 37.169 seconds, duration
3:23 and the revised result table. ML playback was checked at 1:16, duration
4:26. Evidence and screenshots live under project artifacts, including
`icon-cloud-playback.json` and `google-vids-icon-centering.jpg`.

| Movie | Duration | Frames | Bytes | Actual Drive MP4 |
| --- | ---: | ---: | ---: | --- |
| CUDA/AlexNet | 203.313923 s | 6,099 | 7,015,218 | [MP4](https://drive.google.com/file/d/1_7xLvXBHblB45GmJTUJVBlEjbCHvQYlS/view) |
| ML training | 265.914921 s | 7,977 | 9,417,427 | [MP4](https://drive.google.com/file/d/1DJ1LxRu8YPwYTHiW5PFLYnt4mWODnSzq/view) |

Native SHA-256 values:

- CUDA: `ed0f6927e4803b43af8b0fc7e9c48b5f95d0de372606a92f74a3077671824021`.
- ML: `3e1a84c15f040f0ce803b221549beae74883f78cbc5a977216058762d21ff5df`.

Full decode/blank-frame checks pass on all 14,076 native frames. CUDA verifies
53/53 encoded guide arrivals; ML retains 80 source cue arrivals and the existing
percentage/important-mark checks. Decoded 16-bit voice PCM is byte-identical to
each immediately preceding native movie; see `icon-native-audio.json`. Existing
scene timing and local render joins pass. The actual paper/SEAL film contains
original source colors and does not need icon recoloring for this revision.

Project scripts `verify_export.py`, `verify_revision.py`, `finish_solid.py`,
`package_project.py`, `check_source_bundle.py` and `package_revision.py` were
executed against the current artifacts. Both current source archives rebuild
and audit from clean extraction. Earlier version archives and native movies are
retained. A long optional 22-scene UI inventory collection timed out before its
journal was saved; only the separately observed changed-scene announcements and
actual export/download/playback are claimed. The timeout required native-window
verification after the browser debugger became unattached.

## Repository gates

Pattern IDs, skill-independence tests, payload check and bounded source/local
sync pass. Global `validate-skills.py` and global sync retain exactly the four
pre-existing unrelated reference-route findings in curate-semantic-model,
extract-ontologies and extract-with-ontology. No unrelated source was changed to
make those gates pass. Review the scoped diff before any future authorized push.
