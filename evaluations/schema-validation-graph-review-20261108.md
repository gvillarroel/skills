# Validation graph review for JSON Schema versions

This public development study compares two pinned schema snapshots.
The unit is a pull request pair. A replayed full-document witness
proves a difference in one direction. A bounded structural or finite
domain certificate can establish the absence of a difference in the
other direction. The study keeps incomplete searches, unsupported
semantics, reference errors and processor errors separate.

## Directional replay and graph comparison

The method follows work on witness generation and partial containment.
It uses the original source files with their declared dialects for
witness replay. The normalized structural view keeps schema keywords
under their own object or instance scope. Draft 7 local references
can be resolved before a comparison. Changes in dialect behavior
require separate validation. [Directional witnesses](https://arxiv.org/abs/2202.12849) · [Partial containment](https://software-lab.org/publications/issta2021_JSON.pdf) · [Modern dialect semantics](https://arxiv.org/abs/2307.10034)

The first prototype refused editor extensions and had an argument
contract defect in generated seed handling. It crashed on 20 of
25 controls. The second repaired the route and added bounded
source-only probes. The third added positive containment rules
and exact reading of integral exponent tokens. It avoids treating
a syntax difference as an acceptance difference.

| Stage | Observed outcome |
| --- | --- |
| Existing examples only | The disclosed Dependabot PR supplied no witness through the neutral seeds. |
| Direct structural edits | The same PR had 11 reported structural edits and no witness. A pure refactor also produced 11 edits. |
| Scoped local reference expansion | The actual change produced 14 scoped edits and witnesses under both update and group entries. The pure relocation and inverse inlining certified equivalence. |
| Positive containment | The actual change certified weakening by proving that every old valid document remains valid and replaying an added example. |
| Offline multi-dialect replay | The baseline found 3/6 expected directions across five additional public PRs. The revised pattern-key routing, scoped negation probes and branch scaffolds found 6/6. |
| Guarded recursive graph equality | The checker certified the equivalent GitHub Workflow refactor, which the previous strict projection deferred. |

The frozen Draft 7 candidate gave 25/25 results consistent with the
independent controls. It found 18/18 supported directional witnesses,
attributed all 24 applicable scopes, retained explicit unknown in
4/4 mandatory deferrals and concluded 9/21 supported-or-deferrable
global relations. An additional proof-polarity suite matched 12/12,
and five numeric controls passed. The controls include masked scope,
optional parents, conditional property closure, duplicate exclusive
branches, dialect-specific reference siblings and numeric precision.
Whole-document replay prevents attributing a local suggestion to a
global acceptance change without a concrete instance.

## Public pull request transfer

Five additional pairs from three repositories were pinned by commit,
Git blob and SHA-256. The independent oracle checks 57 full documents
and 134 validation assertions. These sources were used during the
iteration and constitute public development evidence.

| Pair | Evidence from the tested methods |
| --- | --- |
| Cargo | A full document with incompatible Git selectors validates only before. Its opposite root inclusion remains unresolved. |
| Compose | A service with a null command validates only after. Its opposite direction remains unresolved by the prototype. |
| Tombi | Both directions were independently witnessed. |
| Dev Containers | Both directions were witnessed using each snapshot's own dialect. |
| GitHub Workflow | Guarded graph equality certified the relocation and redundant branch conditions. |

The improved replay produced byte-identical reports under a second
Python hash seed. The independent validator confirmed all six
witnesses against the original files. The minimal JSON instances
demonstrate schema acceptance under the declared policy. Execution
of the corresponding runtime configuration is a different check.
[Cargo](https://github.com/SchemaStore/schemastore/pull/6443) · [Compose](https://github.com/compose-spec/compose-spec/pull/309) · [Tombi](https://github.com/SchemaStore/schemastore/pull/5458) · [Dev Containers](https://github.com/devcontainers/spec/pull/167) · [GitHub Workflow](https://github.com/SchemaStore/schemastore/pull/4145)

## OSS and verifier audit

Released jsonsubschema 0.0.8 produced seven false containments in
88 measured directions. Forcing a Draft 7 validator retained the
same outcome. The upstream Draft 7 proposal produced five false
containments. In a separate exhaustive finite matrix, each direct
variant falsely approved nine containments. A closed object's
required Boolean field was reported as contained in the same field
restricted to true. A document with false refutes that result.

Explicit Boolean enumeration repaired those nine matrix cases
while retaining other errors and abstentions. The independent
finite method matched 1,936/1,936 directions, with 12,584
schema-instance evaluations confirmed by a second interpreter.
The library remains a development diagnostic. [Published package](https://pypi.org/project/jsonsubschema/0.0.8/) · [Draft 7 proposal](https://github.com/IBM/jsonsubschema/pull/41)

## Released Draft 7 graph check

The standalone checker certifies equality only after supported
rewrites. It treats optional format and content keywords as
annotations. It preserves the scope of object closure, the number
of oneOf branches and guarded recursive binder identities.
Unsupported resource scope, external references and unguarded
cycles leave the comparison unresolved.

The GitHub Workflow comparison resolves both snapshots to the same
graph. The independent audit passed eight targeted controls and 20
recursive comparison pairs. All ten equivalent recursive pairs
were certified. The ten changed pairs stayed unresolved and had
replayed counterexamples. A separate predicate oracle agreed with
the Draft 7 validator on 5,800 instance evaluations. The audit
also verified the optional-format boundary and reproduced an input
Unicode error. The release checks the input for unpaired Unicode
surrogates before comparing.

Eight executable repository tests passed, along with the three
existing curation test suites and repository checks. Two strict
isolated Luna executions loaded the new reference and ran the
same checker twice. Both preserved all three schema inputs,
certified the refactor, and left the actual choice change
unresolved in the graph checker. The semantic view hashes
repeated across the two executions. The runtime qualification
receipt SHA-256 is
`24e5a9d55dc54ca8b616c62a0512598b72de9a54f79ab92d5f1d0b56cf6d666c`.

~~~powershell
uv run --script evaluations/contracts/test_schema_validation_graph_review.py
uv run --script scripts/run-pi-skill-eval.py curate-semantic-model --prompt-file evaluations/pi-prompts/schema-validation-graph-review.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id schema-validation-review-replay --expect-output before.json --expect-output refactor.json --expect-output change.json --expect-output refactor-report.json --expect-output change-report.json
~~~

The research prototypes and receipts remain in the local
semantic-skill-evaluation project under the
schema-reference-delta-20261108 artifact directory. The
independent ontology generation gate remains separate.
