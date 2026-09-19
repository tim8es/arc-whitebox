# E112 terminal result — factorized fourth-cumulant joint-CGF closure

Idempotency key: `ARC-E112-CUMULANT-JOINTLAW-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Mechanism

E112 tested a genuinely non-Gaussian later-layer closure rather than the E111
Gaussian plug-in.

Each post-ReLU coordinate is represented by cumulants through order four.
Under the frozen factorized-source law, the full preactivation joint cumulant
generating function is

`K_z(t)=sum_i K_i((W t)_i)`.

Thus linear mixing of all order-1..4 joint cumulants is exact under the
factorized non-Gaussian source ansatz. The hierarchy is closed after each ReLU
by computing positive-part raw moments 1..4 from an analytic second-order
Edgeworth/Hermite signed-density correction, converting those moments back to
cumulants, and re-factorizing the post-ReLU coordinates.

No Gaussian mean/variance plug-in, Haar/Rao-Blackwell, Stein/JVP, first-layer
control, QMC/cubature, latent mixture, E091 or E100 sampler was used.

## Exact small-law falsifier

The falsifier reused the already-validated target-free E111 exact fixture only
as a truth construction:

- latent Gaussian dimension: `2`
- width/depth: `8 / 4`
- weight seed: `111111`
- zero biases
- no Monte Carlo
- no numerical quadrature
- no benchmark/public target

Every angular ReLU sector was recursively enumerated exactly. Powers 1..4 were
integrated analytically with exact Rayleigh radial moments. Pair products were
also integrated exactly to obtain the full post-ReLU covariance matrix at every
layer.

Final exact interval count: `91`.

Exact-reference deterministic replay max abs: `0.0`.

## Joint-law evidence

Exact off-diagonal covariance RMS by layer:

1. `0.14817407919653816`
2. `0.07758978031131109`
3. `0.027408636712609007`
4. `0.007907209362973842`

Exact off-diagonal covariance max abs by layer:

1. `0.47393835093714576`
2. `0.3193293345217606`
3. `0.15326296137900922`
4. `0.03930782543999707`

The frozen closure explicitly discards these dependencies when it re-factorizes
the post-ReLU law. This is a directly measured joint-law blocker, not a target
fit or stochastic diagnostic.

## Mean-bias falsifier

Layerwise exact mean-bias MSE:

1. `2.4314865547888853e-33`
2. `8.172662030772975e-3`
3. `1.25910790455065e-2`
4. `4.138954933770478e-3`

The first layer is exact to floating-point precision, confirming the analytic
machinery on the genuinely Gaussian layer.

After the first ReLU the non-Gaussian cumulant closure fails sharply.

At layers 3 and 4 the Edgeworth signed-density closure becomes physically
invalid:

- negative predicted ReLU mean counts: `[0, 0, 1, 1]`
- negative predicted ReLU variance counts: `[0, 0, 1, 1]`
- minimum predicted variance by layer:
  `[0.020292012361871538, 0.0010939319077548325,
    -0.004512970521328679, -0.068569750723808]`

Final-layer mean-bias MSE:

`4.138954933770478e-3`.

Relative to the competition raw target scale `1.89e-8`:

`218,992.3245x`.

Relative to the frozen E111 Gaussian plug-in final bias
`1.6698051697168073e-3`:

`2.4787053x` **worse**.

Therefore keeping marginal skewness/kurtosis while discarding post-ReLU joint
dependence does not repair E111; on this exact fixture it is materially worse.

## Budget admission

Frozen production accounting path:

- width: `1024`
- depth: `16`
- budget: `2^41`
- cap: `0.13`
- exact dense core bound:
  `11 * 16 * 1024^2 = 184,549,376 FLOPs`
- frozen nonlinear/helper reserve:
  `5,000,000,000 FLOPs`
- production upper:
  `5,184,549,376 FLOPs`
- upper utilization:
  `0.0023576600942760706`

Budget admission therefore **PASS** by a wide margin.

The executed JSON contains a diagnostic field
`dense_core_flops=46,137,344` because that display field reused the small
falsifier's `DEPTH=4` constant. This is an accounting-label bug only: the
preregistered and gate-driving `production_upper_flops=5,184,549,376`
already includes the correct 16-layer dense core
`184,549,376`. No scientific or budget gate depends on the mislabeled
diagnostic field, and no rerun is performed.

## Sole workflow

- protocol freeze commit: `91f47f246c6abce34ad5aef42895d7a8a05690d9`
- protocol arithmetic correction commit:
  `2875ae1b7d16d6b912b222b2d06c14934a54af3e`
- implementation commit: `421ab39cf8d2bf878d802624c91008246c82ab77`
- workflow commit: `21af36019076c4add11829c4225d8a4cd51c9edc`
- arm / executed head: `0feffc6a57457e7a0b94174139458bcc17b71356`
- run/job: `35455150908 / 105929003614`
- run attempt: `1`
- workflow conclusion: `success`
- exactly one workflow run for the arm head
- artifact: `e112-cumulant-jointlaw`
- artifact ID: `10588441092`
- artifact ZIP SHA256:
  `61cdcf57a364f1a30b38e290dc188d19ddd7fdcd1b179214e1723aa9e2d5be3d`

## Verdict

**E112 = TERMINAL NO-GO / DROP.**

Cost is not the blocker. The exact small-law falsifier shows two independent
scientific failures:

1. the post-ReLU factorization discards large, exactly measured joint
   dependencies;
2. the fourth-cumulant Edgeworth closure becomes non-physical by layer 3 and
   produces final mean bias larger than the already-failed E111 Gaussian
   plug-in.

Per frozen protocol there is no clipping, moment repair, variance flooring,
higher Edgeworth order, dependence patch, alternate fixture/seed, tuning,
rescue, rerun, public diagnostic, scorer, holdout/full evaluation, canonical
mutation or ledger mutation.
