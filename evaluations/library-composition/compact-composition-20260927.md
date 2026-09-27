# D3 and Three.js compact composition â€” 2026-09-27

## Result

Updated the canonical D3 and Three.js runtime instructions, builders, templates,
and local installations. Both skills default to compact spacing and colorset1
with neutral surfaces/materials and deliberate red emphasis. Pink remains a
documented last-resort category or explicit request; no standard builder assigns
it automatically. Colorset2 and deliberately larger spacing remain available.

The final selected cohort meets every repository threshold. All 16 final
artifacts pass independent desktop/mobile inspection. The strict harness result
is **14/16**. One D3 generalization trial read the skill before the
prompt, violating the harness read-order rule. One Three.js naturalistic trial
produced a valid scene but ended with an unnecessary assertion that the read-only
skill directory should not exist. The other two repetitions in each affected
case passed. Both failures are retained rather than counted as strict passes.

| Skill | Contract | Naturalistic | Boundary | Generalization |
| --- | --- | --- | --- | --- |
| d3 | 1/1 | 3/3 | 1/1 | 2/3 |
| threejs-animated-3d | 1/1 | 2/3 | 1/1 | 3/3 |

## Measured changes

| Fixture | Before | Updated |
| --- | --- | --- |
| D3 flow box | 64 px high | 32 px high, with the same 16 px label |
| D3 flow canvas | 520 px high | 180 px default; explicit height is preserved |
| D3 stage-template box | 132 px high | 100 px high |
| D3 stage-template canvas | 420 px high | 320 px high |
| D3 starter outer padding | 24 px | 12 px |
| Three.js stage at a 390 px viewport | 320 px high | 205.875 px high |
| Three.js replay target | 36 px | 32 px on desktop; 44 px for coarse pointers |

D3 measures text before drawing compact flow boxes, keeps a 32 px minimum node
height, and uses a scrollable native-size diagram on narrow screens. Explicit
18 px node padding and a 960Ã—300 viewBox passed the boundary test. The editable
starters now use bundled offline D3 and select colorset1 by default. Neutral
fills replace automatic soft-red surfaces in the supporting generators.

Three.js uses white ambient/key/rim lights and explicit sRGB output. Camera
distance fits the complete token motion envelope when aspect or orbit changes.
Five and twelve orbiting objects reuse the same roles; the fixture also covers
an explicitly extended palette, comfortable spacing, and a long heading.
Lit pixels are reviewed separately from exact material tokens because shading
changes rendered RGB values. See the official [color-management guide](https://threejs.org/manual/pages/color-management.html)
and [responsive-design guide](https://threejs.org/manual/pages/responsive.html).

## Repairs found during verification

- The D3 stage template animated CSS transforms over its SVG positioning,
  collapsing the boxes at the origin. Its entrance now animates opacity while
  retaining the authored positions, including reduced-motion mode.
- SVG export previously dropped page-defined text and paint styles. It now
  preserves computed font, fill, stroke, and visibility using canonical hex.
  A separate round-trip test proves identical font, paint, stroke, and label width.
- The palette checker misclassified SMIL `fill="freeze"`/`fill="remove"` as named
  colors. It now recognizes animation lifetime only on SMIL elements and still
  rejects invalid rectangle paint and out-of-palette animation targets.
- Isolated traces exposed bare-Python renderer calls, guessed validator classes,
  and inappropriate single-file checks on editable directories. The skill now
  gives the required `uv run --script` command, literal validator syntax, and a
  direct dashboard-builder route with the correct offline-directory checks.

## Validation

- 50 independent browser renders: 42 updated cases and 8 baseline comparisons.
- Five Three.js variants at two viewports, each sampled at 41 animation phases;
  all token bounds remain inside the camera frame.
- 29 existing D3 unit tests, four new SMIL test methods, and the SVG style
  round-trip check passed. All changed Python scripts parsed successfully.
- Both skill-creator metadata checks passed.
- Pattern IDs, repository skill validation, independence, payload checks, and
  all 14 Pi harness tests passed.
- Local sync/check passed for 317 D3 and 17 Three.js canonical source files.

### Commands

```powershell
uv run --script evaluations/library-composition/verify_defaults.py
uv run --script evaluations/library-composition/test_palette_animation.py
uv run --script evaluations/library-composition/test_render_styles.py
uv run --script evaluations/library-composition/run_forward.py --cohort verified --libraries d3
uv run --script evaluations/library-composition/run_forward.py --cohort release --libraries threejs
uv run --script evaluations/library-composition/verify_forward.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

The helper records every full Pi command, exact expected path, result, event
policy, and payload manifest under `evaluations/runs/`. Release uses strict JSON,
runtime-only skill copies, disabled ambient context, and immutable payloads.
The deliberate model exception is `openai-codex/gpt-5.6-luna` at medium thinking:
Spark was rejected as unsupported before its first tool call in the same-session
[Mermaid evaluation](../mermaid/compact-composition-20260927.md). Naturalistic and
generalization cases each use three fresh workspaces, requiring at least two
strict passes. All final artifacts were independently checked, including the
two valid artifacts whose agent traces failed harness protocol checks.

### Final runtime payloads

- `d3`: 282 runtime files; SHA-256 `88e22fb9fa07d710659f94bd113c04f2982bce5be8791d996fee326a44f23f1a`.
- `threejs-animated-3d`: 10 runtime files; SHA-256 `424322c771e98862a8a3e637cdaaf59a4b1247299a3fc558a582166372e6e078`.

## Retained attempts and scope

All 36 completed attempts remain under `evaluations/runs/`. Early
cohorts exposed the invocation, validator-syntax, dashboard-routing, and SMIL
issues above. One command-contract retry passed its artifact checks but failed
the harness's literal-command check because four commands were joined with
`&&`; its prompt was corrected to use separate exact command blocks. Earlier
failures are included in the [machine-readable record](compact-composition-20260927.json).
Existing sealed Harbor studies were not rerun or reinterpreted.

This pass changes runtime resources and uses local review artifacts. Published
acceptance galleries and the Pages catalog were not changed, so no Pages
publication was required. The local [comparison](../../projects/library-composition/artifacts/comparison.html)
includes before/after views and links to interactive examples. Bulky renders,
screenshots, browser measurements, and raw runs remain in ignored artifact paths.
