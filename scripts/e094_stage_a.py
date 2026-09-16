from __future__ import annotations

import json
from pathlib import Path

from methods.e094_source_axis import run_stage_a


def main() -> None:
    result = run_stage_a()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    Path("e094-stage-a.json").write_text(payload, encoding="utf-8")
    print("E094_STAGE_A_JSON=" + json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "STAGE_A_GO" else 1)


if __name__ == "__main__":
    main()
