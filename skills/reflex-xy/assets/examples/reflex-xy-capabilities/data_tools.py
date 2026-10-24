#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Exercise XY's low-level column store without pretending it is a chart demo.

Run: uv run --script data_tools.py --output-dir <artifact-directory>
Optional tables: uv run --with pandas --with pyarrow --script data_tools.py --with-dataframes --output-dir <artifact-directory>
Only xy and its core NumPy dependency are needed. The report distinguishes
executed data/registry operations, a configuration-only structural probe, and
reference-only types. The optional flag adds pandas/Arrow adapter checks and a
native SVG; neither mode needs a browser or notebook kernel.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

import numpy as np
import xy


def _dataframe_probe(output: Path) -> dict:
    """Test optional adapters with their real resolved versions and copy costs."""
    import pandas as pd
    import pyarrow as pa

    table = pd.DataFrame({"time": [1.0, 2.0, 3.0], "response": [2.0, 4.0, 3.0]})
    chart = xy.chart(
        xy.scatter("time", "response", data=table, color="#9e1b32", opacity=1, density=False),
        xy.x_axis(domain=(0, 4)), xy.y_axis(domain=(0, 5)),
        xy.legend(show=False), width=640, height=360,
    )
    svg = chart.to_svg(width=640, height=360)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg") and len(svg) > 1000
    memory = chart.memory_report()
    assert memory["canonical_bytes"] == 6 * 8
    (output / "pandas-named-columns.svg").write_text(svg, encoding="utf-8")

    store = xy.ColumnStore()
    null_free = pa.array([1.25, 2.5, 3.75], type=pa.float64())
    arrow_view = null_free.to_numpy(zero_copy_only=True)
    shared = store.ingest(null_free)
    assert np.shares_memory(shared.values, arrow_view)
    assert shared.ingest_copies == 0 and shared.zone.null_count == 0
    nullable = store.ingest(pa.array([1.25, None, 3.75], type=pa.float64()))
    assert np.array_equal(nullable.values, [1.25, np.nan, 3.75], equal_nan=True)
    assert nullable.zone.count == 2 and nullable.zone.null_count == 1
    assert nullable.ingest_copies >= 1
    chunks = pa.chunked_array([[1.0, 2.0], [3.0]], type=pa.float64())
    combined = store.ingest(chunks)
    assert np.array_equal(combined.values, [1.0, 2.0, 3.0])
    assert combined.ingest_copies >= 1
    return {
        "status": "passed", "versions": {"pandas": pd.__version__, "pyarrow": pa.__version__},
        "apis": ["xy.chart", "xy.scatter", "xy.Chart.to_svg", "xy.Chart.memory_report",
                 "xy.ColumnStore.ingest", "xy.ColumnStore.memory_report"],
        "pandas": {"named_columns": ["time", "response"], "rows": len(table),
                   "native_svg": "pandas-named-columns.svg", "memory": memory},
        "arrow": {"null_free_float64_shared": True, "null_free_ingest_copies": shared.ingest_copies,
                  "nullable_values": [1.25, None, 3.75], "nullable_ingest_copies": nullable.ingest_copies,
                  "multi_chunk_ingest_copies": combined.ingest_copies, "memory": store.memory_report()},
        "scope": "Zero-copy is asserted only for the tested null-free float64 Arrow array; null materialization and chunk combination report their actual copy costs.",
    }


