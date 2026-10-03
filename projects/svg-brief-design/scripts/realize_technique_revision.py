#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Realize the one budgeted construction revision from public evidence only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from seal_technique_evolution import REPO, ROOT, REALIZER, sha, read, write

ORBIT = '''def orbit(group, p, box, weight):
    """Repeat original tapered polar bands while preserving a clear central disk."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    outer = min(w, h) / 2 - weight
    inner = outer * bounded(p, "inner_ratio", .64, .2, .9)
    n = count(p, "count", 5, 3, 24)
    coverage = bounded(p, "coverage", 1.35, .25, 1.8)
    taper = bounded(p, "taper", 1.1, .5, 3)
    rotation = math.radians(bounded(p, "rotation", -90, -360, 360))
    direction = p.get("direction", 1)
    if direction not in (-1, 1):
        raise ValueError("direction must be 1 or -1")
    span = outer - inner
    sweep = direction * 2 * math.pi / n * coverage
    steps = max(96, math.ceil(abs(sweep) * 40))
    for band in range(n):
        outside, inside = [], []
        for j in range(steps + 1):
            t = j / steps
            angle = rotation + direction * band * 2 * math.pi / n + t * sweep
            mid = (inner + outer) / 2 + span * .12 * math.sin(2 * math.pi * t)
            half = span * .35 * max(0, math.sin(math.pi * t)) ** taper
            # .12 + .35 < .5 keeps both boundaries strictly inside the
            # declared annulus for every t, regardless of repetition count.
            outside.append((cx + (mid + half) * math.cos(angle), cy + (mid + half) * math.sin(angle)))
            inside.append((cx + (mid - half) * math.cos(angle), cy + (mid - half) * math.sin(angle)))
        node(group, "path", id=f"orbit-band-{band + 1}",
             d=path_points(outside + list(reversed(inside)), close=True),
             fill="currentColor", stroke="none")


'''

GUIDE = '''# Purpose and construction

Use these methods when their geometry and information needs fit the brief.
They provide starting structures; they do not select a finished design for you.

## Preserve the requested topology

Translate spatial words into reserved regions before making paths. An empty
center means a clear central area, not several small white cells separated by
lines. A frame's curves belong around its opening. A long bar keeps its shallow
occupied proportions even on a larger canvas. An open body needs edges whose
alignment and spacing imply continuity across gaps.

For a flowing circular frame, start with the original `orbit` scaffold:

```text
python <skill-root>/scripts/scaffold.py init orbit --recipe design.json --output artwork.svg
```

Edit its count, inner_ratio, coverage, taper, rotation and direction, then build
again. The generator confines tapered bands to an annulus, so they cannot cross
the reserved central disk. Lower coverage separates the bands; higher coverage
overlaps their ends. Choose the relationship the brief needs, inspect the joins
and shape the gaps before adding details. Do not add a second rim merely to hide
awkward junctions. For a noncircular subject, make different geometry rather than
forcing an orbit into it. Other exact geometry belongs in the scaffold guide.

## Let white describe the form

For an open mechanical form, draw its principal rails, plates or facets around
the channels that describe its body. Coordinate their directions and widths;
connected contour flow can imply a body without filling the whole silhouette.
Avoid a solid slab followed by a few tiny holes. Keep essential facial openings
and joints visible after all black parts overlap. Inspect their combined shape.

## Match notation and ink to the use

For a sparse printed illustration, begin with the explanatory trace and joined
axes. Give them related, substantial weights at the final display size; check
that arrowheads meet their shafts without a collar. A practical starting point
is a principal trace about 1–2 percent of the occupied drawing's short dimension,
with axes slightly quieter. Adjust optically after rendering. Add only reference
letters that explain the relationship, and use coherent curvature rather than
jitter to vary an organic gesture. A serif font by itself does not create the
print idiom. Preserve mathematical accuracy and requested measurements whenever
the brief asks for a quantitative graph.

For a compact identifier, choose the shallow footprint and primary identifier
first. Add required codes or navigation cues in a clear order. Do not invent a
full specification table, but do not remove a requested code, heading or data
field in the name of simplicity. If a machine-readable code is requested, encode
its actual payload with an appropriate implementation.

Render and open the drawing at working size and as a thumbnail. Check the brief's
reserved regions and required features before judging decoration. Repair one
visible relationship—such as a pinched opening, merged joint or oversized label—
and render the final state again. Do not claim a visual inspection without one.
'''

TESTS = '''    def test_orbit_reserves_empty_center(self):
        recipe = scaffold.defaults("orbit")
        image = rgba(scaffold.build(recipe))
        alpha = image.getchannel("A")
        self.assertIsNone(alpha.crop((150, 150, 330, 330)).getbbox())
        self.assertIsNotNone(alpha.getbbox())
        root = ET.fromstring(scaffold.build(recipe))
        bands = [e for e in root.iter() if e.get("id", "").startswith("orbit-band-")]
        self.assertEqual(len(bands), 5)
        self.assertTrue(all(e.get("stroke") == "none" for e in bands))

    def test_orbit_boundary_and_parameter_extremes(self):
        for n, coverage, inner, taper, direction in [(3,.25,.2,.5,1),(24,1.8,.9,3,-1),(8,1.5,.55,1,1)]:
            recipe = scaffold.defaults("orbit")
            recipe["parameters"].update(count=n,coverage=coverage,inner_ratio=inner,taper=taper,direction=direction)
            alpha = rgba(scaffold.build(recipe)).getchannel("A")
            box = alpha.getbbox()
            self.assertIsNotNone(box)
            self.assertTrue(20 <= box[0] < box[2] <= 460 and 20 <= box[1] < box[3] <= 460)
            self.assertEqual(alpha.getpixel((240,240)),0)

    def test_orbit_rejects_invalid_geometry(self):
        for key,value in [("inner_ratio",0),("inner_ratio",1),("count",3.5),("coverage",2),("taper",float("nan")),("direction",0)]:
            recipe = scaffold.defaults("orbit")
            recipe["parameters"][key]=value
            with self.assertRaises(ValueError): scaffold.build(recipe)

'''


