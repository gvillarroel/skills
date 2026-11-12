#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["pydantic==2.13.5"]
# ///
"""Compare unchanged NVIDIA model classes under source-order and semantic changes."""

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


REPO = Path(sys.argv[1]).resolve()
REVISION = "fc43a82600e18b19d159c52023f54f5572f537ac"
actual_revision = subprocess.run(
    ["git", "-C", str(REPO), "rev-parse", "HEAD"],
    capture_output=True, text=True, check=True,
).stdout.strip()
if actual_revision != REVISION:
    raise ValueError(f"Expected NVIDIA/auto-ontology revision {REVISION}")
sys.path.insert(0, str(REPO))

from auto_ontology.server.model_interchange.schemas import AutoOntologyModelDocument, ModelTerm


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def raw(document):
    return encode(document.model_dump(mode="json"))


def sort_every_list(value):
    if isinstance(value, dict):
        return {key: sort_every_list(item) for key, item in value.items()}
    if isinstance(value, list):
        return sorted((sort_every_list(item) for item in value), key=encode)
    return value


UNORDERED = {
    ("data_layer", "databases"),
    ("data_layer", "databases", "*", "schemas"),
    ("data_layer", "databases", "*", "schemas", "*", "tables"),
    ("data_layer", "foreign_keys"),
    ("data_layer", "joins"),
    ("semantic_layer", "terms"),
    ("semantic_layer", "terms", "*", "represents"),
    ("semantic_layer", "terms", "*", "columns_attributes"),
    ("semantic_layer", "semantic_fks"),
    ("semantic_layer", "sql_attributes", "manual"),
    ("semantic_layer", "sql_attributes", "table"),
    ("semantic_layer", "sql_attributes", "sql"),
    ("semantic_layer", "sql_attributes", "bridge_table"),
    ("semantic_layer", "custom_analyses"),
}


def typed_normalize(value, path=()):
    if isinstance(value, dict):
        return {key: typed_normalize(item, (*path, key)) for key, item in value.items()}
    if isinstance(value, list):
        rows = [typed_normalize(item, (*path, "*")) for item in value]
        return sorted(rows, key=encode) if path in UNORDERED else rows
    return value


def fixture():
    return {
        "data_layer": {
            "databases": [{
                "id": "db", "dialect": "postgres", "schemas": [{
                    "id": "schema", "name": "public", "database_name": "catalog",
                    "tables": [{
                        "id": "products", "name": "products", "pk": ["tenant", "id"],
                        "columns": [{"id": "product-id", "name": "id", "type": "integer"},
                                    {"id": "product-tenant", "name": "tenant", "type": "integer"}],
                    }, {
                        "id": "features", "name": "features",
                        "columns": [{"id": "feature-product", "name": "product_id", "type": "integer"},
                                    {"id": "feature-id", "name": "id", "type": "integer"}],
                    }],
                }],
            }],
            "foreign_keys": [
                {"source_column_id": "feature-product", "target_column_id": "product-id"},
                {"source_column_id": "feature-id", "target_column_id": "product-id"},
            ],
            "joins": [
                {"source_table_id": "features", "target_table_id": "products",
                 "join_columns": [{"source": "product_id", "target": "id"}]},
                {"source_table_id": "products", "target_table_id": "features",
                 "join_columns": [{"source": "id", "target": "product_id"}]},
            ],
        },
        "semantic_layer": {
            "terms": [
                {"id": "product", "name": "Product", "description": "A product.",
                 "represents": ["products"],
                 "columns_attributes": [{"id": "product-key", "name": "Product ID", "column_id": "product-id"}]},
                {"id": "feature", "name": "Feature", "description": "A capability.",
                 "represents": ["features"],
                 "columns_attributes": [{"id": "feature-key", "name": "Feature ID", "column_id": "feature-id"}]},
            ],
            "semantic_fks": [
                {"column_attribute_id": "feature-key", "column_id": "product-id", "use_in_join_paths": True},
                {"column_attribute_id": "product-key", "column_id": "feature-product", "use_in_join_paths": True},
            ],
        },
    }


