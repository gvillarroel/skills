#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the curated Prime-continuity spacecraft evidence ledger."""
from pathlib import Path
from urllib.parse import quote
import json

PROJECT = Path(__file__).resolve().parents[1]
ships, sources = [], {}


def add(id, name, design, registry, operator, chapter, years, note, credit, page,
        launch=None, launch_kind="launch", yard=None, built=None, use=None,
        end=None, special=None, qualifier=None, shape=None, important=False):
    """An observation envelope is never automatically a service duration."""
    key = id
    sources[key] = dict(title=page.replace("_", " "), publisher="Memory Alpha",
                        url="https://memory-alpha.fandom.com/wiki/" + quote(page.replace(" ", "_"), safe="_"),
                        evidence=credit, accessed="2026-09-12")
    ships.append(dict(id=id, name=name, design=design, registry=registry,
                      operator=operator, chapter=chapter,
                      construction=built, launch=launch, launch_kind=launch_kind,
                      shipyard=yard, observations=years, service=use,
                      endpoint=end, special=special or [], note=note,
                      credit=credit, source=key, qualifier=qualifier,
                      shape=shape, important=important))


# Early spaceflight. Museum evidence is not counted as an active service year.
add("phoenix", "Phoenix", "Warp prototype", "Prototype", "Earth", "early", [2063],
    "Cochrane's first human warp flight: 5 April. A converted missile, built in Montana.",
    "First Contact", "Phoenix", launch=2063, yard="Bozeman, Montana", built=[2063], shape="phoenix", important=True)
add("t-plana-hath", "T'Plana-Hath", "Vulcan survey ship", "Registry not stated", "Vulcan", "early", [2063],
    "Detects Phoenix's warp signature; its landing initiates public human–Vulcan contact.",
    "First Contact", "T'Plana-Hath_(starship)", shape="vulcan-lander")
add("friendship-1", "Friendship 1", "Warp probe", "UESPA-1", "Earth", "early", [2067],
    "Launched to share human knowledge. Voyager recovers its wreckage in 2378.",
    "VOY · Friendship One", "Friendship_1", launch=2067, special=[dict(year=2378,kind="recovered",label="Recovered 2378")], shape="probe")
add("conestoga", "SS Conestoga", "Colony transport", "Conestoga type", "Earth", "early", [2069,2078],
    "Nine-year voyage to Terra Nova; dismantled into buildings on arrival in 2078.",
    "ENT · Terra Nova", "SS_Conestoga", launch=2069, use=[2069,2078], end="dismantled", shape="freighter")
add("horizon", "ECS Horizon", "J-class freighter", "ECS Horizon", "Earth", "early", [2126,2153],
    "Travis Mayweather's family cargo ship. His birth aboard in 2126 anchors its earlier use.",
    "ENT · Horizon; Fortunate Son", "ECS_Horizon", launch=2102, launch_kind="commission",
    qualifier="Commissioning in 2102 follows the ship and class histories; 2126 and 2153 are selected later attested years.", shape="freighter")
add("kumari", "Kumari", "Andorian battle cruiser", "Imperial Guard", "Andorian", "early", [2142,2153,2154],
    "Shran's command from 2142. A Romulan drone destroys the ship in 2154.",
    "ENT · Babel One; United", "Kumari", end="destroyed", shape="andorian")
add("nx-alpha", "NX-Alpha", "NX test vehicle", "NX Project", "Earth", "early", [2143],
    "A. G. Robinson exceeds warp 2; loss of the prototype exposes engine instability.",
    "ENT · First Flight", "NX-Alpha", end="destroyed", shape="nx-test")
add("nx-beta", "NX-Beta", "NX test vehicle", "NX Project", "Earth", "early", [2143],
    "Archer and Robinson reach warp 2.5 on an unauthorized test and return safely.",
    "ENT · First Flight", "NX-Beta", shape="nx-test")
add("nx-delta", "NX-Delta", "NX test vehicle", "NX Project", "Earth", "early", [2145],
    "Duvall's warp 3 trial continues the engine program that leads to the NX-class.",
    "ENT · First Flight", "NX-Delta", qualifier="Relative dating is approximately 2144–2145: reference pages differ by one year. The craft is mentioned, not depicted.")
ships[-1]["uncertain_range"] = [2144,2145]
add("enterprise-nx", "Enterprise NX-01", "NX-class explorer", "NX-01", "Earth", "early", [2151,2153,2154,2161],
    "Archer's warp 5 explorer fights the Xindi crisis; retired in 2161, later preserved.",
    "ENT · Broken Bow; These Are the Voyages…", "Enterprise_(NX-01)", launch=2151,
    yard="Earth orbital drydock", use=[2151,2161], end="retired", shape="nx", important=True)
