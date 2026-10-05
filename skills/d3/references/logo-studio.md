# Logo studio commands

Use this route for a complete offline editable logo studio or browsable logo
catalog. A single extracted logo uses the contract builder instead. Keep the
skill bundle read-only and generate into the caller's requested directory.

After the entry point's mandatory `build_logo_studio.py --help` call, use this
sequence. Replace `skills/d3` with the exact loaded bundle directory, and replace
the example brand, tagline, pattern and output paths with the caller's values.
Keep colorset1 as the default; the studio retains both embedded palette modes.

```bash
uv run --script skills/d3/scripts/build_logo_studio.py --output deliverables/logo.html --brand ATLAS --tagline "Signals in motion" --colorset colorset1 --pattern d3-logo-type-orbit
uv run --script skills/d3/scripts/validate_logo_artifact.py deliverables/logo.html --require-colorset colorset1 --json-report deliverables/validation.json
uv run --script skills/d3/scripts/check_self_contained_html.py deliverables/logo.html
uv run --script skills/d3/scripts/verify_logo_gallery.py deliverables/logo.html --small-only --json-report deliverables/native.json --small-logo-screenshot deliverables/small-logo.png
```

`verify_logo_gallery.py` declares Playwright in its uv metadata. Use
`uv run --script` for this verifier, the texture verifier and the SVG renderer,
including their `--help` calls, so the isolated workspace receives their
dependencies. The studio builder and static validators are dependency-free.

For the requested 96×64 Type Orbit check, `--small-only` verifies the gallery's
settled geometry and text, then captures the actual compact studio mark. It
preserves the declared small-size tagline omission in the accessible
description. Inspect the PNG and the reports' `ok`/`clean`, `findings` and
`smallLogo` fields. A successful process exit alone is insufficient. Read a
short JSON summary rather than loading the complete native report or generated
HTML, both of which can be large.

The static logo validator checks both embedded palette registries. For a
requested full interaction audit, run the native verifier without `--small-only`
to exercise every control, both palette switches and all replay actions. Keep
its reports and screenshots at the requested paths. Other patterns require
their own appropriate native size checks; the Type Orbit compact-lockup check
does not certify all small-size pattern variants.

When an explicit extended-palette paint check is required, export the actual
settled colorset2 SVG with `render_d3_svg.py` and apply
`check_palette_contract.py --colorset colorset2 --require-extended` to that SVG.
The studio HTML contains JavaScript-generated marks and cannot satisfy that
settled-paint gate directly. Keep categorical order separate from numeric tone
ramps and semantic roles. Do not read or substitute the large engine, vendor
runtime or catalog to assemble the studio; use its bundled builder.
