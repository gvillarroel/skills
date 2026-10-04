Create a small native PlantUML delivery architecture using Colorset 1 and
the skill's normal styling. Save editable source at `source/priority.puml`.
It must show a component named Intake linked to a component named Review,
Review linked to a database named Record, and Record linked to a cloud
named Archive. Keep the four labels and the three directed relationships
exactly as stated. The diagram title is "Delivery architecture".

Also create `source/layers.puml`, an ArchiMate diagram showing the seven
layer roles Business, Application, Technology, Motivation, Strategy,
Physical, and Implementation as separately labeled native layer elements,
with one relationship from Business to Application and one from
Application to Technology. Use the supplied native authoring references
for valid grammar rather than inventing custom shapes.

Use the bundled render-and-validate workflow with the normal local
PlantUML installation. Create exact `renders/svg/priority.svg`,
`renders/png/priority.png`, `renders/svg/layers.svg`, `renders/png/layers.png`, and
`render-report.json`. Apply the editable themes through the renderer.
Preserve native symbols, compartments, and complete directed heads.

Use only the current workspace, the copied skill, and normal installed
tools. Treat `skills/plantuml-colorset-renderer/` as read-only. Do not read
acceptance examples, sibling skills, parent run records, repository context,
or outside source files. Keep all task files outside the copied skill.
