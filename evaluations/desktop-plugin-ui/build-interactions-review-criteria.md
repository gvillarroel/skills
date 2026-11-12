# Plugin authoring and interaction revision: independent criteria

Frozen before reviewing implementation changes or forward outputs on
October 25, 2026. These criteria cover the new authoring and interaction
behavior only; they do not replace prior skill evidence or prove live host
acceptance. The evaluator prepared the prompts from the user request and the
pre-revision skill, without reading the new authoring references.

## Cases and repetition

| Case | Prompt | Exact required outputs | Repetitions and threshold |
| --- | --- | --- | --- |
| Contract smoke | `evaluations/pi-prompts/desktop-plugin-ui-build-contract.md` | `plugin/queue.ts`, `review/interaction-review.md`, `review/checks.json` | One, 1/1 joint pass |
| Naturalistic forward | `evaluations/pi-prompts/desktop-plugin-ui-build-naturalistic.md` | `extension/releases.ts`, `review/design.md`, `review/validation.json` | Three fresh workspaces, at least 2/3 joint passes |
| Generalization | `evaluations/pi-prompts/desktop-plugin-ui-build-generalization.md` | `blueprint/implementation.md`, `blueprint/contracts.json` | Three fresh workspaces, at least 2/3 joint passes |
| Boundary recovery | `evaluations/pi-prompts/desktop-plugin-ui-build-boundary.md` | `fallback/recommendation.md`, `fallback/interaction.json` | One, 1/1 joint pass |

Use the repository strict JSON isolated Pi harness with the default Spark
model, or a separately recorded explicit model exception. Include every
required artifact with `--expect-output`. Record frozen payload hashes,
commands, model, all attempts, read surface, and failure classifications.
The copied skill remains unchanged. Read only task and relevant runtime
bundle resources; do not use fixture examples, sibling skills, installed
package sources, global context, network or provider calls beyond the outer
forward-test model. Check command traces for indirect reads and mutations.

## Independent artifact review

For every case:

- Verify exact nonempty files and parse JSON independently. Check required
  fields and H1-H10 coverage, actual semantic content, and English authored
  text. A field's existence is insufficient.
- Assess the task outcome, required choices, visible controls, primary
  action, state and recovery behavior, and architecture together. Counts
  must have clear counting rules and match the implementation or plan.
  One control can offer several choices; explain rather than conflating
  control count with decision count. A low count alone proves no quality.
- Check that local selection, filtering, status, cancellation and validation
  do not require an assistant completion. Optional model analysis requires
  an explicit user action. No fabricated progress or implicit acceptance.
- H1-H10 findings must name actual interactions and evidence, proposed fixes
  or concrete checks. Justified `not-applicable` and `untested` are valid;
  uniform generic passes with no supporting inspection are not.
- Default palette is ColorSet 1. Host-native theme/control paint is scoped
  honestly; do not require exact authored hex values where no authored
  styling is available. Verify exact tokens/contrast if the output claims
  them. Preserve keyboard operation and host accessibility behavior.
- Separate declarations, inspected source, mocks/protocol checks, actual
  host rendering, and user studies. Offline task flags cannot claim native
  paint, host acceptance or user testing. A stub execution is evidence at
  that layer only. Sources must be exact bundled primary URLs and not imply
  current re-verification.

For executable Pi contract and naturalistic artifacts:

1. Compile or transpile the TypeScript and load the default initializer
   with an evaluator-owned Pi API stub. Type-only upstream imports are
   acceptable; unexplained runtime dependencies or services are not.
2. Capture command registration. The required command must exist and expose
   the current documented handler contract, rather than merely describing
   an extension in comments.
3. Invoke the command with a UI context and scripted native selections for
   each offered filter. Capture emitted display data and verify exact IDs,
   status/priority values, selection membership and absence of invented rows.
4. Invoke with the native cancellation value. Verify that the handler
   returns without selecting a filter, mutating persistent state, or
   triggering a model turn. An explicit cancellation notice is acceptable.
5. Invoke without UI. Verify useful caller-visible text with the supplied
   rows and an actionable interactive route, with no dialog invocation.
6. Configure every provider/network/process/persistent-write method in the
   stub to reject or record calls. Normal paths must make zero such calls.
   Ordinary custom-message display is allowed only without triggering a
   model turn. No permission-sensitive real actions are needed for this task.
7. Review the real-host load command against the documented extension
   loading contract. A stub check does not count as real TUI paint or a live
   interactive run; record this limitation and remaining manual checks.

For generalization:

- Cover all seven explicitly named product/surface combinations. Preserve
  Claude Chat versus Code, Codex desktop versus CLI, and Pi extension
  distinctions. File, transport and packaging routes cannot rely on one
  universal plugin manifest or on product names alone.
- The proposal must be buildable at the blueprint level: named artifacts,
  meaningful shared logic and adapters, realistic conditions, fallback,
  and local validation for each route. Missing real host checks stay pending.
- Draft correction and cancellation preserve the original authoritative
  input. Invalid rows cannot silently commit; explicit model explanation
  cannot be conflated with deterministic review or commit.
- Compare complexity with one plausible alternative without adding a
  dashboard/server/model call merely because it is available.

For boundary recovery:

- Honor every stock-CLI and zero-extra-process constraint while preserving
  a useful read-only reporting path. The graphical-sidebar preference is
  subordinate to the user's explicitly stated task-success preference.
- Rich-form support is conditioned on real negotiation/frontend behavior.
  Always provide usable text recovery, input preservation and cancellation.
- Do not substitute an owned frontend, browser, global configuration, host
  activation or provider call. Do not convert absent evidence into failure
  or an unconditional unsupported claim.

## Acceptance and retained failures

Joint pass requires strict harness, independent artifact validation and
semantic/manual review on the same attempt. Preserve unsuccessful outputs
and classify skill, agent, validator, harness, infrastructure, or external
service failures before making corrections. Keep different model cohorts and
frozen subjects separate. Meeting these scoped thresholds does not close the
skill's pre-existing broader validation gaps or establish live acceptance
across all hosts.
