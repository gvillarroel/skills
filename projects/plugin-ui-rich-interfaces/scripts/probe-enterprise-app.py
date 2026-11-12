#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read the configured Google project's engine inventory without changing cloud resources."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="global")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]{4,62}", args.project) or not re.fullmatch(r"[a-z0-9-]+", args.location):
        parser.error("Use an explicit project ID and location.")
    command = shutil.which("gcloud.cmd") or shutil.which("gcloud")
    if not command:
        parser.error("The existing gcloud CLI is unavailable.")
    token_result = subprocess.run([command, "auth", "print-access-token", "--quiet"], capture_output=True, text=True, timeout=30)
    report = {"capturedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "project": args.project, "location": args.location, "collection": "default_collection", "scope": "Read-only engine inventory in one configured project/location; no deployment, API enablement, IAM change or host painting."}
    if token_result.returncode:
        report.update({"status": "credentials-unavailable", "tokenCommandExit": token_result.returncode})
    else:
        endpoint = f"https://discoveryengine.googleapis.com/v1beta/projects/{args.project}/locations/{args.location}/collections/default_collection/engines"
        request = urllib.request.Request(endpoint, headers={"Authorization": "Bearer " + token_result.stdout.strip(), "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = json.load(response)
                report.update({"status": "listed", "httpStatus": response.status, "engines": [{key: row.get(key) for key in ["name", "displayName", "solutionType", "industryVertical"]} for row in payload.get("engines", [])], "nextPageTokenPresent": bool(payload.get("nextPageToken"))})
        except urllib.error.HTTPError as error:
            payload = json.load(error)
            report.update({"status": "request-rejected", "httpStatus": error.code, "apiStatus": payload.get("error", {}).get("status"), "reasons": [detail.get("reason") for detail in payload.get("error", {}).get("details", []) if detail.get("reason")]})
        except (urllib.error.URLError, TimeoutError) as error:
            report.update({"status": "transport-unavailable", "errorType": type(error).__name__})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"project", "engines"}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
