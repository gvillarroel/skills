# Codex, Pi and Claude UI composition study

Date: 2026-10-31. Result: the requested composition-guidance revision is
implemented and accepted by the scoped checks below. Preserve the skill's
broader validating status for historical strict failures and live-host/user
coverage outside this revision; do not pool those older subjects with this one.

## Research and final runtime subject

Primary documentation was rechecked for Codex MCP UI and app-server forms,
ChatGPT-specific extension placements, Pi extensions/TUI/RPC, and Claude Chat
MCP Apps versus native Mods. Observed local versions: npm Codex CLI 0.145.0,
Pi 1.4.0 and Claude Code 2.1.302. Installed Codex experimental schema generation
exited 0 and exposed the extended-form opt-in and elicitation request. Schema
generation is contract evidence, not form execution or frontend paint.

Project research notes: [Codex](../../projects/plugin-ui-exploration/research/codex-ui.md),
[Pi](../../projects/plugin-ui-exploration/research/pi-ui.md) and
[Claude](../../projects/plugin-ui-exploration/research/claude-ui.md).
The final skill adds two compact runtime references, ui-composition.md and
visual-review.md, and targeted Pi/native composition guidance. Six recipes
cover focus/disclosure, status/inspector, choice/command, preview/controls,
summary/workspace and shared surfaces. Each includes input, rule, fallback
and validation. The matrix now preserves bounded historical Codex desktop
chart paint instead of implying that every desktop paint path is untested.

Final source/runtime/full payload: **39 files**, SHA-256
48a9e002e36aaa756babd78af3b7ae52d3d33c223002c7e9dd38a144bcddbf6b.
All three profiles were audited, matched exact copies and retained unchanged
canonical source. Runtime reads need no acceptance gallery or project file.

## Actual vision review and repairs

The [project prototype](../../projects/plugin-ui-exploration/prototype/index.html)
contains six stable local scenes and three comparison pairs. It is visibly
labeled as a browser design prototype, and its terminal is explicitly synthetic.
It is not a published example set and does not change the Pages catalog.

The root and an independent reviewer actually received and inspected PNG
pixels through view_image. Initial review covered all six before captures at
360 and 1280 px. Independent repaired-state review covered all nine pair
captures at 360/768/1280 px plus 320 px error/focus, 360 px keyboard focus,
result preview and long filename/path: **13 repaired images**. The root
separately inspected the focused/error, preview and long-path states.

| Finding | Repair and bounded recheck |
| --- | --- |
| Comparisons changed task scope and facts. | Inline sides now share 24 changes, three files and unapplied state; both terminal sides choose workspace in fixed Development. The exaggerated completion baseline remains explicitly a failure illustration, not a measured product baseline. |
| Recommended Copy path only displayed text. | The action is named Show path and focuses the visible full destination. No clipboard effect is claimed. |
| Inspect result opened diagnostics rather than content. | It opens matching export ID/path and two actual synthetic CSV rows; validation remains a separate disclosure. Hide/Escape restores focus. |
| Global Escape could affect a neighboring busy card. | Handlers belong to their card, chooser or preview. Browser checks verify that another surface retains its busy state and focus ownership. |
| Reopened chooser lacked an exit. | Visible Cancel and chooser-local Escape preserve the committed workspace and return focus. |
| Implementation commentary, nested borders and global state selector added ambiguity. | Study notes moved outside task content, the nested border was removed and Inline review state hides on unrelated scenes. |
| Narrow target sizes and long paths needed checking. | Recommended controls are at least 44 CSS px high; long names/paths wrap; actual 320 px error/focus capture retains recovery and context. |

The independent [source review](../../projects/plugin-ui-exploration/research/independent-review.md)
and [before/after vision review](../../projects/plugin-ui-exploration/research/vision-review.md)
retain initial findings and limits. No material clipping, overlap, hidden
recovery or ambiguous artifact identity remained in the pictured recommended
states. Paired-gallery whitespace and weak-first mobile order remain
nonblocking study-presentation costs; single-scene links isolate the task UI.

These observations support bounded design choices: separate summary, detail,
status and committed result; preserve native context and other plugins;
use rich workspaces when the task needs them. They do not prove that users
always prefer fewer controls, that dashboards/logs are poor in general, or
that a browser prototype paints in a native host.

## Browser and deterministic checks

Command:

    uv run --script projects/plugin-ui-exploration/scripts/verify_prototype.py --browser C:/Users/villa/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe

Final result: **52/52 checks pass**, exit 0. Coverage includes unique scene IDs,
recommended views/targets at 320/360/768/1280 px, six synthetic states, real
keyboard and pointer activation, visible keyboard focus, duplicate prevention,
error/retry/cancel context, chooser reopen/cancel/focus, Escape isolation,
truthful path action, artifact content and preview exits, long-name wrapping,
literal palette membership, zero page script errors and zero external
browser requests. This is browser behavior, not native integration.
Synthetic state injection does not test real IO failures, exports or jobs.

The palette helper computed nine relevant opaque color pairs. Ordinary text
pairs pass 4.5:1; the terminal #696969 border against #1c1c1c is 3.1043:1 and
passes the applicable 3:1 non-text threshold, but would fail ordinary text.
It is not used for ordinary terminal text. Ratios do not establish a full
accessibility audit, host theme compliance or compositing acceptance.

