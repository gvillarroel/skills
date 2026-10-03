#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the authored, source-attributed Star Trek poster dataset."""
from pathlib import Path
import json

PROJECT = Path(__file__).resolve().parents[1]
SOURCES = {
    "first": ("First Contact Day", "https://www.startrek.com/news/have-a-great-first-contact-day"),
    "frontier": ("What is Frontier Day?", "https://www.startrek.com/news/what-is-frontier-day"),
    "history": ("Federation history; episode citations", "https://memory-alpha.fandom.com/wiki/Federation_history"),
    "romulan": ("Romulan history; episode citations", "https://memory-alpha.fandom.com/wiki/Romulan_history"),
    "klingon": ("Klingon history; episode citations", "https://memory-alpha.fandom.com/wiki/Klingon_history"),
    "humanklingon": ("Human-Klingon history", "https://memory-alpha.fandom.com/wiki/Human-Klingon_history"),
    "early": ("In the Year 2255; use only the Prime-history passages", "https://www.startrek.com/news/in-the-year-2255"),
    "xindi": ("The Xindi and their Council", "https://www.startrek.com/news/things-to-know-about-the-xindi"),
    "xindus": ("Destruction of Xindus", "https://memory-alpha.fandom.com/wiki/Xindus"),
    "xindiwar": ("Xindi Civil War", "https://memory-alpha.fandom.com/wiki/Xindi_Civil_War"),
    "occupation": ("Occupation of Bajor", "https://memory-alpha.fandom.com/wiki/Occupation_of_Bajor"),
    "bajor": ("Bajoran history", "https://memory-alpha.fandom.com/wiki/Bajoran_history"),
    "bajorancient": ("Bajor: early history", "https://memory-alpha.fandom.com/wiki/Bajor"),
    "cardwar": ("Federation-Cardassian border wars", "https://memory-alpha.fandom.com/wiki/Federation-Cardassian_War"),
    "dmz": ("Federation-Cardassian Treaty", "https://memory-alpha.fandom.com/wiki/Federation-Cardassian_Treaty"),
    "dominion": ("Star Trek 101: The Dominion", "https://www.startrek.com/news/star-trek-101-the-dominion"),
    "dompolitics": ("Galactic Politics: Federation and Dominion", "https://www.startrek.com/news/galactic-politics-the-federation-and-the-dominion"),
    "omarion": ("Deep Space Nine's two-part turning point", "https://www.startrek.com/news/ds9s-two-part-turning-point"),
    "domships": ("The starships of the Dominion War", "https://www.startrek.com/news/the-starships-of-the-dominion-war"),
    "domallies": ("The mystery ally of the Dominion War", "https://www.startrek.com/news/the-mystery-ally-of-the-dominion-war"),
    "return": ("Operation Return: official episode clip", "https://www.startrek.com/videos/star-trek-deep-space-nine-operation-return"),
    "klwar": ("Federation-Klingon War, 2372-73", "https://memory-alpha.fandom.com/wiki/Federation-Klingon_War_%282372-73%29"),
    "conflicts": ("On-screen interstellar conflicts; exclude possible futures", "https://memory-alpha.fandom.com/wiki/Interstellar_history"),
    "borg": ("Borg history", "https://memory-alpha.fandom.com/wiki/Borg_history"),
    "collective": ("The Borg Collective", "https://memory-alpha.fandom.com/wiki/Borg"),
    "8472": ("Borg-Species 8472 War", "https://memory-alpha.fandom.com/wiki/Borg-Species_8472_War"),
    "8472species": ("Species 8472", "https://memory-alpha.fandom.com/wiki/Species_8472"),
    "queen": ("The Borg Queen", "https://www.startrek.com/en-un/news/everything-you-need-to-know-borg-queen"),
    "gorn": ("Gorn Hegemony; on-screen passages only", "https://memory-alpha.fandom.com/wiki/Gorn_Hegemony"),
    "hegemony": ("Hegemony: official recap", "https://www.startrek.com/news/recap-210-hegemony-strange-new-worlds"),
    "hegemony2": ("Hegemony, Part II: official recap", "https://www.startrek.com/news/recap-301-hegemony-part-ii-strange-new-worlds"),
    "terrarium": ("Terrarium: official recap", "https://www.startrek.com/news/recap-309-terrarium-strange-new-worlds"),
    "gornpeople": ("Gorn; dated on-screen encounters", "https://memory-alpha.fandom.com/wiki/Gorn"),
    "progenitors": ("A brief history of the Progenitors", "https://www.startrek.com/news/brief-history-of-the-progenitors"),
    "tkon": ("Tkon Empire; on-screen history only", "https://memory-alpha.fandom.com/wiki/Tkon_Empire"),
    "iconian": ("Iconians; on-screen history only", "https://memory-alpha.fandom.com/wiki/Iconian"),
    "eugenics": ("Eugenics Wars and temporal revisions", "https://memory-alpha.fandom.com/wiki/Eugenics_Wars"),
    "kelvin": ("Nero and the 2387 supernova", "https://www.startrek.com/news/everything-you-need-to-know-about-nero"),
    "protostar": ("The flight of the Protostar", "https://www.startrek.com/news/flight-of-the-protostar-prodigy-journey"),
    "solum": ("Vau N'Akat Civil War; distinguish both timelines", "https://memory-alpha.fandom.com/wiki/Vau_N%27Akat_Civil_War"),
    "solumbattle": ("Battle of Solum", "https://memory-alpha.fandom.com/wiki/Battle_of_Solum"),
    "contacts": ("First contacts; episode attributions", "https://memory-alpha.fandom.com/wiki/First_contacts"),
    "vox": ("Vox: official Picard recap", "https://www.startrek.com/news/recap-star-trek-picard-309-vox"),
    "bounty": ("The Bounty: official Picard recap", "https://www.startrek.com/news/recap-star-trek-picard-306-the-bounty"),
    "enterprise": ("Enterprise: Starfleet's flagships", "https://www.startrek.com/news/enterprise-starfleets-finest-flagships"),
    "burn": ("Discovery's Burn: production science consultants", "https://www.startrek.com/news/the-science-behind-discoverys-burn"),
    "burnhistory": ("The Burn and its aftermath", "https://memory-alpha.fandom.com/wiki/The_Burn"),
    "chain": ("Emerald Chain", "https://memory-alpha.fandom.com/wiki/Emerald_Chain"),
    "hq": ("Battle at Federation Headquarters", "https://memory-alpha.fandom.com/wiki/Battle_at_Federation_Headquarters"),
    "kwejian": ("Kwejian and the DMA", "https://memory-alpha.fandom.com/wiki/Kwejian"),
    "discontacts": ("Discovery's first contacts", "https://www.startrek.com/news/star-trek-discovery-first-contacts-guide"),
    "academy": ("Vox In Excelso: episode and continuity notes", "https://memory-alpha.fandom.com/wiki/Vox_In_Excelso_%28episode%29"),
    "empire": ("Klingon Empire; 32nd-century screen history", "https://memory-alpha.fandom.com/wiki/Klingon_Empire"),
    "32c": ("32nd century; Academy dating uncertainties", "https://memory-alpha.fandom.com/wiki/32nd_century"),
    "time": ("Time travel; episode citations", "https://memory-alpha.fandom.com/wiki/Time_travel"),
    "hell": ("Year of Hell: erased timelines", "https://memory-alpha.fandom.com/wiki/Year_of_Hell"),
    "timeline": ("In-universe series and film chronology", "https://memory-alpha.fandom.com/wiki/Timeline"),
    "endgame": ("Endgame: 2394 return and 2404 intervention", "https://memory-alpha.fandom.com/wiki/Endgame_%28episode%29"),
    "haakonian": ("Haakonian conquest of Talax", "https://memory-alpha.fandom.com/wiki/Haakonian"),
    "life": ("Life, Itself: official Discovery finale recap", "https://www.startrek.com/news/recap-510-discovery-life-itself"),
    "tholian": ("Tholian conflicts and Kyle Riker's unnamed starbase", "https://memory-alpha.fandom.com/wiki/Tholian"),
    "maxia": ("The Battle of Maxia", "https://memory-alpha.fandom.com/wiki/Battle_of_Maxia"),
    "pjem": ("The sanctuary of P'Jem", "https://memory-alpha.fandom.com/wiki/Sanctuary_of_P%27Jem"),
    "kaminar": ("The Sound of Thunder: episode chronology", "https://memory-alpha.fandom.com/wiki/The_Sound_of_Thunder_%28episode%29"),
    "xahea": ("Battle near Xahea", "https://memory-alpha.fandom.com/wiki/Battle_near_Xahea"),
    "farewell": ("Farewell: Jurati's separate Borg and provisional-membership request", "https://www.startrek.com/news/recap-star-trek-picard-farewell"),
    "tzenkethi": ("Federation-Tzenkethi War; approximate chronology", "https://memory-alpha.fandom.com/wiki/Federation-Tzenkethi_War"),
    "kzinti": ("Kzinti Wars: the on-screen account and its date conflict", "https://memory-alpha.fandom.com/wiki/Kzinti_Wars"),
    "temporal": ("Star Trek 101: The Temporal Cold War", "https://www.startrek.com/news/star-trek-101-the-temporal-cold-war"),
    "parth": ("Parth Ferengi's Heart Place: membership application", "https://memory-alpha.fandom.com/wiki/Parth_Ferengi%27s_Heart_Place_%28episode%29"),
    "rom": ("Rom's crucial Deep Space Nine moments", "https://www.startrek.com/news/rom-moments-from-star-trek-deep-space-nine"),
    "phage": ("Vidiian organ harvesting and the Phage", "https://www.startrek.com/news/treknosis-die-and-let-live"),
}

