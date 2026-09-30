"""Exact target-necessary projection: free C1 and one selected C2 row."""
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

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf'
KERNEL = ROOT/'acceleration/results/20260930_triangle_factor_components/kernel_certificate.json'
PINS = {
    BASE/'scope.json': '51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',
    KERNEL: '34852bbae744a346c87843bdd76d1697767cbbc9d9ad0b2276e9c8ccba47e0e1',
    ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json': '03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b',
    ROOT/'acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json': '5a6ebade41cf1ab35796ca5d5ce3840c23b624ab06d0ed5a4ff327327ea2b97f',
}


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def controls():
    # Check the defining conjunction clauses by their truth table, not a SAT solver.
    cases = 0
    for a, b, z in product((False, True), repeat=3):
        clauses = ((a or not z), (b or not z), (not a or not b or z))
        assert all(clauses) == (z == (a and b))
        cases += 1
    return {'and_truth_cases': cases, 'prefix_controls': counter_controls(),
            'scope': 'Producer calibration only; independent semantic review remains required.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    for p, h in PINS.items():
        assert digest(p) == h
    inputs = [Path(__file__), Path(__file__).with_name('theory_20260930_triangle_one_c2_row_cnf_spec.md'),
              *PINS, ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json', {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): digest(p) for p in inputs},
        'status': 'CANDIDATE_PROJECTED_ENCODING',
        'scope': 'Exact 25-row necessary target projection of one fixed triangle core; Q1 free, C2 coordinate0 included.',
        'limits': {'build_seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0},
        'random_seed': None, 'random_seed_reason': 'Deterministic exact construction.',
        'target_automorphism_assumed': False,
    })
    save(out/'counter_controls.json', controls())
    base = json.loads((BASE/'scope.json').read_bytes())
    kernel = json.loads(KERNEL.read_bytes())
    known = base['known_incidence_rows'][:25]
    gram = [r[:25] for r in base['target_gram_rows'][:25]]
    components = kernel['components']
    entries = [x for x in base['entry_variables'] if x['row'] < 25]
    assert len(entries) == 650 and [x['id'] for x in entries] == list(range(1, 651))
    assert all(sum(r) == 10 for r in known[:12])
    assert all(sum(known[a][d]*known[b][d] for d in range(60)) == gram[a][b]
               for a in range(12) for b in range(12))
    symbolic = [[bool(x) if x >= 0 else None for x in r] for r in known]
    for item in entries:
        symbolic[item['row']][item['column']] = item['id']
    assert all(x is not None for r in symbolic for x in r)
    scope = {
        'schema': 'FIXED_TRIANGLE_ONE_C2_ROW_TARGET_SCOPE_V1',
        'parent_scope': key(BASE/'scope.json'), 'parent_scope_sha256': digest(BASE/'scope.json'),
        'kernel_certificate': key(KERNEL), 'kernel_certificate_sha256': digest(KERNEL),
        'selected_original_rows': list(range(25)), 'selected_C2_coordinate': 0, 'selected_C2_graph_vertex': 27,
        'known_incidence_rows': known, 'target_gram_rows': gram, 'entry_variables': entries,
        'edge_columns_C0': base['edge_columns_C0'], 'components': components,
        'row_sum': 10, 'complete_fibres': [0, 1], 'column_sum_per_complete_fibre': 2,
        'partial_component_column_upper_bound': 2, 'column_pair_overlap_upper_bound': 2,
        'C1_free': True, 'C2_rows_included': [0], 'D_included': False,
        'full_core_coverage_relation': 'Every target containing this fixed core can be relabeled to restrict to a model; converse extension not claimed.',
        'abstract_36_factor_projection_claimed': False, 'unrestricted_target_coverage': False,
        'target_automorphism_assumed': False,
    }
    save(out/'scope.json', scope)
    rows, products = [], []
    with (out/'clauses.body').open('xb') as body:
        clauses = Clauses(body, cap)
        enc = Encoder(650, clauses)

        def append_product(x, y, metadata, terms):
            if x is False or y is False:
                return 0
            if x is True and y is True:
                return 1
            if x is True:
                terms.append(y)
            elif y is True:
                terms.append(x)
            else:
                first = clauses.count + 1
                z = enc.conjunction(x, y)
                products.append({'id': z, 'left': x, 'right': y, **metadata,
                                 'first_clause': first, 'clause_count': clauses.count-first+1})
                terms.append(z)
            return 0

        for r in range(12, 25):
            rows.append(enc.counter([x for x in symbolic[r] if type(x) is int], 10, True,
                                    {'kind': 'row_margin', 'row': r, 'constant': 0, 'original_bound': 10}))
        for d in range(60):
            rows.append(enc.counter([symbolic[r][d] for r in range(12, 24) if type(symbolic[r][d]) is int], 2, True,
                                    {'kind': 'column_margin', 'fibre': 1, 'column': d, 'constant': 0, 'original_bound': 2}))
        for a in range(12):
            for b in range(12, 25):
                terms = [symbolic[b][d] for d in range(60) if known[a][d] == 1 and type(symbolic[b][d]) is int]
                rows.append(enc.counter(terms, gram[a][b], True,
                                        {'kind': 'C0_cross_gram', 'pair': [a, b], 'constant': 0, 'original_bound': gram[a][b]}))
        for a, b in combinations(range(12, 25), 2):
            terms = []
            constant = sum(append_product(symbolic[a][d], symbolic[b][d],
                                          {'kind': 'row_gram', 'pair': [a, b], 'column': d}, terms) for d in range(60))
            rows.append(enc.counter(terms, gram[a][b]-constant, True,
                                    {'kind': 'unknown_pair_gram', 'pair': [a, b], 'constant': constant, 'original_bound': gram[a][b]}))
        for ci, component in enumerate(components):
            support = [r for r in component if r < 25]
            for d in range(60):
                constant = sum(symbolic[r][d] is True for r in support)
                terms = [symbolic[r][d] for r in support if type(symbolic[r][d]) is int]
                rows.append(enc.counter(terms, 2-constant, False,
                                        {'kind': 'partial_component_capacity', 'component': ci, 'column': d,
                                         'raw_component_rows': component, 'included_rows': support,
                                         'constant': constant, 'original_bound': 2}))
        for d, e in combinations(range(60), 2):
            terms = []
            constant = sum(append_product(symbolic[r][d], symbolic[r][e],
                                          {'kind': 'column_overlap', 'column_pair': [d, e], 'row': r}, terms) for r in range(25))
            rows.append(enc.counter(terms, 2-constant, False,
                                    {'kind': 'column_pair_overlap', 'column_pair': [d, e],
                                     'included_rows': list(range(25)), 'constant': constant, 'original_bound': 2}))
    cnf = out/'instance.cnf'
    with cnf.open('xb') as f, (out/'clauses.body').open('rb') as body:
        f.write(('p cnf %d %d\n' % (enc.top, clauses.count)).encode('ascii'))
        shutil.copyfileobj(body, f, 1048576)
    model = {
        'schema': 'TRIANGLE_ONE_C2_ROW_TARGET_PREFIX_CNF_V1',
        'scope_path': key(out/'scope.json'), 'scope_sha256': digest(out/'scope.json'),
        'known_incidence_rows': known, 'target_gram_rows': gram, 'entry_variables': entries,
        'product_variables': products, 'counter_rows': rows, 'components': components,
        'variables': enc.top, 'clauses': clauses.count,
        'prefix_reference_format': 'JSON booleans are constants; positive integers are variable IDs.',
        'gate_clause_order': {'and': ['a -z', 'b -z', '-a -b z'], 'or': ['-a z', '-b z', 'a b -z'],
                              'a_or_b_and_c': ['-a z', '-b -c z', 'a b -z', 'a c -z']},
        'clauses_constant_folded': True, 'selected_original_rows': list(range(25)),
        'full_target_graph_encoded': False, 'complete36row_factor_encoded': False,
        'abstract_36_factor_projection_claimed': False, 'solver_calls': 0,
    }
    save(out/'model.json', model)
    cap.check()
    assert len(rows) == 2257
    assert sum(x['equality'] for x in rows) == 307
    save(out/'artifact_packages.json', {'packages': [package(p, cap) for p in (cnf, out/'model.json')],
                                       'retrieval': 'Concatenate gzip parts, decompress, verify exact length/hash.'})
    summary = {
        'status': 'CANDIDATE_ONE_C2_ROW_TARGET_PROJECTION_CNF', 'independent_verification': 'PENDING',
        'variables': enc.top, 'clauses': clauses.count, 'entry_variables': len(entries),
        'AND_products': len(products), 'counter_rows': len(rows), 'equality_rows': 307,
        'component_capacity_rows': 180, 'column_pair_overlap_rows': 1770,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes,
        'solver_calls': 0, 'target_resolution': False,
        'outputs': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                    for p in sorted(out.iterdir()) if p.is_file() and p.name != 'clauses.body'},
        'limitations': ['SAT provides only this 25-row necessary projection, neither a 36-row factor nor a 99-vertex graph.',
                        'UNSAT requires exact encoding and necessary-projection review and a complete independently checked proof.',
                        'No unrestricted fixed-core containment; no implication asserted for every abstract 36-row Gram factor.'],
    }
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'outputs'}))


if __name__ == '__main__':
    main()
