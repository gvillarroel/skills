# Independent artifact review: final v3 naturalistic/generalization cohort

Reviewed on 2026-10-24 against the unchanged task prompts and each run's copied `desktop-plugin-ui` bundle. All six run manifests identify the same nine-file runtime, SHA-256 `93deff855cc7172a09e125235323e8fda95121b532d017e1cb14284764508149`.

This review covers submitted Markdown/JSON semantics, artifact identity, and exact source URLs. The root reviewer separately grades model identity, runtime isolation/integrity, tool errors, mandatory author-side source-audit execution, and strict harness gates. No submitted output or skill source was edited. This final v3 cohort is separate from the original and v2 cohorts; their outcomes are not pooled.

## Results

All six artifact pairs pass: naturalistic **3/3**, generalization **3/3**. This does not establish signed-in Claude Desktop/ChatGPT acceptance or a strict/joint result.

| Run suffix under `evaluations/runs/20261024-desktop-ui-v3-` | Result | JSON canonical patterns | Independent source audit | Specific finding |
| --- | --- | ---: | --- | --- |
| `naturalistic-luna-1` | Pass | 12 | 17 URLs, passed | Complete local Chat route with typed versioned edits, explicit explanation, error retention, optional fullscreen/export, and layered validation. |
| `naturalistic-luna-2` | Pass | 9 | 8 URLs, passed | Correct local service/server boundary, deliberate context/follow-up, useful text fallback, authoritative threshold writes, and realistic failure tests. |
| `naturalistic-luna-3` | Pass, wording note | 10 | 8 URLs, passed | Correct recommendation and bridge recipes; server explanation-operation wording could be clearer, as recorded below. |
| `generalization-luna-1` | Pass | 14 | 18 URLs, passed | Concrete Claude local/remote and ChatGPT HTTPS routes, full Claude origin derivation, native-runtime separation, and per-host tests. |
| `generalization-luna-2` | Pass | 7 | 26 URLs, passed | Useful deployment matrix, stable IDs/versions, authoritative priority mutation/export, preserved state, exact-origin sensitivity, and separate native adapter. |
| `generalization-luna-3` | Pass | 12 | 25 URLs, passed | Correct shared-versus-host-specific contracts, reachable remote ChatGPT route, local Claude domain omission, optional capability denial, and native transport unknowns. |

All six JSON files parse, contain the requested fields, use existing canonical pattern IDs, and explicitly set `host_acceptance_verified` to `false`. Every report identifies the 2026-10-24 source snapshot and includes primary-source links.

## Source audit

The copied v3 `scripts/check_sources.py` was independently run against both generated artifacts in each workspace with `--fail-on-findings`. All six commands returned `passed: true`, no findings, and the URL counts shown above: **102 checked official URLs across the twelve files**. Counts deduplicate URLs within each individual output file; the same source in another file is counted again.

The command shape was:

```powershell
uv run --script evaluations/runs/<run-id>/workspace/skills/desktop-plugin-ui/scripts/check_sources.py <generated-markdown> <generated-json> --fail-on-findings
```

For naturalistic cases, the artifact arguments were the exact `workspace/proposal/ui.md` and `workspace/proposal/decision.json` paths. For generalization cases, they were `workspace/handoff/cross-host.md` and `workspace/handoff/matrix.json`.

A separate complete HTTP(S)-URL comparison against each corresponding copied bundle also found **zero unmatched URLs**, including domain/path/anchor differences. This independently checks the auditor's observed acceptance rather than relying only on the recommendations' statement that links were copied. No extra allowlist or `--allow-url` override was used. These checks validate citation identity, not the factual truth of every prose claim or current web availability.

## Semantic assessment

All naturalistic outputs recommend an ordinary Claude Desktop Chat MCP App backed by a local stdio server that calls the workstation service. They distinguish MCPB installation/settings from the runtime HTML View, keep the browser away from the stdio stream and privileged local service work, and avoid substituting a native Mod or arbitrary host panel for Chat.

The recommendations include a concrete tool/resource/metadata/MIME contract, useful text plus structured data, stable stock IDs and freshness markers, and relevant canonical patterns. They keep threshold drafts separate from committed values, validate locally and again on the authoritative server, send record versions, reject stale/unauthorized requests, and render returned server state. Refresh failures keep prior rows, compatible selection/drafts, stale markers, and retry rather than silently becoming zero stock. Async ordering and duplicate submission receive explicit tests.