# Each row is authored prose, not a copied synopsis. Screen credits anchor the claims.
# A year is a chronological locator, not a claim that a civilization began then.
ROWS = r'''
2063|earth|Federation|milestone|FIRST CONTACT|Cochrane's Phoenix flight brings the Vulcans to Earth on 5 April. Reconstruction becomes an interstellar project.|First Contact|first
2151|earth|Federation|milestone|Enterprise NX-01|Archer launches Earth's warp-five mission; a human, Vulcan and Denobulan senior crew begins sustained exploration.|ENT: Broken Bow|frontier
2151|klingon|Klingon|contact|Broken Bow|Returning the injured courier Klaang brings humans into direct contact with the Klingon Empire.|ENT: Broken Bow|early
2151|founders|Vulcan|rupture|P'Jem exposed|Archer discovers a Vulcan listening post under the monastery; Andorian distrust gains concrete evidence.|ENT: The Andorian Incident|history
2152|romulan|Romulan|contact|Romulan minefield|NX-01 encounters Romulan territorial defenses. Audio contact conceals their shared ancestry with Vulcans.|ENT: Minefield|early
2152|founders|Andorian|conflict|P'Jem destroyed|Andorian forces destroy the surveillance site, escalating the Vulcan-Andorian confrontation.|ENT: Shadows of P'Jem|history
2153|earth|Federation|war|XINDI CRISIS|A weapon strikes Earth. Archer enters the Delphic Expanse to stop a second, planet-destroying attack.|ENT: The Expanse / S3|xindi
2153|delta|Borg|incursion|The Arctic survivors|Drones left by the 2063 incursion awaken and transmit toward Borg space before NX-01 destroys their ship.|ENT: Regeneration|collective
2153|other|Xindi|context|Five species, one Council|Primates, Arboreals, Aquatics, Reptilians and Insectoids share a council; the Avians died with Xindus.|ENT: The Xindi / The Shipment|xindi
2154|earth|Federation|resolution|Earth saved|Archer and Xindi allies defeat the weapon. Enterprise disables the spheres that sustain the Expanse.|ENT: Zero Hour|xindi
2154|founders|Vulcan|reform|The Kir'Shara|Surak's recovered teachings discredit V'Las. The High Command falls and a planned Andorian attack is stopped.|ENT: Kir'Shara|history
2154|other|Xindi|rupture|The Council divides|Some Xindi reject the Sphere-Builders' deception; Reptilian and Insectoid hardliners continue the attack.|ENT: The Council / Countdown|xindi
2155|founders|Andorian|milestone|Babel and the Coalition|Romulan drone attacks meant to divide humans, Vulcans, Andorians and Tellarites instead encourage cooperation.|ENT: Babel One / United / The Aenar|romulan
2155|earth|Federation|conflict|Terra Prime|Human isolationists try to expel aliens from Earth. Their defeat preserves the interspecies political project.|ENT: Demons / Terra Prime|history
2156|romulan|Romulan|war|EARTH-ROMULAN WAR|Earth and its allies fight the Star Empire. The war precedes the Federation; its full campaigns are not shown.|TOS: Balance of Terror / ENT references|early
2160|romulan|Romulan|resolution|Cheron and the Neutral Zone|Romulan defeat ends the war. A buffer zone separates the powers, with no face-to-face peace negotiation.|TOS: Balance of Terror / TNG: The Defector|early
2161|earth|Federation|milestone|UNITED FEDERATION OF PLANETS|Earth, Vulcan, Andoria and Tellar become the four founding members of a common interstellar polity.|ENT: These Are the Voyages...|frontier
2223|klingon|Klingon|war|A long cold war|Federation-Klingon antagonism intensifies; later disputes combine border battles, proxy struggles and diplomacy.|Star Trek VI / TOS|humanklingon
2239|other|Kelpien|contact|Saru leaves Kaminar|Georgiou brings Saru to Starfleet. His departure does not yet free the Kelpiens from Ba'ul rule.|ST: The Brightest Star|contacts
2245|klingon|Klingon|battle|Donatu V|An inconclusive battle near Sherman's Planet becomes a landmark of the disputed Klingon-Federation frontier.|TOS: The Trouble with Tribbles|humanklingon
2246|earth|Federation|atrocity|Tarsus IV|Governor Kodos orders thousands of colonists killed during a famine; the massacre scars the young James Kirk.|TOS: The Conscience of the King|history
2256|klingon|Klingon|war|WAR AT THE BINARY STARS|T'Kuvma uses confrontation with Starfleet to rally the Great Houses. His death does not stop the war.|DIS: The Vulcan Hello / Battle at the Binary Stars|humanklingon
2257|klingon|Klingon|resolution|L'Rell's settlement|The threat of destroying Qo'noS gives L'Rell leverage to unite the Houses and end the Federation war.|DIS: Will You Take My Hand?|humanklingon
2258|earth|Federation|conflict|Control neutralized|Discovery's allies defeat the rogue intelligence. The ship departs for the future to protect the Sphere data.|DIS: Such Sweet Sorrow, Parts 1-2|discontacts
2257|other|Kelpien|reform|Kaminar's balance changes|Kelpiens pass through vahar'ai instead of being culled; the old Ba'ul system of control is challenged.|DIS: The Sound of Thunder|kaminar
2259|other|Gorn|incursion|Finibus III|Gorn raids devastate the colony and nearly destroy Enterprise. Starfleet prepares for further attacks.|SNW: Memento Mori|gorn
2260|other|Gorn|incursion|Parnassus Beta|The Gorn destroy Cayuga and claim a border through the system. Starfleet tries to prevent a wider war.|SNW: Hegemony|hegemony
2260|earth|Federation|resolution|The invasion interrupted|Pike rescues captives and triggers a Gorn hibernation response, halting the approaching fleet.|SNW: Hegemony, Part II|hegemony2
2261|other|Metron|contact|A Gorn shows compassion|A Metron survival experiment forces Ortegas and a Gorn pilot to cooperate, complicating their mutual hostility.|SNW: Terrarium|terrarium
2266|romulan|Romulan|incursion|Balance of terror|A cloaked Romulan ship attacks Federation outposts. Starfleet finally confirms the Vulcan-Romulan resemblance.|TOS: Balance of Terror|romulan
2267|klingon|Klingon|war|THE ORGANIAN CRISIS|War is declared, but the Organians immobilize both fleets and compel an end to hostilities.|TOS: Errand of Mercy|humanklingon
2267|other|Gorn|battle|Cestus III|The Gorn destroy a colony they consider an intrusion. The Metrons test Kirk and the Gorn captain.|TOS: Arena|gorn
2268|romulan|Romulan|alliance|A limited Klingon connection|Romulans operate Klingon-design warships. Cooperation is real, but does not become a permanent friendship.|TOS: The Enterprise Incident|romulan
2268|other|Tholian|conflict|The Tholian web|Tholian ships trap Enterprise near interphased space; Defiant disappears into another universe and century.|TOS: The Tholian Web / ENT: In a Mirror, Darkly|time
2271|klingon|Klingon|battle|Klach D'kel Brakt|Kor leads a celebrated Klingon victory over Romulan forces; the date is reconstructed from later dialogue.|DS9: Blood Oath|romulan
2285|earth|Federation|battle|Genesis and the Mutara Nebula|Khan seizes Reliant and the Genesis device. Enterprise defeats him, at the cost of Spock's life.|Star Trek II: The Wrath of Khan|conflicts
2286|earth|Federation|crisis|The whale probe|An alien probe threatens Earth's environment. Restored humpback whales answer it and end the crisis.|Star Trek IV: The Voyage Home|timeline
2293|klingon|Klingon|milestone|PRAXIS TO KHITOMER|Praxis explodes. Despite a conspiracy and Gorkon's assassination, negotiations open a durable path to peace.|Star Trek VI: The Undiscovered Country|humanklingon
2311|romulan|Romulan|treaty|Tomed and Algeron|After the Tomed Incident, the treaty reinforces the Neutral Zone and prohibits Federation cloaking research.|TNG: The Neutral Zone / The Pegasus|romulan
2319|cardassia|Cardassian|occupation|BAJOR UNDER OCCUPATION|Cardassian military control begins around this period. Resource extraction and repression provoke organized resistance.|DS9: Emissary / Duet / Waltz|occupation
2328|cardassia|Bajoran|occupation|Formal annexation|Cardassia incorporates Bajor; the imposed government masks coercive military rule rather than voluntary union.|TNG: Ensign Ro / DS9 history|bajor
2344|earth|Federation|alliance|NARENDRA III|Enterprise-C defends a Klingon colony against Romulans. Its sacrifice helps transform Federation-Klingon relations.|TNG: Yesterday's Enterprise|romulan
2346|klingon|Klingon|atrocity|Khitomer massacre|Romulans attack the Klingon colony with inside help from Ja'rod. Worf's family bears the political consequences.|TNG: Sins of the Father / Redemption|romulan
2346|cardassia|Cardassian|occupation|Terok Nor|Bajoran forced labor builds the orbital mining station over several years; it later becomes Deep Space 9.|DS9: Wrongs Darker Than Death or Night|bajor
2347|cardassia|Cardassian|war|CARDASSIAN BORDER WARS|Conflict with the Federation includes the Setlik III massacre; subsequent truces leave disputed colonies unresolved.|TNG: The Wounded / Chain of Command|cardwar
2350|delta|Borg|assimilation|The Hansen family|Borg research ends in assimilation for Magnus, Erin and Annika Hansen. Annika becomes Seven of Nine.|VOY: The Raven / Dark Frontier|collective
2353|other|Tholian|conflict|A starbase attacked|Kyle Riker survives a Tholian attack that kills the base's crew. The episode does not identify the starbase.|TNG: The Icarus Factor|tholian
2355|other|Ferengi|battle|Maxia|A Ferengi ship attacks Stargazer; Picard's maneuver wins the battle and creates a later Ferengi vendetta.|TNG: The Battle|conflicts
2356|delta|Talaxian|war|TALAXIAN-HA AKONIAN WAR|The metreon cascade destroys life on Rinax. Talax surrenders; Neelix loses his family in the catastrophe.|VOY: Jetrel|conflicts
2364|earth|Federation|milestone|Enterprise-D's mission|Picard's flagship begins a new exploration era, encountering Q at Farpoint and a shifting political frontier.|TNG: Encounter at Farpoint|timeline
2364|other|Ferengi|contact|Open contact at Delphi Ardu|Enterprise meets Ferengi representatives and awakens Portal 63, a surviving guardian of the ancient Tkon Empire.|TNG: The Last Outpost|tkon
2364|romulan|Romulan|crisis|Outposts disappear|Both Romulan and Federation border outposts are destroyed. The unseen threat precedes confirmed Borg contact.|TNG: The Neutral Zone|collective
2365|delta|Borg|contact|Q at system J-25|Q forces Enterprise-D into a Borg encounter. Conventional Starfleet assumptions fail against the adaptive cube.|TNG: Q Who|borg
2366|other|Douwd|atrocity|The Husnock erased|Kevin Uxbridge, a Douwd, retaliates for a colony's destruction by annihilating the entire Husnock species.|TNG: The Survivors|conflicts
2366|cardassia|Cardassian|treaty|A fragile truce|The border war winds down. An armistice in 2367 precedes the final territorial settlement of 2370.|TNG: The Wounded / Journey's End|cardwar
2367|delta|Borg|battle|WOLF 359|Locutus's knowledge helps a Borg cube devastate Starfleet. Enterprise recovers Picard and stops the assault on Earth.|TNG: The Best of Both Worlds, Parts 1-2|borg
2367|klingon|Klingon|war|KLINGON CIVIL WAR|Gowron contests the Duras faction, whose covert Romulan support is exposed by a Federation blockade.|TNG: Redemption, Parts 1-2|klingon
2367|other|Talarian|conflict|A contested border child|Jono's case exposes the legacy of Federation-Talarian raids and the competing claims of family and state.|TNG: Suddenly Human|conflicts
2368|founders|Vulcan|diplomacy|Spock on Romulus|Spock promotes peaceful reunification. Sela attempts to exploit the movement as cover for an invasion of Vulcan.|TNG: Unification, Parts 1-2|romulan
2368|delta|Borg|rupture|Hugh's individuality|A rescued drone returns to the Collective with an individual identity, helping destabilize a group of Borg.|TNG: I, Borg / Descent|borg
2369|cardassia|Bajoran|milestone|BAJOR REGAINS CONTROL|Cardassia withdraws. Bajor's provisional government invites Starfleet to administer the renamed Deep Space 9.|DS9: Emissary|occupation
2369|earth|Federation|contact|The Gamma Quadrant opens|Sisko and Dax discover the stable Bajoran wormhole; the Prophets become a religious and strategic presence.|DS9: Emissary|bajor
2369|founders|Vulcan|discovery|A common humanoid inheritance|Human, Klingon, Romulan and Cardassian representatives uncover the Progenitors' ancient genetic message.|TNG: The Chase|progenitors
2369|klingon|Klingon|reform|An emperor without state power|A clone of Kahless becomes a ceremonial emperor; Gowron retains practical political leadership.|TNG: Rightful Heir|klingon
2370|cardassia|Cardassian|treaty|THE DEMILITARIZED ZONE|The border treaty relocates sovereignty over colonies. Some displaced Federation citizens form the Maquis.|TNG: Journey's End / DS9: The Maquis|dmz
2370|dominion|Dominion|war|THE DOMINION REVEALS ITSELF|Jem'Hadar destroy Odyssey and attack Gamma Quadrant settlements. The Founders govern through Vorta and soldiers.|DS9: The Jem'Hadar|dominion
2371|dominion|Dominion|discovery|Odo finds the Great Link|The Founders are Changelings. Their pursuit of security takes the form of control over other peoples.|DS9: The Search, Parts 1-2|dominion
2371|romulan|Romulan|battle|OMARION NEBULA|A Tal Shiar-Obsidian Order fleet attacks the Founders, falls into an ambush and is destroyed.|DS9: Improbable Cause / The Die Is Cast|omarion
2371|cardassia|Bajoran|treaty|Bajor-Cardassia accord|Negotiations establish a new peace agreement between the former occupier and occupied world.|DS9: Life Support|bajor
2371|delta|Kazon|conflict|Voyager in the Delta Quadrant|The Caretaker strands Starfleet and Maquis crews far from home; Kazon factions fight for technology and resources.|VOY: Caretaker|conflicts
2371|delta|Vidiian|contact|The Phage|Vidiian organ harvesting brings them into conflict with Voyager, revealing a civilization transformed by disease.|VOY: Phage / Faces|contacts
2372|cardassia|Cardassian|war|KLINGONS INVADE CARDASSIA|Gowron claims the new civilian government is infiltrated. The invasion weakens Cardassia and strains the alliance.|DS9: The Way of the Warrior|dompolitics
2372|klingon|Klingon|war|ALLIANCE BROKEN|Federation opposition to the invasion ruptures the Khitomer relationship; open war follows over Archanis.|DS9: The Way of the Warrior / Broken Link|klwar
2372|earth|Federation|crisis|A coup on Earth fails|Changeling fears let Admiral Leyton attempt military control; Sisko exposes the manufactured crisis.|DS9: Homefront / Paradise Lost|dompolitics
2372|dominion|Dominion|conflict|An Iconian gateway destroyed|Starfleet and loyal Jem'Hadar cooperate against rebels who could use an ancient gateway to bypass defenses.|DS9: To the Death|iconian
2373|cardassia|Cardassian|alliance|DUKAT JOINS THE DOMINION|Dukat takes power under Dominion patronage. Jem'Hadar drive out the Klingons and crush the Maquis.|DS9: By Inferno's Light / Blaze of Glory|klwar
2373|klingon|Klingon|alliance|The Khitomer alliance restored|The Dominion foothold brings Gowron and Sisko back together; Martok leads a Klingon presence at DS9.|DS9: By Inferno's Light|klwar
2373|romulan|Romulan|treaty|Nonaggression, for now|The Star Empire signs a pact with the Dominion, remaining outside the opening Federation alliance.|DS9: Call to Arms|omarion
2373|cardassia|Bajoran|treaty|Bajor stays neutral|On Sisko's advice, Bajor signs a Dominion nonaggression pact. Neutrality is not Dominion membership.|DS9: Call to Arms|domallies
2373|earth|Federation|war|THE DOMINION WAR BEGINS|Starfleet mines the wormhole. Dominion-Cardassian forces seize DS9 while the Federation and Klingons attack Torros III.|DS9: Call to Arms|domships
2373|delta|Borg|battle|SECTOR 001|A second cube is destroyed near Earth. Its sphere travels to 2063, where Enterprise-E preserves First Contact.|Star Trek: First Contact|collective
2373|delta|Borg|war|BORG-SPECIES 8472 WAR|A Borg invasion of fluidic space provokes a devastating counterattack. Voyager provides an effective nanoprobe defense.|VOY: Scorpion, Parts 1-2|8472
2373|other|Q|war|Q CIVIL WAR|Conflict over change within the Continuum spills into stellar space. Voyager helps resolve the confrontation.|VOY: The Q and the Grey|conflicts
2374|earth|Federation|battle|OPERATION RETURN|The Federation and Klingons retake DS9. The Prophets remove the Dominion reinforcement fleet from the wormhole.|DS9: Favor the Bold / Sacrifice of Angels|return
2374|romulan|Romulan|alliance|ROMULANS ENTER THE WAR|Vreenak's death and fabricated evidence persuade the Star Empire that the Dominion threatens it; the alliance expands.|DS9: In the Pale Moonlight|domallies
2374|dominion|Dominion|occupation|Betazed falls|Dominion forces seize a Federation member world, bringing the war close to major population centers.|DS9: In the Pale Moonlight|dompolitics
2374|cardassia|Cardassian|battle|First Chin'toka offensive|Federation, Klingon and Romulan fleets capture a foothold inside Cardassian territory.|DS9: Tears of the Prophets|domships
2374|delta|Borg|rupture|Seven leaves the Collective|Voyager's temporary cooperation with the Borg ends. Seven of Nine begins life outside the hive mind.|VOY: Scorpion, Part II / The Gift|8472
2374|delta|Hirogen|conflict|The hunters take Voyager|Hirogen use captive crews in lethal holodeck hunts. Janeway negotiates a settlement involving holographic technology.|VOY: The Killing Game, Parts 1-2|conflicts
2375|dominion|Breen|alliance|BREEN JOIN THE DOMINION|The Confederacy changes the balance of the war with an energy-dampening weapon and a strike on Earth.|DS9: Strange Bedfellows / The Changing Face of Evil|domships
2375|earth|Federation|battle|Earth struck; Chin'toka lost|The Breen raid Starfleet Headquarters. Their weapon devastates the alliance fleet at the second Chin'toka battle.|DS9: The Changing Face of Evil|domships
2375|cardassia|Cardassian|rebellion|DAMAR'S REBELLION|Cardassian resistance turns against Dominion rule. Kira and Garak help the movement adopt insurgent tactics.|DS9: The Changing Face of Evil / Tacking Into the Wind|domallies
2375|klingon|Klingon|reform|Martok becomes Chancellor|Worf kills Gowron over his destructive wartime leadership and gives the chancellorship to Martok.|DS9: Tacking Into the Wind|klingon
2375|dominion|Dominion|crisis|The Founders' infection|Section 31's biological attack threatens the Great Link. Bashir secures a cure, later carried by Odo.|DS9: Extreme Measures / What You Leave Behind|bounty
2375|cardassia|Cardassian|battle|THE BATTLE OF CARDASSIA|Cardassian ships switch sides. Dominion reprisals devastate the population before the final surrender.|DS9: What You Leave Behind|domallies
2375|earth|Federation|treaty|PEACE AT BAJOR|The Dominion surrenders. Odo returns to the Great Link with the cure; the Alpha Quadrant war ends.|DS9: What You Leave Behind|dominion
2375|other|Ferengi|reform|Rom becomes Grand Nagus|Zek's reforms and Rom's succession challenge traditional Ferengi structures of wealth, welfare and gender.|DS9: The Dogs of War|contacts
2375|other|Ba'ku|conflict|The Ba'ku-Son'a conflict|A forced-relocation scheme conceals a family rupture: the Son'a are exiled Ba'ku seeking their world's restorative properties.|Star Trek: Insurrection|conflicts
2375|delta|8472|diplomacy|Fear gives way to dialogue|Voyager meets Species 8472 on a replica of Starfleet Headquarters; negotiation defuses a planned infiltration.|VOY: In the Flesh|8472species
2376|delta|Vaadwaur|conflict|An ancient power returns|Voyager revives Vaadwaur survivors. Their attempt to recover regional dominance ends in battle and dispersal.|VOY: Dragon's Teeth|conflicts
2377|delta|Borg|rebellion|UNIMATRIX ZERO|Drones organize an individualist resistance. Voyager supports the movement against the Borg Queen.|VOY: Unimatrix Zero, Parts 1-2|borg
2377|delta|Hirogen|rebellion|Holograms fight their hunters|Iden's rebellion turns Hirogen hunting technology against its creators; Voyager confronts the revolt's excesses.|VOY: Flesh and Blood|conflicts
2378|delta|Borg|milestone|ENDGAME|An alternate future Janeway infects the Collective. Voyager destroys a transwarp hub and returns to Earth early.|VOY: Endgame|collective
2379|romulan|Reman|coup|SHINZON'S COUP|A Reman-backed ruler replaces the Romulan Senate. His promised peace hides a plan to attack Earth.|Star Trek: Nemesis|history
2379|earth|Federation|battle|The Bassen Rift|Enterprise-E and Romulan allies stop Scimitar. Data's sacrifice destroys the thalaron weapon.|Star Trek: Nemesis|conflicts
2380|other|Pakled|conflict|Pakled attacks|Salvaged technology turns the Pakleds into a serious threat; their attack destroys Solvang and nearly defeats Cerritos.|LD: No Small Parts|timeline
2381|klingon|Klingon|rupture|Dorg's covert war|A Klingon captain arms Pakled attacks on the Federation. His removal stops the scheme without a general Klingon war.|LD: wej Duj|klingon
2381|other|Ferengi|diplomacy|Federation talks on Ferenginar|Rom and Leeta test Starfleet's negotiators while pursuing membership talks; talks are not a confirmed accession date.|LD: Parth Ferengi's Heart Place|contacts
2384|earth|Federation|attack|The Living Construct|A Vau N'Akat weapon turns Starfleet ships against one another. The Protostar crew sacrifices its ship to stop it.|PRO: Supernova, Parts 1-2|solum
2384|other|Vau N'Akat|war|THE STRUGGLE FOR SOLUM|Asencia imposes rule with future technology. Ilthuran's Uprising and Gwyndala oppose her project of vengeance.|PRO S2 / Ouroboros, Parts 1-2|solum
2385|other|Vau N'Akat|resolution|A different first contact|Asencia is defeated. Solum opens peaceful contact with the Federation, changing the future that produced the Diviner.|PRO: Ouroboros, Part II|solumbattle
2385|earth|Federation|attack|MARS AND THE SYNTHETIC BAN|Sabotaged synths destroy Utopia Planitia and the rescue fleet. Starfleet abandons the Romulan evacuation effort.|ST: Children of Mars / PIC S1|protostar
2387|romulan|Romulan|catastrophe|THE ROMULAN SUPERNOVA|Romulus is lost and the imperial order fragments. Spock and Nero disappear into the event that creates the Kelvin branch.|Star Trek (2009) / PIC S1|kelvin
2399|romulan|Romulan|context|Successor powers and the Artifact|The Romulan Free State operates in the aftermath; a captured Borg cube houses a contested reclamation project.|PIC: Maps and Legends / The Impossible Box|queen
2399|earth|Federation|crisis|Coppelius|The Zhat Vash seek to destroy synthetic life. Picard's intervention and Starfleet's arrival avert the final assault.|PIC: Et in Arcadia Ego, Parts 1-2|timeline
2401|delta|Borg|alliance|JURATI'S COOPERATIVE BORG|A separate Queen seeks voluntary connection and provisional Federation membership to guard a transwarp conduit.|PIC: Farewell|farewell
2401|dominion|Dominion|rupture|Rogue Changelings|Survivors of Section 31 experiments work with the Borg Queen; this faction is not the entire Dominion.|PIC: Dominion / The Bounty|bounty
2401|earth|Federation|attack|FRONTIER DAY|Altered transporter code enables the Borg to assimilate young crew members and seize the networked fleet.|PIC: Vox|vox
2401|delta|Borg|resolution|The Jupiter hive destroyed|Enterprise-D rescues Jack and destroys the attacking Queen's cube. Jurati's separate collective is not erased by this victory.|PIC: The Last Generation|enterprise
2402|earth|Federation|milestone|Enterprise-G|Seven of Nine commands the renamed Titan-A, beginning a new exploratory chapter after the Frontier Day attack.|PIC: The Last Generation|enterprise
2151|other|Suliban|war|THE TEMPORAL COLD WAR|Future factions use agents such as the Suliban Cabal to alter Archer's era. The 2151-2154 encounters form one front in a conflict across centuries.|ENT: Broken Bow / Cold Front / Storm Front|temporal
2269|other|Kzinti|war|THE FOUR KZINTI WARS|Sulu recalls four Kzinti defeats by humans. Their dating conflicts with later human-spaceflight history; the Treaty of Sirius restricts Kzinti armaments.|TAS: The Slaver Weapon|kzinti
2360|other|Tzenkethi|war|FEDERATION-TZENKETHI WAR|Sisko serves aboard Okinawa during this earlier conflict. In 2371, a Changeling tries to provoke renewed hostilities.|DS9: The Adversary / Paradise Lost|tzenkethi
'''

