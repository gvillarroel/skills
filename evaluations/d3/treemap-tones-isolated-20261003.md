# D3 Treemap and Dense Overlap Isolated Validation

Date: 2026-10-03. Model exception: `openai-codex/gpt-5.6-luna`, recorded in the D3 backlog because Spark was unsupported. All finalized runs use JSON strict mode, the runtime profile, exact non-empty output expectations, prompt-first/observed-model/read-surface checks, zero tool-error acceptance, and unchanged copied skill payloads.

Final payload: `85f8b06cb64e88ba83448270804dab58671e707d1cf1cb1b48983313c90d5bd0`. Final cohort acceptance: **PASS**.

The initial treemap freeze used 288 runtime files with digest `fec0c61e4ff3ad2a4ffc4a0fec4444040f5be94d07767e45bc93bc24a253ca30`. Added dense-overlap steering produced the second 288-file digest `fd964189150e248e286954dc1b3019473980a2c47c2efe178a4d891241d39195`. Repeated agent omissions of mandatory finalization and incorrect exact black/white text motivated the compact deterministic standalone treemap route. These old-payload attempts are retained and cannot certify the later release payload.

The first deterministic treemap builder produced 289 runtime files with digest `869500828be9b356d53b9603c2aac23597f24562832e9fc77c758bdbf42de869`. Its treemap contract passed, all 28 rendered states passed, and exactly two of three fresh naturalistic runs passed jointly; the third had an invented SVG-ID check error. Two subsequent dense-overlap contracts failed strict and rendered acceptance. The complete payload is superseded by a deterministic dense-overlap builder; the earlier accepted treemap cohort remains evidence but is not counted toward a later digest.

The final runtime contains 290 files. Its selected treemap contracts are `d3-treemap-tones-contract-20261003-luna-5`; selected dense-overlap contracts are `d3-dense-overlap-contract-20261003-luna-4`. The fresh naturalistic denominator is exactly `d3-treemap-tones-naturalistic-20261003-luna-7`, `d3-treemap-tones-naturalistic-20261003-luna-8`, `d3-treemap-tones-naturalistic-20261003-luna-9`: 2/3 pass jointly. Independent artifact grades pass in 47 current rendered states. Invented ordering or rounded-dimension assertions remain strict failures and are not promoted by a passing artifact review.

| Attempt | Thinking | Strict | Independent artifacts | Status |
| --- | --- | --- | --- | --- |
| `d3-treemap-tones-contract-20261003-luna-1` | high | FAIL | PASS | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-1` | high | Unfinalized | Not accepted | unfinalized-infrastructure |
| `d3-treemap-tones-contract-20261003-luna-2` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-2` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-3` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-contract-20261003-luna-3` | medium | PASS | PASS | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-4` | medium | PASS | PASS | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-5` | medium | FAIL | PASS | superseded |
| `d3-treemap-tones-naturalistic-20261003-luna-6` | medium | PASS | PASS | superseded |
| `d3-dense-overlap-contract-20261003-luna-1` | medium | FAIL | FAIL | superseded |
| `d3-dense-overlap-contract-20261003-luna-2` | medium | FAIL | FAIL | superseded |
| `d3-treemap-tones-contract-20261003-luna-4` | medium | FAIL | PASS | current |
| `d3-treemap-tones-naturalistic-20261003-luna-7` | medium | FAIL | PASS | current |
| `d3-treemap-tones-naturalistic-20261003-luna-8` | medium | PASS | PASS | current |
| `d3-treemap-tones-naturalistic-20261003-luna-9` | medium | PASS | PASS | current |
| `d3-dense-overlap-contract-20261003-luna-3` | medium | FAIL | PASS | current |
| `d3-treemap-tones-contract-20261003-luna-5` | medium | PASS | PASS | current |
| `d3-dense-overlap-contract-20261003-luna-4` | medium | PASS | PASS | current |

## Retained Failure Classification

