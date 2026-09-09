#!/usr/bin/env bash
set -euo pipefail

DATASET="hf://aicrowd/arc-whestbench-public-2026@v2-phase2"
SPLIT="${1:-mini}"
RUNNER="${2:-local}"

uv run whest validate --estimator estimator.py
uv run whest run \
  --estimator estimator.py \
  --dataset "$DATASET" \
  --split "$SPLIT" \
  --runner "$RUNNER"
