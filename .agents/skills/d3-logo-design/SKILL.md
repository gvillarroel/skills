---
name: d3-logo-design
description: Create, adapt, implement, and validate parametric D3/SVG logo systems using only the bundled colorset1 and colorset2 palettes. Use when Codex needs a wordmark, monogram, seal, circular text logo, animal or organic silhouette mask, responsive brand mark, typographic treatment, texture-filled emblem, texture atlas, logo exploration gallery, or reusable HTML/SVG logo generator with adjustable copy, font stack, geometry, texture, scale, rotation, density, and curvature.
---

# D3 Logo Design

## Core Contract

- Treat this package as one logo-design skin. Do not route normal logo work through the general D3 gallery.
- Use only exact hex tokens declared in `assets/palettes/colorsets.json`. Do not introduce gradients, named colors, RGB/HSL values, sampled colors, or arbitrary user-provided colors.
- Preserve the requested brand text exactly. Keep generated animal and organic shapes generic; never trace or imitate a protected logo, mascot, or campaign asset.
- Build geometry with D3 and SVG. Keep a stable `viewBox`, deterministic data, unique DOM IDs, `<title>`, `<desc>`, and a readable final state.
- Deliver standalone HTML with the bundled D3 7.9.0 runtime; do not add CDN, font, image, or other network dependencies.
- Make variation explicit through parameters instead of one-off coordinate edits: copy, pattern, texture, colorset, font stack, density, curvature, scale, rotation, and texture strength.
- Keep every gallery example traceable: local `exampleId` is the technique slug, global `patternId` is `d3-logo-<exampleId>`, and editorial preset IDs remain separate composition metadata.
- Prohibit text occlusion and omission by default. Declare a narrowly scoped exception only under `references/text-clearance-contract.md`; an intentional occlusion may never exceed a 0.30 ratio.
- Test the mark at small size and in monochrome-like colorset1 before accepting a detailed result.

## Fast Path and Read Discipline

When the request already supplies exact output paths, pattern or texture IDs, colorset, copy, and seed, execute the bundled builder and validator directly. Do not enumerate the skill directory first. Do not preflight or list the output directory: the builder creates the output parent automatically. Do not read `assets/templates/`, `assets/catalog/`, `assets/palettes/`, or Python script source during normal generation; use the scripts as black boxes and call `--help` only when a flag is unclear. Read a catalog or contract reference only when the request leaves that decision open. Inspect implementation files only when maintaining or extending this skill.

## Workflow

1. Freeze the brief: brand text, optional tagline, audience, desired personality, delivery format, and whether the mark should be typographic, symbolic, masked, or a lockup.
2. If the pattern is open-ended, read `references/pattern-catalog.md`, choose one primary pattern and at most one supporting mechanism, and retain its canonical `d3-logo-*` ID in the artifact.
3. If the texture is open-ended, read `references/texture-catalog.md`. Select one of the 40 bundled textures and tune density, curvature, strength, or seed; do not invent an unregistered texture without extending the catalog and validators. When the user asks to compare or inspect textures, build the standalone atlas with `scripts/build_texture_gallery.py` and retain the selected canonical texture ID in the final logo.

```powershell
uv run --script skills/d3-logo-design/scripts/build_texture_gallery.py --output outputs/d3-logo-textures.html
```

4. If the colorset is open-ended, read `references/palette-contract.md`. Choose `colorset1` for restrained red-neutral identity work or `colorset2` only when multiple semantic hues materially improve the concept.
5. Start from the deterministic studio builder unless the user already supplied a codebase. Resolve this skill directory, then run:

```powershell
uv run --script skills/d3-logo-design/scripts/build_logo_studio.py --output outputs/logo-studio.html --brand "Northlight" --tagline "Signal in motion" --colorset colorset1 --pattern d3-logo-type-orbit --texture d3-logo-diagonal-hatch
```

6. Adjust the generated configuration or call `D3LogoDesign.renderLogo(...)` from `assets/templates/logo-engine.js`. Treat `assets/catalog/logo-manifest.json` and `assets/palettes/colorsets.json` as the machine-readable sources of truth; keep the engine registries in exact parity with them.
7. Validate every deliverable. For generated studio HTML, run:

```powershell
uv run --script skills/d3-logo-design/scripts/validate_logo_artifact.py outputs/logo-studio.html --expect-patterns 90 --expect-textures 40 --expect-compositions 90 --require-colorset colorset1
```

For a generated texture atlas, run both gates:

```powershell
uv run --script skills/d3-logo-design/scripts/validate_texture_gallery.py outputs/d3-logo-textures.html
uv run --script skills/d3-logo-design/scripts/verify_logo_texture_gallery.py outputs/d3-logo-textures.html --viewport 1440x1100 --json-report outputs/d3-logo-textures-browser.json
```

8. For browser-visible or published work, run the Playwright verifier, inspect desktop and mobile screenshots, and correct clipping, illegible type, collisions, weak negative space, or palette leakage before delivery.

## Selection Rules

- Prefer circular text, concentric seals, or banner lockups for institutional and heritage cues.
- Prefer wave, spiral, echo, offset, split, or stacked wordmarks for expressive campaign identities.
- Prefer silhouette masks, contour fauna, wing symmetry, or leaf-animal fusion for nature and animal cues without copying a specific mascot.
- Prefer modular grids, ribbons, cubes, hexagons, mosaics, halftones, contours, or Voronoi cells for technical and generative identities.
- Use texture as secondary evidence. If texture obscures the name at 96 px wide, reduce its strength or remove it.
- Do not combine two high-complexity patterns. Preserve one dominant silhouette and one clear reading path.

## Progressive Disclosure

- `references/pattern-catalog.md`: read when selecting or adapting one of the 90 typographic, generative, perceptual, and mathematical mechanisms.
- `references/mathematical-patterns.md`: read when the pattern catalog routes a request to a mathematical construction, dynamical system, topology, or optimization mechanism.
- `references/texture-catalog.md`: read when choosing and tuning one of the 40 palette-safe SVG textures or when a user names a canonical texture ID.
- `references/palette-contract.md`: read before any palette, paint, opacity, or colorset decision.
- `references/composition-contract.md`: read when building a gallery, a responsive lockup system, or a new finished composition.
- `references/text-clearance-contract.md`: read before intentionally occluding or omitting any brand, tagline, wordmark, monogram, or initials.
- `references/research-foundations.md`: read when explaining why text paths, masks, D3 shape generators, and dynamic identity parameters are appropriate.

## Maintenance

When changing the engine, bundled D3 runtime, catalogs, example galleries, or palette rules, keep the runtime license, pattern, texture, and composition inventories synchronized. Run the logo and texture artifact validators, both browser gallery verifiers at desktop and mobile sizes, the Pages build, the repository validators, and an isolated `pi` forward test before marking the skill done.