Capture reproduction:

    uv run --script projects/plugin-ui-exploration/scripts/capture_prototype.py --browser C:/Users/villa/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe --pair inline --width 360 --label after

The helper also accepts terminal/completion pairs, --scene, --state, --focus
and other widths. Before captures were retained; after captures use a prefix.
Screenshots and machine manifests live in ignored project artifacts.

## Isolated forward validation

Frozen [criteria](composition-criteria-20261031.md) require one contract pass
and at least two of three naturalistic joint strict/artifact passes. All four
final runs used the final 39-file subject, strict JSON runtime payload,
openai-codex/gpt-6.1-sol with medium reasoning, exact required output paths,
no ambient discovery and unchanged copied skill resources.

| Final run suffix | Required outputs | Strict and independent artifact | Duration |
| --- | --- | --- | ---: |
| final-contract-sol-1 | deliverables/choice.md | Pass | 44.318 s |
| final-naturalistic-sol-1 | deliverables/review.md and deliverables/acceptance.json | Pass | 248.156 s |
| final-naturalistic-sol-2 | Same two exact outputs | Pass | 230.806 s |
| final-naturalistic-sol-3 | Same two exact outputs | Pass | 208.248 s |

Run prefix: 20261031-desktop-ui-composition-. Result: **contract 1/1** and
**naturalistic 3/3** joint passes. Independent review inspected full artifacts,
JSON plan structure, bash commands and read surfaces; the plans contain
22/22/26 unique actionable scenarios. All four trace summaries verify the
observed Sol model, valid JSON, zero tool errors and prompt-first reads; no
gallery, sibling skill, repository document, project artifact or global
configuration was read. The naturalistic six-surface task explains its
13-15 compact reads; no large gallery/source substitute was used.

See [independent forward review](composition-forward-review-20261031.md) for
complete case outcomes, semantics, exact outputs and trace checks. These runs
produce designs and acceptance plans as requested, not executed native plugins.

Representative final command:

    uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-composition-contract.md --mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium --run-id 20261031-desktop-ui-composition-final-contract-sol-1 --expect-output deliverables/choice.md --timeout-seconds 360

For each naturalistic index 1, 2 and 3, the actual command used
desktop-plugin-ui-composition-naturalistic.md, the matching final-naturalistic-sol
run ID, --expect-output deliverables/review.md, --expect-output
deliverables/acceptance.json and --timeout-seconds 480 with the same strict
model/thinking options. Prompt source files remain versioned under pi-prompts.

## Repository and local installation

All commands exited 0 on the final source:

    uv run --script scripts/validate-pattern-ids.py
    uv run --script scripts/validate-skills.py
    uv run --script scripts/test-skill-independence.py
    uv run --script scripts/check-repo-payload.py
    uv run --script scripts/test-pi-eval-harness.py
    uv run --script projects/plugin-ui-exploration/scripts/audit_ui_payload.py
    uv run --script projects/plugin-ui-exploration/scripts/sync_ui_skill.py

Pattern validation covers 1,348 IDs; the Pi harness has 17 passing tests.
The scoped sync reproducer invokes the actual sync-local-skills.py with a
temporary, project-local one-skill source and .agents/skills destination.
Both sync and --check pass; **39/39 source-owned installed files** match
canonical hashes. Other skill installations are preserved. Temporary staging
was removed only after verifying its resolved path inside this project.

The composition-era repository, payload and installation receipts are retained
as composition-repo-checks.json, composition-payload-audit.json and
composition-local-sync.json. Later guidance revisions use separate delivery
receipts. Prototype-browser.json, contrast.json, contrast-secondary.json and
the composition forward/trace results remain separate as well.

## Retained failures and recovery

The initial environment loaded DOM snapshots but timed out on screenshots and
pointer stability. Subsequent shell dispatch and native inventory also stalled;
a UI session reset ended in a 300-second tool transport timeout. A later
continuation found the old process handles missing and fresh shell dispatch
working; only then were executions restarted. No application setting was
changed, and no product exclusion was inferred from this outage.

Spark run 20261031-desktop-ui-composition-contract-spark-1 is retained:
its actual event trace reports that gpt-5.3-codex-spark is unsupported for this
ChatGPT account, before tools, with zero usage and no required artifact.
The existing per-run Sol exception was used without changing semantic
thresholds or global model settings. The earlier Sol dispatch during the outage
created no run directory; a separate recovered pre-promotion contract
(contract-sol-2, older fd7c4d987... subject) passed but is not pooled with final
acceptance.

The browser evaluator first used a stale Cancel label and then assumed the
CSV preview was a table rather than preformatted CSV. These evaluator errors
were corrected against the actual visible contract; the final independent
outcome checks pass. They are not product regressions or isolated-model tool
errors. The source review and old captures retain the real prototype defects.

## Practical limits

No new signed-in Codex/Pi/Claude native paint, OS clipboard/download effect,
real export/server failure, multi-plugin installation, forced-colors audit,
representative-user preference or measured task-time advantage is claimed.
The synthetic terminal cannot establish native columns/rows or retained
transcript/editor space. Existing historical host evidence remains separate.
These are explicit evidence limits; the requested skill guidance, actual
vision critique, scoped forward tests and repository checks are complete.
