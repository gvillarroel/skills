---
name: hierarchy-lens
description: Build offline interactive radial hierarchies, including text-free pixel-art heatmaps, with fixed geometry and switchable categorical or numeric color lenses. Use for organizational maps, reporting structures, portfolios, or taxonomies that need one visual object with multiple attribute views, branch exploration, and exact record lookup.
---

# Hierarchy Lens

Create one explorable radial image inside a self-contained HTML file. Put the root in the center, direct children in the first ring, and subsequent generations outward. Keep geometry independent of the selected color dimension.

## Choose the visual language

For pixel art, a radial heatmap, a text-free procedural data image, or an image whose color patterns reveal attributes, use `--view pixel`. Read [radial-pixels.md](references/radial-pixels.md). Build square pixels directly from the hierarchy, keep every record represented, and place controls and the visual key outside the image. Use the hide-controls mode for an image-only view. Do not add names, legends, connectors, decorative noise, or glow inside this image.

For a conventional labeled radial chart, use `--view analytical` (the builder default). Read [radial-lenses.md](references/radial-lenses.md) for labels, ring limits, and rebased branch focus. Both views share the same input contract; honor an explicit choice of style.

## Prepare the data

Read [data-contract.md](references/data-contract.md) to normalize the source into a flat JSON tree and explicit dimension descriptors. Preserve source IDs, missing values, units, and reporting periods. Use a single declared primary parent; a matrix organization needs an agreed primary reporting line rather than duplicated people.

If no source data was supplied, clearly identify any demonstration as synthetic outside the image. Never infer leadership level from reporting depth unless that is the supplied definition. Keep individual metrics distinct from observed subtree sums.

## Build

The bundled builder needs only Python through `uv`. Replace `<skill-root>` with this bundle's location. Write task outputs outside the read-only bundle and honor exact requested paths.

```text
uv run --script <skill-root>/scripts/build_explorer.py --input hierarchy.json --view pixel --output explorer.html --report build-report.json
```

For a fictional organization of N people, use `--demo --demo-size N` unless the user specifies a custom reporting structure. This route already supplies leadership, contract, role, monthly tokens, zero values, and missing observations with an exact record count; do not recalculate synthetic team sizes by hand. Customize the exported JSON only when the request needs different attributes. For example:

```text
uv run --script <skill-root>/scripts/build_explorer.py --demo --demo-size 1200 --view pixel --output explorer.html --data-output hierarchy.json --report build-report.json
```

`--demo-size` controls the number of synthetic records (default 1200, range 2–20000). Normal authoring reads the compact contract and runs the builder; it does not need template source or acceptance examples. Customize title, description, entity label, dimensions, and source notes through the input. The output embeds data, styles, and runtime without CDNs, telemetry, or external requests.

## Validate

Run the browser audit after the last build. It requires the Python `playwright` package (declared by the script) and an installed Chromium browser. If Chromium is missing, install it with `uv run --with playwright python -m playwright install chromium` when local dependency installation is authorized, or report the browser gate as incomplete.

```text
uv run --script <skill-root>/scripts/audit_pixels.py explorer.html --report audit.json --screenshot overview.png
```

Use `audit_explorer.py` instead for the analytical view. Inspect the screenshot and interact with a meaningful branch and a numeric lens. For pixels, verify hard square edges, a text-free image, stable regions across lenses, and recognizable color patterns. Check mobile controls, missing-value treatment, global scales, period/unit wording in the external key, and whether the map answers the actual question. Read [validation.md](references/validation.md) when adapting the interaction or evaluating a large or unusual input.

Deliver the HTML and its normalized input. Pixel SVG/PNG downloads capture the complete map with the active colors and highlighting, without visible text; SVG also keeps the source and metric context in hidden metadata. Analytical downloads include the current chart and legend. HTML retains interaction. Report tested size and any incomplete gate without implying unlimited-scale performance. Do not publish private source data without authorization.
