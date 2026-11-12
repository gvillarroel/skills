# Gemini Enterprise A2UI and A2A

Primary-source review: November 11, 2026. Gemini Enterprise documents A2UI
v0.8 and v0.9 with host styling and versioned component catalogs. This is a
documented integration route; this skill has no inherited signed-in Gemini
Enterprise paint result.
[Registration](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/register-and-manage-an-a2ui-agent),
[component reference](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/a2ui-component-gallery-reference).

## Pin the host contract

A2UI describes UI; A2A carries agent communication. A generic MCP tool result,
HTML resource, or Gemini model API does not establish a Gemini Enterprise
renderer. Choose the documented host catalog, inspect its schema and component
properties, and use stable surface/component IDs. Host-owned styling does not
promise arbitrary CSS, Node access, or insertion into host chrome.

For the bundled v0.9 starter, send `version:"v0.9"` envelopes with
`createSurface`, `updateComponents`, and `updateDataModel`; use `deleteSurface`
when closing the surface. The root component is `root`. Keep component IDs
unique within a surface and ensure child references resolve. Data bindings
refer to paths in that surface's model. The starter is an original read-only
panel using documented MaterialCard/MaterialColumn/MaterialText components.
It is not a complete A2A server or an action-handler example.

Upstream A2UI has newer specifications. The v0.9 documentation now redirects
to v0.9.1 while retaining v0.9 wire values, and upstream also offers v1.0.
Do not infer Gemini Enterprise v1.0 support from upstream availability.
[Versioned specification](https://a2ui.org/specification/v0.9.1-a2ui/),
[official hosting example](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/tutorial-host-agent-cloud-run).

For richer controls, use the host's actual catalog schema, not similarly named
MCP/HTML/Material framework props. A bound input or filter choice does not
automatically run a server action. Implement and test the chosen event
contract with a task/request ID and version-bound authority. Preserve drafts
after errors; cancellation must not commit; stale responses must not override
newer state. Inspect the matching A2A/A2UI SDK for exact action wrapping.

## Validate in layers

1. Run the bundled message checker. It checks v0.9 operation shape, surface
   lifecycle, unique IDs, root, referenced children, and model update paths.
   It accepts only a closed, acyclic component tree per update batch; streaming
   forward references and incremental partial trees are outside its profile.
2. Validate the actual envelope and component properties with pinned official
   JSON schemas/catalogs. Record source/version/digest; a generic structural
   checker cannot certify catalog property support. The upstream envelope uses
   a relative `catalog.json` slot. Bind it to the selected host component union
   while retaining official schema base URIs for common-type references;
   fetching that placeholder as a public URL can return 404. Report any theme
   semantics excluded by a validation adapter instead of claiming full coverage.
3. Exercise A2A discovery, extension/catalog negotiation, streamed UI, action
   dispatch, plain-text fallback, cancellation, error, and reconnect using the
   real SDK. Keep arbitrary SDK versions separate from host compatibility.
4. After authorized deployment/admin registration, check actual Gemini
   Enterprise component paint, keyboard, state updates, catalog styling, and
   actions. A local renderer or JSON stream does not establish this result.

The published composite catalog is
`https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json`.
Use its canonical `catalogId`, not an invented URL. The documented agent card
advertises `https://a2ui.org/a2a-extension/a2ui/v0.9` with supported catalog IDs.
Do not copy a production identity or credentials from a sample.
