"""Unique entry point for the corrected independent E0=80 CP-SAT model."""

from pathlib import Path

import scratch_general_e80_compact_cpsat as implementation


if __name__ == "__main__":
    implementation.RESULT_PATH = Path("scratch_general_e80_corrected_cpsat.json")
    implementation.main()
