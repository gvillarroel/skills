# Production Notes

## Source Facts

- The four alternatives named by the user map to four different “home bases” for AI work.
- **Atlassian Rovo** is strongest when the center of gravity is organizational knowledge across Jira, Confluence, and connected tools; **Gemini App** is a consumer and prosumer assistant with subscription tiers and deep Google ecosystem ties; **GitHub Copilot** is strongest as a coding harness inside developer workflows; and **Claude Desktop/Code** is strongest as a high-capability coding and research assistant with strong connector, skill, hook, and MCP patterns.
- Rovo now ships in paid Atlassian cloud subscriptions, Gemini offers Free/AI Pro/AI Ultra plans, Copilot has Free through Enterprise and AI-credit billing, and Claude offers Free through Enterprise plus API pricing.

## Visual Metaphor Decision

- Visual pattern: swimlane-handoff.
- Concept claim: a good What AI alternatives we have explainer should show each assistant as a different workflow home, not as a feature-list card or generic brand comparison.
- Mechanic: a four-column comparison grid activates first, each platform anchors to its natural workspace, a shared fit radar turns into quadrants, pricing meters rise underneath, and a workflow-gravity selector routes through guardrail, permission, and observability blocks.
- Candidate metaphors: workflow-gravity megacanvas, generic feature table, and product-logo carousel.
- Rejected alternative: a generic feature table would preserve platform names but hide the central choice mechanic: match the assistant to where context, approvals, and work already live.
- Chosen metaphor: AI alternatives megacanvas with comparison_grid, Rovo/Gemini/Copilot/Claude workspace anchors, shared radar/quadrant fit map, four cost meters, selected workflow path, and guardrail/permission/observability wrapper.
- Visual vocabulary: brand red marks the selected workflow path and primary flow; status red marks cost or governance pressure; dark red marks approval and permission boundaries; gray levels separate platform homes, fit axes, pricing models, selector state, and governance wrap. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles.
- Narration split: plan names, vendor details, and exact pricing caveats stay in narration or source facts; the frame carries workflow gravity, fit, cost, and governance mechanics without explanatory text.

## Strategy Anchors

- comparison_grid
- credit_meter
- Choose by workflow gravity
- comparison_grid with one strong icon per platform
- Show each alternative anchored to its natural workspace: Atlassian suite
- Use one shared radar chart for **knowledge**
- credit_meter but relabel for each pricing model
- Fade in "home base" text for each tool rather than feature walls
- End with a use-case selector the audience can mentally replay later
- swimlane-handoff
- inline-bar-table
- circuit-signal-traces
- masonry-wall
- flow-tokens
- dependency-map
- masonry wall
- megacanvas zones
- camera reframe

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-ai-alternatives-we-have --title "What AI alternatives we have" --output-id what-ai-alternatives-we-have --pattern swimlane-handoff
```
