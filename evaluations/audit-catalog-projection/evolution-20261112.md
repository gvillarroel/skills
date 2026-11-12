# Catalog projection invocation evolution

Date: 2026-11-12. **Outcome: keep baseline; no canonical skill promotion.**
The experiment improves public execution of a bounded deterministic
projection auditor from public Harbor traces. The selected minimal variant
qualifies 4/4 development attempts and 4/4 physically fresh replay attempts,
with zero errors and 2/2 raw-identical report pairs in each phase. Independent
private validation did not qualify. The [deterministic component](prototype/README.md)
is released separately for direct use. The complete candidate bundle stays local,
outside Git, and nothing is promoted into `skills/`.

The [frozen invocation protocol](invocation-protocol-20261112.md) defines the
same-skill baseline, exact budgets, ranking, three-consecutive-nonimprovement
stop rule, fresh public replay and one-way independent validation. The original
[fixed-capability pilot](qualification-20261112.md) remains failed and closed;
its private gate was never released.

## Baseline and correction

The initial skill c9a50 produces the correct final audit reports but qualifies
only 3/4executions, because one trace calls unavailable bare `python` before
repairing to available `python3`. Its unchanged later replay qualifies 2/4 with
two similar tool errors. All eight artifact gates are 1; the helper reports
repeat byte-for-byte in all four pairs. These are execution errors despite
correct final files. No environment alias is installed to hide them.

The selected entrypoint adds seven lines directing the agent to resolve a
supported Python3.11+ runner before either helper or wrapper invocation and use
that confirmed runner consistently. The helper,49tests, contract reference,
task inputs, verifiers, model, quotas, retry policy and native executor remain
unchanged. Three larger variants test captured exit/receipt discipline,
unavailable-environment handling and delivery/execution closure.

Native schema2 trace proposals cite four unique public discovery trials spanning
two locked task checksums, including the failure and successful counterexamples.
Materialized candidate bytes match each frozen native source. Analyze-only is
proposal preparation, not a performance qualification or private release.

## Development results

The [public native aggregate summary](invocation-public-summary-20261112.json)
copies the owning report counts, source identities, fairness and resource
metrics. It binds native reports, actual repetition inspections and the fresh
development gate by SHA-256; private data is not read by this projection.

| Variant | Qualified / completed | Strict errors | Qualified raw-identical pairs | Changed files / inserted+deleted lines |
| --- | ---: | ---: | ---: | ---: |
| c9a50 baseline, first whole job |3/4 |1 |1/2 |0/0 |
| v1, confirmed interpreter |4/4 |0 |2/2 |1/7 |
| v2, batch process results |4/4 |0 |2/2 |1/11 |
| v3, unavailable-environment handling |3/4 |1 |1/2 |1/11 |
| v4, delivery/execution closure |4/4 |0 |2/2 |1/11 |
| v1, physically fresh public replay |4/4 |0 |2/2 |1/7 |

The three variants after v1 do not improve it: v2 ties but has more edits,
v3 is worse, and v4 ties but has more edits. This completes the user's three
consecutive nonimprovement stopping rule. The minimal v1 is frozen before any
private feedback. Its source-edit count is seven inserted/deleted lines in one
file. Helper capability is unchanged, and extra instructions alone do not count
as a new capability. Prepared capacity beyond v4 is unused.

The schema2 trace development gate passes the actual fresh public replay with
verified native locks, four unique physical attempts distinct from discovery,
complete required rewards, zero errors and the exact selected digest. The
private gate was then released once. Its full paired outcome is reported only
after all eight validation attempts complete. No failed attempt is replaced.
The first baseline job was specified before viewing the later baseline replay;
all whole diagnostic jobs remain retained without import duplication.

This study accounts for 40 native task-model attempts: 12 imported from the
fixed pilot, 16 exploratory, four fresh public and eight private. Only the latter
28 are new executions. Across the broad study, fixed pilot and this evolution,
there are 124 distinct scored-study task-model executions (84+12+28), without
counting imports twice. An earlier 12-attempt retired diagnostic instrument is
kept separately. Curator/reviewer coordination and deterministic Oracle checks
are outside these task-model denominators. No pooled accuracy is computed.

The v1 digest is
`sha256:a959fccd3eedeeaad160dafcdd006cd00432bb7ad3b37082c396753b934ed9b4`.
Its matched native comparison with baseline c9a50 passes strict lock/trial
fairness. The broader-curator control from the previous pilot is not this
study's baseline and supplies no fair-comparison delta.

## Private result and instrument disposition

