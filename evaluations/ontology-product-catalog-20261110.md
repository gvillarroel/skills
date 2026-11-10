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
Two separate glossary vocabulary inspections listed the same 14
declared terms and produced byte-identical inventories.

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
retains the full approved corpus. Eight retrieval controls passed
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

## First paired results

All four actors successfully read the assigned product reference
and rebuilt the exact crawl. All four retained artifacts passed the
mechanical verifier. One variant trace had a shell syntax error and
was excluded from strict semantic results. The blinded adjudication
was sealed before revealing arm assignment.

| Strict result | Published skill | Operation-boundary variant |
| --- | ---: | ---: |
| Exact crawl, all attempted runs | 2/2 | 2/2 |
| Mechanical artifact pass, all retained runs | 2/2 | 2/2 |
| Strict trace admission | 2/2 | 1/2 |
| Correct classifications in admitted runs | 15/16 | 8/8 |
| Correct required graph assertions in admitted runs | 39/40 | 20/20 |
| Independently sufficient selected witnesses | 27/40 | 14/20 |
| Direct resolution questions with a source authority | 0/4 | 2/2 |
| Exact reference graphs | 0/2 | 0/1 |
| Full strict semantic pass, all attempted runs | 0/2 | 0/2 |

All three admitted runs asserted the required guarded expression
reuse, but also inferred a second reuse route from a link to a
related help page. The linked page documents a general authoring
capability. The assessed property requires the specific transfer
into the target setting. One run transferred a named model provider
across feature boundaries. The other missed an explicit fixed trigger
rule. With the governing text around selected citations, the
reviewer found support for 59/60 required assertions. The selected
witnesses alone supported 41/60. All three reviews distinguished a
documented control from the organization's effective settings.

The excluded artifact was separately scored at 8/8 classes and
16/20 sufficiently cited required assertions. The two retained
variant graphs agree on the eight classes but differ on a named
provider edge. Both baseline graphs differ even after excluding
labels. Native trace distillation verified both skill locks on the
matching Linux runtime and normalized both jobs separately. Each
pool contains two trials with one task checksum. This experiment
cannot establish the trace diversity required for a patch or the
repeatability of independent graph generation.

A separate read-only replay expanded the selected citations by
one, two, or four lines on each side, refusing expansions above
1,800 characters. It did not add source IDs or alter the graph.
Among the 60 required assertions in admitted runs, selected line
intervals enclosing a frozen valid witness bundle went from 13 to
13, 26, and 30, respectively. Four-line expansion increased cited
characters from 25,438 to 47,051. This measures interval coverage.
The blinded sufficiency scores and original artifacts remain fixed.

## Exact authority variant

A second paired run reuses the exact task, baseline, actor tools,
mechanical verifier, and primary semantic criteria. The revised
reference asks for the produced value, receiving setting, and
documented transfer action for a directed reuse claim. It attaches
named providers and scopes to the exact operation and checks whether
a review statement describes a selected witness or consulted text.
Eleven Docker verifier controls and the native zero-inference gate
passed before the four new Luna low attempts.

| Strict result | Published skill | Exact-authority variant |
| --- | ---: | ---: |
| Exact crawl and mechanical artifact pass, all retained runs | 2/2 | 2/2 |
| Strict trace admission | 1/2 | 1/2 |
| Correct classifications in admitted runs | 8/8 | 8/8 |
| Correct required graph assertions in admitted runs | 20/20 | 20/20 |
| Independently sufficient selected witnesses | 15/20 | 14/20 |
| Direct resolution questions with a source authority | 0/2 | 2/2 |
| Unsupported assertions in admitted runs | 2 | 1 |
| Full strict semantic pass, all attempted runs | 0/2 | 0/2 |

The baseline exclusion attempted to repeat the crawl into an existing
directory. The variant exclusion misread the numbered-source response
and tried to open a path outside the workspace. All four retained
artifacts passed source, roster, replay and SHACL checks. Both pairs
agreed on all eight classes and differed on the provider assertion.
With one admitted run per arm, strict repeatability is unmeasured
in this comparison.

A second masked reviewer confirmed that all eight retained graphs
added the unsupported assistant-to-trigger edge and correctly
preserved the explicit Filter array-to-trigger relation. Across all
five admitted runs, the full source attached the named provider to
cloud-flow authoring, but none of the chosen passages identified
that operation under the second reviewer's exact-scope criterion.
The reviewer also confirmed that each variant's sole admitted run
asked both direct questions. The first and second comparisons share
one development family and do not qualify either variant for release.

A third experiment has been designed to check each optional
asserted relation against its selected source intervals after draft
extraction. It would let the reviewer propose removal while locking
the product, ownership and class assertions, and measure changes in
precision and coverage separately. This experiment has not run.

## Prospective independent check

A curator prepared a separate product family with private evaluator
data. Two live crawls and two offline checks reproduced eight source
files, including four non-seed discoveries. The pinned verifier
passed 15 proof controls and five acquisition controls. Two valid
witness plans produced the same 25-assertion reference graph. The
provisional actor could read its own inputs and could not read
evaluator files. Native registration, executor-specific access
checks, and blinded semantic calibration remain pending. No model
has accessed this family.

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
| First native comparison | `1e9abece7454baa60b7cefdff130c3fcf580cf462673c1612a96689a0cbee907` |
| First independent masked assessment | `9329299846feee46a87c9d657bdf55f0a4ba9e46b1b249ed9b688be5b10431df` |
| First repeat signatures | `feb64953b6e21cde8f20003be1b91ed081fb158909bbedfd077efdfa8e78a234` |
| First baseline trace pool | `2fc6791665df19a574ebb3631f9639f8b20b455163a1800fb69eba4752fab329` |
| First variant trace pool | `5f667a20afbe04047000c8bd8df43a099fce74e69104ce0d9a44eb9ff157a332` |
| Citation context replay | `85c7e4b8fb64f5df839d43865d1405823b9017bd2c93bd6f1fd295043627784a` |
| Second paired Harbor protocol | `da904251cc0a8b79732f3cbba71f68d4cc3c003a0cedcb5126babb6e00140526` |
| Second native zero-inference preflight | `ef9d8a3e298990bbd4cffdbfde2320b1b29b653e4627d4fd9e9340490ba72d6e` |
| Second native comparison | `96c4628b82475a4bdfcbd0eadb31c3b6dd41e2d3a9d8b40ca12cfaed10ccc860` |
| Second independent masked assessment | `42b0a64d75d3d6416f278af2edbcf6a432367297ec345b7f0caaf378137eebd4` |
| Second repeat signatures | `6b70d291ae215a02445d61692c452b2a673243218e6aca9423336f617ee9d954` |
| Independent relation and question audit, first comparison | `9f76c86d9070376903b0dedf3190235dd8d69ec7640914b1781f542354007b50` |
| Independent relation and question audit, second comparison | `ee3e37f3f7b7d36f60ed9239f1e757710b4a6025e292e3bccef455fa05d1ce3f` |
| Prospective curator proof controls | `b4bcfdc116abbf616520c7f6787dd9c40f55435dc27976346bf12437cc40cb59` |
| Glossary vocabulary inventory | `afe237ce669a477d5a290f9f0a18627c7dbac1404dc91fa7cbe79429ecce9037` |
