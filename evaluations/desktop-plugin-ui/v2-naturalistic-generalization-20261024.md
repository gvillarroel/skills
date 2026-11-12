# Independent artifact review: v2 naturalistic/generalization cohort

Reviewed on 2026-10-24 against the task prompts and each run's copied `desktop-plugin-ui` bundle. The subject is the eight-file runtime with SHA-256 `e6595579f0c0ab026a9fa1e60e65578926d583d11f306d2693dd14b69f7e1518`, as recorded in the run manifest. This report grades submitted Markdown/JSON semantics and exact source URLs; the root reviewer separately grades strict trace, model, isolation, integrity, and tool-error gates. No submitted artifact was edited.

This is a fresh v2 cohort. The original six reviews remain in `naturalistic-generalization-20261024.md`; their results are not pooled with this subject.

## Results

All six artifact pairs pass: naturalistic **3/3**, generalization **3/3**. Every JSON file parses, contains its requested fields, uses existing canonical pattern IDs, and sets `host_acceptance_verified` to `false`. This is an artifact result, not a claim of signed-in host acceptance or a strict/joint result.

| Run suffix under `evaluations/runs/20261024-desktop-ui-v2-` | Result | JSON pattern IDs | Complete primary URLs in Markdown | Semantic finding |
| --- | --- | ---: | ---: | --- |
| `naturalistic-luna-1` | Pass | 9 | 9, all verbatim | Correct workstation-local Chat App route, server-authoritative edits, deliberate explanation action, retained stale rows, and concrete layered tests. |
| `naturalistic-luna-2` | Pass | 8 | 8, all verbatim | Correct local route and detailed typed tools; explicit stale-version/double-submit handling, capability-denied CSV/fullscreen fallbacks, and no unverified host claims. |
| `naturalistic-luna-3` | Pass | 7 | 7, all verbatim | Implements the complete stock flow with useful non-UI results, valid edit/version contract, refresh retention, explicit-only follow-up, and genuine host unknowns. |
| `generalization-luna-1` | Pass | 12 | 16, all verbatim | Shares portable View/backend semantics while separating Claude local/remote, ChatGPT deployment/extensions, and future native Code pane. |
| `generalization-luna-2` | Pass | 13 | 13, all verbatim | Concrete reachable ChatGPT HTTPS route, exact Claude URL/domain derivation, local domain omission, native adapter boundary, and per-host failure/validation plan. |
| `generalization-luna-3` | Pass | 12 | 14, all verbatim | Explicit local/remote Claude matrix, ChatGPT HTTPS baseline, native runtime/service-connection unknowns, authoritative priority writes, and useful export/text fallbacks. |

No primary-source URL appears in these JSON files. Every HTTP(S) URL generated in the Markdown was compared against the corresponding copied bundle's complete URL set, including domain, path, and anchor. **No unmatched or rewritten primary-source URL was found.** The source snapshot date is explicit in every recommendation.

## Semantic review

The naturalistic recommendations select ordinary Claude Desktop Chat with a local stdio MCP server and sandboxed MCP Apps HTML resource. They keep the workstation service behind the server and distinguish the tool transport from the View bridge. MCPB is correctly treated as optional packaging/settings. They do not substitute a native Mod, arbitrary sidebar, artifact, browser-only dashboard, or unreachable cloud connector for the required Chat/local-service route.

All three recommendations describe relevant canonical patterns as implementation decisions, including matching `ui://` metadata/resource/MIME, handler ordering, useful text/structured fallback, typed server calls, validated threshold forms, async recovery, file export, and optional fullscreen. They separate server-owned committed state from View drafts, send stable item IDs plus concurrency versions, require server-side validation/authorization, and render authoritative responses. Refresh failures keep prior rows and compatible selection/drafts, mark data stale, and expose retry. Newer-response ordering and denied/missing optional capabilities are addressed.

All three correctly distinguish `updateModelContext` from `sendMessage`: selection/filtering does not start a model turn, and the intentional explanation action requests the follow-up. Export does not claim that an anchor, resource generation, or fixture acknowledgement saved bytes. CSV names/MIME/authorization and actual downloaded bytes are included in the test plans. Fullscreen denial leaves inline behavior useful.

