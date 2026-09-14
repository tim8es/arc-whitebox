from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED_V29_GIT_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"

ORIGINAL_JOINER_BLOCK = '''                    Yq = pool.get("yq", (n, r_old))
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

PATCHED_JOINER_BLOCK = '''                    Yq = pool.get("yq", (n, r_old))
                    Yq2 = pool.get("yq2", (n, r_old))
                    # E014: preserve V29 joiner arithmetic while scheduling the A/P
                    # transpose as one dense batch and pricing only the forward pair
                    # with the frozen level-1 Strassen family.
                    join_ap4 = legs4["AP0"][2 * j:2 * j + 2]
                    join_inner4 = pool.get("e014_join_inner4", (2, 1, n, r_old))
                    join_outer4 = pool.get("e014_join_outer4", (2, 1, n, r_old))
                    join_weights4 = pool.get("e014_join_weights4", (2, 1, n, 1))
                    fnp.copyto(join_weights4[0, 0], dAj)
                    fnp.copyto(join_weights4[1, 0], dPj)
                    for _pass in range(QPASS):
                        # Pair-batched E012 schedule for [Aj, Pj]^T @ Om.
                        fnp.matmul(fnp.swapaxes(join_ap4[:, 0], -1, -2), Om, out=join_inner4[:, 0])
                        fnp.multiply(join_weights4, join_inner4, out=join_inner4)
                        # Single E014 priced change: one level-1 Strassen family.
                        smm.mm(join_ap4, join_inner4, join_outer4, 1)
                        fnp.add(join_outer4[0, 0], join_outer4[1, 0], out=Yq)
                        if ka > 0:
                            # V24: full core of the confined legs = tier-1 core + lifted tier-2 core
                            Sfull = Sg if kb == 0 else Sg + U @ (S2 @ U.T)
                            fnp.matmul(Qp, Sfull @ (Qp.T @ Om), out=Yq2)
                            fnp.add(Yq, Yq2, out=Yq)
'''


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git identity, not security


def patch_joiner_block(source: str) -> str:
    count = source.count(ORIGINAL_JOINER_BLOCK)
    if count != 1:
        raise ValueError(f"expected exactly one frozen V29 joiner block, found {count}")
    return source.replace(ORIGINAL_JOINER_BLOCK, PATCHED_JOINER_BLOCK, 1)


def patch_file(source_path: Path, output_path: Path) -> None:
    raw = source_path.read_bytes()
    actual = git_blob_sha1(raw)
    if actual != EXPECTED_V29_GIT_BLOB:
        raise ValueError(
            f"unexpected V29 git blob: {actual}; expected {EXPECTED_V29_GIT_BLOB}"
        )
    patched = patch_joiner_block(raw.decode("utf-8"))
    output_path.write_text(patched, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    patch_file(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
