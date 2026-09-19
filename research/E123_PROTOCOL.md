# E123 protocol — independent adversarial multi-source verifier for E122

Idempotency key: `ARC-E123-INDEPENDENT-MULTISOURCE-VERIFIER-20260920`.

Status at freeze: **INDEPENDENT VERIFIER / FAIL-CLOSED READINESS GATE**.

Branch:
`research/e123-independent-multisource-verifier-20260920`.

Parent:
`research/e128-integrate-e121-20260919@6f0b294134bee4b1818bdf0739ece0b99865895a`.

## E122 readiness observed before E123 code

At E123 freeze, repository evidence is:

- `research/E122_PROTOCOL.md` exists only on the E128 integration branch;
- its own status is **PROTOCOL ONLY / NO SCIENTIFIC RUN AUTHORIZED BY E128**;
- it explicitly requires a future dedicated E122 owner to freeze an
  implementation-level protocol before code;
- a remote placeholder branch `research/e122-haar8-antipodal-simplex-source-code-20260920` exists, but at verifier freeze it still points to the E121 terminal head and contains no E122 artifact;
- no authoritative E122 owner commit exists;
- no `methods/e122*.py`, `scripts/e122*.py`, candidate manifest, E122
  result receipt, or E122 scientific run exists;
- E128 registry classifies E122 as
  `RESERVED_SUCCESSOR_PROTOCOL_REQUIRED`.

Therefore E123 must not invent a surrogate E122 mechanism. Candidate-specific
determinism, target/oracle firewall, error-certificate correctness and all-in
candidate cost are **UNEXECUTED unless an actual frozen E122 candidate is
present in the checked tree**.

## Adversarial exact fixture

E123 nevertheless freezes a reusable verifier fixture stronger than E121's
8-D four-source block stress.

### 12-D / six-source dense-input fixture

Construct six independent zero-bias width-2/depth-4 ReLU subnetworks with
He-normal float64 weights and seeds

`123300,123301,123302,123303,123304,123305`.

Let their 2-D input blocks form block-diagonal layer matrices
`B_1,...,B_4 in R^(12x12)`.

Generate a deterministic dense orthogonal matrix `Q in R^(12x12)` from
PCG64 seed `123390` using QR decomposition plus deterministic column-sign
canonicalization.

The verifier gives a candidate only the dense full-network weights

`W_1 = Q B_1,quad W_l=B_l, l=2,3,4`.

For `X~N(0,I_12)`, `Z=XQ~N(0,I_12)`, so the six 2-D source pairs remain
independent standard Gaussians after the hidden rotation. The exact 12-D output
mean is therefore the concatenation of the six exact 2-D E114 means.

This fixture forces a candidate to preserve six simultaneous independent
source pairs while hiding the source decomposition behind dense input mixing.

### Firewall discipline

The exact decomposition, block seeds, `Q`, and exact mean belong to the
verifier only.

A future E122 candidate must execute before the exact reference is
materialized. The candidate may receive only:

- the four dense weight matrices;
- its own frozen seed/configuration from the E122 owner protocol.

It may not receive:

- block decomposition;
- block seeds;
- mixing matrix `Q`;
- exact 2-D references;
- exact 12-D mean;
- benchmark/public/scorer/holdout/full data.

## Frozen verifier checks when E122 becomes runnable

A candidate-bearing E122 snapshot is admissible only if an authoritative
implementation-level protocol freezes, before candidate execution:

1. source-state representation and dimension;
2. compression operator;
3. deterministic candidate seeds;
4. callable/module identity;
5. candidate error-certificate formula and numerical gate;
6. complete all-in cost formula/ledger;
7. same-cost comparator or other preregistered baseline if its E122 protocol
   claims variance/error improvement;
8. one-run/no-rescue discipline.

Then E123 checks:

### Deterministic replay

Run the exact E122 candidate twice with identical frozen weights/config/seed.

Require bitwise-identical prediction/certificate state where representable and
exactly identical accounting ledger. Any stochastic metadata required by the
candidate must also replay exactly.

### Target/oracle firewall

Static source audit plus runtime ordering must show:

- candidate module imports no E114 exact reference or verifier fixture module;
- candidate imports no benchmark/public dataset/scorer helper;
- exact reference is built only after candidate execution;
- candidate inputs contain no block decomposition, `Q`, exact mean, target,
  oracle region state or target-fitted coefficient.

### Error certificate

Let candidate prediction be `m_hat`, exact verifier mean `m_exact`.

For any candidate-provided per-output or global absolute-error certificate
`B`, verifier requires the exact realized error to be contained by the
certificate according to the E122 protocol's frozen norm, with no post-result
reinterpretation.

If the E122 owner protocol fails to define the certificate norm/formula before
execution, this check is **not evaluable and therefore NO-GO**.

### Cost

Recompute every candidate operation class from actual dimensions and compare
against its measured/replayed ledger. At minimum the verifier must account for:

- source-state construction/RNG;
- all dense maps;
- all nonlinearities/gates;
- compression/decompression;
- certificate computation;
- final materialization/reduction.

Missing operation classes are an accounting failure.

## Current E123 decision discipline

The current repository snapshot has no runnable E122 candidate.

E123 therefore performs only:

- repository readiness audit;
- adversarial fixture construction;
- exact-reference construction self-check;
- deterministic fixture replay;
- dense-vs-latent forward equivalence probes;
- candidate-presence/firewall readiness scan.

It does **not** fabricate an E122 candidate, error certificate, or cost.

If no actual candidate is present, the immutable verifier receipt must say:

`BLOCKED_BY_MISSING_E122_CANDIDATE`

with candidate-specific checks classified
`UNEXECUTED_BY_READINESS_GATE`, not PASS.

## Scope

No canonical or ledger mutation. No public/public-mini, benchmark target,
official scorer, holdout, full suite, production execution, tuning, sweep,
rescue or E121 rerun.

Only append-only E123 verifier artifacts and receipt may be committed.
