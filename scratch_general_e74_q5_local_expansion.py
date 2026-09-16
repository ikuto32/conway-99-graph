"""Conditional-priority E0=74 local expansion restricted to Q>=5.

This is not an unconditional exclusion artifact.  It accepts the externally
supplied premise implying Q>=5 only to prioritize exact local representatives.
"""

from pathlib import Path

import scratch_general_e75_local_expansion as generic


def part_path(partition_index):
    return Path(f"scratch_general_e74_q5_local_expansion_part_{partition_index:02d}.json")


def configure():
    generic.PORT_PATH = Path("scratch_general_e74_port_feasible_states.json")
    generic.COUNT_PATH = Path("scratch_general_e74_local_completion_counts.json")
    generic.OUTPUT_PATH = Path("scratch_general_e74_q5_local_expansion.json")
    generic.REP_PATH = Path("scratch_general_e74_q5_local_graph_reps.json")
    generic.MODEL_E0 = 74
    generic.EXPECTED_SUPPORT_ROWS = 11
    generic.EXPECTED_STATE_ASSIGNMENTS = 89
    generic.EXPECTED_OVERLAP_EDGES = 20
    generic.EXPECTED_COMPLETIONS = 1461248
    generic.MIN_Q = 5
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
