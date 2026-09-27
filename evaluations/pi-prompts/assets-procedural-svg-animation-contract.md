Build the complete procedural SVG catalog by executing this exact command:

Run the fenced command as its own shell call, separate from validation.

```bash
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --output-dir gallery
```

Validate the complete output with this exact command in a separate shell call:

```bash
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --output-dir gallery --check
```

Verify gallery/index.html, gallery/gallery.css and gallery/manifest.json exist.
Treat skills/procedural-svg-animation/ as
read-only. Write all task files in the current workspace. Use local tools
without network access or other repositories.
