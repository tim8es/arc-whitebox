from __future__ import annotations

import json
from pathlib import Path

from methods.e116_output_specific_transport import canonical_json, run_frozen_payload

OUT = Path("e116-output-specific-gradient-span.json")


def main() -> None:
    first = run_frozen_payload()
    second = run_frozen_payload()
    replay_exact = canonical_json(first) == canonical_json(second)

    first["gates"]["deterministic_replay_exact"] = replay_exact
    integrity_ok = all(first["gates"].values())
    first["decision"] = (
        "TERMINAL_STRUCTURAL_NO_GO_FIXED_LINEAR_OUTPUT_TRANSPORT"
        if integrity_ok
        else "INSTRUMENT_NO_GO"
    )
    first["determinism"] = {"canonical_payload_replay_exact": replay_exact}

    OUT.write_text(
        json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "E116_OUTPUT_SPECIFIC_GRADIENT_SPAN="
        + json.dumps(first, sort_keys=True),
        flush=True,
    )
    if not integrity_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
