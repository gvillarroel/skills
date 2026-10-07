# Lucidchart SVG compatibility and presentation revision — 2026-10-07

## Objective and scope

Research which Lucid elements best represent transformed diagrams. Encode documented, repeatable choices in scripts; keep semantic and rendering judgments in compact references. Preserve artwork, topology and native editing as separate outcomes. This revision does not infer arbitrary SVG graph meaning or promise lossless round-tripping.

The frozen runtime has 21 files, SHA-256 `0e4d5c69add73792b268cb0890edbb48d39c573e1fdb9a908ba017ad50679f93`. Normal use invokes helpers and reads compact references. The extractor is 57,223 bytes; its source is not normal runtime reading. Query the 45KB catalog through its compact CLI.

Keep the skill **validating**: authenticated SVG download, formal custom-SVG insertion and Standard Import parser/render/native-edit acceptance remain unverified. Saved Mermaid/editor evidence and local packages do not establish those routes. Research and local validation can be complete while service acceptance remains open.

## Requirement audit

| Requirement | Encoded checks | Judgment and boundaries |
| --- | --- | --- |
| Choose compatible elements |63 documented types;327 freshly verified cloud classes; required/nested property contracts | Formal notation needs explicit roles; geometry and colors do not assign semantics |
| Preserve supported styles | Stroke width/style, rounding, rotation, opacity, safe typography/emphasis, stack, groups/layers and page controls | Font metrics, wrapping, native outlines and substitutions require rendering |
| Preserve relations |22 endpoint markers; shape/absolute/line endpoints, straight joints/elbow turns/curved family, smart attachment, multiple positioned labels | Cardinality, parent/whole and navigation roles are supplied; exact Bézier/dash/marker artwork is not certified |
| Resolve SVG geometry | Explicit user-space/viewport modes; root aspect alignment, ordered positive transforms, independent contour/port checks | Unsupported transforms, CSS/responsive geometry and nested viewports require normalization or artwork fallback |
| Disclose incompatible details | Per-source ledger and refusal; no graph for incomplete mapping | Rich artwork, gradients, masks/clips, filters, images, animation and text paths use asset/hybrid guidance |
| Generate appropriate families | Checked org/mind-map records, supplied sequence markup and assisted-layout selection | Lucid computes dimensions/routing; grammar and editing need service verification |
| Qualify vector/export fidelity | XML/resource inventory, SVG-only counts, literal whitespace/definition/hidden contexts, byte-preserving copies | XML preflight does not establish rendering/native eligibility; custom vector insertion differs from drag/drop and SI PNG conversion |
| Improve presentation | Explicit routes/ports, labels, tables, lanes/containers and source page controls | Preserve reading order/palette; check full labels, overlaps, heads and crop; redesign only when requested |

Transferable guidance is inside the skill in `shape-selection.md`, `diagram-families.md`, `svg-mapping.md`, `native-reconstruction.md`, `generated-layouts.md` and `fidelity.md`. Detailed research stays outside runtime: [shape evidence](../../projects/lucid-svg-best-practices/reviews/shape-evidence.md), [style evidence](../../projects/lucid-svg-best-practices/reviews/style-evidence.md), [SVG mapping evidence](../../projects/lucid-svg-best-practices/reviews/svg-mapping-evidence.md), [extractor validation](../../projects/lucid-svg-best-practices/reviews/extractor-validation-20261007.md).

Primary sources cover Lucid primitive, flowchart, BPMN, container/table and four cloud libraries; shapes, lines, groups/layers, pages, data-backed types and collections; official ER/UML/lane/BPMN converter examples; current export/custom-library support; and W3C SVG coordinate, text and painting contracts. Dated URLs/conflicts are in the catalog and references. Ambiguous Azure 2021 classes and undocumented example-only fields are blocked. The scripts implement a conservative documented profile, not the complete live schema.

## Deterministic and visual validation

122 test methods pass:23 inspector,26 native,10 catalog,47 extractor and 16 generated-layout tests. Catalog tests iterate all 63 types/327 classes; native tests exercise all 22 markers at both ends and retain exact legacy package bytes. Fixtures cover BPMN properties, table merges, provider defaults, cardinality labels, elbow turns, groups/layers and explicit pages. Generated boundaries include exactly 4000 items, exactly 50000 markup characters, byte caps and hierarchy failures.

```powershell
uv run --script skills/lucidchart-svg/scripts/test_svg.py
uv run --script skills/lucidchart-svg/scripts/test_native.py
uv run --script skills/lucidchart-svg/scripts/test_catalog.py
uv run --script skills/lucidchart-svg/scripts/test_extract.py
uv run --script skills/lucidchart-svg/scripts/test_generated.py
uv run --script projects/lucid-svg-best-practices/scripts/smoke-contracts.py
```

Cross-review repaired dropped root opacity, rounded-corner attachments, transformed-marker assumptions, huge JSON integer overflow, actual page-ID collisions, bytecode/resource mutation, hard-link aliases and nonfinite viewport diagnostics. Retain the intermediate 46/47 extractor failure; frozen tests are 47/47. An initial project fixture incorrectly repeated endpoints as elbow controls; the corrected contract uses interior turns. No agent trial artifact was repaired or replaced.

