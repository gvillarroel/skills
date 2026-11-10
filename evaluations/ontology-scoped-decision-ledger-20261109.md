# Scoped decision review for ontology extraction

V47 tested a working list with one entry per requested decision.
The entries distinguish source-established outcomes from open
decisions and consequential representation gaps. A supported
uncertainty class can appear in the asserted graph while the
underlying decision stays open. An open entry asks for the
authoritative observation that would settle the requested outcome.
A consequential mapping gap asks how to represent a known fact.
The candidate uses the existing review artifact format.

The design separates evidence sufficiency from graph construction
and retains source scope during decomposition. [ODKE+](https://arxiv.org/abs/2509.04696) ·
[Decomposition Dilemmas](https://arxiv.org/abs/2411.02400) ·
[MT-InfoSeek](https://arxiv.org/abs/2608.14808)

## Native Harbor development

Four new synthetic domains covered an open deployment capability,
an unresolved directed authorization, a consequential mapping gap,
and a settled scope. Both arms shared the same task roots, source
manifests, ontology, shapes and exact view commands. Each task ran
once with GPT-6 Luna low in Harbor 0.18.0 and zero retries. The 59
preflight controls passed locally and in pinned Docker. The actor
isolation probes confirmed the verifier and private tasks were out
of the visible workspace.

| Outcome | Published skill | Decision-list candidate |
| --- | ---: | ---: |
| Strict admissions | 3/4 | 4/4 |
| Full native passes | 1/4 | 3/4 |
| Complete reviews by masked semantic assessment, retained | 2/4 | 4/4 |
| Strictly admitted and complete semantic reviews | 1/4 | 4/4 |
| Correctly cited expected triples | 48/48 | 48/48 |
| Retained graphs conforming to SHACL | 4/4 | 4/4 |
| Successful preprovided numbered views | 8/8 | 8/8 |

All paired retained graphs had matching fingerprints. The baseline
strict exception attempted to read a nonexistent review reference.
The 16 exact manifest views succeeded. In Estuary, the candidate
asked for the outcome if an authoritative current decision exists.
An authoritative response that there is no decision leaves no
confirmed authorization under the task rule. The automatic verifier
rejected that question. The independent assessment credited it and
kept the native reward unchanged.

In Loam, the baseline asked whether a documented stop also authorizes
boarding. That question failed the frozen scope rubric. The task's
wording permits a broader reading under which the question is
reasonable. Three pairs were jointly admitted. Discounting Loam
leaves a jointly admitted gain in Estuary and preserves the
predeclared selection outcome. Raw Harbor comparison reported
skill inventory lock drift. The separate normalized lock audit
confirmed the remaining paired task and execution contract.

The development job IDs are `d662c0d3-7e05-41da-a64b-005eb7704030`
and `6f01d116-e56e-4bfc-a64c-e659c68347ee`. The organizer
released the digest-bound candidate once after development passed.

## Independent validation

The exact candidate entered three previously unseen cases. Before
the model runs, 39 hard controls replayed twice, 12 semantic
calibration controls and six manifest-view controls passed. Each arm
ran once per case with GPT-6 Luna low and zero retries.

| Outcome | Published skill | Decision-list candidate |
| --- | ---: | ---: |
| Strict admissions | 2/3 | 0/3 |
| Jointly admitted pairs | 0 | 0 |
| Exact expected graph and SHACL, all retained outputs | 3/3 | 3/3 |
| Masked review criteria, all retained outputs | 15/15 | 15/15 |
| Successful preprovided manifest views | 6/6 | 6/6 |

The semantic scores for unadmitted runs are retained artifact
diagnostics. The strict gate excluded model-issued tool actions
and one absolute-path read flagged by the trace policy. The
published arm recorded one no-op edit and one materializer source
digest mismatch. The candidate recorded two no-op edits, two
materializer digest mismatches and four create-only destination
collisions. Multiple findings can come from the same trial.
All six Pi processes exited successfully. The audit found zero
provider, evaluator or transport failures.

The organizer closed independent validation without promotion.
The sealed gate aggregate is
`2ea61ef75fb8e96b05a31d173fae0a4d7811d92a7452227da4c2166c7f8f8b7e`.
The redacted failure-domain receipt is
`ce9c58ad991762c4cb22f8c43735231dcac45fbddecf32fe6b3d2b8130d06087`.

## Public documentation transfer

A separate diagnostic compared free-form review with a required
four-row review plan rendered into Markdown. Both used the same
decision-list guidance, exact manifest views and ontology inventory.
The compiler checks complete IDs, open versus settled question
fields, and pinned evidence ranges. It passed 13 preflight controls.
An initial setup attempt stopped before inference when a generated
Python cache appeared in the seed directory. The actor then received
the identical regular input files in a clean workspace.

Both formats ran once on each of two cases with GPT-6 Luna low,
with four strict admissions. The underlying release facts came
from immutable public documents. The deployment profiles were
authored fixtures.

| Outcome | Free-form review | Rendered review plan |
| --- | ---: | ---: |
| Strict admissions | 2/2 | 2/2 |
| Correct scoped decisions under masked review labels | 7/8 | 8/8 |
| False review alerts | 1 | 0 |
| Exact asserted graph | 1/2 | 1/2 |

The OpenTelemetry pair recovered the same directed replacement
of `http.method` by `http.request.method`. In the prose output,
the request for a mapping term was conditional even though the
inventory required the known precedence relation. It also asked
for an empirical capture after the explicitly unset control was
settled by the documented default. In checkout, both reviewers
attributed credential storage to the relevant release, asked
for the Docker runner version and persistence setting for the
open case, and kept the host-only case outside the Docker-specific
threshold. The independent reviewer saw masked labels while the
different review formats remained visible. [OpenTelemetry migration](https://github.com/open-telemetry/semantic-conventions/blob/2d91ead21027a8a58fbb7488b12d80238e7c0ac5/docs/non-normative/http-migration.md#L36-L50) ·
[OpenTelemetry v1.23.1 policy](https://github.com/open-telemetry/semantic-conventions/blob/73720582560b5a020df8aee90504fcb411f62713/docs/http/http-spans.md#L45-L63) ·
[Checkout v6 storage change](https://github.com/actions/checkout/blob/1af3b93b6815bc44a9784bd300feb67ff0d1eeb3/README.md#L5-L8)

The two checkout graphs expressed the documented storage locations
with different strings. Neither matched the exact vocabulary
requested by the fixture. A diagnostic follow-up used named
`StorageLocation` individuals and `sh:in` in the same source
slice. Both fresh strict runs produced the exact graph, with the
same digest
`ea91b758872a4cb9f1260bde5b53f42beca1b9fcd869273786d8dd368f176555`.
Seven controls checked the reviewed case, free text, missing and
multiple values, an unlisted IRI, and swapped valid values. The
allowed-value shapes accepted the swapped values. Exact fact and
role checking identified that error. The compiler and controlled
checkout schema stay in the experiment archive.
[Checkout storage PR](https://github.com/actions/checkout/pull/2286) ·
[SHACL allowed values](https://www.w3.org/TR/shacl/#InConstraintComponent)

## Local reproducibility receipts

| Receipt | SHA-256 |
| --- | --- |
| Development selection gate | `21828d9cfe053d4dadb3a84e81b07b9e211fa5f7be2247e9798d130ab2a8d6ff` |
| Development masked review | `7be6666f0edcffed01bb8e02ebc5dbaa35cc950fb841607f4539e2097b1bf808` |
| Public transfer protocol | `4b08e9ba3d74f587b34062cb329bb9e75be8f54104660f1ae3697f67a46d17a8` |
| Public transfer masked review | `05093626cd8dc4e92e653b965ee689b8841323b2ee10248fd50eefa73c62ee58` |
| Controlled vocabulary follow-up | `7f468620a7c6b869639ca3894256ecbda767f56f6c5e3e668522d3d443bfea54` |
