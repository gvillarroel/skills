# Compact parallel chronology

Use `design: editorial`, `mode: timeline`, `layout: compact` for a short comparison with a few lanes and a small number of consecutive or separated phases. Adapt [the data-only template](../assets/templates/compact-timeline.json). A small subject does not require a 2:3 mural: names should be readable while a visitor compares simultaneous phases.

Supply `id`, `title`, `source_note`, `reading_note`, named `groups` with colors, `time: {start,end,step}`, named `lanes`, and `periods`. Each period needs `id`, `label`, `group`, `lane`, numeric `start` and `end`. Dates are numbers, including negative values when appropriate. Choose the scale's step for useful reference lines. State synthetic data when the records are invented.

Omit dimensions, offsets, bar widths, font overrides and custom imprint in the first render. The renderer measures horizontal names beside slim duration ribbons, prints both endpoint years, and fits the shortest interval without distorting time. Each lane retains its source category. Do not add events or inter-period arrows solely to decorate a sparse subject; chronological adjacency alone is not a stated succession relation.

The shared numeric axis determines every top and bottom. Label centers sit within their actual periods; the separate label backplate is not an interval. A longer period remains longer. Branches, concurrent intervals within a lane, many events and complicated transitions usually need the dense authored ribbon route in [the editorial contract](editorial-contract.md).

Run the normal renderer and source-backed browser audit, using the user's exact output paths:

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Open the PNG. Check the shared year alignment, the shortest phase, the longest horizontal name and the balance between colored duration marks and text. If specific dimensions are required, set them after previewing; increasing height is preferable to falsifying a short interval. Optional period `label_width`, `size`, `bar_width` and `offset` tune measured placement. Keep the source's wording and dates.
