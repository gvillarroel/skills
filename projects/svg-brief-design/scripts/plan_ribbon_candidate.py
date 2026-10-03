#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Declare an original variable-width ribbon hypothesis from public evidence."""
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]

RIBBON = '''def ribbon(group, p, box, weight):
    """Offset an original cubic centerline by a smooth variable-width profile."""
    x, y, w, h = box
    width = bounded(p, "width", .18, .01, .5) * min(w, h)
    taper = bounded(p, "taper", 1.2, .5, 3)
    controls = p.get("controls", [[.15,.85],[.05,.15],[.8,.05],[.85,.6]])
    if (not isinstance(controls, list) or len(controls) != 4
            or any(not isinstance(point, list) or len(point) != 2 for point in controls)):
        raise ValueError("Ribbon controls require four normalized coordinate pairs")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
           or not 0 <= v <= 1 for point in controls for v in point):
        raise ValueError("Ribbon coordinates must be finite numbers from zero to one")
    pad = width / 2
    controls = [(x + pad + a * (w - 2 * pad), y + pad + b * (h - 2 * pad)) for a,b in controls]
    samples = 120
    centers = []
    for j in range(samples + 1):
        t = j / samples
        weights = [(1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3]
        centers.append(tuple(sum(weights[k]*controls[k][axis] for k in range(4)) for axis in range(2)))
    if max(math.dist(centers[0], q) for q in centers) < 1e-8:
        raise ValueError("Ribbon centerline must have nonzero extent")
    left, right = [], []
    for j, center in enumerate(centers):
        before, after = centers[max(0,j-1)], centers[min(samples,j+1)]
        dx, dy = after[0]-before[0], after[1]-before[1]
        length = math.hypot(dx,dy)
        if length < 1e-8:
            # Repeated controls can create a stationary endpoint. A neighboring
            # noncoincident sample supplies the limiting direction for a tip.
            neighbors = centers[j+1:] + list(reversed(centers[:j]))
            target = next(q for q in neighbors if math.dist(q,center) >= 1e-8)
            dx,dy = target[0]-center[0],target[1]-center[1]
            length = math.hypot(dx,dy)
        half = width / 2 * max(0,math.sin(math.pi*j/samples))**taper
        nx,ny = -dy/length,dx/length
        left.append((center[0]+nx*half,center[1]+ny*half))
        right.append((center[0]-nx*half,center[1]-ny*half))
    node(group,"path",id="ribbon-band",d=path_points(left+list(reversed(right)),close=True),
         fill="currentColor",stroke="none")


'''

GUIDE = '''# Construct a form and its openings together

Use this method for a silhouette, figurative motif, flowing ornament or open
mechanical body. Preserve every requested feature. Simplification should remove
redundancy while keeping the planes, joints and openings that identify the form.

Start with the dominant envelope and the major empty regions at the same time.
A long channel can establish a body axis; a widening opening can explain the
space between two planes. Let neighboring contours follow that opening. If the
result is a large slab with a few tiny holes, revise the proportions of the
openings before adding incisions. For an open body, some channels should remain
connected to the exterior rather than becoming a collection of enclosed dots.

Choose how each junction works: a clear gap, a smooth shared boundary, or an
intentional over-under crossing. A crossing accumulates ink unless you remove
the hidden part. Use a compound path with `fill-rule="evenodd"` for enclosed
transparent holes, or a self-contained mask for an underpass. For an opening
connected to the exterior, shape the separate adjacent masses instead of laying
one unbroken black polygon over them. White paint is not a transparent opening.

## Original curved bands

For a curved rail, rim or organic plane, use the `ribbon` base. It creates a
closed band around an original cubic centerline, with smoothly varying width:

```text
python <skill-root>/scripts/scaffold.py init ribbon --recipe band.json --output band.svg
```

Its four normalized `controls` are the start, two handles and end; `width`
controls the broadest section and `taper` controls its progression toward the
tips. Adjust these for the required contour, then build again. Use `composition`
for several bands in separate boxes. Inspect their junctions; the helper keeps
each band inside its box but does not prevent self-intersections from looping
controls or arrange a finished subject. For an annular frame, `orbit` reserves
the central disk; finish the local overlaps as designed joints, not knots.

For a diagram or label, apply the same separation principle to traces, arrows,
text and codes. Each requested feature needs its own readable space. Do not put
a second coordinate system beneath an existing one or let a code cover text.
Keep a printed diagram's main trace substantial and its annotations subordinate.

Render and open both the working view and an explicit small preview:

```text
python <skill-root>/scripts/render_svg.py artwork.svg --output preview.png
python <skill-root>/scripts/render_svg.py artwork.svg --output thumbnail.png --size 192
```

Inspect the black shape and the shapes of the main openings. If they merge into
an undifferentiated block, widen or reconnect an important gap. If they read as
unrelated fragments, align their contours and direction. Repair the largest
visible relationship, preserving required features, and render the final state.
'''

