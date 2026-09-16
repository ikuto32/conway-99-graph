"""Exact E0=72 selected-root Q>=3 local expansion and weighted quotient."""

from pathlib import Path

import scratch_general_e75_local_expansion as generic
import scratch_root_e73_q4_port_census as port_engine


def part_path(partition_index):
    return Path(f"scratch_general_e72_q3_local_expansion_part_{partition_index:02d}.json")


def configure():
    # Deficits 1--3 agree with the older E75 tables; E72 additionally needs
    # the deficit-4 state supplied by the extended E73/E72 census engine.
    assert all(
        port_engine.FIBRE_STATES[d] == generic.port75.FIBRE_STATES[d]
        for d in (1, 2, 3)
    )
    generic.port75 = port_engine
    generic.PORT_PATH = Path("scratch_general_e72_q3_port_feasible_states.json")
    generic.COUNT_PATH = Path("scratch_general_e72_q3_local_completion_counts.json")
    generic.OUTPUT_PATH = Path("scratch_general_e72_q3_local_expansion.json")
    generic.REP_PATH = Path("scratch_general_e72_q3_local_graph_reps.json")
    generic.MODEL_E0 = 72
    generic.EXPECTED_SUPPORT_ROWS = 377
    generic.EXPECTED_STATE_ASSIGNMENTS = 15586
    generic.EXPECTED_OVERLAP_EDGES = 24
    generic.EXPECTED_COMPLETIONS = 1018392576
    # The normalized input consists exactly of the necessary Q>=3 states.
    generic.MIN_Q = None
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
