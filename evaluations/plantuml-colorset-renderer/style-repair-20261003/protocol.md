# PlantUML native-style release protocol — 2026-10-03

This preregistered suite evaluates the native theme and finished SVG behavior
of `plantuml-colorset-renderer`. Preparation does not establish a release pass.
Run it only after the implementation owner announces a frozen candidate and
the deterministic skill checks pass.

The recorded model exception in `SKILLS.md` permits
`openai-codex/gpt-5.6-luna`, `medium`; the 2026-09-27 release recorded a provider
rejection of Spark before execution. Retain all normal isolation, strict JSON,
exact artifact, tool-error, payload-integrity, and direct visual review gates.

| Case | Taxonomy | Runs | Surface |
| --- | --- | ---: | --- |
| baseline | contract-smoke | 1 | Default colorset1; activity branches; plain and weak Chen entities; deployment region, actor, components, database, and direction |
| boundary | boundary-recovery | 1 | Explicit Padding 18, pale-blue rectangle fill and 3 px border; native sequence database glyph and exterior text |
| generalization | generalization | 3 | Fresh mindmap, WBS, Gantt and network inputs in colorset2; tree/schedule/network semantics |

All cases require source paths, SVG and PNG paths, `render-report.json`,
`validation.json`, and `review.md`. Both static delivery formats must preserve
native geometry and semantic strokes; PNG must report `svg_derived: true`.
Generalization requires at least two joint passes out of three fresh runs.
A joint pass includes harness, independent artifact validation, trace review,
and direct visual review. Record every attempt and classification before any
repair or repetition. Do not reuse workspaces or reveal earlier artifacts to
the tested agent.

Only the runtime skill payload is copied into each workspace. It excludes
`assets/examples/`, dependencies, caches, and generated output. The loaded
bundle is immutable, and tasks may use only their supplied prompt and normal
local tools. The tested agent must not discover repository or sibling paths.

The evaluator supplies `plantuml` as a normal local executable on PATH. The
ignored Windows `.cmd` wrapper and extensionless Bash shim invoke the same
fixed PlantUML 1.2026.6 jar with Java 17;
the tested agent sees no launcher path or external source data. The evaluator
checks both bare `plantuml -version` in Pi-compatible Git Bash and normal
Python CLI discovery/version before each non-dry case dispatcher launches
its repetitions, and records both
wrapper hashes and the jar hash. This is an
installed tool boundary, not task knowledge or an extra skill payload.

Run only the ordinary local-tool preflight while a runtime freeze is pending:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/run_cases.py --case baseline --cohort final-r3 --tool-preflight-only
```

This writes `tool-preflight-<cohort>-<case>.json` without creating a Pi workspace
or copying any skill. The same checks automatically run at real dispatch.

The exact sources in contract/boundary prompts are new task inputs. Chen
weak-entity and identifying-relationship grammar was checked against the
[official PlantUML Chen documentation](https://plantuml.com/er-diagram).
Generalization prompts provide facts rather than fixture syntax.

Execute the runner from the repository root after the frozen-candidate notice:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/run_cases.py --case baseline --cohort final-r3
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/run_cases.py --case boundary --cohort final-r3
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/run_cases.py --case generalization --cohort final-r3
```

Each runner call dispatches the repository helper with `--profile runtime`,
`--mode json`, `--strict`, the recorded model exception, every exact
`--expect-output`, and report/validator JSON field assertions. It uses
`--require-exact-command-from-prompt` only for baseline. The run IDs are
`20261003-plantuml-style-<case>-<cohort>-<repetition>`. Bulky events, artifacts,
logs, and screenshots remain under ignored `evaluations/runs/`.

After a run, summarize its trace using the observed model exception:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!plantuml-colorset-renderer([\\/]|$))'
```

On Windows, use the evaluator's structured-argument wrapper to run exactly
the trace command above without shell regex escaping:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/summarize_traces.py --run-id <run-id>
```

The wrapper records the exact trace command and its log in the retained run
folder. It fails explicitly when no Pi event trace exists.

Run the independent artifact inspector for every retained run:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/verify_outputs.py --case <case> --run-id <run-id>
```

This inspector parses exact sources and native families, decodes PNG colors and
dimensions, collects a full shape inventory, and samples actual Chromium
backings with labels and links hidden to measure text and shaft/head contrast.
It saves every SVG screenshot and requires a separate direct visual review.
Its shape annotation checks are supplementary; a missing annotation cannot
establish that a native shape has the correct border policy.

For every completed run, independently inspect all actual shell commands for
indirect outside-workspace, sibling, example, repository or harness reads,
network access, payload edits, or renderer bypass. Save the review as
`command-audit.json` in that retained run folder with boolean `passed`,
`isolationPassed` and `strictRuntimePassed` fields. Keep recovery or bounded
pre-render task-source observations explicit. Artifact/direct visual
acceptance remains a separate scope.

After completing all direct and command reviews, collect the durable
hash/dimension/read surface proof from the completed run records:

```powershell
uv run --script evaluations/plantuml-colorset-renderer/style-repair-20261003/collect_evidence.py --cohort <cohort>
```

This writes `<cohort>-artifact-identities.json` beside the protocol. It records
every attempt and preserves failing gates; it does not award a release pass.

Independently inspect all final SVG and PNG artifacts. Check exact source
semantics, expected labels, diagram families, actual solid fill/border behavior,
maximum black/white text contrast against actual backing, visible actor and
database details, preserved Chen weak/identifying glyphs, and arrow shaft/head
contrast through compound regions. The bundled validator alone cannot prove
the entire semantic or visual contract. Record dimensions, hashes, independent
findings, screenshot evidence, read surface, and immutable payload digest in
the durable release summary. Do not promote a visually defective zero-error
model run.
