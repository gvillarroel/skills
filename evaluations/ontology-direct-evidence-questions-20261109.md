# Direct evidence questions for ontology review

This study tested a documentation-only candidate against the numbered
source version of `extract-with-ontology` at `9da39424`. The candidate
keeps a supported uncertainty assertion in the graph, asks for the
authoritative value that would settle the open decision, and checks
whether two incompatible outcomes could share the same answer.
Compound decisions can require several observations. A decisive
yes-or-no answer is sufficient for a binary question.

The experiment borrowed the distinction between asking and acquiring
decisive information from clarification research. It used a finite
set of authoritative answer possibilities and an independent semantic
rubric. [MT-InfoSeek](https://arxiv.org/abs/2608.14808) ·
[CIGAsk](https://aclanthology.org/2026.findings-emnlp.314/) ·
[Clarification in ambiguous QA](https://aclanthology.org/2023.findings-emnlp.772/)

## Targeted pilot

Three GPT-6 Luna low prompt arms used the same scoped decisions and
explicit rules across three four-case shards. Nine cases were open
and three were settled. All nine strict cells were admitted and
65 preflight controls passed. The grader was blind to the arm.

| Prompt | Scoped, sufficient question or correct abstention |
| --- | ---: |
| Ask directly for the missing fact | 12/12 |
| Add a two-answer counterfactual check | 12/12 |
| Check every possible outcome | 11/12 |

All arms identified the correct deciding observations. The exhaustive
arm lost one standalone scope check. It asked for two needed facts
while omitting the archive and snapshot to which they applied. The
direct arm reached the ceiling on this slice with explicit rules.

## Native Harbor development

Four independent synthetic domains covered a compound decision,
a genuine binary decision, a settled control and an unreported
measurement with an exact boundary. Both arms used the same tasks,
pinned sources, graph contract and numbered source workflow. Harbor
0.18.0 ran GPT-6 Luna low once per cell with zero retries. The
51 controls passed locally and in Docker. The actual actor preflight
probed access to hidden answers, other tasks and prior artifacts.

| Result | Published skill | Direct-question candidate |
| --- | ---: | ---: |
| Strict admissions | 2/4 | 3/4 |
| Full native passes | 1/4 | 1/4 |
| Expected, correctly cited triples in retained graphs | 48/48 | 48/48 |
| SHACL-conforming retained graphs | 4/4 | 4/4 |
| Complete scoped review by independent audit, retained | 1/4 | 2/4 |
| Directly sufficient review by independent audit, retained | 0/4 | 2/4 |
| Directly sufficient review among all planned attempts, strict only | 0/4 | 1/4 |

The masked semantic auditor scored the whole review. In Alder, the
automatic checker accepted a question about whether evidence existed,
and rejected a valid question about the current enrollment under the
correct source entity name. The frozen native reward is preserved.
In Skyline both versions asked for the two missing observations and
also opened a vocabulary mapping question about a settled fact.
In Juniper both identified that a measurement was missing and
omitted the actual question.

Only one of four pairs passed strict admission in both arms. Two
attempts used a SHA-256 with one extra character while calling the
numbered view. One attempted a nonexistent CLI subcommand. The
ordinary Harbor comparison flagged raw lock drift. An independent
normalization verified equal task, model, environment and retry
contracts after accounting for the declared skill inventory and
serialization differences.

The predeclared gate required at least three jointly admitted pairs,
complete hard controls and a paired improvement in direct review.
Development failed that gate. The candidate stays in the archive
and the sealed independent cohort received zero inference calls.
The organizer's verified ledger retains the exact candidate, reports
and selection decision. Native job IDs were
`16dc2167-00e2-4b2c-a2a5-d9c9543007d3` and
`0b8c1740-8e78-4a44-a818-276642d858cf`.

## Transfer to actual release changes

A separate four-attempt Pi probe paired both skills on two actual
release changes. Repository files were pinned to exact commits.
The workflow and cluster profiles were authored fixtures that left
the effective setting open. Each episode generated two asserted
graphs with the same feature and product identifiers across releases.
The evaluator checked exact changes, source pins and review
separately. The 105 preflight checks included correct spans and
neighboring or wrong-source citation controls.

| Source pair | Expected semantic change |
| --- | --- |
| `upload-artifact` v4.3.6 to v4.4.0 | Hidden files switch from included by default to excluded by default. A dedicated inclusion input appears. |
| Kubernetes v1.28.0 to v1.29.0 | The `SidecarContainers` gate changes from Alpha and disabled by default to Beta and enabled by default. |

Both arms recovered all **20/20 expected triples** and both exact
deltas in their retained artifacts. The published arm cited 20/20
claims using the frozen approved witnesses, and the candidate used
17/20. A review of the three citation findings found two generic
old action titles and one new hidden-file setting that supports the
product membership through the file's pinned provenance. The frozen
citation count remains unchanged. Both masked pairs resolved the
deployment evidence question in the review. Strict admissions were
2/2 and 1/2. The candidate's action run corrected two vocabulary
errors before materializing the final artifacts.

The runtime questions distinguish defaults from a deployed value.
In the workflow case, all reviews asked for the resolved
`include-hidden-files` input at the named step. In the cluster case,
all requested the effective gate states for both named components.
This diagnostic probe did not participate in native selection.
[Upload artifact release note](https://github.com/actions/upload-artifact/releases/tag/v4.4.0) ·
[Kubernetes v1.28.0 feature registration](https://github.com/kubernetes/kubernetes/blob/855e7c48de7388eb330da0f8d9d2394ee818fb8d/pkg/features/kube_features.go#L1148) ·
[Kubernetes v1.29.0 feature registration](https://github.com/kubernetes/kubernetes/blob/3f7a50f38688eb332e2a1b013678c6435d539ae6/pkg/features/kube_features.go#L1195)
