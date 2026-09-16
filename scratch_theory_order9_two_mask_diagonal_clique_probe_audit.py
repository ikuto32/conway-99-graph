"""Independent replay of the six-flag/two-mask clique probe.

The probe producer is not imported.  Graph primitives are reused from the
already independent R0 audit module.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path

from scratch_theory_order9_r0_closure_audit import (
    canonical,
    delete_vertex,
    glue_support,
    locally_upper,
)


CERTIFICATE = Path("scratch_theory_order9_two_mask_diagonal_clique_probe.json")
R0_CERT = Path("scratch_theory_order9_r0_closure.json")
CROSS_CERT = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
OUTPUT = Path("scratch_theory_order9_two_mask_diagonal_clique_probe_audit.json")


def sha(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            state.update(chunk)
    return state.hexdigest()


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    r0 = json.loads(R0_CERT.read_text(encoding="utf-8"))
    cross = json.loads(CROSS_CERT.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    for path in (R0_CERT, CROSS_CERT, DECK, WAVE147, WAVE163):
        assert certificate["inputs"][str(path)]["sha256"] == sha(path)

    visible = tuple(map(int, deck["T0_all_G_targeted_order9_projection"]
                        ["visible_19_H9_masks"]))
    universe35 = set(visible + tuple(map(int, cross["added_nine_masks"]))
                     + tuple(map(int, r0["added_seven_masks"])))
    flags = tuple(map(int, certificate["flag_masks"]))
    diagonal_masks = tuple(map(int, certificate["shared_diagonal_masks"]))
    universe37 = universe35 | set(diagonal_masks)
    assert len(flags) == 6 and len(universe35) == 35 and len(universe37) == 37

    frozen8 = set(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    shadows = set()
    deletion_slots = 0
    for mask in diagonal_masks:
        assert canonical(mask, 9) == mask and locally_upper(mask, 9)
        for removed in range(9):
            raw, _ = delete_vertex(mask, 9, removed)
            shadow = canonical(raw, 8)
            assert shadow in frozen8 and x8[shadow] > 0
            shadows.add(shadow)
            deletion_slots += 1

    emitted = {(int(row["left_flag_index"]), int(row["right_flag_index"])): row
               for row in certificate["complete_six_flag_product_scan"]["rows"]}
    closed_cross = []
    deficit_histogram = Counter()
    minimum_pairs = Counter()
    for left, right in itertools.combinations_with_replacement(range(6), 2):
        support = glue_support(flags[left], flags[right])
        outside35 = sorted(support - universe35)
        outside37 = sorted(support - universe37)
        row = emitted[(left, right)]
        assert row["outside_35_masks"] == outside35
        assert row["outside_37_masks"] == outside37
        assert int(row["canonical_support_size"]) == len(support)
        assert row["closed_on_37"] == (not outside37)
        if left == right:
            assert outside35 == list(diagonal_masks) and not outside37
        else:
            deficit_histogram[len(outside37)] += 1
            if not outside37:
                closed_cross.append((left, right))
            if len(outside37) == 2:
                minimum_pairs[tuple(outside37)] += 1

    assert not closed_cross
    assert deficit_histogram == Counter({2: 6, 9: 6, 15: 3})
    assert minimum_pairs == Counter({
        (14681719440, 56449716416): 3,
        (46748225728, 47606550720): 3,
    })
    result = {
        "status": "independent-two-mask-six-flag-clique-audit-passed",
        "probe_producer_imported": False,
        "certificate_sha256": sha(CERTIFICATE),
        "input_hashes_match": True,
        "diagonal_masks_checked": len(diagonal_masks),
        "deletion_slots_checked": deletion_slots,
        "distinct_frozen_H8_shadows": len(shadows),
        "flag_products_recomputed": len(emitted),
        "closed_off_diagonal_products": 0,
        "maximum_clique_size": 1,
        "minimum_cross_deficit": 2,
        "R1_extension_attempted": False,
        "ambient_order9_census_generated": False,
        "submission_txt_written": False,
    }
    save(OUTPUT, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
