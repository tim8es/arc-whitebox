from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any

import torch

from mlp_kprop.diagslice import DSTensor
from mlp_kprop.factor_k3 import FactoredTensor
from mlp_kprop.tensor_utils import symmetrize


def _canonical_columns(q: torch.Tensor) -> torch.Tensor:
    q = q.clone()
    for j in range(q.shape[1]):
        col = q[:, j]
        idx = int(torch.argmax(torch.abs(col)).item())
        if float(col[idx]) < 0.0:
            q[:, j].neg_()
    return q


def _canonical_qr(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    q, r = torch.linalg.qr(x, mode="reduced")
    for j in range(q.shape[1]):
        idx = int(torch.argmax(torch.abs(q[:, j])).item())
        if float(q[idx, j]) < 0.0:
            q[:, j].neg_()
            r[j, :].neg_()
    return q, r


def _top_left_basis(x: torch.Tensor, rank: int) -> torch.Tensor:
    u, _, _ = torch.linalg.svd(x, full_matrices=False)
    return _canonical_columns(u[:, :rank])


def _matrix_op_bound(w: torch.Tensor) -> float:
    # sqrt(||W||_1 ||W||_inf) is a deterministic O(n^2) upper bound on ||W||_2.
    a = float(torch.max(torch.sum(torch.abs(w), dim=0)).item())
    b = float(torch.max(torch.sum(torch.abs(w), dim=1)).item())
    return math.sqrt(max(a * b, 0.0))


def _tt_norm(g: torch.Tensor) -> float:
    return float(torch.linalg.vector_norm(g).item())


@dataclass
class GSTTAudit:
    identity_middle_checks: int = 0
    identity_middle_failures: int = 0
    projection_losses: list[float] = field(default_factory=list)
    newborn_residual_bounds: list[float] = field(default_factory=list)
    transport_bounds: list[float] = field(default_factory=list)
    wick_bounds: list[float] = field(default_factory=list)
    finalize_calls: int = 0

    @property
    def identity_middle_pass(self) -> bool:
        return self.identity_middle_failures == 0


class GSTTTensor(FactoredTensor):
    """Rank-fixed open-core TT for an ordered K3 seed S with K=Sym(S).

    S_ijk = sum_ab U_ia G_ajb V_kb.  The middle neuron mode stays physical.
    New factored atoms are queued during the nonlinear closure and projected once
    at the layer boundary, so there is exactly one global basis update per layer.
    """

    def __init__(
        self,
        *,
        n: int,
        rank: int,
        u: torch.Tensor | None,
        g: torch.Tensor | None,
        v: torch.Tensor | None,
        certificate: float = 0.0,
        audit: GSTTAudit | None = None,
    ) -> None:
        self.n = int(n)
        self.d = 3
        self.rank = int(rank)
        self._u = u
        self._g = g
        self._v = v
        self.certificate = float(certificate)
        self.audit = copy.deepcopy(audit) if audit is not None else GSTTAudit()
        self._pending: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = []
        if u is not None:
            self.device = u.device
            self.dtype = u.dtype
        elif g is not None:
            self.device = g.device
            self.dtype = g.dtype
        else:
            self.device = torch.device("cpu")
            self.dtype = torch.float64

    @property
    def ndim(self) -> int:
        return 3

    @property
    def shape(self) -> tuple[int, int, int]:
        return (self.n, self.n, self.n)

    @property
    def u(self) -> torch.Tensor:
        assert self._u is not None
        return self._u

    @property
    def g(self) -> torch.Tensor:
        assert self._g is not None
        return self._g

    @property
    def v(self) -> torch.Tensor:
        assert self._v is not None
        return self._v

    @classmethod
    def from_factored(
        cls,
        x: FactoredTensor,
        *,
        rank: int,
        omega: torch.Tensor,
    ) -> "GSTTTensor":
        ret = cls(n=x.n, rank=rank, u=None, g=None, v=None)
        ret.device = x.device
        ret.dtype = x.dtype
        ret.add_factors_(x.factors)
        ret.finalize(omega)
        return ret

    def clone(self) -> "GSTTTensor":
        ret = GSTTTensor(
            n=self.n,
            rank=self.rank,
            u=None if self._u is None else self._u.clone(),
            g=None if self._g is None else self._g.clone(),
            v=None if self._v is None else self._v.clone(),
            certificate=self.certificate,
            audit=self.audit,
        )
        ret.device = self.device
        ret.dtype = self.dtype
        ret._pending = tuple((a.clone(), b.clone(), c.clone()) for a, b, c in self._pending)
        ret._pending = list(ret._pending)
        return ret

    def _orthonormalize_outer(self) -> None:
        if self._u is None:
            return
        qu, ru = _canonical_qr(self._u)
        qv, rv = _canonical_qr(self._v)
        self._g = torch.einsum("ap,pjq,bq->ajb", ru, self._g, rv)
        self._u = qu
        self._v = qv

    def contract_W(self, w: torch.Tensor) -> "GSTTTensor":
        if self._pending:
            raise RuntimeError("GSTT pending births must be finalized before linear transport")
        ret = self.clone()
        if ret._u is None:
            return ret
        op = _matrix_op_bound(w)
        ret.certificate *= op ** 3
        ret.audit.transport_bounds.append(op)
        ret._u = w @ ret._u
        ret._v = w @ ret._v
        ret._g = torch.einsum("jt,atb->ajb", w, ret._g)
        ret._orthonormalize_outer()
        return ret

    def contract_wick_(self, wick: torch.Tensor) -> None:
        if self._pending:
            raise RuntimeError("GSTT pending births before Wick scaling")
        if self._u is None:
            return
        m = float(torch.max(torch.abs(wick)).item())
        self.certificate *= m ** 3
        self.audit.wick_bounds.append(m)
        self._u = wick[:, None] * self._u
        self._v = wick[:, None] * self._v
        self._g = self._g * wick[None, :, None]
        self._orthonormalize_outer()

    def contract_wick(self, wick: torch.Tensor) -> "GSTTTensor":
        ret = self.clone()
        ret.contract_wick_(wick)
        return ret

    def add_factors_(self, factors: tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> None:
        a, b, c = factors
        if not (a.shape[0] == b.shape[0] == c.shape[0] == self.n):
            raise ValueError("GSTT factor width mismatch")
        if not (a.shape[1] == b.shape[1] == c.shape[1]):
            raise ValueError("GSTT factor rank mismatch")
        self.device = a.device
        self.dtype = a.dtype
        self._pending.append((a.clone(), b.clone(), c.clone()))

    def add_factors(self, factors: tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> "GSTTTensor":
        ret = self.clone()
        ret.add_factors_(factors)
        return ret

    def __add__(self, other: Any) -> "GSTTTensor":
        ret = self.clone()
        if isinstance(other, GSTTTensor):
            raise TypeError("GSTT+GSTT is intentionally unsupported in the frozen E148 path")
        if not isinstance(other, FactoredTensor):
            return NotImplemented
        ret.add_factors_(other.factors)
        return ret

    def _current_d3(self) -> torch.Tensor:
        if self._u is None:
            return torch.zeros(self.n, dtype=self.dtype, device=self.device)
        return torch.einsum("ia,aib,ib->i", self._u, self._g, self._v)

    def _current_d21(self) -> torch.Tensor:
        if self._u is None:
            return torch.zeros((self.n, self.n), dtype=self.dtype, device=self.device)
        s_iic = torch.einsum("ia,aib,cb->ic", self._u, self._g, self._v)
        s_ici = torch.einsum("ia,acb,ib->ic", self._u, self._g, self._v)
        s_cii = torch.einsum("ca,aib,ib->ic", self._u, self._g, self._v)
        out = (s_iic + s_ici + s_cii) / 3.0
        out = out.clone()
        out.fill_diagonal_(0.0)
        return out

    def _pending_dslice(self, part: tuple[int, ...]) -> torch.Tensor:
        if len(self._pending) == 0:
            shape = (self.n,) * len(part)
            return torch.zeros(shape, dtype=self.dtype, device=self.device)
        out = None
        for factors in self._pending:
            ft = FactoredTensor(n=self.n, d=3, factors=factors, device=self.device, dtype=self.dtype)
            x = ft.get_dslice(part)
            out = x.clone() if out is None else out + x
        assert out is not None
        return out

    def get_dslice(self, part: tuple[int, ...]) -> torch.Tensor:
        part = tuple(part)
        if part == (3,):
            return self._current_d3() + self._pending_dslice(part)
        if part == (2, 1):
            return self._current_d21() + self._pending_dslice(part)
        if part == (1, 2):
            return (self._current_d21() + self._pending_dslice((2, 1))).T
        raise NotImplementedError(f"GSTT only exposes repeated K3 slices, got {part}")

    def get_repeated(self) -> DSTensor:
        return DSTensor(
            d=3,
            n=self.n,
            slices={(3,): self.get_dslice((3,)), (2, 1): self.get_dslice((2, 1))},
            device=self.device,
            dtype=self.dtype,
        )

    def _identity_blocks(
        self, factors: tuple[torch.Tensor, torch.Tensor, torch.Tensor]
    ) -> list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        a, b, c = factors
        cols = a.shape[1]
        if cols % self.n != 0:
            self.audit.identity_middle_checks += 1
            self.audit.identity_middle_failures += 1
            raise RuntimeError(f"birth rank {cols} is not a multiple of n={self.n}")
        blocks = []
        for lo in range(0, cols, self.n):
            aa = a[:, lo : lo + self.n]
            bb = b[:, lo : lo + self.n]
            cc = c[:, lo : lo + self.n]
            diag = torch.diagonal(bb)
            off = bb - torch.diag(diag)
            den = max(float(torch.linalg.vector_norm(bb).item()), 1e-300)
            ratio = float(torch.linalg.vector_norm(off).item()) / den
            self.audit.identity_middle_checks += 1
            if ratio > 1e-11:
                self.audit.identity_middle_failures += 1
                raise RuntimeError(f"non-identity middle birth block: offdiag ratio={ratio}")
            # Absorb the diagonal middle scaling into the first outer factor.
            blocks.append((aa * diag[None, :], torch.eye(self.n, dtype=bb.dtype, device=bb.device), cc))
        return blocks

    def finalize(self, omega: torch.Tensor) -> None:
        if not self._pending:
            return
        blocks: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = []
        for factors in self._pending:
            blocks.extend(self._identity_blocks(factors))

        us = []
        vs = []
        if self._u is not None:
            us.append(self._u)
            vs.append(self._v)
        for a, _, c in blocks:
            us.append(a @ omega)
            vs.append(c @ omega)

        u_new = _top_left_basis(torch.cat(us, dim=1), self.rank)
        v_new = _top_left_basis(torch.cat(vs, dim=1), self.rank)

        g_new = torch.zeros(
            (self.rank, self.n, self.rank), dtype=self.dtype, device=self.device
        )
        old_projection_loss = 0.0
        if self._u is not None:
            old_norm = _tt_norm(self._g)
            mu = u_new.T @ self._u
            mv = v_new.T @ self._v
            old_kept = torch.einsum("ap,pjq,bq->ajb", mu, self._g, mv)
            kept_norm = _tt_norm(old_kept)
            old_projection_loss = math.sqrt(max(old_norm * old_norm - kept_norm * kept_norm, 0.0))
            g_new.add_(old_kept)

        newborn_bound = 0.0
        for a, b, c in blocks:
            au = u_new.T @ a
            cv = v_new.T @ c
            g_new.add_(torch.einsum("at,jt,bt->ajb", au, b, cv))

            a_proj = u_new @ au
            c_proj = v_new @ cv
            a_perp = a - a_proj
            c_perp = c - c_proj
            for t in range(a.shape[1]):
                bn = float(torch.linalg.vector_norm(b[:, t]).item())
                newborn_bound += (
                    float(torch.linalg.vector_norm(a_perp[:, t]).item())
                    * bn
                    * float(torch.linalg.vector_norm(c[:, t]).item())
                )
                newborn_bound += (
                    float(torch.linalg.vector_norm(a_proj[:, t]).item())
                    * bn
                    * float(torch.linalg.vector_norm(c_perp[:, t]).item())
                )

        self.certificate += old_projection_loss + newborn_bound
        self.audit.projection_losses.append(old_projection_loss)
        self.audit.newborn_residual_bounds.append(newborn_bound)
        self.audit.finalize_calls += 1
        self._u = u_new
        self._v = v_new
        self._g = g_new
        self._pending.clear()

    def ordered_seed(self) -> torch.Tensor:
        if self._pending:
            raise RuntimeError("cannot materialize GSTT with pending births")
        if self._u is None:
            return torch.zeros(
                (self.n, self.n, self.n), dtype=self.dtype, device=self.device
            )
        return torch.einsum("ia,ajb,kb->ijk", self._u, self._g, self._v)

    def to_tensor(self) -> torch.Tensor:
        return symmetrize(self.ordered_seed())


def production_cost_receipt(rank: int = 40) -> dict[str, int | float]:
    n = 1024
    transitions = 15
    budget = 2**41
    unit = 2 * n**3
    retained = 38 * unit
    transport = transitions * (2 * n * n * rank * rank + 4 * n * n * rank + 4 * n * rank**3)
    readout = transitions * (2 * n * n * rank * rank + 4 * n * n * rank + 4 * n * rank * rank)
    birth = transitions * (4 * n * n * rank + 2 * n * rank * rank)
    basis = transitions * (4 * n * n * rank + 8 * n * rank * rank + 8 * n * rank**3)
    certificate = 12 * unit
    helpers = 12 * unit
    total = retained + transport + readout + birth + basis + certificate + helpers
    cap = math.floor(0.135 * budget)
    return {
        "rank": rank,
        "budget_flops": budget,
        "cap_flops": cap,
        "retained_low_order": retained,
        "open_core_transport": transport,
        "d21_d3_readout": readout,
        "newborn_projection_insertion": birth,
        "deterministic_basis_update": basis,
        "certificate_reserve": certificate,
        "helper_materialization_reserve": helpers,
        "all_in_upper": total,
        "utilization": total / budget,
        "slack_to_cap": cap - total,
    }
