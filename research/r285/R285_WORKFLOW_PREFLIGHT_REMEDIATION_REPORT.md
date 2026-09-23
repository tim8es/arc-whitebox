# R285 - PR #35 residual preflight remediation

Status: COMPLETE. Owner `preflight-r283-remediation-responsive`; run `R285-pr35-r283-remediation-20260923`.

Pinned pre-edit PR head: `05733f3bfa6730124c4601a918bcc6d401719e09`; post-R281 analyzer blob `f9b01ba259cd57bd1692fbfc904585b05f561000` / SHA-256 `1f73f557d943dc6b4fb4d42b2a5935f1d627082b292d8465f5018794dc8a38ce`. R281 receipt SHA-256 `6251bc55894ffec016f6e185c4017c757d6bd80b33cc7746673ee68fe7f35de6`; R283 receipt SHA-256 `fb1002ca8e67d4d1cc791443a70559a4037ae0bba260d3121050746839952180`.

Pre-edit exact current-head reproduction retained by R286 on those same bytes: R283 N1 REJECT (exact input already closed) but structural fake-checkout residual E1 PASS; N2 PASS; N3 REJECT (exact direct `get` closed) but alias/dynamic residuals E2/E3 PASS; N4 PASS with `del`/conditional no-write residuals E4/E5 PASS. Only those confirmed residual classes were repaired.

Tests-first commit: `37754c23d1b0c8ef64b3f95bb657f7d0e071f86b`. Production commits: `7ccf984908d0341fc513410d9117b9b0f53ae591` (structural checkout metadata, whitespace/continuation ancestry normalization, AST manifest-access validation, fail-closed generator control flow), `5e37e3de741341202f29cecc3406d29e8cc735f1` (docs), `3b58d9f0e9b8b279d3608b633aaccee786be44a0` (preserve prior fail-closed diagnostics).

Exact committed bytes tested:
- analyzer blob `2c87bc09992228be915e117a6d3aac8a703f68ab`, SHA-256 `946d7c79f988f0b739b8213b2423a315875a8c7c10699c21f1aa9b477a3551ac`;
- tests blob `f1549f1c75f2566e8a347363e2807f87be31ee1f`, SHA-256 `75020df0dd484a2859c60ab20c65453d686e30ad2662f6ce0f25fc98e06d08bc`;
- docs blob `e7f59af7a6684d37ce0899b851bb3d3043661d4f`.

Offline stdlib verification: compatibility 16/16 PASS (`9560b38aed17edc3ceab34f1e5bbb28161765d0cc9c9cae4df4d4f72bae609de`); R285 focused 8/8 PASS (`c430069fc21e8a40f145acee95d15ca19b39ea1a7abb7f5f5ed874b25e67bf77`); full 24/24 PASS (`c3a54cf0506a6eb9de539cc2bc8cf18a4f5c4acfd85f3b2c2918000f00bb34dc`). Exact R283 N1-N4 post-fix replay is 4/4 REJECT (`43d85be2ebc931be680d52c6c37f89611bb9b4b41b8b1962724c493309ff03ca`).

PR #35 remains OPEN/unmerged; pre-evidence head was ahead 10 / behind 0 versus main and the PR body was updated. No Actions, workflow/fixture/estimator/science/benchmark/data execution, paid/private/holdout/full access, canonical changes, historical receipt rewrites, or merge.
