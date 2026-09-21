# E159 PRIMARY-SOURCE NOTE — published Phase-2 angular/radial mechanism

Date: 2026-09-21  
Branch: `research/e159-published-angular-gauge-20260921`  
Clean-room base: `main@2af54da98045e36b37330e1f7c9f36f0943f3661`

## Scope

E159 reconstructs only the distinct published Phase-8 angular/radial mechanism from
the public implementation. It does not import, copy, or execute E151, E154, or E157
code or artifacts. It does not use public benchmark targets.

Primary public repository:
https://github.com/barnobarno666/ARC-White-Box-Estimation-2026

Pinned public commit:
`1558651e49d68b40821930f0f9c9a059f33d3a52`

Pinned evidence:
- `phase8report.md`, blob `3087457e972c0ea4692aeb9070c2a456cd1aed60`
- `candidates/estimator_p8_a1_g_k2.py`, blob `116244b48085e3c4c7447cdca1354ef43a990212`
- `candidates/estimator_p8_a1_a_k2.py`, blob `be22c6b881bb154867ca66ba7c288d349cb6d093`
- `candidates/estimator_p8_a1_g_k2k4.py`, blob `384abab18ff39c11a7ce573276576bf091442f74`
- `candidates/estimator_p8_a1_a_k2k4.py`, blob `67a4bee83517314cb122fe2691826ec910cdb21d`
- `candidates/estimator_p8_a1_g_k3c65.py`, blob `dbf1f6b662208a2624272c8c179cae86fbdde5d7`
- `candidates/estimator_p8_a1_a_k3c65.py`, blob `17faa6cfe84f26c28d8238c908e84e9ab3028c6e`
- `whest-starterkit/scripts/p8_build_candidate.py`, blob
  `ddc796052106e97e611f01b090b0ed94b2e8b803`

## What the published 7.92% comparison actually changes

The two published full K3C65 files are byte-identical except for metadata and one
runtime switch:

`A1-G-K3C65`: `is_angular = False`  
`A1-A-K3C65`: `is_angular = True`

Both have `use_k4 = True` and the same K3C65 retention/schedule.

Therefore the reported raw-MSE change

[
3.7859	imes10^{-8}	o3.4859	imes10^{-8}
]

is attributable at code level to the **published angular switch as a package**.
That switch has three arithmetic consequences:

1. input scalar fourth cumulant starts at
   [
   c_{4,0}=-6/(n+2)
   ]
   instead of zero when K4 is enabled;
2. after the first nonlinear state update, the implementation applies
   [
   mu_A=mu_G/a_1,qquad
   C_A=C_G-(a_1^{-2}-1)mu_Gmu_G^T;
   ]
3. every reported layer mean, including the terminal output, is multiplied by
   (a_1).

At width 1024 the public constant is `A1_CONST=0.9997558892211914`, matching
the exact radial factor
[
a_1(n)=sqrt{2/n},Gamma((n+1)/2)/Gamma(n/2)
]
to float32 precision.

The full-K3 published pair does **not** isolate these gauge operations from the
nonzero initial K4, because `use_k4=True` in both files. A claim that the 7.92%
gain was specifically caused by K4 is therefore not identified by that comparison.

## Public ablation that separates gauge from K4

The four K2 files are generated from the same source and differ in executable
configuration only by the two Boolean switches `is_angular` and `use_k4`.

Direct file diff:

- G-K2 -> A-K2: only `is_angular: False -> True`;
- G-K2 -> G-K2K4: only `use_k4: False -> True`;
- A-K2 -> A-K2K4: only `use_k4: False -> True`.

The public report gives:

| arm | raw MSE | billed utilization |
|---|---:|---:|
| G-K2 | 4.1257e-6 | 4.36% |
| A-K2 | 3.4236e-6 | 4.36% |
| G-K2K4 | 4.0639e-6 | 4.41% |
| A-K2K4 | 3.4303e-6 | 4.41% |

Consequences from the published numbers:

[
A	ext{-}K2/G	ext{-}K2=0.8298228,
]
so the radial/angular gauge with K4 disabled improved the reported K2 raw MSE by
17.02%.

Within the angular representation,
[
A	ext{-}K2K4/A	ext{-}K2=1.0019570,
]
so enabling the recurrent scalar-K4 path made the reported K2 raw MSE about 0.196%
worse, not better.

Within the Gaussian representation, K4 improved K2 by about 1.50%.

Thus the primary implementation evidence establishes:

- the full-K3 7.92% result is an **angular-switch package effect**, not an isolated
  K4 result;
- radial/angular gauge arithmetic is independently sufficient to produce a large
  published improvement in the K2 ablation;
- recurrent scalar K4 is not necessary for that angular K2 improvement and is
  slightly adverse in that ablation.

This does not prove that K4 contributed zero to the full K3 result. The public
full-K3 experiment did not include the required A-K3C65/K4-off arm, so that causal
quantity is not identified.

## Clean-room reconstruction target

E159 will reconstruct the four **K2** configurations only, because they are the
published ablation that actually separates gauge from K4 and their published cost
is already far below 0.135B.

No public predictions, labels, mini data, or target values are used in the
falsifier. The published aggregate MSE values above are evidence for choosing the
mechanism, not execution inputs or gates.

The target-free falsifier will use exact synthetic Gaussian means and will measure
three orthogonal effects:

[
Delta_{m gauge}=MSE(A	ext{-}K2)-MSE(G	ext{-}K2),
]
[
Delta_{m K4|A}=MSE(A	ext{-}K2K4)-MSE(A	ext{-}K2),
]
[
Delta_{m K4|G}=MSE(G	ext{-}K2K4)-MSE(G	ext{-}K2).
]

The scientific gate is on the gauge-only effect. K4 effects are frozen diagnostics;
they cannot rescue a failed gauge gate.
