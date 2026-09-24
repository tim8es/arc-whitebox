#!/usr/bin/env python3
"""Offline/static safety gate for the R293/R294/R296 one-shot capture workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_RESULT_BRANCH = "research/r293-v25-capture-result"
EXPECTED_CONFIRMATION = "RUN_R293_V25_CAPTURE_ONCE"
CHECKOUT_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"  # actions/checkout v4.2.2
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"  # actions/setup-python v5.6.0
TOKEN_EXPR = "GITHUB_TOKEN: ${{ github.token }}"
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
    "git remote set-url",
    "https://x-access-token:",
)
FROZEN_FILES = {
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
    "research/r294/R294_WHESTBENCH_0_16_1_INTEGRATION.patch": {
        "blob": "65abb2e2040e44a7965f5123acd17bb838891532",
        "sha256": "bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3",
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
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if match:
            starts.append((i, match.group(1)))
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

    require(
        text.startswith("name: R293 V25 residual capture one-shot\n\non:\n  workflow_dispatch:\n"),
        "workflow must have workflow_dispatch as its only declared trigger",
    )
    for needle in BANNED:
        require(needle not in text, f"banned workflow surface present: {needle}")

    require("permissions: {}" in text, "top-level permissions must be empty")
    require(text.count("contents: write") == 1, "contents: write must appear exactly once")
    require(text.count("runs-on: ubuntu-24.04") == 2, "both jobs must use ubuntu-24.04")
    require("self-hosted" not in text and "ubuntu-latest" not in text,
            "only standard pinned ubuntu-24.04 is allowed")
    require(text.count("persist-credentials: false") == 2,
            "both checkouts must keep credentials out of git config")
    require(text.count("github.ref == 'refs/heads/main'") == 2,
            "both jobs must fail closed unless dispatch ref is main")
    require(text.count("github.run_attempt == 1") == 2,
            "both jobs must fail closed on workflow re-runs")
    require(text.count(EXPECTED_CONFIRMATION) >= 3,
            "frozen confirmation token is missing")
    require(f"RESULT_BRANCH: {EXPECTED_RESULT_BRANCH}" in text,
            "result branch must be frozen")
    require("inputs.result_branch" not in text, "result branch must not be dispatch-controlled")

    require(text.count(f"actions/checkout@{CHECKOUT_SHA}") == 2,
            "checkout must be pinned twice to verified v4.2.2 SHA")
    require("actions/checkout@v4" not in text, "mutable checkout tag forbidden")
    require(text.count(f"actions/setup-python@{SETUP_PYTHON_SHA}") == 1,
            "setup-python must be pinned to verified v5.6.0 SHA")
    require("actions/setup-python@v5" not in text, "mutable setup-python tag forbidden")

    require(text.count("git push") == 2,
            "only durable claim CAS and final-result CAS pushes are allowed")
    require(text.count("--force-with-lease=") == 2,
            "both ref updates must use explicit expected-old-tip leases")
    require('--force-with-lease="refs/heads/$RESULT_BRANCH:$GITHUB_SHA"' in text,
            "claim lease must require exact pre-created dispatch SHA")
    require('--force-with-lease="refs/heads/$RESULT_BRANCH:$claim_sha"' in text,
            "final lease must require exact durable claim SHA")
    require("git commit --allow-empty" in text,
            "durable empty claim commit is required")
    require(text.count(TOKEN_EXPR) == 2,
            "GITHUB_TOKEN must be explicitly exposed only in two minimal CAS steps")
    require("GH_TOKEN:" not in text, "read-only checks must not expose a token")
    require("git remote set-url" not in text and "https://x-access-token:" not in text,
            "token must never be stored in remote URL")
    require("git config credential" not in text,
            "persistent credential-helper config is forbidden")
    require(text.count("GIT_CONFIG_KEY_0=credential.helper") == 2,
            "both authenticated pushes must use process-scoped credential helpers")
    require("git add ." not in text and "git add -A" not in text,
            "broad git add forbidden")
    require("protected" in text and "GITHUB_SHA" in text and "ls-remote" in text,
            "branch protection/tip gates are required")
    require("git cat-file -e" in text, "existing-output one-shot gate required")

    jobs = job_blocks(text)
    require(set(jobs) == {"preflight", "persist"}, f"unexpected jobs: {sorted(jobs)}")
    require("permissions:\n      contents: read" in jobs["preflight"],
            "preflight must have contents: read only")
    require("permissions:\n      contents: write" in jobs["persist"],
            "persist must be sole contents: write job")
    require("github.run_attempt == 1" in jobs["persist"],
            "benchmark-capable persist job must reject re-runs")
    require("git commit --allow-empty" in jobs["persist"],
            "persist job must durably claim before benchmark")
    require(
        jobs["persist"].index("git commit --allow-empty")
        < jobs["persist"].index("Install exact direct runtime pins"),
        "durable claim must precede dependency install / benchmark-capable work",
    )
    require(jobs["persist"].count(TOKEN_EXPR) == 2,
            "token exposure in write job must be only claim/final CAS steps")

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
        require(value in text, f"frozen source identity missing: {value}")

    evaluator = protocol["evaluator"]
    require(evaluator["active_integration_patch"] == "r294_patch_path",
            "protocol must select R294 patch")
    for value in (
        evaluator["r294_patch_path"],
        evaluator["r294_patch_blob_sha1"],
        evaluator["r294_patch_sha256"],
        evaluator["r294_patched_scoring_blob_sha1"],
    ):
        require(value in text, f"R294 patch identity missing: {value}")
    require("python scripts/r294_patch_apply_check.py" in text,
            "workflow must run real R294 apply checker")
    require("--old-patch research/r291/R291_WHESTBENCH_0_16_1_INTEGRATION.patch" in text,
            "workflow must retain old malformed-patch rejection evidence")
    require('git -C "$PATCH_ROOT" apply --check' in text,
            "workflow must run git apply --check")
    require("$GITHUB_WORKSPACE/research/r294/R294_WHESTBENCH_0_16_1_INTEGRATION.patch" in text,
            "workflow must apply only corrected R294 patch")

    require(protocol["dispatch"]["trigger"] == "workflow_dispatch only", "protocol trigger drift")
    require(protocol["dispatch"]["required_ref"] == "refs/heads/main", "protocol ref drift")
    require(protocol["dispatch"]["run_attempt_must_equal"] == 1, "protocol run-attempt drift")
    require(protocol["dispatch"]["result_branch"] == EXPECTED_RESULT_BRANCH, "protocol branch drift")
    require(protocol["actions"]["checkout"]["commit_sha"] == CHECKOUT_SHA,
            "protocol checkout SHA drift")
    require(protocol["actions"]["setup_python"]["commit_sha"] == SETUP_PYTHON_SHA,
            "protocol setup-python SHA drift")
    require(protocol["persistence"]["claim"]["branch_creation_allowed"] is False,
            "claim must forbid branch creation")
    require(protocol["persistence"]["claim"]["branch_movement_allowed"] is False,
            "claim must reject branch movement")
    require(protocol["persistence"]["claim"]["rerun_allowed"] is False,
            "claim protocol must reject re-runs")
    require(protocol["persistence"]["claim"]["second_dispatch_allowed"] is False,
            "claim protocol must reject second dispatch")
    require(protocol["persistence"]["result"]["branch_creation_allowed"] is False,
            "final persistence must forbid branch creation")
    require(protocol["persistence"]["credentials"]["token_in_remote_url"] is False,
            "protocol must forbid token-bearing remote URL")
    require(protocol["persistence"]["credentials"]["token_in_persistent_git_config"] is False,
            "protocol must forbid persistent token config")
    require(protocol["output"]["allowlist"] == EXPECTED_OUTPUTS, "output allowlist drift")
    require(protocol["permissions"]["persistence_job"] == "contents: write",
            "persistence permission drift")
    require(all(value is False for value in protocol["authorization"].values()),
            "protocol must not authorize merge/run/benchmark/result-branch creation")

    for rel, expected in FROZEN_FILES.items():
        data = (root / rel).read_bytes()
        require(git_blob_sha1(data) == expected["blob"], f"frozen blob drift: {rel}")
        require(hashlib.sha256(data).hexdigest() == expected["sha256"],
                f"frozen SHA256 drift: {rel}")

    for path in EXPECTED_OUTPUTS:
        require(path in text, f"allowlist member absent: {path}")
    for broad in ("research/captures/r293/", "research/captures/", "research/"):
        pattern = re.compile(r"(?m)^\s*git add\s+" + re.escape(broad) + r"\s*$")
        require(pattern.search(text) is None, f"broad git add target forbidden: {broad}")

    print(json.dumps({
        "status": "PASS",
        "workflow": str(args.workflow),
        "protocol": str(args.protocol),
        "jobs": sorted(jobs),
        "checkout_sha": CHECKOUT_SHA,
        "setup_python_sha": SETUP_PYTHON_SHA,
        "result_branch": EXPECTED_RESULT_BRANCH,
        "lease_updates": 2,
        "token_steps": 2,
        "output_allowlist": EXPECTED_OUTPUTS,
        "frozen_artifacts_verified": sorted(FROZEN_FILES),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
