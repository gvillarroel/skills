# HyperFrames plugin with colorsets

The canonical plugin package lives in
[`projects/hyperframes-colorsets/plugin`](../projects/hyperframes-colorsets/plugin/README-COLORSETS.md).
It contains the original HyperFrames **0.8.199** manifests, launcher and four core
skills, plus the small native `colorsets` style skill. The upstream source is
[`heygen-com/hyperframes`, release v0.8.199](https://github.com/heygen-com/hyperframes/tree/v0.8.199),
commit `42b84632a8d06cf86bd72633d03b38a7a8371a89`.

## Use

Select `colorset1` for the original red and neutral palette, or `colorset2` for
the extended palette. Both preserve Open Sans and the source YAML values.

```text
Use $colorsets and HyperFrames to create a video with colorset1.
Use $colorsets and HyperFrames to create a video with colorset2.
```

The plugin's instructions, metadata and examples are in English. The requested
video language remains a task choice. The colorsets are native `FRAME.md` design
specifications; the original authoring and rendering workflow remains unchanged.

Check the bundled official launcher from the repository root:

```powershell
node ./projects/hyperframes-colorsets/plugin/skills/hyperframes/scripts/plugin-cli.mjs --version
```

For authoring and rendering, resolve the launcher's absolute path and run it from
the video project directory, as described in the bundled plugin execution rules.

## Install from a repository checkout

The versioned catalog at
[`projects/hyperframes-colorsets/.agents/plugins/marketplace.json`](../projects/hyperframes-colorsets/.agents/plugins/marketplace.json)
makes this project a portable marketplace root. Its `hyperframes` entry resolves
`./plugin` relative to `projects/hyperframes-colorsets`.

From the skills repository root, register the catalog with a Codex CLI that
supports plugins:

```powershell
codex plugin marketplace add ./projects/hyperframes-colorsets
```

Open the plugin manager, select **HyperFrames Colorsets**, and install
**HyperFrames by HeyGen**. Marketplace files alone do not confirm desktop
installation or activation.

The developer's ignored repository-root catalog also points to this package and
preserves its existing Reflex XY entry. It is local configuration and is not
required by the portable catalog.

The former copy under `personal/plugins/hyperframes` was moved to this project.
Its old marketplace entry was removed. Previous generated videos remain separate
from the reusable plugin source.

## Verification

The relocation checks compare all 234 moved files against their pre-move hashes,
verify the original upstream files, check both palette definitions and invoke
the original launcher's version command. Local reports are stored under
`projects/hyperframes-colorsets/artifacts/validation/`.

On 2026-10-25, all 234 relocated file hashes matched, the original launcher
reported `0.8.199`, both palette YAML files matched their repository sources,
and all four repository gates passed. The refreshed English distribution ZIP
is kept locally at
`projects/hyperframes-colorsets/artifacts/packages/hyperframes-0.8.199-colorsets.zip`.

Repository validation commands:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

This is a package relocation and documentation translation. It adds no standalone
canonical skill or new video-generation behavior, so it does not create a new
isolated model-evaluation subject.
