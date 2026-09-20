#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e126_adversarial_fixture import (
    all_weights_dense_fraction,
    build_candidate_visible_fixture,
    dense_vs_latent_probe,
    materialize_exact_reference_after_candidate,
    positive_mix_condition_number,
)
from methods.e126_frame_certificate import (
    DELTA,
    RMS_CAP,
    certified_simplex_frame_mean,
    production_cost_upper,
    regular_simplex_code,
    simplex_algebra_metrics,
    spectral_range_envelope_verifier_only,
)

FRAMES = 225
OUT = Path("e126-multisource-frame-certificate.json")
CANDIDATE_PATH = Path("methods/e126_frame_certificate.py")

FIXTURES = (
    {
        "dimension": 8,
        "block_seed_start": 126800,
        "mixing_seed": 126890,
        "probe_seed": 126899,
        "candidate_seeds": (126900, 126901, 126902, 126903),
    },
    {
        "dimension": 16,
        "block_seed_start": 1261600,
        "mixing_seed": 1261690,
        "probe_seed": 1261699,
        "candidate_seeds": (1261700, 1261701, 1261702, 1261703),
    },
)


def sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def rms(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.sqrt(np.mean(d * d)))


def source_firewall() -> dict:
    source = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    dangerous: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                dangerous.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    x in name
                    for x in (
                        "read_text",
                        "read_bytes",
                        "urlopen",
                        "request",
                        "download",
                    )
                ):
                    dangerous.append(name)

    forbidden_terms = (
        "e126_adversarial_fixture",
        "e123_multisource_verifier_fixture",
        "e114",
        "dataset",
        "scorer",
        "requests",
        "urllib",
        "http",
    )
    forbidden = [
        imp for imp in imports
        if any(term in imp.lower() for term in forbidden_terms)
    ]
    return {
        "candidate_path": str(CANDIDATE_PATH),
        "candidate_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden,
        "dangerous_io_or_network_calls": dangerous,
        "passes": bool(not forbidden and not dangerous),
    }


def spectral_certificate(
    frame_values: np.ndarray,
    spectral_range: np.ndarray,
    *,
    delta: float,
) -> dict:
    x = np.asarray(frame_values, dtype=np.float64)
    p, m = x.shape
    sample_variance = np.var(x, axis=0, ddof=1)
    logterm = math.log(4.0 * float(m) / float(delta))
    variance_term = np.sqrt(2.0 * sample_variance * logterm / float(p))
    range_term = (
        7.0 * np.asarray(spectral_range, dtype=np.float64) * logterm
        / (3.0 * float(p - 1))
    )
    radii = variance_term + range_term
    return {
        "rms": float(np.sqrt(np.mean(radii * radii))),
        "range_penalty_rms": float(
            np.sqrt(np.mean(range_term * range_term))
        ),
        "variance_only_rms": float(
            np.sqrt(np.mean(variance_term * variance_term))
        ),
        "range_max": float(np.max(spectral_range)),
    }


def compact_candidate(out) -> dict:
    return {
        "mean_sha256": sha(out.mean),
        "frame_contributions_sha256": sha(out.frame_contributions),
        "sample_variance_sha256": sha(out.sample_variance),
        "frobenius_range_sha256": sha(out.frobenius_range),
        "coordinate_radii_sha256": sha(out.coordinate_radii),
        "rms_certificate": out.rms_certificate,
        "variance_only_rms": out.variance_only_rms,
        "frame_orthogonality_max_abs": out.frame_orthogonality_max_abs,
        "source_direction_norm_max_abs": out.source_direction_norm_max_abs,
        "observed_range_violation_max_abs": out.observed_range_violation_max_abs,
        "frobenius_range_max": float(np.max(out.frobenius_range)),
        "sample_variance_mean": float(np.mean(out.sample_variance)),
        "sample_variance_max": float(np.max(out.sample_variance)),
        "ledger": out.ledger,
        "finite": out.finite,
    }


