# Read-only diagram publication review — 2026-10-02

This review compares the working tree with HEAD and identifies the dependency
closure for publishing the final colorset fixtures on `main`. No files were
staged, committed, reverted or pushed by this subagent. At inspection there were
776 dirty/untracked status entries across the repository, including substantial
pre-existing authoring and reviewer work. Whole-repository staging would publish
that unrelated work accidentally.

## Existing publication pipeline

`.github/workflows/pages.yml` deploys on every push to `main`, with no path filter,
or through `workflow_dispatch`. Its existing pipeline validates skills, diagram
coverage and payload, tests the authored-docs/build-output boundary, builds
`dist/pages/`, validates the unified output, and uploads that generated directory.
The output must stay under `dist/pages/`; authored `docs/` must not be cleaned or
uploaded as generated Pages output.

`scripts/build-pages.py` is unchanged against HEAD at this review. Its catalog
already includes Mermaid maximum complexity, both PlantUML variants, ECharts
animated SVG, Slidev ECharts and Slidev Anime.js. No new catalog item is needed.
It copies the Mermaid/PlantUML pre-rendered artifacts, rebuilds ECharts, and
builds both Slidev decks from their package-locked sources. Its own main-index
chrome still contains off-palette tokens at review time (`#f6f7f9`, `#28313b`,
`#66717f`, `#d7dde5`); the root agent was notified to normalize those root-owned
authored paints before a final generated-output check.

The workflow has 13 added lines that introduce three new gates. The colorset gate
is part of this task. The other additions invoke an untracked
`skills/repository-reviewer-creator/`, `scripts/audit-skill-authoring.py`,
`scripts/test-bundle-validation.py`, and modified runner/sync/validator behavior.
Those authoring gates have a separate dependency closure. Do not stage the whole
workflow file merely to publish the colorset step: either stage that specific
step while preserving the other dirty hunks, or deliberately publish the full
separately reviewed authoring closure.

## Smallest fixture publication closure

Use exact files from `diagrams-20261002.json` rather than `git add .` or a broad
skill-directory glob. These six existing fixture routes need the following
closure:

1. Mermaid: changed canonical static/animated SVGs under
   `skills/mermaid/assets/examples/mermaid-max-complexity/svg/`, the updated
   `gallery.json` pair hashes, and corrected `gallery.css`. Geometry and source
   facts stay unchanged. The Pages build copies these final SVGs; it does not
   require the dirty 6341-line Mermaid renderer consolidation to publish the
   existing fixtures.
2. PlantUML: the six changed SVGs (`archimate`, `files`, `salt` in both variants),
   the two Ditaa PNGs, and both updated `render-report.json` files. Existing
   coverage metadata and both gallery routes remain unchanged and are already
   cataloged. No new remote rendering is required for these final stored assets.
3. ECharts: `assets/examples/echarts-animated-svg/scripts/build-gallery.mjs`, its
   generated `index.html`, and the imported self-contained
   `assets/templates/echarts-colorsets.mjs`. The helper is an actual build
   dependency outside the fixture directory; omitting it would break clean CI.
4. Slidev ECharts: changed `ExecutiveDashboard.vue`, `GeneratedSvgMotion.vue`,
   `ResponsiveEChart.vue`, `lib/chart-lab.js`, `styles/index.css`, and
   `assets/templates/echarts-colorsets.mjs`. Existing lockfiles and data fixtures
   are unchanged. The wrapper imports the runtime helper during the Pages build.
5. Slidev Anime.js: changed `AnimeFeatureSlide.vue`, fixture CSS, the portable
   runtime `SvgAssetSlide.vue`, and all six runtime SVGs. The fixture consumes
   the runtime pack, so these template assets are required clean-build inputs.
6. Root colorset gate: canonical `docs/colorsets.json`,
   `scripts/validate-colorsets.py`, `scripts/test-colorsets.py`, the final
   `evaluations/colorset-audit/coverage.json`, and the colorset-only workflow
   step, plus any root-owned builder paint correction. The root inventory
   covers all 34 skills, so its complete declared artifact closure must also be
   staged across the other palette audit groups; publishing a full inventory
   while omitting referenced new artifacts would cause clean CI failure.

The companion inventory contains 193 exact scoped skill paths, including runtime
behavior/instructions in addition to the narrower fixture build closure above.
For the complete colorset skill repair, also stage the independent local palette
copies/contracts, actual renderer/validator changes and aligned SKILL guidance.
Keep the three input-decoder JSON tables; the SVG paint helpers read them at
runtime. Stage the SVG/bar templates and public audit evidence with their owning
changes. Generated build trees, screenshots, dependency directories, raw pi
runs and project artifact folders stay ignored.

## Mixed files and preserving prior work

All six `SKILL.md` files were already dirty before this audit. Mermaid's
`animate_mermaid_svg.py` had substantial pre-existing consolidation, and Slidev
ECharts' integration reference had earlier authoring edits. The touched inventory
marks these mixed files explicitly. Mermaid's `references/diagram-selection.md`,
ECharts' `references/chart-animation-profiles.md`, and Slidev Anime.js'
`references/integration-patterns.md` were not changed by this palette audit and
are excluded from its changed-path list.

For fixture publication, the large Mermaid renderer change can remain unstaged
without affecting Pages. For a separate canonical runtime behavior release,
either include that consolidation only after its prior work is intentionally
reviewed, or apply the palette gate to the HEAD modular runtime in a temporary
clean index/worktree while preserving the current working-tree consolidation.
Do not present a whole-file commit of that pre-existing change as a palette-only
patch. Other mixed Markdown files can use explicitly reviewed palette hunks.

## Verification before the authorized push

After forming the explicit staged closure, run the repository validators and
Pages build against the staged tree or a temporary checkout of that exact tree,
not only the dirty working tree. Otherwise untracked templates, reviewer code,
or unstaged helper changes could hide a clean-CI failure. Verify the generated
main index and all six final gallery routes with the root checker and confirm
that stable pattern IDs/legacy PlantUML routes still resolve. Review the staged
diff and file list, push the Pages-deploying `main`, and verify the GitHub Pages
workflow's deployed SHA and resulting stable example links. No commit or push
has been performed as part of this read-only review.
