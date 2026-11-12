Target Google Cloud Gemini Enterprise with its documented v0.9 composite catalog. Treat skills/gemini-enterprise-ui/ as a read-only resource. Write task files only outside that skill, within this workspace. Use only this supplied skill and normal local tools. Do not read other skills, repository docs, installed examples, personal configuration or anything outside this workspace. Do not install, deploy, change settings or contact a live service. Keep temporary state task-local.

Build a clean workflow inspection interface.

The synthetic workflow has nodes ingest, validate, enrich, store, publish and notify.
Their display names match their IDs. Directed edges: ingest->validate (120 jobs/hour),
validate->enrich (110), validate->notify (10), enrich->store (110), store->publish (105),
publish->notify (105). These rates are observations, not a conserved flow model.
The selected node is enrich, with latency [90,100,95,130,160,180] ms at UTC hours
[0,4,8,12,16,20]. Its objective is 150 ms. State is degraded, owner is Data.
All other nodes are healthy. Provide exact values and clear units. No production
connection or editing action is requested.

Create a v0.9 A2UI message-array file at deliverables/interface.json using the
documented Gemini Enterprise composite catalog. Make a clean native analysis
view with a quantitative chart and exact table, plus direction-preserving
dependency information. Include the selected node's values without external
data URLs. Write deliverables/review.json with keys host, route, alternatives
(array), testsPerformed (array), untested (array), and critique (array of
observation/userCost/repair objects). Use the supplied skill's bounded checker
where suitable, and distinguish it from official catalog/host validation.