The generalization recommendations separate shared ticket schemas, validation, state/error rules, text fallback, and portable View behavior from deployment, origins/CSP, consent, and host-specific extensions. Claude local stdio omits remote `ui.domain`; remote configuration is exact-URL-sensitive and must be reachable to the actual remote host infrastructure. ChatGPT uses a separately tested reachable HTTPS deployment rather than assuming it consumes the workstation's stdio process. `window.openai` and domain rules remain in a ChatGPT adapter. Native Claude Code/Code-tab panes remain a separate tree/runtime with their own connection and installed-placement checks.

The first two generalization recommendations spell out the Claude hash derivation. The third states exact full-URL and trailing-slash sensitivity and points to bundled troubleshooting documentation rather than repeating the arithmetic. This is sufficient for the requested origin/deployment recommendation; no incorrect formula or cross-host metadata is supplied.

Every output distinguishes documented behavior, scoped SDK/browser/native-engine evidence, conditional capabilities, and untested signed-in host outcomes. Practical tests cover tool/resource discovery, MIME/initialization, normal and negative server calls, stale writes, pending/error retention, narrow/theme/focus behavior, denied fullscreen/download, real host consent/paint, and actual export delivery. Cross-host outputs additionally require separate deployment/origin/auth and optional native Mod validation. None elevates a browser or native-engine result to installed Desktop/ChatGPT acceptance.

## Defects and limits

No material semantic, routing, server-authority, error-retention, capability, citation, or evidence-overclaim defect was found. The v2 recommendations include direct primary links, so the original naturalistic-3 traceability gap is absent from this cohort.

The queue task does not request a model-analysis feature. A generalization recommendation may leave context/follow-up as an optional design consideration rather than adding an unsolicited action. No hidden keyword, exact tool name, optional pattern count, or JSON string-versus-object convention was imposed beyond the task's explicit requirements.

These artifacts remain design recommendations. They do not implement a warehouse/ticket application, install a connector, validate account policy, or exercise an installed host. A fully unavailable server cannot itself originate an MCP fallback result; useful text fallback applies when an operation can return, while startup failure needs host/chat diagnostics. This normal availability boundary does not invalidate the proposed route.

## Artifact identity

Each run is under `evaluations/runs/<run-id>/workspace/`. Naturalistic outputs are `proposal/ui.md` and `proposal/decision.json`; generalization outputs are `handoff/cross-host.md` and `handoff/matrix.json`.

| Run suffix | Markdown SHA-256 | JSON SHA-256 |
| --- | --- | --- |
| `naturalistic-luna-1` | `b958d12681ff52fba2b87ea69f8f52b87c4fc3b1a7b552c45ade8b3f9590f1a6` | `dc52abfeb8e7203dd5bba2822618cfed87c2e47211723213bb3071b32f030666` |
| `naturalistic-luna-2` | `cd8784ce89d1539c1aa06963c7b1ace675846a48b3e6f76e4b2f3ef08862f4ef` | `2942a9d5d8476d4da9711c893e88a8ef477ef9c78b707fcdb9bd45b1ec0b8c52` |
| `naturalistic-luna-3` | `a1beddd1c0ec4f48a0b8f14f69c6c463c93c8fca0702502b6d5b07f052557097` | `a7cd23f9c4ef225f470c66e181862c8b4c3d42ad8f65e5ea4bc3f8a06b51b313` |
| `generalization-luna-1` | `1959c4c380bdc0013be69b4dd46eefacfc3f43755adb176e0e2ea734d9ed3fcb` | `12e3cd4a7ac28a2f585a726aa4913e0510210f0a333bb74dd2fce2ca1dd3af2b` |
| `generalization-luna-2` | `99f1ce252c6cef5ff74d4739a32d95916096ab66805413a4a94b0c84ae2b251a` | `46d130661e0943a1797bca0296ec034b15a99a507f72d886e2230e4bc3b3350f` |
| `generalization-luna-3` | `14cee392b160fa0589ac06b0823317c9cbb8e09ed3622101224fc5fa70a96d9d` | `f86a53a6664e991e3c0f772a24707e5529192486d87315fa86f01812e65eb250` |