The [approved aggregate and append-only audit](validation-aggregate-20261112.json)
bind the original native summary and independent metric-interface finding by
SHA-256. Eight authorized Luna attempts complete once, four per arm, with zero
native retries. The candidate is unchanged after private feedback.

| Private arm | Native primary passes / completed | Verifier failures | Strict errors | Required artifact reward present |
| --- | ---: | ---: | ---: | ---: |
| c9a50 baseline |0/4 |3 |1 |0/4 |
| Frozen v1 candidate |1/4 |2 |1 |0/4 |

These primary counts are diagnostics, not full required-gate qualifications or
ontology-accuracy percentages. One of two candidate semantic-core pairs and one
of two raw helper-report pairs agree. Strict paired native lock/trial fairness
passes and expected skill digests match. The schema2 private gate returns
`keep-baseline`: execution error, incomplete required rewards and insufficient
complete pair agreement. No alternate variant is tested against private results.

Read-only curator/peer audit identifies a **test-interface defect**: both private
verifiers emit only `reward`, while the trace gate additionally requires
`artifact_gate`. All ten inspected Oracle/private-trial reward maps omit that
key, and raw verifier files match native rewards10/10. The canonical Oracle's
2/2 primary successes therefore did not prove the complete required interface
satisfiable; its artifact-gate presence is0/2. This phase cannot certify the
declared full qualification. The candidate independently fails execution and
repetition criteria. No reward alias, rescore, weakened gate or model rerun
repairs the result. The cohort is consumed.

### Startup records

Two initial host launches fail before model execution because the launcher cannot
import the adapter. Each retains four pending, unstarted scaffolds, zero
running/completed/errored/retried trials, null usage/cost, empty logs and no
results/rewards/trajectories. Eight allocated scaffolds are not eight model calls.

The host repair restores the same publicly evaluated import path and verifies
its source hash. Original bound configs and failed trees remain unchanged; one
corrected launch per arm uses a fresh append-only destination. These are the
first eight actual task-model calls under the original budget. The completed-job
external-retry engine is inapplicable to all-pending initialization roots and
is not used. No semantic result is replaced.

### Evaluation guard added afterward

The [required-reward preflight](../../projects/semantic-skill-evaluation/README.md)
checks actual packaged canonical Oracle reports against every required reward
name and threshold before inference. It does not score, repair or authenticate
reports. Six regression controls pass; the real public Oracle passes its complete
reward contract. An independent run against the actual consumed private Oracle's
owning report correctly rejects both missing artifact rewards, while its primary
2/2 status remains unchanged. The [aggregate guard controls](reward-preflight-controls-20261112.json)
bind source/report/peer digests. Zero new task-model or verifier calls are made.
CI now runs these six controls and the prototype's49deterministic regressions.
This correction applies to future studies. The candidate
stays experimental; the three existing semantic skill bundles stay unchanged.

## Independent verification boundaries

The public dataset has two composite tasks and ten scenarios, conservatively
ONE authored family. The private two-task cohort is exactly the unconsumed,
optimizer-unseen cohort from the stopped pilot, with original source ancestry.
It is not renamed into new independent cases. The transfer receipt binds actual
dataset and all task digests and preserves native Oracle, alternative/mutant,
source-bound inspection and isolation evidence. Moderate competency adjacency,
tiny-family, English-only and procedural shared-account blinding remain limits.

The native runtime stages one read-only skill with ambient context disabled,
separate verifier and tested host/private/test/socket/memory denial. Use
Harbor0.18.0, Pi1.4.0 and the user's explicit github-copilot/gpt-6-luna override,
thinking low, retry 0, one trial/job, at most two jobs and the same pinned V3 image.
No model judge scores these artifacts. Private outcomes are returned only after
the complete paired portfolio, with no later mutation or reselection.

The frozen inspector checks actual artifacts and raw contract/report bindings,
preserves typed values, IDs, roles, qualifiers, scope, direction and list nesting,
and distinguishes semantic-core equality from incidental JSON/contract ordering.
Missing/invalid artifacts do not establish agreement. Native correctness and
pair agreement are separate criteria; no gold hash substitutes for observed files.

## Scope

This is reliable invocation and delivery of an existing structural field-audit
engine. It does not improve natural-language ontology truth, infer identities
from labels, prove OWL consistency or qualify arbitrary extraction from text.
Every report keeps semantic_status=not_checked. The other three semantic skill
bundles remain unchanged. Unit, mutant, scenario, native attempt and independent
source-family counts retain their separate denominators.