def versions():
    base = fixture()
    variants = []
    for name, path in (
        ("foreign-key-order", ["data_layer", "foreign_keys"]),
        ("join-order", ["data_layer", "joins"]),
        ("term-order", ["semantic_layer", "terms"]),
        ("semantic-fk-order", ["semantic_layer", "semantic_fks"]),
        ("table-order", ["data_layer", "databases", 0, "schemas", 0, "tables"]),
    ):
        changed = deepcopy(base)
        target = changed
        for key in path:
            target = target[key]
        target.reverse()
        variants.append((name, changed, True))
    repeated = deepcopy(base)
    repeated["data_layer"]["foreign_keys"].append(deepcopy(repeated["data_layer"]["foreign_keys"][0]))
    variants.append(("duplicate-source-record", repeated, False))
    changed = deepcopy(base)
    changed["semantic_layer"]["terms"][0]["description"] = "A licensed product."
    variants.append(("definition-change", changed, False))
    changed = deepcopy(base)
    edge = changed["data_layer"]["foreign_keys"][0]
    edge["source_column_id"], edge["target_column_id"] = edge["target_column_id"], edge["source_column_id"]
    variants.append(("relationship-reversal", changed, False))
    changed = deepcopy(base)
    changed["semantic_layer"]["semantic_fks"][0]["use_in_join_paths"] = False
    variants.append(("relationship-disabled", changed, False))
    changed = deepcopy(base)
    changed["data_layer"]["foreign_keys"].pop()
    variants.append(("relationship-removed", changed, False))
    changed = deepcopy(base)
    changed["data_layer"]["databases"][0]["schemas"][0]["tables"][0]["pk"].reverse()
    variants.append(("composite-key-order", changed, False))
    changed = deepcopy(base)
    changed["data_layer"]["databases"][0]["schemas"][0]["tables"][0]["columns"][0]["type"] = "text"
    variants.append(("column-type", changed, False))
    changed = deepcopy(base)
    changed["semantic_layer"]["terms"][0]["id"] = "new-identity"
    variants.append(("term-identity", changed, False))
    changed = deepcopy(base)
    changed["semantic_layer"]["terms"][1]["name"] = "Product"
    variants.append(("homonymous-term", changed, False))
    return base, variants


def main():
    base, variants = versions()
    document = AutoOntologyModelDocument.model_validate(base)
    baseline = document.model_dump(mode="json")
    strategies = {
        "raw-json": lambda value: encode(value),
        "sort-all-lists": lambda value: encode(sort_every_list(value)),
        "schema-aware-order": lambda value: encode(typed_normalize(value)),
    }
    comparisons = {}
    for label, normalize in strategies.items():
        before = normalize(baseline)
        cases = {}
        for name, proposed, expected_equal in variants:
            observed = AutoOntologyModelDocument.model_validate(proposed).model_dump(mode="json")
            equal = before == normalize(observed)
            cases[name] = {"expected_equal": expected_equal, "observed_equal": equal, "correct": equal == expected_equal}
        comparisons[label] = {"passed": sum(row["correct"] for row in cases.values()), "total": len(cases), "cases": cases}
    term = ModelTerm.model_validate({
        "id": "glossary-entry", "name": "Feature", "description": "A capability.",
        "synonyms": ["Capability"], "name_certified": True, "description_certified": True,
    })
    node_path = REPO / "auto_ontology" / "catalog" / "model" / "node.py"
    spec = importlib.util.spec_from_file_location("nvidia_node_probe", node_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    node = module.CatalogNode
    report = {
        "revision": REVISION,
        "comparisons": comparisons,
        "term_export_fields": sorted(ModelTerm.model_fields),
        "term_roundtrip": term.model_dump(mode="json"),
        "fresh_node_ids_equal": node("Feature", "Term", {}).get_id() == node("Feature", "Term", {}).get_id(),
        "supplied_node_ids_equal": node("Feature", "Term", {}, existing_id="source:feature").get_id()
                                  == node("Feature", "Term", {}, existing_id="source:feature").get_id(),
        "module_sha256": {
            str(path.relative_to(REPO)).replace("\\", "/"): sha256(path.read_bytes()).hexdigest()
            for path in [node_path, REPO / "auto_ontology" / "server" / "model_interchange" / "schemas.py"]
        },
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    output = Path(sys.argv[2])
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text + "\n")
    print(encode({
        "comparisons": {name: {"passed": row["passed"], "total": row["total"]} for name, row in comparisons.items()},
        "synonyms_preserved": "synonyms" in report["term_roundtrip"],
        "certification_preserved": "name_certified" in report["term_roundtrip"],
        "fresh_node_ids_equal": report["fresh_node_ids_equal"],
        "supplied_node_ids_equal": report["supplied_node_ids_equal"],
    }))


if __name__ == "__main__":
    main()
