Use the read-only skill at skills/hierarchy-lens to build a synthetic organization demonstration. Run this exact command:

```sh
uv run --script skills/hierarchy-lens/scripts/build_explorer.py --demo --demo-size 73 --output deliverables/map.html --data-output deliverables/source.json --report deliverables/build.json
```

Then audit deliverables/map.html with the bundled browser auditor and save deliverables/audit.json and deliverables/overview.png. The browser runtime is already available through the environment. All generated files must stay in this workspace, outside skills/. Do not read acceptance examples, unrelated files, or external services. Verify that the build has exactly 73 records and the audit passes. Report the exact output links.
