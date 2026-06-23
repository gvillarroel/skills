#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
SOURCE_DIR = SKILLS / "mermaid-animated-svg" / "assets" / "examples" / "mermaid"
OUTPUT_DIR = SKILLS / "mermaid-animated-svg" / "assets" / "examples" / "mermaid-animation-directives" / "by-type"


EXAMPLES = [
    {
        "slug": "architecture-service-pipeline",
        "type": "Architecture",
        "source": "architecture",
        "critique": "Strong example because architecture aliases produce stable service and edge IDs; grouped source/markdown reveal avoids overlapping fixtures.",
        "directives": """
            %% @animate v1 duration=5.2s default-duration=320ms
            %% @animate target docs = id:my-svg-group-docs
            %% @animate target source = id:my-svg-service-source
            %% @animate target markdown = id:my-svg-service-markdown
            %% @animate target renderer = id:my-svg-service-renderer
            %% @animate target browser = id:my-svg-service-browser
            %% @animate target validator = id:my-svg-service-validator
            %% @animate target links = role:edge
            %% @animate group inputs = source, markdown
            %% @animate point send = source.right
            %% @animate point render-in = renderer.left
            %% @animate point browser-in = browser.left
            %% @animate point validate-in = validator.top
            %% @animate mark artifact at send shape=dot size=8 fill=#1c7ed6
            %% @animate at 0ms reveal docs effect=fade duration=240ms
            %% @animate at 180ms reveal inputs mode=together effect=pop duration=300ms name=show-inputs
            %% @animate at show-inputs.end reveal renderer effect=pop duration=300ms name=show-renderer
            %% @animate at show-renderer.end trace links duration=620ms name=trace-links
            %% @animate at show-renderer.end move artifact to render-in duration=620ms ease=in-out name=to-renderer
            %% @animate at to-renderer.end reveal browser effect=pop duration=280ms name=show-browser
            %% @animate at show-browser.end move artifact to browser-in duration=520ms ease=out name=to-browser
            %% @animate at trace-links.end reveal validator effect=pop duration=280ms name=show-validator
            %% @animate at show-validator.end move artifact to validate-in duration=520ms ease=out name=to-validator
            %% @animate at to-validator.end color validator fill=#d3f9d8 stroke=#45842a duration=260ms
        """,
    },
    {
        "slug": "block-diagram-directive-selectors",
        "type": "Block",
        "source": "block-diagram",
        "critique": "Uses stable rendered block IDs and one connection ID; it intentionally avoids role:edge for precise connector movement.",
        "directives": """
            %% @animate v1 duration=4.8s default-duration=300ms
            %% @animate target source = id:my-svg-source
            %% @animate target render = id:my-svg-arrow1
            %% @animate target markdown = id:my-svg-markdown
            %% @animate target check = id:my-svg-arrow2
            %% @animate target result = id:my-svg-result
            %% @animate target palette = id:my-svg-palette
            %% @animate target diagram = id:my-svg-diagram
            %% @animate target source-markdown = id:my-svg-1-source-markdown
            %% @animate group pipeline = source, render, markdown, check, result
            %% @animate point send = source.right
            %% @animate point wrapped = markdown.left
            %% @animate point passed = result.top
            %% @animate mark payload at send shape=dot size=8 fill=#1971c2
            %% @animate at 0ms reveal pipeline mode=sequence gap=140ms effect=pop name=show-pipeline
            %% @animate at show-pipeline.end trace source-markdown duration=420ms name=trace-first
            %% @animate at trace-first.end move payload to wrapped duration=650ms ease=in-out name=render-hop
            %% @animate at render-hop.end color markdown fill=#d3f9d8 stroke=#2b8a3e duration=260ms
            %% @animate at render-hop.end+120ms move payload to passed duration=700ms ease=out name=check-hop
            %% @animate at check-hop.end color result fill=#f9ccff stroke=#9e1b32 duration=280ms
            %% @animate at check-hop.end reveal palette effect=fade duration=240ms
            %% @animate at check-hop.end+180ms reveal diagram effect=pop duration=260ms
        """,
    },
    {
        "slug": "c4-context-message-flow",
        "type": "C4",
        "source": "c4-diagram",
        "critique": "Good for box-level orchestration, but C4 relationship selection is still coarse because Mermaid renders all relation lines as one candidate.",
        "directives": """
            %% @animate v1 duration=5s default-duration=450ms
            %% @animate target author = text:"Skill Author"
            %% @animate target repo = text:"Skills Repository"
            %% @animate target renderer = text:"Mermaid Renderer"
            %% @animate target browser = text:"Documentation Browser"
            %% @animate target relationships = text:"Updates"
            %% @animate group boxes = author, repo, renderer, browser
            %% @animate point author-out = author.right
            %% @animate point repo-in = repo.left
            %% @animate point renderer-in = renderer.top
            %% @animate point browser-in = browser.left
            %% @animate mark packet at author-out shape=dot size=9 fill=#1971c2
            %% @animate at 0ms reveal boxes mode=sequence gap=180ms effect=pop name=show-boxes
            %% @animate at show-boxes.end trace relationships duration=700ms name=show-relations
            %% @animate at show-relations.end move packet to repo-in duration=650ms ease=out name=send-update
            %% @animate at send-update.end pulse repo scale=1.04 duration=260ms
            %% @animate at send-update.end move packet to renderer-in duration=750ms ease=out name=send-source
            %% @animate at send-source.end move packet to browser-in duration=650ms ease=out name=publish
            %% @animate at publish.end pulse browser scale=1.04 stroke=#9e1b32 duration=300ms
        """,
    },
    {
        "slug": "class-relation-token",
        "type": "Class",
        "source": "class-diagram",
        "critique": "Uses exact class and relation IDs, which is safer than substring text matching for class names.",
        "directives": """
            %% @animate v1 duration=5s default-duration=420ms
            %% @animate target catalog = id:my-svg-classId-DiagramCatalog-0
            %% @animate target example = id:my-svg-classId-MermaidExample-1
            %% @animate target theme = id:my-svg-classId-ThemeConfig-2
            %% @animate target catalog-example = id:my-svg-id_DiagramCatalog_MermaidExample_1
            %% @animate group core-classes = catalog, example, theme
            %% @animate point send = catalog.right
            %% @animate point receive = example.left
            %% @animate mark relation-token at send shape=dot size=9 fill=#1f6feb
            %% @animate at 0ms reveal core-classes mode=sequence gap=180ms effect=pop name=show-classes
            %% @animate at show-classes.end trace catalog-example duration=650ms name=trace-relation
            %% @animate at trace-relation.end move relation-token to receive duration=650ms ease=out name=deliver
            %% @animate at deliver.end color example fill=#d3f9d8 stroke=#2b8a3e duration=300ms
        """,
    },
    {
        "slug": "er-relationship-trace",
        "type": "Entity Relationship",
        "source": "entity-relationship-diagram",
        "critique": "Strong current-language example: exact entity and relationship IDs give stable anchors and path tracing.",
        "directives": """
            %% @animate v1 duration=4.8s default-duration=650ms
            %% @animate target customer = id:my-svg-entity-CUSTOMER-0
            %% @animate target order = id:my-svg-entity-ORDER-1
            %% @animate target places = id:my-svg-id_entity-CUSTOMER-0_entity-ORDER-1_0
            %% @animate target places-label = text:"places"
            %% @animate point order-start = customer.bottom
            %% @animate point order-end = order.top
            %% @animate mark order-token at order-start shape=dot size=8 fill=#652f6c
            %% @animate at 0ms reveal customer effect=pop duration=350ms
            %% @animate at 450ms reveal order effect=pop duration=350ms name=show-order
            %% @animate at show-order.end trace places duration=650ms name=places-edge
            %% @animate at show-order.end move order-token to order-end duration=650ms ease=out name=move-order
            %% @animate at places-edge.end reveal places-label effect=fade duration=250ms
            %% @animate at move-order.end pulse order scale=1.04 duration=300ms
        """,
    },
    {
        "slug": "event-modeling-causality",
        "type": "Event Modeling",
        "source": "event-modeling",
        "critique": "Shows the right workaround for missing per-edge selectors: keep swimlanes static and animate causality with marks.",
        "directives": """
            %% @animate v1 duration=4.2s default-duration=350ms
            %% @animate target examples = text:"ExamplesPage"
            %% @animate target create = text:"CreateMermaidPair"
            %% @animate target created = text:"MermaidPairCreated"
            %% @animate target index = text:"MermaidIndex"
            %% @animate target runner = text:"ValidationRunner"
            %% @animate target validated = text:"ExamplesValidated"
            %% @animate group flow = examples, create, created, index, runner, validated
            %% @animate point request-start = examples.bottom
            %% @animate point request-end = create.top
            %% @animate point event-end = created.top
            %% @animate mark token at request-start shape=dot size=9 fill=#1971c2
            %% @animate mark event-ring at created.center shape=ring size=34 stroke=#c19a0f
            %% @animate at 0ms reveal flow mode=sequence gap=220ms effect=pop duration=300ms name=reveal-flow
            %% @animate at 380ms move token to request-end duration=650ms ease=out name=to-command
            %% @animate at to-command.end move token to event-end duration=650ms ease=out name=to-event
            %% @animate at to-event.end pulse created scale=1.05 stroke=#c19a0f duration=320ms
            %% @animate at to-event.end+120ms show event-ring effect=pop duration=240ms
            %% @animate at reveal-flow.end pulse validated scale=1.05 stroke=#c19a0f duration=320ms
        """,
    },
    {
        "slug": "flowchart-branch-review",
        "type": "Flowchart",
        "source": "flowchart",
        "critique": "Readable node selectors work well; broad edge tracing remains the main limitation until edge:A->B exists.",
        "directives": """
            %% @animate v1 duration=5s default-duration=300ms
            %% @animate target start = text:"Start"
            %% @animate target collect = text:"Collect request"
            %% @animate target valid = text:"Valid payload?"
            %% @animate target store = text:"Store event"
            %% @animate target notify = text:"Notify subscriber"
            %% @animate target edges = role:edge
            %% @animate group main = start, collect, valid, store, notify
            %% @animate point send = start.right
            %% @animate point check = valid.left
            %% @animate point done = notify.left
            %% @animate mark request at send shape=dot size=8 fill=#1971c2
            %% @animate at 0ms reveal main mode=sequence gap=150ms effect=pop name=show-main
            %% @animate at show-main.end trace edges duration=650ms name=trace-flow
            %% @animate at trace-flow.end move request to check duration=600ms ease=in-out name=to-check
            %% @animate at to-check.end color valid fill=#fff3bf stroke=#f08c00 duration=260ms restore=true
            %% @animate at to-check.end move request to done duration=750ms ease=out name=to-done
            %% @animate at to-done.end pulse notify scale=1.04 stroke=#45842a duration=360ms
        """,
    },
    {
        "slug": "gantt-progress-lane",
        "type": "Gantt",
        "source": "gantt",
        "critique": "Preserves date geometry by moving a mark rather than moving task bars.",
        "directives": """
            %% @animate v1 duration=5s default-duration=280ms
            %% @animate target build-rows = css:".section0"
            %% @animate target build-title = text:"Build"
            %% @animate target draft = id:my-svg-src
            %% @animate target draft-label = text:"Draft sources"
            %% @animate target valid = id:my-svg-valid
            %% @animate target valid-label = text:"Validate diagrams"
            %% @animate target ship = id:my-svg-ship
            %% @animate target ship-label = text:"Publish examples"
            %% @animate group draft-step = draft, draft-label
            %% @animate group valid-step = valid, valid-label
            %% @animate group ship-step = ship, ship-label
            %% @animate point draft-end = draft.right
            %% @animate point valid-mid = valid.center
            %% @animate point ship-callout = offset(ship.top, 0, -18)
            %% @animate mark progress at draft-end shape=dot size=8 fill=#007298
            %% @animate mark ship-note at ship-callout shape=label text=ship fill=#fff4cc stroke=#45842a
            %% @animate at 0ms reveal build-rows effect=fade duration=250ms name=show-build
            %% @animate at show-build.end reveal build-title effect=fade duration=200ms
            %% @animate at show-build.end+150ms reveal draft-step mode=together effect=pop name=show-draft
            %% @animate at show-draft.end move progress to valid-mid duration=650ms ease=in-out name=to-valid
            %% @animate at to-valid.end reveal valid-step mode=together effect=pop name=show-valid
            %% @animate at show-valid.end color valid fill=#fff4cc stroke=#f08c00 duration=250ms restore=true
            %% @animate at show-valid.end+250ms reveal ship-step mode=together effect=pop name=show-ship
            %% @animate at show-ship.end show ship-note effect=fade duration=180ms
            %% @animate at show-ship.end pulse ship scale=1.08 stroke=#45842a duration=450ms
        """,
    },
    {
        "slug": "gitgraph-release-flow",
        "type": "GitGraph",
        "source": "gitgraph-diagram",
        "critique": "Uses stable commit label text for point anchors and avoids hash-like generated classes; some commit classes resolve both outer and inner shapes.",
        "directives": """
            %% @animate v1 duration=5s default-duration=450ms
            %% @animate target init = css:.init
            %% @animate target mmd = text:"mmd"
            %% @animate target md = css:.md
            %% @animate target validator = css:.validator
            %% @animate target merge = css:.commit-merge
            %% @animate target verify = text:"verify"
            %% @animate group commits = init, mmd, md, validator, merge, verify
            %% @animate point from-init = init.center
            %% @animate point to-mmd = mmd.center
            %% @animate point to-merge = merge.center
            %% @animate mark release-token at from-init shape=dot size=7 fill=#1f6feb
            %% @animate at 0ms reveal commits mode=sequence gap=150ms effect=pop name=show-commits
            %% @animate at show-commits.end move release-token to to-mmd duration=700ms ease=out name=to-mmd
            %% @animate at to-mmd.end pulse mmd scale=1.08 duration=300ms
            %% @animate at to-mmd.end+250ms move release-token to to-merge duration=900ms ease=out name=to-merge
            %% @animate at to-merge.end color merge fill=#fff4cc stroke=#f08c00 duration=300ms
            %% @animate at to-merge.end+150ms pulse verify scale=1.06 stroke=#2b8a3e duration=350ms
        """,
    },
    {
        "slug": "ishikawa-root-cause",
        "type": "Ishikawa",
        "source": "ishikawa",
        "critique": "Branch labels are easy to select by text, but exact per-branch line selection still needs future cause/branch syntax.",
        "directives": """
            %% @animate v1 duration=6.5s default-duration=320ms
            %% @animate target problem = text:"Missing diagram polish"
            %% @animate target source = text:"Source coverage"
            %% @animate target styling = text:"Styling"
            %% @animate target validation = text:"Validation"
            %% @animate target docs = text:"Documentation"
            %% @animate target fish-lines = role:edge
            %% @animate group main-causes = source, styling, validation, docs
            %% @animate point source-note = offset(source.top, 0, -24)
            %% @animate mark root-cause at source-note shape=label text=root-cause fill=#fff3bf stroke=#f08c00
            %% @animate at 0ms reveal problem effect=pop duration=360ms
            %% @animate at 360ms trace fish-lines duration=900ms name=draw-fish
            %% @animate at draw-fish.end reveal main-causes mode=sequence gap=320ms effect=fade duration=260ms name=reveal-causes
            %% @animate at reveal-causes.end show root-cause effect=pop duration=260ms name=show-root-cause
            %% @animate at show-root-cause.end pulse source scale=1.04 stroke=#f08c00 duration=420ms restore=true
        """,
    },
    {
        "slug": "kanban-card-flow",
        "type": "Kanban",
        "source": "kanban",
        "critique": "Uses stable card and column IDs; movement is carried by an overlay mark so the board layout remains true.",
        "directives": """
            %% @animate v1 duration=4s default-duration=500ms
            %% @animate target backlog = #my-svg-backlog
            %% @animate target progress = #my-svg-progress
            %% @animate target done = #my-svg-done
            %% @animate target colors = #my-svg-colors
            %% @animate target wrappers = #my-svg-wrappers
            %% @animate target validator = #my-svg-validator
            %% @animate group columns = backlog, progress, done
            %% @animate group cards = colors, wrappers, validator
            %% @animate point from-backlog = colors.right
            %% @animate point to-progress = wrappers.left
            %% @animate point to-done = validator.left
            %% @animate mark work-item at from-backlog shape=ring size=18 stroke=#f08c00 fill=none
            %% @animate at 0ms reveal columns mode=together effect=pop duration=450ms name=show-columns
            %% @animate at show-columns.end reveal cards mode=sequence gap=140ms effect=slide-up duration=420ms name=show-cards
            %% @animate at show-cards.end move work-item to to-progress duration=750ms ease=out name=to-progress
            %% @animate at to-progress.end pulse wrappers scale=1.04 stroke=#f08c00 duration=300ms
            %% @animate at to-progress.end+250ms move work-item to to-done duration=750ms ease=out name=to-done
            %% @animate at to-done.end pulse validator scale=1.05 stroke=#2b8a3e duration=350ms
        """,
    },
    {
        "slug": "mindmap-branch-focus",
        "type": "Mindmap",
        "source": "mindmap",
        "critique": "Combines readable node text with explicit generated edge IDs, which is the safest current branch-level pattern.",
        "directives": """
            %% @animate v1 duration=5s default-duration=300ms
            %% @animate target root = text:"Mermaid examples"
            %% @animate target sources = text:"Sources"
            %% @animate target styling = text:"Styling"
            %% @animate target validation = text:"Validation"
            %% @animate target style-edge = #my-svg-edge_0_4
            %% @animate group branches = sources, styling, validation
            %% @animate point root-out = root.center
            %% @animate point style-mid = style-edge:path(0.5)
            %% @animate mark focus at root-out shape=ring size=18 stroke=#007298
            %% @animate at 0ms reveal root effect=pop duration=350ms name=show-root
            %% @animate at show-root.end move focus to style-mid duration=650ms name=scan-style
            %% @animate at scan-style.end trace style-edge duration=450ms name=trace-style
            %% @animate at trace-style.end reveal branches mode=sequence gap=220ms effect=pop name=show-branches
            %% @animate at show-branches.end pulse styling scale=1.04 stroke=#007298 duration=500ms
        """,
    },
    {
        "slug": "packet-field-scan",
        "type": "Packet",
        "source": "packet-diagram",
        "critique": "Uses full row text plus absolute field centers because packet fields have no semantic IDs yet.",
        "directives": """
            %% @animate v1 duration=5s default-duration=280ms
            %% @animate target title = text:"Example metadata packet"
            %% @animate target header-row = text:"Type 0 3 Version 4 7 Palette id 8 15 Shape id 16 23 Flags 24 31"
            %% @animate target length-row = text:"Diagram source length 32 63"
            %% @animate target hash-a = text:"Content hash 64 95"
            %% @animate target hash-b = text:"Content hash 96 127"
            %% @animate group rows = header-row, length-row, hash-a, hash-b
            %% @animate point type-center = xy(62.5,31)
            %% @animate point version-center = xy(190.5,31)
            %% @animate point palette-center = xy(382.5,31)
            %% @animate point flags-center = xy(894.5,31)
            %% @animate point length-center = xy(510.5,78)
            %% @animate point hash-center = xy(510.5,125)
            %% @animate mark scanner at type-center shape=ring size=18 stroke=#1c7ed6
            %% @animate mark note at xy(62.5,3) shape=label text=bits-0-3 size=10 fill=#e7f5ff stroke=#1c7ed6
            %% @animate at 0ms reveal title effect=fade duration=220ms name=show-title
            %% @animate at show-title.end reveal rows mode=sequence gap=180ms effect=fade duration=260ms name=show-rows
            %% @animate at show-rows.end show scanner effect=fade duration=160ms name=scan-start
            %% @animate at scan-start.end move scanner to version-center duration=380ms name=scan-version
            %% @animate at scan-version.end move scanner to palette-center duration=480ms name=scan-palette
            %% @animate at scan-palette.end move scanner to flags-center duration=650ms name=scan-flags
            %% @animate at scan-flags.end color header-row fill=#fff3bf stroke=#f08c00 duration=280ms restore=true
            %% @animate at scan-flags.end+120ms move scanner to length-center duration=520ms name=scan-length
            %% @animate at scan-length.end move scanner to hash-center duration=520ms name=scan-hash
            %% @animate at scan-hash.end pulse hash-a scale=1.02 stroke=#2b8a3e duration=450ms
        """,
    },
    {
        "slug": "pie-segment-callout",
        "type": "Pie",
        "source": "pie-chart",
        "critique": "Segment classes are compact, but each category selector intentionally affects wedge, percentage, and legend together.",
        "directives": """
            %% @animate v1 duration=4.2s default-duration=450ms
            %% @animate target shapes = .pie-label-shapes
            %% @animate target color-config = .pie-label-color-config
            %% @animate target validation = .pie-label-validation
            %% @animate target syntax = .pie-label-syntax
            %% @animate point note-pos = xy(80%, 20%)
            %% @animate mark note at note-pos shape=label text=Validation fill=#fff4cc stroke=#333E48 size=12
            %% @animate at 0ms reveal shapes mode=together name=show-shapes
            %% @animate at show-shapes.end reveal color-config mode=together name=show-color
            %% @animate at show-color.end reveal validation mode=together name=show-validation
            %% @animate at show-validation.end pulse validation scale=1.06 stroke=#333E48 duration=360ms name=validation-pulse
            %% @animate at validation-pulse.end show note effect=pop duration=260ms
            %% @animate at show-validation.end+520ms reveal syntax mode=together name=show-syntax
        """,
    },
    {
        "slug": "quadrant-point-routing",
        "type": "Quadrant",
        "source": "quadrant-chart",
        "critique": "Uses text labels for exact point selection; plot-space selectors remain future syntax.",
        "directives": """
            %% @animate v1 duration=4s default-duration=360ms
            %% @animate target flowchart = text:"Flowchart"
            %% @animate target c4 = text:"C4"
            %% @animate target pie = text:"Pie"
            %% @animate target wardley = text:"Wardley"
            %% @animate group candidates = flowchart, c4, pie, wardley
            %% @animate point start = pie.center
            %% @animate point candidate = c4.center
            %% @animate point selected = flowchart.center
            %% @animate mark decision at start shape=ring size=18 stroke=#f08c00
            %% @animate at 0ms reveal candidates mode=sequence gap=220ms effect=pop duration=420ms name=reveal-points
            %% @animate at reveal-points.end show decision effect=fade duration=180ms name=show-decision
            %% @animate at show-decision.end move decision to candidate duration=650ms ease=out name=to-candidate
            %% @animate at to-candidate.end move decision to selected duration=850ms ease=in-out name=to-selected
            %% @animate at to-selected.end color flowchart fill=#d3f9d8 stroke=#2b8a3e text=#1b4332 duration=350ms
            %% @animate at to-selected.end pulse flowchart scale=1.06 stroke=#2b8a3e duration=500ms
        """,
    },
    {
        "slug": "radar-series-layering",
        "type": "Radar",
        "source": "radar",
        "critique": "Series-level CSS selectors work; per-axis and per-vertex domain selectors remain missing.",
        "directives": """
            %% @animate v1 duration=4.8s default-duration=650ms
            %% @animate target grid = css:".radarGraticule"
            %% @animate target axes = css:".radarAxisLine"
            %% @animate target labels = css:".radarAxisLabel"
            %% @animate target title = css:".radarTitle"
            %% @animate target target-curve = css:".radarCurve-0"
            %% @animate target current-curve = css:".radarCurve-1"
            %% @animate target current-legend = text:"Current"
            %% @animate group frame = grid, axes, labels, title
            %% @animate point current-note = offset(current-legend.center, 54, 8)
            %% @animate mark note at current-note shape=label text=coverage fill=#ffffff stroke=#45842a
            %% @animate at 0ms reveal frame mode=together effect=fade duration=500ms name=show-frame
            %% @animate at show-frame.end reveal target-curve effect=pop duration=650ms name=show-target
            %% @animate at show-target.end+180ms reveal current-curve effect=pop duration=650ms name=show-current
            %% @animate at show-current.end pulse current-curve scale=1.03 stroke=#1f7a35 duration=420ms restore=true
            %% @animate at show-current.end+120ms reveal note effect=pop duration=300ms
        """,
    },
    {
        "slug": "requirement-traceability-thread",
        "type": "Requirement",
        "source": "requirement-diagram",
        "critique": "Exact requirement and relation IDs make this a good candidate for current directive syntax, but edge direction must be taken from --list-elements.",
        "directives": """
            %% @animate v1 duration=5.2s default-duration=650ms
            %% @animate target folder = id:my-svg-examples_folder
            %% @animate target examples = id:my-svg-diagram_examples
            %% @animate target frontmatter = id:my-svg-frontmatter_config
            %% @animate target examples-link = id:my-svg-examples_folder-diagram_examples-0
            %% @animate target frontmatter-link = id:my-svg-frontmatter_config-diagram_examples-0
            %% @animate point handoff-start = folder.right
            %% @animate point examples-end = examples.left
            %% @animate point frontmatter-end = frontmatter.right
            %% @animate mark trace-token at handoff-start shape=dot size=9 fill=#1f6feb
            %% @animate mark verified-note at offset(examples.top, 0, -28) shape=label text=verified fill=#fff4cc stroke=#45842a
            %% @animate at 0ms reveal folder effect=pop name=show-folder
            %% @animate at show-folder.end reveal examples effect=pop name=show-examples
            %% @animate at show-examples.end trace examples-link duration=750ms name=trace-examples
            %% @animate at trace-examples.end move trace-token to examples-end duration=800ms name=to-examples
            %% @animate at to-examples.end pulse examples scale=1.04 stroke=#1f6feb duration=350ms
            %% @animate at to-examples.end+150ms reveal verified-note effect=pop duration=350ms
            %% @animate at to-examples.end+450ms reveal frontmatter effect=pop name=show-frontmatter
            %% @animate at show-frontmatter.end trace frontmatter-link duration=750ms name=trace-frontmatter
            %% @animate at trace-frontmatter.end move trace-token to frontmatter-end duration=700ms name=to-frontmatter
        """,
    },
    {
        "slug": "sankey-flow-handoff",
        "type": "Sankey",
        "source": "sankey",
        "critique": "Uses node IDs and all-flow tracing; precise individual link syntax is still a gap.",
        "directives": """
            %% @animate v1 duration=4.8s default-duration=360ms
            %% @animate target source = id:node-1
            %% @animate target markdown = id:node-2
            %% @animate target render = id:node-3
            %% @animate target review = id:node-4
            %% @animate target published = id:node-5
            %% @animate target flows = role:edge
            %% @animate group first-hop = markdown, render
            %% @animate point send = source.right
            %% @animate point review-in = review.left
            %% @animate point done = published.left
            %% @animate mark packet at send shape=dot size=9 fill=#1971c2
            %% @animate at 0ms reveal source effect=pop name=show-source
            %% @animate at show-source.end trace flows duration=700ms name=trace-flows
            %% @animate at trace-flows.end reveal first-hop mode=together effect=pop duration=300ms name=show-middle
            %% @animate at show-middle.end move packet to review-in duration=850ms ease=in-out name=handoff
            %% @animate at handoff.end reveal review effect=pop duration=300ms name=show-review
            %% @animate at show-review.end color review fill=#fff3bf stroke=#f08c00 duration=300ms restore=true
            %% @animate at show-review.end move packet to done duration=700ms ease=out name=publish
            %% @animate at publish.end reveal published effect=pop duration=300ms
            %% @animate at publish.end pulse published scale=1.04 stroke=#2b8a3e duration=450ms
        """,
    },
    {
        "slug": "sequence-message-token",
        "type": "Sequence",
        "source": "sequence-diagram",
        "critique": "Uses broad message tracing and explicit points, because current sequence SVG does not expose semantic message selectors.",
        "directives": """
            %% @animate v1 duration=4s default-duration=300ms
            %% @animate target actors = role:actor
            %% @animate target messages = role:edge
            %% @animate target labels = role:label
            %% @animate point client-send = xy(18%, 26%)
            %% @animate point api-receive = xy(50%, 26%)
            %% @animate point db-receive = xy(82%, 42%)
            %% @animate mark request at client-send shape=dot size=8 fill=#1971c2
            %% @animate at 0ms reveal actors mode=together effect=pop duration=300ms name=show-actors
            %% @animate at show-actors.end trace messages duration=900ms name=trace-messages
            %% @animate at show-actors.end move request to api-receive duration=520ms name=to-api
            %% @animate at to-api.end move request to db-receive duration=620ms name=to-db
            %% @animate at trace-messages.end reveal labels mode=sequence gap=90ms effect=fade duration=160ms
            %% @animate at to-db.end hide request effect=fade duration=180ms
        """,
    },
    {
        "slug": "state-dwell-token",
        "type": "State",
        "source": "state-diagram",
        "critique": "Demonstrates dwell with marks and color; future wait/dwell verbs would reduce directive count.",
        "directives": """
            %% @animate v1 duration=5.5s default-duration=260ms
            %% @animate target draft = text:"Draft"
            %% @animate target review = text:"Review"
            %% @animate target approved = text:"Approved"
            %% @animate point draft-out = draft.right
            %% @animate point review-in = review.left
            %% @animate point approved-in = approved.left
            %% @animate point review-badge = offset(review.top-right, -8, 8)
            %% @animate mark token at draft-out shape=dot size=9 fill=#1971c2
            %% @animate mark wait-label at review-badge shape=label text=waiting size=10 fill=#fff3bf stroke=#f08c00
            %% @animate at 0ms reveal draft effect=pop duration=250ms name=show-draft
            %% @animate at show-draft.end move token to review-in duration=700ms ease=out name=submit-hop
            %% @animate at submit-hop.end reveal review effect=pop duration=250ms name=show-review
            %% @animate at show-review.end color review fill=#fff3bf stroke=#f08c00 text=#5c3d00 duration=250ms name=review-active
            %% @animate at review-active.end show wait-label effect=fade duration=150ms name=show-wait
            %% @animate at show-wait.end pulse review scale=1.02 stroke=#f08c00 duration=900ms name=review-dwell
            %% @animate at review-dwell.end hide wait-label effect=fade duration=150ms
            %% @animate at review-dwell.end move token to approved-in duration=650ms ease=in-out name=approve-hop
            %% @animate at approve-hop.end reveal approved effect=pop duration=250ms name=show-approved
            %% @animate at show-approved.end color approved fill=#d3f9d8 stroke=#2b8a3e text=#1b4332 duration=250ms
        """,
    },
    {
        "slug": "timeline-milestone-scan",
        "type": "Timeline",
        "source": "timeline",
        "critique": "Uses visible timeline labels and generated timeline classes; dense timelines need shorter gaps.",
        "directives": """
            %% @animate v1 duration=4s default-duration=500ms
            %% @animate target plan = text:"Plan"
            %% @animate target build = text:"Build"
            %% @animate target validate = text:"Validate"
            %% @animate target events = .timeline-event
            %% @animate target lines = .timeline-line
            %% @animate point start = plan.bottom
            %% @animate point finish = validate.bottom
            %% @animate mark progress at start shape=dot size=9 fill=#007298
            %% @animate at 0ms reveal lines effect=draw duration=700ms name=draw-lines
            %% @animate at draw-lines.end reveal plan effect=pop name=show-plan
            %% @animate at show-plan.end reveal build effect=pop name=show-build
            %% @animate at show-build.end reveal validate effect=pop name=show-validate
            %% @animate at show-validate.end reveal events mode=sequence gap=140ms effect=fade name=show-events
            %% @animate at show-events.end move progress to finish via=build.bottom duration=1100ms ease=in-out name=to-finish
            %% @animate at to-finish.end pulse validate scale=1.04 stroke=#007298 duration=450ms
        """,
    },
    {
        "slug": "treemap-hierarchy-focus",
        "type": "Treemap",
        "source": "treemap",
        "critique": "Label selectors work for readable sections/leaves; tiny hidden leaves are intentionally not emphasized.",
        "directives": """
            %% @animate v1 duration=4.5s default-duration=320ms
            %% @animate target sources = text:"Sources"
            %% @animate target config = text:"Configuration"
            %% @animate target validation = text:"Validation"
            %% @animate target mmd = text:".mmd"
            %% @animate target docs = text:".md"
            %% @animate target colors = text:"colors"
            %% @animate target shapes = text:"shapes"
            %% @animate target render = text:"render"
            %% @animate group sections = sources, config, validation
            %% @animate group leaves = mmd, docs, colors, shapes, render
            %% @animate point render-callout = offset(render.top, 0, -24)
            %% @animate mark focus at render.center shape=ring size=22 stroke=#652f6c
            %% @animate mark note at render-callout shape=label text=render fill=#ffffff stroke=#652f6c
            %% @animate at 0ms reveal sections mode=sequence gap=180ms effect=pop name=reveal-sections
            %% @animate at reveal-sections.end reveal leaves mode=sequence gap=120ms effect=pop name=reveal-leaves
            %% @animate at reveal-leaves.end show focus effect=fade duration=180ms
            %% @animate at reveal-leaves.end+120ms color render fill=#eadcff stroke=#652f6c duration=320ms
            %% @animate at reveal-leaves.end+180ms show note effect=slide-up duration=260ms
            %% @animate at reveal-leaves.end+260ms pulse render scale=1.035 stroke=#652f6c duration=420ms
        """,
    },
    {
        "slug": "treeview-directory-scan",
        "type": "Treeview",
        "source": "treeview",
        "critique": "Labels are exact text targets; branch lines are only emphasized as a group because text-selected folder candidates can overlap line containers.",
        "directives": """
            %% @animate v1 duration=5s default-duration=450ms
            %% @animate target examples = text:"examples/"
            %% @animate target mermaid = text:"mermaid/"
            %% @animate target scripts = text:"scripts/"
            %% @animate target flow-mmd = text:"flowchart.mmd"
            %% @animate target sequence-mmd = text:"sequence-diagram.mmd"
            %% @animate target validator = text:"validate-skills.py"
            %% @animate group folders = examples, mermaid, scripts
            %% @animate group key-files = flow-mmd, sequence-mmd, validator
            %% @animate point scan-start = offset(examples.right, 14, 0)
            %% @animate point scan-flow = offset(flow-mmd.right, 12, 0)
            %% @animate point scan-sequence = offset(sequence-mmd.right, 12, 0)
            %% @animate point scan-validator = offset(validator.right, 12, 0)
            %% @animate mark scan at scan-start shape=ring size=12 stroke=#1f6feb
            %% @animate at 0ms reveal folders mode=sequence gap=220ms effect=slide-left name=show-folders
            %% @animate at show-folders.end reveal key-files mode=sequence gap=260ms effect=fade name=show-files
            %% @animate at show-files.end move scan to scan-flow duration=650ms ease=out name=scan-flow
            %% @animate at scan-flow.end move scan to scan-sequence duration=650ms ease=out name=scan-sequence
            %% @animate at scan-sequence.end move scan to scan-validator duration=850ms ease=out name=scan-validator
            %% @animate at scan-validator.end pulse validator scale=1.06 stroke=#2b8a3e duration=450ms
        """,
    },
    {
        "slug": "journey-stage-progress",
        "type": "Journey",
        "source": "user-journey",
        "critique": "Uses exact task/section text; no stable IDs are emitted, so broad column classes remain group-only tools.",
        "directives": """
            %% @animate v1 duration=4s default-duration=300ms
            %% @animate target discover = text:"Discover"
            %% @animate target open-examples = text:"Open examples folder"
            %% @animate target pick-type = text:"Pick a diagram type"
            %% @animate target inspect = text:"Inspect"
            %% @animate group discover-start = discover, open-examples
            %% @animate point open-out = open-examples.right
            %% @animate point pick-in = pick-type.left
            %% @animate point inspect-in = inspect.left
            %% @animate mark progress at open-out shape=dot size=8 fill=#1971c2
            %% @animate at 0ms reveal discover-start mode=together effect=pop name=show-discover
            %% @animate at show-discover.end move progress to pick-in duration=600ms ease=in-out name=advance
            %% @animate at advance.end reveal pick-type effect=pop duration=300ms name=show-pick
            %% @animate at show-pick.end move progress to inspect-in duration=650ms ease=in-out name=to-inspect
            %% @animate at to-inspect.end reveal inspect effect=pop duration=300ms
            %% @animate at to-inspect.end pulse inspect scale=1.03 stroke=#45842a duration=280ms restore=true
        """,
    },
    {
        "slug": "venn-coverage-focus",
        "type": "Venn",
        "source": "venn",
        "critique": "Generated .venn-sets-* classes are strong current syntax for set/intersection choreography.",
        "directives": """
            %% @animate v1 duration=4s default-duration=520ms
            %% @animate target source = .venn-sets-source
            %% @animate target markdown = .venn-sets-markdown
            %% @animate target styled = .venn-sets-styled
            %% @animate target pair = .venn-sets-markdown-source
            %% @animate target theme = .venn-sets-source-styled
            %% @animate target render = .venn-sets-markdown-styled
            %% @animate target all = .venn-sets-markdown-source-styled
            %% @animate group sets = source, markdown, styled
            %% @animate group overlaps = pair, theme, render
            %% @animate point all-callout = offset(all.top, 0, -26)
            %% @animate mark focus at all.center shape=ring size=52 stroke=#1f6feb
            %% @animate mark note at all-callout shape=label text=coverage fill=#ffffff stroke=#1f6feb
            %% @animate at 0ms reveal sets mode=sequence gap=260ms effect=fade name=show-sets
            %% @animate at show-sets.end reveal overlaps mode=sequence gap=180ms effect=fade name=show-overlaps
            %% @animate at show-overlaps.end reveal all effect=pop duration=420ms name=show-all
            %% @animate at show-all.end show focus effect=pop duration=260ms
            %% @animate at show-all.end+120ms pulse all scale=1.05 stroke=#1f6feb duration=520ms
            %% @animate at show-all.end+260ms show note effect=slide-up duration=300ms
        """,
    },
    {
        "slug": "wardley-value-chain",
        "type": "Wardley",
        "source": "wardley",
        "critique": "Uses text labels for components and xy points for precise symbols because component IDs are absent.",
        "directives": """
            %% @animate v1 duration=4.2s default-duration=300ms
            %% @animate target reader = text:"Reader"
            %% @animate target wrapper = text:"Markdown wrapper"
            %% @animate target source = text:"MMD source"
            %% @animate target frontmatter = text:"Frontmatter config"
            %% @animate target vocabulary = text:"Shape vocabulary"
            %% @animate target renderer = text:"Mermaid renderer"
            %% @animate target validator = text:"Repository validator"
            %% @animate target links = css:".wardley-link"
            %% @animate target trends = css:".wardley-trend"
            %% @animate group chain = reader, wrapper, source, frontmatter, vocabulary, renderer, validator
            %% @animate point reader-pos = xy(906.8, 95.4)
            %% @animate point source-pos = xy(789.28, 199.2)
            %% @animate point frontmatter-pos = xy(608.48, 259.68)
            %% @animate point vocabulary-pos = xy(481.92, 325.2)
            %% @animate point renderer-pos = xy(843.52, 400.8)
            %% @animate mark value at reader-pos shape=dot size=8 fill=#1971c2
            %% @animate mark evolved at frontmatter-pos shape=ring size=22 stroke=#dc3545
            %% @animate at 0ms reveal chain mode=sequence gap=130ms effect=pop duration=260ms name=reveal-map
            %% @animate at reveal-map.end trace links duration=650ms name=trace-dependencies
            %% @animate at trace-dependencies.end move value to source-pos duration=520ms ease=in-out name=to-source
            %% @animate at to-source.end move value to renderer-pos via=frontmatter-pos|vocabulary-pos duration=900ms ease=in-out name=to-renderer
            %% @animate at to-renderer.end trace trends duration=500ms name=show-evolution
            %% @animate at show-evolution.end show evolved effect=fade duration=180ms
            %% @animate at show-evolution.end color frontmatter stroke=#dc3545 text=#7a1f1f duration=300ms restore=true
        """,
    },
    {
        "slug": "xy-chart-series-reveal",
        "type": "XY Chart",
        "source": "xy-chart",
        "critique": "Uses chart-level roles and xy points because individual bars and plot-domain points are not addressable yet.",
        "directives": """
            %% @animate v1 duration=4.8s default-duration=320ms
            %% @animate target bars = role:node
            %% @animate target lines = role:edge
            %% @animate target labels = role:label
            %% @animate point checked = xy(84%, 34%)
            %% @animate point callout = xy(76%, 18%)
            %% @animate mark milestone at checked shape=ring size=18 stroke=#1f6feb
            %% @animate mark note at callout shape=label text=checked fill=#ffffff stroke=#1f6feb
            %% @animate at 0ms reveal labels mode=together effect=fade duration=300ms name=show-frame
            %% @animate at show-frame.end reveal bars effect=pop duration=500ms name=show-bars
            %% @animate at show-bars.end trace lines duration=650ms name=show-line
            %% @animate at show-line.end show milestone effect=pop duration=220ms
            %% @animate at show-line.end+120ms show note effect=fade duration=220ms
        """,
    },
    {
        "slug": "zenuml-frontmatter-render",
        "type": "ZenUML",
        "source": "zenuml",
        "critique": "Relies on explicit xy points and broad item/message groups because data-participant attributes are not selectable yet.",
        "directives": """
            %% @animate v1 duration=5s default-duration=300ms
            %% @animate target frame = role:item
            %% @animate point author-send = xy(54, 87)
            %% @animate point docs-open = xy(259, 87)
            %% @animate point repo-load = xy(461, 119)
            %% @animate point docs-return = xy(259, 151)
            %% @animate mark token at author-send shape=dot size=8 fill=#1971c2
            %% @animate at 0ms reveal frame mode=sequence gap=120ms effect=fade duration=240ms name=show-frame
            %% @animate at show-frame.end move token to docs-open duration=500ms name=open-docs
            %% @animate at open-docs.end move token to repo-load duration=500ms name=load-repo
            %% @animate at load-repo.end move token to docs-return duration=500ms name=return-text
            %% @animate at return-text.end hide token effect=fade duration=180ms
        """,
    },
]


