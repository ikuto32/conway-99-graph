"""Replace dynamic overlap counters by equivalent clauses under retained Gram."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import ResourceCap, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_triangle_one_c2_row_cnf'
GATE = ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json'
PINS = {
    BASE/'instance.cnf': 'bdafe54585c4f49f2ef4ca7a29862172c7410e73d34c2ac4ac7af4c5cdd79b1b',
    BASE/'model.json': '918d3a35b1b240874997cb7ac6a001ef5d78ce05792414eeb336a192b8fc1e2a',
    BASE/'scope.json': '9c2c0618e4b07dc549eb006b2a81a5e9338b919cc499f01abcddc4dcac8402c8',
    GATE: '661062b1fbdf0d9e076082867b44353509fb892d9946dc142d1c70b91f59558d',
}


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def controls():
    rows = []
    for n in (4, 6):
        edges = [set(e) for e in combinations(range(n), 2) if e[1] != (e[0]^1)]
        pairs = list(combinations(edges, 2))
        cases = 0
        for (a, b), (c, d), (x, y) in product(pairs, pairs, product((0, 1), repeat=2)):
            k, q = len(a & b), len(c & d)
            assert k in (0, 1) and q in (0, 1)
            original = k+q+x*y <= 2
            compact = True if k == 0 else all(not (r in c and r in d and x and y) for r in range(n))
            assert original == compact
            cases += 1
        rows.append({'coordinates': n, 'distinct_nonmatching_two_subsets': len(edges), 'exact_cases': cases})
    # Dropping distinctness can break the equivalence when fixed C0 overlap is zero.
    k, q, x, y = 0, 2, 1, 1
    assert not (k+q+x*y <= 2) and (True if k == 0 else False)
    return {'status': 'PRODUCER_COMPACT_EQUIVALENCE_CONTROLS_PASS', 'cases': rows,
            'missing_distinctness_counterexample': {'C0_overlap': k, 'C1_overlap': q, 'x': x, 'y': y,
                'original_accepts': False, 'unguarded_compact_accepts': True},
            'independent_approval': False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    for p, h in PINS.items():
        assert digest(p) == h
    inputs = [Path(__file__), Path(__file__).with_name('theory_20260930_triangle_one_c2_compact_spec.md'),
              *PINS, ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): digest(p) for p in inputs}, 'status': 'CANDIDATE_EQUIVALENT_COMPACT_ENCODING',
        'limits': {'build_seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0},
        'random_seed': None, 'random_seed_reason': 'Deterministic exact construction.',
        'scope': 'Exactly the existing 25-row target-necessary finite problem; no new coverage claim.'})
    save(out/'controls.json', controls())
    old = json.loads((BASE/'model.json').read_bytes())
    scope = json.loads((BASE/'scope.json').read_bytes())
    assert old['counter_rows'][487]['kind'] == 'column_pair_overlap'
    kept_rows = old['counter_rows'][:487]
    assert len(kept_rows) == 487 and all(r['kind'] != 'column_pair_overlap' for r in kept_rows)
    kept_products = [p for p in old['product_variables'] if p['kind'] == 'row_gram']
    removed_products = [p for p in old['product_variables'] if p['kind'] == 'column_overlap']
    cutoff = min(p['first_clause'] for p in removed_products)-1
    top = min(p['id'] for p in removed_products)-1
    assert cutoff == 77721 and top == 22379
    assert max(r['first_clause']+r['clause_count']-1 for r in kept_rows) == cutoff
    assert all(p['first_clause']+p['clause_count']-1 <= cutoff for p in kept_products)
    refs = [item['id'] for item in old['entry_variables']] + [p['id'] for p in kept_products]
    for r in kept_rows:
        refs += [x for x in r['inputs'] if type(x) is int]
        refs += [s[2] for s in r['states'] if type(s[2]) is int]
    assert max(refs) == top
    symbolic = [[bool(x) if x >= 0 else None for x in r] for r in old['known_incidence_rows']]
    for item in old['entry_variables']:
        symbolic[item['row']][item['column']] = item['id']
    c0edges = [set(e) for e in scope['edge_columns_C0']]
    universe, clauses = [], []
    for d, e in combinations(range(60), 2):
        overlap = sorted(c0edges[d] & c0edges[e])
        assert len(overlap) in (0, 1)
        if not overlap:
            continue
        for r in range(12, 24):
            coordinates = [[r, d], [r, e], [24, d], [24, e]]
            values = [symbolic[a][b] for a, b in coordinates]
            assert all(v is False or type(v) is int for v in values)
            zeros = [coord for coord, value in zip(coordinates, values) if value is False]
            record = {'C0_common_endpoint': overlap[0], 'column_pair': [d, e], 'C1_row': r,
                      'coordinates': coordinates, 'references': values}
            if zeros:
                record.update({'action': 'OMIT_TAUTOLOGY_FIXED_ZERO', 'zero_coordinates': zeros,
                               'clause': None, 'clause_null_reason': 'At least one negated fixed-zero literal is true.'})
            else:
                clause = [-v for v in values]
                assert len(set(clause)) == 4
                clauses.append(clause)
                record.update({'action': 'EMIT', 'zero_coordinates': [], 'clause': clause,
                               'first_clause': cutoff+len(clauses), 'clause_count': 1})
            universe.append(record)
    assert len(universe) == 540*12
    assert len({tuple(r['column_pair']) for r in universe}) == 540
    recipe = {'schema': 'TRIANGLE_ONE_C2_COMPACT_REPLACEMENT_RECIPE_V1',
        'base_cnf_path': key(BASE/'instance.cnf'), 'base_cnf_sha256': digest(BASE/'instance.cnf'),
        'base_model_sha256': digest(BASE/'model.json'), 'scope_path': key(BASE/'scope.json'),
        'scope_sha256': digest(BASE/'scope.json'), 'retained_body_clause_count': cutoff,
        'retained_maximum_variable': top, 'intersecting_C0_column_pairs': 540,
        'full_pair_row_universe': 6480, 'candidate_clauses': universe,
        'emitted_count': len(clauses), 'omitted_fixed_zero_tautologies': len(universe)-len(clauses),
        'disjoint_C0_column_pair_count': 1230,
        'disjoint_omission_reason': 'C1 columns are distinct 2-subsets by retained Gram and column margins, so C1 overlap<=1; selected row contributes<=1.',
        'mathematical_equivalence_proof': key(Path(__file__).with_name('theory_20260930_triangle_one_c2_compact_spec.md'))}
    save(out/'replacement_recipe.json', recipe)
    cnf = out/'instance.cnf'
    with cnf.open('xb') as f, (BASE/'instance.cnf').open('rb') as original:
        assert original.readline() == b'p cnf 74814 256151\n'
        f.write(('p cnf %d %d\n' % (top, cutoff+len(clauses))).encode('ascii'))
        for _ in range(cutoff):
            line = original.readline()
            assert line.endswith(b' 0\n')
            f.write(line)
        for clause in clauses:
            f.write((' '.join(map(str, clause))+' 0\n').encode('ascii'))
    model = {**old, 'schema': 'TRIANGLE_ONE_C2_ROW_COMPACT_PREFIX_CNF_V1',
        'product_variables': kept_products, 'counter_rows': kept_rows, 'compact_clauses': clauses,
        'variables': top, 'clauses': cutoff+len(clauses), 'retained_original_clause_count': cutoff,
        'original_model_path': key(BASE/'model.json'), 'original_model_sha256': digest(BASE/'model.json'),
        'replacement_recipe_path': key(out/'replacement_recipe.json'),
        'replacement_recipe_sha256': digest(out/'replacement_recipe.json'),
        'equivalence_review': 'PENDING_INDEPENDENT_REVIEW', 'solver_calls': 0}
    save(out/'model.json', model)
    cap.check()
    save(out/'artifact_packages.json', {'packages': [package(p, cap) for p in (cnf, out/'model.json', out/'replacement_recipe.json')],
                                       'retrieval': 'Concatenate ordered gzip parts and decompress; verify exact original hash and length.'})
    summary = {'status': 'CANDIDATE_EQUIVALENT_COMPACT_25_ROW_CNF', 'independent_verification': 'PENDING',
        'variables': top, 'clauses': cutoff+len(clauses), 'entry_variables': len(old['entry_variables']),
        'retained_AND_products': len(kept_products), 'retained_counter_rows': len(kept_rows),
        'retained_clauses': cutoff, 'new_four_literal_clauses': len(clauses), 'universe_tuples': len(universe),
        'fixed_zero_tautologies': len(universe)-len(clauses), 'solver_calls': 0,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes,
        'outputs': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()},
        'limitations': ['Equivalent finite 25-row scope only; no larger graph or unrestricted exclusion.',
                        'Clause-count reduction is not a solver performance guarantee.',
                        'New independent encoding/object gates required before a solver run.']}
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'outputs'}))


if __name__ == '__main__':
    main()
