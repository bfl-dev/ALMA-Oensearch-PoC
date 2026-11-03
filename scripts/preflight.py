#!/usr/bin/env python3
"""Measure prerequisites before pulls; resolve public image manifests, never prune.

Compressed metadata is an estimate, not installed-size evidence. Actual Docker
growth is checked after every authorized pull; a 2 GB reserve remains untouched.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = {
    "OPENSEARCH_IMAGE": ("opensearchproject/opensearch", "3.9.0"),
    "DASHBOARDS_IMAGE": ("opensearchproject/opensearch-dashboards", "3.9.0"),
    "RABBITMQ_IMAGE": ("library/rabbitmq", "4.4.0-management"),
    "PYTHON_IMAGE": ("library/python", "3.12.16-slim-bookworm"),
}
ACCEPT = ", ".join(("application/vnd.oci.image.index.v1+json", "application/vnd.docker.distribution.manifest.list.v2+json", "application/vnd.oci.image.manifest.v1+json", "application/vnd.docker.distribution.manifest.v2+json"))


def command(arguments, timeout=30):
    result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env={**os.environ, "UV_CACHE_DIR": str(ROOT / ".cache/uv")})
    if result.returncode:
        # Commands here contain no secret arguments. Avoid dumping ambient
        # daemon/client configuration or full exception/credential-bearing URLs.
        raise RuntimeError(f"{arguments[0]} {arguments[1] if len(arguments)>1 else ''} failed: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'nonzero exit'}")
    return result.stdout.strip()


def request_json(url, headers=None):
    request = urllib.request.Request(url, headers={"User-Agent": "alma-opensearch-poc-preflight", **(headers or {})})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise RuntimeError("registry metadata exceeds bound")
        return json.loads(data), "sha256:" + hashlib.sha256(data).hexdigest()


def image_manifest(repository, tag):
    query = urllib.parse.urlencode({"service": "registry.docker.io", "scope": f"repository:{repository}:pull"})
    token, _ = request_json("https://auth.docker.io/token?" + query)
    headers = {"Authorization": "Bearer " + token["token"], "Accept": ACCEPT}
    base = "https://registry-1.docker.io/v2/" + repository + "/manifests/"
    manifest, index_digest = request_json(base + tag, headers)
    platform_digest = index_digest
    if "manifests" in manifest:
        candidates = [x for x in manifest["manifests"] if x.get("platform", {}).get("os") == "linux" and x.get("platform", {}).get("architecture") == "amd64" and x.get("platform", {}).get("variant", "") in ("", "v1")]
        if len(candidates) != 1:
            raise RuntimeError("image does not have one unambiguous Linux/amd64 manifest")
        platform_digest = candidates[0]["digest"]
        manifest, actual = request_json(base + platform_digest, headers)
        if actual != platform_digest:
            raise RuntimeError("registry platform digest mismatch")
    if not isinstance(manifest.get("layers"), list):
        raise RuntimeError("image manifest has no layer sizes")
    return {"repository": repository, "tag": tag, "platform": "linux/amd64", "index_digest": index_digest, "platform_digest": platform_digest, "reference": repository + "@" + platform_digest, "compressed_bytes": sum(x["size"] for x in manifest["layers"]), "layers": [{"digest": x["digest"], "size": x["size"]} for x in manifest["layers"]]}


def human_bytes(text):
    match = re.fullmatch(r"([\d.]+)\s*([kKmMgGtT]?)(i?)[bB]", text.strip())
    if not match:
        raise RuntimeError("unrecognized Docker disk usage unit")
    power = "kmgt".find(match[2].lower()) + 1 if match[2] else 0
    return int(float(match[1]) * (1024 if match[3] else 1000) ** power)


def docker_bytes():
    output = command(["docker", "system", "df", "--format", "{{json .}}"])
    return sum(human_bytes(json.loads(line)["Size"]) for line in output.splitlines() if line.strip())


def write_env():
    path = ROOT / ".env"
    if path.exists():
        return
    password = secrets.token_urlsafe(30) + "!aA7"
    rabbit = secrets.token_urlsafe(30)
    content = f"OPENSEARCH_INITIAL_ADMIN_PASSWORD={password}\nOPENSEARCH_PASSWORD={password}\nRABBITMQ_DEFAULT_USER=poc\nRABBITMQ_DEFAULT_PASS={rabbit}\nOPENSEARCH_VERIFY_CERTS=false\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        handle.write(content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pull", action="store_true", help="pull only after metadata, lock and capacity checks")
    parser.add_argument("--offline", action="store_true", help="prerequisites only; no network, lock, or pulls")
    parser.add_argument("--budget-gb", type=float, default=10)
    parser.add_argument("--headroom-gb", type=float, default=2)
    parser.add_argument("--min-memory-gib", type=float, default=7.25)
    args = parser.parse_args(argv)
    report = {"time": datetime.now(timezone.utc).isoformat(), "status": "blocked", "project_budget_bytes": int(args.budget_gb * 10**9), "headroom_bytes": int(args.headroom_gb * 10**9), "pulls_performed": [], "checks": {}, "failures": []}
    try:
        if not 2 < args.budget_gb or not 0 < args.headroom_gb < args.budget_gb or args.min_memory_gib <= 0:
            raise RuntimeError("invalid resource budget")
        memory = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        available = int(memory["MemAvailable"].strip().split()[0]) * 1024
        report["checks"].update(available_memory_bytes=available, required_memory_bytes=int(args.min_memory_gib * 1024**3), vm_max_map_count=int(Path("/proc/sys/vm/max_map_count").read_text()), project_filesystem_free=shutil.disk_usage(ROOT).free)
        report["checks"]["compose"] = command(["docker", "compose", "version"])
        context = json.loads(command(["docker", "context", "inspect"]))[0]
        endpoint = os.environ.get("DOCKER_HOST") or context["Endpoints"]["docker"]["Host"]
        report["checks"]["docker_endpoint"] = endpoint
        if not endpoint.startswith("unix://"):
            raise RuntimeError("this deployment is authorized for a local Docker daemon only")
        info = json.loads(command(["docker", "info", "--format", "{{json .}}"], timeout=20))
        report["checks"]["docker_server"] = info["ServerVersion"]
        report["checks"]["docker_storage_filesystem_free"] = shutil.disk_usage(info["DockerRootDir"]).free
        if available < args.min_memory_gib * 1024**3:
            raise RuntimeError("available memory is below configured stack ceilings; close other applications or use the main PC")
        if report["checks"]["vm_max_map_count"] < 262144:
            raise RuntimeError("vm.max_map_count needs host configuration; no system setting was changed")
        if args.offline:
            report["status"] = "prerequisites_only"
        else:
            images = {key: image_manifest(*value) for key, value in IMAGES.items()}
            report["images"] = images
            layers = {layer["digest"]: layer["size"] for image in images.values() for layer in image["layers"]}
            compressed = sum(layers.values())
            # Explicit heuristic only; enforce measured growth as pulls proceed.
            estimate = compressed * 3 + 10**9 + report["headroom_bytes"]
            report.update(unique_compressed_bytes=compressed, estimated_peak_bytes=estimate, estimate_is_not_installed_size=True)
            if estimate > report["project_budget_bytes"] or estimate > report["checks"]["docker_storage_filesystem_free"]:
                raise RuntimeError("candidate images/build/data reserve have no demonstrated fit in the storage budget")
            if not shutil.which("uv"):
                raise RuntimeError("uv is required to resolve the complete hashed dependency lock before building")
            report["checks"]["uv"] = command(["uv", "--version"])
            command(["uv", "pip", "compile", "--python-version", "3.12", "--generate-hashes", "--output-file", "requirements.lock", "requirements.in"], timeout=120)
            report["requirements_lock_sha256"] = hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest()
            report["checks"]["baseline_docker_bytes"] = baseline = docker_bytes()
            if args.pull:
                for key, image in images.items():
                    command(["docker", "pull", image["reference"]], timeout=600)
                    growth = max(0, docker_bytes() - baseline)
                    report["pulls_performed"].append({"component": key, "measured_global_docker_growth_bytes": growth})
                    if growth + 10**9 + report["headroom_bytes"] > report["project_budget_bytes"]:
                        raise RuntimeError("measured image growth exceeds safe project allowance; stop without pruning unrelated data")
            write_env()
            revision = command(["git", "rev-parse", "HEAD"])
            dirty = bool(command(["git", "status", "--porcelain"]))
            report["source_revision"] = revision + ("-dirty" if dirty else "")
            image_env = "\n".join(key + "=" + value["reference"] for key, value in images.items()) + "\nSOURCE_REVISION=" + report["source_revision"] + "\n"
            (ROOT / ".env.images").write_text(image_env)
            report["status"] = "images_pulled" if args.pull else "metadata_and_lock_only"
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        report["failures"].append(str(exc))
    artifact = ROOT / "artifacts/preflight.json"
    artifact.parent.mkdir(exist_ok=True)
    artifact.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "report": str(artifact), "failures": report["failures"]}))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
