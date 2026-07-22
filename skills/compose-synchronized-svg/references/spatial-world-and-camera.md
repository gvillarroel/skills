# Spatial World and Camera

Use this reference only when the requested SVG must be explored in parts: a PoE-style skill tree, giant genealogy, causal world, or atlas whose local regions contain complete diagrams. Keep compact compositions on the normal brief template.

## Choose the navigable-world mode

Declare a world when all of these are true:

- the idea needs 12–48 nonredundant modules;
- modules form 4–12 meaningful districts;
- an overview should expose topology rather than readable chart detail;
- district views should act as navigable indexes;
- module views should reveal complete diagrams;
- a deterministic camera route would support explanation or video.

Use `world.mode: "navigable-atlas"`. Choose `world.armature` deliberately:

- `radial-skill-tree`: one semantic root with branches arranged around it;
- `genealogical-tree`: generations or stages arranged by directed depth;
- `constellation-map`: accepted for crosslinked systems, but currently shares the radial district placement; do not claim a separate force-layout algorithm.

Each district needs an ID, label, concise summary, role, `localArmature`, and 1–8 module IDs. Use `radial`, `branch`, `lanes`, or `orbit` for the local armature. Assign every module to exactly one district. Keep equal-count peer districts at one camera scale; let a small semantic root remain visually distinct.

## Author the world graph

Declare 1–28 district links with stable IDs, readable labels, and `flow`, `dependency`, or `feedback` kinds. Every district must be reachable from `rootDistrictId` through directed non-feedback links.

The compiler derives one visual spanning tree:

- one incoming `trunk` reaches every non-root district;
- remaining non-feedback routes become `crosslink`;
- feedback routes remain `feedback`.

At world tier, emphasize trunks and district hubs. Keep crosslinks and feedback contextual. Do not let all edges compete equally. Local spokes group module destinations; they do not assert causality unless the brief declares a real local dependency.

Use the three semantic tiers consistently:

1. **World:** show root, district hubs, primary trunks, and compact unlabeled local nodes. Hide painted module cards after runtime readiness.
2. **District:** show one active district as a labeled local branch/index. Expose one keyboard destination per module and keep chart bodies hidden.
3. **Module:** show the complete target diagram and its focus controls. Recede world and district index geometry.

Keep literal module geometry in the file before JavaScript runs. Scope runtime level-of-detail CSS under `.svg-sync-ready[data-world-mode="true"]`; otherwise script-free viewers would permanently lose detailed diagrams. Hide the inactive navigation HUD in script-free mode.

## Use explicit structural diagrams

Add `module.diagram` when a tree or network is qualitative rather than a projection of the numeric derived DAG.

- Use 2–18 nodes and 1–32 links.
- Use `tree`, `radial`, or `lanes` layout.
- Use node kinds `root`, `notable`, `merge`, `gate`, `leaf`, or `evidence`.
- Use link kinds `parent`, `prerequisite`, `dependency`, `flow`, or `feedback`.
- Keep the graph connected.
- Bind every numeric value listed by the module exactly once; qualitative nodes may remain unbound.
- Wrap node labels into complete lines. Do not depend on ellipsis at module tier.

Without `module.diagram`, compact network modules continue to derive their topology from direct numeric dependencies and must include every intermediate node required by the claim.

## Author the camera route

Put navigation inside `world.navigation`:

```json
{
  "initialTarget": "world",
  "route": {
    "loop": true,
    "autoplay": false,
    "stops": [
      {
        "id": "overview",
        "label": "Whole world",
        "target": "world",
        "travelMs": 0,
        "holdMs": 2400,
        "focusId": "overview-story"
      },
      {
        "id": "first-branch",
        "label": "First branch",
        "target": "district-one",
        "travelMs": 1600,
        "holdMs": 2800,
        "handoff": "Follow the first dependency trunk"
      },
      {
        "id": "return",
        "label": "Return to the whole",
        "target": "world",
        "travelMs": 1800,
        "holdMs": 2600
      }
    ]
  }
}
```

Use `world`, district IDs, or module IDs as brief targets. The compiler emits `world`, `district-<id>`, and `module-<id>` anchors. Every required district must occur in the route. A looping route must finish at its initial anchor. Treat `focusId` and `handoff` as narration metadata for the camera route; camera movement must not mutate semantic focus or values.

The compiler emits:

- a fixed `1920×1080` root;
- a nested camera viewport at `[0, 120, 1600, 900]`;
- exact 16:9 world bounds;
- world, district, and module anchors with depths 0, 1, and 2;
- semantic-zoom thresholds;
- an overview HUD, minimap, deep links, and a deterministic route.

Use `#view=<anchor-id>` for deep links. `Home` and `0` call `fitOverview()` and return to `world`; `resetCamera()` restores the declared initial target. Pointer drag pans, wheel zooms, arrow keys pan, and `+`/`-` zoom. Reduced motion disables camera autoplay but preserves instant navigation.

## Keep camera and semantic state independent

World plans add `navigation` to `syncModes` and publish these methods:

```text
getCamera()       setCamera(viewBox)
navigateTo(id)    seekCamera(timeMs)
fitOverview()     nextAnchor()
previousAnchor()  playCamera()
pauseCamera()     resetCamera()
```

Camera snapshots carry their own revision, anchor, viewBox, tier, route time, stop, playback, and motion fields. Commit root camera attributes before dispatching one `svg-camera-change` event. Never increment semantic revision or dispatch `svg-sync-change` for camera-only movement.

Prefer an exact anchor's declared `zoomTier`. Infer a tier from width only for free pan or zoom. This prevents a small root district from being misclassified as a module.

Keep tab order camera-aware:

- world tier: district hubs and camera controls;
- district tier: module-index controls in the active district;
- module tier: focus controls in the visible target module;
- off-camera controls: `tabindex="-1"`.

## Validate all three scales

Run the normal static validator plus world gates:

```powershell
uv run --script <skill-root>/scripts/validate_synchronized_svg.py <output.svg> `
  --output <static-report.json> `
  --require-navigation `
  --min-navigation-regions 4 `
  --min-anchor-depth 2 `
  --min-world-detail-area-ratio 16 `
  --min-distant-shared-sources 1
```

Then run the bundled browser audit. It must prove:

- exact DOM parity for districts, nodes, links, anchors, HUD, and minimap;
- at least 95% target-frame coverage at every module anchor against the fixed outer camera viewport;
- readable detail text and no frame escapes at every module anchor;
- history-independent route seeks and an exact loop seam;
- byte-identical semantic snapshots before and after camera actions;
- independent camera revision and one post-commit event;
- correct world/district/module tab order;
- pointer and keyboard navigation, deep links, and camera playback;
- reduced-motion instant navigation with autoplay disabled;
- a meaningful script-free world with hidden dead controls.

Capture and inspect the whole world, every district, representative modules from different renderer families, and the script-free fallback. For video preparation, also inspect route arrivals and travel midpoints. Require two consecutive clean visual rounds after the final material change.