ORIGINS = [
    ("Billions of years ago", "Progenitors", "Ancient humanoids seed life across many worlds, leaving a genetic message later found in 2369.", "TNG: The Chase", "progenitors"),
    ("c.600,000 years ago", "Tkon Empire", "A stellar catastrophe ends a civilization able to move stars; isolated guardians outlast the empire.", "TNG: The Last Outpost", "tkon"),
    ("c.500,000 years ago", "Bajoran civilization", "Bajor's culture flourishes long before human spaceflight; its later occupation is not its historical beginning.", "TNG: Ensign Ro", "bajorancient"),
    ("c.200,000 years ago", "Iconia bombarded", "Iconian gateways survive the destruction of their homeworld. Later powers compete over that technology.", "TNG: Contagion / DS9: To the Death", "iconian"),
    ("c.4th century CE", "Vulcan's Time of Awakening", "Surak's logic reforms Vulcan. Those who leave eventually become the Romulan civilization; the exodus is not precisely dated.", "ENT: Awakening / Kir'Shara", "romulan"),
    ("c.10th century", "Kahless and the First Empire", "Kahless defeats Molor and unifies Klingon society; history and sacred tradition overlap in the surviving account.", "TNG: Rightful Heir", "klingon"),
    ("14th century", "The Hur'q invasion", "Invaders from the Gamma Quadrant sack Qo'noS and steal the Sword of Kahless. Their rule does not last.", "DS9: The Sword of Kahless", "klingon"),
    ("1484", "Vaadwaur defeat", "A hostile coalition destroys Vaadwaur power. Survivors enter stasis; contemporary Borg hold only a few systems.", "VOY: Dragon's Teeth", "collective"),
    ("c.16th century", "Bajoran solar sailors", "Lightships reach interstellar space; evidence of an ancient voyage to Cardassia later challenges Cardassian prejudice.", "DS9: Explorers", "bajorancient"),
    ("1930s-2030s", "Xindi Civil War", "A long interspecies war destroys Xindus in 2033. Five species escape; the Avians become extinct.", "ENT: The Shipment", "xindiwar"),
    ("Dates altered by time travel", "Eugenics Wars", "TOS gives 1992-96. SNW places young Khan in the 21st century and attributes the delay to temporal interference.", "TOS: Space Seed / SNW: Tomorrow and Tomorrow and Tomorrow", "eugenics"),
    ("21st century; ends 2053", "World War III", "Earth's devastating global war precedes the 2063 contact. Later screen accounts revise the sequence of earlier wars.", "First Contact / SNW: Strange New Worlds", "eugenics"),
]

