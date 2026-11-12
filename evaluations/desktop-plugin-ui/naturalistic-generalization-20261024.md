# Independent artifact review: original naturalistic/generalization cohort

Reviewed on 2026-10-24 against the original task prompts and each run's copied `desktop-plugin-ui` skill. This is a semantic review of the submitted Markdown and JSON; it does not grade model identity, trace isolation, tool errors, runtime integrity, or other strict harness gates. The root reviewer handles those separately. No submitted artifact was edited.

The reported frozen runtime is seven files, SHA-256 `8ae7ae5066ab3eee6913ecbb57f137204f15aba527d7eafc4f0e2b82e65c4808`. This review remains attached to the original runs and is not pooled with the later v2 subject.

## Results

All six outputs pass the meaningful artifact requirements: naturalistic **3/3**, generalization **3/3**. This conclusion does not imply a strict/joint pass or actual application acceptance.

| Run suffix under `evaluations/runs/20261024-desktop-ui-` | Artifact result | Patterns in JSON | Primary URL check | Findings |
| --- | --- | ---: | --- | --- |
| `naturalistic-luna-1` | Pass | 9 | 7 Markdown URLs match copied bundle | Correct local Chat route, complete stock/error/edit/export/explanation design, practical layered tests. |
| `naturalistic-luna-2` | Pass | 9 | 8 Markdown URLs match copied bundle | Same essential behavior; exact record versions, initial-load error state, and explicit follow-up are clear. Minor bridge wording note below. |
| `naturalistic-luna-3` | Pass, traceability gap | 11 | No primary URLs supplied | Substantive recommendation and evidence boundaries are correct. Direct source links are missing; recorded below. |
| `generalization-luna-1` | Pass | 7 | 12 Markdown URLs match copied bundle | Separates portable View, local Claude, remote Claude origin, ChatGPT deployment/adapters, and optional native Mod. |
| `generalization-luna-2` | Pass | 16 | 17 Markdown and 8 JSON URLs match copied bundle | Detailed cross-host matrix, useful optional/native patterns, authoritative state and explicit evidence limits. |
| `generalization-luna-3` | Pass | 14 | 15 Markdown URLs match copied bundle | Concrete ChatGPT HTTPS route, exact Claude URL hashing, local omission, and appropriately unverified native transport reuse. |

URL checks compare the complete generated URL, including domain/path/anchor, with URLs in the corresponding copied bundle. No unmatched generated primary URL was found. Counts are per output file and do not represent distinct sources across files.

## Applied criteria and evidence

Every naturalistic output recommends a local stdio MCP server with an MCP App in ordinary Claude Desktop Chat, keeping the workstation service behind the server. Each separates MCPB installation/configuration from the runtime View and avoids substituting the Code Mod runtime for Chat. Tool/resource metadata, UI MIME, startup ordering, useful text/structured fallback, stable stock IDs, and relevant canonical patterns are concrete enough to implement.

Every naturalistic output preserves a last-successful table on refresh failure, marks stale/error state, offers retry, and preserves drafts after rejection. Threshold updates use server-side schema/authorization plus record version checks and render the authoritative response. Export handles capability absence/denial and distinguishes generated resources or bridge acknowledgement from actual saved CSV bytes. Fullscreen negotiation preserves useful inline behavior. Selection context and explicit explanation are correctly separated: context updates do not themselves start a model turn, and only the deliberate explanation action sends a follow-up.

Every generalization output distinguishes the portable MCP Apps View and backend contracts from host-specific deployment, origin/CSP, optional APIs, and the native Mod tree. Claude local stdio omits remote `ui.domain`; the remote hash depends on the exact configured URL, including a trailing slash. ChatGPT uses a separately verified reachable remote route and isolates `window.openai`/domain behavior. The optional Code pane is a separate native runtime. No output claims that an ordinary Chat pass verifies Code placement, or that a local server is automatically remotely reachable.

All six JSON documents are valid, contain their requested fields, use existing canonical pattern IDs, and explicitly set `host_acceptance_verified` to `false`. All six distinguish documented/scoped fixture evidence from installed host behavior and retain genuine unknowns. Their test plans cover protocol/resource/handshake, negative server calls and stale edits, state retention, optional capability denial, browser/painter behavior, and eventual authorized host acceptance. Generalization outputs additionally separate per-host deployments and origin checks.

The generalization task did not request selected-ticket model analysis. Its third output does not add a follow-up feature; this is not a failure. It does not claim that selection starts a model turn and correctly warns that model context is not a durable state store.

## Defects and nonblocking notes

- **Naturalistic 3 source traceability:** The output identifies the 2026-10-24 snapshot and describes SDK/fixture layers accurately, but supplies no direct primary-source links. The skill asks for links, so this is a real traceability gap. The naturalistic task prompt does not explicitly require citations; it is retained as a nonblocking artifact-quality issue rather than a hidden content gate. Its functional recommendation remains a pass.
- **Naturalistic 2 bridge wording:** JSON labels the iframe bridge as `postMessage`, whereas the bundle also permits SDK-selected host transports. The implementation body uses `App.connect()` rather than forcing a transport, so the chosen route is implementable. Prefer “MCP Apps bridge selected by the SDK” in future recommendations.
- No material host-routing, mutation-authority, data-loss, optional-capability, cross-host-domain, or evidence-overclaim defect was found.

## Artifact identity

Each run is under `evaluations/runs/<run-id>/workspace/`; naturalistic outputs are `proposal/ui.md` and `proposal/decision.json`, and generalization outputs are `handoff/cross-host.md` and `handoff/matrix.json`.

| Run suffix | Markdown SHA-256 | JSON SHA-256 |
| --- | --- | --- |
| `naturalistic-luna-1` | `cbccb501700144d5f27af6cfe6c98295258fc72bda16eb57f6e2e62795492380` | `84432fd1ee267db503bc0dded7b9519f0145403157e2833ad72b477161739697` |
| `naturalistic-luna-2` | `10b97456cfc198f64dfcba8183ca97e2cb9bb84a088148765a94abdef87ce12f` | `7f6d16ab8fd236e200903a284b9a1e3261b4b007862e24b01de229fb371b2545` |
| `naturalistic-luna-3` | `a4573448dc0baae2ea9411c473ca10bc48d8b378d5dc0346198b177044f6e531` | `0629cd2db6cbb8c1340231c6b35f6ce08bcc30a3ed4ebd7555c2723e7412ab39` |
| `generalization-luna-1` | `31f537e352e322a58c5d56af61ed93c7060c385dae0056a618ce40557c9fa3dd` | `6885bffee9982240641227eba493b4958b161e4efd5e0a561ad4dad909c76841` |
| `generalization-luna-2` | `5a1acecef66697dba0179b0ba58a8af3092fdcfe6abfab6ca8ec3922c28029de` | `c85b57feae4001d1ed7ed2e1ee9e392c56be1376d9e03e904e4877f85aa42e8b` |
| `generalization-luna-3` | `bacf96b317c2eca62e2e42d7281e823254dfeba3d8f52793f4dabecf99140dbd` | `c1117d5d2aaca97842c912097f388557f8fc233ec120d55d41b55ddf28233aaf` |
