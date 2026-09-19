# E119 skeptical protocol — positive-scaling adversary against generic boundary compression

Idempotency key: `ARC-E119-SKEPTICAL-SCALING-COMPRESSION-20260919`

Status: **PREREGISTERED / INDEPENDENT ADVERSARIAL REVIEW**.

## Reviewed claim and scope

Reviewed branch:
`research/e119-generic-boundary-flux-certificate-20260919@de346277894ccb89ceef39e76ca6d8f12853b2ee`.

E119 verified two distinct facts:

1. generic weight-driven boundary construction is exact for 2-D zero-bias
   width<=8/depth<=4 networks;
2. the frozen omitted-flux L1 certificate is rigorous.

It explicitly did **not** establish material boundary compression: on its random
corpus only a zero-jump atom was omitted.

This review attacks the deployability claim one level harder: can that same
generic L1 certificate give nontrivial compression on adversarial dense
small-width networks while preserving its exact remainder guarantee?

No public/benchmark/scorer/holdout/full access, target fitting, tuning,
canonical mutation, or ledger mutation.

## Exact scaling adversary

Let a depth-`L` zero-bias ReLU network have weights
`W_1,...,W_L`. For any scalar `s>0`, define
`\hat W_l = s W_l` for every layer.

Positive homogeneity gives recursively

`h_l^(scaled)(x) = s^l h_l^(base)(x)`.

Therefore:

- every preactivation sign is unchanged;
- every activation boundary angle is unchanged;
- every angular region partition is unchanged;
- the final scalar observable is multiplied by `s^L`;
- every final scalar derivative jump is multiplied by `s^L`.

E119's frozen omitted-flux budget is absolute and scale-independent:

`L_flux = 0.000689208828456787`.

Hence if a base network has minimum nonzero scalar jump magnitude `m>0`,
choosing

`s^L m > L_flux`

forces the rigorous E119 L1 certificate to retain **every nonzero boundary
atom**. This is a structural adversary to generic absolute-flux compression,
not a target-bearing empirical counterexample.

## Frozen adversarial corpus

Construct dense deterministic He-normal base networks using the repository's
independent exact angular generator, then apply the same positive scale
`s=8` to every layer.

Frozen cases:

- A: width 4, depth 3, seed 119401;
- B: width 6, depth 4, seed 119601;
- C: width 8, depth 4, seed 119801.

All weight entries must be finite and nonzero. No seed or scale sweep is
allowed.

The base network is evaluated only to verify the exact scaling law. The
scientific adversary is the scaled network.

## Exact-reference gates

For every case, the executable must verify:

1. all matrices are dense (no exact zero entries);
2. generic scaled region counts equal the independent E114 exact reference;
3. generic scaled boundary angles match reference to <=1e-10;
4. generic scaled scalar jumps match reference to absolute/relative tolerance
   `1e-9 * max(1,max_abs_jump)`;
5. generic full scalar mean matches exact sector mean to the same scaled
   tolerance;
6. base and scaled region counts are identical;
7. base and scaled boundary angles match <=1e-10;
8. each nonzero scaled jump divided by its corresponding base jump equals
   `8^depth` to relative tolerance <=1e-10;
9. deterministic replay is exact.

## Compression-survival gate

Let "nonzero atom" mean `abs(jump)>1e-12`.

The E119 generic compression survives this adversarial review only if it omits
at least one nonzero atom on **every** frozen case while keeping its certified
remainder within the frozen `1.89e-8` MSE scale.

If on any case:

- every nonzero atom is retained, and
- the smallest nonzero jump exceeds the frozen L1 omission budget,

then the adversary succeeds.

If the adversary succeeds on all three cases, record:

**TERMINAL NO-GO — E119 GENERIC ABSOLUTE-L1 BOUNDARY COMPRESSION.**

This verdict is deliberately scoped:

- it does **not** falsify E114 boundary-flux exactness;
- it does **not** falsify E119 generic boundary construction;
- it does **not** rule out a new cancellation-aware, relative-error,
  grouped-flux, symbolic, or otherwise different compression certificate.

It closes only the frozen E119 independent-atom absolute-L1 omission rule as a
generic material-compression mechanism.
