Build the offline delivery flow by running this exact command, then inspect the resulting artifacts. Keep all files under this workspace and treat skills/d3/ as read-only. Do not inspect acceptance fixtures or other skills.

```bash
uv run --script skills/d3/scripts/build_contract_artifact.py --kind flow --output flow.html --decision-output flow.json --title "Delivery stages" --description "Capture to release" --route flow --colorset colorset2 --pattern-id d3-delivery-stages --svg-id delivery --reason "Ordered transfers" --flow-node Capture --flow-node Review --flow-node Release --link "Capture->Review" --link "Review->Release" --link-value 8 --link-value 6
```
