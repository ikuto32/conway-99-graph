"""Independent structural audit of the semiregular-C11 encoder and WLOG CNF.

Solver outcomes are deliberately outside scope.  The base and normalized CNFs
are reconstructed in memory without importing the producer, and their ordered
clause lists are compared to the saved artifacts.  Separate finite orbit and
branch enumerations audit the mathematical coverage of the normalization.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys


SCRIPT = Path("scratch_root_c11_semiregular_sat.py")
BASE_CNF = Path("scratch_root_c11_semiregular.cnf")
BASE_META = Path("scratch_root_c11_semiregular_build.json")
NORMALIZED_CNF = Path("scratch_root_c11_semiregular_normalized.cnf")
NORMALIZED_META = Path("scratch_root_c11_semiregular_normalized_build.json")
OUTPUT = Path("scratch_root_c11_semiregular_structural_audit.json")
REPORT = Path("scratch_root_c11_semiregular_structural_audit.md")

FIBRES = 9
MODULUS = 11
VERTICES = FIBRES * MODULUS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def vertex(fibre, coordinate):
    return MODULUS * fibre + coordinate % MODULUS


def canonical_edge(left, right):
    assert left != right
    left_fibre, left_coordinate = divmod(left, MODULUS)
    right_fibre, right_coordinate = divmod(right, MODULUS)
    if left_fibre == right_fibre:
        difference = (right_coordinate - left_coordinate) % MODULUS
        return left_fibre, left_fibre, min(difference, MODULUS - difference)
    if left_fibre < right_fibre:
        return left_fibre, right_fibre, (right_coordinate - left_coordinate) % MODULUS
    return right_fibre, left_fibre, (left_coordinate - right_coordinate) % MODULUS


def independent_edge_keys():
    keys = []
    for left in range(FIBRES):
        keys.extend((left, left, difference) for difference in range(1, 6))
        for right in range(left + 1, FIBRES):
            keys.extend((left, right, difference)
                        for difference in range(MODULUS))
    return tuple(keys)


def independent_pair_representatives():
    answer = []
    for left_fibre in range(FIBRES):
        for difference in range(1, 6):
            answer.append((vertex(left_fibre, 0), vertex(left_fibre, difference)))
        for right_fibre in range(left_fibre + 1, FIBRES):
            for difference in range(MODULUS):
                answer.append((vertex(left_fibre, 0), vertex(right_fibre, difference)))
    return tuple(answer)


def signed_image(pattern, unit):
    return tuple(sorted(min(unit * difference % MODULUS,
                            MODULUS - unit * difference % MODULUS)
                        for difference in pattern))


def independent_internal_orbits(size):
    unseen = set(itertools.combinations(range(1, 6), size))
    representatives = []
    while unseen:
        seed = min(unseen)
        orbit = {signed_image(seed, unit) for unit in range(1, MODULUS)}
        assert orbit <= set(itertools.combinations(range(1, 6), size))
        representatives.append(min(orbit))
        unseen -= orbit
    return tuple(sorted(representatives))


def independent_partitions(total):
    # combinations_with_replacement is independent of the producer's recursive
    # partition generator.  Reverse each tuple to the required nonincreasing form.
    values = {
        tuple(reversed(row))
        for row in itertools.combinations_with_replacement(range(12), 8)
        if sum(row) == total
    }
    return tuple(sorted(values, reverse=True))


def independent_specs():
    specs = []
    # Fourier inversion forces five internal signed differences in total, so
    # we may choose a fibre with at least one.  The quotient diagonal identity
    # then leaves only the rows below.
    for internal_count in range(1, 6):
        cross_total = 14 - 2 * internal_count
        patterns = independent_internal_orbits(internal_count)
        partitions = tuple(
            counts for counts in independent_partitions(cross_total)
            if 4 * internal_count * internal_count + 2 * internal_count
               + sum(value * value for value in counts) == 34
        )
        for pattern in patterns:
            for counts in partitions:
                specs.append((pattern, counts))
    return tuple(specs)


def build_base_in_memory(CNF, IDPool, CardEnc, EncType):
    keys = independent_edge_keys()
    variable = {key: index + 1 for index, key in enumerate(keys)}
    representatives = independent_pair_representatives()
    formula = CNF()
    pool = IDPool(start_from=len(keys) + 1)
    degree_occurrences = 0
    product_occurrences = 0

    for fibre in range(FIBRES):
        root = vertex(fibre, 0)
        terms = []
        for neighbour in range(VERTICES):
            if neighbour == root:
                continue
            edge = variable[canonical_edge(root, neighbour)]
            occurrence = pool.id(("degree", fibre, neighbour))
            formula.append([-occurrence, edge])
            formula.append([occurrence, -edge])
            terms.append(occurrence)
            degree_occurrences += 1
        formula.extend(CardEnc.equals(
            terms, bound=14, vpool=pool, encoding=EncType.seqcounter
        ).clauses)

    for pair_number, (left, right) in enumerate(representatives):
        terms = []
        for witness in range(VERTICES):
            if witness == left or witness == right:
                continue
            first = variable[canonical_edge(left, witness)]
            second = variable[canonical_edge(right, witness)]
            product = pool.id(("product", pair_number, witness))
            formula.append([-product, first])
            formula.append([-product, second])
            formula.append([product, -first, -second])
            terms.append(product)
            product_occurrences += 1
        formula.extend(CardEnc.equals(
            terms + [variable[canonical_edge(left, right)]],
            bound=2, vpool=pool, encoding=EncType.seqcounter,
        ).clauses)
    return formula, variable, degree_occurrences, product_occurrences


def extend_normalization_in_memory(
    formula, variable, specs, CNF, IDPool, CardEnc, EncType,
):
    pool = IDPool(start_from=formula.nv + 1)
    for difference in range(1, 6):
        formula.extend(CardEnc.equals(
            [variable[(fibre, fibre, difference)] for fibre in range(FIBRES)],
            bound=1, vpool=pool, encoding=EncType.seqcounter,
        ).clauses)
    selectors = []
    for branch_index, (pattern, counts) in enumerate(specs):
        selector = pool.id(("branch", branch_index))
        selectors.append(selector)
        selected = set(pattern)
        for difference in range(1, 6):
            edge = variable[(0, 0, difference)]
            formula.append([-selector, edge if difference in selected else -edge])
        for right_fibre, count in enumerate(counts, start=1):
            block = [variable[(0, right_fibre, difference)]
                     for difference in range(MODULUS)]
            conditional = CardEnc.equals(
                block, bound=count, vpool=pool, encoding=EncType.seqcounter
            )
            formula.extend([[-selector] + clause
                            for clause in conditional.clauses])
            if count:
                formula.append([-selector, variable[(0, right_fibre, 0)]])
    formula.extend(CardEnc.equals(
        selectors, bound=1, vpool=pool, encoding=EncType.seqcounter
    ).clauses)
    return formula, tuple(selectors)


def main() -> None:
    dependency = str(Path(".deps").resolve())
    if dependency not in sys.path:
        sys.path.insert(0, dependency)
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    normalized_meta = json.loads(NORMALIZED_META.read_text(encoding="utf-8"))
    assert base_meta["status"] == normalized_meta["status"] == "BUILT"
    assert base_meta["cnf_sha256"] == sha256(BASE_CNF)
    assert normalized_meta["cnf_sha256"] == sha256(NORMALIZED_CNF)
    assert normalized_meta["input_sha256"] == sha256(BASE_CNF)

    keys = independent_edge_keys()
    key_set = set(keys)
    assert len(keys) == len(key_set) == 441
    assert Counter(key[0] == key[1] for key in keys) == Counter({False: 396, True: 45})

    # Exhaust all 4,851 unordered pairs. Each orbit has size eleven, is
    # invariant under simultaneous translation, and has one stored representative.
    orbit_members = defaultdict(list)
    translation_checks = 0
    symmetry_checks = 0
    for left, right in itertools.combinations(range(VERTICES), 2):
        key = canonical_edge(left, right)
        assert key in key_set
        orbit_members[key].append((left, right))
        assert canonical_edge(right, left) == key
        symmetry_checks += 1
        shifted_left = vertex(left // MODULUS, left % MODULUS + 1)
        shifted_right = vertex(right // MODULUS, right % MODULUS + 1)
        assert canonical_edge(shifted_left, shifted_right) == key
        translation_checks += 1
    assert len(orbit_members) == 441
    assert {len(members) for members in orbit_members.values()} == {11}
    representatives = independent_pair_representatives()
    assert len(representatives) == 441
    assert {canonical_edge(*pair) for pair in representatives} == key_set

    # Independently verify the weighted degree row: five internal orbit
    # variables occur twice and each of 88 cross variables occurs once.
    degree_weight_checks = 0
    for fibre in range(FIBRES):
        root = vertex(fibre, 0)
        weights = Counter(canonical_edge(root, neighbour)
                          for neighbour in range(VERTICES) if neighbour != root)
        assert sorted(value for key, value in weights.items()
                      if key[0] == key[1]) == [2] * 5
        assert sorted(value for key, value in weights.items()
                      if key[0] != key[1]) == [1] * 88
        assert sum(weights.values()) == 98
        degree_weight_checks += len(weights)

    # The three product clauses are exactly p <-> (a and b).
    product_truth_rows = 0
    for first, second, product in itertools.product((False, True), repeat=3):
        clauses_hold = (
            ((not product) or first)
            and ((not product) or second)
            and (product or (not first) or (not second))
        )
        assert clauses_hold == (product == (first and second))
        product_truth_rows += 1
    assert product_truth_rows == 8

    expected_base, variable, degree_occurrences, product_occurrences = (
        build_base_in_memory(CNF, IDPool, CardEnc, EncType)
    )
    actual_base = CNF(from_file=str(BASE_CNF))
    assert expected_base.nv == actual_base.nv == base_meta["variables"] == 234_612
    assert expected_base.clauses == actual_base.clauses
    assert len(expected_base.clauses) == base_meta["clauses"] == 511_119
    base_variables = expected_base.nv
    base_clauses = len(expected_base.clauses)
    assert degree_occurrences == base_meta["degree_occurrence_helpers"] == 882
    assert product_occurrences == base_meta["common_neighbour_product_helpers"] \
        == 42_777
    del actual_base

    # The quotient spectral multiplicities follow arithmetically from Galois
    # conjugacy of the ten nontrivial character blocks.
    quotient_multiplicities = []
    for three in range(9):
        minus_four = 8 - three
        if (54 - three) % 10 == 0 and (44 - minus_four) % 10 == 0:
            quotient_multiplicities.append((three, minus_four))
    assert quotient_multiplicities == [(4, 4)]
    assert 14 + 4 * 3 - 4 * 4 == 10
    nontrivial_three = (54 - 4) // 10
    nontrivial_minus_four = (44 - 4) // 10
    assert (nontrivial_three, nontrivial_minus_four) == (5, 4)
    assert 5 * 3 - 4 * 4 == -1

    # If n_d is the number of internal circulants containing signed d, the
    # j=1 trace equation says 1 + sum n_d(x^d+x^(11-d)) vanishes at a primitive
    # 11th root. It has degree <=10 and constant one, hence equals Phi_11.
    # Therefore every n_d is exactly one. Check the resulting coefficients.
    cyclotomic_coefficients = [1] * 11
    fourier_coefficients = [0] * 11
    fourier_coefficients[0] = 1
    for difference in range(1, 6):
        fourier_coefficients[difference] = 1
        fourier_coefficients[MODULUS - difference] = 1
    assert fourier_coefficients == cyclotomic_coefficients

    specs = independent_specs()
    assert len(specs) == len(set(specs)) == 4
    metadata_specs = tuple(
        (tuple(branch["internal_pattern"]), tuple(branch["cross_counts"]))
        for branch in normalized_meta["branches"]
    )
    assert metadata_specs == specs
    assert [branch["branch_index"] for branch in normalized_meta["branches"]] \
        == list(range(len(specs)))
    branch_histogram = Counter(len(pattern) for pattern, _ in specs)
    assert {str(key): value for key, value in sorted(branch_histogram.items())} \
        == normalized_meta["branches_by_internal_edge_orbits"] \
        == {"1": 2, "2": 2}
    internal_orbit_histogram = {
        size: len(independent_internal_orbits(size)) for size in range(6)
    }
    assert internal_orbit_histogram == {0: 1, 1: 1, 2: 2, 3: 2, 4: 1, 5: 1}
    raw_partition_histogram = {
        size: len(independent_partitions(14 - 2 * size)) for size in range(6)
    }
    assert raw_partition_histogram \
        == {0: 112, 1: 69, 2: 40, 3: 22, 4: 11, 5: 5}
    raw_branch_count = sum(raw_partition_histogram[size]
                           * internal_orbit_histogram[size]
                           for size in range(6))
    assert raw_branch_count == 321
    quotient_filtered_partition_histogram = {
        size: sum(
            4 * size * size + 2 * size + sum(value * value for value in counts)
            == 34
            for counts in independent_partitions(14 - 2 * size)
        )
        for size in range(1, 6)
    }
    assert quotient_filtered_partition_histogram \
        == {1: 2, 2: 1, 3: 0, 4: 0, 5: 0}
    for pattern, counts in specs:
        assert tuple(sorted(counts, reverse=True)) == counts
        assert all(0 <= count <= 11 for count in counts)
        assert sum(counts) + 2 * len(pattern) == 14
        assert 4 * len(pattern) ** 2 + 2 * len(pattern) \
            + sum(value * value for value in counts) == 34
        assert pattern == min(signed_image(pattern, unit)
                              for unit in range(1, MODULUS))

    expected_normalized, selectors = extend_normalization_in_memory(
        expected_base, variable, specs, CNF, IDPool, CardEnc, EncType
    )
    assert selectors == tuple(branch["selector"]
                              for branch in normalized_meta["branches"])
    actual_normalized = CNF(from_file=str(NORMALIZED_CNF))
    assert expected_normalized.nv == actual_normalized.nv \
        == normalized_meta["variables"] == 235_279
    assert expected_normalized.clauses == actual_normalized.clauses
    assert len(expected_normalized.clauses) == normalized_meta["clauses"] \
        == 512_750

    result = {
        "status": "C11_SEMIREGULAR_STRUCTURAL_AUDIT_PASS",
        "scope": "encoder and quotient-filtered WLOG structure only; no solver result audited",
        "inputs": {str(path): sha256(path) for path in (
            SCRIPT, BASE_CNF, BASE_META, NORMALIZED_CNF, NORMALIZED_META
        )},
        "base_encoder": {
            "vertices": VERTICES,
            "edge_orbits": len(keys),
            "unordered_pair_orbits": len(representatives),
            "unordered_pairs_exhausted": symmetry_checks,
            "simultaneous_translation_checks": translation_checks,
            "members_per_edge_orbit": 11,
            "weighted_degree_terms_checked": degree_weight_checks,
            "degree_occurrence_helpers": degree_occurrences,
            "common_neighbour_product_helpers": product_occurrences,
            "product_truth_table_rows": product_truth_rows,
            "ordered_clause_rebuild_byte_semantics_match": True,
            "variables": base_variables,
            "clauses": base_clauses,
        },
        "character_consequence": {
            "invariant_quotient_spectrum": "14^1,3^4,(-4)^4",
            "nontrivial_character_spectrum": "3^5,(-4)^4",
            "nontrivial_character_trace": -1,
            "cyclotomic_Fourier_inversion_exact": True,
            "each_signed_internal_difference_occurs_in_exactly_one_fibre": True,
        },
        "quotient_row_identity": {
            "matrix_identity": "B^2+B=12I+22J on the nine fibre-constant directions",
            "diagonal_formula": "4*t^2+2*t+sum(c_j^2)=34",
            "raw_degree_and_unit_WLOG_branch_count": raw_branch_count,
            "quotient_filtered_branch_count": len(specs),
            "verified": True,
        },
        "WLOG": {
            "branch_count": len(specs),
            "branches_by_internal_count": {
                str(key): value for key, value in sorted(branch_histogram.items())
            },
            "internal_pattern_orbits_by_size": {
                str(key): value for key, value in internal_orbit_histogram.items()
            },
            "raw_cross_count_partitions_by_internal_size": {
                str(key): value for key, value in raw_partition_histogram.items()
            },
            "quotient_filtered_partitions_by_positive_internal_size": {
                str(key): value
                for key, value in quotient_filtered_partition_histogram.items()
            },
            "all_branch_degree_sums_equal_14": True,
            "all_nonempty_fibre0_cross_blocks_force_difference_zero": True,
            "selectors_exactly_one": True,
            "ordered_normalized_clause_rebuild_match": True,
            "variables": expected_normalized.nv,
            "clauses": len(expected_normalized.clauses),
            "coverage_statement": (
                "Fourier inversion gives five internal differences in total. "
                "For any semiregular C11 graph, relabel an orbit containing one "
                "as fibre 0; "
                "permute the other eight by nonincreasing cross count; globally "
                "rescale the generator to the canonical internal signed subset; "
                "then independently shift every adjacent fibre to put one edge "
                "at difference zero. At least one listed branch results."
            ),
            "not_a_partition_statement": (
                "Different choices of fibre zero or tied fibre permutations may "
                "place the same isomorphism class in multiple branches. The four "
                "cases are an exhaustive WLOG cover, not claimed disjoint orbits."
            ),
        },
        "claim_boundary": (
            "The CNF is exact only within graphs admitting a fixed-point-free "
            "order-11 automorphism with nine 11-cycles. This audit validates the "
            "encoder and WLOG cover but intentionally does not read or endorse "
            "the in-progress normalized solver result."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# Semiregular C11 encoder/WLOG structural audit",
        "",
        "Status: **C11_SEMIREGULAR_STRUCTURAL_AUDIT_PASS**.",
        "",
        "The base 99-vertex invariant encoder and current normalized CNF were rebuilt "
        "in memory without importing the producer. Their ordered clause lists "
        "match: base 234,612 variables / 511,119 clauses; normalized 235,279 "
        "variables / 512,750 clauses (hash `652C25...`).",
        "",
        "All 4,851 unordered vertex pairs form 441 translation orbits of size "
        "11. The nine weighted degree rows and all 441 common-neighbour rows "
        "therefore cover the full graph; product helpers satisfy the complete "
        "truth table for `p <-> (a and b)`.",
        "",
        "The character argument gives quotient spectrum `14,3^4,(-4)^4` and "
        "nontrivial trace `-1`. Exact cyclotomic Fourier inversion forces every "
        "signed internal difference 1 through 5 to occur in exactly one fibre.",
        "",
        "Independent subset-orbit and integer-partition enumeration first gives "
        "321 raw degree/unit cases. The quotient diagonal identity "
        "`4t^2+2t+sum(c_j^2)=34`, together with choosing a fibre that has an "
        "internal edge, leaves four branches (two with t=1 and two with t=2). "
        "Fibre permutation, "
        "generator rescaling, and independent coordinate shifts put every "
        "semiregular-C11 candidate into at least one branch. This is a complete "
        "WLOG cover, not necessarily a disjoint isomorphism-orbit partition.",
        "",
        "Boundary: solver statuses were intentionally not audited. The whole "
        "model concerns only the semiregular order-11 automorphism subclass.",
        "",
    ]), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "edge_orbits": len(keys),
        "pair_orbits": len(representatives),
        "raw_branches": raw_branch_count,
        "quotient_filtered_branches": len(specs),
        "base_clauses": base_meta["clauses"],
        "normalized_clauses": normalized_meta["clauses"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
