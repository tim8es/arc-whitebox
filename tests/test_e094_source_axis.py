import numpy as np

from methods.e094_source_axis import (
    V29_LEDGER,
    compressed_hub,
    compressed_transport,
    cost_necessity,
    direct_hub,
    direct_transport,
    make_exact_case,
    make_near_low_rank_case,
    run_stage_a,
    source_axis_factor,
)


def test_exact_source_axis_transport_and_signed_hub_identity():
    case = make_exact_case(seed=94094, n=48, sources=12, rank=3)
    W = case["W"]
    gamma = case["gamma"]
    assert np.min(gamma) < 0.0 < np.max(gamma)

    direct_t = direct_transport(W, case["A"])
    compressed_t = compressed_transport(W, case["C_A"], case["A_basis"])
    assert np.max(np.abs(direct_t - compressed_t)) <= 1e-11

    direct_h = direct_hub(gamma, case["L"], case["R"])
    compressed_h, metric_rank = compressed_hub(
        gamma,
        case["C_L"],
        case["L_basis"],
        case["C_R"],
        case["R_basis"],
    )
    diff = compressed_h - direct_h
    assert metric_rank <= 3
    assert np.max(np.abs(diff)) <= 1e-10
    assert np.linalg.norm(diff) / np.linalg.norm(direct_h) <= 1e-11


def test_joint_source_svd_truncation_error_tracks_discarded_energy():
    stack_errors = []
    transport_errors = []
    hub_errors = []
    for eps in (1e-6, 1e-4, 1e-2):
        case = make_near_low_rank_case(seed=94094, n=48, sources=12, rank=3, eps=eps)
        C_A, (A_basis, P_basis), predicted_A = source_axis_factor(
            (case["A"], case["P"]), rank=3
        )
        C_L, (L_basis,), predicted_L = source_axis_factor((case["L"],), rank=3)
        C_R, (R_basis,), predicted_R = source_axis_factor((case["R"],), rank=3)

        A_rec = np.einsum("sr,rij->sij", C_A, A_basis)
        P_rec = np.einsum("sr,rij->sij", C_A, P_basis)
        num = np.sqrt(np.sum((A_rec - case["A"]) ** 2) + np.sum((P_rec - case["P"]) ** 2))
        den = np.sqrt(np.sum(case["A"] ** 2) + np.sum(case["P"] ** 2))
        stack_err = float(num / den)
        assert stack_err <= 1.05 * predicted_A + 1e-14

        dt = direct_transport(case["W"], case["A"])
        ct = compressed_transport(case["W"], C_A, A_basis)
        transport_err = float(np.linalg.norm(ct - dt) / np.linalg.norm(dt))
        assert transport_err <= 4.0 * stack_err + 1e-13

        dh = direct_hub(case["gamma"], case["L"], case["R"])
        ch, _ = compressed_hub(case["gamma"], C_L, L_basis, C_R, R_basis)
        hub_err = float(np.linalg.norm(ch - dh) / np.linalg.norm(dh))
        lr_err = max(predicted_L, predicted_R)
        assert hub_err <= 12.0 * lr_err + 1e-13

        stack_errors.append(stack_err)
        transport_errors.append(transport_err)
        hub_errors.append(hub_err)

    assert all(a <= b for a, b in zip(stack_errors, stack_errors[1:]))
    assert all(a <= b for a, b in zip(transport_errors, transport_errors[1:]))
    assert all(a <= b for a, b in zip(hub_errors, hub_errors[1:]))


def test_measured_v29_cost_necessity_requires_joint_family_attack():
    result = cost_necessity()
    assert V29_LEDGER["total"] == 260.1
    assert result["delete_old_only_units"] > 138.24
    assert result["delete_young_only_units"] > 138.24
    assert 0.40 <= result["symmetric_remaining_fraction"] <= 0.50
    assert 0.0 < result["young_remaining_if_old_half"] < 0.50
    assert 0.0 < result["old_remaining_if_young_half"] < 0.50


def test_frozen_stage_a_go():
    result = run_stage_a()
    assert result["decision"] == "STAGE_A_GO"
    assert result["scope"] == {
        "public": False,
        "scorer": False,
        "holdout": False,
        "full_suite": False,
    }
    assert all(result["gates"].values())
