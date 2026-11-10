# Product inventory extraction from pinned documentation

This study evaluates `extract-with-ontology` on product
documentation. The caller supplies the ontology and the corpus scope.
The extractor produces instance assertions, exact source citations,
and a review of decisions that the documentation leaves open.
The crawler and the materializer each have their own replay checks.

The public [GitHub example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/README.md)
uses 14 Markdown documents at an immutable GitHub Docs revision.
The reviewed inventory contains 13 capabilities, with five AI
operations, seven documented manual, static or rule-driven operations,
and one mechanism left open. A new online crawl and offline
verification reproduced all source files and the manifest byte for byte.
An assertions-only plan for the 47 reviewed triples reproduced the
previous graph and evidence in the manifest route.
[Reference and original native results](product-feature-inventory-20261109.md) ·
[Materializer audit](ontology-manifest-materialization-20261109.md)

## GitHub native development comparison

The four product strata reuse the 13 feature targets, 14 official
documents, supplied ontology, SHACL shapes and six required directed
relations. The same task bytes run against the previous release and
the manifest release. Both actors select numbered lines and write
assertions-only plans. The shared wrapper derives the explicit source
roster for the previous release and uses the native manifest option
for the current release. Both routes receive the same pins. This
comparison tests controlled integration. It does not estimate the
effect of independently discovering the helper.

Harbor 0.18.0 used one GPT-6 Luna low attempt per cell and zero
retries. Forty preflight controls passed twice locally and once in
pinned Docker. They included narrow citations that support a claim
and exact quotes with insufficient scope. Eight no-inference wrapper
runs reproduced the same artifacts across the two CLI routes.
The preregistered native gate and the separately reviewed semantic
results remain distinct. Earlier product results use different task
instructions and an enclosing-paragraph citation metric.

| Native result | Explicit roster | Manifest-backed |
| --- | ---: | ---: |
| Strict admission and successful controlled route | 4/4 | 4/4 |
| Full native pass | 0/4 | 0/4 |
| Mechanical binding and exact source whitelist | 3/4 | 3/4 |
| SHACL conformity | 1/4 | 0/4 |
| Correct classes across the planned targets | 10/13 | 11/13 |
| Class citations matching the native semantic criteria | 9/13 | 9/13 |
| Correct memberships across the planned targets | 11/13 | 10/13 |
| Correct labels across the planned targets | 11/13 | 11/13 |
| Required directed relations present | 4/6 | 5/6 |
| Unsupported directed relations | 1 | 1 |

The strict execution gate admitted all eight trials. The native
artifact gate excluded one stratum per arm from semantic scoring.
The table uses the planned denominators and counts the unreached
targets as missed. Both modes processed all four plans by the
intended route. The manifest option simplifies source provenance.
The native full pass count and strict admissions are tied.

An independent graph-only replay included the artifact gated by
the citation cap in each arm. It found 12/13 versus 13/13 correct
classes, 13/13 versus 12/13 memberships, 13/13 labels in each arm,
and 5/6 versus 6/6 required directed relations. There were two
versus one unsupported edges. These scores count present facts
before checking that their citations meet the task contract.

The masked assessment of exact-bound citations in the strata
that reached semantic scoring credited 9/11 versus 10/11 class
citations and 4/5 versus 5/5 directed relations. Shorter citations
for the agentic review and the branch-protection relation
supported the required scope despite the enclosing-span rule.
Each dependency artifact included a 1,974-character quote above
the 1,800-character task cap. There were zero offset errors and
the bundled extraction checker passed 4/4 outputs in each arm.
Seven of eight graphs omitted the explicit product type that
the shape requires. Native rewards remain at zero for both arms.

## Independent product transfer to Zed

