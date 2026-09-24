#!/usr/bin/env python3
"""R296 offline adversarial self-check for PR #36 one-shot ref security."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

CHECKOUT_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"
RESULT_REF = "refs/heads/research/r293-v25-capture-result"


class CheckError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise CheckError(message)


def git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if check and proc.returncode != 0:
        raise CheckError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc


def remote_tip(remote: Path) -> str | None:
    proc = subprocess.run(
        ["git", "--git-dir", str(remote), "show-ref", "--verify", "--hash", RESULT_REF],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def set_remote(repo: Path, remote: Path, sha: str | None) -> None:
    if sha is None:
        proc = subprocess.run(
            ["git", "--git-dir", str(remote), "update-ref", "-d", RESULT_REF],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    else:
        proc = git(repo, ["push", "--force", str(remote), f"{sha}:{RESULT_REF}"], check=False)
    if proc.returncode != 0:
        raise CheckError(proc.stderr.strip())


def make_empty(repo: Path, message: str) -> str:
    git(["commit", "--allow-empty", "-m", message], repo)
    return git(["rev-parse", "HEAD"], repo).stdout.strip()


def lease_push(repo: Path, remote: Path, expected: str) -> subprocess.CompletedProcess[str]:
    return git(
        [
            "push",
            f"--force-with-lease={RESULT_REF}:{expected}",
            str(remote),
            f"HEAD:{RESULT_REF}",
        ],
        repo,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", type=Path, required=True)
    ap.add_argument("--protocol", type=Path, required=True)
    args = ap.parse_args()

    text = args.workflow.read_text(encoding="utf-8")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["rerun_gate_two_jobs"] = text.count("github.run_attempt == 1") == 2
    checks["checkout_full_sha"] = text.count(f"actions/checkout@{CHECKOUT_SHA}") == 2
    checks["setup_python_full_sha"] = text.count(f"actions/setup-python@{SETUP_PYTHON_SHA}") == 1
    checks["no_mutable_action_tags"] = (
        "actions/checkout@v4" not in text and "actions/setup-python@v5" not in text
    )
    checks["two_atomic_leases"] = text.count("--force-with-lease=") == 2
    checks["claim_expected_dispatch_tip"] = (
        '--force-with-lease="refs/heads/$RESULT_BRANCH:$GITHUB_SHA"' in text
    )
    checks["result_expected_claim_tip"] = (
        '--force-with-lease="refs/heads/$RESULT_BRANCH:$claim_sha"' in text
    )
    checks["durable_claim_before_install"] = (
        text.index("git commit --allow-empty") < text.index("Install exact direct runtime pins")
    )
    checks["token_not_in_remote"] = (
        "git remote set-url" not in text
        and "https://x-access-token:" not in text
        and "Authorization" not in text
    )
    checks["token_only_two_minimal_steps"] = (
        text.count("GITHUB_TOKEN: ${{ github.token }}") == 2
        and text.count("GIT_CONFIG_KEY_0=credential.helper") == 2
    )
    checks["protocol_no_branch_creation"] = (
        protocol["persistence"]["claim"]["branch_creation_allowed"] is False
        and protocol["persistence"]["result"]["branch_creation_allowed"] is False
    )
    checks["protocol_no_rerun_or_second_dispatch"] = (
        protocol["persistence"]["claim"]["rerun_allowed"] is False
        and protocol["persistence"]["claim"]["second_dispatch_allowed"] is False
    )

    with tempfile.TemporaryDirectory(prefix="r296-cas-") as td:
        root = Path(td)
        remote = root / "remote.git"
        repo = root / "work"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "init", str(repo)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        git(["config", "user.name", "R296 selfcheck"], repo)
        git(["config", "user.email", "r296@example.invalid"], repo)

        # The workflow's GIT_CONFIG_* helper is process-scoped: no token/helper survives in .git/config.
        dummy = "r296-dummy-token-must-not-persist"
        helper = '!f() { printf "%s\\n" "username=x-access-token" "password=$GITHUB_TOKEN"; }; f'
        env = {
            **os.environ,
            "GITHUB_TOKEN": dummy,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "credential.helper",
            "GIT_CONFIG_VALUE_0": helper,
        }
        visible = subprocess.run(
            ["git", "config", "--get", "credential.helper"],
            cwd=repo, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        local_after = git(["config", "--local", "--get", "credential.helper"], repo, check=False)
        config_text = (repo / ".git" / "config").read_text(encoding="utf-8")
        checks["process_scoped_helper_not_persisted"] = (
            visible.returncode == 0
            and "$GITHUB_TOKEN" in visible.stdout
            and local_after.returncode != 0
            and dummy not in config_text
            and "credential" not in config_text.lower()
        )

        (repo / "base.txt").write_text("base\n", encoding="utf-8")
        git(["add", "base.txt"], repo)
        git(["commit", "-m", "base"], repo)
        base = git(["rev-parse", "HEAD"], repo).stdout.strip()

        # Normal claim: pre-created exact tip -> succeeds.
        set_remote(repo, remote, base)
        claim1 = make_empty(repo, "claim1")
        p = lease_push(repo, remote, base)
        checks["claim_cas_success"] = p.returncode == 0 and remote_tip(remote) == claim1

        # Same dispatch / rerun: expected old tip is stale -> must fail.
        git(["reset", "--hard", base], repo)
        make_empty(repo, "claim-rerun")
        p = lease_push(repo, remote, base)
        checks["rerun_or_second_dispatch_lease_rejected"] = (
            p.returncode != 0 and remote_tip(remote) == claim1
        )

        # Branch absent after a successful pre-check: explicit expected-old lease must not create it.
        set_remote(repo, remote, None)
        git(["reset", "--hard", base], repo)
        make_empty(repo, "claim-after-delete")
        p = lease_push(repo, remote, base)
        checks["deleted_branch_not_recreated"] = (
            p.returncode != 0 and remote_tip(remote) is None
        )

        # Branch moved after check: stale expected old tip must reject.
        git(["reset", "--hard", base], repo)
        moved = make_empty(repo, "external-move")
        set_remote(repo, remote, moved)
        git(["reset", "--hard", base], repo)
        make_empty(repo, "claim-after-move")
        p = lease_push(repo, remote, base)
        checks["moved_branch_rejected"] = (
            p.returncode != 0 and remote_tip(remote) == moved
        )

        # Durable claim used by final-stage race tests.
        set_remote(repo, remote, base)
        git(["reset", "--hard", base], repo)
        claim = make_empty(repo, "durable-claim")
        p1 = lease_push(repo, remote, base)
        require(p1.returncode == 0 and remote_tip(remote) == claim,
                "setup durable claim failed")

        # Deletion after claim must not let final lease recreate the branch.
        git(["reset", "--hard", claim], repo)
        (repo / "deleted-final.txt").write_text("candidate\n", encoding="utf-8")
        git(["add", "deleted-final.txt"], repo)
        git(["commit", "-m", "candidate-after-delete"], repo)
        set_remote(repo, remote, None)
        p_deleted = lease_push(repo, remote, claim)
        checks["deleted_before_final_not_recreated"] = (
            p_deleted.returncode != 0 and remote_tip(remote) is None
        )

        # Movement after claim must reject a stale final lease.
        set_remote(repo, remote, claim)
        git(["reset", "--hard", claim], repo)
        moved_after_claim = make_empty(repo, "external-move-after-claim")
        set_remote(repo, remote, moved_after_claim)
        git(["reset", "--hard", claim], repo)
        (repo / "moved-final.txt").write_text("candidate\n", encoding="utf-8")
        git(["add", "moved-final.txt"], repo)
        git(["commit", "-m", "candidate-after-move"], repo)
        p_moved = lease_push(repo, remote, claim)
        checks["moved_before_final_rejected"] = (
            p_moved.returncode != 0 and remote_tip(remote) == moved_after_claim
        )

        # Happy path through durable claim then final result CAS.
        set_remote(repo, remote, claim)
        git(["reset", "--hard", claim], repo)
        (repo / "result.txt").write_text("result\n", encoding="utf-8")
        git(["add", "result.txt"], repo)
        git(["commit", "-m", "result"], repo)
        result = git(["rev-parse", "HEAD"], repo).stdout.strip()
        p2 = lease_push(repo, remote, claim)
        checks["final_cas_success"] = p2.returncode == 0 and remote_tip(remote) == result

        # A stale final lease cannot overwrite/move after the result has landed.
        git(["reset", "--hard", claim], repo)
        (repo / "other.txt").write_text("other\n", encoding="utf-8")
        git(["add", "other.txt"], repo)
        git(["commit", "-m", "other-result"], repo)
        p3 = lease_push(repo, remote, claim)
        checks["stale_final_lease_rejected"] = (
            p3.returncode != 0 and remote_tip(remote) == result
        )

    failed = sorted(k for k, v in checks.items() if not v)
    print(json.dumps({"status": "PASS" if not failed else "FAIL",
                      "checks": checks, "failed": failed},
                     indent=2, sort_keys=True))
    if failed:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
