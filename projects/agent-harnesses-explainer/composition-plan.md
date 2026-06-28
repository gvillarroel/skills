# Composition Plan

## Video Direction

- format: 1280x720 landscape, five-shot silent Spanish explainer.
- source anchors: `harness`, `agente`, `ayudante de codificación`, `modelo`, `herramientas`, `pruebas`, `trazas`, `sandbox`, `evaluación`.
- palette/type source: existing project palette and system sans typography.
- safe zones: keep primary text in the top 130 px and key diagrams between x 80-1200 and y 180-620.
- caption policy: no external captions; on-screen Spanish copy is part of the video.
- rhythm: each shot needs a visible mid-shot state change, not only an entrance and hold.
- held scenes: the final definition holds in the last four seconds.
- negative list: no GSAP, no decorative status bars, no chapter rail, no progress widgets, no purely decorative motion.

## Critique Of The First Render

- Scene 1 had the right idea, but the task path and harness enclosure were too quiet in the first contact-sheet frame.
- Scene 2 was the strongest scene because the radial loop and trace stack gave the viewer a visible mechanism.
- Scene 3 was too close to a row of small web cards; the tool chain needed larger panels, stronger route hierarchy, and a test gate that clearly authorizes the patch.
- Scene 4 had correct facts but too many small checklist items in a dense card. The improved version should make "blocked risky action" and "evidence produced" the focal events.
- Scene 5 was readable, but the closing definition should receive more visual weight than the secondary lane labels.

## Scene 1 - Model Versus Harness

- id: `s01-model-vs-harness`
- duration: 9 seconds
- source anchors: `harness`, `modelo`, `herramientas`, `pruebas`
- scene job: definition hook
- viewer task: distinguish inner model from outer operating system
- composition choice: centered hero with enclosure
- rejected alternatives: split screen, because it would make model and harness look like peer products
- choice rationale: the enclosure is the concept; the model sits inside a runtime chassis
- focal: central model core surrounded by harness frame
- roles: model as core, harness as boundary, modules as runtime capabilities, packet as task identity
- armature: centered frame with four corner modules and left-to-right task path
- validation checks: harness word large enough in contact sheet; task packet visibly travels through frame

## Scene 2 - Agent Loop

- id: `s02-agent-loop`
- duration: 11 seconds
- source anchors: `agente`, `trazas`
- scene job: mechanism
- viewer task: follow a repeated cycle
- composition choice: radial hub
- rejected alternatives: linear pipeline, because it would hide retries and observation loops
- choice rationale: the loop makes repeated observation and verification visible
- focal: moving packet on loop
- roles: nodes as phases, packet as action state, stack as durable trace
- armature: radial loop with side evidence stack
- validation checks: active node changes and trace stack grows

## Scene 3 - Coding Tool Chain

- id: `s03-coding-workflow`
- duration: 12 seconds
- source anchors: `ayudante de codificación`, `herramientas`, `pruebas`
- scene job: concrete coding use case
- viewer task: trace a task through tools into a validated patch
- composition choice: full-width flow spine
- rejected alternatives: modular board, because equal cards hide order and causality
- choice rationale: the viewer must see that tests gate the patch
- focal: thick route from task to validated patch
- roles: panels as tools, packet as task, test gate as authorization, patch as output
- armature: left-to-right spine with a dominant test gate near the end
- validation checks: panels readable in contact sheet; route does not collide with labels; patch appears after test gate

## Scene 4 - Boundaries And Evidence

- id: `s04-boundaries-evidence`
- duration: 11 seconds
- source anchors: `sandbox`, `trazas`, `evaluación`
- scene job: comparison and proof
- viewer task: compare chat-only model against model with control gates
- composition choice: split screen
- rejected alternatives: centered hero, because the before/after contrast is the lesson
- choice rationale: split screen makes the harness side visibly safer and more auditable
- focal: blocked risky action on the harness side
- roles: left column as unbounded answer, right column as gated runtime, evidence cards as outputs
- armature: mirrored columns with the right side winning through gates
- validation checks: risky action block is visible; trace and evaluation are distinct cards

## Scene 5 - Closing Formula

- id: `s05-closing-formula`
- duration: 9 seconds
- source anchors: `harness`, `ayudante de codificación`, `modelo`, `herramientas`, `pruebas`
- scene job: outro definition
- viewer task: remember one formula and one definition
- composition choice: centered hero with held read
- rejected alternatives: dense process recap, because the ending should simplify
- choice rationale: the final formula needs to be remembered more than inspected
- focal: final definition card
- roles: tiles as ingredients, lane labels as secondary, definition as final memory
- armature: centered formula above held definition
- validation checks: final definition readable in full-size frame and contact sheet
