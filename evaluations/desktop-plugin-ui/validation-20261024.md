# Desktop plugin UI knowledge skill validation

Date: 2026-10-24. Canonical bundle: `skills/desktop-plugin-ui/`. The user asked
for an information skill about plugin UI in “Cloud Desktop,” with at least ten
rule-based patterns and investigation of working/failing methods. Product
clarification remained unanswered; development explicitly assumed **Claude
Desktop** from the existing plugin context. The skill preserves that ambiguity
rule for future requests and distinguishes ordinary Chat from the Code tab.
All skill content, research notes, scripts, and reports are in English.

## Final subject and scope

The final runtime, source, and full profiles each contain **nine files**, with
SHA-256 `93deff855cc7172a09e125235323e8fda95121b532d017e1cb14284764508149`.
There are no runtime dependencies on project probes, sibling skills,
repository documents, acceptance galleries, or installed adapter projects.
The source checker uses Python 3.11+ standard library; `uv` is a convenient
runner rather than a required Python library dependency.

The bundle contains **25 unique canonical patterns**:

| Reference | Count | Mechanisms |
| --- | --- | --- |
| `chat-patterns.md` | 10 | Text fallback, inline card, option carousel, fullscreen, validated form, chart/canvas, file preview/export, responsive theme, progressive details, async state |
| `bridge-patterns.md` | 6 | Tool/resource registration, server actions, model context/follow-up, display negotiation, CSP/sandbox, optional capabilities |
| `native-patterns.md` | 6 | Panes, input/select, SVG/image preview, links/copy/process actions, lifecycle/feedback, custom native Client regions |
| `host-prompts.md` | 2 | Host-rendered MCP elicitation and native render-site customization |
| `distribution.md` | 1 | MCPB host-generated installation/settings form |

Every pattern records trigger/input, implementation rule, failure/fallback,
validation action, and scoped evidence. Sources and probe methods are bundled
progressively; individual references are about 4–10 KiB. Names and descriptions
are metadata-only; automatic invocation remains enabled by default.

The skill is advisory. Its release criterion is producing correct bounded
recommendations, rather than installing a connector or proving every possible
UI in an actual signed-in host. It labels documentation, SDK tests, synthetic
browser fixtures, native hook-engine tests, conditional features, and untested
host behavior separately. No Claude Desktop account installation, Desktop
painting, OS delivery, real clipboard mutation, external messaging, browser
permission grant, or production deployment was performed or claimed.

## Executed compatibility research

**MCP/browser:** 25 assertions pass with MCP SDK 1.32.1, ext-apps 1.7.5,
Playwright 1.64.1, Node 24.18.0, and Edge 156.0.4314.42. A real linked SDK
client/server checks metadata, MIME, useful text/data and schema rejection. The
real App SDK runs inside an opaque-origin sandboxed browser iframe connected
to a deliberately synthetic protocol host. It checks delivery, interactive
updates, retained value after error, context/message shapes, returned display
modes, open/download request transport, unsupported capability denial, unknown
tool rejection, parent DOM isolation, file-path assignment rejection, CSP
network denial, theme updates, keyboard disclosure and 360px layout.

The first probe failed an evaluator assumption: `downloadFile` still dispatched
without advertised support. The corrected fixture explicitly rejects it and
retains a separate assertion proving method existence is insufficient.
Fullscreen, PiP denial, context delivery and downloads use synthetic host
responses; none establishes the corresponding real Claude action. Desktop and
narrow screenshots were inspected. The report and screenshots remain ignored
under `projects/desktop-plugin-ui/artifacts/mcp-probe/`.

**Native Mods:** Official Claude Code 2.1.302 passes strict plugin validation
and **34/34 native hook-engine tests**, including six real Client module
checks. Executable SHA-256:
`3ab075f78998efef8b87f491c2e4a39c309dddf44e51d0103eba4f3713d2a0ae`.
Tests exercise three surface trees, input/change/submit/select, invalidation,
graphics restrictions, URL downgrades, oversized payload rejection, invalid
autofocus, duplicate values, native Client state/pointer/key/frame/resize/post,
and argument/event boundaries for process, copy, feedback and pane placement.
External effects are stubbed; actual native tree/Client execution is real.
Exploratory failures are retained, including incorrect leaf children, URL
rejection expectations and constructor-presence detection. The full commands
and all 34 observations are in
[the native research ledger](../../projects/desktop-plugin-ui/research/mods-results.md).

