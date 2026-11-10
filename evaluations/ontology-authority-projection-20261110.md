# Scope and source authority in ontology-guided extraction

The preceding OpenSearch inventory conflated two decisions.
The caller had identified a configured destination, while the
destination's implementation remained open. One admitted artifact
withheld the route. Another asserted it using documentation about a
different provider. This study tests whether explicit evidence
requirements preserve the known routing relation and the open
implementation question independently.
[OpenSearch inventory results](ontology-product-crawler-opensearch-20261110.md)

WiCE and ProgramFC motivate verifying smaller obligations. TriQua
motivates retaining qualifiers when breaking a fact into parts. This
prototype keeps the exact scenario, role, and direction attached to
each claim while separating documentation, configuration, execution
observations, and implementation records. It treats source type as an
admission check. Sufficiency and matching scope remain separate
semantic decisions.
[WiCE](https://arxiv.org/abs/2303.01432) ·
[ProgramFC](https://aclanthology.org/2023.acl-long.386/) ·
[TriQua](https://arxiv.org/abs/2608.05228) ·
[PROV-O](https://www.w3.org/TR/prov-o/)

## Project reviewed decisions

The prototype accepts a holistic status with a flat set of
case-local evidence IDs, or separate positive and negative evidence
for each declared requirement. Both arms see the same candidate
claim, authorities, and permitted alternatives. The typed route
requires all requirements of one proof branch to support a claim.
It derives refutation when each branch has an explicit refuting
requirement. Missing evidence preserves an open decision. Competing
polarity and proof that depends only on disputed premises retain
conflict for review. A clean alternate branch can establish support.

Only supported decisions emit named triples. The typed ledger keeps
the selected evidence by requirement, and both arms emit a common
normalized decision surface. The compiler checks the supplied case
roster, case-local references, evidence authority, and declared
proof structure. A citation with the right authority can still
describe another deployment, scope, or operation.

The standalone projector passed its six test groups on both Python
3.11 and 3.14. The checked OpenSearch fixture reproduced 11 decisions
and four supported triples in both carriers, with identical fixture
bytes across interpreters. The independent n8n preflight reproduced
13 decisions and four triples from each carrier and from an alternate
reviewed citation set. Nine controls exercised wrong authorities,
wrong endpoints with the correct authority, reverse relations,
incorrect branch selection, and missing capture versus explicit
refutation.

An independent audit compared 77,204 polarity and proof-structure
cases with a separate valuation model and passed 19 command-line
controls in each of Python 3.11 and 3.14. It reproduced an initial
publication defect by forcing the evidence write to fail after the
graph write. A separate revision stages both files and publishes
them in a single same-filesystem operation with a no-replacement
condition. It passed 17 controls on each tested Windows Python
version and on Ubuntu WSL, including injected write and rename
failures, an existing destination created during the race, and two
competing subprocesses. Its successful output bytes match the
original. The native experiment uses the original frozen projector.
The staging revision tests atomic visibility on the tested file
systems and makes no power-loss durability claim.
[Python rename documentation](https://docs.python.org/3/library/os.html#os.rename) ·
[Linux renameat2](https://man7.org/linux/man-pages/man2/rename.2.html)

## Paired Harbor extraction

The native task used 11 OpenSearch and 13 n8n decisions. The
OpenSearch cases vary effective request routing, private endpoint
implementation, conflicting owner records, direction, and release.
The fresh n8n family varies workflow selection, implementation
knowledge, and human approval of the exact tool call. Its actor
packet contains 62 case-local passages from five pinned official
files. The workflow configurations, deployment statements, and
execution records are synthetic. Two fixture authoring fixes were
made before inference and their draft freezes were retained.
[OpenSearch connector blueprint](https://docs.opensearch.org/2.19/ml-commons-plugin/remote-models/blueprints/) ·
[Pinned n8n documentation](https://github.com/n8n-io/n8n-docs/tree/156b2983a0c65deac8c4d7a7bdc1b98ecffd02b6)

Harbor 0.18.0 ran two GPT-6 Luna low attempts per arm with zero
retries. Both arms received identical evidence packets and proof
requirements. The response carrier and its projection were the
experimental difference. All 30 local and actual Docker verifier
controls passed. A native no-inference trial per arm exercised
three actor commands, artifact transfer, and denied oracle access.
Both approved reference carriers emitted the same eight-triple
graph.

| Native outcome | Holistic | Typed premises |
| --- | ---: | ---: |
| Strict trace and carrier admission | 2/2 | 2/2 |
| Correct decision status | 46/48 | 48/48 |
| Correct graph admission decision | 47/48 | 48/48 |
| Joint status, graph admission, and approved evidence set | 34/48 | 39/48 |
| Joint outcome on n8n | 16/26 | 19/26 |
| Joint outcome on OpenSearch | 18/22 | 20/22 |
| Targeted review by the frozen lexical check | 7/14 | 8/14 |
| Complete exact native pass | 0/2 | 0/2 |

One holistic output asserted a route from a disabled branch and
treated an unknown implementation as refuted. The typed outputs
resolved both cases. Both typed graphs and one holistic graph
matched the eight-triple reference byte for byte. The other holistic
graph contained one extra triple. Within the typed repeats, the
selected evidence IDs differed on five cases, so the evidence
ledgers still differed. These repeats measure a fixed, scoped
development task with supplied passages and candidate triples.

An independent reviewer scored the retained artifacts with arm
identities masked. The reviewer accepted equivalent evidence when
it established the same source rule, scope, and result. The
suggested review controls included checking route activation, the
open service mechanism, and conflict. The arm mapping remained
sealed during scoring. The exact native criterion remains separate.

| Independent outcome | Holistic | Typed premises |
| --- | ---: | ---: |
| Sufficient evidence for the scoped decision | 46/48 | 48/48 |
| Known documentation rule retained where applicable | 40/48 | 48/48 |
| Direct question for an insufficient decision | 6/12 | 9/12 |
| Direct question for a conflicting decision | 0/2 | 0/2 |
| Complete decision including direct resolution where needed | 39/48 | 43/48 |

Some alternative citations support the claimed relation without
copying every approved window. Some open decisions cite only the
missing caller observation and leave the applicable documented
rule unrecorded. The audit credits the withheld outcome and tracks
rule coverage separately. All four correctly retained the
conflicting owner records. None asked which observation would
settle the disagreement. These results support further testing
with typed premises. The evaluated default skill remains on its
published workflow.

## Rule-engine contrast on Terraform and AWS

The separate clingo 5.8.2 study froze 29 paired scenarios with 58
claims before implementing the rules. It used complete pinned
Terraform AWS provider and AWS Lambda documentation and synthetic
configuration, applied mapping, and invocation records. The target
questions distinguished plan intent from observed handling of a
mixed-success SQS invocation. Each record was scoped by resource
and release, and execution records also by deployment and invocation.
[Pinned provider documentation](https://github.com/hashicorp/terraform-provider-aws/blob/92b670b8b4714cca75fa802c0ec0689b62b0c10d/website/docs/r/lambda_event_source_mapping.html.markdown#L215) ·
[Pinned AWS Lambda documentation](https://github.com/awsdocs/aws-lambda-developer-guide/blob/03f7fcb0b771f031f7cb3aa43e8b18407c00b3a8/doc_source/with-sqs.md#L199-L256) ·
[Terraform JSON plan format](https://developer.hashicorp.com/terraform/internals/json-format) ·
[clingo](https://potassco.org/clingo/)

| Rule variant | Correct decisions | Fully correct scenarios | Incorrect promotions |
| --- | ---: | ---: | ---: |
| Positive scoped joins | 44/58 | 15/29 | 8 |
| Explicit refutation, unknown and conflict | 53/58 | 24/29 | 5 |
| Conjunctive guards and alternate evidence | 58/58 | 29/29 | 0 |

The last variant required the applicable documentation, matching
applied mapping, invocation evidence, and the documented response
guard. It preserved four proof sets from two independent observations
and two documentary witnesses. All 15 metamorphic controls passed.
Reversing and interleaving the input records yielded byte-identical
results for each variant in both Python versions. The study measures
the composition of already typed facts and synthetic observations.
It includes no generative extraction or deployed AWS invocation.

## Local entailment as a referral filter

The same frozen OpenSearch and n8n actor packets supplied 24 claims,
eight of which were supported. A local quantized DeBERTa NLI model
scored 361 unique text pairs. Twenty exceeded its 512-token budget
and were omitted without truncation. This probe considers automatic
positive acceptance versus referral. Refutations, conflicts, and
insufficient cases all require referral. No reference decision
was passed to the scorer.
[Pinned NLI model](https://huggingface.co/cross-encoder/nli-deberta-v3-small/tree/fa2804872c3b4bd748f38c0185cc85775361e735)

| Method at margin 0 | Supported claims accepted | Other claims accepted in error | Referred |
| --- | ---: | ---: | ---: |
| Flat evidence against the whole claim | 3/8 | 4/16 | 17/24 |
| Same-authority evidence grouped by requirement | 3/8 | 1/16 | 20/24 |
| Best one- or two-record bundle with contradiction check | 5/8 | 5/16 | 14/24 |

At fixed margins of 1 and 2, grouping still accepted one unsupported
claim at each setting. In that case, the only implementation
record concerns the sandbox endpoint. Its source category is
correct and its endpoint is different. The bounded-bundle route
accepted four at each setting. These are development sensitivities on the same
packets. No tested route reached zero incorrect acceptances.
The raw scores and results were byte-identical on Python 3.11
and 3.12.

## Dedicated review pass

A separate native task froze the first typed trial by lexicographic
trial ID. Its six insufficient decisions and one conflict were
given to both review arms with the same source excerpts, state,
and selected evidence. Both prompts asked for a direct question
and an explanation of which answer would resolve it. The treatment
also received a machine-derived list of unresolved or disputed
requirements. The two arms used the same output fields and could
write only the review artifact. They ran twice with GPT-6 Luna low
and zero retries.

All 11 exact Docker carrier controls and both no-inference Harbor
probes passed. All four live traces and structural carriers passed.
The independent rubric was frozen before inference. It checks the
exact scope, relevant authority, a discriminating question, and a
valid mapping from an observation to the decision. It accepts
semantically equivalent wording.

| Review-only outcome | Common review prompt | Common prompt plus unresolved requirements |
| --- | ---: | ---: |
| Strict carrier and trace admission | 2/2 | 2/2 |
| Complete review decisions | 14/14 | 14/14 |
| Direct resolution question for the conflict | 2/2 | 2/2 |

The selected extraction artifact already supplied direct questions
for its six insufficient decisions. It described the conflicting
testimony without asking how to resolve it. Every dedicated review
addressed the conflict. The added requirement list gave no observed
benefit over the common review prompt in this sample. This test
measures question quality with already-fixed upstream decisions.
It leaves extraction and graph repeatability to the preceding study.
Three answers could distinguish observed nonapproval from a missing
approval record more explicitly. Their questions asked about the
actual decision for the correct call and met the frozen rubric.

## Choose the next discriminating observation

A separate deterministic probe compared lexical order, the shortest
unresolved branch, and exact expected-cost optimization on small
monotone proof formulas. It used nine structures and enumerated 158
simulated truth assignments. The inputs included the n8n task's
declared alternate proof shape, a shared guard, unequal observation
costs, a redundant branch, and an already-settled outcome. The probe
assumes independently obtainable Boolean observations with supplied
probabilities and costs. It does not model ambiguous observations or
competing testimony.
[Stochastic Boolean Function Evaluation](https://arxiv.org/abs/1303.0726) ·
[Adaptivity Gaps](https://arxiv.org/abs/2208.03810)

The adaptive policy reduced expected cost in five of nine structures
against lexical order and in three against the shortest branch.
All policies resolved every assignment correctly. For the n8n
alternate proof, equal costs and probabilities gave 39/16 expected
queries in lexical order and 31/16 with either of the other methods.
For a shared guard the adaptive method asked about that guard first
and reduced the expected count from 21/8 to 15/8. The result was
byte-identical in Python 3.11 and 3.14. This probe measures selection
over declared alternatives with simulated answers. The wording of
questions is evaluated separately.

## Prospective Terraform and AWS transfer

An independent author prepared 11 new extraction decisions from
ten scenarios selected before consulting the Luna outcomes.
The packet combines the pinned primary documents with raw JSON
excerpts for a plan, deployed mapping, and runtime observations.
It tests neighboring resource addresses, after-unknown values,
deployment scope, exact invocation IDs, explicit guard failure,
conflict, and alternate proof paths. Twenty-four controls passed
on Windows Python 3.11 and 3.14 and Ubuntu WSL Python 3.12.
Both reference carriers produced the same three-triple graph.
This package has no Luna or native semantic results yet.

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| Experimental projector | `ee901fabdf4a35ffbd9d9024da96818a0e11fafc9e9549a08f8fb83632319b55` |
| OpenSearch actor and reference freeze | `9c47c2e8f0e519e3c7257a80d4e673e83c79f5ef23430452e73e6a806cbf4306` |
| n8n actor and reference freeze | `2558fd5a2d3a5cccd2e1566b93c246f14d2588643558109d14110a2c36479e80` |
| n8n projector and semantic controls | `fa5c9aebc4c810f36d351ee2e4d8e1b06675cb75994b817d5e8d69d94b7501ac` |
| Paired native protocol | `ad287a8097523be740bd561b19602a9bd27f9d22eaa0f9dda87d48f872033369` |
| Docker and native no-inference preflight | `e27d71594dd201eb3e8a4b2d7069d31c5e71e72bbd63a86bd692af2eb5a3c443` |
| Native comparison | `5078d1a5d0a2b2e4bbf771a88d025ba0586d11412c8b790a100111e04c4c9fed` |
| Repeated graph and evidence identity | `a3eacf5582ac76f41575ed30c175d40255963c88d4d469b1b8bbf772c685c34a` |
| Independent masked semantic assessment | `9fc2ac32b7bd11920da8bff654e8e88209cac238e26b192e38b061f382450dfb` |
| Terraform fixture | `c74b514c010312090ce34ea53c32a69089a087864444fb49583af99e5de5b870` |
| Terraform independent reference | `fe2210ae558e34e6a3bfe1d49e368213f0c203834a0581c461c29e92f83fe2e6` |
| clingo cross-interpreter receipt | `cb022e3a90028c84d7c43a73cb7246b4c8ad56c8d5adf9a161b5dbdff2663810` |
| Independent projector logical and CLI audit | `8df46b4daebdc5ea707ae131218937da18c09d969673e55d9489761bfddb1527` |
| Atomic publication candidate | `e0c6841826ca4ac98dc78cb6101e893b5349a8db57468426265e9bfc15dacac3` |
| Atomic audit on Windows Python 3.11 | `43db97bdf02f7961cbdad7b07cbe555e947094596c525f081f1848d488e66f2e` |
| Atomic audit on Windows Python 3.14 | `bd8d4e9980596be64cfb7fe1020021d9e5fd4b48d52edfbf99361d350bbbe8f6` |
| Atomic audit on Ubuntu WSL Python 3.12 | `843490d0deb2ade5b10066092f3134e4efdea339a4e2d8c84cac0f2a4cc5e949` |
| Frozen NLI model receipt | `48e91fec8e08ebcf57e10314787b84d562043a5fdf230dad5ab1172cc0760a13` |
| Local NLI scores, both interpreters | `732bcb965766089181338aeadce9974cbc097de89a540a7e302e5ab4e775dd50` |
| Local NLI assessment, both interpreters | `ef14febaddeeadbcaa8257604f073bb7be8f38255c84f75a49ec5f417c343766` |
| Review-only protocol | `d3c476c7ebeeed0f929c54d9e4738b21689c60fbffc60b0c600817f601d0546b` |
| Review-only pre-inference receipt | `4caf7856801df113ba473a5c03744ec857b17c5b9c08791a90e08d33acd743c7` |
| Frozen independent review rubric | `ffab4c9bda55da709d77eeb6db827578b7a4b5809f8ef2bac79b2dd4e54f8c98` |
| Review-only native comparison | `045df45e421722b42c7da03de859cc9f77e1b281cd768ab2000508b85d02d455` |
| Review-only observed read and write boundary | `630bd5413970787a8d853580ff35d8beddfbe288eb9439bb73a18dd7eddb8c8a` |
| Review-only independent masked assessment | `637b4cff50577524f0e25a6e426c053f342c02e0c9a85c02fbfa6916fdb127f7` |
| Adaptive query order, both interpreters | `4e3f1f1726f4f3d895b69bb3c0a0f759a6c18ae0851e396a864e800239d7836e` |
| Prospective transfer actor freeze | `2b8a4d746064a501ed1e53406c9c5a317a48bbcbb9b1af30aa238c932f69eff1` |
| Prospective transfer full freeze | `aa93fae9fdfba9dfc659376f3ef41bb839986dd84bcca0f5974aa81091cacb61` |
| Prospective transfer reference and preflight controls | `510d1f47772e5310db12bc690b04d3620413615a9f640dcde9ae89e585d55096` |
