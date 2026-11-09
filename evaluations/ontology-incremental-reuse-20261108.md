# Reuse approved OWL premises across source revisions

The planner treats reuse as a decision about reviewed inputs. It binds
the source unit, authoring profile and prior ledger, then traces the
governing source units and watched membership sets in both versions.
An empty reviewed exception set has a distinct state. An incomplete
or unavailable set leaves its dependent rows for recomputation. The
planner also preserves relative order within the reviewed closure.

The experiment builds on verifying traces and change propagation.
The earlier accepted-baseline guard in this repository compared a
closed authority region and one declared selector. This study adds
transitive reads, named selector memberships and exact per-version
input pins. [Self-adjusting computation](https://arxiv.org/abs/1106.0478) · [Verifying traces](https://simon.peytonjones.org/assets/pdfs/build-systems-original.pdf)

## Decision controls

Eleven synthetic revision pairs contain 41 head premises. Sixteen are
eligible to reuse. The independent oracle separates semantic change,
source identity, evidence refresh, and unresolved authority.

| Policy | Correct decisions | Unsafe reuses | Eligible reuses missed |
| --- | ---: | ---: | ---: |
| Whole source equality | 25/41 | 0 | 16 |
| Identical own text | 28/41 | 13 | 0 |
| Reviewed immediate reads | 38/41 | 3 | 0 |
| Transitive reviewed reads | 39/41 | 2 | 0 |
| Transitive reads and watched sets | 41/41 | 0 | 0 |

The transitive-only policy overlooks two default and exception
cases. The watched policy detects the first authority in a previously
empty set and changes in replacement membership. These results
assume the dependency reviews are complete.

## Archived evidence baseline

An independent audit reproduced seven archived native Harbor reference
pairs and all 70 exact source citations. Known-correct recomputation
gave a retrospective ceiling. Identical own text kept three complete
pairs, while the watched policy kept all seven and reused eight
source lines. Expanding reviewed selector members into explicit reads
also kept all seven. A stronger literal baseline reanchored all
complete old citations and invalidated duplicate class IDs at the
merge. It kept all seven and reused 15 lines. The archived citations
already contained the affected governing context in these cases.
This comparison measures routing and assembly given a correct fallback.

## Four real public revisions

The study pins eight exact snapshots from four repositories. HermiT
confirmed the author-reviewed labels on all 14 isolated premise pairs.
Five premises retain their meaning and nine change under their
declared projections. Four changing premises retain identical own
text. The preflight accepted eight full references and eight logical
alternates, rejected eight same-whole-graph attribution swaps, and
rejected eight omitted-row controls.

The two authoring arms used the same typed grammar and full head
source with only the target ID roster changed. Both made eight
independent tool-disabled Luna requests. The incremental host reused
the approved before rows selected by the reviewed policy. The oracle
verified exact typed signature, consistency, whole-ontology and
isolated premise equivalence. Exact correct repeats require equal
canonical RDF, Functional Syntax and premise-ledger SHA-256.

| Arm | Correct head ontologies | Exact correct pairs | Rows requested | Total provider tokens |
| --- | ---: | ---: | ---: | ---: |
| Complete head extraction | 1/8 | 0/4 | 28 | 38,782 |
| Watched overlay using the same complete drafts | 1/8 | 0/4 | 18 selected for recompute | No added calls |
| Watched target-only extraction | 2/8 | 1/4 | 18 | 36,852 |

The one improved trial was the second OCI repetition. Carrying the
approved independent row and a fresh targeted draft supplied
different missing parts of that case. The target-only route requested
35.7 percent fewer rows and spent 5.0 percent fewer provider tokens
in this study. Those figures exclude prior approval and dependency
review. Both routes still had six or more failed trials.

Immediate reads, transitive reads and watched sets made the same
14 decisions on this real cohort. The synthetic controls isolate
the additional value of depth-two propagation and empty membership.

Using known-correct recomputation, the watched policy reaches four
complete heads. Literal reuse reaches one. This is a routing ceiling
and is separate from model authoring. An independent audit checked
the 16 provider receipts, all 68 scored artifact instances, and the
reported route accuracy. It rederived the route labels from the
earlier pinned formal audit because the first scorer did not directly
bind the textual reuse-oracle files in its run lock.
[Compose](https://github.com/compose-spec/compose-spec/pull/376) · [OCI Runtime](https://github.com/opencontainers/runtime-spec/pull/1324) · [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification/pull/1269) · [MCP](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2106)

## Authoring with the approved interpretation

A second matched study used the same four public pairs, reviewed
reuse plan and 18 requested rows per arm. Each arm made eight new
independent, tool-disabled Luna calls. Both saw the complete head
source and the reviewed authority trace for each target. The
transition arm also saw the preceding source, approved prior OWL
rows for the targets where available, and instructions to preserve
only assertions that the head still licenses. It saw no approved
head rows for the targets. The independent audit matched all 16
provider user messages, verified the input separation and reproduced
the following scores.

| Arm | Correct head ontologies | Exact correct raw pairs | Total provider tokens |
| --- | ---: | ---: | ---: |
| Reviewed authority trace | 2/8 | 1/4 | 43,634 |
| Reviewed trace and approved prior interpretation | 6/8 | 1/4 | 33,851 |

Four matched runs passed only with transition, two passed in both
arms and two failed in both. One transition failure was rejected at
actor admission. The other failed semantic verification. The
comparison measures the joint effect of prior source, prior formal
rows and edit instructions. These sources had already been inspected
for development. Provider totals exclude prior authoring and review.

The two correct Compose outputs used different OWL forms for the
absence of a declared build context. An experimental comparison view
rewrites qualified maximum-zero to the complement of an existential
on the same property and filler before Boolean normalization. The
original asserted graph and premise ledger remain intact. HermiT
accepted all six distinct view proofs, checking whole-ontology and
per-premise equivalence against the original artifacts. The
transition arm kept one exact correct pair with the existing Boolean
view and had two with the additional rewrite. The trace arm kept
one. This retrospective replay used zero model calls. The rewrite
is experimental.

The independent provider audit SHA-256 is
`39bf0070e22235f80e47187cfcab713a80e1ad244d950064107f35e45b55773e`.
The comparison replay SHA-256 is
`6628422f0c4db56814e8f3ca7af7353b0d6f1d22703115ccb6f3387bdb3c98a2`.

## Dependency proposal and release boundary

Luna proposed dependency sidecars on eight public development pairs.
The unreviewed proposals obtained 25/28 correct decisions, with one
unsafe reuse and two eligible reuses missed. The published CLI
requires exact pinned review inputs and a prior ledger. It treats
missing authority, unresolved prior rows, and changed authoring
profiles as recomputation conditions. Planning and graph approval
remain separate.

A separate eight-call Luna reviewer let all ten proposed reuses
through, including the unsafe case. The example has two clauses
with identical text in the prior revision and one in the head.
Editorial IDs could be reassigned, so identical content did not
establish historical clause identity. An offline retrospective guard
deferred proposals with duplicate exact text in either version.
It reached 26/28 and held the one unsafe proposal. Two eligible
reuses were still missed. This guard was designed after observing
the error and applies only to the experiment with unreviewed IDs.
A reviewed stable identity can distinguish duplicate clauses.

Eight executable repository tests passed. The independent CLI
audit matched all 41 expected decisions, repeated all 11 result
files byte for byte, and passed nine boundary controls. Two final
strict isolated Luna executions each produced the three expected
decisions and the same exact plan bytes. The isolation receipt
SHA-256 is
`2caadf6ef581789b6e3cdd85b4a6c480a271638df208510a175a789ad33667cf`.
The result certifies the scoped planning workflow on its supplied
review input. The separate ontology generation promotion gate
remains open.
