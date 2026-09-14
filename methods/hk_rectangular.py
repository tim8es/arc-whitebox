from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import flopscope.numpy as fnp


@dataclass(frozen=True)
class SparseColumn:
    indices: tuple[int, ...]
    coeffs: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.indices) != len(self.coeffs):
            raise ValueError("indices/coeffs length mismatch")
        if not self.indices:
            raise ValueError("empty sparse column")
        if any(c not in (-1, 1) for c in self.coeffs):
            raise ValueError("E011 prototype supports only +/-1 HK coefficients")


@dataclass(frozen=True)
class SparseBilinearScheme:
    n: int
    m: int
    p: int
    rank: int
    u: tuple[SparseColumn, ...]
    v: tuple[SparseColumn, ...]
    w: tuple[SparseColumn, ...]

    @classmethod
    def from_catalog_json(cls, data: dict) -> "SparseBilinearScheme":
        n, m, p = (int(x) for x in data["n"])
        rank = int(data["m"])

        def parse(name: str, *, w_col_major: bool = False) -> tuple[SparseColumn, ...]:
            raw = data[name]
            cols = []
            for r in range(rank):
                col = raw[str(r)]
                positions = tuple(int(i) for i in col["i"])
                if w_col_major:
                    positions = tuple((pos % n) * p + (pos // n) for pos in positions)
                cols.append(SparseColumn(positions, tuple(int(c) for c in col["c"])))
            return tuple(cols)

        return cls(
            n,
            m,
            p,
            rank,
            parse("u_sparse"),
            parse("v_sparse"),
            parse("w_sparse", w_col_major=True),
        )

    def cyclic_shift(self) -> "SparseBilinearScheme":
        """Return the exact <m,p,n> cyclic orientation used by matmulcatalog."""

        def remap(col: SparseColumn, fn) -> SparseColumn:
            return SparseColumn(tuple(fn(i) for i in col.indices), col.coeffs)

        new_u = self.v
        new_v = tuple(
            remap(col, lambda old: (old % self.p) * self.n + (old // self.p))
            for col in self.w
        )
        new_w = tuple(
            remap(col, lambda old: (old % self.m) * self.n + (old // self.m))
            for col in self.u
        )
        return SparseBilinearScheme(
            self.m,
            self.p,
            self.n,
            self.rank,
            new_u,
            new_v,
            new_w,
        )

    def orient_16_2_16(self) -> "SparseBilinearScheme":
        out = self.cyclic_shift().cyclic_shift()
        if (out.n, out.m, out.p, out.rank) != (16, 2, 16, 392):
            raise ValueError(f"unexpected oriented HK shape {(out.n, out.m, out.p, out.rank)}")
        return out


def dense_matmul_flops(m: int, k: int, n: int) -> int:
    return m * n * (2 * k - 1)


def terminal_old_tier_shapes() -> tuple[tuple[int, int, int], ...]:
    return (
        (128, 48, 128),
        (128, 128, 48),
        (256, 56, 256),
        (256, 256, 56),
    )


def _blocked_2d(x, rows: int, cols: int, block: int):
    if x.shape != (rows * block, cols * block):
        raise ValueError(f"expected {(rows * block, cols * block)}, got {x.shape}")
    return fnp.swapaxes(fnp.reshape(x, (rows, block, cols, block)), 1, 2)


def _unblock_2d(x, block: int):
    rows, cols = x.shape[:2]
    return fnp.reshape(fnp.swapaxes(x, 1, 2), (rows * block, cols * block))


def _write_linear_form(dst, flat_blocks, col: SparseColumn) -> None:
    idx = col.indices
    coeff = col.coeffs
    if len(idx) == 1:
        fnp.multiply(flat_blocks[idx[0]], float(coeff[0]), out=dst)
        return

    a = flat_blocks[idx[0]]
    b = flat_blocks[idx[1]]
    c0, c1 = coeff[0], coeff[1]
    if c0 == 1 and c1 == 1:
        fnp.add(a, b, out=dst)
    elif c0 == 1 and c1 == -1:
        fnp.subtract(a, b, out=dst)
    elif c0 == -1 and c1 == 1:
        fnp.subtract(b, a, out=dst)
    else:
        fnp.add(a, b, out=dst)
        fnp.negative(dst, out=dst)

    for source, sign in zip(idx[2:], coeff[2:], strict=True):
        if sign == 1:
            fnp.add(dst, flat_blocks[source], out=dst)
        else:
            fnp.subtract(dst, flat_blocks[source], out=dst)


def _decode_chunk(
    out_blocks,
    products,
    w_cols: Iterable[SparseColumn],
    initialized: list[bool],
) -> None:
    for local_r, col in enumerate(w_cols):
        product = products[local_r]
        for output_index, sign in zip(col.indices, col.coeffs, strict=True):
            if not initialized[output_index]:
                fnp.multiply(product, float(sign), out=out_blocks[output_index])
                initialized[output_index] = True
            elif sign == 1:
                fnp.add(out_blocks[output_index], product, out=out_blocks[output_index])
            else:
                fnp.subtract(out_blocks[output_index], product, out=out_blocks[output_index])


def hk_pair_16_2_16(
    a_pair,
    b_pair,
    scheme: SparseBilinearScheme,
    *,
    block: int = 8,
    rank_chunk: int = 64,
):
    if (scheme.n, scheme.m, scheme.p) != (16, 2, 16):
        raise ValueError("scheme must be oriented as <16,2,16>")
    if scheme.rank != 392:
        raise ValueError("E011 prototype is pinned to rank 392")
    if rank_chunk <= 0:
        raise ValueError("rank_chunk must be positive")

    a_blocks = _blocked_2d(a_pair, 16, 2, block)
    b_blocks = _blocked_2d(b_pair, 2, 16, block)
    a_flat = fnp.reshape(a_blocks, (32, block, block))
    b_flat = fnp.reshape(b_blocks, (32, block, block))
    out_blocks = fnp.empty((256, block, block), dtype=a_pair.dtype)
    initialized = [False] * 256

    lbuf = fnp.empty((rank_chunk, block, block), dtype=a_pair.dtype)
    rbuf = fnp.empty((rank_chunk, block, block), dtype=a_pair.dtype)
    mbuf = fnp.empty((rank_chunk, block, block), dtype=a_pair.dtype)

    for start in range(0, scheme.rank, rank_chunk):
        stop = min(start + rank_chunk, scheme.rank)
        width = stop - start
        for local, rank in enumerate(range(start, stop)):
            _write_linear_form(lbuf[local], a_flat, scheme.u[rank])
            _write_linear_form(rbuf[local], b_flat, scheme.v[rank])
        fnp.matmul(lbuf[:width], rbuf[:width], out=mbuf[:width])
        _decode_chunk(out_blocks, mbuf[:width], scheme.w[start:stop], initialized)

    if not all(initialized):
        raise RuntimeError("HK decode left at least one output block unwritten")
    out4 = fnp.reshape(out_blocks, (16, 16, block, block))
    return _unblock_2d(out4, block)


def hk_leaf_128x48_128(
    a,
    b,
    scheme: SparseBilinearScheme,
    *,
    block: int = 8,
    rank_chunk: int = 64,
):
    if a.shape != (128, 48) or b.shape != (48, 128):
        raise ValueError("E011 tier-1 forming leaf requires (128,48) @ (48,128)")
    out = fnp.empty((128, 128), dtype=a.dtype)
    for pair in range(3):
        lo = pair * 16
        hi = lo + 16
        partial = hk_pair_16_2_16(
            a[:, lo:hi],
            b[lo:hi, :],
            scheme,
            block=block,
            rank_chunk=rank_chunk,
        )
        if pair == 0:
            fnp.multiply(partial, 1.0, out=out)
        else:
            fnp.add(out, partial, out=out)
    return out


def direct_sparse_nonproduct_flops(
    scheme: SparseBilinearScheme,
    *,
    block: int = 8,
    pairs: int = 3,
) -> int:
    """FLOPs of this direct sparse encode/decode schedule, excluding rank matmuls."""
    cells = block * block

    def encode_ops(cols: tuple[SparseColumn, ...]) -> int:
        total = 0
        for col in cols:
            support = len(col.indices)
            if support == 1:
                total += 1
            else:
                total += support - 1
                if col.coeffs[0] == -1 and col.coeffs[1] == -1:
                    total += 1
        return total

    per_pair = encode_ops(scheme.u) + encode_ops(scheme.v)
    per_pair += sum(len(col.indices) for col in scheme.w)
    per_pair += 256
    return pairs * per_pair * cells
