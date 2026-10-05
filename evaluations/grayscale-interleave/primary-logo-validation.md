# Primary D3 logo validation

Date: 2026-10-05. The fresh R2 cohort is accepted: its command contract and two of three natural repetitions jointly pass strict trace checks and independent native inspection. The failed repetition remains failed. [The durable JSON](primary-logo-validation.json) binds each raw trace, manifest, result, integrity check, output and independent report by SHA-256.

The current and all four copied runtime payloads are identical: D3 SHA-256 `1c61ccd9693630dc686eb408cba1736fe83fbf0ff70449a44e2894b779ef2450`, 296 files. All four traces observe only `openai-codex/gpt-5.6-luna`. The contract requires the exact fenced commands. Every run checks these four exact outputs: `deliverables/logo.html`, `deliverables/validation.json`, `deliverables/native.json`, and `deliverables/small-logo.png`. The prompt text digests are `13da5ca6cc529d0e00c1ff505b6da9ae027a89d74cb40263517d861008500c0e` for the contract and `a67b3a77dd32031cd2e13010b7c4f6070fd476dc654d9e8958e58a5e2ba218bd` for all natural repetitions. Raw copied prompt bytes are also bound separately in JSON.

| Run under `evaluations/runs/` | Strict | Native/manual | Joint | Duration |
| --- | --- | --- | --- | --- |
| `gray-20261005-logo-r2-d3-contract-1` | Pass | Pass | Pass | 56.050 s |
| `gray-20261005-logo-r2-d3-naturalistic-1` | Fail | Pass | Fail | 62.297 s |
| `gray-20261005-logo-r2-d3-naturalistic-2` | Pass | Pass | Pass | 67.451 s |
| `gray-20261005-logo-r2-d3-naturalistic-3` | Pass | Pass | Pass | 61.404 s |

The successful traces contain no invalid JSON or tool errors, preserve the copied bundle, and create all exact output paths. Runtime reading is limited to the task prompt, `SKILL.md`, the compact `references/logo-studio.md` when needed, and generated reports or the PNG. No trace reads examples, a gallery source, a vendor file, the large logo engine, a sibling skill, or repository guidance. The builder and compact verifier execute their bundled resources normally.

Independent checks reran the current `validate_logo_artifact.py --require-colorset colorset1` and the uv `verify_logo_gallery.py --small-only` for each retained HTML, writing to project-owned evidence paths without changing trial files. All four static checks have exact engine/registry parity and no findings; all four native checks have no findings, console errors, page errors or external requests. Every retained and independently recaptured PNG was opened at its original 96 × 64 size. ATLAS is complete and legible, and the red mark and white initials remain visible without clipping or glyph overlap. The small-size tagline omission preserves its accessible text. All eight PNGs have SHA-256 `0ae2904d6816a045385205061577a177c54c6f0d67dd40686a0d377eee8a371b`; all four HTML outputs have SHA-256 `09bf2b6e36cc00420d22be610b35b21221416d23a4c7980d1f9a7f32a1ec5bac`.

R2 naturalistic-1 has a single tool error at event line 527: an extra plain-Python artifact inspection imports Pillow and raises `ModuleNotFoundError`. Its documented builder, validator and uv compact verifier had already succeeded. A later standard-library PNG-header inspection at line 714 recovers, but neither that recovery nor its readable artifact overrides the strict failure. No further canonical repair was needed.

The earlier R1 naturalistic-2 timeout and R1 naturalistic-3 Playwright import failure remain preserved as development failures on the prior 295-file payload. Their exact outcomes and raw hashes are bound in the JSON; [the SVG native summary](svg-native-summary.md) explains the narrow guidance repair before R2. Earlier recovered artifacts do not contribute to the accepted repetition count.

The audit is reproducible with:

```bash
uv run --script projects/grayscale-interleave/scripts/svg-review-primary-logo.py --capture
uv run --script projects/grayscale-interleave/scripts/svg-review-primary-logo.py --manual-review projects/grayscale-interleave/artifacts/reviews/primary-logo/manual-png-review.json
```

The first command prepares independent reports but cannot accept without a hash-bound visual verdict. The second command verifies the retained evidence and those manually recorded PNG verdicts. Bulky reports, screenshots and command logs remain under `projects/grayscale-interleave/artifacts/reviews/primary-logo/`. This focused primary-logo acceptance covers the requested compact Type Orbit flow; it supplements the complete 90-card fixture regression and does not certify every future authored logo or every shaded palette pixel.
