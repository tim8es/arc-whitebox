#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

EXPECTED = {
    "v25": "195373a110215256b759d7c172ba8c923c62e5cc",
    "probe": "2a443055a58e577700585d5664902d0541ec2d2c",
    "findings": "09cf41e8826052ceb83109115cae688c03baaaca",
    "claims": "087aaa2404a046afd06bd954a1cc0bf09ffdf05c",
}
B = 2**41
N = 1024
FEED_LAYERS = 14
PARENT_FLOPS = 806_303_721_965
PARENT_CB = 0.36666448157347986
ORACLE_RAW_MULT = 0.989


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path)], text=True
    ).strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--v25", type=Path, required=True)
    p.add_argument("--probe", type=Path, required=True)
    p.add_argument("--findings", type=Path, required=True)
    p.add_argument("--claims", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("r227-feasibility.json"))
    args = p.parse_args()

    paths = {
        "v25": args.v25,
        "probe": args.probe,
        "findings": args.findings,
        "claims": args.claims,
    }
    blobs = {k: git_blob(v) for k, v in paths.items()}
    identity = {k: blobs[k] == EXPECTED[k] for k in EXPECTED}

    v25 = args.v25.read_text(encoding="utf-8")
    probe = args.probe.read_text(encoding="utf-8")
    findings = args.findings.read_text(encoding="utf-8")
    claims = args.claims.read_text(encoding="utf-8")

    oracle_lstsq = "torch.linalg.lstsq(X, y[:, None])" in probe
    oracle_target_is_goff = "Goff = G if full else zd(G)" in probe and "y = Goff[mask]" in probe
    xregen_fit_then_replay = (
        'if nok == "xregen":' in probe
        and "pass 1 on every dump" in probe
        and "MEAN of the" in probe
        and "OTHER dumps" in probe
    )
    upstream_untried = (
        "only" in findings
        and "untested item is the F68 second regeneration mode" in findings
    )
    oracle_9mode = (
        "9 modes" in findings
        and "2.205e-8" in findings
        and "2.230" in findings
    )
    claims_oracle = "oracle projections" in claims and "2.205e-8" in claims

    # A deployable second-mode table/rule would need to be present in V25.
    # V25 has only the scalar LAM/REF_R/BETA regeneration law.
    multimode_runtime = any(
        token in v25
        for token in (
            "SECOND_REGEN",
            "REGEN2",
            "K4_MODE2",
            "MULTIMODE_REGEN",
            "G_MODE2",
        )
    )

    extra = FEED_LAYERS * 2 * N**3
    extra_cb = extra / B
    optimistic_ratio = ORACLE_RAW_MULT * (PARENT_CB + extra_cb) / PARENT_CB

    gates = {
        "all_pinned_blob_identities": all(identity.values()),
        "oracle_coefficients_use_dense_Goff": oracle_lstsq and oracle_target_is_goff,
        "xregen_fits_dense_chain_before_replay": xregen_fit_then_replay,
        "upstream_marks_second_mode_only_untried_track2": upstream_untried,
        "oracle_9mode_gain_recorded": oracle_9mode and claims_oracle,
        "published_deployable_multimode_runtime_rule": multimode_runtime,
        "literal_dense_mode_would_improve_adjusted_score": optimistic_ratio < 1.0,
    }

    deployable = bool(
        gates["all_pinned_blob_identities"]
        and gates["published_deployable_multimode_runtime_rule"]
        and gates["literal_dense_mode_would_improve_adjusted_score"]
    )
    result = {
        "schema": "arc.whitebox.r227.srm2_feasibility.v1",
        "job_id": "R227",
        "blobs": blobs,
        "identity": identity,
        "facts": {
            "oracle_lstsq_against_Goff": oracle_lstsq and oracle_target_is_goff,
            "xregen_fit_then_replay": xregen_fit_then_replay,
            "upstream_untried_marker": upstream_untried,
            "oracle_9mode_marker": oracle_9mode and claims_oracle,
            "v25_multimode_runtime_marker": multimode_runtime,
        },
        "cost": {
            "parent_flops": PARENT_FLOPS,
            "parent_c_over_b": PARENT_CB,
            "literal_dense_extra_lower_bound_flops": extra,
            "literal_dense_extra_c_over_b": extra_cb,
            "optimistic_oracle_raw_multiplier": ORACLE_RAW_MULT,
            "optimistic_adjusted_ratio_vs_parent": optimistic_ratio,
        },
        "deployable_second_mode_found": deployable,
        "decision": (
            "R227_FEASIBILITY_PASS_MINI100_MAY_BE_ARMED"
            if deployable
            else "R227_TERMINAL_PRE_SCIENCE_NO_GO"
        ),
        "gates": gates,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R227_FEASIBILITY=" + json.dumps(result, sort_keys=True))
    if not all(identity.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
