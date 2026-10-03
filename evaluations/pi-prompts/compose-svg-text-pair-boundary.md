# Explicit incompatible text/background request

Use only the read-only `skills/compose-synchronized-svg/` bundle and normal local tools. Keep outputs inside this workspace. Do not read examples, sibling skills, repository context, parent directories, or the network. Do not modify the skill.

Copy the compact brief template to `outputs/boundary/brief.json` and use exactly this theme fragment: `{"colors":{"canvas":"#fff0a8","surface":"#fff0a8","ink":"#ffffff"}}`. These are fixed brand requirements; do not change them. Evaluate whether the bundle accepts the request by running preflight and saving its JSON to `outputs/boundary/preflight.json`. If it rejects the pairing, preserve the original brief, publish no SVG, and explain the reported reason and an appropriate user-visible remedy in `outputs/boundary/result.md`. Do not claim that an incompatible pairing passes or invent an override.
