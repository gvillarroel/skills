#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify a BigQuery pricing SQL artifact against a frozen semantic contract."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def score_sql(contract: dict[str, Any], sql: str | None) -> dict[str, Any]:
    checks: list[tuple[str, bool]] = []
    text = sql or ""
    checks.append(("artifact-present", bool(text.strip())))
    checks.append(("plain-sql", "```" not in text))
    checks.append(("balanced-backticks", text.count("`") % 2 == 0))
    checks.append(("single-statement-family", bool(re.search(r"(?is)\b(DECLARE|CREATE|WITH|SELECT)\b", text))))

    for item in contract.get("requiredAll", []):
        checks.append(
            (
                str(item["id"]),
                re.search(str(item["pattern"]), text, flags=re.IGNORECASE | re.DOTALL)
                is not None,
            )
        )
    for item in contract.get("requiredAny", []):
        patterns = [str(pattern) for pattern in item.get("patterns", [])]
        checks.append(
            (
                str(item["id"]),
                any(
                    re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
                    is not None
                    for pattern in patterns
                ),
            )
        )
    folded = text.casefold()
    for item in contract.get("requiredLiterals", []):
        checks.append((f"literal:{item}", str(item).casefold() in folded))
    for item in contract.get("forbidden", []):
        checks.append(
            (
                f"forbidden:{item['id']}",
                re.search(
                    str(item["pattern"]), text, flags=re.IGNORECASE | re.DOTALL
                )
                is None,
            )
        )

    failed = [identifier for identifier, passed in checks if not passed]
    passed = len(checks) - len(failed)
    reward = passed / len(checks) if checks else 0.0
    return {
        "ok": not failed,
        "reward": reward,
        "passedChecks": passed,
        "totalChecks": len(checks),
        "failedChecks": failed,
    }


def main() -> int:
    workspace = Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    verifier_dir = Path(
        os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")
    ).resolve()
    verifier_dir.mkdir(parents=True, exist_ok=True)
    try:
        contract = read_json(Path(__file__).with_name("contract.json"))
    except (OSError, json.JSONDecodeError, TypeError) as error:
        print(f"Verifier contract is unreadable: {type(error).__name__}", file=sys.stderr)
        return 2
    query_path = workspace / "query.sql"
    try:
        sql = query_path.read_text(encoding="utf-8")
    except OSError:
        sql = None
    result = score_sql(contract, sql)
    reward = {
        "reward": result["reward"],
        "semantic_contract": result["reward"],
        "format": 1.0
        if "artifact-present" not in result["failedChecks"]
        and "plain-sql" not in result["failedChecks"]
        else 0.0,
    }
    (verifier_dir / "verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (verifier_dir / "reward.json").write_text(
        json.dumps(reward, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
