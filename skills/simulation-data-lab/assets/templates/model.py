"""Executable model-adapter template for simulation-data-lab.

Copy this file into a fresh experiment bundle, then replace the model and
metadata with a mathematical representation of the user's mechanism. Never
launch the system being represented, call its APIs/tools, or collect live data.
Represent disturbances with declared distributions and dependencies, not real
failures injected into a target. The narrow ``simulate(run)``
interface lets the bundled runner stay independent of the chosen engine.
"""

from __future__ import annotations

import platform
import random
from typing import Any


MODEL_METADATA = {
    "modelId": "inventory-policy-model",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "random.Random-MT19937",
    "rngVersion": platform.python_version(),
    "reproducibility": "exact-within-locked-environment",
}


def simulate(run: dict[str, Any]) -> dict[str, Any]:
    """Simulate one independent period using the runner-assigned seed."""

    parameters = run["parameters"]
    rng = random.Random(run["seed"])
    demand = max(0.0, rng.gauss(parameters["demand_mean"], parameters["demand_sd"]))
    stock = float(parameters["stock_units"])
    fulfilled = min(stock, demand)
    unmet = max(0.0, demand - fulfilled)
    fill_rate = 1.0 if demand == 0 else fulfilled / demand
    return {
        "outcomes": {
            "fill_rate": fill_rate,
            "unmet_units": unmet,
        },
        "diagnostics": [
            {
                "check_id": "bounded-fill-rate",
                "status": "pass" if 0.0 <= fill_rate <= 1.0 else "fail",
                "value": fill_rate,
                "threshold": 1.0,
                "invalidates_hypotheses": not 0.0 <= fill_rate <= 1.0,
                "message": "Fill rate remains within its invariant range [0, 1].",
            }
        ],
    }