add("fortunate", "ECS Fortunate", "Y-class freighter", "ECS-2801", "Earth", "early", [2151],
    "A family-operated cargo ship targeted by Nausicaan raiders. Construction year unstated.",
    "ENT · Fortunate Son", "ECS_Fortunate", shape="freighter")
add("vahklas", "Vahklas", "Vulcan civilian ship", "Vahklas type", "Vulcan", "early", [2151],
    "Transports the V'tosh ka'tur. Enterprise assists with repairs during its journey.",
    "ENT · Fusion", "Vahklas", shape="vulcan-ring")
add("d-kyr", "D'kyr", "Vulcan combat cruiser", "High Command", "Vulcan", "early", [2152],
    "Rendezvous ship for Enterprise's canceled mission; its crew monitors the Suliban confrontation.",
    "ENT · Shockwave I–II", "D'kyr", shape="vulcan-ring")
add("columbia", "Columbia NX-02", "NX-class explorer", "NX-02", "Earth", "early", [2154],
    "Under construction in 2153. Engine trouble delays launch; Hernandez takes command.",
    "ENT · The Expanse; Affliction; Divergence", "Columbia", launch=2154,
    yard="Earth orbital drydock", built=[2153], shape="nx")

# 23rd-century hulls. Unknown retirements remain unknown.
add("enterprise-1701", "USS Enterprise", "Constitution → refit", "NCC-1701", "Federation", "classic", [2245,2254,2259,2266,2270,2285],
    "April, Pike and Kirk's ship; extensively refit in the 2270s. Scuttled above Genesis in 2285.",
    "DIS · Brother; TOS/TAS; films I–III", "USS_Enterprise_(NCC-1701)", launch=2245,
    yard="San Francisco Fleet Yards", use=[2245,2285], end="destroyed", shape="constitution", important=True)
add("shenzhou", "USS Shenzhou", "Walker-class", "NCC-1227", "Federation", "classic", [2249,2256],
    "Georgiou's veteran vessel. Abandoned after the Battle at the Binary Stars in 2256.",
    "DIS · The Vulcan Hello; Battle at the Binary Stars", "USS_Shenzhou", yard="San Francisco Fleet Yards",
    end="abandoned", shape="walker", qualifier="In service by 2249; construction and launch years are not established here.")
add("discovery", "USS Discovery", "Crossfield-class", "NCC-1031 → 1031-A", "Federation", "classic", [2256,2257,2258],
    "Spore-drive research ship. Leaves 2258 for 3189; the gap is time travel, not service.",
    "DIS · Context Is for Kings; Such Sweet Sorrow II", "USS_Discovery", launch=2256,
    yard="San Francisco Fleet Yards", special=[dict(year=3189,kind="time-arrival",label="3189 arrival / refit"),dict(year=3191,kind="active",label="Active 3191")],
    end="time-jump", shape="crossfield", important=True,
    qualifier="Active again in 3189–3191 and in the 33rd-century coda; the exact coda year is not used.")
add("glenn", "USS Glenn", "Crossfield-class", "NCC-1030", "Federation", "classic", [2256],
    "Sister ship in the spore-drive program. A failed jump kills the crew; Discovery scuttles it.",
    "DIS · Context Is for Kings", "USS_Glenn", end="destroyed", shape="crossfield")
add("farragut", "USS Farragut", "Farragut type", "NCC-1647", "Federation", "classic", [2257,2259],
    "Kirk's early posting. The 2257 cloud-creature attack kills crew, not the ship itself.",
    "TOS · Obsession; SNW · Lost in Translation", "USS_Farragut_(NCC-1647)", shape="miranda",
    qualifier="The 2243 launch plaque is shown in an alternate-future episode; it is not adopted as a Prime launch date here.")
add("archer", "USS Archer", "Scout ship", "NCC-627", "Federation", "classic", [2259],
    "A three-person first-contact mission to Kiley 279 requires Enterprise's intervention.",
    "SNW · Strange New Worlds", "USS_Archer_(NCC-627)",
    qualifier="Often catalogued as Gral-class; a screen-neutral scout descriptor avoids implying a spoken class name.")
