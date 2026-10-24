#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Run small real XY host probes and write an editable local Reflex application.

Keep xy_colorsets.py and colorsets.json beside this source. Example:
uv run --script host_examples.py --colorset colorset1 --output-dir host-output
uv run --with "xy[reflex]==0.0.8" --with "reflex==0.10.0" --script host_examples.py --output-dir host-live-output --with-reflex

The report distinguishes construction/compile evidence from live frontend
delivery. GitHub Pages can serve snapshots and source downloads; it cannot run
the Python kernel or Reflex backend required by callback and streaming demos.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import xy
import xy.pyplot as plt
import xy_colorsets

from xy_colorsets import categorical_colors, css, legend_style, theme


REFLEX_SOURCE = '''from typing import TypedDict
import os
import numpy as np
import reflex as rx
import reflex_xy as rxy
import xy
from xy_colorsets import categorical_colors, legend_style, theme

PALETTE = os.environ.get("XY_CAP_PALETTE", "colorset1")
COLORS = categorical_colors(PALETTE, 3)

def fixed_chart():
    return xy.chart(xy.scatter([0.,1.,2.,3.], [2.,4.,3.,5.], color=COLORS[0], size=8, opacity=1, density=False),
                    xy.line([0.,1.,2.,3.], [2.,4.,3.,5.], color=COLORS[1], width=3),
                    xy.x_axis(label="Sample"), xy.y_axis(label="Reading"),
                    xy.legend(show=False), xy.interaction_config(click=True,select=True),
                    theme(PALETTE), title="Fixed source", width="100%", height=300)

STATIC = fixed_chart()
LIVE = rxy.inline(fixed_chart())

class CloudColumns(TypedDict):
    x: np.ndarray
    y: np.ndarray

class Dashboard(rx.State):
    points: int = 8
    next_x: int = 4
    message: str = "Click a live point"
    selected_count: int = 0

    @rxy.data
    def cloud(self) -> CloudColumns:
        x = np.arange(self.points, dtype=float)
        return {"x": x, "y": 3 + np.sqrt(x + 1)}

    @rxy.figure(probe="figure")
    def dynamic(self) -> xy.Chart:
        x = np.arange(self.points, dtype=float)
        marks = [xy.scatter(x, 2 + x * .8, color=COLORS[0], size=8, opacity=1, density=False)]
        if self.points > 8:
            marks.append(xy.hline(6, color=COLORS[1]))
        return xy.chart(*marks, xy.legend(show=False), theme(PALETTE),
                        xy.x_axis(label="Sample"), xy.y_axis(label="Reading"),
                        title="State-dependent structure", width="100%", height=300)

    @rx.event
    def add_points(self):
        self.points += 2

    @rx.event
    def stream(self):
        rxy.append(LIVE, x=[float(self.next_x)], y=[float(self.next_x % 4 + 2)])
        rxy.append(LIVE, x=[float(self.next_x)], y=[float(self.next_x % 4 + 2)], trace=1)
        self.next_x += 1

    @rx.event
    def clicked(self, event: rxy.PointClickEvent):
        point = event.get("data") or {}
        self.message = f"Canonical row {event.get('canonical_row_id')}: x={point.get('x')}, y={point.get('y')}"

    @rx.event
    def selected(self, event: rxy.SelectEndEvent):
        selection = rxy.resolve_selection(event)
        self.selected_count = len(selection) if selection is not None else 0

    @rx.event
    def hovered(self, event: rxy.PointHoverEvent):
        self.message = f"Hover canonical row {event.get('canonical_row_id')}"

    @rx.event
    def viewed(self, event: rxy.ViewChangeEvent):
        if event.get("phase") == "final":
            self.message = f"Final view: {event.get('x_domain')}"

def index() -> rx.Component:
    return rx.vstack(
        rx.heading("XY host boundaries"),
        rx.text("Static payload: browser interactions only; no Python event dispatch."),
        rxy.chart(STATIC, height="300px", width="100%"),
        rx.text("Inline handle: shared fixed data with live canonical events and append."),
        rxy.chart(LIVE, on_point_click=Dashboard.clicked, on_point_hover=Dashboard.hovered,
                  on_select_end=Dashboard.selected, on_view_change=Dashboard.viewed,
                  height="300px", width="100%"),
        rx.button("Append one point", on_click=Dashboard.stream, background=COLORS[0], color="#ffffff"),
        rx.text(Dashboard.message), rx.text("Selected rows: ", Dashboard.selected_count),
        rx.text("State data: column arrays change while the chart structure stays fixed."),
        rxy.chart(xy.scatter("x", "y", color=COLORS[0], size=8, opacity=1, density=False),
                  xy.legend(show=False), theme(PALETTE), data=Dashboard.cloud,
                  height="300px", width="100%"),
        rx.text("State figure: adding observations also adds a reference mark."),
        rxy.chart(figure=Dashboard.dynamic, height="300px", width="100%"),
        rx.button("Add two state observations", on_click=Dashboard.add_points, background=COLORS[0], color="#ffffff"),
        width="100%", max_width="1000px", padding="24px", spacing="4", background="#f7f7f7", color="#000000",
    )

app = rx.App()
app.add_page(index)
'''


