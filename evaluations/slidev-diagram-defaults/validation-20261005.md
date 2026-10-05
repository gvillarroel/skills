# Slidev Mermaid Defaults Validation — 2026-10-05

## Scope and resulting behavior

Updated `slidev-echarts` and `slidev-animejs` so a deck installs one self-contained native Mermaid setup and ordinary Mermaid fences inherit Colorset 1. The runtime uses the same exact palette contract as Mermaid and PlantUML: primary red `#9e1b32`, red/neutral category slots, white canvas, neutral containers, `#696969` relationships, and black/white inside text chosen by contrast. Colorset 2 requires an explicit selector change. Existing diagram facts, accessible metadata, layout and semantic strokes remain native Mermaid output.

The two three-file runtime packs are byte-identical. Final `diagram-style.mjs` SHA-256: `b16f9f5cade2898beead219b0c451636e8608d16dc162dcb26043dd5c122b8da`. Both setup hooks import only their deck-local dependencies; fixture hooks inject those dependencies into the same runtime helper rather than importing a package-dependent hook from outside the fixture.

The renderer serializes native calls across fresh hook factories, keeps the selected palette when Slidev supplies its automatic dark theme, waits for Open Sans before measuring, provides an actual white diagram canvas, and repairs native ER attribute text, pie-slice labels and class compartment separators. An explicit `colorsetPresentation: 'source'` fence bypasses the palette configuration and finisher so requested native themes and outlines remain intact.

Indexed categories use native slots. Reordering categories can change their colors; the integration does not claim a deck-wide identity allocator. Keep category order or explicit semantic mappings consistent when identity continuity matters.

## Native browser evidence

Final native matrix: **40/40 pass**, ten diagram families × two palettes × light/dark UI. Families: flowchart, sequence, class, state, ER, pie, mindmap, Gantt, gitGraph and timeline. The timeline fixture uses normal `scale: 0.65` sizing metadata; it has no color or theme directives. Source/forest preservation also passes with native green bodies and 1 px green outlines.

Evidence is local and ignored: `projects/slidev-diagram-defaults/artifacts/final3/` contains the six common families and source boundary; `extended-final3/` contains the four additional families. Each run retains its generated deck, build log, native PNG/SVG and `verification.json`. The evaluator records the copied helper hash and checks exact palette paints, supplied labels, visible nonblank geometry, foreignObject glyph containment, viewport containment, maximum black/white inside contrast, outside text contrast, relationship shafts/markers, and class compartment contrast.

Root and delegated manual reviews inspected real screenshots. Final class separators retain their original 1 px widths and paths, use white on primary red, and measure 7.9047:1. ER rows retain visible black attributes; source mode preserves original SVG presentation.

Representative reproducible command:

```powershell
node --experimental-strip-types projects/slidev-diagram-defaults/scripts/verify-mermaid-defaults.ts --palette colorset1 --scheme light --output projects/slidev-diagram-defaults/artifacts/final3/colorset1-light
```

Repeat with `--palette colorset2`, `--scheme dark`, and `--extended`. Use `--source` for the native theme boundary. Use a fresh output path when regenerating evidence.

## Findings, fixes and retained failures

- Initial ER output used white attribute glyphs on white rows; exact native row surfaces and black attribute labels now pass.
- A gray pie slice used a shared white label; each slice now chooses contrast from its native fill.
- Initial actual acceptance screenshots cropped final glyphs after asynchronous Open Sans loading even though DOM strings were complete. Font readiness fixes native measurement. The evaluator now checks actual glyph bounds. `negative-font-baseline/` rejects the untouched first output.
- The first class gate missed red-on-red compartment separators. The corrected gate rejects four 1:1 separators in `negative-divider-baseline/`, and the final native class output passes without geometry changes.
- An initially unscaled timeline overflowed its slide. This remains a retained composition failure; normal size metadata makes the final test readable and contained.
- Initial fixture imports could not resolve packages from a runtime-template directory. Thin deck-local hooks now inject native Mermaid into the shared helper; both full acceptance builds pass.
- The first Pages build metadata helper matched a `<body>` literal inside bundled Mermaid JavaScript. Native HTML tag parsing now places metadata in the actual document. Subsequent head metadata/favicon and whitespace normalization findings are addressed by the same publication regression work.

