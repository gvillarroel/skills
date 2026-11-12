Use the supplied desktop-plugin-ui skill to recommend a low-setup output-mode
chooser for Pi TUI, RPC and print mode. The options are compact, standard and
detailed. A teammate suggested using OpenUI because its coding-agent skill
supports many assistants. Explain what that support does and which rendering
and action integration this particular task needs.

Write `deliverables/native-choice.md`. Include the interaction choice,
explicit-input path, state/cancel handling, inference boundary, other-extension
coexistence and a concrete acceptance check. Include the exact bundled primary
OpenUI coding-agent and chat-renderer source links so reviewers can distinguish
their roles. This is a recommendation; do not implement a plugin or claim to
have rendered one.

Create the deliverables directory and Markdown before running this exact
contract command from the workspace root:

```bash
python skills/desktop-plugin-ui/scripts/check_sources.py deliverables/native-choice.md --fail-on-findings > deliverables/source-check.json
```

Inspect the resulting JSON. It must pass and actually check both OpenUI links.
Treat `skills/desktop-plugin-ui/` as read-only. Use only this supplied skill and
normal local tools; do not browse, discover other skills, inspect host/global
configuration, install software, launch assistant sessions or change settings.
Write exact output paths outside the copied skill.
