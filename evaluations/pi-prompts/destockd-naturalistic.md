# Naturalistic forward case

Use the supplied skill as a read-only resource. Keep every generated file in this
isolated workspace and do not read external local files or other skills. Public
Destockd reads are allowed. Do not download full video files for this search.

The user asks in Spanish: “Busco material de ordenadores antiguos y personas
trabajando en una sala de control. Enséñame seis opciones para elegir después.”

Produce `options.json` with six real, distinct, stable film/shot selections and
`options.html` with their previews. Write a short Spanish reply to `reply.md`
using the same option numbers and actual shot links, explaining how the user
can request a selected download. Describe candidates honestly: if you cannot
visually inspect them, say they remain unverified. Avoid inventing duration,
resolution, dates, sound or certainty from a title or similarity score.
