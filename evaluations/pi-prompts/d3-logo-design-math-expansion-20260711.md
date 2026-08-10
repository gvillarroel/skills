Use the loaded `d3-logo-design` skill to generate and validate one deterministic standalone logo studio that exercises the new Lorenz-attractor mathematical mechanism.

Work only from this prompt and the loaded skill at `skills/d3/`. Treat the skill directory as read-only. Write only under `outputs/`. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, acceptance examples, hidden context, or the network. Do not install packages or substitute tools.

Immediately after reading this prompt, read `skills/d3/SKILL.md`. There is no skill README: do not probe `README.md`, list directories, or run either script with `--help`. The two exact commands below contain every required argument.

Create these exact deliverables:

- `outputs/lorenz-attractor-logo.html`
- `outputs/lorenz-attractor-evidence.json`

Use brand `CHAOS FIELD`, tagline `Order inside motion`, colorset2, pattern `d3-logo-lorenz-attractor`, texture `d3-logo-topographic-lines`, monospace font, density `1.1`, curvature `0.68`, scale `1`, rotation `0`, texture strength `0.34`, and seed `171`. Preserve the full adjustable catalog of 90 patterns, 10 textures, and 90 finished compositions.

The generated standalone HTML/SVG must retain these stable catalog values exactly:

- pattern ID `d3-logo-lorenz-attractor`
- local example ID `lorenz-attractor`
- composition ID `d3-logo-lorenz-attractor-lockup`
- geometry signature `nonlinear-ode-chaotic-trajectory`

Use only the exact bundled colorset1 and colorset2 tokens. Do not add gradients, arbitrary colors, external fonts, images, scripts, or other network dependencies. Keep the brand and tagline visibly clear; do not hide, clip, or accidentally occlude either text layer, and do not declare an intentional-occlusion exception for this mechanism.

Run these exact commands in order:

```bash
uv run --script skills/d3/scripts/build_logo_studio.py --output outputs/lorenz-attractor-logo.html --brand "CHAOS FIELD" --tagline "Order inside motion" --colorset colorset2 --pattern d3-logo-lorenz-attractor --texture d3-logo-topographic-lines --font monospace --density 1.1 --curvature 0.68 --scale 1 --rotation 0 --texture-strength 0.34 --seed 171
uv run --script skills/d3/scripts/validate_logo_artifact.py outputs/lorenz-attractor-logo.html --expect-patterns 90 --expect-textures 10 --expect-compositions 90 --require-colorset colorset2 --json-report outputs/lorenz-attractor-evidence.json
```

Make the validator write its own JSON report to the exact evidence path; do not hand-author or post-process that report. Read the generated report and fail the task if any required value differs:

- `ok: true`
- `patternCount: 90`
- `textureCount: 10`
- `compositionCount: 90`
- `exampleIdCount: 90`
- `patternSignatureCount: 90`
- `patternRendererCount: 90`
- `initialPattern: "d3-logo-lorenz-attractor"`
- `initialExampleId: "lorenz-attractor"`
- `initialTexture: "d3-logo-topographic-lines"`
- `selectedColorset: "colorset2"`
- `initialSeed: 171`
- `textClearanceContractValid: true`
- `textOcclusionDefault: "prohibited"`
- `standalone: true`

Also verify directly in the generated HTML that the exact composition ID and geometry signature above are present. At the end, report both exact output paths, the observed validator fields, and whether both stable catalog strings were found.
