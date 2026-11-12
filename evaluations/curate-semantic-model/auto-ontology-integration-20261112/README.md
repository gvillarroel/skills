# NVIDIA-informed semantic skill experiments

Date: 2026-11-12. Outcome: retain the existing three skill bundles. The strongest
curation variant reached 4/4 in development but only 3/4 in its physically fresh
public replay, below the frozen 4/4 release gate. Private validation was never
released and made zero task-model calls. No rejected candidate replaces a
published skill.

The [machine-readable native aggregate summary](native-aggregate-summary.json)
projects the owning `harbor-run-results` reports without rescoring trials.
It includes all 21 completed model-job rows, their report SHA-256 commitments,
native counts/rewards/resource metrics, fairness basis and the failed schema 2
trace-development gate. Raw task outputs, private datasets, traces and local
paths are excluded.

## Question and execution profile

Can NVIDIA Auto Ontology's catalog/interchange boundaries suggest more reliable
curation, reviewed glossary construction and ontology-guided extraction?
The preceding [pinned upstream feasibility audit](../auto-ontology-20261112/README.md)
identified omissions of aliases and certification flags during `ModelTerm`
interchange, and unstable fresh IDs unless existing identities are supplied.
Those are structural observations, not model extraction scores.

This follow-up uses native Harbor 0.18.0, Pi 1.4.0 and
`github-copilot/gpt-6-luna`, thinking low. Luna is the user's explicit override
to the repository's usual forward-test model. Each job has two public tasks
with two attempts each, one trial per job, at most two jobs simultaneously,
300 s agent and45 s verifier, one CPU and1536 MB memory. The pinned task image is
`sha256:728764f2e22fb52ed9c241960e14601c5c6d7b8517e1822cbbc2cb36d0b015d6`.
All six retry settings are locked; max_retries=0. Source/task/model/skill locks,
native artifacts and mandatory rewards are checked by the owning reporter.

The runtime stages exactly one skill, disables ambient context and sibling
skills, checks unchanged skill/task input bytes, and uses a separate verifier
container. Actual mount and denial probes cover host/private/test/memory/socket
exposure. Provider network is required. Separate curator/peer contexts and
filtered metadata provide procedural host blinding under a trusted shared
account; this is not an OS-denied boundary against a malicious coordinator.

## Native results

Each cell is qualified native executions /4, followed by strict execution
errors. Errors remain failures even if an archived artifact happens to be right.
The tasks measure the complete explicit output contract, including provenance
and delivery paths; these are not general ontology-accuracy percentages.

| Target | Fresh baseline | Evaluated development variants, in execution order | Frozen public replay | Decision |
| --- | --- | --- | --- | --- |
| `curate-semantic-model` |2/4;0 errors |v1=3/4;1 error, v2=3/4;0, v3=2/4;0, v4=3/4;0, v5=4/4;0, v6=3/4;1, v7=3/4;0, v8=2/4;1 |v5=3/4;0 errors |Reject v5 release; retain baseline |
| `extract-ontologies` |4/4;0 errors |v1=4/4;0, v2=2/4;2, v3=3/4;1 |unchanged baseline=4/4;0 errors |Three nonimproving variants; retain baseline |
| `extract-with-ontology` |2/4;0 errors |v4=3/4;0, v5=1/4;3, v6=2/4;0, v1=2/4;0 |unchanged baseline=3/4;0 errors |Three nonimprovements after v4; v4 below admission gate; retain baseline |

Guided v2/v3 were prepared but not executed; they are not counted as trials.
Curation v6/v7/v8 supply the three consecutive nonimprovements after v5 required
by the user. All three are larger prose extensions with the same helper; they
test output-coverage closure, source authority/dependency review, and
counterfactual checking. The fixed ranking prefers qualified correctness,
qualified repeated-case agreement, validated deterministic capability, fewer
errors, smaller source changes, then the earliest immutable variant ordinal.

There are 84 physical native task-model attempts in this corrected study portfolio:
12 baseline +60 exploratory +12 final replay. Study 4 results imported into study 5
are the same physical attempts, not new samples. An earlier 12-attempt diagnostic
instrument was retired and is excluded from these comparisons; it remains
recorded locally. Curator/reviewer coordination is outside this scored task-model
denominator. No private task-model outcome was used for selection or tuning.

## What helped, and what did not qualify

The best development curation variant puts a per-ID, per-property inventory
directly in the entrypoint: compare complete authoritative and projected records,
including review and provenance properties, before deciding which differences
affect meaning. This narrowed a repeated omission seen in the baseline. However,
its fresh replay still omitted a certification-property projection loss in one
attempt. The new selected bundle therefore fails the required public gate.

