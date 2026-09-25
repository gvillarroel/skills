Build a compact connected organic pixel map for exactly 73 fictional people. Use the read-only bundle at skills/hierarchy-lens, keep outputs outside skills/, and do not read acceptance examples or external files/services. The browser runtime is available.

Run this command:

```text
uv run --script skills/hierarchy-lens/scripts/build_explorer.py --demo --demo-size 73 --view organic --cell-pixels 2 --seed 73021 --output deliverables/map.html --data-output deliverables/source.json --report deliverables/build.json
```

Run the browser audit to deliverables/audit.json with overview screenshot deliverables/overview.png. Inspect the result. Every record must occupy exactly four pixels, the root must be small, the body must remain connected, and changing the color dimension must not change the cells. Return the five exact paths and explain the meaning of cell contact and outward progression.
