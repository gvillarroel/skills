# Claude Code native UI limits

## Contents

[Surfaces](#supported-surface-contract), [rejections](#reproduced-rejection-and-fallback-rules),
[budgets](#documented-budgets-to-check-before-implementation),
[host verification](#verify-the-actual-host-without-spending-model-tokens).

Snapshot: 2026-10-24 local date. Installed Windows Claude Code **2.1.302**;
strict plugin validation passed; **57/57** native engine tests passed. These
tests execute the installed executable's hooks, native tree validator, Client
modules, and simulated interactions. They spend **zero model calls** and do
not prove terminal paint, Claude Desktop paint, clipboard effects, process
launching, or a file decoder's eventual output.

Read this with [native-patterns.md](native-patterns.md). Ordinary Claude
Desktop **Chat** uses the MCP Apps contract in
[chat-patterns.md](chat-patterns.md), not these native elements. Native Mods
apply to Claude Code, the Desktop Code tab, and the Claude Code VS Code
extension within their individual support matrices. Do not apply this matrix
to Codex, ChatGPT, GitHub Copilot, Cowork, mobile, or headless output.

## Supported surface contract

| Element or method | Terminal | Desktop Code | Claude Code VS Code | Evidence and rule |
| --- | --- | --- | --- | --- |
| Box, Text, Button, Input, Select, Link, Code, Markdown | Accepted | Accepted | Accepted | `observed-working`, native engine. Acceptance does not prove every style or keyboard prop paints identically. |
| Svg | Refused | Accepted | Accepted | `observed-working` / `observed-failed`, native engine. Provide text or an artifact route for terminal users. |
| Image and Raster | Accepted | Refused | Refused | `observed-working` / `observed-failed`, native engine. Branch on `e.surface`; constructor-table names are not a capability probe. |
| Client native region | Accepted | Accepted | Refused | `observed-working` / `observed-failed`, native engine. A Client draws native elements, with its own input/frame clock, not browser DOM. |
| div, canvas, iframe, script, webview, lowercase svg | Refused | Raw iframe refused | Untested raw HTML cases | `observed-failed`, native engine. Never substitute HTML tags for allowlisted native primitives. |
| React DOM `style` object on Box | Untested | Refused | Untested | `observed-failed`, native engine. Use the documented native props; arbitrary CSS is not part of the contract. |
| Hooks access to window/document/Node process or `require('node:fs')` | Absent / refused | Same isolated hooks runtime | Same isolated hooks runtime | `observed-failed`, engine environment. Use the mods API for host filesystem/process/network boundaries. |
| `.mcpb` settings form or MCP App iframe | Separate mechanism | Separate Chat surface | Separate mechanism | Native test results do not establish MCP App installation or rendering support. |

The [official element matrix](https://code.claude.com/docs/en/plugins/mods/reference#elements)
also documents these presentation differences; they were **not painted** in
this engine cohort:

- Terminal has one monospaced text size. `size`, `mono`, and `tabular` cannot
  change that; semibold/bold weight draws bold.
- VS Code ignores Box positioning/offsets, alignSelf, borderDimColor, and
  hover; Text size/mono/tabular/hover; Button hotkey/plain/autoFocus/action/
  hover; Input/Select autoFocus; Svg isInteractive; and Code language/path/
  startLine/format/wrap. An accepted diff block can therefore show raw diff
  text without coloring or line numbers.
- Native interactive SVG supports scriptless hover/CSS/SMIL, not arbitrary
  JavaScript or event-handler scripts. VS Code ignores its interactive flag.
- An Image's actual decoding and display depend on the terminal, protocol,
  local file availability, and OS. A path-based Image with a deliberately
  nonexistent filename **passed native validation** in this cohort. Never
  report that result as a successfully displayed image.

## Reproduced rejection and fallback rules

| Boundary | Observed result in 2.1.302 | Implementation rule |
| --- | --- | --- |
| Link href length | 2,048 characters accepted; 2,049 refused the drawing | Bound the complete literal URL, including its scheme and query. |
| Link destination | Desktop `file:`, `javascript:`, remote `http:` downgraded to Text; HTTPS and localhost HTTP remained Links | Keep a copy-path or supported action fallback. A mounted Link was not opened in these tests. |
| SVG source length | 131,072 characters accepted; 131,073 refused the drawing | Simplify or export oversized graphics. `alt` remains required. |
| Native leaf children | Even an empty children array on raw Svg refused | Omit children entirely on leaf elements. |
| Control autofocus | `autoFocus: false` skipped the hook and exposed its fallback | Supply only `true` when enabled; omit when disabled. |
| Select options | Duplicate values refused; value length 10,000 accepted and 10,001 refused | Make values unique and short, and keep labels separate. |
| Image payload | Missing alt, invalid PNG header, mismatched RGBA byte count, fractional generation, and 256 columns refused | Validate source bytes and whole-number dimensions/counters before returning the tree. |
| Raster payload | One valid cell accepted; wrong byte count, 513 columns, or 257 rows refused | Encode exactly columns × rows × 12 bytes as padded base64; enforce dimensions. |
| Missing host effect implementation | Copy/process/toast/status/log were tested through explicit stubs | A dispatch pass proves the payload boundary; check actual host effects separately. |
| Unplaced pane | Stubbed `isPlaced: false` reached the transcript fallback | Preserve a usable transcript path when placement fails. |

Native region tests also reproduced local button state, draft/submit
separation, selection, invalidation, Client keyboard/pointer coordinates,
timer ticks, validated posts, and resize. These actions do not require a model
turn. The test kit's controlled clock is not a real display frame rate.

## Documented budgets to check before implementation

These limits come from the current
[Mods reference](https://code.claude.com/docs/en/plugins/mods/reference#limits)
and [public declarations](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts).
Except where reproduced above, label them `documented`, not empirically
verified in this cohort. Prefer declarations generated by the installed build.

| Limit | Contract |
| --- | --- |
| Hook execution | 10 seconds of its own execution; prompt.edit 50 ms; catch handler 1 second. API/next wait time is generally excluded, except clock.sleep. |
| Text in one tree | First 100,000 characters drawn. |
| Image dimensions and bytes | columns/rows 1–255; inline PNG/RGBA at most 2 MiB decoded; RGBA dimensions 1–2048. File/shm raw dimensions 1–4096; path at most 3,072 bytes. POSIX shm is platform dependent. |
| Raster | columns 1–512, rows 1–256; printable width-one BMP cell glyphs; 1,024 simultaneous color pairs before nearest-color mapping. |
| Code language/path, Select value, Client module | At most 10,000 characters each. |
| Redraw invalidation | 10/s, or 30/s for terminal visible pane, expanded band, and prompt hint; faster calls coalesce. |
| Automatic pane placement | Width threshold 144 terminal columns, 110 after the user has opened it once. Explicit request and actual placement are separate. |
| Identifiers | Command/tool/subagent/pane names use letters, digits, underscore, hyphen; at most 64 characters. |
| Host API payloads | fs read/write 4 MiB/file; store 4 MiB JSON total; http request 4 MiB characters, response 4 MiB bytes, 30 seconds, five redirects. Oversized Content-Length rejects except the documented HEAD exemption. |
| Process and feedback | process.run defaults 30 seconds, maximum 10 minutes; toast defaults four seconds. |
| Native host authority | Permission dialog remains host owned; add context through notice rather than overriding authorization UI. |

## Verify the actual host without spending model tokens

1. Run `claude --version`, `claude plugin validate <dir> --strict --json`,
   and `claude plugin test <dir>`. Keep raw failures as well as final passes.
   Test hook-floor registrations must precede the first `$` call. A schema
   rejection at mount is not necessarily a constructor exception that a floor
   fallback can recover from.
2. Inspect sanitized `claude auth status`: retain logged-in boolean, method,
   and subscription type only. Desktop and CLI authentication are separate;
   one being signed in does not establish the other.
3. If requested and signed out, start `claude auth login --claudeai`; let the
   person finish the OAuth browser/account challenge. Do not expose login
   URLs with state, codes, account identifiers, or credential files. Login,
   help, validation, and native tests are not model inference.
4. For real paint, load a trusted local Mod in an interactive authenticated
   session, open its registered local command, and inspect keyboard, focus,
   narrow layout, and image behavior. Do not send a prompt just to activate a
   local control. Obtain build-specific declarations as documented in
   [creating Mods](https://code.claude.com/docs/en/plugins/mods/create#get-type-definitions-for-your-version).
5. Treat `--print` and JSON/stream-json output as a separate noninteractive
   output route. CLI help confirms these formats; the native test kit does not
   demonstrate an interactive painter in those streams.

No account or model call is needed for the first step. A login challenge or
missing plan is an account gate, not evidence that native primitives fail.
