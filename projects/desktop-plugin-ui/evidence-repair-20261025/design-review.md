# Independent evidence-contract review

Date: October 25, 2026. Scope: evidence classification in `desktop-plugin-ui`.
This review changes no canonical skill source, historical evaluation or UI.

## Diagnosed failure mechanism

The latest narrow output correctly described the main facts but labeled
unestablished readiness/paint `observed-failed` and promoted source-declared
fullscreen behavior to an observed request. The current report checker accepts
both because it only looks for an `observed-*` token in each historical row.
The report-authoring instructions also encourage placing every reused fact in
that array. This creates pressure to give static or unrun claims an empirical
label. More prose warnings alone have already failed in isolated trials.

## Recommended compact contract

Use one typed `evidence_records` array for the report's claims. Derive canonical
labels from a record's basis, rather than asking the author to type a label.
Keep host, surface, version, execution layer, concise claim and source locator
in every record; use JSON null or an explicit unknown string for unrecorded
versions. Use stable IDs to reference records from findings. Field naming is a
design choice; the invariants below matter more than these exact spellings.

| Basis | Required support | Derived evidence | Runtime claim boundary |
| --- | --- | --- | --- |
| `execution` | Named action, expected result, actual result, and explicit matched/mismatched outcome | `observed-working` / `observed-failed` | Only that action in its named layer was exercised. |
| `source-inspection` | Inspected source locator and exact declared behavior | `documented` with basis retained | Code declares/calls an API; no runtime request is asserted. |
| `primary-documentation` | Exact primary-source locator and supported contract | `documented` | Documentation does not establish installed behavior. |
| `user-report` | Attributed reported result | `untested` for the agent's acceptance, with report preserved | Human visibility can be recorded without inventing an automated pixel/control check. |
| `not-run` | Named unperformed check and reason | `untested` | Missing acceptance evidence is not a failed action. |
| `conditional` | Nonempty prerequisites or reasoned dependency | `conditional` | Dependency is not negotiated/executed acceptance. |
| `explicit-exclusion` | Primary contract/source locator and precise exclusion | `unsupported` | Apply only to the stated host/surface/version/feature. |

For source inspection, `documented` must explicitly mean source-declared
behavior in the skill's definition. Do not silently reuse a definition limited
to vendor prose. An explicit basis and `runtime_tested:false` keep this use
honest. A source file that contains a request call can support “the handler is
defined to request fullscreen,” not “the host received/accepted fullscreen.”

Reject contradictory fields, such as `actual` or a runtime pass/fail verdict on
a `not-run` record. Do not auto-repair a false classification into the preferred
answer. Derive the label from the supported input or return an English finding.
The helper remains a consistency checker, not an oracle for whether evidence
actually exists or a source says what the author claims.

If `historical_observations` is retained for compatibility, generate it only
from executed records. Put source declarations, user reports and pending checks
in the broader evidence ledger. Never fabricate a failed historical observation
merely to populate that legacy array. Existing historical outputs stay immutable.

## Important edge cases

- A policy request expected to decline and actually declining is a **passing
  policy check**. It does not establish a failed UI renderer. Record expected
  and actual values; don't classify by the returned word or Boolean alone.
- Boolean `false` is valid data. JSON null can be a valid cancellation result.
  Missing keys, null, false, zero and empty strings must remain distinct. If the
  helper compares values, use type-sensitive JSON equality: Python `False == 0`
  must not erase this distinction.
- An activation log is an executed/log-inspection fact about an activation
  attempt. Its absence of a failure stack neither establishes completed
  activation nor certifies model/account/UI readiness. Those checks get their
  own not-run records when relevant.
- A declared capability and an accepted mode request are different claims.
  A protocol pass, source declaration and user-reported paint need separate
  records even when they concern one feature.
- A negative code search cannot prove global unsupported behavior. Only a
  supported explicit exclusion may receive `unsupported`; a missing path or
  untested stock frontend should remain scoped and untested/conditional.
- Several layers may form one deliberately combined fixture result, but don't
  claim the outer assistant was exercised. Preserve the composite layer label
  and its result rather than converting a synthetic browser to Copilot paint.
- Whole-report acceptance flags describe the current task. Historical probe
  passes must not flip them to true.

## Validation plan

Test the helper's mapping and rejection behavior independently of generated
prose: all bases, valid pass and mismatch, unrun-with-result contradiction,
source-as-runtime contradiction, expected refusal, false/null/zero separation,
unknown versions, duplicate IDs, missing locators and references to absent IDs.
Exercise CLI diagnostics/CI exit codes, exact outputs and a relocated read-only
bundle. Keep output deterministic and make no account, network or model call.

Freeze the revised payload and test a small exact-path contract once, three
naturalistic requests and one boundary case using the documented model
exception. Naturalistic prompts should provide mixed raw evidence and ask for a
practical report without naming the suspected bug or desired implementation.
The boundary case should include refusal/null/static declarations with unused
unperformed checks. Preserve English, Nielsen and ColorSet expectations where
the task actually asks for UI advice; they should not coerce an invented UI test.

Review strict traces, exact artifacts, helper output and semantic claims
separately. A clean typed ledger can still accompany unsupported prose, so
inspect whether every executed claim in both report formats has a matching
record and whether a record's locator supports its claim. Keep all old failures
separate and do not rerun an unchanged subject to select a better answer.