**Source checker:** The evaluator-owned deterministic suite passes **18/18**
cases. The pre-fix 16/18 result is retained. It prompted narrow fixes for
single-quoted code URLs and URL-as-label Markdown links. The checker audits
both Markdown and JSON, reports exact canonical candidates, distinguishes
diagnostic status from optional CI exit failure, validates JSON, accepts
explicitly verified new URLs, and does not change input files or skill sources.
[Full cases and hashes](source-checker-20261024.md).

Reproduction commands, from the repository root unless stated otherwise:

```powershell
# Run from projects/desktop-plugin-ui/mcp-probe after npm ci --ignore-scripts:
npm run probe

$env:CLAUDE_CONFIG_DIR = Join-Path (Get-Location) 'projects/desktop-plugin-ui/artifacts/mods-config'
$probeExecutable = 'projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/@anthropic-ai/claude-code-win32-x64/claude.exe'
& $probeExecutable plugin validate projects/desktop-plugin-ui/mods-probe --strict
& $probeExecutable plugin test projects/desktop-plugin-ui/mods-probe

uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
```

The native executable was read from an existing installation; the new skill
does not require that project or executable path. The project files are
investigation sources rather than published examples. No Pages content or
example catalog was changed, so there was no publication step.

## Isolated forward evaluation

Spark was attempted first. Retained run
`20261024-desktop-ui-contract-spark-1` was provider-rejected before tools:
`gpt-5.3-codex-spark` is unsupported with this ChatGPT account. No artifact or
skill-quality pass is inferred from its exit code. `SKILLS.md` recorded the
deliberate model exception **openai-codex/gpt-5.6-luna** before its use.

All Luna runs use Pi 1.4.0, high thinking, JSON strict mode, separate workspaces,
the runtime payload only, disabled ambient context/extensions/skills/templates/
themes, exact expected outputs, observed-model checking, unchanged copied
payload and zero tool-error gates. No tested agent had network or a live host.

Final cohort results are recorded after completion in the linked independent
reviews and the retained `desktop-ui-v3-artifact-audit.json`.

| Case | Final run IDs below `evaluations/runs/` | Required outcome |
| --- | --- | --- |
| Contract | `20261024-desktop-ui-v3-contract-luna-1` | One strict and independent artifact pass |
| Naturalistic inventory recommendation | `20261024-desktop-ui-v3-naturalistic-luna-{1,2,3}` | At least two joint passes in three fresh runs |
| Cross-host generalization | `20261024-desktop-ui-v3-generalization-luna-{1,2,3}` | At least two joint passes in three fresh runs |
| Boundary review | `20261024-desktop-ui-v3-boundary-luna-1` | One strict and independent artifact pass |
| Metadata routing control | `20261024-desktop-ui-routing-luna-1` | 10/10 metadata decisions, no forced skill |

Final outcome: **8/8 strict, 8/8 structural/source, and 8/8 independent semantic
passes** on the same frozen nine-file subject: contract 1/1, naturalistic 3/3,
generalization 3/3, boundary 1/1. All observed models match the recorded Luna
exception. Trace summaries contain valid JSON, zero tool errors, no forbidden
reads, and unchanged copied payloads. Agents read the entry point and relevant
compact in-bundle references, wrote exact requested files, and checked every
generated Markdown/JSON report with the bundled helper. They did not access
repository docs, sibling skills, project research, or acceptance galleries.
The final source/runtime/full audit and repository gates pass; skill status is
**done for its advisory scope**.

The independent reviews are
[contract/boundary](v3-contract-boundary-20261024.md) and
[naturalistic/generalization](v3-naturalistic-generalization-20261024.md).
They retain a nonblocking wording ambiguity in one inventory proposal's
introductory server explanation operation; its operative context/sendMessage
recipe is correct. Six independently repeated source audits cover 102 official
URL occurrences with no findings or allowlist overrides. Contract and boundary
each also audit both formats. No result claims actual signed-in host acceptance.

