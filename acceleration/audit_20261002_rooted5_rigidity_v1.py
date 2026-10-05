"""Source-free complete rooted5 basis/marked-row/rational-rigidity audit v1."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'acceleration/results/20261002_rooted5_flag_rigidity'
BIND = ROOT / 'acceleration/results/20261002_rooted5_moment_identity_binding'
ENDPOINT = ROOT / 'acceleration/results/20261002_order8_exact_endpoint'
ARCHIVE = ROOT / 'external_conway99_research/attempts/wave147-alternative-lane/exact-results.json'
MODEL_PINS = {'ordered_edge': '4b8cf1c43602408d0c09512b565fb8a8ee5a171c134dafabad7355ddebe29f1f', 'ordered_nonedge': 'd4f6cd2da1bab52c0cb0f75a7ebb02e252a46fae936cdfe4c80f6de8942ba0b1'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def save(p, data):
    with p.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


@lru_cache(None)
def pairs(n):
    return tuple(combinations(range(n), 2))


@lru_cache(None)
def matrix(n, mask):
    value = [[0] * n for _ in range(n)]
    for bit, (a, b) in enumerate(pairs(n)):
        value[a][b] = value[b][a] = (mask >> bit) & 1
    return tuple(tuple(row) for row in value)


def bits(mat, labels):
    value = 0
    for bit, (a, b) in enumerate(pairs(len(labels))):
        value |= mat[labels[a]][labels[b]] << bit
    return value


@lru_cache(None)
def orbit(n, mask):
    mat = matrix(n, mask)
    return frozenset(bits(mat, (0, 1, *tail)) for tail in permutations(range(2, n)))


def caps(mat):
    return all(sum(mat[a][x] * mat[b][x] for x in range(len(mat))) <= 2 - mat[a][b] for a, b in pairs(len(mat)))


def bases(adjacent):
    result = {}
    exhaustions = []
    for n in range(2, 6):
        unprocessed = {mask for mask in range(1 << len(pairs(n))) if (mask & 1) == adjacent and caps(matrix(n, mask))}
        labelled = len(unprocessed)
        representatives = []
        while unprocessed:
            member = min(unprocessed)
            image = orbit(n, member)
            need(image <= unprocessed, 'complete admissible orbit remains intact')
            representatives.append(min(image))
            unprocessed.difference_update(image)
        result[n] = representatives
        exhaustions.append({'order': n, 'simple_masks_enumerated': 1 << len(pairs(n)), 'admissible_labelled_masks_of_root_relation': labelled, 'rooted_classes': len(representatives)})
    return result, exhaustions


def mark_orbits(n, mask):
    """Independent DSU action on all marked vertices/pairs, no producer canon map."""
    mat = matrix(n, mask)
    marks = [(i,) for i in range(n)] + list(pairs(n))
    parent = {mark: mark for mark in marks}
    def find(mark):
        while parent[mark] != mark:
            parent[mark] = parent[parent[mark]]
            mark = parent[mark]
        return mark
    for tail in permutations(range(2, n)):
        mapping = (0, 1, *tail)
        if bits(mat, mapping) != mask:
            continue
        for mark in marks:
            target = tuple(sorted(mapping[i] for i in mark))
            parent[find(target)] = find(mark)
    groups = {}
    for mark in marks:
        groups.setdefault(find(mark), []).append(mark)
    return sorted((sorted(group) for group in groups.values()), key=lambda group: (len(group[0]), group[0]))


def signature(row):
    mark = None if row['mark'] is None else tuple(tuple(x) for x in row['mark'])
    return row['kind'], row['order'], row['mask'], mark


def reconstruct(n, degree, adjacent):
    base, inventory = bases(adjacent)
    variables = [(order, mask) for order in range(2, 6) for mask in base[order]]
    index = {var: i for i, var in enumerate(variables)}
    rows = []
    for order in range(2, 6):
        rows.append({'kind': 'total', 'order': order, 'mask': None, 'mark': None, 'terms': [[index[order, mask], 1] for mask in base[order]], 'rhs': math.comb(n - 2, order - 2)})
    for order in range(2, 5):
        for mask in base[order]:
            mat = matrix(order, mask)
            descriptors = [('deletion', None, n - order)]
            for marked in mark_orbits(order, mask):
                if len(marked[0]) == 1:
                    descriptors.append(('degree', marked, sum(degree - sum(mat[a]) for (a,) in marked)))
                else:
                    descriptors.append(('common_neighbor', marked, sum(2 - mat[a][b] - sum(mat[a][x] * mat[b][x] for x in range(order)) for a, b in marked)))
            coefficients = [Counter({index[order, mask]: -constant}) if constant else Counter() for _, _, constant in descriptors]
            for bigmask in base[order + 1]:
                big = matrix(order + 1, bigmask)
                for deleted in range(2, order + 1):
                    remaining = [v for v in range(2, order + 1) if v != deleted]
                    # Enumerate every isomorphism to the fixed small flag;
                    # roots stay pointwise fixed. This does not use a canonical
                    # producer transport and independently checks orbit invariance.
                    maps = [(0, 1, *tail) for tail in permutations(remaining) if bits(big, (0, 1, *tail)) == mask]
                    if not maps:
                        continue
                    for at, (kind, marked, _) in enumerate(descriptors):
                        values = []
                        for mapping in maps:
                            values.append(1 if kind == 'deletion' else sum(all(big[deleted][mapping[v]] for v in mark) for mark in marked))
                        need(len(set(values)) == 1, 'marked coefficient independent of choice of isomorphism')
                        if values[0]:
                            coefficients[at][index[order + 1, bigmask]] += values[0]
            for (kind, marked, _), coeff in zip(descriptors, coefficients):
                rows.append({'kind': kind, 'order': order, 'mask': mask, 'mark': None if marked is None else [list(mark) for mark in marked], 'terms': [[col, coefficient] for col, coefficient in sorted(coeff.items()) if coefficient], 'rhs': 0})
    return variables, rows, inventory


def verify_model(raw, variables, rows):
    need(raw['n'] == 99 and raw['k'] == 14 and raw['lambda_'] == 1 and raw['mu'] == 2, 'precise target parameters')
    need(raw['variables'] == [list(v) for v in variables], 'entire independent variable basis')
    actual = {signature(row): row for row in raw['equations']}
    expected = {signature(row): row for row in rows}
    need(len(actual) == len(raw['equations']) and len(expected) == len(rows), 'unique row descriptions')
    need(actual == expected, 'complete independent marked integer row reconstruction')


def dense(rows, count):
    result = []
    for row in rows:
        vector = [0] * count
        for column, coefficient in row['terms']:
            vector[column] = coefficient
        result.append(vector)
    return result


def modular_rank(rows, columns, prime):
    need(all(prime % divisor for divisor in range(2, math.isqrt(prime) + 1)), 'audit modulus is prime')
    work = [[value % prime for value in row] for row in dense(rows, columns)]
    position, pivots = 0, []
    for column in range(columns):
        chosen = next((i for i in range(position, len(work)) if work[i][column]), None)
        if chosen is None:
            continue
        work[position], work[chosen] = work[chosen], work[position]
        inverse = pow(work[position][column], prime - 2, prime)
        work[position] = [(value * inverse) % prime for value in work[position]]
        for i in range(position + 1, len(work)):
            multiple = work[i][column]
            if multiple:
                work[i] = [(left - multiple * right) % prime for left, right in zip(work[i], work[position])]
        pivots.append(column)
        position += 1
    return {'modulus': prime, 'rank': position, 'pivot_columns': pivots, 'exact_rational_implication': 'A full-column-rank integer matrix modulo a prime has a nonzero integer maximal minor, hence full column rank over Q.'}


def equations_hold(values, rows):
    return all(sum(coefficient * values[column] for column, coefficient in row['terms']) == row['rhs'] for row in rows)


def graph_is_srg(mat, degree):
    return all(mat[a][a] == 0 and sum(mat[a]) == degree for a in range(len(mat))) and all(mat[a][b] == mat[b][a] and sum(mat[a][x] * mat[b][x] for x in range(len(mat))) == 2 - mat[a][b] for a, b in pairs(len(mat)))


def count_root(mat, root, variables):
    counts = Counter()
    free = [v for v in range(len(mat)) if v not in root]
    for order in range(2, 6):
        for tail in combinations(free, order - 2):
            mask = bits(mat, (*root, *tail))
            counts[order, min(orbit(order, mask))] += 1
    need(set(counts) <= set(variables), 'all actual fixture flags lie in exhaustive basis')
    return [counts[var] for var in variables]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started, pins, results = time.monotonic(), {}, []
    def pin(p, expected=None):
        with p.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(expected is None or actual == expected, 'artifact hash ' + p.name)
        pins[p.resolve().relative_to(ROOT).as_posix()] = actual
        return actual
    def load(p, expected=None):
        pin(p, expected)
        return json.loads(p.read_bytes())
    try:
        archive = load(ARCHIVE)
        rook = [[int(a != b and (a // 3 == b // 3 or a % 3 == b % 3)) for b in range(9)] for a in range(9)]
        need(graph_is_srg(rook, 4), 'independent exact known-valid rook fixture')
        damaged = copy.deepcopy(rook)
        damaged[0][1] = damaged[1][0] = 0
        need(not graph_is_srg(damaged, 4), 'corrupted rook graph rejected by exact SRG check')
        for family, adjacent, population, multiplier in tqdm([('ordered_edge', 1, 1386, 2), ('ordered_nonedge', 0, 8316, 1)], desc='Independent rooted families'):
            variables, rows, inventory = reconstruct(99, 14, adjacent)
            raw = load(DATA / (family + '_model.json'), MODEL_PINS[family])
            need(raw['adjacent_roots'] == bool(adjacent), 'same fixed root relation')
            verify_model(raw, variables, rows)
            rank = modular_rank(rows, len(variables), 1009)
            need(rank['rank'] == len(variables), 'full rational column rank independently established')
            rref = load(DATA / (family + '_rref.json'))
            values = [Fraction(numerator, denominator) for numerator, denominator in rref['unique_solution']]
            need(len(values) == len(variables) and equations_hold(values, rows), 'explicit exact rational solution satisfies every reconstructed row')
            need(all(value.denominator == 1 and value >= 0 for value in values), 'forced counts are nonnegative exact integers')
            forced = {mask: values[i] for i, (order, mask) in enumerate(variables) if order == 5}
            saved_forced = load(DATA / (family + '_forced5flags.json'))
            need(forced == {mask: Fraction(*count) for mask, count in saved_forced['flag_counts']}, 'all forced five-flag coordinates')
            basis_masks = archive['families'][family]['flag_masks']
            certificate = load(ENDPOINT / (family + '_certificate.json'))
            need(set(basis_masks) == set(forced) and len(basis_masks) == len(forced), 'entire archived coordinate mask population')
            vector = [int(forced[mask]) for mask in basis_masks]
            need(vector == [multiplier * value for value in certificate['terms'][0]['integer_vector']], 'exact endpoint vector coordinate identity')
            need(sum(vector) == math.comb(97, 3) == 147440, 'all unordered free triples total')
            expected_moment = [[population * left * right for right in vector] for left in vector]
            binding = load(BIND / (family + '_universal_moment.json'))
            endpoint_matrix = load(ENDPOINT / (family + '_matrix.json'))
            need(binding['flag_masks'] == basis_masks and binding['forced_per_root_counts'] == vector and binding['ordered_root_count'] == population and binding['matrix'] == expected_moment, 'entire proposed universal moment artifact')
            actual_matrix = [[Fraction(*cell) for cell in row] for row in endpoint_matrix['matrix']]
            need(actual_matrix == expected_moment, 'entire exact endpoint matrix matches universal moment equality')
            control_variables, control_rows, _ = reconstruct(9, 4, adjacent)
            need(control_variables == variables, 'same complete local basis for known-valid control')
            roots = [(a, b) for a in range(9) for b in range(9) if a != b and rook[a][b] == adjacent]
            for root in roots:
                need(equations_hold(count_root(rook, root, variables), control_rows), 'every actual ordered fixture root satisfies every independently reconstructed necessary row')
            changed_count = values[:]
            changed_count[0] += 1
            need(not equations_hold(changed_count, rows), 'deliberately corrupted solution rejected')
            changed_model = copy.deepcopy(raw)
            changed_model['equations'][0]['terms'][0][1] += 1
            try:
                verify_model(changed_model, variables, rows)
            except ValueError:
                pass
            else:
                raise ValueError('corrupted raw coefficient accepted')
            damaged_roots = [(a, b) for a in range(9) for b in range(9) if a != b and damaged[a][b] == adjacent]
            detected = 0
            for root in damaged_roots:
                if not equations_hold(count_root(damaged, root, variables), control_rows):
                    detected += 1
            need(detected > 0, 'non-SRG corrupted graph cannot pass all necessary rows')
            report = {'family': family, 'variable_basis': [list(v) for v in variables], 'basis_inventory': inventory, 'equations': rows, 'exact_modular_rank_certificate': rank, 'exact_unique_solution': [[value.numerator, value.denominator] for value in values], 'flag_masks': basis_masks, 'forced_per_root_counts': vector, 'ordered_root_population': population, 'complete_moment_entries_checked': len(vector) ** 2, 'controls': {'known_valid_rook_ordered_roots_checked': len(roots), 'all_rows_per_root': len(control_rows), 'corrupted_count_rejected': True, 'corrupted_raw_coefficient_rejected': True, 'corrupted_graph_roots_failing_necessary_rows': detected}, 'unrestricted_conditional_scope': 'Every actual ordered root of this relation in every hypothetical srg(99,14,1,2); no target automorphism, N3, prism-free or support assumption.'}
            results.append(report)
            save(out / (family + '_audit.json'), report)
        for p in [Path(__file__), ROOT / 'uv.lock', ROOT / 'pyproject.toml', ROOT / 'docs/DERIVATION_20261002_ROOTED5_MOMENT_RIGIDITY.md']:
            pin(p)
        for p in [DATA / 'manifest.json', DATA / 'summary.json', BIND / 'manifest.json', BIND / 'summary.json']:
            pin(p)
        save(out / 'summary.json', {'status': 'INDEPENDENT_ROOTED5_RIGIDITY_AND_EXPLICIT_MOMENTS_PASS', 'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(), 'verifier': '/root/checkpoint_audit', 'producer': '/root/structural', 'method': 'independent_derivation', 'inputs_sha256': pins, 'families': [{'family': result['family'], 'variables': len(result['variable_basis']), 'rows': len(result['equations']), 'rank_over_Q': result['exact_modular_rank_certificate']['rank'], 'flags_order5': len(result['flag_masks']), 'ordered_root_population': result['ordered_root_population'], 'controls': result['controls']} for result in results], 'statement': 'Every srg(99,14,1,2) has the exact saved constant 66-coordinate ordered-edge and87-coordinate ordered-nonedge five-flag vectors. For M defined as the actual ordered-root second moment, M_edge=1386*c_edge*c_edge^T and M_nonedge=8316*c_nonedge*c_nonedge^T; the saved endpoint matrices match these equalities exactly.', 'target_resolution': False, 'new_exclusions': 0, 'artifact_availability': 'LOCAL_ONLY', 'elapsed_seconds': time.monotonic() - started, 'shared_components': ['Python integer/Fraction, SHA-256, JSON and OS/runtime.', 'Producer artifacts are raw checking inputs only; no producer or archived code is imported.', 'The archived five-flag mask list is fully matched against a newly exhausted independent basis.'], 'limitations': ['Necessary exact constant root statistics and moment equalities do not construct a graph or prove nonexistence.', 'The moment is explicitly defined by actual root extension counts; the full archived order5..8 coefficient-layer derivation is not replayed here.', 'No novelty or complete audit of Pech2021 is claimed; literature context is separate from this finite independent derivation.', 'No sampled or floating-point check is used for the recorded finite bases, rows, ranks, solutions or matrix entries.']})
        print(json.dumps({'status': 'PASS', 'families': len(results), 'elapsed_seconds': time.monotonic() - started}), flush=True)
    except BaseException as error:
        save(out / 'failure.json', {'error': repr(error), 'timestamp': datetime.now(timezone.utc).isoformat(), 'inputs_sha256': pins, 'completed_families': [result['family'] for result in results]})
        raise


if __name__ == '__main__':
    main()
