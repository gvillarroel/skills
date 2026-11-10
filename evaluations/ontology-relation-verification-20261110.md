# Relation verification and provenance for ontology-guided extraction

This development work follows the
[Power Automate catalog experiments](ontology-product-catalog-20261110.md).
All eight retained inventories in those experiments asserted a feature
relationship from a help cross-link. The supplied predicate requires a
documented transfer into the receiving setting. This evaluation separates
claim support, evidence selection, and the mechanical ability to change a
graph. The verification pass follows earlier work that independently checks
claims from a draft. [Chain-of-Verification](https://aclanthology.org/2024.findings-acl.212/)

## Surface matches and directed evidence

An offline probe used 28 bounded evidence decisions from the Power Automate,
OpenSearch, GitLab, and Zed development corpora. The same sources and
candidate passages fed three rules. The most restrictive rule required an
operative clause that binds source and target roles, plus caller guards
where applicable. Its patterns were authored with access to the
development examples.

| Evidence rule | Supported accepted, of 8 | Unsupported accepted, of 20 |
| --- | ---: | ---: |
| Unordered mentions | 8 | 20 |
| Ordered roles and proximity | 8 | 15 |
| Operative clauses and explicit guards | 8 | 0 |

Removing guards added six false accepts. Requiring a single span lost
three valid joins. Dropping every Markdown link label lost a valid
relation where the linked noun served as the grammatical recipient.
Leaving navigational labels visible did not change the final decisions
in this probe because the operative clause still had to support the
transfer. On eight alternative bundles already accepted by the source
rubrics, the three rules retained 8/8, 7/8, and 3/8 respectively.
The operative patterns are useful for checking retrieved text. These
results leave them unsuitable as a general acceptance gate.

## Local entailment as a verifier

The same 28 development decisions and eight alternative witness sets
were checked with the previously pinned local DeBERTa ONNX model.
The raw-input run refused three windows above its 512-token limit.
A frozen visible-Markdown rendering preserved link labels, navigation
cues, and operative raw URLs while keeping every scored input within
482 tokens. It evaluated 195 distinct premise and hypothesis pairs.
The original refusal remained in the record.

| Local verifier rule | Supported accepted, of 8 | Unsupported accepted, of 20 | Valid alternatives accepted, of 8 |
| --- | ---: | ---: | ---: |
| Direct entailment at zero margin | 4 | 11 | 5 |
| Entailment of separate roles at zero margin | 0 | 1 | 2 |
| Forward versus reverse and navigation contrast at zero margin | 4 | 7 | 4 |
| Direct entailment, family-left-out calibration | 3 | 7 | 3 |
| Separate roles, family-left-out calibration | 2 | 6 | 3 |
| Contrast, family-left-out calibration | 7 | 14 | 7 |

The family-left-out thresholds were selected using the other
development families. No private validation data entered the run.
The contrast increased recall at the cost of false acceptance.
These results leave the local verifier unsuitable as an automatic
decision gate for this task. [AttributionBench](https://aclanthology.org/2024.findings-acl.886/)

A selective replay required agreement between the direct and
contrastive entailment scores and one or two mechanical signals.
At fixed zero margin, the ordered variant automated 11/28
decisions with five errors. The operative variant automated
13/28 with zero errors on the original examples. Requiring both
mechanical signals automated 6/28 with zero errors. Conservative
thresholds calibrated without the tested family still wrongly
withheld at least one valid alternative in every variant. The
operative variant withheld two. Agreement is useful for triage;
the accepted alternate citations rule out using it for deletion.

## Paired review of fixed Power Automate claims

The experiment froze both strictly admitted graphs from the previous
comparison and their selected citations. Each task exposes only the
asserted optional relation or aspect, its ontology meaning, scope,
and the selected source lines. Two fresh GPT-6 Luna low attempts per
arm ran with zero retries. The control makes a direct decision.
The treatment checks the producer, receiver, transfer, and governing
condition and seeks a counterexample. Both return the same
`keep` or `drop` carrier.

The compiler can remove only addressed optional assertions.
Product identity, ownership, classes, source pins, and all citations
for retained assertions remain fixed. Fourteen local and Docker
controls checked byte-identical all-keep replay, correct removal, and
invalid decisions. A native no-inference job exercised both task
roots before the live trials.

| Paired result | Direct review | Roles and counterexample |
| --- | ---: | ---: |
| Strict traces and valid projection | 2/2 | 2/2 |
| Unsupported assertions removed | 3/3 | 3/3 |
| Source-supported optional assertions retained | 3/6 | 2/6 |
| Decisions correct for the exact selected citations | 8/9 | 9/9 |
| Exact reference graphs after review | 0/2 | 0/2 |

All four reviews preserved the documented Filter array transfer.
Across the fixed pairs, seven source-supported assertions disappeared,
including four tenant opt-out statements and three named provider
statements. Their selected text lacked a governing scope or antecedent.
The count of required assertions with sufficient selected citations
stayed at 58/80. Both variants eliminated all six unsupported
assertions. The treatment improved the narrow citation decision by
one and lost one additional true graph assertion. A citation-only
decision that cannot reacquire context therefore remains a diagnostic
for this workflow.

The prospective private family remained sealed. Its isolated
verifier passed 12 offline controls. The equivalent public Harbor
transport passed both zero-inference tasks. Private native execution
is still gated on a verifier environment that cannot expose the
oracle through shared build layers.

## Citation repair with the graph held fixed

The repair prototype addresses only evidence selections for a
predeclared roster of assertions. It supports keeping a citation,
replacing it with authorized source ranges, or requesting decisive
evidence. The last option preserves the pending assertion in the
fixed graph for inspection and leaves its approval open. The same
subject, predicate, object, and pins are checked before and after.
Non-target citations and the original RDF bytes are preserved.

The evaluator represents alternative proofs as a choice among
complete evidence sets. Within each set, all required role,
operation identity, and governing-condition witnesses must be
present. A quote that binds mechanically can still fail that test.
The independent prototype reproduced the same Power Automate
20-triple and OpenSearch 31-triple graphs with two different
valid repair selections per fixture. On three scoped positive
claims per fixture, sufficient selected evidence rose from one
to three using human-reviewed repairs. Twenty invalid-carrier
controls were rejected. Two exact but insufficient quote controls
stayed semantic failures. Input reordering preserved outputs, and
Python 3.11 and 3.14 produced the same receipt.

## Application-produced evidence from dbt

The installed dbt experiment stopped during dependency installation when
the host drive ran out of space. The fallback read three checked-in
manifest fixtures directly from pinned commits and verified their bytes
before parsing. It compared complete direct parent sets for 16 active
models with 14 observed parent edges. The two structured paths read
fields produced by the same application as the expected parent map.
They test faithful reconstruction and consistency within a captured
artifact.

| Route | Exact model parent sets | True edges | False edges | Missed edges |
| --- | ---: | ---: | ---: | ---: |
| Names in SQL or description | 13/16 | 13 | 3 | 1 |
| Literal Jinja calls in template forms | 15/16 | 13 | 0 | 1 |
| Declared reference and source records | 16/16 | 14 | 0 | 0 |
| Resolved dependencies checked against both indices | 16/16 | 14 | 0 | 0 |

The SQL-only routes missed a source dependency that was present in
the model's recorded source references. The lexical route also mistook
an SQL alias and a CTE name for dependencies. The projection reconciled
`depends_on.nodes` with `parent_map` and the reverse `child_map`, and
rejected project, schema, identity, activity and edge mutations in
18/18 negative controls after adding an explicit active-configuration
check. Three order-permutation controls preserved the graph, and three
isolated-vertex controls changed its fingerprint without changing its
edges. The strengthened projection produced identical receipts on
Windows and Linux. [dbt ref](https://docs.getdbt.com/reference/dbt-jinja-functions/ref) ·
[dbt doc](https://docs.getdbt.com/reference/dbt-jinja-functions/doc) ·
[Manifest format](https://docs.getdbt.com/reference/artifacts/manifest-json)

Jinja 3.1.2 provided a separate syntax-only experiment without rendering
the templates. On 14 authored controls, template regex passed 8/14,
literal AST calls 9/14, possibly reachable AST calls 12/14, and
definitely reachable AST calls 14/14. The last method also preserved
all 14 expected open-branch outcomes. The controls included SQL and
Jinja comments, a hidden `execute` branch, a literal version argument,
an uncalled macro, and an unresolved configuration guard. All three
AST variants still recovered only 15/16 model parent sets from the
authentic fixture SQL. Parsing one source cannot reconstruct an
application's additional inputs.

Whole-artifact schema validation gave a separate result. The checked-in
state fixture passed both the schema from its containing release and
the schema from the version named by its producer. The defer fixture
had nine schema findings outside the scoped dependency projection.
The Jaffle Shop fixture omitted the schema-required macro map. Removing
a parent from the index in either nonempty graph left its JSON Schema
findings unchanged, while reciprocal index validation rejected it.
[dbt state fixture](https://github.com/dbt-labs/dbt-core/blob/59f31c26d6eb23bbc611c5e457c652ac471b248b/tests/functional/artifacts/data/state/v12/manifest.json) ·
[dbt defer fixture](https://github.com/dbt-labs/dbt-core/blob/59f31c26d6eb23bbc611c5e457c652ac471b248b/tests/functional/defer_state/data/manifest.json) ·
[Jaffle Shop manifest fixture](https://github.com/voi-oss/dbt-exposures-crawler/blob/7074c91de9667635ed8867b70094be8d8b033c4a/tests/_fixtures/manifest.json)

Five checked-in previous-state fixtures share the same project ID and
have different raw digests. Their four adjacent comparisons yielded
three identical typed model graphs. The v9-to-v10 comparison added
the isolated `metricflow_time_spine` model and changed no edges.
Including vertex identity detects this change. Windows and Linux
reproduced the same four deltas.
[Previous-state tests and fixtures](https://github.com/dbt-labs/dbt-core/tree/59f31c26d6eb23bbc611c5e457c652ac471b248b/tests/functional/artifacts)

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| Directed passage comparison | `e92bb88c08779d92808c775bd54dca17e86d5959232019bdc5f4459065191a0c` |
| Alternative witnesses and ablations | `71b4baf4a03d79d9b2cb706c4fabfd52767fa087e2e83bad86c59a2cb062b247` |
| Local entailment comparison | `7342df1dcbd2f7d4f32413bd5c098be0da20b4986c0cbf63fa868a426cbf5796` |
| Selective entailment and mechanical agreement | `677cab33268681a9217d89ec1f5b16109d17d7223b2f977d4d3121372029031a` |
| Paired relation-review protocol | `7366119a1c4847ab0112037c1dea214d79f788b420889eabc14faa96a2d347f0` |
| Native no-inference relation-review preflight | `f3cec27a4baad7bd9df82eb0065bd64a497a9dec1a330330a51a861ef4d155ca` |
| Paired relation-review results | `afadd30dab813152c6a1f26c76db200be8a89d9259d90df32f800edf58061578` |
| First independent relation-review assessment | `2e9940a5a1c31183139e0848f59016848308de22e508fe808df766bc5a8f947b` |
| Second independent relation-review assessment | `1d0e677c89ed23b3ea61bce68b42b8153f9bd886ee924adb22437ee858580c1e` |
| Citation repair prototype and alternate selections | `078e316569ea19095c5965c99de185e75cb9942a6b85cb53ac74c91fabc30c56` |
| dbt projection and negative controls | `c3243d834bfc422d5ff1c3431dd0a153f5426f3e8495f608660817ad21e2023f` |
| dbt projection with vertex identity and activity checks | `936ab3a0d20b5604b33b4bbf97f2bdc8f18d0be9b4e3a67539aa5294eb4e7517` |
| dbt Jinja syntax and reachability | `5a52fdb1fee91c197661b0ab705115eb6b0f484a650ef4bda060a7b0610449be` |
| dbt artifact schema comparison | `50f6caa46e68e9bad6de3b6cca4f8e833f3755d7ae3d923f6f18911c4ebfc6be` |
| dbt previous-state semantic differences | `e3f5a9d9b58e0824616c829e934dfb57852a2f79f6ba2cd5e7c6e176c474e96a` |
