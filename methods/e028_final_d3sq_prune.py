from __future__ import annotations

_TARGET = "            pk1v, pk2v, pk3v, pk4v = PK1[0], PK1[1], PK1[2], PK1[3]\n"
_INSERT = (
    _TARGET
    + "            if last and mode == 1:\n"
    + "                pk1v = pk1v - (D3 * D3) * (WT[18] * (1.0 / 72.0))\n"
)


def patch_v25_source(source: str) -> str:
    count = source.count(_TARGET)
    if count != 1:
        raise RuntimeError(f"E028 V25 patch target count={count}, expected 1")
    return source.replace(_TARGET, _INSERT, 1)
