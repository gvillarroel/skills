# PlantUML renderer-only release validation — 2026-09-02

## Scope and verdict

- Skill: `plantuml-colorset-renderer`
- Source revision inspected: `29ae22617120b1d04fae1bfbd10f9b22cf4d1c3f`
- Release model: `openai-codex/gpt-5.3-codex-spark`
- Runtime payload: 12 files, SHA-256
  `50c472bc3455956ca3704d1cee02c36a725213faf4e2b5620c3357f3bb453203`
- Boundary result: pass. The runtime bundle contains renderer, report validator,
  coverage references, and Colorset 1/2 themes. It no longer contains the
  technical-logo catalog, logo maintenance scripts, logo licenses, or logo
  manifests. The skill only names `$technical-logo-assets` as an optional
  companion and explicitly forbids reading a sibling skill directory.
- Deterministic and independent artifact gates: pass.
- Current strict isolated Spark gate: blocked by global Codex usage quota before
  the model made a tool call. This is an `infrastructure` failure, not a skill,
  agent, validator, or harness failure. The current payload therefore must remain
  in `validating` state until the same strict contract is rerun after quota reset.

## Deterministic checks

Python compilation passed for all six renderer scripts:

```powershell
uv run python -m py_compile skills/plantuml-colorset-renderer/scripts/build_plantuml_gallery_metadata.py skills/plantuml-colorset-renderer/scripts/plantuml_coverage.py skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py skills/plantuml-colorset-renderer/scripts/test_plantuml_coverage.py skills/plantuml-colorset-renderer/scripts/validate_plantuml_coverage.py skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py
```

The focused suite passed 16/16 tests:

```powershell
uv run --script skills/plantuml-colorset-renderer/scripts/test_plantuml_coverage.py
```

The frozen coverage contract passed with 27 canonical families, one release-extra
family, 28 total families, 29 fixtures, 28 published fixtures, and no findings:

```powershell
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_coverage.py --fixtures skills/plantuml-colorset-renderer/assets/examples/base --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/render-report.json --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/render-report.json --gallery skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer --gallery skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1
```

Both published reports passed exact manifest-aware artifact validation:

```powershell
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer --colorset colorset2 --coverage-manifest skills/plantuml-colorset-renderer/references/diagram-types.json
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1 --colorset colorset1 --coverage-manifest skills/plantuml-colorset-renderer/references/diagram-types.json
```

## Renderer-only artifact validation

The evaluator created fresh synthetic sequence, class, and mind-map sources under
the ignored run workspace, rendered each to SVG and PNG through Kroki with
Colorset 2, and validated the report with the bundled validator:

```powershell
$root = 'evaluations/runs/20260902-plantuml-independent/workspace'
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py "$root/inputs" --output "$root/outputs/plantuml" --colorset colorset2 --format svg --format png --engine kroki --report "$root/outputs/plantuml/report.json"
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report "$root/outputs/plantuml/report.json" --output "$root/outputs/plantuml" --colorset colorset2 --expected-diagrams 3 --expect-format svg --expect-format png
```

Result: `ok=true`, three sources, three rendered diagrams, six outputs, zero
failures. The report SHA-256 is
`f2f940ec00d73e086e767f5c9bf2c8f153efa6e487d137af9a95abc4253af6d7`;
the bundled validation JSON SHA-256 is
`94a8bb38428c411aee3ebb2b6498b270f255ef4ee8e09421cd9ef1dccaca1104`.

