from __future__ import annotations

import json
import math
from pathlib import Path

P = Path("e112-exact-gate.json")


def main() -> None:
    x = json.loads(P.read_text(encoding="utf-8"))
    assert x["schema"] == "arc.whitebox.e112.edgeworth4_exact_gate.v1"
    assert x["network"] == {
        "latent_dim": 2,
        "width": 8,
        "depth": 4,
        "weight_seed": 112112,
        "zero_bias": True,
    }
    assert len(x["layers"]) == 4
    assert x["reference"]["monte_carlo"] is False
    assert x["reference"]["numerical_quadrature"] is False
    assert x["cost_admission"]["all_in_upper_flops"] == 149720512434
    assert x["cost_admission"]["utilization"] < 0.13
    assert x["aggregate"]["deterministic_repeat_max_abs"] == 0.0
    assert math.isfinite(x["aggregate"]["final_edgeworth4_bias_mse"])
    assert math.isfinite(x["aggregate"]["final_gaussian_bias_mse"])
    expected = (
        "SMALL_EXACT_SCIENTIFIC_GO"
        if all(x["gates"].values())
        else "TERMINAL_NO_GO_DROP"
    )
    assert x["decision"] == expected
    print(json.dumps({
        "verified": True,
        "decision": x["decision"],
        "final_edgeworth4_bias_mse": x["aggregate"]["final_edgeworth4_bias_mse"],
        "final_gaussian_bias_mse": x["aggregate"]["final_gaussian_bias_mse"],
        "utilization_upper": x["cost_admission"]["utilization"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