The naturalistic oracle resolves root 300×200/viewBox 100×100 default meet to scale 2 and offset 50: request `(60,20,40,60)`, audit `(180,20,40,60)`, endpoints `(100,50)`/`(180,50)`, font 5→10px, audit-only dashed border and rounding 8. Marker/dash classes and text placement retain adaptation notices. Read-only browser AX/screenshot inspection of the source showed both shapes, all three labels, correct border attribution and the connecting line. This is source evidence, not simulated Lucid output or a pixel-fidelity score. The browser bridge does not expose SVG getBBox; attempted measurement was not used. Temporary tab/server were closed.

## Isolated forward tests

Model: `openai-codex/gpt-5.6-luna`, high thinking, the recorded evaluation-only exception after Spark provider rejection before tools. Strict JSON, exact outputs, zero tool errors, observed model, immutable payload and clean reads are unchanged. Runtime copies exclude examples/dependencies and are read-only.

```powershell
uv run --script scripts/run-pi-skill-eval.py lucidchart-svg --prompt-file evaluations/pi-prompts/lucidchart-svg-best-practices-<case>.md --model openai-codex/gpt-5.6-luna --thinking high --mode json --strict --run-id <run-id> --expect-output <each-required-path>
uv run --script evaluations/lucidchart-svg/validate_best_practices.py <case> evaluations/runs/<run-id>/workspace --report evaluations/runs/<run-id>/independent-artifacts.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/<run-id>/read-surface.json
```

Contract adds `--require-exact-command-from-prompt`; naturalistic/generalization workflows stay open. Exact paths are defined in the [new prompts](../pi-prompts/lucidchart-svg-best-practices-contract.md). Boundary reuses [the original prompt](../pi-prompts/lucidchart-svg-boundary.md) and independent oracle. The final frozen cohort passes all eight strict and independent gates; direct narrative/trace review is recorded below. Earlier snapshots are not pooled.

## Retained evaluator repairs

The pre-guard candidate used payload `7804681c9c0e712fb4f865c57cebb1a7632a7378636c100f25bab24ff99ff80e`. Its positive contract/naturalistic/generated cohort passed seven joint cases, while boundary-luna-1 produced a correct diagnosis but failed the strict zero-error gate after an unnecessary extraction on a resource-blocked source. This workflow failure is retained. The entry point and extraction reference now stop at existing preflight blockers; the final eight-case cohort reruns every case under the new payload rather than pooling old passes.

Contract-luna-1 emitted the correct package/JSON/report and executed the exact command with zero tool errors. Strict event checking failed `no-fenced-command-in-prompt` because the evaluator used a PowerShell fence while the harness recognizes shell blocks. This is an evaluator-design failure, retained before a fresh contract-luna-2 with a Bash fence. Skill payload did not change.

The parent's initial inference that naturalistic-1 omitted a newline was disproved by its actual bytes/trace: it has LF and 1057 bytes. The 1058-byte project smoke source had CRLF from Windows writing. The fresh `smoke-lf` fixture matches the prompt. The independent oracle uses UTF-8/LF bytes and does not normalize/rewrite trials.

## Final frozen cohort and repository gates

All eight final strict, independent artifact and read-surface checks pass on the 21-file digest above. Run IDs use prefix `20261007-lucid-svg-best-final-`:

| Case | Run suffixes | Final checks |
| --- | --- | --- |
| Rich native contract | `contract-luna-1` | Exact command, package/JSON equality, literal text, native fields, memberships and cloud defaults |
| Boundary | `boundary-luna-1` | Existing blocked preflight, no unnecessary extraction, no fabricated graph or remote success |
| Naturalistic SVG conversion | `naturalistic-luna-1`, `-2`, `-3` | Exact source bytes, geometry, page, border attribution, typography, marker/dash notices and attached ports |
| Generated-family generalization | `generalization-luna-1`, `-2`, `-3` | Literal records/markup, hierarchy counts, all four layouts, explicit reflow and live-acceptance limits |

The independent evaluator also rejects all 16 mutations of separate smoke copies, including wrong letterboxing, both borders dashed, dropped labels, altered cells, forced cloud styles, detached endpoints, changed parents/markup, inflated counts, finite crop, report disagreement and ZIP mismatch. Original agent outputs remain untouched. The project's `run-final-cohort.py` records every command/exit and manifest under ignored artifacts; per-run independent/read/manual review JSON remains outside each isolated workspace. The [independent forward review](../../projects/lucid-svg-best-practices/reviews/forward-review-20261007.md) records all eight manual passes, their evidence boundaries and two nonblocking observations.

Repository pattern-ID, skill, independence and payload validators pass. `git diff --check` passes with ordinary CRLF normalization notices. The default local sync copied 18 changed source-owned files; its check verifies all 10,396 canonical sources and bundle validation. No new Pages example set or source catalog was added, so a Pages build is not required for this runtime-only change. Existing unrelated ECharts/source work remains outside the skill commit.

The initial testing preview was published as `a52e2b58982fe72797e335d7840ce1d65e4f2f1a`; remote content matched and Pages workflow 37655590879 succeeded. The researched revision is committed/pushed separately after these gates. Live service acceptance remains pending; no local pass changes that boundary.
