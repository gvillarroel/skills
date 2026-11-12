# Evidence-classification repair

Date: October 25, 2026, America/New_York. The user requested correction of
evidence labels and fresh skill validation, preserving English, Nielsen,
ColorSet 1/2 and continuation without Copilot sign-in. No assistant UI,
authentication, Copilot model turn or Claude model turn is required here.

**Current outcome:** the repaired workflow meets every frozen family threshold
on the recorded GPT-6.1 Sol configuration: contract 1/1, naturalistic 2/3,
boundary 1/1 and generalization 2/3 joint acceptance. Typed checking passes
8/8; strict/joint acceptance is 6/8, retaining one tool error and one timeout.
This is a scoped model-specific validation. Earlier Luna failures and untested
native-host behavior remain explicit; overall skill status stays `validating`.

## Root cause and correction

The prior workflow required an observed label for every historical row,
including static declarations and unperformed checks. The old checker could
confirm literal labels and source URLs while accepting a false execution
claim. The [independent design audit](../../projects/desktop-plugin-ui/evidence-repair-20261025/design-review.md)
identifies that contradiction and the canonical negative-check cases.

The new workflow uses one typed `evidence_records` entry per atomic claim and
derives its classification from the declared basis:

| Basis | Correct classification | Execution |
| --- | --- | --- |
| Executed check matches its expectation | `observed-working` | Executed |
| Executed check misses its expectation | `observed-failed` | Executed |
| Inspected source or primary documentation | `documented` | Not run |
| Human report | `untested` by the agent; preserve the reported result | Not run |
| Skipped/unperformed check | `untested` | Not run |
| Unverified prerequisites | `conditional` | Not run |
| Explicit authoritative exclusion | `unsupported` on the stated surface | Not run |

An expected rejection is a passing negative check. The canonical Codex `never`
entry now records its automatic decline as working and form pixels as untested.
Copilot protocol/gate/callback/DOM entries retain their raw results but identify
intended negative assertions separately. The source guide no longer treats
every refusal as a failed UI. Earlier evaluation artifacts remain unchanged.

The [new helper](../../skills/desktop-plugin-ui/scripts/evidence_ledger.py)
requires explicit basis/context fields, separates source from execution fields,
and derives normalized JSON plus an optional Markdown table. It refuses
inconsistent supplied labels, mixed bases, duplicate IDs, invalid outcomes,
incomplete context and bundle output writes. Invalid data creates no outputs.
It preserves literal source URLs when rendering Markdown.

The [report checker](../../skills/desktop-plugin-ui/scripts/check_reports.py)
now validates normalized records, derived fields and `evidence_ids`, with a
`--require-evidence-records` mode. Duplicate JSON keys are refused. Legacy-only
checking remains available for historical consumers but explicitly reports its
limited scope. This does not prove factual truth, complete coverage, artifact
authenticity or actual host painting; independent semantic review remains.

The [core workflow](../../skills/desktop-plugin-ui/SKILL.md) and
[report-authoring reference](../../skills/desktop-plugin-ui/references/report-authoring.md)
require generation before prose, reuse of the rendered ledger, and review of
claims against their actual basis. The English, H1-H10, CS1-default/explicit-CS2
and host-owned/accessibility styling boundaries remain unchanged. All 42
canonical pattern IDs are preserved.

## Concrete corrected observations

The [reviewable input](../../projects/desktop-plugin-ui/evidence-repair-20261025/corrected-observations.json)
materializes eight bounded observations without changing previous runs. Its
generated JSON/Markdown pass typed checking for all eight records:

```powershell
uv run --script skills/desktop-plugin-ui/scripts/evidence_ledger.py --input projects/desktop-plugin-ui/evidence-repair-20261025/corrected-observations.json --output projects/desktop-plugin-ui/artifacts/data/corrected-evidence-v2-20261025.json --markdown projects/desktop-plugin-ui/artifacts/data/corrected-evidence-v2-20261025.md --fail-on-findings
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py projects/desktop-plugin-ui/artifacts/data/corrected-evidence-v2-20261025.md projects/desktop-plugin-ui/artifacts/data/corrected-evidence-v2-20261025.json --require-evidence-records --fail-on-findings
```

