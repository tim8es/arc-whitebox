from __future__ import annotations

from scripts.e014_patch_v29 import patch_joiner_block


ORIGINAL = '''                    Yq = pool.get("yq", (n, r_old))
                    Yq1 = pool.get("yq1", (n, r_old))
                    Yq2 = pool.get("yq2", (n, r_old))
                    for _pass in range(QPASS):
                        # Yq = G Om with G = Aj dA Aj^T + Pj dP Pj^T + Qp Sg Qp^T
                        fnp.matmul(Aj.T, Om, out=Yq1)
                        fnp.multiply(dAj, Yq1, out=Yq1)
                        fnp.matmul(Aj, Yq1, out=Yq)
                        fnp.matmul(Pj.T, Om, out=Yq1)
                        fnp.multiply(dPj, Yq1, out=Yq1)
                        fnp.matmul(Pj, Yq1, out=Yq2)
                        fnp.add(Yq, Yq2, out=Yq)
                        if ka > 0:
                            # V24: full core of the confined legs = tier-1 core + lifted tier-2 core
                            Sfull = Sg if kb == 0 else Sg + U @ (S2 @ U.T)
                            fnp.matmul(Qp, Sfull @ (Qp.T @ Om), out=Yq2)
                            fnp.add(Yq, Yq2, out=Yq)
'''


def test_joiner_patch_is_pair_batched_and_only_forward_pair_is_level1_strassen() -> None:
    patched = patch_joiner_block(ORIGINAL)

    assert 'join_ap4 = legs4["AP0"][2 * j:2 * j + 2]' in patched
    assert 'fnp.matmul(fnp.swapaxes(join_ap4[:, 0], -1, -2), Om, out=join_inner4[:, 0])' in patched
    assert 'smm.mm(join_ap4, join_inner4, join_outer4, 1)' in patched
    assert 'fnp.add(join_outer4[0, 0], join_outer4[1, 0], out=Yq)' in patched
    assert 'fnp.matmul(Qp, Sfull @ (Qp.T @ Om), out=Yq2)' in patched

    assert 'fnp.matmul(Aj.T, Om, out=Yq1)' not in patched
    assert 'fnp.matmul(Pj.T, Om, out=Yq1)' not in patched
    assert 'fnp.matmul(Aj, Yq1, out=Yq)' not in patched
    assert 'fnp.matmul(Pj, Yq1, out=Yq2)' not in patched


def test_joiner_patch_refuses_nonmatching_source() -> None:
    try:
        patch_joiner_block("not the frozen V29 joiner block")
    except ValueError as exc:
        assert "joiner block" in str(exc)
    else:
        raise AssertionError("patcher must refuse an unknown source")
