# R217 — R207 ↔ R210 read-only runtime forensics

## Scope and verdict

No scientific benchmark was launched. This diagnosis reads the immutable R207 and R210 public-50 artifacts only.

**Verdict: `CPU0_CAUSAL_ROLE_NOT_ESTABLISHED`.** R210 is associated with a large deterioration, but the existing evidence does not identify CPU 0 as its cause. The paired pattern is strongly sequence/time dependent and the two runs used different GitHub-hosted workers in different Azure regions.

## Immutable evidence

- R207 Actions run/job: `35755631386` / `106840538172`; artifact `10709911534`; ZIP SHA256 `53fecd878787078ff9526da4af80531a8eee1314fcaf8f7c905e09f505b36090`.
- R207 artifact files: `R207_RECEIPT.json` `fa40c03b89c493d811e493498c152ffc1c7bd6f069626316318e33ba826ea9ee`; `report.json` `6427cf6db345bbb47bdb551507f5afe83e2d21d981d0a495cb8c19e41a85807e`; `environment.txt` `0d14c31303a0f3552f6f9c3976624a77444d09be3d58771ca6325803dd042a66`; `command.txt` `af15c7aaf53ea27bd562758ac8e34393f0ff29ce69d8164c2e5d0c9cb3e9d3d3`.
- R210 Actions run/job: `35762066733` / `106862288745`; artifact `10712680276`; ZIP SHA256 `09719be2466bf43d513f52a025a60482ec9402a3455783710d3fe22e699e30f2`.
- R210 artifact files: `R210_RECEIPT.json` `7651e4d8caccaa720f9cbfa928b2b84649dc0aeafde8057f411a5b40094698b2`; `report.json` `dc1e37f7fbc57853e05dfb91ecfe7919906391f79f44aaedeacd471fea8f9645`; `environment.txt` `a1ba544bbd863ce908d86a2610ac5e8853da57d45b4692df33874b26a7c4e4c2`; `command.txt` `7ab6ddd65c1234b715f418785228d2a09259bdae521f20ef5a7778dc1bc827d1`; `chosen_cpu.txt` `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.
- Canonical per-MLP SHA256 (JSON sorted keys, compact separators): R207 `2056a1d2210d4b2f90da7b8c488548d6cf65a0910bf273b241dca68d242f564f`; R210 `d722d5ed2e5a7a3f1c383798d1f7ce9978d08e72d85c77a2c3fa54c91388f300`.
- Paired table: `research/r217/R217_PAIRED_RESIDUALS.csv`, SHA256 `cc26d4b83ce4d541d76b16e634927815db98b54f1da28eb830c7474285ff68f1`.
- Frozen next protocol: `research/r217/R217_NEXT_RUNTIME_PROTOCOL.json`, SHA256 `40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968`.

## Identity and environment

Both artifacts use estimator SHA256 `86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27`, dataset SHA256 `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`, Python 3.11.16, NumPy 2.4.6, flopscope 0.12.1, whestbench 0.16.1, `V26_STRASSEN=4`, and one thread for OMP/OpenBLAS/MKL/NumExpr. The 50 MLP names/order and every per-MLP FLOP count are identical.

R210 recorded allowed affinity `{0,1,2,3}` and chose CPU `0`; its `whest` process was run under `taskset -c 0`. R207 did not record effective affinity or migration history and did not use `taskset`.

Actions job logs show the same runner software/image but different hosted workers: R207 worker `4817e550-240d-4a81-9194-e4c6a950a28c`, region `westus3`; R210 worker `6ee598a9-b114-409e-a9f9-525c5b725b6b`, region `eastus`. Thus CPU affinity is confounded with worker/region.

## Paired residual result

R207: 10/50 failures, official adjusted score `0.1980992436461347`, mean residual `0.389516962s`, median `0.372765867s`, p95 `0.483909527s`, max `0.530085923s`.

R210: 33/50 failures, official adjusted score `0.614635961915704`, mean residual `0.424767246s`, median `0.413115633s`, p95 `0.518709036s`, max `0.601279514s`.

Paired R210−R207: mean `+0.035250283s`, median `+0.039267820s`; 37/50 residuals increased and 13/50 decreased. Failure transitions: 27 `OK→FAIL`, 13 `OK→OK`, 6 `FAIL→FAIL`, 4 `FAIL→OK`.

The strongest descriptive change point is index 16: indices 0–15 have mean delta `-0.019574196s` with 13/16 faster in R210; indices 16–49 have mean delta `+0.061050038s` and **34/34 are slower** in R210. This is inconsistent with a simple constant CPU0 penalty and is compatible with time-varying host contention or another late-run runtime effect. It does not prove either mechanism.

### Residual quantiles

| quantile | R207 | R210 | paired Δ |
|---:|---:|---:|---:|
| 0% | 0.360578 | 0.357964 | -0.041865 |
| 5% | 0.361288 | 0.372440 | -0.036353 |
| 10% | 0.361923 | 0.373965 | -0.028508 |
| 25% | 0.365185 | 0.394135 | -0.007715 |
| 50% | 0.372766 | 0.413116 | +0.039268 |
| 75% | 0.396068 | 0.452866 | +0.063830 |
| 90% | 0.448445 | 0.472360 | +0.096022 |
| 95% | 0.483910 | 0.518709 | +0.106857 |
| 100% | 0.530086 | 0.601280 | +0.112385 |

## All 50 paired rows

| # | MLP | R207 residual | R210 residual | Δ R210−R207 | transition |
|---:|---|---:|---:|---:|---|
| 0 | logan-fitzgerald | 0.392883 | 0.403221 | +0.010338 | OK→FAIL |
| 1 | william-graves | 0.372069 | 0.357964 | -0.014105 | OK→OK |
| 2 | raymond-barnes | 0.375414 | 0.364995 | -0.010419 | OK→OK |
| 3 | steven-rice | 0.411330 | 0.374029 | -0.037301 | FAIL→OK |
| 4 | sarah-kelley | 0.472446 | 0.440731 | -0.031715 | FAIL→FAIL |
| 5 | christopher-morales | 0.391727 | 0.380761 | -0.010966 | OK→OK |
| 6 | cheryl-graham | 0.387615 | 0.372772 | -0.014844 | OK→OK |
| 7 | renee-park | 0.401533 | 0.373382 | -0.028152 | FAIL→OK |
| 8 | justin-johnson | 0.399063 | 0.380060 | -0.019004 | OK→OK |
| 9 | christina-lopez | 0.415798 | 0.380604 | -0.035194 | FAIL→OK |
| 10 | randy-murray | 0.394509 | 0.381444 | -0.013065 | OK→OK |
| 11 | john-koch | 0.451482 | 0.423544 | -0.027937 | FAIL→FAIL |
| 12 | susan-butler | 0.413042 | 0.372169 | -0.040873 | FAIL→OK |
| 13 | crystal-gonzales | 0.448107 | 0.406242 | -0.041865 | FAIL→FAIL |
| 14 | troy-richardson | 0.399841 | 0.401357 | +0.001515 | OK→FAIL |
| 15 | sharon-whitehead | 0.394042 | 0.394440 | +0.000399 | OK→OK |
| 16 | adam-morrison | 0.530086 | 0.569200 | +0.039114 | FAIL→FAIL |
| 17 | william-simmons | 0.377006 | 0.399148 | +0.022142 | OK→OK |
| 18 | william-bryant | 0.368074 | 0.412922 | +0.044847 | OK→FAIL |
| 19 | angela-hancock | 0.378245 | 0.422525 | +0.044280 | OK→FAIL |
| 20 | lisa-aguirre | 0.369030 | 0.463527 | +0.094497 | OK→FAIL |
| 21 | marissa-perez | 0.369574 | 0.475046 | +0.105472 | OK→FAIL |
| 22 | matthew-cruz | 0.360578 | 0.472235 | +0.111656 | OK→FAIL |
| 23 | dana-parker | 0.361104 | 0.473489 | +0.112385 | OK→FAIL |
| 24 | justin-thomas | 0.361965 | 0.433486 | +0.071521 | OK→FAIL |
| 25 | jose-booker | 0.361514 | 0.462004 | +0.100490 | OK→FAIL |
| 26 | jennifer-best | 0.370157 | 0.446607 | +0.076449 | OK→FAIL |
| 27 | lisa-dean | 0.361944 | 0.454516 | +0.092573 | OK→FAIL |
| 28 | terri-salazar | 0.499413 | 0.554433 | +0.055020 | FAIL→FAIL |
| 29 | monica-duncan | 0.362953 | 0.413310 | +0.050357 | OK→FAIL |
| 30 | katherine-allen | 0.362360 | 0.411555 | +0.049195 | OK→FAIL |
| 31 | stephanie-fowler | 0.362041 | 0.399692 | +0.037650 | OK→OK |
| 32 | nathan-valdez | 0.363150 | 0.419030 | +0.055880 | OK→FAIL |
| 33 | mark-sweeney | 0.364815 | 0.402371 | +0.037556 | OK→FAIL |
| 34 | rachel-warren | 0.364191 | 0.398157 | +0.033965 | OK→OK |
| 35 | cory-clarke | 0.369191 | 0.454035 | +0.084844 | OK→FAIL |
| 36 | patricia-cochran | 0.384851 | 0.449359 | +0.064507 | OK→FAIL |
| 37 | paige-miller | 0.371806 | 0.387808 | +0.016002 | OK→OK |
| 38 | daniel-smith | 0.360856 | 0.414697 | +0.053841 | OK→FAIL |
| 39 | rebecca-jackson | 0.361738 | 0.457263 | +0.095526 | OK→FAIL |
| 40 | sylvia-stanley | 0.493289 | 0.601280 | +0.107990 | FAIL→FAIL |
| 41 | john-lee | 0.377459 | 0.439255 | +0.061797 | OK→FAIL |
| 42 | crystal-carrillo | 0.366896 | 0.425441 | +0.058545 | OK→FAIL |
| 43 | renee-garcia | 0.396588 | 0.454381 | +0.057793 | OK→FAIL |
| 44 | anita-collier | 0.367013 | 0.457733 | +0.090720 | OK→FAIL |
| 45 | tina-webb | 0.372689 | 0.419109 | +0.046420 | OK→FAIL |
| 46 | lisa-mitchell | 0.375754 | 0.394033 | +0.018279 | OK→OK |
| 47 | douglas-kelly | 0.366295 | 0.405716 | +0.039421 | OK→FAIL |
| 48 | maria-calderon | 0.369476 | 0.401339 | +0.031864 | OK→FAIL |
| 49 | jay-harris | 0.372842 | 0.385946 | +0.013103 | OK→OK |

## Causal limits

1. R207 did not record effective CPU affinity or CPU migration history.
2. R207 and R210 ran on different hosted workers and different Azure regions.
3. There is only one run per condition; there is no same-worker randomized/counterbalanced crossover.
4. CPU model/frequency, steal time, scheduler pressure and noisy-neighbor telemetry were not captured.
5. Therefore the data support an association between the R210 execution condition and worse late-run residuals, **not** a causal claim that CPU 0 itself caused the regression.

## One frozen next runtime protocol

`research/r217/R217_NEXT_RUNTIME_PROTOCOL.json` freezes a single **same-runner balanced three-condition crossover**: `U, C0, C1, C1, C0, U`, where U is unpinned, C0 is CPU0, and C1 is CPU1. All six blocks use unchanged V29, `V26_STRASSEN=4`, the same public first-50 panel and official 0.4s residual limit. The symmetric order gives all three conditions the same mean block position and therefore balances a linear time trend.

Primary CPU0-specific GO requires all provenance/contract gates plus: median per-MLP `mean(C0)-mean(C1) >= 0.020s`, at least 35/50 MLPs slower on C0, and at least 10 more total residual timeouts across the two C0 blocks than the two C1 blocks. If the contract is valid and any threshold fails, verdict is `NO_GO_CPU0_SPECIFIC`. Contract/provenance mismatch is `PROTOCOL_INVALID`, not a scientific result.

This protocol is **frozen but not executed in R217**.