The corrected ledger separates not-run Copilot paint, a source-declared Expand
handler, not-run fullscreen acceptance, an actually failed controller binding,
user-reported visibility, expected automatic decline, not-run form painting,
and a successful inspection of a still-signed-out workspace. No source handler
is recast as an observed fullscreen request. No missing paint test is failed.

## Deterministic validation

| Check | Result and scope |
| --- | --- |
| Evidence helper v1 | 26/26: basis mapping, tampering, paths, readonly relocation, JSON/Markdown consistency and exact URL preservation |
| Current evidence helper v2 | 32/32, including protected report metadata and domain findings |
| Typed-report integration | 41/41: normalized-field requirements, duplicate JSON, references, true failures, expected refusals and legacy compatibility |
| Existing report checker | 33/33 regression cases |
| Existing source checker | 53/53 regression cases |
| Existing Nielsen/ColorSet contract | 20/20; no new host paint/user study |
| Pi harness | 17/17 tests |

The first evidence-helper attempt's Windows stdout encoding issue is preserved;
ASCII-safe stdout JSON fixes it while UTF-8 artifacts retain original text.
The 34-case initial integration contract is retained separately from the final
41-case contract. A pre-freeze authoring audit flagged the enlarged reference's
missing contents list; after adding the list, all source/runtime/full checks
pass. These are deterministic authoring/tool corrections, not new product facts.

V1 runtime helper SHA-256:
`deee829a1e9461a656f5f6c61dd50d83ed487cf1f40ea5bade07be90cdd2e839`.
Report checker SHA-256:
`c95c17b1fdb90e1105d5372afedc1717270d9ce71f67024d591d133a23f51f47`.
Receipts reside under ignored project artifacts, including
`evidence-ledger-tests-20261025/final-url-preserving.json`,
`typed-report-checker-tests-20261025/run-002/results.json`, and
`data/evidence-repair-design-contract-20261025.json`.

## Frozen isolated study

The new source/runtime/full payload contains **23 files**, SHA-256
`a06c9f918308160272427d8a97f40d19ebfa82db65a7f2ff0a5571406f3a1799`.
It is distinct from the prior 22-file follow-up and offerings cohorts.
The [review criteria](evidence-repair-review-criteria.md) and all four prompt
hashes were frozen before outputs:

| Case | Prompt SHA-256 | First attempts |
| --- | --- | --- |
| [Contract](../pi-prompts/desktop-plugin-ui-evidence-contract.md) | `fa2e1a287c431754549c93d86a97c36bb379e3934c86f1f784789b6ffb012838` | 1 |
| [Naturalistic](../pi-prompts/desktop-plugin-ui-evidence-naturalistic.md) | `ee44ad5752083b38ea153182d63eb31955fb790e8c86969c01ebd42c3134a390` | 3 |
| [Boundary](../pi-prompts/desktop-plugin-ui-evidence-boundary.md) | `441c75ee394a7e4f2a2e8ef95235c54deb62099f1577d5444768855508c6716e` | 1 |
| [Generalization](../pi-prompts/desktop-plugin-ui-evidence-generalization.md) | `3a3cd5053096f4f0e0e994a318c0bc72207fc0f31133fb12ef7a57d6ba13e977` | 3 |

Criteria SHA-256:
`c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2`.
All runs use the existing documented `openai-codex/gpt-5.6-luna` exception
after the prior Spark account rejection, JSON strict mode, exact artifacts,
false current host/testing flags and read-only skill-only workspaces. They
prohibit network, extra providers, accounts, actual models/hosts/UI inside the
task, installation or global configuration. Copilot sign-in remains omitted.

Contract covers all bases. Naturalistic reuses the support-queue task with the
new typed schema, retaining client/state/English/Nielsen/default-CS1 quality
requirements. Boundary checks the actual follow-up failures. Generalization
transfers to supplied fictional lab records and explicitly selected CS2.
Require joint contract 1/1, naturalistic at least 2/3, boundary 1/1 and
generalization at least 2/3. Do not pool old subjects or repair tested outputs.

### First repair subject results

| Case | Strict | Typed checker | Content review | Conservative joint |
| --- | --- | --- | --- | --- |
| Contract | 1/1 | 1/1 | 1/1 | 1/1 |
| Naturalistic | 1/3 | 3/3 | 2/3 | 1/3 |
| Boundary | 1/1 | 1/1 | 1/1 | 1/1 |
| Generalization | 2/3 | 3/3 | 3/3 | 2/3 |
| V1 total only | **5/8** | **8/8** | **7/8** | **5/8** |

