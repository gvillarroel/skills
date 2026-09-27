Build the bundled standalone logo studio for ASTER with tagline Field notes.
Execute this exact command from the workspace root:

```bash
uv run --script skills/d3/scripts/build_logo_studio.py --output studio.html --brand ASTER --tagline "Field notes"
```

Keep its live controls and catalog available. Treat skills/d3/ as read-only.
Also export its settled live SVG to settled.svg in the current workspace.
Keep browser verification exports at this path, including temporary checks.
Write outputs in the current workspace. Use local tools without network access
or other repositories. Validate the required output before finishing.