def run(output_dir: Path, include_dataframes: bool = False) -> dict:
    """Write data-report.json and return real low-level API evidence."""
    if importlib.metadata.version("xy") != "0.0.8":
        raise RuntimeError("This acceptance utility requires xy==0.0.8")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    store = xy.ColumnStore()
    epoch = 1_700_000_000_000.0
    source = np.array([epoch, epoch + 0.25, epoch + 0.5, np.nan], dtype=np.float64)
    column = store.ingest(source, defer_zone_maps=True)
    assert isinstance(column, xy.Column)
    assert len(store) == 1 and len(column) == 4
    assert column.kind == "float" and column.values.dtype == np.float64
    assert np.shares_memory(column.values, source)
    assert store.ingest(source) is column and len(store) == 1
    first_offset = column.suggest_offset()
    assert first_offset == epoch + 0.25
    assert column.zone.count == 3 and column.zone.null_count == 1

    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 8.0])
    x_column, y_column = store.ingest_pair(x, y)
    assert len(store) == 3 and len(x_column) == len(y_column) == 3
    assert store.ingest(x) is x_column
    assert x_column.min == 1 and x_column.max == 3
    assert y_column.min == 2 and y_column.max == 8
    before = store.memory_report()
    assert before["canonical_bytes"] == (4 + 3 + 3) * 8
    assert before["canonical_capacity_bytes"] == before["canonical_bytes"]
    assert before["canonical_mapped_bytes"] == 0

    checkpoint = store.checkpoint()
    speculative = store.ingest(np.array([99.0, 100.0]))
    assert len(store) == 4 and speculative.id == 3
    store.rollback(checkpoint)
    after_rollback = store.memory_report()
    assert len(store) == 3 and after_rollback == before
    assert store.ingest_pair(x, y) == (x_column, y_column)

    # Rollback restores the store registry, not existing column contents. Append
    # is deliberately after rollback, so that distinction is not misrepresented.
    column.append(np.array([epoch + 0.75, epoch + 1.0]))
    assert len(column) == 6 and len(source) == 4
    assert np.array_equal(column.values[:4], source, equal_nan=True)
    assert column.zone.count == 5 and column.zone.null_count == 1
    assert column.min == epoch and column.max == epoch + 1
    after = store.memory_report()
    assert after["canonical_bytes"] == before["canonical_bytes"] + 16
    assert after["canonical_capacity_bytes"] >= after["canonical_bytes"]
    assert after["columns"][0]["capacity_bytes"] == column.capacity_bytes
    next_offset = column.suggest_offset()
    assert next_offset == first_offset  # The documented sticky offset remains valid.

    with xy.structural_probe():
        export_policy = xy.export_config(
            formats=["png", "svg", "html"], filename="atlas-data",
            width=640, height=360, scale=1.5,
        )
        empty_chart = xy.chart(
            xy.scatter([], [], color="#9e1b32", opacity=1, density=False),
            xy.x_axis(domain=(0, 1)), xy.y_axis(domain=(0, 1)),
            export_policy,
        )
        structural_memory = empty_chart.memory_report()
        assert structural_memory["canonical_bytes"] == 0
        assert tuple(export_policy.formats) == ("png", "svg", "html")
        assert export_policy.filename == "atlas-data" and export_policy.width == 640
        assert export_policy.height == 360 and export_policy.scale == 1.5

    initial_registry = xy.registered_marks()
    temporary_name = "atlas_data_probe_" + uuid.uuid4().hex
    plugin = xy.MarkPlugin(temporary_name, build=lambda context: [])
    try:
        assert xy.register_mark(plugin) is plugin
        assert temporary_name in xy.registered_marks()
    finally:
        xy.unregister_mark(temporary_name)
    assert xy.registered_marks() == initial_registry

    result = {
        "schema_version": 1, "version": "0.0.8", "passed": True,
        "apis": ["xy.ColumnStore", "xy.ColumnStore.ingest", "xy.ColumnStore.ingest_pair",
                 "xy.ColumnStore.checkpoint", "xy.ColumnStore.rollback", "xy.ColumnStore.memory_report",
                 "xy.Column.append", "xy.Column.suggest_offset", "xy.structural_probe",
                 "xy.export_config",
                 "xy.MarkPlugin", "xy.register_mark", "xy.registered_marks", "xy.unregister_mark"],
        "observed_returned_types": ["xy.Column", "xy.ZoneMaps"],
        "reference_only_constructors": ["xy.ZoneMaps"],
        "ingest": {"shared_float64_storage": True, "identity_deduplication": True,
                   "paired_lengths": [len(x_column), len(y_column)], "missing_values_preserved": True},
        "memory": {"before_append": before, "after_speculative_rollback": after_rollback,
                   "after_append": after},
        "append": {"original_length": len(source), "current_length": len(column),
                   "current_values": [None if np.isnan(v) else float(v) for v in column.values],
                   "finite_count": column.zone.count, "null_count": column.zone.null_count,
                   "initial_offset": first_offset, "offset_after_append": next_offset},
        "structural_probe": {"constructed": True, "canonical_bytes": structural_memory["canonical_bytes"],
                             "rendered": False, "scope": "Empty-data configuration compilation only; no rendering or live-host claim."},
        "export_config": {"constructed_as_chart_child": True, "formats": export_policy.formats,
                          "filename": export_policy.filename, "width": export_policy.width,
                          "height": export_policy.height, "scale": export_policy.scale,
                          "files_exported_by_this_check": False,
                          "scope": "Public export-policy configuration was compiled; this is not a CSV write_image promise."},
        "registry": {"own_temporary_plugin_registered": True, "own_temporary_plugin_removed": True,
                     "initial_registry_restored": True, "plugin_build_invoked": False},
        "optional_dataframes": _dataframe_probe(output) if include_dataframes else {"status": "not_requested"},
        "boundaries": {
            "rollback": "Restores speculative column registrations; it does not undo prior mutation of an existing Column.",
            "zone_maps": "Observed through Column.zone; no direct ZoneMaps construction is needed for ordinary chart use.",
            "optional_tables": "Pandas and Arrow adapters were exercised with the recorded versions." if include_dataframes else "Pandas and Arrow adapters were not requested; install the optional packages and use --with-dataframes to exercise them.",
            "rendering": "The optional pandas case adds a native SVG. The core report validates data structures and configuration; neither mode establishes browser rendering, GPU performance, or callback delivery.",
        },
    }
    (output / "data-report.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--with-dataframes", action="store_true", help="Exercise installed pandas and PyArrow optional input adapters")
    args = parser.parse_args()
    if args.output_dir.resolve().is_relative_to(Path(__file__).resolve().parent):
        parser.error("Write generated artifacts outside this acceptance source directory")
    report = run(args.output_dir, include_dataframes=args.with_dataframes)
    print(json.dumps({"passed": report["passed"], "invoked_apis": report["apis"],
                      "report": str(args.output_dir.resolve() / "data-report.json")}))
