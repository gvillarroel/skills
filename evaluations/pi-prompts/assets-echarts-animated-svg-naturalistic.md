Create input.svg from this supplied renderer SVG, then produce output.svg
as a portable animated scatter chart. Preserve the geometry and labels and
provide a readable reduced-motion state. Write the bundled pair-validation
report to validation.json.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320"><rect width="400" height="320" fill="white"/><g font-family="sans-serif" font-size="14" fill="#333e48"><path d="M50 40V220H350" fill="none" stroke="#696969"/><path d="M 0,-9 A9,9 0 1,1 -.01,-9Z" transform="translate(90 180)" fill="#9e1b32"/><path d="M 0,-7 A7,7 0 1,1 -.01,-7Z" transform="translate(210 85)" fill="#696969"/><text transform="translate(90 208)" text-anchor="middle">Moss</text><text transform="translate(210 65)" text-anchor="middle">Fern</text></g></svg>
```

Treat skills/echarts-animated-svg/ as read-only. Write all task files in the
current workspace. Use local tools without network access or other repositories.
