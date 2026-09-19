from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

WIDTH = 8
DEPTH = 4
RAW_TARGET = Fraction(189, 10_000_000_000)
OUT = Path("e117-schur-certificate.json")


def sylvester_hadamard(n: int) -> np.ndarray:
    if n < 1 or n & (n - 1):
        raise ValueError("n must be a positive power of two")
    h = np.array([[1]], dtype=np.int64)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    return h


def run_once() -> dict:
    h_int = sylvester_hadamard(WIDTH)
    gram_int = h_int @ h_int.T
    exact_orthogonal = bool(np.array_equal(gram_int, WIDTH * np.eye(WIDTH, dtype=np.int64)))

    h = h_int.astype(np.float64) / math.sqrt(float(WIDTH))
    gram = h @ h.T
    float_orthogonality_max_abs = float(
        np.max(np.abs(gram - np.eye(WIDTH, dtype=np.float64)))
    )
    singular_values = np.linalg.svd(h, compute_uv=False)
    spectral_norms = [float(singular_values[0])] * (DEPTH - 1)
    spectral_norm_max_abs_from_one = max(abs(x - 1.0) for x in spectral_norms)

    v = 0.5 - 1.0 / (2.0 * math.pi)
    certificates = [v * (WIDTH - r) for r in range(WIDTH + 1)]
    nontrivial = certificates[:WIDTH]
    best_nontrivial = min(nontrivial)
    best_rank = nontrivial.index(best_nontrivial)

    # Fully rigorous comparison independent of floating pi evaluation:
    # pi > 3 -> 1/(2*pi) < 1/6 -> v > 1/3.
    symbolic_lower_bound = Fraction(1, 3)
    target_below_symbolic_lower_bound = RAW_TARGET < symbolic_lower_bound
    target_ratio_float = best_nontrivial / float(RAW_TARGET)

    gates = {
        "integer_hadamard_orthogonality_exact": exact_orthogonal,
        "float_hadamard_orthogonality_le_1e_15": float_orthogonality_max_abs <= 1e-15,
        "suffix_spectral_norms_le_1e_15_from_one": spectral_norm_max_abs_from_one <= 1e-15,
        "variance_positive_finite": math.isfinite(v) and v > 0.0,
        "certificate_strictly_decreasing": all(
            certificates[i + 1] < certificates[i] for i in range(WIDTH)
        ),
        "full_rank_certificate_zero": certificates[WIDTH] == 0.0,
        "best_nontrivial_rank_is_7": best_rank == WIDTH - 1,
        "rigorous_lower_bound_exceeds_target": target_below_symbolic_lower_bound,
    }

    admission = best_nontrivial <= float(RAW_TARGET)
    decision = (
        "NONTRIVIAL_RANK_CERTIFICATE_GO"
        if admission
        else "TERMINAL_CERTIFICATE_NO_GO"
    )

    return {
        "schema": "arc.whitebox.e117.schur_certificate.v1",
        "experiment": "E117",
        "fixture": {
            "width": WIDTH,
            "depth": DEPTH,
            "input": "X~N(0,I_8)",
            "layer1_weight": "I_8",
            "suffix_weights": "normalized Sylvester H8/sqrt(8), repeated 3 times",
            "biases": "all_zero",
        },
        "theorem": {
            "compression": "h_hat = m + P(h-m), rank(P)=r",
            "remainder_bound": "|E f_j(h)-E f_j(h_hat)|^2 <= L_j^2 tr((I-P)Sigma)",
            "optimal_tail": "min_P tr((I-P)Sigma) = sum_{k>r} lambda_k(Sigma)",
            "centered_covariance": "Sigma = v I_8",
            "v_exact": "1/2 - 1/(2*pi)",
            "suffix_lipschitz": "L_j <= 1 because normalized Hadamard has norm 1 and ReLU is 1-Lipschitz",
            "certificate": "C_r = v*(8-r)",
        },
        "exact_checks": {
            "integer_hadamard_gram": gram_int.tolist(),
            "integer_hadamard_orthogonality_exact": exact_orthogonal,
            "pi_bound_used": "pi > 3",
            "v_rigorous_lower_bound": "1/3",
            "target_exact_fraction": f"{RAW_TARGET.numerator}/{RAW_TARGET.denominator}",
            "one_third_exceeds_target_exact": target_below_symbolic_lower_bound,
        },
        "numeric_crosscheck": {
            "v": v,
            "float_orthogonality_max_abs": float_orthogonality_max_abs,
            "suffix_spectral_norms": spectral_norms,
            "spectral_norm_max_abs_from_one": spectral_norm_max_abs_from_one,
            "certificates_by_rank": certificates,
            "best_nontrivial_rank": best_rank,
            "best_nontrivial_certificate": best_nontrivial,
            "raw_target": float(RAW_TARGET),
            "best_nontrivial_over_target": target_ratio_float,
        },
        "production_interpretation": {
            "only_zero_certificate_rank": WIDTH,
            "rank_reduction_at_zero_certificate": 0,
            "compression_ratio": 1.0,
            "cost_statement": (
                "The only certifiable rank is full rank; therefore this frozen "
                "low-rank/Schur certificate yields no compression. A full-rank "
                "identity can be skipped but provides no compute reduction."
            ),
            "production_prototype_authorized": False,
        },
        "gates": gates,
        "admission_gate": {
            "require_best_rank_reducing_certificate_le_1_89e_8": admission,
        },
        "decision": decision,
        "scientific_go": False,
        "scope": {
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "rescue": False,
            "production_run": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def max_numeric_delta(a: dict, b: dict) -> float:
    keys = [
        "v",
        "float_orthogonality_max_abs",
        "spectral_norm_max_abs_from_one",
        "best_nontrivial_certificate",
        "best_nontrivial_over_target",
    ]
    d = 0.0
    for key in keys:
        d = max(
            d,
            abs(
                float(a["numeric_crosscheck"][key])
                - float(b["numeric_crosscheck"][key])
            ),
        )
    ca = a["numeric_crosscheck"]["certificates_by_rank"]
    cb = b["numeric_crosscheck"]["certificates_by_rank"]
    d = max(d, max(abs(float(x) - float(y)) for x, y in zip(ca, cb)))
    return d


def main() -> None:
    first = run_once()
    second = run_once()
    repeat_max_abs = max_numeric_delta(first, second)
    first["determinism"] = {"repeat_max_abs": repeat_max_abs}
    first["gates"]["deterministic_repeat_max_abs_eq_0"] = repeat_max_abs == 0.0

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E117_SCHUR_CERTIFICATE=" + json.dumps(first, sort_keys=True), flush=True)

    integrity_names = [
        "integer_hadamard_orthogonality_exact",
        "float_hadamard_orthogonality_le_1e_15",
        "suffix_spectral_norms_le_1e_15_from_one",
        "variance_positive_finite",
        "certificate_strictly_decreasing",
        "full_rank_certificate_zero",
        "best_nontrivial_rank_is_7",
        "rigorous_lower_bound_exceeds_target",
        "deterministic_repeat_max_abs_eq_0",
    ]
    if not all(first["gates"][name] for name in integrity_names):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