The classification correction works across the first-attempt outputs, but the
subject misses its naturalistic joint threshold. One naturalistic record uses
an observed canvas flag in a not-run reason without a supporting execution
record. Scratch-path isolation also fails in three samples: naturalistic runs
1 and 3, and generalization run 3 use generic shell/system temporary directories. Tool/read
failures remain strict failures after recovery. The evaluator does not inspect
or delete the external temporary files. Earlier tested outputs remain intact.

The v1 compact reviews are [contract/boundary](evidence-contract-boundary-v1-luna.md),
[naturalistic](evidence-naturalistic-v1-luna.md) and
[generalization](evidence-generalization-v1-luna.md). Exact tables may remove
nonsemantic underscore escaping; independent review compares table data rather
than imposing byte-exact Markdown that the prompt did not request.

### Scope and serialization repair before a new subject

The old portable-temp advice contributed to the isolation failures. Replace it
with workspace-relative `work/` and explicit temporary-directory placement
within the authorized task root. Add optional `report` metadata to the input
helper so it can emit complete report JSON without a hand-built Python/long
heredoc merge. Domain findings remain separate from protected classifier
diagnostics. Preserve the v1 cohort and run a new frozen subject with the same
prompts and criteria; do not reroll a failed v1 sample.

Final revised-subject results and installation receipts follow after completion.