## Canonical-reference audit before parent edits

These line numbers refer to the source read in this review, before the parent
applies corrections. Historical evaluation outputs are not repair targets.

| Reference and line | Existing wording | Judgment and bounded correction |
| --- | --- | --- |
| `references/codex-limits.md:91-93` | `observed-failed` presentation under `never` | **Definite correction.** The surrounding record says automatic decline without a host callback. No presentation action ran. Classify the policy decline as an observed policy result; presentation stays untested/not-run. |
| `references/capability-offerings.md:7-9` | `observed-failed` for their specific refused cases | **Overbroad rule.** Refusal alone cannot select a verdict. Require expected versus actual behavior; an expected safety/validation/policy rejection is a passing check, while a request expected to succeed can fail. |
| `references/report-authoring.md:9-16` | Put each observation in `historical_observations` with an `observed-*` value | **Structural pressure.** Limit historical rows to executed observations. Route declarations, reported outcomes and unrun checks to typed records with their actual basis; the checker must not force an empirical tag on them. |
| `references/copilot-limits.md:63` | Wrong `value:true` field returned false; `observed-working/failed` | **Clarify expectation.** Preserve the actual false result. If the fixture deliberately verifies rejection of the wrong field, its validation assertion passed. Do not call the whole UI or callback system broken. |
| `references/copilot-limits.md:68` | Top application document raised `SecurityError`; `observed-working/failed` | **Clarify scope.** Parent-access operation was denied and the intended isolation check passed. Keep those two statements separate instead of a mixed unscoped verdict. |
| `references/copilot-limits.md:57,62` | Invented `ui/show` returned -32601; bare consumer's confirm threw unsupported-host | **Real attempted requests, not missing tests.** Preserve the named rejection and exact consumer/endpoint. A deliberately expected rejection can be a passing negative assertion; it cannot exclude all MCP Apps or all Copilot UI. |
| `references/codex-limits.md:74-75,110-113` | `ui/initialize` failed at app-server; arbitrary nested schema rejected | **Keep bounded raw outcomes.** Actual attempted requests were rejected. Do not retag them untested or erase the errors. Their negative assertions may pass; the request failure cannot prove a whole renderer/extension is unavailable. |
| `references/copilot-limits.md:65` | Attempted extension downgrade rejected | **Retain as a real install-attempt failure.** The installed guard refusing it may work as intended. Neither fact is an MCP App paint failure. |
| `references/claude-host-limits.md:28-33` | Refused native primitive/prop/runtime access cases carry `observed-failed` | **Do not blanket-retag.** Native engine requests actually ran. Preserve the engine refusals, mark untested cells separately, and record whether the relevant negative assertion passed. No conclusion about actual terminal/Desktop paint follows. |
| `references/evidence-and-probing.md:27` | `observed-failed assumption, not a host defect` | **Retain with harness scope.** An expectation about SDK auto-rejection was falsified. The source already separates this failed assumption from host behavior. A typed record can make the failed harness expectation explicit. |

The canonical capability guide's source-declaration/fullscreen paragraph
already attributes registration to source and distinguishes tab binding from
controls. Its source wording should become more explicit if helpful, but it
does not itself claim the actual fullscreen request executed. That unsupported
promotion occurs in the immutable generated follow-up, not in the canonical
reference. Similarly, the October 24 surface matrix identifies its older
snapshot date; its historical paint boundary is not a new observation to retag.

## Independent integration checks after implementation

The implemented helper uses a nonempty string for every context field,
including an explicit `unknown` for unrecorded versions; it does not accept
JSON null for that field. Execution `expected` and `actual` are descriptive
strings and `outcome` is the caller's explicit `pass` or `fail`. The helper
does not compare those strings semantically or verify the underlying evidence.
These implementation choices keep the input contract small; the human/forward
review must still establish that an execution really occurred and its verdict
is justified.

The new project-owned test suite is
`projects/desktop-plugin-ui/scripts/test-typed-report-checker.py`. It copies the
runtime resources, invokes the actual ledger CLI, independently checks all
seven basis mappings and states, then tests report validation against that
normalized output. No original historical output or canonical file is edited.

- Retained `run-001`: **34/34** passed under the initial integration contract,
  which allowed raw evidence records to be recomputed by the report checker.
- Fresh `run-002`: **41/41** passed after the final-report contract was
  tightened to require all derived fields. This rejects unnormalized final
  records, each missing derived field, label/state tampering, duplicate JSON
  basis/label keys, missing/empty/malformed records, Markdown-only strict
  validation, unknown/nonstrings/blank references, mixed missing companion
  JSON, and illegal runtime data on source/not-run bases. It also accepts a
  named genuine failure, an expected-refusal pass, nested valid references,
  independent JSON ledgers, empty optional reference arrays and legacy checks.

The final run completes in 8.59 seconds with an unchanged copied bundle.
Checker SHA-256:
`c95c17b1fdb90e1105d5372afedc1717270d9ce71f67024d591d133a23f51f47`.
Ledger helper SHA-256:
`deee829a1e9461a656f5f6c61dd50d83ed487cf1f40ea5bade07be90cdd2e839`.
Raw receipts are retained under ignored
`projects/desktop-plugin-ui/artifacts/typed-report-checker-tests-20261025/`.
This is deterministic CLI integration, not a UI test or semantic certification.
