# Solid-First Custom Renderer Validation

The final runtime payloads of `d3`, `threejs-animated-3d`,
`procedural-svg-animation`, `svg-brief-design`, and `vectorize-art-patterns`
have **20 passing strict isolated runs**, comprising one contract and three
naturalistic passes per bundle, with independent artifact inspection on
2026-10-03. Every attempt is retained below, including the final D3 agent
failure; this is a passing evidence set, not an assertion that every attempt
passed.
The existing backlog exception uses `openai-codex/gpt-5.6-luna`, high reasoning,
rather than the default Spark model. No commit or push was performed here.

## Policy and Implemented Boundaries

Each bundle consumes its local palette contract. Filled categorical marks use
the complete `solidSequence`, exclude the actual canvas only, and remain
borderless until distinct solid colors are exhausted. Text uses pure black or
white selected by maximum WCAG relative-luminance contrast. Soft palette tokens
come late. Overflow borders use allowed colors with at least 3:1 fill contrast,
cycle border colors before solid/dashed/dotted styles and 1–3 px widths, and
end in direct labels, symbols or split views after the finite alternatives.

D3 now applies this to production builders, custom HTML finalization, starter
templates, logo output, kinetic type, and published SVG cards. It preserves
embedded vendor JavaScript byte-for-byte. The finalizer preserves genuine open
paths, connectors, source artwork, and explicit line-art modes, and handles
SMIL text fills that override CSS. Animated categorical text and paired mark
paint use discrete timing so label paint stays exactly black or white between
keyframes. Ordinary static alpha becomes opaque; explicit semantic overlap,
value/density opacity, hidden states, reveal animation and focus behavior stay
meaningful. Category Burst now omits separate satellite rims, decorative guide
rings and drop shadows while retaining eight relationship spokes and motion.

Three.js uses solid material colors without default decorative edge meshes;
lighting, orbit curves, and other physical or line geometry remain intact.
The offline orbit template allocates all available colors rather than cycling
five materials. Procedural SVG output preserves the numerical solver state,
animation timing, and geometry while normalizing filled shapes and label
contrast, including alpha-composited animated fills. SVG brief scaffolds use
filled nodes, readable text, and genuine arrow/stem geometry. Vectorization
keeps source rights and contour fidelity while delaying soft palette colors.

The vector palette's original `source`, `artSequence`, `backgroundCandidates`,
and `ink` extensions were restored alongside the new common metadata.
The 60 masterpiece derivatives retain their 30 original source/geometry pairs.
The two abstract maps retain every path ID and path-data string; 61 decorative
path outlines were removed, with meaningful axes and coastline geometry kept.

## Final Isolated Cohort

Every run used the runtime profile, excluded acceptance fixtures, disabled
ambient context/extensions/skill discovery, loaded only its copied bundle,
required exact artifact paths, and enforced immutable copied skill resources.
Contract cases also required their exact fenced command. Final runs observed
the requested Luna model, zero tool errors, valid JSON events, and clean read
surfaces. Generated files stayed outside the copied skill tree.

| Bundle | Contract suffix | Naturalistic suffixes | Runtime files | Payload SHA-256 |
| --- | --- | --- | ---: | --- |
| d3 | 14 | 14, 15, 17 | 288 | `b6a4839c0a1aad96da170f698a9861beb898c41b6565119615fda22c43769633` |
| threejs-animated-3d | 2 | 1, 2, 3 | 11 | `5c243bd8b3226eef250da8e6015ce43f8dc8d015ed5071f5f7470d92736e957f` |
| procedural-svg-animation | 11 | 11, 12, 13 | 18 | `ca3352642eff1fe7f0731ca7f7fa330cd10f1c709b881999e2a557d51863103a` |
| svg-brief-design | 2 | 1, 2, 3 | 10 | `374da01c957b98b3b6e9e6fb5db3977a51c9a1561688b057601725f1ea07bfa8` |
| vectorize-art-patterns | 2 | 1, 2, 3 | 55 | `3e81d3098d50729416b17c7377f265fa22415c24257057551c3dccead1d8ec57` |

Run IDs follow `custom-solid-<bundle>-<case>-20261003-luna-<suffix>`.
[results-20261003.json](results-20261003.json) records each exact run command,
prompt hash, output path, observed model, reads, gates, findings, and payload
identity. Reusable prompts are in
[custom-solid-style](../pi-prompts/custom-solid-style/). Raw manifests,
workspaces, events, stderr, and outputs remain under the corresponding ignored
`evaluations/runs/<run-id>/` directories.

The D3 cases cover a production directed workflow; Three.js covers a replayable
18-token scene; procedural SVG covers eight timed states and static fallback;
SVG brief covers equal geometry with maroon and yellow text contrast; vectorize
covers paired palette derivatives with identical source contours. These cases
validate the changed style paths, not every possible prompt or pattern family.

## Retained Failures and Superseded Trials

All **47** attempts remain recorded; 41 passed the strict harness. The initial
five contract attempts ran their correct commands and produced artifacts, but
failed the event gate with `no-fenced-command-in-prompt`: the harness recognizes
the bash fence, while the prompt used a PowerShell fence. These are retained
`harness` failures, with zero tool errors and preserved payloads. Corrected
prompt retries passed; failed trials were never counted as release passes.

Earlier D3 trials use superseded payloads. Gallery review revealed SMIL
label-fill behavior, a stale styling reference, and a kinetic regression test
revealed vendor-byte mutation in the palette adapter. These findings were
fixed before freezing the final payload and rerunning the final cohort.
Earlier D3 outputs pass the independent style checks but their
`vendorRuntimePreserved: false` result remains visible. Only the four final D3
outputs count toward release acceptance; all four preserve the vendor bytes.

