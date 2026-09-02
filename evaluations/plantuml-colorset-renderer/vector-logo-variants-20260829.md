# PlantUML vector logo variants — 2026-08-29

## Outcome

The catalog retains 1,960 stable logo identities and now guarantees actual vector SVG source content. The audit replaced 954 raster-backed wrappers (AWS 860, GCP 93, Gemini CLI 1) plus one OpenCode wrapper that embedded Git symlink text. Exact provider/category mappings retained every stable ID and asset path. The GCP artwork is explicitly marked as official legacy console artwork; five AWS identities use archived January 2026 artwork and are marked accordingly.

The selectable inventory has 7,923 normalized SVG files: original 1,960, color 1,960, grayscale 1,007, mono-black 983, mono-white 1,030, and adaptive `currentColor` 983. AWS/GCP transformations that would violate the recorded no-derivatives constraint are unavailable rather than fabricated. Forty-seven provider-authored native white cloud sources remain available unchanged. Twenty-four permissively licensed identities lack a safe single-paint source and therefore have no black, white, or adaptive silhouette. Every unavailable choice has a machine-readable reason.

Selection markers are present in filenames and SVG metadata. `list_logo_assets.py` resolves exact IDs and reports availability. `export_logo_asset.py` writes one selected SVG plus exact provenance and complete-license sidecars, and safely bakes a literal color only from an adaptive source.

## Deterministic validation

- `upgrade_logo_vectors.py` dry run and backed-up apply: 1,960/1,960 actual vector sources; 955 reviewed replacements.
- `sync_normalized_logos.py --check`: pass for 1,960 normalized originals and exact 8,543-SVG registered inventory including internal alternate sources.
- `build_logo_variants.py --check`: pass; deterministic regeneration equals every indexed byte.
- Unit tests: 26/26 vector/variant/export, 6/6 logo catalog, and 16/16 PlantUML coverage tests passed.
- Skill quick validation, Python AST parse for 11 changed scripts, skill independence, payload, Pi-harness 11/11, and target diff checks passed.
- At the time of this run, repository-wide pattern-ID validation treated the intentional D3 template token `__PATTERN_ID__` as a public ID. On 2026-09-02 the validator was corrected to ignore uppercase template placeholders, and the pattern-ID, skill, independence, and payload gates passed. PlantUML remains `validating` for its own post-extraction runtime evidence, not because of that resolved shared gate.

## Browser validation

The self-contained Playwright audit decoded and painted 7,923/7,923 selectable SVGs, found zero blank assets, verified grayscale/black/white pixel palettes, and exercised 983/983 adaptive SVGs under two CSS colors (1,966 checks), with zero failures. A representative light/dark contact sheet showed preserved details and negative space. The only initial console entry was a missing favicon in the local QA page; a self-contained favicon removed the request and no new console errors occurred after reload. Evidence is retained under ignored `projects/plantuml-colorset-renderer/artifacts/logo-vector-audit/`.

## Isolated runtime validation

Model: `openai-codex/gpt-5.3-codex-spark`; runtime profile; strict JSON mode. These runs evaluated the pre-extraction combined PlantUML-and-logo payload. They are valid historical evidence for the logo machinery but do not by themselves validate either the current reduced PlantUML bundle or the new standalone `technical-logo-assets` bundle.

- Contract smoke `20260829-plantuml-logo-variants-contract-spark-2`: pass. All four exact outputs, JSON fields, observed model, valid events, zero tool errors, clean reads, unchanged 43.01 MiB payload, and independent byte/provenance/license validation passed. The preceding run 1 is retained as a validator/prompt plus agent failure: a PowerShell fence was not recognized as a command fence and the sample guessed a nonexistent README.
- Naturalistic repetitions 1 and 2: strict harness and independent exact-artifact validators passed. Both produced ten required files with exact SVG, provenance, and license bytes plus accurate selection notes.
- Naturalistic repetition 3: retained agent failure. It produced all nine SVG/provenance/license artifacts correctly but omitted the required `selection-notes.md`; the harness failed the exact-output gate. The predeclared naturalistic threshold passes at 2/3.

The source payload remained unchanged in every isolated run. The equivalent post-extraction prompts are versioned as `evaluations/pi-prompts/technical-logo-assets-contract.md` and `evaluations/pi-prompts/technical-logo-assets-naturalistic.md`; bulky raw evidence remains under ignored `evaluations/runs/`.
