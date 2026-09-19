# E119 result — generic weight-driven boundary flux with omitted-flux certificate

Idempotency key: `ARC-E119-GENERIC-BOUNDARY-FLUX-CERT-20260919`

Decision under frozen gates: **E119 GENERIC BOUNDARY-FLUX CERTIFICATE GO**

This is a width<=8/depth<=4 deployability-bridge result only. It does not
establish useful production compression.

## Generic construction

E119 removes all fixture-specific boundary/mask state.

For arbitrary zero-bias 2-D ReLU weights with width<=8/depth<=4, the
implementation mechanically:

1. propagates affine angular coefficient states;
2. solves every preactivation root inside each current region;
3. splits regions from those weight-derived roots;
4. applies midpoint ReLU masks;
5. constructs final scalar-observable derivative jumps;
6. reconstructs the E114 scalar mean from the jump sum.

No E114 boundary angles, masks, region coefficients or jumps are provided to
the candidate constructor.

Focused tests passed: `3 passed in 0.37s`.

## Exact independent reference agreement

Frozen width-8/depth-4 seeds:
`114200,114201,114202,114203`.

Layerwise region counts:

- 114200: `[17,33,47,55]`
- 114201: `[17,31,47,61]`
- 114202: `[17,37,53,83]`
- 114203: `[17,35,45,55]`

Final region/boundary counts exactly match independent E114:
`[55,61,83,55]`.

Measured worst discrepancies:

- wrapped boundary-angle error: `0.0`
- scalar derivative-jump max abs error:
  `4.440892098500626e-16`
- generic full mean vs independent exact mean:
  `2.220446049250313e-16`
- E114 flux mean vs sector mean:
  `1.1102230246251565e-16`
- deterministic replay max abs: `0.0`

Thus the generic weight-driven state construction passes the exact gate.

## Frozen omitted-flux certificate

Frozen scalar-MSE gate:

`1.89e-8`.

Corresponding absolute-mean bound:

`sqrt(1.89e-8)=0.0001374772708486752`.

For Gaussian flux factor

`g=sqrt(pi/2)/(2*pi)=0.19947114020071632`,

the allowed omitted scalar-flux L1 is

`0.000689208828456787`.

The frozen algorithm sorts boundary atoms by absolute scalar jump and omits the
longest prefix whose L1 mass stays within this budget. It certifies

`|mu_kept-mu_full|
 <= g * sum_abs(omitted_jumps)`.

All certificate gates pass.

Measured retained/omitted state:

- seed 114200: retained `54/55`, omitted `1`
- seed 114201: retained `60/61`, omitted `1`
- seed 114202: retained `82/83`, omitted `1`
- seed 114203: retained `54/55`, omitted `1`

For every network the sole omitted atom has exactly zero scalar jump, so:

- omitted L1 flux: `0`
- absolute remainder certificate: `0`
- certificate squared: `0`
- compressed exact bias MSE:
  `[4.930380657631324e-32, 0,
    4.930380657631324e-32, 0]`

The next-smallest nonzero atom has magnitude:

- `0.009142560506137522`
- `0.0008991440333659011`
- `0.003739433377093484`
- `0.0007752215692883401`

respectively, all larger than the frozen omitted-flux budget
`0.000689208828456787`.

Therefore the L1 certificate is valid and exact, but it cannot safely discard
even one nonzero atom on this frozen corpus.

Retained fractions are
`[0.98181818,0.98360656,0.98795181,0.98181818]`.

## Accounting

Generic dense region-state propagation runs inside
`flopscope.BudgetContext`.

Maximum actual flopscope dense count:

`51,456 FLOPs`.

Maximum conservative manual geometry equivalent:

`53,816`.

Maximum all-in accounted cost:

`105,272`.

All-in utilization versus `2^41`:

`4.787216312251985e-8`.

All dense ledgers reconciled exactly and replayed deterministically.

The manual ledger explicitly covers root solving, midpoint trigonometry,
midpoint signs, coefficient mask application, boundary tangent construction,
scalar jump evaluation, sorting and certificate arithmetic.

## Execution

- arm/executed head:
  `d731e845c96d401ac001da82c8998c06a03ec484`
- run/job:
  `35458020001 / 105936659806`
- run attempt: `1`
- workflow conclusion: `success`
- exactly one workflow run for the arm head
- artifact:
  `e119-generic-boundary-flux-certificate`
- artifact ID:
  `10589345345`
- artifact ZIP SHA256:
  `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`

No rerun, public/public-mini, benchmark target, scorer, holdout/full, tuning,
sweep, rescue, canonical mutation or ledger mutation.

## Interpretation

**Frozen E119 gates pass.**

The positive result is narrow but real:

- E118/E114 boundary flux is now constructed generically from actual weights
  and actual induced regions at width<=8/depth<=4;
- a rigorous target-free omitted-flux certificate is executable and validated;
- actual BudgetContext and geometry accounting are recorded.

The measured deployment blocker is equally clear:

> the frozen triangle-inequality remainder certificate provides essentially no
> nonzero-atom compression on the exact corpus.

So E119 verifies the generic construction/certificate bridge, but does **not**
show that exact boundary enumeration has become practically compressible.
