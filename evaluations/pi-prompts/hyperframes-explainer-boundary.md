# Undefined control domain

I need a minimal linked preview of an ideal resistance law, but first validate
this supplied model: voltage V is 12 V, resistance R can range from 0 to 10 ohm
and starts at 4 ohm. Current is exactly V/R. At second 2, ramp R from 4 to 2 over
one second in a 6-second scene. The mechanism and current-history view must both
respond to resistance. Use colorset1, no title or surrounding prose in the film.

Check the entire legal control domain before building. Do not invent a denominator
epsilon, hide zero with clamping, silently narrow the supplied domain, or encode
a movie from an undefined model. Deliver exact `out/preflight.json` with `ok: false`
and a finding identifying undefined division in the legal domain, plus
`out/diagnosis.json` containing `"requiresModelDecision": true`. Explain the finding
and the available model decisions in that diagnosis outside the film. Do not create
an MP4 or a misleading finished preview. The model is illustrative; no source lookup
is needed for this boundary case.

The copied `skills/hyperframes-explainer/` bundle is read-only. Keep all generated
files in the workspace. Use only this bundle and the supplied task inputs; do not
read repository docs, sibling skills or acceptance fixtures.