add("romulan-bop", "Romulan Bird-of-Prey", "23rd-century warbird", "Neutral Zone attacker", "Romulan", "classic", [2266],
    "Cloaked ship attacks Federation outposts; its commander destroys it after defeat.",
    "TOS · Balance of Terror", "Unnamed_Romulan_Birds-of-Prey", end="destroyed", shape="romulan-bop")
add("constellation", "USS Constellation", "Constitution-class", "NCC-1017", "Federation", "classic", [2261,2267],
    "Decker's disabled cruiser is sent inside the planet killer, destroying both vessels.",
    "PIC · The Star Gazer plaque; SNW · Terrarium; TOS · The Doomsday Machine", "USS_Constellation_(NCC-1017)", launch=2245, end="destroyed", shape="constitution",
    qualifier="The 2245 launch is recorded on the screen commemorative plaque. Later years are selected mission attestations.")
add("groth", "IKS Gr'oth", "D7 battle cruiser", "Koloth's command", "Klingon", "classic", [2268],
    "Confronts Enterprise at Deep Space K-7 during the tribble incident.",
    "TOS · The Trouble with Tribbles; DS9 · Trials…", "IKS_Gr'oth", shape="d7")
add("intrepid", "USS Intrepid", "Constitution-class", "NCC-1631", "Federation", "classic", [2267,2268],
    "Crewed by Vulcans. Destroyed by the giant space organism in 2268.",
    "TOS · Court Martial; The Immunity Syndrome", "USS_Intrepid_(NCC-1631)", end="destroyed", shape="constitution")
add("defiant-1764", "USS Defiant", "Constitution-class", "NCC-1764", "Federation", "classic", [2268],
    "Vanishes into spatial interphase; emerges in the Mirror Universe in 2155.",
    "TOS · The Tholian Web; ENT · In a Mirror, Darkly", "USS_Defiant_(NCC-1764)", end="time-jump",
    special=[dict(year=2155,kind="mirror-arrival",label="Mirror arrival 2155")], shape="constitution")
add("bozeman", "USS Bozeman", "Soyuz-class", "NCC-1941", "Federation", "classic", [2278],
    "Time displacement carries Bateson's ship to 2368; it later fights at Sector 001 in 2373.",
    "TNG · Cause and Effect; First Contact", "USS_Bozeman", end="time-jump",
    special=[dict(year=2368,kind="time-arrival",label="Reappears 2368"),dict(year=2373,kind="active",label="Active 2373")], shape="soyuz")
add("reliant", "USS Reliant", "Miranda-class", "NCC-1864", "Federation", "classic", [2285],
    "Genesis survey ship seized by Khan. Destroyed in the Mutara Nebula confrontation.",
    "The Wrath of Khan", "USS_Reliant_(NCC-1864)", end="destroyed", shape="miranda")
add("grissom", "USS Grissom", "Oberth-class", "NCC-638", "Federation", "classic", [2285],
    "Science vessel studying Genesis. Destroyed by Kruge's Bird-of-Prey.",
    "The Search for Spock", "USS_Grissom_(NCC-638)", end="destroyed", shape="oberth")
add("excelsior", "USS Excelsior", "Excelsior-class", "NX-2000 → NCC-2000", "Federation", "classic", [2285,2286,2293],
    "Transwarp prototype becomes Sulu's command. Preserved at the Fleet Museum by 2401.",
    "Films III, IV, VI; PIC · The Bounty", "USS_Excelsior_(NCC-2000)", launch=2285, yard="San Francisco Fleet Yards",
    special=[dict(year=2401,kind="museum",label="Museum by 2401")], shape="excelsior", important=True,
    qualifier="Launch in 2285 follows the dedication plaque; construction start and final retirement are not established here. Later dots are selected sightings.")
add("bounty", "Kruge's ship / HMS Bounty", "Klingon Bird-of-Prey", "Captured by Kirk", "Klingon", "classic", [2285,2286],
    "Captured in 2285; transports whales from 1986 in 2286. Later recovered for the museum.",
    "Films III–IV; PIC · The Bounty", "HMS_Bounty", end="abandoned",
    special=[dict(year=2401,kind="museum",label="Museum by 2401")], shape="bird-of-prey")
add("enterprise-a", "USS Enterprise-A", "Constitution II-class", "NCC-1701-A", "Federation", "classic", [2286,2287,2293],
    "Commissioned for Kirk's crew. The Khitomer mission precedes retirement in 2293.",
    "The Voyage Home; The Undiscovered Country", "USS_Enterprise_(NCC-1701-A)", launch=2286,
    launch_kind="commission", yard="San Francisco Fleet Yards", use=[2286,2293], end="retired", shape="constitution-refit", important=True)
