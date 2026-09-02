# Vector logo export contract

Use the provided technical-logo-assets skill. Treat `skills/technical-logo-assets/` as read-only. Stay inside this isolated workspace, do not use the network, and do not inspect examples or other skills.

Export the Python logo as a fixed blue SVG to exactly `deliverable/python-blue.svg`, with its generated provenance and license sidecars. Run exactly these two commands and no exploratory directory listings, help commands, or guessed README reads:

```bash
python -B skills/technical-logo-assets/scripts/export_logo_asset.py --id devicon-python --variant adaptive --color "#007298" --output deliverable/python-blue.svg
python -B skills/technical-logo-assets/scripts/list_logo_assets.py --id aws-compute-lambda --variant adaptive --json > deliverable/lambda-choice.json
```

The second command creates `deliverable/lambda-choice.json` with the exact AWS Lambda adaptive-variant search result. It must explicitly indicate whether that choice is available and why. Do not attempt an unavailable export.

Confirm the exact output paths without traversing the whole SVG library. Do not modify the skill payload or create files inside it.
