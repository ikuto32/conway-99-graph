"""Small semantic corruption controls for the independent fresh-ranking audit.

Uses synthetic graph-shaped records and sparse toy matrices only; it performs
no domain enumeration, LP solve, GPU run, or scientific candidate evaluation.
"""
import argparse
import copy
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
import audit_fresh_star_ranking as audit


def controls():
    checks = []
    def positive(name, operation):
        operation()
        checks.append(dict(name=name, expected='ACCEPT', result='PASS'))
    def negative(name, operation):
        try:
            operation()
        except (ValueError, KeyError, IndexError, TypeError, AssertionError) as error:
            checks.append(dict(name=name, expected='REJECT', result='PASS', rejection=str(error)))
        else:
            raise AssertionError('Corruption accepted: ' + name)
    def equal(actual, expected):
        audit.require(actual == expected, 'Unexpected independently specified result')

    edges = [list(e) for e in combinations(range(84), 2)]
    graphs = [edges[:167] + [edges[167+i]] for i in range(66)]
    family = dict(status='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION', selector='cross_3_4', cycle_sizes=[3, 4],
                  overlap_candidates=graphs, moves=[{} for _ in graphs], original_native_indices=list(range(66)), legal_count=66)
    excluded = [(i, dict(overlap_edges_outer_zero_based=graphs[i])) for i in range(64)]
    positive('two_request_indices_outside_all64_exact_graphs', lambda: equal(audit.validate_requested_indices([65, 64], family, excluded)[1], list(range(64))))
    for name, indices in [('duplicate', [64, 64]), ('reused_edge_LP_graph', [63]), ('negative', [-1]),
                           ('outside', [66]), ('bool', [True]), ('empty', []), ('too_many', list(range(257)))]:
        negative('request_' + name, lambda indices=indices: audit.validate_requested_indices(indices, family, excluded))
    for name, mutate in [
        ('family_count', lambda f: f.update(legal_count=65)),
        ('family_selector', lambda f: f.update(selector='both')),
        ('family_status', lambda f: f.update(status='PARTIAL')),
        ('duplicate_exact_family_graph', lambda f: f['overlap_candidates'].__setitem__(65, f['overlap_candidates'][64])),
        ('noncanonical_edge', lambda f: f['overlap_candidates'][65].__setitem__(0, [1, 0])),
    ]:
        changed = copy.deepcopy(family)
        mutate(changed)
        negative(name, lambda changed=changed: audit.validate_requested_indices([64], changed, excluded))
    negative('incomplete_edge_LP_exclusion_inventory', lambda: audit.validate_requested_indices([64], family, excluded[:-1]))
    changed_excluded = copy.deepcopy(excluded)
    changed_excluded[0] = (0, dict(overlap_edges_outer_zero_based=graphs[1]))
    negative('edge_LP_candidate_graph_mismatch', lambda: audit.validate_requested_indices([64], family, changed_excluded))

    scores = {i: 0. for i in range(200)}
    moves = [dict(root_group=0 if i < 160 else 1, cycle_size=3) for i in range(200)]
    expected = list(range(64)) + [i for pair in zip(range(64, 96), range(160, 192)) for i in pair]
    positive('cohort_tie_break_and_horizontal_rounds', lambda: equal(audit.reconstruct_cohort(scores, moves, [])[0], expected))
    expected_excluded = list(range(10, 74)) + [i for pair in zip(range(74, 106), range(160, 192)) for i in pair]
    positive('cohort_exclusions_applied_before_global_stage', lambda: equal(audit.reconstruct_cohort(scores, moves, list(range(10)))[0], expected_excluded))
    negative('cohort_fewer_than128', lambda: audit.reconstruct_cohort({i: 0 for i in range(127)}, moves, []))
    negative('cohort_nonfinite_score', lambda: audit.reconstruct_cohort(scores | {0: float('nan')}, moves, []))

    upper = list(range(20))
    lower = [8, 9, 10, 11] + [i for i in upper if i not in (8, 9, 10, 11)]
    positive('union_disjoint_halves_order', lambda: equal([r['proposal_index'] for r in audit.evaluation_selection(upper, lower, 8, 'union')], [0, 1, 2, 3, 8, 9, 10, 11]))
    positive('union_overlap_fill_order_and_roles', lambda: equal(audit.evaluation_selection(upper, upper, 8, 'union'),
        [dict(proposal_index=i, selection_roles=['upper', 'lower'] if i < 4 else ['upper_fill']) for i in range(8)]))
    positive('upper_selection', lambda: equal(audit.evaluation_selection(upper, lower, 8, 'upper'),
        [dict(proposal_index=i, selection_roles=['upper']) for i in range(8)]))
    positive('insufficient_available_inventory_is_explicit', lambda: equal([r['proposal_index'] for r in audit.evaluation_selection([2, 4], [4, 2], 16, 'union')], [2, 4]))
    positive('zero_available_inventory_is_explicit', lambda: equal(audit.evaluation_selection([], [], 8, 'upper'), []))
    negative('rank_duplicate', lambda: audit.evaluation_selection([1, 1], [1], 8, 'union'))
    negative('rank_inventory_difference', lambda: audit.evaluation_selection([1], [2], 8, 'union'))
    negative('unsupported_selection_size', lambda: audit.evaluation_selection(upper, lower, 12, 'union'))

    domains = dict(backend='rust', complete_domain_enumeration=True,
        status='COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY',
        domains=[dict(outer_vertex=u, status='COMPLETE', cap_reason=None, domain_masks_hex=['0xff']) for u in range(84)])
    positive('native_complete_mask_structure_only', lambda: equal(audit.inspect_domains(domains), (True, [1]*84)))
    capped = dict(backend='rust', complete_domain_enumeration=False, status='INCOMPLETE',
        domains=[dict(outer_vertex=0, status='INCOMPLETE', cap_reason='GLOBAL_NODE_CAP', domain_masks_hex=[])])
    positive('capped_table_remains_incomplete', lambda: equal(audit.inspect_domains(capped), (False, [0])))
    for name, mutate in [
        ('native_backend', lambda d: d.update(backend='unknown')),
        ('native_false_complete', lambda d: d['domains'].pop()),
        ('native_vertex_order', lambda d: d['domains'][0].update(outer_vertex=1)),
        ('native_complete_with_cap', lambda d: d['domains'][0].update(cap_reason='NODE_CAP')),
        ('native_duplicate_mask', lambda d: d['domains'][0].update(domain_masks_hex=['0xff', '0xff'])),
        ('native_mask_width', lambda d: d['domains'][0].update(domain_masks_hex=[hex((1 << 84) | 0x7f)])),
        ('native_mask_weight', lambda d: d['domains'][0].update(domain_masks_hex=['0x7f'])),
        ('native_unknown_complete_status', lambda d: d.update(status='COMPLETE_DOMAINS_FAKE')),
    ]:
        changed = copy.deepcopy(domains)
        mutate(changed)
        negative(name, lambda changed=changed: audit.inspect_domains(changed))
    changed = copy.deepcopy(capped)
    changed['propagation'] = {}
    negative('propagation_after_cap', lambda: audit.inspect_domains(changed))

    A = csr_matrix(([1., -1.], ([0, 0], [0, 1])), shape=(5166, 2))
    model = dict(A=A, AT=A.transpose().tocsr(), b=np.zeros(5166), offsets=np.array([0, 1, 2]))
    parsed = dict(**model, Q=1680)
    positive('canonical_sparse_matrix_equal', lambda: audit.compare_model(model, parsed))
    for name, mutate in [
        ('wrong_target', lambda m: m['b'].__setitem__(1680, 1)),
        ('wrong_transpose_sign', lambda m: m['AT'].data.__setitem__(0, -1)),
        ('wrong_forward_coefficient', lambda m: m['A'].data.__setitem__(0, 2)),
        ('wrong_offsets', lambda m: m['offsets'].__setitem__(1, 0)),
        ('wrong_equality_count', lambda m: m.update(Q=1679)),
    ]:
        changed = copy.deepcopy(parsed)
        mutate(changed)
        negative(name, lambda changed=changed: audit.compare_model(model, changed))
    result = dict(candidate_index=0, n_variables=2, n_rows=5166, n_equalities=1680, domain_counts=[1, 1],
        initial=dict(primal_upper_numeric=2., dual_lower_numeric=0., numeric_gap=2.),
        checkpoints=[dict(iterations=500,
            last=dict(primal_upper_numeric=1., dual_lower_numeric=.5, numeric_gap=.5),
            average=dict(primal_upper_numeric=1.5, dual_lower_numeric=.25, numeric_gap=1.25),
            best_upper_numeric=1., best_lower_numeric=.5)])
    positive('GPU_scalar_shape_and_best_aggregation', lambda: audit.inspect_gpu_result(result, 0, parsed, [500]))
    positive('CPU_saved_scalar_parity', lambda: equal(audit.compare_cpu(result, result)['maximum_absolute_error'], 0.))
    for name, mutate in [
        ('GPU_wrong_candidate_index', lambda r: r.update(candidate_index=1)),
        ('GPU_boolean_candidate_index', lambda r: r.update(candidate_index=False)),
        ('GPU_wrong_domain_order', lambda r: r.update(domain_counts=[2, 0])),
        ('GPU_wrong_checkpoint', lambda r: r['checkpoints'][0].update(iterations=499)),
        ('GPU_nonfinite_score', lambda r: r['checkpoints'][0]['last'].update(primal_upper_numeric=float('nan'))),
        ('GPU_false_gap', lambda r: r['checkpoints'][0]['last'].update(numeric_gap=.25)),
        ('GPU_wrong_best_upper', lambda r: r['checkpoints'][0].update(best_upper_numeric=.25)),
        ('GPU_wrong_best_lower', lambda r: r['checkpoints'][0].update(best_lower_numeric=.75)),
    ]:
        changed = copy.deepcopy(result)
        mutate(changed)
        negative(name, lambda changed=changed: audit.inspect_gpu_result(changed, 0, parsed, [500]))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--request', required=True)
    args = parser.parse_args()
    out = audit.path(args.out)
    audit.require(not out.exists(), 'Preserve prior controls')
    checks = controls()
    sources = [Path(__file__), Path(audit.__file__)] + [audit.ROOT/'acceleration'/name for name in audit.PINS]
    bindings = {audit.key(p): audit.digest(p) for p in sources}
    def bind(name, expected=None):
        label = audit.key(name)
        if label not in bindings:
            bindings[label] = audit.digest(name)
        audit.require(expected is None or bindings[label] == expected, 'Changed request binding')
        return bindings[label]
    def read(name):
        bind(name)
        document = json.loads(audit.path(name).read_bytes())
        for filename, expected in document.get('inputs_sha256', {}).items():
            bind(filename, expected)
        return document
    for name, expected in audit.PINS.items():
        bind(audit.ROOT/'acceleration'/name, expected)
    request = read(args.request)
    request_review = audit.verify_request(request, read(request['family_path']), read(request['family_audit_path']), read, bind)
    result = dict(status='FRESH_STAR_RANKING_INDEPENDENT_AUDITOR_SEMANTIC_CONTROLS_PASS',
                  inputs_sha256=bindings, controls=checks, actual_request_audit=request_review,
                  positive_controls=sum(c['expected'] == 'ACCEPT' for c in checks),
                  negative_controls=sum(c['expected'] == 'REJECT' for c in checks),
                  numeric_controls_synthetic_only=True, native_domain_runs=0, LP_runs=0, GPU_runs=0,
                  numeric_CP_iterations=0, graph_completion_claimed=False,
                  scope='Synthetic auditor semantic guards and actual request selection-policy replay only; no fresh model/PDHG scientific run.')
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], positive=result['positive_controls'], negative=result['negative_controls'], sha256=audit.digest(out))))


if __name__ == '__main__':
    main()
