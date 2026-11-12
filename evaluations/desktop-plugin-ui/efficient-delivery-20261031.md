# Efficient UI delivery and OpenUI guidance validation

Date: October 31, 2026, America/New_York. Executions after midnight UTC use
November 1 run IDs. Result: the requested narrow advice revision is accepted;
desktop-plugin-ui keeps its broader validating status and historical limits.

## Change and decision coverage

Added [efficient-delivery.md](../../skills/desktop-plugin-ui/references/efficient-delivery.md)
and routed it from the skill entry, composition guide and authoring workflow.
The guide brings the requested reflections together without repeating the
host API catalogs, Nielsen table or installation procedures:

- Select the delivery surface by task, frontend and mode. Web MCP Apps and
  native/TUI controls are useful presentation families, not mandatory new apps.
- Share stable IDs, data/action schemas, authoritative state, validation and
  cancel/retry semantics. Keep host presentation, manifests, permissions,
  themes, focus and lifecycle in small adapters.
- Prefer predefined components for predictable tasks and reuse an existing
  framework/component library where it reduces work. A small view need not
  introduce an entire web application.
- Use OpenUI when model-chosen composition is itself useful and the renderer,
  component registry and action integration are available. Its coding-agent
  skill and documentation MCP connection do not install host renderers.
- Execute deterministic filters, selections, validation, navigation and known
  actions directly. Separate initial host opening turns, deliberate reasoning
  and ordinary tool/network traffic when counting inference.
- Justify a browser preview or owned client through a visual/persistent task.
  A Pi browser view is explicitly separate from its TUI; no embedded webview
  API is implied. An owned client does not inject stock Codex sidebars.
- Measure setup, first useful result, decisions, bundle/dependencies,
  maintenance and model requests where relevant; do not invent benchmarks.

The authoring table now allows a scoped preview or justified owned-client
proposal within authorized exploration while preserving deployment scope.
No framework or OpenUI runtime dependency was installed.

The citation helper adds three ownership/classification entries for OpenUI.
Its exact source-catalog matching is unchanged: recognized vendor ownership
does not approve arbitrary paths or establish a working integration.

## Subject and deterministic checks

Final source/runtime/full: **40 files**, **25 runtime references**, SHA-256
0c46695ae767c116e1c5d134f76c001809f777d054e566c5e747558d21226457.
All three profiles pass static authoring/structure audit, exact-copy checks and
source-integrity verification. This is a new subject, separate from the
[preceding composition study](ui-composition-20261031.md).

Commands and results:

    uv run --script projects/plugin-ui-exploration/scripts/test_openui_sources.py
    uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py --run-id openui-regression-20261101-1

New OpenUI cases: **20/20**, exit 0. Existing regression: **81/81**, exit 0.
Coverage includes exact Markdown/JSON citations, unlisted/mutated paths,
query/fragments, lookalikes/subdomains, HTTP/credentials/ports, allowance
bypasses and read-only inputs. Checker SHA-256:
af381b069c9d46ffa29a34725c1fd4c3a791dbd2ba532e4393dbd87d53f9efe9.
The guide's four recognized primary URLs also pass its exact-citation check.

All required repository commands pass:

    uv run --script scripts/validate-pattern-ids.py
    uv run --script scripts/validate-skills.py
    uv run --script scripts/test-skill-independence.py
    uv run --script scripts/check-repo-payload.py
    uv run --script scripts/test-pi-eval-harness.py
    uv run --script projects/plugin-ui-exploration/scripts/audit_ui_payload.py
    uv run --script projects/plugin-ui-exploration/scripts/sync_ui_skill.py

Pattern IDs: 1,348; Pi harness: 17/17. The scoped sync invokes the actual
sync-local-skills.py, then --check, through a temporary one-skill project
source. Both exit 0; **40/40 source-owned installed files** match canonical
hashes, other installed skills are preserved, and verified staging is removed.

## Frozen isolated cases and outcomes

The [criteria](delivery-criteria-20261031.md) were frozen before forward runs:
one contract pass and at least two of three naturalistic joint passes. The
runtime profile copies only this skill, disables ambient discovery, requires
exact outputs, strict JSON, actual model identity, zero tool errors and an
unchanged payload.

Final model: openai-codex/gpt-6.1-sol, medium reasoning, under the existing
per-run exception. All four final runs use the exact 40-file subject above.

Run IDs share prefix 20261101-desktop-ui-delivery-:

| Suffix | Required outputs | Strict | Independent artifact | Duration |
| --- | --- | --- | --- | ---: |
| contract-sol-1 | deliverables/native-choice.md and deliverables/source-check.json | Pass | Pass | 71.359 s |
| naturalistic-sol-1 | deliverables/delivery-plan.md and deliverables/decisions.json | Pass | Pass | 145.514 s |
| naturalistic-sol-2 | Same two exact outputs | Pass | Pass | 156.600 s |
| naturalistic-sol-3 | Same two exact outputs | Pass | Pass | 184.457 s |

Result: **contract 1/1** and **naturalistic 3/3 joint passes**. The contract ran
the exact source-checker command and inspected passed=true with two checked
OpenUI URLs. Naturalistic JSON has 8/9/9 unique host/surface routes, covering
all seven requested targets plus useful distinct transport/noninteractive
routes. Independent schema controls and full semantic review pass. The plans
preserve existing React reuse, shared state authority, direct actions,
conditional generated UI and justified future spatial editing. Their prose
is thorough rather than maximally concise, a nonblocking editorial limit.

All four trace summaries pass the observed Sol model, prompt-first/entry reads,
valid JSON, zero tool errors and a focused read surface. No acceptance gallery,
sibling skill, project file, repository document or global configuration is
used by the forward agents. Exact commands, complete artifact judgments and
trace details are in the
[independent forward review](delivery-forward-review-20261031.md).

Representative contract command:

    uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-delivery-contract.md --mode json --strict --require-exact-command-from-prompt --model openai-codex/gpt-6.1-sol --thinking medium --run-id 20261101-desktop-ui-delivery-contract-sol-1 --expect-output deliverables/native-choice.md --expect-output deliverables/source-check.json --expect-output-json-field deliverables/source-check.json::passed=true --timeout-seconds 360

The three naturalistic commands use desktop-plugin-ui-delivery-naturalistic.md,
their indexed run IDs, both exact delivery-plan.md/decisions.json outputs and
--timeout-seconds 480, retaining the same strict/model/thinking settings.

## Retained attempts and practical limits

Spark contract-spark-1 is retained separately. Its actual trace reports the
ChatGPT account does not support gpt-5.3-codex-spark, before tools with zero
usage and no output. Sol is a per-run exception, not a global setting change
or a Spark pass. A final wording clarification distinguishing Pi TUI from a
separate browser view occurred before freezing the four Sol subjects.

Independent source review found no blocking unsupported-host, duplication or
authorization issue. The forward tests grade recommendations and proposed
acceptance plans, not executed native integrations or performance rankings.
No new screenshots were required for this prose/catalog change; the preceding
vision study remains a separately bounded subject. No new signed-in host
paint, OpenUI-inside-MCP-App implementation, clipboard/export effect or user
preference is claimed.

Raw runs remain under ignored evaluations/runs. Project manifests retain
openui-source-checks.json and delivery-repo-checks.json,
delivery-payload-audit.json, delivery-local-sync.json, the independent
schema/adjudication results and four delivery trace summaries. Earlier
composition receipts are preserved separately; no historical cohort is pooled.