FUTURE = [
    ("26th-31st centuries", "Temporal conflicts", "Future factions intervene in earlier centuries. A future battle at Procyon V is a contested outcome, not a guaranteed Prime event.", "ENT: Azati Prime / Storm Front", "time"),
    ("By the 32nd century", "The Temporal Accords", "Time travel is prohibited after the Temporal Wars; Discovery's displaced crew encounters this new legal order.", "DIS: That Hope Is You, Part 1 / Die Trying", "time"),
    ("c.3069", "THE BURN", "Active dilithium becomes inert, destroying warp-powered ships. Interstellar transport and Federation cohesion collapse.", "DIS S3", "burn"),
    ("After the Burn", "The Klingon diaspora", "Qo'noS and the imperial system are devastated. Surviving Houses become displaced communities rather than a united empire.", "SA: Vox In Excelso", "empire"),
    ("By 3189", "Vulcan and Romulus: NI'VAR", "Vulcans and Romulans have reunited. Their world's departure from the Federation follows the Burn; the unification date is unknown.", "DIS: Unification III", "burnhistory"),
    ("3188-3189", "Discovery reaches a fractured future", "Burnham arrives first; Discovery follows a year later. The Federation's known membership has fallen from a peak of 350 to 38 worlds.", "DIS: That Hope Is You, Part 1 / Die Trying", "history"),
    ("3189", "EMERALD CHAIN DEFEATED", "Osyraa's attack on Federation Headquarters fails. Her death fractures the Orion-Andorian syndicate; dilithium distribution aids recovery.", "DIS: That Hope Is You, Part 2", "hq"),
    ("3190", "Species 10-C and the DMA", "An extragalactic mining device destroys Kwejian. Communication with its creators ends the crisis; this was not a declared invasion.", "DIS: Species Ten-C / Coming Home", "kwejian"),
    ("3190", "Federation reconstruction", "Ni'Var and Earth return. Contact with Species 10-C and renewed cooperation shift the balance toward diplomacy and exploration.", "DIS: All Is Possible / Coming Home", "discontacts"),
    ("3191", "Breen and Progenitor technology", "Breen succession politics intersect with the search for a power capable of creating life. Discovery ultimately relinquishes that power.", "DIS: Red Directive / Life, Itself", "life"),
    ("3190s; dating varies", "FAAN ALPHA", "Starfleet and Klingon leaders stage a bloodless battle so refugees can accept a new home through an honorable symbolic conquest.", "SA: Vox In Excelso", "academy"),
    ("c.3195-3196", "A new Academy generation", "The San Francisco campus welcomes cadets from a rebuilding galaxy. Personnel files, dialogue and stardates do not align perfectly.", "SA S1 / Kids These Days / Rubincon", "32c"),
]

