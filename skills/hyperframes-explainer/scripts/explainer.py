#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Run: uv run --script scripts/explainer.py <preflight|build|patch|verify-media> --help."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
ARITY = {"add": (2, 32), "sub": (2, 2), "mul": (2, 32), "div": (2, 2),
         "min": (2, 32), "max": (2, 32), "pow": (2, 2), "clamp": (3, 3),
         "abs": (1, 1), "sqrt": (1, 1), "sin": (1, 1), "cos": (1, 1), "mod": (2, 2), "integrate": (2, 2)}
ATTRS = {"circle": {"cx", "cy", "r"}, "rect": {"x", "y", "width", "height", "rx"},
         "ellipse": {"cx", "cy", "rx", "ry"},
         "line": {"x1", "y1", "x2", "y2"}, "path": {"translateX", "translateY", "rotation"},
         "text": {"x", "y", "fontSize"}, "plot": {"x", "y", "width", "height"}}
REQUIRED = {kind: keys - {"fontSize", "translateX", "translateY", "rotation"} - ({"rx"} if kind == "rect" else set()) for kind, keys in ATTRS.items()}
SAFE_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def normalize_brief(brief):
    """Accept a common text-attribute spelling while preserving canonical output."""
    if not isinstance(brief, dict): return brief
    result = copy.deepcopy(brief)
    for mark in result.get("marks", []):
        attrs = mark.get("attrs", {})
        if mark.get("kind") == "text" and "anchor" in attrs and "anchor" not in mark and attrs["anchor"] in ["start", "middle", "end"]:
            mark["anchor"] = attrs.pop("anchor")
    return result


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def integral(brief, name, seconds, overrides):
    if name in overrides:
        return overrides[name] * seconds
    total, cursor, value = 0.0, 0.0, brief["sources"][name]["value"]
    for event in sorted(brief["events"], key=lambda e: e["at"]):
        if name not in event["changes"]:
            continue
        if seconds <= event["at"]:
            break
        total += value * (event["at"] - cursor)
        target, span = event["changes"][name], event["duration"]
        if span:
            elapsed = min(seconds - event["at"], span)
            total += value * elapsed + (target - value) * elapsed ** 2 / (2 * span)
            if seconds < event["at"] + span:
                return total
        value, cursor = target, event["at"] + span
    return total + value * (seconds - cursor)


def evaluate(brief, seconds, overrides=None):
    overrides = overrides or {}
    seconds = max(0, min(brief["output"]["duration"], seconds))
    state, visiting = {"time": seconds}, set()
    for name, source in brief["sources"].items():
        value = source["value"]
        for event in sorted(brief["events"], key=lambda e: e["at"]):
            if name not in event["changes"] or seconds < event["at"]:
                continue
            fraction = min(1, (seconds - event["at"]) / event["duration"]) if event["duration"] else 1
            value += (event["changes"][name] - value) * fraction
            if fraction < 1:
                break
        state[name] = overrides.get(name, value)

    def expr(x):
        if number(x):
            return x
        if isinstance(x, str):
            if x not in state:
                if x in visiting:
                    raise ValueError(f"Cyclic derived quantity: {x}")
                visiting.add(x)
                state[x] = expr(brief["derived"][x]["expr"])
                visiting.remove(x)
            return state[x]
        op, args = next(iter(x.items()))
        if op == "integrate":
            value = integral(brief, args[0], expr(args[1]), overrides)
        else:
            a = [expr(item) for item in args]
            operations = {"add": lambda: sum(a), "sub": lambda: a[0] - a[1],
                          "mul": lambda: math.prod(a), "div": lambda: a[0] / a[1],
                          "min": lambda: min(a), "max": lambda: max(a), "pow": lambda: a[0] ** a[1],
                          "clamp": lambda: max(a[1], min(a[2], a[0])), "abs": lambda: abs(a[0]),
                          "sqrt": lambda: math.sqrt(a[0]), "sin": lambda: math.sin(a[0]), "cos": lambda: math.cos(a[0]),
                          "mod": lambda: a[0] % a[1] if a[1] > 0 else float("nan")}
            value = operations[op]()
        if not number(value):
            raise ValueError(f"Non-finite {op} result at {seconds} s")
        return value

    for name in brief.get("derived", {}):
        expr(name)
    return state, expr


def samples(brief):
    duration = brief["output"]["duration"]
    times = {0, duration, duration / 2}
    times.update(duration * i / 40 for i in range(41))
    for event in brief["events"]:
        times.update([event["at"], event["at"] + event["duration"] / 2, event["at"] + event["duration"]])
    return sorted(times)


