Use the loaded skill's runtime starter to generate both palette variants. Run
these commands exactly from this workspace:

```bash
uv run --script skills/reflex-xy/assets/templates/chart.py --colorset colorset1 --output-dir results/cs1
uv run --script skills/reflex-xy/assets/templates/chart.py --colorset colorset2 --output-dir results/cs2
```

Required non-empty outputs are `results/cs1/chart.html`, `results/cs1/chart.svg`,
`results/cs1/chart.png`, `results/cs2/chart.html`, `results/cs2/chart.svg`, and
`results/cs2/chart.png`. Inspect at least one native image and check both SVGs
for authored paints outside their selected palettes. Use the bundled browser
verifier to check both HTML files and save its reports as
`results/cs1/browser.json` and `results/cs2/browser.json`, with screenshots
`results/cs1/browser.png` and `results/cs2/browser.png`.

Keep `skills/reflex-xy/` read-only. Write only in this workspace outside `skills/`.
Do not read acceptance examples, sibling skills, parent directories or repository
documentation. Registry access for declared dependencies is allowed; HTML must
render without external network dependencies. Do not publish or deploy anything.
