# Copilot and Codex capability study

Date: October 25, 2026. Platform: Windows. This pass completes the available
local verification work and studies practical plugin UI offerings in Codex
and GitHub Copilot. All authored components, accessible copy, probes and
reports are English. Preserve the separate Claude/ChatGPT evidence in the
[cross-assistant study](cross-assistant-validation-20261024.md).

The later [live readiness follow-up](live-followup-20261025.md) supersedes this
pass's pending-trust assumption: workspace trust cleared, the user chose to
skip Copilot sign-in, and the Codex app tab was briefly discovered before a
binding failure. Keep those later results and subject identity separate.

## Current practical findings

The [Codex matrix](../../projects/desktop-plugin-ui/capability-study-20261025/codex/capability-matrix.json)
has 21 capability rows; the [Copilot matrix](../../projects/desktop-plugin-ui/capability-study-20261025/copilot/capability-matrix.json)
has 22. These are scoped offerings and limitations, not 43 universally accepted
widgets. Both studies keep documentation, protocol transport, runtime callbacks,
real extension-host behavior and assistant frontend paint separate.

| Surface | Useful offering | Measured boundary |
| --- | --- | --- |
| Codex npm CLI 0.145.0 | Structured tools, standard elicitation, media/resource transport and versioned synthetic state | Backend assertions pass; terminal/frontend pixels are separate. |
| Codex desktop package 26.1021.3705.0, bundled core 0.164.0-alpha.11.1 | Same tested core contracts; component routes through supported MCP configuration | Historical Codex-mode inline chart paint is attributed separately; this current study's fresh chart result establishes metadata, not new controls/paint. |
| Codex IDE | Direct MCP integration documented separately from plugin bundles | Current official plugin-bundle controls exclude the IDE extension; this does not exclude IDE MCP tools. No fresh IDE rendering is claimed. |
| Copilot CLI 1.0.103 / SDK 1.0.26 | Confirmation, choice, input and extension actions | Fresh callbacks pass; historical terminal painter evidence remains separate. Renderer opt-in and feature gates matter. |
| Ordinary VS Code extension, 1.143.1 | HTML panel, validated actions, host theme variables, temporary JSON state and constrained resource/script access | Eight real extension-host checks pass; this does not establish Copilot Chat paint. |
| Copilot Chat MCP Apps in VS Code | Documented sandboxed inline cards/forms/charts, context attachments, drafted follow-ups and clipboard | Fullscreen/PiP and camera/microphone/geolocation are excluded by this host's support table. Signed-in rendering remains pending. |
| VS Code preview canvas / standalone GitHub Copilot app canvas | Documented shared work surfaces through their own supported harnesses/extensions | CLI capability flags do not prove either renderer. No standalone GitHub app executable or canvas paint was verified here. |

See the [Codex report](../../projects/desktop-plugin-ui/capability-study-20261025/codex/report.md)
and [Copilot report](../../projects/desktop-plugin-ui/capability-study-20261025/copilot/study.md)
for exact commands, per-feature limits, primary sources and retained failures.
The installed Microsoft consumer Copilot executables are distinct from GitHub
Copilot and do not establish a GitHub desktop-app installation.

## Empirical checks and corrections

- Codex: six current, version-aware cases pass **21/21 each**, totaling 126
  assertions across npm/bundled cores, approval/extension opt-in variations and
  per-process experimental MCP Apps flags. Prior baseline mismatches are retained:
  the newer core returns -32602 for an invalid nested schema where the older
  core returns -32601. This is not proof that all richer forms are unsupported.
- PID-bound Codex logs correct an earlier attribution: the process actually
  serving the tool advertises `openai/form` when opted in in **both** cores.
  An idle connection can omit it. Flat-form normalization and actual rich-form
  paint are different observations. The old missing-extension inference is
  withdrawn in the canonical reference.
- Copilot: **11/11** public inventory commands, **15/15** SDK/runtime cases,
  **2/2** ACP cases and **8/8** ordinary VS Code extension-host cases pass.
  Callback results are method-specific: confirmation decline/cancel both give
  `false`; selection cancel and input decline give `null`. Do not impose one
  universal false/null meaning.