add("kronos-one", "Kronos One", "K't'inga-class", "Chancellor's flagship", "Klingon", "classic", [2293],
    "Carries Gorkon to peace talks; the attack on the ship triggers the Khitomer conspiracy.",
    "The Undiscovered Country", "Kronos_One", shape="d7")
add("enterprise-b", "USS Enterprise-B", "Excelsior-class refit", "NCC-1701-B", "Federation", "classic", [2293],
    "Harriman's maiden voyage rescues El-Aurian refugees from the Nexus. Final fate unstated.",
    "Generations", "USS_Enterprise_(NCC-1701-B)", launch=2293,
    yard="Earth Spacedock", shape="excelsior", important=True)

# Federation: selected hulls, not the manufacturing lifetimes of their classes.
add("stargazer-old", "USS Stargazer", "Constellation-class", "NCC-2893", "Federation", "modern", [2333,2355],
    "Picard commands from 2333; abandoned at Maxia in 2355, recovered in 2364, later a museum ship.",
    "TNG · The Battle; PIC · The Bounty", "USS_Stargazer_(NCC-2893)", launch=2326,
    launch_kind="commission", end="abandoned", special=[dict(year=2364,kind="recovered",label="Recovered 2364"),dict(year=2401,kind="museum",label="Museum by 2401")], shape="constellation")
add("enterprise-c", "USS Enterprise-C", "Ambassador-class", "NCC-1701-C", "Federation", "modern", [2344],
    "Garrett's ship returns from an altered 2366 to defend Narendra III; destroyed in 2344.",
    "TNG · Yesterday's Enterprise", "USS_Enterprise_(NCC-1701-C)", end="destroyed", shape="ambassador", important=True)
add("enterprise-d", "USS Enterprise-D", "Galaxy-class", "NCC-1701-D", "Federation", "modern", [2363,2371],
    "Lost at Veridian III in 2371. Saucer rebuilt with Syracuse parts; back in action in 2401.",
    "TNG; Generations; PIC · Võx; The Last Generation", "USS_Enterprise_(NCC-1701-D)", launch=2363,
    yard="Utopia Planitia, Mars", use=[2363,2371], end="wrecked",
    special=[dict(year=2401,kind="reactivated",label="Reactivated 2401"),dict(year=2402,kind="museum",label="Museum 2402")], shape="galaxy", important=True,
    qualifier="2363 follows the dedication plaque and commissioning chronology. The conflicting 2362 promotional-log date is not used. Restoration is not active service.")
add("phoenix-nebula", "USS Phoenix", "Nebula-class", "NCC-65420", "Federation", "modern", [2363,2367],
    "Built by Yoyodyne at 40 Eridani A; Maxwell's unauthorized Cardassian attacks occur in 2367.",
    "TNG · The Wounded (including dedication plaque)", "USS_Phoenix", launch=2363,
    launch_kind="commission", yard="40 Eridani A", shape="nebula")
add("yamato", "USS Yamato", "Galaxy-class", "NCC-71807", "Federation", "modern", [2365],
    "Iconian software disables safeguards and destroys the ship. Other hull graphics use different registries.",
    "TNG · Contagion", "USS_Yamato", end="destroyed", shape="galaxy")
add("saratoga", "USS Saratoga", "Miranda-class", "NCC-31911", "Federation", "modern", [2367],
    "Destroyed at Wolf 359. Benjamin and Jake Sisko escape; Jennifer Sisko dies aboard.",
    "DS9 · Emissary", "USS_Saratoga_(NCC-31911)", end="destroyed", shape="miranda")
add("rio-grande", "USS Rio Grande", "Danube-class runabout", "NCC-72452", "Federation", "modern", [2369,2373,2375],
    "Sisko and Dax discover the Bajoran wormhole aboard this DS9 support craft in 2369.",
    "DS9 · Emissary; series service record", "USS_Rio_Grande", shape="runabout")
add("odyssey", "USS Odyssey", "Galaxy-class", "NCC-71832", "Federation", "modern", [2370],
    "A Jem'Hadar suicide attack destroys the ship during a Gamma Quadrant rescue mission.",
    "DS9 · The Jem'Hadar", "USS_Odyssey", end="destroyed", shape="galaxy")
