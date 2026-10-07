# Outlined export label review

Use only the read-only skill at `skills/lucidchart-svg/` and normal local tools. Work offline in this workspace. No Lucid browser or export download is available. Do not modify the skill bundle.

An SVG inspection reports zero text elements. The small drawing below uses visible glyph-like paths, and the user asks whether zero text proves the drawing lost its labels and whether inserting it in Lucid will create separately editable text. Create `input/outlined.svg` verbatim, inspect it into `deliver/inspection.json`, and prepare a byte-preserving candidate `deliver/artwork.svg`. Write `deliver/review.md` answering that question with evidence boundaries, the differences between supported insertion routes, and an appropriate way to verify appearance and editability. Do not claim the mock fixture was exported from Lucid or uploaded successfully. Do not invent the words encoded by the paths.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="240" height="100" viewBox="0 0 240 100"><rect x="5" y="5" width="230" height="90" fill="#FFFFFF" stroke="#333333"/><g id="outlined-label" fill="#111111"><path d="M30 25H38V65H30Z"/><path d="M50 25H80V33H50ZM61 33H69V65H61Z"/></g></svg>
```
