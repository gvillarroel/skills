# Video Skill Consolidation Validation

Date: 2026-08-13

## Scope

Consolidated seven overlapping video skills into one canonical `video` skill. The resulting bundle owns source/storyboard contracts, exact output geometry, scene composition, master timing, cross-producer ports/events/states, transitions, browser/Slidev/Manim rendering backends, audio/video encoding, and final review. D3, ECharts, PlantUML, Mermaid, Three.js, image, animated-SVG/GIF, and Slidev specialists retain ownership of their internal artifacts.

## Deterministic validation

- `uv run --script skills/video/scripts/test_scene_contracts.py --json`: passed 11/11 checks. The fixture composes PlantUML SVG, Mermaid SVG, and two decoded GIFs; verifies four simultaneous elements, three interactions, two cross-producer interactions, SVG ID namespacing, master-clock GIF selection, Chromium renderer state, a real 960x540 H.264 MP4 at 12 fps for 7 seconds, and negative port/ratio/clock cases.
- `uv run --script skills/video/scripts/check_runtime_tools.py --require-render-tools --require-node --json`: passed for Python, uv, Node, ffmpeg, ffprobe, and all required bundle files.
- Skill Creator quick validation passed, and all 22 Python scripts parsed successfully.
- `uv run --script scripts/build-pages.py`: passed and rebuilt 412 Pages files.
- `uv run --script scripts/validate-pattern-ids.py`: passed 1,159 canonical IDs.
- `uv run --script scripts/validate-skills.py`, `uv run --script scripts/test-skill-independence.py`, and `uv run --script scripts/check-repo-payload.py`: passed.
- `uv run --script scripts/sync-local-skills.py --check`: passed after installing `video` and retiring the seven obsolete local skill copies.

## Isolated Spark forward test

Case: `evaluations/pi-prompts/video-mixed-scene-contract.md`

Model: `openai-codex/gpt-5.3-codex-spark`, high thinking, runtime profile, strict JSON mode.

The contract-smoke case requests exact 1080x1920, 9:16, 30 fps, 12-second composition output for PlantUML, Mermaid, and two GIF assets. It requires three semantic interactions, two cross-producer interactions, deterministic tracks, exact paths, and a passing bundled validation report.

| Run | Artifact/field gates | Event gate | Classification |
| --- | --- | --- | --- |
| `video-mixed-scene-contract-20260813-spark-1` | Passed | Failed because the harness did not recognize a `powershell` fence even though the exact command ran | Validator fixture |
| `video-mixed-scene-contract-20260813-spark-2` | Passed | Failed after a missing `README.md` read and a shell-wrapped exact command | Agent |
| `video-mixed-scene-contract-20260813-spark-3` | Passed | Failed after probing an absent output directory and one invalid partial read | Agent |
| `video-mixed-scene-contract-20260813-spark-4` | Passed | Passed with zero tool errors | Pass |

Final strict command:

```powershell
uv run --script scripts/run-pi-skill-eval.py video --prompt-file evaluations/pi-prompts/video-mixed-scene-contract.md --model openai-codex/gpt-5.3-codex-spark --thinking high --mode json --strict --run-id video-mixed-scene-contract-20260813-spark-4 --timeout-seconds 900 --expect-output deliverables/scene-contract.json --expect-output deliverables/scene-validation.json --require-exact-command-from-prompt --expect-output-json-field deliverables/scene-validation.json::ok=true --expect-output-json-field deliverables/scene-validation.json::summary.width=1080 --expect-output-json-field deliverables/scene-validation.json::summary.height=1920 --expect-output-json-field deliverables/scene-validation.json::summary.aspectRatio=9:16 --expect-output-json-field deliverables/scene-validation.json::summary.elementCount=4 --expect-output-json-field deliverables/scene-validation.json::summary.interactionCount=3 --expect-output-json-field deliverables/scene-validation.json::summary.crossProducerInteractionCount=2
```

