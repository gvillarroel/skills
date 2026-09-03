# Technical Logo Assets standalone validation — 2026-09-02

## Outcome

The standalone bundle passes every available deterministic, artifact, rights/provenance, and browser-rendering gate. The catalog contains 1,960 stable identities and 7,923 selectable SVG files. All 620 digest-sealed alternate source snapshots match their manifest SHA-256 values, the full browser audit decoded and painted every selectable SVG, and the two isolated local evaluation cases produced exactly the requested outputs.

A fresh strict `pi` release run with `openai-codex/gpt-5.3-codex-spark` was not launched because the shared Spark allowance was already exhausted before this validation pass. No retained strict run for this standalone skill was present under `evaluations/runs/`. This is an infrastructure-blocked release-evidence gap, not a task, agent, verifier, or skill failure. The bundle should remain `validating` until a fresh strict Spark run can be recorded.

## Defect found and corrected

The initial `sync_normalized_logos.py --check` failed on a digest-sealed Devicon source snapshot. Repository-wide `*.svg text eol=lf` handling had converted the upstream snapshot's final CRLF to LF, changing its SHA-256 while leaving the artwork unchanged. A bounded check of all 620 alternate sources found nine snapshots with exactly this failure shape: replacing only the terminal LF with the upstream CRLF produced the pinned manifest digest in every case.

The repair is deliberately narrow:

- `.gitattributes` now marks only `skills/technical-logo-assets/assets/logos/sources/*.source.svg` as `binary`, preserving exact provider bytes and disabling misleading text diffs/merges for digest-sealed snapshots.
- The nine affected snapshots were restored to their pinned bytes; each file grew by exactly one CR byte.
- `git check-attr` reports `binary: set`, `diff: unset`, `merge: unset`, and `text: unset` for the snapshots.
- `git diff --check -- .gitattributes skills/technical-logo-assets evaluations/technical-logo-assets` passes.
- The immutable Devicon Gazebo URL at commit `7330accdbc47e2dc0c19789a48533c4a3c50fe58` was independently fetched during diagnosis: its 1,158 bytes end in CRLF and hash to the manifest value `ad8f495ed6f5ab0a3bbc0928169c09353ae3991b7deb33327296d15492932732`.

This was classified as a repository packaging defect. The catalog identity, geometry, licenses, and derived variant manifests did not need to change.

## Deterministic catalog gates

All commands ran from the repository root after the byte-preservation repair:

```powershell
uv run --script skills/technical-logo-assets/scripts/sync_normalized_logos.py --check
uv run --script skills/technical-logo-assets/scripts/build_logo_variants.py --check
uv run --script skills/technical-logo-assets/scripts/test_logo_assets.py
uv run --script skills/technical-logo-assets/scripts/test_logo_variants.py
```

Results:

- Normalized catalog validation: PASS, 1,960/1,960 identities.
- Variant regeneration check: PASS, `{"ok": true, "errors": []}`.
- Logo asset tests: PASS, 6/6.
- Variant tests: PASS, 26/26.
- Pinned source digest sweep: PASS, 620 checked, 0 mismatches.
- Catalog root: schema 3, `vectorOnly: true`, 22 source groups.
- Variant inventory: schema 1, policy 1, 1,960 identities, 7,923 selectable SVGs, 620 source snapshots.
- Coverage: 1,960 original, 1,960 color, 1,007 grayscale, 983 mono-black, 1,030 mono-white, and 983 adaptive.

The bundled tests recursively decode SVG content and reject raster images, external resources, active content, invalid fonts, missing source bytes, digest drift, invalid normalization, or inventory drift. Provider SVGs protected by no-derivatives licenses may contain a self-contained `data:image/svg+xml;base64` wrapper to preserve exact artwork; this is vector SVG, not raster. The evaluator decodes and recursively inspects that nested SVG.

## Isolated local evaluation cases

Both cases used a fresh workspace under `evaluations/runs/` containing only the runtime skill bundle. Each copied payload contained 8,571 files / 45,253,096 bytes. A read-only `robocopy /L /MIR` comparison after execution returned difference code 0 for both copies, proving the skill payload was unchanged.

### Contract case

Workspace: `evaluations/runs/20260902-technical-logo-local-contract/workspace/`

The two exact fenced commands from `evaluations/pi-prompts/technical-logo-assets-contract.md` ran without exploratory commands. The output set was exactly:

- `deliverable/python-blue.svg`
- `deliverable/python-blue.provenance.json`
- `deliverable/python-blue.license.txt`
- `deliverable/lambda-choice.json`

