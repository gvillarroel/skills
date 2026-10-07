# Metadata extractor implementation validation

Date: 2026-10-07. This records local deterministic checks only. No browser, account, network call, or live Lucid import was performed.

Implemented canonical resources:

| File | Size | Frozen SHA-256 |
| --- | ---: | --- |
| `skills/lucidchart-svg/scripts/extract_native.py` | 57,223 bytes | `4af41b4d96d09098bb2ed5c959b1619e980c30732fbe27591b20776f156e391f` |
| `skills/lucidchart-svg/scripts/test_extract.py` | 28,143 bytes | `88f8ddd1674c993b1b15c0d2d37c328664e95c449d7b05be021d80c6451b8a57` |
| `skills/lucidchart-svg/references/svg-mapping.md` | 7,800 bytes | `f1ae9600ab09b8649ae3f8c70fd46d4ff92b04d41eeaf52b26c586a58e9b1d88` |

The extractor requires an explicit producer metadata contract and a coordinate mode. It resolves supported primitives, root viewport/viewBox/aspect-ratio mapping, positive axis transforms, restricted inherited/inline styles, and source contour-to-port agreement. It does not infer topology or discard unowned artwork to make an eligible graph. Native-type declarations and type-specific properties are checked by the compiler/catalog. Unsupported source features receive source-referenced ledger entries and an artwork/hybrid fallback.

An unstroked metadata edge is refused unless `--semantic-edges` deliberately authorizes new arrow artwork. A visible unmarked edge remains unmarked. Literal strings retain decoded characters and whitespace; the ledger separately discloses native text layout, glyph/availability uncertainty, and explicit font defaults. The full script is executed from its compact reference; runtime agents need not read its 57 KB implementation.

## Commands and results

```powershell
uv run --script skills/lucidchart-svg/scripts/test_extract.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
```

All 47 extractor test groups pass. The repository validators pass. A copied standalone runtime bundle retains exactly the same file digests after a CLI extraction and creates no `.pyc` files. Source/input aliases are protected, existing graph files are preserved unless replacement is explicit, invalid XML/resource inputs get diagnostics, and output-write failures report `graph_written: false`.

Tests cover the original 24 researched feature families with supported or refused outcomes: inherited/inline/CSS paint and geometry; hidden/definition labels; internal/cyclic/unresolved uses; compound nodes; unstroked edges; `none`/alpha paints; dashes; markers; gradients; outlined text; spans/whitespace; CSS/SMIL animation; malformed paths; invalid dimensions; foreign namespaces; viewport scale/alignment; nested viewport refusal; primitive and translated incident geometry. Additional checks cover coordinate composition, metadata/reference conflicts, native catalog type selection, color normalization, rounding, opacity, nonuniform scaling, literal Unicode, route joints, fonts, and safe file boundaries.

## Cross-review failures retained and repaired

An independent reviewer retained source probes and pre-fix results in [independent-extractor-probes.json](../artifacts/data/independent-extractor-probes.json). Three inputs had incorrectly returned eligible before correction: root container opacity, a rounded rectangle bounding-box corner used as a contour attachment, and marker artwork translated away from its raw reference point.

These cases are now checked in the existing test groups `test_opacity_preserved_only_when_fusion_does_not_change_text`, `test_endpoint_match_requires_declared_contour`, and `test_recognized_marker_and_marker_refusals`. Root/link container opacity is refused, rounded arcs are checked against their actual contour, and transformed marker artwork is refused unless separately normalized. The repaired original probes remain available for review; prior evidence was not rewritten.

The first expanded 47-group run passed 46 groups and failed `test_nonfinite_viewport_diagnostic`: a NaN viewport supplied in user-space mode appeared in the coordinate ledger even when the finite viewBox determined the page size, causing report serialization to fail. The final guard checks all explicitly supplied viewport values before either mode branch. The final 47-group run passes, and the refused input writes its diagnostic report. File alias checks also cover source hard links and graph/report hard-link aliases; the bytecode guard executes before any helper import.

## Independent end-to-end geometry check

Retained source, graph, mapping ledger, `.lucid`, document JSON, compiler report, and exact CLI traces are under [viewport-meet-translation-final](../artifacts/data/viewport-meet-translation-final/verification.json).

Source viewport: 300 × 200. Source viewBox: `0 0 100 100`, default `xMidYMid meet`. Ancestor transform: `translate(5 10)`. Independent expected boxes are `(70,30,40,20)` and `(160,30,40,20)`, and both recovered boxes match exactly. The edge meets the first right-middle port `(1,.5)` and second left-middle port `(0,.5)`; its two native markers are `none`, matching the unmarked source. The page remains 300 × 200.

Original source SHA-256 is `14d877f8ede8b4751b810539e17541325a6184dbd96d1447104b04861d858d85`; bytes are unchanged after extraction and packaging. The ZIP contains only root `document.json`, and those bytes exactly match the separately written document. These results verify local transformation/packaging, not live rendering or service acceptance.

## Evaluation interface

Exit `0`: complete eligible graph written. Exit `2`: blocked source, compiler rejection, or file/argument error. Expected refusals should be captured as process results in evaluation code; their diagnostic ledger is the outcome, not an unexpected tool failure. Protected report/source path collisions can prevent report creation because overwriting the original or an existing report is forbidden.

Successful source analysis reports `native_mapping_eligibility`, declared/resolved node and edge counts, source-to-native IDs, coordinate/page evidence, upload preflight scope, `ledger`, `graph_written`, `blocking_count`, and `live_import: "not executed"`. A ledger entry includes `source_ref`, `feature`, `action`, and `detail`; actions are `preserved`, `adapted`, `omitted`, `blocked`, and `unknown`. Unsupported input remains available through the independent SVG asset workflow. No report states that a native package was accepted by Lucid.

This implementation audit changed only the extractor, its tests/reference, and project-scoped evidence. Entry instructions, inspector, compiler, catalog, backlog, runtime evaluation, and publication are owned by the parent and peer agents.
