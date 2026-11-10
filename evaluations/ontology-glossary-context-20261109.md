# Contextual glossary anchors and extraction transfer

## Exact adjacent context

A glossary term or value can use exact adjacent `prefix` and
`suffix` strings to distinguish repeated occurrences in its cited
lines. All provided selectors, including `first_char`, must agree on
one token-aligned occurrence. The compiler still emits the exact
source quote and resolved offsets. When text moves within a cited
window, the same adjacent strings can locate it against the newly
pinned source.

The standalone suite passed 14/14 tests on Python 3.11 and 3.14.
An independent audit passed 44 controls on both versions, including
ambiguity, conflicting selectors, text outside the cited lines,
Unicode, line endings, and batch quarantine. V39 retained 60
proposals from 40 sources and 20 additional CLI controls. The
V40 report was unchanged over 57 CLI invocations.

Two strict GPT-6 Luna low runtime checks compiled the same supplied
contextual selectors. Both distinguished the example's attestation
from the operative definition in one line and emitted identical
ledger bytes, SHA-256
`840a42e22323d67ced6d1fb3eb9ad74c5bab13166056f91496ffa8266e70a3d4`.

A targeted drafting pilot used 12 synthetic documents with repeated
term and value spans and a specified operative scope. All six Luna
low calls were admitted. Numeric offsets produced 1/12 exact
documents and adjacent context produced 4/12, with four gains and
one loss. The context arm still missed a unique value location in
four documents and emitted an extra nested field in four others.
A shape-only replay of the nested field compiled one additional
document and kept the exact score at 4/12. The task supplied each
term, requested one operative row and left numeric offset drafting
to the model.

[W3C Text Quote Selector](https://www.w3.org/TR/annotation-model/#text-quote-selector) ·
[Glossary workflow](../skills/extract-ontologies/references/glossary.md#compile-proposals-before-assigning-identity)

## Transfer to new source documents

An independent curator froze 18 documents across 18 source families
and seven languages, with eight official excerpts and ten synthetic
controls. The cohort avoids exact-source overlap with the earlier
representation selection set. Some official publishers appeared in
earlier pilots. The scorer checks one complete accepted draft per
document, with 36 whole-draft alternatives across the cohort.
Seventeen documents were representable without a disambiguating
selector. All 18 remain in the primary denominator.

The protocol pinned the existing V41 bundle, source and scorer before
execution. Each of the three initial arms used three GPT-6 Luna low
calls, without retries. The two compact runs used identical prompts
and inputs. The review routed only documents where the compact drafts
disagreed or failed to compile. It supplied the source and both drafts
to a new call, with the first valid draft as fallback.

| Approach | Compiled documents | Exact documents | Matched proposals | Unmatched definitions or aliases |
| --- | ---: | ---: | ---: | ---: |
| Nested objects | 16/18 | 12/18 | 19/25 | 2 |
| Compact exact quotes, first run | 11/18 | 8/18 | 13/25 | 4 |
| Compact exact quotes, second run | 14/18 | 12/18 | 17/25 | 2 |
| Intersection of compiled compact drafts | 9/18 | 6/18 | 9/25 | 0 |
| Compact with selective review | 16/18 | 11/18 | 19/25 | 4 |

The compact drafts agreed on six complete ledgers, all exact. The
review routed the other twelve documents, supplied a valid draft
for nine, used the fallback once, and left two unresolved. Review
gained three exact documents over the first compact run. The complete
review strategy used 3.18 times the tokens reported for nested
objects and produced one fewer exact document. The transfer result
supports retaining the object format. The frozen score reproduced
byte for byte on Python 3.11 and 3.14.

[Chain-of-Verification](https://arxiv.org/abs/2309.11495) ·
[Earlier representation comparison](ontology-glossary-anchors-20261109.md#luna-representation-comparison)

## Evidence across passages

The retrieval prototype tests two-sentence shortlists for known
entity pairs. It repairs a BM25 shortlist only when it omits one
endpoint. The scorer keeps relation labels and evidence sentences
separate from ranking. On 600 source-disjoint DocRED articles with
annotated entity clusters, complete evidence coverage increased from
5,567 to 5,827 of 7,265 relations. For noncontiguous evidence, it rose
from 1,166 to 1,307 of 2,379.

On another 600 disjoint articles, the ranker received one surface
form per endpoint and recovered exact mentions from raw sentences.
Complete evidence coverage increased from 5,507 to 5,637 of 7,363
relations, with 139 gains and nine losses. Noncontiguous evidence
coverage increased from 1,180 to 1,258 of 2,578. The selected
source text grew from 27.49% to 27.57%. Identity-scoped bridges
helped the synthetic homonym controls, while the simpler endpoint
repair accounted for almost all of the overall gain.

The entity pair is supplied in both comparisons. These results
measure retrieval of annotated evidence, with relation discovery
and inference quality still to be evaluated.

[DocRED](https://arxiv.org/abs/1906.06127) ·
[EIDER](https://arxiv.org/abs/2106.08657) ·
[DREEAM](https://arxiv.org/abs/2302.08675)

## Native Harbor file carriers

Harbor job `a644f03f-1369-4acf-8cec-f15e489e5ee3` compared one
aggregate draft with a file per document across four new source
families. It used GPT-6 Luna low, with one attempt per family and
carrier. Forty actual Docker verifier controls and eight environment
and isolation probes passed. All eight live trials were admitted,
with zero execution errors and zero retries.

Both carriers produced 12/12 documents with exact evidence.
The aggregate passed 4/4 cases and the file-per-document carrier
passed 3/4. They used 75,192 and 110,055 reported tokens,
respectively. The sole difference was a typed lane for the adjective
`partitioned` in Kafka documentation. A separate sensitivity
replay allowing both reviewed interpretations yielded 4/4 for
each carrier. The frozen results remain unchanged. The trials
used the same grouped sources in both carriers.
