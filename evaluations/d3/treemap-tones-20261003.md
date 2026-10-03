# Borderless treemap tones and semantic set transparency

## Scope and result

The reported `d3-treemap-cs1` card painted each parent and all three children with the same opaque branch color. Its three-unit padding exposed that same parent fill after decorative strokes were removed. The children consequently disappeared into three large branch blocks.

The shared renderer now keeps the existing data and D3 layout, paints a neutral parent body with a separate original-color header, and assigns each sibling a stable dark-to-bright solid family token. The CS1 red and gray families, CS2 blue/orange/green families, IDs, values, ordering and animation are preserved. Labels use maximum-contrast exact black or white. No palette tokens, gradients or decorative borders were added.

The same compact renderer and a finite-ramp contract were promoted to `skills/d3/references/patterns/treemap.md`; the skill entrypoint routes treemap sibling visibility there. Beyond three siblings, the finite ramp quantizes and neutral gutters/direct labels continue to separate cells; unique color for every arbitrarily large sibling set is not claimed.

The subsequent `d3-task-overlap-dense-cs1` request adds an explicit semantic transparency exception. The nine scope circles now use their existing saturated tokens at 0.28 fill opacity, declare `data-opacity-role="semantic"`, and omit decorative outlines. The 100 task dots and external label faces remain opaque. All task data, memberships, geometry and leader endpoints are preserved. The compact dense-overlap recipe now describes the same behavior and generates its standalone input through the bundled layout script with an explicit output path outside the read-only skill.

## Independent rendered acceptance

[Machine-readable visual evidence](treemap-tones-visual-20261003.json) records a retained failing baseline and 36 passing final states across the CS1, CS2 and base galleries: desktop/mobile, normal/reduced motion, initial settled state and two replays. All 432 node geometry, value and relationship comparisons match the baseline. All nine sibling gutters are white and three SVG units wide, all faces remain opaque and borderless, and all twelve direct labels stay within their cells. Minimum label contrast is 4.7037:1 in CS1 and 4.5870:1 in CS2/base. Eight native DOM negative controls reject identical sibling paint, wrong label contrast, borders and changed cell geometry. Screenshots received direct visual review.

Bulky captures and the frozen baseline remain under the ignored `projects/treemap-tones/artifacts/`. The versioned project scripts reproduce the independent paint, geometry and negative-control checks.

[Dense-overlap visual evidence](task-overlap-transparency-visual-20261003.json) records twelve passing native CS1 states, four helper-export deliveries, four production-renderer SVG deliveries, a CS2 smoke case and five rejected negative controls. Single-, double- and triple-region pixels match actual source-over compositing within 0.746 RGB channel units; every tested label uses maximum-contrast black or white, with minimum contrast 11.9083:1. All 1,308 task, region, membership and leader geometry/data records match the baseline. A twelve-state CS1 treemap regression also passes on the combined renderer, whose treemap function is byte-identical to the previously accepted version. The report distinguishes existing fixture layout limitations from the corrected opacity behavior and retains the corrected scanner/export-tool attempts.

[Standalone builder acceptance](treemap-builder-local-20261003.md) records five passing focused tests, 96 HTML states, four production SVG states and eight independently graded prompt-data HTML/SVG states. Changed data, one/two/four-child boundaries, tiny cells, literal-name safety, both palettes, narrow layout, Replay twice and reduced motion are covered. The builder uses D3 dice for new branch columns and slice for weighted leaf rows, preserving sufficient label width; this new-data layout is separate from the unchanged geometry of the published gallery. It automatically applies the existing colorset adapter. Root independently reviewed its desktop and narrow screenshots.

## Repository and fixture checks

The following checks passed against the changed source:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script skills/d3/assets/examples/skill-tests/test_palette_contract.py
uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/extract_gallery_pattern_references.py --check-only --expected 225
uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/verify_d3_gallery.py skills/d3/assets/examples/d3-animated-svg/index.html --expected 225 --replay-all --screenshot projects/treemap-tones/artifacts/screenshots/gallery-desktop.png --wait-ms 2200
uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/verify_d3_gallery.py skills/d3/assets/examples/d3-animated-svg/index.html --expected 225 --viewport 390x900 --screenshot projects/treemap-tones/artifacts/screenshots/gallery-mobile.png --wait-ms 2200
uv run --script skills/d3/assets/examples/d3-animated-svg-cs1/scripts/verify_style_gallery.py --expected 225 --json-report projects/treemap-tones/artifacts/data/cs1-gallery.json
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/sync-local-skills.py
```

The fixture verifies 225 cards and all 225 Replay controls; the CS1 style check reports zero off-palette paint. Palette unit checks pass 7/7; harness tests pass 17/17; colorset tests pass 15/15; pattern IDs remain 1,222. Pages builds 648 files and validates fourteen catalog entries. The checks were repeated on the combined treemap and overlap source; the palette and harness unit results remain applicable because those helpers were unchanged. The changed D3 bundle is synchronized into the local installation. The skill-creator quick check passes with `uv run --with pyyaml python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/d3`; its first bare runner lacked the external PyYAML dependency, which was corrected without modifying the tool or skill.

## Isolated acceptance and publication

The release uses the existing recorded `openai-codex/gpt-5.6-luna` exception, strict JSON runtime payloads and independent HTML/SVG grading. One treemap contract case, three fresh naturalistic repetitions and a dense-overlap contract case are required; every failed attempt is retained. The second combined freeze had 288 files and SHA-256 `fd964189150e248e286954dc1b3019473980a2c47c2efe178a4d891241d39195`; it is superseded by the deterministic-builder route after repeated omissions of mandatory finalization. The [isolated record](treemap-tones-isolated-20261003.md) retains all five earlier attempts and distinguishes a successful diagnostic normalized copy from a real Pi pass. The final frozen builder runtime has 289 files and SHA-256 `869500828be9b356d53b9603c2aac23597f24562832e9fc77c758bdbf42de869`; the final cohort is running. Final cases use medium thinking; no comparison with the superseded high-thinking attempts is claimed. The skill remains `validating` while those checks run.

Publish the shared source and its references through the normal main-branch Pages workflow. Require a successful deployment bound to the pushed commit and exact public shared-renderer bytes before handoff. The unchanged public item URLs are [d3-treemap-cs1](https://gvillarroel.github.io/skills/examples/d3-animated-svg-cs1/#d3-treemap-cs1) and [d3-task-overlap-dense-cs1](https://gvillarroel.github.io/skills/examples/d3-animated-svg-cs1/#d3-task-overlap-dense-cs1); published visual acceptance and byte proof are retained under the project artifacts.