The naturalistic outputs correctly separate selection context from an intentional model follow-up. The detailed recipes use `updateModelContext` for concise facts and `sendMessage` for the explicit explanation action; filtering/selection does not start an unsolicited turn. CSV exports remain server-authorized and capability-dependent, preserve usable fallbacks, and require actual byte/name checks before an OS-save claim. Fullscreen remains negotiated with useful inline behavior after denial.

All generalization outputs share ticket schemas, stable IDs, server validation, state/error semantics, useful text, and portable HTML/bridge behavior while separating deployment, origins/CSP, account consent, optional APIs, and native UI. Claude local stdio omits remote `ui.domain`; remote setup depends on the exact full configured URL, including slash choice. The first output spells out the hash arithmetic; the other two retain exact-origin requirements and cite the bundled diagnosis rather than supplying a conflicting formula.

ChatGPT is assigned a separately verified reachable HTTPS/remote route rather than assumed access to the workstation's stdio process. ChatGPT-only `window.openai` APIs and sandbox domains stay in a host adapter. The possible Code pane remains a separate native Mod tree/runtime, with its own package/service connection, surface handling, native tests, and real placement/focus checks. No output promotes Chat resource support into native-pane or arbitrary-sidebar support.

All six distinguish documented behavior, scoped SDK/browser/native-engine observations, conditional host features, and genuine untested outcomes. Their validation plans include protocol/resource/initialization, normal and negative server calls, stale writes, retained data, optional capability denial, narrow/theme/keyboard behavior, real host discovery/consent/paint, and eventual actual export delivery. Generalization cases also separate origin/auth/deployment and host-specific adapter tests.

## Defects and nonblocking notes

- **Naturalistic 3 explanation-operation wording:** The introduction says model explanation goes through server tools and suggests an `explain_stock_item` operation. Its later `claude-ui-context-followup` recipe correctly initiates the intentional turn with `sendMessage`. The implementation should use the server operation for authoritative item retrieval/validation and the explicit bridge request for model follow-up. This is a wording ambiguity rather than a material failure because the operative method and no-unsolicited-turn rule are correct.
- A fully unavailable server cannot originate its own MCP fallback result. References to startup failure must lead to host/chat diagnostics; text fallback applies when a tool operation can return. This normal availability boundary does not invalidate the chosen routes.
- No material routing, mutation-authority, data-loss, capability-denial, cross-host-origin, citation-identity, or evidence-overclaim defect was found.

The ticket-queue prompt does not require a model-analysis feature. Optional context/follow-up treatment is acceptable when it does not claim that context updates create replies. No hidden keyword, optional pattern-count minimum, exact operation name, or unrequested JSON representation constraint was imposed. No generated output was repaired for this review.

## Artifact identity

Each run is under `evaluations/runs/<run-id>/workspace/`. Naturalistic outputs are `proposal/ui.md` and `proposal/decision.json`; generalization outputs are `handoff/cross-host.md` and `handoff/matrix.json`.

| Run suffix | Markdown SHA-256 | JSON SHA-256 |
| --- | --- | --- |
| `naturalistic-luna-1` | `770196afd86469e10cea96a8334350aff9c2de3f951dc5d52bfedc041b44c5dc` | `cb2e7ebfed5664ab19a7485a7a1848f18a04aa769a6bf31c2ca07b5d628f1b3a` |
| `naturalistic-luna-2` | `1b73c5c8c966abf12ea05efb00fcd1a0c2dc6c97757f0ec0994cb76d67e92518` | `af10193e5c8de4f88bf3eead969874c80f337daa6b67792cb63e5333c40d2c97` |
| `naturalistic-luna-3` | `414e09b4c1d64b7346e78fc5eb8b69c36cc59ca8c90715d3810555a57c49a372` | `54f9b5fa4b84e6d99a8db113417e1cd9adbb4834420255291130c724d2a631a6` |
| `generalization-luna-1` | `029493dc53ba5fd5e3e0c7979dd33e592b7cfc51ad3d9a34f25a0bc07e9b0ee5` | `58546ea7d0ac684e5c640cf17cdc97beb907532ec14b95da52d9f4f2521854df` |
| `generalization-luna-2` | `196b597af5d7f1f8bcc9667fdaacce03729cf9224b12aa302657162eccf6c4dd` | `84d28fd74b930da40d8cc9014dfd810ceb9b09dd6c8ea5593f33ddfc222bd790` |
| `generalization-luna-3` | `448b8025fd0ec5b3763ea34676e6ea2aa88061f6b0fcda68be6bfbe79688b822` | `b40fde6f5d4a20eb932e4b41b23ae383ec469181097e1cf863049538050cb72e` |