add("defiant-first", "USS Defiant · prototype", "Defiant-class escort", "NX-74205", "Federation", "modern", [2370,2371,2375],
    "Launched in 2370; assigned to DS9 in 2371. Destroyed at the second Battle of Chin'toka.",
    "DS9 · The Search; The Changing Face of Evil", "USS_Defiant_(2370)", launch=2370,
    yard="Antares Ship Yards", end="destroyed", shape="defiant", important=True,
    qualifier="Trials and storage precede DS9 service. Development began in 2366; this is not a 2366 launch.")
add("equinox", "USS Equinox", "Nova-class", "NCC-72381", "Federation", "modern", [2370,2371,2376],
    "Science ship pulled into the Delta Quadrant. Destroyed after exploiting nucleogenic lifeforms.",
    "VOY · Equinox I–II", "USS_Equinox", launch=2370, yard="Utopia Planitia, Mars", end="destroyed", shape="nova")
add("voyager", "USS Voyager", "Intrepid-class", "NCC-74656", "Federation", "modern", [2371,2378],
    "Seven-year Delta Quadrant journey ends in 2378. Preserved by 2381; no 2404 Prime return.",
    "VOY · Relativity; Endgame; LD · Twovix", "USS_Voyager", launch=2371,
    yard="Utopia Planitia → McKinley", use=[2371,2378], special=[dict(year=2381,kind="museum",label="Preserved by 2381")], shape="intrepid", important=True)
add("enterprise-e", "USS Enterprise-E", "Sovereign-class", "NCC-1701-E", "Federation", "modern", [2372,2373,2379],
    "Fights the Borg and Shinzon. Its later loss of availability is mentioned; exact fate is unstated.",
    "First Contact; Nemesis; PIC · Võx", "USS_Enterprise_(NCC-1701-E)", launch=2372,
    yard="San Francisco Fleet Yards", shape="sovereign", important=True,
    qualifier="Selected screen-attested active years only. No 2385/2386 retirement or destruction date is inferred from promotional logs.")
add("valiant", "USS Valiant", "Defiant-class", "NCC-74210", "Federation", "modern", [2373,2374],
    "A cadet training cruise becomes a wartime command; a Dominion battleship destroys it.",
    "DS9 · Valiant", "USS_Valiant_(NCC-74210)", launch=2372, yard="Antares Ship Yards", end="destroyed", shape="defiant")
add("prometheus", "USS Prometheus", "Prometheus-class", "NX-59650 / NX-74913", "Federation", "modern", [2374,2378],
    "Experimental vessel with multi-vector assault mode; recovered from Romulan hijackers.",
    "VOY · Message in a Bottle; Endgame", "USS_Prometheus_(Prometheus_class)", launch=2374,
    yard="Beta Antares Ship Yards", shape="prometheus")
add("delta-flyer-1", "Delta Flyer · first hull", "Delta Flyer type", "Built aboard Voyager", "Federation", "modern", [2375,2377],
    "Paris's custom craft is built in the Delta Quadrant. Destroyed during the Borg infiltration.",
    "VOY · Extreme Risk; Unimatrix Zero", "Delta_Flyer_(2375)", built=[2375], launch=2375,
    launch_kind="built", yard="USS Voyager", use=[2375,2377], end="destroyed", shape="flyer")
add("defiant-second", "USS Sao Paulo → Defiant", "Defiant-class", "NCC-75633 → NX-74205", "Federation", "modern", [2375,2384],
    "New hull replaces the lost Defiant in 2375. Still active in 2384; museum ship by 2401.",
    "DS9 · The Dogs of War; PRO · Supernova I; PIC", "USS_Defiant_(2375)", launch=2375,
    special=[dict(year=2401,kind="museum",label="Museum by 2401")], shape="defiant", important=True)
add("delta-flyer-2", "Delta Flyer · second hull", "Delta Flyer type", "Built aboard Voyager", "Federation", "modern", [2377,2378],
    "Replacement built after the first Flyer's loss; Paris and Torres race it in Drive.",
    "VOY · Drive; Endgame", "Delta_Flyer_(2377)", launch=2377, launch_kind="built",
    built=[2377], yard="USS Voyager", shape="flyer")
add("titan", "USS Titan", "Luna-class", "NCC-80102", "Federation", "modern", [2379,2380,2382],
    "Riker's command after Nemesis. Helps Cerritos against the Pakleds; a different hull from Titan-A.",
    "Nemesis; LD · No Small Parts; The New Next Generation", "USS_Titan_(NCC-80102)", shape="luna",
    qualifier="2379 is Riker's command appointment, not a documented launch. Conflicting promotional retirement dates are excluded.")
