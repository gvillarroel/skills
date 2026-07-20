Use the procedural-svg-animation skill to build one deterministic, standalone SVG that demonstrates a deeply layered numerical technique.

Requirements:

- Build `procedural-svg-optimal-transport` with the bundled generator.
- Create `pattern-config.json` in the workspace root with seed `32452843`, width `960`, height `640`, duration `7200` ms, palette `colorset2`, full motion, loop enabled, and these non-default typed parameters: `site_count=10`, `epsilon=0.1`, `minimum_iterations=100`, `frame_count=7`.
- Generate the exact output path `artifacts/optimal-transport.svg` by using `--config pattern-config.json`.
- Validate it as standalone full motion and write the exact report path by running this command verbatim (do not invent extra expectation flags):

  `uv run --script skills/procedural-svg-animation/scripts/validate_procedural_svg.py artifacts/optimal-transport.svg --require-motion --require-standalone --expect-pattern-id procedural-svg-optimal-transport --expect-seed 32452843 --expect-palette colorset2 --expect-motion full --report artifacts/optimal-transport-validation.json`
- Do not read acceptance examples or files outside the copied skill bundle.
- Before finishing, inspect the validation report with the read tool and confirm that all five numerical invariants pass—including row and column marginals, mass conservation, `u/K/v` scaling reconstruction, and zero negative plan entries—six ordered strata are present, diagnostics and state hashes are valid, and the SVG contains a reduced-motion fallback. The validator report is authoritative; do not create ad hoc parsing scripts.

Do not substitute output paths. Leave both requested artifacts in place.
