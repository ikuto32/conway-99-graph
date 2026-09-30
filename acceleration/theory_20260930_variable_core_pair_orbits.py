"""Candidate complete ordered matching-pair normalization, with explicit transports."""
from collections import deque
from copy import deepcopy
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
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import ResourceCap, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
CENSUS = B/'20260930_triangle_matching_pair_census_v2'
FIRST = B/'20260930_variable_core_m1_orbits'
BASE = B/'20260930_variable_core_factor_cnf'
GATES = {
    B/'20260930_independent_review/triangle_matching_pair_census/summary.json':
        '085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79',
    B/'20260930_independent_review/variable_core_m1_orbits/summary.json':
        'ef13877c79a1115cf34a105a9704bb58c0ad981189dfe6acda9b4de4a27d6584',
    B/'20260930_independent_review/variable_core_factor_cnf_v2/summary.json':
        'ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
    B/'20260930_independent_review/unrestricted_triangle_factor/summary.json':
        'a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd',
}


def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()


def need(ok, message):
    if not ok: raise ValueError(message)


def conjugate(m, h):
    result = [0]*len(m)
    for a, b in enumerate(m): result[h[a]] = h[b]
    return tuple(result)


def inverse(h):
    result = [0]*len(h)
    for a, b in enumerate(h): result[b] = a
    return tuple(result)


def transport_check(record, m0, m1, source, target, labels):
    h = record['coordinate_permutation']
    need(len(h) == 12 and sorted(h) == list(range(12)), 'stabilizer transport is a permutation')
    need(conjugate(m0, h) == m0 and conjugate(m1, h) == m1, 'stabilizer fixes both M0 and first representative')
    need(conjugate(source, h) == target, 'second matching sent to exact representative')
    need(sorted(tuple(sorted((h[a], h[b]))) for a, b in labels) == labels, 'all canonical C0 columns permuted')


def composed_check(q1, q2, h, k, r1, r2):
    composed = tuple(k[h[a]] for a in range(12))
    need(conjugate(q1, composed) == r1 and conjugate(q2, composed) == r2, 'composed matching-pair transport')
    need(conjugate(tuple(a ^ 1 for a in range(12)), composed) == tuple(a ^ 1 for a in range(12)), 'composed map fixes M0')
    return composed


