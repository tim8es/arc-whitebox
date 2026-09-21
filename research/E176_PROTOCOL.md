# E176 OWNER PROTOCOL — clean-room AGO gauge transfer to public gain-only covariance closure

Date: 2026-09-21  
Idempotency: `ARC-E176-CLEANROOM-AGO-GAIN-MINI-20260921`  
Status: **FROZEN BEFORE IMPLEMENTATION / EXACTLY ONE TARGET-FREE LOCAL-MINI RUN**

Branch:
`research/e176-cleanroom-ago-gain-mini-20260921`.

Scientific parent:
`review/e172-e171-independent-verifier-20260921`.

E175 is explicitly excluded from ancestry, implementation imports, run evidence, and
scientific reuse. E175 remains terminal due its frozen hash guard and is not rescued.

## 1. Primary sources

### Official public gain-only covariance closure

Repository:
`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`.

File:
`examples/03_covariance_propagation.py`.

Pinned blob:
`675b3dd8f032f342112a99f431115b35f8481620`.

The parent update is reconstructed clean-room:

[
mu^- = Wmu,qquad C^- = WCW^T,
]

[
v=max(operatorname{diag}C^-,10^{-12}),quad
sigma=sqrt v,quad alpha=mu^-/sigma,
]

[
mu^+=mu^-Phi(alpha)+sigmaphi(alpha),
]

[
v^+=(mu^{-2}+v)Phi(alpha)+mu^-sigmaphi(alpha)-mu^{+2},
]

and for off-diagonal entries

[
C^+_{ij}=Phi_iPhi_j C^-_{ij}.
]

No (C_{ij}^2) second-order Wick term is allowed.

The official source records measured competition-shape cost
`51,709,240,799 FLOPs` for width 1024, depth 16.

### Verified AGO identity source

E171/E172 retain the independently verified gauge:

[
a_1(n)=
sqrt{rac{2}{n}},
rac{Gamma((n+1)/2)}{Gamma(n/2)},
]

[
mu_A=mu_G/a_1,
]

[
C_A=C_G-left(a_1^{-2}-1ight)mu_Gmu_G^T.
]

For homogeneous zero-bias ReLU networks, Gaussian readout is recovered by
multiplying angular means by (a_1).

E176 may use this identity and E172's verification conclusion, but it must implement
the transfer independently and must not import E175 code.

## 2. Exactly one hypothesis

**H176 / AGO-GAIN-MINI**

Apply the exact AGO gauge once, immediately after the first ReLU state of the clean-room
official gain-only covariance parent. Continue all later layers with the same gain-only
closure, interpreted on the angular state. Convert recorded/final means back to Gaussian
coordinates by multiplication with (a_1(n)).

No other arithmetic change is permitted.

Specifically forbidden:

- E175 code/imports/artifacts;
- second-order Wick covariance term;
- K3/K4/V29 mechanism;
- coefficient fitting;
- layer selection;
- multiple gauges;
- particle correction;
- rank/source changes;
- seed/sample sweep;
- post-result tuning.

## 3. Frozen target-free local-mini falsifier

One synthetic fixture only:

- width `n=256`;
- depth `8`;
- zero bias;
- He-Gaussian weights;
- NumPy PCG64 weight seed `1760256`;
- float64 research arithmetic.

Reference:

- 65,536 angular samples on sphere radius (sqrt{256});
- antithetic pairs;
- 16 batches of 4096;
- NumPy PCG64 reference seed `17665536`;
- exact chi-radial factor (a_1(256)) converts angular batch/final means to Gaussian means.

This is a synthetic local mini. It does not load the public dataset, any baked target,
scorer, holdout, full split, leaderboard, or submission endpoint.

## 4. Mandatory candidate-before-reference ordering

1. Generate and hash frozen weights.
2. Run parent.
3. Run candidate.
4. Replay parent and candidate.
5. Freeze parent/candidate vectors, hashes, gauge diagnostics, and FLOP ledgers.
6. Only then import the reference-only module.
7. Stream the frozen angular reference.
8. Save immutable reference/batch/error/SE vectors and manifest.
9. Compute final gates and write result.

The candidate module must not import the reference module.

## 5. Immutable evidence

Retain and hash at minimum:

- weights summary/hash;
- parent all-layer mean prediction;
- candidate all-layer mean prediction;
- parent final mean;
- candidate final mean;
- reference final mean;
- 16 reference batch final means;
- parent final error and squared error;
- candidate final error and squared error;
- per-coordinate reference SE;
- per-batch parent MSE;
- per-batch candidate MSE;
- per-batch parent-minus-candidate delta;
- manifest with dtype, shape, nbytes, file SHA256 and raw-array SHA256.

Replay must be bitwise exact for both deterministic estimators.

## 6. Frozen scientific gates

All gates are mandatory.

1. Clean source firewall: no E175 import and no public target/scorer/holdout/full/submission access.
2. Parent source audit: gain-only off-diagonal formula and no second-order Wick term.
3. Gauge roundtrip max relative error <= `2e-12`.
4. Parent replay bitwise exact.
5. Candidate replay bitwise exact.
6. All retained arrays finite.
7. Reference final mean equals the mean of the 16 batch means to <= `2e-12` max absolute.
8. RMS reference coordinate SE <= `1.5e-3`.
9. Candidate final MSE < parent final MSE.
10. Strong transfer: `candidate_MSE / parent_MSE <= 0.98`.
11. Mean paired batch delta (MSE_b(parent)-MSE_b(candidate)) > 0.
12. Paired batch delta mean > `2 * SE(delta)`.
13. At least 11/16 reference batches favor candidate.
14. Production all-in candidate cost upper <= `0.135 B`.
15. Exactly one external scientific workflow run; no rescue/rerun/sweep.

Any failure is **E176 SCIENTIFIC NO-GO**. A noisy reference is a failure and does not
authorize more samples.

## 7. Frozen FLOP envelopes

Competition budget:

[
B=2^{41}=2,199,023,255,552.
]

### Production target shape 1024x16

Official measured parent:

[
C_P=51,709,240,799.
]

AGO gauge/readout arithmetic upper:

[
C_G=9n^2+Ln
=9,453,568
quad(n=1024,L=16).
]

Independent integration/accounting reserve:

[
C_R=64,000,000.
]

Candidate production upper:

[
C_C^{upper}
=51,782,694,367
<0.135B.
]

The reserve is deliberately larger than the gauge delta; it is not a tuning parameter.

### Local-mini research arithmetic upper

For the clean-room NumPy parent, conservatively charge per layer

[
4n^3+16n^2+64n.
]

At (n=256,L=8):

[
C_{P,mini}^{upper}=545,390,592.
]

Candidate adds (9n^2+Ln=591,872):

[
C_{C,mini}^{upper}=545,982,464.
]

Reference-only research propagation upper:

[
2N L n^2
=68,719,476,736
]

for (N=65,536). Reference cost is evidence-generation cost, not estimator production cost.

## 8. Decision

All mandatory gates pass:

**E176 TARGET-FREE LOCAL-MINI SCIENTIFIC GO — AGO gauge transfers to the public gain-only covariance closure.**

Any mandatory gate fails:

**E176 SCIENTIFIC NO-GO — AGO gauge does not pass the frozen gain-only local-mini falsifier.**

A GO does not authorize public-mini, leaderboard, scorer, holdout, full, or submission.
Canonical baseline and canonical ledger remain untouched.
