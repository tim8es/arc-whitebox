#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, sys
from pathlib import Path
import numpy as np

PARENT_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"

OLD = """            Om = fnp.copy(w32[:, :r])  # V20: contiguous sketch
            Y = Rres @ Om
            Q, _ = fnp.linalg.qr(Y)
            Y = Rres @ (Rres.T @ Q)
            Q, _ = fnp.linalg.qr(Y)
            Bm = Q.T @ Rres                      # Rres ~= Q @ Bm
            # M_b = diag(S3c) + 3 S21^T = diag(S3c) + 3 a_b diag(e_b) + 3 Rr Lr^T
            # with Rr = Bm^T (n,r) [transported as Z = P Rr] and Lr = Q (static).
            # extra thin columns: M_t1 = u v^T -> Z column P u, L column v; and the Y3
            # row vector y is a LEFT factor of the hub tensor, so it is transported
            # like a leg (y(l) = P(l) y): Z column P y with a ZERO L column (keeps it
            # out of the M leg). Zeros off-suite / at layer 0 so every source keeps
            # r+2 columns.
            Rr_full = fnp.concatenate([Bm.T * 3.0, fnp.reshape(u_b, (-1, 1)),
                                       fnp.reshape(y_b, (-1, 1))], axis=1)
            Lr_full = fnp.concatenate([Q, fnp.reshape(w1sq, (-1, 1)),
                                       fnp.zeros((n, 1), dtype=f32)], axis=1)
"""

NEW = """            # R244 MP-R16: reserve two of the unchanged R_RES=16 columns for the
            # exact all-ones row/column marginals of Rres, then compress only the
            # doubly-centered remainder with the existing one-power range finder.
            rb = r - 2
            u0 = ones_n * (1.0 / math.sqrt(float(n)))
            a0 = Rres @ u0
            b0 = Rres.T @ u0
            c0 = fnp.sum(u0 * a0)
            ac0 = a0 - u0 * c0
            M0 = (fnp.reshape(u0, (-1, 1)) * fnp.reshape(b0, (1, -1))
                  + fnp.reshape(ac0, (-1, 1)) * fnp.reshape(u0, (1, -1)))
            Eres = Rres - M0
            Om = fnp.copy(w32[:, :rb])  # same deterministic sketch family, rank 14 bulk
            Y = Eres @ Om
            Q, _ = fnp.linalg.qr(Y)
            Y = Eres @ (Eres.T @ Q)
            Q, _ = fnp.linalg.qr(Y)
            Bm = Q.T @ Eres                      # centered bulk Eres ~= Q @ Bm
            # Rres^T ~= Bm^T Q^T + b0 u0^T + u0 ac0^T, exactly preserving
            # Rres*u0 and Rres^T*u0 while keeping total residual rank r == 16.
            Rr_res = fnp.concatenate([Bm.T, fnp.reshape(b0, (-1, 1)),
                                       fnp.reshape(u0, (-1, 1))], axis=1) * 3.0
            Lr_res = fnp.concatenate([Q, fnp.reshape(u0, (-1, 1)),
                                       fnp.reshape(ac0, (-1, 1))], axis=1)
            # Existing two V17 feed columns remain appended after the r residual columns.
            Rr_full = fnp.concatenate([Rr_res, fnp.reshape(u_b, (-1, 1)),
                                       fnp.reshape(y_b, (-1, 1))], axis=1)
            Lr_full = fnp.concatenate([Lr_res, fnp.reshape(w1sq, (-1, 1)),
                                       fnp.zeros((n, 1), dtype=f32)], axis=1)
"""

def decompose(A, total_rank):
    n=A.shape[0]
    u=np.ones(n,dtype=np.float64)/math.sqrt(n)
    a=A@u; b=A.T@u; c=float(u@a); ac=a-c*u
    M=np.outer(u,b)+np.outer(ac,u)
    E=A-M
    k=total_rank-2
    U,s,Vt=np.linalg.svd(E,full_matrices=False)
    Q=U[:,:k]; B=Q.T@E
    approx_t=np.column_stack([B.T,b,u]) @ np.column_stack([Q,u,ac]).T
    return u,E,approx_t.T

def main():
    parent=Path(sys.argv[1]).read_text()
    cand=Path(sys.argv[2]).read_text()
    transformed=parent.replace(OLD,NEW)
    source_guard=(parent.count(OLD)==1 and transformed==cand and "R_RES = 16" in cand)

    rng=np.random.default_rng(244)
    n=12; total_rank=6; u=np.ones(n)/math.sqrt(n)
    # Exact-rank centered bulk plus arbitrary marginal component.
    X=rng.normal(size=(n,total_rank-2)); Y=rng.normal(size=(n,total_rank-2))
    P=np.eye(n)-np.outer(u,u)
    bulk=(P@X)@(P@Y).T
    a=rng.normal(size=n); b=rng.normal(size=n)
    # Construct a marginal component in the same canonical form.
    c=float(u@a); A=bulk+np.outer(u,b)+np.outer(a-c*u,u)
    uu,E,Ah=decompose(A,total_rank)
    exact_center=max(float(np.max(np.abs(E@uu))),float(np.max(np.abs(E.T@uu))))
    exact_recon=float(np.max(np.abs(Ah-A)))
    exact_marg=max(float(np.max(np.abs((Ah-A)@uu))),float(np.max(np.abs((Ah-A).T@uu))))

    A2=rng.normal(size=(n,n))
    uu2,E2,A2h=decompose(A2,total_rank)
    full_marg=max(float(np.max(np.abs((A2h-A2)@uu2))),float(np.max(np.abs((A2h-A2).T@uu2))))
    finite=bool(np.isfinite(A2h).all())

    gates={
      "centered_remainder_annihilates_u": exact_center<=1e-12,
      "exact_rank_reconstruction": exact_recon<=1e-11,
      "exact_rank_marginals": exact_marg<=1e-11,
      "full_rank_marginals": full_marg<=1e-10,
      "full_rank_finite": finite,
      "source_exact_single_block_transform_and_rres16": source_guard,
    }
    out={
      "schema":"arc.whitebox.r244.mp_r16_falsifier.v1",
      "seed":244,"n":n,"total_rank":total_rank,"bulk_rank":total_rank-2,
      "metrics":{"exact_center_max":exact_center,"exact_reconstruction_max":exact_recon,
                 "exact_marginal_max":exact_marg,"full_rank_marginal_max":full_marg},
      "gates":gates,"go":all(gates.values()),
      "parent_sha256":hashlib.sha256(parent.encode()).hexdigest(),
      "candidate_sha256":hashlib.sha256(cand.encode()).hexdigest(),
    }
    Path(sys.argv[3]).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    raise SystemExit(0 if out["go"] else 2)

if __name__=="__main__": main()
