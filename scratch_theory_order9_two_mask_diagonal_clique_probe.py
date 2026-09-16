"""Bounded clique probe for the six minimum-deficit rooted flags.

Only the two H9 masks common to their diagonals are provisionally added to
the certified 35-column universe.  The 21 products among the six fixed flags
are scanned.  This is not an ambient order-nine census.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path

import scratch_theory_order9_cross_x_closure as base


OUTPUT = Path("scratch_theory_order9_two_mask_diagonal_clique_probe.json")
R0_CERT = Path("scratch_theory_order9_r0_closure.json")
CROSS_CERT = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")

FLAGS = (24699, 24939, 25147, 25507, 27179, 27299)
DIAGONAL_MASKS = (46817920192, 56196485312)


def sha(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            state.update(chunk)
    return state.hexdigest()


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    r0 = json.loads(R0_CERT.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    visible = tuple(map(int, deck["T0_all_G_targeted_order9_projection"]
                        ["visible_19_H9_masks"]))
    old9 = tuple(map(int, json.loads(CROSS_CERT.read_text(
        encoding="utf-8"
    ))["added_nine_masks"]))
    r0seven = tuple(map(int, r0["added_seven_masks"]))
    universe35 = set(visible + old9 + r0seven)
    universe37 = universe35 | set(DIAGONAL_MASKS)
    assert len(universe35) == 35 and len(universe37) == 37

    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    deletion_decks = []
    all_shadows = set()
    for mask in DIAGONAL_MASKS:
        assert base.canonical(mask, 9) == mask and base.pair_upper(mask, 9)
        histogram = Counter()
        slots = []
        for removed in range(9):
            raw8, _ = base.delete(mask, 9, removed)
            shadow = base.canonical(raw8, 8)
            assert shadow in frozen8_set
            histogram[shadow] += 1
            all_shadows.add(shadow)
            slots.append({
                "deleted_vertex": removed,
                "canonical_order8_mask": shadow,
                "frozen_order8_index_0_based": frozen8.index(shadow),
                "wave163_order8_count": x8[shadow],
            })
        deletion_decks.append({
            "canonical_order9_mask": mask,
            "deletion_histogram": [[key, value]
                                   for key, value in sorted(histogram.items())],
            "vertex_deletions": slots,
        })
    assert all(x8[shadow] > 0 for shadow in all_shadows)

    rows = []
    closed_edges = []
    deficit_histogram = Counter()
    for left, right in itertools.combinations_with_replacement(range(6), 2):
        support = base.completion_support(FLAGS[left], FLAGS[right])
        outside35 = sorted(support - universe35)
        outside37 = sorted(support - universe37)
        if left == right:
            assert outside35 == list(DIAGONAL_MASKS)
            assert not outside37
        else:
            deficit_histogram[len(outside37)] += 1
            if not outside37:
                closed_edges.append((left, right))
        rows.append({
            "left_flag_index": left,
            "right_flag_index": right,
            "left_flag_mask": FLAGS[left],
            "right_flag_mask": FLAGS[right],
            "canonical_support_size": len(support),
            "outside_35_masks": outside35,
            "outside_37_masks": outside37,
            "closed_on_37": not outside37,
        })
    assert not closed_edges
    assert deficit_histogram == Counter({2: 6, 9: 6, 15: 3})

    two_deficit_rows = [row for row in rows
                        if row["left_flag_index"] != row["right_flag_index"]
                        and len(row["outside_37_masks"]) == 2]
    missing_pair_orbits = Counter(
        tuple(row["outside_37_masks"]) for row in two_deficit_rows
    )
    assert missing_pair_orbits == Counter({
        (46748225728, 47606550720): 3,
        (14681719440, 56449716416): 3,
    })

    result = {
        "status": "no-nontrivial-clique-on-shared-two-mask-diagonal-extension",
        "scope": {
            "base_order9_columns": 35,
            "provisional_diagonal_columns": 2,
            "fixed_rooted_flags": 6,
            "ambient_order9_census_generated": False,
            "frozen_order8_classes_regenerated": False,
            "submission_txt_written": False,
        },
        "inputs": {str(path): {"sha256": sha(path)}
                   for path in (R0_CERT, CROSS_CERT, DECK, WAVE147, WAVE163)},
        "flag_masks": list(FLAGS),
        "shared_diagonal_masks": list(DIAGONAL_MASKS),
        "shared_diagonal_mask_deletion_decks": {
            "slots_checked": 18,
            "distinct_frozen_order8_shadows": len(all_shadows),
            "all_deletions_in_frozen_916": True,
            "all_shadow_Wave163_counts_positive": True,
            "decks": deletion_decks,
        },
        "complete_six_flag_product_scan": {
            "products_checked": len(rows),
            "diagonals_closed_on_37": 6,
            "off_diagonal_products_checked": 15,
            "closed_off_diagonal_products": [],
            "closure_graph_edge_count": 0,
            "maximum_clique_size": 1,
            "nontrivial_2x2_or_larger_closed_clique_exists": False,
            "off_diagonal_deficit_histogram": {
                str(key): value for key, value in sorted(deficit_histogram.items())
            },
            "rows": rows,
        },
        "next_exact_boundary": {
            "minimum_additional_masks_for_one_cross_product": 2,
            "two_minimum_missing_mask_pairs": [
                [14681719440, 56449716416],
                [46748225728, 47606550720],
            ],
            "cross_products_per_pair": 3,
            "meaning": (
                "Adding either pair would close three disjoint off-diagonal "
                "products and create 2x2 blocks; no such pair is introduced "
                "or evaluated in this probe."
            ),
        },
        "claim_boundary": {
            "negative_direction_tested": False,
            "reason": (
                "The shared two diagonal masks close no off-diagonal product, "
                "so there is no licensed nontrivial Gram block to evaluate."
            ),
            "R1_extension_attempted": False,
        },
    }
    save(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "products": len(rows),
        "closed_cross_edges": len(closed_edges),
        "maximum_clique": 1,
        "minimum_cross_deficit": 2,
    }, indent=2))


if __name__ == "__main__":
    main()
