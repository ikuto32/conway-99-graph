"""Exact overlap-matching completion counts for E0=71, Q>=2."""

from pathlib import Path

import scratch_general_e75_local_counts as generic
import scratch_root_e73_q4_port_census as port_engine


def part_path(partition_index):
    return Path(f"scratch_root_e71_q2_local_count_part_{partition_index:02d}.json")


def configure():
    assert all(
        port_engine.FIBRE_STATES[d] == generic.port75.FIBRE_STATES[d]
        for d in (1, 2, 3)
    )
    generic.port75 = port_engine
    generic.INPUT_PATH = Path("scratch_root_e71_q2_port_feasible_states.json")
    generic.OUTPUT_PATH = Path("scratch_root_e71_q2_local_completion_counts.json")
    generic.MODEL_E0 = 71
    generic.EXPECTED_SUPPORT_ROWS = 3220
    generic.EXPECTED_STATE_ASSIGNMENTS = 599222
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
