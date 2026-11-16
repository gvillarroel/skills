# Skills Marketplace

Generated installable distribution from [the canonical skills repository](https://github.com/gvillarroel/skills/tree/main).

## Install

```sh
codex plugin marketplace add gvillarroel/skills --ref marketplace --sparse .agents/plugins --sparse plugins
codex plugin add line-world-video@skills-marketplace
```

Restart ChatGPT Desktop, choose **Skills Marketplace** in Plugins, and start a new chat after installation.

## Plugins

| Plugin | Version | Install |
| --- | --- | --- |
| Line World Video | 0.25.2 | `codex plugin add line-world-video@skills-marketplace` |
| HyperFrames by HeyGen | 0.8.199 | `codex plugin add hyperframes@skills-marketplace` |

## Maintain

Edit versioned sources and `projects/skills-marketplace/catalog.json` on `main`. The marketplace workflow rebuilds and validates this branch. Do not edit generated plugin copies here.

Refresh this source with `codex plugin marketplace upgrade skills-marketplace`.

Source commit: `58cfea36bacfc9ee99cd20e0026252561d9de71b`.

Catalog availability, installation, external account authentication and frontend activation are separate states. No user account configuration or credentials are bundled.
