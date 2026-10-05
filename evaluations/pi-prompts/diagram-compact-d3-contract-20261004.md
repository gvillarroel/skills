Create an offline D3 HTML for a three-stage process with labels Capture, Inspect, Publish and directed links Capture->Inspect (4), Inspect->Publish (7). Use colorset1, SVG ID workflow, pattern ID d3-review-flow, title Workflow, route diagram and a factual decision reason. Keep all labels and arrowheads readable at the displayed size. Omit dimensions so the skill chooses its normal layout.

Write artifacts/workflow.html, artifacts/decision.json, artifacts/workflow.svg and artifacts/preview.png. Run this exact builder command after its required help command:

```bash
python skills/d3/scripts/build_contract_artifact.py --kind flow --output artifacts/workflow.html --decision-output artifacts/decision.json --title Workflow --description Review --route diagram --colorset colorset1 --pattern-id d3-review-flow --svg-id workflow --reason Relationships --flow-node Capture --flow-node Inspect --flow-node Publish --link "Capture->Inspect" --link-value 4 --link "Inspect->Publish" --link-value 7
```

Validate and render the result with the bundled helpers, then inspect the preview. The copied skills/d3 directory is read-only. Keep generated files in this workspace outside skills/. Do not browse the network or discover other skills.
