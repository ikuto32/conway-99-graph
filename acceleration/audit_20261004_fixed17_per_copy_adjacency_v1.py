"""SOURCE ONLY: distinct labelled-copy set, model, receipt and full-graph diagnostic checker."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import stat
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1.py'
SPEC = 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1_spec.md'
PRODUCER = 'acceleration/solve_20261004_fixed17_copy_adjacency_v1.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_fixed17_copy_adjacency_v1_spec.md'
CAL_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_COMPLETE_PASS'
AUTHOR_COUNTS = {'positive':7,'negative':22,'total':29}
OWN_COUNTS = {'positive':20,'negative':54,'total':74}
MODEL_SCHEMA = 'FIXED17_COPY_ADJACENCY_MODEL_V1'
CANDIDATE_SCHEMA = 'FIXED17_COPY_ADJACENCY_INTEGER_CANDIDATE_V1'
TRUSTED_PROFILE = 'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json'
TRUSTED_PROFILE_SHA = '468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'
AUTHOR_SOFTWARE = {
  "acceleration/solve_20261004_fixed17_copy_adjacency_v1.py": "3652307d347f5cf26602613d6b5dc0cb6fca6ea6c13d3812e72cef1cf5dc7900",
  "acceleration/solve_20261004_fixed17_copy_adjacency_v1_spec.md": "bf17482ce4a5622c2dbbbb9a54ad19219443291593d0afb7138c39070228d67a",
  "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
  "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
  "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
  "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
  "build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi": "53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699",
  "build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd": "f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2",
  "build/research-venv/Lib/site-packages/highspy/highs.py": "00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a",
  "build/research-venv/Lib/site-packages/highspy/__init__.py": "01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9",
  "build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA": "cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d"
}
PREMISES = {
  "acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json": "468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e",
  "acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json": "133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5",
  "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json": "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8",
  "acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json": "4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3",
  "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json": "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218",
  "acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json": "910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6",
  "acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json": "3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d",
  "acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json": "d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017",
  "acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json": "39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586",
  "acceleration/results/20261004_target_exterior_type_edge_moments_root_written_acceptance01.json": "0e09566986883576c0f421cb1e47391eaadb49db72183d4e90c3ce55f9356728"
}
SOFTWARE = dict(AUTHOR_SOFTWARE)
SOFTWARE.update({
 'acceleration/audit_20261004_fixed17_aggregate_edge_flow_v2.py':'d9d4a5346cafdcca81dc787debc13ace6f63c9be2817965c6c382d22c6336e34',
 'acceleration/audit_20261004_fixed17_aggregate_edge_flow_v2_spec.md':'deb53cc248d361fdb1f7cfc378d51196e7749e98ed222715600fc960b59d9254'})
# Only Native engineering helpers are copied; producer algorithms are not imported or copied.

class Veto(ValueError):
    pass


def need(condition, stage):
    if not condition:
        raise Veto(stage)


def tick(budget):
    if budget is not None:
        budget.tick()


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def profile_geometry(raw, budget=None):
    required = {'target_order', 'target_degree', 'support_adjacency', 'ordered_masks', 'counts', 'pair_bits'}
    need(type(raw) is dict and raw.keys() == required, 'PROFILE_FIELDS')
    n, k, h, masks, counts, table = (raw[name] for name in (
        'target_order', 'target_degree', 'support_adjacency', 'ordered_masks', 'counts', 'pair_bits'))
    need(type(n) is int and type(k) is int and 0 < k < n - 1, 'PROFILE_TARGET')
    need(type(h) is list and 0 < len(h) < n, 'PROFILE_GRAPH')
    support = len(h)
    need(all(type(row) is list and len(row) == support for row in h), 'PROFILE_GRAPH')
    need(all(type(value) is int and value in (0, 1) for row in h for value in row), 'PROFILE_GRAPH')
    for u in range(support):
        tick(budget)
        need(h[u][u] == 0 and all(h[u][v] == h[v][u] for v in range(support)), 'PROFILE_GRAPH')
    need(type(masks) is list and masks and all(type(mask) is int and 0 <= mask < 2**support for mask in masks)
         and all(a < b for a, b in zip(masks, masks[1:])), 'PROFILE_MASKS')
    need(type(counts) is list and len(counts) == len(masks)
         and all(type(value) is int and value >= 0 for value in counts), 'PROFILE_COUNTS')
    need(sum(counts) == n - support, 'PROFILE_COUNTS')
    q = len(masks)
    need(type(table) is list and len(table) == q*(q+1)//2, 'PROFILE_PAIR_POPULATION')
    pair_bits = {}
    ordinal = 0
    for i in range(q):
        tick(budget)
        for j in range(i, q):
            row = table[ordinal]
            need(type(row) is dict and row.keys() == {'i', 'j', 'bits'}
                 and type(row['i']) is int and type(row['j']) is int
                 and row['i'] == i and row['j'] == j, 'PROFILE_PAIR_ORDER')
            bits = row['bits']
            need(type(bits) is list and all(type(bit) is int and bit in (0, 1) for bit in bits)
                 and bits in ([], [0], [1], [0, 1]), 'PROFILE_PAIR_BITS')
            pair_bits[i, j] = set(bits)
            ordinal += 1
    labels, types = [], []
    for i, multiplicity in enumerate(counts):
        members = {u for u in range(support) if (masks[i] >> u) & 1}
        for copy_number in range(multiplicity):
            labels.append([i, copy_number])
            types.append(set(members))
    return {'n': n, 'k': k, 'h': h, 'support': support, 'labels': labels,
            'types': types, 'pair_bits': pair_bits}


def unordered_rank(x, y, size):
    need(type(x) is int and type(y) is int and 0 <= x < y < size, 'VARIABLE_PAIR_DOMAIN')
    return x*(2*size-x-1)//2 + y-x-1


def abstract_model(raw, budget=None):
    geometry = profile_geometry(raw, budget)
    labels, types = geometry['labels'], geometry['types']
    size, support, k = len(labels), geometry['support'], geometry['k']
    pairs = [None]*(size*(size-1)//2)
    lower, upper = [None]*len(pairs), [None]*len(pairs)
    incident = [set() for _ in labels]
    for x in range(size):
        tick(budget)
        for y in range(x+1, size):
            ordinal = unordered_rank(x, y, size)
            pairs[ordinal] = [x, y]
            i, j = sorted((labels[x][0], labels[y][0]))
            allowed = geometry['pair_bits'][i, j]
            need(allowed, 'PROFILE_INCOMPATIBLE_PAIR')
            lower[ordinal] = 1 if allowed == {1} else 0
            upper[ordinal] = 1 if 1 in allowed else 0
            incident[x].add(ordinal)
            incident[y].add(ordinal)
    rows = []
    for x in range(size):
        tick(budget)
        degree_rhs = k - len(types[x])
        rows.append({'copy': x, 'coordinate': None, 'rhs': degree_rhs,
                     'terms': [[ordinal, 1] for ordinal in sorted(incident[x])]})
        for u in range(support):
            required = 2 - int(u in types[x]) - sum(geometry['h'][u][v] for v in types[x])
            coordinates = []
            for y in range(size):
                if y != x and u in types[y]:
                    a, b = sorted((x, y))
                    coordinates.append(unordered_rank(a, b, size))
            rows.append({'copy': x, 'coordinate': u, 'rhs': required,
                         'terms': [[ordinal, 1] for ordinal in sorted(coordinates)]})
    return geometry, {'labels': labels, 'variable_pairs': pairs, 'lower': lower, 'upper': upper, 'rows': rows}


def matrix_neighbors(matrix, size, budget=None):
    need(type(matrix) is list and len(matrix) == size
         and all(type(row) is list and len(row) == size for row in matrix), 'MATRIX_BINARY')
    for x in range(size):
        tick(budget)
        need(all(type(value) is int and value in (0, 1) for value in matrix[x]), 'MATRIX_BINARY')
    need(all(matrix[x][x] == 0 for x in range(size)), 'MATRIX_DIAGONAL')
    for x in range(size):
        tick(budget)
        need(all(matrix[x][y] == matrix[y][x] for y in range(size)), 'MATRIX_SYMMETRY')
    return [{y for y, value in enumerate(matrix[x]) if value == 1} for x in range(size)]


def check_copy_matrix(raw, labels, matrix, budget=None):
    geometry = profile_geometry(raw, budget)
    size, support, types = len(geometry['labels']), geometry['support'], geometry['types']
    need(typed_equal(labels, geometry['labels']), 'CANDIDATE_COPY_LABELS')
    neighbors = matrix_neighbors(matrix, size, budget)
    pair_rows, equation_rows = [], []
    for x in range(size):
        tick(budget)
        for y in range(x+1, size):
            i, j = sorted((labels[x][0], labels[y][0]))
            allowed = geometry['pair_bits'][i, j]
            need(matrix[x][y] in allowed, 'PAIR_BOUND')
            pair_rows.append({'x': x, 'y': y, 'bit': matrix[x][y], 'allowed_bits': sorted(allowed)})
    # All bounds precede the first equation, matching the documented producer wire.
    for x in range(size):
        tick(budget)
        degree_rhs = geometry['k'] - len(types[x])
        degree_lhs = len(neighbors[x])
        need(degree_lhs == degree_rhs, 'DEGREE_EQUATION')
        equation_rows.append({'copy': x, 'coordinate': None, 'lhs': degree_lhs, 'rhs': degree_rhs})
        for u in range(support):
            lhs = sum(u in types[y] for y in neighbors[x])
            rhs = 2 - int(u in types[x]) - sum(geometry['h'][u][v] for v in types[x])
            need(lhs == rhs, 'INCIDENCE_EQUATION')
            equation_rows.append({'copy': x, 'coordinate': u, 'lhs': lhs, 'rhs': rhs})
    # A new direct whole graph reconstruction, not a producer or old matrix validator.
    graph_neighbors = [set() for _ in range(geometry['n'])]
    for u in range(support):
        graph_neighbors[u].update(v for v, value in enumerate(geometry['h'][u]) if value)
    for x in range(size):
        full_x = support+x
        for u in types[x]:
            graph_neighbors[u].add(full_x)
            graph_neighbors[full_x].add(u)
        graph_neighbors[full_x].update(support+y for y in neighbors[x])
    full_matrix = [[int(v in graph_neighbors[u]) for v in range(geometry['n'])]
                   for u in range(geometry['n'])]
    diagnostic = whole_srg_diagnostic(full_matrix, geometry['k'], budget)
    return {'complete_pair_rows': pair_rows, 'complete_equations': equation_rows,
            'full_adjacency': full_matrix, 'srg_diagnostic': diagnostic,
            'relaxation_exact_checked': True,
            'reconstructed_graph_srg_valid': diagnostic['srg_valid'],
            'target_object_acceptance_requires_separate_receipt': True}


def whole_srg_diagnostic(matrix, degree, budget=None):
    need(type(matrix) is list and matrix and type(degree) is int, 'SRG_MATRIX_SHAPE')
    n = len(matrix)
    need(0 < degree < n-1 and all(type(row) is list and len(row) == n for row in matrix), 'SRG_PARAMETERS')
    need(all(type(value) is int and value in (0, 1) for row in matrix for value in row), 'SRG_BINARY')
    neighbors = []
    for u in range(n):
        tick(budget)
        need(matrix[u][u] == 0 and all(matrix[u][v] == matrix[v][u] for v in range(n)), 'SRG_SYMMETRY')
        neighbors.append({v for v, value in enumerate(matrix[u]) if value})
    degrees = [len(row) for row in neighbors]
    common, first_failure = [], None
    for u, actual in enumerate(degrees):
        if actual != degree and first_failure is None:
            first_failure = {'u': u, 'actual': actual, 'expected': degree, 'stage': 'SRG_DEGREE'}
    for u in range(n):
        tick(budget)
        row = []
        for v in range(n):
            actual = len(neighbors[u] & neighbors[v])
            expected = degree if u == v else 1 if v in neighbors[u] else 2
            row.append(actual)
            if actual != expected and first_failure is None:
                first_failure = {'u': u, 'v': v, 'actual': actual, 'expected': expected,
                                 'stage': 'SRG_DIAGONAL_CN' if u == v else 'SRG_EDGE_CN' if v in neighbors[u] else 'SRG_NONEDGE_CN'}
        common.append(row)
    return {'srg_valid': first_failure is None, 'complete_ordered_cn_entries': n*n,
            'degrees': degrees, 'common_neighbor_matrix': common, 'first_failure': first_failure}


def check_candidate(raw, candidate, budget=None):
    keys = {'schema', 'copy_labels', 'variable_pairs', 'edge_values',
            'exterior_adjacency', 'graph_object_validated'}
    need(type(candidate) is dict and candidate.keys() == keys
         and candidate['schema'] == CANDIDATE_SCHEMA
         and candidate['graph_object_validated'] is False, 'CANDIDATE_HEADER')
    geometry = profile_geometry(raw, budget)
    need(typed_equal(candidate['copy_labels'], geometry['labels']), 'CANDIDATE_COPY_LABELS')
    size = len(geometry['labels'])
    pairs = [[x, y] for x in range(size) for y in range(x+1, size)]
    need(typed_equal(candidate['variable_pairs'], pairs), 'CANDIDATE_VARIABLE_ORDER')
    values = candidate['edge_values']
    need(type(values) is list and len(values) == len(pairs)
         and all(type(value) is int and value in (0, 1) for value in values), 'CANDIDATE_BINARY')
    matrix_neighbors(candidate['exterior_adjacency'], size, budget)
    need(all(candidate['exterior_adjacency'][x][y] == values[ordinal]
             for ordinal, (x, y) in enumerate(pairs)), 'EDGE_MATRIX_IDENTITY')
    return check_copy_matrix(raw, candidate['copy_labels'], candidate['exterior_adjacency'], budget)


def rook_fixture():
    # The support is (0,0),(0,1); exterior order is canonical type/copy order.
    raw = {'target_order': 9, 'target_degree': 4,
           'support_adjacency': [[0, 1], [1, 0]],
           'ordered_masks': [0, 1, 2, 3], 'counts': [2, 2, 2, 1],
           'pair_bits': [{'i': i, 'j': j, 'bits': [0, 1]}
                         for i in range(4) for j in range(i, 4)]}
    labels = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1], [3, 0]]
    edges = {(0, 1), (0, 2), (0, 4), (0, 6), (1, 3), (1, 5),
             (1, 6), (2, 3), (2, 4), (3, 5), (4, 5)}
    pairs = [[x, y] for x in range(7) for y in range(x+1, 7)]
    matrix = [[int((min(x, y), max(x, y)) in edges) for y in range(7)] for x in range(7)]
    candidate = {'schema': 'FIXED17_COPY_ADJACENCY_INTEGER_CANDIDATE_V1',
                 'copy_labels': [list(label) for label in labels], 'variable_pairs': pairs,
                 'edge_values': [matrix[x][y] for x, y in pairs], 'exterior_adjacency': matrix,
                 'graph_object_validated': False}
    return {'profile': raw, 'candidate': candidate}


def switched_rook_fixture():
    fixture = rook_fixture()
    matrix = fixture['candidate']['exterior_adjacency']
    for x, y, value in ((2, 4, 0), (3, 5, 0), (2, 5, 1), (3, 4, 1)):
        matrix[x][y] = matrix[y][x] = value
    fixture['candidate']['edge_values'] = [matrix[x][y] for x, y in fixture['candidate']['variable_pairs']]
    return fixture


def kernel_fixture_assertions(budget=None):
    # Finite calibration action; no actual fixed17 data or producer code.
    fixture = rook_fixture()
    good = check_candidate(fixture['profile'], fixture['candidate'], budget)
    need(good['relaxation_exact_checked'] is True and good['reconstructed_graph_srg_valid'] is True
         and good['srg_diagnostic']['complete_ordered_cn_entries'] == 81
         and good['srg_diagnostic']['first_failure'] is None, 'ROOK_POSITIVE_DIAGNOSTIC')
    changed = switched_rook_fixture()
    noncompletion = check_candidate(changed['profile'], changed['candidate'], budget)
    need(noncompletion['relaxation_exact_checked'] is True
         and noncompletion['reconstructed_graph_srg_valid'] is False
         and noncompletion['srg_diagnostic']['complete_ordered_cn_entries'] == 81
         and typed_equal(noncompletion['srg_diagnostic']['first_failure'],
             {'u': 2, 'v': 4, 'actual': 0, 'expected': 1, 'stage': 'SRG_EDGE_CN'}),
         'ROOK_RELAXATION_BOUNDARY')
    # A copied fixture branch must not mutate either another branch or its own map.
    isolated = copy.deepcopy(fixture)
    isolated['candidate']['copy_labels'][0][1] = False
    need(type(fixture['candidate']['copy_labels'][0][1]) is int
         and fixture['candidate']['variable_pairs'][0] == [0, 1], 'FIXTURE_ALIAS_SEPARATION')
    return {'rook': good, 'relaxation_noncompletion': noncompletion,
            'fixture_alias_separation': True}


def wire_model(raw, budget=None):
    geometry, abstract = abstract_model(raw, budget)
    rows = []
    for row in abstract['rows']:
        tick(budget)
        x, u, rhs = row['copy'], row['coordinate'], row['rhs']
        rows.append({'kind':'degree' if u is None else 'support_incidence', 'copy_x':x,
            'type_i':geometry['labels'][x][0], 'support_u':u, 'lower':rhs, 'upper':rhs,
            'terms':row['terms']})
    return {'schema':MODEL_SCHEMA, 'target_order':raw['target_order'], 'target_degree':raw['target_degree'],
        'support_order':geometry['support'], 'ordered_masks':copy.deepcopy(raw['ordered_masks']),
        'counts':list(raw['counts']), 'copy_labels':copy.deepcopy(geometry['labels']),
        'variable_pairs':abstract['variable_pairs'], 'variables':len(abstract['variable_pairs']),
        'outside_copies':len(geometry['labels']), 'lower':abstract['lower'], 'upper':abstract['upper'],
        'rows':rows, 'no_equitable_profile_assumed':True, 'outside_pair_CN_equations_included':False}


def candidate_from_vector(built, values):
    n = built['outside_copies']
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for ordinal,(x,y) in enumerate(built['variable_pairs']):
        matrix[x][y] = matrix[y][x] = values[ordinal]
    return {'schema':CANDIDATE_SCHEMA, 'copy_labels':copy.deepcopy(built['copy_labels']),
        'variable_pairs':copy.deepcopy(built['variable_pairs']), 'edge_values':list(values),
        'exterior_adjacency':matrix, 'graph_object_validated':False}


def producer_row_receipt(built, independent):
    observations = []
    for ordinal,row in enumerate(independent['complete_equations']):
        x,u = row['copy'],row['coordinate']
        observations.append({'row':ordinal,'kind':'degree' if u is None else 'support_incidence',
            'copy_x':x,'type_i':built['copy_labels'][x][0],'support_u':u,'lhs':row['lhs'],'rhs':row['rhs']})
    return {'exact_binary_edge_variables':built['variables'], 'exact_copy_rows':len(observations),
        'degree_rows':built['outside_copies'], 'cross_incidence_rows':built['outside_copies']*built['support_order'],
        'copy_adjacency_local_feasible':True, 'graph_object_validated':False, 'observations':observations}


def model_identity(raw, expected):
    need(typed_equal(raw,expected),'MODEL_RECONSTRUCTION')


def checkpoint_prefix(built, ordinal, completed):
    return {'schema':'FIXED17_COPY_ADJACENCY_MODEL_CHECKPOINT_V1','index':ordinal,
        'completed_copies':completed,'rows':completed*(built['support_order']+1),'variables':built['variables'],
        'copy_labels_prefix':copy.deepcopy(built['copy_labels'][:completed])}


def checkpoint_identity(raw, expected):
    need(type(raw) is dict and raw.keys() == expected.keys()|{'deadline'},'CHECKPOINT_FIELDS')
    need(typed_equal({k:v for k,v in raw.items() if k != 'deadline'},expected),'CHECKPOINT_PREFIX')
    checkpoint_status(raw['deadline'],'CHECKPOINT_DEADLINE')


def forced_rook_profile():
    raw = rook_fixture()['profile']
    fixed = {(0,0):[1],(1,1):[1],(2,2):[1],(0,3):[1],(1,3):[0],(2,3):[0],(3,3):[0]}
    for row in raw['pair_bits']:
        row['bits'] = list(fixed.get((row['i'],row['j']),[0,1]))
    return raw


def corner_rook_fixture():
    raw = {'target_order':9,'target_degree':4,
        'support_adjacency':[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
        'ordered_masks':[0,1,2,3,5,10,12],'counts':[1,0,0,1,1,1,1],
        'pair_bits':[{'i':i,'j':j,'bits':[0,1]} for i in range(7) for j in range(i,7)]}
    # Outside order (2,2),(0,2),(2,0),(2,1),(1,2); explicitly listed rook edges.
    edges = {(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)}
    built = wire_model(raw)
    values = [int((x,y) in edges) for x,y in built['variable_pairs']]
    return {'profile':raw,'values':values}


AUTHOR_ROUTES = [
 ('rook_model','PASS'),('rook_integer','PASS'),('sole1_rook','PASS'),('zero_count_four_corners','PASS'),
 ('singleton_empty_diagonal','PASS'),('local_relaxation_not_SRG','PASS'),('native_known_rook','PASS'),
 ('bool_order','PROFILE_TARGET'),('bool_degree','PROFILE_TARGET'),('graph_float','PROFILE_GRAPH'),
 ('graph_asymmetric','PROFILE_GRAPH'),('mask_float','PROFILE_MASKS'),('duplicate_mask','PROFILE_MASKS'),
 ('count_bool','PROFILE_COUNTS'),('count_total','PROFILE_COUNTS'),('pair_order','PROFILE_PAIR_ORDER'),
 ('bits_bool','PROFILE_PAIR_BITS'),('bits_unsorted','PROFILE_PAIR_BITS'),('empty_positive_pair','PROFILE_INCOMPATIBLE_PAIR'),
 ('copy_label_bool','CANDIDATE_COPY_LABELS'),('edge_bool','CANDIDATE_BINARY'),('edge_float','CANDIDATE_BINARY'),
 ('self_loop','MATRIX_DIAGONAL'),('asymmetric','MATRIX_SYMMETRY'),('matrix_float','MATRIX_BINARY'),
 ('edge_disagreement','EDGE_MATRIX_IDENTITY'),('forbidden_pair','PAIR_BOUND'),
 ('degree_corruption','DEGREE_EQUATION'),('incidence_corruption','INCIDENCE_EQUATION')]


def author_action(name, payload, budget):
    profile_names = {name for name,_ in AUTHOR_ROUTES[7:19]}
    if name == 'rook_model' or name in profile_names:
        return wire_model(payload,budget)
    if name == 'native_known_rook':
        # Own calibration replaces the native call by a separately hand-listed exact rook witness.
        fixture = rook_fixture(); built = wire_model(payload,budget)
        return producer_row_receipt(built,check_candidate(payload,fixture['candidate'],budget))
    if name in ('zero_count_four_corners','singleton_empty_diagonal'):
        profile = payload['profile']; built = wire_model(profile,budget)
        return producer_row_receipt(built,check_candidate(profile,candidate_from_vector(built,payload['values']),budget))
    profile = forced_rook_profile() if name in ('sole1_rook','forbidden_pair') else rook_fixture()['profile']
    built = wire_model(profile,budget)
    return producer_row_receipt(built,check_candidate(profile,payload,budget))



def decode(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'JSON_DUPLICATE')
            result[k] = v
        return result
    def constant(_):
        raise Veto('JSON_NONFINITE')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise Veto('JSON_SYNTAX') from None

class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'Independent labelled-copy adjacency/model and raw closure checking; all authentication and saves share the allocation')
    def tick(self):
        s = self.deadline.status()
        need(not s['stop_required'] and s['remaining_seconds'] > 20, 'SAVE_RESERVE')
        return s

def safe(name, exists=True):
    p = Path(name)
    p = p if p.is_absolute() else ROOT / p
    need(p.resolve().is_relative_to(ROOT), 'PATH_SCOPE')
    for component in (p, *p.parents):
        if component == ROOT.parent:
            break
        if component.exists():
            flags = getattr(component.lstat(), 'st_file_attributes', 0)
            need(not component.is_symlink() and not (flags & stat.FILE_ATTRIBUTE_REPARSE_POINT), 'PATH_REPARSE')
    if exists:
        need(p.is_file(), 'INPUT_FILE')
    return p.resolve()

class Reader:
    def __init__(self, budget):
        self.budget = budget
        self.pins = {}
    def read(self, name, digest, parse=True):
        self.budget.tick()
        p = safe(name)
        need(type(digest) is str and len(digest) == 64 and
             all(c in '0123456789abcdef' for c in digest), 'HASH_SCHEMA')
        limit = 64 * 1024**2
        need(p.stat().st_size <= limit, 'INPUT_SIZE')
        h, chunks, size = hashlib.sha256(), [], 0
        with p.open('rb') as f:
            while True:
                self.budget.tick()
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                need(size <= limit, 'INPUT_SIZE')
                h.update(chunk)
                if parse:
                    chunks.append(chunk)
        need(h.hexdigest() == digest, 'INPUT_HASH')
        key = p.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == digest, 'PIN_CONFLICT')
        self.pins[key] = digest
        self.budget.tick()
        return decode(b''.join(chunks)) if parse else None
    def map(self, identities):
        need(type(identities) is dict and identities, 'INPUT_MAP')
        for name, digest in sorted(identities.items()):
            self.read(name, digest, False)
    def closing(self):
        self.map(dict(self.pins))

def write(path, obj, budget):
    budget.tick()
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')
    budget.tick()

def inventory(base, budget):
    result = set()
    for p in base.rglob('*'):
        budget.tick()
        if p.is_dir():
            safe(p,False)
        else:
            safe(p)
            result.add(p.relative_to(base).as_posix())
    return result

def packet(reader, path, digest):
    summary = reader.read(path,digest)
    need(type(summary) is dict, 'REPORT_SCHEMA')
    base = safe(path).parent
    outputs = summary.get('outputs_sha256')
    need(type(outputs) is dict and outputs and all(type(k) is str and type(v) is str for k,v in outputs.items()),
         'OUTPUT_MAP')
    need('summary.json' not in outputs and inventory(base,reader.budget) == set(outputs)|{'summary.json'},
         'OUTPUT_POPULATION')
    for name,digest in outputs.items():
        destination = base/name
        need(destination.resolve().is_relative_to(base) and destination != base, 'OUTPUT_PATH')
        reader.read(destination,digest,False)
    return summary,base


def options(words):
    need(type(words) is list and len(words)%2 == 0, 'ARGV_PAIRS')
    result = {}
    for key,value in zip(words[::2],words[1::2]):
        need(type(key) is str and key.startswith('--') and key not in result and type(value) is str,
             'ARGV_OPTION')
        result[key] = value
    return result

def runtime(plan, manifest, terminal, summary, mode, source):
    command,child,worker = (plan.get(k) for k in ('command','child_argv','worker_argv'))
    need(type(command) is list and type(child) is list and type(worker) is list and '--' in command, 'RUNTIME_PLAN')
    split = command.index('--')
    need(typed_equal(command[split+1:],child) and typed_equal(child[8:],worker), 'RUNTIME_SUFFIX')
    need(len(worker) == (14 if mode == 'calibrate' else 18) and worker[1] == '-B'
         and safe(worker[2]) == ROOT/PRODUCER and worker[3] == mode, 'RUNTIME_WORKER')
    need(safe(command[2]) == ROOT/'acceleration/run_compute_command.py', 'RUNTIME_SUPERVISOR')
    outer,flags = options(command[3:split]),options(worker[4:])
    need(flags.get('--self-sha256') == source['source'] and flags.get('--spec-sha256') == source['spec']
         and flags.get('--executor') in ('/root','/root/checkpoint_audit'), 'RUNTIME_SOURCE')
    need(typed_equal(manifest.get('command'),child) and manifest.get('source_sha256') ==
         SOFTWARE['acceleration/run_compute_command.py'] and type(manifest.get('schema_version')) is int and
         manifest['schema_version'] == 1 and manifest.get('process_scope') ==
         'Local non-escaping process tree only; remote/daemonized compute is unsupported' and
         manifest.get('cumulative_across_commands') is False and manifest.get('automatic_retry') is False and
         Path(manifest.get('cwd','')).resolve() == ROOT, 'RUNTIME_MANIFEST')
    for key in ('seconds','shutdown_reserve_seconds'):
        name = '--seconds' if key == 'seconds' else '--shutdown-reserve-seconds'
        need(type(manifest.get(key)) in (int,float) and math.isfinite(manifest[key]) and
             manifest[key] == float(outer[name]), 'RUNTIME_ALLOCATION')
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0 and
         terminal.get('error') is None and terminal.get('deadline_reached') is False, 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and all(cleanup.get(k) is True for k in ('created_suspended','resumed','reaped','job_active_zero_observed'))
         and cleanup.get('cleanup_errors') == [], 'RUNTIME_CLEANUP')
    need(type(manifest.get('invocation_id')) is str and manifest['invocation_id'] and
         terminal.get('invocation_id') == manifest['invocation_id'], 'RUNTIME_INVOCATION')
    elapsed = terminal.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and 0 <= elapsed <= manifest['seconds'], 'RUNTIME_ELAPSED')
    need(typed_equal(summary.get('command'),worker[2:]) and Path(summary.get('cwd','')).resolve() == ROOT,
         'RUNTIME_SUMMARY_COMMAND')
    need(summary.get('executor_declaration') == flags['--executor'] and
         summary.get('actual_executor_requires_external_receipt') is True, 'RUNTIME_EXECUTOR')
    status = summary.get('deadline')
    need(type(status) is dict and status.get('stop_required') is False and
         type(status.get('remaining_seconds')) in (int,float) and math.isfinite(status['remaining_seconds']) and
         status['remaining_seconds'] > 20, 'RUNTIME_WORKER_DEADLINE')
    return flags

def synthetic_runtime():
    worker = [str(ROOT/'build/research-venv/Scripts/python.exe'),'-B',str(ROOT/PRODUCER),'calibrate',
        '--seconds','100','--out',str(ROOT/'acceleration/results/synthetic_integer_controls'),
        '--self-sha256','pin','--spec-sha256','pin','--executor','/root']
    child = ['uv','run','--locked','--offline','--cache-dir',str(ROOT/'build/uv-cache'),'--python',worker[0],*worker]
    command = [worker[0],'-B',str(ROOT/'acceleration/run_compute_command.py'),'--seconds','120',
        '--shutdown-reserve-seconds','20','--out','synthetic_supervision','--allocation-reason','synthetic',
        '--success-criterion','synthetic','--verification-criterion','synthetic','--',*child]
    manifest = {'command':child,'source_sha256':SOFTWARE['acceleration/run_compute_command.py'],
        'schema_version':1,'process_scope':'Local non-escaping process tree only; remote/daemonized compute is unsupported',
        'cumulative_across_commands':False,'automatic_retry':False,'cwd':str(ROOT),'seconds':120,
        'shutdown_reserve_seconds':20,'invocation_id':'synthetic_integer'}
    terminal = {'command_exit_code':0,'error':None,'deadline_reached':False,'elapsed_seconds':1,
        'invocation_id':'synthetic_integer','cleanup':{'actual_exit_code':0,'created_suspended':True,
            'resumed':True,'reaped':True,'job_active_zero_observed':True,'cleanup_errors':[]}}
    summary = {'command':worker[2:],'cwd':str(ROOT),'executor_declaration':'/root',
        'actual_executor_requires_external_receipt':True,
        'deadline':{'stop_required':False,'remaining_seconds':90}}
    return {'plan':{'command':command,'child_argv':child,'worker_argv':worker},
            'manifest':manifest,'terminal':terminal,'summary':summary}


def reserve(raw):
    need(type(raw) is dict and raw.get('stop_required') is False and
         type(raw.get('remaining_seconds')) in (int,float) and math.isfinite(raw['remaining_seconds'])
         and raw['remaining_seconds'] > 20, 'SAVE_RESERVE')
    return raw



def runtime_profile(plan, mode):
    need(type(plan) is dict, 'RUNTIME_PLAN_SCHEMA')
    schema = plan.get('schema')
    if schema == 'FIXED17_COPY_ADJACENCY_SOURCE_ONLY_PLAN_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA'); result = plan.get('calibration')
    elif schema == 'ROOT_CONCRETE_FIXED17_COPY_ADJACENCY_AUTHOR_CALIBRATION_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA'); result = plan
    elif schema == 'FIXED17_COPY_ADJACENCY_CONCRETE_PLAN_V1':
        need(mode == 'solve', 'RUNTIME_PLAN_SCHEMA'); result = plan.get('solve')
        need(type(result) is dict and all(typed_equal(plan.get(k),result.get(k)) for k in
             ('command','supervisor_argv','child_argv','worker_argv','allocation')), 'RUNTIME_PLAN_ALIASES')
    else: raise Veto('RUNTIME_PLAN_SCHEMA')
    need(type(result) is dict, 'RUNTIME_PLAN_PROFILE')
    return result



def checkpoint_status(raw, stage):
    keys = {'elapsed_seconds','remaining_seconds','review_remaining_seconds','review_due','review_overdue_seconds',
            'deadline_reached','stop_required','deadline_at','review_deadline_at','completed_reviews'}
    numbers = keys-{'review_due','deadline_reached','stop_required','completed_reviews'}
    need(type(raw) is dict and set(raw) == keys and all(type(raw[k]) in (int,float) and
         math.isfinite(raw[k]) and raw[k] >= 0 for k in numbers) and
         all(raw[k] is False for k in ('review_due','deadline_reached','stop_required')) and
         type(raw['completed_reviews']) is int and raw['completed_reviews'] >= 0 and
         raw['remaining_seconds'] > 20 and raw['review_remaining_seconds'] > 0 and raw['review_overdue_seconds'] == 0,
         stage)


def synthetic_native_checkpoints(built, guidance):
    def status(elapsed,remaining):
        return {'elapsed_seconds':elapsed,'remaining_seconds':remaining,'review_remaining_seconds':1800.0-elapsed,
                'review_due':False,'review_overdue_seconds':0.0,'deadline_reached':False,'stop_required':False,
                'deadline_at':101.0,'review_deadline_at':1800.0,'completed_reviews':0}
    return {'before':{'variables':built['variables'],'rows':len(built['rows']),
        'nnz':sum(len(row['terms']) for row in built['rows']),'proposed_options':copy.deepcopy(guidance['options']),
        'remaining':status(1.0,100.0),'native_limit_finalized_after_checkpoint':True},
        'after':{'native_status':guidance['run_status'],'model_status':guidance['model_status'],
            'wall_seconds':guidance['wall_seconds'],'remaining':status(2.0,99.0),'is_proof':False},
        'guidance':guidance}

def native_checkpoints(before,after,guidance,built,maximum):
    need(type(before) is dict and set(before) == {'variables','rows','nnz','proposed_options','remaining',
        'native_limit_finalized_after_checkpoint'} and type(before['variables']) is int and
        before['variables'] == built['variables'] and type(before['rows']) is int and before['rows'] == len(built['rows'])
        and type(before['nnz']) is int and before['nnz'] == sum(len(row['terms']) for row in built['rows'])
        and before['native_limit_finalized_after_checkpoint'] is True, 'NATIVE_BEFORE_CHECKPOINT')
    checkpoint_status(before['remaining'],'NATIVE_BEFORE_DEADLINE')
    expected_options = dict(guidance['options']); expected_options['time_limit'] = float(maximum)
    need(typed_equal(before['proposed_options'],expected_options),'NATIVE_OPTIONS_CHECKPOINT')
    need(type(after) is dict and set(after) == {'native_status','model_status','wall_seconds','remaining','is_proof'}
         and after['native_status'] == guidance['run_status'] and after['model_status'] == guidance['model_status']
         and typed_equal(after['wall_seconds'],guidance['wall_seconds']) and after['is_proof'] is False, 'NATIVE_AFTER_CHECKPOINT')
    checkpoint_status(after['remaining'],'NATIVE_AFTER_DEADLINE')
    a,b = before['remaining'],after['remaining']
    need(b['elapsed_seconds'] >= a['elapsed_seconds'] and b['remaining_seconds'] <= a['remaining_seconds']
         and typed_equal(a['deadline_at'],b['deadline_at']) and typed_equal(a['review_deadline_at'],b['review_deadline_at'])
         and a['completed_reviews'] == b['completed_reviews'], 'NATIVE_DEADLINE_ORDER')



def guidance_checked(raw, built, budget, maximum):
    need(type(raw) is dict and set(raw) == {'schema','native_version','numpy_version','run_status','model_status',
        'solution_value_valid','col_value','col_value_float_hex','options','wall_seconds','objective_all_zero',
        'solver_calls','floating_status_is_proof','numeric_infeasibility_is_proof'} and
        raw['schema'] == 'FIXED17_COPY_ADJACENCY_NUMERIC_GUIDANCE_V1' and raw['native_version'] == '1.15.1'
        and type(raw['numpy_version']) is str and type(raw['run_status']) is str and type(raw['model_status']) is str,
        'GUIDANCE_HEADER')
    xs = raw['col_value']
    need(type(xs) is list and len(xs) in (0,built['variables']) and all(type(x) is float and math.isfinite(x) for x in xs), 'GUIDANCE_VALUES')
    need(type(raw['solution_value_valid']) is bool and (not raw['solution_value_valid'] or len(xs) == built['variables']), 'GUIDANCE_VALIDITY')
    need(typed_equal(raw['col_value_float_hex'],[x.hex() for x in xs]), 'GUIDANCE_HEX')
    need(type(raw['solver_calls']) is int and raw['solver_calls'] == 1 and raw['objective_all_zero'] is True and
         raw['floating_status_is_proof'] is False and raw['numeric_infeasibility_is_proof'] is False,'GUIDANCE_SCOPE')
    need(type(raw['wall_seconds']) in (int,float) and math.isfinite(raw['wall_seconds']) and raw['wall_seconds'] >= 0, 'GUIDANCE_ELAPSED')
    opts = raw['options']; expected = {'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
        'mip_rel_gap':0.0,'mip_abs_gap':0.0,'mip_feasibility_tolerance':1e-7,'primal_feasibility_tolerance':1e-7,
        'output_flag':True,'log_to_console':False}
    need(type(opts) is dict and set(opts) == set(expected)|{'log_file','time_limit'} and
         all(typed_equal(opts.get(k),v) for k,v in expected.items()) and type(opts['log_file']) is str and
         type(opts['time_limit']) in (int,float) and math.isfinite(opts['time_limit']) and 0 < opts['time_limit'] <= maximum,
         'GUIDANCE_OPTIONS')
    budget.tick(); return raw['wall_seconds']



def own_header(raw,software,mode):
    need(type(raw) is dict and raw.get('status') == (CAL_STATUS if mode == 'calibrate' else CONTROLS_STATUS)
         and raw.get('mode') == mode and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 1
         and raw.get('producer') == '/root/checkpoint_audit' and raw.get('verifier') == '/root/native_driver'
         and raw.get('method') == 'independent_artifact_check' and raw.get('target_resolution') == 'NONE'
         and raw.get('actual_target_input_read') is False and typed_equal(raw.get('source_software'),software),'OWN_HEADER')
    need(typed_equal(raw.get('outcome',{}).get('counts'),OWN_COUNTS if mode == 'calibrate' else AUTHOR_COUNTS)
         and raw['outcome'].get('all_precise_stages_match') is True,'OWN_SCOPE')


def qualify(reader,args,software):
    summary,base = packet(reader,args.calibration,args.calibration_sha256)
    own_header(summary,software,'calibrate'); need(typed_equal(summary.get('inputs_sha256'),software),'OWN_SOFTWARE')
    rows = reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(rows) is list and len(rows) == OWN_COUNTS['total'] and all(type(row) is dict and
         type(row.get('index')) is int and row['index'] == i and row.get('matches') is True and
         row.get('expected_stage') == row.get('actual_stage') for i,row in enumerate(rows)), 'OWN_STAGE_TABLE')


def source_packet(reader,args,mode):
    plan = reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base = packet(reader,args.producer_summary,args.producer_summary_sha256)
    need(summary.get('schema') == 'FIXED17_COPY_ADJACENCY_PRODUCER_REPORT_V1'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1
         and summary.get('mode') == mode and summary.get('producer') == '/root/checkpoint_audit'
         and summary.get('source_author') == '/root/checkpoint_audit' and summary.get('independent_approval') is False
         and summary.get('target_resolution') == 'NONE' and summary.get('automatic_retry') is False
         and summary.get('actual_count_input_read') is (mode == 'solve'),'PRODUCER_HEADER')
    need(typed_equal(summary.get('source_software'),AUTHOR_SOFTWARE),'PRODUCER_SOFTWARE')
    declared = summary.get('inputs_sha256')
    need(type(declared) is dict and all(type(p) is str and type(h) is str and len(h) == 64 and
         all(c in '0123456789abcdef' for c in h) for p,h in declared.items()) and
         all(declared.get(p) == h for p,h in AUTHOR_SOFTWARE.items()),'PRODUCER_DECLARED_INPUTS')
    reader.map(AUTHOR_SOFTWARE)
    manifest = reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal = reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags = runtime(runtime_profile(plan,mode),manifest,terminal,summary,mode,
        {'source':AUTHOR_SOFTWARE[PRODUCER],'spec':AUTHOR_SOFTWARE[PRODUCER_SPEC]})
    output_directory(flags['--out'],base)
    if mode == 'calibrate':
        need(summary.get('status') == 'FIXED17_COPY_ADJACENCY_V1_AUTHOR_CONTROLS_PASS'
             and typed_equal(declared,AUTHOR_SOFTWARE),'PRODUCER_STATUS')
    else:
        need(summary.get('status') in ('CANDIDATE_FIXED17_COPY_ADJACENCY_V1','NO_EXACT_COPY_ADJACENCY_WITNESS_V1'), 'PRODUCER_STATUS')
    return summary,base,flags



def direct_premises(reader):
    reader.map(PREMISES)
    trusted = reader.read(TRUSTED_PROFILE,TRUSTED_PROFILE_SHA)
    prefix = 'acceleration/results/20261004_independent_review/'
    for name,status,implementation,producer in (
        ('external_moment_integer_counts_full01','INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS',1,'/root/checkpoint_audit'),
        ('fixed17_dual_gram_pairs_full02','INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS',2,'/root/structural'),
        ('fixed17_count_neighbor_capacity_full01','INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS',1,'/root/checkpoint_audit')):
        path = prefix+name+'/summary.json'; raw = reader.read(path,PREMISES[path])
        need(raw.get('status') == status and raw.get('mode') == 'full' and type(raw.get('implementation_version')) is int
             and raw['implementation_version'] == implementation and raw.get('producer') == producer
             and raw.get('verifier') == '/root/native_driver' and raw.get('method') == 'independent_artifact_check'
             and raw.get('target_resolution') == 'NONE','PREMISE_GATE')
        if name.startswith('fixed17_count_neighbor'):
            need(raw.get('inputs_sha256',{}).get(TRUSTED_PROFILE) == TRUSTED_PROFILE_SHA and
                 raw.get('outcome',{}).get('all_screens_pass') is True,'PROFILE_PREMISE')
        if name.startswith('external_moment'):
            cp = 'acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json'
            need(raw.get('inputs_sha256',{}).get(cp) == PREMISES[cp] and raw.get('outcome',{}).get('candidate_exact_checked') is True,'COUNT_PREMISE')
    cp = 'acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json'
    count = reader.read(cp,PREMISES[cp])
    need(typed_equal(count.get('ordered_masks'),trusted.get('ordered_masks')) and typed_equal(count.get('counts'),trusted.get('counts')),'COUNT_PROFILE_IDENTITY')
    theorem_path = prefix+'target_exterior_type_edge_moments01/summary.json'
    theorem = reader.read(theorem_path,PREMISES[theorem_path])
    need(theorem.get('status') == 'INDEPENDENT_TARGET_EXTERIOR_TYPE_NEIGHBOR_PROFILES_AND_EDGE_MOMENTS_V1_WRITTEN_PASS'
         and theorem.get('claim_id') == 'C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS'
         and type(theorem.get('claim_revision')) is int and theorem['claim_revision'] == 1
         and theorem.get('producer') == '/root/structural' and theorem.get('verifier') == '/root/native_driver'
         and theorem.get('method') == 'independent_derivation' and theorem.get('outcome') == 'PASS'
         and theorem.get('target_resolution') == 'NONE','BLOCK_PREMISE')
    return trusted


def configuration(reader,args,flags,software):
    controls,cbase = packet(reader,args.producer_controls,args.producer_controls_sha256)
    own_header(controls,software,'controls')
    need(controls.get('inputs_sha256',{}).get(safe(args.calibration).relative_to(ROOT).as_posix()) == args.calibration_sha256,
         'CONTROLS_CALIBRATION_PIN')
    config = reader.read(flags['--configuration'],flags['--configuration-sha256'])
    need(type(config) is dict and config.get('schema') == 'FIXED17_COPY_ADJACENCY_CONFIGURATION_V1'
         and config.get('target_resolution') == 'NONE' and type(config.get('inputs_sha256')) is dict,'CONFIG_HEADER')
    pins = config['inputs_sha256']
    for path,digest in {**PREMISES,**AUTHOR_SOFTWARE}.items(): need(pins.get(path) == digest,'CONFIG_DIRECT_PIN')
    for key,path,digest in (
        ('independent_checker_source',SELF,software[SELF]),('independent_checker_spec',SPEC,software[SPEC]),
        ('independent_calibration',args.calibration,args.calibration_sha256),
        ('independent_producer_controls',args.producer_controls,args.producer_controls_sha256)):
        name = config.get(key+'_path'); sha = config.get(key+'_sha256')
        need(type(name) is str and safe(name) == safe(path) and sha == digest and
             pins.get(safe(path).relative_to(ROOT).as_posix()) == digest,'CONFIG_QUALIFICATION_PIN')
    maximum = config.get('maximum_solver_seconds')
    need(type(maximum) is int and 0 < maximum <= 1200,'CONFIG_SOLVER_RANGE')
    author_path = config.get('author_calibration_path'); author_sha = config.get('author_calibration_sha256')
    need(type(author_path) is str and type(author_sha) is str and pins.get(safe(author_path).relative_to(ROOT).as_posix()) == author_sha
         and controls.get('inputs_sha256',{}).get(safe(author_path).relative_to(ROOT).as_posix()) == author_sha,'CONFIG_AUTHOR_PIN')
    author,abase = packet(reader,author_path,author_sha)
    need(author.get('status') == 'FIXED17_COPY_ADJACENCY_V1_AUTHOR_CONTROLS_PASS' and
         author.get('mode') == 'calibrate' and typed_equal(author.get('source_software'),AUTHOR_SOFTWARE),'AUTHOR_HEADER')
    need(all(type(p) is str and type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h)
         for p,h in pins.items()),'CONFIG_PIN_SCHEMA')
    reader.map(pins)
    declared = {**AUTHOR_SOFTWARE,**pins,
        safe(flags['--configuration']).relative_to(ROOT).as_posix():flags['--configuration-sha256']}
    for name,digest in author['outputs_sha256'].items():
        declared[(abase/name).relative_to(ROOT).as_posix()] = digest
    return direct_premises(reader),maximum,author,abase,declared


def output_directory(name, base):
    need(type(name) is str,'PRODUCER_OUTPUT_DIRECTORY')
    path = safe(name,False)
    need(path.is_dir() and path == base,'PRODUCER_OUTPUT_DIRECTORY')


def extraction(profile, built, guidance, budget):
    xs = guidance['col_value']
    if not guidance['solution_value_valid'] or len(xs) != built['variables']:
        return {'candidate':None,'reason':'No complete value-valid numeric incumbent','infeasibility_proved':False}
    values = [int(round(x)) for x in xs]
    distances = [abs(x-y) for x,y in zip(xs,values)]
    if any(x > 1e-7 for x in distances):
        return {'candidate':None,'reason':'Numerical coordinates exceed the declared extraction distance',
            'max_rounding_distance':max(distances),'infeasibility_proved':False}
    candidate = candidate_from_vector(built,values)
    try: receipt = producer_row_receipt(built,check_candidate(profile,candidate,budget))
    except Veto as exc:
        if str(exc) == 'SAVE_RESERVE': raise
        return {'candidate':None,'reason':'Extracted integers fail exact check: '+str(exc),'infeasibility_proved':False}
    return {'candidate':candidate,'exact_check':receipt,'rounding_tolerance':1e-7,
        'max_rounding_distance':max(distances,default=0.0),'infeasibility_proved':False}


def extraction_identity(raw, expected):
    need(typed_equal(raw,expected),'EXTRACTION_IDENTITY')


def synthetic_guidance(values, valid=True):
    xs = [float(x) for x in values]
    return {'schema':'FIXED17_COPY_ADJACENCY_NUMERIC_GUIDANCE_V1','native_version':'1.15.1',
        'numpy_version':'synthetic','run_status':'synthetic','model_status':'synthetic',
        'solution_value_valid':valid,'col_value':xs,'col_value_float_hex':[x.hex() for x in xs],
        'options':{'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
            'mip_rel_gap':0.0,'mip_abs_gap':0.0,'mip_feasibility_tolerance':1e-7,'primal_feasibility_tolerance':1e-7,
            'output_flag':True,'log_to_console':False,'log_file':'synthetic','time_limit':5.0},
        'wall_seconds':0.0,'objective_all_zero':True,'solver_calls':1,
        'floating_status_is_proof':False,'numeric_infeasibility_is_proof':False}


def author_fixture_payloads(budget):
    fixture = rook_fixture(); free,witness = fixture['profile'],fixture['candidate']
    built = wire_model(free,budget); forced = forced_rook_profile()
    empty = copy.deepcopy(free); empty['pair_bits'][-1]['bits'] = []
    payloads = [free,witness,copy.deepcopy(witness),corner_rook_fixture(),
        {'profile':empty,'values':list(witness['edge_values'])},switched_rook_fixture()['candidate'],copy.deepcopy(free)]
    edits = [
        ('profile',lambda x:x.__setitem__('target_order',True)),
        ('profile',lambda x:x.__setitem__('target_degree',True)),
        ('profile',lambda x:x['support_adjacency'][0].__setitem__(1,1.0)),
        ('profile',lambda x:x['support_adjacency'][0].__setitem__(1,0)),
        ('profile',lambda x:x['ordered_masks'].__setitem__(0,0.0)),
        ('profile',lambda x:x['ordered_masks'].__setitem__(1,0)),
        ('profile',lambda x:x['counts'].__setitem__(0,True)),
        ('profile',lambda x:x['counts'].__setitem__(0,1)),
        ('profile',lambda x:x['pair_bits'][0].__setitem__('i',1)),
        ('profile',lambda x:x['pair_bits'][0].__setitem__('bits',[True])),
        ('profile',lambda x:x['pair_bits'][0].__setitem__('bits',[1,0])),
        ('profile',lambda x:x['pair_bits'][1].__setitem__('bits',[])),
        ('candidate',lambda x:x['copy_labels'][0].__setitem__(0,False)),
        ('candidate',lambda x:x['edge_values'].__setitem__(0,True)),
        ('candidate',lambda x:x['edge_values'].__setitem__(0,1.0)),
        ('candidate',lambda x:x['exterior_adjacency'][0].__setitem__(0,1)),
        ('candidate',lambda x:x['exterior_adjacency'][0].__setitem__(1,0)),
        ('candidate',lambda x:x['exterior_adjacency'][0].__setitem__(1,1.0)),
        ('candidate',lambda x:x['edge_values'].__setitem__(0,0))]
    for category,edit in edits:
        altered = copy.deepcopy(free if category == 'profile' else witness)
        edit(altered); payloads.append(altered)
    forbidden = list(witness['edge_values']); forbidden[unordered_rank(2,6,7)] = 1
    removed = list(witness['edge_values']); removed[0] = 0
    incidence = list(witness['edge_values'])
    for x,y,bit in ((0,1,0),(2,3,0),(0,3,1),(1,2,1)):
        incidence[unordered_rank(x,y,7)] = bit
    payloads += [candidate_from_vector(wire_model(forced,budget),forbidden),
        candidate_from_vector(built,removed),candidate_from_vector(built,incidence)]
    return payloads


def own_routes(budget,out):
    records = []
    def run(name,expected,payload,action):
        budget.tick(); ordinal = len(records)
        write(out/('control_%03d_%s.json'%(ordinal,name)),payload,budget)
        try: result,stage = action(payload),'PASS'
        except Veto as exc:
            if str(exc) == 'SAVE_RESERVE' and expected != 'SAVE_RESERVE': raise
            result,stage = None,str(exc)
        row = {'index':ordinal,'name':name,'expected_stage':expected,'actual_stage':stage,'matches':stage == expected}
        write(out/('stage_%03d.json'%ordinal),row,budget); records.append(row)
        if name == 'positive_direct_graph_and_alias': write(out/'independent_rook_diagnostics.json',result,budget)
        need(stage == expected,'CONTROL_STAGE:'+name+':'+stage)
    def altered(name,stage,original,edit,action):
        changed = copy.deepcopy(original); edit(changed); run(name,stage,changed,action)
    payloads = author_fixture_payloads(budget)
    need(len(payloads) == len(AUTHOR_ROUTES),'AUTHOR_COUNTERPART_POPULATION')
    for (name,stage),payload in zip(AUTHOR_ROUTES,payloads):
        run(name,stage,payload,lambda p,name=name:author_action(name,p,budget))
    fixture = rook_fixture(); raw,witness = fixture['profile'],fixture['candidate']; built = wire_model(raw,budget)
    guidance = synthetic_guidance(witness['edge_values']); absent_guidance = synthetic_guidance([],False)
    fractional = synthetic_guidance([0.5]+witness['edge_values'][1:])
    absent = extraction(raw,built,absent_guidance,budget)
    cp = {**checkpoint_prefix(built,0,7),'deadline':synthetic_native_checkpoints(built,guidance)['before']['remaining']}
    native = synthetic_native_checkpoints(built,guidance); rt = synthetic_runtime()
    rt_action = lambda p:runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate',{'source':'pin','spec':'pin'})
    native_action = lambda p:native_checkpoints(p['before'],p['after'],p['guidance'],built,5)
    # Thirteen new positive actions beyond the seven author counterparts.
    run('positive_direct_graph_and_alias','PASS',{'known_rook_order':9},lambda p:kernel_fixture_assertions(budget))
    run('positive_model_wire','PASS',built,lambda p:model_identity(p,built))
    run('positive_complete_checkpoint','PASS',cp,lambda p:checkpoint_identity(p,checkpoint_prefix(built,0,7)))
    run('positive_guidance','PASS',guidance,lambda p:guidance_checked(p,built,budget,5))
    run('positive_absent_without_exclusion','PASS',absent,lambda p:extraction_identity(p,absent))
    run('positive_fractional_without_exclusion','PASS',fractional,lambda p:extraction(raw,built,p,budget))
    run('positive_exact_extraction','PASS',guidance,lambda p:extraction(raw,built,p,budget))
    run('positive_actual_status_native_checkpoints','PASS',native,native_action)
    run('positive_actual_593_runtime','PASS',rt,rt_action)
    run('positive_save_reserve','PASS',{'stop_required':False,'remaining_seconds':21.0},reserve)
    run('positive_output_directory','PASS',str(out),lambda p:output_directory(p,out))
    run('positive_strict_json','PASS',{'text':'[0,1,2]'},lambda p:decode(p['text']))
    run('positive_invalid_complete_numeric_vector','PASS',synthetic_guidance([0]*built['variables'],False),
        lambda p:extraction(raw,built,p,budget))
    # Thirty-two new precise negative actions.
    altered('candidate_graph_approval_flag','CANDIDATE_HEADER',witness,lambda p:p.__setitem__('graph_object_validated',True),lambda p:check_candidate(raw,p,budget))
    altered('candidate_pair_bool','CANDIDATE_VARIABLE_ORDER',witness,lambda p:p['variable_pairs'][0].__setitem__(0,False),lambda p:check_candidate(raw,p,budget))
    altered('candidate_edge_two','CANDIDATE_BINARY',witness,lambda p:p['edge_values'].__setitem__(0,2),lambda p:check_candidate(raw,p,budget))
    altered('candidate_matrix_missing','MATRIX_BINARY',witness,lambda p:p['exterior_adjacency'].pop(),lambda p:check_candidate(raw,p,budget))
    altered('model_rhs_bool','MODEL_RECONSTRUCTION',built,lambda p:p['rows'][0].__setitem__('lower',True),lambda p:model_identity(p,built))
    altered('model_last_coordinate','MODEL_RECONSTRUCTION',built,lambda p:p['rows'][-1]['terms'].pop(),lambda p:model_identity(p,built))
    altered('checkpoint_late_count','CHECKPOINT_PREFIX',cp,lambda p:p.__setitem__('completed_copies',6),lambda p:checkpoint_identity(p,checkpoint_prefix(built,0,7)))
    altered('checkpoint_prefix_bool','CHECKPOINT_PREFIX',cp,lambda p:p['copy_labels_prefix'][-1].__setitem__(1,False),lambda p:checkpoint_identity(p,checkpoint_prefix(built,0,7)))
    altered('checkpoint_legacy_scalar','CHECKPOINT_DEADLINE',cp,lambda p:p.__setitem__('deadline',99.0),lambda p:checkpoint_identity(p,checkpoint_prefix(built,0,7)))
    altered('guidance_bool','GUIDANCE_VALUES',guidance,lambda p:p['col_value'].__setitem__(0,True),lambda p:guidance_checked(p,built,budget,5))
    altered('guidance_hex','GUIDANCE_HEX',guidance,lambda p:p['col_value_float_hex'].__setitem__(0,'wrong'),lambda p:guidance_checked(p,built,budget,5))
    def float_control(p):
        changed = copy.deepcopy(p['guidance']); changed['col_value'][0] = float(p['value'])
        return guidance_checked(changed,built,budget,5)
    run('guidance_nonfinite','GUIDANCE_VALUES',{'guidance':guidance,'value':'inf'},float_control)
    altered('guidance_validity_integer','GUIDANCE_VALIDITY',guidance,lambda p:p.__setitem__('solution_value_valid',1),lambda p:guidance_checked(p,built,budget,5))
    altered('guidance_proof_flag','GUIDANCE_SCOPE',guidance,lambda p:p.__setitem__('floating_status_is_proof',True),lambda p:guidance_checked(p,built,budget,5))
    altered('absence_infeasibility_flag','EXTRACTION_IDENTITY',absent,lambda p:p.__setitem__('infeasibility_proved',True),lambda p:extraction_identity(p,absent))
    altered('native_before_legacy_scalar','NATIVE_BEFORE_DEADLINE',native,lambda p:p['before'].__setitem__('remaining',100.0),native_action)
    altered('native_before_remaining_bool','NATIVE_BEFORE_DEADLINE',native,lambda p:p['before']['remaining'].__setitem__('remaining_seconds',True),native_action)
    altered('native_after_stop','NATIVE_AFTER_DEADLINE',native,lambda p:p['after']['remaining'].__setitem__('stop_required',True),native_action)
    altered('native_reversed_elapsed','NATIVE_DEADLINE_ORDER',native,lambda p:p['after']['remaining'].__setitem__('elapsed_seconds',0.0),native_action)
    altered('runtime_wrong_source','RUNTIME_MANIFEST',rt,lambda p:p['manifest'].__setitem__('source_sha256','wrong'),rt_action)
    altered('runtime_bool_actual_exit','RUNTIME_CLEANUP',rt,lambda p:p['terminal']['cleanup'].__setitem__('actual_exit_code',False),rt_action)
    altered('runtime_elapsed_bool','RUNTIME_ELAPSED',rt,lambda p:p['terminal'].__setitem__('elapsed_seconds',True),rt_action)
    run('plan_schema','RUNTIME_PLAN_SCHEMA',{'schema':'invented'},lambda p:runtime_profile(p,'calibrate'))
    nested = {'schema':'FIXED17_COPY_ADJACENCY_CONCRETE_PLAN_V1','solve':rt['plan'],**rt['plan']}
    altered('science_alias_mismatch','RUNTIME_PLAN_ALIASES',nested,lambda p:p.__setitem__('worker_argv',[]),lambda p:runtime_profile(p,'solve'))
    run('output_file_as_directory','PRODUCER_OUTPUT_DIRECTORY',str(out/'control_000_rook_model.json'),lambda p:output_directory(p,out))
    run('reserve_boundary','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20.0},reserve)
    run('reserve_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':21.0},reserve)
    run('json_duplicate','JSON_DUPLICATE',{'text':'{"x":1,"x":2}'},lambda p:decode(p['text']))
    run('json_nonfinite','JSON_NONFINITE',{'text':'{"x":NaN}'},lambda p:decode(p['text']))
    good_graph = kernel_fixture_assertions(budget)['rook']['full_adjacency']
    altered('srg_matrix_float','SRG_BINARY',good_graph,lambda p:p[0].__setitem__(1,1.0),lambda p:whole_srg_diagnostic(p,4,budget))
    altered('native_before_missing_key','NATIVE_BEFORE_DEADLINE',native,lambda p:p['before']['remaining'].pop('review_due'),native_action)
    altered('native_proposed_options','NATIVE_OPTIONS_CHECKPOINT',native,lambda p:p['before']['proposed_options'].__setitem__('threads',2),native_action)
    return records


def replay_controls(reader,summary,base,out):
    expected = {**AUTHOR_COUNTS,'stage_mismatches':[],'native_fixture_calls':1,
        'known_rook_order':9,'known_rook_degree':4,'actual_fixed17_read':False}
    need(typed_equal(summary.get('outcome'),expected),'AUTHOR_SCOPE')
    outputs,names,pairs = summary['outputs_sha256'],set(),[]
    def load(name):
        names.add(name); need(name in outputs,'AUTHOR_PAYLOAD')
        return reader.read(base/name,outputs[name])
    rows = load('controls.json')
    need(type(rows) is list and len(rows) == AUTHOR_COUNTS['total'],'AUTHOR_STAGE_POPULATION')
    for ordinal,(name,expected_stage) in enumerate(AUTHOR_ROUTES):
        reader.budget.tick(); payload = load('control_%03d_%s.json'%(ordinal,name))
        try:
            if name == 'native_known_rook':
                built = wire_model(payload,reader.budget)
                guidance = load('known_rook_guidance.json')
                guidance_checked(guidance,built,reader.budget,5)
                native_checkpoints(load('known_rook_before_solver.json'),load('known_rook_after_solver.json'),guidance,built,5)
                names.add('known_rook_solver.log')
                need(guidance['options']['log_file'] == str(base/'known_rook_solver.log'),'NATIVE_LOG_PATH')
                result = extraction(payload,built,guidance,reader.budget)
                need(result['candidate'] is not None,'FIXTURE_EXACT_WITNESS')
            else: result = author_action(name,payload,reader.budget)
            stage = 'PASS'
        except Veto as exc:
            if str(exc) == 'SAVE_RESERVE': raise
            result,stage = None,str(exc)
        expected_row = {'index':ordinal,'name':name,'expected_stage':expected_stage,
            'actual_stage':expected_stage,'matches':True}
        need(typed_equal(rows[ordinal],expected_row) and
            typed_equal(load('stage_%03d.json'%ordinal),expected_row),'AUTHOR_STAGE_ROW')
        need(stage == expected_stage,'AUTHOR_INDEPENDENT_STAGE:'+name+':'+stage)
        if expected_stage == 'PASS':
            need(typed_equal(load('result_%03d.json'%ordinal),result),'AUTHOR_RETURNED_RESULT')
            write(out/('independent_result_%03d.json'%ordinal),result,reader.budget)
        pairs.append({'index':ordinal,'name':name,'expected_stage':expected_stage,
            'producer_stage':rows[ordinal]['actual_stage'],'independent_stage':stage,'matches':True})
    need(names == set(outputs) and len(names) == 70,'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',pairs,reader.budget)
    return {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'producer_physical_files':71,
        'producer_output_hashes':70,'complete_rook_local_systems':6,'complete_native_fixture_receipts':1,
        'solver_calls':0,'actual_target_input_read':False,'graph_object_approved':False}


def full(reader,args,summary,base,flags,out,software):
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'CONTROLS_ARGUMENTS')
    trusted,maximum,author,abase,declared = configuration(reader,args,flags,software)
    need(typed_equal(summary.get('inputs_sha256'),declared),'SCIENTIFIC_DECLARED_INPUTS')
    reader.map(declared)
    author_scope = replay_controls(reader,author,abase,out)
    outputs,names = summary['outputs_sha256'],set()
    def load(name):
        names.add(name); need(name in outputs,'SCIENTIFIC_PAYLOAD')
        return reader.read(base/name,outputs[name])
    raw = load('parsed_copy_input.json'); need(typed_equal(raw,trusted),'TRUSTED_PROFILE_IDENTITY')
    built = wire_model(raw,reader.budget); model_identity(load('copy_model.json'),built)
    need(raw['target_order'] == 99 and raw['target_degree'] == 14 and built['support_order'] == 17 and
        len(raw['ordered_masks']) == 472 and sum(raw['counts']) == 82 and sum(n > 0 for n in raw['counts']) == 68 and
        built['variables'] == 3321 and built['outside_copies'] == 82 and len(built['rows']) == 1476,'FIXED_SCOPE')
    prefixes = []; previous = None
    for ordinal,completed in enumerate([10,20,30,40,50,60,70,80,82]):
        actual = load('model_checkpoint_%03d.json'%ordinal)
        expected = checkpoint_prefix(built,ordinal,completed); checkpoint_identity(actual,expected)
        status = actual['deadline']
        if previous is not None:
            need(status['elapsed_seconds'] >= previous['elapsed_seconds'] and
                status['remaining_seconds'] <= previous['remaining_seconds'] and
                typed_equal(status['deadline_at'],previous['deadline_at']) and
                typed_equal(status['review_deadline_at'],previous['review_deadline_at']) and
                status['completed_reviews'] == previous['completed_reviews'],'CHECKPOINT_DEADLINE_ORDER')
        previous = status; prefixes.append(expected)
    guidance = load('scientific_guidance.json'); guidance_checked(guidance,built,reader.budget,maximum)
    native_checkpoints(load('scientific_before_solver.json'),load('scientific_after_solver.json'),guidance,built,maximum)
    names.add('scientific_solver.log')
    need(guidance['options']['log_file'] == str(base/'scientific_solver.log'),'NATIVE_LOG_PATH')
    extracted = extraction(raw,built,guidance,reader.budget)
    extraction_identity(load('extraction.json'),extracted)
    present = extracted['candidate'] is not None
    diagnostic = None
    if present:
        candidate = load('exact_integer_copy_edges.json')
        need(typed_equal(candidate,extracted['candidate']),'EXACT_CANDIDATE_IDENTITY')
        checked = check_candidate(raw,candidate,reader.budget)
        receipt = producer_row_receipt(built,checked)
        need(typed_equal(load('exact_copy_rows.json'),receipt['observations']),'EXACT_ROW_TABLE')
        write(out/'independent_exact_copy_rows.json',receipt,reader.budget)
        write(out/'independent_full_adjacency.json',checked['full_adjacency'],reader.budget)
        diagnostic = checked['srg_diagnostic']; write(out/'independent_full_srg_diagnostic.json',diagnostic,reader.budget)
    need(names == set(outputs) and len(names) == (18 if present else 16),'SCIENTIFIC_OUTPUT_POPULATION')
    expected = {'complete_input_type_count':472,'positive_types':68,'outside_copies':82,
        'binary_edge_variables':3321,'degree_rows':82,'cross_incidence_rows':1394,'equations':1476,
        'model_checkpoints':9,'scientific_solver_calls':1,'exact_integer_candidate_produced':present,
        'candidate_absent_reason':extracted.get('reason'),'numeric_model_status':guidance['model_status'],
        'copy_adjacency_local_feasibility':'CANDIDATE' if present else 'UNKNOWN','infeasibility_proved':False,
        'graph_object_validated':False,'full99_matrix_written':False,'outside_pair_CN_equations_included':False,
        'no_equitable_profile_assumed':True}
    need(typed_equal(summary.get('outcome'),expected),'SCIENTIFIC_OUTCOME')
    need(summary['status'] == ('CANDIDATE_FIXED17_COPY_ADJACENCY_V1' if present else 'NO_EXACT_COPY_ADJACENCY_WITNESS_V1'),'SCIENTIFIC_STATUS')
    write(out/'independent_copy_model.json',built,reader.budget)
    write(out/'independent_model_checkpoint_prefixes.json',prefixes,reader.budget)
    return {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'author_control_scope':author_scope,
        'complete_input_type_count':472,'positive_types':68,'outside_copies':82,'binary_edge_variables':3321,
        'complete_degree_rows':82,'complete_support_incidence_rows':1394,'complete_equations':1476,
        'model_checkpoints':9,'candidate_exact_checked':present,'copy_adjacency_local_feasible':True if present else None,
        'unknown_reason':None if present else 'No exact saved binary per-copy witness; no infeasibility conclusion',
        'full_srg_diagnostic_checked':present,'complete_ordered_cn_entries':9801 if present else 0,
        'reconstructed_graph_srg_valid':diagnostic['srg_valid'] if present else None,
        'first_graph_diagnostic_failure':diagnostic['first_failure'] if present else None,
        'target_object_acceptance_requires_separate_receipt':True,'graph_object_approved':False,
        'no_equitable_profile_assumed':True,'outside_pair_CN_model_equations_included':False,
        'count_witness_excluded':False,'numeric_status_is_proof':False,'solver_calls':0}


def calibrate(out,budget):
    rows = own_routes(budget,out)
    positives = sum(row['expected_stage'] == 'PASS' for row in rows)
    need(len(rows) == OWN_COUNTS['total'] and positives == OWN_COUNTS['positive'] and
        all(row['matches'] for row in rows),'OWN_POPULATION')
    write(out/'controls.json',rows,budget)
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'actual_target_input_read':False,
        'solver_calls':0,'producer_imports':0,'graph_object_approved':False,'complete_rook_cn_entries':162}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    for name in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+name,required=True,type=float if name == 'seconds' else str)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name); parser.add_argument('--'+name+'-sha256')
    args = parser.parse_args(); budget = Budget(args.seconds); out = safe(args.out,False)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_FRESH'); out.mkdir(parents=True)
    reader = Reader(budget); software = {**SOFTWARE,SELF:args.self_sha256,SPEC:args.spec_sha256}
    try:
        reader.map(software)
        if args.mode == 'calibrate': outcome,status = calibrate(out,budget),CAL_STATUS
        else:
            for name in ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal'):
                need(getattr(args,name) is not None and getattr(args,name+'_sha256') is not None,'SOURCE_ARGUMENTS')
            qualify(reader,args,software)
            summary,base,flags = source_packet(reader,args,'calibrate' if args.mode == 'controls' else 'solve')
            if args.mode == 'controls': outcome,status = replay_controls(reader,summary,base,out),CONTROLS_STATUS
            else: outcome,status = full(reader,args,summary,base,flags,out,software),FULL_STATUS
        reader.closing(); outputs = {}
        for name in sorted(inventory(out,budget)):
            digest = hashlib.sha256()
            with (out/name).open('rb') as handle:
                while True:
                    budget.tick(); block = handle.read(1024*1024)
                    if not block: break
                    digest.update(block)
            outputs[name] = digest.hexdigest()
        report = {'status':status,'implementation_version':1,'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),
            'producer':'/root/checkpoint_audit','verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
            'actual_executor_requires_external_receipt':True,'method':'independent_artifact_check','target_resolution':'NONE',
            'source_software':software,'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,
            'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'actual_target_input_read':args.mode == 'full',
            'producer_imports':0,'solver_calls':0,'graph_object_approved':False,'automatic_retry':False,'deadline':budget.tick(),
            'shared_components':['Pinned Native aggregateV2 reader/runtime/options/status helpers copied as explicit text ancestry',
                'Qualified468f/count37bc/pair ee9fa/capacity4f671/block910a are direct inherited immutable premises',
                'Independent unordered-pair rank and incidence-set model; dense neighbor-set witness equations and full SRG diagnostic',
                'Public rook geometry, exact JSON wire and first-stage vocabulary shared; no producer module/functions/AST/HiGHS/NumPy'],
            'limitations':['The1476-row relaxation omits exterior-pair CN equations and is necessary only',
                'Full SRG diagnostic is separately reported; any actual99 object requires Root independent object acceptance',
                'Absent or fractional incumbent remains UNKNOWN; no numerical status or engineering veto excludes counts or target',
                'Full authenticates own74 packet, replays all29 author actions and checks complete science; own74 actions are not rerun',
                'Status/closing guards are allocated reserve intent, not a hard-real-time theorem; actual SUP receipt is necessary',
                'Direct inherited premises only; no transitive Gram/count/pair proof/hash crawler or novelty/formal/external approval',
                'No automatic retry or Git/index/ledger mutation']}
        write(out/'summary.json',report,budget); reader.closing(); budget.tick()
        print(json.dumps({'status':status,'mode':args.mode}),flush=True)
    except Exception as exc:
        try:
            (out/'failure.json').write_text(json.dumps({'status':'FAILED_PRESERVED','stage':str(exc),'exception':type(exc).__name__,
                'inputs_sha256':reader.pins,'target_resolution':'NONE','infeasibility_inferred':False,'automatic_retry':False,
                'timestamp':datetime.now(timezone.utc).isoformat(),'deadline':budget.deadline.status()},indent=2,allow_nan=False)+'\n',encoding='utf8')
        except Exception: pass
        raise


if __name__ == '__main__': main()


