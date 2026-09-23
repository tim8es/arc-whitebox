# R279 protocol — compliant local path to the official visible-50 panel

- Job: R279
- Owner: `phase2-public-panel-audit`
- Dependency: R271 COMPLETE.
- Start point: R271 `NOT_COMPARABLE`: visible-50 labels overlap R209 by 0/50; public online artifacts expose no `network_id` or target fingerprint; exact grader/meter versions differ from R209.
- Question: using only first-party AIcrowd, whestbench/starterkit, and Hugging Face public metadata/docs, determine whether the exact online Phase-2 visible-50 panel can be reproduced locally with stable identities or target fingerprints and the official grader+meter versions, without submission or sealed/private/full data.
- Allowed: public metadata/docs, repository source/manifests, HTTP/API metadata, package/version metadata.
- Forbidden: benchmark data download, estimator/benchmark execution, Actions, competition submission, sealed/private/full data access, paid resources, leaderboard/canonical/model mutation.
- Output: one concise cited report naming exact endpoints/artifacts/permissions, a yes/no pathway, and the minimum missing public artifact.
