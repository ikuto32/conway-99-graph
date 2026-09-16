"""Symmetry-reduced exact local expansion for the E0=72, Q>=3 frontier.

The older local-expansion engine loops over the complete Cartesian product of
the seven root-group matchings.  That is perfectly adequate for E0=73, but the
E0=72 input contains more than one billion labelled completions.  This module
computes exactly the same quantities without visiting that full product:

* labelled fibre-state assignments are quotiented by the *full* weighted
  support stabilizer (root-group permutations and sign flips);
* the overlap block-square histogram is an exact convolution of the seven
  independent group histograms;
* induced-pair upper bounds are checked monotonically while matching choices
  are added; and
* the forced-C4 support condition is represented by the down-closure of its
  exact allowed incidence vectors, permitting sound prefix pruning.

Every quotient is checked for closure.  Counts are restored with exact orbit
weights, and surviving graph orbits are computed with the full original group
action.  The ``--preset e73`` mode writes separate check artifacts and is used
to compare this engine against the already completed exhaustive E73 result.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import scratch_general_e75_local_expansion as generic
import scratch_root_e73_q4_port_census as extended_ports
from scratch_theory_local_psd_filter import bilinear_coefficients
from scratch_theory_unsigned_kernel_filter import (
    linear_system_status,
    nullspace,
    psd_by_principal_minors,
)


@dataclass(frozen=True)
class Preset:
    name: str
    model_e0: int
    port_path: Path
    count_path: Path
    output_path: Path
    rep_path: Path
    part_prefix: str
    expected_support_rows: int
    expected_state_assignments: int
    expected_overlap_edges: int
    expected_completions: int
    reference_path: Path | None
    support_filter_path: Path | None
    global_mask_canonical: bool
    local_gram_filter: bool


PRESETS = {
    "e71gram": Preset(
        name="e71gram",
        model_e0=71,
        port_path=Path("scratch_root_e71_q2_port_feasible_states.json"),
        count_path=Path("scratch_root_e71_q2_local_completion_counts.json"),
        output_path=Path("scratch_root_e71_q2_gram_fast_expansion.json"),
        rep_path=Path("scratch_root_e71_q2_gram_fast_local_graph_reps.json"),
        part_prefix="scratch_root_e71_q2_gram_fast_expansion_part_",
        expected_support_rows=1512,
        expected_state_assignments=361900,
        expected_overlap_edges=26,
        expected_completions=15215493120,
        reference_path=None,
        support_filter_path=Path("scratch_root_e71_unsigned_kernel_filter.json"),
        global_mask_canonical=False,
        local_gram_filter=True,
    ),
    "e72": Preset(
        name="e72",
        model_e0=72,
        port_path=Path("scratch_general_e72_q3_port_feasible_states.json"),
        count_path=Path("scratch_general_e72_q3_local_completion_counts.json"),
        output_path=Path("scratch_general_e72_q3_fast_expansion.json"),
        rep_path=Path("scratch_general_e72_q3_fast_local_graph_reps.json"),
        part_prefix="scratch_general_e72_q3_fast_expansion_part_",
        expected_support_rows=377,
        expected_state_assignments=15586,
        expected_overlap_edges=24,
        expected_completions=1018392576,
        reference_path=None,
        support_filter_path=None,
        global_mask_canonical=True,
        local_gram_filter=False,
    ),
    "e72gram": Preset(
        name="e72gram",
        model_e0=72,
        port_path=Path("scratch_general_e72_q3_port_feasible_states.json"),
        count_path=Path("scratch_general_e72_q3_local_completion_counts.json"),
        output_path=Path("scratch_general_e72_q3_gram_fast_expansion.json"),
        rep_path=Path("scratch_general_e72_q3_gram_fast_local_graph_reps.json"),
        part_prefix="scratch_general_e72_q3_gram_fast_expansion_part_",
        expected_support_rows=162,
        expected_state_assignments=8354,
        expected_overlap_edges=24,
        expected_completions=596148224,
        reference_path=None,
        support_filter_path=Path("scratch_theory_e72_unsigned_kernel_filter.json"),
        # A canonical state-orbit representative followed by a canonical
        # stabilizer-orbit representative is an exact transversal and avoids
        # applying every full-group element merely to minimize an integer mask.
        global_mask_canonical=False,
        local_gram_filter=True,
    ),
    "e73": Preset(
        name="e73",
        model_e0=73,
        port_path=Path("scratch_general_e73_q4_port_feasible_states.json"),
        count_path=Path("scratch_general_e73_q4_local_completion_counts.json"),
        output_path=Path("scratch_general_e73_q4_fast_expansion.json"),
        rep_path=Path("scratch_general_e73_q4_fast_local_graph_reps.json"),
        part_prefix="scratch_general_e73_q4_fast_expansion_part_",
        expected_support_rows=58,
        expected_state_assignments=980,
        expected_overlap_edges=22,
        expected_completions=21061632,
        reference_path=Path("scratch_general_e73_q4_local_expansion.json"),
        support_filter_path=None,
        global_mask_canonical=True,
        local_gram_filter=False,
    ),
}


# Independent signature-census totals used to guard macro materialization.
# Keeping these preset-specific values here preserves the established E72
# checks while admitting the separately audited E71 Gram frontier.
GRAM_MACRO_EXPECTATIONS = {
    "e71gram": {
        "entries": 193,
        "labelled_coverage": 61_112_320,
        "state_orbits": 14_607,
        "nonempty_support_rows": 93,
    },
    "e72gram": {
        "entries": 177,
        "labelled_coverage": 141_545_472,
        "state_orbits": 578,
        "nonempty_support_rows": 71,
    },
}


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def part_path(preset: Preset, partition_index: int) -> Path:
    return Path(f"{preset.part_prefix}{partition_index:02d}.json")


def configure_generic(preset: Preset) -> None:
    # Deficits 1--3 are identical to the original E75 table.  E72 can also
    # contain the unique deficit-four (empty) fibre.
    assert all(
        extended_ports.FIBRE_STATES[d] == generic.port75.FIBRE_STATES[d]
        for d in (1, 2, 3)
    )
    generic.port75 = extended_ports
    generic.PORT_PATH = preset.port_path
    generic.COUNT_PATH = preset.count_path
    generic.MODEL_E0 = preset.model_e0
    generic.EXPECTED_SUPPORT_ROWS = preset.expected_support_rows
    generic.EXPECTED_STATE_ASSIGNMENTS = preset.expected_state_assignments
    generic.EXPECTED_OVERLAP_EDGES = preset.expected_overlap_edges
    generic.EXPECTED_COMPLETIONS = preset.expected_completions
    generic.MIN_Q = None


def row_key(row):
    return tuple(sorted(row["partition"], reverse=True)), row["compression_orbit_index"]


def input_rows(preset: Preset):
    port = json.loads(preset.port_path.read_text(encoding="utf-8"))
    counts = json.loads(preset.count_path.read_text(encoding="utf-8"))
    rows = [row for row in port["rows"] if row["locally_port_feasible_assignments"]]
    if preset.support_filter_path is not None:
        support_filter = json.loads(
            preset.support_filter_path.read_text(encoding="utf-8")
        )
        passing = {
            row["source_row_index"]
            for row in support_filter["rows"]
            if row["passes_exact_support_diagonal_psd_test"]
        }
        assert all("source_row_index" in row for row in rows)
        rows = [row for row in rows if row["source_row_index"] in passing]
    count_map = {row_key(row): row for row in counts["rows"]}
    assert len(rows) == preset.expected_support_rows
    assert all(row_key(row) in count_map for row in rows)
    partition_index = {
        tuple(part["partition"]): part["partition_index"] for part in port["by_partition"]
    }
    grouped = {}
    for row in rows:
        index = partition_index[tuple(row["partition"])]
        grouped.setdefault(index, []).append((row, count_map[row_key(row)]))
    return port, grouped


def assignment_q(exceptional, state_indices) -> int:
    return generic.assignment_diagonal_count(exceptional, state_indices)


class RowGeometry:
    """Immutable labelled geometry and the exact weighted symmetry action."""

    def __init__(self, source):
        self.supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
        self.deficits = tuple(item["deficit"] for item in source["exceptional_supports"])
        (
            self.vertices,
            self.pair_positions,
            self.pair_index,
            self.mask_of,
            self.edges_of,
        ) = generic.vertices_and_masks(self.supports)
        self.vertex_index = {vertex: index for index, vertex in enumerate(self.vertices)}
        self.fibre_of = {
            generic.local79.vertex_label(support, bits): fibre
            for fibre, support in enumerate(self.supports)
            for bits in itertools.product((0, 1), repeat=2)
        }
        self.fibre_index = tuple(self.fibre_of[vertex] for vertex in self.vertices)
        (
            self.actions,
            self.full_stabilizer,
            self.used_groups,
        ) = generic.weighted_vertex_actions(
            self.supports,
            self.deficits,
            self.vertices,
            source["weighted_stabilizer_order"],
        )
        # This table depends only on the support row.  Its direct construction
        # enumerates small disjoint-fibre integer profiles and is deliberately
        # done once, not once per state orbit/search pass.
        self.forced_profiles = generic.build_forced_c4_profiles(self.supports)
        self.action_index = {action: index for index, action in enumerate(self.actions)}
        self._action_pair_maps = [None] * len(self.actions)
        self._component_images = [dict() for _ in self.actions]
        group_masks = [0] * len(generic.local79.GROUPS)
        for bit, (left, right) in enumerate(self.pair_positions):
            left_fibre = self.fibre_index[left]
            right_fibre = self.fibre_index[right]
            if left_fibre == right_fibre:
                continue
            common = set(self.supports[left_fibre]) & set(self.supports[right_fibre])
            if len(common) == 1:
                group_masks[next(iter(common))] |= 1 << bit
        self.overlap_group_masks = tuple(group_masks)

    def action_pair_map(self, action_index):
        cached = self._action_pair_maps[action_index]
        if cached is None:
            action = self.actions[action_index]
            cached = tuple(
                self.pair_index[tuple(sorted((action[left], action[right])))]
                for left, right in self.pair_positions
            )
            self._action_pair_maps[action_index] = cached
        return cached

    def transform(self, mask: int, action_index: int) -> int:
        pair_map = self.action_pair_map(action_index)
        answer = 0
        work = mask
        while work:
            low = work & -work
            answer |= 1 << pair_map[low.bit_length() - 1]
            work ^= low
        return answer

    def transform_local_graph(self, mask: int, internal: int, action_index: int) -> int:
        """Transform a local graph using cached root-group components."""
        cache = self._component_images[action_index]

        def image(component):
            if component not in cache:
                cache[component] = self.transform(component, action_index)
            return cache[component]

        answer = image(internal)
        overlap = mask ^ internal
        reconstructed = 0
        for group_mask in self.overlap_group_masks:
            component = overlap & group_mask
            reconstructed |= component
            answer |= image(component)
        assert reconstructed == overlap
        return answer

    def index_edges(self, edges):
        return tuple(
            sorted(
                tuple(sorted((self.vertex_index[left], self.vertex_index[right])))
                for left, right in edges
            )
        )

    def labelled_edges(self, mask: int):
        return frozenset(
            tuple(sorted((self.vertices[left], self.vertices[right])))
            for bit, (left, right) in enumerate(self.pair_positions)
            if (mask >> bit) & 1
        )


def oriented_assignment(geometry: RowGeometry, state_indices):
    return tuple(
        generic.fibre_variant(support, deficit, state_index)
        for support, deficit, state_index in zip(
            geometry.supports, geometry.deficits, state_indices
        )
    )


def internal_mask(geometry: RowGeometry, oriented) -> int:
    return geometry.mask_of(edge for data in oriented for edge in data["internal"])


def state_orbits(source, geometry: RowGeometry):
    """Quotient feasible labelled fibre states by the exact full action."""
    assignments = tuple(tuple(values) for values in source["feasible_state_indices"])
    masks = []
    for values in assignments:
        masks.append(internal_mask(geometry, oriented_assignment(geometry, values)))
    assert len(set(masks)) == len(masks), "fibre-state assignments must have unique internal graphs"
    assignment_by_mask = dict(zip(masks, assignments))
    feasible_masks = set(masks)
    remaining = set(masks)
    answer = []
    while remaining:
        representative_mask = min(remaining)
        orbit_masks = {
            geometry.transform(representative_mask, action_index)
            for action_index in range(len(geometry.actions))
        }
        assert orbit_masks <= feasible_masks, "feasible state set is not symmetry closed"
        stabilizer = tuple(
            action_index
            for action_index in range(len(geometry.actions))
            if geometry.transform(representative_mask, action_index) == representative_mask
        )
        assert len(geometry.actions) == len(orbit_masks) * len(stabilizer)
        representative = assignment_by_mask[representative_mask]
        q_values = {
            assignment_q(source["exceptional_supports"], assignment_by_mask[mask])
            for mask in orbit_masks
        }
        assert len(q_values) == 1, "Q must be invariant under the weighted action"
        answer.append(
            {
                "state_indices": representative,
                "internal_mask": representative_mask,
                "weight": len(orbit_masks),
                "stabilizer": stabilizer,
                "Q": next(iter(q_values)),
            }
        )
        remaining.difference_update(orbit_masks)
    assert sum(item["weight"] for item in answer) == len(assignments)
    return tuple(answer)


@dataclass(frozen=True)
class Choice:
    mask: int
    edges: tuple
    block_square: int
    block_counts: tuple


def matching_choices(geometry: RowGeometry, oriented, state_indices, cache):
    """Encode every group matching; block-square contributions are disjoint."""
    answer = []
    seen_fibre_pairs = set()
    for group in generic.local79.GROUPS:
        incident = tuple(
            index for index, support in enumerate(geometry.supports) if group in support
        )
        cache_key = (group, tuple(state_indices[index] for index in incident))
        if cache_key in cache:
            encoded = cache[cache_key]
            answer.append(encoded)
            fibre_pairs = {
                tuple(sorted((geometry.fibre_index[left], geometry.fibre_index[right])))
                for choice in encoded
                for left, right in choice.edges
            }
            assert not (seen_fibre_pairs & fibre_pairs)
            seen_fibre_pairs.update(fibre_pairs)
            continue
        encoded = []
        raw = generic.group_matchings(oriented, group)
        for matching in raw:
            edges = geometry.index_edges(matching)
            mask = 0
            counts = Counter()
            for left, right in edges:
                bit = geometry.pair_index[(left, right)]
                mask |= 1 << bit
                left_fibre = geometry.fibre_index[left]
                right_fibre = geometry.fibre_index[right]
                assert left_fibre != right_fibre
                fibre_pair = tuple(sorted((left_fibre, right_fibre)))
                common = set(geometry.supports[left_fibre]) & set(
                    geometry.supports[right_fibre]
                )
                assert common == {group}
                counts[fibre_pair] += 1
            encoded.append(
                Choice(
                    mask=mask,
                    edges=edges,
                    block_square=sum(value * value for value in counts.values()),
                    block_counts=tuple(sorted(counts.items())),
                )
            )
        assert len({choice.mask for choice in encoded}) == len(encoded)
        fibre_pairs = {
            tuple(sorted((geometry.fibre_index[left], geometry.fibre_index[right])))
            for choice in encoded
            for left, right in choice.edges
        }
        assert not (seen_fibre_pairs & fibre_pairs)
        seen_fibre_pairs.update(fibre_pairs)
        encoded = tuple(sorted(encoded, key=lambda choice: choice.mask))
        cache[cache_key] = encoded
        answer.append(encoded)
    return tuple(answer)


def convolved_square_histogram(by_group) -> Counter:
    """Small exact polynomial convolution (written without candidate expansion)."""
    distribution = Counter({0: 1})
    for choices in by_group:
        local = Counter(choice.block_square for choice in choices)
        updated = Counter()
        for left, left_count in distribution.items():
            for right, right_count in local.items():
                updated[left + right] += left_count * right_count
        distribution = updated
    return distribution


class GramSignatureFilter:
    """Exact rational Gram feasibility on overlap block-total signatures."""

    def __init__(self, geometry: RowGeometry):
        self.geometry = geometry
        supports = geometry.supports
        incidence_t = [
            [int(group in support) for support in supports]
            for group in generic.local79.GROUPS
        ]
        basis_columns = nullspace(incidence_t)
        self.dimension = len(basis_columns)
        self.W = [
            [basis_columns[column][row] for column in range(self.dimension)]
            for row in range(len(supports))
        ]
        self.base_coefficients = [
            bilinear_coefficients(self.W[index], self.W[index])
            for index in range(len(supports))
        ]
        self.base_targets = [Fraction(2 * deficit) for deficit in geometry.deficits]
        self.pairs_by_group = [[] for _ in generic.local79.GROUPS]
        for left, right in itertools.combinations(range(len(supports)), 2):
            common = set(supports[left]) & set(supports[right])
            if not common:
                continue
            assert len(common) == 1
            group = next(iter(common))
            self.pairs_by_group[group].append(
                (
                    (left, right),
                    bilinear_coefficients(self.W[left], self.W[right]),
                )
            )
        self.status_cache = {}
        assert self.partial_pass({}), "support-level Gram filter should have run first"

    def signature(self, group: int, choice: Choice):
        counts = dict(choice.block_counts)
        return tuple(counts.get(pair, 0) for pair, _ in self.pairs_by_group[group])

    def partial_pass(self, selected) -> bool:
        key = tuple(sorted(selected.items()))
        if key in self.status_cache:
            return self.status_cache[key]
        coefficients = list(self.base_coefficients)
        targets = list(self.base_targets)
        for group, signature in key:
            assert len(signature) == len(self.pairs_by_group[group])
            for count, (_pair, coefficient) in zip(
                signature, self.pairs_by_group[group]
            ):
                coefficients.append(coefficient)
                targets.append(Fraction(-count))
        status = linear_system_status(coefficients, targets)
        passing = status["consistent"]
        if passing and status.get("unique_solution") is not None:
            matrix = [
                [Fraction(0) for _ in range(self.dimension)]
                for _ in range(self.dimension)
            ]
            pairs = [
                (left, right)
                for left in range(self.dimension)
                for right in range(left, self.dimension)
            ]
            for value, (left, right) in zip(status["unique_solution"], pairs):
                matrix[left][right] = matrix[right][left] = value
            passing = psd_by_principal_minors(matrix)[0]
        self.status_cache[key] = passing
        return passing

    def feasible_classes(self, by_group):
        """Return every feasible group-signature product with exact weights."""
        classes = []
        for group, choices in enumerate(by_group):
            grouped = {}
            for choice in choices:
                grouped.setdefault(self.signature(group, choice), []).append(choice)
            # A constraint that is already impossible using only one group's
            # equations cannot be repaired by adding further equations.
            grouped = {
                signature: tuple(values)
                for signature, values in grouped.items()
                if self.partial_pass({group: signature})
            }
            classes.append(grouped)
        if any(not values for values in classes):
            return (), {"nodes": 0, "prefix_prunes": 0, "signature_domains": []}
        order = tuple(sorted(generic.local79.GROUPS, key=lambda group: len(classes[group])))
        selected = {}
        feasible = []
        nodes = 0
        prunes = 0

        def visit(depth):
            nonlocal nodes, prunes
            nodes += 1
            if depth == len(order):
                feasible.append(
                    tuple(classes[group][selected[group]] for group in generic.local79.GROUPS)
                )
                return
            group = order[depth]
            for signature in sorted(classes[group]):
                selected[group] = signature
                if self.partial_pass(selected):
                    visit(depth + 1)
                else:
                    prunes += 1
                del selected[group]

        visit(0)
        return tuple(feasible), {
            "nodes": nodes,
            "prefix_prunes": prunes,
            "signature_domains": [len(values) for values in classes],
            "feasible_signature_products": len(feasible),
        }


class PairSearch:
    """Monotone induced-pair search, optionally with exact BP-prefix pruning."""

    def __init__(self, geometry: RowGeometry, oriented, internal: int, build_bp=True):
        self.geometry = geometry
        self.oriented = oriented
        size = len(geometry.vertices)
        self.adjacency = [0] * size
        for bit, (left, right) in enumerate(geometry.pair_positions):
            if (internal >> bit) & 1:
                self.adjacency[left] |= 1 << right
                self.adjacency[right] |= 1 << left
        self.target = [
            [
                0 if left == right else 2 - len(set(geometry.vertices[left]) & set(geometry.vertices[right]))
                for right in range(size)
            ]
            for left in range(size)
        ]
        assert self.full_pair_ok(), "fixed internal graph already violates pair upper bound"
        self.internal = internal
        self.nodes = 0
        self.choice_attempts = 0
        self.pair_prunes = 0
        self.spectral_prunes = 0
        self.bp_prunes = 0
        self.pow5 = tuple(5**group for group in generic.local79.GROUPS)
        self.bp_codes = [0] * size
        if build_bp:
            self.bp_prefix, self.bp_final = self.build_bp_codes()
        else:
            self.bp_prefix = self.bp_final = None

    def pair_ok(self, left: int, right: int) -> bool:
        if left > right:
            left, right = right, left
        direct = (self.adjacency[left] >> right) & 1
        common = (self.adjacency[left] & self.adjacency[right]).bit_count()
        return direct + common <= self.target[left][right]

    def full_pair_ok(self) -> bool:
        return all(
            self.pair_ok(left, right)
            for left, right in itertools.combinations(range(len(self.adjacency)), 2)
        )

    def build_bp_codes(self):
        profiles = self.geometry.forced_profiles
        prefix_sets = []
        final_sets = []
        for vertex, fibre in enumerate(self.geometry.fibre_index):
            support = self.geometry.supports[fibre]
            data = self.oriented[fibre]
            fibre_vertices = {self.geometry.vertex_index[value] for value in data["vertices"]}
            a = sum((self.adjacency[vertex] >> other) & 1 for other in fibre_vertices - {vertex})
            profile = profiles[fibre]
            allowed = set()
            for wanted in profile["feasible_profiles"][a]:
                observed = tuple(
                    target - value for target, value in zip(profile["target"], wanted)
                )
                if min(observed, default=0) < 0:
                    continue
                code = sum(
                    value * self.pow5[group]
                    for group, value in zip(profile["external_groups"], observed)
                )
                allowed.add(code)
            final_sets.append(frozenset(allowed))
            prefixes = set()
            for code in allowed:
                digits = tuple((code // self.pow5[group]) % 5 for group in generic.local79.GROUPS)
                ranges = tuple(range(value + 1) for value in digits)
                for values in itertools.product(*ranges):
                    prefixes.add(sum(value * power for value, power in zip(values, self.pow5)))
            prefix_sets.append(frozenset(prefixes))
        return tuple(prefix_sets), tuple(final_sets)

    def edge_bp_increments(self, left: int, right: int):
        left_support = self.geometry.supports[self.geometry.fibre_index[left]]
        right_support = self.geometry.supports[self.geometry.fibre_index[right]]
        common = set(left_support) & set(right_support)
        assert len(common) == 1
        shared = next(iter(common))
        left_external = next(group for group in right_support if group != shared)
        right_external = next(group for group in left_support if group != shared)
        return self.pow5[left_external], self.pow5[right_external]

    def try_choice(self, choice: Choice, use_bp: bool) -> bool:
        added = []
        for left, right in choice.edges:
            old_left = self.adjacency[left]
            old_right = self.adjacency[right]
            assert not ((old_left >> right) & 1), "overlap edge selected twice"
            self.adjacency[left] = old_left | (1 << right)
            self.adjacency[right] = old_right | (1 << left)
            inc_left = inc_right = 0
            if use_bp:
                inc_left, inc_right = self.edge_bp_increments(left, right)
                self.bp_codes[left] += inc_left
                self.bp_codes[right] += inc_right
            added.append((left, right, inc_left, inc_right))
            valid = self.pair_ok(left, right)
            work = old_left
            while valid and work:
                low = work & -work
                other = low.bit_length() - 1
                valid = self.pair_ok(right, other)
                work ^= low
            work = old_right
            while valid and work:
                low = work & -work
                other = low.bit_length() - 1
                valid = self.pair_ok(left, other)
                work ^= low
            if valid and use_bp:
                valid = (
                    self.bp_codes[left] in self.bp_prefix[left]
                    and self.bp_codes[right] in self.bp_prefix[right]
                )
                if not valid:
                    self.bp_prunes += 1
            if not valid:
                if not use_bp or (
                    self.bp_codes[left] in self.bp_prefix[left]
                    and self.bp_codes[right] in self.bp_prefix[right]
                ):
                    self.pair_prunes += 1
                self.rollback(added, use_bp)
                return False
        return True

    def rollback(self, added, use_bp: bool) -> None:
        for left, right, inc_left, inc_right in reversed(added):
            self.adjacency[left] ^= 1 << right
            self.adjacency[right] ^= 1 << left
            if use_bp:
                self.bp_codes[left] -= inc_left
                self.bp_codes[right] -= inc_right

    def choice_is_pair_valid_from_base(self, choice: Choice) -> bool:
        ok = self.try_choice(choice, False)
        if ok:
            self.rollback(
                [(left, right, 0, 0) for left, right in choice.edges], False
            )
        return ok

    def search(
        self, by_group, square_limit: int, use_bp: bool, collect_masks: bool = False
    ):
        # Choices invalid against the fixed internal graph can never become
        # valid after adding edges, so this is a monotone and exact prefilter.
        filtered = []
        for choices in by_group:
            filtered.append(
                tuple(choice for choice in choices if self.choice_is_pair_valid_from_base(choice))
            )
        if any(not choices for choices in filtered):
            return Counter(), []

        # Low branching groups establish forced adjacencies early.  Ties put
        # groups with more edges first, which tends to expose common-neighbour
        # violations sooner.
        ordered = tuple(
            sorted(
                filtered,
                key=lambda choices: (len(choices), -len(choices[0].edges)),
            )
        )
        suffix_min = [0] * (len(ordered) + 1)
        for depth in range(len(ordered) - 1, -1, -1):
            suffix_min[depth] = suffix_min[depth + 1] + min(
                choice.block_square for choice in ordered[depth]
            )

        histogram = Counter()
        masks = []

        def visit(depth: int, square: int, overlap_mask: int) -> None:
            self.nodes += 1
            if square + suffix_min[depth] > square_limit:
                self.spectral_prunes += 1
                return
            if depth == len(ordered):
                if use_bp:
                    assert all(
                        code in allowed
                        for code, allowed in zip(self.bp_codes, self.bp_final)
                    )
                if use_bp or collect_masks:
                    masks.append(self.internal | overlap_mask)
                histogram[square] += 1
                return
            for choice in ordered[depth]:
                next_square = square + choice.block_square
                if next_square + suffix_min[depth + 1] > square_limit:
                    self.spectral_prunes += 1
                    continue
                self.choice_attempts += 1
                if not self.try_choice(choice, use_bp):
                    continue
                visit(depth + 1, next_square, overlap_mask | choice.mask)
                self.rollback(
                    [(left, right, *self.edge_bp_increments(left, right))
                     if use_bp else (left, right, 0, 0)
                     for left, right in choice.edges],
                    use_bp,
                )

        if use_bp and any(0 not in allowed for allowed in self.bp_prefix):
            return Counter(), []
        visit(0, 0, 0)
        assert all(code == 0 for code in self.bp_codes)
        assert self.full_pair_ok()
        return histogram, masks


class ForcedBPCSP:
    """Exact binary CSP form of the forced-C4 support condition.

    A vertex in a fibre supported on ``{g,h}`` receives all overlap neighbours
    through choices for groups g and h.  Consequently the final BP condition
    for all four vertices of that fibre is a binary relation between precisely
    those two group-choice variables.  Intersecting these relations during DFS
    is exact (not a relaxation).
    """

    def __init__(self, pair_search: PairSearch, by_group, prefilter_pair=True):
        self.search = pair_search
        self.geometry = pair_search.geometry
        self.oriented = pair_search.oriented
        self.by_group = tuple(
            tuple(
                choice
                for choice in choices
                if (
                    not prefilter_pair
                    or pair_search.choice_is_pair_valid_from_base(choice)
                )
            )
            for choices in by_group
        )
        self.neighbours = [set() for _ in generic.local79.GROUPS]
        self.signatures = {}
        self.allowed = {}
        self.impossible = any(not choices for choices in self.by_group)
        if not self.impossible:
            self.build_relations()
        self.universal = (
            not self.impossible
            and all(
                all(
                    allowed_mask == (1 << len(self.by_group[other])) - 1
                    for allowed_mask in self.allowed[(group, other)].values()
                )
                for group in generic.local79.GROUPS
                for other in self.neighbours[group]
            )
        )

    def contribution_signature(self, group: int, fibre: int):
        vertices = tuple(
            self.geometry.vertex_index[value]
            for value in self.oriented[fibre]["vertices"]
        )
        position = {vertex: index for index, vertex in enumerate(vertices)}
        signatures = []
        for choice in self.by_group[group]:
            values = [0] * len(vertices)
            for left, right in choice.edges:
                inc_left, inc_right = self.search.edge_bp_increments(left, right)
                if left in position:
                    values[position[left]] += inc_left
                if right in position:
                    values[position[right]] += inc_right
            signatures.append(tuple(values))
        return tuple(signatures), vertices

    def build_relations(self) -> None:
        for fibre, support in enumerate(self.geometry.supports):
            left_group, right_group = support
            self.neighbours[left_group].add(right_group)
            self.neighbours[right_group].add(left_group)
            left_signatures, vertices = self.contribution_signature(left_group, fibre)
            right_signatures, right_vertices = self.contribution_signature(right_group, fibre)
            assert vertices == right_vertices
            self.signatures[(left_group, right_group)] = left_signatures
            self.signatures[(right_group, left_group)] = right_signatures

            right_classes = {}
            for index, signature in enumerate(right_signatures):
                right_classes[signature] = right_classes.get(signature, 0) | (1 << index)
            left_classes = {}
            for index, signature in enumerate(left_signatures):
                left_classes[signature] = left_classes.get(signature, 0) | (1 << index)

            left_allowed = {}
            for left_signature in set(left_signatures):
                mask = 0
                for right_signature, class_mask in right_classes.items():
                    if all(
                        left_value + right_value in self.search.bp_final[vertex]
                        for vertex, left_value, right_value in zip(
                            vertices, left_signature, right_signature
                        )
                    ):
                        mask |= class_mask
                left_allowed[left_signature] = mask
            right_allowed = {}
            for right_signature in set(right_signatures):
                mask = 0
                for left_signature, class_mask in left_classes.items():
                    if all(
                        left_value + right_value in self.search.bp_final[vertex]
                        for vertex, left_value, right_value in zip(
                            vertices, left_signature, right_signature
                        )
                    ):
                        mask |= class_mask
                right_allowed[right_signature] = mask
            self.allowed[(left_group, right_group)] = left_allowed
            self.allowed[(right_group, left_group)] = right_allowed

    def compatible_mask(self, group: int, option: int, other: int) -> int:
        signature = self.signatures[(group, other)][option]
        return self.allowed[(group, other)][signature]

    def signature_class_products(self):
        """Enumerate BP-feasible half-signature classes, never raw matchings."""
        if self.impossible:
            return (), {"nodes": 0, "prefix_prunes": 0, "domain_sizes": []}
        classes = []
        for group, choices in enumerate(self.by_group):
            grouped = {}
            for option, choice in enumerate(choices):
                signature = tuple(
                    (other, self.signatures[(group, other)][option])
                    for other in sorted(self.neighbours[group])
                )
                grouped.setdefault(signature, []).append((option, choice))
            classes.append(
                tuple(
                    (signature, tuple(values))
                    for signature, values in sorted(grouped.items())
                )
            )
        order = tuple(
            sorted(
                generic.local79.GROUPS,
                key=lambda group: (len(classes[group]), -len(self.neighbours[group]), group),
            )
        )
        assigned = {}
        products = []
        nodes = 0
        prunes = 0

        def compatible(group, representative_option):
            for other, other_option in assigned.items():
                if other not in self.neighbours[group]:
                    continue
                if not (
                    self.compatible_mask(group, representative_option, other)
                    & (1 << other_option)
                ):
                    return False
            return True

        def visit(depth):
            nonlocal nodes, prunes
            nodes += 1
            if depth == len(order):
                chosen = []
                for group in generic.local79.GROUPS:
                    signature = tuple(
                        (other, self.signatures[(group, other)][assigned[group]])
                        for other in sorted(self.neighbours[group])
                    )
                    bucket = next(
                        values for key, values in classes[group] if key == signature
                    )
                    chosen.append(tuple(choice for _option, choice in bucket))
                products.append(tuple(chosen))
                return
            group = order[depth]
            for _signature, bucket in classes[group]:
                representative_option = bucket[0][0]
                if not compatible(group, representative_option):
                    prunes += 1
                    continue
                assigned[group] = representative_option
                visit(depth + 1)
                del assigned[group]

        visit(0)
        return tuple(products), {
            "nodes": nodes,
            "prefix_prunes": prunes,
            "domain_sizes": [len(values) for values in classes],
            "feasible_signature_products": len(products),
        }

    def run(self, square_limit: int):
        if self.impossible:
            return Counter(), []
        domains = [(1 << len(choices)) - 1 for choices in self.by_group]
        assigned = [False] * len(self.by_group)
        minimum_cost = [min(choice.block_square for choice in choices) for choices in self.by_group]
        histogram = Counter()
        masks = []

        def visit(depth: int, square: int, overlap_mask: int) -> None:
            self.search.nodes += 1
            if depth == len(self.by_group):
                if square <= square_limit:
                    histogram[square] += 1
                    masks.append(self.search.internal | overlap_mask)
                else:
                    self.search.spectral_prunes += 1
                return
            remaining_minimum = sum(
                minimum_cost[group]
                for group in generic.local79.GROUPS
                if not assigned[group]
            )
            if square + remaining_minimum > square_limit:
                self.search.spectral_prunes += 1
                return
            group = min(
                (value for value in generic.local79.GROUPS if not assigned[value]),
                key=lambda value: (
                    domains[value].bit_count(),
                    -sum(assigned[other] for other in self.neighbours[value]),
                    value,
                ),
            )
            old_group_domain = domains[group]
            work = old_group_domain
            while work:
                low = work & -work
                option = low.bit_length() - 1
                work ^= low
                choice = self.by_group[group][option]
                self.search.choice_attempts += 1
                if not self.search.try_choice(choice, False):
                    continue
                assigned[group] = True
                domains[group] = low
                changed = []
                valid = True
                for other in self.neighbours[group]:
                    allowed = self.compatible_mask(group, option, other)
                    narrowed = domains[other] & allowed
                    if not narrowed:
                        valid = False
                        self.search.bp_prunes += 1
                        break
                    if narrowed != domains[other]:
                        changed.append((other, domains[other]))
                        domains[other] = narrowed
                if valid:
                    visit(depth + 1, square + choice.block_square, overlap_mask | choice.mask)
                for other, old_domain in reversed(changed):
                    domains[other] = old_domain
                domains[group] = old_group_domain
                assigned[group] = False
                self.search.rollback(
                    [(left, right, 0, 0) for left, right in choice.edges], False
                )
        visit(0, 0, 0)
        assert self.search.full_pair_ok()
        return histogram, masks


def graph_orbits_from_state_representatives(
    geometry: RowGeometry, state_results, global_mask_canonical: bool
):
    records_by_canonical = {}
    weighted_graph_count = 0
    for state in state_results:
        graph_set = set(state["forced_masks"])
        assert len(graph_set) == len(state["forced_masks"])
        remaining = set(graph_set)
        while remaining:
            seed = min(remaining)
            stabilizer_orbit = {
                geometry.transform_local_graph(
                    seed, state["internal_mask"], action_index
                )
                for action_index in state["stabilizer"]
            }
            assert stabilizer_orbit <= graph_set, "state-stabilizer graph closure failure"
            full_orbit_size = state["weight"] * len(stabilizer_orbit)
            if global_mask_canonical:
                full_orbit = {
                    geometry.transform_local_graph(
                        seed, state["internal_mask"], action_index
                    )
                    for action_index in range(len(geometry.actions))
                }
                assert len(full_orbit) == full_orbit_size
                canonical = min(full_orbit)
            else:
                # The state itself is the minimum internal mask in its full
                # orbit, and seed is the minimum graph mask under its state
                # stabilizer.  This two-stage canonicalization is a complete,
                # deterministic transversal even when seed is not the global
                # minimum integer among all full-orbit masks.
                canonical = seed
            assert canonical not in records_by_canonical, "duplicate full graph orbit"
            records_by_canonical[canonical] = {
                "mask_hex": hex(canonical),
                "orbit_size": full_orbit_size,
                "edges": geometry.edges_of(canonical),
                "Q": state["Q"],
            }
            weighted_graph_count += full_orbit_size
            remaining.difference_update(stabilizer_orbit)
    records = [records_by_canonical[key] for key in sorted(records_by_canonical)]
    assert sum(row["orbit_size"] for row in records) == weighted_graph_count
    return records


def add_weighted(target: Counter, source: Counter, weight: int) -> None:
    for key, value in source.items():
        target[key] += weight * value


def audit_row(
    source,
    expected_completions,
    global_mask_canonical=True,
    local_gram_filter=False,
):
    geometry = RowGeometry(source)
    orbits = state_orbits(source, geometry)
    state_q = Counter()
    completion_q = Counter()
    spectral_q = Counter()
    gram_q = Counter()
    pair_q = Counter()
    forced_q = Counter()
    actual_squares = Counter()
    spectral_squares = Counter()
    gram_squares = Counter()
    pair_squares = Counter()
    forced_squares = Counter()
    pair_nodes = 0
    forced_nodes = 0
    state_results = []
    direct_control = 0
    square_limit = math.floor(
        Fraction(source["joint_square_budget"])
        - Fraction(source["disjoint_continuous_minimum"])
    )
    matching_cache = {}
    gram_filter = GramSignatureFilter(geometry) if local_gram_filter else None
    gram_signature_nodes = 0
    gram_signature_products = 0
    bp_signature_nodes = 0
    bp_signature_products = 0

    for state in orbits:
        oriented = oriented_assignment(geometry, state["state_indices"])
        assert internal_mask(geometry, oriented) == state["internal_mask"]
        by_group = matching_choices(
            geometry, oriented, state["state_indices"], matching_cache
        )
        assert sum(len(choices[0].edges) for choices in by_group) == generic.EXPECTED_OVERLAP_EDGES
        raw_histogram = convolved_square_histogram(by_group)
        raw_count = sum(raw_histogram.values())
        assert raw_count == math.prod(len(choices) for choices in by_group)
        weight = state["weight"]
        q_value = state["Q"]
        state_q[q_value] += weight
        completion_q[q_value] += weight * raw_count
        add_weighted(actual_squares, raw_histogram, weight)
        spectral_histogram = Counter(
            {square: count for square, count in raw_histogram.items() if square <= square_limit}
        )
        spectral_count = sum(spectral_histogram.values())
        if spectral_count:
            spectral_q[q_value] += weight * spectral_count
        add_weighted(spectral_squares, spectral_histogram, weight)

        if gram_filter is None:
            class_products = (by_group,)
            gram_histogram = spectral_histogram.copy()
        else:
            all_class_products, gram_stats = gram_filter.feasible_classes(by_group)
            gram_signature_nodes += gram_stats["nodes"]
            gram_signature_products += len(all_class_products)
            class_products = []
            gram_histogram = Counter()
            for product_classes in all_class_products:
                squares = {
                    choice.block_square
                    for choices in product_classes
                    for choice in choices
                }
                # This cross-group set assertion is intentionally weaker than
                # equality: different groups may have different fixed costs.
                assert squares
                square = sum(choices[0].block_square for choices in product_classes)
                assert all(
                    all(choice.block_square == choices[0].block_square for choice in choices)
                    for choices in product_classes
                )
                count = math.prod(len(choices) for choices in product_classes)
                if square <= square_limit:
                    gram_histogram[square] += count
                    class_products.append(product_classes)
            class_products = tuple(class_products)
        gram_count = sum(gram_histogram.values())
        if gram_count:
            gram_q[q_value] += weight * gram_count
        add_weighted(gram_squares, gram_histogram, weight)

        pair_histogram = Counter()
        forced_histogram = Counter()
        forced_masks = []
        for product_classes in class_products:
            bp_compile_search = PairSearch(
                geometry, oriented, state["internal_mask"], build_bp=True
            )
            bp_compiler = ForcedBPCSP(
                bp_compile_search, product_classes, prefilter_pair=False
            )
            bp_products, bp_stats = bp_compiler.signature_class_products()
            bp_signature_nodes += bp_stats["nodes"]
            bp_signature_products += len(bp_products)
            product_raw_count = math.prod(len(choices) for choices in product_classes)
            product_bp_count = sum(
                math.prod(len(choices) for choices in bp_product)
                for bp_product in bp_products
            )
            bp_is_universal = product_bp_count == product_raw_count
            pair_search = PairSearch(
                geometry, oriented, state["internal_mask"], build_bp=False
            )
            product_pair_histogram, reusable_masks = pair_search.search(
                product_classes,
                square_limit,
                False,
                collect_masks=bp_is_universal,
            )
            pair_nodes += pair_search.nodes
            pair_histogram.update(product_pair_histogram)
            if bp_is_universal:
                product_forced_histogram = product_pair_histogram
                product_forced_masks = reusable_masks
            else:
                product_forced_histogram = Counter()
                product_forced_masks = []
                for bp_product in bp_products:
                    forced_search = PairSearch(
                        geometry,
                        oriented,
                        state["internal_mask"],
                        build_bp=False,
                    )
                    bp_pair_histogram, bp_pair_masks = forced_search.search(
                        bp_product,
                        square_limit,
                        False,
                        collect_masks=True,
                    )
                    forced_nodes += forced_search.nodes
                    product_forced_histogram.update(bp_pair_histogram)
                    product_forced_masks.extend(bp_pair_masks)
            forced_histogram.update(product_forced_histogram)
            forced_masks.extend(product_forced_masks)
        assert len(set(forced_masks)) == len(forced_masks)
        pair_count = sum(pair_histogram.values())
        if pair_count:
            pair_q[q_value] += weight * pair_count
        add_weighted(pair_squares, pair_histogram, weight)
        forced_count = sum(forced_histogram.values())
        assert forced_count == len(forced_masks)
        if forced_count:
            forced_q[q_value] += weight * forced_count
        add_weighted(forced_squares, forced_histogram, weight)
        if forced_masks and direct_control == 0:
            graph = geometry.labelled_edges(forced_masks[0])
            assert generic.forced_c4_support_bp_fast(
                geometry.supports,
                oriented,
                graph,
                generic.build_forced_c4_profiles(geometry.supports),
            )
            from scratch_general_e78_local_ports_all import forced_c4_support_bp_feasible

            assert forced_c4_support_bp_feasible(geometry.supports, oriented, graph)
            direct_control = 1
        state_results.append({**state, "forced_masks": forced_masks})

    assert sum(state_q.values()) == source["locally_port_feasible_assignments"]
    assert sum(completion_q.values()) == expected_completions
    representatives = graph_orbits_from_state_representatives(
        geometry, state_results, global_mask_canonical
    )
    assert sum(row["orbit_size"] for row in representatives) == sum(forced_q.values())

    result = {
        "partition": source["partition"],
        "compression_orbit_index": source["compression_orbit_index"],
        "support_orbit_size": source["support_orbit_size"],
        "weighted_stabilizer_order": geometry.full_stabilizer,
        "used_root_groups": geometry.used_groups,
        "exceptional_supports": source["exceptional_supports"],
        "input_port_feasible_state_assignments": source["locally_port_feasible_assignments"],
        "port_feasible_state_assignments": sum(state_q.values()),
        "Q_condition": None,
        "state_Q_histogram": {str(k): v for k, v in sorted(state_q.items())},
        "exact_overlap_completions": sum(completion_q.values()),
        "completion_Q_histogram": {str(k): v for k, v in sorted(completion_q.items())},
        "actual_overlap_square_histogram": {str(k): v for k, v in sorted(actual_squares.items())},
        "after_exact_real_spectral_bound": sum(spectral_q.values()),
        "spectral_Q_histogram": {str(k): v for k, v in sorted(spectral_q.items())},
        "spectral_overlap_square_histogram": {str(k): v for k, v in sorted(spectral_squares.items())},
        "after_induced_pair_upper": sum(pair_q.values()),
        "pair_Q_histogram": {str(k): v for k, v in sorted(pair_q.items())},
        "pair_overlap_square_histogram": {str(k): v for k, v in sorted(pair_squares.items())},
        "after_forced_C4_support_BP": sum(forced_q.values()),
        "forced_BP_Q_histogram": {str(k): v for k, v in sorted(forced_q.items())},
        "forced_BP_overlap_square_histogram": {str(k): v for k, v in sorted(forced_squares.items())},
        "old_forced_BP_direct_controls": direct_control,
        "distinct_local_symmetry_actions": len(geometry.actions) if representatives else None,
        "local_graph_orbits": len(representatives),
        "orbit_size_histogram": {
            str(k): v
            for k, v in sorted(Counter(row["orbit_size"] for row in representatives).items())
        },
        "local_graph_representatives": representatives,
        "fast_engine_audit": {
            "fibre_state_orbits": len(orbits),
            "fibre_state_orbit_sizes": dict(sorted(Counter(item["weight"] for item in orbits).items())),
            "pair_search_nodes": pair_nodes,
            "forced_BP_search_nodes": forced_nodes,
            "local_Gram_filter": local_gram_filter,
            "Gram_signature_search_nodes": gram_signature_nodes,
            "Gram_feasible_signature_products": gram_signature_products,
            "BP_signature_search_nodes": bp_signature_nodes,
            "BP_feasible_signature_products": bp_signature_products,
            "square_limit": square_limit,
            "representative_convention": (
                "global-minimum-mask"
                if global_mask_canonical
                else "minimum-internal-state then minimum-state-stabilizer-mask"
            ),
        },
    }
    if local_gram_filter:
        result.update(
            {
                "after_exact_overlap_Gram_filter": sum(gram_q.values()),
                "Gram_Q_histogram": {str(k): v for k, v in sorted(gram_q.items())},
                "Gram_overlap_square_histogram": {
                    str(k): v for k, v in sorted(gram_squares.items())
                },
            }
        )
    return result


def summarize(rows):
    histogram_names = (
        "state_Q_histogram",
        "completion_Q_histogram",
        "spectral_Q_histogram",
        "pair_Q_histogram",
        "forced_BP_Q_histogram",
    )
    q_histograms = {name: Counter() for name in histogram_names}
    for row in rows:
        for name in histogram_names:
            q_histograms[name].update({int(k): v for k, v in row[name].items()})
    result = {
        "support_rows": len(rows),
        "port_feasible_state_assignments": sum(row["port_feasible_state_assignments"] for row in rows),
        "exact_overlap_completions": sum(row["exact_overlap_completions"] for row in rows),
        "after_exact_real_spectral_bound": sum(row["after_exact_real_spectral_bound"] for row in rows),
        "after_induced_pair_upper": sum(row["after_induced_pair_upper"] for row in rows),
        "after_forced_C4_support_BP": sum(row["after_forced_C4_support_BP"] for row in rows),
        "nonempty_support_rows": sum(row["after_forced_C4_support_BP"] > 0 for row in rows),
        "local_graph_orbits": sum(row["local_graph_orbits"] for row in rows),
        **{
            name: {str(k): v for k, v in sorted(histogram.items())}
            for name, histogram in q_histograms.items()
        },
    }
    if rows and all("after_exact_overlap_Gram_filter" in row for row in rows):
        gram_q = Counter()
        for row in rows:
            gram_q.update({int(k): v for k, v in row["Gram_Q_histogram"].items()})
        result.update(
            {
                "after_exact_overlap_Gram_filter": sum(
                    row["after_exact_overlap_Gram_filter"] for row in rows
                ),
                "Gram_Q_histogram": {
                    str(k): v for k, v in sorted(gram_q.items())
                },
            }
        )
    return result


def run_partition(
    preset: Preset,
    partition_index: int,
    force=False,
    compression_orbit_index: int | None = None,
):
    _port, grouped = input_rows(preset)
    rows_in = grouped.get(partition_index, [])
    if compression_orbit_index is not None:
        rows_in = [
            pair
            for pair in rows_in
            if pair[0]["compression_orbit_index"] == compression_orbit_index
        ]
        if len(rows_in) != 1:
            raise RuntimeError(
                f"expected one row for partition {partition_index}, "
                f"orbit {compression_orbit_index}; found {len(rows_in)}"
            )
        path = Path(
            f"{preset.part_prefix}{partition_index:02d}_orbit_"
            f"{compression_orbit_index:03d}.json"
        )
    else:
        path = part_path(preset, partition_index)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["status"] == "COMPLETE":
            print(json.dumps({"phase": "resume", "partition_index": partition_index, "status": "COMPLETE"}), flush=True)
            return result
        completed = {row["compression_orbit_index"] for row in result["rows"]}
    else:
        result = {
            "status": "EXPANDING",
            "model": f"symmetry-reduced exact E0={preset.model_e0} local overlap expansion",
            "partition_index": partition_index,
            "partition": rows_in[0][0]["partition"] if rows_in else None,
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, (source, count_row) in enumerate(rows_in):
        if source["compression_orbit_index"] in completed:
            continue
        record = audit_row(
            source,
            count_row["exact_overlap_completions"],
            preset.global_mask_canonical,
            preset.local_gram_filter,
        )
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(
            json.dumps(
                {
                    "partition_index": partition_index,
                    "offset": offset,
                    "compression_orbit_index": record["compression_orbit_index"],
                    "state_orbits": record["fast_engine_audit"]["fibre_state_orbits"],
                    "completions": record["exact_overlap_completions"],
                    "spectral": record["after_exact_real_spectral_bound"],
                    "pair": record["after_induced_pair_upper"],
                    "BP": record["after_forced_C4_support_BP"],
                    "orbits": record["local_graph_orbits"],
                }
            ),
            flush=True,
        )
    assert len(result["rows"]) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge(preset: Preset):
    _port, grouped = input_rows(preset)
    parts = []
    for partition_index in sorted(grouped):
        path = part_path(preset, partition_index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": f"symmetry-reduced solver-free exact E0={preset.model_e0} local expansion",
        "inputs": [str(preset.port_path), str(preset.count_path)],
        "coverage": (
            f"all exact overlap completions of all {preset.expected_state_assignments} "
            f"port-feasible labelled fibre states on all {preset.expected_support_rows} support rows"
        ),
        "method": (
            "exact weighted-state orbits; exact group-square convolution; monotone "
            "incremental induced-pair pruning; exact forced-C4 BP down-closure pruning"
        ),
        "support_filter": (
            None if preset.support_filter_path is None else str(preset.support_filter_path)
        ),
        "representative_convention": (
            "global-minimum-mask"
            if preset.global_mask_canonical
            else "minimum-internal-state then minimum-state-stabilizer-mask"
        ),
        "Q_condition": None,
        "summary": summarize(rows),
        "by_partition": [
            {
                "partition_index": part["partition_index"],
                "partition": part["partition"],
                **part["summary"],
                "artifact": str(part_path(preset, part["partition_index"])),
            }
            for part in parts
        ],
        "rows": rows,
    }
    assert result["summary"]["support_rows"] == preset.expected_support_rows
    assert result["summary"]["port_feasible_state_assignments"] == preset.expected_state_assignments
    assert result["summary"]["exact_overlap_completions"] == preset.expected_completions
    atomic_json(preset.output_path, result)
    rep_result = {
        "status": "COMPLETE",
        "model": f"canonical explicit E0={preset.model_e0} local graph representatives",
        "input": str(preset.output_path),
        "vertex_label": "a low vertex is [2*g_a+bit_a,2*g_b+bit_b] on support {g_a,g_b}",
        "raw_graphs": result["summary"]["after_forced_C4_support_BP"],
        "local_graph_orbits": result["summary"]["local_graph_orbits"],
        "support_rows": [
            {
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "exceptional_supports": row["exceptional_supports"],
                "weighted_stabilizer_order": row["weighted_stabilizer_order"],
                "used_root_groups": row["used_root_groups"],
                "symmetry_actions": row["distinct_local_symmetry_actions"],
                "raw_survivors": row["after_forced_C4_support_BP"],
                "orbit_count": row["local_graph_orbits"],
                "orbit_size_histogram": row["orbit_size_histogram"],
                "representatives": row["local_graph_representatives"],
            }
            for row in rows
            if row["after_forced_C4_support_BP"]
        ],
    }
    assert sum(row["raw_survivors"] for row in rep_result["support_rows"]) == rep_result["raw_graphs"]
    assert sum(row["orbit_count"] for row in rep_result["support_rows"]) == rep_result["local_graph_orbits"]
    atomic_json(preset.rep_path, rep_result)
    print(json.dumps({"status": result["status"], **result["summary"]}), flush=True)
    return result


def compare_reference(preset: Preset) -> None:
    if preset.reference_path is None:
        raise RuntimeError(f"preset {preset.name} has no completed reference")
    fast = json.loads(preset.output_path.read_text(encoding="utf-8"))
    reference = json.loads(preset.reference_path.read_text(encoding="utf-8"))
    fast_rows = {row_key(row): row for row in fast["rows"]}
    reference_rows = {row_key(row): row for row in reference["rows"]}
    assert fast_rows.keys() == reference_rows.keys()
    ignored = {"fast_engine_audit"}
    mismatches = []
    for key in sorted(fast_rows):
        left = {k: v for k, v in fast_rows[key].items() if k not in ignored}
        right = {k: v for k, v in reference_rows[key].items() if k not in ignored}
        if left != right:
            differing = sorted(set(left) | set(right))
            differing = [name for name in differing if left.get(name) != right.get(name)]
            mismatches.append({"row": [list(key[0]), key[1]], "fields": differing})
    summary_equal = fast["summary"] == reference["summary"]
    result = {
        "status": "MATCH" if not mismatches and summary_equal else "MISMATCH",
        "preset": preset.name,
        "fast": str(preset.output_path),
        "reference": str(preset.reference_path),
        "rows_compared": len(fast_rows),
        "summary_equal": summary_equal,
        "row_mismatches": mismatches,
    }
    output = preset.output_path.with_name(preset.output_path.stem + "_reference_check.json")
    atomic_json(output, result)
    print(json.dumps(result), flush=True)
    assert result["status"] == "MATCH"


def gram_signature_census(preset: Preset) -> None:
    """Count the exact local-Gram survivors before any vertex-level DFS."""
    if not preset.local_gram_filter:
        raise RuntimeError("Gram census requires a preset with local_gram_filter")
    _port, grouped = input_rows(preset)
    rows_out = []
    totals = Counter()
    q_input = Counter()
    q_gram = Counter()
    for partition_index in sorted(grouped):
        for source, count_row in grouped[partition_index]:
            geometry = RowGeometry(source)
            gram_filter = GramSignatureFilter(geometry)
            cache = {}
            row_input = 0
            row_gram = 0
            row_state_orbits = 0
            row_signature_products = 0
            for state in state_orbits(source, geometry):
                row_state_orbits += 1
                oriented = oriented_assignment(geometry, state["state_indices"])
                by_group = matching_choices(
                    geometry, oriented, state["state_indices"], cache
                )
                raw = math.prod(len(choices) for choices in by_group)
                classes, _stats = gram_filter.feasible_classes(by_group)
                gram = sum(
                    math.prod(len(choices) for choices in product_classes)
                    for product_classes in classes
                )
                weight = state["weight"]
                q_value = state["Q"]
                row_input += weight * raw
                row_gram += weight * gram
                row_signature_products += len(classes)
                q_input[q_value] += weight * raw
                if gram:
                    q_gram[q_value] += weight * gram
            assert row_input == count_row["exact_overlap_completions"]
            rows_out.append(
                {
                    "partition_index": partition_index,
                    "partition": source["partition"],
                    "compression_orbit_index": source["compression_orbit_index"],
                    "source_row_index": source["source_row_index"],
                    "port_feasible_states": source["locally_port_feasible_assignments"],
                    "state_orbits": row_state_orbits,
                    "input_overlap_completions": row_input,
                    "after_exact_overlap_Gram_filter": row_gram,
                    "feasible_signature_products_on_state_representatives": row_signature_products,
                }
            )
            totals["support_rows"] += 1
            totals["state_orbits"] += row_state_orbits
            totals["input_overlap_completions"] += row_input
            totals["after_exact_overlap_Gram_filter"] += row_gram
            totals["nonempty_support_rows"] += int(row_gram > 0)
            totals["feasible_signature_products_on_state_representatives"] += row_signature_products
            print(
                json.dumps(
                    {
                        "partition_index": partition_index,
                        "compression_orbit_index": source["compression_orbit_index"],
                        "input": row_input,
                        "Gram": row_gram,
                    }
                ),
                flush=True,
            )
    assert totals["support_rows"] == preset.expected_support_rows
    assert totals["input_overlap_completions"] == preset.expected_completions
    result = {
        "status": "COMPLETE",
        "model": "exact overlap-block Gram signature census before vertex-level DFS",
        "inputs": [
            str(preset.port_path),
            str(preset.count_path),
            str(preset.support_filter_path),
        ],
        "method": (
            "group choices are partitioned by exact fibre-pair block totals; "
            "the diagonal and selected overlap equations for Z=W H W^T are "
            "solved over Fraction at every prefix, with only inconsistent or "
            "uniquely non-PSD systems rejected"
        ),
        "summary": {
            **dict(totals),
            "input_Q_histogram": {str(k): v for k, v in sorted(q_input.items())},
            "Gram_Q_histogram": {str(k): v for k, v in sorted(q_gram.items())},
        },
        "rows": rows_out,
    }
    output = preset.output_path.with_name(
        preset.output_path.stem + "_signature_census.json"
    )
    atomic_json(output, result)
    print(json.dumps({"status": "COMPLETE", **result["summary"]}), flush=True)


def overlap_block_key(geometry: RowGeometry, mask: int):
    pairs = tuple(
        (left, right)
        for left, right in itertools.combinations(range(len(geometry.supports)), 2)
        if set(geometry.supports[left]) & set(geometry.supports[right])
    )
    counts = Counter()
    work = mask
    while work:
        low = work & -work
        left, right = geometry.pair_positions[low.bit_length() - 1]
        left_fibre = geometry.fibre_index[left]
        right_fibre = geometry.fibre_index[right]
        if left_fibre != right_fibre:
            pair = tuple(sorted((left_fibre, right_fibre)))
            if pair in pairs:
                counts[pair] += 1
        work ^= low
    return pairs, tuple(counts[pair] for pair in pairs)


def gram_macro_catalog(preset: Preset) -> None:
    """Materialize the small complete set of Gram-feasible macro branches."""
    if not preset.local_gram_filter:
        raise RuntimeError("macro catalog requires a preset with local_gram_filter")
    if preset.name not in GRAM_MACRO_EXPECTATIONS:
        raise RuntimeError(f"no audited macro expectation for preset {preset.name}")
    _port, grouped = input_rows(preset)
    census_path = preset.output_path.with_name(
        preset.output_path.stem + "_signature_census.json"
    )
    census = json.loads(census_path.read_text(encoding="utf-8"))
    assert census["status"] == "COMPLETE"
    assert census["inputs"] == [
        str(preset.port_path),
        str(preset.count_path),
        str(preset.support_filter_path),
    ]
    census_summary = census["summary"]
    expected = GRAM_MACRO_EXPECTATIONS[preset.name]
    input_completion_total = sum(
        count_row["exact_overlap_completions"]
        for rows in grouped.values()
        for _source, count_row in rows
    )
    assert input_completion_total == preset.expected_completions
    assert census_summary["support_rows"] == preset.expected_support_rows
    assert census_summary["input_overlap_completions"] == input_completion_total
    assert census_summary["state_orbits"] == expected["state_orbits"]
    assert census_summary["nonempty_support_rows"] == expected["nonempty_support_rows"]
    assert (
        census_summary["feasible_signature_products_on_state_representatives"]
        == expected["entries"]
    )
    assert (
        census_summary["after_exact_overlap_Gram_filter"]
        == expected["labelled_coverage"]
    )
    catalog = []
    state_orbit_count = 0
    for partition_index in sorted(grouped):
        for source, _count_row in grouped[partition_index]:
            geometry = RowGeometry(source)
            gram_filter = GramSignatureFilter(geometry)
            matching_cache = {}
            for state_number, state in enumerate(state_orbits(source, geometry)):
                state_orbit_count += 1
                oriented = oriented_assignment(geometry, state["state_indices"])
                by_group = matching_choices(
                    geometry, oriented, state["state_indices"], matching_cache
                )
                class_products, _stats = gram_filter.feasible_classes(by_group)
                state_entries = []
                for product_classes in class_products:
                    overlap_mask = 0
                    group_rows = []
                    for group, choices in enumerate(product_classes):
                        signature = gram_filter.signature(group, choices[0])
                        assert all(
                            gram_filter.signature(group, choice) == signature
                            for choice in choices
                        )
                        overlap_mask |= choices[0].mask
                        group_rows.append(
                            {
                                "group": group,
                                "fibre_pairs": [
                                    list(pair)
                                    for pair, _coefficient in gram_filter.pairs_by_group[group]
                                ],
                                "block_counts": list(signature),
                                "matching_choice_count": len(choices),
                            }
                        )
                    full_mask = state["internal_mask"] | overlap_mask
                    pairs, d_key = overlap_block_key(geometry, overlap_mask)
                    product_weight = math.prod(len(choices) for choices in product_classes)
                    entry = {
                        "partition_index": partition_index,
                        "partition": source["partition"],
                        "compression_orbit_index": source["compression_orbit_index"],
                        "source_row_index": source["source_row_index"],
                        "support_orbit_size": source["support_orbit_size"],
                        "exceptional_supports": source["exceptional_supports"],
                        "state_orbit_number": state_number,
                        "state_indices": list(state["state_indices"]),
                        "Q": state["Q"],
                        "internal_mask_hex": hex(state["internal_mask"]),
                        "internal_edges": geometry.edges_of(state["internal_mask"]),
                        "full_weighted_action_order": len(geometry.actions),
                        "state_orbit_size": state["weight"],
                        "state_stabilizer_order": len(state["stabilizer"]),
                        "orbit_stabilizer_identity_verified": (
                            len(geometry.actions)
                            == state["weight"] * len(state["stabilizer"])
                        ),
                        "group_signature_classes": group_rows,
                        "overlap_block_totals": [
                            [left, right, count]
                            for (left, right), count in zip(pairs, d_key)
                        ],
                        "overlap_square": sum(value * value for value in d_key),
                        "matching_completion_weight_per_state": product_weight,
                        "labelled_state_matching_coverage": (
                            state["weight"] * product_weight
                        ),
                        "_d_key": d_key,
                        "_example_full_mask": full_mask,
                        "_state_stabilizer": state["stabilizer"],
                    }
                    state_entries.append(entry)

                # Verify closure of every block-total macro under the exact
                # stabilizer of this canonical internal state.
                by_d = {entry["_d_key"]: entry for entry in state_entries}
                assert len(by_d) == len(state_entries)
                remaining = set(by_d)
                macro_orbit_number = 0
                while remaining:
                    seed_key = min(remaining)
                    seed = by_d[seed_key]
                    image_keys = set()
                    for action_index in seed["_state_stabilizer"]:
                        image_mask = geometry.transform_local_graph(
                            seed["_example_full_mask"],
                            state["internal_mask"],
                            action_index,
                        )
                        image_overlap = image_mask ^ state["internal_mask"]
                        image_pairs, image_key = overlap_block_key(
                            geometry, image_overlap
                        )
                        assert image_pairs == tuple(
                            (row[0], row[1])
                            for row in seed["overlap_block_totals"]
                        )
                        assert image_key in by_d, "Gram macro set is not stabilizer closed"
                        assert (
                            by_d[image_key]["matching_completion_weight_per_state"]
                            == seed["matching_completion_weight_per_state"]
                        )
                        image_keys.add(image_key)
                    coverage = sum(
                        by_d[key]["labelled_state_matching_coverage"]
                        for key in image_keys
                    )
                    for key in image_keys:
                        by_d[key].update(
                            {
                                "signature_stabilizer_orbit_number": macro_orbit_number,
                                "signature_stabilizer_orbit_size": len(image_keys),
                                "signature_stabilizer_canonical_D": list(seed_key),
                                "signature_orbit_labelled_coverage": coverage,
                                "signature_stabilizer_canonical": key == seed_key,
                            }
                        )
                    remaining.difference_update(image_keys)
                    macro_orbit_number += 1
                for entry in sorted(state_entries, key=lambda item: item["_d_key"]):
                    for private in ("_d_key", "_example_full_mask", "_state_stabilizer"):
                        del entry[private]
                    catalog.append(entry)

    total_coverage = sum(entry["labelled_state_matching_coverage"] for entry in catalog)
    q_histogram = Counter()
    for entry in catalog:
        q_histogram[entry["Q"]] += entry["labelled_state_matching_coverage"]
    canonical_entries = [
        entry for entry in catalog if entry["signature_stabilizer_canonical"]
    ]
    entry_keys = {
        (
            entry["partition_index"],
            entry["compression_orbit_index"],
            entry["source_row_index"],
            entry["state_orbit_number"],
            tuple(tuple(row) for row in entry["overlap_block_totals"]),
        )
        for entry in catalog
    }
    assert len(entry_keys) == len(catalog)
    assert total_coverage == expected["labelled_coverage"]
    assert len(catalog) == expected["entries"]
    assert state_orbit_count == expected["state_orbits"]
    assert q_histogram == Counter(
        {int(key): value for key, value in census_summary["Gram_Q_histogram"].items()}
    )
    assert sum(
        entry["signature_stabilizer_orbit_size"]
        for entry in canonical_entries
    ) == len(catalog)
    assert sum(
        entry["signature_orbit_labelled_coverage"]
        for entry in canonical_entries
    ) == total_coverage
    canonical_q_histogram = Counter()
    for entry in canonical_entries:
        canonical_q_histogram[entry["Q"]] += entry[
            "signature_orbit_labelled_coverage"
        ]
    assert canonical_q_histogram == q_histogram
    result = {
        "status": "COMPLETE",
        "model": (
            f"complete E0={preset.model_e0} support+overlap-Gram "
            "macro-branch catalog"
        ),
        "inputs": [
            str(preset.port_path),
            str(preset.count_path),
            str(preset.support_filter_path),
        ],
        # Preserve the established E72 artifact schema/hash chain.  The new
        # census provenance is materialized only on the new E71 artifact;
        # both presets still execute all assertions above.
        **({
            "signature_census_audit": {
                "path": str(census_path),
                "sha256": sha256(census_path),
                "input_overlap_completions": input_completion_total,
                "after_exact_overlap_Gram_filter": census_summary[
                    "after_exact_overlap_Gram_filter"
                ],
                "feasible_signature_products_on_state_representatives": (
                    census_summary[
                        "feasible_signature_products_on_state_representatives"
                    ]
                ),
                "Q_histogram": census_summary["Gram_Q_histogram"],
            },
        } if preset.name == "e71gram" else {}),
        "coverage_note": (
            "support_orbit_size is recorded but not multiplied into local labelled "
            "coverage, matching the rooted support-orbit convention; each feasible "
            "fibre-state orbit and block-total signature product is represented"
        ),
        "summary": {
            "support_rows_before_overlap_Gram": preset.expected_support_rows,
            "state_orbits_before_overlap_Gram": state_orbit_count,
            "Gram_feasible_macro_entries": len(catalog),
            "macro_entries_mod_state_stabilizers": len(canonical_entries),
            "labelled_state_matching_coverage": total_coverage,
            "Q_histogram": {str(k): v for k, v in sorted(q_histogram.items())},
            "all_orbit_stabilizer_identities_verified": all(
                entry["orbit_stabilizer_identity_verified"] for entry in catalog
            ),
            "all_signature_stabilizer_orbits_closed": True,
            **({
                "all_macro_entry_keys_distinct": True,
                "canonical_orbits_partition_all_macro_entries": True,
                "canonical_orbit_coverage_equals_labelled_coverage": True,
                "macro_totals_match_independent_signature_census": True,
                "input_completion_total_verified": input_completion_total,
            } if preset.name == "e71gram" else {}),
        },
        "macro_entries": catalog,
    }
    output = preset.output_path.with_name(
        preset.output_path.stem + "_macro_catalog.json"
    )
    atomic_json(output, result)
    print(json.dumps({"status": "COMPLETE", **result["summary"]}), flush=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def merge_frontier_representatives(preset: Preset) -> None:
    """Merge the exact p27/p29/p30/p31 local survivors for SAT branching."""
    if preset.name != "e72gram":
        raise RuntimeError("frontier merge is defined for the e72gram preset")
    paths = [
        Path(f"{preset.part_prefix}27_orbit_{orbit:03d}.json")
        for orbit in (0, 1, 2, 4)
    ] + [part_path(preset, partition) for partition in (29, 30, 31)]
    artifacts = []
    rows = []
    seen = set()
    for path in paths:
        source = json.loads(path.read_text(encoding="utf-8"))
        assert source["status"] == "COMPLETE"
        artifacts.append({"path": str(path), "sha256": sha256(path)})
        for row in source["rows"]:
            key = row_key(row)
            assert key not in seen
            seen.add(key)
            assert sum(
                representative["orbit_size"]
                for representative in row["local_graph_representatives"]
            ) == row["after_forced_C4_support_BP"]
            rep_q = Counter()
            masks = set()
            for representative in row["local_graph_representatives"]:
                rep_q[representative["Q"]] += representative["orbit_size"]
                assert representative["mask_hex"] not in masks
                masks.add(representative["mask_hex"])
            assert {
                str(key): value for key, value in sorted(rep_q.items())
            } == row["forced_BP_Q_histogram"]
            rows.append({**row, "source_artifact": str(path)})
    assert len(rows) == 150
    surviving_rows = [row for row in rows if row["after_forced_C4_support_BP"]]
    q_histogram = Counter()
    for row in surviving_rows:
        q_histogram.update(
            {int(key): value for key, value in row["forced_BP_Q_histogram"].items()}
        )
    raw = sum(row["after_forced_C4_support_BP"] for row in surviving_rows)
    orbit_count = sum(row["local_graph_orbits"] for row in surviving_rows)
    result = {
        "status": "COMPLETE",
        "model": "normalized E0=72 p27/p29/p30/p31 local graph orbit frontier",
        "inputs": artifacts,
        "excluded_small_partitions": [15, 19, 23, 24, 25],
        "coverage": (
            "every support-filter survivor in p27,p29,p30,p31; rows killed by "
            "the overlap-Gram or local filters are retained in the row audit, "
            "while support_rows below contains exactly the nonempty graph orbits"
        ),
        "representative_convention": (
            "minimum internal fibre-state in its full weighted orbit, followed "
            "by minimum graph mask under that state's stabilizer"
        ),
        "summary": {
            "input_support_rows": len(rows),
            "nonempty_support_rows": len(surviving_rows),
            "raw_BP_survivors": raw,
            "local_graph_orbits": orbit_count,
            "Q_histogram": {str(key): value for key, value in sorted(q_histogram.items())},
            "all_row_orbit_mass_identities_verified": True,
            "all_row_Q_mass_identities_verified": True,
            "all_producer_symmetry_closure_assertions_present": all(
                "representative_convention" in row["fast_engine_audit"] for row in rows
            ),
        },
        "row_audit": [
            {
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "source_artifact": row["source_artifact"],
                "after_overlap_Gram": row.get("after_exact_overlap_Gram_filter"),
                "after_pair_upper": row["after_induced_pair_upper"],
                "raw_BP_survivors": row["after_forced_C4_support_BP"],
                "local_graph_orbits": row["local_graph_orbits"],
            }
            for row in rows
        ],
        "support_rows": [
            {
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "support_orbit_size": row["support_orbit_size"],
                "exceptional_supports": row["exceptional_supports"],
                "weighted_stabilizer_order": row["weighted_stabilizer_order"],
                "used_root_groups": row["used_root_groups"],
                "raw_survivors": row["after_forced_C4_support_BP"],
                "Q_histogram": row["forced_BP_Q_histogram"],
                "orbit_count": row["local_graph_orbits"],
                "orbit_size_histogram": row["orbit_size_histogram"],
                "representatives": row["local_graph_representatives"],
                "source_artifact": row["source_artifact"],
            }
            for row in surviving_rows
        ],
    }
    assert sum(row["raw_survivors"] for row in result["support_rows"]) == raw
    assert sum(row["orbit_count"] for row in result["support_rows"]) == orbit_count
    output = Path("scratch_general_e72_q3_gram_frontier_local_graph_reps.json")
    atomic_json(output, result)
    print(json.dumps({"status": "COMPLETE", **result["summary"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=sorted(PRESETS), default="e72")
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--compression-orbit-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--compare-reference", action="store_true")
    parser.add_argument("--gram-census", action="store_true")
    parser.add_argument("--macro-catalog", action="store_true")
    parser.add_argument("--merge-frontier-reps", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = sum(
        (
            args.partition_index is not None,
            args.partition_indices is not None,
            args.all,
            args.merge,
            args.compare_reference,
            args.gram_census,
            args.macro_catalog,
            args.merge_frontier_reps,
        )
    )
    if selected != 1:
        parser.error("choose exactly one mode")
    if args.compression_orbit_index is not None and args.partition_index is None:
        parser.error("--compression-orbit-index requires --partition-index")
    preset = PRESETS[args.preset]
    configure_generic(preset)
    if args.partition_index is not None:
        run_partition(
            preset,
            args.partition_index,
            args.force,
            args.compression_orbit_index,
        )
    elif args.partition_indices is not None:
        for index in (int(value) for value in args.partition_indices.split(",")):
            run_partition(preset, index, args.force)
    elif args.all:
        _port, grouped = input_rows(preset)
        for index in sorted(grouped):
            run_partition(preset, index, args.force)
    elif args.merge:
        merge(preset)
    elif args.compare_reference:
        compare_reference(preset)
    elif args.gram_census:
        gram_signature_census(preset)
    elif args.macro_catalog:
        gram_macro_catalog(preset)
    else:
        merge_frontier_representatives(preset)


if __name__ == "__main__":
    main()
