Animate an already-rendered Apache ECharts-style SVG.

Requirements:

- Use the `echarts-animated-svg` skill.
- Work only from the copied skill and the prompt. Do not look outside the workspace.
- Create exactly `bar.static.svg` as a small inline SVG that resembles an ECharts SVGRenderer bar chart: include a title, two axes, three category labels, three bar rectangles, and value labels. You may copy from `skills/echarts-animated-svg/assets/templates/static-bar-chart.svg` if useful.
- Use the skill script to create exactly `bar.animated.svg` from `bar.static.svg` with `--chart-type bar`, `--duration-ms 800`, and `--stagger-ms 90`.
- Verify that the exact file `bar.animated.svg` exists, preserves the original chart labels and bar geometry, includes animation CSS or animation attributes, and contains no external network references.
- Keep outputs in the workspace root. Do not write generated task files inside `skills/echarts-animated-svg/`.
- At the end, print a concise summary of files created and validation checks.
