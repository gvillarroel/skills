Create exactly `flow.html`, `decision.json`, and `flow.svg` in the workspace root.
Treat `skills/d3/` as read-only. Use only that copied skill and local tools;
do not read outside the workspace or use the network.

After reading the skill and its required help, execute this build command:

```sh
python skills/d3/scripts/build_contract_artifact.py --kind flow --output flow.html --decision-output decision.json --title "Release flow" --description "Three ordered release stages." --route flow --colorset colorset1 --pattern-id d3-flow-spine --svg-id release-flow --reason "Ordered workflow" --flow-node Draft --flow-node Review --flow-node Publish --link "Draft->Review" --link "Review->Publish" --link-value 12 --link-value 8
```

Run each matching contract check and render command below in a separate tool call, exactly as written:

```sh
python skills/d3/scripts/check_self_contained_html.py flow.html
```

```sh
python skills/d3/scripts/check_palette_contract.py flow.html --colorset colorset1
```

```sh
uv run --script skills/d3/scripts/render_d3_svg.py flow.html --output flow.svg
```

```sh
python skills/d3/scripts/check_visual_contract.py flow.svg --require-id release-flow --require-class flow-node:3 --require-class link:2 --require-class link-value:2 --require-text Draft --require-text Review --require-text Publish --require-text 12 --require-text 8
```

Report the result. Keep all three labels and both link values.
