# Genealogical name and date groups

Use this refinement when a family resembles a succession of thin colored strips with detached date lines. Preserve all names, date meanings, categories and relationships. Improve the visible grouping before adding extra decoration.

## Compose three related treatments

- For an ordinary principal person with a short lifespan or reign, use a compact colored `card` with `detail_position: inside`. Keep the name bold and the date smaller. Grouping both inside the color makes the complete record easier to recognize at page scale. The card's height follows its content; do not impose a fixed thin strip or stretch every name across the width of a column.
- For a selected portrait, normally use `detail_position: outside`, with the image and name together and the date below. This preserves a visible distinction from ordinary people and avoids wrapping a long date beside a narrow portrait. Follow [focal people](focal-people.md) for source selection, sizing and provenance. An explicitly requested inside treatment is supported, but measure every unbreakable name and date word in the space remaining beside the image.
- Keep supporting spouses and terminated relatives as smaller plain names when the source and relationships justify that hierarchy. Preserve each person's stated category. Use an outside caption for a longer explanatory record or an explicit `date_label`; an institutional date/name/consequence stack is a different construction from a short genealogical date pair.

The medium-family baseline helper supplies these measured defaults: ordinary principal records use inside details, portrait records and explicit `date_label` records use outside details, and explicit source treatments remain unchanged. Avoid overriding every record before seeing the preview. For a dense authored source, change the intended treatments, then recompose with [local baselines](branch-baselines.md). Painting a taller card over the previous layout can occupy a previously clear connector attachment.

When the task supplies no category colors, use the light coral, sky blue, gold, sage, lilac, orange and pink palette in `SKILL.md`. Keep names predominantly black or near-black. A dark palette can pass contrast checks yet have a visibly different balance from the reference. Respect supplied colors; do not silently recolor categories to satisfy this preference.

## Separate territory and local court captions

A large serif territory heading and a smaller court or family capsule should not merge into one competing row of headings. Keep their original node/field associations and distinguish their roles through size, shape and placement. Review the named person and nearby competing branches, not just a vacant geometric pocket.

Try wrapping a long capsule into two short lines at its existing type size. Its narrower width can fit a local space that a wide one-line pill cannot use. Recompose around the actual person: a capsule may sit below or beside its associated record when its local connectors make that reading clear. Preserve the label's exact words and order. Do not rename a court, attach it to another person, or reduce type merely to make it fit.

Apply a final authored capsule placement after the automatic `--local-labels` pass, which otherwise restores the normal above-person preference. The renderer may also relocate a pill around occupied boxes. Check its actual painted center and text in the SVG or browser, not only the requested `dx`/`dy` in JSON. If the visible label returned to its old location, the intended improvement did not happen.

Inspect the entire capsule against every nearby descent and partnership path. A node-overlap check alone does not prove that a pill is clear of a connector. Keep the full label readable and the named person's ownership clear; do not conceal a relationship under a white label.

## Inspect before acceptance

Run `space_family_branches.py`, `render_chart.py` and `audit_chart.py` with the exact output paths from [local baselines](branch-baselines.md). Open the final PNG at matched page width and a dense reading-scale crop. Check a principal name/date card, a portrait, a plain spouse, a cross-family union and any manually moved capsule. Compare complete records rather than counting colored rectangles.

Record the remaining differences separately. Solid date groups can improve recognition while repeated family units and long cross-family routes remain conspicuous. Neither a geometry pass nor a successful local caption change proves visual equivalence to an original poster.
