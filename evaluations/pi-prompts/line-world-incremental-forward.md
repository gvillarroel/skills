Read ../prompt.md first. The loaded skills/line-world-video directory is
read-only. Write task files in the workspace. No editor account or new film is
needed: this request is about making a small revision reproducible.

Create this existing project input as film/story.json:
{"language":"en","voice":"Nyla","scenes":[
 {"id":"observe","clipSeconds":8,"essentialAnimationSeconds":5,"script":"First inspect the data and define the prediction target."},
 {"id":"split","clipSeconds":9,"essentialAnimationSeconds":6,"script":"Keep sixty percent for training, twenty for validation, and twenty for the final test."},
 {"id":"regularize","clipSeconds":8,"essentialAnimationSeconds":5,"script":"Compare a baseline and tune regularization using validation evidence."},
 {"id":"evaluate","clipSeconds":8,"essentialAnimationSeconds":5,"script":"Evaluate the selected model once on the untouched test partition."}]}

Create film/cues.json with exactly these existing cues:
{"scenes":[
 {"id":"observe","cues":[{"id":"data","target":"source-table","at":1.4,"travelSeconds":0.25}]},
 {"id":"split","cues":[{"id":"train","target":"train-60","at":1.5,"travelSeconds":0.25},{"id":"validation","target":"validation-20","at":2.5,"travelSeconds":0.25},{"id":"test","target":"test-20","at":3.2,"travelSeconds":0.25}]},
 {"id":"regularize","cues":[{"id":"baseline","target":"baseline-bar","at":2.1,"travelSeconds":0.25}]},
 {"id":"evaluate","cues":[{"id":"holdout","target":"test-score","at":3.6,"travelSeconds":0.25}]}]}

Revise only the split scene's test cue: its measured arrival is now 3.8 seconds
and its travel should take 0.18 seconds. Keep both other percentages distinct.
For the shared visual theme, make text five percent larger and use #4f4f4f as
the secondary highlight. Keep the main red and the approved narration intact.
Use the bundled reusable workflow so a later creator can repeat this edit with
a small patch instead of rewriting complete lists or source code. Inspect the
relevant part of the project rather than printing the complete document.

Save a bounded inspection as film/inspection.json, a repeatable patch as
film/changes.json, the applied-change receipt as film/edit-report.json and the
detailed local render plan as film/render-plan.json. Also leave the final
film/story.json, film/cues.json, film/theme.json and film/theme.css. Do not invent
prior render receipts: this project has no local renders yet. Explain what
needs real visual/audio review; this data edit is not an audio verification.
