# Manifest-backed source views for ontology citations

The `lines` command accepts an optional `--manifest` argument in
place of the explicit SHA-256. It looks up the exact relative
`path` in a manifest's `sources` array and uses that row's
`sha256` to check the local snapshot. Existing numbered ranges,
source-root containment and the output JSON remain compatible.
The product crawler example uses the saved manifest directly.
[Product example](../skills/extract-with-ontology/assets/examples/product-feature-inventory/README.md)

## Reproduced execution problem

Two V46 native actor traces transcribed an exact 64-character
SHA-256 with an extra trailing character. The numbered view
rejected both calls as mismatches. A replay on the original
pinned files reproduced both failures. The manifest option
returned the same numbered JSON bytes as both corrected
explicit SHA-256 calls, without any model calls or changes
to the native study results. [V46 native development](ontology-direct-evidence-questions-20261109.md#native-harbor-development)

An independent audit passed 46 controls on Python 3.11 and
again on 3.14, with byte-identical reports. All 14 actual
crawler source views matched the explicit SHA route and
independent line extraction. The audit checked duplicate JSON
keys and path rows, missing or malformed pins, exact local
paths, stale sources, line boundaries and create-only output.
Both versions reproduced the 47-assertion product graph and
its evidence bytes. Nine binding and view tests plus four
materializer tests passed in each interpreter. The crawler,
shape controls and Pages build also passed.

## Isolated product transfer

The exact same four-feature product task ran twice with each
skill in strict Pi. The actor received the pinned GitHub Docs
manifest, supplied ontology and existing shapes. Each cell used
GPT-6 Luna low once and zero retries. All four traces were
admitted and each actor used the installed numbered tool.
Both candidate executions used the manifest flag. The two
published-skill executions used explicit SHA arguments.

| Result | Explicit SHA | Manifest option |
| --- | ---: | ---: |
| Strict admissions | 2/2 | 2/2 |
| Expected feature classifications | 8/8 | 8/8 |
| Exact graph | 2/2 | 0/2 |
| Graphs conforming to the supplied SHACL | 2/2 | 2/2 |
| Source pins and quote coverage | 2/2 | 2/2 |

Both manifest runs asserted a reverse `relatedFeature` edge
from auto-merge to Agent Merge in addition to the forward
edge. One also omitted the required-status-checks dependency.
The reverse relation cites a real cross-reference in the
auto-merge documentation. The broad predicate covers use,
requirements and contrast, which leaves the direction of
this cross-reference open to interpretation. The frozen graph
oracle requires the reviewed direction. The materializer and
SHACL checks do not decide relation semantics.

This slice compares execution and reproducibility on one
product task with two repetitions. The manifest option
provides a deterministic remedy for the observed hash
transcription failure. It is documented as an alternative
view input. The general extraction guidance retains the
explicit SHA example and the released product vocabulary
retains its existing graph contract.

## Typed relationship follow-up

A diagnostic follow-up used the same manifest-enabled skill,
source slice and product classes in two fresh Luna low attempts.
The ontology and matching task wording separated
`preparesFor`, where a source operation establishes a condition
for a later operation, from `requiresFeature`, where an explicit
condition must pass before the subject acts. The exact two
relationships and shapes were frozen before execution.

| Result | Broad relation | Typed relations |
| --- | ---: | ---: |
| Strict admissions | 2/2 | 2/2 |
| Expected directed edges | 3/4 | 4/4 |
| Extra directed edges | 2 | 0 |
| Expected feature classifications | 8/8 | 7/8 |
| Exact full graph | 0/2 | 1/2 |

Both typed runs reproduced the two intended arrows. One classified
the required status checks as unclassified. The experiment suggests
that a more specific predicate can reduce direction ambiguity on
this slice. The fixture uses the existing four-feature corpus, so
the results are a diagnostic follow-up with two repetitions. The
typed schema remains in the study archive.

## Receipts

| Local receipt | SHA-256 |
| --- | --- |
| Native hash replay | `7bc177ca757b420fece9ff464ed7b56680b485c9eaec6d4d73d7aaa052f21932` |
| Independent manifest audit | `04167869eb7ea60e414b49793950f5af5ea6fdd78ecf91167654afa8882fae99` |
| Product transfer protocol | `fe7de7bd63951b755c780bf24b6a7fdc9f4fd1bd7ca48f0a0e7efaba2d286925` |
| Product transfer results | `8f071a9a5f68098bac32d0abbb9dcd982cdf065b750014e3332aa165e625b41a` |
| Typed relation protocol | `dde64d1dc479708b841374ccb141956521b421dd581915c7d2df8cb571b04303` |
| Typed relation results | `db308d7e5f4c1af807b7c6d8ac9a990291432b44702e230f3dabf1c6ca0763d4` |
