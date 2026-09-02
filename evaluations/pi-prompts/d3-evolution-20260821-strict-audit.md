Evaluate the following visible SVG artifact as `release-audit.svg`:

```svg
<svg id="release-audit" viewBox="0 0 360 180" role="img">
  <title>Release path</title>
  <desc>Three ordered stages.</desc>
  <path id="release-route" d="M18 35 L178 35 L342 162" fill="none" stroke="#9e1b32"/>
  <circle id="entry-node" cx="18" cy="35" r="24" fill="#ffccd5"/>
  <circle id="middle-node" cx="178" cy="35" r="17" fill="#cfcfcf"/>
  <circle id="exit-node" cx="342" cy="162" r="16" fill="#e7e7e7"/>
  <text id="entry-label" x="18" y="35">Intake</text>
  <text id="exit-label" x="356" y="166">Publish</text>
</svg>
```

Use the installed `d3` skill and treat it as read-only. Create exactly these two non-empty files:

- `deliverables/evaluation.md`
- `deliverables/decision.json`

Start `evaluation.md` with exactly `Artifact: release-audit.svg`. Include selector-specific findings for `#entry-label`, `#entry-node`, `#exit-label`, and `#release-route`; cover collision, clipping, label clearance, reading path, balance, data integrity, and implementation contract. Keep composition findings separate from implementation-contract findings. Include a `Validation` section and exactly one line matching `Overall composition score: <integer>/100`.

Write `decision.json` as one JSON object with exactly these four keys: `route`, `colorset`, `patternId`, and `reason`. Use route `evaluation`, colorset `colorset1`, pattern ID `d3-composition-audit`, and a concise non-empty reason. Preserve every supplied identifier and do not create screenshots or any other files.
