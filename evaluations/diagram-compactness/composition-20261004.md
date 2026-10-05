# Composition, 3D, and explainer compactness validation — 2026-10-04

## Scope and behavior

Updated canonical diagram-composition, compose-synchronized-svg, threejs-animated-3d, and hyperframes-explainer bundles. Connected conceptual diagrams now start with the smallest readable footprint and make at most two focused compaction revisions, retaining the tightest passing version. Fonts, arrowheads, terminal runs, explicit endpoints, distinct route lanes, and all animation/camera envelopes constrain compaction. Quantitative charts keep domains, axes, legends, encodings, and information density; physical 3D scenes retain physical scale.

The diagram-composition template margin changed from 28 to 20 and gap from 32 to 24. Its 1200×760 canvas is an initial budget when no dimensions are requested. Explicit output dimensions remain binding.

The synchronized SVG compiler now reserves gutter space according to competing relationship traffic. Sparse layouts retain 24 units, the workshop's three relationships receive 40, and the eight-route boundary receives 80. The implicit dependency renderer allocates unique lanes to adjacent and skipped edges, keeps full arrowhead approaches, and adds local crossing gaps away from arrowheads. It wraps complete concept names into spare card height at the existing font size, and refuses an allocation that cannot fit them. Workshop network card width changed from 188 to 160.296 units at the same 58-unit height, about 14.7% less card area, while labels increased from 10 to 12 units. This comparison does not imply a universal density target.

Repeated isolated attempts revealed that bare Python lacked Pillow despite the browser auditor's uv environment. The bundle now includes a uv/Pillow module-crop helper, linked from its runtime workflow. It captures actual-size compact-plan module crops without upscaling, rejects mismatched/world screenshots and unsafe IDs/input overwrite, and keeps generated crops outside the skill bundle. World plans retain the browser auditor's camera-anchor crops.

All four bundles meet the prescribed contract and natural-repetition policy for this update. The synchronized compiler also passes boundary/recovery validation. Fifteen of 17 final strict runs pass; the two agent failures remain recorded, and all 17 final artifacts independently pass browser checks. This does not erase the synchronized composition backlog's pre-existing broader validation history.

## Frozen payloads and model

All release runs used runtime payloads, read-only copied bundles, ambient-context/discovery exclusions, exact required outputs, JSON event traces, and strict gates. Acceptance examples and dependency directories were excluded. Root recorded the openai-codex/gpt-5.6-luna exception in the backlog after gpt-5.3-codex-spark was rejected by the account before any tool use. The strict policy was unchanged.

| Skill | Runtime payload SHA-256 |
|---|---|
| diagram-composition | 31323f522f383e52b8a044361ca66bc4bec53c7d3495c95514b271c81bbe1abe |
| compose-synchronized-svg | 0a9a2569788d25a6e883130fddc2092b24c3b2603b89f03a880f721f7c3ce532 |
| threejs-animated-3d | 5eb72758f96c4a7c3421f14b2ef3001ced4b236e2e030ab03f473c82d030cbc4 |
| hyperframes-explainer | c049fe584ba57efbf312cdab2f50843c13b7069db32cca1fe1352cc78388b9eb |

Full manifest, command, source/prompt hashes, expected paths, integrity reports, raw traces, generated assets, reviews, and screenshots are retained under evaluations/runs/<run-id>/. Source-changing development cohorts are retained separately and are not release evidence.

## Prompts and exact outputs

The following versioned prompts are byte-for-byte copies of the prompts used in the corresponding release manifests:

| Skill | Contract | Natural | Required artifact paths |
|---|---|---|---|
| diagram-composition | [contract](../pi-prompts/compactness-composition-diagram-contract.md) | [natural](../pi-prompts/compactness-composition-diagram-natural.md) | out/brief.json, out/plan.json, out/figure.svg, out/audit.json, out/preview.png, out/review.md |
| compose-synchronized-svg | [contract](../pi-prompts/compactness-composition-compose-contract.md) | [natural](../pi-prompts/compactness-composition-compose-natural.md) | out/brief.json, out/plan.json, out/atlas.svg, out/static.json, out/audit.json, out/preview.png, out/review.md |
| threejs-animated-3d | [contract](../pi-prompts/compactness-composition-threejs-contract.md) | [natural](../pi-prompts/compactness-composition-threejs-natural.md) | out/field.html, out/audit.json, out/preview.png, out/review.md |
| hyperframes-explainer | [contract](../pi-prompts/compactness-composition-hyperframes-contract.md) | [natural](../pi-prompts/compactness-composition-hyperframes-natural.md) | out/model.json, out/scene.json, out/mechanism.svg, out/assets.json, out/project/index.html, out/audit.json, out/preview.png, out/review.md |