def preflight(brief, base=Path.cwd()):
    brief = normalize_brief(brief)
    errors, bindings = [], {}
    def fail(code, message):
        errors.append({"code": code, "message": message})
    if not isinstance(brief, dict):
        return {"ok": False, "findings": [{"code": "shape", "message": "Brief must be a JSON object."}]}
    if brief.get("schemaVersion") != 1 or not SAFE_ID.fullmatch(str(brief.get("id", ""))) or len(brief.get("id", "")) > 64:
        fail("identity", "Use schemaVersion 1 and a lowercase hyphen-case scene ID, at most 64 characters.")
    for key in ["claim", "evidence"]:
        if not isinstance(brief.get(key), str) or not brief[key].strip():
            fail("meaning", f"Provide {key} outside the film.")
    if not re.fullmatch(r"[a-zA-Z]+(?:-[a-zA-Z0-9]+)*", str(brief.get("language", "en"))):
        fail("language", "Use a language tag such as en, es or en-US.")
    output = brief.get("output", {})
    for key in ["width", "height", "fps"]:
        val = output.get(key)
        if not isinstance(val, int) or isinstance(val, bool) or val < 1 or (key != "fps" and val % 2):
            fail("output", f"{key} must be positive; canvas dimensions must be even integers for yuv420p.")
    if not number(output.get("duration")) or output["duration"] <= 0:
        fail("output", "Duration must be finite and positive.")
    elif number(output.get("fps")) and abs(output["duration"] * output["fps"] - round(output["duration"] * output["fps"])) > 1e-6:
        fail("output", "Duration multiplied by fps must be an integer frame count.")
    if output.get("audio") and not (base / output["audio"]).is_file():
        fail("audio", "The requested local audio file is missing.")
    palettes = json.loads((BUNDLE / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    selection = brief.get("palette", {"mode": "colorset1"})
    mode = selection.get("mode", "colorset1")
    palette = palettes.get(mode)
    if not palette:
        fail("palette", "Palette mode must be colorset1 or colorset2.")
    if mode == "colorset2" and (selection.get("decision") not in ["explicit", "semantic-capacity"] or not selection.get("reason", "").strip()):
        fail("palette", "colorset2 requires an explicit request or a concrete semantic-capacity reason.")
    sources, derived = brief.get("sources", {}), brief.get("derived", {})
    if not isinstance(sources, dict) or not sources:
        fail("sources", "Declare at least one numerical causal source."); sources = {}
    if not isinstance(derived, dict):
        fail("derived", "Derived quantities must be a keyed object."); derived = {}
    names = set(sources) | set(derived) | {"time"}
    if "time" in sources or "time" in derived or set(sources) & set(derived):
        fail("quantity", "time is reserved; source and derived names must be unique.")
    for name, source in sources.items():
        domain = source.get("domain", [])
        if len(domain) != 2 or not all(number(v) for v in domain) or domain[0] >= domain[1] or not number(source.get("value")) or not domain[0] <= source["value"] <= domain[1]:
            fail("domain", f"Source {name} needs a finite value within an increasing two-value domain.")
        if not isinstance(source.get("unit"), str):
            fail("unit", f"Source {name} needs a unit string; use an empty string for a dimensionless quantity.")
    for name, quantity in derived.items():
        if not isinstance(quantity.get("unit"), str):
            fail("unit", f"Derived quantity {name} needs a unit string.")

    def deps(expression, trail=()):
        if number(expression):
            return set()
        if isinstance(expression, str):
            if expression not in names:
                fail("expression", f"Unknown quantity: {expression}"); return set()
            if expression in sources or expression == "time":
                return {expression}
            if expression in trail:
                fail("cycle", f"Cyclic quantity: {' -> '.join((*trail, expression))}"); return set()
            return deps(derived[expression].get("expr"), (*trail, expression))
        if not isinstance(expression, dict) or len(expression) != 1:
            fail("expression", f"Invalid expression: {expression!r}"); return set()
        op, args = next(iter(expression.items()))
        if op not in ARITY or not isinstance(args, list) or not ARITY[op][0] <= len(args) <= ARITY[op][1]:
            fail("expression", f"Invalid operation or arity: {op}"); return set()
        if op == "integrate" and (not isinstance(args[0], str) or args[0] not in sources):
            fail("integrate", "Integrate a declared source rate, not a derived quantity."); return set()
        return set().union(*(deps(arg, trail) for arg in args))

    for name, quantity in derived.items():
        deps(quantity.get("expr"), (name,))
    events = brief.get("events", [])
    if not isinstance(events, list) or not events:
        fail("events", "Provide a meaningful source event, not unrelated timed decorations."); events = []
    occupied, ids = {}, set()
    for event in events:
        if not isinstance(event.get("id"), str) or event["id"] in ids:
            fail("event", "Event IDs must be unique strings.")
        ids.add(event.get("id"))
        at, span = event.get("at"), event.get("duration")
        if not number(at) or not number(span) or at < 0 or span < 0 or (number(output.get("duration")) and at + span > output["duration"]):
            fail("event", "Event windows must fit inside the output duration."); continue
        if not isinstance(event.get("cause"), str) or not event["cause"].strip():
            fail("event", "State the event cause in the manifest.")
        changes = event.get("changes", {})
        if not changes:
            fail("event", "An event must change a declared source.")
        for name, value in changes.items():
            if name not in sources or not number(value):
                fail("event", f"Invalid event source: {name}"); continue
            domain = sources[name].get("domain", [])
            if len(domain) == 2 and all(number(v) for v in domain) and not domain[0] <= value <= domain[1]:
                fail("domain", f"Event value for {name} is outside its legal domain.")
            occupied.setdefault(name, []).append((at, at + span))
    for name, windows in occupied.items():
        windows.sort()
        for left, right in zip(windows, windows[1:]):
            if right[0] < left[1] or right[0] == left[0]:
                fail("event-overlap", f"Overlapping writes to {name} would make its causal history ambiguous.")
    views = brief.get("views", [])
    regions = {}
    if sum(v.get("importance") == "main" for v in views) != 1:
        fail("layout", "Choose exactly one main mechanism.")
    for view in views:
        region, name = view.get("region", []), view.get("id")
        if not name or name in regions or not view.get("question"):
            fail("view", "Each view needs a unique ID and a distinct explanatory question.")
        if len(region) != 4 or not all(number(v) for v in region) or min(region[2:]) <= 0:
            fail("layout", f"Invalid region: {name}"); continue
        x, y, w, h = region
        if x < 0 or y < 0 or x + w > output.get("width", 0) or y + h > output.get("height", 0):
            fail("layout", f"View {name} is outside the output canvas.")
        full_canvas = [0, 0, output.get("width"), output.get("height")]
        for other, (ox, oy, ow, oh) in regions.items():
            shared_canvas = list(region) == full_canvas and [ox, oy, ow, oh] == full_canvas
            if not shared_canvas and x < ox + ow and ox < x + w and y < oy + oh and oy < y + h:
                fail("layout", f"Views {name} and {other} overlap.")
        regions[name] = region
    marks, ids, context_count, used_paints = brief.get("marks", []), set(), 0, set()
    for mark in marks:
        mid, kind = mark.get("id"), mark.get("kind")
        if not mid or mid in ids or mark.get("view") not in regions or kind not in ATTRS:
            fail("mark", f"Invalid mark identity, kind or view: {mid}"); continue
        ids.add(mid)
        attrs = mark.get("attrs", {})
        if not REQUIRED[kind] <= set(attrs) or set(attrs) - ATTRS[kind]:
            fail("geometry", f"Invalid or missing geometry for {mid}: {sorted(set(attrs))}")
        dependencies = set().union(*(deps(v) for v in attrs.values())) if attrs else set()
        if "value" in mark:
            dependencies |= deps(mark["value"])
        if kind == "plot":
            dependencies |= deps(mark.get("xValue")) | deps(mark.get("yValue"))
            for key in ["xDomain", "yDomain"]:
                domain = mark.get(key, [])
                if len(domain) != 2 or not all(number(v) for v in domain) or domain[0] >= domain[1]:
                    fail("plot", f"Plot {mid} needs increasing fixed {key}.")
            if not isinstance(mark.get("samples", 100), int) or not 2 <= mark.get("samples", 100) <= 500:
                fail("plot", "Plot samples must be an integer from 2 to 500.")
        if kind == "text":
            label = str(mark.get("text", ""))
            if "\ufffd" in label or re.search(r"(?:\u00c2[\u0080-\u00bf]|\u00c3[\u0080-\u00bf]|\u00e2[\u0080-\u00bf]{2})", label):
                fail("text-encoding", f"{mid} contains replacement characters or probable mojibake. Rewrite its source as UTF-8; use plain ASCII unit separators when useful.")
            words = str(mark.get("text", "")).split()
            if len(words) > 9 or len(str(mark.get("text", ""))) > 90:
                fail("text", f"{mid} is prose; replace it with a direct label or put the explanation outside the film.")
            context_count += mark.get("textRole") == "context"
            if mark.get("anchor", "start") not in ["start", "middle", "end"]:
                fail("text", f"Invalid text anchor: {mid}")
            if not isinstance(mark.get("digits", 1), int) or not 0 <= mark.get("digits", 1) <= 6:
                fail("text", "Display precision must be between zero and six digits.")
        if kind == "path" and (not isinstance(mark.get("d"), str) or not re.fullmatch(r"[MmLlHhVvCcSsQqTtAaZz0-9eE.,+\s-]+", mark.get("d", ""))):
            fail("path", f"{mid} needs literal path geometry, not markup or code.")
        if not number(mark.get("opacity", 1)) or not 0 < mark.get("opacity", 1) <= 1:
            fail("visibility", "Explanation marks must have a visible, positive opacity.")
        entity_role = (brief.get("entities", {})).get(mark.get("entity"))
        for role in [mark.get("fill"), mark.get("stroke"), entity_role]:
            if role is not None and role != "none":
                if not palette or role not in palette["roles"]:
                    fail("paint", f"Unknown palette role: {role}")
        actual_fill = entity_role if entity_role and kind not in ["text", "line", "path", "plot"] else mark.get("fill")
        actual_stroke = entity_role if entity_role and kind in ["line", "path", "plot"] else mark.get("stroke")
        for role in [actual_fill, actual_stroke]:
            if palette and role in palette["roles"]:
                used_paints.add(palette["roles"][role])
        if not number(mark.get("strokeWidth", 3)) or mark.get("strokeWidth", 3) < 0:
            fail("paint", f"{mid} needs a finite, nonnegative stroke width; bind geometry, not arbitrary attribute objects.")
        if mark.get("entity") and mark["entity"] not in brief.get("entities", {}):
            fail("entity", f"Unregistered entity: {mark['entity']}")
        if mark.get("fill", "none") == "none" and mark.get("stroke", "none") == "none" and not mark.get("entity"):
            fail("visibility", f"{mid} has no visible paint.")
        bindings[mid] = {"view": mark["view"], "dependencies": sorted(dependencies)}
    if context_count > 1:
        fail("text", "Use at most one context label on the filmed stage.")
    for source in sources:
        if not any(source in item["dependencies"] for item in bindings.values()):
            fail("unbound-source", f"{source} has no visible explanation.")
    event_views = {}
    for event in events:
        affected = {item["view"] for item in bindings.values() if set(event.get("changes", {})) & set(item["dependencies"])}
        event_views[event.get("id", "invalid")] = sorted(affected)
    if not any(len(v) >= 2 for v in event_views.values()):
        fail("synchronization", "At least one causal event must affect two distinct representations.")
    if mode == "colorset2" and not used_paints - set(palettes["colorset1"]["allowed"]):
        fail("palette", "The scene fits colorset1; colorset2 needs an actual semantic use of its additional colors.")
    checks = []
    if not errors:
        states = [(t, {}) for t in samples(brief)]
        states += [(t, {name: bound}) for name, source in sources.items() for bound in source["domain"] for t in [0, output["duration"] / 2, output["duration"]]]
        try:
            for t, override in states:
                state, expr = evaluate(brief, t, override)
                for invariant in brief.get("invariants", []):
                    if abs(expr(invariant["lhs"]) - expr(invariant["rhs"])) > invariant.get("tolerance", 1e-8):
                        fail("invariant", f"{invariant['id']} fails at {t} s with {override}.")
                for mark in marks:
                    attrs = {k: expr(v) for k, v in mark.get("attrs", {}).items()}
                    if any(attrs.get(k, 0) < 0 for k in ["r", "rx", "ry", "width", "height"]):
                        fail("geometry", f"{mark['id']} has negative size at {t} s.")
                    if "value" in mark:
                        expr(mark["value"])
                    if mark["kind"] == "plot":
                        for key in ["x", "y"]:
                            val, domain = expr(mark[f"{key}Value"]), mark[f"{key}Domain"]
                            if not domain[0] - 1e-8 <= val <= domain[1] + 1e-8:
                                fail("plot-domain", f"{mark['id']} {key} value {val} leaves its fixed domain at {t} s; do not clamp away evidence.")
                checks.append({"time": t, "overrides": override, "state": state})
        except (ValueError, KeyError, ZeroDivisionError, OverflowError, TypeError) as error:
            fail("model", str(error))
    return {"ok": not errors, "schemaVersion": 1, "findings": errors, "palette": mode,
            "bindings": bindings, "eventViews": event_views, "oracle": checks}


def build(brief_path, project, refresh=False):
    brief_path, project = Path(brief_path).resolve(), Path(project).resolve()
    brief = normalize_brief(json.loads(brief_path.read_text(encoding="utf-8-sig")))
    report = preflight(brief, brief_path.parent)
    if not report["ok"]:
        return report
    if project.is_relative_to(BUNDLE):
        raise ValueError("The skill is read-only; choose a project outside the bundle.")
    if (project / "manifest.json").exists() or (project / "index.html").exists():
        if not refresh:
            return {"ok": False, "findings": [{"code": "project-exists", "message": "An authored project already exists. Choose a fresh project or explicitly --refresh this builder's project with the same scene ID after updating its owned brief/assets."}]}
        manifest_path = project / "manifest.json"
        prior = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        if prior.get("generatedBy") != "hyperframes-explainer-v1" or prior.get("id") != brief["id"]:
            raise ValueError("Refresh is only allowed for this builder's project with the same scene ID.")
    assets = copy.deepcopy(brief.get("assetProvenance", []))
    for asset in assets:
        source = Path(asset["source"])
        if hashlib.sha256(source.read_bytes()).hexdigest() != asset["sha256"]:
            return {"ok": False, "findings": [{"code": "asset-source-changed", "message": "An imported SVG changed after assembly. Reimport from the original unexpanded brief, inspect import.json ok:true, then build (use --refresh for this builder's existing project)."}]}
    templates = BUNDLE / "assets/templates"
    project.mkdir(parents=True, exist_ok=True)
    for folder in ["vendor", "fonts"]:
        shutil.copytree(BUNDLE / "assets" / folder, project / "assets" / folder, dirs_exist_ok=True)
    scripts = project / "scripts"; scripts.mkdir(exist_ok=True)
    for name in ["hf.ts", "local-runtime.ts", "audit.ts", "arrow-quality.js"]:
        shutil.copy2(templates / name, scripts / name)
    shutil.copy2(templates / "kernel.js", project / "kernel.js")
    palettes = json.loads((BUNDLE / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    palette = palettes[report["palette"]]
    for asset in assets:
        source = Path(asset["source"])
        target = project / "assets" / "source" / (asset["id"] + ".svg")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        asset["projectSource"] = "assets/source/" + asset["id"] + ".svg"
    audio = ""
    if brief["output"].get("audio"):
        source = brief_path.parent / brief["output"]["audio"]
        dest = project / "assets" / ("audio" + source.suffix.lower())
        shutil.copy2(source, dest)
        audio = f'<audio id="soundtrack" src="assets/{dest.name}" data-start="0" data-duration="{brief["output"]["duration"]}" data-track-index="1"></audio>'
        brief["output"]["audio"] = f"assets/{dest.name}"
    def embedded(value):
        return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    substitutions = {"ID": brief["id"], "LANG": brief.get("language", "en"), "WIDTH": brief["output"]["width"],
                     "HEIGHT": brief["output"]["height"], "FPS": brief["output"]["fps"], "DURATION": brief["output"]["duration"],
                     "BACKGROUND": palette["roles"]["background"], "ARIA": html.escape(brief["claim"], quote=True),
                     "AUDIO": audio, "BRIEF": embedded(brief), "PALETTE": embedded(palette)}
    for name in ["index.html", "preview.html"]:
        content = (templates / name).read_text(encoding="utf-8")
        for key, val in substitutions.items():
            content = content.replace(f"__{key}__", str(val))
        (project / name).write_text(content, encoding="utf-8")
    write_json(project / "brief.json", brief)
    write_json(project / "oracle.json", report)
    write_json(project / "manifest.json", {"schemaVersion": 1, "generatedBy": "hyperframes-explainer-v1", "id": brief["id"], "claim": brief["claim"], "evidence": brief["evidence"],
               "palette": brief.get("palette", {"mode": "colorset1"}), "output": brief["output"], "events": brief["events"],
               "bindings": report["bindings"], "assets": assets, "versions": {"hyperframes": "0.8.111", "gsap": "3.14.2"}})
    write_json(project / "package.json", {"name": brief["id"], "private": True, "type": "module",
               "scripts": {"check": "node scripts/hf.ts check", "preview": "node scripts/hf.ts preview --no-open",
                           "audit": "node scripts/audit.ts --report audit.json --screenshot preview.png"},
               "dependencies": {"hyperframes": "0.8.111", "puppeteer-core": "25.12.0"}})
    (project / ".npmrc").write_text("cache=./.cache/npm\naudit=false\nfund=false\n", encoding="utf-8")
    (project / ".gitignore").write_text("node_modules/\n.cache/\n*.mp4\n*.png\n*.jpg\n", encoding="utf-8")
    return {"ok": True, "project": str(project), "palette": report["palette"], "findings": [],
            "outputs": ["index.html", "preview.html", "brief.json", "manifest.json", "oracle.json", "package.json"],
            "next": "Install project dependencies with npm install --prefix <project> --cache <project>/.cache/npm --no-audit --no-fund before invoking the browser audit or native HyperFrames commands. Then inspect their reports."}


def initialize_brief(brief_path, *, width=1920, height=1080, fps=30, duration=16,
                     initial=2, maximum=5, target=4, at=4, ramp=2,
                     source="rate", source_unit="L/s", quantity="volume", quantity_unit="L",
                     palette="colorset1"):
    """Seed an illustrative nonnegative rate/integral model; leave the mechanism to its asset producer."""
    brief_path = Path(brief_path).resolve()
    def rejected(message):
        return {"ok": False, "created": False, "findings": [{"code": "init", "message": message}]}
    if brief_path.is_relative_to(BUNDLE): return rejected("The skill is read-only. Initialize a project-owned brief.")
    if brief_path.exists(): return rejected("Brief already exists. Preserve it and use parsed edits or the patch command.")
    if not all(number(n) for n in [width, height, fps, duration, initial, maximum, target, at, ramp]):
        return rejected("Initializer parameters must be finite numbers.")
    if width < 720 or height < 400 or width < height or fps <= 0 or duration <= 0:
        return rejected("This layout needs a landscape canvas of at least 720 by 400, positive fps and duration. Author a custom scene for other layouts.")
    if maximum <= 0 or min(initial, target, at, ramp) < 0 or max(initial, target) > maximum or at + ramp > duration:
        return rejected("Use a nonnegative input domain, initial/target within its maximum and an event inside the duration.")
    if source == quantity or "time" in [source, quantity] or not all(SAFE_ID.fullmatch(n) for n in [source, quantity]):
        return rejected("Source and quantity need distinct lowercase hyphen-case names other than time.")
    if palette not in ["colorset1", "colorset2"]: return rejected("Choose colorset1 or an explicitly requested colorset2.")
    main = [width*.05, height*.10, width*.60, height*.82]
    support = [width*.71, height*.11, width*.25, height*.78]
    font = max(16, min(32, height/30)); small = max(14, font*.85)
    x, y, pw, ph = 35, 45, support[2]-55, support[3]-115
    maximum_quantity = maximum * duration
    quantity_paint = "secondary" if palette == "colorset2" else "primary"
    label = lambda identity, view, px, py, text, **extra: {
        "id": identity, "view": view, "kind": "text",
        "attrs": {"x": px, "y": py, "fontSize": extra.pop("fontSize", font)},
        "text": text, "fill": "ink", **extra}
    marks = [label("input-value", "mechanism", 16, 30, source.replace("-", " "), value=source, digits=1, unit=source_unit),
             label("accumulated-value", "mechanism", 16, main[3]-12, quantity.replace("-", " "), value=quantity, digits=1, unit=quantity_unit),
             {"id": "history-axis", "view": "history", "kind": "path", "d": f"M{x} {y} V{y+ph} H{x+pw}",
              "attrs": {}, "fill": "none", "stroke": "line", "strokeWidth": 2},
             {"id": "history-curve", "view": "history", "kind": "plot", "attrs": {"x": x, "y": y, "width": pw, "height": ph},
              "xValue": "time", "yValue": quantity, "xDomain": [0, duration], "yDomain": [0, maximum_quantity],
              "samples": 96, "fill": "none", "stroke": quantity_paint, "strokeWidth": max(3,height/270), "entity": quantity},
             label("history-unit", "history", x, 22, f"{quantity.replace('-', ' ')} ({quantity_unit})"),
             label("history-top", "history", x-10, y+5, f"{maximum_quantity:g}", anchor="end", fontSize=small),
             label("history-bottom", "history", x-10, y+ph+5, "0", anchor="end", fontSize=small),
             label("history-start", "history", x, y+ph+28, "0 s", fontSize=small),
             label("history-end", "history", x+pw, y+ph+28, f"{duration:g} s", anchor="end", fontSize=small)]
    brief = {"schemaVersion": 1, "id": "controlled-accumulation",
             "claim": f"Changing {source} changes the mechanism and the accumulation rate of {quantity}.",
             "evidence": "Illustrative imposed nonnegative input, accumulation from zero, no losses or output. Replace these assumptions when the subject requires another model.",
             "output": {"width": width, "height": height, "fps": fps, "duration": duration},
             "palette": {"mode": palette, "decision": "explicit" if palette == "colorset2" else "default",
                         "reason": "Explicit second-palette request separates input in red and accumulated quantity in blue." if palette == "colorset2" else "One controlled quantity can use red and neutral structure."},
             "sources": {source: {"value": initial, "domain": [0,maximum], "unit": source_unit}},
             "derived": {quantity: {"expr": {"integrate": [source,"time"]}, "unit": quantity_unit}},
             "events": [{"id": "change-input", "at": at, "duration": ramp, "changes": {source:target},
                         "cause": f"The controlled {source} changes."}],
             "entities": {quantity:quantity_paint},
             "views": [{"id": "mechanism", "question": f"What does {source} change in the actual mechanism?", "region": main, "importance": "main"},
                       {"id": "history", "question": f"How does the input change the history of {quantity}?", "region": support, "importance": "support"}],
             "marks": marks, "invariants": [{"id": "accumulation", "lhs": quantity, "rhs": {"integrate": [source,"time"]}, "tolerance": 1e-9}]}
    report = preflight(brief,brief_path.parent)
    report.update(created=report["ok"], output=str(brief_path), maximumQuantity=maximum_quantity,
                  next="Create the view-sized SVG scaffold, author the selected recognizable mechanism and bind its changing parts. This numerical layout alone is not a finished explanation.")
    if report["ok"]: write_json(brief_path,brief)
    return report


def patch_brief(brief_path, patch_path):
    brief_path, patch_path = Path(brief_path).resolve(), Path(patch_path).resolve()
    def rejected(message):
        return {"ok": False, "applied": False, "findings": [{"code": "patch", "message": message}]}
    if brief_path.is_relative_to(BUNDLE):
        return rejected("The skill is read-only. Patch a project-owned copy of the brief.")
    brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
    patch = json.loads(patch_path.read_text(encoding="utf-8-sig"))
    if not isinstance(patch, dict) or set(patch) - {"marks", "views", "events", "sources", "derived", "output", "palette", "claim", "evidence", "language"}:
        return rejected("Patch only declared scene groups, output, palette, claim, evidence or language.")
    def merge(old, new):
        if isinstance(old, dict) and isinstance(new, dict) and not set(new) & set(ARITY):
            result = copy.deepcopy(old)
            for key, value in new.items(): result[key] = merge(result.get(key), value)
            return result
        return copy.deepcopy(new)
    updated = copy.deepcopy(brief)
    for group, changes in patch.items():
        if group in ["marks", "views", "events"]:
            if not isinstance(changes, dict): return rejected(f"{group} updates must be keyed by existing ID.")
            indexed = {item["id"]: item for item in updated.get(group, [])}
            for identity, values in changes.items():
                if identity not in indexed or not isinstance(values, dict) or values.get("id", identity) != identity:
                    return rejected(f"Unknown or renamed {group} ID: {identity}")
                item = indexed[identity]; replacement = merge(item, values); item.clear(); item.update(replacement)
        elif group in ["sources", "derived"]:
            if not isinstance(changes, dict) or set(changes) - set(updated.get(group, {})):
                return rejected(f"Patch existing {group} names; write a new brief to add or remove quantities.")
            updated[group] = merge(updated[group], changes)
        else: updated[group] = merge(updated.get(group), changes)
    report = preflight(updated, brief_path.parent)
    report["applied"] = report["ok"]
    if report["ok"]: write_json(brief_path, updated)
    return report


def verify_media(video, brief, contact_sheet=None):
    video = Path(video).resolve(); duration = brief["output"]["duration"]
    result = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(video)], capture_output=True, text=True, check=True)
    info = json.loads(result.stdout); stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    rate = stream["avg_frame_rate"].split("/"); fps = int(rate[0]) / int(rate[1])
    findings = []
    for key in ["width", "height"]:
        if stream[key] != brief["output"][key]: findings.append(f"Wrong {key}: {stream[key]}")
    if abs(fps - brief["output"]["fps"]) > 1e-6: findings.append(f"Wrong fps: {fps}")
    frames = int(stream["nb_read_frames"])
    if frames != round(duration * fps): findings.append(f"Wrong frame count: {frames}")
    actual_duration = float(stream.get("duration", info["format"]["duration"]))
    if abs(actual_duration - duration) > 1 / fps + 1e-4: findings.append(f"Wrong duration: {actual_duration}")
    if stream["codec_name"] != "h264" or stream.get("pix_fmt") != "yuv420p": findings.append("Expected H264/yuv420p delivery.")
    audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if bool(audio) != bool(brief["output"].get("audio")): findings.append("Audio presence differs from the requested brief.")
    if audio and audio[0]["codec_name"] != "aac": findings.append("Expected AAC audio.")
    decoded = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"], capture_output=True, text=True)
    if decoded.returncode or decoded.stderr.strip(): findings.append("Full media decode reported errors: " + decoded.stderr[-2000:])
    from PIL import Image, ImageChops, ImageDraw, ImageStat
    times = sorted({0, duration * .2, duration * .4, duration * .6, duration * .8, max(0, duration - 1/fps)} |
                   {e["at"] + e["duration"] / 2 for e in brief["events"]})
    images, motion = [], []
    from io import BytesIO
    for t in times:
        data = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1", "-vf", "scale=640:-1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
        image = Image.open(BytesIO(data)).convert("RGB")
        if images: motion.append({"from": times[len(images)-1], "to": t, "meanAbsoluteDifference": sum(ImageStat.Stat(ImageChops.difference(images[-1], image)).mean) / 3})
        images.append(image)
    if not any(item["meanAbsoluteDifference"] > .05 for item in motion): findings.append("Sampled movie appears frozen; inspect the causal event.")
    if contact_sheet:
        cols, cellw, cellh = 3, images[0].width, images[0].height + 28
        sheet = Image.new("RGB", (cols * cellw, math.ceil(len(images) / cols) * cellh), "#f7f7f7")
        draw = ImageDraw.Draw(sheet)
        for i, (t, image) in enumerate(zip(times, images)):
            x, y = (i % cols) * cellw, (i // cols) * cellh
            sheet.paste(image, (x, y)); draw.text((x+12, y+image.height+6), f"{t:.2f} s", fill="#333e48")
        target = Path(contact_sheet); target.parent.mkdir(parents=True, exist_ok=True); sheet.save(target)
    return {"ok": not findings, "findings": findings, "video": str(video), "width": stream["width"], "height": stream["height"],
            "fps": fps, "frames": frames, "duration": actual_duration, "codec": stream["codec_name"], "pixelFormat": stream["pix_fmt"],
            "audio": bool(audio), "bytes": video.stat().st_size, "sha256": hashlib.sha256(video.read_bytes()).hexdigest(), "motion": motion}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["init", "preflight", "build", "patch", "verify-media"]:
        cmd = sub.add_parser(name); cmd.add_argument("--brief", required=True); cmd.add_argument("--report", required=True)
        if name == "init":
            for key,default in [("width",1920),("height",1080),("fps",30)]:
                cmd.add_argument(f"--{key}",type=int,default=default)
            for key, default in [("duration",16),("initial",2),("maximum",5),("target",4),("at",4),("ramp",2)]:
                cmd.add_argument(f"--{key}",type=float,default=default)
            for key,default in [("source","rate"),("source-unit","L/s"),("quantity","volume"),("quantity-unit","L")]:
                cmd.add_argument(f"--{key}",default=default)
            cmd.add_argument("--palette",choices=["colorset1","colorset2"],default="colorset1")
        if name == "build": cmd.add_argument("--project", required=True); cmd.add_argument("--refresh", action="store_true")
        if name == "patch": cmd.add_argument("--patch", required=True)
        if name == "verify-media": cmd.add_argument("--video", required=True); cmd.add_argument("--contact-sheet")
    args = parser.parse_args()
    try:
        brief_path = Path(args.brief).resolve()
        if args.command == "init":
            keys = ["width","height","fps","duration","initial","maximum","target","at","ramp","source","source_unit","quantity","quantity_unit","palette"]
            report = initialize_brief(brief_path,**{key:getattr(args,key) for key in keys})
            write_json(args.report,report)
            print(json.dumps({"ok":report["ok"],"report":str(Path(args.report).resolve()),"findings":len(report["findings"])}))
            return 0
        brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
        if args.command == "preflight": report = preflight(brief, brief_path.parent)
        elif args.command == "build": report = build(brief_path, args.project, args.refresh)
        elif args.command == "patch": report = patch_brief(brief_path, args.patch)
        else: report = verify_media(args.video, brief, args.contact_sheet)
        write_json(args.report, report)
        print(json.dumps({"ok": report["ok"], "report": str(Path(args.report).resolve()), "findings": len(report["findings"])}))
        return 0
    except json.JSONDecodeError as error:
        report = {"ok": False, "findings": [{"code": "json", "message": f"Invalid brief JSON at line {error.lineno}, column {error.colno}: {error.msg}"}]}
        write_json(args.report, report)
        print(json.dumps({"ok": False, "report": str(Path(args.report).resolve()), "findings": 1}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        write_json(args.report, {"ok": False, "findings": [{"code": "runtime", "message": str(error)}]})
        print(f"Runtime failure: {error}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
