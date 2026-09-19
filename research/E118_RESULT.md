# E118 result — output-specific angular-cell boundary-flux sketch

Idempotency key: `ARC-E118-OUTPUT-SPECIFIC-FLUX-SKETCH-20260919`

Decision: **E118 OUTPUT-SPECIFIC COMPRESSED FLUX REPRESENTATION GO**

This is a target-free exact-small-corpus GO only. It is not a production or
competition-accuracy claim.

## Representation

E118 turns the E114 boundary-flux identity into an executable scalar final-
observable representation without enumerating the complete activation-mask
partition.

For the fixed normalized dense final observable

`c_j=(j+1)/sqrt(sum_{r=1}^n r^2)`,

the candidate evaluates only `F_c` and its input gradient at 1024 fixed
angular grid points.

Inside a boundary-free angular cell the scalar harmonic state
`s=[F_c,F'_c]` obeys the exact transport

`s(theta+h)=R(h)s(theta)`.

The endpoint state defect contains all boundary jumps inside that cell. E118
compresses that entire cell to one midpoint flux atom

`Delta_hat_m = [sin(h/2),cos(h/2)] dot
                (s_{m+1}-R(h)s_m)`.

The deployable representation is therefore exactly 1024 signed scalars. It
stores no region list, no mask table, no boundary roots and no exact-reference
state.

The reconstructed Gaussian mean is

`mu_hat=sqrt(pi/2)/(2*pi) * sum_m Delta_hat_m`.

## Frozen exact-reference corpus

- input dimension: 2
- width/depth: 8 / 4
- zero bias
- iid He-normal float64 weights
- seeds: 114200, 114201, 114202, 114203
- exact E114 final boundary counts: 55, 61, 83, 55
- no public/benchmark target
- no Monte Carlo
- no Gaussian plug-in
- no target fitting

## Exact/reference bias

Candidate scalar means and exact E114 means:

- seed 114200:
  `0.46234502503087094` vs `0.4623458110358122`;
  bias `-7.860049412444781e-7`;
  bias MSE `6.178037676607354e-13`.
- seed 114201:
  `0.5059417304272034` vs `0.5059412406917312`;
  bias `4.897354721755676e-7`;
  bias MSE `2.3984083270702613e-13`.
- seed 114202:
  `0.7299415644365735` vs `0.7299440517627314`;
  bias `-2.487326157818437e-6`;
  bias MSE `6.186791415367828e-12`.
- seed 114203:
  `0.1539114948965861` vs `0.15391146559110228`;
  bias `2.930548381741005e-8`;
  bias MSE `8.588113817724823e-16`.

Summary:

- pooled bias MSE: `1.7613237067793404e-12`
- maximum network bias MSE: `6.186791415367828e-12`
- frozen raw target scale: `1.89e-8`
- max bias-MSE / target: `0.00032734346113057287`
- pooled bias-MSE / target: `9.319173051742541e-05`

Both preregistered scientific gates passed.

## Independent exact formula check

The exact E114 boundary list is used only after candidate construction to
measure the representation.

For a true scalar jump `Delta_k` at angle `tau_k` in a cell ending at
`b_k`, the exact midpoint sketch contribution is

`Delta_k cos((b_k-tau_k)-h/2)`.

The independently reconstructed exact sketch agrees with the executable
candidate at:

- max atom error: `1.1102230246251565e-15`
- max total compressed-flux error: `3.1086244689504383e-15`
- max candidate-bias vs exact-formula error:
  `6.661338147750939e-16`

E114 exact flux mean vs sector integration was also within
`1.1102230246251565e-16` on each frozen network.

## Actual flopscope cost

Every frozen network measured exactly:

`1,886,208 FLOPs`.

Breakdown:

- forward: `917,504`
- observable reduction: `30,720`
- reverse scalar-observable pass: `897,024`
- angular derivative: `6,144`
- flux sketch: `34,816`
- input wrap: `0`

Exact category reconciliation: PASS.

Measured utilization versus `2^41`:

`8.577480912208557e-7`.

The fixed angle/tangent table is a declared compile-time representation
constant and is not included in online flopscope billing.

Frozen production-shape admission bound:

- width/depth: `1024 / 16`
- cells: `1024`
- forward+reverse dense core: `68,719,476,736 FLOPs`
- helper reserve: `5,000,000,000 FLOPs`
- upper: `73,719,476,736 FLOPs`
- utilization: `0.03352373675443232 <= 0.13`

No production scientific run was performed.

## Determinism and scope

- deterministic replay max abs: `0.0`
- exact FLOP ledger replay: PASS
- full mask enumeration: false
- Gaussian plug-in: false
- target fitting: false
- candidate use of exact boundary/reference: false
- public/public-mini: false
- benchmark targets: false
- official scorer: false
- holdout/full: false
- tuning/sweep/rescue/rerun: false
- canonical/ledger mutation: false

## Workflow evidence

- arm/executed head:
  `4f7bae911dcfa85e4e96c39b599d639622602f9c`
- run/job:
  `35457418719 / 105935065614`
- run attempt: `1`
- workflow conclusion: `success`
- exactly one workflow run for the arm head
- artifact: `e118-output-specific-flux-sketch`
- artifact ID: `10588194482`
- artifact ZIP SHA256:
  `f88ca8168f9b938081bd63a8667012872f61b2d8ae7039ace341cbcf45fc41d3`

## Verdict

**E118 OUTPUT-SPECIFIC COMPRESSED FLUX REPRESENTATION GO.**

The exact-small-width evidence establishes an executable 1024-scalar
output-specific boundary-flux representation with measured low bias and a
preregistered production cost path below utilization 0.13.

What remains unexecuted is production-shape scientific accuracy. E118 does not
authorize public/benchmark evaluation.
