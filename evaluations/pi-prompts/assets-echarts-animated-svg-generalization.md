Create input.svg from this supplied renderer SVG, then produce output.svg
as a portable animated line chart. Preserve the geometry and labels and
provide a readable reduced-motion state. Write the bundled pair-validation
report to validation.json.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320"><rect width="400" height="320" fill="white"/><g font-family="sans-serif" font-size="14" fill="#333e48"><path d="M50 40V220H350" fill="none" stroke="#696969"/><path d="M0 100L80 50L160 70L240 0" transform="translate(65 70)" fill="none" stroke="#9e1b32" stroke-width="3"/><text transform="matrix(1 0 0 1 65 210)">Spring</text><text transform="matrix(1 0 0 1 285 210)">Winter</text><text transform="translate(25 130) rotate(-90)" text-anchor="middle">Rainfall</text></g></svg>
```

Treat skills/echarts-animated-svg/ as read-only. Write all task files in the
current workspace. Use local tools without network access or other repositories.
