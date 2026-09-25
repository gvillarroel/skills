---
name: hierarchy-lens
description: Build an offline interactive radial hierarchy whose blocks keep their positions while categorical or numeric color lenses change. Use for large organizational maps, reporting structures, portfolios, or taxonomies that need one overview with branch focus, search, details, and comparable attribute views.
---

# Hierarchy Lens

Create one explorable SVG map inside a self-contained HTML file. Put the root in the center, direct children in the first ring, and subsequent generations outward. Keep geometry independent of the selected color dimension.

## Prepare the data

Read [data-contract.md](references/data-contract.md) to normalize the source into a flat JSON tree and explicit dimension descriptors. Preserve source IDs, missing values, units, and reporting periods. Use a single declared primary parent; a matrix organization needs an agreed primary reporting line rather than duplicated people.

Read [radial-lenses.md](references/radial-lenses.md) for angle semantics, individual versus subtree metrics, density limits, and interaction decisions. If no source data was supplied, clearly identify any demonstration as synthetic. Never infer leadership level from reporting depth unless that is the supplied definition.

## Build

The bundled builder needs only Python through `uv`. Replace `<skill-root>` with this bundle's location. Write task outputs outside the read-only bundle and honor exact requested paths.

```text
uv run --script <skill-root>/scripts/build_explorer.py --input hierarchy.json --output explorer.html --report build-report.json
```

For a fictional organization of N people, use `--demo --demo-size N` unless the user specifies a custom reporting structure. This route already supplies leadership, contract, role, monthly tokens, zero values, and missing observations with an exact record count; do not recalculate synthetic team sizes by hand. Customize the exported JSON only when the request needs different attributes. For example:

```text
uv run --script <skill-root>/scripts/build_explorer.py --demo --demo-size 1200 --output explorer.html --data-output hierarchy.json --report build-report.json
```

`--demo-size` controls the number of synthetic records (default 1200, range 2–20000). Normal authoring reads the compact contract and runs the builder; it does not need template source or acceptance examples. Customize title, description, entity label, dimensions, and source notes through the input. The output embeds data, styles, and runtime without CDNs, telemetry, or external requests.

## Validate

Run the browser audit after the last build. It requires the Python `playwright` package (declared by the script) and an installed Chromium browser. If Chromium is missing, install it with `uv run --with playwright python -m playwright install chromium` when local dependency installation is authorized, or report the browser gate as incomplete.

```text
uv run --script <skill-root>/scripts/audit_explorer.py explorer.html --report audit.json --screenshot overview.png
```

Inspect the screenshot and interact with a meaningful branch and a numeric lens. Check labels at overview and focused sizes, mobile controls, missing-value treatment, global color scales, period/unit wording, and whether the map answers the actual question. Read [validation.md](references/validation.md) when adapting the interaction or evaluating a large or unusual input.

Deliver the HTML and its normalized input. Explain that SVG/PNG downloads capture the current view as a static image; the HTML retains the interactive controls. Report tested size and any incomplete gate without implying unlimited-scale performance. Do not publish private source data without authorization.
