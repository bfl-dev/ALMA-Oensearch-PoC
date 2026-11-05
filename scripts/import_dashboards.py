#!/usr/bin/env python3
"""Import standard saved objects; no custom UI or credential output."""
import argparse
import base64
import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5601")
    args = parser.parse_args()
    values = {}
    path = ROOT / ".env"
    if path.exists():
        values = dict(line.split("=", 1) for line in path.read_text().splitlines() if line and not line.startswith("#") and "=" in line)
    password = os.environ.get("OPENSEARCH_PASSWORD") or values.get("OPENSEARCH_PASSWORD")
    if not password:
        raise SystemExit("OPENSEARCH_PASSWORD or generated .env is required")
    boundary = "poc-" + uuid.uuid4().hex
    objects = (ROOT / "deployment/dashboards.ndjson").read_bytes()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="dashboards.ndjson"\r\nContent-Type: application/ndjson\r\n\r\n').encode() + objects + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(args.url.rstrip("/") + "/api/saved_objects/_import?overwrite=true", data=body, method="POST", headers={"Content-Type": "multipart/form-data; boundary=" + boundary, "osd-xsrf": "true", "securitytenant": "global", "Authorization": "Basic " + base64.b64encode(("admin:" + password).encode()).decode()})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Dashboards import failed with HTTP {exc.code}; no object import is claimed") from None
    output = {"success": result.get("success", False), "imported": result.get("successCount", 0), "errors": result.get("errors", [])}
    if output["success"]:
        output["tenant"] = "global"
        output["dashboard_url"] = args.url.rstrip("/") + "/app/dashboards?security_tenant=global#/view/poc-overview"
    print(json.dumps(output))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
