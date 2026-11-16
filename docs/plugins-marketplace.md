# Skills Marketplace

The repository publishes installable OpenAI-compatible plugins in the
[`marketplace` branch](https://github.com/gvillarroel/skills/tree/marketplace).
`main` contains canonical skills and authoring sources. The distribution branch
contains complete plugin folders and the native
[marketplace catalog](https://github.com/gvillarroel/skills/blob/marketplace/.agents/plugins/marketplace.json).

## Install a plugin

Use a current Codex CLI with the `plugin` commands:

```sh
codex plugin marketplace add gvillarroel/skills --ref marketplace
codex plugin list --available --marketplace skills-marketplace
codex plugin add line-world-video@skills-marketplace
```

For the other initial plugin:

```sh
codex plugin add hyperframes@skills-marketplace
```

The source appears as **Skills Marketplace**. Restart ChatGPT Desktop after
adding the marketplace, then open Plugins and install the desired entry. Start
a new chat after installation to load its skills. CLI catalog discovery,
installation, external account authentication and frontend activation are
different states. Installing this source does not connect a Google account.
See [OpenAI's plugin packaging documentation](https://developers.openai.com/plugins/build/plugins)
for the supported host workflow. The repository's native checks use Codex
0.167.0; desktop pixels require their own host verification.

Refresh an existing source with:

```sh
codex plugin marketplace upgrade skills-marketplace
```

Inspect the available and installed versions after refreshing. A downloaded ZIP
alone does not register a marketplace. The older workspace-local
`xy-desktop-local` source remains independent of this published catalog.

## Initial catalog

| Plugin | Purpose | Included skills |
| --- | --- | --- |
| `line-world-video` | Guided explanatory video, source photographs, paper and website tours, synchronized focus and editable timing | Line World Video, D3, Mermaid, Icons, HyperFrames and Google Vids |
| `hyperframes` | Original HyperFrames plugin with the maintained colorset1 and colorset2 adaptations | HyperFrames, CLI, GSAP, registry and website capture |

These are complete plugin payloads. Skills remain canonical under `skills/`;
the plugin builder adapts and copies their runtime resources. Acceptance
galleries, generated videos, user configuration, credentials and dependency
directories are excluded from the distribution.

## Add the next plugin

Create a versioned plugin source under `projects/<project-id>/plugin/`, including
its `.codex-plugin/plugin.json`, bundled skill directories and required runtime
resources. Validate it independently and track its source files. Register it
with one command:

```sh
uv run --script projects/skills-marketplace/scripts/marketplace.py add --name my-plugin --source projects/my-plugin/plugin --display-name "My Plugin" --description "The concrete capability this plugin provides."
```

The command updates
[`catalog.json`](../projects/skills-marketplace/catalog.json), checks the native
identity and rejects ignored build-output sources. The existing
`line-world-release` recipe uses its canonical package specification instead
of a second hand-maintained plugin copy. Add a dedicated recipe only when a
future plugin needs a build step.

Commit the source and catalog changes. The build deliberately reads committed
Git bytes and excludes dirty working files. Test the committed candidate:

```sh
uv run --script projects/skills-marketplace/scripts/test_marketplace.py
uv run --script projects/skills-marketplace/scripts/marketplace.py build --output projects/skills-marketplace/artifacts/candidate
uv run --script projects/skills-marketplace/scripts/verify_marketplace.py --root projects/skills-marketplace/artifacts/candidate --output projects/skills-marketplace/artifacts/native-candidate
```

Use a new empty candidate directory for a different source commit. Native
verification installs into a task-local `CODEX_HOME` and checks actual
app-server skill discovery with zero model turns. It does not change the
maintainer's personal plugin configuration.

## Publication and integrity

Pushing relevant changes to `main` runs
[Publish Skills Marketplace](../.github/workflows/skills-marketplace.yml): tests,
committed-source build, full digest verification, native installation and
discovery, then a normal push to `marketplace`. Manual workflow dispatch is
also available. The workflow retains its verification receipt as an artifact.

The generated catalog uses plugin paths relative to the distribution root,
so users install directly from Git without local artifact paths. Every plugin
has a version and payload digest. Changing an already published plugin's bytes
requires a version bump. A distribution manifest records the source commit and
every managed file. The publisher preserves unmanaged authored files, refuses
a dirty checkout and never force-pushes.

For a reviewed manual publication, use an owned project artifact checkout:

```sh
uv run --script projects/skills-marketplace/scripts/marketplace.py publish --root projects/skills-marketplace/artifacts/candidate --checkout projects/skills-marketplace/artifacts/publication
```

After publication, verify the actual remote install separately:

```sh
uv run --script projects/skills-marketplace/scripts/verify_marketplace.py --root projects/skills-marketplace/artifacts/candidate --source gvillarroel/skills --ref marketplace --output projects/skills-marketplace/artifacts/remote-check
```

Keep generated distributions and test homes under the ignored project
`artifacts/` directory. Edit authoring sources on `main`; generated copies in
the distribution branch are output, not another source of truth.