- Webview state survives tested HTML replacement but is absent in a newly
  created panel after disposal. The runtime received host dark-theme values;
  they are host-mapped paint, not exact ColorSet pixels. Default script blocking,
  validated 7→8 actions, unknown-action refusal, CSP refusal and DOM isolation
  were exercised without Copilot inference.
- Three newly corrected local component copies pass **22 source/provenance**
  checks and **108 browser checks**, across 135 captured states and 63 screenshots
  at 1100, 360 and 320 pixels. Historical generated outputs remain unchanged.
  Contrast, alpha/opacity, borders, missing Explain actions, responsive table
  alternatives and tooltip association/dismissal/pointer/bounds were repaired.
  See the [verification closure](verification-closure-20261025.md).
- The new bundled design-value helper passes **16/16** project tests, covering
  230 exact token-path resolutions, 13 independent contrast expectations,
  unsupported syntax, diagnostic/CI behavior and a read-only relocated bundle.
  The separate existing design-contract verifier passes **20/20**.

These study probes started **zero Claude or Copilot model inference turns**.
The Copilot SDK provider guard observed zero requests. OpenAI-only isolated
skill trials are counted separately below. Documentation retrieval, public
catalog calls and app initialization are not described as network-free.

## Access and interaction gates

The visible task-profile VS Code workspace was observed in Restricted Mode,
with Models unavailable and Sign In present. Human workspace-trust review and
GitHub authentication remain pending. Read-only Running Extensions inspection
did not show Copilot Chat active. Scoped logs have requested-but-not-granted
`authIssuers`/`languageModelRateLimit` diagnostics without an observed Copilot
activation failure stack; neither fatal incompatibility nor harmlessness is
established. No proposal bypass was attempted.

The Windows Computer Use skill prohibits automating authentication dialogs and
security/privacy permission requests. The root left these human steps pending,
rather than reclassifying them as a product exclusion. Task-scoped VS Code
arguments also allowed the app to initialize external shared storage; neither
agent read or edited that database. Profile flags are not complete filesystem
isolation.

The fresh Codex connected chart call returned CS1 metadata and export formats.
The MCP Apps controller exposed no expanded side-panel tab; inline-only apps
are outside its listed tabs. Expansion was requested from the user, and actual
controls remain untested. Historical direct-MCP chart paint is kept separate
from current-package acceptance. Returned download links, expired capabilities,
transported audio or method names do not establish OS delivery, playback or
device permission effects.

## Skill promotion and isolated validation

The reusable [capability guide](../../skills/desktop-plugin-ui/references/capability-offerings.md)
promotes current findings into the skill. The skill retains 42 canonical
interaction patterns, all ten Nielsen heuristics, CS1 by default/explicit CS2,
host-owned styling boundaries and English visible/accessible content rules.
The new [design-value helper](../../skills/desktop-plugin-ui/scripts/design_values.py)
resolves exact paths and computes unrounded contrast without dependencies,
network or writes. Role-specific contrast flags must still be inspected.

The first offerings subject contains 21 source/runtime/full files, SHA-256
`26b12b4879ba0e4663b7d225bba066424f1baa1dee7d1461ba1c84a4de1060a5`.
Its first retained cohort passes strict execution 3/5 and report checkers 5/5,
but conservative manual/joint acceptance 0/5: omitted empirical ledger rows,
one canvas host/version misattribution and one MCP App/webview CSP crossover.
Contract and boundary runs also have three edit-tool errors and one Windows
`/tmp` path error respectively. All requested outputs/false task flags/payload
integrity pass. Numeric/token/English positives do not erase these failures.
See [contract v1](offerings-contract-v1-luna-1.md),
[naturalistic v1](offerings-naturalistic-v1-luna.md) and
[boundary v1](offerings-boundary-v1-luna-1.md).

