#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bundle the verified poster and offline viewer without reference images or tiles."""
from pathlib import Path
import hashlib
import argparse
import json
import shutil
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "artifacts"
ROOT = PROJECT.parents[1]


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--space',action='store_true',help='Package the separate space edition')
    parser.add_argument('--numeric',action='store_true',help='Package the shared calendar-axis edition')
    parser.add_argument('--flow',action='store_true',help='Package the full-context flow application')
    args=parser.parse_args()
    if args.space:OUT=PROJECT/'artifacts/space-edition'
    if args.numeric:OUT=PROJECT/'artifacts/numeric-edition'
    if args.flow:OUT=PROJECT/'artifacts/flow-edition'
    verification = json.loads((OUT / "reviews/final/verification.json").read_text())
    assert verification["status"] == "pass"
    for field,path in [("svg_sha256",OUT / "svgs/star-trek-starships.svg"),
                       ("source_sha256",PROJECT / "data/ships.json")]:
        assert verification[field] == hashlib.sha256(path.read_bytes()).hexdigest()
    review_name='starships-flow-edition-20260912.md' if args.flow else 'starships-numeric-edition-20260912.md' if args.numeric else 'starships-space-edition-20260912.md' if args.space else 'starships-atlas-20260912.md'
    shutil.copyfile(ROOT / 'evaluations/usefulcharts-style' / review_name,OUT / 'reviews/review.md')
    guide = """STAR TREK / STARSHIPS THROUGH TIME

Extract the entire archive, then open viewer/index.html in a modern browser.
The poster, filters and evidence details work without an internet connection.
External source articles need a connection. PDF, SVG and CSV downloads remain
relative to the viewer; keep the extracted folders together.

Use Fit width for the composition and Reading size or the zoom buttons for text.
Search by ship, class, registry or year. Click a fleet lane to inspect evidence.
Each chapter has its own linear year scale. The Enterprise name chain and the
eight lower relationship diagrams are schematic, not duration scales.

Diamonds mark documented launch, commissioning or construction. Solid bands
represent supported service/mission intervals. Dots joined by dashes connect
selected attested years without asserting continuous service. Crosses mark loss;
squares mark retirement, abandonment or dismantling. Unknown launch years stay
unstated. Source qualifications are available in documents/sources.html.

The vector PDF preserves fonts and has a source link for each vessel. Its page is
approximately 36 by 66.98 inches; use tiled printing or a suitable large-format
printer. The SVG is editable and the JSON/CSV preserve the underlying evidence.
SVG body text uses Arial or the system sans-serif fallback; its condensed display
font is embedded under the included open font license.

This independent educational fan reference covers selected Prime-continuity
spacecraft. Original schematic vessel drawings are not to scale or engineering
accurate. Star Trek properties belong to their respective rights holders.
"""
    if args.space:
        art=json.loads((OUT/'reviews/final/art-audit.json').read_text())
        assert art['status']=='pass'
        guide=guide.replace('STARSHIPS THROUGH TIME','STARSHIPS IN MOTION / SPACE EDITION')
        guide=guide.replace('Solid bands','Solid luminous wakes').replace('36 by 66.98','36 by 77.60')
        guide=guide.replace('Original schematic vessel drawings are not to scale or engineering\naccurate.', 'Six reference-guided generated ship illustrations and a generated nebula\nbackground supply the thematic artwork. The illustrations are not to physical\nscale or engineering accuracy. A wake measures years, not distance or speed.\nImages extend beyond endpoint markers without changing the duration.\n\nReusable accepted PNGs are in images/assets/. The exact accepted prompts,\nreference provenance, background/alpha modes and rejected attempts are\nrecorded in data/image-generation.json. Black-background assets are not\ntransparent; the SVG uses screen compositing on its dark-space background.')
    if args.numeric:
        assert json.loads((OUT/'reviews/final/art-audit.json').read_text())['status']=='pass'
        guide="""STAR TREK / FLEET LINES THROUGH TIME

Extract this archive, then open viewer/index.html in a modern browser. The
poster, search, filters and ship details work offline. External source links
need a connection. Keep all extracted folders together for relative downloads.

The horizontal axis is calendar time. Every displayed year has the same x
position in every family. Six piecewise-linear calendar windows expand the
crowded 2360-2385 period. Double slashes mark omitted years. Widths in different
windows cannot be compared without their scales; each window is internally
linear. Thirteen family groups reuse free pockets; local subtracks separate
simultaneous vessels and labels. Family comparison does not imply ancestry.

There are 79 physical spacecraft and 90 separately placed time fragments.
The eleven other-state fragments show 14 later or earlier events for the same
physical hulls. They do not add spacecraft or assert continuous service across
time jumps. The Defiant's Mirror-universe arrival is explicitly labeled.

Diamonds mark documented launch, commissioning or building. Solid wakes show
seven supported service or mission intervals. Dashed wakes connect selected
dated evidence, without asserting uninterrupted service. Crosses mark losses;
squares mark retirement, abandonment or dismantling. L, C and B distinguish
launch, commissioning and build dates. A dash keeps unstated dates unknown.
Two hatched ranges preserve uncertain dating. Wakes measure years, not distance.

The poster selects names, registries, compact class labels, dates and fates.
Six design profiles add original context; the separate inset has no time scale.
Full original notes, source credits, construction evidence and 21 typed links
remain available for all ships in the viewer, JSON, CSV and evidence ledger.

Use Fit width for the composition, Reading size for text, and the family menu
for a region. Search by name, class, registry or primary/secondary year. Select
a ship or other-state fragment for evidence. Related-ship links clear filters.

The editable SVG embeds six reference-guided generated ship assets and its
display font. Illustrations identify design families; reused artwork and hull
markings are illustrative and not to physical scale. The accepted generation
prompts and photographic reference provenance are in data/image-generation.json.
The one-page vector PDF is 52 by 46.11 inches and includes 79 source links.
Use a suitable large-format printer or tiled printing. Full-size PNG is
5200 by 4611 pixels. This is an independent educational fan reference.
"""
    if args.flow:
        assert json.loads((OUT/'reviews/final/art-audit.json').read_text())['status']=='pass'
        guide="""STAR TREK / THE FLEET THROUGH TIME

Extract this archive and open viewer/index.html. The chart, search, filters,
family navigation and complete source records work offline. Keep its folders
together for the relative PDF, SVG, CSV and JSON downloads. External source
articles require an internet connection.

The horizontal axis is calendar time. Six labeled linear windows have different
scales; three double-slash cuts mark omitted years. Every date aligns across
the page. Shared tracks reuse ended fragments without extending their service.
Color and bracketed numbers identify 13 families. Neighbors need not be related.

There are 79 physical spacecraft, 90 state fragments and 79 full printed source
notes. Later or earlier state fragments preserve the same physical hull. Solid
wakes show seven supported service intervals. Dashed wakes join dated evidence
without asserting uninterrupted service. Hatched ranges preserve uncertainty.
Short thin elbows connect labels to exact dates. Lines between nameplates show
typed relationships indexed below the chart, not service duration.

L means launch, C commissioned, B built; a dash means the date is unstated.
The dated marks encode documented launches/builds, sightings, losses, retirement,
museum display or other explicitly identified states. Wakes measure years, not
distance or speed. Artwork identifies design families, not physical scale or
engineering details. Six reference-guided generated ship assets are embedded.

The vector PDF is 64 by 56.02 inches with 79 source links and embedded fonts.
Use a large-format printer or tiled printing. The SVG is editable and the PNG
is 6400 by 5602 pixels. This independent educational fan reference is an
application study: its technical checks pass, but body composition and measured
UsefulCharts reference-density parity remain open. Read reviews/review.md.
"""
    (OUT / "START-HERE.txt").write_text(guide,encoding="utf-8")
    files = ["START-HERE.txt","viewer/index.html","svgs/star-trek-starships.svg",
             "images/star-trek-starships.png","images/star-trek-starships-preview.png",
             "documents/star-trek-starships.pdf","documents/sources.html","documents/font-license.txt",
             "data/ships.json","data/ships.csv","reviews/review.md",
             "reviews/final/verification.json","reviews/final/pdf-audit.json"]
    if args.space:
        files+=['data/image-generation.json','reviews/final/art-audit.json']
        files += [p.relative_to(OUT).as_posix() for p in sorted((OUT/'images/assets').glob('*.png'))]
    if args.numeric or args.flow:files+=['data/image-generation.json','reviews/final/art-audit.json','reviews/layout.json']
    manifest = {p: {"bytes": (OUT/p).stat().st_size,"sha256":hashlib.sha256((OUT/p).read_bytes()).hexdigest()} for p in files}
    (OUT / "manifests").mkdir(exist_ok=True)
    (OUT / "manifests/package.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    files.append("manifests/package.json")
    (OUT / "archives").mkdir(exist_ok=True)
    target = OUT / ('archives/star-trek-starships-flow-edition.zip' if args.flow else 'archives/star-trek-starships-numeric-edition.zip' if args.numeric else 'archives/star-trek-starships-space-edition.zip' if args.space else 'archives/star-trek-starships-offline.zip')
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files:
            archive.write(OUT/path,path)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(files)
        for path,record in manifest.items():
            assert hashlib.sha256(archive.read(path)).hexdigest() == record["sha256"]
    print(json.dumps({"archive":str(target),"files":len(files),"bytes":target.stat().st_size,"integrity":"pass"}))


if __name__ == "__main__":
    main()
