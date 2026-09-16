"""Independent provenance/model/numeric audit of fresh-star heuristic ranking.

This module never imports the ranking producer or a native domain producer.
Original-domain completeness remains a native claim until the later exhaustive
domain auditor runs. Numeric bounds here are not exact exclusion certificates.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[_name] = '1'
import argparse
from hashlib import sha256, file_digest
import json
import math
from pathlib import Path
import time

import numpy as np
from audit_certificate import full_graph
from star_marginal_cp_cpu_v2 import build_model, product_simplex_projection
from review_star_pdhg_gpu import parse_binary, bounds

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'rank_fresh_star_pdhg.py': '0feedea50f90a852d62a659e2e9e3979edf83756c9bd07af1e24db5ae50b8eea',
    'export_star_pdhg_binary.py': 'dd1ba00013e03cdaeb6f2c2ef20cf8ba0fc2a4e2f83f94ecdffd3720c16e740f',
    'audit_certificate.py': '22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d',
    'star_marginal_cp_cpu_v2.py': '6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d',
    'review_star_pdhg_gpu.py': '555e9595808d2e9045876c895d96845a2baad3d2f0773de65c9f745756ac0786',
    'star_domains.rs': 'b3637615352c0a5372fe7ed2237f34bc2d5c8773a892ee647c05acb772584d80',
    'build/star_domains.exe': 'e34d5081e1ce73ef68c47cd9dff2baa41046b7defbea8abe12c2126c5eb95f36',
    'star_domains_batch.rs': '84be679f31ae0fc365dc51a2b05a60d0467fa660c9c72a3572b3681da887c482',
    'build/star_domains_batch.exe': '6f14259f98cf47c2ffa11a7ea0b609cc494f710937468ad11ee318f2b35ae3dd',
    'star_pdhg_gpu.cu': '79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8',
    'build/star_pdhg_gpu.exe': '9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075',
}
METRICS = {'primal_upper_numeric', 'dual_lower_numeric', 'numeric_gap'}
SCALAR_TOLERANCE = 2e-6


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(name):
    return (ROOT / str(name).replace('\\', '/')).resolve()


def key(name):
    return path(name).relative_to(ROOT).as_posix()


def digest(name):
    with path(name).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def graph_key(edges):
    require(type(edges) is list and len(edges) == 168, 'Expected 168 outer edges')
    require(all(type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
                and 0 <= e[0] < e[1] < 84 for e in edges), 'Noncanonical outer edge')
    require(edges == sorted(edges) and len(set(map(tuple, edges))) == 168, 'Unsorted or repeated edge')
    return bytes(v for edge in edges for v in edge)


def validate_requested_indices(indices, family, excluded):
    """Explicit request is authoritative; exclude graphs, not merely indices."""
    require(type(indices) is list and 1 <= len(indices) <= 256
            and all(type(i) is int for i in indices) and len(set(indices)) == len(indices), 'Invalid request index list')
    require(family['status'] == 'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION'
            and family['selector'] == 'cross_3_4' and family['cycle_sizes'] == [3, 4], 'Unsupported fresh family')
    candidates = family['overlap_candidates']
    require(len(candidates) == len(family['moves']) == len(family['original_native_indices']) == family['legal_count'], 'Family inventory')
    keys = [graph_key(edges) for edges in candidates]
    require(len(set(keys)) == len(keys), 'Repeated exact family graph')
    require(all(0 <= i < len(keys) for i in indices), 'Request index out of bounds')
    excluded_keys = set()
    excluded_indices = []
    for index, candidate in excluded:
        require(type(index) is int and 0 <= index < len(keys), 'Bad excluded family index')
        signature = graph_key(candidate['overlap_edges_outer_zero_based'])
        require(signature == keys[index] and signature not in excluded_keys, 'Excluded candidate graph association')
        excluded_keys.add(signature)
        excluded_indices.append(index)
    require(len(excluded_keys) == 64 and len(set(excluded_indices)) == 64, 'All64 edge-LP candidates must be excluded')
    require(all(keys[i] not in excluded_keys for i in indices), 'Request reuses an edge-LP graph')
    return keys, sorted(excluded_indices)


def edge_hash(edges):
    return sha256(json.dumps(edges, separators=(',', ':')).encode('ascii')).hexdigest()


def reconstruct_cohort(score_by_index, moves, excluded_indices):
    """Independent batch-round formulation of the documented64+64 policy."""
    require(all(type(i) is int and 0 <= i < len(moves) and type(v) in (int, float)
                and math.isfinite(v) for i, v in score_by_index.items()), 'Nonfinite or malformed cohort score')
    eligible = sorted(set(score_by_index)-set(excluded_indices), key=lambda i: (score_by_index[i], i))
    require(len(eligible) >= 128, 'Fewer than128 fresh refined candidates')
    first = eligible[:64]
    strata = sorted({(moves[i]['root_group'], moves[i]['cycle_size']) for i in eligible[64:]})
    per_stratum = [[i for i in eligible[64:] if (moves[i]['root_group'], moves[i]['cycle_size']) == group] for group in strata]
    # Concatenate horizontal rounds through the sorted strata, stopping at64.
    second = [bucket[round_number] for round_number in range(max(map(len, per_stratum)))
              for bucket in per_stratum if round_number < len(bucket)][:64]
    require(len(second) == 64 and len(set(first+second)) == 128, 'Bad round-robin inventory')
    return first+second, {i: ['global_refined_upper'] if i in first else ['round_robin_root_group_cycle_size'] for i in first+second}, eligible


def verify_request(request, family, family_audit, read, bind):
    """Recompute request selection from its independent recovered edge audit."""
    require(request['status'] == 'EXPLICIT_FRESH_STAR_COHORT_REQUEST', 'Wrong request status')
    require(request['selection_policy'] == dict(name='64_GLOBAL_REFINED_UPPER_THEN64_ROUND_ROBIN_ROOT_SIZE',
            global_count=64, stratified_count=64, ordering='score,index; strata sorted(root_group,cycle_size)'), 'Unknown cohort policy')
    cp = read(request['original_search_path'])
    recovered = read(request['recovery_audit_path'])
    require(cp['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED' and cp['producer_version'] == 'cross1', 'Wrong original edge search')
    require(recovered['status'] == 'INDEPENDENT_CP_CROSS_REPAIRED_LP_AUDIT_PASS' and recovered['audited_producer_version'] == 'cross1'
            and recovered['independent_LP_audit_tolerance'] == 1e-7, 'Wrong independent recovery audit')
    closure = {key(p): h for p, h in recovered['inputs_sha256'].items()}
    require(closure.get('acceleration/audit_cp_cross_recovery.py') == '3a3e0c93d540982248254d87a3de753d8171be0081b6a7c82a4a7b89187721c8', 'Recovery auditor pin')
    require(key(recovered['original_summary_path']) == key(request['original_search_path'])
            and recovered['original_summary_sha256'] == bind(request['original_search_path']), 'Recovery/original association')
    effective = read(recovered['effective_summary_path'])
    require(bind(recovered['effective_summary_path']) == recovered['effective_summary_sha256'], 'Recovery view changed')
    require([r['proposal_index'] for r in cp['records']] == [r['proposal_index'] for r in effective['records']]
            and len(cp['records']) == 64, 'Recovery inventory differs')
    manifest_path = path(request['original_search_path']).with_name('manifest.json')
    manifest = read(manifest_path)
    family_sha = bind(request['family_path'], request['family_sha256'])
    require(closure.get(key(manifest_path)) == bind(manifest_path), 'Unaudited search manifest')
    require(key(cp['paths']['native']) == key(request['family_path'])
            and key(cp['paths']['family_audit']) == key(request['family_audit_path'])
            and closure.get(key(request['family_path'])) == family_sha
            and recovered['family_association']['native_sha256'] == family_sha, 'Recovered family differs')
    require(family_audit['status'] == 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS'
            and family_audit['all_original_native_indices_and_final_graphs_checked'] is True
            and family_audit['all_cycles_min_vertex_removed_first_checked'] is True, 'Family proof scope')
    require({key(p): h for p, h in family_audit['inputs_sha256'].items()}.get(key(request['family_path'])) == family_sha
            and family_audit['legal_count'] == family['legal_count'], 'Family proof association')
    excluded = []
    for row in cp['records']:
        candidate = read(row['candidate_path'])
        bind(row['candidate_path'], row['candidate_sha256'])
        require(closure.get(key(row['candidate_path'])) == row['candidate_sha256'], 'Unaudited CP candidate')
        excluded.append((row['proposal_index'], candidate))
    keys, current_indices = validate_requested_indices(request['indices'], family, excluded)
    base = read(family['candidate_path'])
    bind(family['candidate_path'], family['candidate_sha256'])
    old_keys = {graph_key(base['overlap_edges_outer_zero_based'])}
    for row in manifest['previous_candidates']:
        candidate = read(row['candidate_path'])
        bind(row['candidate_path'], row['candidate_sha256'])
        edges = candidate['overlap_edges_outer_zero_based']
        require(edge_hash(edges) == row['overlap_edges_sha256'], 'Prior graph signature mismatch')
        old_keys.add(graph_key(edges))
    old_keys.update(keys[i] for i in current_indices)
    excluded_all = [i for i, signature in enumerate(keys) if signature in old_keys]
    require(request['excluded_family_indices'] == excluded_all and request['previous_or_CP_graphs_excluded'] is True, 'Prior/current exclusion scope')
    stage = read(request['refined_stage_path'])
    require(key(request['refined_stage_path']) == key(path(request['original_search_path']).with_name('refined_stage.json'))
            and closure.get(key(request['refined_stage_path'])) == bind(request['refined_stage_path']), 'Unbound refined stage')
    gpu = read(stage['gpu_output_path'])
    bind(stage['gpu_output_path'], stage['gpu_output_sha256'])
    require(closure.get(key(stage['gpu_output_path'])) == stage['gpu_output_sha256'], 'Unbound refined GPU output')
    indices = stage['proposal_indices']
    require(stage['stage'] == 'refined' and stage['steps'] == 2000 and len(indices) == len(gpu['results']) == 2049
            and indices[0] is None and len(set(indices[1:])) == 2048, 'Refined inventory')
    scores = {}
    for j, (index, result) in enumerate(zip(indices, gpu['results'])):
        require(result['candidate_index'] == j and len(result['checkpoints']) == 1, 'Refined candidate order')
        point = result['checkpoints'][0]
        require(point['iterations'] == 2000, 'Refined iteration count')
        values = [result['initial']['primal_upper'], point['last']['primal_upper'], point['average']['primal_upper']]
        require(all(type(v) in (int, float) and math.isfinite(v) for v in values)
                and math.isfinite(point['best_upper']) and abs(point['best_upper']-min(values)) < 1e-10, 'Refined finite score')
        if index is not None:
            require(type(index) is int and 0 <= index < len(keys), 'Refined family index')
            scores[index] = min(values)
    selected, roles, eligible = reconstruct_cohort(scores, family['moves'], excluded_all)
    require(request['indices'] == selected and request['eligible_refined_count'] == len(eligible), 'Requested cohort selection differs')
    expected = [dict(proposal_index=i, roles=roles[i], refined_upper=scores[i], root_group=family['moves'][i]['root_group'],
                     cycle_size=family['moves'][i]['cycle_size'], original_native_index=family['original_native_indices'][i],
                     overlap_edges_sha256=edge_hash(family['overlap_candidates'][i])) for i in selected]
    require(request['records'] == expected, 'Request record/order/score/role differs')
    counts_by_root = {str(group): sum(family['moves'][i]['root_group'] == group for i in selected)
                      for group in sorted({family['moves'][i]['root_group'] for i in selected})}
    require(request['count_by_root_group'] == counts_by_root and request['LP_or_domain_or_GPU_runs'] == 0
            and request['graph_exclusions_claimed'] == 0 and request['exhaustive_family_evaluation_claimed'] is False, 'Request scope/count differs')
    return dict(selected_indices=selected, excluded_CP_indices=current_indices, excluded_family_indices=excluded_all,
                eligible_refined_count=len(eligible), selection_policy=request['selection_policy'])


def inspect_domains(document):
    """Validate native table structure, not independently prove completeness."""
    require(document['backend'] == 'rust', 'Unexpected domain backend')
    rows = document['domains']
    require(type(rows) is list and len(rows) <= 84 and [r['outer_vertex'] for r in rows] == list(range(len(rows))), 'Native vertex order')
    complete = document['complete_domain_enumeration']
    require(type(complete) is bool, 'Invalid completeness flag')
    counts = []
    for row in rows:
        require(row['status'] in ('COMPLETE', 'INCOMPLETE'), 'Unknown vertex status')
        require((row['status'] == 'COMPLETE') == (row['cap_reason'] is None), 'Vertex cap status differs')
        if row['status'] == 'INCOMPLETE':
            require(row['cap_reason'] in ('TIME_CAP', 'GLOBAL_NODE_CAP', 'PER_VERTEX_DOMAIN_CAP'), 'Unknown native cap')
        masks = [int(v, 16) for v in row['domain_masks_hex']]
        require(masks == sorted(set(masks)) and all(0 <= m < 1 << 84 and m.bit_count() == 8 for m in masks), 'Malformed or unordered native masks')
        counts.append(len(masks))
    require(complete == (len(rows) == 84 and all(r['status'] == 'COMPLETE' for r in rows)), 'Native completeness flag differs from rows')
    if complete:
        require(len(rows) == 84 and all(r['status'] == 'COMPLETE' for r in rows), 'Incomplete original table marked complete')
        require(document['status'] in ('COMPLETE_DOMAINS_RECIPROCITY_EMPTY_DOMAIN',
                                       'COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY'), 'Complete native status differs')
    else:
        require(document['status'] == 'INCOMPLETE' and 'propagation' not in document, 'Capped tables used as complete')
    return complete, counts


def compare_model(expected, parsed):
    """All CSR coefficients/indices and targets must agree exactly."""
    require(parsed['Q'] == 1680 and expected['A'].shape[0] == 5166, 'Model row coordinates')
    require(np.array_equal(expected['offsets'], parsed['offsets']) and np.array_equal(expected['b'], parsed['b']), 'Model target/offset mismatch')
    comparisons = 0
    for name in ('A', 'AT'):
        matrix = expected[name].copy()
        matrix.sum_duplicates()
        matrix.sort_indices()
        actual = parsed[name]
        require(matrix.shape == actual.shape, 'CSR shape mismatch')
        for field in ('indptr', 'indices', 'data'):
            left, right = getattr(matrix, field), getattr(actual, field)
            require(np.array_equal(left, right), 'CSR ' + name + '/' + field + ' mismatch')
            comparisons += len(left)
    return comparisons + len(parsed['b']) + len(parsed['offsets'])


def inspect_gpu_result(result, index, model, checkpoints):
    shape = dict(candidate_index=index, n_variables=model['A'].shape[1], n_rows=5166,
                 n_equalities=1680, domain_counts=np.diff(model['offsets']).tolist())
    require(all(type(result[k]) is int for k in ('candidate_index', 'n_variables', 'n_rows', 'n_equalities'))
            and all(type(v) is int for v in result['domain_counts'])
            and all(result[k] == v for k, v in shape.items()), 'GPU candidate/model order mismatch')
    require([p['iterations'] for p in result['checkpoints']] == checkpoints, 'GPU checkpoints mismatch')
    upper, lower = result['initial']['primal_upper_numeric'], result['initial']['dual_lower_numeric']
    for values in [result['initial']] + [p[t] for p in result['checkpoints'] for t in ('last', 'average')]:
        require(set(values) == METRICS and all(type(v) in (float, int) and math.isfinite(v) for v in values.values()), 'Nonfinite/invalid scalar schema')
        require(abs(values['numeric_gap'] - (values['primal_upper_numeric']-values['dual_lower_numeric'])) <= 1e-10, 'Scalar gap differs')
        require(values['primal_upper_numeric'] >= -1e-10 and values['dual_lower_numeric'] <= values['primal_upper_numeric'] + 1e-7, 'Inconsistent numerical interval')
    for point in result['checkpoints']:
        upper = min(upper, point['last']['primal_upper_numeric'], point['average']['primal_upper_numeric'])
        lower = max(lower, point['last']['dual_lower_numeric'], point['average']['dual_lower_numeric'])
        require(point['best_upper_numeric'] == upper and point['best_lower_numeric'] == lower, 'Best checkpoint scope differs')


def replay_cpu(model, checkpoints):
    """Cold recurrence on independently parsed canonical CSR, no model solver."""
    counts = np.diff(model['offsets'])
    p = np.repeat(1. / counts, counts)
    bar = p.copy()
    y = np.zeros(model['A'].shape[0])
    pa, ya = np.zeros_like(p), np.zeros_like(y)
    lower = np.r_[np.full(model['Q'], -1.), np.zeros(len(y)-model['Q'])]
    initial = bounds(model, p, y)
    best_upper, best_lower = initial['primal_upper_numeric'], initial['dual_lower_numeric']
    points = []
    for iteration in range(1, checkpoints[-1]+1):
        newy = np.clip(y+model['sigma']*(model['A']@bar-model['b']), lower, 1.)
        newp = product_simplex_projection(p-model['tau']*(model['AT']@newy), model['offsets'])
        bar, p, y = 2*newp-p, newp, newy
        pa += (p-pa)/iteration
        ya += (y-ya)/iteration
        if iteration in checkpoints:
            last, average = bounds(model, p, y), bounds(model, pa, ya)
            best_upper = min(best_upper, last['primal_upper_numeric'], average['primal_upper_numeric'])
            best_lower = max(best_lower, last['dual_lower_numeric'], average['dual_lower_numeric'])
            points.append(dict(iterations=iteration, last=last, average=average,
                               best_upper_numeric=best_upper, best_lower_numeric=best_lower))
    return dict(initial=initial, checkpoints=points)


def compare_cpu(cpu, gpu):
    differences = [abs(cpu['initial'][k]-gpu['initial'][k]) for k in METRICS]
    require(len(cpu['checkpoints']) == len(gpu['checkpoints']), 'CPU checkpoint count')
    for left, right in zip(cpu['checkpoints'], gpu['checkpoints']):
        require(left['iterations'] == right['iterations'], 'CPU checkpoint mismatch')
        differences += [abs(left[t][k]-right[t][k]) for t in ('last', 'average') for k in METRICS]
        differences += [abs(left[k]-right[k]) for k in ('best_upper_numeric', 'best_lower_numeric')]
    require(all(math.isfinite(v) and v <= SCALAR_TOLERANCE for v in differences), 'Independent CPU/GPU scalar mismatch')
    return dict(scalar_comparisons=len(differences), maximum_absolute_error=max(differences), absolute_tolerance=SCALAR_TOLERANCE)


def evaluation_selection(upper_order, lower_order, count, mode):
    """Ordered union of top halves, then upper-fill; duplicate roles retained."""
    require(count in (8, 16) and mode in ('upper', 'union'), 'Unsupported downstream selection')
    require(len(set(upper_order)) == len(upper_order) and len(set(lower_order)) == len(lower_order)
            and set(upper_order) == set(lower_order), 'Ranking inventory mismatch')
    selected, roles = [], {}
    def add(index, role):
        if index not in roles:
            roles[index] = []
            selected.append(index)
        if role not in roles[index]:
            roles[index].append(role)
    if mode == 'upper':
        for index in upper_order[:count]:
            add(index, 'upper')
    else:
        for index in upper_order[:count//2]:
            add(index, 'upper')
        for index in lower_order[:count//2]:
            add(index, 'lower')
        for index in upper_order:
            if len(selected) >= count:
                break
            if index not in roles:
                add(index, 'upper_fill')
    return [dict(proposal_index=i, selection_roles=roles[i]) for i in selected]


def audit_ranking(summary_path, cpu_controls=3):
    require(cpu_controls in (0, 3), 'Choose zero or three CPU controls')
    bindings = {}
    def bind(name, expected=None):
        label = key(name)
        if label not in bindings:
            bindings[label] = digest(name)
        require(expected is None or bindings[label] == expected, 'Changed bound file: ' + label)
        return bindings[label]
    def read(name):
        bind(name)
        document = json.loads(path(name).read_bytes())
        require(type(document) is dict, 'JSON object required')
        for field in ('inputs_sha256', 'outputs_sha256'):
            for filename, expected in document.get(field, {}).items():
                bind(filename, expected)
        return document
    for name, expected in PINS.items():
        bind(ROOT/'acceleration'/name, expected)
    bind(__file__)
    summary = read(summary_path)
    require(summary['status'] == 'NUMERICAL_FRESH_STAR_PDHG_RANKING_FINISHED'
            and summary['producer_version'] == 'fresh1', 'Unfinished or unsupported ranking')
    require(summary['iterations'] == 500, 'This audit/control protocol is fixed at500 steps')
    require(summary['numerical_scores_are_proofs'] is False and summary['independently_audited_original_domains'] is False
            and summary['pair_pruned_domains_used'] is False and summary['original_complete_domains_used'] is True
            and summary['candidates_pruned'] == summary['exclusions_claimed'] == summary['LP_runs'] == 0, 'Ranking scope overstated')
    manifest = read(summary['manifest_path'])
    bind(summary['manifest_path'], summary['manifest_sha256'])
    require(manifest['status'] == 'FRESH_STAR_PDHG_RANKING_INPUTS_BOUND'
            and manifest['scores_are_proofs'] is False and manifest['independently_audited_original_domains'] is False, 'Ranking manifest scope')
    for field in ('family', 'family_audit', 'request', 'native_input'):
        require(key(manifest[field+'_path']) == key(summary[field+'_path'])
                and manifest[field+'_sha256'] == summary[field+'_sha256'] == bind(summary[field+'_path']), 'Manifest/summary association: ' + field)
    family, family_audit, request = [read(summary[field+'_path']) for field in ('family', 'family_audit', 'request')]
    for field in ('family', 'family_audit'):
        require(key(request[field+'_path']) == key(summary[field+'_path']) and request[field+'_sha256'] == summary[field+'_sha256'], 'Request/family association')
    selection = verify_request(request, family, family_audit, read, bind)
    indices = selection['selected_indices']
    require(summary['input_selected_indices'] == manifest['input_selected_indices'] == indices
            and summary['requested_count'] == len(summary['records']) == len(indices), 'Rank request inventory/order')
    caps = dict(seconds=1.0, global_nodes=2000000, per_vertex_domains=20000)
    limits = dict(chunk_count=32, N=100000, M=20000, blocks=128, domain=8192,
                  nnz=8000000, total_N=2000000, total_M=1000000, total_nnz=64000000, binary_bytes=2**31)
    require(manifest['native_caps'] == caps and manifest['GPU_limits'] == limits and manifest['iterations'] == 500, 'Execution caps changed')
    command = manifest['native_command']
    require(len(command) == 6 and key(command[0]) == 'acceleration/build/star_domains_batch.exe'
            and key(command[1]) == key(summary['native_input_path']) and key(command[2]) == key(summary['native_output_path'])
            and [float(command[3]), int(command[4]), int(command[5])] == [1., 2000000, 20000], 'Native command/caps')
    tokens = path(summary['native_input_path']).read_text(encoding='ascii').split()
    require(tokens[:2] == ['C99OVERLAPS1', str(len(indices))]
            and list(map(int, tokens[2:])) == [v for i in indices for edge in family['overlap_candidates'][i] for v in edge], 'Native input graph/order differs')
    native = read(summary['native_output_path'])
    bind(summary['native_output_path'], summary['native_output_sha256'])
    require(native['candidate_count'] == len(native['results']) == len(indices) and native['caps_reset_per_candidate'] is True, 'Native batch inventory/caps')
    normalized, documents, expected_available = [], {}, []
    for position, (index, row, native_row) in enumerate(zip(indices, summary['records'], native['results'])):
        require(row['proposal_index'] == index and row['native_result_index'] == position
                and row['original_native_index'] == family['original_native_indices'][index]
                and row['root_group'] == family['moves'][index]['root_group'] and row['cycle_size'] == family['moves'][index]['cycle_size']
                and row['input_roles'] == request['records'][position]['roles'], 'Record/native/geometry mapping')
        candidate, domains = read(row['candidate_path']), read(row['domains_path'])
        bind(row['candidate_path'], row['candidate_sha256']); bind(row['domains_path'], row['domains_sha256'])
        require(graph_key(candidate['overlap_edges_outer_zero_based']) == graph_key(family['overlap_candidates'][index])
                and row['overlap_edges_sha256'] == edge_hash(family['overlap_candidates'][index]), 'Materialized candidate graph differs')
        require(candidate['proposal_index'] == index and candidate['original_native_index'] == row['original_native_index']
                and key(candidate['family_path']) == key(summary['family_path']) and candidate['family_sha256'] == summary['family_sha256'], 'Candidate provenance differs')
        full_graph(candidate)
        require(domains == native_row and domains['caps'] == caps and row['native_caps'] == caps, 'Original native masks/caps were changed')
        complete, counts = inspect_domains(domains)
        require(row['domain_counts'] == counts and row['complete_domain_enumeration'] == complete and row['native_status'] == domains['status']
                and row['native_total_nodes'] == domains['total_nodes']
                and row['native_reciprocity_status'] == domains.get('propagation', {}).get('status'), 'Native record summary differs')
        reason = 'INCOMPLETE_NATIVE_DOMAINS' if not complete else 'EMPTY_ORIGINAL_DOMAIN' if not all(counts) else None
        if reason is None and (max(counts) > 8192 or sum(counts) > 100000):
            reason = 'UNSUPPORTED_GPU_DOMAIN_OR_VARIABLE_LIMIT'
        if reason is None and row['unavailable_reason'] == 'UNSUPPORTED_GPU_NNZ_LIMIT':
            check_model = build_model(candidate, domains['domains'])
            require(check_model['A'].nnz > 8000000, 'Unsupported-nnz claim is false')
            del check_model
            reason = 'UNSUPPORTED_GPU_NNZ_LIMIT'
        available = reason is None
        require(row['status'] == ('NUMERICALLY_SCORED' if available else 'UNAVAILABLE') and row['unavailable_reason'] == reason, 'Availability/cap classification differs')
        if available:
            require(type(row['chunk_index']) is int and type(row['binary_candidate_index']) is int, 'Missing chunk index')
            expected_available.append(index)
        else:
            require(all(row[k] is None for k in ('chunk_index', 'binary_candidate_index', 'best_lower_numeric', 'best_upper_numeric')), 'Unavailable candidate acquired a score')
        normalized.append(dict(proposal_index=index, original_native_index=row['original_native_index'],
            candidate_path=key(row['candidate_path']), candidate_sha256=row['candidate_sha256'],
            domains_path=key(row['domains_path']), domains_sha256=row['domains_sha256'], available=available,
            status=row['status'], reason=reason, best_upper_numeric=row['best_upper_numeric'], best_lower_numeric=row['best_lower_numeric'],
            native_result_index=position, chunk_index=row['chunk_index'], binary_candidate_index=row['binary_candidate_index']))
        documents[index] = (candidate, domains)
    by_index = {r['proposal_index']: r for r in normalized}
    control_indices = [] if not cpu_controls else list(dict.fromkeys(expected_available[j] for j in (0, len(expected_available)//2, len(expected_available)-1))) if expected_available else []
    controls, checked_indices, scalar_initial_errors = [], [], []
    array_entries = 0
    for chunk_index, chunk in enumerate(summary['chunks']):
        require(chunk['chunk_index'] == chunk_index, 'Chunk ordering')
        chunk_manifest = read(chunk['manifest_path']); bind(chunk['manifest_path'], chunk['manifest_sha256'])
        bind(chunk['input_path'], chunk['input_sha256'])
        gpu = read(chunk['gpu_output_path']); bind(chunk['gpu_output_path'], chunk['gpu_output_sha256'])
        require(chunk_manifest['status'] == 'NATIVE_ORIGINAL_STAR_PDHG_CHUNK_EXPORTED'
                and chunk_manifest['chunk_index'] == chunk_index and chunk_manifest['original_complete_domains_used'] is True
                and chunk_manifest['pair_pruned_domains_used'] is False and chunk_manifest['independently_audited_original_domains'] is False, 'Chunk domain scope')
        require(key(chunk_manifest['binary_path']) == key(chunk['input_path']) and chunk_manifest['binary_sha256'] == chunk['input_sha256'], 'Chunk binary binding')
        require([key(p) for p in chunk['gpu_command']] == ['acceleration/build/star_pdhg_gpu.exe', key(chunk['input_path']), key(chunk['gpu_output_path'])], 'GPU command differs')
        checks, models = parse_binary(chunk['input_path'])
        cases = chunk_manifest['cases']
        require(checks == chunk_manifest['checkpoints'] == [500] and len(models) == len(cases) == len(chunk['proposal_indices']) == chunk_manifest['candidate_count']
                and 1 <= len(models) <= 32, 'Chunk candidate/checkpoint count')
        require(path(chunk['input_path']).stat().st_size == chunk_manifest['binary_bytes'] <= 2**31, 'Chunk bytes')
        require(gpu['status'] == 'NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED' and gpu['candidate_count'] == len(gpu['results']) == len(models)
                and gpu['eta'] == .9 and gpu['theta'] == 1 and gpu['float_type'] == 'float64'
                and gpu['initialization'] == 'uniform_per_simplex_probability_zero_dual'
                and gpu['best_scope'] == 'initial_and_requested_checkpoint_last_and_average'
                and gpu['numerical_scores_are_proofs'] is False and gpu['scalar_metrics_computed_on_host'] is True, 'GPU header/scope')
        aggregate = [0, 0, 0]
        for position, (case, parsed, gpu_result, index) in enumerate(zip(cases, models, gpu['results'], chunk['proposal_indices'])):
            require(index in by_index and by_index[index]['available'] and index not in checked_indices, 'Unexpected/repeated chunk candidate')
            row = by_index[index]
            require(case['index'] == position and case['proposal_index'] == index and case['native_result_index'] == row['native_result_index']
                    and case['original_native_index'] == row['original_native_index']
                    and row['chunk_index'] == chunk_index and row['binary_candidate_index'] == position, 'Case/binary/summary mapping')
            for field in ('candidate_path', 'candidate_sha256', 'domains_path', 'domains_sha256'):
                require(case[field] == row[field], 'Case input binding differs')
            require(case['record_byte_offset'] == parsed['start'] and case['record_sha256'] == parsed['record_sha256']
                    and case['byte_length'] == parsed['end']-parsed['start'], 'Record byte identity')
            require((case['N'], case['M'], case['Q'], case['blocks'], case['nnz']) ==
                    (parsed['A'].shape[1], 5166, 1680, 84, parsed['A'].nnz), 'Case dimensions')
            require(case['offsets'] == parsed['offsets'].tolist() and case['domain_counts'] == np.diff(parsed['offsets']).tolist(), 'Case original domain counts')
            require(case['canonical_sorted_unique_CSR'] is True and case['exact_transpose'] is True
                    and case['eta'] == .9 and case['theta'] == 1, 'Case numerical convention')
            arrays = [('offsets', parsed['offsets'], '<u4'), ('A_rowptr', parsed['A'].indptr, '<u4'),
                      ('A_indices', parsed['A'].indices, '<u4'), ('A_values', parsed['A'].data, '<f8'),
                      ('AT_rowptr', parsed['AT'].indptr, '<u4'), ('AT_indices', parsed['AT'].indices, '<u4'),
                      ('AT_values', parsed['AT'].data, '<f8'), ('b', parsed['b'], '<f8')]
            cursor = 20
            for name, values, dtype in arrays:
                payload = np.asarray(values, dtype=dtype).tobytes()
                require(case['arrays'][name] == dict(relative_byte_offset=cursor, byte_length=len(payload),
                        sha256=sha256(payload).hexdigest(), dtype=dtype), 'Case array hash/position differs')
                cursor += len(payload)
            require(cursor == case['byte_length'], 'Case byte size')
            require(case['block_tau'] == [float(parsed['tau'][i]) for i in parsed['offsets'][:-1]]
                    and case['sigma_f64le_sha256'] == sha256(np.asarray(parsed['sigma'], dtype='<f8').tobytes()).hexdigest(), 'Case diagonal steps differ')
            candidate, domains = documents[index]
            model = build_model(candidate, domains['domains'])
            array_entries += compare_model(model, parsed)
            del model
            inspect_gpu_result(gpu_result, position, parsed, [500])
            initial = bounds(parsed, np.repeat(1./np.diff(parsed['offsets']), np.diff(parsed['offsets'])), np.zeros(5166))
            error = max(abs(initial[k]-gpu_result['initial'][k]) for k in METRICS)
            require(error <= 2e-8, 'Cold initial scalar mismatch')
            scalar_initial_errors.append(error)
            point = gpu_result['checkpoints'][0]
            require(row['best_upper_numeric'] == point['best_upper_numeric'] and row['best_lower_numeric'] == point['best_lower_numeric'], 'Ranking/GPU score differs')
            if index in control_indices:
                controls.append(dict(proposal_index=index, chunk_index=chunk_index, binary_candidate_index=position,
                                     iterations=500, **compare_cpu(replay_cpu(parsed, [500]), gpu_result)))
            aggregate = [a+b for a, b in zip(aggregate, (case['N'], case['M'], case['nnz']))]
            checked_indices.append(index)
        require(aggregate == [chunk_manifest['aggregate_N'], chunk_manifest['aggregate_M'], chunk_manifest['aggregate_nnz']], 'Chunk aggregate accounting')
        del models
        print(json.dumps(dict(audit_chunk_finished=chunk_index, models_checked=len(checked_indices),
                              numeric_cpu_controls=len(controls))), flush=True)
    require(checked_indices == expected_available, 'Missing/reordered complete available inventory')
    upper_order = sorted(expected_available, key=lambda i: (by_index[i]['best_upper_numeric'], i))
    lower_order = sorted(expected_available, key=lambda i: (by_index[i]['best_lower_numeric'], i))
    require(all(type(v) is int for field in ('ranked_by_upper', 'ranked_by_lower') for v in summary[field])
            and summary['ranked_by_upper'] == upper_order and summary['ranked_by_lower'] == lower_order, 'Deterministic scalar ordering differs')
    require(summary['scored_count'] == len(expected_available) and summary['unavailable_count'] == len(indices)-len(expected_available), 'Availability totals')
    reasons = {}
    for row in normalized:
        if not row['available']:
            reasons[row['reason']] = reasons.get(row['reason'], 0)+1
    require(summary['unavailable_counts'] == reasons, 'Unavailable reason accounting')
    require([r['proposal_index'] for r in controls] == control_indices, 'CPU control inventory')
    require(all(digest(p) == h for p, h in bindings.items()), 'Input changed during audit')
    return dict(status='INDEPENDENT_FRESH_STAR_PDHG_RANKING_AUDIT_PASS', inputs_sha256=bindings,
        ranking_summary_path=key(summary_path), ranking_summary_sha256=bind(summary_path),
        family_path=key(summary['family_path']), family_sha256=summary['family_sha256'],
        family_audit_path=key(summary['family_audit_path']), family_audit_sha256=summary['family_audit_sha256'],
        selection_request_path=key(summary['request_path']), selection_request_sha256=summary['request_sha256'],
        input_selected_indices=indices, request_selection_audit=selection, records=normalized,
        ranked_by_upper_indices=upper_order, ranked_by_lower_indices=lower_order,
        evaluation_selections={f'{mode}_{n}': evaluation_selection(upper_order, lower_order, n, mode) for mode in ('upper', 'union') for n in (8, 16)},
        unavailable_indices=[r['proposal_index'] for r in normalized if not r['available']], unavailable_reasons=reasons,
        all_serialized_models_reconstructed=True, reconstructed_model_count=len(checked_indices), exact_compared_array_entries=array_entries,
        maximum_initial_scalar_error=max(scalar_initial_errors, default=0.), numeric_cpu_controls=controls,
        CPU_control_policy='First, middle and last available model in original request order; exactly500 cold iterations.',
        producer_or_native_imported=False, independent_domain_enumeration_performed=False,
        native_domain_completeness_independently_verified=False, all_original_native_masks_preserved=True,
        LP_runs=0, GPU_runs=0, native_domain_runs=0, exclusions_claimed=0, numerical_scores_are_proofs=False,
        scope='Candidate, request policy, original-mask and exact serialized-model associations plus sampled CPU numerical parity. Complete native domains remain source/status claims until independently enumerated for any later exact certificate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cpu-controls', type=int, choices=(0, 3), default=3)
    args = parser.parse_args()
    require(not path(args.out).exists(), 'Preserve previous audit')
    started = time.perf_counter()
    result = audit_ranking(args.ranking, args.cpu_controls)
    result['elapsed_seconds'] = time.perf_counter()-started
    with path(args.out).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], requested=len(result['records']), models=result['reconstructed_model_count'],
                         cpu_controls=len(result['numeric_cpu_controls']), elapsed_seconds=result['elapsed_seconds'], sha256=digest(args.out))))


if __name__ == '__main__':
    main()