A compact [report-authoring procedure](../../skills/desktop-plugin-ui/references/report-authoring.md)
addresses those errors: ledger first, every reused empirical fact reconciled,
versions and mechanism-specific CSP kept attached, portable scratch paths and
structured JSON repairs. The separately frozen revised subject has **22**
matching source/runtime/full files, SHA-256
`42df224d120f4bfd71445670e55c25891cb8e540eb8a2ec6c21fb8ee7a9d34f6`.
Its five fresh cases use unchanged prompts and the unchanged
[pre-frozen review criteria](offerings-review-criteria.md). No v1 output is
repaired or replaced. The deliberate `openai-codex/gpt-5.6-luna` exception
continues after the prior Spark account rejection.

The revised cohort is complete, without reruns or reviewer repairs:

| Revised-subject case | Strict | Final checker | Conservative manual / joint |
| --- | --- | --- | --- |
| [Contract](offerings-contract-v2-luna-1.md) | 1/1 | 1/1 | 0/1 / 0/1 |
| [Naturalistic, three first attempts](offerings-naturalistic-v2-luna.md) | 2/3 | 3/3 | 0/3 / 0/3 |
| [Boundary](offerings-boundary-v2-luna-1.md) | 1/1 | 1/1 | 0/1 / 0/1 |
| Total for this subject only | **4/5** | **5/5** | **0/5 / 0/5** |

The added procedure improves ledger coverage and eliminates the prior CSP
crossover in this cohort, but does not meet the frozen semantic threshold.
Contract still omits a used top-DOM observation and misattributes a terminal
capability measurement to ACP. Boundary still omits the used terminal
`canvases:true` observation. Naturalistic outputs retain two stock-Codex
ownership restrictions, a missing capability row, or weak authored focus
without a contrast warning; the third also retains four failed text edits.
The final checker validates listed fields and URLs, not complete semantic
coverage. The retained outputs are evaluation evidence, not endorsed designs.

All five revised copies preserve the frozen 22-file payload, exact outputs,
false current-task acceptance flags and required Luna model. English copy,
canonical Nielsen labels, checked token bindings and explicit contrast
arithmetic pass their scoped independent reviews. Do not reinterpret those
positives as overall acceptance.

## Final repository and installation receipts

At the close of this initial study, the canonical source and local installation
both contained 22 files with
SHA-256 `42df224d120f4bfd71445670e55c25891cb8e540eb8a2ec6c21fb8ee7a9d34f6`.
Scoped source/runtime/full authoring audits pass. Source checking finds no
findings across 80 official URL occurrences. Source helper regressions pass
53/53; report helper regressions pass 33/33. The new helper's final 16-test
receipt is `projects/desktop-plugin-ui/artifacts/design-values-tests-20261025/offerings-final.json`.
Root additionally inspected desktop Explain and 320px default screenshots from
the corrected fixture; visible content is English and the narrow cards remain
readable. This is fixture review, not assistant acceptance.

Representative final commands:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-report-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-design-values.py
uv run --script projects/desktop-plugin-ui/scripts/verify-design-contract.py --output projects/desktop-plugin-ui/artifacts/data/offerings-v2-design-contract.json
```

Local synchronization used a scoped source snapshot with the normal
`scripts/sync-local-skills.py --source <study-snapshot>` helper and its `--check`
mode. Source and installed snapshots were independently compared. Both source
staging folders were then moved, with resolved project-boundary checks, into
ignored `projects/desktop-plugin-ui/artifacts/data/sync-source-snapshots-20261025/`.
Repeating the git-aware sync check against that ignored archive enumerated
zero source files; that result is noncertifying. An independent final
canonical-source/installation comparison explicitly requires 22 files and the
frozen hash and passes; its receipt is
`projects/desktop-plugin-ui/artifacts/data/offerings-v2-final-integrity-20261025.json`.
No unrelated skill installation was refreshed. No published Pages example,
deployment, commit or push was introduced by this pass.

Keep overall status **validating**: the revised advisory cohort misses its
semantic threshold, and live account/frontend checks remain unresolved.
These scoped results never pool earlier cross-assistant, design or English
cohorts into a new pass. The empirical study and curated capability reference
remain useful within their explicitly recorded layers and versions.
