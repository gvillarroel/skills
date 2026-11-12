# Prepare Gemini Enterprise hosting and registration

Source review: November 11, 2026. Keep artifact preparation, local validation,
cloud deployment, IAM changes, and administrator registration as distinct steps.
Build the requested package and a concrete deployment/configuration plan before
any cloud changes that need authorization. A request to design UI does not
require creating a cloud project, changing IAM, or publishing an endpoint.

Use the host-compatible A2A transport/SDK and an A2UI extension/catalog
declaration. Current Gemini Enterprise documentation specifies the A2A v0.3
streaming mechanism; newer A2A SDK versions may need their compatibility layer.
Do not infer host compatibility from a newer upstream SDK's successful local
test. Verify the agent card, endpoint, extension URI, catalog IDs, security
configuration, streaming, and user-action handling together.
[A2A registration](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent).

The agent must be hosted and reachable by Gemini Enterprise. Google documents
Cloud Run and Agent Runtime routes. Use the actual reachable endpoint in the
agent card; localhost is only a local development address. Authentication and
reachability are separate requirements, so reachable does not mean unauthenticated.
The documented Cloud Run service-agent invoker rule depends on the exact
hosting URL/path; do not generalize it to a custom domain or a gateway.
[A2UI hosting tutorial](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/tutorial-host-agent-cloud-run).

Registration requires an existing Gemini Enterprise app, enabled APIs, and the
documented administrator role. Use console or the exact current REST contract
for the selected project, location, app/engine, assistant, and agent. Record
those resource identities without credentials. Registration and licensing
quotas are deployment conditions; verify current values instead of hard-coding
a copied quota. Registering one backend into several apps can consume quota
separately. Keep tokens out of manifests, command output, and screenshots.
[Registration prerequisites](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent),
[A2UI management](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/register-and-manage-an-a2ui-agent).

Prepare the following reviewable deliverables when deployment is requested:

- An agent package with pinned dependencies, start command, and local tests.
- A real agent card with supported A2A transport and A2UI/catalog declaration.
- Required resource IDs, runtime configuration, authentication, and IAM plan.
- A local streaming/action smoke test, followed by authorized cloud reachability.
- A host acceptance check for discovery, rendered components, action responses,
  cancellation, error recovery, state lifetimes, and keyboard access.

Report which of these were executed. A valid card, an HTTP response, or a local
renderer does not establish completed registration or Gemini Enterprise paint.
Keep this distinction even when a user reports seeing the agent.
