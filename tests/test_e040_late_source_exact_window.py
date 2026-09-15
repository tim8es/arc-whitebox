from __future__ import annotations

from methods.e040_late_source_exact_window import (
    INSERTION_CUTOFF,
    PINNED_BLOB_SHA,
    PINNED_COMMIT,
    PINNED_PATH,
    PROJECTED_UTILIZATION,
    birth_schedule,
    patch_source,
    source_layer_pairs,
)


def test_pinned_upstream_identity_and_frozen_cutoff():
    assert PINNED_COMMIT == "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
    assert PINNED_PATH == "estimators/estimator_v25.py"
    assert PINNED_BLOB_SHA == "195373a110215256b759d7c172ba8c923c62e5cc"
    assert INSERTION_CUTOFF == 8


def test_patch_changes_exactly_one_newborn_predicate_only():
    before = "x\n            if newborn is not None and not skip_src:\n                use()\ny\n"
    after, count = patch_source(before)
    assert count == 1
    assert "if newborn is not None and not skip_src and li >= 8:" in after
    assert after.replace(" and li >= 8", "") == before


def test_patch_rejects_nonunique_target():
    target = "            if newborn is not None and not skip_src:\n"
    try:
        patch_source(target + target)
    except ValueError as exc:
        assert "target count=2" in str(exc)
    else:
        raise AssertionError("nonunique target must fail")


def test_frozen_birth_schedule_and_pair_count():
    births, insertions = birth_schedule(depth=16)
    assert births == tuple(range(7, 15))
    assert insertions == tuple(range(8, 16))
    assert len(births) == 8
    assert source_layer_pairs(depth=16) == 36


def test_projected_utilization_is_frozen_and_under_gate():
    expected = 0.36666448 * (0.05 + 0.95 * (36.0 / 120.0))
    assert abs(PROJECTED_UTILIZATION - expected) <= 1e-15
    assert abs(PROJECTED_UTILIZATION - 0.1228326008) <= 1e-12
    assert PROJECTED_UTILIZATION < 0.14