BRANCHES = [
    ("KELVIN", "2233 / 2258-2263", "Nero arrives from Prime 2387 and destroys Kelvin. Vulcan is destroyed in 2258; the Khan and Krall conflicts belong to this branch.", "Star Trek (2009) / Into Darkness / Beyond", "kelvin"),
    ("MIRROR", "2063 / 2155 / 2267 / 2370s", "The Terran Empire follows an altered history. By DS9, a Klingon-Cardassian Alliance dominates former Terran territory and faces human rebellion.", "ENT: In a Mirror, Darkly / TOS: Mirror, Mirror / DS9 mirror episodes", "time"),
    ("YESTERDAY'S ENTERPRISE", "2344 -> 2366 -> restored", "Enterprise-C's disappearance creates a Federation-Klingon war timeline. Its return to Narendra III restores the history of cooperation.", "TNG: Yesterday's Enterprise", "romulan"),
    ("YEAR OF HELL", "2374 -> erased", "Annorax's Krenim weapon repeatedly rewrites civilizations. Voyager destroys it; the catastrophic year is removed from the surviving history.", "VOY: Year of Hell, Parts 1-2", "hell"),
    ("ENDGAME", "2404 -> 2378; future replaced", "In the replaced future, Voyager returns in 2394. Janeway travels from 2404 to bring the ship home in 2378 instead.", "VOY: Endgame", "endgame"),
    ("CONFEDERATION", "2024 divergence -> 2401", "Q places Picard in a human-supremacist future. Intervention around Renee Picard's Europa mission restores the Federation present.", "PIC S2 / Farewell", "time"),
    ("SOLUM'S LOST FUTURE", "2430s -> 2383-2385", "A future Vau N'Akat civil war produces the Diviner's revenge mission. Gwyndala and her allies change Solum's path before that outcome.", "PRO S1-S2", "protostar"),
    ("PROCYON V", "Possible 26th century", "The Sphere-Builders see a future defeat by the Federation and manipulate the Xindi in response. Treat the battle as conditional, not fixed.", "ENT: Azati Prime / Zero Hour", "xindi"),
]

