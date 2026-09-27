Create input.svg from this supplied renderer SVG, then produce output.svg
as a portable animated bar chart. Preserve the geometry and labels and
provide a readable reduced-motion state. Write the bundled pair-validation
report to validation.json.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320"><rect width="400" height="320" fill="white"/><g font-family="sans-serif" font-size="14" fill="#333e48"><path d="M50 40V220H350" fill="none" stroke="#696969"/><rect x="80" y="100" width="40" height="120" fill="#9e1b32"/><rect x="170" y="60" width="40" height="160" fill="#696969"/><text transform="translate(90 252) rotate(-35)" text-anchor="end">Northern station</text><text transform="translate(200 252) rotate(-35)" text-anchor="end">Coastal station</text><text transform="translate(28 148) rotate(-90)" text-anchor="middle">Observations</text></g></svg>
```

Treat skills/echarts-animated-svg/ as read-only. Write all task files in the
current workspace. Use local tools without network access or other repositories.
