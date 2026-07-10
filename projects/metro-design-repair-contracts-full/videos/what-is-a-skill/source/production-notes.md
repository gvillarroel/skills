# Production Notes

## Source Facts

- A skill is a reusable capability package that gives the harness structured instructions, scripts, and supporting resources for a specialized task.
- The cost insight is important: skills support **progressive disclosure** because they load when relevant instead of forcing long procedures into every prompt.
- GitHub Copilot defines skills as folders of instructions, scripts, and resources; Claude Code says long reference material in a skill “costs almost nothing until you need it”; OpenCode also loads `SKILL.md`-based skills on demand.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is a Skill explainer should show a skill as on-demand reusable workflow packaging, not as a static prompt or generic pipeline.
- Mechanic: skill cards fan open only when invoked, a long prompt wall collapses into one scoped SKILL.md package, compatible folder structures align, a progressive disclosure cost meter stays flat until activation, examples and tool/script modules attach, and an oversized mini-novel skill is trimmed into a reusable workflow stamp.
- Candidate metaphors: skill-package megacanvas, generic systems-flow pipeline, and feature card gallery.
- Rejected alternative: a generic systems-flow pipeline would show queue movement but hide the skill-specific mechanic: reusable instructions, scripts, references, and assets stay available without loading every session.
- Chosen metaphor: skill-package megacanvas with skill_card_stack, long prompt wall collapse, SKILL.md-compatible folder structures, progressive disclosure cost meter, deploy/debug/architecture/onboarding/codebase-map example cards, tool badges, script blocks, read-surface levels, bloated skill trimming, and on-demand reusable workflow stamp.
- Visual vocabulary: brand red marks the selected reusable workflow and activation route; status red marks trimmed bloat or cost risk; dark red marks hard gates; gray levels separate cards, folder surfaces, resource modules, validation blocks, read surfaces, and evidence floor. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates all Skill roles.
- Narration split: vendor names, exact markdown syntax, and the final definition stay in narration or source facts; the frame carries reusable packaging, progressive disclosure, activation, and trimming mechanics without explanatory text.

## Strategy Anchors

- SKILL.md
- markdown # SKILL.md --- name: deploy-preview description: Build, test, and deploy a preview safely tools: - bash - read - write --- 1. Run targeted tests first. 2. Validate required environment variables. 3. Deploy only to preview environment. 4. Summarize URL and rollback command
- The point of a skill is not fancy syntax. It is reusable, scoped expertise that the harness can invoke when relevant instead of re-learning the same workflow every session. citeturn10view3turn9view2turn11view2 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "A skill is a reusable task package. It gives the assistant a named way to perform a specialized job again and again." |
- fans open | | 0:15-0:30 | "Good skills are not giant permanent prompts. They are loaded only when relevant, which keeps normal sessions lighter." | Long prompt wall shrinks into one skill card | | 0:30-0:45 | "GitHub Copilot describes skills as folders of instructions, scripts, and resources. Claude and OpenCode use similar SKILL-dot-MD patterns." | Three compatible folder structures align | | 0:45-1:00 | "This is progressive disclosure. You keep rich procedures available, but you only pay the token cost when the procedure is actually used." | Cost meter stays flat until skill activates | | 1:00-1:15 | "That makes skills perfect for deploy checklists, debugging routines, architecture explainers, onboarding flows, or codebase maps." | Example skill cards cycle quickly | | 1:15-1:30 | "A skill can also call scripts or specify approved tools, which makes the workflow more repeatable and safer." | Tool badges snap onto the skill card | | 1:30-1:45 | "The common mistake is turning skills into mini novels. Keep them sharp, task-scoped, and reusable." | A huge bloated card gets trimmed down | | 1:45-2:00 | "So define a skill as on-demand domain expertise for the harness: reusable, composable, and usually cheaper than repeating the same long prompt." | Final tag: **Skill = on-demand reusable workflow** | Reference basis for narration: GitHub skill docs, Claude skill docs, OpenCode skill docs. citeturn10view3turn7search1turn9view2turn11view2 #### Shot and animation plan - Reuse
- and show activation only when relevant. - Show one giant static prompt turning into three small skills. - Use a cost line that stays flat until the skill is invoked. - Animate a deploy workflow skill from checklist to executed steps. - Reuse the same visual card style later for instruction layers. - End with a reusable "progressive disclosure" callout. #### Q&A | Question | Answer | Source | |---|---|---| | What is a skill? | A reusable set of instructions, scripts, and resources for specialized tasks. citeturn10view3turn7search1 | citeturn10view3turn7search1 | | Why are skills useful? | They make recurring workflows repeatable and easier to discover. citeturn10view3turn9view2 | citeturn10view3turn9view2 | | What is progressive disclosure here? | Long procedures stay available but load only when needed. citeturn9view2 | citeturn9view2 | | Do skills reduce cost? | Often yes, because they avoid repeating long instructions every session. citeturn9view2turn28view0 | citeturn9view2turn28view0 | | Where do Copilot skills live? | In project or personal skill folders, including
- ,
- , or
- citeturn10view3 | citeturn10view3 | | Can Claude skills be invoked directly? | Yes, via slash-style invocation as skills or commands. citeturn9view2 | citeturn9view2 | | Does OpenCode support Claude-style skills? | Yes. It discovers Claude-compatible
- Skill = on-demand reusable workflow
- skill_card_stack and show activation only when relevant
- Show one giant static prompt turning into three small skills
- Use a cost line that stays flat until the skill is invoked
- Animate a deploy workflow skill from checklist to executed steps
- the same visual card style later for instruction layers
- End with a reusable "progressive disclosure" callout
- flow-tokens
- layered-architecture
- swimlane-handoff

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-skill --title "What is a Skill" --output-id what-is-a-skill --pattern systems-flow
```
