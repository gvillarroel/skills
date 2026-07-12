# Pattern ID Normalization — 2026-07-11

## Outcome

Pattern IDs now follow one repository-wide contract: `<namespace>-<semantic-slug>[-<variant>]`. The normalized inventory contains 1,037 unique canonical item IDs. The longest ID is 47 characters; none exceed the 48-character review threshold or the 64-character limit.

Page and example-set IDs remain unchanged. Upstream API keys, renderer modes, and local source IDs also remain unchanged; item surfaces expose those values through `data-example-id` while `data-pattern-id` carries the globally unique public ID.

## Canonical Contract

- Use lowercase hyphen-case.
- Omit redundant `pattern`, `item`, `example`, and `feature` segments.
- Keep the renderer or owning family as the namespace.
- Reuse the same semantic slug across namespaces for the same mechanism.
- Put style variants last, such as `-cs1` and `-cs2`.
- Keep a legacy alias only when it differs from the canonical ID.
- Redirect old hashes to canonical hashes on published galleries.

## Inventory

| Family | Canonical item IDs |
| --- | ---: |
| D3 base registry | 241 |
| D3 colorset1 gallery | 224 |
| D3 colorset2 gallery | 224 |
| D3 composition variants | 78 |
| ECharts | 43 |
| Mermaid base | 41 |
| Mermaid directives | 36 |
| PlantUML colorset1 | 28 |
| PlantUML colorset2 | 28 |
| Three.js | 24 |
| Slidev ECharts | 32 |
| Slidev Anime.js | 27 |
| AI concepts | 11 |
| **Total** | **1,037** |

The D3 registry has 237 reference files because four references intentionally declare multiple related IDs. Of the 241 base IDs, 224 are backed by the published gallery.

## Migration Highlights

| Former public ID | Canonical ID |
| --- | --- |
| `d3-pattern-critical-rate-limit-token-bucket` | `d3-token-bucket` |
| `d3-pattern-deep-learning-model-execution` | `d3-mlp-execution` |
| `d3-pattern-token-boxes-to-context-window` | `d3-context-window-fill` |
| `d3-pattern-document-token-extraction-buckets` | `d3-document-token-bins` |
| `d3-pattern-correlogram-histogram` | `d3-correlogram` |
| `d3-pattern-cs2-force-network` | `d3-force-network-cs2` |
| `d3-composition-balance-symmetry-force-network` | `d3-composition-symmetry-force-network` |
| `d3-composition-thirds-fifths-grid-correlogram-histogram` | `d3-composition-modular-grid-correlogram` |
| `echarts-pattern-map` | `echarts-geo-map` |
| `mermaid-pattern-block-diagram` | `mermaid-block` |
| `mermaid-directive-block-diagram-directive-selectors` | `mermaid-directive-block-selectors` |
| `plantuml-usecase` | `plantuml-use-case-cs2` |
| `threejs-pattern-scaled-attention-3d` | `threejs-scaled-dot-product-attention` |
| `slidev-echarts-chart-map` | `slidev-echarts-geo-map` |
| `slidev-animejs-feature-svg-drawable` | `slidev-animejs-svg-drawable` |
| `ai-concept-pattern-01-what-is-an-llm` | `ai-llm` |

The same-mechanism alignment now includes pairs such as `d3-speculative-decoding` / `threejs-speculative-decoding`, `d3-moe-router-capacity` / `threejs-moe-router-capacity`, and `echarts-geo-map` / `slidev-echarts-geo-map`.

## Backward Compatibility

Published example sources retain former IDs as `data-legacy-pattern-id` values when an actual rename occurred. D3, ECharts, Mermaid, PlantUML, Three.js, and AI concept pages redirect matching legacy hashes to their canonical card or scene. Mermaid directives and PlantUML colorset1 omit redundant legacy metadata when the old and canonical IDs are equal.

## Validation

The following checks passed on 2026-07-11:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/build-pages.py
```

`validate-pattern-ids.py` derives every family inventory, validates global uniqueness and length, checks local/source IDs, enforces style ordering and semantic mappings, checks active evaluation prompts, and verifies the 78-entry D3 composition manifest.

Fixture checks also passed for 224 D3 base cards, 224 colorset1 cards, 224 colorset2 cards, 78 D3 compositions, 43 ECharts cards, 77 Mermaid cards on the directives page, 28 PlantUML cards per colorset, 24 Three.js scenes, 32 Slidev ECharts patterns, 27 Slidev Anime.js patterns, and 11 AI concepts. Slidev builds, browser metadata checks, legacy redirects, child SVG/canvas metadata, and D3 index/reference extraction passed.

Strict isolated `pi` validation with `openai-codex/gpt-5.3-codex-spark` passed for:

- `20260711-pattern-id-d3-fault-tree`
- `20260711-pattern-id-composition-evaluator`
- `20260711-pattern-id-composition-recomposer-2`
- `20260711-pattern-id-html-metro`

The first recomposer run produced a correct artifact but failed strict event validation after two brittle ad hoc parsing commands returned tool errors. The skill was simplified with `scripts/check_recomposition_contract.py`; the repeated strict run and independent artifact check passed with eight nodes, nine links, correct base/variant IDs, and no tool errors.

The D3 composition audit also exposed a pre-existing manifest/runtime mismatch: `d3-composition-symmetry-fault-tree` was declared but dropped. Its semantic hierarchy target was restored, and the verifier now requires exact 78/78 manifest parity.

GitHub Pages output was rebuilt locally to 571 files. Remote publication was not performed in this pass.
