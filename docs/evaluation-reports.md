# Skill evaluation reports

Inventory date: 2026-11-12. This navigation page repeats reviewed report outcomes;
it does not rescore native trials or rank unrelated skill profiles. Runtime,
model, task and skill versions belong to each linked report. Installation and
completed tests alone do not establish an improvement.

## Semantic knowledge skills

| Report | Question and evidence maturity | Target skills | Outcome |
| --- | --- | --- | --- |
| [NVIDIA Auto Ontology feasibility audit](../evaluations/curate-semantic-model/auto-ontology-20261112/README.md) | Pinned upstream interchange modules; authored structural controls, no model jobs | `curate-semantic-model`, `extract-ontologies`, `extract-with-ontology` integration feasibility | A local schema-aware comparator satisfies 14/14 controls on one fixture; not extraction accuracy or a skill promotion |
| [NVIDIA-informed skill experiments](../evaluations/curate-semantic-model/auto-ontology-integration-20261112/README.md) | Native Harbor Luna development and fresh public replay,84 physical attempts; private gate unopened | Three existing semantic skills | Retain all three baselines. Curation v5 wins development 4/4 but fails the required 4/4 fresh gate at 3/4. Authoring and guided variants do not qualify for promotion. [Native aggregate data](../evaluations/curate-semantic-model/auto-ontology-integration-20261112/native-aggregate-summary.json) |
| [Fixed projection-auditor qualification](../evaluations/audit-catalog-projection/qualification-20261112.md) | Closed fixed-capability pilot, 12 public native attempts | Experimental `audit-catalog-projection`, broader curator control | Initial skill 3/4 and unchanged replay 2/4; strict errors block release. Cross-skill fair delta is rejected. Private gate unopened. [Native summary](../evaluations/audit-catalog-projection/qualification-native-summary-20261112.json) |
| [Invocation evolution and instrument audit](../evaluations/audit-catalog-projection/evolution-20261112.md) | Same-skill trace evolution, fresh public replay and completed one-way private portfolio | Experimental `audit-catalog-projection` | Selected v1 public 4/4 + fresh 4/4; private primary 1/4 with one error and 1/2 core pairs. Required-reward interface is defective; no full qualification or promotion. [Public native data](../evaluations/audit-catalog-projection/invocation-public-summary-20261112.json), [approved private aggregate and audit](../evaluations/audit-catalog-projection/validation-aggregate-20261112.json), [unpromoted prototype](../evaluations/audit-catalog-projection/prototype/README.md) |

The newest pilot is intentionally small. Unit tests, verifier mutants, repeated
attempts, scenarios from a shared generator and independent source families have
different denominators. Consult each report before interpreting a percentage.
An unchanged control fluctuating between runs is not a measured skill gain.

## Earlier semantic evidence

- [Reviewed curation refinement and limits](../evaluations/curate-semantic-model/refinement-20261102.md)
- [Ontology migration, native reasoning boundaries and blockers](../evaluations/curate-semantic-model/migration-20261102.md)
- [Ontology-guided cross-file/glossary routing](../evaluations/ontology-guided-cross-file-20261108.md)

Earlier published evidence is linked at its original path and retains its original
model and task scope. It is not pooled with the new NVIDIA-informed pilot.

## Method coverage

`harbor-run-results` owns the native counts, rewards, fairness checks and source
reports. `harbor-organize-evaluations` owns dataset locks, ordered stages and
one-way private release. `harbor-trace-distillation` owns the rejected broad
candidate's fresh-development gate. Dataset-authoring and skill-creator workflows
support independent contract/mutant review. These methods were used to evaluate
the target skills; their own quality is not a measured target in this catalog.

Native job directories, private tasks, answers, trial diagnostics and trajectories
remain local. Published aggregate JSON binds its source reports by SHA-256 without
revealing private case identities. The [evaluation methodology](../evaluations/README.md)
explains repository-level validation conventions.
