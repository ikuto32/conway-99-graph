"""Exact E0=74 overlap-matching completion counts via the generic engine."""

from pathlib import Path

import scratch_general_e75_local_counts as generic


def part_path(partition_index):
    return Path(f"scratch_general_e74_local_count_part_{partition_index:02d}.json")


def configure():
    generic.INPUT_PATH = Path("scratch_general_e74_port_feasible_states.json")
    generic.OUTPUT_PATH = Path("scratch_general_e74_local_completion_counts.json")
    generic.MODEL_E0 = 74
    generic.EXPECTED_SUPPORT_ROWS = 175
    generic.EXPECTED_STATE_ASSIGNMENTS = 29203
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
