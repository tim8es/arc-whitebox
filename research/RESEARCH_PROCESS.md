# ARC research operating system v2

Effective 2026-09-22. Goal: improve validated official adjusted score efficiently.
This repository now has a shared entrypoint on main; experiment code remains in its
own branches. Historical decisions are preserved, not reinterpreted as fresh results.

## Daily view

- [Research overview](control/STATUS.md): queue snapshot, exact-panel comparisons, E-ID coverage.
- [Live queue](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/control/state.json): authoritative owners and attempts.
- [Historical index](history.json): available evidence from all fetched research refs.
- [Original ledger](legacy-ledger.csv): lossless snapshot of bootstrap's free-text ledger.
- [Normalized results](results): per-network data for automatic comparisons.

The bootstrap ledger is not suitable for automatic ranking: multiple metrics live in
free text and many branch results are absent. It is retained and linked in the history
index. New numerical records are structured separately instead of guessing missing values.

## Objective and comparisons

For each valid network: `score_m = final_mse_m * max(0.1, measured_flops_m / budget_m)`.
Average score_m, not average MSE times average cost. Failed networks must retain their
official adjusted penalty. Do not omit failures or estimate them from successful output.

Current Phase-2 reference: `B=2**41`, width 1024, depth 16. Official constraints apply:
120 s predict, 0.4 s residual, 5 s setup, 8 GB process memory. Pin evaluator/meter
versions and verify these against the official kit before a release. Numeric work in
submissions must use the permitted metered path; no unmetered arithmetic or packing tricks.

Sources: [score](https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md),
[round](https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/rounds.md),
[code](https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/allowed-code.md).

The historical `0.135B` cap is a research target, not the official cutoff. Keep the
accuracy/cost tradeoff visible. A 20%-budget estimator can beat a 13%-budget estimator.
Below 10%, only a lower error improves score. Do not globally require exact D21/K3.

Automatic comparison requires identical panel metadata, network IDs, target hashes,
budgets, shape, dtype, evaluator and meter. Otherwise `NOT_COMPARABLE`.
Five networks do not mean the full 100-network mini split; all exposed panels are
development data. Confirmation uses newly preregistered independent networks and
logs access. Do not treat dependent neurons as independent repetitions.
The paired SE reported by this tool is descriptive across networks, not an automatic
significance test or proof of held-out improvement. Promotion needs an independent
review of reference uncertainty, selection/multiple testing and failure behavior.

## Work cycle

1. Read history and claim one concrete question with a bounded resource budget.
2. Run a cheap exploratory falsifier. Debug normally and retain every attempt.
3. Measure candidate, parent and the strongest known comparator on the same panel.
4. Freeze promising code/configuration; confirm on an independent preregistered panel.
5. Reviewer recomputes from retained evidence; integrator updates the shared overview.
6. Prepare the official local evaluation and submission package for competitive candidates.

An error before valid measurement is INFRA_ERROR; fix it and record another attempt.
A weak/noisy signal is INCONCLUSIVE. A measured loss rejects a configuration, not every
future member of its family. Reopening research needs a stated changed assumption,
versioned code and a test that distinguishes it from the earlier result.

Suggested effort allocation: 60% strongest-baseline improvements, 25% alternative
mechanisms, 15% infrastructure/review. This is a starting guide, not another launch gate.
Measure throughput by useful measured hypotheses, time to result, infrastructure failure
rate and best confirmed score on a fixed panel. Do not count messages/commits as gains.

## Tools (Python standard library only)

```powershell
python -m unittest discover -s tests -v
python scripts/arc_history.py refresh
python scripts/arc_import_e174.py
python scripts/arc_control.py report
python scripts/arc_control.py check
python scripts/arc_control.py compare research/results/E173-ago.json research/results/E173-parent.json
python scripts/arc_control.py status --remote
```

Fetch research refs before refreshing history. The importer does not launch scientific
work. The history is an evidence inventory, not an automatic interpretation of success.
Before publishing a result add a complete JSON record using E173 as the schema example.
Use `null` for unknown optional fields; required comparison fields cannot be guessed.

## Exclusive job ownership across independent checkouts

The queue lives on `research/control-v2` at `research/control/state.json`.
Only the coordinator adds/reassigns jobs or resolves a dead owner's claim. Workers
can publish state transitions for their assigned owner. Commands without `--publish`
are previews and do not authorize execution.

```powershell
python scripts/arc_control.py claim R201 --owner baseline --publish
python scripts/arc_control.py start R201 --owner baseline --payload start.json --publish
python scripts/arc_control.py finish R201 --owner baseline --payload finish.json --publish
python scripts/arc_control.py repair R201 --owner baseline --payload repair.json --publish
```

start.json is `{"run_id":"unique-run-id","code_commit":"full SHA","command":"actual executable command"}`.
Use a local UUID if no external run ID exists yet and include the external ID in the
receipt afterwards. finish.json is `{"run_id":"same unique-run-id","status":"COMPLETE","reason":"measured conclusion",
"receipt":{"url":"durable artifact URL","sha256":"64 hex characters"}}`.
For failure use INFRA_ERROR, INCONCLUSIVE or SCIENTIFIC_REJECT. repair.json records
`{"reason":"root cause and repair; scientific changes if any"}`.

Every completion, including a desk review, must identify a recorded start and full
40-character code/source commit. Late identical completions are no-ops; a different
completion for an old attempt is rejected. Repair does not overwrite earlier evidence.

The command fetches current control state, validates dependencies/ownership, creates
a commit with that exact parent and pushes without force. If two checkouts race, one
push is rejected. The loser must inspect current state, not launch a second experiment.
Same-owner duplicate claims/starts are idempotent. This is an operational guard, not
an access-control boundary against users with direct Git write access.

The command doesn't change the worker's checkout/index/HEAD. Commit identity and push
permissions must be configured. No local-only fallback may authorize work. A GitHub
connector worker can ask the coordinator to publish the claim, or perform the same
read-parent -> commit -> non-force update transaction. Never force an old queue snapshot.

The coordinator allocates new work with `enqueue R205 --owner coordinator --payload job.json --publish`.
job.json contains title, hypothesis_id, priority, deliverable, depends_on and assigned_owner.
This publishes both state and the queue overview atomically. Any reassignment requires
an explicit coordinator state change and event after checking that the old execution stopped.

If an owner stops responding, first check existing process/run/artifact. The coordinator
records transfer and checks that the old run cannot resume before assigning another
owner. No time-expiry rule automatically authorizes a duplicate execution.

Only Control Center 7.09 dispatches work. On its recurring wake it reads live state,
actual task replies and run artifacts, advances completed dependencies, and sends one
specific continuation when useful. It must not retransmit generic starts or create
additional guard schedules. Unknown/unchanged state is not a reason for fake progress.

## Initial state and what is not yet proven

E173-AGO is imported from the pinned E174 verifier receipt: 16.8459% better than its
covariance-like parent on five networks, raw MSE about 3.50e-6. It is NOT a demonstrated
improvement over V29. The analytical upper bound 112.1B FLOPs differs from measured
69.159B FLOPs per network. The normalized table uses measured values.

Historical E007/E051/E136 may be stronger; before a project-wide champion claim they
need compatible per-network evidence and current runtime verification. Historical
artifacts with incomplete panel metadata stay in the archive, never in an invented ranking.

Spending remains capped at $100 total; historical spending is incomplete. Current jobs
must use verified free/existing resources until the remaining budget is reconciled.
No competition submission is performed by this system's installation.
