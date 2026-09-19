# Deep-error portfolio handoff — E109 / E110

Handoff key: `ARC-DEEP-ERROR-HANDOFF-E109-E110-20260919`

Control receipt: `ARC-PORTFOLIO-DEEP-ERROR-E104-E110-20260919`.

## Frozen portfolio boundary

**E104 is sealed terminal portfolio NO-GO.** Its local Haar radial Rao–Blackwell result remains mathematically valid, but E105 measured the production-shape target-free stochastic-risk scale at `8.604586912926751e-6`, about `455.27x` the raw target `1.89e-8`. No further E104 execution, benchmark authorization, rescue or reinterpretation is allowed under E104.

**E108 is sealed terminal NO-GO/DROP.** Run `35449335693`, job `105913650102`, artifact `10585484463` measured only `0.275171%` risk reduction versus its matched E104 baseline; candidate risk remains `529.968x` the raw target. No transport/coefficient/seed/sample rescue or rerun.

E105, E106 and E107 are also closed. Their mechanisms may be used as negative evidence only.

## Active lane A — E109

Tracking ID: `ARC-E109-COUPLED-HAAR-HADAMARD-20260919`

Owner branch: `research/e109-coupled-haar-hadamard-design-20260919@4b249887503862889448858093b8b374d8510bba`

Owner: **research owner**.

Verifier: **independent verifier**, future branch `review/e109-independent-verifier-20260919`, created only from the immutable owner result tip.

Mechanism: replace E104's two independent Haar bases by one Haar basis `Q` and the coupled basis `H Q` for fixed normalized Walsh-Hadamard `H`; retain analytic chi radius, antipodes and exactly 4096 trajectories.

Immediate owner gate:

1. commit a pre-code admission receipt with marginal-law proof and complete RNG/QR/Hadamard/forward/reduction FLOP bound;
2. if conservative utilization > `0.13`, close E109 without code;
3. otherwise implement exactly the frozen mechanism and execute one synthetic production-shape run.

Terminal scientific kill gates:

- aggregate target-free risk / matched E104 risk `<=0.35`;
- wins on at least `3/4` frozen networks;
- worst per-network ratio `<=0.80`;
- exact antipodes, deterministic replay, exact FLOP reconciliation;
- measured utilization `<=0.13`;
- zero target/public/scorer/holdout/full access.

Any failure closes E109. No alternate Hadamard, extra signs/bases, seeds, samples, blending or rerun.

## Active lane B — E110

Tracking ID: `ARC-E110-DEEP-HOUSEHOLDER-ORBIT-20260919`

Owner branch: `research/e110-deep-householder-orbit-20260919@ca6d9430644e745d174c46cbc27334332671d1f0`

Owner: **research owner**.

Verifier: **independent verifier**, future branch `review/e110-independent-verifier-20260919`, created only from the immutable owner result tip.

Mechanism: compute one target-free deep sensitivity axis from the all-gates-half backward linearization of the fixed network; couple one Haar basis with its Householder-reflected basis; retain analytic chi radius, antipodes and exactly 4096 trajectories.

Immediate owner gate:

1. commit the deterministic sensitivity definition, reflection orthogonality proof/check and complete pre-code FLOP bound;
2. kill immediately if sensitivity is non-finite/zero, orthogonality error exceeds `1e-10`, or conservative utilization > `0.13`;
3. otherwise implement exactly the frozen mechanism and execute one synthetic production-shape run.

Terminal scientific kill gates:

- aggregate target-free risk / matched E104 risk `<=0.35`;
- wins on at least `3/4` frozen networks;
- worst per-network ratio `<=0.80`;
- Householder orthogonality max error `<=1e-10`;
- deterministic replay and exact FLOP reconciliation;
- measured utilization `<=0.13`;
- zero target/public/scorer/holdout/full access.

Any failure closes E110. No alternative sensitivity axis, multiple reflections, fitted coefficients, seed/sample changes or rerun.

## Concurrency / verification rule

E109 and E110 are the **only two active deep-error lanes**. They may run in parallel because their mechanisms are disjoint: E109 is network-agnostic angular moment balancing; E110 is network-adaptive geometric coupling.

Do not allocate E111+ until at least one owner lane produces an immutable result and its independent verifier has checked commit identity, physical run/job/artifact digest, no-target scope, deterministic replay, complete billing and frozen kill gates.

Text updates and idle branch reservations do not count as progress.
