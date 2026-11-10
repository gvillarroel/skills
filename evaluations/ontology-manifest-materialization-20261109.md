# Manifest-backed materialization for supplied ontologies

The `bind` and `materialize` commands can use the source roster
and byte pins from a saved manifest. The extraction plan supplies
only the assertions and their source line ranges. The command
verifies the complete manifest against the retained corpus, derives
the exact citations, and preserves the existing evidence format.
An explicit plan with its own source roster remains supported.

This addresses the copied-hash failure observed when producing
extraction plans in the [independent review study](ontology-scoped-decision-ledger-20261109.md).
A plan still needs the exact source identifier on each assertion
and an unused result directory.

## Reproducibility and integrity

The independent CLI audit passed 55 controls on each of Python
3.11 and 3.14 with zero skips. It covered legacy binding,
materialization and source views, identifier resolution, duplicate
or conflicting identifiers, path confinement, tampered and unused
sources, assertion permutations, and existing outputs. The nine
binding tests and six materializer tests passed on each interpreter.

For the GitHub product example, the explicit and manifest modes
reproduced identical graph and evidence files from 47 assertions
and 14 pinned sources. The graph also conformed to the supplied
SHACL shapes. The one-statement plan in the guide produced the
documented auto-merge classification. The downloadable inventory
scope gives the 13 target IRIs and labels to the extractor. The
reference graph, evidence and review can be reserved for scoring.
[Runnable example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/README.md)

On Windows, both versions showed the same legacy Unicode encoding
error on a default redirected `bind` stdout. Explicit `--output`
and a UTF-8-configured pipe produced the expected bytes.

## Native tooling comparison

Two new synthetic cases used the same actor instructions and
exact manifest views in both arms. Harbor 0.18.0 ran GPT-6 Luna low
once per cell with zero retries. The 16 verifier controls passed
locally and in pinned Docker. The local preflight also exercised
12 actual materializer calls and eight exact source views.

| Outcome | Explicit roster | Manifest-backed |
| --- | ---: | ---: |
| Strictly admitted and full passes | 1/2 | 1/2 |
| Retained supported assertions | 23/24 | 23/24 |
| Retained output with exact source roster and SHACL conformity | 2/2 | 2/2 |
| Successful numbered views | 4/4 | 4/4 |
| Retained assertions-only plans using the manifest route | 0/2 | 2/2 |

The strictly admitted pair produced identical graph and evidence
bytes. The other case used a short source ID where the manifest
required the exact path. Both modes rejected that assertion ID in
a mechanical replay. The candidate also attempted to write to a
pre-created output directory. The retained graphs in that case
differed. Both missed one fully supported assertion, with an
insufficient calibration citation in the explicit arm and a
classification as unknown in the manifest arm. This pilot
demonstrates uptake and removes source-roster transcription from
the successful path. Strict reliability and retained semantic
scores were unchanged across the two arms.

## Reproducibility receipts

| Receipt | SHA-256 |
| --- | --- |
| GitHub product graph | `29932eeb33e0096b5350c4f1706ccf6c96ead7676f6283a7acf51abe8ce3b900` |
| GitHub product line-bound evidence | `e8c643c82c8e5572f3626195e832317acc53d8ae3d1990315ea3b51a802af3d7` |
| Independent audit, both interpreter reports | `78908af6dea281e4a0c17f2ba68903f77599e0dc32b11327979d2b282555698a` |
| Native comparison protocol | `f02f2ed5ab72320579a584572a620393f1c6a89762c69158b68c82f994478c31` |
| Native paired comparison | `4e2e2df1a2ab74d03792dd0d8dcebcf0e8b2b13e0355c0895ee8b8fa1e722bfa` |
| Native normalized lock audit | `79b2706b3876f2ac7c2ddc23f524ccbaffce46433fbc0510f894c6c60d8d7883` |
| Exact source ID replay | `64b2ed997d0be9f7d7ba129f72e6b84235f6a8be0036febb599c3a967bcf8cf3` |

The native job IDs are `df6edf81-4630-47be-90e5-c2d6777abb9a`
and `0756427e-06a4-4c9c-b4b4-a4bc83bf9ac7`.
