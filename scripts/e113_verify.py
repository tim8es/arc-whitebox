from __future__ import annotations

import json
import math
from pathlib import Path

P = Path("e113-exact-gate.json")


def main() -> None:
    x = json.loads(P.read_text(encoding="utf-8"))
    assert x["schema"] == "arc.whitebox.e113.top4_gate_conditioned_exact_gate.v1"
    assert x["network"] == {
        "latent_dim": 2,
        "width": 8,
        "depth": 4,
        "weight_seed": 113113,
        "zero_bias": True,
        "topk_parent_gates": 4,
        "state_count": 16,
    }
    assert len(x["layers"]) == 4
    assert x["reference"]["monte_carlo"] is False
    assert x["reference"]["numerical_quadrature"] is False
    assert x["aggregate"]["max_state_probability_abs_error"] <= 1e-14
    assert x["aggregate"]["deterministic_repeat_max_abs"] == 0.0
    assert x["cost_admission"]["all_in_upper_flops"] == 151720512434
    assert x["cost_admission"]["utilization"] < 0.13
    assert math.isfinite(x["aggregate"]["final_conditional_bias_mse"])
    expected = (
        "SMALL_EXACT_SCIENTIFIC_GO"
        if all(x["gates"].values())
        else "TERMINAL_NO_GO_DROP"
    )
    assert x["decision"] == expected
    print(json.dumps({
        "verified": True,
        "decision": x["decision"],
        "final_conditional_bias_mse": x["aggregate"]["final_conditional_bias_mse"],
        "final_gaussian_bias_mse": x["aggregate"]["final_gaussian_bias_mse"],
        "utilization_upper": x["cost_admission"]["utilization"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