Initial reports and screenshots remain under the project artifact directories, including `fixtures/`, `final2/`, `extended/`, and the explicit negative baselines. They are not counted as final release passes.

## Isolated runtime evaluations

Every run uses the runtime payload, disabled ambient context/discovery, strict JSON mode, exact expected outputs, observed-model checks, zero tool errors, a prompt-first read, clean read surface and immutable copied skill payload. No acceptance gallery, sibling skill or repository documentation is provided to the agent.

Fresh Spark contract attempts for both skills failed before tools: this ChatGPT account does not support `gpt-5.3-codex-spark`. Those failures are retained as external/provider failures, not passed runs. Preliminary Luna trials are also retained: both ECharts contract attempts failed strict gates because self-authored global grep checks incorrectly rejected legal Slidev headmatter `theme: default`; Anime.js naturalistic trial 1 failed a nonexistent output-directory self-check. One Luna contract and one naturalistic run passed strict gates, but predate the final class-divider repair and are not final release evidence.

The model exception is `openai-codex/gpt-5.6-sol`, recorded in `SKILLS.md`. The first Sol cohort on the repaired runtime passed both contract cases, ECharts naturalistic runs 1 and 2, and Anime.js naturalistic run 3; ECharts run 3 and Anime.js runs 1 and 2 failed strict zero-tool-error gates because their ad hoc checks counted headmatter separators or both opening and closing fence lines. Independent native rendering passed all 24 diagrams, but those failed strict runs remain failures. This cohort prompted an actual skill simplification rather than a relaxed acceptance gate.

Both bundles now provide a read-only `scripts/check_mermaid_deck.py` (SHA-256 `d57cf4088aeb42e7f298f438278153ea8a3067eafb29752afec43e57c2273952`). It verifies nonempty runtime files, Slidev/theme declarations, balanced fences, an optional Mermaid block count, and an optional plain-source check limited to Mermaid bodies and options. Legal deck headmatter and extra CSS pass; the checker does not infer Slidev slide counts. The compact skill routes tell agents to use it for static checks and native Slidev metadata for slide counts. Deterministic positive/negative regressions pass, including empty hooks and malformed or styled Mermaid inputs. The frozen final cohort below uses this simplified bundle and retains every repetition. Acceptance gates are unchanged.

Final command shape (repeat required artifact flags for all six paths):

```powershell
uv run --script scripts/run-pi-skill-eval.py slidev-echarts --prompt-file evaluations/pi-prompts/slidev-mermaid-defaults-echarts-naturalistic.md --model openai-codex/gpt-5.6-sol --thinking high --mode json --strict --run-id 20261005-slidev-mermaid-echarts-sol-final-natural-1 --expect-output deck/slides.md --expect-output deck/package.json --expect-output deck/diagram-style.mjs --expect-output deck/setup/mermaid.ts --expect-output deck/setup/mermaid-renderer.ts --expect-output deliverables/style-review.md
```

Independent artifact command shape:

```powershell
node --experimental-strip-types projects/slidev-diagram-defaults/scripts/verify-mermaid-defaults.ts --existing --deck evaluations/runs/20261005-slidev-mermaid-echarts-sol-final-natural-1/workspace/deck --expect-helper-sha b16f9f5cade2898beead219b0c451636e8608d16dc162dcb26043dd5c122b8da --output projects/slidev-diagram-defaults/artifacts/pi-final/20261005-slidev-mermaid-echarts-sol-final-natural-1
```