The [compose boundary/recovery prompt](../pi-prompts/compactness-composition-compose-boundary.md) adds out/crowded-plan.json and out/rejection.json. The prescribed 24-unit advanced plan must refuse eight competing routes; the same semantic relationships are then compiled from a brief with adequate separated lanes. Expected rejection is captured from stdout and asserted inside a successful command; a refused compose does not emit the optional report.

Command pattern, with one repeated --expect-output for every artifact in the table:

    uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/compactness-composition-<case>.md --mode json --strict --run-id <run-id> --model openai-codex/gpt-5.6-luna --expect-output <artifact> --timeout-seconds 900

Each run's run-manifest.json retains the complete expanded command and exact list. Read-surface checks used:

    uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error

## Release outcomes

All run IDs below begin with 20261004-composition-compactness-.

| Skill/case | Run suffixes | Strict outcome | Independent artifact outcome |
|---|---|---|---|
| diagram contract | diagram-contract-luna-1 | Pass | Browser pass, visible arrowheads/shafts and attached endpoints |
| diagram natural | diagram-natural-luna-1, -2, -3 | 3/3 pass | All three browser pass; delivery-size visuals inspected |
| ThreeJS contract | threejs-contract-luna-1 | Pass | Offline browser pass, visible vector heads/shafts |
| ThreeJS natural | threejs-natural-luna-1, -2, -3 | 3/3 pass | All three responsive/replay/pointer browser checks pass; delivery-size visual inspected |
| Hyperframes contract | hyperframes-contract-luna-1 | Pass | Browser mechanism/envelope/seeking pass |
| Hyperframes natural | hyperframes-natural-luna-1, -2, -3 | 2/3 pass | All final artifacts independently pass; repetitions 2 and 3 visually inspected |
| Compose contract | compose-complete-label-contract-1 | Pass | 229/229 independent browser checks and actual-size visual pass |
| Compose boundary/recovery | compose-complete-label-boundary-1 | Pass | Narrow 24-unit plan rejected; recovery with an 80-unit gap passes 229/229 independent browser checks and actual-size visual inspection |
| Compose natural | compose-complete-label-natural-1, -2, -3 | 2/3 pass; repetition1 retains strict read-offset failure | All three independent browser98/98 and actual-size visual pass; repetitions2 and3 are joint passes |

Hyperframes natural repetition 1 is an agent/wrong-output-path failure: it first created out/assets/mechanism.svg instead of out/mechanism.svg. It subsequently copied the correct artifact, but the strict tool-error failure remains a failure. This was not a BOM or infrastructure error.

Compose contract-release-1 is an infrastructure failure: Windows cygheap child-copy error 299, spawn UNKNOWN, and a failed pwd process occurred before successful generation. The same unchanged intermediate payload passed contract-release-2. Compose natural-release-1 crashed with Node semi-space allocation failure and pi exit 134, followed by Python MemoryError in harness integrity collection. Natural-release-2 had Python MemoryError writing its captured trace. Neither infrastructure attempt is counted toward a natural-quality cohort. Infrastructure retry 1 passed strict and browser checks, but manual review found truncated network labels, so its output was a quality failure. Retry 2 was interrupted as superseded development after that finding. All compose release/retry cohorts before complete-label are development evidence for the final payload, not final release passes. Natural-release-3 is an agent failure: white-on-white network labels, temporary unbound success-rate source, and temporary JSON syntax errors. Its final atlas recovered and passes independently; strict failure is retained.

Final complete-label natural repetition 1 is an agent/tool-use failure: it attempted to read offset 240 of the 175-line generated audit report. Its final atlas independently passes browser and delivery-size visual checks, but its strict failure remains part of the final three-repetition cohort.

The original unsupported Spark attempts are retained as threejs-contract-1 and hyperframes-contract-1. Initial compose contract/natural, final, and frozen development cohorts remain under the same prefix. They exposed endpoint, parallel-lane, crop dependency, and rejection-report issues that the final canonical changes address; their successes do not substitute for final-bundle release evidence.

## Independent checks and visual evidence

Auditors were rerun on all twelve diagram/ThreeJS/Hyperframes release artifacts. Each workspace/out/independent-audit.json and independent-preview.png retains the independent result. For synchronized SVG release artifacts:

    uv run --script skills/compose-synchronized-svg/scripts/audit_synchronized_svg.py evaluations/runs/<run-id>/workspace/out/atlas.svg --report evaluations/runs/<run-id>/workspace/out/independent-audit.json --screenshot evaluations/runs/<run-id>/workspace/out/independent-preview.png --compact-report

Final complete-label contract and boundary each passed 229/229 checks, including scenarios, perturbations, zero-flow boundaries, timeline states, arrow occlusion, contrast, metadata and accessibility, with no console/page/network errors. Actual-size preview and network crops were inspected: labels remain separate, heads and terminal runs remain visible, source/target attribution is clear, and chart scale space is retained. The eight-route boundary has separated parallel routes and some perpendicular dotted cross-module crossings without junction dots; local bridge masks cover implicit network crossings. Do not interpret these results as a universal zero-crossing guarantee for arbitrary graph topology.