def main():
    evidence = ROOT / "development-supplement.json"
    assert evidence.exists() and not (ROOT / "validation-release-ready.json").exists()
    supplement = read(evidence)
    assert supplement["comparison"]["complete_evaluable"]
    config = read(ROOT / "realize-cv.json")
    r = config["realization"]
    r.update(id="constructive-space-v2",candidateId="d",workspaceDir=str(ROOT / "workspace-d"),outputDir=str(ROOT / "sealed-d"))
    r["operator"]={"operatorId":"reserve-space-procedurally","instruction":"Return to the preserved baseline, replace the broad mandatory guide with concise conditional construction guidance and a brief-first spatial contract. Add an original parametric annular tapered-band scaffold that reserves the central opening; add meaningful geometry/render tests and document editing controls. No original paths, copied artwork or fixed benchmark designs. Preserve other scaffold behavior and required information.","origin":"development-reflection","parentOperatorIds":["construct-mass-and-void"]}
    r["allowedChanges"]=["SKILL.md","references/construction-decisions.md","references/scaffold-recipes.md","scripts/scaffold.py","scripts/test_scaffold.py"]
    r["developmentEvidence"].append({"id":"first-candidate-complete-development","role":"development","path":str(evidence),"sha256":"sha256:"+sha(evidence)})
    path=ROOT / "realize-d.json";write(path,config)
    subprocess.run([sys.executable,str(REALIZER),"prepare",str(path)],check=True)
    candidate=ROOT / "workspace-d/candidate/skills/svg-brief-design"
    skill=candidate / "SKILL.md"
    text=skill.read_text(encoding="utf-8")
    insertion='''
First make a compact checklist of the brief's subject, occupied proportions,
required features and regions that must stay empty. Preserve those relationships
before adding style or detail. An opening divided by lines is not an empty
opening; a decorative title does not replace a requested identifier or code.
For flowing frames, open mechanical forms, printed diagrams or compact labels,
read [purpose and construction](references/construction-decisions.md) before
choosing geometry. Use its original orbit base when an annular construction fits.
'''
    text=text.replace("mathematical constructions, not stored artwork or recovered reference paths.\n","mathematical constructions, not stored artwork or recovered reference paths.\n"+insertion)
    skill.write_text(text,encoding="utf-8",newline="\n")
    (candidate / "references/construction-decisions.md").write_text(GUIDE,encoding="utf-8",newline="\n")
    script=candidate / "scripts/scaffold.py";text=script.read_text(encoding="utf-8")
    text=text.replace('("blank", "radial",','("blank", "orbit", "radial",',1)
    text=text.replace('"blank": {},','"blank": {},\n        "orbit": {"count": 5, "inner_ratio": .64, "coverage": 1.35, "taper": 1.1, "rotation": -90, "direction": 1},',1)
    text=text.replace('def radial(group, p, box, weight):',ORBIT+'def radial(group, p, box, weight):',1)
    text=text.replace('DRAW = {"radial": radial,','DRAW = {"orbit": orbit, "radial": radial,',1)
    script.write_text(text,encoding="utf-8",newline="\n")
    test=candidate / "scripts/test_scaffold.py";text=test.read_text(encoding="utf-8")
    text=text.replace('class ScaffoldTests(unittest.TestCase):\n','class ScaffoldTests(unittest.TestCase):\n'+TESTS,1)
    test.write_text(text,encoding="utf-8",newline="\n")
    guide=candidate / "references/scaffold-recipes.md"
    with guide.open("a",encoding="utf-8") as handle:
        handle.write('''\n## Orbit: tapered bands with a reserved opening\n\nUse `orbit` for an annular frame, not a central emblem. Parameters: `count`\n(3–24), `inner_ratio` (.2–.9), `coverage` (.25–1.8 times the angular spacing),\n`taper` (.5–3), `rotation` in degrees and `direction` (1 or -1). Each closed\nband uses an original polar construction; the declared inner disk stays empty.\nThe radius drifts sinusoidally and the width rises from and returns to zero.\nNo stored path or artwork is used. Inspect overlaps after changing coverage: a\nprotected center does not guarantee resolved junctions or a finished ornament.\nKeep the recipe for proportion edits; edit original vector paths for local\nfinishing, and do not regenerate over those direct edits.\n''')
    subprocess.run([sys.executable,str(REALIZER),"seal",str(path)],check=True)
    subprocess.run([sys.executable,str(REALIZER),"verify",str(path)],check=True)
    shutil.copytree(ROOT / "sealed-d/candidate/skills/svg-brief-design",ROOT / "inputs/d/svg-brief-design")
    print(json.dumps({"candidate":"d","parent":"preserved baseline","new_original_generator":"orbit","private_gate":"closed"}))


if __name__=="__main__": main()
