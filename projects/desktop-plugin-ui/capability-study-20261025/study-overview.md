# Copilot and Codex UI capability study

Date: October 25, 2026, America/New_York. The user requested completion of
available verification work and an empirical study of the features each
coding assistant can offer. All authored components and reports are English.

## Study surfaces

| Surface | Current inventory | Evidence boundary |
| --- | --- | --- |
| Codex in the Windows desktop app | Appx `OpenAI.Codex` 26.1021.3705.0; bundled core 0.164.0-alpha.11.1 | Separate desktop frontend acceptance from backend/CLI tests. |
| npm Codex CLI | 0.145.0 | Preserve its results independently from the newer desktop core. |
| GitHub Copilot CLI | Current global and task-local binary 1.0.103 | Negotiated SDK/ACP capability is not visible canvas or MCP App acceptance. |
| VS Code and Copilot | Portable VS Code 1.143.1; bundled Copilot Chat 0.71.0 on disk | Actual extension activation, authentication and chat rendering remain separate checks. |

The installed Microsoft consumer/Office Copilot is not GitHub Copilot. A model
provider is also distinct from its assistant harness and renderer.

## Feature questions

For each surface, record the supported offering, input contract, limits,
fallback, version, execution layer and one useful success/failure where feasible:

- Text, structured results, images, HTML/SVG, files and exported artifacts.
- MCP App registration, iframe initialization, inline/panel/fullscreen modes.
- Native confirmation, selection, text entry and rich-form negotiation.
- Tool callbacks, authoritative state, local controls and inference cost.
- Context updates, drafted versus submitted follow-ups and clipboard actions.
- CSP/network isolation, host permissions, downloads and device access.
- Theme/palette ownership, English copy, keyboard/focus and accessible help.
- Close/reopen, persistence, deployment and account/workspace restrictions.

Use `observed-working`, `observed-failed`, `documented`, `conditional`,
`untested` or an explicit-contract `unsupported` label. A failed invented method,
an outdated verifier, an automation constraint or a login gate is not a blanket
product exclusion. Preserve failures and version changes instead of pooling.

## Execution and cost boundary

Start with local version/help/schema, synthetic protocol requests and installed
extension/runtime checks. Use no model inference for setup, direct controls or
protocol negotiation. Count any later natural-language turn separately, using
minimal synthetic context. Do not consume Claude allowance for this study.

Task-owned profiles and generated evidence live under
`projects/desktop-plugin-ui/artifacts/capability-study-20261025/`. Authored
probes and reports live in the matching project source directories. No global
credentials are copied or inspected. VS Code's own shared-storage initialization
is an observed profile-isolation caveat, not a claim of complete filesystem
isolation. Do not remove or inspect that external database.

The browser controller only exposes MCP Apps already expanded into side-panel
tabs; inline-only rendering is not controllable through it. A synthetic chart
request succeeded, and expansion was requested from the user for direct control
checks. Windows app automation restrictions are method constraints, not evidence
that the product lacks UI support. No sign-in or safety gate is bypassed.

## Verification closure

New corrected copies under `projects/desktop-plugin-ui/verification-20261025/`
address the prior local panel defects. Their acceptance is a fresh result;
historical evaluation workspaces and failed results remain immutable. Promote
only small reusable fixes into the owning skill, then validate the changed
standalone bundle and synchronize the local installation.