The bundled projection auditor was not consistently invoked in the broad
curation trials. Do not attribute the observed development gain causally to
that helper. Additional layers of prose did not improve the winner. Several
variants introduced strict failures while trying an unavailable `python` alias;
the task image provides `python3`. These errors are retained, not relabeled as
external model failures.

The guided baseline sometimes writes otherwise plausible output under a
different directory than the explicit requested artifact. Missing the required
path is a legitimate delivery failure. Unarchived wrong-path content is not
assumed semantically correct. Its unchanged final replay improving from 2/4 to 3/4
also demonstrates run-to-run variance without any skill change.

## Repetition and correctness

Repeated-task analysis reads actual archived final files. It does not return a
gold hash when a verifier passes. Curation v5 has 2/2 qualified equal model pairs
in development, but only 1/2 in the final replay. The replay's selected semantic
fact view matches in both pairs, while a review-property omission makes one
complete report wrong. Equality of a selected model view is therefore weaker
than qualified correctness of the complete artifact.

The [separate sanitized artifact-inspection receipt](repeatability-inspection-summary.json)
copies the repetition summaries and binds the inspector and source receipts by
SHA-256. The curation fact view includes only `semantic_changes` and
`unchanged_ids`, dropping evidence; it excludes `projection_losses` and
`review_changes`. Direct inspection of the two archived public reports confirms
the one differing top-level section is `projection_losses`, with one omitted
`description_certified` loss. This decomposition is an independent artifact
inspection, not a claim made by the native reward reporter and not a complete
semantic-model comparison.

The unchanged authoring final replay has 2/2 qualified matching pairs; guided has
1/2. Missing artifacts never establish agreement. Report/model views are kept
separate. These are fixed authored cases, not evidence that unrestricted
ontology learning always creates the same correct graph.

## Test and gate quality

Public task/verifier preparation includes 42 general and19 targeted deterministic
controls; these are verifier controls, not61 model ontology cases. The final
private preparation receipt has an independently checked native Oracle 6/6,
valid alternative and wrong-source/locator/value/qualifier controls. A suspected
stale-output cause was disproved: two separate verifier images needed their
declared nested source root. The actual source, oracle and verification rules
were preserved. No evaluated task-execution model saw those private tasks;
the independent curator and reviewer inspected them during preparation.

A later read-only [required-reward audit](../../audit-catalog-projection/unused-validation-readiness-20261112.json)
finds that this six-task Oracle emits only the primary `reward`, omitting the
separately required `artifact_gate` in all6cases. The6/6 label is primary-only,
not a complete gate qualification. The cohort remains unconsumed and is marked
NOT_READY for any future model study until an append-only instrument correction
and full reward-interface preflight. Neither its roots nor original scores are
edited. The broad candidate's failed public replay independently prevents promotion.

The append-only studies retain retired drafts, failed native packaging checks,
all completed native jobs and the unsuccessful final gate. The organizer
verifies the closed study ledger and sources; trace distillation independently
rejects the frozen candidate with 3/4 qualified fresh attempts, required 4/4,
zero execution errors, verified locks and distinct attempt IDs. Its private
gate remains `not-evaluated` because development did not pass.

## Deterministic capability and next boundary

The new explicit-contract auditor passes 49 unit tests, independent additional
CLI controls and an actual unchanged NVIDIA `ModelTerm` conversion probe.
That probe has two same-label records and ten selected source field values:
four preserved and six omissions, all reported. Two audit reports are byte
identical. It checks structural field preservation, with semantic_status always
`not_checked`; it does not establish natural-language equivalence or logical
consistency. No NVIDIA service, SQL database, full crawler or embedding model
was needed for these controls.

A [separate fixed-capability qualification](../../audit-catalog-projection/qualification-20261112.md)
tests this bounded operation as its own skill. Its result cannot rescue this
failed broad-skill gate. Selected fields/identity bridges remain an explicit
contract, and fields outside that scope remain outside the claim. The local
JSON field-view hashes are not an RFC8785/JCS interoperability implementation.

## Limits

The broad pilot has six public task worlds, two per target. Repeated attempts,
variants, verifier mutants and unit controls do not increase independent source
breadth. No significance claim, global best-skill ranking, ten independent
correct ontology-authoring cases, OWL consistency claim or exhaustion of OSS
alternatives follows. More complete documents, real pull requests, multilingual
definitions and varied independent sources remain open research directions.

Native baseline digests: curation
`sha256:44005570c4d357f87c526d9190684c9654471d813ad7a467cf81795c37f5d084`,
authoring
`sha256:2f1ec4596317086169f88c5dce5ceaa200f57409b7c2e980155d75643c45f738`,
guided
`sha256:adc1c9f0f1e15b87dce24bd969e02520dd75d6a4e7f4b6dcf0837a208cd4f56e`.
Rejected curation v5:
`sha256:e58a70c28c3eb0a38e5b29ca2b3b8189e99562b92239de12a6c7468517b01a5f`.
