Build a text-free radial pixel heatmap for exactly 73 fictional people, using the read-only bundle at skills/hierarchy-lens. Keep generated files outside skills/ and do not read acceptance fixtures or external files/services. The browser runtime is available.

Run this command, substituting only the Python/uv invocation if required by the shell:

```text
uv run --script skills/hierarchy-lens/scripts/build_explorer.py --demo --demo-size 73 --view pixel --pixel-grid 128 --output deliverables/map.html --data-output deliverables/source.json --report deliverables/build.json
```

Run the bundled pixel browser audit and write deliverables/audit.json and deliverables/overview.png. Inspect the result. The image and exports must contain no visible labels, every record must own pixels, and color controls must leave the ownership grid unchanged. Return the five exact output paths and any material limitations.
