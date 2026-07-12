---
name: plantuml-colorset-renderer
description: Render PlantUML diagrams with bundled colorset1 and colorset2 themes and a normalized 1,500+ SVG catalog spanning AWS, Google Cloud, major companies, programming languages, databases, frameworks, infrastructure, and developer tools. Use when Codex needs to create, style, batch-render, or validate PlantUML `.puml`, `.plantuml`, or `.pu` sources as SVG and PNG, find and insert consistently sized technical logos, build cloud architecture diagrams, or check PlantUML diagram-family coverage.
---

# PlantUML Colorset Renderer

## Core Contract

Preserve the user's PlantUML source semantics. Apply the requested bundled colorset theme as presentation only, then render SVG and PNG outputs with a report that records every source, output path, format, colorset, and render engine. Default to colorset2 unless the user asks for colorset1.

Prefer local rendering for private diagrams. Use a remote fallback such as Kroki or PlantUML Server only when the user permits external rendering or the task is validation/example work with non-sensitive sources.

## Workflow

1. Read `references/diagram-types.md` and its machine-readable source `references/diagram-types.json` when the task asks which PlantUML diagram types are covered or when maintaining examples.
2. Run `scripts/render_plantuml_directory.py` against the requested directory with `--colorset colorset2` or `--colorset colorset1`, `--format svg --format png`, and a JSON report.
3. Inspect the report. Confirm `ok` is `true`, failures are zero, and each result has the requested or capability-declared formats.
4. If maintaining this skill, supply `--coverage-manifest references/diagram-types.json`. Validate exact family and fixture sets instead of relying on a count.

Normal user rendering does not load the coverage manifest. Ditaa, standalone AsciiMath, and standalone LaTeX still bypass theme injection because adding theme text would corrupt or be ignored by those syntaxes.

## Commands

Render a directory to SVG and PNG with the bundled colorset2 theme:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py path/to/plantuml --output path/to/renders --colorset colorset2 --format svg --format png --report path/to/plantuml-render-report.json
```

Render the same directory with the bundled colorset1 red-neutral theme:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py path/to/plantuml --output path/to/renders-cs1 --colorset colorset1 --format svg --format png --report path/to/plantuml-render-report-cs1.json
```

Render the bundled coverage examples when maintaining the skill:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py .agents/skills/plantuml-colorset-renderer/assets/examples/base --output projects/plantuml-colorset-renderer/artifacts/examples --format svg --format png --coverage-manifest .agents/skills/plantuml-colorset-renderer/references/diagram-types.json --publication-only --report projects/plantuml-colorset-renderer/artifacts/examples/report.json
```

Validate a render report and artifacts:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report projects/plantuml-colorset-renderer/artifacts/examples/report.json --output projects/plantuml-colorset-renderer/artifacts/examples --colorset colorset2 --coverage-manifest .agents/skills/plantuml-colorset-renderer/references/diagram-types.json
```

Validate the frozen manifest, fixtures, reports, and published galleries:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/validate_plantuml_coverage.py --fixtures .agents/skills/plantuml-colorset-renderer/assets/examples/base --report .agents/skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/render-report.json --report .agents/skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/render-report.json --gallery .agents/skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer --gallery .agents/skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1
```

Use a private/local PlantUML endpoint instead of the public server:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py path/to/plantuml --output path/to/renders --format svg --format png --engine server --server-url http://localhost:8080/plantuml --report path/to/plantuml-render-report.json
```

Use Kroki explicitly for remote rendering:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py path/to/plantuml --output path/to/renders --format svg --format png --engine kroki --report path/to/plantuml-render-report.json
```

Write themed source copies for debugging or handoff:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py path/to/plantuml --output path/to/renders --format svg --format png --write-themed
```

## Normalized Logo Assets

Use the 1,648 SVG files in `assets/logos/` when a PlantUML diagram needs a cloud, company, programming-language, database, framework, infrastructure, or developer-tool logo. The catalog contains 860 AWS symbols, 93 GCP symbols, 578 Devicon technologies, and 117 individually licensed Simple Icons brands. Every logo has the same intrinsic `256×256` size, `0 0 256 256` viewBox, 16-unit padding, and centered `meet` scaling, so one scale value produces predictable boxes without stretching.