The separately frozen v2 subject has **23** matching source/runtime/full files,
SHA-256 `ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
The four prompts and criteria above are unchanged; every v2 case uses a new
workspace and run ID. Helper SHA-256 is now
`63fddc71df0b659b9d630487b73bcfe05f18b395a08b49398f75d07dfc01a80b`.
Its expanded deterministic suite passes **32/32**, while a fresh copied-runtime
typed integration run passes **41/41**. Report metadata preserves domain
findings and false flags without allowing replacement of classifications or
the protected classifier diagnostics. CLI diagnostic behavior and the pure
classification API remain unchanged; old no-metadata inputs remain compatible.

Fresh v2 typed integration receipt:
`projects/desktop-plugin-ui/artifacts/typed-report-checker-tests-20261025/run-003-v2-metadata/results.json`.
The current concrete corrected input includes report metadata and produces the
`corrected-evidence-v2-20261025` artifacts, passing typed checking for all eight
records and their domain references. Initial pre-metadata artifacts remain
separate.

### Separate model validation

The v2 Luna cohort retains report-support/basis errors and tool-handling
failures despite the corrected classifier. These are not reclassified as
passes. A separate cross-model cohort uses the installed
`openai-codex/gpt-6.1-sol` model on the unchanged v2 payload and prompts.
`pi --list-models sol` lists the model; one contract first verifies account
acceptance before dispatching the remaining cases. The explicit per-run model
exception is recorded in `SKILLS.md`; no global model setting is changed.

The [Sol criteria](evidence-repair-sol-review-criteria.md) change only the
required evaluator model and cohort framing, keeping all semantic standards,
artifact paths, isolation checks and thresholds. Their frozen SHA-256 is
`0a94fd291070d026215d42b19ef816fad4b6b0e2e8aab55de87e35ce63f4a3db`.
Each model has its own run IDs, workspaces, outputs and judgments. Sol success
cannot erase Luna failures or establish model-independent reliability.

### Revised Luna results retained

| Case | Strict | Typed checker | Content review | Workspace/action scope | Joint |
| --- | --- | --- | --- | --- | --- |
| [Contract/boundary review: contract](evidence-contract-boundary-v2-luna.md) | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| [Naturalistic](evidence-naturalistic-v2-luna.md) | 2/3 | 3/3 | 2/3 | 3/3 | 1/3 |
| [Contract/boundary review: boundary](evidence-contract-boundary-v2-luna.md) | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 |
| [Generalization](evidence-generalization-v2-luna.md) | 0/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| V2 Luna total only | **4/8** | **8/8** | **6/8** | **8/8** | **2/8** |

The workspace repair clears the earlier outside-scratch violations in all
eight revised samples. Remaining tool failures include reads beyond file
length, ambiguous text edits, malformed intermediate JSON and a Windows
UTF-8 omission in an ad-hoc inspection script. They remain strict failures
after recovery. Content failures are a missing terminal flag record, a mixed
native/user-report basis and a CLI claim linked to a webview record. The
deterministic checker validates declared structure and references; those
factual support errors remain the independent reviewer's responsibility.

The Sol account path is verified by its completed contract, which records the
actual `gpt-6.1-sol` model rather than relying on a local catalog or manifest.
No user account operation or global model change is involved.

### Sol acceptance on the unchanged v2 subject

| Case | Strict | Typed checker | Joint | Required family threshold |
| --- | --- | --- | --- | --- |
| [Contract](evidence-contract-v2-sol-1.md) | 1/1 | 1/1 | 1/1 | Met: 1/1 |
| [Naturalistic](evidence-naturalistic-v2-sol.md) | 2/3 | 3/3 | 2/3 | Met: at least 2/3 |
| [Boundary](evidence-boundary-v2-sol-1.md) | 1/1 | 1/1 | 1/1 | Met: 1/1 |
| [Generalization](evidence-generalization-v2-sol.md) | 2/3 | 3/3 | 2/3 | Met: at least 2/3 |
| Sol total only | **6/8** | **8/8** | **6/8** | **All families meet the frozen threshold** |

The accepted samples independently pass factual/basis/coverage review,
source/record reference checks, source/runtime payload integrity, English,
Nielsen and applicable ColorSet/contrast requirements. Full raw command audits
check write paths as well as reads. Every family uses first attempts with no
reviewer repair or reroll.

Independent content and workspace/action-scope reviews pass **8/8** Sol outputs,
including the completed artifacts from the two execution-failed cases. The
187 normalized records are checked. The six UI recommendations pass 60
canonical Nielsen ID/label checks; selected token bindings and all 81 reported
contrast pairs independently match the bundled values/calculation. CS1 is
exercised by naturalistic recommendations and explicit CS2 by generalization.
This is recommendation/data validation, not new assistant-host paint or a user
study. The timeout case's final artifacts were fully reviewed and stable.

Generalization run 2 retains its initial redirection into a missing `work/`
directory. Naturalistic run 3 retains its timeout: requested limit 600 seconds,
effective duration 685.208 seconds. Its final artifacts exist and receive
separate content review, but cannot turn the timed-out execution into a pass.
Naturalistic runs 1 and 2 pass strict at 498.060 and 599.085 seconds respectively.
No deadline or acceptance rule was changed after seeing results.

The same skill and prompts therefore produce different reliability by model.
Report the qualified Sol result alongside both Luna cohorts; do not claim
model-independent certification or use correct final artifacts to erase
execution failures. No Copilot sign-in, Claude/Copilot inference or actual
assistant-host UI action occurred during this repair.

## Final repository and local installation

Canonical and installed snapshots both contain exactly **23** files at
`ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
The scoped source/runtime/full authoring audit passes, along with 80 official
source-URL occurrences, pattern IDs, skill validation, independence, payload
and the 17-case Pi harness test. No renderer or acceptance gallery was added.

Scoped sync/check ran against the non-ignored source staging copy and verified
all 23 files. Afterward, both v1/v2 stages were moved inside the ignored project
artifact directory with explicit resolved-path boundary checks. A direct final
comparison validates canonical source, local install and both retained stage
hashes without relying on git enumeration of ignored files. Receipt:
`projects/desktop-plugin-ui/artifacts/data/evidence-repair-source-install-archive-integrity-20261025.json`.

The current eight-observation correction is reproducible from its versioned
input and the helper commands above. All prior failed model outputs, original
classification mistakes and independent judgments remain retained. No commit,
push, deployment, publication or unrelated skill installation was performed.

Final commands include:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-evidence-ledger.py
uv run --script projects/desktop-plugin-ui/scripts/test-typed-report-checker.py --run-id <fresh-run-id>
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
```

Choose a fresh typed-checker test ID rather than overwriting its retained
receipts. The scoped local installation comparison uses direct snapshots
after stage archival; a git-aware check of an ignored archive is insufficient.
The backlog records the current payload, separate model judgments and broader
`validating` boundary. No further user authentication is requested.
