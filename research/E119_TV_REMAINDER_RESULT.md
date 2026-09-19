# E119 result — output-specific omitted-boundary TV remainder

Decision: **TERMINAL MATHEMATICAL NO-GO / CLOSE THIS CERTIFICATE**

Idempotency key: `ARC-E119-OUTPUT-FLUX-TV-REMAINDER-20260919`

## Derived certificate

For the E118 1024-cell scalar flux sketch, a true boundary jump `Delta_k`
inside a cell contributes `Delta_k cos(epsilon_k)`, with
`|epsilon_k|<=pi/1024`, instead of the exact `Delta_k`.

Therefore

`|error| <= g [1-cos(pi/M)] TV(F_c)`

where `g=sqrt(pi/2)/(2*pi)` and
`TV(F_c)=sum_k |Delta_k|`.

The candidate avoids boundary enumeration using the weight-only recursion

`A_1=V_1=2||W_1[:,j]||_2`,

`A_next <= W_+^T A`,

`V_next <= A_next + 2 |W|^T V`,

followed by

`TV(F_c) <= |c|^T V_L`.

The bound is target-free and uses weights only.

## Frozen exact corpus

Same E118 corpus: width 8, depth 4, input dimension 2, seeds
114200–114203, 1024 angular cells.

Requested RMS certificate limit:

`1.3747727085e-4`.

The midpoint identity implies that the weight-only scalar TV bound would need
to be at most `146.4472888680176`.

Measured weight-only TV bounds were:

- 114200: `1795.2996561827213`
- 114201: `2244.4965923469354`
- 114202: `2057.592746244526`
- 114203: `1708.1731694596886`.

Corresponding rigorous absolute mean-error bounds:

- `1.6853360618534804e-3`
- `2.107019312771786e-3`
- `1.9315634824034632e-3`
- `1.603546144771259e-3`.

Pooled RMS bound:

`1.84270085409586e-3`.

Ratio to required RMS limit:

`13.403676423766163x`.

Thus the decisive certificate gate fails.

## Exact verifier evidence

The exact E114 boundary reference was used only after candidate construction.

Exact scalar total variations were
`9.8611, 24.0086, 32.8223, 6.70976`; every exact value was below the
weight-only bound, so the recurrence is conservative as intended.

The exact E118 sketch RMS bias was only

`1.3271487131363013e-6`,

roughly 100x below the requested RMS scale. The certificate is therefore the
problem, not the underlying E118 sketch accuracy.

The rigorous bound is about `1388.47x` the measured RMS sketch bias.

## Cost

Certificate production overhead upper:

`95,433,280 FLOPs`.

E118 production upper plus certificate:

`73,814,910,016 FLOPs`.

Utilization:

`0.03356713478569873 <= 0.13`.

Compute is not the blocker.

## Execution

- protocol: `f2236ea7715d1bf7c625355b6cc9bfb02b2e80f5`
- method: `306176fc49123f618c74d15a22a9055feccd897e`
- tests: `e1c9b38efa19f15a91209fb6cb8852ceaadce0cb`
- falsifier: `55f6d44a8b0679a53030826d385b10367c235d6b`
- executed head: `b2662f54f1707a67c33109671e285b918b6a9ba7`
- run/job: `35458271579 / 105937346267`
- focused tests: `4 passed in 0.13s`
- deterministic replay: exact
- artifact: `e119-output-flux-tv-remainder`
- artifact ID: `10589575446`
- artifact ZIP SHA256:
  `3f75a6de98c9a79c966672aff2fd47fe3e5cbdb53448c12a3b6bd8c2beab5fc1`.

## Formal closure

The cheapest weight-only TV certificate tested here is rigorous and
computationally admissible, but it misses the required RMS certificate by
13.4x on the frozen exact corpus.

**E119 TV-remainder mechanism is formally closed.**

No alternate norm, empirical calibration, boundary-count correction,
cancellation heuristic, cell-count change, seed/width/depth change, tuning,
rescue, rerun, production scientific execution, public/scorer/holdout/full
access, canonical mutation or ledger mutation occurred.
