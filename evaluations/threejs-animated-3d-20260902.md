# Three.js Animated 3D release validation — 2026-09-02

## Outcome

PASS. Three fresh isolated Spark repetitions created the requested standalone
token-orbit scene and validation artifacts on one unchanged runtime payload.

| Run | Strict gates | Tool calls | Duration |
| --- | --- | ---: | ---: |
| `20260902-threejs-runtime-token-orbit-spark-2` | pass | 7 | 84.922 s |
| `20260902-threejs-runtime-token-orbit-spark-3` | pass | 9 | 36.687 s |
| `20260902-threejs-runtime-token-orbit-spark-4` | pass | 16 | 60.922 s |

Runtime payload: 10 files, SHA-256
`6729c63226db5083cd96307f4c9e52de07bddf14147a5d1330fb65c9b9093104`.
Every run observed `openai-codex/gpt-5.3-codex-spark`, passed exact-output and
event gates with zero tool errors, kept reads inside the copied bundle and
prompt, and left the payload unchanged.

Independent deep browser validation of repetition 2 passed. The 1,008,100-byte
self-contained HTML has SHA-256
`ded4dba15d02a3d93e0709e313217f9e7001972541c1aca1ab9668e2a01ab09f`
and zero remote references. Chromium found one ready WebGL canvas and one
replay control at both 1280×720 and 390×844, zero horizontal overflow, rich
nonwhite/color samples, distinct time-separated frame hashes, and working
replay plus pointer-drag interactions. There were no browser errors or
independent-validator findings.

Durable event/read-surface summary:

- `evaluations/threejs-animated-3d-20260902-read-surface.json`
