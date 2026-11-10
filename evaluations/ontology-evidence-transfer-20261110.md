# Evidence verification and directed relation transfer

V50 measured three ways to improve source-grounded inventory
extraction. It transferred relation identifiers that spell out the
subject, predicate and object, compared direct and structured evidence
judgments with GPT-6 Luna low, and evaluated a local entailment model
as a selective route into Luna. The experiments keep graph correctness,
citation sufficiency and execution admission separate.

The literature motivates several distinct checks. Evidence ablation
tests whether a conclusion depends on its operative witness. The
attribution studies distinguish exact source support from support
against a compressed representation. The experiments below retain the
source spans and include tempting nearby or reversed claims.
[Evidence ablation](https://arxiv.org/abs/2609.08943) ·
[Attribution and verification](https://arxiv.org/abs/2604.21193) ·
[The attribution-compression frontier](https://arxiv.org/abs/2609.14245)

## GitLab relation address transfer

The independent transfer uses six official documents from GitLab
commit `0e842e9d238cd11398afe923838497280fdd5dd7`. It covers seven
operations and both orientations of three guarded relations.
Eight fixture controls checked alternate valid witnesses, reverse
direction with an exact quote, lost guards, a neighboring AI
passage and altered evidence. Two valid ledgers produced identical
reference RDF. The model workspace and the oracle were separate.

The paired Harbor comparison used the same compiler and task
bytes except for the six relation IDs and their verifier mirror.
Two Luna low attempts per arm ran with zero retries. Twenty local
and Docker controls and two actual no-inference boundary probes
passed.

| GitLab metric | Ordinal IDs | IDs naming subject, predicate and object |
| --- | ---: | ---: |
| Strict execution admissions | 1/2 | 0/2 |
| Retained structural and SHACL passes | 2/2 | 2/2 |
| Correct scoped classifications | 14/14 | 14/14 |
| Sufficient class witnesses in the masked review | 14/14 | 12/14 |
| Correctly directed relations with sufficient scope evidence | 1/6 | 4/6 |
| Reversed edges | 4 | 2 |
| Correct addressed relation denials | 2/6 | 4/6 |
| Direct open-mechanism questions | 1/2 | 1/2 |
| Complete semantic artifacts | 0/2 | 0/2 |
| Equal graph across repeats | No | Yes |

The actors tried to invoke `rg`, absent from the pinned image.
Preflight missed that availability mismatch. Other strict findings
included a malformed shell loop and a missing question for an
unresolved feature. The recovered artifacts passed exact plan
replay. The retained outcomes and the execution admissions are
scored separately.

The role-addressed graphs recovered the external check direction
and the artifact publication direction. Both still treated the
deploy job as the cause of delay. The reviewed source describes the
included optional test as the prerequisite that can delay deploy.
The actor identified the operation waiting and assigned it as
subject of the inverse predicate.

A model-free probe represented the source example as four reviewed
Boolean atoms. The published consequence CLI entailed the two
scoped branches for an optional job present or absent and returned
counterexamples for reversed necessity, dropping the presence
guard, and reading optional as incapable of blocking. An independent
enumeration matched all five classifications across 16 assignments.
Six assignments satisfy the reviewed premises. The model considers
eligibility under the listed dependencies separately from actual
start time.
[GitLab optional dependency example](https://gitlab.com/gitlab-org/gitlab/-/blob/0e842e9d238cd11398afe923838497280fdd5dd7/doc/ci/yaml/needs.md#L444-492)

## Structured review of fixed passages

Four native Harbor trials used the same 12 decisions and source
passages from Zed, Home Assistant and Kubernetes. Both variants
returned a verdict and selected evidence. The structured version
also identified the operation, actor and governing condition,
rejected distracting passages, and asked for a decisive missing
fact. Fourteen carrier controls passed in local and Docker preflight.
Both arms ran two Luna low attempts without retries, with all four
strictly admitted.

| Metric | Direct | Structured |
| --- | ---: | ---: |
| Native complete passes | 1/2 | 1/2 |
| Correct verdict | 23/24 | 23/24 |
| Exact supporting evidence set | 23/24 | 24/24 |
| Correct verdict and evidence together | 22/24 | 23/24 |
| Same verdict and evidence across repetitions | 9/12 | 11/12 |
| Specific question for an unknown in independent review | 3/4 | 3/4 |

The one joint gain came from preserving both the Parallel policy
scope and the rolling update condition on `maxUnavailable` in
Kubernetes. One repetition per arm still called the Zed compound
reverse claim insufficient when a necessary part of it was already
contradicted. An independent masked subset check confirmed both
diagnoses. The structured extra fields met 17/24 role checks and
19/24 distractor checks. Its output token total was 2,855 versus
1,285 and the reported cost was approximately 43% higher.
This measures judgment over provided passages.
[Kubernetes StatefulSets](https://github.com/kubernetes/website/blob/7e043a0539947ec11ef64ce3cdcc780de39c6263/content/en/docs/concepts/workloads/controllers/statefulset.md) ·
[Zed Edit Prediction](https://github.com/zed-industries/zed/blob/c84af5b99cbc366d675064e52b23664a015b6e35/docs/src/ai/edit-prediction.md)

## Local verifier and selective Luna review

The local experiment used the publisher's quantized DeBERTa NLI
checkpoint on CPU, pinned to `fa2804872c3b4bd748f38c0185cc85775361e735`.
Its upstream LFS digest matched the downloaded model. Scoring
reads source bytes from SHA-256 manifests, composes exact candidate
line spans, and runs without truncation. No source text leaves the
machine during local inference. The development and Docker scoring
files reproduced byte for byte on Python 3.11 and 3.12.
[Published NLI model and license](https://huggingface.co/cross-encoder/nli-deberta-v3-small/tree/fa2804872c3b4bd748f38c0185cc85775361e735)

Nine development decisions used Zed and Home Assistant evidence.
For each method, calibration optimized balanced accuracy across
supported and insufficient candidate bundles, with a tie preference
for fewer false accepts. Variant selection then used case accuracy
and false accepts. Contrastive NLI tied the direct version at 4/9
development decisions. The selection and thresholds froze before
the Docker and Caddy inference. The Docker and Caddy options were
independently reviewed against their pinned documents before the
auditor inspected the expected options. The independent support
sets matched all 19 author labels. Caddy was a later source family
for transfer of the fixed selective route.

| Method | Docker decisions | Docker false accepts per insufficient bundle | Caddy decisions | Caddy false accepts per insufficient bundle |
| --- | ---: | ---: | ---: | ---: |
| Word-count cosine | 5/10 | 17/23 | 7/9 | 9/21 |
| Direct entailment | 7/10 | 2/23 | 7/9 | 1/21 |
| Penalty for a supported contrast | 7/10 | 1/23 | 7/9 | 0/21 |
| Minimum over the claim and required facets | 7/10 | 9/23 | 7/9 | 8/21 |
| Facets and contrast together | 7/10 | 0/23 | 6/9 | 1/21 |

The contrast variant accepts fewer insufficient bundles than direct
entailment. The combined variant placed an approved option first
on all eight supported Docker cases, but its threshold withheld
valid bundles. A drop-one-development-case sensitivity check
preserved zero incorrect automatic acceptances on Docker while
automatic coverage varied from one to four cases. On Caddy the
automatic route varied from two to six cases, with one incorrect
acceptance under some recalibrations. This sensitivity analysis
does not change the frozen evaluations.
[Docker build cache invalidation](https://github.com/docker/docs/blob/34992b922461d20cc97107b84056756802584571/content/manuals/build/cache/invalidation.md#L90-L111) ·
[Docker Compose startup conditions](https://github.com/docker/docs/blob/34992b922461d20cc97107b84056756802584571/content/manuals/compose/how-tos/startup-order.md) ·
[Caddy Automatic HTTPS](https://github.com/caddyserver/website/blob/c33ee8b02a245045bc18c406a1aa0e06cd1fb772/src/docs/markdown/automatic-https.md)

The combined workflow accepts a bundle locally only when direct,
contrastive and joint NLI rank the same option first and each score
clears its development threshold. All other cases go to Luna with
the exact same candidate options as the Luna-only comparison.
The route makes no automatic decisions of insufficiency.
Eight isolated strict Luna low runs completed, two per corpus and
route, with zero retries. Each repeat reused the exact prompt.
Every projected case choice repeated, including the selected
option where several were valid. Reason text and whole artifact
bytes are scored separately.

| Corpus | Correct decisions with all cases sent to Luna | Correct decisions with selective review | Sent to Luna per selective run |
| --- | ---: | ---: | ---: |
| Docker | 10/10 in both | 10/10 in both | 6/10 |
| Caddy | 9/9 in both | 9/9 in both | 4/9 |

The fixed route accepted four Docker and five Caddy cases locally,
all sufficient in independent review. Luna assessed the other ten.
These are bounded decisions over supplied candidate bundles. The
routing and role-addressed inventory workflows remain development
candidates.

## Reproducibility receipts

| Local evidence | SHA-256 |
| --- | --- |
| GitLab fixture freeze | `ea834c6b60768c5392287599a744e41c5b463781f66d64f73dd990ccb3b71b80` |
| GitLab paired protocol | `3b5424a08d65b6b2288a610debcca8fb34d27826a223a6acd0f02e796887d279` |
| GitLab bound masked comparison | `45b7d1a95eea5c8ece618834419a27195c421d055748430b409d88996d17ce2b` |
| GitLab guarded consequence probe | `c2b0e834ac11532f01983ce4625bcf832a6455dfea244801413b4f5a0b8fa83f` |
| Structured evidence native comparison | `a680f22d239e865b65eed6e03fbca7c8d8c101c8194a1b75229a2ab4016ce380` |
| Structured evidence blind subset audit | `eb0dc06dd5dc121faf0ef0d4e9a5780cd6813f795883f24d8dc54e70324f2298` |
| Local verifier protocol | `49dccd2efc9b9e2fe105d669ce41e0173292b9cd69479afd93ff684c49514d05` |
| Frozen development calibration | `880675f6b3b3b8c872d5b6b4887aa04f0d817998916bb1d914e4356be0c418b7` |
| Docker local results | `9026562e7f591f990ae1405278c5b4591137787f2e7369da47e2b255559ec596` |
| Docker blind option audit | `641293278c120a9c3091b2da7a9f39cf8b2eea4aadbcf6a7636be4d40a3be789` |
| Docker initial and repeat selective results | `e9bb9574cc6e598debe3dc5f70ea78c9ef83240e7864bc0c56dbd28236ac3691`, `f469ae364e3c3bc9a7c026f204e6b60211ccec9ba451cdb74f102fbc31ba3f29` |
| Caddy transfer protocol | `ecaa10e1ca53d61d57be8e5ecf16a55132bb52b390efa9612ee58f77e488cf56` |
| Caddy blind option audit | `1df949547394d23ac12260ca7007a825dda9f17649b8ba771c68c07682994fdf` |
| Caddy initial and repeat selective results | `a9f3c6e50916c882b1fc3f7ce72d0e0d3c4d97d4ec1c8dde0743bd5693668778`, `ada9d4420b67e1b14f85f693a93b7030bc0916ae78011bd930841595561e5cf3` |
| Threshold sensitivity | `833d20b4a7a656ecfc69d3d938c0f5285f9c53f928dd5bd13ceaebf4762f4616` |