TESTS = '''    def test_ribbon_is_visible_bounded_and_tapered(self):
        recipe = scaffold.defaults("ribbon")
        for width,taper in [(.01,.5),(.18,1.2),(.5,3)]:
            recipe["parameters"].update(width=width,taper=taper)
            alpha = rgba(scaffold.build(recipe)).getchannel("A")
            box = alpha.getbbox()
            self.assertIsNotNone(box)
            self.assertTrue(27 <= box[0] < box[2] <= 453 and 27 <= box[1] < box[3] <= 453)
            self.assertLess(sum(v > 0 for v in alpha.getdata()),480*480*.5)
        recipe["parameters"]["controls"] = [[0,0],[0,0],[1,1],[1,1]]
        self.assertIsNotNone(rgba(scaffold.build(recipe)).getchannel("A").getbbox())

    def test_ribbon_rejects_collapsed_or_invalid_controls(self):
        for controls in [[[.5,.5]]*4,[[0,0],[1,1]],[[0,0],[0,1],[1,0],[2,1]],
                         [[0,0],[0,1],[1,0],[float("nan"),1]]]:
            recipe = scaffold.defaults("ribbon")
            recipe["parameters"]["controls"] = controls
            with self.assertRaises(ValueError): scaffold.build(recipe)

'''


def main():
    phase,arm = sys.argv[1:3]
    root = REPO / "evaluations/runs" / phase
    parent = root / "inputs/b/svg-brief-design"
    prior = REPO / "evaluations/runs/svt3"
    plan = {"operator":"coupled-openings-and-ribbons",
        "hypothesis":"Construct masses and openings jointly with deliberate junction types; provide an original cubic variable-width band scaffold and explicit small-preview inspection. Return to the installed parent without inheriting the failed, verbose helper-description intervention. Expected improvement is articulated figure-ground structure without random cuts or constant-width crossing knots. Risks are extra helper complexity, unsuitable template use and over-simplification. No source paths, artwork, task IDs, coordinates from references or evaluator prompts enter the bundle.",
        "development_evidence":["decision-c.json","decision-d.json"] if phase=="svt3" else [],"files":{}}
    # This inheritance is development-only and does not import any private gate.
    if "def ribbon(" in (parent / "scripts/scaffold.py").read_text():
        raise ValueError("The parent already has this mechanism; declare a new hypothesis")
    def edit(path,old,new):
        plan["files"].setdefault(path,[]).append({"replace":old,"with":new})
    edit("SKILL.md","## Construct the drawing\n",'''## Construct the drawing

For silhouettes, figurative motifs, flowing ornaments and open mechanical forms,
read [form and openings](references/figure-ground.md). Design the main openings
alongside the black masses; use its original variable-width ribbon base when a
curved band fits the subject. A simpler drawing must still articulate its body.
''')
    edit("scripts/scaffold.py",'("blank", "orbit",','("blank", "ribbon", "orbit",')
    edit("scripts/scaffold.py",'"blank": {},','"blank": {},\n        "ribbon": {"controls": [[.15,.85],[.05,.15],[.8,.05],[.85,.6]], "width": .18, "taper": 1.2},')
    edit("scripts/scaffold.py","def orbit(group, p, box, weight):",RIBBON+"def orbit(group, p, box, weight):")
    edit("scripts/scaffold.py",'DRAW = {"orbit": orbit,','DRAW = {"ribbon": ribbon, "orbit": orbit,')
    edit("scripts/test_scaffold.py","class ScaffoldTests(unittest.TestCase):\n","class ScaffoldTests(unittest.TestCase):\n"+TESTS)
    plan["files"]["references/figure-ground.md"]=[{"append":GUIDE}]
    plan["files"].setdefault("references/scaffold-recipes.md",[]).append({"append":'''\n## Ribbon: an original variable-width curved band\n\n`ribbon` uses four normalized `controls` (start, two handles, end), `width`\n(.01–.5 of the box's shorter side) and `taper` (.5–3). A cubic centerline and\nits local normal generate both boundaries; a sine profile closes the pointed\nends. The helper reserves padding for the maximum half-width. It fits the box\nbut cannot resolve crossings from looping controls or decide a composition.\nUse separate composition boxes for related rails or contour bands, then finish\ntheir joins. See [form and openings](figure-ground.md) for construction choices.\n'''})
    with (root / f"mutation-{arm}.json").open("x",encoding="utf-8") as handle:
        json.dump(plan,handle,indent=2)
    print(json.dumps({"phase":phase,"candidate":arm,"files":list(plan["files"]),"new_geometry":"original cubic ribbon"}))


if __name__=="__main__":main()
