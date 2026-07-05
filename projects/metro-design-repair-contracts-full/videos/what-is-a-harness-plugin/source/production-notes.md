# Production Notes

## Source Facts

- A plugin is a distribution mechanism for reusable harness customization.
- The exact packaging differs by product, but the pattern is consistent: bundle runtime capabilities so teams can install, share, version, and govern them instead of hand-copying local setup.
- In current official docs, GitHub Copilot CLI plugins can bundle agents, skills, hooks, and MCP configuration; Claude Code plugins can bundle skills, agents, hooks, and MCP servers from marketplaces; OpenCode plugins are JS/TS modules loaded locally or from npm to add hooks, tools, and integrations.

## Visual Metaphor Decision

- Visual pattern: swimlane-handoff.
- Concept claim: a good What is a Harness Plugin explainer should show a plugin as an installable, versioned, governed bundle of reusable harness behavior, not as an extension icon or generic handoff chart.
- Mechanic: a plugin_bundle_cube assembles from smaller blocks, opens into detachable skills/hooks/MCP/agent/tool modules, passes through provider packaging surfaces, fans out to teams through governance/version gates, then contrasts efficient defaults with noisy context/tool spread before the package-install stamp.
- Candidate metaphors: plugin-bundle megacanvas, generic swimlane handoff, and provider feature table.
- Rejected alternative: a generic swimlane would show ownership transfer but hide the actual plugin idea: packaging runtime capabilities into one installable unit that can be shared, versioned, and governed.
- Chosen metaphor: plugin-bundle megacanvas with detachable modules, GitHub manifest surface, Claude marketplace allowlist gate, OpenCode npm/runtime drop, team install fanout, versioning arrows, good/noisy plugin split, and packaged harness behavior stamp.
- Visual vocabulary: brand red marks the installable bundle and approved package-install flow; status red marks allowlist gates and noisy-plugin risk; dark red marks governance controls; gray levels separate bundle, module, provider, governance, and cost/risk hierarchy. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles.
- Narration split: provider names and exact package syntax stay in narration or source facts; the frame carries distribution, governance, versioning, install, and cost mechanics without explanatory text.

## Strategy Anchors

- json { "name": "security-pack", "contains": ["hooks", "skills", "mcp", "agent-profile"], "defaultEnabled": true, "purpose": "secret scanning, safer tool use, shared deploy workflow" }
- The important design principle is not the exact file format. It is that plugins package multiple runtime behaviors into one installable unit that can be versioned and governed. citeturn10view2turn9view0 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "A harness plugin is how you package and share runtime customization. Instead of copying files by hand, you install one reusable unit." |
- assembles from smaller blocks | | 0:15-0:30 | "The bundle usually contains behavior, not just visuals: skills, hooks, MCP config, special agents, or custom tools." | Bundle opens to reveal labeled modules | | 0:30-0:45 | "GitHub Copilot CLI plugins explicitly support reusable agents, skills, hooks, and MCP server configuration." | GitHub plugin manifest card | | 0:45-1:00 | "Claude Code's plugin system also packages skills, agents, hooks, and MCP servers, and it supports controlled marketplaces and managed settings." | Claude marketplace diagram with allowlist gate | | 1:00-1:15 | "OpenCode keeps plugins very developer-friendly. They are JavaScript or TypeScript modules that subscribe to events and extend behavior." | NPM package drops into OpenCode runtime | | 1:15-1:30 | "This matters because distribution is governance. Plugins let you standardize the approved way to work." | Team-wide install animation | | 1:30-1:45 | "Plugins can lower cost by packaging efficient defaults. They can also raise cost if they inject noisy context or expensive tool calls everywhere." | Good plugin vs bad plugin split | | 1:45-2:00 | "So define a plugin as a shareable harness bundle for behavior, policy, and integrations-not as just another extension icon." | Final text: **Plugin = packaged harness behavior** | Reference basis for narration: GitHub Copilot CLI plugin docs, Claude Code plugin configuration, OpenCode plugin docs. citeturn10view2turn9view0turn11view0turn11view1 #### Shot and animation plan - Reuse
- Plugin = packaged harness behavior
- plugin_bundle_cube with detachable inner parts
- Show GitHub
- Add a marketplace / allowlist lane for enterprise governance
- Visualize versioning and upgrade arrows over the same plugin pack
- Use a red "noisy plugin" example that adds unnecessary tools everywhere
- End with a package-install visual that can be reused in skills and MCP modules
- swimlane-handoff
- flow-tokens
- circuit-signal-traces
- masonry-wall
- risk-bowtie
- dependency-map
- masonry wall
- megacanvas zones

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-harness-plugin --title "What is a Harness Plugin" --output-id what-is-a-harness-plugin --pattern swimlane-handoff
```