- `d3-treemap-tones-contract-20261003-luna-1`: Agent omitted active palette metadata at its first check and attempted an exact SVG replacement with stale oldText. The final artifact passes independently; strict release acceptance fails.
- `d3-treemap-tones-naturalistic-20261003-luna-1`: The environment update interrupted the run and no evaluation-result.json or live runner remained. Its payload was superseded by added overlap steering. No pass is claimed.
- `d3-treemap-tones-contract-20261003-luna-2`: Agent omitted active palette metadata at its first check; actual labels violate exact maximum-contrast black/white, and Operations area fractions diverge by 0.0734. Both strict and artifact gates fail.
- `d3-treemap-tones-naturalistic-20261003-luna-2`: Agent used #fff shorthand and omitted active metadata, guessed a missing ID, and issued unsuccessful edit/substring probes. Actual light-gray leaf labels violate maximum-contrast black/white; the portable SVG additionally gets Intake wrong.
- `d3-treemap-tones-naturalistic-20261003-luna-3`: Agent used #fff shorthand and omitted active metadata. Its custom no-network assertion incorrectly rejects the required SVG xmlns URI as an external dependency. Actual light-gray labels violate maximum-contrast black/white.
- `d3-treemap-tones-naturalistic-20261003-luna-5`: Agent required d3-treemap-cs1 pattern metadata as the SVG DOM id, although the builder root id is treemap. Actual artifacts pass all seven independent states; the single failed guessed-ID check rejects strict acceptance.
- `d3-dense-overlap-contract-20261003-luna-1`: Agent omitted --force when replacing an existing finalized HTML, causing a strict tool error. Native HTML passes four painted-radius states, but CSS/Web Animation radii leave the exported SVG at r=0 for nine regions and 100 dots; both portable SVG states fail. Originals remain untouched.
- `d3-dense-overlap-contract-20261003-luna-2`: Agent first omitted SVG desc, attempted a stale exact edit and again omitted --force on an existing final HTML. Actual geometry, semantic alpha, maximum BW and sampled pixels pass, but its inherited 16px footer overlaps T094, T095 and T100 in every HTML/SVG state. Strict and independently rendered acceptance both fail; no artifact repair is accepted.
- `d3-treemap-tones-contract-20261003-luna-4`: Agent imposed an unrequested parent/children interleaving order with --ordered-text although the builder emits parent headers and then leaves. Required names, values, true geometry, tonal paint and all seven independent rendered states pass; the invented ordering assertion rejects strict acceptance.
- `d3-treemap-tones-naturalistic-20261003-luna-7`: Agent imposed a guessed fixed viewBox of 0 0 960 540 on a responsive export. The task and builder do not promise those dimensions; all seven independent rendered states and direct narrow review pass, but the unnecessary fixed-size assertion rejects strict acceptance.
- `d3-dense-overlap-contract-20261003-luna-3`: Agent imposed a rounded fixed viewBox of 0 0 880 490 on the portable export, then repeated the same false requirement with lower-case attribute spelling. Actual export is 0 0 880 489.85; all six independent rendered states and direct SVG review pass. Both unnecessary dimension assertions remain strict tool errors.

## Diagnostic Finalization

The existing colorset adapter was applied only to a separate diagnostic copy of naturalistic attempt 2, followed by a fresh SVG export. The original exact-output hashes remain unchanged. The diagnostic copy passes the active-palette check and independent HTML/SVG rendering at 960 and 420 pixels, including exact maximum-contrast black/white labels. **This diagnostic copy is not a Pi pass and does not repair the failed run.** The independent metadata/BW proof is retained under `projects/treemap-tones/artifacts/diagnostic/naturalistic-2/`. Incorrect quantitative geometry, such as contract attempt 2, still requires truthful D3 construction.

The original input and normalized-copy commands, all manifest/event/artifact/grade hashes, complete tool errors, read lists and payload digests are in [the machine record](treemap-tones-isolated-20261003.json). Raw workspaces and JSONL traces remain under `evaluations/runs/`.

## Independent Review

The evaluator captures actual rendered fill, stroke, effective ancestor opacity, text and rectangles for HTML and portable SVG at 960/420 pixels. It checks exact branch/leaf names and values, three distinct opaque solid sibling tones, contained labels, proportional leaf areas, borderless cells, maximum-contrast black/white paint and HTML/SVG color parity. A local 1.15:1 minimum step between sorted sibling luminances is a distinguishability check, not a WCAG claim. Direct screenshot review remains part of acceptance.

The capture initially treated adjacent tspan lines as concatenated tokens and incorrectly applied HTML responsive overflow to an intrinsic-width SVG export; those evaluator findings were corrected before judging artifacts. A native SVG full-page screenshot timeout was resolved with viewport capture without changing generated artifacts.

Dense overlap uses the independent source-over inspector from `projects/task-overlap-transparency/scripts/verify_overlap.py`, bound to the retained original geometry manifest. Its standalone wrapper checks nine semantic-alpha regions, 100 task dots/labels/leaders, original positions and memberships, opaque borderless label faces, maximum BW text over actual composited backing, clear single/double/triple overlap pixel samples, two Replay states and reduced motion.

The standalone overlap evaluator measures each circle's actually painted local radius via `getBBox`, including CSS/SMIL animation. Comparing only the underlying `r` attribute falsely rejected the native HTML of overlap attempt 1. Corrected native review passes four states, while its exported SVG genuinely retains `r=0` and shows none of the nine regions or 100 task dots. That portable export remains a failure; the evaluator correction does not repair or waive it.

Direct inspection of overlap attempt 2 found that its footer caption inherited a 16px font and covered task labels T094, T095 and T100. Rendered bounding-box measurements confirm three caption/task-label collisions in every one of the six states; these explicit readability findings reject the artifact gate even though the geometry, semantic alpha, BW and pixel audits pass. The inspector now retains the caption font and both intersecting bounds.

Final runs use the original unmodified task prompts. Medium thinking is a scoped runtime choice for this narrow painting revision; model, isolation, strict trace and independent rendered acceptance requirements are unchanged.
