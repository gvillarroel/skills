Create a compact public synthetic expedition dossier with four PlantUML
non-UML diagrams. Use colorset2 consistently, preserve the facts below, and
keep category bodies as opaque solid fills without decorative outlines.
Meaningful network lines, schedule measurements and dependencies, and tree
connections must remain visible. Use exactly black or white text according to
the actual painted backing. Directional shafts and complete heads must have
at least 3:1 contrast against every crossed backing.

- `input/expedition-map.puml`: a mind map rooted at Expedition. Its three main
  branches are Preparation (Permits and Instrument calibration), Fieldwork
  (Sampling and Weather), and Delivery (Analysis and Archive).
- `input/work-breakdown.puml`: a work breakdown structure rooted at Survey.
  Preparation contains Permit and Calibration. Execution contains Transect and
  Samples. Delivery contains Analysis and Deposit.
- `input/survey-schedule.puml`: a Gantt schedule beginning 2026-11-02. Intake
  lasts 2 days. Calibrate lasts 3 days and starts after Intake ends. Survey
  lasts 4 days and starts after Calibrate ends. Show both dependencies.
- `input/lab-network.puml`: a network diagram with one network named Lab
  network, address 192.0.2.0/24. It connects a Workstation at 192.0.2.10 and a
  Sample server at 192.0.2.20. The node labels must display the given names and
  addresses.

Use the normal local `plantuml` command on PATH. Render all four sources as
SVG and PNG with root `rendered`, preserving the requested filenames. Required
delivery files are `rendered/svg/expedition-map.svg`,
`rendered/png/expedition-map.png`, `rendered/svg/work-breakdown.svg`,
`rendered/png/work-breakdown.png`, `rendered/svg/survey-schedule.svg`,
`rendered/png/survey-schedule.png`, `rendered/svg/lab-network.svg`, and
`rendered/png/lab-network.png`. Save render evidence in `render-report.json` and
the bundled report validator's JSON result in `validation.json`. Confirm the
PNG outputs derive from the finished SVG.

Inspect all four diagrams in both formats. Write `review.md` with a concise
check of branch membership, task duration/dependencies, network membership and
addresses, native category styling, text backings, and connector contrast.

Treat `skills/plantuml-colorset-renderer/` as read-only. Write all task files in
this workspace. Use only the loaded skill and normal local tools. Do not read
acceptance fixtures, sibling skills, repository documents, harness metadata,
ancestor Git state, or parent files other than the supplied prompt. Do not use
network access.
