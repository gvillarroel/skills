# OpenSearch 2.19 product feature inventory

Apply the supplied [ontology](ontology.ttl) and [shapes](shapes.ttl) to
the seven operation identities in [scope.json](scope.json).
The case distinguishes a model that runs in the cluster, documented
inference at an external provider, fixed operations that consume
vectors or scores, and a private endpoint whose implementation remains
open. The scope also asks for release facts and separately evaluates
two configured request routes.

## Capture the sources

From this example directory, run the crawler with Python 3.11 or later.
On the published example, download `../crawl.py` or use the installed
skill's `scripts/crawl_product_docs.py`. Use a fresh corpus directory.

```bash
python ../crawl.py crawl --spec crawl-spec.json --output corpus
python ../crawl.py verify --spec crawl-spec.json --output corpus
```

The [specification](crawl-spec.json) pins nine official documents.
Six are seeds and three are reached through approved links. The
manifest retains the source paths, exact hashes, versioned publisher
routes, and discovery edges. The publisher aliases share their
canonical source identity. The upstream project distributes the
documentation under the Apache License, Version 2.0.
[Pinned OpenSearch documentation and license](https://github.com/opensearch-project/documentation-website/tree/f5e5e211d197f0fcee0cbf6dfc93e680b8c7ff12)

## Populate and verify the ontology

Give `extract-with-ontology` the supplied ontology, shapes, scope,
and `corpus/manifest.json` with its downloaded files. Ask for
`data.ttl`, `evidence.json`, and `review.md` in a new output
directory. Each classification, boundary, version, and directed
relation needs its own sufficient evidence. In review, explain the
disposition of each proposed direction, the requested release
contrast, and the observation that would resolve the open
implementation question.

Replace `SKILL` with the installed skill directory. Check the exact
source and assertion coverage, then verify the declared graph
constraints separately.

```bash
uv run --script SKILL/scripts/check_extraction.py check --ontology ontology.ttl --data output/data.ttl --evidence output/evidence.json --source-root corpus --output checks.json
uv run --isolated --no-project --with pyshacl==0.40.0 pyshacl -s shapes.ttl -e ontology.ttl -i none output/data.ttl
```
