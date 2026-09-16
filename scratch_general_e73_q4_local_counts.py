"""Exact E0=73 root-side Q>=4 overlap-completion counts."""

from pathlib import Path

import scratch_general_e75_local_counts as generic


def part_path(partition_index):
    return Path(f"scratch_general_e73_q4_local_count_part_{partition_index:02d}.json")


def configure():
    generic.INPUT_PATH = Path("scratch_general_e73_q4_port_feasible_states.json")
    generic.OUTPUT_PATH = Path("scratch_general_e73_q4_local_completion_counts.json")
    generic.MODEL_E0 = 73
    generic.EXPECTED_SUPPORT_ROWS = 58
    generic.EXPECTED_STATE_ASSIGNMENTS = 980
    generic.part_path = part_path


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
