"""Exact E0=72 root-side Q>=3 overlap-completion counts."""

from pathlib import Path

import scratch_general_e75_local_counts as generic
import scratch_root_e73_q4_port_census as port_engine


def part_path(partition_index):
    return Path(f"scratch_general_e72_q3_local_count_part_{partition_index:02d}.json")


def configure():
    # The E75 engine only needed deficits 1--3.  E72 also has the unique
    # deficit-4 fibre state, so use the extended, otherwise identical census
    # tables when reconstructing signatures and diagonal counts.
    assert all(
        port_engine.FIBRE_STATES[d] == generic.port75.FIBRE_STATES[d]
        for d in (1, 2, 3)
    )
    generic.port75 = port_engine
    generic.INPUT_PATH = Path("scratch_general_e72_q3_port_feasible_states.json")
    generic.OUTPUT_PATH = Path("scratch_general_e72_q3_local_completion_counts.json")
    generic.MODEL_E0 = 72
    generic.EXPECTED_SUPPORT_ROWS = 377
    generic.EXPECTED_STATE_ASSIGNMENTS = 15586
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
