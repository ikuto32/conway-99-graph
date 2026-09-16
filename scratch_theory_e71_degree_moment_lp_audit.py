"""Standalone exact audit of frozen E71 degree-moment Farkas certificates.

No producer/base modules or LP solver are imported.  Principal inverses
reconstruct complete raw row domains and the equality model from scratch.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
KERNEL = Path("scratch_theory_e71_equitable_kernel_port_census.json")
CERT = Path("scratch_theory_e71_degree_moment_lp_frontier.json")
OUT = Path("scratch_theory_e71_degree_moment_lp_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
LABELS = tuple((2 * a + p, 2 * b + q) for a, b in SUPPORTS
               for p, q in itertools.product((0, 1), repeat=2))
LABEL_INDEX = {label: index for index, label in enumerate(LABELS)}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def macro_key(row: dict) -> tuple[int, ...]:
    return tuple(int(row[field]) for field in
                 ("source_row_index", "state_orbit_number", "signature_stabilizer_orbit_number"))


def product(left, right):
    columns = tuple(zip(*right))
    return [[sum(a * b for a, b in zip(row, column)) for column in columns]
            for row in left]


def reconstruct(entry: dict, profile: dict):
    exceptional = tuple(SUPPORTS.index(tuple(record["support"]))
                        for record in entry["exceptional_supports"])
    baseline = [[8 if i == j else (4 if set(a).isdisjoint(b) else 0)
                 for j, b in enumerate(SUPPORTS)] for i, a in enumerate(SUPPORTS)]
    compression = [row[:] for row in baseline]
    for index, record in zip(exceptional, entry["exceptional_supports"]):
        compression[index][index] = 2 * (4 - int(record["deficit"]))
    overlapping = {(min(a, b), max(a, b)): int(value)
                   for a, b, value in entry["overlap_block_totals"]}
    disjoint = {(min(a, b), max(a, b)): int(value)
                for a, b, value in profile["disjoint_D"]}
    assert len(overlapping) == len(entry["overlap_block_totals"])
    assert len(disjoint) == len(profile["disjoint_D"])
    used_overlap, used_disjoint = set(), set()
    for a, b in itertools.combinations(range(len(exceptional)), 2):
        i, j = exceptional[a], exceptional[b]
        if set(SUPPORTS[i]).isdisjoint(SUPPORTS[j]):
            value = disjoint[(a, b)]
            used_disjoint.add((a, b))
        else:
            value = overlapping[(a, b)]
            used_overlap.add((a, b))
        compression[i][j] = compression[j][i] = value
    assert used_overlap == set(overlapping) and used_disjoint == set(disjoint)
    assert all(sum(row) == 48 for row in compression)
    defect = [[baseline[i][j] - compression[i][j] for j in range(21)] for i in range(21)]
    defect_square = product(defect, defect)
    gram = [[28 * defect[i][j] - defect_square[i][j] for j in range(21)] for i in range(21)]
    compression_square = product(compression, compression)
    alternate = [[192 * int(i == j) + 128 - 4 * compression[i][j]
                  - 32 * len(set(SUPPORTS[i]) & set(SUPPORTS[j]))
                  - compression_square[i][j] for j in range(21)] for i in range(21)]
    assert gram == alternate
    assert all(gram[i][j] == 0 for i in range(21) for j in range(21)
               if i not in exceptional or j not in exceptional)
    return exceptional, compression, gram


def principal_coordinates(gram):
    """Lexicographic PSD principal elimination, not the producer's RREF."""
    size = len(gram)
    residual = [list(map(Fraction, row)) for row in gram]
    selected = []
    for index in range(size):
        pivot = residual[index][index]
        if not pivot:
            assert all(residual[index][j] == 0 for j in range(index, size))
            continue
        assert pivot > 0
        selected.append(index)
        for a in range(index + 1, size):
            for b in range(index + 1, size):
                residual[a][b] -= residual[a][index] * residual[index][b] / pivot
    rank = len(selected)
    assert 1 <= rank <= 5
    principal = [[Fraction(gram[i][j]) for j in selected] for i in selected]
    augmented = [row[:] + [Fraction(a == b) for b in range(rank)]
                 for a, row in enumerate(principal)]
    for column in range(rank):
        pivot_row = next(row for row in range(column, rank) if augmented[row][column])
        augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(rank):
            if row == column:
                continue
            coefficient = augmented[row][column]
            augmented[row] = [a - coefficient * b for a, b in zip(augmented[row], augmented[column])]
    inverse = [row[rank:] for row in augmented]
    coordinates = product(inverse, [gram[index] for index in selected])
    assert product([[row[index] for index in selected] for row in gram], coordinates) == gram
    assert [[coordinates[i][j] for j in selected] for i in range(rank)] == [
        [int(i == j) for j in range(rank)] for i in range(rank)]
    return tuple(selected), coordinates


