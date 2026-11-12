Use the desktop-plugin-ui skill to recommend a plugin interaction for choosing
one of three output modes (compact, standard, detailed). It must run as a Pi
extension in TUI and RPC, with a useful noninteractive path. This is a design
task, not an implementation or capability study.

Write `deliverables/choice.md`. Include the selected interaction, mode-specific
fallback, cancellation and state ownership, whether selection requires model
work, coexistence with another extension, and one concrete visual/behavioral
acceptance check. Keep the advice proportionate to this task. Distinguish
documented API contracts from design recommendations and unperformed checks.

Use only the supplied skill and ordinary local tools; do not browse, discover
other skills or inspect host configuration. Treat `skills/desktop-plugin-ui/`
as read-only. Write generated files outside it. Do not install anything or
change application settings. Do not claim a UI was rendered or tested.
