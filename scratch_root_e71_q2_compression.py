"""Selected-root E0=71, Q>=2 support-compression census.

This is the next branch below the active E0=72 frontier.  It reuses the
audited checkpointed compression engine with all constants independently
recomputed for total deficit 13.  Running ``--plan`` is cheap; individual
partition scans remain explicit and resumable.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import scratch_root_e73_q4_compression as generic


MASTER_PATH = Path("scratch_root_e71_q2_compression_audit.json")
PLAN_PATH = Path("scratch_root_e71_q2_compression_plan.json")


def part_path(index):
    return Path(f"scratch_root_e71_q2_compression_part_{index:02d}.json")


def theorem_inputs():
    free_target = Fraction(71, 2)
    free = generic.spectral_endpoint_maximizer(
        14, Fraction(-4), Fraction(3), free_target
    )
    free_square = sum(value * value for value in free)
    assert free == [Fraction(3)] * 13 + [Fraction(-7, 2)]
    assert free_square == Fraction(517, 4)
    assert 4756 == 16 * (12**2 + 6 * 2**2 + free_square)
    assert 3152 == 3360 - 16 * 13
    return {
        "external_premise_required": False,
        "self_contained_root_reduction": "every putative SRG has a root with S(r)<=69",
        "root_implication": "E0=71 and S(r)<=69 imply Q=E0-S>=2",
        "side_bound_audit": "scratch_root_side_bound_selfcontained_audit.json",
        "total_deficit": 13,
        "total_fibre_edges_E0": 71,
        "required_diagonal_edges_Q": ">=2",
        "free_Ritz_interval": ["-4", "3"],
        "free_Ritz_sum": str(free_target),
        "spectral_maximizing_free_Ritz_multiset": [str(value) for value in free],
        "free_Ritz_maximum_square_sum": str(free_square),
        "spectral_D_square_upper": 4756,
        "disjoint_constant_derivation": "3360-16*13=3152",
        "trace_identity": (
            "tr(D^2)=sum_F(8-2*delta_F)^2+3152+"
            "2*(overlap_square+x_square)"
        ),
        "BP_overlap_row_sum": "4*delta_F",
        "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        "weighted_port_balance": (
            "at every root group, 2*max(incident delta)<=sum(incident delta)"
        ),
        "partition_Q_capacity": "2*(number of delta2 fibres)+(number of delta3 fibres)",
        "external_n3_bound_used": False,
        "legacy_schema_note": (
            "fields named passes_Q_at_least_4_capacity are engine compatibility "
            "fields and mean passes configured Q>=2 in this artifact"
        ),
    }


def configure():
    generic.TOTAL_DEFICIT = 13
    generic.E0 = 71
    generic.Q_MIN = 2
    generic.S_MAX = 69
    generic.SPECTRAL_UPPER = 4756
    generic.DISJOINT_CONSTANT = 3152
    generic.PARTITIONS = generic.integer_partitions(13)
    generic.MASTER_PATH = MASTER_PATH
    generic.PLAN_PATH = PLAN_PATH
    generic.part_path = part_path
    generic.theorem_inputs = theorem_inputs

    original_plan = generic.plan_document
    original_refresh = generic.refresh_scope_fields
    original_excluded = generic.excluded_result
    original_scanning = generic.scanning_checkpoint
    original_merge = generic.merge_parts

    def plan_document():
        result = original_plan()
        result["model"] = "self-contained-root-reduced E0=71,Q>=2 support-partition plan"
        result["schema_compatibility"] = theorem_inputs()["legacy_schema_note"]
        result["claim_boundary"] = (
            "Q>=2 follows from the audited S<=69 theorem; this is a necessary "
            "branch census, not an E0=71 exclusion."
        )
        return result

    def refresh_scope_fields(result):
        original_refresh(result)
        result["model"] = "self-contained-root-reduced E0=71,Q>=2 exact compression partition"
        result["theorem_inputs"] = theorem_inputs()
        result["schema_compatibility"] = theorem_inputs()["legacy_schema_note"]
        result["claim_boundary"] = "Necessary E0=71,Q>=2 selected-root branch only."
        return result

    def excluded_result(index, partition, plan_row):
        return refresh_scope_fields(original_excluded(index, partition, plan_row))

    def scanning_checkpoint(index, partition, plan_row):
        return refresh_scope_fields(original_scanning(index, partition, plan_row))

    def merge_parts():
        result = original_merge()
        result["model"] = "self-contained-root-reduced E0=71,Q>=2 merged exact support compression"
        result["theorem_inputs"] = theorem_inputs()
        result["schema_compatibility"] = theorem_inputs()["legacy_schema_note"]
        result["claim_boundary"] = "Necessary E0=71,Q>=2 selected-root branch only."
        generic.atomic_json(MASTER_PATH, result)
        return result

    generic.plan_document = plan_document
    generic.refresh_scope_fields = refresh_scope_fields
    generic.excluded_result = excluded_result
    generic.scanning_checkpoint = scanning_checkpoint
    generic.merge_parts = merge_parts


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
