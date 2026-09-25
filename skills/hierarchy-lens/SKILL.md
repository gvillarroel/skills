---
name: hierarchy-lens
description: Build offline interactive hierarchies with decision-driven pixel composition, compact organic cells, radial heatmaps, or labeled charts. Use for organizational maps, portfolios, or taxonomies needing explicit placement priorities, proximity rules, step-by-step growth, switchable color lenses, and exact record lookup.
---

# Hierarchy Lens

Create one explorable hierarchy image inside a self-contained HTML file. Put the root in the center and organize generations outward. Keep geometry independent of the selected color dimension.

## Choose the visual language

For a composition engine that decides which record enters next and which vacancy it occupies, use `--view decision`. Read [decision-growth.md](references/decision-growth.md). Define placement priority separately from spatial affinity and color. Expose editable rules, weighted explanations, and replay of actual placements. Recompose when the policy changes; switching color lenses preserves the current composition.

For a compact organic or slime-like body, a tiny center, equal small cells, or requests to eliminate thick bands and needle-like regions, use `--view organic`. Read [organic-pixels.md](references/organic-pixels.md). Each record occupies one square of `--cell-pixels 2` by default; generations consume successive positions on a connected growth front. Keep the image compact instead of stretching it to fill the screen. Explain that growth order represents depth, while physical adjacency is packing rather than a reporting edge.

For pixel art, a radial heatmap, a text-free procedural data image, or an image whose color patterns reveal attributes, use `--view pixel`. Read [radial-pixels.md](references/radial-pixels.md). Build square pixels directly from the hierarchy, keep every record represented, and place controls and the visual key outside the image. Use the hide-controls mode for an image-only view. Do not add names, legends, connectors, decorative noise, or glow inside this image.

For a conventional labeled radial chart, use `--view analytical` (the builder default). Read [radial-lenses.md](references/radial-lenses.md) for labels, ring limits, and rebased branch focus. All views share the same input contract; honor an explicit choice of style.

## Prepare the data

Read [data-contract.md](references/data-contract.md) to normalize the source into a flat JSON tree and explicit dimension descriptors. Preserve source IDs, missing values, units, and reporting periods. Use a single declared primary parent; a matrix organization needs an agreed primary reporting line rather than duplicated people.

If no source data was supplied, clearly identify any demonstration as synthetic outside the image. Never infer leadership level from reporting depth unless that is the supplied definition. Keep individual metrics distinct from observed subtree sums.

## Build

The bundled builder uses Python through `uv`; decision mode also uses Node.js to execute the same engine embedded in the offline HTML. Replace `<skill-root>` with this bundle's location. Write task outputs outside the read-only bundle and honor exact requested paths.

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

Use `audit_decisions.py` for decision mode, `audit_pixels.py` for organic mode, and `audit_explorer.py` for the analytical view. For decisions, verify priority eligibility, parent precedence, editable weights, exact playback prefixes, exported traces, and deterministic restore. Parent-ready mode intentionally relaxes generation order. Inspect the screenshot and interact with a meaningful branch and a numeric lens. For organic cells, verify equal small squares, a small root, one connected body, connected generation prefixes, and the native-size export. For all pixels, verify hard edges, a text-free image, stable regions across lenses, and recognizable color patterns. Check mobile controls, missing-value treatment, global scales, period/unit wording in the external key, and whether the map answers the actual question. Read [validation.md](references/validation.md) when adapting the interaction or evaluating a large or unusual input.

Deliver the HTML and its normalized input, including its explicit composition policy when used. Pixel SVG/PNG downloads capture active colors and highlighting without visible text; decision mode captures the current replay prefix. Organic exports retain the native small grid. Decision SVG additionally keeps the policy, complete trace, and visible record count. SVG keeps the source and metric context in hidden metadata. Analytical downloads include the current chart and legend. HTML retains interaction. Report tested size and any incomplete gate without implying unlimited-scale performance. Do not publish private source data without authorization.
