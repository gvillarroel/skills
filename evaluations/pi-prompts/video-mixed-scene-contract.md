Use the `$video` skill to design a mixed-media scene contract. Read this prompt before any skill file.

The skill has no `README.md`; do not try to read one. Read `skills/video/SKILL.md` and only the references or scripts needed for this contract.

Do not search or list the skill bundle, and do not read the validator source. The complete allowed skill read surface for this case is `skills/video/SKILL.md`, `skills/video/references/scene-interaction-contract.md`, `skills/video/references/output-format-contract.md`, and `skills/video/assets/templates/scene-contract.json`. Construct the final JSON before writing it; after the single write, run the required validation command without rereading or editing the contract.

Keep every JSON string value on one physical line. Do not place literal newlines, tabs, or unescaped quotation marks inside `meaning` or `validationChecks` strings.

The `deliverables/` directory starts absent. Do not probe or list it before creating the requested output. Write the complete contract in one operation; do not use partial line-range reads or incremental rewrites on the generated JSON. Let the bundled validator perform the structural verification, then read only its finished report.

Create exactly these non-empty outputs:

- `deliverables/scene-contract.json`
- `deliverables/scene-validation.json`

Do not create or redraw any PlantUML, Mermaid, or GIF artifact. Treat the following producer outputs as already contracted but not present in this isolated planning workspace:

- `assets/architecture.svg`, produced by `plantuml-colorset-renderer`, intrinsic viewBox `0 0 1200 800`, selector port `service-out` at `#service`, static clock, report path `reports/architecture.json`.
- `assets/process.svg`, produced by `mermaid`, intrinsic viewBox `0 0 1000 900`, selector ports `request-in` at `#request` and `result-out` at `#result`, states `idle`, `running`, and `success`, static clock, report path `reports/process.json`.
- `assets/result.gif`, produced by `animated-svg-to-gif`, intrinsic size 640x360, normalized port `result-center` at 0.5/0.5, decoded playback on the master clock, report path `reports/result.json`.
- `assets/alert.gif`, produced by `animated-svg-to-gif`, intrinsic size 480x480, normalized port `alert-center` at 0.5/0.5, decoded playback on the master clock, report path `reports/alert.json`.

The output is a vertical 1080x1920 scene at 30 fps for exactly 12 seconds, with exact reduced aspect ratio `9:16`, a deterministic non-looping master clock, a dark background, and nonzero safe areas. Place all four assets inside the canvas without overlap that hides another asset. Use an explicit z-order.

Define this semantic sequence:

1. A visible signal travels from PlantUML `service-out` to Mermaid `request-in` from 1.5 to 3.0 seconds and emits `request-arrived`.
2. Mermaid changes from `idle` to `running`, then `success`. A visible handoff travels from Mermaid `result-out` to GIF A `result-center` from 5.0 to 6.0 seconds, consumes `request-arrived`, and emits `result-ready`.
3. GIF A is revealed by a deterministic opacity track. A visible signal travels from GIF A `result-center` to GIF B `alert-center` from 8.0 to 9.0 seconds, consumes `result-ready`, and emits `alert-ready`.
4. GIF B is revealed by a deterministic opacity track.

Include concrete plain-English meanings and validation checks for every interaction. Use project-relative paths, stable lowercase hyphen-case IDs, valid fit/overflow/background/clock fields, and 64-character lowercase hexadecimal placeholder hashes. Keep diagram internals owned by their producer skills; express all cross-tool behavior through ports, events, tracks, and interactions.

After writing the contract, run this exact command directly from the isolated workspace. Do not wrap it in `bash -lc`, `sh -c`, `cmd /c`, or another shell command:

```shell
uv run --script skills/video/scripts/validate_scene_contract.py deliverables/scene-contract.json --project-root . --output deliverables/scene-validation.json --json
```

Finish only after that command exits successfully and `scene-validation.json` reports `ok=true`, `summary.width=1080`, `summary.height=1920`, `summary.aspectRatio=9:16`, `summary.elementCount=4`, `summary.interactionCount=3`, and `summary.crossProducerInteractionCount=2`.
