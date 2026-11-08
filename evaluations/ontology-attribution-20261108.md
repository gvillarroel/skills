# Direct, joint, and derived ontology evidence

The earlier scope study found six equivalent Fetch graphs that
missed an axiom assigned to one particular premise. Two concepts are
involved. Minimal formal support identifies which axioms suffice for an
entailment. Source attribution identifies which text licenses asserting
those axioms. WiCE separates claim components and their necessary
evidence. VitaminC uses near-identical source contrasts to test whether
the decisive evidence changes the verdict. [Axiom
Pinpointing](https://arxiv.org/abs/2003.08298), [WiCE](https://aclanthology.org/2023.emnlp-main.470/),
and [VitaminC](https://aclanthology.org/2021.naacl-main.52/).

## Archived attribution audit

Fetch's IDL assigns a type to the exposed attribute. The disputed prose
instead types a stream within the internal body. The getter explicitly
connects those layers in the specification, and its text was outside
the archived packet. A global range in the frozen reference entails
the local target restriction independently of the disputed attribution.
The frozen score remains unchanged. [Body composition](https://fetch.spec.whatwg.org/#concept-body)
and [body getter](https://fetch.spec.whatwg.org/#dom-body-body).

In Java, four of five aligned drafts were equivalent as a whole.
They differed in where they placed the presence or emptiness rules.
A global range also made two maximum-zero formulations equivalent as
a whole while their isolated premises differed. The remaining aligned
draft added a converse that the source wording can support and that
the scoped reference did not include. The sixth draft failed anchor
admission on a one-character type parameter. [Java Optional
specification](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html).

An offline HermiT probe passed 18/18 checks. The global range alone
entails the local target, while the internal role and the reversed
public role do not. Two reviewed formal statements together imply a
third that neither alone implies. The Java forward rule does not imply
its converse. Explicit zero values support a classification only when
the converse is present. The probe distinguishes an inconsistent
background from an entailment.

## Matched comparison

Three policies share one fixed-roster draft per case and round. The
direct policy uses that draft. Ordinary review may change both the
axioms and their evidence rows. Attribution review takes the same
draft's axioms without the original evidence assignments. It can name
one or more source owners and governing context for each axiom. The
host requires the exact same asserted Functional Syntax. An unsupported
candidate or unresolved draft prevents a revised attribution artifact.
Each review policy uses one extra Luna call. A strict success requires
whole and premise-level semantic correctness, and a strict pair also
requires identical canonical RDF in both rounds.

| Cohort | Direct strict trials / pairs | Ordinary review strict trials / pairs | Fixed-graph attribution strict trials / pairs |
| --- | --- | --- | --- |
| Archived Fetch and Java, 12 physical receipts | 0/4 · 0/2 | 0/4 · 0/2 | 0/4 · 0/2 |
| Public diagnostic v1, 24 physical receipts | 2/8 · 1/4 | 0/8 · 0/4 | 1/8 · 0/4 |
| Exact excerpts with coordinate guard v2, 24 physical receipts | 5/8 · 2/4 | 5/8 · 2/4 | 5/8 · 2/4 |
| Clarified projection v3, 24 physical receipts | 7/8 · 3/4 | 7/8 · 3/4 | 7/8 · 3/4 |

The four public cases cover independent evidence for a duplicate axiom,
directional property declarations, several restrictions from one row,
and joint support across rows. [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html#section-3),
[PROV-O](https://www.w3.org/TR/2013/REC-prov-o-20130430/),
[RFC 3339](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.6), and
[RDF 1.1 Concepts](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/).

Three source packets were edited during the first run. The scorer
detected the digest mismatch. All four exact originals were restored
from the captured request bodies and verified against the pre-run
digests in a separate directory. The run was then scored against
unchanged references. The v1 PROV reference had a roster defect
and misplaced the inverse. The RFC 3339 task scope requested numeric
ranges that the fixed roster could not express. The ambiguous JSON
direction also allowed a stronger reading of the grammar row. These
results are diagnostics and are not clean prospective quality estimates.

An independent replay removed only the exact vocabulary metadata
coordinate from context arrays. It preserved all source owners and
unresolved gaps and did not change the graph. RDF 1.1 round one then
passed, raising the attribution arm from 1/8 to 2/8 and from 0/4 to
1/4 strict pairs. The reference audit still rejected the RFC 3339 gaps
and did not repair the PROV or JSON cases. No new model calls were used.

The v2 fixture verified every excerpt against its pinned source with
normalized whitespace and kept the complete PROV roster and the
inverse with the premise that states it. The v2 prompts explicitly
separate the term registry from numbered evidence coordinates.
Attribution admitted six of eight artifacts. The two remaining holds
were the unresolved RFC 3339 scope rows. V2 changed both excerpts
and actor guidance, so the increase over v1 cannot isolate a causal
prompt effect.

The v3 scope explicitly excludes numeric ranges from the RFC 3339
component abstraction and reverse classification from the RFC 8259
value taxonomy. All four source packets passed exact-excerpt checks
and the verifier rejected all four wrong-attribution controls while
preserving whole-graph equivalence. Every v3 policy passed both
rounds for PROV-O, RFC 3339 and RFC 8259. All three failed RDF 1.1
round one. The draft used qualified exact-one restrictions for triple
components, while the reference required only existence. Ordinary
review also inlined the component rules into the graph's target
restriction. Graph-preserving attribution correctly could not change
the cardinalities. Neither extra review call improved the final score.

A separate retrospective reference uses qualified exact-one
restrictions for the three RDF component roles. In round one the
direct and fixed-graph outputs pass both whole and premise checks
against that reference. Ordinary review passes whole equivalence and
still fails premise attribution. All round-two outputs fail whole
equivalence under exact-one. This swaps which round satisfies the
scope and leaves the RDF repeatability failure unchanged. The v3
primary result remains frozen. Replay SHA-256
`cc94cbfc29face8c67f8907161cc773e83588a2310ef4e6a2a140659f18ee0b8`.

## Skill integration

The authoring reference now explains direct, joint, and derived
support and distinguishes evidence passages from vocabulary metadata.
An isolated review fixture checks an independently supported
duplicate, a background-only derivation, a necessary two-passage link,
a misleading internal reference and an unsupported existence claim.
The published baseline and revised bundle each passed 5/5 decisions
with exact evidence sets. The revised strict run
`semantic-attribution-candidate-20261108-b` also loaded the updated
reference during the review. The score is a tie on this fixture.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-attribution-review.md --run-id semantic-attribution-review-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output findings.json
uv run --script evaluations/contracts/grade_ontology_attribution_review.py evaluations/runs/semantic-attribution-review-replay/workspace
```

## Reproduction and boundary

Raw prompts, model receipts, archived graphs, manifests, and offline
controls are under
`projects/semantic-skill-evaluation/artifacts/ontology-attribution-20261108/`.
The frozen v1 fresh score SHA-256 is
`96d16ac7df1d4aeaece8b61365a4435e176f6fc9e65a9294ab7bea980ff29a04`.
The coordinate replay SHA-256 is
`da68f61494962d7b24621793b1e800d962e2c4468b86a95973351c2014145d5b`.
The formal probe SHA-256 is
`42bc4c52d09a88be062277d6b645e198e149fd1be2e4404c9d2cf9e117054a7e`.
The v3 preflight SHA-256 is
`deba7b72141159b215e2a84696ee2ff4968b471d4dab0e52673b3e4b18dffcce`.
The v3 score SHA-256 is
`9c34b1acf7cc1eba11a243493db68ae5750508a8b3f4d23e3a9eb906d1141e03`.
These are bounded public development studies. The independent Harbor
promotion gate is separate.