def main():
    events = []
    for index, row in enumerate(ROWS.strip().splitlines(), 1):
        year, lane, actor, kind, label, detail, credit, source = row.split("|")
        events.append(dict(id=f"st-{index:03}", year=int(year), date=year, lane=lane, actor=actor,
                           kind=kind, label=label, detail=detail, credit=credit, source=source))
    for event in events:
        if event["label"] == "Federation talks on Ferenginar": event["source"] = "parth"
        if event["label"] == "Rom becomes Grand Nagus": event["source"] = "rom"
        if event["label"] == "The Phage": event["source"] = "phage"
        if event["label"] == "The Ba'ku-Son'a conflict":
            event["detail"] = "A Starfleet admiral's relocation scheme exposes the Son'a as exiled Ba'ku. The Son'a also supply the Dominion with ketracel-white."
            event["credit"] = "Insurrection / DS9: Penumbra"
            event["source"] = "domallies"
        if event["label"] == "THE TEMPORAL COLD WAR": event["date"] = "2151-2154: Archer's front"
        if event["label"] == "THE FOUR KZINTI WARS": event["date"] = "Earlier wars; recalled in 2269"
        if event["label"] == "FEDERATION-TZENKETHI WAR": event["date"] = "c.early 2360s; before 2371"
        if event["label"] in {"P'Jem exposed", "P'Jem destroyed"}: event["source"] = "pjem"
        if event["label"] == "Control neutralized": event["source"] = "xahea"
        if event["label"] == "Maxia": event["source"] = "maxia"
        if event["label"] == "BAJOR UNDER OCCUPATION": event["date"] = "c.2319-2369"
        if event["label"] == "Terok Nor": event["date"] = "2346-2351"
        if event["label"] == "EARTH-ROMULAN WAR": event["date"] = "2156-2160"
        if event["label"] == "WAR AT THE BINARY STARS": event["date"] = "2256-2257"
        if event["label"] == "XINDI CRISIS": event["date"] = "2153-2154"
        if event["label"] == "KLINGON CIVIL WAR": event["date"] = "2367-2368"
        if event["label"] == "CARDASSIAN BORDER WARS": event["date"] = "2347-2366; treaty 2370"
        if event["label"] == "KLINGONS INVADE CARDASSIA": event["date"] = "2372-2373"
        if event["label"] == "ALLIANCE BROKEN": event["date"] = "2372-2373"
        if event["label"] == "THE DOMINION WAR BEGINS": event["date"] = "2373-2375"
        if event["label"] == "BORG-SPECIES 8472 WAR": event["date"] = "2373-2374"
        if event["label"] == "THE STRUGGLE FOR SOLUM": event["date"] = "2384-2385"
        if event["label"] in {"Klach D'kel Brakt", "The Ba'ku-Son'a conflict"}: event["date"] = "c."+str(event["year"])
        if event["label"] in {"Parnassus Beta", "The invasion interrupted"}: event["date"] = "c.2260"
        if event["label"] == "TALAXIAN-HA AKONIAN WAR":
            event["label"] = "TALAXIAN-HAAKONIAN WAR"
            event["date"] = "c.2346-2356"
            event["source"] = "haakonian"
    cards = lambda prefix, rows: [dict(id=f"st-{prefix}-{i:02}", date=r[0], label=r[1], detail=r[2], credit=r[3], source=r[4]) for i,r in enumerate(rows,1)]
    branches = [dict(id=f"st-branch-{i:02}", label=r[0], date=r[1], detail=r[2], credit=r[3], source=r[4]) for i,r in enumerate(BRANCHES,1)]
    data = dict(schema_version=1, title="STAR TREK", subtitle="CIVILIZATIONS, WARS & THE PRIME TIMELINE",
                researched="2026-09-12", language="en", events=events, origins=cards("origin",ORIGINS),
                future=cards("future",FUTURE), branches=branches,
                sources={key:dict(title=value[0],url=value[1],type="official" if "startrek.com" in value[1] else "episode-index") for key,value in SOURCES.items()},
                scope="Selected major on-screen civilizations, conflicts and political changes. Prime continuity is the main history; alternate and erased timelines are separated. Gregorian years; schematic chronological spacing, not a uniform elapsed-time scale. Colored strands track subjects, not foundation or extinction dates.")
    all_records = events+data["origins"]+data["future"]+branches
    assert len({e["id"] for e in all_records}) == len(all_records)
    assert all(e["source"] in data["sources"] and e["credit"] for e in all_records)
    target=PROJECT/"data/timeline.json"
    target.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"path":str(target),"main_events":len(events),"origin_entries":len(ORIGINS),"future_entries":len(FUTURE),"alternative_branches":len(branches),"sources":len(SOURCES)}))

if __name__ == "__main__":
    main()