def selector_controls():
    matchings = [(1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0)]
    pairs = list(product(matchings, repeat=2)); labels = list(combinations(range(4), 2))
    edges = {(g, a, b): 1+6*g+d for g in range(2) for d, (a, b) in enumerate(labels)}
    selectors = list(range(13, 22)); clauses = [selectors]
    for variable, pair in zip(selectors, pairs):
        clauses.extend([[-variable, edges[g, a, b]] for g, q in enumerate(pair) for a, b in labels if q[a] == b])
    cases = 0
    for index, pair in enumerate(pairs):
        base = {edges[g, a, b]: int(q[a] == b) for g, q in enumerate(pair) for a, b in labels}
        for bits in product((0, 1), repeat=9):
            values = {**base, **dict(zip(selectors, bits))}
            actual = all(any(values[abs(v)] == int(v > 0) for v in clause) for clause in clauses)
            need(actual == (bits == tuple(int(i == index) for i in range(9))), 'exhaustive small pair-selector semantics')
            cases += 1
    return dict(ordered_matching_pairs=9, selector_bit_assignments_per_pair=512,
                exhaustive_cases=cases, positive_unique_selector_cases=9)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False); cap = ResourceCap(); bindings = {}
    for path, expected in GATES.items():
        need(digest(path) == expected, 'frozen independent gate'); bindings[key(path)] = expected
        gate = json.loads(path.read_bytes())
        for p, value in gate['inputs_sha256'].items():
            need(digest(ROOT/p) == value, 'premise input '+p); bindings[p] = value
    for p in [Path(__file__), Path(__file__).with_name('theory_20260930_variable_core_pair_orbits_spec.md'),
              ROOT/'acceleration/theory_20260930_eight_full99_cnf.py', ROOT/'acceleration/theory_20260930_full_srg_validator.py',
              ROOT/'uv.lock', ROOT/'pyproject.toml']:
        bindings[key(p)] = digest(p)
    save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(), inputs_sha256=bindings,
        scope='Universal necessary arbitrary-core factor with M1/M2 normalized simultaneously; P remains arbitrary.',
        limits=dict(seconds=120, memory_bytes=8*1024**3, solver_calls=0), random_seed=None,
        random_seed_reason='Deterministic traversal of all frozen second-stage census orbits.', independent_approval=False))
    controls = selector_controls()
    matchings = [tuple(q) for q in json.loads((CENSUS/'matchings.json').read_bytes())]
    lookup = {q: i for i, q in enumerate(matchings)}
    need(len(lookup) == 10395, 'complete bound matching universe')
    m0 = tuple(a ^ 1 for a in range(12)); labels = [p for p in combinations(range(12), 2) if p[1] != (p[0] ^ 1)]
    first = json.loads((FIRST/'transports.json').read_bytes())
    need(len(first['records']) == 10395 and first['M0'] == list(m0), 'bound first-stage transports')
    pair_representatives, stage_records, stages = [], [], []
    for stage_id in tqdm(range(11), desc='complete stabilizer transports'):
        source_path = CENSUS/f'stage_{stage_id:02d}.json'; stage = json.loads(source_path.read_bytes())
        m1 = tuple(stage['M1']); generators = [tuple(g) for g in stage['stabilizer_generators']]
        need(list(m1) == first['representatives'][stage_id], 'first representative order')
        need(all(conjugate(m0, g) == m0 and conjugate(m1, g) == m1 for g in generators), 'all generators stabilize premise matchings')
        records = {}; group_representatives = []
        for local, orbit in enumerate(stage['second_orbits']):
            rep = tuple(orbit['representative']); global_id = len(pair_representatives)
            pair_representatives.append(dict(pair_representative_index=global_id, first_stage=stage_id,
                second_orbit=local, M1=list(m1), M2=list(rep)))
            group_representatives.append(global_id)
            todo = deque([(rep, tuple(range(12)))]); seen = {rep}
            while todo:
                matching, forward = todo.popleft(); back = inverse(forward); index = lookup[matching]
                need(index not in records, 'second-stage orbit disjointness')
                record = dict(matching_index=index, pair_representative_index=global_id,
                    second_orbit=local, coordinate_permutation=list(back))
                transport_check(record, m0, m1, matching, rep, labels)
                records[index] = record
                for g in generators:
                    next_matching = conjugate(matching, g)
                    if next_matching not in seen:
                        seen.add(next_matching); todo.append((next_matching, tuple(g[forward[a]] for a in range(12))))
            need(sorted(lookup[q] for q in seen) == orbit['members'], 'exact frozen second-orbit membership')
        need(set(records) == set(range(10395)), 'complete second-stage matching coverage')
        ordered = [records[i] for i in range(10395)]; stage_records.append(ordered)
        output = out/f'stage_{stage_id:02d}_transports.json'
        save(output, dict(first_stage=stage_id, M1=list(m1), source_stage=key(source_path), source_stage_sha256=digest(source_path),
            matching_universe_path=key(CENSUS/'matchings.json'), matching_universe_sha256=digest(CENSUS/'matchings.json'),
            pair_representative_indices=group_representatives, records=ordered, records_count=10395,
            P_restriction=False, coordinate_action='Apply the saved map simultaneously to all three fibres.'))
        stages.append(dict(first_stage=stage_id, transports_path=key(output), transports_sha256=digest(output),
            pair_representatives=len(group_representatives), covered_second_matchings=10395,
            first_orbit_size=stage['first_orbit_size']))
        cap.check()
    need(len(pair_representatives) == 3580 and len({(tuple(r['M1']), tuple(r['M2'])) for r in pair_representatives}) == 3580, 'exact distinct representative pairs')
    composed_controls = []
    for record in first['records']:
        index = record['matching_index']; stage_id = record['representative']; h = record['coordinate_permutation']
        second_index = (37*index+997) % 10395
        moved_second = conjugate(matchings[second_index], h)
        second = stage_records[stage_id][lookup[moved_second]]
        target = pair_representatives[second['pair_representative_index']]
        combined = composed_check(matchings[index], matchings[second_index], h, second['coordinate_permutation'],
            tuple(target['M1']), tuple(target['M2']))
        composed_controls.append(dict(first_matching_index=index, second_matching_index=second_index,
            first_stage=stage_id, normalized_second_matching_index=lookup[moved_second],
            pair_representative_index=target['pair_representative_index'], composed_coordinate_permutation=list(combined)))
    need(sum(s['first_orbit_size']*s['covered_second_matchings'] for s in stages) == 108056025, 'exact weighted labelled-pair coverage')
    save(out/'composition_controls.json', dict(selection='For each first matching index i, second matching index=(37*i+997) mod10395.',
        count=len(composed_controls), records=composed_controls, exhaustive_labelled_pair_check=False,
        limitation='These are composition controls. Complete coverage follows from all first-stage transports, all second-stage transports, and matching-universe bijectivity.'))
    save(out/'coverage.json', dict(schema='ARBITRARY_CORE_ORDERED_MATCHING_PAIR_COVERAGE_V1',
        first_transports_path=key(FIRST/'transports.json'), first_transports_sha256=digest(FIRST/'transports.json'),
        first_transport_audit=key(next(p for p in GATES if '/variable_core_m1_orbits/' in p.as_posix())),
        first_transport_audit_sha256='ef13877c79a1115cf34a105a9704bb58c0ad981189dfe6acda9b4de4a27d6584',
        matching_universe=10395, first_stages=11, second_transport_records=114345, stages=stages,
        pair_representatives=pair_representatives, complete_labelled_pair_population=108056025,
        population_materialized=False, composition='For original(M1,M2), use first map h, look up h*M2*h^-1 in stage s, then use k; final map is k composed with h.',
        exact_scope='Ordered M1/M2 modulo simultaneous relabelling preserving M0; P stays arbitrary.'))
    model = json.loads((BASE/'model.json').read_bytes())
    ids = {(r['fibre'], *r['endpoints']): r['id'] for r in model['matching_variables']}
    need(len(ids) == 132 and model['variables'] == 110904 and model['clauses'] == 518160, 'original base matching variables')
    selectors = list(range(110905, 114485)); clauses = [selectors]
    for selector, rep in zip(selectors, pair_representatives):
        for fibre in (1, 2):
            q = rep[f'M{fibre}']
            clauses += [[-selector, ids[fibre, a, q[a]]] for a in range(12) if a < q[a]]
    need(len(clauses) == 42961, 'one disjunction and twelve implications per representative')
    extension = dict(schema='ARBITRARY_CORE_ORDERED_MATCHING_PAIR_ORBIT_EXTENSION_V1',
        base_cnf_path=key(BASE/'instance.cnf'), base_cnf_sha256=digest(BASE/'instance.cnf'),
        base_model_path=key(BASE/'model.json'), base_model_sha256=digest(BASE/'model.json'),
        variables=114484, clauses=561121, selectors=selectors, representative_pairs=pair_representatives,
        appended_clauses=clauses, coverage_path=key(out/'coverage.json'), coverage_sha256=digest(out/'coverage.json'),
        P_restricted=False, component_restrictions=False, target_automorphism_assumed=False, residual_D_included=False,
        equivalence='Equisatisfiable up to complete ordered-matching-pair relabelling; not pointwise equality of primary assignments.',
        independent_approval=False)
    save(out/'extension.json', extension)
    cnf = out/'instance.cnf'
    suffix = b''.join((' '.join(map(str, c))+' 0\n').encode() for c in clauses)
    with (BASE/'instance.cnf').open('rb') as source, cnf.open('xb') as dest:
        need(source.readline() == b'p cnf 110904 518160\n', 'exact original base header')
        dest.write(b'p cnf 114484 561121\n'); shutil.copyfileobj(source, dest); dest.write(suffix)
    with (BASE/'instance.cnf').open('rb') as source, cnf.open('rb') as dest:
        source.readline(); need(dest.readline() == b'p cnf 114484 561121\n', 'exact extension header')
        for chunk in iter(lambda: source.read(1048576), b''): need(dest.read(len(chunk)) == chunk, 'byte-identical original base body')
        need(dest.read() == suffix, 'only exact selector suffix')
    negative = []
    def reject(name, call):
        try: call()
        except (ValueError, IndexError, KeyError, TypeError): negative.append(name)
        else: raise ValueError('corrupt control accepted '+name)
    second = stage_records[0][0]; target = pair_representatives[second['pair_representative_index']]
    bad = deepcopy(second); bad['coordinate_permutation'][0] = bad['coordinate_permutation'][1]
    reject('nonbijective_second_transport', lambda: transport_check(bad, m0, tuple(target['M1']), matchings[0], tuple(target['M2']), labels))
    bad = deepcopy(second); bad['coordinate_permutation'] = [0, 2, 1]+list(range(3, 12))
    reject('noncentralizing_second_transport', lambda: transport_check(bad, m0, tuple(target['M1']), matchings[0], tuple(target['M2']), labels))
    reject('wrong_second_representative', lambda: transport_check(second, m0, tuple(target['M1']), matchings[0], matchings[1], labels))
    nontrivial = next(r for r in composed_controls if r['composed_coordinate_permutation'] != list(range(12)) and matchings[r['first_matching_index']] != tuple(pair_representatives[r['pair_representative_index']]['M1']))
    wanted = pair_representatives[nontrivial['pair_representative_index']]
    reject('missing_composition', lambda: composed_check(matchings[nontrivial['first_matching_index']], matchings[nontrivial['second_matching_index']],
        tuple(range(12)), tuple(range(12)), tuple(wanted['M1']), tuple(wanted['M2'])))
    reject('missing_second_record', lambda: need(len(stage_records[0][:-1]) == 10395, 'complete second records'))
    save(out/'controls.json', dict(selector_controls=controls, composed_pair_controls=10395,
        second_transport_checks=114345, canonical_column_images_checked=6860700,
        fresh_corruptions_rejected=negative, self_approval=False))
    cap.check()
    packed = [package(cnf, cap)]
    for path in [out/'extension.json', out/'coverage.json', out/'composition_controls.json', *[out/f'stage_{i:02d}_transports.json' for i in range(11)]]:
        if path.stat().st_size >= 10*1024**2: packed.append(package(path, cap))
    save(out/'artifact_packages.json', dict(packages=packed, recovery='Concatenate each ordered gzip part list, decompress and check original byte length/SHA256.'))
    summary = dict(status='CANDIDATE_VARIABLE_CORE_ORDERED_MATCHING_PAIR_NORMALIZATION',
        independent_verification='PENDING', matching_universe=10395, representative_pairs=3580,
        first_stage_transports_reused=10395, second_stage_transports=114345,
        complete_labelled_ordered_pair_population=108056025, population_materialized=False,
        variables=114484, clauses=561121, appended_variables=3580, appended_clauses=42961,
        P_arbitrary=True, target_automorphism_assumed=False, solver_calls=0, target_resolution=False,
        elapsed_seconds=time.monotonic()-cap.start, peak_working_set_bytes=cap.peak_bytes,
        limitations=['Candidate until separate complete transport/equivalence/byte audit.',
            'No P normalization, residual D or complete target graph.', 'Composition controls are sampled pairs; the two-stage complete coverage argument is explicit.'],
        outputs={key(p): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file()})
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('outputs', 'limitations')}))


if __name__ == '__main__': main()
