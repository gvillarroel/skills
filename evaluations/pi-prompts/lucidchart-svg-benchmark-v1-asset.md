# Keep a night-shift badge as artwork

Please prepare this illustrated badge as a visual SVG asset for later Lucidchart insertion. Its gradient, circular clipping, decorative paths, and complete text should remain intact. Save the original to `source/night-shift.svg`, prepare a byte-preserving upload candidate at `ready/night-shift.svg`, and write a source inspection to `review/inspection.json`.

Write `review/fidelity.md` reviewing this particular file's resource safety, rich visual details, and fidelity risks. Inspect a local rendering if a renderer is available; clearly identify whether you could perform that visual check. Explain what the visual-asset route establishes, why this artwork is not an independently editable native diagram, and what still needs verification in Lucid. No semantic node or relationship data is supplied, so do not fabricate a native graph, document JSON, or `.lucid` package. Do not claim a completed upload or an overall visual-fidelity percentage.

Use only the read-only `skills/lucidchart-svg/` bundle and normal local tools. Keep generated files outside the bundle in this workspace. Work offline: do not use network access, external services, credentials, or a live Lucid session. Save the source exactly as UTF-8 without a BOM, with LF line endings and one final LF; preserve its bytes thereafter.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240" aria-labelledby="badge-title badge-desc">
  <title id="badge-title">Night-shift operations badge</title>
  <desc id="badge-desc">A dusk gradient panel with a clipped moon illustration and queue status.</desc>
  <defs>
    <linearGradient id="dusk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#142943"/><stop offset="1" stop-color="#526795"/></linearGradient>
    <clipPath id="moon-window"><circle cx="390" cy="66" r="44"/></clipPath>
  </defs>
  <rect x="8" y="8" width="464" height="224" rx="20" fill="url(#dusk)"/>
  <g clip-path="url(#moon-window)"><rect x="342" y="18" width="96" height="96" fill="#F8DF9B"/><path d="M340 75 Q390 35 440 75 L440 120 L340 120 Z" fill="#DCA861"/><path d="M340 96 Q388 58 440 98 L440 124 L340 124 Z" fill="#8D6B6C"/></g>
  <path d="M30 166 C130 132 210 210 310 170" fill="none" stroke="#C5D9ED" stroke-width="3"/>
  <text x="30" y="64" font-family="Arial" font-size="25" font-weight="bold" fill="#FFFFFF">Night shift — queue 7</text>
  <text x="30" y="105" font-family="Arial" font-size="17" fill="#E8F0FF">Ready &amp; monitored</text>
  <text x="30" y="206" font-family="Arial" font-size="14" fill="#E8F0FF">Window: 22:00–06:00</text>
</svg>
```
