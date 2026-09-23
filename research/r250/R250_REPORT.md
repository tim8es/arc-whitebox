# R250 — one distinct V25 score-improvement method after R248

## Outcome

**DEVELOPMENT NO-GO before estimator/public measurement.**

The single frozen candidate `V25-LEG2-R1-YOUNG-AP` passed the history-novelty screen,
source-contract preflight, and conservative static `<=0.9x` cost bound, but failed the
pre-registered target-free structural falsifier by a very large margin. Per protocol,
R250 stops here: no estimator implementation, validation, benchmark, public mini-100,
GitHub Actions workflow, retry, or second method.

## Queue / scope

- Job: `R250`
- Owner: `post-r248-next-method-research`
- Run ID: `R250-post-r248-next-method-research-20260923`
- Enqueue / claim / start revisions: `226 / 227 / 228`
- Start code commit: `99f35592913f59360b7f5c3e9645af6ee529b9f9`
- Control head after start/status refresh: `dafe918a7193782e083ed26c0009beeea90f35ca`
- Research branch: `research/r250-leg2-r1-young-ap-20260923`

No R223/R244 candidate output or artifact was read. No paid/private/holdout data,
submission, leaderboard mutation, canonical V25 edit, or gate relaxation occurred.

## Frozen evidence and novelty

The screen read current `AGENTS.md`, `research/RESEARCH_PROCESS.md`, the complete
194-entry `research/history.json` inventory (blob
`8f94f371572fedbd8c1ebd9d19cc48ca837592fb`), immutable R209 V25, R246 score
decomposition, R245 source-compliance report, R248 terminal report, R233/R235 exact
compute audits, and exact public V25 source blob
`195373a110215256b759d7c172ba8c923c62e5cc`.

The complete history mechanism/ref inventory covers, among others, source
dropping/windowing, source-axis compression, old-tier spatial rank/bases, sketches and
sampling, DEIM/cubature, FWHT/structured projection, response-aligned D21, tensor-train
K3, CP carrier, trilinear aggregation, fast matrix multiplication, precision changes,
and displacement structure. Literal history search found zero occurrences of the frozen
leg-channel terminology. The candidate is not R247 2:4 D21 sparsity, R248 Kronecker
transport, R244 MP-R16, or R223 V25-LF.

## Frozen candidate and cost path

For each young source, form the two-channel matrix

`X_s = stack(vec(A_s), vec(P_s))`.

The candidate asks whether this two-dimensional **leg-type** channel is effectively
rank one, so `A_s ~= a_s H_s` and `P_s ~= p_s H_s` for one shared spatial matrix `H_s`.
This is not spatial low rank, source-axis low rank, entry sparsity, or a structured
approximation of the transport operator.

If valid, separate A/P transport becomes one transport of `H_s`, and the two dense D21
right-factor contractions collapse algebraically:

`LA @ Ahat.T + LP @ Phat.T = (a*LA + p*LP) @ H.T`.

Using the conservative R247/R248 anatomy, 54 units of young A/P transport and 54 units
of young D21 contractions each halve to 27 units. Reserving 8 units for metered
extraction/integration gives:

- parent: `375.4644291312434` units;
- candidate bound: `329.4644291312434` units;
- candidate FLOPs bound: `707519474157`;
- candidate/parent: `0.8774850653457754`.

The frozen `<=0.9` static cost gate therefore passed as a planning bound.

Production source was never implemented. The frozen source contract required all
output-affecting numerical work through `flopscope.numpy`: the 2x2 channel Gram,
principal-direction normalization, coefficients, and division would use `fnp`
reductions/`fnp.sqrt`/array operations without `math.*`, NumPy, or materialization to
Python numeric scalars.

## Frozen target-free falsifier

Protocol commit: `0101551e119ccee19a8deadf6629c111528ba598`.

Artifacts frozen before execution:

- `research/r250/R250_CANDIDATE_SPEC.json`, blob
  `df0eb473b2c10d8cdc89ded495214d32e7a8ef9d`;
- `research/r250/R250_PROTOCOL.md`, blob
  `4b184e2f2f16f6ba6df4e0fc183e9f555d5edd00`;
- `scripts/r250_leg2_r1_falsifier.py`, blob
  `c431b1fe95ceb36eba08ad4313b8bb31d0752c62`.

The falsifier uses no ARC dataset or target. It computes the best possible rank-1
two-channel SVD oracle, making the test more favorable than a production 2x2-Gram
implementation. Frozen realistic cases are width 192, covariance latent rank 24, seeds
25001–25004, ages 0 and 2 (8 cases). Birth and transport follow the V25 A/P structure;
the downstream target-free diagnostic mirrors the dense A/P portion of `_dslices`.

Frozen GO gates:
- exact rank-1 control max RRMS `<=1e-12`;
- deterministic replay;
- 8/8 finite;
- every A and P reconstruction RRMS `<=0.015`;
- every D21-core RRMS `<=0.015`;
- mean D21-core RRMS `<=0.012`.

## Result

Result artifact: `research/r250/R250_FALSIFIER_RESULT.json`, commit
`c97cf138ec31752f69638bdff1af38971c251343`, blob
`d0374f319487f4b048e0ab9f843152ef37cf285c`.

Canonical result hash:
`e50801c502e8f0a2dfd7cbf9dbf0eef38d4386ce774156a44b35da322fa50fbc`.

Observed:
- exact-rank-1 control: A RRMS `2.3702863780049514e-16`, P RRMS
  `1.3167213188881879e-16`, D21-core RRMS `4.421498507036677e-16` — PASS;
- deterministic replay — PASS;
- finite realistic cases: `8/8` — PASS;
- maximum A/P reconstruction RRMS: `0.9999977498858067` — FAIL vs `0.015`;
- maximum D21-core RRMS: `1.0024907470453626` — FAIL vs `0.015`;
- mean D21-core RRMS: `0.9997770493726187` — FAIL vs `0.012`.

The oracle preserves one of the two channels well only by discarding almost all of the
other; the joint channel error is about 0.51–0.54 and the downstream D21-core error is
approximately 100%. The failure is therefore structural, not a near-threshold numerical
miss.

## Decision

**R250 DEVELOPMENT NO-GO — `V25-LEG2-R1-YOUNG-AP` fails the frozen target-free
leg-channel fidelity gate.**

The protocol's stop condition is binding. Public R209 mini-100 gates remain unmeasured,
and no Actions run is authorized. No second method is attempted under R250.
