# Colorset1 grayscale interleave validation

Date: 2026-10-05. Baseline: `daaee75353c63ed6dde204d57cfdbae6b9936586`.

## Change and coverage

Primary red remains first. The twelve neutral tokens are sorted by relative
luminance, split into equal dark/light halves, and interleaved. White and the
remaining red/pink tokens retain their suffix priority. The central definition
and thirty self-contained skill copies agree. Exact allowed tokens, named
roles, text-on-fill choices and the entire Colorset2 definition are unchanged.
Canvas filtering follows the fixed sequence. Ordered numeric ramps and source
artwork retain their separate mappings.

The neutral sequence is `#000000`, `#828282`, `#1c1c1c`, `#9c9c9c`, `#363636`,
`#b5b5b5`, `#333e48`, `#cfcfcf`, `#4f4f4f`, `#e7e7e7`, `#696969`, `#f7f7f7`.
Minimum adjacent neutral CIE lightness separation increases from 7.988 to
41.744; revised gaps range from 41.744 to 58.042. This is a scalar D65-relative
sRGB lightness comparison, not full color distance or accessibility certification.
The formula follows [W3C CSS Color 4](https://www.w3.org/TR/css-color-4/#color-conversion-code).
Filtered spatial neighbors, pale gray next to white, connectors and text still
need their own readability checks.

## Isolated forward evidence

The [frozen protocol](protocol.md), [complete results](results.json) and
[independent review](reviewer-notes.md) define the narrow palette-key scope.
All thirty owners have a current-source exact-command contract and one complete
three-run natural cohort with at least two joint strict/native passes.
There are 317 retained reviewed attempts: 314 pass raw strict
gates and 205 pass all current-source and artifact gates. Older payloads and
genuine agent/artifact failures remain unaccepted. No successful repetitions are mixed across
cohorts.

The original seventeen-category cases additionally tested manual first-overflow
styling. Several failed border contrast, suffix indexing or label geometry.
The new thirteen-category prefix family directly exercises primary red plus
all twelve changed neutral positions. Its complete-label, actual-paint,
opacity, contrast, overlap, canvas and ordered-quantitative-legend checks are
unchanged. Full seventeen-token contracts and owning native capacity tests
separately protect white, remaining colors, canvas filtering and overflow.
These scoped results do not establish reliable unconstrained manual overflow
styling or recertify every media retrieval/conversion workflow.

The validator's initial string-only canvas check was an overconstraint: the
prompts leave that metadata field's type open. The explicit uniform repair
accepts an unambiguous white declaration in a string or object, while keeping
actual native white-backing and all visual gates. Original reports remain
separate. Earlier diagnostic capture passes reused screenshot filenames;
final captures are separated by review version. The immutable raw artifacts,
strict results and prior JSON reviews remain retained. Final supplemental
checks cover exact quantitative indexes, positive in-stage swatch geometry
and label association. A second contract overconstraint compared complete owner
definitions with the shorter central definition, rejecting the vectorization
bundle's preserved artwork extensions. The uniform repair requires an exact
export of the copied owner's full definition and equality of every central
canonical field; missing canonical fields still fail. Baseline comparisons
independently preserve all owner extensions. The protocol and independent review record all repairs
and binding hashes; no model cohort is rerun for a schema-only correction.

The fresh Spark availability probe failed before tools because the ChatGPT
account does not support `gpt-5.3-codex-spark`. The recorded scoped model
exception is `openai-codex/gpt-5.6-luna`. Runs use `pi --mode json --strict`,
exact expected paths, prompt-first/event/read-surface gates and immutable
runtime-only copies under `evaluations/runs/`. The collector binds raw gates,
prompt hashes, output hashes, native observations and every normalized source
filename/byte. `bind_release_payload.py` independently binds those inventories
to staged and committed Git blobs.
The release binder reads immutable Git objects in one batch. For the unchanged
Vue template, it additionally proves Git LF bytes equal the validated CRLF
checkout after only newline conversion, recording both hashes. That format was
absent from the original runtime normalizer; all other bytes and filenames
remain exact under the recorded profile.

| Skill | Natural cohort | Joint passes | Runtime files | Normalized runtime SHA-256 |
| --- | --- | --- | --- | --- |
| ambientcg-material-search | r4 | 3/3 | 8 | `f64f11b22205ff0d6eb13e6f6ca01ec63c4d2cdf052b206b1639bed25a2e5eed` |
| animated-svg-to-gif | r4 | 3/3 | 7 | `eaf23598775c95ecbbc071ea55a9c97884171dbd74e66bb2830cb8a6df20616f` |
| asciinema-real-command-video | r4 | 3/3 | 21 | `cf1cedf02dfd34b2966cfed4d2fd0553c512dc3994501285e36fbcbc6061b4d9` |
| compose-synchronized-svg | r4 | 3/3 | 40 | `81aa151c9d3a4ec31b0d1ff7b21526456036a18e708bc4027d54c7c5f6f77a6a` |
| d3 | r4 | 2/3 | 296 | `fcda782e17888101f4f5d7ba8dcbad2f74c0e50cb80e5e4c53f87746659783a4` |
| destockd-video-search | r4 | 3/3 | 7 | `06550ba57ff36ab655c41d54cda0c61d4b32c0afb28bea03d88ca4d857f8a705` |
| diagram-composition | r4 | 2/3 | 27 | `dc1147c95b4611331247619c4895d08f79d7c9025c46b1450a69fadfeea66109` |
| echarts-animated-svg | r4 | 3/3 | 26 | `14b58e14e22d97f405541f73719f689fce020267bb99274253ce2ffc0150749e` |
| harbor-author-evaluation-datasets | r4 | 3/3 | 11 | `1187823b28295478e01bfbe485525838f58950ce8f76db74b18be3883b003747` |
| hierarchy-lens | r4 | 3/3 | 23 | `05bcf291cd7fdfb25f0263c778c297a27bba9356446405f3442d718160eddbb4` |
| hyperframes-explainer | r4 | 3/3 | 33 | `949096ac70bcfcaf000fe6688298493985425bd5147ead3859ca19b799f2a325` |
| iconify-icon-search | r4 | 2/3 | 8 | `b6d2b8b8acbb7e68ccbc41d0658b91370576caceb97377d8d70c3f91c7cef70e` |
| kenney-asset-search | r4 | 3/3 | 8 | `b30c5c1dadbc6d014149b5a59633184cf56862f5b3dd2714f4fb1c1c5597762f` |
| manim-svg-video | r4 | 3/3 | 13 | `e29027d937f5a84d01fcafaa8f41815c32854504c5a4b858c680c499f61f3ed1` |
| mermaid | r4 | 3/3 | 27 | `ce25cb594ca0218f548b4b89364e16165d9fbc252e1f6b9ddc55bcea000cdd7c` |
| one-bit-dither-svg | r4 | 3/3 | 12 | `b2f5fae557e6d777d4149355e5e5088af92a42caf2c6edc4b37ef206f8824161` |
| pexels-media-search | r4 | 3/3 | 8 | `4cef89b365b9b0e08ea35f76f44c3bde8e33f4bc80a0e33d658dd4031c9d0077` |
| pixel-art-image-video | r4 | 3/3 | 9 | `9171046798f2f7f93efd35b1a8af6aba7a45912d2722f5b1b3df58bc19dacebf` |
| plantuml-colorset-renderer | r4 | 3/3 | 28 | `649851e91b8484a304f96fa7569b35f0efc54d1a1ef518a55ca000670ed2409f` |
| polyhaven-asset-search | r4 | 3/3 | 8 | `95c8711d512014578e485279369132560e2e0d9285d89d0d4be1368428f039e7` |
| procedural-svg-animation | r4 | 3/3 | 22 | `76bcd5b3a95e0b69462bbc34d739679b0484d99017aa48140822529dc8e22a5b` |
| slidev-animejs | r4 | 3/3 | 42 | `ff5d6bd3d94550a31ae8413264cd7a4734fb0bd6efd8613e99b058f0f0cbd7dc` |
| slidev-echarts | r4 | 3/3 | 46 | `4a39db7e4160a48fb887e3401b2fb072f87360fe750b1094805fb5921cd419a9` |
| slidev-quality-audit | r4 | 3/3 | 10 | `d0ee69f5d6ba86e5388c6205dece51ca2040ed15f7e51dc42df6e41ea7ee781d` |
| svg-brief-design | r4 | 3/3 | 10 | `a04e291efc7dbd318170c8dee17692b2f7523de73ddd1fa451116b04a840a49d` |
| technical-logo-assets | r4 | 3/3 | 8572 | `79012535bf1f68fb798991b37cfe5471f95535a9f6ea546505ba15bdf760c1e6` |
| threejs-animated-3d | r4 | 3/3 | 11 | `37f2264f2c7b67baf5e774e912473654a3042a94fc7bcc7cf6e5451ad0997faa` |
| usefulcharts-style | r4 | 2/3 | 140 | `ec071cc2ea7bc4071c49564387b949c65228b85811d2cc974acdc5e2dd22bcf8` |
| vectorize-art-patterns | r4 | 3/3 | 55 | `e5d294acced11c2aae21353669121fe622f7d708874b3fcc949cadff18912bff` |
| video | r4 | 3/3 | 60 | `8851821a56c0a8b4f592ec7e94ba3976f8853da6ce316392aee6033702af984a` |

## Native renderers and publication

Native evidence is summarized in [SVG-family validation](svg-native-summary.md),
[renderer validation](renderer-native-summary.md), and the separate
[primary-logo assessment](primary-logo-validation.md). Actual automatic
allocators and embedded registries were tested beyond JSON equality. Native
checks cover both palettes, finite capacity/canvas boundaries, visible text,
motion/replay, export states and protected numeric mappings where applicable.

The vectorization fixtures retain their source geometry and paint byte-for-byte
after removing refreshed metadata. Procedural fixture geometry is unchanged;
two text-ink switch times adjust to the changed substrate luminance. The
inference composition fixture needed a narrow slot/route correction before
its new native audit passed. Mermaid C4 retains its qualified baseline source
and outputs after an attempted regeneration reduced readability; its existing
caption contact is recorded in the renderer note. No universal claim that
every historical gallery is free of layout defects is made.

The two pre-existing ECharts gallery drafts are preserved outside the commit.
The isolated committed gallery candidate changed only a non-drawing timestamp;
its qualified Colorset2 baseline is retained. Historical evaluations remain
unchanged. Source publication uses explicit owned paths, the Pages build,
exact-commit deployment workflow, and committed-builder byte verification.

The [publication record](publication.md) binds the successful source deployment
to its exact commit, workflow artifact and served resources. The documentation
follow-up preserves the same accepted skill payloads.

Required repository gates passed: `validate-pattern-ids.py`,
`validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`,
`validate-colorsets.py` (34 skills, 30 copies, 672 artifacts, no findings),
`test-colorsets.py` (19 tests), and `test-pages-output.py` (3 tests).
`build-pages.py` and local skill synchronization/check also passed. Runtime
behavior commands are retained in the owning summaries and run manifests.

The scoped revision restores each owner's previous backlog state, preserving
broader pre-existing `validating` states instead of claiming those independent
capabilities are newly done.
