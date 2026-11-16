# Scene handoff

Accept a UTF-8 JSON object with `projectTitle`, `language`, `width`, `height`,
`fps` and an ordered `scenes` list. Each scene needs a unique lowercase ID,
nonempty `script`, a visual description or `clip` path, `clipSeconds` and
`essentialAnimationSeconds`. Optional `cues` describe the visual state needed
when a concept is spoken. Scripts may use the requested narration language;
the skill's instructions and receipts remain English.

The helper creates a draft worksheet, not a claimed measured edit. Update each
scene's `voiceoverSeconds` and `sceneSeconds` only after reading the native
Vids result. Record `observed: true`, `voice`, and the project URL. An explicit
`audioLeadSeconds` or `tailSeconds` describes an intentional pause. Compilation
requires observed values, sufficient room for speech, normal-rate visual
coverage and all essential animation completed before a scene is cut.

Keep the final frame readable. A longer source clip may contain a static hold
that Vids can trim after narration. Preserve the planned final camera state so
the next scene can begin there. Repeated category IDs, symbols and palette
roles must remain stable. Never stretch a chart scale or change facts to fill
an audio budget.

For the Line World style, use white, primary red #9e1b32 and secondary grays.
Black belongs among the last fill options, while charcoal text and fine lines
remain readable. Keep the guiding dot primary red, allow meaningful size
changes, and use additional hues only for documented information categories.
Do not add title bands, stock decoration, music or avatars by default.
