# Preserve an ambiguous drawing while evaluating native reconstruction

Use the read-only skill at `skills/lucidchart-svg/`. All files must remain in this workspace. No network, authenticated Lucid session, or upload capability is available.

I want separately editable Lucidchart elements from this drawing. It has two crossing strokes, but I do not know whether the strokes are relationships, decoration, or part of another symbol, and I have no source graph data. Preserve a visual fallback and tell me what further information is needed for a reliable editable reconstruction. Keep the original design and labels.

Create `source/sketch.svg` as the exact UTF-8/LF text below, with one final newline:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="360" height="180" viewBox="0 0 360 180">
  <rect id="left-box" x="20" y="60" width="90" height="50" fill="#dce8f7" stroke="#223344"/>
  <text x="35" y="90" font-family="Arial" font-size="12" fill="#223344">Queue &amp; sort</text>
  <rect id="right-box" x="250" y="60" width="90" height="50" fill="#f7e6dc" stroke="#443322"/>
  <text x="265" y="90" font-family="Arial" font-size="12" fill="#443322">Release</text>
  <path id="stroke-a" d="M110 60 L250 110" fill="none" stroke="#555555"/>
  <path id="stroke-b" d="M110 110 L250 60" fill="none" stroke="#777777"/>
</svg>
```

Deliver the original at `source/sketch.svg`, `out/ambiguity/inspection.json`, a checked SVG visual copy at `out/ambiguity/visual.svg`, and an English note at `out/ambiguity/notes.md` explaining editability, topology uncertainty and the route/prerequisite for using the visual asset in Lucidchart. These are the only requested delivered artifacts. The visual copy must preserve the original bytes. Do not claim that preparing the file created or validated a live Lucid document.
