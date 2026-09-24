# R363 — independent cross-session audit of R352 mathematics and R364 correction

**Status:** COMPLETE  
**Verdict:** **PASS_WITH_MINOR_ARTIFACT_SEMANTICS_NUANCE — R364 CORRECTED R352 NARROW VERDICT REMAINS VALID**  
**Universal impossibility claim:** **NO**  
**Measurement classification:** THEORY / PRIMARY-SOURCE / STATIC ARITHMETIC AUDIT ONLY — **0 estimator measurements**  
**Exact base:** \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`  
**Branch:** \`review/r363-r352-correction-independent-audit-20260924\`

## 1. Scope

R363 independently audits:

1. immutable original R352 at
   \`4e46b2bd8d04c15270b40872101555b6ac77f3e7\`;
2. completed independent R361 red-team at
   \`4a99ea885d0a66141af823cd308770d66b8f8245\`;
3. live R352 after completed R364 correction at
   \`c51af6c62639503d326f4cbda5b2d59116bbb718\`.

No R352 or R320 file is edited by R363.

The requested final corrected-artifact verdict is now possible because R364 appeared on the live R352 branch during the R363 audit.

## 2. Immutable provenance

### Original R352

Branch:
\`review/r352-tensorized-hermite-frontier-20260924\`

Original immutable head:
\`4e46b2bd8d04c15270b40872101555b6ac77f3e7\`

Original artifacts:

- report:
  \`research/r352/R352_TENSORIZED_HERMITE_FRONTIER.md\`
  - blob \`6f25841331f0199bd6ee7966a4bda796d79d2c59\`
- receipt:
  \`research/r352/R352_RECEIPT.json\`
  - blob \`432737e41f2b3576d1b5192a01a177c799c58d3b\`

Original verdict:
\`EVIDENCE_BASED_NO_GO_NO_CERTIFIED_LOW_RANK_TT_HERMITE_PATH\`.

### R361 independent red-team

Branch:
\`review/r361-r352-independent-math-redteam-20260924\`

Live head:
\`4a99ea885d0a66141af823cd308770d66b8f8245\`

Artifacts:

- report blob:
  \`d4797eb6075f84731679eab15a4f343c98d8f478\`
- receipt blob:
  \`f1c0951a382a195a367c01cddc850a9c55537aec\`

Verdict:
\`PASS_WITH_NONMATERIAL_CORRECTIONS_R352_NARROW_VERDICT_CONFIRMED\`.

Exact base→R361:
- ahead 1;
- behind 0;
- merge-base \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`;
- exactly the two R361 files.

### R364 corrected live R352

