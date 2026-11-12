# V4 report checker and evaluator review

Date: 2026-10-24 America/New_York / 2026-10-25 UTC. This deterministic review
preceded the v4 forward-test launch. It uses no model inference or external
services. The reviewer did not edit either canonical checker script.

Final reviewed `check_reports.py` SHA-256:

`68892c9952c6036c2e07cade284280282f4d97f7aef2f04be0395fd3a983e1b2`

The independent v4 evaluator is a new file,
[`inspect_cross_v4.py`](inspect_cross_v4.py), version
`desktop-plugin-ui-cross-v4`, SHA-256:

`5014634fcd76e38a3b4aea35390b6d0669fbc52a169fe0cd45d7eb35543a9155`

The original [`inspect_cross_runs.py`](inspect_cross_runs.py) remains unchanged
at SHA-256
`56148e95f0d4dace09a07ef600c39dc61bd07eed56422e9e48492abc6ea9bf10`.
It remains the reproducer for v1–v3 reports. The stricter v4 evaluator is
declared before v4 outcomes and must not retroactively replace older grades.

## Checker review

Reviewed implementation and deterministic test cases for these properties:

- Default diagnostics do not modify reports and return zero with actionable
  findings. `--fail-on-findings` is a separate clean CI gate.
- Historical evidence is checked in **each row's `evidence` string** using
  lowercase literal canonical tokens. A label in `result`, a non-string field,
  or another row cannot satisfy it. The helper never adds labels or infers
  empirical success, acceptance, version, scope, or facts.
- Citation validation uses the checker sibling loaded by absolute
  script-relative path and the owning copied bundle's source catalog. It
  suppresses import bytecode and does not import a same-named CWD file.
- Explicit URL repairs operate on complete matching URL tokens and replace
  every exact occurrence simultaneously. They do not cascade or change a
  longer prefix URL. Replacement destinations must be exact bundled sources;
  `--allow-url` cannot enlarge the repair catalog.
- All reports are preflighted before any planned repair. Invalid JSON or
  invalid replacement arguments block the batch. Per-file writes are atomic,
  preserve UTF-8 BOM/newlines, and break external hardlink aliases without
  mutating bundle source. Lexical and resolved paths protect the read-only
  bundle, including a symlink alias.
- Decoded JSON string/key inspection catches escaped-slash URL mutations.
  It performs validation only and does not implicitly reformat JSON or expand
  literal replacement behavior.

The owning agent's final deterministic suite reported **33/33 passes**, no
skips, and the exact final helper hash above. Tests cover source/evidence
diagnostics, malformed inputs, all-occurrence repair, no cascading, prefix
nonmatching, batch preflight, bundle/symlink/hardlink guards, safe imports,
Unicode/BOM/CRLF, and escaped JSON URLs.

## Independent probes and correction retained

An independent byte probe found that a prior candidate removed UTF-8 BOM
while repairing a URL. It preserved CRLF after the author's earlier newline
fix. This report's reviewer sent the finding to the owner; the owner fixed
the canonical script and added combined Markdown/JSON BOM+CRLF cases.
The original failing byte result remains in
`projects/desktop-plugin-ui/artifacts/report-checker-independent-review/bom-crlf-result-before-fix.json`.

Five independent probes passed against the final `68892c...` candidate:

1. BOM+CRLF Markdown repair preserves every byte except the exact requested URL.
2. BOM+CRLF JSON repair has the same preservation and still parses.
3. A canonical URL serialized with escaped solidus characters passes.
4. An escaped mutated URL is diagnosed with its exact source candidate,
   default exit zero, and no report mutation.
5. The unmodified real v3 boundary JSON produces all six misplaced-field
   findings, default exit zero, and identical before/after bytes.

Results are retained in
`projects/desktop-plugin-ui/artifacts/report-checker-independent-review/independent-review-6889.json`.
Earlier helper-candidate review results remain separate; only the final hash
above is cleared for the v4 cohort.

## V4 grader declaration

The new grader retains exact outputs, frozen payload/model checks, canonical
pattern discovery, host coverage, exact source membership, artifact hashes,
and manual-review cues. It strengthens historical evidence checks to require
the canonical token in **every requested `evidence` string**, with exact
lowercase spelling. It independently executes the copied `check_reports.py`
and requires successful post-final-write report checks covering both artifacts.
That report check includes source validation.

Its **21 deterministic self-tests passed**, including the former v3
result-versus-evidence error, mixed good/bad rows, noncanonical spelling,
non-string evidence, unknown sources, missing host coverage, exact pattern
counts, and malformed decision JSON shape. A separate real-v3 regression
probe found all six wrong-field rows through the new per-field criterion.

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-report-checker.py
uv run --script evaluations/desktop-plugin-ui/inspect_cross_v4.py --self-test
```

No v4 forward run was launched by this reviewer before final clearance and
root's coordinated frozen-payload notification. Do not silently mix the prior
`acf9c69...` helper candidate with the final `68892c...` candidate in a cohort.
Facts and UI acceptance still require independent semantic review; neither
checker can establish host support from a label or source link.
