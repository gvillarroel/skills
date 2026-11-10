# GitHub product feature inventory

This example applies the supplied [ontology](ontology.ttl) to an
inventory of documented GitHub.com features. The ontology separates
product membership, feature identity, and the evidence for a feature's
documented use of AI. It includes an explicit unresolved class for
features whose documented behavior leaves their mechanism open.

## Crawl the source snapshot

Run from this example directory with Python 3.11 or later. Choose a new
directory outside the skill for the downloads. Create its parent first.

```bash
python crawl.py crawl --spec crawl-spec.json --output /path/to/product-corpus
python crawl.py verify --spec crawl-spec.json --output /path/to/product-corpus
```

The [crawl specification](crawl-spec.json) pins a commit of
`github/docs`. The crawler follows links within its declared scope
and records the exact bytes, SHA-256 and discovery path of each
download. Verification uses the saved snapshot. The source Markdown
comes from GitHub Docs and is distributed by its publisher under
[CC BY 4.0](https://github.com/github/docs#license).

## Populate the existing ontology

Give `extract-with-ontology` the ontology, the [SHACL shapes](shapes.ttl),
`manifest.json`, and the downloaded Markdown directory. Request an
asserted graph in `data.ttl`, source-bound `evidence.json`, and a
`review.md` file. Keep the product and feature IRIs stable when the
same feature appears in another source or revision.

Use a separate workspace for newly extracted outputs. The
[reference graph](data.ttl), [evidence ledger](evidence.json), and
[review decisions](review.md) in this directory form the reviewed
example for the pinned corpus.

Use `AIFeature` for an evidenced AI operation. Use `NonAIFeature`
for a specifically documented human operation, static service or
fixed-input rule in the assessed scope. Use `UnclassifiedFeature`
when the evidence establishes the feature and leaves the mechanism
open. In review, state what is known, which evidence is missing and
what observation would settle the classification. A documented
connection between two features has its own evidence.

For this product, distinguish ordinary pull request review, Copilot
code review, and the dashboard that measures Copilot usage. Each
describes a different operation. The ontology classifies those
operations in the pinned snapshot.

## Build and check the result

Replace `SKILL` with the absolute directory of `extract-with-ontology`
and set the source root to the crawler output. Inspect a source
using its pin from the saved manifest.

```bash
uv run --script SKILL/scripts/check_extraction.py lines --source-root /path/to/product-corpus --source sources/auto-merge.md --manifest /path/to/product-corpus/manifest.json --start-line 19 --end-line 23
```

In `selections.json`, record each assertion with its source ID and
inclusive line range using the skill's evidence binder format.
For a new extraction, generate the graph and its exact citations from
this plan.
Choose a new result directory under an existing parent.

```bash
uv run --script SKILL/scripts/check_extraction.py materialize --ontology ontology.ttl --selection selections.json --source-root /path/to/product-corpus --output-dir /path/to/product-result
```

Write the review queue separately. To bind citations to an existing
graph, use the skill's `bind` command. The following commands validate
the reviewed reference in this directory. Substitute the generated
graph and evidence paths to check a new extraction.

```bash
uv run --script SKILL/scripts/check_extraction.py check --ontology ontology.ttl --data data.ttl --evidence evidence.json --source-root /path/to/product-corpus --output checks.json
uv run --isolated --no-project --with pyshacl==0.40.0 pyshacl -s shapes.ttl -e ontology.ttl -i none data.ttl
uv run --script test_shapes.py
```

Compare graph fingerprints across repeated runs. Review the supporting
passage for each classification and relation. SHACL checks that every
cataloged feature has one owner and exactly one of the three assessed
classes. The example shapes require the GitHub product node and catch
relationships that point from a feature to itself. Change the target
product IRI when adapting the shapes to another product. The evidence
check verifies the source pins and citation spans. Assess the meaning
of the cited operation separately.
