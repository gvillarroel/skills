# Independent content review

Reviewed on 2026-10-24. Scope: `skills/claude-desktop-plugin-ui/SKILL.md`, `references/chat-patterns.md`, `references/bridge-patterns.md`, and `references/distribution.md`. The native and evidence references were not yet present during this review. No skill files were edited, and no signed-in host was exercised.

## Result

No blocking factual error found in the ordinary Chat, packaging, transport, download, or model-context guidance. The skill correctly separates documented contracts, local fixtures, and actual Desktop behavior. Two source-backed additions would make its failure guidance materially more complete.

### P2: External-link fallback omits Claude's concrete confirmation contract

**Location:** `references/chat-patterns.md:103-104` and `references/bridge-patterns.md:17`.

The fallback names `openLink` but does not explain what Claude will show. Current official documentation says custom/local connectors always display an external-link confirmation modal. Directory connectors can bypass it only for declared destinations after real user activation. A successful bypass response establishes an attempted open, not arrival at the destination. These details matter when choosing a file/export fallback and diagnosing an apparent failed click.

**Suggested change:** Add a small external-link rule, either to the existing export pattern or as a separate pattern: initiate on a clear user action, identify the destination, handle cancellation, and avoid claiming actual navigation from an acknowledgement. Distinguish the directory listing's allowed-link destinations from resource CSP allowlists. [Official external-link guide](https://claude.com/docs/connectors/building/mcp-apps/external-links).

### P2: Missing-UI diagnosis omits a documented large-result failure

**Location:** `SKILL.md`, investigation step 4, and `references/chat-patterns.md`, chart/file data contracts.

Claude's troubleshooting page documents a specific hydration failure when an initial tool result exceeds roughly 150,000 characters while its code execution sandbox is active: the result is replaced by a sandbox-file pointer rather than the widget data. This is distinct from a URI, MIME, connection, or zero-height failure.

**Suggested change:** Add payload size/result shape to the diagnostic sequence. Recommend lean initial results, pagination, and app-initiated detail fetching. State the threshold as approximate and scoped to claude.ai/Desktop with the documented condition; do not present it as an MCP or SDK limit. [Official troubleshooting](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting).

## Confirmed semantics and boundaries

- `downloadFile` remains correctly marked conditional and host-mediated. The current skill does not claim direct iframe download, OS delivery from a fixture acknowledgement, or universal PDF preview. No change needed to the present wording. [App API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#downloadFile).
- The context rule correctly distinguishes replacing current View context from requesting a follow-up message. The acceptance record is explicitly limited to method shapes, with real next-turn/model delivery still untested. No semantic correction needed. [App API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#updateModelContext).
- Local stdio Chat configuration is directly documented. The distinction from plugin-supplied local servers and remote cloud-origin connectors is correct. The local route is not being falsely generalized to Cowork or web. [Claude setup](https://claude.com/docs/connectors/building/mcp-apps/getting-started), [plugin behavior](https://support.claude.com/en/articles/13837440-use-plugins-in-claude), [remote networking](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).
- The card/carousel numerical rules, fullscreen composer, optional PiP, mobile camera/microphone/location exclusion, and Claude restriction of nested iframe origins agree with the current design guide. Calling the numerical rules design guidance rather than schema validation is appropriate. [Design guide](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines).

## Pattern completeness

A read-only parser found **17 unique complete patterns** across the three reviewed references: ten Chat patterns, six bridge patterns, and one extension-settings pattern. Every pattern has `Trigger/input`, `Rule`, `Failure/fallback`, `Validate`, and `Evidence`. The requested minimum of ten is satisfied independently of the still-pending native reference.

The ten Chat IDs are `claude-ui-text-fallback`, `claude-ui-inline-card`, `claude-ui-option-carousel`, `claude-ui-fullscreen-workspace`, `claude-ui-validated-form`, `claude-ui-chart-canvas`, `claude-ui-file-review-export`, `claude-ui-responsive-theme`, `claude-ui-progressive-details`, and `claude-ui-async-state`.

## Review limits

I checked public contracts and scope accuracy, not the implementation or retained output of the other agent's SDK/browser probes. Probe-specific observed claims still need the final evidence reference and artifact manifest. The links from `SKILL.md` to pending references should be rechecked after all authors finish. Current desktop compatibility remains untested until an actual host run is available; that qualification is already explicit.
