Create an offline directed network for Gateway, Queue and Output. Show two distinct Gateway->Queue links, a Queue->Gateway return, Queue->Output and an Output->Output self-loop. Use readable actual labels and visible arrowheads. Preserve a 720 by 400 canvas. Use colorset1, title Workflow and SVG ID network. Execute this exact command after the required builder help command:

```bash
python skills/d3/scripts/build_contract_artifact.py --kind network --output artifacts/network.html --decision-output artifacts/decision.json --title Workflow --description Network --route diagram --colorset colorset1 --pattern-id d3-network-flow --svg-id network --reason Relationships --width 720 --height 400 --node Gateway=primary --node Queue=muted --node Output=neutral --link "Gateway->Queue" --link "Gateway->Queue" --link "Queue->Gateway" --link "Queue->Output" --link "Output->Output"
```

Deliver artifacts/network.html, artifacts/decision.json, artifacts/network.svg and artifacts/preview.png. Validate and inspect the rendered geometry and every endpoint. Keep skills/d3 read-only; all outputs belong in this workspace outside skills/. Do not browse the network or discover other skills.