Search the compact manifest instead of reading the 1,500-row license log:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/list_logo_assets.py --search lambda --provider AWS
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/list_logo_assets.py --search kubernetes --json
```

Read the selected records in `assets/logos/logo_manifest.json` and consult `assets/logos/license_log.md` for redistribution. Treat trademark permission as separate from the artwork copyright license, and do not imply endorsement.

AWS and GCP artwork uses CC-BY-ND-2.0. Preserve its embedded source bytes and do not recolor, crop, redraw, or extract and modify it. Resize only through the normalized outer SVG viewport or PlantUML image scale. Devicon artwork uses MIT, but its marks still remain subject to owner trademark policies.

For a portable handoff, export all logos and the license log byte-for-byte without network access:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/sync_normalized_logos.py --export path/to/deliverable/logos
```

For the full catalog, use this single export command and trust its built-in manifest, embedded-hash, inventory, license, and SVG checks. Do not enumerate, print, read, or compare all 1,648 files individually; large directory output can overwhelm the runtime. Confirm only the command exit code and a few requested exact paths.

Insert a local logo with PlantUML image markup, using the same scale for peer logos:

```plantuml
rectangle "<img:assets/logos/aws/compute/lambda.svg{scale=0.25}>\nAWS Lambda" as lambda
rectangle "<img:assets/logos/gcp/compute/cloud-run.svg{scale=0.25}>\nCloud Run" as run
rectangle "<img:assets/logos/devicon/technology/kubernetes.svg{scale=0.25}>\nKubernetes" as k8s
```

Resolve image paths from the PlantUML source or renderer working directory. Prefer paths without spaces. For a portable delivery, export the complete bundle or copy selected SVGs while retaining `license_log.md`, `logo_manifest.json`, and `licenses/`.

Refresh the pinned source assets and validate their hashes and common sizing contract:

```powershell
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/sync_normalized_logos.py
uv run --script .agents/skills/plantuml-colorset-renderer/scripts/sync_normalized_logos.py --check
```

When maintaining the catalog, rebuild `logo_manifest.json` from the four pinned source clones with `scripts/build_logo_manifest.py`, then run the sync command with `--source aws=...`, `--source gcp=...`, `--source devicon=...`, and `--source 'simple icons'=...`. Do not hand-edit generated SVG wrappers or the generated license log.

## Bundled Themes

Use `assets/themes/cs2.puml` for the full colorset2 palette. It maps the repository colorset2 palette to PlantUML `skinparam` and CSS-like `<style>` rules:

- Primary red: `#9e1b32`
- Accent blue: `#007298`
- Warning orange: `#e77204`
- Success green: `#45842a`
- Info cyan: `#00ace6`
- Special purple: `#652f6c`
- Neutral ink and grays: `#333e48`, `#696969`, `#e7e7e7`

Use `assets/themes/cs1.puml` for the colorset1 red-neutral palette:

- Primary red: `#9e1b32`
- Red hover/emphasis: `#6d1222`
- Critical red: `#e8002a`
- Red highlight: `#ffccd5`
- Neutral ink and grays: `#333e48`, `#696969`, `#9c9c9c`, `#cfcfcf`, `#e7e7e7`

Do not add semantic classes or labels to user diagrams unless the user asks. The renderer injects the theme in memory after compatible `@start...` lines and leaves the original files unchanged unless `--write-themed` is passed. It never injects theme text into `@startditaa`, `@startmath`, or `@startlatex`. Kroki Ditaa requests use the `ditaa` route.

## Output Checks

After rendering, verify:

- `ok` is `true` in the report.
- `failedDiagramCount` is `0`.
- Each arbitrary diagram result has the requested outputs. Coverage-mode fixtures have the exact formats declared in `diagram-types.json`; Ditaa is PNG-only.
- Coverage reports contain all 28 family IDs and all 29 fixture IDs exactly once, with Chronology recorded as `expected-unavailable` and no artifact.
- SVG outputs contain `<svg` and expected colorset tokens such as `#9e1b32`, `#007298`, or `#e77204` for colorset2, or `#9e1b32`, `#6d1222`, and `#ffccd5` for colorset1.
- PNG outputs are non-empty binary files.
- For private source, the report uses a local endpoint or local PlantUML command rather than a public remote service.
