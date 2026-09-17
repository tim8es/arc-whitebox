from __future__ import annotations

import inspect
import json
import math
import runpy
from pathlib import Path

import numpy as np

WIDTH = 32
BLOCKS = 512
TOTAL = 2 * WIDTH * BLOCKS
CANDIDATE_SEED = 100100
IID32_SEED = 100101
IID64CAST_SEED = 100102

PROD_N = 1024
PROD_D = 16
PROD_SAMPLES = 4096
BUDGET = 2**41


def scalar_moments(x: np.ndarray) -> dict[str, float]:
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    return {
        "mean": float(np.mean(a)),
        "variance_about_zero": float(np.mean(a * a)),
        "fourth_moment": float(np.mean(a ** 4)),
    }


def main() -> None:
    ns = runpy.run_path("scripts/e100_orthogonal_gaussian_antithetic.py")
    sampler = ns["haar_orthogonal_antithetic"]
    iid_sampler = ns["antithetic_iid"]
    cost_fn = ns["production_cost_bound"]

    cand = np.asarray(sampler(CANDIDATE_SEED, TOTAL), dtype=np.float32)
    iid32 = np.asarray(iid_sampler(IID32_SEED, TOTAL), dtype=np.float32)

    rng = np.random.Generator(np.random.PCG64(IID64CAST_SEED))
    pos64 = rng.standard_normal((TOTAL // 2, WIDTH)).astype(np.float32)
    iid64cast = np.concatenate((pos64, -pos64), axis=0)

    half = TOTAL // 2
    antithetic_max_abs = float(np.max(np.abs(cand[:half] + cand[half:])))

    pos = cand[:half].astype(np.float64)
    worst_orth = 0.0
    for b in range(BLOCKS):
        block = pos[b * WIDTH : (b + 1) * WIDTH]
        norms = np.linalg.norm(block, axis=1)
        dirs = block / norms[:, None]
        gram = dirs @ dirs.T
        worst_orth = max(worst_orth, float(np.max(np.abs(gram - np.eye(WIDTH)))))

    radius_sq = np.sum(pos * pos, axis=1)
    radius_mean = float(np.mean(radius_sq))
    radius_var = float(np.var(radius_sq, ddof=1))
    radius_mean_rel = abs(radius_mean - WIDTH) / WIDTH
    radius_var_rel = abs(radius_var - 2.0 * WIDTH) / (2.0 * WIDTH)

    m_c = scalar_moments(cand)
    m_i32 = scalar_moments(iid32)
    m_i64 = scalar_moments(iid64cast)
    variance_abs_from_one = abs(m_c["variance_about_zero"] - 1.0)
    fourth_abs_from_three = abs(m_c["fourth_moment"] - 3.0)
    variance_gap = max(
        abs(m_c["variance_about_zero"] - m_i32["variance_about_zero"]),
        abs(m_c["variance_about_zero"] - m_i64["variance_about_zero"]),
    )
    fourth_gap = max(
        abs(m_c["fourth_moment"] - m_i32["fourth_moment"]),
        abs(m_c["fourth_moment"] - m_i64["fourth_moment"]),
    )

    expected_forward = 2 * PROD_SAMPLES * PROD_D * PROD_N * PROD_N
    qr_blocks = (PROD_SAMPLES // 2) // PROD_N
    expected_qr = int(math.ceil(qr_blocks * (4.0 / 3.0) * PROD_N ** 3))
    expected_radial = 4 * PROD_SAMPLES * PROD_N
    expected_total = expected_forward + expected_qr + expected_radial
    expected_cost = {
        "forward_flops": expected_forward,
        "qr_flops": expected_qr,
        "radial_and_reduction_flops": expected_radial,
        "total_flops": expected_total,
        "utilization": expected_total / BUDGET,
    }
    observed_cost = cost_fn()
    cost_exact = observed_cost == expected_cost

    network = set(ns["NETWORK_SEEDS"])
    reference = set(ns["REFERENCE_SEEDS"])
    iid = set(ns["IID_SEEDS"])
    ortho = set(ns["ORTHO_SEEDS"])
    seed_sets_disjoint = all(
        a.isdisjoint(b)
        for i, a in enumerate((network, reference, iid, ortho))
        for b in (network, reference, iid, ortho)[i + 1 :]
    )

    source = inspect.getsource(sampler)
    sign_convention_present = (
        "signs = np.where(diag < 0.0, -1.0, 1.0)" in source
        and "q = q * signs[None, :]" in source
        and "rng.chisquare(df=WIDTH, size=WIDTH)" in source
    )

    gates = {
        "candidate_finite": bool(np.isfinite(cand).all()),
        "antithetic_pair_exact": antithetic_max_abs == 0.0,
        "direction_orthogonality_le_5e_6": worst_orth <= 5e-6,
        "candidate_variance_abs_from_one_le_0_05": variance_abs_from_one <= 0.05,
        "candidate_fourth_abs_from_three_le_0_30": fourth_abs_from_three <= 0.30,
        "variance_gap_vs_iid_le_0_05": variance_gap <= 0.05,
        "fourth_gap_vs_iid_le_0_30": fourth_gap <= 0.30,
        "radius_sq_mean_rel_le_0_02": radius_mean_rel <= 0.02,
        "radius_sq_var_rel_le_0_10": radius_var_rel <= 0.10,
        "cost_exact_match": bool(cost_exact),
        "seed_sets_pairwise_disjoint": bool(seed_sets_disjoint),
        "qr_sign_and_chi_source_present": bool(sign_convention_present),
    }

    out = {
        "schema": "arc.whitebox.e100.independent_review.v1",
        "experiment": "E100",
        "review_scope": "sampling-law-and-cost-only; no network scientific rerun",
        "samples": {"width": WIDTH, "blocks": BLOCKS, "total": TOTAL},
        "candidate_moments": m_c,
        "iid_float32_moments": m_i32,
        "iid_float64_cast_moments": m_i64,
        "antithetic_pair_max_abs": antithetic_max_abs,
        "direction_orthogonality_max_abs": worst_orth,
        "radius_sq": {
            "mean": radius_mean,
            "variance": radius_var,
            "mean_relative_error_vs_chi2": radius_mean_rel,
            "variance_relative_error_vs_chi2": radius_var_rel,
        },
        "marginal_gaps": {
            "variance_abs_from_one": variance_abs_from_one,
            "fourth_abs_from_three": fourth_abs_from_three,
            "max_variance_gap_vs_two_iid_paths": variance_gap,
            "max_fourth_gap_vs_two_iid_paths": fourth_gap,
        },
        "cost_recomputed": expected_cost,
        "cost_from_stage_a_code": observed_cost,
        "qr_blocks": qr_blocks,
        "seed_sets_pairwise_disjoint": seed_sets_disjoint,
        "qr_sign_and_chi_source_present": sign_convention_present,
        "finite_precision_caveat": (
            "The candidate is float32 rounding of a float64 Haar-direction times chi-radius Gaussian; "
            "the Stage-A iid comparator uses NumPy direct float32 normal generation. The discrete RNG "
            "laws are not bit-identical, although both target the same N(0,I) marginal. Low-order "
            "marginal checks against both direct-f32 and f64-cast iid paths are reported here."
        ),
        "theorem": (
            "Gaussian QR with positive-diagonal sign correction gives Haar Q. Each row is uniform "
            "on the unit sphere. Multiplication by an independent chi_n radius gives an exact "
            "N(0,I) marginal in real arithmetic; appending its negative yields an unbiased "
            "antithetic estimator. Cross-row dependence changes variance, not the expectation."
        ),
        "gates": gates,
        "review_pass": bool(all(gates.values())),
        "scientific_go": False,
        "scope": {"public": False, "scorer": False, "holdout": False, "full_suite": False},
    }
    Path("e100-independent-review.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )
    print("E100_INDEPENDENT_REVIEW=" + json.dumps(out, sort_keys=True), flush=True)
    if not out["review_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