def directive_block(raw: str) -> str:
    return "\n".join(line.rstrip() for line in textwrap.dedent(raw).strip().splitlines())


def write_example(example: dict[str, str]) -> None:
    source = SOURCE_DIR / f"{example['source']}.mmd"
    target = OUTPUT_DIR / f"{example['slug']}.mmd"
    base = source.read_text(encoding="utf-8").rstrip()
    block = directive_block(example["directives"])
    target.write_text(
        f"{base}\n\n%% Directive critique: {example['critique']}\n{block}\n",
        encoding="utf-8",
    )


def write_manifest() -> None:
    manifest = [
        {
            "slug": example["slug"],
            "type": example["type"],
            "source": f".agents/skills/mermaid-animated-svg/assets/examples/mermaid/{example['source']}.mmd",
            "directiveSource": (
                ".agents/skills/mermaid-animated-svg/assets/examples/"
                f"mermaid-animation-directives/by-type/{example['slug']}.mmd"
            ),
            "critique": example["critique"],
        }
        for example in EXAMPLES
    ]
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_critique() -> None:
    lines = [
        "# Mermaid Directive Example Critique",
        "",
        "This file is generated by `scripts/generate-mermaid-directive-examples.py`.",
        "Each row records the reason the by-type directive example is useful and the current language limitation it exposes.",
        "",
        "| Type | Example | Critique |",
        "| --- | --- | --- |",
    ]
    for example in EXAMPLES:
        lines.append(f"| {example['type']} | `{example['slug']}.mmd` | {example['critique']} |")
    lines.append("")
    (OUTPUT_DIR / "CRITIQUE.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for example in EXAMPLES:
        write_example(example)
    write_manifest()
    write_critique()
    print(f"Wrote {len(EXAMPLES)} directive examples to {OUTPUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