Live R352 head:
\`c51af6c62639503d326f4cbda5b2d59116bbb718\`

Commit message:
\`R364: apply R361 corrections to R352\`

Parent:
\`4e46b2bd8d04c15270b40872101555b6ac77f3e7\`

Current artifacts:

- corrected report blob:
  \`f384caa56b1a43212bf909ccfd3567fa86a7b4e4\`
- corrected receipt blob:
  \`ca4f4608a592594a321790e760aa2d7f6398476b\`

Original→R364:
- ahead 1;
- behind 0;
- merge-base is exactly the immutable original R352 head;
- only the same two R352 artifact paths changed.

R364 preserves the original head/blobs in correction provenance.

## 3. Primary sources independently checked

R363 independently checked the primary papers rather than relying only on R352/R361 summaries.

### Goel–Karmalkar–Klivans 2019

S. Goel, S. Karmalkar, A. R. Klivans,  
**“Time/Accuracy Tradeoffs for Learning a ReLU with respect to Gaussian Marginals,”** NeurIPS 2019.

Primary proceedings PDF:
https://proceedings.neurips.cc/paper_files/paper/2019/file/067a26d87265ea39030f5bd82408ce7c-Paper.pdf

Claim 1 gives the normalized probabilists' Hermite coefficients:
\[
\widehat{\operatorname{ReLU}}_0=\frac1{\sqrt{2\pi}},
\qquad
\widehat{\operatorname{ReLU}}_1=\frac12,
\]
and for \(i\ge2\),
\[
\widehat{\operatorname{ReLU}}_i
=
\frac{H_i(0)+iH_{i-2}(0)}
{\sqrt{2\pi\,i!}}.
\]

Claim 2 gives the corresponding multivariate ridge expansion.

### Oseledets 2011

I. V. Oseledets,  
**“Tensor-Train Decomposition,”** SIAM J. Sci. Comput. 33(5), 2295–2317.

DOI:
https://doi.org/10.1137/090752286

Primary facts checked:

- TT ranks are controlled by unfolding matrix ranks; Theorem 2.1 gives achievability.
- Theorem 2.2 gives TT-SVD Frobenius error control from unfolding approximation errors.
- TT addition concatenates/block-diagonalizes cores and sums auxiliary ranks.
- repeated addition followed by rounding has standard cost \(O(dnr^3)\).
- Hadamard products multiply TT ranks.

### Dolgov et al. 2015

S. Dolgov, B. N. Khoromskij, A. Litvinenko, H. G. Matthies,  
**“Polynomial Chaos Expansion of Random Coefficients and the Solution of Stochastic Partial Differential Equations in the Tensor Train Format,”** SIAM/ASA J. Uncertainty Quantification 3 (2015).

DOI:
https://doi.org/10.1137/140972536

Primary manuscript:
https://arxiv.org/pdf/1503.03210

Primary facts checked:

- scalar PCE TT cores have dimensions
  \(r_{m-1}\times(p_m+1)\times r_m\);
- storage scales as \(O(Mpr^2)\);
- rank \(r\) is explicitly called **data-dependent**, with theoretical estimates under development;
- multiple coefficient tensors may be stored in one shared/block TT;
- the paper explicitly states stable TT rank reduction complexity
  \(O(Mpr^3)\), citing reference [52], which is Oseledets 2011;
- its block-TT-cross cost is separately given in Statement 6.

This provenance detail matters for §8 below.

## 4. Normalized ReLU Hermite coefficient formula

Starting from Goel–Karmalkar–Klivans Claim 1 and

\[
H_{2m+1}(0)=0,
\qquad
H_{2m}(0)=(-1)^m\frac{(2m)!}{m!\,2^m},
\]

for \(m\ge1\),

\[
c_{2m}
=
\frac{H_{2m}(0)+2mH_{2m-2}(0)}
{\sqrt{2\pi(2m)!}}
\]

reduces to

\[
c_{2m}
=
(-1)^{m-1}
\frac{(2m-2)!}
{\sqrt{2\pi(2m)!}(m-1)!2^{m-1}}.
\]

Therefore

\[
\boxed{
c_{2m}^2
=
\frac1{2\pi}
\frac{\binom{2m}{m}}
{4^m(2m-1)^2}
}.
\]

All odd coefficients above degree 1 vanish.

**R363 finding:** R352's normalized coefficient formula is correct.

## 5. Tail recurrence and the 214 / 17116 / 17118 values

Set

\[
a_m=\frac{\binom{2m}{m}}{4^m}.
\]

Then

\[
a_0=1,\qquad
a_m=a_{m-1}\frac{2m-1}{2m},
\]

and

\[
c_{2m}^2=\frac{a_m}{2\pi(2m-1)^2}.
\]

By Parseval for the normalized Hermite basis,

\[
T_{2M}
=
\sum_{m=M+1}^{\infty}c_{2m}^2
\]

is the squared Gaussian-\(L^2\) projection tail.

R363 independently confirms the original reported values:

\[
\boxed{
T_{214}
=
0.000013492776924771552593505491419418409773612758086801
}
\]

\[
\boxed{
T_{17116}
=
0.000000018902711367864330420500761794859257860834116110138
}
\]

\[
\boxed{
T_{17118}
=
0.000000018899398744672019163911215174428104806218667786487
}
\]

The local threshold crossing against

\[
1.89\times10^{-8}
\]

is internally consistent:

\[
T_{17116}-1.89\times10^{-8}
=
2.7113678643304205007617948592579\times10^{-12}>0,
\]

while

\[
1.89\times10^{-8}-T_{17118}
=
6.012553279808360887848255718956\times10^{-13}>0.
\]

Also,

\[
T_{17116}-T_{17118}
=
3.3126231923112565895466204311535\times10^{-12}
=
c_{17118}^2.
\]

Since the degree-17117 coefficient is zero, degree 17117 has the same tail as degree 17116.

Therefore:

\[
\boxed{p=17118}
\]

is the smallest integer degree, and hence the smallest even degree, whose standardized single-ReLU squared-\(L^2\) tail crosses the stated \(1.89\times10^{-8}\) certificate scale.

As both R352 and R361 state, this is a sufficient function-space certificate scale, not a necessity theorem for the final network mean.

## 6. Exact ratio \(T_{214}/(1.89\times10^{-8})\)

The original R352 receipt stored:

\[
713.9035440471721,
\]

which is numerically wrong in the sixth decimal place of the ratio.

Using the exact displayed \(T_{214}\),

\[
\frac{T_{214}}{1.89\times10^{-8}}
=
713.9035409932038409262164772179052790271300575026984\ldots
\]

The R364 corrected report prints the valid prefix

\[
\boxed{713.9035409932038409\ldots}.
\]

### Exact representation nuance

The exact finite input decimal is

\[
T_{214}
=
\frac{
13492776924771552593505491419418409773612758086801
}{10^{54}},
\]

so the ratio is exactly

\[
\boxed{
\frac{
13492776924771552593505491419418409773612758086801
}{
189\cdot10^{44}
}
}.
\]

The numerator digit sum is 231, so it is divisible by 3 but not by 9. After cancellation the denominator still contains a factor 3; hence the decimal expansion is **nonterminating**.

Therefore no finite decimal string is the exact ratio.

**Minor R364 artifact semantics nuance:**  
the R364 report correctly uses an ellipsis, but the corrected JSON receipt field

\`r364_append_only_correction.corrections[P214_TAIL_TARGET_RATIO].current_decimal\`

stores the finite string

\`713.9035409932038409262164772179052790271300575026984\`

without an explicit \`...\`, \`prefix\`, or \`approx\` marker.

The digits themselves are correct as a decimal prefix. The field name/value should be interpreted as a high-precision prefix/approximation, not as an exact terminating decimal.

This is nonmaterial to the R352 verdict.

## 7. Generic central-cut rank lower bound

For the fixed total-degree-\(p\) first-layer coefficient slice and a split \(S|T\), \(|S|=s\), with the neuron/output label on the \(T\)-side, decompose

\[
\alpha=(\beta,\gamma),
\qquad
|\beta|=j,\quad|\gamma|=p-j.
\]

The \(j\)-sector unfolding has the factorization

\[
M_j=U_jR_j,
\]

where \(U_j\) contains degree-\(j\) Veronese features of the restricted dense row directions \(a_{i,S}\).

Under the generic assumptions:

1. even \(p\ge2\), so \(c_p\ne0\);
2. generic normalized dense row directions;
3. generic Veronese rank after restriction to \(S\);
4. nonzero complementary restrictions;
5. the shared-coordinate standard block-TT/PCE representation used by R352;

the right factor has row rank 1024 and

\[
\operatorname{rank}M_j
=
\min\left(
1024,\binom{s+j-1}{j}
\right).
\]

Different \(j\) sectors have disjoint left-degree and right-degree blocks, so their ranks add.

At \(s=512\):

\[
D_0=1,\qquad D_1=512,\qquad
D_j\ge D_2=\binom{513}{2}=131328>1024
\quad (j\ge2).
\]

Hence

\[
\boxed{
r_{512}
\ge
1+512+(p-1)1024
=
1024p-511
}.
\]

At the adjacent \(s=511\) cut:

\[
\boxed{r_{511}\ge1024p-512}.
\]

The output-mode ordering argument is also valid: one side of the single output mode contains at least 512 latent coordinates, and transposition preserves unfolding rank.

**R363 finding:** the R352 central-cut result is mathematically correct under its stated genericity assumptions.

It is an **exact-rank** statement, not an approximate-\(\varepsilon\)-rank lower bound.

## 8. Oseledets 2011 versus Dolgov 2015 attribution

R361 called the R352 attribution to Dolgov “imprecise” and requested that standard dense TT rounding be attributed to Oseledets 2011.

R363's direct primary-source check gives a more precise provenance statement:

### Oseledets 2011

Oseledets is the **upstream/original source** for the standard TT construction and rounding result. Section 4.1 states that repeated TT addition increases ranks and rounding after addition costs

\[
O(dnr^3).
\]

### Dolgov et al. 2015

Dolgov et al. do **not merely** discuss PCE storage and block cross. Their §3.1 explicitly states:

- TT storage \(O(Mpr^2)\);
- linear combinations via TT block concatenations;
- stable quasi-optimal TT rank reduction;
- rank reduction complexity
  \[
  O(Mpr^3),
  \]
  and cites reference [52], which is Oseledets 2011.

Therefore:

- attributing the **origin** of the standard rounding result to Oseledets 2011 is correct;
- citing Dolgov 2015 for the same \(O(Mpr^3)\) PCE-context statement is also factually supported;
- R352's original formula/source statement was not a false citation;
- R364's change is best described as a **source-lineage/provenance refinement**, not a correction of a mathematically wrong complexity formula.

Dolgov remains independently necessary for:
- PCE TT storage \(O(Mpr^2)\);
- data-dependent-rank caveat;
- block/shared TT-PCE construction;
- block TT-cross Statement 6.

R364's current wording is acceptable, but R361's characterization “source correction” is slightly stronger than required.

This nuance does not change any R352 cost conclusion, because both sources state the same asymptotic standard-rank-reduction scale, and R352/R364 already disclaim it as an exact FlopScope/runtime lower bound.

## 9. Core-entry and byte arithmetic

### Degree \(p=214\)

\[
r_{511}=218624,\qquad
r_{512}=218625,\qquad
p+1=215.
\]

Exact entries:

\[
218624\cdot215\cdot218625
=
\boxed{10,276,284,480,000}.
\]

Float32 bytes:

\[
4\cdot10,276,284,480,000
=
\boxed{41,105,137,920,000}.
\]

Thus:

\[
\boxed{41.10513792\text{ TB decimal}}.
\]

The original R352 Markdown is correct.

### Degree \(p=17118\)

\[
r_{511}=17,528,320,\qquad
r_{512}=17,528,321,\qquad
p+1=17,119.
\]

Exact multiplication:

\[
17,528,320\cdot17,119\cdot17,528,321
=
\boxed{5,259,676,132,688,775,680}.
\]

Float32:

\[
\boxed{21,038,704,530,755,102,720\text{ bytes}}
=
21.03870453075510272\text{ EB decimal}.
\]

Float64:

\[
\boxed{42,077,409,061,510,205,440\text{ bytes}}
=
42.07740906151020544\text{ EB decimal}.
\]

The original R352 **Markdown report** already contained the correct exact entries and corresponding rounded EB statements.

The original R352 **JSON receipt** contained low-digit numerical corruption:

- entries:
  \`5259676132688775000\` instead of
  \`5259676132688775680\`;
- float32 bytes:
  \`21038704530755100000\` instead of
  \`21038704530755102720\`;
- float64 bytes:
  \`42077409061510200000\` instead of
  \`42077409061510205440\`.

R364 correctly replaces the current authoritative receipt values with exact decimal strings.

## 10. R364 correction audit

R364 applies three intended corrections.

### 10.1 Large integer serialization — PASS

Current corrected receipt stores:

- \`"5259676132688775680"\`
- \`"21038704530755102720"\`
- \`"42077409061510205440"\`

as strings.

These are exact.

### 10.2 p=214 tail/target ratio — PASS WITH MINOR FIELD-SEMANTICS NUANCE

The digits in R364 are correct.

The Markdown correctly marks the decimal as continuing.

The JSON field should be read as a high-precision decimal prefix because the exact rational is nonterminating.

### 10.3 Complexity provenance — PASS WITH CLARIFICATION

Oseledets 2011 is the original standard TT-rounding source.

Dolgov 2015 explicitly repeats \(O(Mpr^3)\) in the PCE setting while citing Oseledets.

R364's current source attribution is valid; calling the original R352 citation outright wrong would be too strong.

## 11. Corrected-artifact verdict

No material mathematical defect was found in the immutable original R352 derivation.

The original defects are:

1. nonmaterial p=214 ratio arithmetic in the JSON receipt;
2. nonmaterial exact-large-integer corruption in the JSON receipt;
3. provenance wording that can be sharpened toward Oseledets as the original rounding source.

R364 successfully corrects items 1 and 2 and gives an acceptable source-lineage refinement for item 3.

The remaining R364 receipt decimal-prefix labeling nuance is artifact semantics only.

Therefore the live corrected R352 artifact at

\`c51af6c62639503d326f4cbda5b2d59116bbb718\`

receives the R363 verdict:

\[
\boxed{
\text{PASS\_WITH\_MINOR\_ARTIFACT\_SEMANTICS\_NUANCE}
}
\]

The narrow scientific conclusion remains:

\[
\boxed{
\text{EVIDENCE\_BASED\_NO\_GO\_NO\_CERTIFIED\_LOW\_RANK\_TT\_HERMITE\_PATH}
}
\]

with the same limitation as before:

- no universal impossibility theorem;
- exact generic rank does not imply approximate-rank necessity;
- the remaining blocker is absence of a generic-dense approximate TT rank/singular-value certificate through repeated ReLU that closes propagated final-mean error and production cost simultaneously.

## 12. Execution accounting

R363 performed source/repository inspection and desk algebra only.

- project/script code execution: **0**
- tests: **0**
- estimator implementation: **NO**
- estimator measurements: **0**
- synthetic runs: **0**
- official/public benchmark runs: **0**
- Actions: **0**
- downloads / dependency installs: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- submission: **0**
- R352 edits: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
