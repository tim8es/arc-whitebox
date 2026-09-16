"""E094 source-axis joint compression algebra.

Synthetic/local-only research code. No benchmark/public/scorer access.
"""

from __future__ import annotations

import numpy as np

V29_LEDGER = {
    "total": 260.1,
    "young": 115.61,
    "old": 106.83,
    "thin_elementwise": 24.78,
    "covariance": 7.10,
    "birth_closure": 5.71,
}
TARGET_UNITS = 0.135 * 1024.0
NON_SOURCE_UNITS = 24.78 + 7.10 + 5.71


def _normal_matrix(rng: np.random.Generator, shape: tuple[int, ...], n: int) -> np.ndarray:
    return rng.standard_normal(shape).astype(np.float64) / np.sqrt(float(n))


def make_exact_case(seed: int, n: int, sources: int, rank: int) -> dict[str, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    W = _normal_matrix(rng, (n, n), n)

    A_basis = _normal_matrix(rng, (rank, n, n), n)
    P_basis = _normal_matrix(rng, (rank, n, n), n)
    L_basis = _normal_matrix(rng, (rank, n, n), n)
    R_basis = _normal_matrix(rng, (rank, n, n), n)

    C_A = rng.standard_normal((sources, rank)).astype(np.float64)
    C_L = rng.standard_normal((sources, rank)).astype(np.float64)
    C_R = rng.standard_normal((sources, rank)).astype(np.float64)

    A = np.einsum("sr,rij->sij", C_A, A_basis)
    P = np.einsum("sr,rij->sij", C_A, P_basis)
    L = np.einsum("sr,rij->sij", C_L, L_basis)
    R = np.einsum("sr,rij->sij", C_R, R_basis)

    magnitude = np.linspace(0.5, 1.5, sources, dtype=np.float64)
    signs = np.where(np.arange(sources) % 2 == 0, 1.0, -1.0)
    gamma = magnitude * signs

    return {
        "W": W,
        "A": A,
        "P": P,
        "L": L,
        "R": R,
        "C_A": C_A,
        "C_L": C_L,
        "C_R": C_R,
        "A_basis": A_basis,
        "P_basis": P_basis,
        "L_basis": L_basis,
        "R_basis": R_basis,
        "gamma": gamma,
    }


def _relative_perturbation(
    rng: np.random.Generator, x: np.ndarray, eps: float
) -> np.ndarray:
    noise = rng.standard_normal(x.shape).astype(np.float64)
    noise_norm = float(np.linalg.norm(noise))
    x_norm = float(np.linalg.norm(x))
    if noise_norm == 0.0 or x_norm == 0.0:
        raise ValueError("degenerate perturbation input")
    noise *= float(eps) * x_norm / noise_norm
    return x + noise


def make_near_low_rank_case(
    seed: int, n: int, sources: int, rank: int, eps: float
) -> dict[str, np.ndarray]:
    case = make_exact_case(seed=seed, n=n, sources=sources, rank=rank)
    # A seed independent of eps gives the same perturbation directions at every
    # frozen eps level, so the Stage-A ladder changes only perturbation amplitude.
    rng = np.random.Generator(np.random.PCG64(seed + 104729))
    for key in ("A", "P", "L", "R"):
        case[key] = _relative_perturbation(rng, case[key], eps)
    return case


def source_axis_factor(
    stacks: tuple[np.ndarray, ...], rank: int
) -> tuple[np.ndarray, tuple[np.ndarray, ...], float]:
    if not stacks:
        raise ValueError("at least one source stack is required")
    source_count = stacks[0].shape[0]
    if any(x.shape[0] != source_count for x in stacks):
        raise ValueError("all source stacks must share the same source axis")

    widths = [int(np.prod(x.shape[1:])) for x in stacks]
    joined = np.concatenate([x.reshape(source_count, -1) for x in stacks], axis=1)
    U, singular, Vh = np.linalg.svd(joined, full_matrices=False)
    r = min(int(rank), len(singular))
    coeff = U[:, :r] * singular[:r][None, :]

    bases: list[np.ndarray] = []
    start = 0
    for stack, width in zip(stacks, widths):
        block = Vh[:r, start : start + width]
        bases.append(block.reshape((r,) + stack.shape[1:]))
        start += width

    total_energy = float(np.sum(singular * singular))
    discarded = float(np.sum(singular[r:] * singular[r:]))
    relative_optimal_error = (
        float(np.sqrt(discarded / total_energy)) if total_energy > 0.0 else 0.0
    )
    return coeff, tuple(bases), relative_optimal_error


def direct_transport(W: np.ndarray, stack: np.ndarray) -> np.ndarray:
    return np.einsum("ij,sjk->sik", W, stack)


def compressed_transport(
    W: np.ndarray, coeff: np.ndarray, basis: np.ndarray
) -> np.ndarray:
    transported_basis = np.einsum("ij,rjk->rik", W, basis)
    return np.einsum("sr,rij->sij", coeff, transported_basis)


def direct_hub(gamma: np.ndarray, L: np.ndarray, R: np.ndarray) -> np.ndarray:
    return np.einsum("s,sik,sjk->ij", gamma, L, R)


def compressed_hub(
    gamma: np.ndarray,
    coeff_L: np.ndarray,
    basis_L: np.ndarray,
    coeff_R: np.ndarray,
    basis_R: np.ndarray,
) -> tuple[np.ndarray, int]:
    metric = coeff_L.T @ (gamma[:, None] * coeff_R)
    U, singular, Vh = np.linalg.svd(metric, full_matrices=False)
    if singular.size == 0:
        return np.zeros_like(basis_L[0] @ basis_R[0].T), 0

    tol = np.finfo(np.float64).eps * max(metric.shape) * float(singular[0])
    metric_rank = int(np.sum(singular > tol))
    if metric_rank == 0:
        return np.zeros_like(basis_L[0] @ basis_R[0].T), 0

    left = np.einsum("rt,rij->tij", U[:, :metric_rank], basis_L)
    right = np.einsum("tr,rij->tij", Vh[:metric_rank], basis_R)
    out = np.einsum(
        "t,tik,tjk->ij", singular[:metric_rank], left, right
    )
    return out, metric_rank


def cost_necessity() -> dict[str, float]:
    budget_for_source = TARGET_UNITS - NON_SOURCE_UNITS
    symmetric = budget_for_source / (V29_LEDGER["young"] + V29_LEDGER["old"])
    young_if_old_half = (
        budget_for_source - 0.5 * V29_LEDGER["old"]
    ) / V29_LEDGER["young"]
    old_if_young_half = (
        budget_for_source - 0.5 * V29_LEDGER["young"]
    ) / V29_LEDGER["old"]
    return {
        "target_units": TARGET_UNITS,
        "non_source_units": NON_SOURCE_UNITS,
        "delete_old_only_units": NON_SOURCE_UNITS + V29_LEDGER["young"],
        "delete_young_only_units": NON_SOURCE_UNITS + V29_LEDGER["old"],
        "symmetric_remaining_fraction": float(symmetric),
        "symmetric_reduction_fraction": float(1.0 - symmetric),
        "young_remaining_if_old_half": float(young_if_old_half),
        "old_remaining_if_young_half": float(old_if_young_half),
    }


def _relative_error(actual: np.ndarray, reference: np.ndarray) -> float:
    denom = float(np.linalg.norm(reference))
    num = float(np.linalg.norm(actual - reference))
    return num / denom if denom > 0.0 else num


def run_stage_a() -> dict[str, object]:
    seed, n, sources, rank = 94094, 48, 12, 3
    exact = make_exact_case(seed=seed, n=n, sources=sources, rank=rank)

    direct_t = direct_transport(exact["W"], exact["A"])
    compressed_t = compressed_transport(
        exact["W"], exact["C_A"], exact["A_basis"]
    )
    transport_max_abs = float(np.max(np.abs(compressed_t - direct_t)))

    direct_h = direct_hub(exact["gamma"], exact["L"], exact["R"])
    compressed_h, exact_metric_rank = compressed_hub(
        exact["gamma"],
        exact["C_L"],
        exact["L_basis"],
        exact["C_R"],
        exact["R_basis"],
    )
    hub_max_abs = float(np.max(np.abs(compressed_h - direct_h)))
    hub_rel = _relative_error(compressed_h, direct_h)

    ladder: list[dict[str, float]] = []
    for eps in (1e-6, 1e-4, 1e-2):
        case = make_near_low_rank_case(
            seed=seed, n=n, sources=sources, rank=rank, eps=eps
        )
        C_AP, (A_basis, P_basis), pred_ap = source_axis_factor(
            (case["A"], case["P"]), rank=rank
        )
        C_L, (L_basis,), pred_l = source_axis_factor((case["L"],), rank=rank)
        C_R, (R_basis,), pred_r = source_axis_factor((case["R"],), rank=rank)

        A_rec = np.einsum("sr,rij->sij", C_AP, A_basis)
        P_rec = np.einsum("sr,rij->sij", C_AP, P_basis)
        stack_num = float(
            np.sqrt(
                np.sum((A_rec - case["A"]) ** 2)
                + np.sum((P_rec - case["P"]) ** 2)
            )
        )
        stack_den = float(
            np.sqrt(np.sum(case["A"] ** 2) + np.sum(case["P"] ** 2))
        )
        stack_err = stack_num / stack_den

        dt = direct_transport(case["W"], case["A"])
        ct = compressed_transport(case["W"], C_AP, A_basis)
        transport_err = _relative_error(ct, dt)

        dh = direct_hub(case["gamma"], case["L"], case["R"])
        ch, metric_rank = compressed_hub(
            case["gamma"], C_L, L_basis, C_R, R_basis
        )
        hub_err = _relative_error(ch, dh)
        lr_pred = max(pred_l, pred_r)

        ladder.append(
            {
                "eps": float(eps),
                "joint_stack_rel_frob": float(stack_err),
                "discarded_energy_prediction": float(pred_ap),
                "transport_rel_frob": float(transport_err),
                "left_discarded_energy_prediction": float(pred_l),
                "right_discarded_energy_prediction": float(pred_r),
                "hub_reference_error_scale": float(lr_pred),
                "hub_rel_frob": float(hub_err),
                "metric_rank": int(metric_rank),
            }
        )

    stack_series = [row["joint_stack_rel_frob"] for row in ladder]
    transport_series = [row["transport_rel_frob"] for row in ladder]
    hub_series = [row["hub_rel_frob"] for row in ladder]

    truncation_each = all(
        row["joint_stack_rel_frob"]
        <= 1.05 * row["discarded_energy_prediction"] + 1e-14
        and row["transport_rel_frob"]
        <= 4.0 * row["joint_stack_rel_frob"] + 1e-13
        and row["hub_rel_frob"]
        <= 12.0 * row["hub_reference_error_scale"] + 1e-13
        for row in ladder
    )
    monotone = all(a <= b for a, b in zip(stack_series, stack_series[1:])) and all(
        a <= b for a, b in zip(transport_series, transport_series[1:])
    ) and all(a <= b for a, b in zip(hub_series, hub_series[1:]))

    costs = cost_necessity()
    finite = bool(
        all(
            np.all(np.isfinite(x))
            for x in (
                exact["W"],
                exact["A"],
                exact["P"],
                exact["L"],
                exact["R"],
                direct_t,
                compressed_t,
                direct_h,
                compressed_h,
            )
        )
        and all(
            np.isfinite(value)
            for row in ladder
            for key, value in row.items()
            if key != "metric_rank"
        )
    )

    gates = {
        "exact_transport": transport_max_abs <= 1e-11,
        "exact_hub_max_abs": hub_max_abs <= 1e-10,
        "exact_hub_rel_frob": hub_rel <= 1e-11,
        "signed_gamma": bool(
            np.min(exact["gamma"]) < 0.0 < np.max(exact["gamma"])
        ),
        "finite": finite,
        "truncation_bounds": bool(truncation_each),
        "truncation_monotone": bool(monotone),
        "single_family_insufficient": bool(
            costs["delete_old_only_units"] > TARGET_UNITS
            and costs["delete_young_only_units"] > TARGET_UNITS
        ),
        "cost_necessity_plausible": bool(
            costs["symmetric_remaining_fraction"] >= 0.40
        ),
    }
    decision = "STAGE_A_GO" if all(gates.values()) else "STAGE_A_NO_GO"

    return {
        "schema": "arc.whitebox.e094.stage_a.v1",
        "experiment": "E094",
        "decision": decision,
        "scientific_go": False,
        "scope": {
            "public": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
        },
        "frozen": {
            "seed": seed,
            "n": n,
            "sources": sources,
            "rank": rank,
            "eps": [1e-6, 1e-4, 1e-2],
        },
        "exact": {
            "transport_max_abs": transport_max_abs,
            "hub_max_abs": hub_max_abs,
            "hub_rel_frob": hub_rel,
            "hub_metric_rank": int(exact_metric_rank),
            "gamma_min": float(np.min(exact["gamma"])),
            "gamma_max": float(np.max(exact["gamma"])),
        },
        "truncation_ladder": ladder,
        "cost_necessity": costs,
        "gates": gates,
        "next_if_go": (
            "one synthetic official-shape V29 source-axis spectrum probe; no public"
        ),
    }