add("cerritos", "USS Cerritos", "California-class", "NCC-75567", "Federation", "modern", [2380,2381,2382],
    "Second-contact workhorse under Freeman, then Ransom. Active through the Lower Decks finale.",
    "LD · Second Contact; The New Next Generation", "USS_Cerritos", shape="california", important=True,
    qualifier="The 2371 launch given in a licensed crew handbook is not a screen-canon launch anchor.")
add("solvang", "USS Solvang", "California-class", "NCC-12101", "Federation", "modern", [2380],
    "A brand-new California-class vessel; destroyed with all hands by a Pakled clumpship.",
    "LD · No Small Parts", "USS_Solvang", launch=2380, end="destroyed", shape="california")
add("aledo", "USS Aledo", "Texas-class", "NA-01", "Federation", "modern", [2381],
    "Autonomous prototype attacks its creator; the California-class fleet destroys it.",
    "LD · The Stars at Night", "USS_Aledo", launch=2381, end="destroyed", shape="texas")
add("protostar", "USS Protostar", "Protostar-class prototype", "NX-76884", "Federation", "modern", [2382,2383,2384],
    "Launched for Chakotay; recovered by Dal's crew. Self-destructs in 2384 to stop the living construct.",
    "PRO · Kobayashi; Supernova II; season 2", "USS_Protostar", launch=2382,
    yard="San Francisco Fleet Yards", end="destroyed", shape="protostar", important=True,
    qualifier="Time travel also places this same hull before launch and after its destruction, including the repaired 2384–2385 loop. Those visits are not a continuous production/service interval.")
add("dauntless", "USS Dauntless", "Dauntless-class", "NCC-80816", "Federation", "modern", [2384],
    "Janeway's quantum-slipstream ship searches for Protostar. Distinct from Arturis's false Starfleet vessel.",
    "PRO · A Moral Star II; Supernova I–II", "USS_Dauntless_(NCC-80816)", shape="dauntless")
add("voyager-a", "USS Voyager-A", "Lamarr-class", "NCC-74656-A", "Federation", "modern", [2384,2385],
    "New Voyager launched six years after the original returns. Janeway's command passes to Chakotay.",
    "PRO · Into the Breach; Ouroboros II", "USS_Voyager_(NCC-74656-A)", launch=2384,
    launch_kind="commission", shape="lamarr", important=True)
add("prodigy", "USS Prodigy", "Protostar-class", "NCC-81084", "Federation", "modern", [2385],
    "A new production-class ship for the young crew's exploration mission after the prototype's loss.",
    "PRO · Ouroboros II", "USS_Prodigy", launch=2385, shape="protostar")
add("titan-a-g", "USS Titan-A → Enterprise-G", "Constitution III-class", "NCC-80102-A → 1701-G", "Federation", "modern", [2396,2401,2402],
    "Shaw commands from 2396. Renamed Enterprise-G in 2402, with Seven of Nine in command.",
    "PIC · The Next Generation; The Last Generation", "USS_Enterprise_(NCC-1701-G)", shape="constitution-iii", important=True,
    qualifier="2396 is anchored by Shaw's five years in command, not a directly stated construction date. The 2402 change is a rename of the same hull.")
add("stargazer-new", "USS Stargazer", "Sagan-class", "NCC-82893", "Federation", "modern", [2401],
    "Rios's four-nacelle command investigates the anomaly and encounters Jurati's Borg faction.",
    "PIC · The Star Gazer; Farewell", "USS_Stargazer_(NCC-82893)", shape="sagan")
add("enterprise-f", "USS Enterprise-F", "Odyssey-class", "NCC-1701-F", "Federation", "modern", [2401],
    "Shelby's Frontier Day flagship. Scheduled for early decommissioning; shown in action in 2401.",
    "PIC · The Next Generation; Võx", "USS_Enterprise_(NCC-1701-F)", shape="odyssey", important=True,
    qualifier="2386 launch comes from promotional Picard Logs, not the screened story; no 2386–2401 bar is asserted.")

# Other powers: identifiable individual craft, not class production runs.
add("krayton", "Krayton", "D'Kora-class marauder", "DaiMon Tog", "Ferengi", "neighbors", [2366],
    "Tog's ship abducts Lwaxana and Deanna Troi and Commander Riker at Betazed.",
    "TNG · Ménage à Troi", "Krayton", shape="ferengi")
add("bortas", "IKS Bortas", "Vor'cha-class", "Gowron's flagship", "Klingon", "neighbors", [2366,2367,2369],
    "Gowron's command during the succession crisis. Not the 22nd-century D5 with the same name.",
    "TNG · The Defector; Redemption; Rightful Heir", "IKS_Bortas_(Vor'cha_class)", shape="vorcha")
