import pytest

from methods.e027_final_d3g4_prune import patch_v25_source


def test_patch_inserts_only_final_mode1_mixed_term_subtraction():
    target = "            pk1v, pk2v, pk3v, pk4v = PK1[0], PK1[1], PK1[2], PK1[3]\n"
    source = "before\n" + target + "after\n"
    patched = patch_v25_source(source)
    expected = (
        target
        + "            if last and mode == 1:\n"
        + "                pk1v = pk1v - D3 * g4row * (WT[20] * (1.0 / 144.0))\n"
    )
    assert "before\n" in patched and "after\n" in patched
    assert expected in patched
    assert patched.count("if last and mode == 1:") == 1


def test_patch_rejects_missing_target():
    with pytest.raises(RuntimeError):
        patch_v25_source("no target")


def test_patch_rejects_ambiguous_target():
    target = "            pk1v, pk2v, pk3v, pk4v = PK1[0], PK1[1], PK1[2], PK1[3]\n"
    with pytest.raises(RuntimeError):
        patch_v25_source(target + target)
