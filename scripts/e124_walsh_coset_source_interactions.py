#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

OUT = Path("e124-walsh-coset-falsifier.json")

DENSE_SEED = 124104
MAG_SEED = 124105
SUBNET_SEEDS = (124200, 124201, 124202, 124203)
CANDIDATE_SEEDS = (124300, 124301, 124302, 124303)
IID_SEEDS = (124400, 124401, 124402, 124403)

P = 2048
M = 4
N = P * M
PROD_D = 1024
PROD_DEPTH = 16
BUDGET = 2**41
UTIL_CAP = 0.13
RAW_TARGET = 1.89e-8
TWO_PI = 2.0 * math.pi

PAIR_MAP = ((0, 1), (1, 2), (2, 3), (3, 0))


def sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def relu_forward(weights: Sequence[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = h @ np.asarray(w, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def dense_he_weights(
    seed: int, input_dim: int = 4, width: int = 8, depth: int = 4
) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    out: list[np.ndarray] = []
    first = rng.standard_normal((input_dim, width)).astype(np.float64)
    first *= math.sqrt(2.0 / input_dim)
    out.append(first)
    for _ in range(1, depth):
        w = rng.standard_normal((width, width)).astype(np.float64)
        w *= math.sqrt(2.0 / width)
        out.append(w)
    return out


def subnet_he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    out: list[np.ndarray] = []
    for layer in range(4):
        w = rng.standard_normal((2, 2)).astype(np.float64)
        w *= 1.0  # sqrt(2/2)
        out.append(w)
    return out


def assemble_overlapping_network(
    seeds: Sequence[int] = SUBNET_SEEDS,
) -> tuple[list[np.ndarray], list[list[np.ndarray]]]:
    subnets = [subnet_he_weights(int(s)) for s in seeds]
    w0 = np.zeros((4, 8), dtype=np.float64)
    later = [np.zeros((8, 8), dtype=np.float64) for _ in range(3)]

    for b, (src_pair, sub) in enumerate(zip(PAIR_MAP, subnets)):
        cols = slice(2 * b, 2 * b + 2)
        rows = list(src_pair)
        w0[np.ix_(rows, range(2 * b, 2 * b + 2))] = sub[0]
        for layer in range(1, 4):
            block = slice(2 * b, 2 * b + 2)
            later[layer - 1][block, block] = sub[layer]

    return [w0, *later], subnets


def walsh_rows(labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(labels, dtype=np.int64)
    if np.any((labels < 1) | (labels > 3)):
        raise ValueError("labels must be in {1,2,3}")
    bits0 = labels & 1
    bits1 = (labels >> 1) & 1
    rows = np.empty((4, labels.size), dtype=np.float64)
    ridx = 0
    for z1 in (0, 1):
        for z0 in (0, 1):
            parity = (z0 * bits0 + z1 * bits1) & 1
            rows[ridx] = np.where(parity == 0, 1.0, -1.0)
            ridx += 1
    return rows


def balanced_labels(rng: np.random.Generator, d: int) -> np.ndarray:
    order = rng.permutation(d)
    labels = np.empty(d, dtype=np.int64)
    cycle = np.array([1, 2, 3], dtype=np.int64)
    labels[order] = cycle[np.arange(d) % 3]
    return labels


def candidate_estimate(
    weights: Sequence[np.ndarray], seed: int, p: int = P
) -> tuple[np.ndarray, dict]:
    d = int(np.asarray(weights[0]).shape[0])
    rng = np.random.Generator(np.random.PCG64(seed))
    total = np.zeros(np.asarray(weights[-1]).shape[1], dtype=np.float64)

    label_counts = np.zeros(3, dtype=np.int64)
    collision_pairs = 0
    total_pairs = 0

    for _ in range(p):
        r = np.abs(rng.standard_normal(d).astype(np.float64))
        b = np.where(rng.integers(0, 2, size=d) == 0, -1.0, 1.0)
        labels = balanced_labels(rng, d)
        label_counts += np.bincount(labels, minlength=4)[1:4]

        for i in range(d):
            for j in range(i + 1, d):
                total_pairs += 1
                collision_pairs += int(labels[i] == labels[j])

        h = walsh_rows(labels)
        x = r[None, :] * b[None, :] * h
        y = relu_forward(weights, x)
        total += np.sum(y, axis=0, dtype=np.float64)

    estimate = total / float(p * M)
    ledger = {
        "outer_orbits": p,
        "walsh_rows_per_orbit": M,
        "deep_propagations": p * M,
        "label_counts": label_counts.tolist(),
        "pair_label_collision_fraction": (
            collision_pairs / total_pairs if total_pairs else 0.0
        ),
    }
    return estimate, ledger


def iid_estimate(
    weights: Sequence[np.ndarray], seed: int, n: int = N
) -> np.ndarray:
    d = int(np.asarray(weights[0]).shape[0])
    rng = np.random.Generator(np.random.PCG64(seed))
    x = rng.standard_normal((n, d)).astype(np.float64)
    y = relu_forward(weights, x)
    return np.mean(y, axis=0, dtype=np.float64)


def all_sign_vectors(d: int) -> np.ndarray:
    out = np.empty((1 << d, d), dtype=np.float64)
    for mask in range(1 << d):
        for j in range(d):
            out[mask, j] = -1.0 if ((mask >> j) & 1) else 1.0
    return out


def conditional_walsh_law() -> dict:
    weights = dense_he_weights(DENSE_SEED)
    rng = np.random.Generator(np.random.PCG64(MAG_SEED))
    r = np.abs(rng.standard_normal(4).astype(np.float64))
    labels = np.array([1, 2, 3, 1], dtype=np.int64)
    h = walsh_rows(labels)

    signs = all_sign_vectors(4)
    all_outputs = relu_forward(weights, r[None, :] * signs)
    exact_mean = np.mean(all_outputs, axis=0, dtype=np.float64)

    cosets: dict[tuple[tuple[float, ...], ...], np.ndarray] = {}
    for b in signs:
        patterns = b[None, :] * h
        key = tuple(sorted(tuple(float(v) for v in row) for row in patterns))
        if key not in cosets:
            y = relu_forward(weights, r[None, :] * patterns)
            cosets[key] = np.mean(y, axis=0, dtype=np.float64)

    coset_matrix = np.stack(list(cosets.values()), axis=0)
    coset_mean = np.mean(coset_matrix, axis=0, dtype=np.float64)
    coset_spread = float(np.max(np.ptp(coset_matrix, axis=0)))

    degree1 = np.mean(h, axis=0)
    degree2_diff = []
    degree2_same = []
    for i in range(4):
        for j in range(i + 1, 4):
            value = float(np.mean(h[:, i] * h[:, j]))
            if labels[i] == labels[j]:
                degree2_same.append(value)
            else:
                degree2_diff.append(value)

    return {
        "exact_conditional_mean": exact_mean.tolist(),
        "mean_over_distinct_cosets": coset_mean.tolist(),
        "distinct_coset_count": len(cosets),
        "full_sign_vs_coset_mean_max_abs": float(
            np.max(np.abs(exact_mean - coset_mean))
        ),
        "degree1_max_abs": float(np.max(np.abs(degree1))),
        "degree2_different_label_max_abs": max(
            (abs(x) for x in degree2_diff), default=0.0
        ),
        "degree2_same_label_max_abs_from_one": max(
            (abs(x - 1.0) for x in degree2_same), default=0.0
        ),
        "dense_coset_output_spread": coset_spread,
        "magnitude_sha256": sha(r),
        "weights_sha256": [sha(w) for w in weights],
    }


# ---- exact 2-D angular reference for verifier only ----

def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    vals = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1e-13 < x < hi - 1e-13:
            vals.append(float(x))
    return vals


def _dedup(xs: Iterable[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(float(v) for v in xs):
        if not out or abs(x - out[-1]) > 2.0 ** -40:
            out.append(x)
    return out


def exact_2d_mean(weights: Sequence[np.ndarray]) -> tuple[np.ndarray, int]:
    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, TWO_PI, np.eye(2, dtype=np.float64))
    ]
    for w in weights:
        nxt: list[tuple[float, float, np.ndarray]] = []
        w = np.asarray(w, dtype=np.float64)
        for lo, hi, coeff in sectors:
            pre = w.T @ coeff
            bounds = [lo, hi]
            for row in pre:
                bounds.extend(_roots(float(row[0]), float(row[1]), lo, hi))
            bounds = _dedup(bounds)
            for a, b in zip(bounds[:-1], bounds[1:]):
                if b - a <= 1e-13:
                    continue
                mid = 0.5 * (a + b)
                q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                active = (pre @ q) > 0.0
                c = pre.copy()
                c[~active, :] = 0.0
                nxt.append((a, b, c))
        sectors = nxt

    width = int(np.asarray(weights[-1]).shape[1])
    angular = np.zeros(width, dtype=np.float64)
    for lo, hi, coeff in sectors:
        b1 = np.array(
            [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
            dtype=np.float64,
        )
        angular += coeff @ b1
    mean = math.sqrt(math.pi / 2.0) * angular / TWO_PI
    return mean, len(sectors)


def exact_overlapping_mean(subnets: Sequence[Sequence[np.ndarray]]) -> tuple[np.ndarray, list[int]]:
    means = []
    counts = []
    for sub in subnets:
        m, c = exact_2d_mean(sub)
        means.append(m)
        counts.append(c)
    return np.concatenate(means, axis=0), counts


def source_audit() -> dict:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {
        "whestbench",
        "datasets",
        "final_means",
        "public",
        "holdout",
        "scorer",
    }
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in forbidden:
                    findings.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in forbidden:
                findings.append(node.module or "")
    return {"findings": findings, "pass": not findings}


def production_flop_proof() -> dict:
    d = PROD_D
    n = PROD_D
    l = PROD_DEPTH
    p = P
    m = M
    total_dirs = p * m
    propagation = total_dirs * l * (2 * n * n + 2 * n)
    outer = p * (20 * d + 64)
    coset_labels = p * (16 * d + 64)
    walsh_materialization = total_dirs * (8 * d + 16)
    final = total_dirs * n + 5 * n
    all_in = propagation + outer + coset_labels + walsh_materialization + final
    cap = UTIL_CAP * BUDGET
    return {
        "dimension": d,
        "depth": l,
        "outer_orbits": p,
        "walsh_rows": m,
        "directions": total_dirs,
        "deep_propagation": propagation,
        "outer_gaussian_abs_bookkeeping": outer,
        "coset_signs_balanced_label_shuffle": coset_labels,
        "walsh_sign_source_materialization": walsh_materialization,
        "final_reduction_materialization": final,
        "all_in_upper": all_in,
        "budget": BUDGET,
        "utilization": all_in / BUDGET,
        "utilization_cap": UTIL_CAP,
        "cap_flops": cap,
        "slack_flops": cap - all_in,
        "expected_all_in": 275297735680,
        "exact_formula_match": all_in == 275297735680,
        "pass": all_in <= cap,
    }


def risk_falsifier() -> dict:
    weights, subnets = assemble_overlapping_network()
    exact_mean, sector_counts = exact_overlapping_mean(subnets)

    candidate_predictions = []
    iid_predictions = []
    ledgers = []

    for seed in CANDIDATE_SEEDS:
        pred, ledger = candidate_estimate(weights, seed)
        candidate_predictions.append(pred)
        ledgers.append(ledger)
    for seed in IID_SEEDS:
        iid_predictions.append(iid_estimate(weights, seed))

    cand = np.stack(candidate_predictions, axis=0)
    iid = np.stack(iid_predictions, axis=0)
    cand_err = cand - exact_mean[None, :]
    iid_err = iid - exact_mean[None, :]
    cand_mse_per = np.mean(cand_err * cand_err, axis=1)
    iid_mse_per = np.mean(iid_err * iid_err, axis=1)
    cand_pooled = float(np.mean(cand_err * cand_err))
    iid_pooled = float(np.mean(iid_err * iid_err))
    ratio = cand_pooled / iid_pooled if iid_pooled > 0.0 else math.inf
    wins = int(np.sum(cand_mse_per < iid_mse_per))

    # exact replay
    cand2 = []
    ledgers2 = []
    for seed in CANDIDATE_SEEDS:
        pred, ledger = candidate_estimate(weights, seed)
        cand2.append(pred)
        ledgers2.append(ledger)
    replay = np.array_equal(cand, np.stack(cand2, axis=0)) and ledgers == ledgers2

    return {
        "exact_mean": exact_mean.tolist(),
        "exact_mean_sha256": sha(exact_mean),
        "subnet_sector_counts": sector_counts,
        "assembled_weight_sha256": [sha(w) for w in weights],
        "candidate_predictions_sha256": sha(cand),
        "iid_predictions_sha256": sha(iid),
        "candidate_mse_per_seed": cand_mse_per.tolist(),
        "iid_mse_per_seed": iid_mse_per.tolist(),
        "candidate_pooled_mse": cand_pooled,
        "iid_pooled_mse": iid_pooled,
        "candidate_over_iid": ratio,
        "candidate_over_raw_target": cand_pooled / RAW_TARGET,
        "iid_over_raw_target": iid_pooled / RAW_TARGET,
        "candidate_wins": wins,
        "candidate_ledgers": ledgers,
        "deterministic_replay_bitwise_exact": bool(replay),
        "all_finite": bool(
            np.isfinite(cand).all()
            and np.isfinite(iid).all()
            and np.isfinite(exact_mean).all()
        ),
    }


def main() -> None:
    law = conditional_walsh_law()
    risk = risk_falsifier()
    flops = production_flop_proof()
    audit = source_audit()

    gates = {
        "all_outputs_finite": risk["all_finite"],
        "conditional_full_sign_coset_mean_le_1e_13": (
            law["full_sign_vs_coset_mean_max_abs"] <= 1e-13
        ),
        "degree1_characters_le_1e_15": law["degree1_max_abs"] <= 1e-15,
        "different_label_degree2_le_1e_15": (
            law["degree2_different_label_max_abs"] <= 1e-15
        ),
        "same_label_degree2_eq_one": (
            law["degree2_same_label_max_abs_from_one"] <= 1e-15
        ),
        "dense_coset_output_spread_positive": law["dense_coset_output_spread"] > 0.0,
        "exact_references_finite": np.isfinite(
            np.asarray(risk["exact_mean"], dtype=np.float64)
        ).all(),
        "deterministic_replay_bitwise_exact": risk["deterministic_replay_bitwise_exact"],
        "candidate_source_audit_clean": audit["pass"],
        "candidate_mse_lt_iid": risk["candidate_pooled_mse"] < risk["iid_pooled_mse"],
        "candidate_over_iid_le_0_90": risk["candidate_over_iid"] <= 0.90,
        "candidate_wins_ge_3_of_4": risk["candidate_wins"] >= 3,
        "production_flops_formula_match": flops["exact_formula_match"],
        "production_util_le_0_13": flops["pass"],
    }
    go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e124.walsh_coset_source_interactions.v1",
        "experiment": "E124",
        "idempotency_key": "ARC-E124-WALSH-COSET-SOURCE-INTERACTIONS-20260920",
        "mechanism": {
            "name": "conditional Walsh-coset source-interaction stratification",
            "walsh_bits": 2,
            "rows_per_orbit": M,
            "outer_orbits": P,
            "deep_propagations": N,
            "target_fit": False,
            "hidden_marginal_moment_closure": False,
            "gaussian_plugin": False,
            "mask_or_boundary_enumeration_candidate": False,
            "haar_plane_orbit": False,
        },
        "exact_conditional_walsh_law": law,
        "exact_gaussian_risk_falsifier": risk,
        "production_flop_proof": flops,
        "candidate_source_audit": audit,
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E124_LOCAL_SCIENTIFIC_GO_CROSS_SOURCE_WALSH_STRATIFICATION"
            if go
            else "E124_TERMINAL_NO_GO_CLOSE_WALSH_COSET_SOURCE_INTERACTION_LANE"
        ),
        "scope": {
            "synthetic_exact_reference_only": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "production_execution": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E124_WALSH_COSET=" + json.dumps(result, sort_keys=True), flush=True)

    # Scientific NO-GO is a valid completed falsifier. Fail only on integrity.
    integrity = [
        "all_outputs_finite",
        "conditional_full_sign_coset_mean_le_1e_13",
        "degree1_characters_le_1e_15",
        "different_label_degree2_le_1e_15",
        "same_label_degree2_eq_one",
        "dense_coset_output_spread_positive",
        "exact_references_finite",
        "deterministic_replay_bitwise_exact",
        "candidate_source_audit_clean",
        "production_flops_formula_match",
        "production_util_le_0_13",
    ]
    if not all(gates[k] for k in integrity):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