add("trager", "Trager", "Galor-class", "Gul Macet", "Cardassian", "neighbors", [2367],
    "Macet's cruiser participates in the pursuit of Maxwell's rogue USS Phoenix.",
    "TNG · The Wounded", "Trager", shape="galor")
add("wolf-cube", "Borg cube · Wolf 359", "Cube", "Locutus's vessel", "Borg", "neighbors", [2366,2367],
    "Abducts Picard and destroys 39 ships at Wolf 359; destroyed near Earth in 2367.",
    "TNG · The Best of Both Worlds I–II", "Battle_of_Wolf_359", end="destroyed", shape="cube")
add("khazara", "IRW Khazara", "D'deridex-class", "Commander Toreth", "Romulan", "neighbors", [2369],
    "Warbird used to smuggle Romulan dissidents while Troi impersonates a Tal Shiar officer.",
    "TNG · Face of the Enemy", "IRW_Khazara", shape="dderidex")
add("koranak", "Koranak", "Keldon-class", "Obsidian Order", "Cardassian", "neighbors", [2371],
    "Part of the secret strike fleet; destroyed in the Dominion ambush at the Omarion Nebula.",
    "DS9 · The Die Is Cast", "Koranak", end="destroyed", shape="keldon")
add("negh-var", "IKS Negh'Var", "Negh'Var-class", "Klingon flagship", "Klingon", "neighbors", [2372,2373],
    "Introduced as the new flagship for the invasion of Cardassia; later attacks Deep Space 9.",
    "DS9 · The Way of the Warrior; By Inferno's Light", "IKS_Negh'Var", shape="neghvar")
add("rotarran", "IKS Rotarran", "Klingon Bird-of-Prey", "Martok's command", "Klingon", "neighbors", [2373,2374,2375],
    "Martok restores its demoralized crew in 2373 and retains it as his wartime flagship.",
    "DS9 · Soldiers of the Empire; Inter Arma…", "IKS_Rotarran", shape="bird-of-prey")
add("captured-jemhadar", "Captured Jem'Hadar ship", "Jem'Hadar attack ship", "Sisko's captured vessel", "Dominion", "neighbors", [2373,2374],
    "Salvaged by Starfleet in 2373; used against a ketracel-white depot, then crashes in 2374.",
    "DS9 · The Ship; A Time to Stand; Rocks and Shoals", "Sisko's_attack_ship", end="wrecked", shape="jemhadar")
add("sector-cube", "Borg cube · Sector 001", "Cube", "Queen's assault vessel", "Borg", "neighbors", [2373],
    "Destroyed by the fleet at Earth. Its escaping sphere travels back to 2063.",
    "First Contact", "Unnamed_Borg_cubes", end="destroyed", shape="cube")
add("valdore", "Valdore", "Valdore-type warbird", "Commander Donatra", "Romulan", "neighbors", [2379],
    "Supports Enterprise-E against Scimitar in the Bassen Rift; damaged but survives.",
    "Nemesis", "Valdore_(starship)", shape="valdore")
add("scimitar", "Scimitar", "Reman warbird", "Shinzon's flagship", "Reman", "neighbors", [2379],
    "Built in secret at Remus. Its thalaron weapon is destroyed by Data, taking the ship with it.",
    "Nemesis", "Scimitar", yard="Remus · year unstated", end="destroyed", shape="scimitar")
add("artifact", "The Artifact", "Disconnected Borg cube", "Borg → Romulan control", "Borg", "neighbors", [2399],
    "A reclamation site rather than an active Collective warship; flies to Coppelius and crashes.",
    "PIC · The Impossible Box; Et in Arcadia Ego", "Artifact_(Borg_cube)", end="wrecked", shape="cube",
    qualifier="2399 covers Romulan reclamation and brief reactivation. Its manufacture and disconnection years are not specified here.")

# Precisely bounded future observations; the era jump is printed explicitly.
add("voyager-j", "USS Voyager-J", "32nd-century Intrepid", "NCC-74656-J", "Federation", "future", [3189,3190,3191],
    "A later bearer of Voyager's name with detached nacelles; distinct from Janeway's hull.",
    "DIS · Die Trying; season 4; Red Directive", "USS_Voyager_(NCC-74656-J)", shape="future-intrepid",
    qualifier="Selected dated observations; later appearances do not imply a 3191 retirement.")
