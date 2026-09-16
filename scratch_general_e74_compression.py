"""Checkpointed exact fibre-compression audit for E0=74 (deficit ten).

This is a parameterized reuse of the audited E75 enumerator.  Every integer
partition is first classified from *all* labelled placements into exact
weighted S7 orbits and atomically checkpointed.  Filtering then records the
orientation-independent weighted port obstruction, exact overlap recursion,
and exact-Fraction disjoint real relaxation one completed orbit at a time.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import scratch_general_e75_compression as generic


TOTAL_DEFICIT = 10
E0 = 84 - TOTAL_DEFICIT
SPECTRAL_UPPER = 4624
DISJOINT_CONSTANT = 3200
PARTITIONS = generic.integer_partitions(TOTAL_DEFICIT, 4)


def part_path(index):
    return Path(f"scratch_general_e74_compression_part_{index:02d}.json")


def configure():
    """Set the generic engine's audited problem constants and artifact names."""
    assert E0 == 74
    assert len(PARTITIONS) == 23
    assert sum(Fraction(value) for value in ([3] * 13 + [-2])) == Fraction(E0, 2)
    assert sum(Fraction(value) ** 2 for value in ([3] * 13 + [-2])) == 121
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + 121)
    assert DISJOINT_CONSTANT == 3360 - 16 * TOTAL_DEFICIT

    generic.PARTITIONS = PARTITIONS
    generic.TOTAL_DEFICIT = TOTAL_DEFICIT
    generic.E0 = E0
    generic.SPECTRAL_UPPER = SPECTRAL_UPPER
    generic.DISJOINT_CONSTANT = DISJOINT_CONSTANT
    generic.MASTER_PATH = Path("scratch_general_e74_compression_audit.json")
    # Each write remains atomic, while ten-row batches avoid rewriting a
    # multi-megabyte partition file thousands of times.  A crash can lose at
    # most nine already computed (deterministic) filters.
    generic.CHECKPOINT_EVERY = 10
    generic.part_path = part_path

    theorem = generic.theorem_inputs()
    assert theorem["spectral_maximizing_free_Ritz_multiset"] == ["3"] * 13 + ["-2"]
    assert theorem["free_Ritz_maximum_square_sum"] == "121"


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
