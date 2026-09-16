from scripts.e091_local_check import run_check


def test_e091_frozen_local_reproducibility():
    r = run_check()
    assert r["corpus_schema"] == "arc.whitebox.e091.synthetic_corpus.v2"
    assert r["public_targets_read"] is False
    assert r["benchmark_data_read"] is False
    assert r["scientific_accuracy_evaluated"] is False
    assert r["finite"] is True
    assert r["press_vs_direct_max_abs"] <= 1e-12
    assert r["press_vs_direct_rel_frob"] <= 1e-12
    assert r["min_one_minus_h"] >= 1e-6
    assert r["self_target_perturb_max_abs"] <= 1e-12
    assert all(r["deterministic"].values())
