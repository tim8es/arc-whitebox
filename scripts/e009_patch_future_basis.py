"""Patch pinned upstream V25 with the preregistered E009 basis-sketch policy.

This is diagnostic-only.  The only arithmetic change is the old-tier range-finder
probe matrix at basis rebuilds.  `current` is byte-equivalent to upstream at that
line; `pulled_next` composes the current and next known weight matrices so that the
range finder is seeded by directions the downstream layer will read, expressed in
the correct pre-current-transport coordinate system.
"""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = "                    Om = fnp.copy(w32[:, :r_old])          # fixed sketch (n, r)\n"
NEW = """                    if _os.environ.get(\"E009_SKETCH_POLICY\", \"current\") == \"pulled_next\" and li + 1 < L:
                        next_w32 = mlp.weights[li + 1]
                        if next_w32.dtype != fnp.float32:
                            next_w32 = next_w32.astype(f32)
                        # The range finder lives before the current W transport.
                        # Pull next-layer read directions back through current_w32.
                        Om = w32 @ next_w32[:, :r_old]
                    else:
                        Om = fnp.copy(w32[:, :r_old])          # upstream V25 policy
"""


def patch(source: str) -> str:
    if source.count(OLD) != 1:
        raise RuntimeError(f"expected exactly one V25 sketch marker, found {source.count(OLD)}")
    return source.replace(OLD, NEW, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(patch(args.source.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
