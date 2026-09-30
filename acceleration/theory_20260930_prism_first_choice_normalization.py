"""Explicit relabelling normalization of the complete six-prism column model."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import argparse
import copy
import json
import platform
import shutil
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import ResourceCap, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_prism_all_columns'
AUDIT = ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
PINS = {
    BASE/'instance.cnf': 'd45b7e9837ed02b669f3681aaa8a63af78ff46487e968c59cf47cd7a49e53d6f',
    BASE/'model.json': 'a801e721a4c03d18e2fa9711a60f053895a4bfb8898b264f5174bcc36265f038',
    AUDIT: '07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3',
    ROOT/'acceleration/theory_20260930_eight_full99_cnf.py': '21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c',
    ROOT/'acceleration/theory_20260930_full_srg_validator.py': 'c0e070aa1ac39e8860b52a7f5e086b3e8da5e01f83d0f4fe76ab1e91c077279b',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def array_digest(values):
    return sha256(json.dumps(values, separators=(',', ':')).encode('ascii')).hexdigest()


def check_core_map(rowmap, c, gram):
    need(sorted(rowmap) == list(range(36)), 'row permutation')
    need(all(i//12 == rowmap[i]//12 for i in range(36)), 'fibre preservation')
    need(all(c[i][j] == c[rowmap[i]][rowmap[j]] for i in range(36) for j in range(36)), 'core preservation')
    need(all(gram[i][j] == gram[rowmap[i]][rowmap[j]] for i in range(36) for j in range(36)), 'Gram preservation')


def check_transport(record, choices):
    source = choices[record['source_choice_id']-1]
    target = choices[record['target_choice_id']-1]
    need(record['target_choice_id'] == 1, 'exact normalized choice ID1')
    need(record['column_map'][source['column']] == target['column'], 'transport column')
    need(sorted(record['row_map'][i] for i in source['rows']) == target['rows'], 'transport support')
    need(record['primary_choice_map'][source['id']-1] == 1, 'transport primary variable')


def check_coverage(transports, choices):
    need(sorted(t['source_choice_id'] for t in transports) == list(range(1, 97)), 'exact 96-choice coverage')
    for item in transports:
        check_transport(item, choices)


def check_unit(recipe):
    need(recipe['unit_clauses'] == [[1]], 'positive ID1 unit only')
    need(recipe['variables'] == 245880 and recipe['clauses'] == 874801, 'exact normalized dimensions')
    need(recipe['base_cnf_sha256'] == PINS[BASE/'instance.cnf'], 'exact base identity')


def rejected(call):
    try:
        call()
    except (ValueError, IndexError, KeyError, TypeError):
        return True
    raise ValueError('corruption was not rejected')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    cap = ResourceCap()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for path, value in PINS.items():
        need(digest(path) == value, 'pinned input '+key(path))
    audit = json.loads(AUDIT.read_bytes())
    need(audit['status'] == 'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS', 'base encoding gate')
    model = json.loads((BASE/'model.json').read_bytes())
    paths = [*PINS, Path(__file__), Path(__file__).with_name('theory_20260930_prism_first_choice_normalization_spec.md'),
             ROOT/'uv.lock', ROOT/'pyproject.toml']
    inputs = {key(p): digest(p) for p in paths}
    save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(), inputs_sha256=inputs,
        limits=dict(seconds=120, memory_bytes=8*1024**3, solver_calls=0), random_seed=None,
        random_seed_reason='Complete deterministic signed permutation action.', independent_approval=False))
    c, gram = model['core_adjacency'], model['target_gram']
    labels, choices = model['canonical_C0_columns'], model['choices']
    need(labels[0] == [0, 2] and choices[0] == dict(id=1, column=0, rows=[0, 2, 16, 18, 32, 34]), 'base first-choice convention')
    label_index = {tuple(x): d for d, x in enumerate(labels)}
    choice_index = {(item['column'], tuple(item['rows'])): item['id'] for item in choices}
    need(len(choice_index) == 5760, 'all distinct primary choices')
    equations = {(frozenset(row['inputs']), row['bound'], row['equality']) for row in model['counter_rows']}
    need(len(equations) == 540, 'all distinct abstract equations')
    actions, transports, orbit = [], {}, set()
    for perm in permutations(range(2, 6)):
        comp = [0, 1, *perm]
        for bits in product(range(2), repeat=4):
            flips = [0, 0, *bits]
            coordinate = [2*comp[a]+(b ^ flips[a]) for a in range(6) for b in range(2)]
            rowmap = [12*g+coordinate[i] for g in range(3) for i in range(12)]
            check_core_map(rowmap, c, gram)
            colmap = [label_index[tuple(sorted(coordinate[i] for i in pair))] for pair in labels]
            need(sorted(colmap) == list(range(60)) and colmap[0] == 0, 'canonical C0 bijection fixing first column')
            primary = [choice_index[colmap[item['column']], tuple(sorted(rowmap[r] for r in item['rows']))] for item in choices]
            need(sorted(primary) == list(range(1, 5761)), 'whole choice-variable bijection')
            for row in model['counter_rows']:
                transformed = (frozenset(primary[v-1] for v in row['inputs']), row['bound'], row['equality'])
                need(transformed in equations, 'abstract counting-equation covariance')
            firstmap = primary[:96]
            need(sorted(firstmap) == list(range(1, 97)), 'first-column domain action')
            orbit.add(primary[0])
            group_id = len(actions)
            actions.append(dict(group_id=group_id, component_permutation=comp, component_bit_flips=flips,
                coordinate_map=coordinate, row_map=rowmap, canonical_C0_column_map=colmap,
                first_column_choice_map=firstmap, primary_choice_map_sha256=array_digest(primary)))
            source = primary.index(1)+1
            need(source <= 96, 'ID1 inverse stays in first column')
            if source not in transports:
                transports[source] = dict(source_choice_id=source, target_choice_id=1, group_id=group_id,
                    row_map=rowmap, column_map=colmap, primary_choice_map=primary)
            cap.check()
    coordinates = {tuple(g['coordinate_map']): g['group_id'] for g in actions}
    need(len(coordinates) == 384, 'complete distinct signed subgroup')
    need(tuple(range(12)) in coordinates, 'group identity')
    inverse_ids = []
    for g in actions:
        inverse_ids.append(coordinates[tuple(g['coordinate_map'].index(i) for i in range(12))])
        for h in actions:
            need(tuple(g['coordinate_map'][h['coordinate_map'][i]] for i in range(12)) in coordinates, 'group closure')
    need(orbit == set(range(1, 97)), 'complete 96-choice orbit')
    transports = [transports[i] for i in range(1, 97)]
    check_coverage(transports, choices)
    recipe = dict(schema='SIX_PRISM_FIRST_CHOICE_NORMALIZATION_V1', base_cnf=key(BASE/'instance.cnf'),
        base_cnf_sha256=PINS[BASE/'instance.cnf'], base_model=key(BASE/'model.json'),
        base_model_sha256=PINS[BASE/'model.json'], variables=245880, clauses=874801,
        base_clauses=874800, unit_clauses=[[1]], normalized_column=0, normalized_C0_pair=[0, 2],
        normalized_choice_id=1, scope='Only the fixed identity-cross six-prism core factor family.',
        target_automorphism_assumed=False, literal_auxiliary_permutation_claimed=False,
        transformed_auxiliaries='Recompute exact prefix states from transformed primary choices.',
        independent_approval=False, residual_D_encoded=False, target_graph_encoded=False)
    check_unit(recipe)
    corruptions = []
    wrong = list(range(36))
    wrong[4], wrong[5] = wrong[5], wrong[4]
    corruptions.append(rejected(lambda: check_core_map(wrong, c, gram)))
    wrong = list(range(36)); wrong[0] = wrong[1]
    corruptions.append(rejected(lambda: check_core_map(wrong, c, gram)))
    corruptions.append(rejected(lambda: check_coverage(transports[:-1], choices)))
    changed = copy.deepcopy(transports[1]); changed['row_map'] = list(range(36))
    corruptions.append(rejected(lambda: check_transport(changed, choices)))
    changed = copy.deepcopy(transports[0]); changed['column_map'][0] = 1
    corruptions.append(rejected(lambda: check_transport(changed, choices)))
    changed = copy.deepcopy(transports[0]); changed['primary_choice_map'][0] = 2
    corruptions.append(rejected(lambda: check_transport(changed, choices)))
    for field, value in [('unit_clauses', [[-1]]), ('unit_clauses', [[2]]), ('clauses', 874800), ('base_cnf_sha256', '0'*64)]:
        changed = dict(recipe); changed[field] = value
        corruptions.append(rejected(lambda changed=changed: check_unit(changed)))
    save(out/'group_actions.json', dict(schema='SIX_PRISM_SIGNED_SUBGROUP_V1', actions=actions,
        inverse_group_ids=inverse_ids, full_group_order=384, orbit_choice_ids=sorted(orbit),
        stabilizer_of_choice1_group_ids=[g['group_id'] for g in actions if g['first_column_choice_map'][0] == 1]))
    save(out/'coverage_transports.json', dict(schema='SIX_PRISM_CHOICE1_TRANSPORTS_V1', transports=transports))
    save(out/'model.json', recipe)
    save(out/'controls.json', dict(status='PRODUCER_NORMALIZATION_CONTROLS_PASS', rejected_corruptions=len(corruptions),
        complete_group_compositions_checked=384*384, complete_primary_choice_images_checked=384*5760,
        complete_equation_images_checked=384*540, known_positive_identity_map=True,
        known_positive_all_transports=True, full_research_factor_positive_available=False,
        unavailable_positive_reason='Relabelling identities use raw finite objects, not an assumed 36x60 witness.'))
    cnf = out/'instance.cnf'
    with (BASE/'instance.cnf').open('rb') as source, cnf.open('xb') as target:
        need(source.readline() == b'p cnf 245880 874800\n', 'exact base header')
        target.write(b'p cnf 245880 874801\n')
        shutil.copyfileobj(source, target)
        target.write(b'1 0\n')
    with (BASE/'instance.cnf').open('rb') as source, cnf.open('rb') as target:
        source.readline(); need(target.readline() == b'p cnf 245880 874801\n', 'new exact header')
        for block in iter(lambda: source.read(1048576), b''):
            need(target.read(len(block)) == block, 'byte-identical base clause body')
        need(target.read() == b'1 0\n', 'exact sole appended unit')
    cap.check()
    packed = [package(p, cap) for p in [cnf, out/'coverage_transports.json']]
    save(out/'artifact_packages.json', dict(packages=packed,
        recovery='Concatenate ordered gzip parts, decompress, compare original byte length and SHA256.'))
    summary = dict(status='CANDIDATE_SIX_PRISM_FIRST_CHOICE_NORMALIZATION', timestamp=datetime.now(timezone.utc).isoformat(),
        independent_approval=False, group_order=384, first_column_choices=96, orbit_size=96,
        choice1_stabilizer_size=4, coverage_transports=96, equations_per_map=540, primary_variables=5760,
        variables=245880, clauses=874801, appended_clauses=1, solver_calls=0,
        controls_rejected=len(corruptions), inputs_sha256=inputs,
        elapsed_seconds=time.monotonic()-cap.start, peak_working_set_bytes=cap.peak_bytes,
        target_resolution=False, scope='Existence-preserving relabelling in the fixed six-prism core factor family only.',
        limitations=['No nontrivial factor or target automorphism is assumed.',
                     'Prefix auxiliaries are recomputed, not asserted to permute literally.',
                     'No column-overlap caps or residual D added; no full target graph.',
                     'Independent normalization and exact artifact gates required before solver launch.'],
        outputs={key(p): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file()})
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('inputs_sha256', 'outputs', 'limitations')}))


if __name__ == '__main__':
    main()
