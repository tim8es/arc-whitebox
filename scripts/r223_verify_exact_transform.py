#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

UPSTREAM_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
ATTEMPT1_CANDIDATE_COMMIT = "3fd18dd4a4ec69f5cb1a9f69b071272e89e1f05d"
CANDIDATE_PATH = "methods/r223_estimator_v25_local_feed.py"

OLD = """                        dG0 = t_g + t_v * lam_prev                # table value first
                        rr = fnp.mean(dG0) / fnp.mean(var)
                        ref = float(REF_R[min(li - 1, len(REF_R) - 1)])
                        # clamp: an odd MLP must never turn the rule into NaN/inf (zero fallback)
                        lam_prev = lam_prev * fnp.power(fnp.clip(rr / ref, 0.5, 2.0), BETA)
                        dG = t_g + t_v * lam_prev                 # var == diag(C_pre)
                    else:
                        dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev  # var == diag(C_pre)"""

NEW = """                        dG0 = t_g + t_v * lam_prev                # table value first
                        rr = fnp.mean(dG0) / fnp.mean(var)
                        ref = float(REF_R[min(li - 1, len(REF_R) - 1)])
                        # R223: feed-only local heterogeneity. Reuse V25's own clamp,
                        # normalize back to unit mean, and leave scalar transport/use-side unchanged.
                        feed_scale = fnp.clip((dG0 / var) / rr, 0.5, 2.0)
                        feed_scale = feed_scale / fnp.mean(feed_scale)
                        # clamp: an odd MLP must never turn the rule into NaN/inf (zero fallback)
                        lam_prev = lam_prev * fnp.power(fnp.clip(rr / ref, 0.5, 2.0), BETA)
                        dG = t_g + t_v * lam_prev                 # var == diag(C_pre)
                        lam_feed = feed_scale * lam_prev
                    else:
                        dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev  # var == diag(C_pre)
                        lam_feed = ones_n * lam_prev"""

OLD_C1 = "                c1_b = w1 * lam_prev"
NEW_C1 = "                c1_b = w1 * lam_feed"

OLD_DOC = "ADAPTIVE PER-MLP LAMBDA (V25, 2026-09-03)."
NEW_DOC = (
    "ADAPTIVE PER-MLP LAMBDA (V25, 2026-09-03).\n"
    "+ R223 FEED-ONLY NORMALIZED PER-NEURON LAMBDA "
    "(development candidate, 2026-09-22)."
)

ATTEMPT1_LITERAL = (
    "ADAPTIVE PER-MLP LAMBDA (V25, 2026-09-03).\\n"
    "+ R223 FEED-ONLY NORMALIZED PER-NEURON LAMBDA "
    "(development candidate, 2026-09-22)."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], text=True).strip()


def git_show(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"])


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verifier PARENT CANDIDATE OUT_JSON")
    parent_path = Path(sys.argv[1])
    candidate_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])

    parent_bytes = parent_path.read_bytes()
    candidate_bytes = candidate_path.read_bytes()
    parent = parent_bytes.decode("utf-8")
    candidate = candidate_bytes.decode("utf-8")

    observed_parent_blob = git_blob(str(parent_path))
    assert observed_parent_blob == UPSTREAM_BLOB, (
        observed_parent_blob,
        UPSTREAM_BLOB,
    )

    # First prove attempt 2 differs from the frozen attempt-1 candidate only by
    # replacing the one literal backslash-n documentation sequence with one LF.
    attempt1_bytes = git_show(ATTEMPT1_CANDIDATE_COMMIT, CANDIDATE_PATH)
    attempt1 = attempt1_bytes.decode("utf-8")
    assert attempt1.count(ATTEMPT1_LITERAL) == 1
    normalized_attempt1 = attempt1.replace(ATTEMPT1_LITERAL, NEW_DOC)
    assert normalized_attempt1 == candidate, (
        "attempt-2 candidate differs from attempt-1 by more than docstring newline"
    )

    # Independently reconstruct the preregistered candidate from pinned V25.
    assert parent.count(OLD) == 1
    expected = parent.replace(OLD, NEW)
    assert expected.count(OLD_C1) == 1
    expected = expected.replace(OLD_C1, NEW_C1)
    assert expected.count(OLD_DOC) == 1
    expected = expected.replace(OLD_DOC, NEW_DOC)
    assert expected == candidate, (
        "candidate differs from exact preregistered V25->V25-LF transform"
    )

    # Guard the intended formula/clamp tokens explicitly.
    required = [
        "feed_scale = fnp.clip((dG0 / var) / rr, 0.5, 2.0)",
        "feed_scale = feed_scale / fnp.mean(feed_scale)",
        "lam_prev = lam_prev * fnp.power(fnp.clip(rr / ref, 0.5, 2.0), BETA)",
        "lam_feed = feed_scale * lam_prev",
        "lam_feed = ones_n * lam_prev",
        "c1_b = w1 * lam_feed",
    ]
    assert all(candidate.count(token) == 1 for token in required)
    assert ATTEMPT1_LITERAL not in candidate

    result = {
        "schema": "arc.whitebox.r223.attempt2_transform_guard.v1",
        "upstream_git_blob_sha1": observed_parent_blob,
        "upstream_sha256": sha256_bytes(parent_bytes),
        "attempt1_candidate_commit": ATTEMPT1_CANDIDATE_COMMIT,
        "attempt1_candidate_sha256": sha256_bytes(attempt1_bytes),
        "attempt2_candidate_git_blob_sha1": git_blob(str(candidate_path)),
        "attempt2_candidate_sha256": sha256_bytes(candidate_bytes),
        "attempt2_equals_attempt1_after_docstring_newline_normalization": True,
        "attempt2_equals_exact_preregistered_parent_transform": True,
        "formula_and_clamp_tokens_exact": True,
        "target_access": False,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
