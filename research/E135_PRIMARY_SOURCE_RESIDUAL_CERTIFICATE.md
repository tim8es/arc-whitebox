# E135 — primary-source study of observable residual certificates

Status: **TERMINAL THEORY NO-GO for Parseval / transported-residual-norm certificates on arbitrary dense weights**

Date: 2026-09-21

This note is a theory/background-research lane. It does **not** execute public,
scorer, holdout, full-suite, or production-shaped benchmark inference.

## Question

Can the unusably loose E132 global Gaussian-Poincare certificate be replaced by
a tight, target-free certificate built from quantities already observable inside
a source-compressed K=3 estimator:

1. an orthogonal/Parseval source decomposition;
2. the norm of the omitted source residual;
3. a transported residual norm;
4. a deterministic truncation bound to the final mean;

without using an exact reference or post-hoc target error?

The desired final RMS scale is

[
epsilon_* = sqrt{1.89	imes 10^{-8}}
            = 1.374772708486752	imes 10^{-4}.
]

The conclusion below is deliberately narrow:

> A certificate whose retained information about the omitted source state is
> only an orthogonal residual norm (scalar or per-block norm), followed by
> deterministic transport/operator bounds, cannot be tight for arbitrary dense
> weights. Making the certificate orientation-aware enough to avoid that
> worst-case bound requires carrying essentially the omitted directional state
> or its action on downstream sensitivities, which reintroduces the old-source
> work this compression was meant to remove.

This does **not** claim that every possible target-free certificate is
impossible. An orientation-aware certificate with a genuinely cheaper exact
state representation would be a new mechanism and needs a new experiment ID.

---

## Primary sources

### Official ARC / challenge sources

1. ARC challenge announcement:
   https://www.alignment.org/blog/announcing-the-arc-white-box-estimation-challenge/

   ARC defines the task as estimating the expected output of random ReLU MLPs
   from weights under a computational budget, and explicitly frames the goal as
   improving mechanistic estimation rather than relying only on sampling.

2. ARC "Competing with sampling":
   https://www.alignment.org/blog/competing-with-sampling/

   This is ARC's public explanation of the matching-sampling agenda and
   cumulant propagation. It describes layerwise propagation of increasingly
   complete cumulant information as an approximation strategy; it does not
   provide a per-instance, depth-uniform deterministic truncation certificate
   for the Phase-2 source-compressed regime.

3. ARC paper:
   https://arxiv.org/abs/2605.05179

   Wilson Wu, Victor Lecomte, Michael Winer, George Robinson, Jacob Hilton,
   Paul Christiano, *Estimating the expected output of wide random MLPs more
   efficiently than sampling*.

4. ARC reference implementation:
   https://github.com/alignment-research-center/mlp_cumulant_propagation

   The public implementation contains the factorized K=3 machinery and the
   diagonal-slice / harmonic representations used by later competition work.

5. Official challenge starter kit:
   https://github.com/AIcrowd/whest-starterkit

   For Phase 2 the suite shape is width 1024, depth 16, with a per-MLP budget
   of (2^{41}) FLOPs. The project target used here requires complete
   utilization <= 0.135.

### 504aldo primary sources

6. Pinned MIT repository:
   https://github.com/504aldo/whest-p2-cumulant-k3/tree/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45

7. Published competition write-up:
   https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

8. Pinned raw findings log:
   https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/findings_log.md

9. Pinned V25 implementation:
   https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v25.py

10. Pinned findings index:
    https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/findings_index.md

Relevant measured findings in the upstream log:

- **F65**: collapsing older K3 content to the live D3/D21 slice state leaves a
  high-rank D21 residual carrying about 18-23% of the energy at every layer;
  fitted local corrections barely change the result.
- **F66**: transported source legs show strong energy concentration, but the
  source explicitly warns that energy is a misleading guide because the
  accuracy-relevant content sits in the small remainder. Rank reduction below
  the measured cliff sharply increases raw error.
- **F72/F73**: age-gated shared/nested bases work only at fairly large ranks
  (roughly 3n/8 at age 4 and about 7n/32 at age 7); lowering rank one notch
  produces an accuracy cliff.
