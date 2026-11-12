# Reflex XY integrations

Four adapters reuse the canonical `skills/reflex-xy` runtime: a Claude Code Mod,
a Claude Desktop MCP extension, a local ChatGPT Desktop plugin and a remote
ChatGPT MCP App. The Python engine renders
native XY 0.0.8 charts with Colorset 1 and Colorset 2 and exports HTML, SVG, PNG,
editable Python and JSON.

The latest distribution is **0.3.2**. It updates installation instructions while
retaining the tested **0.3.1 MCP runtime** byte-for-byte. Installed-host results
remain attached to the versions actually exercised, including the 0.3.0 native
Code installation.

The initial view prioritizes the chart and one primary action. Display and
export choices remain available through More options; Colorset 1 is the default.

Desktop controls use deterministic local code. The Claude Mod can open a sample
through `/xy-chart line` and save an image without a model turn. The ChatGPT
plugin declares direct global/thread MCP App entrypoints and an optional data
editor. Release **0.3.1** carries genuine XY HTML/SVG in app-private MCP results
and uses host-mediated file exports, avoiding a nested loopback navigation.

Actual Claude Desktop Chat paints the chart and supports palette, fullscreen,
image saving and exact-data editing. ChatGPT Desktop paints the same component
after registering the packaged server directly in local MCP settings and
selecting Restart. Its folder plugin is installed, but its bundled server did
not surface in the tested build; the direct connection is the observed local
workaround. ChatGPT controls/sidebar entrypoints and the installed native Code
pane remain separate acceptance gaps. The Code app currently shows its access
screen before a project can be opened.

Read the [integration guide](../../docs/reflex-xy-plugins.md) for build, installation,
configuration, supported chart contracts and verification boundaries. Source
adapters do not maintain a second copy of the skill; packaging copies its current
runtime payload and excludes acceptance galleries and generated artifacts.
The [installed-host evaluation](../../evaluations/reflex-xy/native-desktop-20261025.md)
records real screenshots, retained failures, exact release hashes and the
difference between original export bytes and host-saved image pixels.