Independent evaluator result: PASS. The Python export is a fixed `#007298` custom-color SVG derived from the available adaptive variant, its SHA-256 is `dd2aa6a60d0c234b7bcf1f910a268b54be46ba1903f3d84c5962bae86f1701f2`, and its provenance hash matches. The Lambda query resolves exact ID `aws-compute-lambda`, requested variant `adaptive`, `available: false`, `path: null`, `recolorable: false`, license `CC-BY-ND-2.0`, and reason `license-no-derivatives`.

Evaluator report: `evaluations/runs/20260902-technical-logo-local-contract/evaluator-report.json` (SHA-256 `7f86cb5d1912d88ceb3ef2770d5278ee01623f205c45f1dc4b8ebaaffb354ac4`).

### Naturalistic case

Workspace: `evaluations/runs/20260902-technical-logo-local-naturalistic/workspace/`

The output set was exactly the three requested SVGs, three provenance files, three full license files, and `selection-notes.md`. Independent evaluator result: PASS.

- `devicon-python`, fixed custom color `#9e1b32`: SHA-256 `1d67ad481e7f8655ad85cf97d4c08aca55487989867cb222cf3af38bec7874e4`.
- `devicon-kubernetes`, `mono-white`: SHA-256 `098073621e2561856bbd1c1827ca4335895c2efb1e51d86bb2dd9dfa7c1d1bc3`.
- `aws-compute-lambda`, exact provider `color`: SHA-256 `56cea10d841780f9081288eabd1337d27af86cd6cf3f4dd22d6f8be9dff98a3c`.

The evaluator checked normalized geometry, exact IDs and variants, fixed-color semantics, pure-white paint, recursive vector-only content, no raster/external/active resources, SVG-to-provenance digest binding, source digests, exact MIT/CC-BY-ND licensing, and the notes' adaptive-color and no-derivatives explanation.

Evaluator report: `evaluations/runs/20260902-technical-logo-local-naturalistic/evaluator-report.json` (SHA-256 `c1848271ba0290c9781c19ca50c8fff480e5e124550cf97f6c4e1ab535dcc872`). The reusable evaluator is `evaluations/technical-logo-assets/verify_exports.py`.

## Full browser audit

The audit page was generated outside the skill with:

```powershell
uv run --script skills/technical-logo-assets/scripts/build_logo_audit.py --output evaluations/runs/20260902-technical-logo-browser-audit/logo-audit.html
```

The generated page was served only on loopback and exercised with `@playwright/cli` in installed Google Chrome. The full audit result was:

- PASS, 7,923 expected and 7,923 decoded.
- 1,657,925 painted pixels detected.
- 983 adaptive SVGs tested with two CSS colors each, for 1,966 adaptive color checks.
- 0 audit failures in 84,454 ms.
- 0 console errors and 0 console warnings.
- 0 external network requests; the only request was the locally served self-contained audit page.

Visual inspection passed for all 12 representative rows, including AWS Lambda and GCP no-derivatives availability labels; original/color/grayscale on light cards; mono-white on dark cards; and adaptive variants first at `#007298` and then at `#9e1b32`. The color change visibly propagated only to the adaptive column while fixed/provider colors remained stable.

Compact local evidence:

- `evaluations/runs/20260902-technical-logo-browser-audit/logo-vector-browser-audit.json` — SHA-256 `5bd324a7e7fcd85fa589db344135167f58aeec840952ed82e23a55a81bc4c63c`.
- `evaluations/runs/20260902-technical-logo-browser-audit/browser-qa.json` — browser, console, network, and inspection record.
- `evaluations/runs/20260902-technical-logo-browser-audit/logo-audit-default.png` — default adaptive color screenshot.
- `evaluations/runs/20260902-technical-logo-browser-audit/logo-audit-adaptive-red.png` — changed adaptive color screenshot.

The 46.4 MB generated audit HTML and screenshots remain under ignored `evaluations/runs/`; they are evidence, not runtime payload.

## Release classification

| Gate | Result | Classification |
| --- | --- | --- |
| Deterministic source/variant maintenance | PASS after repair | Initial failure was a repository EOL-packaging defect; fixed |
| Unit/contract tests | PASS, 32/32 | No remaining defect |
| Exact inventory and source SHA sweep | PASS | No remaining defect |
| Isolated local contract artifacts | PASS | No remaining defect |
| Isolated local naturalistic artifacts | PASS | No remaining defect |
| Full browser decode/paint/adaptive audit | PASS | No remaining defect |
| Fresh strict Spark forward run | BLOCKED before launch | External shared-model quota; no skill verdict |

Recommended backlog state: `validating` until the strict Spark run is available; after that single remaining release-evidence gate passes, promote to `done`.
