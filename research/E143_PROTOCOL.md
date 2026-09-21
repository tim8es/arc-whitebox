# E143 protocol — primary-source particle-repair / structured-cloud research

Idempotency key: `ARC-E143-PRIMARY-SOURCE-PARTICLE-REPAIR-20260921`

Status: **PRIMARY-SOURCE RESEARCH ONLY / NO E143 IMPLEMENTATION OR SCIENTIFIC RUN AUTHORIZED**.

Branch:
`research/e143-primary-source-particle-repair-20260921`.

Parent:
`research/bootstrap`.

## Research question

After the verified public V29 cumulant-propagation baseline, is there any admissible
Phase-2 mechanism in the family of:

- in-flow particle repair;
- structured particle clouds;
- Kerdock / mutually-unbiased-basis (MUB) quadrature;
- variance-reduction / moment-matching;

that is not already closed by Phase-2 cost, official restrictions, or measured
negative results?

This lane is research-only. It must end with one note and one immutable receipt.
No estimator implementation, Actions run, public/mini/scorer/holdout/full execution,
canonical mutation, or ledger mutation is authorized.

## Evidence classes

Every quantitative statement in the note must be labeled as one of:

- **ARC OFFICIAL** — Alignment Research Center paper/blog/reference code;
- **WHEST OFFICIAL** — AIcrowd WhestBench/starter-kit contract/rules;
- **PARTICIPANT PRIMARY** — author repository/forum write-up for the method measured;
- **504ALDO PRIMARY** — pinned public V25/V29 release and findings;
- **DERIVATION** — arithmetic/algebra derived from cited facts;
- **HYPOTHESIS** — unexecuted E143 proposal.

Secondary technique censuses may be mentioned only as corroboration, never as sole evidence.

## Mandatory Phase-2 restrictions to enforce

Current WhestBench Phase-2 contract:

- width `1024`;
- depth `16`;
- FLOP budget `B=2^41=2,199,023,255,552` per MLP;
- 120 s wall cap;
- 400 ms residual cap;
- 5 s setup cap;
- 8 GB participant-process memory;
- numerical work in `predict()` must use FlopScope primitives;
- setup may load shipped MLP-independent precomputed artifacts but is not a loophole
  for MLP-dependent numerical computation.

Any candidate whose lower-bound FLOPs exceed `B`, whose required array/state violates
the memory/array restrictions, or whose construction requires prohibited unmetered compute
is closed analytically before implementation.

## V29 baseline boundary

Use pinned public release:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Treat V29 as the same arithmetic closure as V25 after cost engineering.

The note must record the public V29 headline:

- raw final-layer MSE `2.13e-8`;
- `C/B=0.2526`;
- adjusted `5.40e-9`.

It must also account for the public Phase-2 negatives relevant to this lane:

- pure/QMC/sampling remains far above V29 at Phase-2 shape;
- MC control-variate hybrids require much larger variance reduction than measured;
- cheap marginal skew/kurtosis closure does not carry cross-neuron K3;
- output/online correction lanes are closed;
- source-window/drop-old-source variants are closed.

## Mandatory structured-cloud cost proof

The note must evaluate complete real Kerdock/MUB transport at Phase-2 width before
admitting any particle method.

Using the standard complete real MUB/Kerdock family at `d=1024`:

- number of bases: `d/2+1=513`;
- antipodal nodes:
  [
  N_{m full}=2(513)(1024)=1,050,624.
  ]

One ordinary dense post-ReLU propagation alone costs at least

[
2N_{m full}d^2
=2,203,318,222,848
=1.001953125B.
]

Therefore a complete Phase-2 Kerdock/MUB cloud is terminally inadmissible even if its
first structured weight application were free. This is a pre-implementation cost kill.

The note may consider only a strict microcloud that does not claim the complete-design
guarantees.

## Non-overlap rules

E143 may not relabel:

- E140 SMV K3 state;
- E137 CountSketch;
- E132/E134 source-age D21/K3 transport;
- E122/E125/E126 frame/source-code estimators;
- output-only control variates or final ridge correction;
- pure Monte Carlo / QMC estimator;
- full complete Kerdock/MUB propagation;
- Gaussian final-hidden Rao-Blackwell/PCA closure;
- endpoint hidden denoisers already killed in the cited participant-primary ledger.

A surviving hypothesis must alter an **in-flow hidden statistical state** before later
nonlinear propagation.

## Single-hypothesis admission gates

At most one hypothesis may survive. It must:

1. use a structured cloud only as a small, target-free side state;
2. repair a specific V29 in-flow state rather than output-only blending;
3. have a deterministic/frozen cloud recipe independent of benchmark targets;
4. fit the official Phase-2 FLOP, memory, wall, setup, and allowed-code contract by a
   conservative arithmetic upper;
5. have an adjusted-score break-even calculation against V29 before implementation;
6. name one target-free small/synthetic falsifier and a binary GO/NO-GO;
7. not require a rank/sample/layer sweep to define the mechanism.

If none pass all seven, E143 must close
`UNKNOWN_NO_ADMISSIBLE_PARTICLE_SUCCESSOR`.

## Deliverables

Append only:

- `research/E143_PRIMARY_SOURCE_NOTE.md`;
- `research/E143_RESEARCH_RECEIPT.json`.

No executable code or workflow.