Deterministic comparison artifacts live at projects/diagram-compactness/artifacts/composition/revised-plan.json, revised-atlas.svg, revised-audit.json, revised-atlas.png, and revised-crops/. The standalone ThreeJS validation lives at the same directory's vector-field.html, vector-field-audit.json, and vector-field.png. The final deterministic full-label recovery lives beside them as full-labels.svg, full-labels-audit.json, and full-labels.png; it passed browser and actual-size visual review. All generated media and bulky raw runs remain ignored.

## Local evidence links

These ignored run artifacts are available in the validation workspace; versioned prompts and this summary remain in git.

| Case | Payload and exact command | Strict result | Independent visual evidence |
|---|---|---|---|
| Diagram natural3 | [manifest](../runs/20261004-composition-compactness-diagram-natural-luna-3/run-manifest.json) | [result](../runs/20261004-composition-compactness-diagram-natural-luna-3/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-diagram-natural-luna-3/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-diagram-natural-luna-3/workspace/out/independent-preview.png) |
| ThreeJS natural3 | [manifest](../runs/20261004-composition-compactness-threejs-natural-luna-3/run-manifest.json) | [result](../runs/20261004-composition-compactness-threejs-natural-luna-3/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-threejs-natural-luna-3/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-threejs-natural-luna-3/workspace/out/independent-preview.png) |
| Hyperframes natural3 | [manifest](../runs/20261004-composition-compactness-hyperframes-natural-luna-3/run-manifest.json) | [result](../runs/20261004-composition-compactness-hyperframes-natural-luna-3/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-hyperframes-natural-luna-3/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-hyperframes-natural-luna-3/workspace/out/independent-preview.png) |
| Compose contract | [manifest](../runs/20261004-composition-compactness-compose-complete-label-contract-1/run-manifest.json) | [result](../runs/20261004-composition-compactness-compose-complete-label-contract-1/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-compose-complete-label-contract-1/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-compose-complete-label-contract-1/workspace/out/independent-preview.png) |
| Compose natural2 | [manifest](../runs/20261004-composition-compactness-compose-complete-label-natural-2/run-manifest.json) | [result](../runs/20261004-composition-compactness-compose-complete-label-natural-2/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-compose-complete-label-natural-2/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-compose-complete-label-natural-2/workspace/out/independent-preview.png) |
| Compose natural3 | [manifest](../runs/20261004-composition-compactness-compose-complete-label-natural-3/run-manifest.json) | [result](../runs/20261004-composition-compactness-compose-complete-label-natural-3/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-compose-complete-label-natural-3/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-compose-complete-label-natural-3/workspace/out/independent-preview.png) |
| Compose boundary | [manifest](../runs/20261004-composition-compactness-compose-complete-label-boundary-1/run-manifest.json) | [result](../runs/20261004-composition-compactness-compose-complete-label-boundary-1/evaluation-result.json) | [audit](../runs/20261004-composition-compactness-compose-complete-label-boundary-1/workspace/out/independent-audit.json), [preview](../runs/20261004-composition-compactness-compose-complete-label-boundary-1/workspace/out/independent-preview.png) |

## Regression commands

The following final source checks passed:

    uv run --script skills/diagram-composition/scripts/test_native_panels.py
    uv run --script skills/diagram-composition/scripts/test_connector_quality.py
    uv run --script skills/compose-synchronized-svg/scripts/test_synchronized_svg_tools.py
    uv run --script skills/compose-synchronized-svg/scripts/test_network_ports.py
    uv run --script skills/compose-synchronized-svg/scripts/test_crop_modules.py --work-dir projects/diagram-compactness/artifacts/composition/crop-tests
    uv run --script skills/hyperframes-explainer/scripts/test_composition.py --work-dir projects/diagram-compactness/artifacts/composition/hyperframes-check

Counts: diagram native panels 13/13; connector quality 21/21; synchronized tools 80/80; network ports 6/6; module crops 3/3; Hyperframes composition 11/11. The network regression proves distinct ports, exact six semantic edges, deterministic body bounds, ≥8-unit local arrow approach, ≥10-unit inter-module terminal runs, separate parallel lanes, adaptive/sparse gutters, six-unit crossing masks at least eight units from arrow tips, full wrapped semantic labels, and explicit refusal of labels that exceed node space. The existing eight-route synchronized regression now compiles a brief rather than assuming an undersized manually allocated plan can fit eight clear routes. The existing dense nine-node fixture now asserts cramped-label refusal, then enlarges only its affected row by 120 units and reruns all original quantitative, overlap, focus, and browser checks.

Targeted validate-skills.py --skill skills/<skill> passed for all four bundles, and targeted git diff --check passed. Root owns final repository validators, independence/payload gates, backlog reconciliation, and local installation synchronization. No published example sources or pattern IDs changed.
