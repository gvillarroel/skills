# Product feature catalog from pinned documentation

This development case applies `extract-with-ontology` to an
eight-operation Microsoft Power Automate cloud-flow inventory.
The caller supplies the ontology, SHACL shapes, scoped identities,
and candidate configuration claims and relationships. The actor
reconstructs the documentation snapshot with the published crawler
and emits an instance graph, source evidence, and a review. The
[example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/power-automate/README.md)
contains the exact acquisition and ontology inputs.

The reference distinguishes two AI-assisted authoring operations,
four documented fixed operations, and two documented capabilities
whose assessed mechanisms remain open. It also includes three
qualified relationship or configuration facts. The questions separate
the model used for authoring, evaluation of a configured condition,
the behavior of an external service, and the current configuration of
a tenant. A procedure for reusing an expression during authoring has
its own direction and scope. [Pinned upstream documentation and license](https://github.com/MicrosoftDocs/power-automate-docs/tree/e7a4c26faaa37ea3432ea7011957f3e72af745c1)

## Acquisition and reference checks

The v2 crawler recorded three approved links and discovered two
documents from six seeds. Two live acquisitions and both offline
checks returned the same eight exact source files and manifest. A
third live acquisition using the crawler copied by the Pages build
also reproduced the manifest. Git blob identities and exact citation
line and Unicode offsets were checked independently.

Two human-reviewed selections with 21 and 24 evidence rows reproduced
the same asserted 20-triple graph. Both passed the published
materializer, evidence checker, and SHACL. The private reference
contains 54 accepted evidence bundles across the claims. All 28
fixture controls passed. These include alternate sufficient sources,
structurally conforming wrong graphs, invalid shapes, and exact text
that is insufficient for the claim. This separates source integrity
and conformance from semantic support.

The Pages build and its pattern validator passed. A headless
Playwright browser loaded the catalog section and verified HTTP 200
responses for all five example files.

## Evidence retrieval experiments

The diagnostic reused a local BM25 implementation and pinned
Markdown line windows. It compared body text, heading context,
rank fusion across the query and its roles, expansion to neighboring
lines, source diversification, and whole-document retrieval. A
follow-up named both scoped endpoints for product membership and
included the requested controlled value for an aspect. It compared
the selected line intervals with the independently authored witness
alternatives. The ranking used the public scope and the addressed
claim slot. It did not use the expected class or the witness text.
These counts measure witness availability and do not measure whether
a model will cite or interpret those passages correctly.
[Claim decomposition and fine-grained evidence retrieval](https://aclanthology.org/2024.naacl-long.196/)

| Retrieval route | OpenSearch complete claims | Power Automate complete claims |
| --- | ---: | ---: |
| Body BM25, up to six windows | 1/17 | 1/20 |
| Heading BM25, up to six windows | 3/17 | 1/20 |
| Heading and role fusion, up to six windows | 3/17 | 1/20 |
| Fusion with nearby lines | 6/17 | 6/20 |
| Fusion with nearby lines and explicit scoped endpoints | 5/17 | 14/20 |
| Source diversification and expansion with scoped endpoints | 1/17 | 6/20 |
| Whole-document BM25 with scoped endpoints, best one | 6/17 | 16/20 |
| Whole-document BM25 with scoped endpoints, best two | 15/17 | 17/20 |
| Whole-document BM25 with scoped endpoints, best three | 17/17 | 20/20 |

At the best-three budget, whole-document retrieval sums 615,442
and 438,022 unique characters per claim across the two datasets,
respectively. The same source may be reused across claims. The
corpora themselves contain 92,511 and 47,325 characters. Narrow
retrieval remains a navigation aid. The paired model evaluation
retains the full approved corpus. Six retrieval controls passed
on each of Python 3.11 and 3.14, and both final results were
byte-identical between the two interpreters.

## Paired Harbor protocol

The paired development comparison assigns two GPT-6 Luna low
attempts to the published skill and two to an isolated variant,
with zero retries. Both receive the same pinned actor fixture,
tools, full source corpus, and exact output paths. The shared
publisher checks the explicit product type, roster coverage,
ownership, class exclusivity, and SHACL before replacing a result.
The held verifier checks the replay, graph, and evidence separately.

The only assigned skill delta is guidance in the product-crawl
reference to separate authoring, runtime action, and delegated
implementation, and to bind requested relationships and controls
to their own scoped witnesses. The protocol counts strict full
end-to-end passes and reports acquisition, conformance, and semantic
decisions separately. Trace review checks whether each run actually
read the reference.

Before inference, eleven verifier controls passed on Windows and
in the real Docker verifier. The actor preflight reproduced the
crawl and checked accepted and rejected publication paths. A native
zero-inference job passed through the real actor and verifier
boundary with credentials disabled.

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| Actor fixture | `e84c277571becb98d3dc12f67b0edbf4d70af58bc80e2e976f6e301c0acc7476` |
| Power Automate crawl manifest | `8b1ee4741023be8127287d0142e2166dcd3b8981ffe6dd5d8170cec3aab6af78` |
| Full development freeze | `c3ff925cacf6da606b73d2d280529ee19b343936b3e85197e58e01d221fd94de` |
| Fixture quality controls | `9a11b7d6bd5b16b0ba412644ee27da2846db2d03e9bb85db090495cc8f9b6b56` |
| Power Automate retrieval with scoped endpoints | `8358ae26afb21eceed98bd6e09578f78abb4329311742c4e184bdc8bb42e4c53` |
| OpenSearch retrieval with scoped endpoints | `c876d58b686d76a4155db27bfddc335656f05c863311ea5925244a157fa368bc` |
| Retrieval probe | `229ff1f3ab38d1617eede05696e2bf9e1a73d75f1fc0805329272d7358f1e2b2` |
| Paired Harbor protocol | `8ada2c54bb738fcc54e3c07437a05f678c5d07ad11a6ddd2313b517c25e0cc49` |
| Native zero-inference preflight | `5251cb916dfe750e7790686ede32015d96f4aa6d9e77befef09977dbc8ccc1a2` |