def run(output_dir: Path, include_reflex: bool = False, *, palette: str = "colorset1") -> dict:
    """Execute the core host examples; optionally compile the local Reflex app.

    Always write report.json and portable source. The default requires only xy;
    include_reflex=True requires the documented optional extra in this process.
    """
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    colors = categorical_colors(palette, 3)
    callback_log = []
    chart = xy.chart(
        xy.scatter([0., 1., 2., 3.], [2., 4., 3., 5.], color=colors[0], size=8, opacity=1, density=False),
        xy.line([0., 1., 2., 3.], [2., 4., 3., 5.], color=colors[1], width=3),
        xy.x_axis(label="Sample"), xy.y_axis(label="Reading"), xy.legend(show=False),
        xy.interaction_config(hover=True, click=True, select=True, brush=True),
        theme(palette), title="Notebook and streaming source", width=820, height=460,
        on_hover=lambda event: callback_log.append(("hover", event)),
        on_click=lambda event: callback_log.append(("click", event)),
        on_brush=lambda event: callback_log.append(("brush", event)),
        on_select=lambda selection: callback_log.append(("select", len(selection))),
        on_view_change=lambda event: callback_log.append(("view", event)),
    )
    before_memory = chart.memory_report()
    picked = chart.pick(0, 2)
    selection = chart.select_range(0.5, 2.5, 0, 10, trace_id=0)
    selection_report = {"count": len(selection), "indices": selection.index.tolist(),
                        "rows": selection.rows(), "xy": [values.tolist() for values in selection.xy(0)]}
    chart.to_html(output / "before-append.html", custom_css=css(palette))
    chart.append(0, [4., 5.], [4., 6.])
    chart.append(1, [4., 5.], [4., 6.])
    after_memory = chart.memory_report()
    chart.to_html(output / "after-append.html", custom_css=css(palette))
    widget = chart.widget()
    chart.set_view({"x": [1., 4.], "y": [1., 7.]}, animate=False, history=True)
    chart.select(range={"x0": 1., "x1": 3., "y0": 1., "y1": 7.})
    chart.select(polygon=[[0., 1.], [3., 1.], [3., 6.], [0., 6.]])
    chart.select(rows={0: [1, 2]})
    chart.clear_selection()
    chart.reset_view(axes=["x", "y"])
    state = chart.view_state()
    notebook_html = chart.show(display="html")
    notebook_widget = chart.show(display="widget")
    exports = []
    for extension in ("png", "jpeg", "webp", "svg", "pdf", "html"):
        path = output / f"native-export.{extension}"
        if extension == "html":
            chart.write_image(path, custom_css=css(palette))
        else:
            chart.write_image(path, width=820, height=460, scale=1)
        exports.append({"format": extension, "path": path.name, "bytes": path.stat().st_size})
    xy.write_images(figures=[chart, chart], files=[str(output / "batch.png"), str(output / "batch.svg")])

    x = np.linspace(0, 6, 31)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(x, np.sin(x), color=colors[0], label="Signal")
    axes[0].set(xlabel="Time", ylabel="Amplitude", title="Pyplot migration")
    axes[0].legend(frameon=False)
    axes[1].scatter(x, np.cos(x), color=colors[1])
    axes[1].set(xlabel="Time", ylabel="Response", title="Paired axes")
    fig.suptitle("XY pyplot without Matplotlib")
    fig.tight_layout()
    fig.savefig(output / "pyplot-migration.svg")
    plt.close(fig)
    widget.close()

    app_root = output / "reflex-example"
    package = app_root / "xyhost"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "xyhost.py").write_text(REFLEX_SOURCE, encoding="utf-8")
    (app_root / "rxconfig.py").write_text(
        'import reflex as rx\nimport reflex_xy as rxy\nconfig = rx.Config(app_name="xyhost", plugins=[rxy.XYPlugin()])\n', encoding="utf-8")
    (app_root / "pyproject.toml").write_text(
        '[project]\nname = "xy-capability-host"\nversion = "0.0.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["xy[reflex]==0.0.8", "reflex==0.10.0"]\n\n[tool.uv]\npackage = false\n', encoding="utf-8")
    palette_module = Path(xy_colorsets.__file__).resolve()
    palette_file = palette_module.with_name("colorsets.json")
    if not palette_file.is_file():
        palette_file = palette_module.parent.parent / "assets" / "palettes" / "colorsets.json"
    for filename, resource in (("xy_colorsets.py", palette_module), ("colorsets.json", palette_file)):
        shutil.copy2(resource, app_root / filename)
    reflex_available = importlib.util.find_spec("reflex") is not None
    reflex_result = {"requested": include_reflex, "available": reflex_available,
                     "status": "not_requested", "app_root": str(app_root), "executed": False,
                     "run_command": "uv run reflex run",
                     "frontend_callback_delivery_tested": False}
    if include_reflex and reflex_available:
        operation = "from xyhost.xyhost import app, index; print(type(index()).__name__)"
        operation += "; app._compile(dry_run=True); print('Compiler dry run passed')"
        environment = dict(os.environ, XY_CAP_PALETTE=palette)
        process = subprocess.run([sys.executable, "-c", operation], cwd=app_root,
                                 env=environment, capture_output=True, text=True, timeout=180)
        reflex_result.update(executed=True, returncode=process.returncode,
                             status="compiled" if process.returncode == 0 else "compile_failed",
                             stdout=process.stdout, stderr=process.stderr)
    elif include_reflex:
        reflex_result.update(status="requires_optional_extra", message="Install xy[reflex]==0.0.8 and reflex==0.10.0 to compile this optional host.")
    versions = {}
    for name in ("xy", "numpy", "reflex", "anywidget"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    core_apis = ["xy.Chart.memory_report", "xy.Chart.pick", "xy.Chart.select_range", "xy.Selection.rows", "xy.Selection.xy", "xy.Chart.append", "xy.Chart.widget", "xy.Chart.set_view", "xy.Chart.select", "xy.Chart.clear_selection", "xy.Chart.reset_view", "xy.Chart.view_state", "xy.Chart.show", "xy.Chart.write_image", "xy.write_images", "xy.pyplot.subplots", "xy.pyplot.close"]
    reflex_compiled_apis = ["reflex_xy.inline", "reflex_xy.data", "reflex_xy.figure", "reflex_xy.chart", "reflex_xy.XYPlugin"]
    result = {
        "schema_version": 1, "palette": palette,
        "versions": versions,
        "core": {"picked": picked, "selection": selection_report,
                 "before_memory": before_memory, "after_memory": after_memory,
                 "widget_type": type(notebook_widget).__name__, "html_view_type": type(notebook_html).__name__,
                 "programmatic_commands": ["set_view", "select.range", "select.polygon", "select.rows", "clear_selection", "reset_view", "view_state"],
                 "view_state_without_mounted_frontend": state,
                 "live_frontend_acknowledgement_tested": False,
                 "callbacks_registered": ["on_hover", "on_click", "on_brush", "on_select", "on_view_change"],
                 "callbacks_delivered": len(callback_log)},
        "exports": exports, "reflex": reflex_result,
        "apis": core_apis + (reflex_compiled_apis if reflex_result["status"] == "compiled" else []),
        "runnable_reflex_source_apis": reflex_compiled_apis + ["reflex_xy.append", "reflex_xy.resolve_selection"],
        "artifacts": [item["path"] for item in exports] + ["before-append.html", "after-append.html", "batch.png", "batch.svg", "pyplot-migration.svg", "reflex-example/rxconfig.py", "reflex-example/pyproject.toml", "reflex-example/xyhost/xyhost.py", "reflex-example/xy_colorsets.py", "reflex-example/colorsets.json"],
        "host_boundaries": {
            "pages": "Standalone interactive snapshots; Python callback delivery and future append calls need a live host.",
            "notebook": "The widget and commands were constructed; actual callbacks require a running Jupyter kernel and mounted widget frontend.",
            "reflex_static": "Concrete charts compile to local client/data assets and do not dispatch Python events.",
            "reflex_inline": "Module-scope content-addressed handle is shared across viewers and needs the running backend.",
            "reflex_data": "State-dependent columns use binary transport; structure remains fixed.",
            "reflex_figure": "State can rebuild chart structure; synchronous probe='figure' validates the default figure at compile time.",
            "csv": "CSV is a client modebar download; write_image does not accept CSV.",
        },
    }
    result["passed"] = len(selection) == 2 and all(item["bytes"] > 0 for item in exports) and (not include_reflex or reflex_result["status"] == "compiled")
    (output / "report.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--with-reflex", action="store_true", help="Compile the generated local app; requires the optional Reflex extra.")
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    if output.is_relative_to(Path(__file__).resolve().parent):
        parser.error("Write generated files outside this source directory.")
    try:
        result = run(output, include_reflex=args.with_reflex, palette=args.colorset)
    except Exception as error:
        output.mkdir(parents=True, exist_ok=True)
        result = {"schema_version": 1, "passed": False, "palette": args.colorset,
                  "error": {"type": type(error).__name__, "message": str(error)}}
    (output / "report.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "exports": len(result.get("exports", [])), "reflex": args.with_reflex, "report": str(output / "report.json")}))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
