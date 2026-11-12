# Source citation checker deterministic validation

- **Date:** 2026-10-24.
- **Skill/helper:** `desktop-plugin-ui`, `scripts/check_sources.py`.
- **Method:** Independent deterministic subprocess tests; no model run.
- **Outcome:** **18/18 behaviors passed** after a narrow URL-tokenization fix.
- **Final helper SHA-256:** `6e7b3534239da779beeadb0637b585841a571de32aa9764110949b0c618a1942`.

Run the reproducible evaluator-owned tests with:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
```

The runner creates small Markdown/JSON fixtures, invokes the helper in a
subprocess, parses its diagnostic JSON, independently checks exit statuses and
canonical candidates, then verifies SHA-256 preservation of all inputs, the
helper, and its source catalog. Raw fixtures and full results are retained under
the ignored directory
`projects/desktop-plugin-ui/artifacts/source-checker-tests/`.

## Defects found and repaired

The first run passed 16/18 cases and exposed two false positives:

1. A correct source inside a Python/JavaScript single-quoted string retained its
   closing apostrophe during URL extraction.
2. A Markdown link using a URL as its visible label merged the label and
   destination into one token across `](`.

The repair adds apostrophes and square brackets to URL-token delimiters. It does
not change the source catalog, matching rule, diagnostic schema, allowed-URL
override, or status policy. The pre-fix failure is retained in
`result-before-fix.json`; the passing final run is `result.json`.

## Coverage

| Behavior | Independent expectation | Outcome |
| --- | --- | --- |
| Correct Markdown | Canonical links pass, including a URL-as-label link and terminal punctuation | Pass |
| Correct JSON | Nested URL strings pass and duplicate identical URLs are counted once per report | Pass |
| Quoted code and anchors | Single/double-quoted URLs and exact fragments remain intact | Pass |
| Mutated `.com` report | Flag the changed host and offer the exact `.io` candidate | Pass |
| Mutated `.org` inside JSON | Flag the changed host and offer the exact `.io` candidate | Pass |
| Mutated anchored host | Preserve path and fragment when offering the exact candidate | Pass |
| GitHub primary source | Recognize bundled `modelcontextprotocol` owner source | Pass |
| Unknown owned GitHub source | Report an unlisted primary URL without inventing a candidate | Pass |
| Verified additional URL | Reject without override; pass only with exact `--allow-url` | Pass |
| Malformed JSON | Emit a diagnostic, with default exit 0 and strict exit 1 | Pass |
| Missing report path | Emit a diagnostic, with default exit 0 and strict exit 1 | Pass |
| Invalid UTF-8 | Emit a readable failure result under strict mode | Pass |
| Unrelated URLs | Ignore ordinary example and unrelated GitHub sources | Pass |
| No mutation | Report bytes, helper, and bundled catalog hashes stay unchanged | Pass |

The detailed result has 18 executable checks because the diagnostic/strict and
allow/disallow alternatives are separate cases. The allowed additional URL is
the [official MCP Apps quickstart](https://apps.extensions.modelcontextprotocol.io/api/documents/quickstart.html),
which was independently fetched in this task's earlier source review and is not
in the helper's bundled catalog.

## Limits

This is a local exact-citation diagnostic. It does not fetch pages, establish
their availability, verify their claims, or independently verify a caller's
`--allow-url` assertion. It scans supported official source families and ignores
unrelated URLs; a clean result is not a general link or provenance audit. The
tests establish deterministic helper behavior, not model compliance with its
output or a live Claude Desktop result.