def main() -> None:
    firewall = source_firewall()
    simplex = simplex_algebra_metrics(regular_simplex_code())

    # Candidate-visible fixture construction does not materialize exact means.
    states = []
    all_candidate_records = []
    integrity_ok = True

    for cfg in FIXTURES:
        state = build_candidate_visible_fixture(
            dimension=cfg["dimension"],
            block_seed_start=cfg["block_seed_start"],
            mixing_seed=cfg["mixing_seed"],
        )
        states.append((cfg, state))

        probe = dense_vs_latent_probe(
            state,
            seed=cfg["probe_seed"],
            samples=128,
        )
        densities = all_weights_dense_fraction(state)
        cond = positive_mix_condition_number(state)
        spectral_env = spectral_range_envelope_verifier_only(
            state.dense_weights
        )

        records = []
        for seed in cfg["candidate_seeds"]:
            cand = certified_simplex_frame_mean(
                state.dense_weights,
                frames=FRAMES,
                seed=seed,
                delta=DELTA,
            )
            replay = certified_simplex_frame_mean(
                state.dense_weights,
                frames=FRAMES,
                seed=seed,
                delta=DELTA,
            )

            deterministic = bool(
                np.array_equal(cand.mean, replay.mean)
                and np.array_equal(
                    cand.frame_contributions,
                    replay.frame_contributions,
                )
                and np.array_equal(
                    cand.coordinate_radii,
                    replay.coordinate_radii,
                )
                and cand.rms_certificate == replay.rms_certificate
                and cand.variance_only_rms == replay.variance_only_rms
                and cand.ledger == replay.ledger
            )
            spec_cert = spectral_certificate(
                cand.frame_contributions,
                spectral_env,
                delta=DELTA,
            )

            integrity_ok = bool(
                integrity_ok
                and cand.finite
                and deterministic
                and cand.observed_range_violation_max_abs <= 1e-12
            )
            records.append(
                {
                    "seed": seed,
                    "candidate": compact_candidate(cand),
                    "deterministic_replay_exact": deterministic,
                    "spectral_range_verifier_only": spec_cert,
                    "_mean": cand.mean.copy(),
                }
            )

        all_candidate_records.append(
            {
                "dimension": cfg["dimension"],
                "fixture_weights_sha256": state.fixture_weights_sha256,
                "dense_vs_latent_probe_max_abs": probe,
                "positive_mix_condition_number": cond,
                "per_weight_dense_fraction": densities,
                "all_weights_dense_fraction_min": min(densities),
                "spectral_range_max": float(np.max(spectral_env)),
                "records": records,
            }
        )
        integrity_ok = bool(
            integrity_ok
            and probe <= 1e-10
            and cond >= 99.999999
            and min(densities) >= 0.99
        )

    # Exact references are materialized only after every candidate and
    # certificate record above has been frozen in memory.
    reference_records = []
    tight_all = True
    var_floor_all = True
    coverage_all = True

    for (cfg, state), fixture_record in zip(states, all_candidate_records):
        exact = materialize_exact_reference_after_candidate(state)
        exact_hash = sha(exact)
        per_seed = []

        for record in fixture_record["records"]:
            actual = rms(record["_mean"], exact)
            cert = float(record["candidate"]["rms_certificate"])
            var_floor = float(record["candidate"]["variance_only_rms"])
            spectral_cert = float(
                record["spectral_range_verifier_only"]["rms"]
            )
            covered = actual <= cert
            cert_tight = cert <= RMS_CAP
            var_tight = var_floor <= RMS_CAP

            coverage_all = coverage_all and covered
            tight_all = tight_all and cert_tight
            var_floor_all = var_floor_all and var_tight

            per_seed.append(
                {
                    "seed": record["seed"],
                    "actual_rms_error_verifier_only": actual,
                    "actual_rms_over_target": actual / RMS_CAP,
                    "target_free_certificate": cert,
                    "certificate_over_target": cert / RMS_CAP,
                    "certificate_over_actual": (
                        cert / actual if actual > 0.0 else math.inf
                    ),
                    "variance_only_rms": var_floor,
                    "variance_only_over_target": var_floor / RMS_CAP,
                    "spectral_range_certificate_verifier_only": spectral_cert,
                    "spectral_certificate_over_target": (
                        spectral_cert / RMS_CAP
                    ),
                    "actual_error_le_certificate": covered,
                    "certificate_le_target": cert_tight,
                    "variance_only_floor_le_target": var_tight,
                }
            )
            del record["_mean"]

        reference_records.append(
            {
                "dimension": cfg["dimension"],
                "exact_mean_sha256": exact_hash,
                "per_seed": per_seed,
                "max_actual_rms_error": max(
                    x["actual_rms_error_verifier_only"] for x in per_seed
                ),
                "min_actual_rms_error": min(
                    x["actual_rms_error_verifier_only"] for x in per_seed
                ),
                "min_target_free_certificate": min(
                    x["target_free_certificate"] for x in per_seed
                ),
                "min_variance_only_rms": min(
                    x["variance_only_rms"] for x in per_seed
                ),
            }
        )

    p225 = production_cost_upper(225)
    p226 = production_cost_upper(226)
    production_gate = bool(p225["passes_cap"] and not p226["passes_cap"])

    algebra_gate = bool(
        simplex["max_vertex_norm_error"] <= 2e-14
        and simplex["max_vertex_gram_error"] <= 2e-14
        and simplex["vertex_sum_inf"] <= 2e-14
        and simplex["second_moment_max_abs_error"] <= 2e-14
    )

    gates = {
        "source_firewall_pass": firewall["passes"],
        "simplex_algebra_pass": algebra_gate,
        "fixture_and_candidate_integrity_pass": integrity_ok,
        "posthoc_coverage_check_all": coverage_all,
        "target_free_certificate_le_raw_rms_target_all": tight_all,
        "optimistic_variance_only_floor_le_raw_rms_target_all": (
            var_floor_all
        ),
        "production_p225_pass_and_p226_fail": production_gate,
        "no_public_benchmark_scorer_holdout_full": True,
    }

    integrity_gates = (
        gates["source_firewall_pass"]
        and gates["simplex_algebra_pass"]
        and gates["fixture_and_candidate_integrity_pass"]
        and gates["posthoc_coverage_check_all"]
        and gates["production_p225_pass_and_p226_fail"]
        and gates["no_public_benchmark_scorer_holdout_full"]
    )

    scientific_go = bool(
        integrity_gates
        and gates["target_free_certificate_le_raw_rms_target_all"]
        and gates["optimistic_variance_only_floor_le_raw_rms_target_all"]
    )

    if not integrity_gates:
        decision = "TERMINAL_INTEGRITY_NO_GO"
    elif scientific_go:
        decision = "E126_THEORY_CERTIFICATE_GO"
    else:
        decision = (
            "TERMINAL_NO_GO_FINITE_SAMPLE_CERTIFICATE_NOT_TIGHT_ENOUGH_"
            "UNDER_PRODUCTION_BUDGET"
        )

    result = {
        "schema": "arc.whitebox.e126.multisource_frame_certificate.v1",
        "experiment": "E126",
        "idempotency_key": (
            "ARC-E126-MULTISOURCE-FRAME-CERTIFICATE-20260920"
        ),
        "certificate": {
            "confidence": 1.0 - DELTA,
            "delta": DELTA,
            "coordinate_formula": (
                "sqrt(2*s_j^2*log(4m/delta)/P) + "
                "7*B_j*log(4m/delta)/(3(P-1))"
            ),
            "range_formula": (
                "B_j=E[chi_d]*prod_{l<L}||W_l||_F*||W_L[:,j]||_2"
            ),
            "familywise_rms": "sqrt(mean_j radius_j^2)",
            "variance_only_floor": (
                "sqrt(mean_j 2*s_j^2*log(4m/delta)/P)"
            ),
            "raw_mse_cap": 1.89e-8,
            "raw_rms_cap": RMS_CAP,
            "target_free": True,
            "arbitrary_dense_weights": True,
        },
        "simplex_algebra": simplex,
        "firewall": firewall,
        "candidate_phase": all_candidate_records,
        "verifier_only_exact_reference_phase": reference_records,
        "production_cost": {
            "p225": p225,
            "p226": p226,
            "max_budget_admissible_frames": 225,
        },
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": decision,
        "scope": {
            "synthetic_adversarial_only": True,
            "production_execution": False,
            "public": False,
            "public_mini": False,
            "benchmark_targets": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E126_FRAME_CERTIFICATE=" + json.dumps(result, sort_keys=True), flush=True)

    if not integrity_gates:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
