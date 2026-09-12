# UsefulCharts-style: complete name/date groups and local court composition

The v25 candidate makes ordinary genealogical records read as compact colored name/date groups and resolves the competing Everen territory and court captions. The revised skill reproduces this grouping in three isolated family runs. This is measurable progress in the full quality-and-composition objective, but the three poster families remain distinguishable from their references. Keep the skill in `validating`.

The immutable comparison baseline is v24 commit `5720173d7f9cfe9e60dcaa8918f4656e53513c7f`. The frozen v25 runtime contains 81 files, SHA-256 `35f5c1657bc5511baffc3acd35d7e2c5c8aabb68caab5e0ffd361fcf61b8423c`. All four forward runs use that same payload. The [complete machine-readable summary](nameplate-composition-summary-20260912.json) retains every prototype, forward run, read surface, independent check and visual rejection. Earlier evidence is unchanged.

## Composition changes

In the dense genealogy, 208 ordinary principal records now place both name and short reign inside their category-colored card. This replaces repetitive thin name strips with more complete visual groups. The 17 selected portrait records retain the v24 outside-date treatment, larger names and larger image widths. Supporting plain relatives retain their smaller, unboxed treatment. These three treatments express different roles within the same family.

Changing card height requires recomposition: simply painting the taller cards over the previous geometry crowded a relationship attachment. The selected candidate therefore refits family baselines and all seven existing territory captions while retaining the v24 routing algorithm and the 1890 × 2835 canvas. It does not shrink the text or enlarge the page again. The early six-row expansion from v24 remains. Final crossing count is 16, compared with 17 in v24; this count is a geometric observation, not an aesthetic score.

The Everen court capsule still belongs to Conrad II, `person-35-0`, and still says exactly “EVEREN OF DUNPORT.” At the existing 9.5-unit type size, it now wraps into two lines in a 74-unit-wide capsule, below the named person. The large territory heading retains its own original source binding. The court's actual painted center is `(431.16, 2453.39)`, matching the requested position within serialization rounding. Its full painted rectangle, plus two units of clearance, intersects none of the sampled descent or partnership paths. A reading-scale browser crop confirms the two headings are visibly separate.

All 561 people, 261 partnerships, 323 relationships, 41 generations, 17 portrait identities and 19 annotations remain. All nonvisual person fields, categories, relationships and annotation bindings match the baseline. The final source-file SHA-256 is `89a0bba6972f1c240d1deaa37844276a5c3b3a7f24a937ec3242a43203044328`. The final canonical PNG is byte-identical to the complete, directly reviewed local-court prototype, SHA-256 `1f3acf13525b8e243c4eb7bb516830ea510d3e8999b0200ccce8e5ec7bd3d997`.

The institutional and chronology SVGs are byte-identical to v24 after line-ending normalization. They remain in the acceptance scope and were independently reaudited.

## Reusable skill behavior

The [name/date composition guide](../../skills/usefulcharts-style/references/genealogy-nameplates.md) records the distinction between ordinary principal cards, portrait groups and plain supporting relatives. It also explains why a wrapped court capsule may need an authored placement after automatic labels, and why actual painted position and full connector clearance must be checked.

The medium-family baseline helper now supplies inside dates for ordinary principal records. It retains outside dates for portraits and explicit `date_label` records, and honors explicitly supplied inside/outside treatments. The additional regression verifies these mixed defaults and verifies that the input source is not mutated. The skill supplies a light category palette only when the task and source have not supplied one, and asks for predominantly dark names. Existing source colors remain authoritative.

These rules are linked from `SKILL.md`, the baseline, cohort and editorial references, and the existing `usefulcharts-dynastic-genealogy` pattern recipe. No new pattern ID or gallery route was introduced.

## Rejected development attempts

Six exploratory variants and the final local-court composition remain under `projects/usefulcharts-style/artifacts/reviews/nameplate-composition-v25/`. They used an evolving project driver with the unchanged v24 router; their retained outcomes are evidence, not a claim of a separately frozen driver for each attempt.