def all_raw_domains(compression, selected, coordinates):
    denominator = math.lcm(*(value.denominator for row in coordinates for value in row))
    scaled_columns = tuple(tuple(int(coordinates[i][j] * denominator)
                                 for i in range(len(selected))) for j in range(21))
    result = []
    for source in range(21):
        domain = []
        for chosen_degrees in itertools.product(range(5), repeat=len(selected)):
            pivot = tuple(4 * degree - compression[source][target]
                          for degree, target in zip(chosen_degrees, selected))
            degrees = []
            for target, column in enumerate(scaled_columns):
                value = sum(a * b for a, b in zip(pivot, column)) + denominator * compression[source][target]
                if value % (4 * denominator) or not 0 <= value <= 16 * denominator:
                    break
                degrees.append(value // (4 * denominator))
            else:
                if sum(degrees) == 12:
                    domain.append((pivot, tuple(degrees)))
        assert len({pivot for pivot, _ in domain}) == len(domain)
        result.append(domain)
    return result


def ordinary_internal_theorem():
    accepted = 0
    for four_edges in itertools.combinations(tuple(itertools.combinations(range(4), 2)), 4):
        edges = set(four_edges)
        if any(all(edge in edges for edge in itertools.combinations(triangle, 2))
               for triangle in itertools.combinations(range(4), 3)):
            continue
        assert all(sum(vertex in edge for edge in edges) == 2 for vertex in range(4))
        accepted += 1
    assert accepted == 3
    # Every three support corners include a pair sharing a root-neighbour.
    corners = ((0, 2), (0, 3), (1, 2), (1, 3))
    assert all(any(set(a) & set(b) for a, b in itertools.combinations(triple, 2))
               for triple in itertools.combinations(corners, 3))
    return accepted


def fibre_incidence_geometry():
    """Check the incidence factor in the independent R^T R derivation."""
    assert len(LABELS) == len(set(LABELS)) == 84
    compressed_incidence = [[sum(neighbor in LABELS[4 * fibre + local]
                                 for local in range(4))
                             for fibre in range(21)] for neighbor in range(14)]
    actual = product(list(zip(*compressed_incidence)), compressed_incidence)
    expected = [[8 * len(set(a) & set(b)) for b in SUPPORTS] for a in SUPPORTS]
    assert actual == expected
    # U^T U=4I; U^T B^2 U=48I-C+32J-8*intersection.
    # R=4BU-UC therefore gives R^T R=16 U^T B^2 U-4C^2=4K4.
    assert 16 * 48 == 4 * 192
    assert 16 * -1 == 4 * -4
    assert 16 * 32 == 4 * 128
    assert 16 * -8 == 4 * -32
    return 4


def internal_degrees(entry, exceptional, compression):
    degrees = [[0] * 4 for _ in range(21)]
    observed = set()
    for left, right in entry["internal_edges"]:
        a, b = LABEL_INDEX[tuple(left)], LABEL_INDEX[tuple(right)]
        assert a != b and a // 4 == b // 4 and a // 4 in exceptional
        edge = tuple(sorted((a, b)))
        assert edge not in observed
        observed.add(edge)
        degrees[a // 4][a % 4] += 1
        degrees[b // 4][b % 4] += 1
    for source in range(21):
        if source not in exceptional:
            assert compression[source][source] == 8
            degrees[source] = [2] * 4
        assert sum(degrees[source]) == compression[source][source]
    return degrees


def check_model(entry, profile, stored):
    exceptional, compression, gram = reconstruct(entry, profile)
    selected, coordinates = principal_coordinates(gram)
    domains = all_raw_domains(compression, selected, coordinates)
    fixed_degrees = internal_degrees(entry, exceptional, compression)
    rank = len(selected)
    groups = [(source, self_degree, multiplicity) for source in range(21)
              for self_degree, multiplicity in sorted(Counter(fixed_degrees[source]).items())]
    assert sum(multiplicity for _, _, multiplicity in groups) == 84
    pairs = tuple(itertools.combinations_with_replacement(range(rank), 2))
    columns, variables = [], []
    for group_index, (source, self_degree, multiplicity) in enumerate(groups):
        for pivot, degrees in domains[source]:
            if degrees[source] != self_degree:
                continue
            column = [0] * (len(groups) + 21 * rank + len(pairs))
            column[group_index] = 1
            for axis in range(rank):
                column[len(groups) + source * rank + axis] = pivot[axis]
            for offset, (a, b) in enumerate(pairs):
                column[len(groups) + 21 * rank + offset] = pivot[a] * pivot[b]
            columns.append(column)
            variables.append({"source": source, "internal_degree": self_degree, "pivot": list(pivot)})
    assert columns
    target = [multiplicity for _, _, multiplicity in groups] + [0] * (21 * rank)
    target.extend(4 * gram[selected[a]][selected[b]] for a, b in pairs)
    matrix = [list(row) for row in zip(*columns)]
    model_hash = hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()
    metadata = stored["model"]
    assert metadata["pivot_supports"] == [list(SUPPORTS[index]) for index in selected]
    assert metadata["rank_K4"] == rank
    assert metadata["raw_row_patterns"] == sum(map(len, domains))
    assert metadata["groups"] == [list(group) for group in groups]
    assert metadata["variables"] == variables
    assert metadata["moment_pairs"] == [list(pair) for pair in pairs]
    assert metadata["matrix_sha256"] == model_hash
    assert stored["equations"] == len(target) and stored["variables"] == len(variables)
    certified = bool(stored["exactly_certified_infeasible"])
    certificate = stored["certificate"]
    if certified:
        assert certificate is not None
        multiplier = certificate["integer_multiplier"]
        assert len(multiplier) == len(target) and all(type(value) is int for value in multiplier)
        slacks = [sum(a * b for a, b in zip(multiplier, column)) for column in columns]
        separation = sum(a * b for a, b in zip(multiplier, target))
        assert min(slacks) >= 0 and separation < 0
        assert min(slacks) == certificate["min_column_slack"]
        assert separation == certificate["target_pairing"]
        assert certificate["exact_integer_check_pass"] is True
    else:
        assert certificate is None
        separation = None
    domain_hash = hashlib.sha256(json.dumps(domains, separators=(",", ":")).encode()).hexdigest()
    return {
        "key": list(macro_key(entry)), "parameter": profile["parameter"],
        "coverage": int(entry["signature_orbit_labelled_coverage"]),
        "rank_K4": rank, "raw_rows_reenumerated": sum(map(len, domains)),
        "equations": len(target), "variables": len(variables),
        "matrix_sha256": model_hash, "raw_domains_sha256": domain_hash,
        "exact_Farkas_certificate_pass": certified, "target_pairing": separation,
    }


def main() -> None:
    started = time.monotonic()
    certificate, catalog, mining, kernel = map(read, (CERT, CATALOG, MINING, KERNEL))
    assert certificate["all_frozen_profiles_requested"] is True
    for name, expected in certificate["inputs_sha256"].items():
        assert sha(Path(name)) == expected.upper(), name
    for name, expected in kernel["inputs"].items():
        assert sha(Path(name)) == expected.upper(), name
    ordinary_count = ordinary_internal_theorem()
    row_gram_scale = fibre_incidence_geometry()
    entries = {macro_key(row): row for row in catalog["macro_entries"]
               if row["signature_stabilizer_canonical"]}
    assert len(entries) == 180
    all_profiles = defaultdict(dict)
    for profile in mining["profile_rows"]["71"]:
        key = macro_key(profile)
        parameter = profile["parameter"]
        assert parameter not in all_profiles[key]
        all_profiles[key][parameter] = profile
        assert profile["coverage"] == entries[key]["signature_orbit_labelled_coverage"]
    assert len(all_profiles) == 157 and sum(map(len, all_profiles.values())) == 165
    kernel_rows = {tuple(row["key"]): row for row in kernel["rows"]}
    assert len(kernel_rows) == len(kernel["rows"]) == 157
    assert set(kernel_rows) == set(all_profiles)
    expected_tasks = {}
    for key, row in kernel_rows.items():
        assert row["coverage"] == entries[key]["signature_orbit_labelled_coverage"]
        kernel_profiles = {profile["parameter"]: profile for profile in row["profiles"]}
        assert len(kernel_profiles) == len(row["profiles"])
        assert set(kernel_profiles) == set(all_profiles[key])
        passes = any(profile["passes_kernel_port_CSP"] for profile in row["profiles"])
        assert passes == row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]
        for parameter, profile in kernel_profiles.items():
            if profile["passes_kernel_port_CSP"]:
                expected_tasks[(key, parameter)] = row["coverage"]
    stored_rows = {(tuple(row["key"]), row["parameter"]): row for row in certificate["profiles"]}
    assert len(stored_rows) == len(certificate["profiles"]) == certificate["profile_count"] == 140
    assert set(stored_rows) == set(expected_tasks)
    audited = []
    for index, ((key, parameter), stored) in enumerate(stored_rows.items(), 1):
        assert stored["coverage"] == expected_tasks[(key, parameter)]
        audited.append(check_model(entries[key], all_profiles[key][parameter], stored))
        if index % 20 == 0:
            print(json.dumps({"profiles_audited": index, "total": len(stored_rows)}), flush=True)
    assert sum(row["exact_Farkas_certificate_pass"] for row in audited) == certificate["exact_infeasible_profiles"] == 68
    results = {(tuple(row["key"]), row["parameter"]): row for row in audited}
    input_macros = {key for key, _ in expected_tasks}
    assert len(input_macros) == 132
    excluded, unresolved = [], []
    for key in sorted(input_macros):
        # For new macro credit require certificates for EVERY frozen full-Gram
        # profile, not merely every selected LP task or a prior status flag.
        covered = all((key, parameter) in results and results[(key, parameter)]["exact_Farkas_certificate_pass"]
                      for parameter in all_profiles[key])
        row = {"key": list(key), "coverage": int(entries[key]["signature_orbit_labelled_coverage"]),
               "full_Gram_profile_parameters": list(all_profiles[key])}
        (excluded if covered else unresolved).append(row)
    excluded_coverage = sum(row["coverage"] for row in excluded)
    input_coverage = sum(entries[key]["signature_orbit_labelled_coverage"] for key in input_macros)
    assert len(excluded) == 66 and excluded_coverage == 22675456
    assert input_coverage == 49086464
    result = {
        "status": "INDEPENDENT_E71_DEGREE_MOMENT_LP_AUDIT_PASS",
        "producer_or_base_imported": False, "LP_solver_used": False,
        "inputs_sha256": {str(path): sha(path) for path in (CERT, CATALOG, MINING, KERNEL)},
        "all_input_hashes_match": True,
        "full_frozen_profile_manifest_checked": True,
        "ordinary_four_edge_triangle_free_cases_checked": ordinary_count,
        "R_transpose_R_equals_this_factor_times_K4": row_gram_scale,
        "profiles_audited": len(audited), "raw_degree_rows_reenumerated": sum(row["raw_rows_reenumerated"] for row in audited),
        "exact_Farkas_profiles": 68,
        "input_macros": len(input_macros), "input_coverage": input_coverage,
        "fully_certified_macros": len(excluded), "excluded_coverage": excluded_coverage,
        "remaining_macros_in_this_input": len(unresolved),
        "remaining_coverage_in_this_input": input_coverage - excluded_coverage,
        "excluded_macro_rows": excluded, "unresolved_macro_rows": unresolved,
        "profile_rows": audited,
        "local_completions_enumerated": 0,
        "pointwise_E0_lower_bound": None,
        "scope": "Exactly the listed66 frozen E71 macros; each has every full-Gram profile independently Farkas-certified. No inference of feasible graph from other LP statuses.",
        "elapsed_seconds": time.monotonic() - started,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("profile_rows", "excluded_macro_rows", "unresolved_macro_rows")}, indent=2))


if __name__ == "__main__":
    main()
