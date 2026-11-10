# GitHub product feature inventory

The product example uses `extract-with-ontology` to populate a
supplied ontology from a bounded crawl of official documentation.
The input fixes the GitHub.com product and thirteen target
capabilities. It includes the ontology, SHACL shapes, fourteen
pinned Markdown sources and their provenance. The extraction
outputs an asserted graph, exact evidence and a review queue.

## Reproducible reference

The crawler followed eight internal links from nine seeds within
the approved paths. Two independent crawls on Python 3.11 and 3.14
produced fourteen identical source files and the same manifest.
Both offline verifications and all eleven crawler tests passed.
The manifest SHA-256 is
`07a91c27f109476f12532d2eb45688b032c2359fd59417da498956bb52b61da9`.

The reviewed reference classifies five capabilities as AI features,
seven by an explicit manual, static or rule-driven documented mode,
and one as unresolved. It keeps the Copilot usage metrics dashboard
in review and preserves thirteen product membership links and six
directed links among features. The standard extraction checker
verified all 47 assertions against the pinned sources. SHACL
conformed and all twelve positive and negative shape controls passed.
The reference graph fingerprint is
`29932eeb33e0096b5350c4f1706ccf6c96ead7676f6283a7acf51abe8ce3b900`.

The catalog assesses the documented operations in the source
snapshot. For example, an AI remediation feature can feed a
rule-driven merge feature. The two retain separate identities and
classes. Each class refers to the documented operation and its scope.

[Runnable example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/README.md) ·
[Pinned GitHub Docs revision](https://github.com/github/docs/tree/f309096a83abde7c311523f8ca97fc587388b0e1) ·
[Documentation license](https://github.com/github/docs#license)

## Native Harbor comparison

The independent rubric covered four topical groups. Each arm used
the same pinned task bytes, source whitelist, ontology, shapes and
verifier, with one GPT-6 Luna low attempt per group and zero
retries. The treatment added guidance to classify documented
operations at the evidence-supported scope. Thirty-two local and
32 Docker verifier controls passed.

| Result | Existing skill | Classification guidance |
| --- | ---: | ---: |
| Strictly admitted trials | 2/4 | 2/4 |
| Full passes among admitted trials | 0/2 | 0/2 |
| Mechanical evidence check and SHACL, all retained artifacts | 4/4 | 4/4 |
| Correct classification at the fixed feature IRI, all retained artifacts | 11/13 | 8/13 |
| Required ownership edges, all retained artifacts | 13/13 | 9/13 |
| Required directed relations, all retained artifacts | 6/6 | 2/6 |

Both arms incurred tool errors while locating copied quotes. The
retained-artifact metrics include trials excluded by the strict
execution gate. An independent post-hoc audit verified the exact
positions of 105 assertion quotes and assessed shorter citations
against their full claims. It found sufficient class citations
for 9/13 baseline and 5/13 guidance targets, and sufficient
relation citations for 6/6 and 2/6. The frozen rewards were
preserved. The additional classification paragraph was rejected.

One retained artifact collapsed branch protection and required
status checks into a single node with a self-relationship. The
frozen evaluator caught the identity error. The released example
shapes also reject self-relationships and require the named product
node, including when the asserted graph is empty. The native
trials used the previously frozen shapes.

## Deterministic evidence binding

The `bind` command takes pinned UTF-8 sources and inclusive line
selections for the asserted triples. It reconstructs exact quotes,
Unicode offsets and locators, then checks the ledger against the
supplied ontology and graph. Four unit tests passed on Python 3.11
and 3.14. Binding all 47 assertions of the reviewed inventory
produced byte-identical ledgers in both versions.

An adaptive Harbor arm made the binder available while retaining the
original tasks. Luna invoked it in 0/4 attempts. One trial was
admitted and zero passed the full gate. The four retained artifacts
included 13/13 correct fixed-IRI classifications, 13/13 membership
edges and 4/6 required directed relations. These results measure
availability and uptake of the tool. The full task still mentioned
manual substring lookup.

Two isolated Luna low checks required the binder explicitly and used
five selected features with bounded excerpts. Both returned all five
reference classifications, the required auto-merge relation and
mechanically valid evidence for all 18 asserted triples. Both graphs
conformed to the released shapes and shared fingerprint
`90feef59d76bb781a9dec13579616a8239edd6da2c48dd4b022c986bdff53bc2`.
Each output tagged its six labels with `@en`, while the reference used
plain strings with the same lexical values. Both review summaries
miscounted the graph as 19 triples. They correctly kept the metrics
mechanism open and asked what evidence would settle it.
