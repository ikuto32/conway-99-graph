"""Unique entry point for the corrected exact E0=80 SAT model."""

from pathlib import Path

import scratch_general_e80_compact_sat as implementation


if __name__ == "__main__":
    implementation.RESULT_PATH = Path("scratch_general_e80_corrected_sat_portfolio.json")
    implementation.main()
