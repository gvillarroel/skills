# D3 Treemap and Dense Overlap Isolated Validation

Date: 2026-10-03. Model exception: `openai-codex/gpt-5.6-luna`, recorded in the D3 backlog because Spark was unsupported. All finalized runs use JSON strict mode, the runtime profile, exact non-empty output expectations, prompt-first/observed-model/read-surface checks, zero tool-error acceptance, and unchanged copied skill payloads.

Current phase: **builder-pending**. The final deterministic-builder cohort is pending until the source is frozen.

The initial treemap freeze used 288 runtime files with digest `fec0c61e4ff3ad2a4ffc4a0fec4444040f5be94d07767e45bc93bc24a253ca30`. Added dense-overlap steering produced the second 288-file digest `fd964189150e248e286954dc1b3019473980a2c47c2efe178a4d891241d39195`. Repeated agent omissions of mandatory finalization and incorrect exact black/white text motivated the compact deterministic standalone treemap route. These old-payload attempts are retained and cannot certify the later release payload.

| Attempt | Thinking | Strict | Independent artifacts | Status |
| --- | --- | --- | --- | --- |
| `d3-treemap-tones-contract-20261003-luna-1` | high | FAIL | PASS | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-1` | high | Unfinalized | Not accepted | unfinalized-infrastructure |
| `d3-treemap-tones-contract-20261003-luna-2` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-2` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-3` | medium | FAIL | FAIL | superseded |

## Retained Failure Classification

- `d3-treemap-tones-contract-20261003-luna-1`: Agent omitted active palette metadata at its first check and attempted an exact SVG replacement with stale oldText. The final artifact passes independently; strict release acceptance fails.
- `d3-treemap-tones-naturalistic-20261003-luna-1`: The environment update interrupted the run and no evaluation-result.json or live runner remained. Its payload was superseded by added overlap steering. No pass is claimed.
- `d3-treemap-tones-contract-20261003-luna-2`: Agent omitted active palette metadata at its first check; actual labels violate exact maximum-contrast black/white, and Operations area fractions diverge by 0.0734. Both strict and artifact gates fail.
- `d3-treemap-tones-naturalistic-20261003-luna-2`: Agent used #fff shorthand and omitted active metadata, guessed a missing ID, and issued unsuccessful edit/substring probes. Actual light-gray leaf labels violate maximum-contrast black/white; the portable SVG additionally gets Intake wrong.
- `d3-treemap-tones-naturalistic-20261003-luna-3`: Agent used #fff shorthand and omitted active metadata. Its custom no-network assertion incorrectly rejects the required SVG xmlns URI as an external dependency. Actual light-gray labels violate maximum-contrast black/white.

## Diagnostic Finalization

The existing colorset adapter was applied only to a separate diagnostic copy of naturalistic attempt 2, followed by a fresh SVG export. The original exact-output hashes remain unchanged. The diagnostic copy passes the active-palette check and independent HTML/SVG rendering at 960 and 420 pixels, including exact maximum-contrast black/white labels. **This diagnostic copy is not a Pi pass and does not repair the failed run.** The independent metadata/BW proof is retained under `projects/treemap-tones/artifacts/diagnostic/naturalistic-2/`. Incorrect quantitative geometry, such as contract attempt 2, still requires truthful D3 construction.

The original input and normalized-copy commands, all manifest/event/artifact/grade hashes, complete tool errors, read lists and payload digests are in [the machine record](treemap-tones-isolated-20261003.json). Raw workspaces and JSONL traces remain under `evaluations/runs/`.

## Independent Review

The evaluator captures actual rendered fill, stroke, effective ancestor opacity, text and rectangles for HTML and portable SVG at 960/420 pixels. It checks exact branch/leaf names and values, three distinct opaque solid sibling tones, contained labels, proportional leaf areas, borderless cells, maximum-contrast black/white paint and HTML/SVG color parity. A local 1.15:1 minimum step between sorted sibling luminances is a distinguishability check, not a WCAG claim. Direct screenshot review remains part of acceptance.

The capture initially treated adjacent tspan lines as concatenated tokens and incorrectly applied HTML responsive overflow to an intrinsic-width SVG export; those evaluator findings were corrected before judging artifacts. A native SVG full-page screenshot timeout was resolved with viewport capture without changing generated artifacts.

Dense overlap uses the independent source-over inspector from `projects/task-overlap-transparency/scripts/verify_overlap.py`, bound to the retained original geometry manifest. Its standalone wrapper checks nine semantic-alpha regions, 100 task dots/labels/leaders, original positions and memberships, opaque borderless label faces, maximum BW text over actual composited backing, clear single/double/triple overlap pixel samples, two Replay states and reduced motion.

Final runs use the original unmodified task prompts. Medium thinking is a scoped runtime choice for this narrow painting revision; model, isolation, strict trace and independent rendered acceptance requirements are unchanged.
