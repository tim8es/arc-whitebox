from __future__ import annotations

import json
from pathlib import Path

BUDGET = 2**41
UTIL_LIMIT = 0.135
RAW_TARGET = 1.89e-8

# Verified E051 reproduction provenance / metrics.
E051_COMMIT = "642b6b0f5ec549a3c0f9e3fdb54fbae09a000133"
E051_RUN = 35097946492
E051_JOB = 104799875919
E051_ARTIFACT = 10446649484
E051_RAW = 2.29004485946887e-8
E051_UTIL = 0.267056

# Frozen E091 production bridge ceiling (p=16, width=1024).
WIDTH = 1024
P = 16
FEATURE_FLOPS_CEILING = 16 * WIDTH * WIDTH
CORRECTION_FLOPS_CEILING = 2 * P * WIDTH
BRIDGE_FLOPS_CEILING = FEATURE_FLOPS_CEILING + CORRECTION_FLOPS_CEILING
BRIDGE_UTIL_CEILING = BRIDGE_FLOPS_CEILING / BUDGET


def main() -> None:
    # Any deployable E091-on-E051 candidate is additive to the E051 base path.
    # Therefore the complete utilization is bounded below by the measured E051
    # utilization even if feature extraction and correction were magically free.
    complete_util_lower_bound = E051_UTIL
    optimistic_zero_cost_bridge_pass = complete_util_lower_bound <= UTIL_LIMIT

    reported_e051_flops_equiv = E051_UTIL * BUDGET
    util_excess = E051_UTIL - UTIL_LIMIT
    excess_flops_equiv = util_excess * BUDGET
    required_raw_reduction = 1.0 - RAW_TARGET / E051_RAW

    result = {
        "schema": "arc.whitebox.e091.e051_base_feasibility.v1",
        "experiment": "E091",
        "candidate": "frozen E091 additive residual bridge on verified E051 base",
        "e051": {
            "commit": E051_COMMIT,
            "run": E051_RUN,
            "job": E051_JOB,
            "artifact": E051_ARTIFACT,
            "raw_final_mse": E051_RAW,
            "reported_all_in_utilization": E051_UTIL,
            "reported_flops_equivalent_from_utilization": reported_e051_flops_equiv,
        },
        "e091_bridge": {
            "p": P,
            "width": WIDTH,
            "feature_flops_ceiling": FEATURE_FLOPS_CEILING,
            "correction_flops_ceiling": CORRECTION_FLOPS_CEILING,
            "bridge_flops_ceiling": BRIDGE_FLOPS_CEILING,
            "bridge_utilization_ceiling": BRIDGE_UTIL_CEILING,
            "additive_nonnegative_cost_assumption": True,
        },
        "targets": {
            "complete_utilization_max": UTIL_LIMIT,
            "raw_final_mse_max": RAW_TARGET,
        },
        "lower_bound": {
            "complete_utilization_even_with_free_bridge": complete_util_lower_bound,
            "utilization_excess_over_limit": util_excess,
            "excess_flops_equivalent": excess_flops_equiv,
            "e051_raw_relative_reduction_needed": required_raw_reduction,
        },
        "gates": {
            "e051_base_alone_meets_complete_utilization": E051_UTIL <= UTIL_LIMIT,
            "optimistic_zero_cost_bridge_meets_complete_utilization": optimistic_zero_cost_bridge_pass,
            "e051_base_raw_meets_target": E051_RAW <= RAW_TARGET,
        },
        "decision": "STRICT_NO_GO_E051_AS_E091_PRODUCTION_BASE",
        "scientific_scope": (
            "This closes only the E051-as-production-base variant. It does not invalidate "
            "the separately frozen E043-based E091 bridge. No public/scorer/holdout/full data "
            "is read by this benchmark."
        ),
    }

    # The strict NO-GO must be logically forced by cost, not by a soft threshold.
    if optimistic_zero_cost_bridge_pass:
        raise RuntimeError("expected E051 base utilization to exceed the complete E091 limit")
    if not (E051_UTIL > UTIL_LIMIT):
        raise RuntimeError("strict lower-bound premise failed")

    Path("e091-e051-base-feasibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("E091_E051_BASE_FEASIBILITY=" + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
