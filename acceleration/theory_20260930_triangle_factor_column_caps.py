"""Append exact compact target column caps to the full component factor CNF."""
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
from theory_20260930_eight_full99_cnf import ResourceCap, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_triangle_factor_components'
ORIGINAL_SCOPE = ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json'
KERNEL = BASE/'kernel_certificate.json'
PINS = {
    BASE/'instance.cnf': 'bf68bbec6c9102ad9627161edad566972396c666aff8f14b336fb06aabf65b0a',
    BASE/'model.json': '03566eb23e2dfe542f979dc84f12747c2791171b4b7293f177e4ac209cdd20a8',
    ORIGINAL_SCOPE: '51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',
    KERNEL: '34852bbae744a346c87843bdd76d1697767cbbc9d9ad0b2276e9c8ccba47e0e1',
    ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json': '03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b',
}


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def controls(cap):
    records = []
    for n in (4, 6):
        edges = [set(e) for e in combinations(range(n), 2) if e[1] != (e[0]^1)]
        pair_intersections = [(a, b, a & b) for a, b in combinations(edges, 2)]
        count = 0
        for (_, _, k), (_, _, q1), (_, _, q2) in product(pair_intersections, repeat=3):
            assert len(k) <= 1 and len(q1) <= 1 and len(q2) <= 1
            direct = len(k)+len(q1)+len(q2) <= 2
            compact = not k or all(not (r in q1 and s in q2) for r in range(n) for s in range(n))
            assert direct == compact
            count += 1
        cap.check()
        records.append({'coordinates': n, 'distinct_nonmatching_pairs': len(edges), 'triple_cases': count})
    assert 0+2+1 > 2
    return {'status': 'PRODUCER_THREE_FIBRE_COMPACT_CONTROLS_PASS', 'records': records,
            'missing_distinctness_counterexample': {'overlaps': [0, 2, 1], 'direct_cap': False,
                'unguarded_compact_cap': True, 'reason': 'A duplicate C1 column violates a retained Gram premise.'},
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
    paths = [Path(__file__), Path(__file__).with_name('theory_20260930_triangle_factor_column_caps_spec.md'),
             *PINS, ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): digest(p) for p in paths}, 'status': 'CANDIDATE_TARGET_NECESSARY_FACTOR_ENCODING',
        'limits': {'build_seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0},
        'random_seed': None, 'random_seed_reason': 'Deterministic exact construction.',
        'scope': 'One fixed triangle core, full binary36x60 factor, component margins and target column-overlap caps; D absent.'})
    save(out/'controls.json', controls(cap))
    old = json.loads((BASE/'model.json').read_bytes())
    original_scope = json.loads(ORIGINAL_SCOPE.read_bytes())
    kernel = json.loads(KERNEL.read_bytes())
    assert old['variables'] == 61296 and old['clauses'] == 212580
    scope = {**original_scope, 'schema': 'FIXED_TRIANGLE_FULL_FACTOR_TARGET_COLUMN_CAP_SCOPE_V1',
        'original_scope_path': key(ORIGINAL_SCOPE), 'original_scope_sha256': digest(ORIGINAL_SCOPE),
        'component_kernel_certificate': key(KERNEL), 'component_kernel_certificate_sha256': digest(KERNEL),
        'components': kernel['components'], 'component_column_sum': 2,
        'column_pair_overlap_upper_bound': 2, 'column_pair_count': 1770,
        'target_implication': 'Every target containing this fixed core can be relabeled to yield this factor with column caps.',
        'abstract_gram_implies_column_caps_claimed': False, 'unrestricted_target_coverage': False,
        'residual_D_included': False, 'target_automorphism_assumed': False}
    save(out/'scope.json', scope)
    symbolic = [[bool(x) if x >= 0 else None for x in r] for r in old['known_incidence_rows']]
    for item in old['entry_variables']:
        symbolic[item['row']][item['column']] = item['id']
    edges = [set(e) for e in original_scope['edge_columns_C0']]
    templates, clauses, overlap_pairs = [], [], []
    for d, e in combinations(range(60), 2):
        common = sorted(edges[d] & edges[e])
        assert len(common) in (0, 1)
        if not common:
            continue
        overlap_pairs.append([d, e, common[0]])
        for r, s in product(range(12, 24), range(24, 36)):
            coordinates = [[r, d], [r, e], [s, d], [s, e]]
            refs = [symbolic[a][b] for a, b in coordinates]
            assert all(x is False or type(x) is int for x in refs)
            zeros = [i for i, x in enumerate(refs) if x is False]
            if zeros:
                templates.append([d, e, r, s, refs, zeros, None])
            else:
                clause = [-x for x in refs]
                assert len(set(clause)) == 4
                clauses.append(clause)
                templates.append([d, e, r, s, refs, [], old['clauses']+len(clauses)])
    assert len(overlap_pairs) == 540 and len(templates) == 77760 and len(clauses) == 43740
    recipe = {'schema': 'TRIANGLE_FULL_FACTOR_COMPACT_COLUMN_CAP_RECIPE_V1',
        'base_cnf_path': key(BASE/'instance.cnf'), 'base_cnf_sha256': digest(BASE/'instance.cnf'),
        'base_model_path': key(BASE/'model.json'), 'base_model_sha256': digest(BASE/'model.json'),
        'base_variables': old['variables'], 'retained_body_clause_count': old['clauses'],
        'scope_path': key(out/'scope.json'), 'scope_sha256': digest(out/'scope.json'),
        'C0_intersecting_pairs': overlap_pairs,
        'template_format': ['column_d', 'column_e', 'C1_row_r', 'C2_row_s', 'references_Crd_Cre_Csd_Cse',
                            'zero_reference_positions', 'emitted_absolute_clause_number_or_null'],
        'null_reason': 'A fixed-zero reference makes the corresponding negated literal true; omit that tautology.',
        'templates': templates, 'emitted_clauses': len(clauses), 'omitted_zero_tautologies': len(templates)-len(clauses),
        'disjoint_C0_pair_count': 1230,
        'disjoint_omission_reason': 'Retained margins and within-fibre Gram force distinct2-subset columns in both C1 and C2, so each overlap<=1.',
        'mathematical_proof': key(Path(__file__).with_name('theory_20260930_triangle_factor_column_caps_spec.md'))}
    save(out/'clause_recipe.json', recipe)
    suffix = out/'column_caps.cnfpart'
    with suffix.open('xb') as f:
        for clause in clauses:
            f.write((' '.join(map(str, clause))+' 0\n').encode('ascii'))
    cnf = out/'instance.cnf'
    with cnf.open('xb') as f, (BASE/'instance.cnf').open('rb') as base, suffix.open('rb') as tail:
        assert base.readline() == b'p cnf 61296 212580\n'
        f.write(b'p cnf 61296 256320\n')
        shutil.copyfileobj(base, f, 1048576)
        shutil.copyfileobj(tail, f, 1048576)
    model = {**old, 'schema': 'FIXED_TRIANGLE_FULL_FACTOR_COLUMN_CAP_PREFIX_CNF_V1',
        'scope_path': key(out/'scope.json'), 'scope_sha256': digest(out/'scope.json'),
        'component_base_model_path': key(BASE/'model.json'), 'component_base_model_sha256': digest(BASE/'model.json'),
        'component_base_cnf_sha256': digest(BASE/'instance.cnf'), 'retained_component_base_clauses': old['clauses'],
        'column_cap_clauses': clauses, 'column_cap_recipe_path': key(out/'clause_recipe.json'),
        'column_cap_recipe_sha256': digest(out/'clause_recipe.json'), 'clauses': old['clauses']+len(clauses),
        'column_pair_overlap_upper_bound': 2, 'abstract_gram_implies_column_caps_claimed': False,
        'full_target_graph_encoded': False, 'solver_calls': 0}
    save(out/'model.json', model)
    cap.check()
    save(out/'artifact_packages.json', {'packages': [package(p, cap) for p in (cnf, out/'model.json', out/'clause_recipe.json')],
                                       'retrieval': 'Concatenate ordered gzip parts and decompress; verify raw exact hash and length.'})
    for p, h in PINS.items():
        assert digest(p) == h
    summary = {'status': 'CANDIDATE_FULL_FACTOR_TARGET_COLUMN_CAP_CNF', 'independent_verification': 'PENDING',
        'variables': old['variables'], 'clauses': old['clauses']+len(clauses), 'entry_variables': len(old['entry_variables']),
        'retained_component_base_clauses': old['clauses'], 'new_four_literal_clauses': len(clauses),
        'template_count': len(templates), 'fixed_zero_tautologies': len(templates)-len(clauses),
        'column_pairs_constrained': 1770, 'solver_calls': 0,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes,
        'outputs': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()},
        'limitations': ['SAT is a full factor with necessary column caps, not a 99-vertex graph.',
                        'UNSAT needs complete independent proof replay and excludes only target graphs containing this fixed core.',
                        'Caps are not claimed to follow from the abstract Gram conditions. No speed comparison is claimed.']}
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'outputs'}))


if __name__ == '__main__':
    main()
