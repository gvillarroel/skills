# Product feature extraction with an OpenSearch documentation crawl

This development study adds an OpenSearch 2.19 variant to the
[product feature inventory example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/README.md).
The caller supplies a fixed ontology, SHACL constraints, a roster
of seven scoped operations, and a bounded documentation specification.
The extractor produces an asserted graph, exact source evidence,
and a review of open decisions. The
[example inputs](../skills/extract-with-ontology/assets/examples/product-feature-inventory/opensearch/README.md)
are sufficient to repeat the collection and run the task.

## Acquisition and deterministic replay

The version 2 crawler walks approved inline Markdown links to
repository paths or publisher routes. It supports declared aliases
and a version prefix for the publisher's Jekyll links. It fetches
only approved files at a full GitHub commit and rejects redirects,
digest mismatches, unreachable approved files, and exceeded bounds.
The crawl preserves exact source bytes and creates a manifest. The
skill uses that manifest to resolve source IDs and verify citations.
The original GitHub Docs specification remains version 1.

Two live captures at the OpenSearch documentation commit
`f5e5e211d197f0fcee0cbf6dfc93e680b8c7ff12` collected nine sources
and 92,515 bytes. Three sources were discovered from six seeds.
Both captured the same seven in-scope links and passed offline
verification. Independent local HTTP and Linux replays matched all
source files and the manifest byte for byte. Six previously published
route aliases resolve to the same source identities. The local
transport probes reject the mutable latest route and an unapproved
same-origin page.
[Pinned upstream sources and license](https://github.com/opensearch-project/documentation-website/tree/f5e5e211d197f0fcee0cbf6dfc93e680b8c7ff12)

The regression tests cover URL and path scope, invalid spec inputs,
deterministic breadth-first traversal, retained file tampering,
partial publication, symlinks, and Windows junctions. The initial
Windows junction fix imported a Windows-only constant on Linux and
failed the actual Harbor Docker preflight before inference. The
portable fix checks the constant only on Windows. Its online and
local replay receipts match the previously frozen bytes. The final
Linux test suite passed 17 checks, with the Windows junction test
skipped on that platform.

The independent Zed and GitHub regressions exercised both spec
versions. Zed yielded nine documents and 15 links in both Python
versions. Feeding its retained source manifest and a reviewed plan
to the published materializer reproduced all 24 assertions and
exact citations byte for byte. The 14-document GitHub v1 snapshot
verified offline.
[Earlier product transfer](ontology-product-crawler-transfer-20261109.md)

The isolated Pi acquisition task used GPT-6 Luna low and the
runtime bundle alone. The first attempt created the requested
directory before invoking the crawler and eventually saved a valid
capture one level too deep. Clarifying that the crawler creates the
directory yielded two strict passes on the same prompt. A third
strict pass exercised the exact portable runtime. The three passing
attempts recovered the same bytes and discovery graph. Their
manifests differed only in the digest of the JSON specification
transcribed from the prompt. Supplying the exact same specification
file avoids that source of difference.

## Fixed ontology and scoring

The scope separates keyword ranking, supplied-vector retrieval,
local text embedding, provider-hosted text embedding, configured
request dispatch, the private endpoint response, and hybrid score
normalization. The ontology asks which operation uses a model,
where each relevant operation executes, which requests reach which
operations, and when two documented capabilities were introduced.
A private endpoint's response can establish the result shape while
leaving its implementation open. The review must ask what would
distinguish model inference from another implementation in that
specific endpoint configuration.

The reference has 31 assertions and 17 separately witnessed
obligations. Two distinct valid evidence sets passed the preflight.
The 12 frozen controls check capture integrity, reversed relations,
dispatch and inference conflation, version scope, and missing
support from another page. The reference and verifier are separate
from the actor bundle. SHACL verifies graph structure. The evaluator
also compares the exact scoped feature identities and checks
semantic evidence, version, and relation direction.
[Text embedding processor](https://docs.opensearch.org/2.19/ingest-pipelines/processors/text-embedding/) ·
[Remote model connectors](https://docs.opensearch.org/2.19/ml-commons-plugin/remote-models/connectors/) ·
[Normalization processor](https://docs.opensearch.org/2.19/search-plugins/search-pipelines/normalization-processor/)

## First paired Harbor development run

Harbor 0.18.0 ran two GPT-6 Luna low attempts per arm with zero
retries. Both arms received the same crawler, scope, ontology,
source bytes, and output contract. The candidate added an
evidence table that distinguishes behavior from mechanism,
qualifies the executor and configuration, and checks relation
direction separately. Before inference, the real Docker
environment passed the actor commands, eight verifier controls,
and a no-inference trial from crawl through artifact transfer.

All four actors retained the exact verified crawl. None passed
strict trace admission. The traces included missing ad hoc search
or SHACL commands and attempts to materialize into an existing
directory. One final artifact per arm contained all three required
extraction files. Another candidate artifact lacked the review, and
one baseline artifact stopped at the crawl. The initial experiment
provides no strict comparison of semantic quality. The acquisition
results and task controls have separate receipts.

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| Portable crawler | `661e99305a6a037a99fdb7e8a284457b32822ebaf5dc24a35a9febe2281efe6d` |
| OpenSearch crawl manifest | `3f961223615e99db597c47e9e9aa556d293dcfea57210ac9681603ffaa01b73d` |
| Frozen actor fixture | `8be898f755911c2e3dc5a6fdcf44baead77a60aaf8593dc30ba17db67703222c` |
| Frozen evaluator and references | `1c4d4d4eb0ccd9ddd8c84835aa8c7075d632b019521050553f027d625901fc97` |
| Initial 12-control receipt | `7214bd9c273e73ac35080d23488fb9b1baf3be0763289552e1eb3917e74414a6` |
| Portable Windows replay | `643806246c397ec451932e39a275a6c53d4efd8c60ae47d77e929b2cbd80367c` |
| Portable Linux replay | `a51aca91786d4768792765ae6e18f06e95e2e190f9ae2030f07b903c3c9024ec` |
| First paired Harbor protocol | `59d67f566bb49d57cdaaf5e60e94bf6c98cc895ea370976ceb2fc3875f4b50bb` |
| Native no-inference preflight | `32c8303f915c544c6017551c04853fd8c9d018ff8280114472993ffcab258238` |
| Published example browser and download audit | `f2bdd9ff9da44ddb23ef3d67929bb9a0d8ed2e550df679797551ed19da3971ec` |