| Attempt | Outcome | Reason |
| --- | --- | --- |
| `solid-principals` | Fail | Taller ordinary cards crowd the existing target attachment at `marriage-2-2-person-3-3`. |
| `solid-all` | Fail | Placing dates beside every portrait cannot fit an unbreakable reign in the existing card width. |
| `solid-principals-reflow` | Pass with unresolved composition | Complete data and geometry pass, but the Everen territory and court labels still compete. |
| `solid-all-reflow` | Fail | Reflow with all portrait dates inside leaves no readable local pocket for the required Bayeux territory caption. |
| `solid-principals-realm-gap` | No intended visual improvement | Geometry passes, but the requested realm offset is silently replaced by the old location. Its PNG is identical to the preceding complete candidate. |
| `solid-all-compact-context` | Fail | Even a narrower Bayeux caption at the same text/art size cannot find a valid local pocket. The intermediate stage lacks seven required captions and is not a final pass. |
| `solid-principals-local-court` | Pass | Ordinary solid cards, distinct portraits, all annotations and a visibly separated court capsule; source-backed audit and direct detail review pass. |

The attempted realm move initially appeared to separate the headings based on its requested offsets. Actual coordinate and PNG comparison disproved that claim; it was explicitly corrected before the final local court placement was accepted. This failure motivates the new painted-position check. No missing caption or partial composition is counted as a successful final artifact.

## Direct visual comparison

This is an unblinded author review, not an independent human discrimination study. The local comparison puts the official preview, v24 and v25 at the same display width while preserving aspect ratios: `projects/usefulcharts-style/artifacts/reviews/nameplate-composition-comparison/index.html`. Official preview artwork stays outside the public gallery.

