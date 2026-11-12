# Cross-assistant UI skill independent review

Date: October 24, 2026, America/New_York. Review scope:
`skills/desktop-plugin-ui/`, its four assistant references, shared matrix,
existing Claude patterns, source checker, and compact empirical reports.
No new UI session or assistant inference was used for this review. Official
OpenAI reference pages were fetched read-only to verify the new ChatGPT claims.

## Assessment

No blocking factual overclaim was found in the reviewed assistant-specific
tables. The references distinguish native validation, real backend protocol,
synthetic iframe host, native terminal UI, VS Code extension webview, and actual
signed-in chat rendering. Failed invented methods are scoped to those methods.
Absent renderers, account gates, and declined forms are not presented as proof
that every frontend excludes the feature.

The practical coverage includes transcript/media output, MCP App iframes,
native Mod controls/render sites/Client regions, host elicitation, installation
settings, terminal forms, VS Code webviews, native canvases, and ChatGPT-specific
extension entrypoints. The matrix lists content, placement, control schema,
authority, browser features, state, lifecycle, deployment, budgets, and evidence
dimensions. It correctly rejects the idea that a model name identifies a UI.
No finite suite establishes all possible restrictions; this bounded framing
must remain in final user-facing claims.

## Findings and corrections

| Finding | Severity | Status and correction |
| --- | --- | --- |
| Copilot wording called all SDK APIs experimental. | Low | Fixed: now describes the CLI extension surface as experimental, without generalizing to every SDK method. |
| Actual Copilot extension loaded while returned capabilities included `extensions:false`. | Medium | Fixed: explicitly warns that this flag does not imply an empty extension inventory. Its exact semantics are not invented. |
| Existing native-pattern reference stated 34/34 while the new cohort stated 57/57 on the same date. | Low | Fixed: labels 34 as baseline and 57 as the expanded suite retaining those baseline cases; shared evidence register agrees. |
| New references exceeded 100 lines without contents sections, and initially had no direct main-skill routes. | Release gate | Contents added to Copilot/Claude references; main routes added by the integrating agent. Codex contents were added by its owner. |
| Source checker initially ignored Copilot/VS Code official domains, yielding zero checked URLs. | Medium | Fixed by integrating agent: exact primary hosts and GitHub owners now recognized. Rechecking the three assistant references inspected 14 official URLs with no findings. The checker still verifies exact URL catalog membership, not remote factual correctness. |
| Main skill description begins with imperative “Select, explain…” in the reviewed snapshot. | Release gate | Reported to integrating agent: use descriptive third person. This was the sole remaining `validate-skills.py` failure on the second run. |
| Shared matrix reports new Claude Desktop Chat paint, while older fixture rows still say Desktop paint/install untested. | Medium clarity | Reported to integrating agent: label the old cohort as historical and add a direct current live-host evidence pointer. Do not relabel individual carousel/fullscreen/device behavior as tested merely because one widget painted. |
| Claude matrix row names both MCP Apps and host elicitation. | Low clarity | Reported to integrating agent: keep native form/URL-elicitation acceptance separate from HTML controls inside the painted MCP App. The mechanism column alone must not imply both were exercised. |

## Numeric and contract checks

- Claude's 34 baseline plus 23 additional cases equals the reported 57 final
  engine tests. Byte/character/dimension limits distinguish reproduced exact
  boundary pairs from documentation-only limits. Missing Image file validation
  is correctly separated from actual decoding or paint.
- Codex's three final protocol cases report 18 assertions each, totaling 54
  assertions with zero model calls. The real CLI run reports one top-level turn,
  not one inference HTTP request. Its documented usage is 61,487 input tokens,
  45,312 cached input tokens, 331 output tokens, and 211 reasoning output tokens.
  The ambient-skill context inflation is disclosed.
- Copilot retains the existing CLI/ACP version mismatch (1.0.75/1.0.73) and
  independently installed task-local 1.0.103. Its actual terminal confirm,
  selection, input, and cancel results are distinct from bare-SDK callbacks.
  Five VS Code extension-host checks do not establish Copilot chat paint.
- The [Secure MCP Tunnel limits](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
  directly support the new values: 600 requests/minute, 10 MiB complete serialized
  envelope, 120 seconds, and 1,000 pending requests per tunnel. These are service
  defaults, not guaranteed throughput or generic component limits. Queue time
  is part of the deadline; pending means waiting for the client to fetch.
- The [ChatGPT plugin reference](https://developers.openai.com/plugins/reference)
  supports the three display-mode names, unique submission domain requirement,
  default sandbox origin, separate CSP fields, retained legacy redirect-domain
  field, and model/component visibility distinctions. These documented methods
  are not marked as empirical ChatGPT paint.
- The [extension contract](https://developers.openai.com/plugins/build/extensions)
  supports desktop-only composer mentions, the Free/Go web rollout caveat,
  thumbnail options, and multi-round-trip requests (MRTR) for OpenAI-registered
  MCP servers. Expanding MRTR on first use would improve runtime readability.

## Repository gates

All commands ran from the repository root. These outcomes belong to the
in-progress integration snapshot and do not replace a final post-edit run.

| Command | Result |
| --- | --- |
| `uv run --script scripts/validate-pattern-ids.py` | Passed: 1,348 canonical item IDs, maximum length 46, none above review threshold. |
| `uv run --script scripts/test-skill-independence.py` | Passed. |
| `uv run --script scripts/check-repo-payload.py` | Passed. |
| `uv run --script scripts/validate-skills.py` (initial) | Failed with six new integration findings: routes and contents for the three new assistant references. These were not unrelated preexisting failures. |
| `uv run --script scripts/validate-skills.py` (after routes/contents) | Failed with one new main-description voice finding; no other failures. |
| Source checker on Claude/Codex/Copilot references | Passed with 14 official URLs actually checked after domain support was added. |

The integrating agent owns final release validation, an isolated skill-only
forward run after all edits, synchronization, and final live-host status.

## Final reference review after integration

The frozen cross-v1 matrix and `claude-chat-live.md` were reread after the root
integration. Earlier pending clarity findings were corrected: the main
description uses third person; prior fixture evidence is labeled historical;
the real Claude Desktop Chat cohort is directly linked; and host-owned form/URL
painting remains explicitly untested despite negotiation and HTML App paint.
The live reference separates the readable immediate proxy parent from untested
top-application access, and cancelled consent from actual file/navigation
delivery. No new factual blocker was found. Cross-v2 additionally preserves
literal evidence labels in machine-readable output and narrows MRTR to
OpenAI-registered MCP servers. Final evaluation pass/fail results belong to the
separate frozen-version reports, including retained v1 formatting failures.