- **F88**: the public chain's old-tier compression doors are closed by measured
  rank laws and arithmetic. The write-up also notes that a backward/adjoint
  sensitivity route still needs per-source transported state and dense
  contractions and does not remove nonlinear feedback.

E136 independently reproduced the public V25/V29 code path in this repository:

- branch: `research/e136-public-k3-reproduction`
- note: `research/E136_PUBLIC_K3_REPRODUCTION.md`
- receipt: `research/E136_REPRODUCTION_RECEIPT.json`

The reproduction found equal reported raw on the same 3 public mini MLPs
((2.33	imes10^{-8})) while V25 and V29 followed the published cost path.

---

## Candidate certificate

Let an exact source state at some compression point be (S) in a Hilbert
space with Frobenius inner product, and let (Q) have orthonormal columns.
Write

[
P = QQ^	op,qquad
S = PS + R,qquad
R=(I-P)S.
]

Parseval/Pythagoras gives the exact, target-free observable identity

[
oxed{
|S|_F^2 = |PS|_F^2 + |R|_F^2
}
]

and therefore

[
ho := |R|_F
]

is an exact truncation residual norm at the projection point.

For a purely linear later transport (T),

[
|TR|_F le |T|_2,ho.
]

For several transports (T_k),

[
|T_mcdots T_1R|_F
le
left(prod_k |T_k|_2ight)ho.
]

At first sight this appears to avoid E132's global input-space
Gaussian-Poincare bound because it starts from the **observed actual
truncation residual**, not from a global Lipschitz constant.

The problem is that the residual norm alone discards the directional
information that determines its coupling to the downstream D21 contractions.

---

## Lemma: norm-only deterministic certificate has an unavoidable orientation bound

Let (mathcal H_perp) be the omitted orthogonal subspace and let a downstream
linear sensitivity on that residual be (ainmathcal H_perp). Suppose a
certificate knows

[
|r|_2=ho
]

but not the direction of (r) inside (mathcal H_perp). The final scalar
error contribution is

[
e=a^	op r.
]

Then

[
|e| le ho|a|_2,
]

and this bound is **best possible**: choose
(r=ho a/|a|_2).

The same residual norm is also compatible with any vector orthogonal to (a),
for which the error is zero.

Therefore no deterministic certificate that retains only (ho) can
distinguish a zero-error omitted residual from the worst-aligned residual.
For arbitrary dense downstream weights, the worst alignment is an admissible
network state.

If the omitted subspace itself is known, the sharp norm-only bound becomes

[
|e|le ho,|P_perp a|_2,
]

and is again attained by alignment with (P_perp a).

This is not looseness introduced by a proof technique. It is an information
loss caused by replacing the residual vector/tensor by its norm.

---

## Extension to K3 / D21 source contractions

The public K3 implementation does not map omitted source content to the final
mean by a single fixed linear operator. The D21 machinery contains Hadamard
products and dense contractions of transported source legs. In V25 the
documented slice expression includes terms of the form

[
(Aodot Podot w),A^	op,qquad
(Aodot Aodot w),P^	op,
]

plus terms involving the transported (M) leg.

For a retained-plus-residual split

[
A=A_Q+A_R,qquad P=P_Q+P_R,
]

the exact contraction difference contains first- and higher-order residual
terms such as

[
A_Rodot P_Q,quad
A_Qodot P_R,quad
A_Rodot P_R.
]

A scalar Parseval norm gives no information about coordinatewise alignment of
these residuals with (w), (A_Q), (P_Q), or the final sensitivity.

A deterministic norm certificate therefore falls back to Hölder/operator-norm
bounds. The orientation lemma applies to each linearized residual term, while
the bilinear residual terms require products of such worst-case norms.

This is exactly the failure mode suggested by upstream F66:

> high retained energy is not a guarantee of accuracy because the
> accuracy-relevant content can live in the small residual.

The public rank cliff in F72/F73 is the empirical manifestation of the same
issue.

---

## Why "transport the residual norm exactly" does not fix the information loss

There are two possible interpretations.

### A. Transport only a scalar/block residual norm

For a dense linear map (T), a scalar norm must use

[
ho' le |T|_2ho
]

unless additional directional information is retained.

Repeated through dense layers, this becomes another product-of-gains bound.
It is more localized than E132's input-space Poincare certificate, but for
arbitrary dense weights the inequality is still sharp in the worst case.