A temporary Zed route adapter retained the published crawler's
breadth-first walk, source limits, exact byte verification and replay.
The adapter changes the repository, official routes and publisher
URLs. Four seeds led to five additional documents and 15 in-scope
links. Independent Python 3.11 and 3.14 crawls reproduced nine
official Markdown documents, totaling 85,763 source bytes, and the
same manifest. Both offline checks passed. Controls covered excluded
routes, tampered sources, manifest changes, extra files and an
insufficient crawl depth.
[Zed v1.27.0](https://github.com/zed-industries/zed/releases/tag/v1.27.0)

The supplied ontology distinguishes model-backed operations,
documented fixed operations, and mechanisms that remain unresolved.
It gives one directed predicate that includes the governing
condition. The reference has seven operations and 24 asserted
triples. Ten independent evaluator controls checked supported
alternate citations, legitimate names with a different graph identity,
missing product type, wrong scope, incorrect class despite SHACL,
reversed and self-directed edges, and the promotion of an
illustrative example into an inventory fact. The actor workspace
contained the crawl, ontology and shapes. The reference and
semantic evaluator remained separate.

### Discovery from operation bands

The first two repeats named the operation bands and let the actor
mint feature identifiers. Both retained plans used the manifest route.
The strict gate excluded both trials. The actor image lacked `rg`,
which the preflight omitted from its tool checks. Each trace also
included one create-only destination error, for materialization or
an inventory command. No actor was retried.

The independent masked review aligned all seven operations in both
graphs despite legitimate identifier and label variants. Each output
correctly classified 5/7 operations and supplied sufficient evidence
for 4/7 correct classes. Both classified the language server's
completion generation and the external formatter as non-AI from
evidence about dispatch. The selected external implementations and
their methods were open. Neither review asked a question sufficient
to resolve either mechanism. The citation for task launching described
picker and rerun controls rather than the shell dispatch.

The graph with the qualified display-priority relation omitted the
product type and label and failed SHACL. The other graph passed
SHACL and omitted the relation after reversing which operation
yields. Mechanical evidence checks covered 22/22 and 23/23 asserted
triples, respectively. Replaying each fixed plan twice reproduced
its graph and evidence byte for byte. The independently authored
plans produced different graphs. The frozen automatic alias and
citation scores remain intact alongside the independent review.
[Zed completion paths](https://github.com/zed-industries/zed/blob/c84af5b99cbc366d675064e52b23664a015b6e35/docs/src/completions.md#L8-L15) ·
[Edit Prediction display modes](https://github.com/zed-industries/zed/blob/c84af5b99cbc366d675064e52b23664a015b6e35/docs/src/ai/edit-prediction.md#L42-L45)

### Adaptive repeat with fixed operation identifiers

The follow-up reused the original corpus, ontology, shapes and
semantic evaluator. It supplied names and identifiers for the seven
operations, required explicit product typing and labels, and
clarified the general scope distinction between dispatch and the
operation of the selected implementation. It supplied and verified
the available search command in Docker. Each trial used the same
manifest route and fresh output directory. The two new GPT-6 Luna
low attempts were a development follow-up with zero retries.

| Outcome | Discovery from bands | Adaptive fixed roster |
| --- | ---: | ---: |
| Strict native admission | 0/2 | 1/2 |
| Retained graphs with all seven operations aligned | 2/2 | 2/2 |
| Retained graphs with all seven exact operation identifiers | 0/2 | 2/2 |
| Retained SHACL conformity | 1/2 | 2/2 |
| Correct classes across both retained graphs | 10/14 | 12/14 |
| Sufficient class citations in the masked review | 8/14 | 8/14 |
| Direct questions for unresolved mechanisms | 0/4 | 2/4 |
| Supported qualified relation | 1/2 | 1/2 |
| Full semantic artifact pass | 0/2 | 0/2 |
| Equal graph fingerprints across attempts | No | No |

One adaptive artifact had all seven correct classes and both
direct review questions. Its graph omitted the qualified display
relation. The other kept the relation and again classified the
two external mechanisms as non-AI. One actor tried a nonexistent
script before using the documented materializer. Both final graphs
had the exact seven feature IRIs and labels and the explicit
product node. The same plan reproduced both files byte for byte
for each run. The two different plans still produced different
graphs. A narrower language-server citation was sufficient in the
masked review and stayed outside the frozen automatic interval
set. The adaptive changes were bundled, so this comparison
measures the supported workflow as a whole.

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| GitHub native protocol | `7455411b16f3eed27fd42659e675c0e852720afff7b2e4b4adb115fe6ac0c74b` |
| GitHub paired native outcomes | `d8f8b59fb0a16e2263b9b0fd40598e03d7b9eaf6a9ace7ce24290f88f6d9403e` |
| GitHub masked citation review | `2c05acb2f02d1c3bdf17b875d35b5ef9a46bd87c14239ea32d5ecfcb40a4b434` |
| Zed crawler manifest | `503f0d0c7f0fb410cdc44dc8666939c8cbd48bbdec69f59dc29991bf4151cb9b` |
| Zed discovery protocol | `a2cb87ffa67e10a30b561418f252ba3f35a0a46a62986ebe4499bd842fd364cd` |
| Zed discovery masked review | `f21ee9a3d34d33f8322a46a4c607b93a461cd9d3727a9cd6d351554bb9316bea` |
| Zed adaptive protocol | `7b63fd902e9ba6d0714b95542bdd75b9599a3292000af7ef6cc67b618c5070a3` |
| Zed adaptive native outcomes | `b7edecd9478d5d315c086a46d39e2462c1fef272e09a00ce4b97b74e6f0649d1` |
| Zed adaptive masked review | `a139941eafd0d419fa00a73b1535a41f64b84808da2e3f9a0b5a7ddd8f88953a` |
