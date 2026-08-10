# Text Clearance Contract

Treat every visible brand, tagline, wordmark, monogram, initial, label, and decorative glyph as unobstructed and present by default. Decorative geometry must clear text. An undeclared overlap or omission is a validation failure, not an implied design exception.

## Declaring an exception

Store exceptions on the owning pattern record in `assets/catalog/logo-manifest.json`. Omit the field or use an empty array when no exception exists.

```json
{
  "intentionalOcclusions": [
    {
      "textRole": "initials",
      "occluderRole": "ligature-connector",
      "reason": "The connector intentionally crosses the joined initials.",
      "maxOcclusionRatio": 0.22
    }
  ],
  "intentionalOmissions": [
    {
      "textRole": "tagline",
      "when": "small-size",
      "reason": "The compact 96 px lockup omits the tagline to preserve legibility."
    }
  ]
}
```

Use lowercase hyphen-case semantic tokens of at most 64 characters for `textRole`, `occluderRole`, and `when`. Typical text roles include `brand`, `tagline`, `wordmark`, `monogram`, `initials`, `label`, and `decorative`; an occluder role names the specific crossing geometry. Write a non-empty, design-specific `reason`.

For an intentional occlusion, set a finite `maxOcclusionRatio` greater than zero and no greater than `0.30`. Measure the observed ratio conservatively as the intersection area between the rendered text region and its named occluder divided by the rendered text bounding-box area. The declared value is a ceiling, not a target; the observed ratio must satisfy both the declaration and the global `0.30` cap.

For an intentional omission, scope `when` to one explicit rendered state such as `small-size`. Preserve the complete copy in the accessible title or description even when that role is visually omitted. Do not use omission to hide a layout failure.

Declare each `textRole`/`occluderRole` or `textRole`/`when` pair at most once per pattern. An exception applies only to its named role, occluder, and state; it never authorizes unrelated collisions.

## Dynamic fitting

Keep the clear-text rule valid across the complete declared control range, not only the default composition. Measure generic brand and tagline width in the rendered font, reserve their lockup area before scaling or rotating the mark, and preserve the requested rotation. Fit a long generic brand to its safe width. When a generic tagline would fall below 9 SVG units, split it into two balanced lines, preserve the complete copy in `aria-label` and the SVG description, and fit each line independently. Validate the maximum 32-character brand, maximum 56-character tagline, every range-control maximum, desktop and mobile layouts, and all replay states.
