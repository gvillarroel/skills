# Materializing an ontology extraction from one assertion plan

V44 tested a single source-bound plan in `extract-with-ontology`. A row names the subject, predicate, RDF object, source ID and
inclusive line range. The deterministic `materialize` command creates
`data.ttl` and `evidence.json` from the same rows. The product feature inventory uses the command
after downloading the pinned GitHub Docs corpus.
[Skill](../skills/extract-with-ontology/SKILL.md) ·
[Product example evaluation](product-feature-inventory-20261109.md)

## Design and retrospective replay

Extract, Define, Canonicalize informed the separation of extraction
from representation. The supplied
ontology and source bytes are fixed here. The tool binds citations from
the selected lines, preserves the selected RDF terms, and writes triples
in sorted N-Triples syntax, a subset of Turtle. Multiple evidence rows
can support one triple. The existing `bind` command handles an existing
asserted graph. [EDC paper](https://arxiv.org/abs/2404.03868) ·
[RDF 1.1 N-Triples](https://www.w3.org/TR/n-triples/)

An independent replay reconstructed plans from the citations in 13
retained V43 outputs, extending the citations to their source lines.
The new CLI reproduced 13/13 exact RDF triple sets and canonical
fingerprints. Reversing the order of source and assertion rows produced
byte-identical graphs and evidence ledgers in 13/13 cases. Python 3.11
and 3.14 produced identical replay reports with SHA-256
`8b8d0a727b9fa8bc277bf3b695b84b84e50f7fc4e9616a913cecdebe8ec5112`.

The V43 open discovery draft had 12 labels with `@en` in its graph
and 12 corresponding labels without a language tag in its selection.
The two-artifact check identified 12 unasserted evidence rows and 12
uncovered graph triples. Materializing the draft selections creates
a coherent graph and evidence pair. Choosing the correct language tag
and remembering the required product type remain extraction decisions.

The frozen V43 SHACL shapes accepted 12/13 replayed graphs. The
released shapes accepted 11/13 and flagged the missing product type
and a feature incorrectly related to itself. An independent adversarial
control with an unrelated exact quote passed materialization and
SHACL. The evidence and SHACL gates therefore remain separate from
judging whether the source supports the full claim.

## Reproducibility and first use

The materializer reproduced all 47 assertions of the reviewed GitHub
inventory, with graph fingerprint
`29932eeb33e0096b5350c4f1706ccf6c96ead7676f6283a7acf51abe8ce3b900`.
Four materializer tests and four existing binder tests passed on
Python 3.11 and 3.14. A separate audit passed 39 controls per interpreter.
Its controls covered language and datatype preservation, file pins,
path containment, multiple sources, output collisions, concurrent
writers and cleanup after a caught second-write failure. Output
directory contents can be visible while the command is writing.

The first two isolated GPT-6 Luna low checks were excluded by the
strict gate. Their prompt pointed to the wrong skill path, and both
plans initially included an extra `ontology_sha256` field. One run
recovered and produced artifacts. The updated reference shows the
complete two-key selection structure, and the corrected prompt uses
the actual skill path and fixes the exact ontology and source bytes.

Both new runs produced the same five supported triples, preserved
`@en` labels, cited the same spans and kept an unspecified dashboard
mechanism in review. Both graph and evidence files were byte-identical.
One run invoked the required command alone and passed the strict gate.
The other executed it successfully in a shell call that also wrote
the plan, which the exact-command check excludes. These targeted
checks supplied the expected assertion set and measure tool use and
artifact repeatability.

| Artifact | SHA-256 |
| --- | --- |
| Graph | `95d5699558b064b917c30704107ea2d869b904aabcb62e779469a1b90847f946` |
| Evidence | `ae1844f5168888eefa24dced3c7c8280750328aea7662a9e8c83cfba0d5579f` |

## Native Harbor development comparison

The frozen cases covered a product feature inventory, incident routing,
and a research catalog. The arms shared the source files, ontologies,
SHACL shapes and private verifier. The task workflow required the
corresponding command in each arm. The previous arm used the V43
line-selection bundle, whose checker and artifact reference match
the published V43 release. The candidate used the new materializer.
Each case had one GPT-6 Luna low attempt and zero retries.

The verifier passed 27 controls locally and again in pinned Docker.
Each case included valid output in two orders and seven targeted
negative controls. They tested a missing root type, reversed relation,
incorrect citation, stale source digest, unsupported extra assertion,
incorrect uncertainty class and missing review question.

| Result | V43 line binder | V44 one plan |
| --- | ---: | ---: |
| Strictly admitted trials | 2/3 | 3/3 |
| Full native passes, all attempts | 0/3 | 1/3 |
| Expected graph claims, all retained artifacts | 36/36 | 36/36 |
| Unsupported extra graph claims | 0 | 0 |
| Claims with supporting citations, all retained artifacts | 26/36 | 36/36 |
| Complete uncertainty review, all retained artifacts | 1/3 | 1/3 |
| SHACL conformance, all retained artifacts | 3/3 | 3/3 |

All three paired graphs had identical fingerprints. The candidate
passed the product case and successfully invoked `materialize` in
all three cases. Independent replay of each candidate plan preserved
both output files byte for byte, including with permuted plan rows.
One baseline case corrected a mismatch between the asserted graph and
its selection after a failed `bind` call and was excluded from strict
admission. In the baseline product case, ten citations pointed to a
neighboring line. The verifier rejected them despite exact source
matching.

In the remaining two cases, both arms used the ontology's uncertainty
class but omitted the question about which evidence would settle the
underlying fact. A future development candidate can make that review
step explicit even when a class is already available. This comparison
used three development cases and does not estimate holdout performance.

The local study archive retains the frozen protocols, verifier
controls, native job receipts and paired comparison in
`integration-v44-plan-live`. The baseline job ID is
`d3d2aa6b-da51-450d-8acf-2dde6fe8ebbb`. The candidate job ID is
`3b9027ab-a559-47f8-a756-dc0f1eee07b9`. The replay and audit reports
are in `integration-v44-plan-replay` and `integration-v44-plan-audit`.
