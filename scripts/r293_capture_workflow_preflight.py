#!/usr/bin/env python3
"""R293 offline/static safety gate for the prepared one-shot capture workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_RESULT_BRANCH = "research/r293-v25-capture-result"
EXPECTED_CONFIRMATION = "RUN_R293_V25_CAPTURE_ONCE"
EXPECTED_OUTPUTS = [
    "research/captures/r293/vectors.f32le",
    "research/captures/r293/manifest.json",
    "research/captures/r293/SHA256SUMS",
    "research/captures/r293/run-receipt.json",
]
BANNED = (
    "pull_request:",
    "pull_request_target:",
    "push:",
    "schedule:",
    "repository_dispatch:",
    "workflow_call:",
    "secrets.",
    "actions/upload-artifact",
    "actions/download-artifact",
    "actions/cache",
    "git lfs",
    "GIT_LFS",
    "personal access token",
    "gh auth",
)
R291_FILES = {
    "research/r291/r291_capture_harness.py": {
        "blob": "3e438c0f6b87ab2fa90c1fc71bbf3cfea1e9052d",
        "sha256": "28526a56505beaa94183ea590810949a3a856639d3f6fa63d8869ddad419ad3e",
    },
    "research/r291/R291_WHESTBENCH_0_16_1_INTEGRATION.patch": {
        "blob": "a3d909540fc079908fcca9987c5cdb0252a1da8c",
        "sha256": "20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e",
    },
    "research/r291/R291_EXPECTED_PUBLIC_MINI100.json": {
        "blob": "caf813cd5eab771108f105fe050fd6631b298733",
        "sha256": "ebeb221b71cf3842e807d5cf28b8c38493e53032c8e1fa897b7f5bef6b1be720",
    },
}


class GateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def job_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    jobs_i = next((i for i, line in enumerate(lines) if line == "jobs:"), None)
    require(jobs_i is not None, "missing top-level jobs:")
    starts: list[tuple[int, str]] = []
    for i in range(jobs_i + 1, len(lines)):
        line = lines[i]
        if line and not line.startswith(" "):
            break
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if m:
            starts.append((i, m.group(1)))
    require(starts, "no jobs found")
    out: dict[str, str] = {}
    for n, (start, name) in enumerate(starts):
        stop = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        out[name] = "\n".join(lines[start:stop])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", type=Path, required=True)
    ap.add_argument("--protocol", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()

    text = args.workflow.read_text(encoding="utf-8")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    root = args.repo_root

    require(text.startswith("name: R293 V25 residual capture one-shot\n\non:\n  workflow_dispatch:\n"),
            "workflow must have workflow_dispatch as its only declared trigger")
    for needle in BANNED:
        require(needle not in text, f"banned workflow surface present: {needle}")
    require("permissions: {}" in text, "top-level permissions must be empty")
    require(text.count("contents: write") == 1, "contents: write must appear exactly once")
    require(text.count("runs-on: ubuntu-24.04") == 2, "both jobs must use ubuntu-24.04")
    require("self-hosted" not in text and "ubuntu-latest" not in text,
            "only the pinned standard ubuntu-24.04 runner is allowed")
    require(text.count("persist-credentials: false") == 2,
            "both checkouts must keep credentials out of git config")
    require(text.count("github.ref == 'refs/heads/main'") == 2,
            "both jobs must fail closed unless dispatch ref is main")
    require(text.count(EXPECTED_CONFIRMATION) >= 3,
            "frozen confirmation token is missing from dispatch/jobs")
    require(f"RESULT_BRANCH: {EXPECTED_RESULT_BRANCH}" in text,
            "result branch must be a frozen env constant")
    require("inputs.result_branch" not in text, "result branch must not be dispatch-controlled")
    require("git push" in text, "persistence job must explicitly use git push")
    require("github.token" in text, "persistence must use the built-in GITHUB_TOKEN")
    require("git add ." not in text and "git add -A" not in text,
            "broad git add is forbidden")
    require("protected" in text and "GITHUB_SHA" in text and "ls-remote" in text,
            "branch protection/tip gates are required")
    require("git cat-file -e" in text, "one-shot existing-output gate is required")

    jobs = job_blocks(text)
    require(set(jobs) == {"preflight", "persist"}, f"unexpected jobs: {sorted(jobs)}")
    require("permissions:\n      contents: read" in jobs["preflight"],
            "preflight job must have contents: read only")
    require("permissions:\n      contents: write" in jobs["persist"],
            "persist job must be the sole contents: write holder")

    pins = protocol["runtime_pins"]
    for package, version in pins.items():
        if package == "python":
            require(f'python-version: "{version}"' in text, "python pin missing")
        else:
            require(f"{package}=={version}" in text, f"runtime pin missing: {package}=={version}")
    v25 = protocol["v25"]
    for value in (
        v25["upstream_commit"],
        v25["git_blob_sha1"],
        v25["sha256"],
        protocol["evaluator"]["whestbench_scoring_blob_sha1"],
    ):
        require(value in text, f"frozen source identity missing from workflow: {value}")

    require(protocol["dispatch"]["trigger"] == "workflow_dispatch only", "protocol trigger drift")
    require(protocol["dispatch"]["required_ref"] == "refs/heads/main", "protocol ref drift")
    require(protocol["dispatch"]["result_branch"] == EXPECTED_RESULT_BRANCH, "protocol branch drift")
    require(protocol["output"]["allowlist"] == EXPECTED_OUTPUTS, "protocol output allowlist drift")
    require(protocol["permissions"]["persistence_job"] == "contents: write",
            "protocol persistence permission drift")
    require(all(value is False for value in protocol["authorization"].values()),
            "R293 protocol must not authorize merge/run/benchmark/result-branch creation")

    for rel, expected in R291_FILES.items():
        data = (root / rel).read_bytes()
        require(git_blob_sha1(data) == expected["blob"], f"R291 blob drift: {rel}")
        require(hashlib.sha256(data).hexdigest() == expected["sha256"], f"R291 SHA256 drift: {rel}")

    for path in EXPECTED_OUTPUTS:
        require(path in text, f"output allowlist member absent from workflow: {path}")
    for broad in ("research/captures/r293/", "research/captures/", "research/"):
        # Directory names may occur in mkdir/copy paths, but never as a git-add target.
        require(f"git add {broad}" not in text, f"broad git add target forbidden: {broad}")

    print(json.dumps({
        "status": "PASS",
        "workflow": str(args.workflow),
        "protocol": str(args.protocol),
        "jobs": sorted(jobs),
        "result_branch": EXPECTED_RESULT_BRANCH,
        "output_allowlist": EXPECTED_OUTPUTS,
        "r291_artifacts_verified": sorted(R291_FILES),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
