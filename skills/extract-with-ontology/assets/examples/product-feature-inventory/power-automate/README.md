# Power Automate cloud-flow feature inventory

Populate a fixed product ontology from eight official documents.
The [scope](scope.json) names eight operations and the candidate
relationships and configuration claims to assess. The supplied
[ontology](ontology.ttl) distinguishes AI-backed operations,
documented fixed rules, and features with an unresolved mechanism.
The [SHACL shapes](shapes.ttl) check the product, ownership, and
exclusive classification of its features.

## Capture and verify the documentation

Run from this directory with Python 3.11 or later. On the published
example, use the parent directory's `crawl.py`. In a checkout, use
`scripts/crawl_product_docs.py` from the installed skill. Choose an
absent corpus path under an existing directory.

```bash
python ../crawl.py crawl --spec crawl-spec.json --output corpus
python ../crawl.py verify --spec crawl-spec.json --output corpus
```

The [crawl specification](crawl-spec.json) fixes the repository,
commit, approved files and SHA-256 digests. Six seeds lead to two
additional documents. The manifest records the downloaded bytes and
the discovered links. The documentation is published by Microsoft
under Creative Commons Attribution 4.0.
[Pinned source and license](https://github.com/MicrosoftDocs/power-automate-docs/tree/e7a4c26faaa37ea3432ea7011957f3e72af745c1)

## Extract and compare

Give `extract-with-ontology` the ontology, shapes, scope, and verified
corpus. Ask for a `data.ttl` instance graph, exact source citations in
`evidence.json`, and a `review.md` file that accounts for every requested
decision. To produce a glossary too, request it as a separate artifact
and use the ontology's labels and definitions for its vocabulary.

Assess what each operation does within its stated boundary. Evidence
that a designer helps author an expression, evidence about evaluating
that expression, and evidence about an external service establish
different claims. Record supported directed edges with the conditions
that govern them. If a mechanism remains open, ask what specific
observation would resolve it. Keep a product-level configuration
option separate from evidence of any tenant's current settings.

Replace `SKILL` with the absolute directory of the installed skill.
Verify the asserted graph and its cited text against the saved corpus,
then check schema conformity.

```bash
uv run --script SKILL/scripts/check_extraction.py check --ontology ontology.ttl --data output/data.ttl --evidence output/evidence.json --source-root corpus --output checks.json
uv run --isolated --no-project --with pyshacl==0.40.0 pyshacl -s shapes.ttl -e ontology.ttl -i none output/data.ttl
```

For independent repeats, keep the ontology and crawl specification
bytes fixed. Compare the asserted-graph fingerprints, then compare
evidence sufficiency and unresolved decisions separately.
