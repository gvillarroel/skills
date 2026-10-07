# Lucidchart SVG best-practice forward review — 2026-10-07

The final frozen cohort passed **8 of 8 joint checks**: strict isolated runtime validation, independent artifact oracles, read-surface validation, and manual narrative/trace review. No final-cohort candidate needed an artifact repair. All eight runs used the runtime-only, 21-file skill payload with SHA-256 `0e4d5c69add73792b268cb0890edbb48d39c573e1fdb9a908ba017ad50679f93` and observed model `gpt-5.6-luna` through `openai-codex`.

The cohort contains one explicit rich native contract, one resource/authentication boundary case, three metadata-bearing SVG reconstruction trials, and three generated-family trials. Each fresh workspace contained only the evaluated skill and task inputs. Strict validation required the exact requested output paths, valid event JSON, the observed model, zero tool errors, an unchanged skill payload, and a clean runtime read surface. The contract case also required the prompt's exact compilation command.

| Final run | Artifact oracle | Manual notes and trace | Skill reading |
| --- | --- | --- | --- |
| [contract-1](../../../evaluations/runs/20261007-lucid-svg-best-final-contract-luna-1/manual-status-review.json) | Passed | Passed | Entry point only |
| [boundary-1](../../../evaluations/runs/20261007-lucid-svg-best-final-boundary-luna-1/manual-status-review.json) | Passed | Passed | Entry point only |
| [naturalistic-1](../../../evaluations/runs/20261007-lucid-svg-best-final-naturalistic-luna-1/manual-status-review.json) | Passed | Passed | Entry point and three conditional references |
| [naturalistic-2](../../../evaluations/runs/20261007-lucid-svg-best-final-naturalistic-luna-2/manual-status-review.json) | Passed | Passed | Entry point and three conditional references |
| [naturalistic-3](../../../evaluations/runs/20261007-lucid-svg-best-final-naturalistic-luna-3/manual-status-review.json) | Passed | Passed, with minor wording observation | Entry point and six conditional references |
| [generalization-1](../../../evaluations/runs/20261007-lucid-svg-best-final-generalization-luna-1/manual-status-review.json) | Passed | Passed | Entry point and generated-layout reference |
| [generalization-2](../../../evaluations/runs/20261007-lucid-svg-best-final-generalization-luna-2/manual-status-review.json) | Passed | Passed | Entry point and generated-layout reference |
| [generalization-3](../../../evaluations/runs/20261007-lucid-svg-best-final-generalization-luna-3/manual-status-review.json) | Passed | Passed, with minor trace observation | Entry point and three conditional references |

## Independent artifact evidence

The evaluator-owned [best-practice validator](../../../evaluations/lucidchart-svg/validate_best_practices.py) imports no skill implementation. Its fixture values come from the prompts and a manual SVG coordinate oracle. It checks exact original bytes or JSON values, ZIP integrity and equality with the separately delivered document, declared native objects and attached endpoints, literal text, supported styles, type-specific properties, table merges, routing and markers, group/layer membership, named-library default styling, generated records/markup/layout fields, counts, and consistency between structured reports and emitted objects. Narrative content was reviewed manually; no keyword or report-prose matching determines the result.

The SVG fixture is 1,057 UTF-8 bytes with its final LF, SHA-256 `9a75c5289598f8c04ddf9d0d14d646f742bf382ce5caa94feea9b1c73592f328`. Default centered `meet` maps the 100-square viewBox into the 300×200 viewport with scale 2 and horizontal translation 50. Composing the outer `translate(5 0)` produces the manually checked boxes `(60,20,40,60)` and `(180,20,40,60)`. All three trials retain the solid Request border, dashed Audit border, literal labels, page extent and connector attached to the source's right port and target's left port. Their ledgers disclose dash-pattern, marker and text-layout adaptations and font uncertainty.

The rich contract preserves BPMN activity properties, literal markup-sensitive labels, the table header merge, interior elbow turns, relationship markers and multiplicity labels, grouping/layer membership, and the exact AWS class. Unspecified named-shape fill, stroke and text formatting remain omitted. Generated-family trials preserve collections and the four layout declarations exactly, including parent keys and sequence markup; the two hierarchy families each retain three items, one root and two relationships. Their pages remain infinite and their notes assign geometry to Lucid.

The boundary trial reports authenticated export and native reconstruction as incomplete, identifies the external image and foreignObject/XHTML dependencies, and explains the missing topology. Its trace executes only source inspection. Blocked preflight causes no extraction command, no tool error and no fabricated native graph or package.

The evaluator was separately tested against 16 copied-artifact negative controls; every deliberate corruption was rejected. These cover byte identity, coordinate mapping, styling, literal labels, merges, cloud defaults, endpoint attachment, routing, parent/data/markup identity, generated clipping/counts, structured-report equality and ZIP equality. The original trial artifacts were untouched; local evidence is retained in [the negative-control report](../artifacts/reviews/evaluator-negative-controls.json).

## Read surface and manual findings

No final run reads skill script source, the large extractor source, acceptance examples, project evidence, sibling skills or repository instructions. The entry point read is 7,249 bytes. Conditional references are 3,777–10,228 bytes; the largest is just under 10 KiB. Naturalistic-3 reads the broadest reference set, while the other tasks follow narrower paths. Full shell commands were reviewed in the event records rather than relying on the summarizer's truncated command strings.

Two minor observations do not invalidate the artifact results. Naturalistic-3 explains the correct root viewBox formula and lists the correct native boxes but does not explicitly say that the outer group translation is composed before that formula. Generalization-3 lists the bundle's filenames after reading the entry point; the inventory adds a step without reading extra source contents. Both observations are retained in their per-run manual reviews.

All eight English notes distinguish local compilation/inspection from live results. They disclose font/layout, marker, dash, parser or generated-geometry limits relevant to their case. None claims a completed remote document, measured visual equivalence or an overall preservation percentage.

## Evidence boundaries

This cohort establishes the tested local artifact and agent workflows. It does not establish Lucid-side schema acceptance, provider icon appearance, font availability, text metrics, interactive editability, connector following, generated reflow, sequence grammar acceptance or end-to-end export fidelity. Those require authenticated service execution and rendered/manual checks. Repeated trials use the same public fixtures; they are repeatability evidence rather than disjoint holdout coverage.

Per-run `manual-status-review.json`, `independent-artifacts.json`, `read-surface.json`, event records and manifests are stored beside each isolated workspace under ignored `evaluations/runs/`. The final machine cohort index is retained locally at [final-cohort.json](../artifacts/reviews/final-cohort.json). The durable summary preserves conclusions without promoting those bulky artifacts into the skill bundle.