| Skill | Case | Strict / model / integrity | Independent native output |
| --- | --- | --- | --- |
| slidev-echarts | `20261005-slidev-mermaid-echarts-sol-final-contract` | PASS | 3/3 PASS |
| slidev-echarts | `20261005-slidev-mermaid-echarts-sol-final-natural-1` | PASS | 3/3 PASS |
| slidev-echarts | `20261005-slidev-mermaid-echarts-sol-final-natural-2` | PASS | 3/3 PASS |
| slidev-echarts | `20261005-slidev-mermaid-echarts-sol-final-natural-3` | PASS | 3/3 PASS |
| slidev-animejs | `20261005-slidev-mermaid-animejs-sol-final-contract` | PASS | 3/3 PASS |
| slidev-animejs | `20261005-slidev-mermaid-animejs-sol-final-natural-1` | PASS | 3/3 PASS |
| slidev-animejs | `20261005-slidev-mermaid-animejs-sol-final-natural-2` | PASS | 3/3 PASS |
| slidev-animejs | `20261005-slidev-mermaid-animejs-sol-final-natural-3` | PASS | 3/3 PASS |

Trace summaries use `summarize-pi-json-events.py` for every final event file with `--require-model gpt-5.6-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md` and explicit forbidden-example/sibling read policies. Review also checks indirect shell reads. Only the prompt, owning skill core, focused small references/palette, required runtime templates, and generated deck files are read; no acceptance gallery, repository documents, sibling bundle, or outside workspace data is accessed. The largest required helper read is 12,608 serialized bytes (12,259 source bytes), with no 50 KB source reads.

Final release cohort: **8/8 strict passes**, both contract cases and **3/3 fresh naturalistic repetitions per skill**. Independent builds and Chromium checks pass all **24/24 generated diagrams**. The official Slidev parser independently confirms exactly three slides and one plain Mermaid fence per slide in every deck; `node --experimental-strip-types projects/slidev-diagram-defaults/scripts/summarize-final-cohort.ts` produces the retained `artifacts/pi-final/final-cohort-summary.json`. Each run creates the six exact required artifacts, has zero tool errors and an unchanged runtime payload, uses the bundled static checker, and copies the frozen b16 helper. All original unsuccessful cohorts remain separately retained.

## Repository, publication and scope limits

Repeatable helper checks are `test-render-queue.ts` and `test-render-queue-browser.ts` under the project scripts. They verify exact configuration paints, concurrent selectors and automatic dark options, native failure propagation/recovery, source preservation, and immutable identical helpers. The browser test uses actual Chromium DOMParser/style/XMLSerializer with a native-state interleaving mock; real Mermaid output is covered independently by the 40-case matrix.

Both existing published decks contain plain accessible flowcharts. Stable pattern IDs/routes are `slidev-animejs-mermaid-defaults` at `https://gvillarroel.github.io/skills/examples/slidev-animejs/#/31` and `slidev-echarts-mermaid-defaults` at `https://gvillarroel.github.io/skills/examples/slidev-echarts/#/37`. They remain discoverable from the canonical examples index through their existing example sets.

Repository gates passed: `validate-pattern-ids.py` (1,222 canonical IDs), `validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`, `test-pi-eval-harness.py` (17 regressions), `audit-skill-authoring.py --check-bundles` (34 skills / 68 bundles, zero issues), exact palette validation and owning Mermaid/PlantUML regression suites. Both render-queue tests and the new static checker regression script pass.

Publication gates passed locally: `test-pages-output.py` (14 regressions), `build-pages.py` (723 files / 56.20 MiB), and `validate-pages-pattern-format.py` (14 listed example sets). The two real `dist/pages` hash routes passed Chromium validation under `artifacts/pages-release/`; reversing the six native metadata insertions exactly reproduces each original HTML export. This preserves the complete 5.3 MB ECharts bundled JavaScript.

`sync-local-skills.py` installed 20 changed source files; `sync-local-skills.py --check` confirms all 10,309 canonical files match the local installation and bundle validation passes. Final GitHub Pages deployment remains pending the reviewed source commit and remote acceptance.

Coverage is scoped to native Slidev 52.16.0 and Mermaid 11.15.0 in the acceptance dependency installation and the ten qualified families. Additional renderer families still require inspection in an actual deck; this record does not assert every Mermaid family or maximum category capacity. Existing Slidev skill validation history remains intact. Generated screenshots/builds/runs stay ignored; pre-existing unrelated working-tree edits are preserved.