The [European royal reference](https://usefulcharts.com/products/european-royal-family-tree) shows a denser and more varied rhythm of complete name groups, selected portraits, heraldry, and localized family branches. The revised ordinary cards approach that visual grouping more closely than the earlier thin strips. The portrait groups are now distinct, and the Everen caption conflict is resolved. Nevertheless, repeated family-unit sequences and several long cross-family paths still make the synthetic genealogy recognizable as a different composition. Image variety remains limited by the selected source records; arbitrary new portraits are not a valid way to fill gaps.

The [denominations reference](https://usefulcharts.com/products/christian-denominations-family-tree) releases and reallocates branch space across its history. The current institutional example still has unusually persistent left, center and right districts, fewer dense local transitions, and conspicuous long influence lines. The [world-history reference](https://usefulcharts.com/products/timeline-of-world-history) has fine, numerous interleaved strands and a varied distribution of objects, maps, periods and notes. The current chronology remains much more regular, with five broad histories and limited illustration variety. Passing their geometry audits does not resolve either visual gap.

## Isolated forward evaluation

The naturalistic prompt uses the complete 48-person Silver Vale family: 21 unions, 36 relationships, 95 known numeric dates, Xavier's unknown birth, three field-bound place captions and exactly three requested decorative museum portrait owners. It asks for light family colors, predominantly dark names and compact records with distinct portraits and supporting relatives. It does not prescribe the implementation or exact card coordinates. This is development reuse of a known family, not a sealed holdout.

The documented GPT-5.5 exception remains limited to image-dependent naturalistic tests because Spark cannot inspect PNG input. The separate command control uses the default Spark model. All runs are strict, isolated runtime-only tests with exact output paths, unchanged skill payloads, no tool errors and confined read surfaces.

| Run ID | Strict execution | Independent facts/browser | Direct visual acceptance |
| --- | --- | --- | --- |
| `usefulcharts-v25-family-nameplates-20260912-gpt55-1` | Pass | Pass | Pass for compact development output; broad connector shelves remain. |
| `usefulcharts-v25-family-nameplates-20260912-gpt55-2` | Pass | Pass | Pass for compact development output; lower route detours and regular family units remain. |
| `usefulcharts-v25-family-nameplates-20260912-gpt55-3` | Pass | Pass | Fail: the printable footer exposes `p32` and `p48` instead of the associated people's names. |
| `usefulcharts-v25-nameplate-contract-20260912-spark-1` | Pass | Pass | Command control only; no aesthetic claim. |

All three naturalistic runs read the new focused guide and inspect their PNG through a supported image result. Each preserves all source facts and contains 30 colored people, 27 solid name/date groups, three distinct portrait groups and 30 dark principal names. Those are descriptive SVG observations, not a visual similarity metric. The complete artifacts are readable, but run 3 fails the editorial acceptance gate despite its correct data and execution. Classify that defect as `agent`; do not relabel it a strict execution failure. Two of three runs pass combined execution and visual acceptance, meeting the repository's compact-case repetition threshold. Dense-poster parity is still unproven.

## Validation and reproduction

All 111 renderer and placement tests pass: 27 classic, 43 editorial, 19 family-baseline, 9 chronology-note and 13 context tests. All 42 deliberate mutations are detected: 19 genealogy, 9 institutional and 14 chronology. All three source-backed Chromium audits and the desktop/mobile, fit/zoom and image-aspect gallery checks pass. The complete posters retain crossing counts of 16, 63 and 0 respectively. Quick skill validation and all 14 Pi-harness tests pass.

Pattern IDs, repository structure, skill independence, payload and diff checks pass. The Pages build produces 639 files / 41.75 MiB. Local synchronization copies 12 changed files and preserves other local files. The standard commands are `uv run --script scripts/validate-pattern-ids.py`, `validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`, `build-pages.py` and `sync-local-skills.py`, with the same `scripts/` prefix for each filename.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_family_baselines.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/scripts/test_context_landmarks.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/verify_genealogy_revision.py --before 5720173d --output projects/usefulcharts-style/artifacts/reviews/nameplates-final-facts.json
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/nameplates-final-gallery
uv run --script projects/usefulcharts-style/scripts/compare_posters.py --repository . --before-revision 5720173d --artifacts projects/usefulcharts-style/artifacts --after-prefix nameplates-final --comparison-name nameplate-composition-comparison --before-label "Previous focal-people revision"
uv run --script projects/usefulcharts-style/scripts/summarize_nameplate_revision.py
```

For each canonical ID (`aurelian-families`, `atlas-of-inquiry`, `five-regional-histories`):

```powershell
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --report projects/usefulcharts-style/artifacts/reviews/nameplates-final-<id>-browser.json --png projects/usefulcharts-style/artifacts/images/nameplates-final-<id>.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --artifacts projects/usefulcharts-style/artifacts/reviews/nameplates-final-mutations/<id>
```

Run fresh workspaces for any repetition; preserve the recorded ones:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-nameplate-composition.md --model openai-codex/gpt-5.5 --mode json --strict --run-id <fresh-family-id> --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-emphasis-contract.md --mode json --strict --require-exact-command-from-prompt --run-id <fresh-contract-id> --expect-output draft.json --expect-output result/source.json --expect-output result/placement.json --expect-output result/poster.svg --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script evaluations/contracts/verify-usefulcharts-nameplate-composition.py evaluations/runs/<fresh-family-id> --output evaluations/runs/<fresh-family-id>/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<fresh-family-id>/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
```

## Delivery state

Implementation `702939483a424dbf625840a74842562b768a71e4` is committed and published on `main`. [Pages workflow 34683860843](https://github.com/gvillarroel/skills/actions/runs/34683860843) completed successfully, including its diagram-coverage, generated-output boundary and unified Pages checks. Independent HTTP verification compared all eleven gallery, manifest and poster files with their complete expected committed bytes after the standard Pages metadata and whitespace transformations; all match. The main examples catalog still links the gallery. Local evidence: `projects/usefulcharts-style/artifacts/reviews/nameplate-composition-publication-verification.json`.

The revised [Aurelian genealogy](https://gvillarroel.github.io/skills/examples/usefulcharts-style/aurelian-families.html) is available at the existing route, with the complete editable source and SVG. The [three-poster gallery](https://gvillarroel.github.io/skills/examples/usefulcharts-style/) retains the institutional and chronology examples. Delivery of this revision does not complete the full quality-and-composition objective; the skill remains in `validating` with the specific visual gaps described above.
