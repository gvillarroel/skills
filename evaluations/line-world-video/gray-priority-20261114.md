# Red/gray-first Line World video release 0.5.1

Date: November 14, 2026 local. Raw runs also carry November 15 UTC timestamps.

## Result

Primary red `#9e1b32` leads; light and medium grays are secondary. Black and near-black move to the end of the category sequences. White surfaces and charcoal text/fine structural lines remain available. The default category map now uses red, gray, pale gray and gray instead of allocating black as the second region. Broad Sankey bands and stacked areas use lighter grays without changing values, widths, areas or timing.

The canonical `assets/palettes/colorsets.json` remains exact. The self-contained `assets/palettes/video-colors.json` supplies the video sequence and text choices with unchanged allowed tokens. All five packaged copies ship both files, record both hashes and route their copied runtime palette readers to the style file. General canonical producer skills are unchanged.

The guide stays primary red with its existing size choreography. Explicit colorset2 point identities remain stable where simultaneous categories need them. Visible titles remain opt-in; full-frame sections and editable timing remain.

## Verification

| Check | Result |
| --- | --- |
| Source contracts | 26 Python tests pass |
| Final isolated contract | 1/1 strict pass |
| Final naturalistic color/area case | 3/3 strict passes with six new records |
| Actual category geometry | Source values, ordered fills, complete area and proportional areas pass |
| Native Mermaid geometry | All 20 families match prior positions, paths, dimensions and labels |
| Shared style | Both palette files match in all five copies; real D3 and Mermaid palette-reader probes pass |
| Browser audit | gray-linked: 26 states, gray-atlas: 40 states; no findings |
| Native media | Both movies fully decode with exact dimensions, fps, duration and frame counts |
| Preview | 13 atlas controls/seek/mobile/context checks pass |
| Packaging | Five standalone bundles validate; both source ZIPs rebuild with identical timing |
| Codex | Five native catalog/install commands exit 0 in a project-owned disposable home |
| Local sync | 94 source files match |

The large-block audit measures actual visible filled geometry and broad strokes, reserving dark text, fine lines and tiny notation marks. The independent evaluator also checks actual category colors and quantitative areas in a fresh browser. The atlas retains one reviewed camera-motion heuristic warning for an imported XY label; the default story has no native layout warnings.

Model: `openai-codex/gpt-6.1-sol`, medium, under the already recorded Spark account-rejection exception. Final run IDs use `20261114-line-world-v051-priority-*`. Strict mode enforces observed model, exact outputs, clean event JSON, zero tool errors, unchanged payload and isolated reads. Read-surface summaries and independent checks are retained beside each run.

The earlier four-run functional candidate also passed, but the repository palette-copy validator rejected its direct modification of the base palette. Retain that diagnostic cohort and [initial compact results](gray-priority-initial-20261114.json). The released design separates the style file, restores the canonical base copy and passes four fresh strict runs. Both compiled story.js files remain byte-identical across that separation; the delivered movies therefore represent the final data, geometry, paint and clock.

This is a focused styling revision. The 0.5.0 broad producer and attention results remain [historical evidence](point-motion-20261114.md), including their failed attempts; they are not presented as a fresh full-suite rerun.

## Reproduction

```text
uv run --script skills/line-world-video/scripts/test_line_world.py
uv run --script projects/line-world-video/scripts/run_gray_evaluations.py --cohort v051-priority
uv run --script projects/line-world-video/scripts/verify_gray_release.py --cohort v051-priority
uv run --script projects/line-world-video/scripts/verify_atlas_preview.py --port 3280 --label gray-atlas
uv run --script projects/line-world-video/scripts/verify_delivery.py --video projects/line-world-video/artifacts/videos/line-world-red-gray-final.mp4 --story projects/line-world-video/artifacts/gray-linked/story.json --label gray-linked-decoded
uv run --script projects/line-world-video/scripts/verify_delivery.py --video projects/line-world-video/artifacts/videos/line-world-gray-atlas-final.mp4 --story projects/line-world-video/artifacts/gray-atlas/story.json --label gray-atlas-decoded
```

Use fresh immutable run IDs for another study. Native render commands and editing steps are included in each source project's EDITING.md. Required pattern, independence and payload gates pass. Scoped validation of all five bundles passes. Global structure validation and global sync retain the same four unrelated semantic reference-route findings; focused sync then confirms this skill. No Pages publication changed.

## Delivery hashes

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `line-world-red-gray-final.mp4` | 5220233 | `e36b070a96140b416b60b2dc3acfe5f7f142652f2f0354af0ff02fb7ab0f9e0e` |
| `line-world-gray-atlas-final.mp4` | 21357458 | `ad885548d0bc7dea4262c984dbf039c63bedc77bc6e060a196d08080512f3c44` |
| `line-world-video-0.5.1.zip` | 1650734 | `9ba18ff02a791bf3ec15434c8405e17846a93960213531915cb4e06a652b4d08` |
| `line-world-video-0.5.1-marketplace.zip` | 1655075 | `a1301119bec7ce8a3b75cb0749028450a5707dcff10f415d7b6244f087fbb28e` |
| `line-world-editable-project-0.5.1.zip` | 208421 | `3f9e6c4f150a81d9a0d9d74b125fd03d69f3c1d1b95a3cc34467b197b1d547a5` |
| `line-world-editable-project-0.5.1-atlas.zip` | 367568 | `1cb8a9360305f8560bb87a54c1d9806b32545648f2552f5edaaae75114ddfdff` |

See [compact final evaluation](gray-priority-20261114.json), [usage](../../docs/line-world-video.md) and the [reusable color-priority rule](../../skills/line-world-video/references/color-priority.md).
