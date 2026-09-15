# E037 terminal result — NO-GO / DROP

Idempotency key: `ARC-KEEP-GOING-RESEARCH-20260915-E037`

## Frozen provenance

- Branch: `research/e037-signed-k3-k4-response-20260915`
- Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `c9869ac0d5a200364448d8ddcb384d1e112c0c06`
- RED workflow head: `732a72879e8bc38d9867f26b85c8b74bbdab6ea9`
- Frozen implementation commit: `1fa726083c61ee0027f0a4905c5021cefdc4d114`
- Focused GREEN head: `3fc24173cdc94a7cc715f1ae36a46f45bf048c23`
- Frozen diagnostic harness commit: `3c4e27d6448297a6f37187e24eece24e34841e9e`
- Frozen measurement arm commit: `9e1190f86e01795ae838676926dacfcc2e7a921b`
- Public Phase-2 mini index: `0` only

No official scorer, holdout/full split, second mini index, fit, tuning, sweep, canonical mutation, or ledger mutation was used.

## TDD evidence

RED:

- run `35010149269`
- job `104519786034`
- expected failure: `ModuleNotFoundError: No module named 'methods.e037_signed_k3_k4_response'`
- public-mini data were not accessed.

Focused implementation iteration remained pre-science. The first implementation test run exposed only an over-tight Gaussian-ReLU quadrature sanity tolerance; the frozen 16-node rule itself was unchanged. After setting a quadrature-appropriate tolerance, GREEN was reached:

- run `35010410129`
- job `104520643963`
- focused suite: success.

The diagnostic-harness preflight run `35010516629` / job `104521001630` also remained tests-only and passed before the workflow was armed for science.

## Single frozen diagnostic

- run `35010616485`
- job `104521337862`
- scientific HEAD: `9e1190f86e01795ae838676926dacfcc2e7a921b`
- focused tests immediately before science: `6 passed in 1.43s`
- artifact: `10413765931` (`e037-frozen-result`)
- artifact ZIP SHA256: `7a7608df5306270bf64ae193170b009cd6f7581eb4b89e3df752cbec51f70f20`

Measured index-0 metrics:

- final-layer raw MSE: `4.923366472773252e-05`
- billed FLOPs: `134395854566`
- utilization: `0.061116158834011`
- adjusted proxy: `4.923366472773253e-06`
- residual wall time: `0.03606086199829406 s`
- wall time: `2.2667189159999452 s`
- maximum absolute standardized skewness: `0.018871309611147222`
- maximum absolute standardized kurtosis: `0.009606840441148843`
- covariance diagonal max absolute error: `1.3877787807814457e-17`
- deterministic repeat max absolute difference: `0.0`
- failures: `0`
- finite: `true`
- scope check: `true`

Frozen K3 and K4 newborn index sequences repeated identically.

## Gates

PASS:

- utilization `0.061116158834011 <= 0.14`
- failures `=0`
- residual `0.03606086199829406 < 0.400 s`
- finite output/state
- deterministic repeat `=0.0` with identical K3/K4 newborn sequences
- covariance diagonal error `1.39e-17 <= 1e-12`
- frozen scope: full covariance + rank-4 signed K3 + rank-4 signed K4 + H3/H4 first-order Edgeworth only.

FAIL:

- raw MSE `<=1.89e-08`: observed `4.923366472773252e-05`
- adjusted proxy `<2.5e-09`: observed `4.923366472773253e-06`.

## Decision

**NO-GO / DROP E037.**

The method is comfortably cheap and stable but scientifically far outside the competitive accuracy regime. Signed global K4 cross-neuron response therefore does not close the gap left by the low-cost covariance/K3 family.

No rank change, Edgeworth-order change, damping, clipping, fitted response, carrier rescue, rerun, second index, holdout, or official scorer is permitted under E037. Any successor requires a fresh experiment ID from canonical.