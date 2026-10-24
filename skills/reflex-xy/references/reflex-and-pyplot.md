# Reflex integration and pyplot migration

Use for Reflex embedding or Matplotlib migration. Examples target `xy==0.0.8`. Keep the dependency lock; check signatures and the tagged compatibility matrix before changing releases.

## Contents

- [Configure Reflex](#configure-reflex)
- [Choose the data lifetime](#choose-the-data-lifetime)
- [Fixed chart](#fixed-chart)
- [State-driven columns](#state-driven-columns)
- [Fixed data with live events](#fixed-data-with-live-events)
- [Migrate pyplot](#migrate-pyplot)
- [Verify the chosen path](#verify-the-chosen-path)
- [Release sources](#release-sources)

## Configure Reflex

Install the integration through the **xy** distribution:

```bash
uv add "xy[reflex]==0.0.8"
```

The import is `reflex_xy`; do not install a separate `reflex-xy` package. The extra declares `reflex>=0.9.6`; also pin resolved Reflex. Register the plugin once, preserving existing configuration and plugins:

```python
# rxconfig.py
import reflex as rx
import reflex_xy as rxy

config = rx.Config(
    app_name="dashboard",
    plugins=[rxy.XYPlugin()],
)
```

Use a package matching `app_name`, such as `dashboard/dashboard.py`. The plugin connects XY to the application's existing Socket.IO server.

## Choose the data lifetime

| Source | Use when | Behavior |
| --- | --- | --- |
| Concrete columns or a direct `xy.Chart` | Data is fixed and browser-local interactions are enough | Compiles to local client and binary payload assets; works with `reflex export`; no Python event dispatch |
| `@rxy.data` state method | Session state changes columns while the chart structure stays fixed | Compiles structure in the page; transports columns as binary buffers over the Reflex connection |
| `rxy.inline(chart)` at module scope | Fixed data needs backend callbacks or live readout | Registers the same content-addressed handle in each worker; requires backend; shared chart across viewers |
| `@rxy.figure` state method | State changes the chart structure itself | Advanced live handle; inspect its release signature and return annotation before use |

Keep viewer-specific data in state methods. Inline figures share kernel drill state across viewers. Avoid development-tier `rxy.register()` for durable apps: it cannot rebuild itself after worker restart.

## Fixed chart

Save this complete page as `dashboard/dashboard.py` after adding the configuration above:

```python
import reflex as rx
import reflex_xy as rxy
import xy

signups = xy.line_chart(
    xy.line([1, 2, 3, 4, 5], [120, 180, 165, 240, 310], name="Signups"),
    xy.x_axis(label="Week"),
    xy.y_axis(label="Signups"),
    title="Weekly signups",
)


def index() -> rx.Component:
    return rx.card(rxy.chart(signups, height="320px"), width="100%")


app = rx.App()
app.add_page(index)
```

Flat factories also accept concrete columns: `rxy.line_chart(data={"x": [1, 2], "y": [3, 5]}, x="x", y="y", height="320px")`. Core XY dimensions use pixel integers or percentages; outer Reflex dimensions accept CSS lengths. Give responsive parents an explicit height.

## State-driven columns

Use this as an alternative complete `dashboard/dashboard.py`:

```python
from typing import TypedDict

import numpy as np
import reflex as rx
import reflex_xy as rxy


class CloudData(TypedDict):
    x: np.ndarray
    y: np.ndarray
    magnitude: np.ndarray


class Dashboard(rx.State):
    points: int = 2_000

    @rxy.data
    def cloud(self) -> CloudData:
        rng = np.random.default_rng(7)
        x = rng.normal(size=self.points)
        y = 0.6 * x + rng.normal(scale=0.6, size=self.points)
        return {"x": x, "y": y, "magnitude": np.hypot(x, y)}

    @rx.event
    def add_points(self):
        self.points += 1_000


def index() -> rx.Component:
    return rx.vstack(
        rx.button("Add 1,000 points", on_click=Dashboard.add_points),
        rxy.scatter_chart(
            data=Dashboard.cloud,
            x="x", y="y", color="magnitude", colormap="viridis",
            density=True, height="420px",
        ),
        width="100%",
    )


app = rx.App()
app.add_page(index)
```

`TypedDict` enables compile-time column-name checks. Arrays travel through the decorated method; Reflex state holds a small typed handle. For multiple marks use data-free nodes: `rxy.chart(xy.scatter("x", "y"), xy.line("x", "magnitude"), data=Dashboard.cloud, height="420px")`. Sort lines first. Async methods and temporary `None` results are supported; check their return annotations.

## Fixed data with live events

For a fixed chart that must call Python, replace the static page with:

```python
import reflex as rx
import reflex_xy as rxy
import xy

cloud = xy.scatter_chart(
    xy.scatter([0, 1, 2], [2, 4, 3], size=9),
    xy.interaction_config(click=True, select=True),
)
cloud_token = rxy.inline(cloud)  # Module scope: every worker registers it.


class Events(rx.State):
    clicked: str = "Click a point"
    selected: int = 0

    @rx.event
    def point(self, event: rxy.PointClickEvent):
        data = event.get("data") or {}
        self.clicked = f"x={data.get('x')}, y={data.get('y')}"

    @rx.event
    def selection(self, event: rxy.SelectEndEvent):
        selection = event.get("selection") or {}
        self.selected = int(selection.get("total_count") or 0)


def index() -> rx.Component:
    return rx.vstack(
        rxy.chart(
            cloud_token, on_point_click=Events.point,
            on_select_end=Events.selection, height="320px",
        ),
        rx.text(Events.clicked),
        rx.text("Selected: ", Events.selected),
        width="100%",
    )


app = rx.App()
app.add_page(index)
```

Attach Reflex handlers to the outer factory: `on_point_hover`, `on_point_click`, `on_select_end`, or `on_view_change`. Core notebook callbacks such as `on_hover`, `on_click`, `on_select`, and `on_brush` do not become Reflex events. There is no Reflex `on_brush` prop.

Point events contain `data` (canonical x/y), `datum` (extra channels), and `canonical_row_id`. Selection events contain `selection.total_count`, `cleared`, `rows`, `canonical_row_ids`, and `truncated`. For complete rows beyond the bounded projection, call `rxy.resolve_selection(event)` server-side. Notebook `on_select` receives an `xy.Selection` instead. Streaming uses `rxy.append(handle, x=[...], y=[...])` on registered line/scatter traces; align channel tails and keep line x increasing. Exported HTML remains a snapshot.

## Migrate pyplot

Use `xy.pyplot` for familiar scientific scripts; prefer declarative XY for new applications:

```python
import numpy as np
import xy.pyplot as plt

x = np.linspace(0, 10, 200)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), "r--", label="Signal")
ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.legend()
fig.savefig("signal.png")
plt.close(fig)
```

In notebooks, `plt.show()` uses XY's host, without a desktop GUI. Matplotlib is not a runtime dependency. Coverage does not imply pixel parity or a complete Artist graph. Resolve errors and warnings and inspect the target output.

3D, geographic, ternary/custom projections, GUI backends, Matplotlib animation, and arbitrary Artist/transform/clipping graphs are unsupported. Polar uses `plt.subplots(subplot_kw={"projection": "polar"})`, `plt.subplot`, `plt.axes`, or `fig.add_subplot`; `plt.subplots(polar=True)` is invalid. Polar `fill` approximates an area against radius zero. Angular navigation, selection, facets, animation, and Cartesian LOD are deferred. Use axes methods; do not assume `plt.polar()`, `plt.thetagrids()`, or `plt.rgrids()` exist.

## Verify the chosen path

Run `uv run reflex run` from the app root and inspect the browser. Also run `reflex export` for static delivery. Test live clicks/selections and state recomputation. Constructors do not prove frontend compilation or event delivery. Inspect pyplot output at the requested dimensions and report which checks ran.

## Release sources

Verified 2026-10-24 against release `v0.0.8`, commit `6483032a7947e1f44ced1a560ac08f1025637529`. Prefer these tagged sources over installation prose that still discusses older uploads:

- [Dependency metadata](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/pyproject.toml)
- [Reflex guide](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/docs/integrations/reflex.md)
- [Handle and inline contracts](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/python/reflex_xy/__init__.py)
- [Exact event envelope fields](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/python/reflex_xy/events.py)
- [Pyplot guide](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/docs/integrations/matplotlib.md) and [compatibility matrix](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/spec/matplotlib/compat-matrix.md)