Final D3 naturalistic repetitions 14, 15 and 16 pass **2/3**, meeting the
repository's documented naturalistic threshold. Repetition 16 produced the
correct artifacts but failed the strict event gate after the sampled agent
guessed a nonexistent `references/patterns/flow-spine.md`; the actual Flow Spine
recipe is an anchor in `references/recomposition-recipes.md`. This is an
`agent` failure and stays failed in the ledger. Extra fresh repetition 17,
using the same unchanged prompt and payload, passes; final D3 naturalistic
coverage is **3/4**, not a silently replaced failure. Other bundles pass their
three final naturalistic repetitions. Earlier vendor-byte mutations remain
classified as `skill` failures even where their separate style checks passed.

## Deterministic and Published Fixture Evidence

[deterministic-style-check.json](deterministic-style-check.json) checks all
usable solid colors before overflow: 16 colors for colorset1 and 36 for
colorset2 on a white canvas; preserved semantic lines and explicit overflow;
three actual distinct production flow fills; 24 Three.js token objects plus
one hub with 25 distinct palette materials; all 54 palette tokens for SVG
label contrast; and the procedural finalizer.

[gallery-style-check.json](gallery-style-check.json) records 225 rendered D3
cards per palette, 7,498 eligible filled marks per palette, zero decorative
outline violations, only black/white visible labels, and zero page errors.
The vector galleries pass border checks at 1440 px and 390 px; all 5,290
masterpiece filled paths and 61 abstract-map filled paths are borderless.
Screenshots wait two animation frames before capture and were manually reviewed.
The full Three.js fixture passes 24 desktop/mobile scenes, animation, replay,
and pointer drag; the 66 procedural SVG examples were regenerated. Explicit
Category Burst checks cover nine distinct solid nodes, zero separate
`fill="none"` decorative rims or filter overlays, and eight preserved spokes.
Manual screenshots cover the filled marks and surrounding geometry, avoiding
the earlier blind spot where a separate ring looked like a node border.

[alpha-chrome-check.json](alpha-chrome-check.json) records 98 text checks across
both palette family tiles, counts, primary buttons and filled pills; ordinary
alpha, semantic overlap, hidden/reveal, CSS/SMIL animation, focus/blur and six
animated-label midpoint checks. [overflow-boundary-check.json](overflow-boundary-check.json)
checks 13,024 category indices across both palettes and white/dark canvases,
including index 100,000, with exact Python/JavaScript parity, contrast-checked
borders, bounded widths and finite structural fallback.

The independent built Pages review passes 206 source-copy checks, including
documented build transformations and immutable logo vendor bytes, with zero
desktop/mobile layout or paint findings. It checks 645 procedural control/text
entries and 25 Three.js controls against the actual composited background.
See [Pages review](../solid-colorset-style/pages-review-20261003.md).

Commands run successfully for the changed machinery and fixtures:

```powershell
uv run --script skills/d3/scripts/test_colorset_adapter.py
uv run --script skills/d3/scripts/test_speculative_decoding.py
uv run --script skills/d3/assets/examples/skill-tests/test_build_contract_artifact.py
uv run --script skills/d3/assets/examples/skill-tests/test_build_kinetic_type.py
uv run --script skills/d3/assets/examples/skill-tests/test_palette_contract.py
uv run --script skills/svg-brief-design/scripts/test_scaffold.py
uv run --script skills/procedural-svg-animation/scripts/test_multistrata_contracts.py
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --check
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_with_vtracer.py
uv run --script skills/vectorize-art-patterns/scripts/build_example_gallery.py
uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py
uv run --script skills/vectorize-art-patterns/scripts/validate_abstract_world_map_examples.py
uv run --script skills/d3/scripts/build_logo_studio.py --output skills/d3/assets/examples/d3-logo-design/index.html
npm run build --prefix skills/threejs-animated-3d/assets/examples/threejs-animated-3d
npm run verify --prefix skills/threejs-animated-3d/assets/examples/threejs-animated-3d
uv run --script projects/custom-solid-style/scripts/check_custom_styles.py
uv run --script projects/custom-solid-style/scripts/audit_galleries.py
uv run --script projects/custom-solid-style/scripts/check_alpha_and_chrome.py
uv run --script projects/custom-solid-style/scripts/check_overflow_boundaries.py
uv run --script projects/custom-solid-style/scripts/review_built_pages.py
uv run --script projects/custom-solid-style/scripts/review_pi_outputs.py
uv run --script projects/custom-solid-style/scripts/seal_results.py
git diff --check -- skills/d3 skills/threejs-animated-3d skills/procedural-svg-animation skills/svg-brief-design skills/vectorize-art-patterns projects/custom-solid-style
```

The individual test counts are 5 adapter, 12 speculative decoding, 8 production
contract, 6 kinetic type, 7 palette contract, and 15 SVG scaffold tests.
The multistrata check covers 12 strata, 81 transport entries, and five rejected
tampering cases, with a maximum numerical error of `4.857e-17`.
Vector fixture validation confirms 30 source hashes, 30 locked geometry pairs,
28 creators, and inventory hash
`8332fb4ffcadadcd6dcf5f1c0bf92a3f1b17efb17f79d52bbcdeebbb4fba2574`.

Browser evidence uses installed Microsoft Edge through Playwright. Raw
screenshots and generated review data live in the ignored
`projects/custom-solid-style/artifacts/` tree. Common repository validation,
local synchronization, Pages regeneration, and release publication are owned
by the coordinating root task; this record does not claim a remote deployment.
