Use $procedural-svg-animation to create a deterministic standalone animated SVG at the exact path `outputs/kinetic-bloom.svg`.

Requirements:

- Use the canonical `procedural-svg-phyllotaxis-bloom` mechanism.
- Use seed `104729`, dimensions `960 × 600`, duration `7200 ms`, the `colorset2` palette, full motion, and a seamless loop.
- Keep the SVG self-contained with no network dependency or script.
- Include a direct title and description, stable viewBox, meaningful base/final state, reduced-motion fallback, and the skill's root audit metadata.
- Validate the result with the bundled validator and write its JSON report at the exact path `outputs/kinetic-bloom-validation.json`.
- The validation report must pass standalone, motion, expected pattern ID, and expected seed checks.

Treat the copied skill directory as read-only. Do not inspect acceptance examples. Create only the requested output files and any disposable temporary files outside the skill bundle.