The final run produced `scene-contract.json` SHA-256 `997d8fc2662ce8195f7900ffabd2be717c9f21d6934915d3da631ca0a64d862f` and `scene-validation.json` SHA-256 `2750b6bce004baed6d2a3a777fd985584c6d25e32ad3f30623a5f086c16382ea`. All seven asserted fields passed. An evaluator-side rerun of `validate_scene_contract.py` also passed with four elements, three interactions, and two cross-producer interactions.

The copied skill remained unchanged at SHA-256 `a46d9ba8b467477afeb8e35ad917742f197988cbe83c17a8914c3151be22bfd2`. The read-surface review passed with the prompt, `SKILL.md`, two focused references, the validator, and the generated report only; there were no sibling-skill or acceptance-fixture reads and no invalid events or tool errors. Durable trace summary: `evaluations/video-mixed-scene-contract-20260813-read-surface.json`.

## Post-project compositor hardening

The 2026-08-13 `projects/what-is-an-agent-regex-loop` render exposed two reusable integration defects: local HTML overlays loaded through `file://` had an opaque-origin boundary that blocked parent-to-iframe master-clock calls, and producer SVGs could retain an inline `max-width` that prevented them from filling assigned scene bounds. The compositor now embeds HTML through base-aware same-origin `srcdoc`, recognizes loaded `srcdoc` iframes during browser validation, and normalizes embedded SVG width, height, and maximum width without changing producer files. The mixed-media fixture gained a deterministic HTML overlay and now passes 13/13 checks with five simultaneous SVG, GIF, and HTML elements.

The same work replaced the nearly empty scene-contract template with a compact, validator-clean worked contract covering exact producer metadata, both port forms, decoded GIF playback, state and opacity tracks, events, and a visible cross-producer handoff. The interaction reference now lists exact supported `producerSkill` IDs. Local commands passed:

```powershell
uv run --script skills/video/scripts/validate_scene_contract.py skills/video/assets/templates/scene-contract.json --project-root skills/video --json
uv run --script skills/video/scripts/test_scene_contracts.py --json
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

The strict isolated contract-smoke regression retained every attempt:

| Run | Artifact/field gates | Event gate | Classification |
| --- | --- | --- | --- |
| `video-compositor-regression-20260813-spark-1` | Passed | One exploratory `rg` command failed | Agent |
| `video-compositor-regression-20260813-spark-2` | Passed | One incremental edit failed | Agent |
| `video-compositor-regression-20260813-spark-3` | Passed | Repeated schema repair exposed the incomplete template | Skill |
| `video-compositor-regression-20260813-spark-4` | Passed | Repeated schema repair exposed the incomplete template | Skill |
| `video-compositor-regression-20260813-spark-5` | Passed | JSON syntax required repair after the complete template landed | Agent |
| `video-compositor-regression-20260813-spark-6` | Passed | The shortened unsupported `plantuml` producer ID exposed missing exact-ID guidance | Skill |
| `video-compositor-regression-20260813-spark-7` | Passed | Passed with zero tool errors | Pass |

Run 7 used `openai-codex/gpt-5.3-codex-spark` with high thinking, strict JSON mode, the runtime profile, exact command enforcement, and seven field assertions. It wrote both required outputs once, ran the required validator once, passed independent evaluator-side validation with four elements, three interactions, and two cross-producer interactions, and preserved skill payload SHA-256 `f2ad1c69cb0f5912211b5341a4c4bacb939c545a2c9ece4ffd62eae6454ad564`. The contract SHA-256 is `6b31789e6479c2fffb829a3305361210e87a4810d1aa9c0516b811c3c779169d`; the validation-report SHA-256 is `3aac0e115fd43931600f8e3a489454eb7333e4045d21e050cf2e38b1d4e1c618`. The focused read surface contains only the prompt, `SKILL.md`, two references, the compact template, and the generated report. Durable trace summary: `evaluations/video-compositor-regression-20260813-read-surface.json`.
