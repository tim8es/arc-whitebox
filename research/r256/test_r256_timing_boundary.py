#!/usr/bin/env python3
"""Single offline R256 regression check for the observed FlopScope 0.12.1 contract."""
from __future__ import annotations

from r256_timing import capture_budget_telemetry, require_residual_wall_time


class FlopScope0121ContractStub:
    """Exact public shape exercised here: summary()->str, residual property->float|None."""

    def __init__(self, residual):
        self._residual = residual

    def summary(self):
        return "flopscope FLOP Budget Summary\nresidual wall time: display-only"

    @property
    def residual_wall_time_s(self):
        return self._residual


def main() -> int:
    measured = capture_budget_telemetry(FlopScope0121ContractStub(0.125))
    assert isinstance(measured["budget_summary"], str)
    assert measured["residual_wall_time_s"] == 0.125
    value, failure = require_residual_wall_time(measured, "candidate")
    assert value == 0.125 and failure is None

    unknown = capture_budget_telemetry(FlopScope0121ContractStub(None))
    value, failure = require_residual_wall_time(unknown, "candidate")
    assert value is None
    assert failure == "candidate_residual_wall_time_unavailable"
    assert unknown["residual_wall_time_s"] is None  # fail-closed: never substitute 0.0

    try:
        capture_budget_telemetry(FlopScope0121ContractStub(float("nan")))
    except ValueError:
        pass
    else:
        raise AssertionError("non-finite residual timing must fail closed")

    print("R256_OFFLINE_REGRESSION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
