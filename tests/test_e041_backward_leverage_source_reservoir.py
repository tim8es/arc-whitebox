from __future__ import annotations

import numpy as np

from methods.e041_backward_leverage_source_reservoir import (
    CAPACITY,
    PINNED_BLOB_SHA,
    PINNED_COMMIT,
    PINNED_PATH,
    PROJECTED_UTILIZATION,
    backward_leverage_scores,
    patch_source,
    select_births_knapsack,
    source_pair_cost,
    walsh_probes,
)


def test_pinned_identity_and_capacity_projection():
    assert PINNED_COMMIT == "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
    assert PINNED_PATH == "estimators/estimator_v25.py"
    assert PINNED_BLOB_SHA == "195373a110215256b759d7c172ba8c923c62e5cc"
    assert CAPACITY == 41
    expected = 0.36666448 * (0.05 + 0.95 * 41.0 / 120.0)
    over = 0.36666448 * (0.05 + 0.95 * 42.0 / 120.0)
    assert abs(PROJECTED_UTILIZATION - expected) <= 1e-15
    assert abs(PROJECTED_UTILIZATION - 0.13734640313333332) <= 1e-15
    assert PROJECTED_UTILIZATION < 0.14 < over


def test_four_walsh_probes_are_deterministic_signs_and_orthogonal():
    q = walsh_probes(np, 8)
    assert q.shape == (8, 4)
    assert set(np.unique(q).tolist()) == {-1.0, 1.0}
    np.testing.assert_array_equal(q.T @ q, 8.0 * np.eye(4))
    np.testing.assert_array_equal(q, walsh_probes(np, 8))


def test_backward_leverage_matches_explicit_scalar_reference():
    # Stored weight w means forward operator is w.T; frozen adjoint update is 0.5*w@g.
    w0 = np.eye(4)
    w1 = np.diag([1.0, 2.0, 3.0, 4.0])
    w2 = np.diag([2.0, 1.0, 0.5, 0.25])
    weights = [w0, w1, w2]
    probes = walsh_probes(np, 4)
    got = backward_leverage_scores(np, weights, probes)

    g = probes.copy()
    ref = [None, None]
    g = 0.5 * (w2 @ g)
    ref[1] = np.mean(np.sum(g * g, axis=0))
    g = 0.5 * (w1 @ g)
    ref[0] = np.mean(np.sum(g * g, axis=0))
    np.testing.assert_allclose(got, np.asarray(ref), rtol=0.0, atol=0.0)


def test_knapsack_capacity_and_lexicographic_tie_break():
    scores = [1.0] * 15
    chosen = select_births_knapsack(scores, capacity=41)
    assert source_pair_cost(chosen) <= 41
    # Exact exhaustive reference with the same frozen value/cost definition.
    best_value = -1.0
    best_tuple = None
    for mask in range(1 << 15):
        tup = tuple(i for i in range(15) if mask & (1 << i))
        cost = source_pair_cost(tup)
        if cost > 41:
            continue
        value = float(len(tup))
        if value > best_value or (value == best_value and (best_tuple is None or tup < best_tuple)):
            best_value = value
            best_tuple = tup
    assert chosen == best_tuple


def test_atomic_patch_guards_complete_source_record():
    source = (
        'NO_CONFINE = _os.environ.get("V21_NO_CONFINE", "0") == "1"  # V21: 1 -> V20 op stream\n'
        '            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n'
        '            if rfb > 0:\n'
        '                r1n = fnp.reshape(R1T_b, (1, n, rfb))\n'
        '                r2n = fnp.reshape(R2T_b, (1, n, rfb))\n'
        '            w2b_list.append(w2)\n'
        '            dA_list.append(9.0 + w2 * w2 + 9.0 * e_b * e_b)\n'
        '            dP_list.append(1.0 + S3c * S3c)\n'
        '            c1_list.append(c1_b)\n'
        '            c2_list.append(dgw)\n'
        '            y_list.append(y_b)\n'
    )
    patched, counts = patch_source(source)
    assert all(v == 1 for v in counts.values())
    assert 'E041_KEEP_BIRTHS' in patched
    assert 'if li in E041_KEEP_BIRTHS else None' in patched
    assert 'if rfb > 0 and li in E041_KEEP_BIRTHS:' in patched
    for name in ('w2b_list', 'dA_list', 'dP_list', 'c1_list', 'c2_list', 'y_list'):
        assert f'if li in E041_KEEP_BIRTHS: {name}.append' in patched
