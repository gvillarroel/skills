Review a short educational video's narration. Use the supplied facts only.
Create `revised-story.json`, `narration-review.json` and `editorial-notes.md` in
the workspace root. This is a script revision; do not render a movie or operate
an external editor. Preserve scene IDs, the Spanish language and essential
scientific scope. Read every scene, remove unnecessary commentary about the
visual's construction and teach the topic instead. Preserve the actual meaning
of useful limitations. Keep the skill bundle unchanged. The review JSON must
include candidates from the supplied original script, plus per-scene editorial
decisions; a lexical scan alone does not constitute approval.

Input story:

```json
{"scenes":[{"id":"parallel","script":"La CPU lanza un kernel que ejecutan muchos hilos, organizados en bloques. El diagrama es un mapa de la realidad, no la realidad misma. La animación no mide una aceleración concreta."},{"id":"arc","script":"En estas ocho tareas seleccionadas de ARC, las autoediciones sin refuerzo alcanzan veinte por ciento y SEAL setenta y dos coma cinco. El gráfico de la derecha traduce exactamente esas filas. No significa que SEAL resuelva el setenta y dos por ciento de todo ARC."},{"id":"evidence","script":"Estos datos son sintéticos; sirven para ilustrar el método y no constituyen un resultado experimental. El punto rojo identifica lo que explicamos."}]}
```

Facts available for a concise rewrite: CUDA kernels execute many GPU threads;
threads are grouped into blocks and can calculate different portions of a
parallelizable operation. No quantitative speedup was measured. For the ARC
experiment, the metric is the percentage of self-edits ending in a correct
solution on eight selected tasks. The two supplied percentages differ by 52.5
percentage points. The last scene's data are synthetic and the viewer must not
mistake them for an experimental result. Explain these facts without inventing
benchmark-wide success or a measured performance claim.
