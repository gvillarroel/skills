# Claude terminal and native UI empirical findings

Date: 2026-10-24 local / 2026-10-25 UTC. Installed PATH executable:
Claude Code 2.1.302, Windows 11 build 26200, SHA-256
`3AB075F78998EFEF8B87F491C2E4A39C309DDDF44E51D0103EBA4F3713D2A0AE`.

The account-free native engine suite passes **57/57 tests** across two files,
and strict plugin validation exits zero. No model calls were made. Original
34-test fixture was copied without changing prior evidence; this workspace
adds 23 focused cross-surface and exact-boundary cases.

## Reproduce

From the repository root:

```powershell
claude --version
claude plugin validate projects/desktop-plugin-ui/cross-assistant/claude/native-probe --strict --json
claude plugin test projects/desktop-plugin-ui/cross-assistant/claude/native-probe
```

Commands use the installed Windows executable, not a substitute JS schema.
The engine runs the hook/Client modules, validates returned native trees,
and dispatches simulated keyboard/pointer/timer/resize events. Process,
clipboard, placement, and feedback host APIs use explicit test stubs.

## New observed findings

- A correctly encoded one-cell Raster validates on terminal. Raster and Image
  refuse desktop and vscode; raw Client refuses vscode.
- div, canvas, iframe, script, webview, and lowercase svg are refused as native
  terminal element names. Desktop Box refuses an arbitrary DOM style object.
- Image refuses missing alt text, mismatched RGBA byte count, and columns 256.
  Raster refuses invalid cell byte count, columns 513, and rows 257.
- Exactly 2,048 href characters and 131,072 SVG source characters pass; one
  additional character refuses the drawing. Select value length 10,000 passes;
  10,001 refuses. Existing duplicate-value/autofocus-negative cases still pass.
- A deliberately nonexistent image filename **passes native tree validation**.
  Actual file loading, decoding, and paint happen beyond this tested layer.
- Original state/input/Client cases continue to pass, with no model turn.

## Account and login attempt

Initial and post-test sanitized `claude auth status` report `loggedIn: false`,
`authMethod: none`, and no subscription type. The user explicitly requested
opening the Claude account in terminal. Started official
`claude auth login --claudeai`; it opens browser OAuth and offers a paste-code
fallback. At this report the login was still pending browser completion.
This attempts subscription login rather than Console API billing. Do not infer
CLI access from a signed-in Claude Desktop session.

Login stdout/stderr remain in ignored private artifact logs. They are not
tracked or suitable for displaying in a report because they can include OAuth
state/URLs. No codes, identities, tokens, or credential file content were
printed. No credential/configuration reset, global plugin install, or model
request was performed.

## Retained evidence and failed attempts

All bulky evidence lives in
`projects/desktop-plugin-ui/artifacts/cross-assistant/claude/`:

- `environment.json`: binary/version/hash, safe auth fields, zero model calls,
  engine-only scope, strict scanner and final test status.
- `native-validate-final.json`, `native-tests-final.txt`: final 57 passes.
- `native-tests-initial.txt`: copied original 34 passes.
- `native-tests-expanded-01.txt`: first expanded suite, 53 passes.
- `native-tests-expanded-02.txt`: 56 passes, one harness authoring failure from
  registering a floor hook after the first `$` call. Fixed registration order.
- `native-tests-expanded-03.txt`: 56 passes, one mistaken fallback expectation
  after a post-hook schema rejection. Changed to assert the observed refusal;
  positive boundary remains tested. This is a test-design correction, not a
  product repair or suppressed unexpected failure.
- Fresh official create/reference/interface/test pages and CLI help snapshots.

Current host constraints are promoted to
`skills/desktop-plugin-ui/references/claude-host-limits.md`. Do not claim actual
terminal/Desktop/editor rendering, browser opening, clipboard writing, or
permission approval from this suite. Root agent owns those GUI observations.
