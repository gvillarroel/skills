# Star Trek: Civilizations, Wars and the Prime Timeline

Create a dense, editable educational atlas of Star Trek's on-screen history, using the usefulcharts-style workflow. This is a subject-specific project, not a published reusable pattern or an isolated model benchmark. Artifact text is English under repository instructions; the user conversation is Spanish.

## Information sufficiency

The reader should be able to locate the Federation's foundation, trace the principal civilizations and powers, distinguish wars from incursions and crises, understand changing Dominion War alignments, and separate Prime continuity from alternate, erased or conditional stories.

The authored dataset contains 123 main entries, 12 ancient antecedents, 12 distant-future entries and eight alternate-history summaries. Main entries use 32 subject categories; these include species, polities and other powers rather than 32 interchangeable sovereign states. Every entry supplies a screen credit and research source key. The catalog contains 72 references, 69 of which are cited by the entries.

This is a selection of major on-screen events, not an exhaustive census of every species, battle or spoken historical reference. Official StarTrek.com summaries and Memory Alpha's episode-cited chronology supplement the named films and episodes. Novels, games and apocryphal timeline passages are excluded.

## Display decisions

- Use six continuous subject histories with unequal widths and compact dates, titles, consequences and episode credits. Narrower histories release space for explicitly separated alternative histories and explanatory diagrams.
- Read downward inside a branch. Dates establish chronology; neighboring branches do not share a linear time scale. The overview strip is also a chronological sequence with compressed intervals. Numeric equal-time geometry is intentionally not claimed.
- Use stable light colors for subjects. Thin links associate entries in a reading sequence; they do not assert ancestry, membership, a government lifespan or a causal relationship.
- Use labeled diagrams for founding membership, Dominion hierarchy, war, coalition membership and the Cardassian side change. State Bajoran neutrality and Son'a material support separately. A two-headed war connector does not identify either coalition as the sole aggressor.
- Keep the 32nd century in a separate lower region. Kelvin, Mirror, Yesterday's Enterprise, Year of Hell, Endgame, the Confederation, Solum's lost future and Procyon V are visibly separated from surviving Prime history.
- Prefer selectable SVG text and a vector PDF. Add browser zoom, search, section navigation and source inspection; export JSON and CSV for editing.

## Canon checks that changed the work

- Endgame's replaced future returns Voyager in 2394; Admiral Janeway departs from 2404 to alter 2378.
- The Sound of Thunder's Kaminar events are dated 2257 in the episode chronology. Control's final battle near Xahea is dated 2258.
- The Icarus Factor does not identify Kyle Riker's attacked starbase. Remove the unsupported Starbase 24 designation.
- Treat 2156-2160 as the Earth-Romulan War, preceding Federation foundation in 2161.
- Preserve the 2366 Cardassian truce, 2367 armistice and 2370 treaty as different stages.
- Preserve Romulan nonaggression in 2373 before the 2374 alliance, Breen entry in 2375, and Cardassian revolt and side change.
- Distinguish Jurati's separate collective and provisional-membership request from the Jupiter hive responsible for Frontier Day.
- Mark the Eugenics Wars' temporal revisions, the Kzinti dating conflict, approximate Tzenkethi chronology, c.2260 Gorn incidents and the uncertain Academy-era dates.
- Treat Solum's revised path and the Sphere-Builders' Procyon V outcome as temporal qualifications; do not append them as guaranteed Prime futures.

## Construction and review

Run these commands from the repository root:

```powershell
uv run --script projects/star-trek-canonical-timeline/scripts/build_data.py
uv run --script projects/star-trek-canonical-timeline/scripts/build_dense_poster.py
uv run --script projects/star-trek-canonical-timeline/scripts/render_review.py --version final --pdf
uv run --script projects/star-trek-canonical-timeline/scripts/package_atlas.py
uv run --script projects/star-trek-canonical-timeline/scripts/verify_atlas.py
```

The shared project drawing primitives are in `scripts/build_poster.py`; the final composition is `scripts/build_dense_poster.py`. Running either script builds the final composition. The renderer uses the repository's bundled Barlow Condensed font and Windows Arial. Barlow and its license notice are embedded in the standalone SVG; the PDF embeds its used fonts. The offline viewer can be opened directly from `artifacts/viewer/index.html` after extracting `artifacts/star-trek-atlas.zip` without flattening its folders.

The reference comparison and acceptance boundary are recorded in [the evaluation](../../evaluations/usefulcharts-style/star-trek-atlas-20260912.md). Generated media and detailed audits remain in the ignored `artifacts/` directory.
