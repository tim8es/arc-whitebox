#!/usr/bin/env python3
"""Offline apply/semantic gate for the R294 repair of the historical R291 patch."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SOURCE_BLOB = "9cf7653a0267c4d048617c9045ac8be127f3c8bf"
OLD_PATCH_BLOB = "a3d909540fc079908fcca9987c5cdb0252a1da8c"
OLD_PATCH_SHA256 = "20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e"
NEW_PATCH_BLOB = "65abb2e2040e44a7965f5123acd17bb838891532"
NEW_PATCH_SHA256 = "bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3"
PATCHED_SOURCE_BLOB = "8493b7ff28110fb13f467400b6895c56bd7550bb"
EXPECTED_HUNKS = [
    "@@ -681,6 +681,17 @@ def evaluate_estimator(",
    "@@ -816,6 +827,21 @@ def evaluate_estimator(",
    "@@ -945,6 +971,21 @@ def evaluate_estimator(",
]
SEMANTIC_ANCHORS = [
    "with budget_ctx:",
    "final_layer_mse_fail = float(fnp.mean((pred_np[-1] - final_target) ** 2))",
    "all_layers_mse_fail = float(fnp.mean((pred_np - all_target) ** 2))",
    "final_layer_mse = float(fnp.mean((final_pred - final_target) ** 2))",
    "all_layers_mse = float(fnp.mean((pred_np - all_target) ** 2))",
    "adjusted_final_layer_score = _compute_budget_adjusted_score(",
    "return {",
]


class CheckError(RuntimeError):
    pass


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise CheckError(msg)


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_lines(patch: Path, prefix: str) -> list[str]:
    marker = prefix * 3
    return [
        line[1:]
        for line in patch.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix) and not line.startswith(marker)
    ]


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--patch", type=Path, required=True)
    ap.add_argument("--old-patch", type=Path, required=True)
    args = ap.parse_args()

    require(git_blob(args.source) == SOURCE_BLOB, "pinned scoring.py blob mismatch")
    require(git_blob(args.old_patch) == OLD_PATCH_BLOB, "historical R291 patch blob mismatch")
    require(sha256(args.old_patch) == OLD_PATCH_SHA256, "historical R291 patch SHA256 mismatch")
    require(git_blob(args.patch) == NEW_PATCH_BLOB, "R294 patch blob mismatch")
    require(sha256(args.patch) == NEW_PATCH_SHA256, "R294 patch SHA256 mismatch")

    old_added = source_lines(args.old_patch, "+")
    new_added = source_lines(args.patch, "+")
    new_deleted = source_lines(args.patch, "-")
    hunks = [line for line in args.patch.read_text(encoding="utf-8").splitlines() if line.startswith("@@")]
    require(len(old_added) == 41, "historical R291 patch must contain 41 source additions")
    require(new_added == old_added, "R294 source additions differ from historical R291 intent")
    require(not new_deleted, "R294 patch must delete zero official source lines")
    require(hunks == EXPECTED_HUNKS, f"unexpected R294 hunk headers: {hunks!r}")

    source_text = args.source.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="r294-patch-check-") as td:
        root = Path(td)
        dst = root / "src" / "whestbench" / "scoring.py"
        dst.parent.mkdir(parents=True)
        shutil.copyfile(args.source, dst)
        require(run_git(root, "init", "-q").returncode == 0, "git init failed")

        old = run_git(root, "apply", "--check", str(args.old_patch.resolve()))
        require(old.returncode != 0, "historical malformed R291 patch unexpectedly applies")
        require(
            "error: corrupt patch at line 23" in old.stderr,
            f"historical R291 failure drifted: {old.stderr.strip()!r}",
        )

        checked = run_git(root, "apply", "--check", str(args.patch.resolve()))
        require(checked.returncode == 0, f"R294 git apply --check failed: {checked.stderr.strip()}")
        applied = run_git(root, "apply", str(args.patch.resolve()))
        require(applied.returncode == 0, f"R294 git apply failed: {applied.stderr.strip()}")
        require(git_blob(dst) == PATCHED_SOURCE_BLOB, "patched scoring.py blob mismatch")

        patched_text = dst.read_text(encoding="utf-8")
        # Zero source deletions plus this subsequence test proves every official line
        # survives byte-for-byte and in order; only the 41 sidecar lines are inserted.
        cursor = 0
        for line in source_text.splitlines(keepends=True):
            pos = patched_text.find(line, cursor)
            require(pos >= cursor, "official scoring.py line deleted/reordered by R294 patch")
            cursor = pos + len(line)
        for anchor in SEMANTIC_ANCHORS:
            require(
                patched_text.count(anchor) == source_text.count(anchor),
                f"official score/return/FLOP anchor count changed: {anchor}",
            )
        require(patched_text.count("r291_capture.safe_capture(") == 2, "expected two capture calls")
        require(patched_text.count("from r291_capture_harness import capture_from_env_best_effort") == 1,
                "expected one sidecar initializer import")

    result = {
        "status": "PASS",
        "source_blob": SOURCE_BLOB,
        "old_patch": {
            "blob": OLD_PATCH_BLOB,
            "sha256": OLD_PATCH_SHA256,
            "git_apply_check_exit": old.returncode,
            "stderr": old.stderr.strip(),
        },
        "r294_patch": {
            "blob": NEW_PATCH_BLOB,
            "sha256": NEW_PATCH_SHA256,
            "git_apply_check_exit": checked.returncode,
            "git_apply_exit": applied.returncode,
            "hunks": hunks,
            "source_additions": len(new_added),
            "source_deletions": len(new_deleted),
            "patched_source_blob": PATCHED_SOURCE_BLOB,
        },
        "source_additions_identical_to_r291": new_added == old_added,
        "official_source_lines_preserved_in_order": True,
        "score_return_flop_anchor_counts_unchanged": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