Independent semantic reviews inspect the actual Markdown/JSON, schemas,
canonical IDs, bounded host claims, route selection, state/error behavior,
source URLs in **both formats**, and practical validation plans. They are
separate from mechanical harness passes. The final skill also requires agents
to check both output formats with the bundled source checker before delivery.
The evaluator-owned [artifact inspector](inspect_runs.py) independently records
structural/source checks and frozen hashes; it does not replace semantic review.

Commands use the four prompts under `evaluations/pi-prompts/` and these flags:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-contract.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-v3-contract-luna-1 --expect-output results/reference.md --expect-output results/decisions.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-v3-naturalistic-luna-1 --expect-output proposal/ui.md --expect-output proposal/decision.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-generalization.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-v3-generalization-luna-1 --expect-output handoff/cross-host.md --expect-output handoff/matrix.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-boundary.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-v3-boundary-luna-1 --expect-output review/boundaries.md --expect-output review/status.json --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/<run-id>/read-surface.json
uv run --script evaluations/desktop-plugin-ui/inspect_runs.py --prefix 20261024-desktop-ui-v3- --output evaluations/runs/desktop-ui-v3-artifact-audit.json
```

All three naturalistic and generalization repetitions were invoked with their
individual retained IDs. The helper refuses workspace reuse; use a fresh ID
when reproducing. [Routing evidence and exact command](routing-20261024.md)
records 10/10 metadata-only decisions. It does not claim real application
auto-selection; metadata is unchanged across the later subject revisions.

## Retained development subjects

- Initial seven-file hash
  `8ae7ae5066ab3eee6913ecbb57f137204f15aba527d7eafc4f0e2b82e65c4808`:
  strict 8/8; independent 7/8. Contract failed an agent-generated `.com` source
  domain replacing bundled `.io`; boundary and both 3/3 cohorts passed.
  [Contract/boundary](contract-boundary-20261024.md),
  [naturalistic/generalization](naturalistic-generalization-20261024.md).
- Revision 2 eight-file hash
  `e6595579f0c0ab026a9fa1e60e65578926d583d11f306d2693dd14b69f7e1518`:
  adds exact-copy guidance and host elicitation/render-site coverage. Strict
  8/8; independent 7/8. Contract correctly cites Markdown but mutates `.io` to
  `.org` inside JSON. This remains an artifact failure, classified `agent`.
  [Contract/boundary](v2-contract-boundary-20261024.md),
  [naturalistic/generalization](v2-naturalistic-generalization-20261024.md).
- Final revision adds the deterministic source catalog/checker because prose
  guidance alone did not prevent the observed citation error. No generated
  evaluation output was repaired by the evaluator. Fresh final runs are not
  pooled with earlier results, and no subject received selective rerolls.

## Repository and bundle gates

Run pattern IDs, complete repository skill validation, independence, payload,
17 harness tests, explicit diff checks and local installation sync/check.
The scoped source/runtime/full authoring audit passes all three profiles with
the same nine-file final hash. A slower whole-repository authoring-copy audit
was cancelled after source changes made its initial snapshot obsolete; it
contributes no pass. The scoped audit is retained under
`projects/desktop-plugin-ui/artifacts/bundle-audit/report.json`.

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/audit-skill-authoring.py --skills projects/desktop-plugin-ui/artifacts/bundle-audit/source --check-bundles --output projects/desktop-plugin-ui/artifacts/bundle-audit/report.json
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
git diff --check
```

The bundle-audit source directory is an exact task-owned copy of the frozen
skill. Local synchronization refreshes the ignored installation; canonical
edits remain under `skills/`. Existing unrelated working-tree changes were
preserved. No commit, push, installed-account mutation or publication occurred.

The final ordinary sync copied two changed files. A supported scoped sync/check
using a fresh exact nine-file task copy additionally passed: zero remaining
changes and installed-bundle validation. That temporary source was then moved
under ignored `projects/desktop-plugin-ui/artifacts/local-sync-stage/`.
The copy was non-ignored while calling the sync helper so its Git-aware source
inventory contained all nine files. This targeted result verifies the new
skill. The ordinary whole-installation recheck subsequently also passed:
all **10,508** source-owned files matched and installed bundles validated.
