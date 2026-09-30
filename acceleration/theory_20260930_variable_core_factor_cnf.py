"""Arbitrary normalized triangle-core factor CNF and producer-only decoder."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package, save
from theory_20260930_variable_core_factor_preflight import calibrate

ROOT = Path(__file__).resolve().parents[1]
NORMALIZATION = ROOT/'acceleration/results/20260930_unrestricted_triangle_factor/summary.json'
NORMALIZATION_SHA = 'fecb50f01e6548c79e486068eeea3ca41dd6922ed4cf74686d9757ae0061b2eb'
PROOF = ROOT/'docs/DERIVATION_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md'
PROOF_SHA = 'a56495f0bc8794f014f670ab56741d769bc2f59ca2308e94b8baaa8f2dc71b17'
COVERAGE = ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json'
COVERAGE_SHA = 'a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd'


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def channel_controls():
    cases = 0
    for n in range(1, 5):
        for selected in range(n):
            for inputs in product((False, True), repeat=n):
                for output in (False, True):
                    clauses = [(k != selected or not inputs[k] or output) and
                               (k != selected or inputs[k] or not output) for k in range(n)]
                    assert all(clauses) == (output == inputs[selected])
                    cases += 1
    # With no selected entry, both outputs satisfy the implication clauses.
    assert all((True or not x or z) and (True or x or not z) for x, z in product((False, True), repeat=2))
    return {'status': 'PRODUCER_ONE_HOT_CHANNEL_CONTROLS_PASS', 'one_hot_input_output_cases': cases,
            'zero_selector_counterexample': 'Both output bits are allowed if no selector is true; exact-one row constraint is essential.',
            'independent_approval': False}


def build(args):
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    assert digest(NORMALIZATION) == NORMALIZATION_SHA and digest(PROOF) == PROOF_SHA
    assert digest(COVERAGE) == COVERAGE_SHA
    coverage = json.loads(COVERAGE.read_bytes())
    assert coverage['status'] == 'INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS'
    paths = [Path(__file__), Path(__file__).with_name('theory_20260930_variable_core_factor_cnf_spec.md'),
             NORMALIZATION, PROOF, COVERAGE, ROOT/'uv.lock', ROOT/'pyproject.toml',
             ROOT/'acceleration/theory_20260930_eight_full99_cnf.py',
             ROOT/'acceleration/theory_20260930_variable_core_factor_preflight.py']
    save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): digest(p) for p in paths}, 'status': 'CANDIDATE_ARBITRARY_CORE_FACTOR_ENCODING',
        'limits': {'build_seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0},
        'normalization_candidate_sha256': NORMALIZATION_SHA, 'independent_coverage_gate': key(COVERAGE),
        'independent_coverage_gate_sha256': COVERAGE_SHA,
        'random_seed': None, 'random_seed_reason': 'Deterministic encoding; formula controls use separately recorded deterministic fixture seed.'})
    save(out/'controls.json', {'prefix': counter_controls(), 'selector_channels': channel_controls(), 'raw_core_formula_fixtures': calibrate()})
    top = 0

    def fresh():
        nonlocal top
        top += 1
        return top

    entries = []
    f = []
    for g in (1, 2):
        block = []
        for a in range(12):
            row = []
            for d in range(60):
                var = fresh()
                row.append(var)
                entries.append({'id': var, 'row': 12*g+a, 'column': d})
            block.append(row)
        f.append(block)
    matching_variables, matchings = [], []
    for g in (1, 2):
        m = [[False]*12 for _ in range(12)]
        for a, b in combinations(range(12), 2):
            var = fresh()
            m[a][b] = m[b][a] = var
            matching_variables.append({'id': var, 'fibre': g, 'endpoints': [a, b]})
        matchings.append(m)
    permutation_variables, p = [], []
    for a in range(12):
        row = []
        for b in range(12):
            var = fresh()
            row.append(var)
            permutation_variables.append({'id': var, 'row': a, 'column': b})
        p.append(row)
    assert top == 1716
    edges = [list(e) for e in combinations(range(12), 2) if e[1] != (e[0]^1)]
    c0 = [[int(a in e) for e in edges] for a in range(12)]
    scope = {'schema': 'ARBITRARY_TRIANGLE_CORE_FACTOR_SCOPE_V1',
        'normalization_candidate_path': key(NORMALIZATION), 'normalization_candidate_sha256': NORMALIZATION_SHA,
        'normalization_claim_id': 'C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION', 'normalization_claim_revision': 1,
        'normalization_coverage_gate': key(COVERAGE), 'normalization_coverage_gate_sha256': COVERAGE_SHA,
        'M0': [a^1 for a in range(12)], 'cross01': list(range(12)), 'cross02': list(range(12)),
        'M1_M2_scope': 'All symmetric zero-diagonal binary12x12 matrices with every row sum1.',
        'P_scope': 'All binary12x12 matrices with every row and column sum1; rowsA1,columnsA2.',
        'core_extra_restrictions': [], 'target_automorphism_assumed': False,
        'edge_columns_C0': edges, 'known_incidence_rows': c0+[[-1]*60 for _ in range(24)],
        'entry_variables': entries, 'matching_variables': matching_variables, 'permutation_variables': permutation_variables,
        'symbolic_C1': f[0], 'symbolic_C2': f[1], 'symbolic_M1': matchings[0], 'symbolic_M2': matchings[1], 'symbolic_P': p,
        'row_sum': 10, 'fibre_column_sum': 2, 'mixed_cap_upper_bound': 2, 'distinct_column_cap_upper_bound': 2,
        'component_restrictions': False, 'fixed_Q1_Q2': False, 'zero_incidence_folds': 0,
        'residual_D_included': False, 'full_target_graph_encoded': False,
        'target_relation': 'Every target admits this normalized necessary factor scope by the pinned independent coverage gate; new CNF equivalence still requires independent review.'}
    save(out/'scope.json', scope)
    rows, products_meta, caps_meta, channels = [], [], [], []
    with (out/'clauses.body').open('xb') as body:
        clauses = Clauses(body, cap)
        enc = Encoder(top, clauses)

        def counter(terms, bound, equality, metadata):
            terms = [x for x in terms if type(x) is int]
            rows.append(enc.counter(terms, bound, equality, metadata))

        def both(a, b, metadata):
            first = clauses.count+1
            z = enc.conjunction(a, b)
            products_meta.append({'id': z, 'left': a, 'right': b, **metadata,
                                  'first_clause': first, 'clause_count': clauses.count-first+1})
            return z

        for g, m in enumerate(matchings, 1):
            for a, row in enumerate(m):
                counter(row, 1, True, {'kind': 'matching_degree', 'fibre': g, 'row': a})
        for a in range(12):
            counter(p[a], 1, True, {'kind': 'permutation_degree', 'axis': 'row', 'index': a})
            counter([p[b][a] for b in range(12)], 1, True, {'kind': 'permutation_degree', 'axis': 'column', 'index': a})
        for g, block in enumerate(f, 1):
            for a, row in enumerate(block):
                counter(row, 10, True, {'kind': 'incidence_row', 'row': 12*g+a})
            for d in range(60):
                counter([block[a][d] for a in range(12)], 2, True, {'kind': 'incidence_column', 'fibre': g, 'column': d})
        for g in range(2):
            for a, b in product(range(12), repeat=2):
                terms = [f[g][b][d] for d, e in enumerate(edges) if a in e]
                terms += [matchings[g][a][b], p[b][a] if g == 0 else p[a][b]]
                counter(terms, 2-int(a == b)-int((a^1) == b), True,
                        {'kind': 'C0_cross_Gram', 'pair': [a, 12*(g+1)+b], 'delta': int(a == b), 'M0_constant': int((a^1) == b)})
            for a, b in combinations(range(12), 2):
                terms = [both(f[g][a][d], f[g][b][d], {'kind': 'within_fibre_incidence', 'pair': [12*(g+1)+a, 12*(g+1)+b], 'column': d}) for d in range(60)]
                counter(terms+[matchings[g][a][b]], 1, True, {'kind': 'within_fibre_Gram', 'pair': [12*(g+1)+a, 12*(g+1)+b]})
        for a, b in product(range(12), repeat=2):
            terms = [both(f[0][a][d], f[1][b][d], {'kind': 'cross_fibre_incidence', 'pair': [12+a, 24+b], 'column': d}) for d in range(60)]
            terms.append(p[a][b])
            terms += [both(matchings[0][a][k], p[k][b], {'kind': 'M1P', 'row': a, 'column': b, 'middle': k}) for k in range(12) if k != a]
            terms += [both(p[a][k], matchings[1][k][b], {'kind': 'PM2', 'row': a, 'column': b, 'middle': k}) for k in range(12) if k != b]
            counter(terms, 2-int(a == b), True, {'kind': 'C1_C2_Gram', 'pair': [12+a, 24+b], 'delta': int(a == b)})
        gram_end = {'variables': enc.top, 'clauses': clauses.count, 'counter_rows': len(rows)}
        for d, e in combinations(range(60), 2):
            shared = sorted(set(edges[d]) & set(edges[e]))
            if shared:
                assert len(shared) == 1
                for a, b in product(range(12), repeat=2):
                    literal = [-f[0][a][d], -f[0][a][e], -f[1][b][d], -f[1][b][e]]
                    clauses.emit(*literal)
                    caps_meta.append([d, e, a, b, clauses.count])
        assert len(caps_meta) == 77760
        channel_specs = [('U1', matchings[0], f[0]), ('U2', matchings[1], f[1]),
                         ('V1', p, f[1]), ('V2', [[p[k][a] for k in range(12)] for a in range(12)], f[0])]
        outputs = {}
        for name, selector, inputs in channel_specs:
            output = [[enc.fresh() for _ in range(60)] for _ in range(12)]
            outputs[name] = output
            first = clauses.count+1
            active = 0
            for a in range(12):
                for k in range(12):
                    selected = selector[a][k]
                    if selected is False:
                        continue
                    assert type(selected) is int
                    active += 1
                    for d in range(60):
                        x, z = inputs[k][d], output[a][d]
                        clauses.emit(-selected, -x, z)
                        clauses.emit(-selected, x, -z)
            channels.append({'name': name, 'selector_matrix': selector, 'input_matrix': inputs, 'output_matrix': output,
                'loop_order': ['output_row', 'source_row', 'column'], 'false_selectors_omitted': True,
                'active_selector_entries': active, 'first_clause': first, 'clause_count': clauses.count-first+1,
                'semantic_relation': 'For the unique selected source row, output equals that source input bit.',
                'clause_order': ['-selector -input output', '-selector input -output']})
        assert sum(x['clause_count'] for x in channels) == 66240
        for a, d in product(range(12), range(60)):
            constant = c0[a][d]+c0[a^1][d]
            assert constant in (0, 1)
            counter([f[0][a][d], f[1][a][d]], 2-constant, False,
                    {'kind': 'mixed_column_cap', 'row': a, 'column': d, 'constant': constant, 'original_bound': 2})
            counter([f[0][a][d], outputs['U1'][a][d], outputs['V1'][a][d]], 2-c0[a][d], False,
                    {'kind': 'mixed_column_cap', 'row': 12+a, 'column': d, 'constant': c0[a][d], 'original_bound': 2})
            counter([f[1][a][d], outputs['U2'][a][d], outputs['V2'][a][d]], 2-c0[a][d], False,
                    {'kind': 'mixed_column_cap', 'row': 24+a, 'column': d, 'constant': c0[a][d], 'original_bound': 2})
    assert len(rows) == 2916 and len(products_meta) == 19728
    cnf = out/'instance.cnf'
    with cnf.open('xb') as fstream, (out/'clauses.body').open('rb') as body:
        fstream.write(('p cnf %d %d\n' % (enc.top, clauses.count)).encode('ascii'))
        shutil.copyfileobj(body, fstream, 1048576)
    model = {'schema': 'ARBITRARY_TRIANGLE_CORE_FACTOR_CHANNEL_PREFIX_CNF_V1',
        'scope_path': key(out/'scope.json'), 'scope_sha256': digest(out/'scope.json'),
        'known_incidence_rows': scope['known_incidence_rows'], 'entry_variables': entries,
        'matching_variables': matching_variables, 'permutation_variables': permutation_variables,
        'product_variables': products_meta, 'counter_rows': rows,
        'column_cap_records': caps_meta, 'column_cap_record_format': ['column_d', 'column_e', 'C1_local_row', 'C2_local_row', 'absolute_clause_number'],
        'selector_channel_groups': channels, 'variables': enc.top, 'clauses': clauses.count,
        'primary_variables': 1716, 'selector_channel_variables': 2880, 'gram_prefix_end': gram_end,
        'prefix_reference_format': 'JSON booleans are constants; positive integers are variable IDs.',
        'gate_clause_order': {'and': ['a -z', 'b -z', '-a -b z'], 'or': ['-a z', '-b z', 'a b -z'],
                             'a_or_b_and_c': ['-a z', '-b -c z', 'a b -z', 'a c -z']},
        'component_restrictions': False, 'zero_incidence_folds': 0, 'residual_D_included': False,
        'full_target_graph_encoded': False, 'solver_calls': 0,
        'normalization_candidate_sha256': NORMALIZATION_SHA, 'normalization_coverage_gate_sha256': COVERAGE_SHA,
        'independent_encoding_and_object_gates_required_before_solver': True}
    save(out/'model.json', model)
    cap.check()
    save(out/'artifact_packages.json', {'packages': [package(p, cap) for p in (cnf, out/'model.json')],
                                       'retrieval': 'Concatenate ordered gzip parts, decompress, verify exact raw hash and length.'})
    summary = {'status': 'CANDIDATE_ARBITRARY_CORE_FACTOR_CNF_BUILT', 'independent_verification': 'PENDING',
        'variables': enc.top, 'clauses': clauses.count, 'primary_variables': 1716,
        'incidence_variables': 1440, 'matching_edge_variables': 132, 'permutation_variables': 144,
        'AND_products': len(products_meta), 'counter_rows': len(rows), 'equality_rows': 756, 'mixed_cap_rows': 2160,
        'column_cap_clauses': len(caps_meta), 'selector_channel_variables': 2880, 'selector_channel_clauses': 66240,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes, 'solver_calls': 0,
        'outputs': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'clauses.body'},
        'limitations': ['Normalization is separately gated; this encoding and raw object checker require independent gates before solver use.',
                       'SAT supplies a necessary factor/core specification only; no residual D or complete target.',
                       'No fixed component, old exclusion, or automorphism premise.']}
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'outputs'}))


def decode(args):
    assert not args.out.exists()
    model = json.loads(args.model.read_bytes())
    assert model['schema'] == 'ARBITRARY_TRIANGLE_CORE_FACTOR_CHANNEL_PREFIX_CNF_V1'
    scope_path = ROOT/model['scope_path']
    assert digest(scope_path) == model['scope_sha256']
    scope = json.loads(scope_path.read_bytes())
    assignment = json.loads(args.assignment.read_bytes())['assignment']
    assert len(assignment) == model['variables'] and all(type(x) is int and x != 0 for x in assignment)
    assert sorted(abs(x) for x in assignment) == list(range(1, model['variables']+1))
    values = {abs(x): int(x > 0) for x in assignment}
    incidence = [r.copy() for r in model['known_incidence_rows']]
    for item in model['entry_variables']:
        incidence[item['row']][item['column']] = values[item['id']]
    matching_matrices = [[[0]*12 for _ in range(12)] for _ in range(2)]
    for item in model['matching_variables']:
        a, b = item['endpoints']
        m = matching_matrices[item['fibre']-1]
        m[a][b] = m[b][a] = values[item['id']]
    permutation = [[0]*12 for _ in range(12)]
    for item in model['permutation_variables']:
        permutation[item['row']][item['column']] = values[item['id']]
    core = [[0]*36 for _ in range(36)]
    all_matching_matrices = [[[int(b == (a^1)) for b in range(12)] for a in range(12)], *matching_matrices]
    for g, m in enumerate(all_matching_matrices):
        for a, b in product(range(12), repeat=2):
            core[12*g+a][12*g+b] = m[a][b]
    for a in range(12):
        core[a][12+a] = core[12+a][a] = core[a][24+a] = core[24+a][a] = 1
        for b in range(12):
            core[12+a][24+b] = core[24+b][12+a] = permutation[a][b]
    gram = [[12*int(a == b)-core[a][b]-sum(core[a][k]*core[k][b] for k in range(36))+2-int(a//12 == b//12)
             for b in range(36)] for a in range(36)]
    failures = []
    for g, m in enumerate(matching_matrices, 1):
        if any(sum(r) != 1 for r in m):
            failures.append(['matching_degree', g])
    if any(sum(r) != 1 for r in permutation) or any(sum(permutation[a][b] for a in range(12)) != 1 for b in range(12)):
        failures.append(['permutation_degree'])
    for a in range(36):
        if sum(incidence[a]) != 10:
            failures.append(['incidence_row', a])
        for b in range(36):
            if sum(incidence[a][d]*incidence[b][d] for d in range(60)) != gram[a][b]:
                failures.append(['Gram', a, b])
        for d in range(60):
            if incidence[a][d]+sum(core[a][b]*incidence[b][d] for b in range(36)) > 2:
                failures.append(['mixed_cap', a, d])
    for g, d in product(range(3), range(60)):
        if sum(incidence[a][d] for a in range(12*g, 12*g+12)) != 2:
            failures.append(['fibre_column', g, d])
    for d, e in combinations(range(60), 2):
        if sum(incidence[a][d]*incidence[a][e] for a in range(36)) > 2:
            failures.append(['column_cap', d, e])
    raw = [[0]*99 for _ in range(99)]
    for a, b in combinations(range(3), 2):
        raw[a][b] = raw[b][a] = 1
    for a in range(36):
        raw[a//12][3+a] = raw[3+a][a//12] = 1
        for b in range(36):
            raw[3+a][3+b] = core[a][b]
        for d in range(60):
            raw[3+a][39+d] = raw[39+d][3+a] = incidence[a][d]
    for d, e in combinations(range(60), 2):
        raw[39+d][39+e] = raw[39+e][39+d] = -1
    result = {'status': 'CANDIDATE_ARBITRARY_CORE_FACTOR_PENDING_INDEPENDENT_CHECK',
        'M1': matching_matrices[0], 'M2': matching_matrices[1], 'P': permutation,
        'core_adjacency': core, 'incidence_matrix': incidence, 'prescribed_gram': gram, 'partial_adjacency_full99': raw,
        'encoding_model_sha256': digest(args.model), 'assignment_sha256': digest(args.assignment), 'scope_sha256': model['scope_sha256'],
        'producer_exact_check': {'valid': not failures, 'error_count': len(failures), 'first_errors': failures[:20]},
        'independent_approval': False, 'full99_graph': False, 'residual_Y_Y_unknown_pairs': 1770,
        'timestamp': datetime.now(timezone.utc).isoformat(), 'command': [sys.executable, *sys.argv]}
    save(args.out, result)
    print(json.dumps({'status': result['status'], 'producer_exact_check': result['producer_exact_check']}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    b = sub.add_parser('build')
    b.add_argument('--out', type=Path, required=True)
    d = sub.add_parser('decode')
    for name in ('model', 'assignment', 'out'):
        d.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    build(args) if args.mode == 'build' else decode(args)


if __name__ == '__main__':
    main()
