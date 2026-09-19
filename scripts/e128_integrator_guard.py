from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

IDS = [f"E{i}" for i in range(121, 128)]
REGISTRY = Path("research/E128_ID_REGISTRY.json")
LEDGER = Path("research/ledger.csv")
OUT = Path("e128-integrator-guard.json")


def remote_heads() -> list[str]:
    raw = subprocess.check_output(
        ["git", "ls-remote", "--heads", "origin"], text=True
    )
    heads = []
    for line in raw.splitlines():
        _sha, ref = line.split("\t", 1)
        if ref.startswith("refs/heads/"):
            heads.append(ref[len("refs/heads/"):])
    return sorted(heads)


def claimed_id(branch: str) -> str | None:
    low = branch.lower()
    for exp in IDS:
        token = exp.lower()
        if re.search(rf"(^|[/_-]){token}([/_-]|$)", low):
            return exp
    return None


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    heads = remote_heads()

    claims = {exp: [] for exp in IDS}
    for branch in heads:
        exp = claimed_id(branch)
        if exp is not None:
            claims[exp].append(branch)

    with LEDGER.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ledger_ids = [row["id"] for row in rows]
    counts = Counter(ledger_ids)
    duplicate_ledger_ids = sorted(k for k, v in counts.items() if v > 1)
    e121_e127_rows = [x for x in ledger_ids if x in IDS]

    registry_ids = sorted(registry["ids"].keys())
    registry_exact = registry_ids == IDS
    registry_claims_match = all(
        registry["ids"][exp]["observed_claiming_branches"] == claims[exp]
        for exp in IDS
    )

    collision_ids = [exp for exp, branches in claims.items() if len(branches) > 1]
    occupied_ids = [exp for exp, branches in claims.items() if len(branches) == 1]

    # At initialization the committed registry says all seven slots are unclaimed.
    # If a new branch appears before this sole guard executes, fail closed rather
    # than silently integrating it without protocol/receipt/run review.
    no_new_claims = not any(claims.values())

    gates = {
        "registry_exact_e121_e127": registry_exact,
        "registry_matches_remote_heads": registry_claims_match,
        "no_same_id_collision": len(collision_ids) == 0,
        "canonical_ledger_has_no_duplicate_ids": len(duplicate_ledger_ids) == 0,
        "no_speculative_e121_e127_ledger_rows": len(e121_e127_rows) == 0,
        "initial_slots_still_unclaimed": no_new_claims,
    }

    result = {
        "schema": "arc.whitebox.e128.integrator_guard.v1",
        "ids": IDS,
        "remote_claims": claims,
        "occupied_ids": occupied_ids,
        "collision_ids": collision_ids,
        "canonical_ledger_duplicate_ids": duplicate_ledger_ids,
        "canonical_e121_e127_rows": e121_e127_rows,
        "gates": gates,
        "pass": all(gates.values()),
        "interpretation": (
            "E121-E127 are collision-free and unclaimed at this guard run; "
            "no speculative canonical ledger rows exist."
            if all(gates.values())
            else "Fail closed: registry/remote/ledger state changed or collided."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E128_INTEGRATOR_GUARD=" + json.dumps(result, sort_keys=True), flush=True)
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
