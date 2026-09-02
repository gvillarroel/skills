# D3 kinetic type contract smoke

Use the provided `d3` skill bundle to create the exact file
`outputs/kinetic-type.html` in this isolated workspace.

The copied `skills/d3/` directory is read-only. Write generated files only under
`outputs/`. Do not inspect repository-level files, sibling skills,
`assets/examples/`, prior evaluation runs, or the network.

The page must use pattern ID `d3-kinetic-glyph-mosaic`, colorset1, energetic
motion, seed `104729`, and this exact ordered text-to-material mapping:

1. `TRACE` — `tiles`
2. `SIGNAL` — `lines`
3. `SYSTEM` — `dots`
4. `REVEAL` — `hybrid`

Use the bundled deterministic builder by running this exact command from the
isolated workspace root after reading this prompt and the relevant skill
instructions:

```bash
python skills/d3/scripts/build_kinetic_type.py outputs/kinetic-type.html --text "TRACE" --variant tiles --text "SIGNAL" --variant lines --text "SYSTEM" --variant dots --text "REVEAL" --variant hybrid --motion energetic --colorset colorset1 --seed 104729 --title "Signals reveal their structure"
```

Then run the bundled self-contained and colorset1 checks against the generated
HTML. The final page must be deterministic and offline, preserve all four words
and their order, expose the requested pattern/color/motion/seed metadata, embed
the bundled D3 runtime, support pointer/keyboard/press activation, and retain a
reduced-motion fallback. Do not modify the copied skill payload.