add("nog", "USS Nog", "Eisenberg-class", "NCC-325070", "Federation", "future", [3189],
    "Part of the fleet around concealed Federation Headquarters when Discovery arrives.",
    "DIS · Die Trying", "USS_Nog", shape="future-oval")
add("tikhov", "USS Tikhov", "Seed-archive vessel", "NCC-1067-M", "Federation", "future", [3189],
    "Preserves the Federation's seed collection. A Barzan family tends the archive.",
    "DIS · Die Trying", "USS_Tikhov", shape="future-oval")
add("credence", "USS Credence", "Credence type", "NCC-2604", "Federation", "future", [3190,3191],
    "Distributes dilithium as the Federation reconnects worlds after the Burn.",
    "DIS · Choose to Live; Erigah", "USS_Credence", shape="future-oval")
add("athena", "USS Athena", "Academy-class", "NCC-392023", "Federation", "future", [3195,3196],
    "Spaceborne home of the reopened Starfleet Academy; serves as both campus and starship.",
    "SA · Kids These Days; Rubincon", "USS_Athena", shape="academy",
    qualifier="Academy calendar dating is disputed (3192 versus 3195–3196 in indexed references). The poster shows the 3190s as an uncertain range, not an exact launch or service interval.")
ships[-1]["uncertain_range"] = [3190,3199]

# Preserve the exact retrieved article aliases where the index returned one.
sources["intrepid"]["url"] = "https://memory-alpha.fandom.com/wiki/NCC-1831"
sources["negh-var"]["url"] = "https://memory-alpha.fandom.com/wiki/IKS_Negh%27var"

relations = [dict(source=a,target=b,kind="name-succession") for a,b in zip(
    ["enterprise-nx","enterprise-1701","enterprise-a","enterprise-b","enterprise-c","enterprise-d","enterprise-e","enterprise-f"],
    ["enterprise-1701","enterprise-a","enterprise-b","enterprise-c","enterprise-d","enterprise-e","enterprise-f","titan-a-g"])]
relations += [
    dict(source="nx-alpha",target="nx-beta",kind="test-program"),
    dict(source="nx-beta",target="nx-delta",kind="test-program"),
    dict(source="nx-delta",target="enterprise-nx",kind="development"),
    dict(source="enterprise-nx",target="columbia",kind="sister-ship"),
    dict(source="discovery",target="glenn",kind="sister-ship"),
    dict(source="defiant-first",target="defiant-second",kind="replacement-hull"),
    dict(source="delta-flyer-1",target="delta-flyer-2",kind="replacement-hull"),
    dict(source="voyager",target="voyager-a",kind="name-succession"),
    dict(source="voyager-a",target="voyager-j",kind="later-name-bearer"),
    dict(source="protostar",target="prodigy",kind="prototype-to-production"),
    dict(source="titan",target="titan-a-g",kind="name-succession"),
    dict(source="stargazer-old",target="stargazer-new",kind="name-succession"),
    dict(source="titan-a-g",target="titan-a-g",kind="rename",year=2402),
]

sources["official-enterprises"] = dict(title="It's the Enterprise! Starfleet's Finest Flagships",publisher="StarTrek.com",
    url="https://www.startrek.com/news/enterprise-starfleets-finest-flagships",evidence="Editorial cross-check of Enterprise identities and succession",accessed="2026-09-12")
sources["official-first-contact"] = dict(title="Sector 001: Federation Starships of First Contact",publisher="StarTrek.com",
    url="https://www.startrek.com/news/sector-001-federation-starships-of-first-contact",evidence="Sovereign-class introduction and 2373 battle",accessed="2026-09-12")

data = dict(title="Star Trek · Starships Through Time",version="1.0",as_of="2026-09-12",continuity="Prime",
    scope="Selected individual spacecraft, not complete fleet inventories or class production runs.",
    date_policy="Earth calendar chronology, interpreted from screen dates, stardates and relative dialogue. Unknown construction/launch dates are null. Selected attested years are not exhaustive service endpoints.",
    ships=ships,relations=relations,sources=sources)
assert len({s['id'] for s in ships})==len(ships)
for s in ships:
    assert s['observations'] == sorted(set(s['observations'])), s['id']
    if s['service']:
        assert s['service'][0]<=s['service'][1]
    assert s['launch'] is None or isinstance(s['launch'],int)
    assert s['source'] in sources
target=PROJECT/"data/ships.json"
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(ships=len(ships),designs=len({s['design'] for s in ships}),relations=len(relations),sources=len(sources),output=str(target))))
