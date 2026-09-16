"""Audit the order-eight relaxation boundary for a positive E0 lower bound.

This script does not run a numerical optimizer and does not import discovery
code.  It checks sealed, independently verified rational-witness artifacts in
the local conway-99-research checkout and combines them with the independently
audited small-motif identity

    sum_r E0(r) = 6 P + N(H_delta)
                = 8316 - n3 - z11/4.

It also reconstructs all pairs of the 126 rooted fibre-edge events, identifies
the sole order-eight part of sum_r binom(E0(r),2), and inspects its coefficients
in the sealed Wave147/148 artifacts.  The conclusion is deliberately scoped:
the listed order-eight linear and pair-root moment constraints cannot, by
themselves, imply a positive global or pointwise E0 lower bound, and contain no
direct order-nine-or-higher contraction.  This says nothing against a stronger
theorem for an actual srg(99,14,1,2).
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXTERNAL = ROOT / "external_conway99_research"
WITNESS = (
    EXTERNAL
    / "attempts/wave159-four-root-cut-loop/exact-witness-after-fifteen-cuts.json"
)
WITNESS_MANIFEST = (
    EXTERNAL / "attempts/wave159-four-root-cut-loop/package-manifest.sha256"
)
WAVE150_VERIFY = (
    EXTERNAL
    / "verification/wave150-exact-rank1-witness/verification-results.json"
)
WAVE161_VERIFY = (
    EXTERNAL / "verification/wave161-four-root-cut-loop/exact-results.json"
)
FIRST_MOMENT_AUDIT = ROOT / "scratch_root_e0_motif_first_moment_audit.json"
WAVE147_COEFFICIENTS = (
    EXTERNAL / "attempts/wave147-alternative-lane/coefficients.json.gz"
)
WAVE148_MARKED_ROWS = (
    EXTERNAL / "attempts/wave148-marked-order8/marked-rows.json.gz"
)
OUTPUT = ROOT / "scratch_root_order8_e0_lower_bound_boundary.json"

EXPECTED_WITNESS_SHA256 = (
    "0073ac9d0d6053eedeb4f9357c10e40a7004e26cedbeee119601a6e1996bea1e"
)
EXPECTED_WAVE150_VERIFY_SHA256 = (
    "1b151b90a6b2fc7043e9a5f47f13a974f171ea70f6d019aa2f5e26bd253e3540"
)
EXPECTED_WAVE161_VERIFY_SHA256 = (
    "be0f78b4125aec18d221bbb1e36be263bbe4c03457bfb6150e3a2793e8e30782"
)
EXPECTED_WAVE147_COEFFICIENTS_SHA256 = (
    "a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e"
)
EXPECTED_WAVE148_MARKED_ROWS_SHA256 = (
    "e7a39699584fe60ff251119063d66d8eed2a14a69d671c183533806cddc92aa1"
)
H_DELTA_MASK = 120568
ORDER8_ADJACENT_SIDE_PAIR_MASK = 127242964
GLOBAL_ADJACENT_SIDE_PAIR_MASK = 14333541
N = 99
N3_ENDPOINT = 4158


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fraction(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    require(isinstance(value, str), f"noncanonical rational value: {value!r}")
    return Fraction(value)


def manifest_hash(path: Path, relative_path: str) -> str | None:
    suffix = "  " + relative_path.replace("\\", "/")
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.endswith(suffix):
            return raw.split()[0].lower()
    return None


def load_gzip_json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


# The following reconstruction is deliberately independent of the E0 search
# code.  An outer vertex is (g,h,a,b): its two root-neighbour symbols are
# (g,a) and (h,b), where g<h are two of the seven matched groups.
def outer_support(vertex: tuple[int, int, int, int]) -> frozenset[tuple[int, int]]:
    g, h, a, b = vertex
    return frozenset(((g, a), (h, b)))


def fibre_edge_flags() -> tuple[dict[str, object], ...]:
    flags: list[dict[str, object]] = []
    for g, h in itertools.combinations(range(7), 2):
        vertices = tuple((g, h, a, b) for a, b in itertools.product((0, 1), repeat=2))
        for left, right in itertools.combinations(vertices, 2):
            distance = (left[2] != right[2]) + (left[3] != right[3])
            require(distance in (1, 2), "bad square edge")
            flags.append(
                {
                    "fibre": (g, h),
                    "kind": "S" if distance == 1 else "D",
                    "left": left,
                    "right": right,
                }
            )
    require(len(flags) == 126, "84 side plus 42 diagonal flags")
    require(Counter(flag["kind"] for flag in flags) == {"S": 84, "D": 42}, "flag split")
    return tuple(flags)


def selected_outer_edges(flags: tuple[dict[str, object], ...]) -> frozenset[frozenset]:
    return frozenset(
        frozenset((flag["left"], flag["right"]))
        for flag in flags
    )


def partial_bp_violations(flags: tuple[dict[str, object], ...]) -> tuple[dict[str, object], ...]:
    """Return target-one/two BP overfills forced by selected outer edges."""
    selected = selected_outer_edges(flags)
    vertices = frozenset(endpoint for edge in selected for endpoint in edge)
    neighbours = {vertex: set() for vertex in vertices}
    for edge in selected:
        left, right = tuple(edge)
        neighbours[left].add(right)
        neighbours[right].add(left)
    violations = []
    for vertex in sorted(vertices):
        own_groups = frozenset(vertex[:2])
        for symbol in itertools.product(range(7), (0, 1)):
            used = sum(symbol in outer_support(other) for other in neighbours[vertex])
            target = 1 if symbol[0] in own_groups else 2
            if used > target:
                violations.append(
                    {
                        "vertex": vertex,
                        "symbol": symbol,
                        "used": used,
                        "target": target,
                    }
                )
    return tuple(violations)


def pair_union_order(flags: tuple[dict[str, object], ...]) -> int:
    outside = frozenset(
        endpoint
        for flag in flags
        for endpoint in (flag["left"], flag["right"])
    )
    symbols = frozenset(symbol for vertex in outside for symbol in outer_support(vertex))
    return 1 + len(outside) + len(symbols)


def pair_category(flags: tuple[dict[str, object], ...]) -> tuple[str, str, int]:
    first, second = flags
    kinds = "".join(sorted((str(first["kind"]), str(second["kind"]))))
    support_first = frozenset(first["fibre"])
    support_second = frozenset(second["fibre"])
    if support_first == support_second:
        relation = "same_fibre"
    elif support_first & support_second:
        relation = "overlapping_fibres"
    else:
        relation = "disjoint_fibres"
    return kinds, relation, pair_union_order(flags)


def forced_union_graph(
    flags: tuple[dict[str, object], ...]
) -> tuple[tuple[tuple, ...], frozenset[frozenset[int]]]:
    """Build the minimal induced graph forced by two selected E0 events."""
    outside = frozenset(
        endpoint
        for flag in flags
        for endpoint in (flag["left"], flag["right"])
    )
    symbols = frozenset(symbol for vertex in outside for symbol in outer_support(vertex))
    root = ("root",)
    symbol_vertices = tuple(("symbol",) + symbol for symbol in sorted(symbols))
    outside_vertices = tuple(("outer",) + vertex for vertex in sorted(outside))
    vertices = (root,) + symbol_vertices + outside_vertices
    index = {vertex: position for position, vertex in enumerate(vertices)}
    edges: set[frozenset[int]] = set()

    def add(left: tuple, right: tuple) -> None:
        edges.add(frozenset((index[left], index[right])))

    for symbol in symbols:
        add(root, ("symbol",) + symbol)
    for left, right in itertools.combinations(symbols, 2):
        if left[0] == right[0]:
            add(("symbol",) + left, ("symbol",) + right)
    for vertex in outside:
        for symbol in outer_support(vertex):
            add(("outer",) + vertex, ("symbol",) + symbol)
    for flag in flags:
        add(("outer",) + flag["left"], ("outer",) + flag["right"])
    return vertices, frozenset(edges)


def adjacency_sets(order: int, edges: frozenset[frozenset[int]]) -> tuple[frozenset[int], ...]:
    rows = [set() for _ in range(order)]
    for edge in edges:
        left, right = tuple(edge)
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def locally_pair_upper(order: int, edges: frozenset[frozenset[int]]) -> bool:
    rows = adjacency_sets(order, edges)
    for left, right in itertools.combinations(range(order), 2):
        adjacent = right in rows[left]
        common = len(rows[left] & rows[right])
        if common > (1 if adjacent else 2):
            return False
    return True


def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def integer_edge_mask(order: int, edges: frozenset[frozenset[int]]) -> int:
    positions = {edge: position for position, edge in enumerate(edge_pairs(order))}
    return sum(1 << positions[tuple(sorted(edge))] for edge in edges)


def relabel_edges(
    edges: frozenset[frozenset[int]], permutation: tuple[int, ...]
) -> frozenset[frozenset[int]]:
    return frozenset(
        frozenset((permutation[left], permutation[right]))
        for left, right in (tuple(edge) for edge in edges)
    )


def canonical_and_automorphisms(
    order: int, edges: frozenset[frozenset[int]]
) -> tuple[int, int]:
    original = edges
    best: int | None = None
    automorphisms = 0
    for permutation in itertools.permutations(range(order)):
        transformed = relabel_edges(edges, permutation)
        mask = integer_edge_mask(order, transformed)
        best = mask if best is None else min(best, mask)
        automorphisms += transformed == original
    require(best is not None, "empty canonicalization")
    return best, automorphisms


def degree_cell_canonical_mask(order: int, edges: frozenset[frozenset[int]]) -> int:
    rows = adjacency_sets(order, edges)
    degree_cells: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        degree_cells.setdefault(len(row), []).append(vertex)
    start = 0
    choices = []
    for degree in sorted(degree_cells):
        sources = degree_cells[degree]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        choices.append(
            tuple(tuple(zip(sources, image)) for image in itertools.permutations(targets))
        )
    best: int | None = None
    for cell_choice in itertools.product(*choices):
        permutation = [0] * order
        for mapping in cell_choice:
            for source, target in mapping:
                permutation[source] = target
        transformed = relabel_edges(edges, tuple(permutation))
        mask = integer_edge_mask(order, transformed)
        best = mask if best is None else min(best, mask)
    require(best is not None, "empty degree-cell canonicalization")
    return best


def adjacent_side_pair_roles(order: int, edges: frozenset[frozenset[int]]) -> tuple[dict[str, object], ...]:
    """Recognize every (root, unordered adjacent side-edge pair) in a graph."""
    rows = adjacency_sets(order, edges)
    edge_tuples = tuple(sorted(tuple(sorted(edge)) for edge in edges))
    roles = []
    for root in range(order):
        root_neighbours = rows[root]
        if len(root_neighbours) != 4:
            continue
        matching = tuple(
            (left, right)
            for left, right in itertools.combinations(sorted(root_neighbours), 2)
            if right in rows[left]
        )
        if len(matching) != 2 or frozenset(v for edge in matching for v in edge) != root_neighbours:
            continue
        outside_edges = tuple(
            edge for edge in edge_tuples if not (set(edge) & ({root} | set(root_neighbours)))
        )
        for first, second in itertools.combinations(outside_edges, 2):
            endpoints_first = frozenset(first)
            endpoints_second = frozenset(second)
            if len(endpoints_first & endpoints_second) != 1:
                continue
            endpoints = endpoints_first | endpoints_second
            supports = {vertex: rows[vertex] & root_neighbours for vertex in endpoints}
            if any(len(support) != 2 for support in supports.values()):
                continue
            if any(
                any(len(support & frozenset(pair)) != 1 for pair in matching)
                for support in supports.values()
            ):
                continue
            if any(len(supports[left] & supports[right]) != 1 for left, right in (first, second)):
                continue
            loose = tuple(endpoints_first ^ endpoints_second)
            require(len(loose) == 2, "bad path endpoints")
            if loose[1] in rows[loose[0]]:
                continue
            if supports[loose[0]] & supports[loose[1]]:
                continue
            roles.append(
                {
                    "root": root,
                    "selected_edges": [list(first), list(second)],
                    "matching": [list(pair) for pair in matching],
                }
            )
    return tuple(roles)


def direct_pair_audit() -> dict[str, object]:
    flags = fibre_edge_flags()
    rejected = []
    order_histogram: Counter[int] = Counter()
    category_histogram: Counter[tuple[str, str, int]] = Counter()
    examples: dict[tuple[str, int], dict[str, object]] = {}
    first_order8_graph: tuple[int, frozenset[frozenset[int]]] | None = None
    for first, second in itertools.combinations(flags, 2):
        pair = (first, second)
        violations = partial_bp_violations(pair)
        if violations:
            rejected.append((pair, violations))
            continue
        union_order = pair_union_order(pair)
        vertices, graph_edges = forced_union_graph(pair)
        require(len(vertices) == union_order, "union order mismatch")
        require(locally_pair_upper(union_order, graph_edges), "minimal union violates pair upper")
        order_histogram[union_order] += 1
        category_histogram[pair_category(pair)] += 1
        kind_pair = "".join(sorted((str(first["kind"]), str(second["kind"]))))
        examples.setdefault(
            (kind_pair, union_order),
            {
                "union_order": union_order,
                "edge_count": len(graph_edges),
                "degree_sequence": sorted(len(row) for row in adjacency_sets(union_order, graph_edges)),
                "selected_flags": [
                    {
                        "fibre": list(flag["fibre"]),
                        "kind": flag["kind"],
                        "endpoints": [list(flag["left"]), list(flag["right"])],
                    }
                    for flag in pair
                ],
                "partial_BP_feasible": True,
                "induced_lambda_mu_upper_feasible": True,
            },
        )
        if union_order == 8 and first_order8_graph is None:
            first_order8_graph = (union_order, graph_edges)

    require(len(rejected) == 168, "same-fibre side-diagonal rejection count")
    for pair, violations in rejected:
        first, second = pair
        require(first["fibre"] == second["fibre"], "unexpected BP rejection across fibres")
        require({first["kind"], second["kind"]} == {"S", "D"}, "unexpected BP rejection kinds")
        require(violations, "missing BP certificate")
    require(
        order_histogram == {8: 84, 9: 483, 10: 1890, 11: 3150, 12: 1680, 13: 420},
        "direct-pair union histogram",
    )
    expected_categories = {
        ("SS", "same_fibre", 8): 84,
        ("SS", "same_fibre", 9): 42,
        ("DD", "same_fibre", 9): 21,
        ("SS", "overlapping_fibres", 9): 420,
        ("SS", "overlapping_fibres", 10): 1050,
        ("DS", "overlapping_fibres", 10): 840,
        ("SS", "overlapping_fibres", 11): 210,
        ("SS", "disjoint_fibres", 11): 1680,
        ("DS", "overlapping_fibres", 11): 840,
        ("DD", "overlapping_fibres", 11): 420,
        ("DS", "disjoint_fibres", 12): 1680,
        ("DD", "disjoint_fibres", 13): 420,
    }
    require(category_histogram == expected_categories, "direct-pair category histogram")
    require(first_order8_graph is not None, "missing order-eight graph")

    order, k8_edges = first_order8_graph
    global_mask, automorphisms = canonical_and_automorphisms(order, k8_edges)
    degree_mask = degree_cell_canonical_mask(order, k8_edges)
    roles = adjacent_side_pair_roles(order, k8_edges)
    require(global_mask == GLOBAL_ADJACENT_SIDE_PAIR_MASK, "global K8 mask")
    require(degree_mask == ORDER8_ADJACENT_SIDE_PAIR_MASK, "Wave147 K8 mask")
    require(automorphisms == 8, "K8 automorphism count")
    require(len(roles) == 4, "K8 rooted pair-role multiplicity")

    category_rows = [
        {
            "kind_pair": kind_pair,
            "fibre_relation": relation,
            "union_order": union_order,
            "candidate_pairs": count,
        }
        for (kind_pair, relation, union_order), count in sorted(category_histogram.items())
    ]
    max_examples = {
        "SS_order11": examples[("SS", 11)],
        "DS_order12": examples[("DS", 12)],
        "DD_order13": examples[("DD", 13)],
    }
    return {
        "candidate_flags": {"side": 84, "diagonal": 42, "total": 126},
        "unordered_distinct_candidate_pairs": comb(126, 2),
        "BP_rejected_same_fibre_side_diagonal_pairs": len(rejected),
        "BP_exclusion_rule": (
            "a selected fibre diagonal consumes both mate-symbol target-one quotas at "
            "each endpoint, so every incident square side is forbidden"
        ),
        "BP_feasible_pairs": sum(order_histogram.values()),
        "union_order_histogram": {str(order): order_histogram[order] for order in sorted(order_histogram)},
        "category_histogram": category_rows,
        "order8_sector": {
            "description": "two adjacent selected square sides in one fibre",
            "candidate_pairs_per_root": order_histogram[8],
            "global_least_mask": global_mask,
            "wave147_degree_cell_mask": degree_mask,
            "wave147_zero_based_order8_index": 515,
            "edge_count": len(k8_edges),
            "degree_sequence": sorted(len(row) for row in adjacency_sets(order, k8_edges)),
            "automorphism_count": automorphisms,
            "rooted_adjacent_side_pair_roles_per_unlabelled_copy": len(roles),
            "roles_in_reconstructed_labelling": roles,
            "coefficient_in_M_E": 4,
            "coefficient_in_sum_E0_squared_factorial_part": 8,
        },
        "locally_admissible_max_order_witnesses": max_examples,
    }


def wave147_148_visibility_audit() -> dict[str, object]:
    coefficients = load_gzip_json(WAVE147_COEFFICIENTS)
    marked = load_gzip_json(WAVE148_MARKED_ROWS)
    families = coefficients["families"]
    require(set(families) == {"ordered_edge", "ordered_nonedge"}, "Wave147 families")
    all_matrix_records = sum(len(family["class_coefficients"]) for family in families.values())
    all_nonzero_entries = sum(
        len(record["upper_entries"])
        for family in families.values()
        for record in family["class_coefficients"]
    )
    represented_matrix_orders = sorted(
        {
            int(record["order"])
            for family in families.values()
            for record in family["class_coefficients"]
        }
    )
    require(all_matrix_records == 2414, "Wave147 matrix record count")
    require(all_nonzero_entries == 272054, "Wave147 nonzero entry count")
    require(represented_matrix_orders == [5, 6, 7, 8], "Wave147 represented orders")

    family_rows = {}
    reference_masks: tuple[int, ...] | None = None
    for name, family in families.items():
        records8 = tuple(record for record in family["class_coefficients"] if record["order"] == 8)
        masks = tuple(int(record["canonical_mask"]) for record in records8)
        require(len(masks) == 916 and len(set(masks)) == 916, f"{name} order8 stream")
        require(masks == tuple(sorted(masks)), f"{name} order8 ordering")
        if reference_masks is None:
            reference_masks = masks
        else:
            require(masks == reference_masks, "family order8 streams differ")
        require(masks[515] == ORDER8_ADJACENT_SIDE_PAIR_MASK, f"{name} K8 index")
        k_record = records8[515]
        require(len(k_record["upper_entries"]) == 37, f"{name} K8 entry count")
        require(all(entry[2] == 8 for entry in k_record["upper_entries"]), f"{name} K8 coefficients")
        coordinate_support: Counter[tuple[int, int]] = Counter()
        for record in records8:
            for left, right, _coefficient in record["upper_entries"]:
                coordinate_support[(left, right)] += 1
        supports = [coordinate_support[(entry[0], entry[1])] for entry in k_record["upper_entries"]]
        family_rows[name] = {
            "matrix_size": family["matrix_size"],
            "K8_nonzero_upper_entries": len(k_record["upper_entries"]),
            "K8_entry_coefficients": sorted(set(entry[2] for entry in k_record["upper_entries"])),
            "minimum_order8_class_support_of_an_entry_containing_K8": min(supports),
            "individual_entry_isolates_K8": min(supports) == 1,
        }
    require(family_rows["ordered_edge"]["minimum_order8_class_support_of_an_entry_containing_K8"] == 9, "edge support")
    require(family_rows["ordered_nonedge"]["minimum_order8_class_support_of_an_entry_containing_K8"] == 3, "nonedge support")

    deletion_rows = coefficients["order7_to_order8_deletion_equations"]
    require(len(deletion_rows) == 208, "deletion rows")
    deletion_hits = []
    for row in deletion_rows:
        hit = [
            term for term in row["terms_order8_mask_multiplicity"]
            if int(term[0]) == ORDER8_ADJACENT_SIDE_PAIR_MASK
        ]
        if hit:
            deletion_hits.append(
                {
                    "order7_mask": row["order7_mask"],
                    "K8_terms": hit,
                    "order8_term_count": len(row["terms_order8_mask_multiplicity"]),
                }
            )
    require(
        deletion_hits
        == [
            {"order7_mask": 111980, "K8_terms": [[ORDER8_ADJACENT_SIDE_PAIR_MASK, 4]], "order8_term_count": 11},
            {"order7_mask": 111989, "K8_terms": [[ORDER8_ADJACENT_SIDE_PAIR_MASK, 4]], "order8_term_count": 7},
        ],
        "K8 deletion incidences",
    )

    require(len(marked["vertex_rows"]) == 944, "Wave148 vertex rows")
    require(len(marked["ordered_pair_rows"]) == 4440, "Wave148 pair rows")
    require(reference_masks is not None, "missing Wave147 order8 stream")
    reference_mask_set = frozenset(reference_masks)
    require(
        all(
            int(term[0]) in reference_mask_set
            for row in marked["vertex_rows"] + marked["ordered_pair_rows"]
            for term in row["terms_order8_mask_coefficient"]
        ),
        "Wave148 has a target outside the 916 order8 classes",
    )

    def marked_hits(rows: list[dict]) -> list[dict[str, object]]:
        result = []
        for row in rows:
            hits = [
                term for term in row["terms_order8_mask_coefficient"]
                if int(term[0]) == ORDER8_ADJACENT_SIDE_PAIR_MASK
            ]
            if hits:
                result.append(
                    {
                        "row_id": row["row_id"],
                        "order7_mask": row["order7_mask"],
                        "root_relation": row.get("root_relation"),
                        "K8_terms": hits,
                        "order8_term_count": len(row["terms_order8_mask_coefficient"]),
                    }
                )
        return result

    vertex_hits = marked_hits(marked["vertex_rows"])
    pair_hits = marked_hits(marked["ordered_pair_rows"])
    require(len(vertex_hits) == 4, "K8 marked-vertex hit count")
    require(len(pair_hits) == 9, "K8 marked-pair hit count")
    vertex_term_histogram = Counter(row["order8_term_count"] for row in vertex_hits)
    pair_term_histogram = Counter(row["order8_term_count"] for row in pair_hits)
    require(vertex_term_histogram == {7: 2, 3: 1, 4: 1}, "vertex hit support histogram")
    require(pair_term_histogram == {4: 4, 2: 3, 3: 2}, "pair hit support histogram")

    return {
        "wave147": {
            "pair_root_matrix_records": all_matrix_records,
            "nonzero_upper_entries": all_nonzero_entries,
            "represented_orders": represented_matrix_orders,
            "order9_or_higher_columns": 0,
            "order8_classes": len(reference_masks or ()),
            "K8_family_visibility": family_rows,
            "ordinary_deletion_rows_containing_K8": deletion_hits,
        },
        "wave148": {
            "marked_vertex_rows": len(marked["vertex_rows"]),
            "marked_ordered_pair_rows": len(marked["ordered_pair_rows"]),
            "row_shape": "marked order7 source -> induced order8 targets",
            "order9_or_higher_columns": 0,
            "marked_vertex_rows_containing_K8": vertex_hits,
            "marked_pair_rows_containing_K8": pair_hits,
            "K8_vertex_row_term_count_histogram": {
                str(size): count for size, count in sorted(vertex_term_histogram.items())
            },
            "K8_pair_row_term_count_histogram": {
                str(size): count for size, count in sorted(pair_term_histogram.items())
            },
        },
        "individual_existing_coefficient_isolates_K8": False,
        "scope": (
            "This is an individual-row/entry support check, not a proof about the full "
            "rational span or all PSD combinations."
        ),
    }


def main() -> None:
    for path in (
        WITNESS,
        WITNESS_MANIFEST,
        WAVE150_VERIFY,
        WAVE161_VERIFY,
        FIRST_MOMENT_AUDIT,
        WAVE147_COEFFICIENTS,
        WAVE148_MARKED_ROWS,
    ):
        require(path.is_file(), f"missing input: {path}")

    hashes = {
        "wave159_fifteen_cut_witness": sha256(WITNESS),
        "wave150_independent_verification": sha256(WAVE150_VERIFY),
        "wave161_independent_verification": sha256(WAVE161_VERIFY),
        "wave147_coefficients_gzip": sha256(WAVE147_COEFFICIENTS),
        "wave148_marked_rows_gzip": sha256(WAVE148_MARKED_ROWS),
    }
    require(
        hashes["wave159_fifteen_cut_witness"] == EXPECTED_WITNESS_SHA256,
        "Wave159 witness hash drift",
    )
    require(
        hashes["wave150_independent_verification"]
        == EXPECTED_WAVE150_VERIFY_SHA256,
        "Wave150 verification hash drift",
    )
    require(
        hashes["wave161_independent_verification"]
        == EXPECTED_WAVE161_VERIFY_SHA256,
        "Wave161 verification hash drift",
    )
    require(
        hashes["wave147_coefficients_gzip"]
        == EXPECTED_WAVE147_COEFFICIENTS_SHA256,
        "Wave147 coefficient hash drift",
    )
    require(
        hashes["wave148_marked_rows_gzip"]
        == EXPECTED_WAVE148_MARKED_ROWS_SHA256,
        "Wave148 marked-row hash drift",
    )
    require(
        manifest_hash(
            WITNESS_MANIFEST,
            "attempts/wave159-four-root-cut-loop/"
            "exact-witness-after-fifteen-cuts.json",
        )
        == EXPECTED_WITNESS_SHA256,
        "Wave159 manifest does not bind the witness",
    )

    witness = load(WITNESS)
    verify150 = load(WAVE150_VERIFY)
    verify161 = load(WAVE161_VERIFY)
    first = load(FIRST_MOMENT_AUDIT)

    require(first["status"] == "E0_MOTIF_FIRST_MOMENT_AUDIT_PASS", "first-moment audit")
    hdelta = first["motifs"]["HDelta_Z2_H18"]
    require(hdelta["unlabelled_coefficient_in_sum_D"] == 1, "H_delta flag coefficient")
    require(
        first["canonical_crosscheck"]["observed_masks"]["HDelta"]
        == H_DELTA_MASK,
        "H_delta canonical mask",
    )
    require(
        first["E0_first_moment"]["conclusion"]
        == "sum_r E0(r)=8316-n3-z11/4",
        "first-moment formula",
    )

    verdict150 = verify150["verdict"]
    require(verdict150["overall"] == "PASS_WITH_SCOPE", "Wave150 verdict")
    require(verdict150["Wave147_all_2414_matrices"] == "PASS", "Wave147 matrices")
    require(verdict150["Wave148_all_5384_rows"] == "PASS", "Wave148 rows")
    require(
        verify150["wave147"]["class_stream_counts"] == {
            "5": 21,
            "6": 62,
            "7": 208,
            "8": 916,
        },
        "class stream sizes",
    )
    require(
        verify150["wave147"]["full_matrix_records_reconstructed"] == 2414,
        "matrix record count",
    )
    require(verify150["wave148"]["vertex_rows"] == 944, "marked-vertex rows")
    require(verify150["wave148"]["ordered_pair_rows"] == 4440, "marked-pair rows")

    verdict161 = verify161["verdict"]
    witness_check = verify161["witness"]
    require(verdict161["fifteen_cut_finite_relaxation"] == "EXACT_RATIONAL_FEASIBLE", "Wave161 verdict")
    require(witness_check["nonnegative_coordinates"], "witness nonnegativity")
    require(witness_check["base_nontrivial_equalities"] == 10310, "base row count")
    require(witness_check["all_equalities"] == 10313, "full retained row count")
    require(witness_check["deletion_equalities"] == 208, "deletion rows")
    require(witness_check["marked_equalities"] == 5384, "marked rows")
    require(
        witness_check["pair_root_upper_entries"]
        == {"ordered_edge": 2211, "ordered_nonedge": 3828},
        "pair-root entries",
    )
    require(verify161["metadata_audit"]["actual_retained_cut_count"] == 15, "retained cut count")

    x7 = witness["x7_support"]
    masks = [int(record["canonical_mask"]) for record in x7]
    require(len(masks) == len(set(masks)) == 204, "x7 support shape")
    counts7 = {int(record["canonical_mask"]): fraction(record["count"]) for record in x7}
    require(all(value > 0 for value in counts7.values()), "x7 positivity")
    require(sum(counts7.values(), Fraction()) == comb(N, 7), "x7 total")

    x8 = witness["x8_support"]
    masks8 = [int(record["canonical_mask"]) for record in x8]
    require(len(masks8) == len(set(masks8)) == 887, "x8 support shape")
    counts8 = [fraction(record["count"]) for record in x8]
    require(all(value > 0 for value in counts8), "x8 positivity")
    require(sum(counts8, Fraction()) == comb(N, 8), "x8 total")

    y = int(witness["x7_record"]["y"])
    z11 = int(witness["x7_record"]["h11"])
    require(y == z11 // 4 == N3_ENDPOINT, "endpoint z11/y coordinate")
    hdelta_count = counts7.get(H_DELTA_MASK, Fraction())
    require(hdelta_count == 0, "H_delta must vanish in the pseudowitness")
    prism_count = Fraction(4158 - N3_ENDPOINT, 3)
    e0_from_motifs = 6 * prism_count + hdelta_count
    e0_from_affine_formula = Fraction(8316) - N3_ENDPOINT - Fraction(z11, 4)
    require(e0_from_motifs == e0_from_affine_formula == 0, "E0 total boundary")

    direct_pairs = direct_pair_audit()
    wave_visibility = wave147_148_visibility_audit()
    k8_witness_count = next(
        (
            fraction(record["count"])
            for record in x8
            if int(record["canonical_mask"]) == ORDER8_ADJACENT_SIDE_PAIR_MASK
        ),
        Fraction(),
    )
    require(k8_witness_count == 0, "K8 coordinate in boundary pseudowitness")

    result = {
        "status": "ORDER8_E0_POSITIVE_LOWER_BOUND_BOUNDARY_PASS",
        "sealed_input_sha256": hashes,
        "verified_resource_counts": {
            "locally_admissible_order8_classes": 916,
            "ordinary_7_to_8_deletion_rows": 208,
            "marked_vertex_rows": 944,
            "marked_pair_rows": 4440,
            "pair_root_coefficient_matrices": 2414,
            "base_nontrivial_equalities": 10310,
            "retained_four_root_scalar_cuts": 15,
        },
        "exact_rational_pseudowitness": {
            "n3": N3_ENDPOINT,
            "z11": z11,
            "z11_over_4": y,
            "prism_count": str(prism_count),
            "H_delta_canonical_mask": H_DELTA_MASK,
            "H_delta_count": str(hdelta_count),
            "sum_E0_from_6P_plus_H_delta": str(e0_from_motifs),
            "sum_E0_from_affine_formula": str(e0_from_affine_formula),
            "x7_support": len(x7),
            "x8_support": len(x8),
            "order8_adjacent_side_pair_K8_count": str(k8_witness_count),
            "all_coordinates_nonnegative": True,
        },
        "direct_E0_second_moment": {
            "status": "DIRECT_PAIR_DECOMPOSITION_PASS",
            "definitions": {
                "T": "sum_r E0(r)",
                "M_E": "sum_r binom(E0(r),2)",
                "R_q": (
                    "number of unordered distinct E0-event pairs at one root whose "
                    "two flag vertex sets have union order q"
                ),
            },
            "exact_identities": [
                "M_E = 4*x_127242964 + R_9 + R_10 + R_11 + R_12 + R_13",
                "sum_r E0(r)^2 = T + 8*x_127242964 + 2*(R_9+R_10+R_11+R_12+R_13)",
                "K_support:=sum_r binom(84-E0(r),2) = 99*binom(84,2)-83*T+M_E",
                "T = 8316-n3-z11/4",
            ],
            "functional_distinction": {
                "direct_pair_functional": "M_E=sum_r binom(E0(r),2)",
                "support_pair_functional": "K_support=sum_r binom(84-E0(r),2)",
                "conversion": "K_support=345114-83*T+M_E",
                "YYT_warning": (
                    "The aggregate YY^T moment is not this support-pair functional: "
                    "the latter uses Z=1_(Y>0), hence ZZ^T rather than YY^T."
                ),
            },
            "catalogue": direct_pairs,
            "wave147_wave148_visibility": wave_visibility,
        },
        "logical_consequence": {
            "pointwise_bound_implies_global": "E0(r)>=L for all r implies sum_r E0(r)>=99L",
            "boundary_value": "sum_r E0(r)=0",
            "excluded_certificate_scope": (
                "No positive L can be derived solely as a valid consequence of the checked "
                "nonnegative order-7/8 count cone, the 208+944+4440 linear rows, the two "
                "Wave147 pair-root centered PSD blocks, and the retained fifteen scalar cuts."
            ),
        },
        "arity_boundary": {
            "distinct_pair_union_order_histogram": direct_pairs["union_order_histogram"],
            "only_order8_distinct_pair_sector": "same-fibre adjacent side-side",
            "two_side_flags_max_union_order": 11,
            "side_and_diagonal_flags_max_union_order": 12,
            "two_diagonal_flags_max_union_order": 13,
            "maxima_pass_induced_pair_upper_and_partial_BP": True,
            "interpretation": (
                "The full factorial term in sum E0(r)^2 is not represented merely by "
                "the order-eight class deck; order eight sees only the sufficiently "
                "overlapping subcases unless an additional reduction identity is proved."
            ),
        },
        "marked_identity_boundary": {
            "Wave148_extension_arity": "one exterior vertex: marked order7 -> induced order8",
            "missing_for_R9_to_R13": (
                "joint extensions by at least two exterior vertices, including their mutual "
                "adjacency and simultaneous incidences"
            ),
            "Wave147_pair_root_scope": (
                "products of order5 flags sharing an ordered two-vertex root; union order at most 8"
            ),
            "conclusion": (
                "No existing row or matrix coefficient directly contracts R9..R13.  "
                "A derived rational-span or PSD consequence remains logically possible, "
                "but would require a separate explicit certificate."
            ),
        },
        "scope_wall": {
            "pseudowitness_is_graph": False,
            "full_four_root_covariance_satisfied": False,
            "actual_positive_E0_lower_bound_refuted": False,
            "next_target": (
                "Use full root-local/four-root covariance or order-9-to-13 overlap "
                "compatibility; the listed pair-root order-eight relaxation alone is exhausted."
            ),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
