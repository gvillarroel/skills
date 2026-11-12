Target Codex desktop with a CLI fallback; exact desktop renderer acceptance is unknown. Treat skills/codex-plugin-ui/ as a read-only resource. Write task files only outside that skill, within this workspace. Use only this supplied skill and normal local tools. Do not read other skills, repository docs, installed examples, personal configuration or anything outside this workspace. Do not install, deploy, change settings or contact a live service. Keep temporary state task-local.

Build a clean workflow inspection interface.

The synthetic workflow has nodes ingest, validate, enrich, store, publish and notify.
Their display names match their IDs. Directed edges: ingest->validate (120 jobs/hour),
validate->enrich (110), validate->notify (10), enrich->store (110), store->publish (105),
publish->notify (105). These rates are observations, not a conserved flow model.
The selected node is enrich, with latency [90,100,95,130,160,180] ms at UTC hours
[0,4,8,12,16,20]. Its objective is 150 ms. State is degraded, owner is Data.
All other nodes are healthy. Provide exact values and clear units. No production
connection or editing action is requested.

Create a self-contained interactive frontend prototype at deliverables/workspace.html.
Keep scripts/styles/data local and dependency-free. Include a selectable directed
graph, a latency chart, exact values, a filter, a selected-item inspector and a
clean narrow layout. This task asks for the authored view, not a complete MCP
package or a claimed host installation. Write deliverables/review.json with
keys host, route, alternatives (array), testsPerformed (array), untested (array),
and critique (array of observation/userCost/repair objects). Run meaningful local
checks using available tools and describe their real scope.