The ReLU/D21 Hadamard structure introduces additional worst-case factors rather
than canceling them.

**Verdict: mathematically valid, not tight in the required arbitrary-dense
sense.**

### B. Transport enough orientation to compute the exact residual norm after each map

For a residual matrix (R),

[
|TR|_F^2
=
operatorname{tr}(R^	op T^	op T R).
]

Computing this tightly requires either:

- the omitted residual factors themselves; or
- an equivalent directional Gram/covariance state that preserves their action
  under (T^	op T).

Once the downstream contraction contains Hadamard products, a single residual
Gram is not closed: coordinatewise products require additional directional
cross-state. This is the same structural reason the published implementation
re-forms dense legs before D21 contraction.

Thus the tight version ceases to be a "residual norm certificate" and becomes
a second transported source representation for the omitted state.

**Verdict: potentially tight, but it reintroduces the state/computation being
certified away.**

---

## Production-cost consequence from primary evidence

The 504aldo forum write-up gives a decisive budget fact for the published K3
family:

- total V29 bill: about 260 units / (0.254B);
- old-source tier: about 107 units;
- bill **without the old tier**: about 153 units = **0.150B**.

The E135 project cap is

[
0.135B.
]

Therefore, for the published V29 source machinery,

[
oxed{
0.150B > 0.135B
}
]

**before paying one FLOP for an old-source residual certificate**.

So even a zero-cost perfect certificate cannot make the public V29
young-source backbone fit the E135 production cap.

E136's measured reproduction is consistent with the public cost anatomy:

- V25 mean (C/B) from the rounded three-MLP report:
  (0.36683);
- V29 three-MLP mean:
  (0.25769), with the first-predict warm-up included.

This cost result is independent of certificate tightness.

---

## Relation to E132

Internal E132 already established that a fully global weight-only
Gaussian-Poincare/Minkowski certificate is useless: the worst frozen
certificate MSE exceeded the raw target by more than (10^{13}).

E135 asked whether using the **observable truncation residual itself** avoids
that failure.

It avoids one source of looseness — the initial residual magnitude is exact —
but not the dominant orientation problem:

[
	ext{exact residual magnitude}

otRightarrow
	ext{tight downstream deterministic error}.
]

For arbitrary dense weights, either:

1. discard residual orientation and accept the sharp worst-case operator bound;
   or
2. retain residual orientation/cross-state and pay source-like transport and
   Hadamard-contraction costs.

The first branch is not tight; the second is not the requested cheap
certificate.

---

## E135 decision

### Terminal theory NO-GO

For the requested certificate family:

> **orthogonal/Parseval source decomposition + observable residual norm +
> transported norm + deterministic truncation bound**

the lane is closed.

Reason:

1. Parseval gives an exact residual magnitude but no accuracy-sensitive
   orientation.
2. For arbitrary dense weights, the sharp deterministic norm-only bound is a
   worst-alignment operator bound; no proof trick can make it smaller without
   retaining more information.
3. The public K3 D21 map is Hadamard/bilinear, so the omitted orientation and
   cross-state matter directly.
4. Primary-source measurements F65/F66/F72/F73 show exactly this pathology:
   high energy capture can coexist with large accuracy loss and a sharp rank
   cliff.
5. Carrying enough residual directional state to make the bound tight
   reconstructs a substantial part of the omitted source representation.
6. On the published 504aldo family, the source machinery **without** the old
   tier is already (0.150B>0.135B), so a certificate add-on cannot satisfy
   the project production cap anyway.

### What is *not* closed

A future mechanism may still be admissible if it has a new exact identity that
maps omitted source content to a much smaller **orientation-aware sufficient
statistic** closed under the D21 Hadamard contractions.

That is not a residual-norm certificate and should not be named E135 rescue.

---

## Scope / firewall

- no exact reference used;
- no benchmark target read;
- no public/public-mini execution;
- no official scorer;
- no holdout/full;
- no production execution;
- no fitted threshold or post-hoc target error;
- no canonical or ledger mutation.

This note uses public primary-source measurements only for mechanism/cost
evidence and the already committed internal E132/E136 receipts for local
context.
