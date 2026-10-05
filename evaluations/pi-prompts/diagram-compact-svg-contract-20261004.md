Create the normal default editable flow SVG with Input, Process and Output and arrows joining consecutive stages. Preserve readable labels and visible directions. Execute this exact scaffold command:

```bash
python skills/svg-brief-design/scripts/scaffold.py init flow --recipe artifacts/design.json --output artifacts/process.svg
```

Render artifacts/process.svg with the bundled renderer into artifacts/preview.png and inspect it. Deliver all three exact files. Keep skills/svg-brief-design read-only, write generated files in this workspace outside skills/, and do not browse the network or discover other skills.
