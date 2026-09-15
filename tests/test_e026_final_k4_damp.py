import pytest

from methods.e026_final_k4_damp import FINAL_K4_DAMP, final_k4_factor, patch_v25_source


def test_final_k4_factor_is_frozen_only_on_last_layer():
    assert FINAL_K4_DAMP == 0.95
    assert final_k4_factor(last=False) == 1.0
    assert final_k4_factor(last=True) == 0.95


def test_patch_changes_only_the_v25_g4row_assignment():
    source = "before\n                    g4row = dG * METRIC_C\nafter\n"
    patched = patch_v25_source(source)
    assert "before\n" in patched and "\nafter\n" in patched
    assert "g4row = dG * METRIC_C * (0.95 if last else 1.0)" in patched
    assert patched.count("g4row =") == 1


def test_patch_rejects_missing_or_ambiguous_target():
    with pytest.raises(RuntimeError):
        patch_v25_source("no target")
    target = "                    g4row = dG * METRIC_C\n"
    with pytest.raises(RuntimeError):
        patch_v25_source(target + target)