The evaluator-owned validator then checked report/result identity, requested and
actual formats, engine identity, reported byte counts, XML parsing, SVG
dimensions and view boxes, PlantUML diagram-type metadata, required labels,
Colorset 2 tokens, error markers, remote references, PNG signatures, PNG decode,
dimensions, nonblank pixel samples, and Chromium rendering at `1024x768` and
`390x844`:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/verify_runtime_artifacts.py --output evaluations/runs/20260902-plantuml-independent/workspace/outputs/plantuml --report evaluations/runs/20260902-plantuml-independent/independent-validation.json --screenshot-dir evaluations/runs/20260902-plantuml-independent/screenshots
```

Result: pass, zero findings, zero console errors, zero page errors, and zero
failed requests. Direct visual review of all six desktop/mobile screenshots found
complete, readable, unclipped sequence, class, and mind-map diagrams with the
expected CS2 styling.

A fail-closed control against a nonexistent output directory returned exit 1,
`passed=false`, and seven findings, proving that the evaluator does not approve
missing report or artifact inputs.

Artifact identities:

| Diagram | SVG bytes | SVG SHA-256 | PNG size | PNG SHA-256 |
| --- | ---: | --- | --- | --- |
| Class | 5,923 | `111a92aed854c44d7d29e3222f936b7fd9964508a0f00a2eb5aaf188649ecfcd` | 162×280 | `fe7be61b10b98ef82f3f625c00f6eb8360778885fdbb060b0355e1be0066e846` |
| Mind map | 3,494 | `b666740deba1b395cd29b9281d01f24172035341822bcb2c892655017162a7f0` | 305×226 | `86185550a3bbd849dc7e62ce0e36c93c5151c2be92bd6540156c0f55eaf13d3b` |
| Sequence | 8,649 | `385c42bc0c4a65740d5b32787f210d42027879467d1cdac59107736039c57e8c` | 217×336 | `249e734ebb018d6a70c426a6135ee601d9be72c8a9415bbe3edb2a2853772e06` |

## Strict isolated Spark attempt

Prompt: `evaluations/pi-prompts/plantuml-colorset-renderer-render-contract.md`

Run ID: `20260902-plantuml-render-contract-spark-1`

The command used strict JSON mode, exact-command enforcement, all eight exact
artifact paths, and eight objective JSON field assertions:

```powershell
uv run --script scripts/run-pi-skill-eval.py plantuml-colorset-renderer --prompt-file evaluations/pi-prompts/plantuml-colorset-renderer-render-contract.md --mode json --strict --run-id 20260902-plantuml-render-contract-spark-1 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output outputs/plantuml/report.json --expect-output outputs/plantuml/validation.json --expect-output outputs/plantuml/svg/sequence.svg --expect-output outputs/plantuml/png/sequence.png --expect-output outputs/plantuml/svg/class.svg --expect-output outputs/plantuml/png/class.png --expect-output outputs/plantuml/svg/mindmap.svg --expect-output outputs/plantuml/png/mindmap.png --expect-output-json-field 'outputs/plantuml/report.json::ok=true' --expect-output-json-field 'outputs/plantuml/report.json::colorset=colorset2' --expect-output-json-field 'outputs/plantuml/report.json::engine=kroki' --expect-output-json-field 'outputs/plantuml/report.json::sourceDiagramCount=3' --expect-output-json-field 'outputs/plantuml/report.json::renderedDiagramCount=3' --expect-output-json-field 'outputs/plantuml/report.json::failedDiagramCount=0' --expect-output-json-field 'outputs/plantuml/validation.json::ok=true' --expect-output-json-field 'outputs/plantuml/validation.json::checkedDiagramCount=3'
```

Pi emitted the requested provider/model identity, then immediately returned
`Codex error: The usage limit has been reached`. It used zero input tokens, zero
output tokens, made zero tool calls, and generated no artifact. The harness
correctly failed the artifact, event, and JSON-field gates while preserving the
copied bundle exactly. Skill integrity passed with identical before/after digest
`50c472bc3455956ca3704d1cee02c36a725213faf4e2b5620c3357f3bb453203`.

Failure classification: `infrastructure` (global model usage quota). This attempt
is retained and must not be counted as a skill failure or a release pass. Because
the prompt is a deterministic command-contract case, one passing fresh repetition
after quota reset is sufficient; no naturalistic repetition cohort was used here.

## Versioned evaluation files added

- `evaluations/pi-prompts/plantuml-colorset-renderer-render-contract.md`
- `evaluations/plantuml-colorset-renderer/verify_runtime_artifacts.py`
- `evaluations/plantuml-colorset-renderer/renderer-only-release-20260902.md`

No PlantUML skill source was changed during this validation pass.
