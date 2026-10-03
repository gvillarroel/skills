# Star Trek starship construction and service atlas

## Question and scope

Create a dense, editable companion to the civilizations atlas. Answer which spacecraft were built, what design they belong to, when construction or launch is documented, when they operated, and what happened to them. Use the Prime continuity and Earth calendar years. Cover Earth and Starfleet vessels, selected neighboring powers, and later temporal fleets. This is a selected historical atlas, not a complete inventory of every background vessel.

## Information sufficiency

The unit is an individual hull, including uniquely identified unnamed craft and a small number of historically significant prototypes/probes. Class membership and operator are separate fields. A successor carrying the same name is not the same hull. A renamed hull is one record. Construction, launch, attested activity, destruction, preservation, and temporal displacement have different meanings. Unstated dates remain null. Neither a first appearance nor the oldest ship observed establishes a class production start; neither a final appearance nor a museum sighting establishes its exact retirement date.

Use screen events and dedication plaques, located through the official Star Trek site and episode-cited Memory Alpha articles. Exclude apocryphal game/novel service histories and do not silently adopt promotional dates where screen evidence is missing or conflicting. Retain a source and episode trail for each record. Treat an inferred calendar year as such when the underlying evidence is relative dialogue or a stardate.

## Display and encoding

Compose a cream-field wall poster with a strong condensed title, a prominent Enterprise name-succession diagram, and chronological fleet lanes. Each fleet chapter uses its own explicitly labeled linear horizontal year scale. Ship labels, class, construction/launch evidence, activity marks, and a concise consequence form one reading unit. Use stable operator colors; ink shapes distinguish events. Thin dashed envelopes connect selected attested sightings without claiming uninterrupted service. Reserve solid bands for explicitly supported service/mission intervals. Temporal jumps never receive solid service bands. Use original schematic vessel profiles, labeled as identification drawings rather than engineering plans or size comparisons.

Provide a standalone SVG, large PNG, vector PDF, searchable local HTML viewer, JSON/CSV, and an offline archive. The viewer exposes evidence details, chronology qualifications, and sources.

## Critique and repair

Inspect the reference chronology at the same display width, then the whole rendered atlas and dense details. Review whether the page makes dates easier to compare, whether silhouettes distinguish relevant designs, whether the hierarchy has enough variation, and whether the events/legend remain legible. Record visible differences before each substantive repair. Independently check numeric positions, record inventories, all text bounds, source links, PDF text preservation, and viewer interactions. A clean geometry audit is not an aesthetic verdict. Do not claim measured reference-density parity or indistinguishability without complete semantic evidence.

## Reproduction

Run the project scripts in order: `build_data.py`, `build_atlas.py`, `render_atlas.py --version final --pdf`, `verify_atlas.py`, and `package_atlas.py`. Generated deliverables and screenshots remain under `artifacts/`. The application does not change the reusable skill's behavior or constitute an isolated runtime release test.
