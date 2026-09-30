"""Independent complete transport/normalization and appended-CNF audit."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import io
import json
import platform
import subprocess
import sys
import time
import audit_20260930_full99_sat_object as common

ROOT = Path(__file__).resolve().parents[1]
OUTBASE = ROOT/'acceleration/results/20260930_variable_core_m1_orbits'
BASE = ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
CENSUS = ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2'
PROOF = ROOT/'docs/AUDIT_20260930_VARIABLE_CORE_M1_ORBITS.md'
GATES = {
    ROOT/'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json':
        ('085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79', None),
    ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json':
        ('ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0', 'INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS'),
    ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json':
        ('a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd', 'INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS'),
}
PINS = {
    BASE/'instance.cnf': '21b2cd8067971da66317afb3814e2b4f9232528fc8b1daceda4ff80594425684',
    BASE/'model.json': '42071b881973450db0f1813356133688b7532dd7d0495d37962acc5fa8c071f2',
    BASE/'scope.json': 'd5366bd061ab9f248d861522241fd28862f7164f591788f859bba90c91936d60',
    OUTBASE/'instance.cnf': 'eeb0c60c111ac6f5f04cb225f072a0812dd88099096802bad3be1788e95fe6d1',
    OUTBASE/'transports.json': '07097877ab86662d86ba85f2c9c2326fc21032cc04eba235bb76788c7cbebe91',
    OUTBASE/'extension.json': 'e725d37f9fd6f4cbc4685db95ec1b609d3582ab61dca2047eb5289acfb1e3005',
    ROOT/'acceleration/audit_20260930_full99_sat_object.py': '65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
}
need, read, save, digest, key = common.need, common.read, common.save, common.digest, common.key


def enumerate_matchings(vertices):
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for b in vertices[1:]:
        for tail in enumerate_matchings(tuple(v for v in vertices[1:] if v != b)):
            yield ((a, b),)+tail


def valid_matching(q):
    need(type(q) is list and len(q) == 12 and all(type(x) is int and 0 <= x < 12 for x in q), 'matching types')
    need(all(q[i] != i and q[q[i]] == i for i in range(12)), 'perfect matching involution')


def validate_transport(record, matchings, representatives, labels):
    index = record['matching_index']; stage = record['representative']; h = record['coordinate_permutation']
    need(type(index) is int and 0 <= index < len(matchings) and type(stage) is int and 0 <= stage < 11, 'record indices')
    need(type(h) is list and len(h) == 12 and all(type(x) is int for x in h) and sorted(h) == list(range(12)), 'coordinate bijection')
    need(all(h[a ^ 1] == (h[a] ^ 1) for a in range(12)), 'centralizes standard M0')
    q, rep = matchings[index], representatives[stage]
    need(all(rep[h[a]] == h[q[a]] for a in range(12)), 'literal source matching edge transport')
    images = [tuple(sorted((h[a], h[b]))) for a, b in labels]
    need(sorted(images) == labels, 'complete canonical C0 column bijection')
    columns = {p: i for i, p in enumerate(labels)}
    return [columns[p] for p in images]


def signature(q):
    unseen = set(range(12)); sizes = []
    while unseen:
        seed = min(unseen); todo = [seed]; component = {seed}
        while todo:
            a = todo.pop()
            for b in (a ^ 1, q[a]):
                if b not in component:
                    component.add(b); todo.append(b)
        unseen -= component
        need(len(component) % 2 == 0, 'even alternating component')
        sizes.append(len(component)//2)
    return tuple(sorted(sizes))


def integer_partitions(total, minimum=1):
    if not total:
        yield ()
    else:
        for a in range(minimum, total+1):
            for tail in integer_partitions(total-a, a):
                yield (a,)+tail


def validate_coverage(records, matchings, representatives, labels):
    need(len(records) == 10395 and sorted(r['matching_index'] for r in records) == list(range(10395)), 'every matching exactly once')
    columns = []
    for record in records:
        columns.append(validate_transport(record, matchings, representatives, labels))
    return columns


def build_suffix(base_model, representatives):
    entries = [r for r in base_model['matching_variables'] if r['fibre'] == 1]
    ids = {tuple(r['endpoints']): r['id'] for r in entries}
    need(len(ids) == 66 and set(ids) == set(combinations(range(12), 2)), 'complete M1 edge labels')
    selectors = list(range(110905, 110916))
    clauses = [selectors]
    for i, rep in enumerate(representatives):
        clauses += [[-selectors[i], ids[a, b]] for a, b in combinations(range(12), 2) if rep[a] == b]
    need(len(clauses) == 67, 'six implications per representative')
    return clauses, ids


def suffix_semantics(matchings, representatives):
    rep_edges = [{(a, q[a]) for a in range(12) if a < q[a]} for q in representatives]
    allowed = Counter()
    for q in matchings:
        actual = {(a, q[a]) for a in range(12) if a < q[a]}
        compatible = [i for i, edges in enumerate(rep_edges) if edges <= actual]
        equal = [i for i, rep in enumerate(representatives) if q == rep]
        need(compatible == equal and len(equal) <= 1, 'selector implications exact representative test')
        allowed[len(equal)] += 1
    cases = 0
    for i, edges in enumerate(rep_edges):
        for bits in product((0, 1), repeat=11):
            satisfies = any(bits) and all(not bits[j] or rep_edges[j] <= edges for j in range(11))
            need(satisfies == (bits == tuple(int(j == i) for j in range(11))), 'complete selector Boolean semantics')
            cases += 1
    return dict(all_matching_cases=len(matchings), representative_cases=allowed[1],
                nonrepresentative_cases=allowed[0], exhaustive_selector_assignments=cases)


def compare_bytes(base, extended, clauses, base_vars=110904, base_clauses=518160, extra_vars=11):
    need(base.readline() == f'p cnf {base_vars} {base_clauses}\n'.encode(), 'exact base header')
    need(extended.readline() == f'p cnf {base_vars+extra_vars} {base_clauses+len(clauses)}\n'.encode(), 'exact extension header')
    n = 0
    for block in iter(lambda: base.read(1048576), b''):
        need(extended.read(len(block)) == block, 'byte-identical complete base body'); n += len(block)
    expected = b''.join((' '.join(map(str, row))+' 0\n').encode() for row in clauses)
    need(extended.read() == expected, 'only exact independent 67-clause suffix')
    return dict(base_body_bytes=n, suffix_bytes=len(expected), suffix_clauses=len(clauses))


def covariance_controls(records, representatives, labels):
    # Literal identities on arbitrary matrices; these do not assert feasibility.
    cases = []
    for stage in range(11):
        record = next(r for r in reversed(records) if r['representative'] == stage)
        h = record['coordinate_permutation']; rowmap = [12*g+h[a] for g in range(3) for a in range(12)]
        cols = {p: d for d, p in enumerate(labels)}
        colmap = [cols[tuple(sorted((h[a], h[b])))] for a, b in labels]
        q1 = representatives[(stage+3) % 11]; q2 = representatives[(stage+7) % 11]
        p = [(5*a+stage) % 12 for a in range(12)]
        core = [[0]*36 for _ in range(36)]
        for g, q in enumerate([[a ^ 1 for a in range(12)], q1, q2]):
            for a in range(12): core[12*g+a][12*g+q[a]] = 1
        for a in range(12):
            for u, v in [(a, 12+a), (a, 24+a), (12+a, 24+p[a])]: core[u][v] = core[v][u] = 1
        f = [[int(a in pair) for pair in labels] for a in range(12)]
        f += [[int((17*i+7*d+stage) % 11 < 5) for d in range(60)] for i in range(24)]
        changed_core = [[0]*36 for _ in range(36)]; changed_f = [[0]*60 for _ in range(36)]
        for a in range(36):
            for b in range(36): changed_core[rowmap[a]][rowmap[b]] = core[a][b]
            for d in range(60): changed_f[rowmap[a]][colmap[d]] = f[a][d]
        need(changed_f[:12] == f[:12], 'literal canonical C0 covariance')
        for a in range(36):
            need(sum(f[a]) == sum(changed_f[rowmap[a]]), 'literal row margin covariance')
            for b in range(36):
                ca, cb = rowmap[a], rowmap[b]
                before = 12*int(a == b)-core[a][b]-sum(core[a][k]*core[k][b] for k in range(36))+2-int(a//12 == b//12)
                after = 12*int(ca == cb)-changed_core[ca][cb]-sum(changed_core[ca][k]*changed_core[k][cb] for k in range(36))+2-int(ca//12 == cb//12)
                need(before == after, 'literal prescribed Gram covariance')
                need(sum(f[a][d]*f[b][d] for d in range(60)) == sum(changed_f[ca][d]*changed_f[cb][d] for d in range(60)), 'literal factor Gram covariance')
            for d in range(60):
                need(f[a][d]+sum(core[a][k]*f[k][d] for k in range(36)) == changed_f[rowmap[a]][colmap[d]]+sum(changed_core[rowmap[a]][k]*changed_f[k][colmap[d]] for k in range(36)), 'literal mixed expression covariance')
        for d in range(60):
            for g in range(3):
                need(sum(f[12*g+a][d] for a in range(12)) == sum(changed_f[12*g+a][colmap[d]] for a in range(12)), 'literal fibre-column margin covariance')
        for d, e in combinations(range(60), 2):
            need(sum(f[a][d]*f[a][e] for a in range(36)) == sum(changed_f[a][colmap[d]]*changed_f[a][colmap[e]] for a in range(36)), 'literal distinct-column cap expression covariance')
        cases.append(dict(stage=stage, matching_index=record['matching_index'], research_witness=False))
    return cases


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    bindings = {}
    for p, expected in PINS.items():
        need(digest(p) == expected, 'frozen input '+key(p)); bindings[key(p)] = expected
    for path, (expected, status) in GATES.items():
        need(digest(path) == expected, 'independent premise gate hash'); gate = read(path)
        if status: need(gate['status'] == status, 'independent premise gate status')
        bindings[key(path)] = expected
        for p, value in gate['inputs_sha256'].items():
            need(digest(ROOT/p) == value, 'premise input identity '+p); bindings[p] = value
    for p in [Path(__file__), PROOF, OUTBASE/'summary.json', OUTBASE/'manifest.json',
              ROOT/'acceleration/theory_20260930_variable_core_m1_orbits.py',
              ROOT/'acceleration/theory_20260930_variable_core_m1_orbits_spec.md', ROOT/'uv.lock', ROOT/'pyproject.toml']:
        bindings[key(p)] = digest(p)
    data = read(OUTBASE/'transports.json'); extension = read(OUTBASE/'extension.json'); model = read(BASE/'model.json')
    universe_file = ROOT/data['matching_universe_path']
    need(digest(universe_file) == data['matching_universe_sha256'], 'recorded matching universe hash')
    bindings[key(universe_file)] = digest(universe_file)
    raw = read(universe_file); matchings = raw['matchings'] if isinstance(raw, dict) else raw
    generated = set()
    for pairs in enumerate_matchings(tuple(range(12))):
        vector = [0]*12
        for a, b in pairs: vector[a] = b; vector[b] = a
        generated.add(tuple(vector))
    need(len(generated) == len(matchings) == 10395 and generated == {tuple(q) for q in matchings}, 'complete independent matching universe')
    reps = data['representatives']; need(len(reps) == 11, 'eleven representatives')
    for q in matchings+reps: valid_matching(q)
    need(data['M0'] == [a ^ 1 for a in range(12)], 'standard matching premise')
    signatures = [signature(q) for q in reps]
    need(len(set(signatures)) == 11 and set(signatures) == set(integer_partitions(6)), 'eleven distinct complete alternating partitions')
    labels = [p for p in combinations(range(12), 2) if p[1] != (p[0] ^ 1)]
    records = data['records']; column_maps = validate_coverage(records, matchings, reps, labels)
    stage_counts = Counter(r['representative'] for r in records)
    for stage in range(11):
        path = CENSUS/f'stage_{stage:02d}.json'; old = read(path); bindings[key(path)] = digest(path)
        need(old['M1'] == reps[stage] and old['first_members'] == sorted(r['matching_index'] for r in records if r['representative'] == stage), 'exact prior census first-stage binding')
    clauses, ids = build_suffix(model, reps)
    need(extension['representatives'] == reps and extension['selectors'] == list(range(110905, 110916)), 'selector mapping')
    need(extension['appended_clauses'] == clauses and (extension['variables'], extension['clauses']) == (110915, 518227), 'exact extension recipe')
    need(extension['base_cnf_path'] == key(BASE/'instance.cnf') and extension['base_cnf_sha256'] == digest(BASE/'instance.cnf') and extension['base_model_path'] == key(BASE/'model.json') and extension['base_model_sha256'] == digest(BASE/'model.json'), 'exact base recipe identities')
    need(extension['M2_P_restricted'] is False and extension['automorphism_of_target_assumed'] is False and extension['residual_D_included'] is False and extension['primary_assignments_restricted'] is True, 'scope boundaries')
    semantics = suffix_semantics(matchings, reps)
    with (BASE/'instance.cnf').open('rb') as base, (OUTBASE/'instance.cnf').open('rb') as extended:
        byte_record = compare_bytes(base, extended, clauses)
    literals = covariance_controls(records, reps, labels)
    negative = []
    def reject(name, call):
        try: call()
        except (ValueError, IndexError, KeyError, TypeError): negative.append(name)
        else: raise ValueError('corrupt control accepted '+name)
    reject('missing_transport', lambda: validate_coverage(records[:-1], matchings, reps, labels))
    wrong = deepcopy(records[0]); wrong['coordinate_permutation'][0] = wrong['coordinate_permutation'][1]
    reject('nonbijective_transport', lambda: validate_transport(wrong, matchings, reps, labels))
    wrong = deepcopy(records[0]); wrong['coordinate_permutation'] = list(range(12)); wrong['coordinate_permutation'][1], wrong['coordinate_permutation'][2] = 2, 1
    reject('noncentralizing_transport', lambda: validate_transport(wrong, matchings, reps, labels))
    wrong = deepcopy(records[0]); wrong['representative'] = (wrong['representative']+1) % 11
    reject('wrong_representative', lambda: validate_transport(wrong, matchings, reps, labels))
    reject('fixedpoint_matching', lambda: valid_matching(list(range(12))))
    base = b'p cnf 2 1\n1 2 0\n'; suffix = [[3], [-3, 1]]; good = b'p cnf 3 3\n1 2 0\n3 0\n-3 1 0\n'
    compare_bytes(io.BytesIO(base), io.BytesIO(good), suffix, 2, 1, 1)
    for name, bad in [('changed_base', good.replace(b'1 2 0', b'-1 2 0')), ('changed_sign', good.replace(b'-3 1 0', b'3 1 0')), ('missing_clause', good[:-7]), ('wrong_header', good.replace(b'3 3', b'3 2')), ('extra_clause', good+b'1 0\n')]:
        reject(name, lambda bad=bad: compare_bytes(io.BytesIO(base), io.BytesIO(bad), suffix, 2, 1, 1))
    save(args.out/'controls.json', dict(fresh_corruptions_rejected=negative, known_positive_byte_fixture=True,
        literal_covariance_fixtures=literals, universal_covariance_method='Written index-renaming proof; finite fixtures are controls only.', selector_semantics=semantics))
    save(args.out/'coverage.json', dict(matching_universe=10395, representatives=reps, alternating_signatures=signatures,
        orbit_sizes=[stage_counts[i] for i in range(11)], checked_transports=10395, checked_column_images=10395*60,
        induced_column_maps=column_maps))
    need(all(digest(ROOT/p) == value for p, value in bindings.items()), 'stable bound inputs')
    report = dict(status='INDEPENDENT_VARIABLE_CORE_M1_ORBIT_NORMALIZATION_PASS',
        claim_id='C-VARIABLE-CORE-M1-ELEVEN-ORBIT-NORMALIZATION', claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        verifier='/root/structural_attack independent matching/transport/CNF reviewer', producer_imports=False,
        recommendation='VERIFIED', review_state='CLEAR', kind='encoding', basis=['DERIVED', 'COMPUTED'],
        statement='The exact110915-variable518227-clause formula is equisatisfiable with the audited arbitrary-core factor formula by simultaneous coordinate and canonical-C0-column relabelling, restricting M1 to eleven representatives while M2 and P remain arbitrary.',
        scope='Universal necessary arbitrary-core factor model after harmless labels; SAT is not a completed target graph.',
        assumptions=['Pinned arbitrary-core factor encoding and universal triangle normalization.', 'Exact base matching constraints and prefix-gate semantics.'],
        target_automorphism_assumed=False, dependencies=[
            dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION', revision=1, relation='normalization'),
            dict(evidence=key(BASE/'instance.cnf'), gate_sha256=GATES[next(p for p in GATES if 'variable_core_factor_cnf_v2' in str(p))][0], relation='encoding_equivalence'),
            dict(evidence=key(CENSUS/'summary.json'), gate_sha256=GATES[next(p for p in GATES if 'matching_pair_census' in str(p))][0], relation='coverage')],
        checked_matchings=10395, representatives=11, checked_transports=10395, checked_column_images=623700,
        variables=110915, clauses=518227, added_variables=11, added_clauses=67, byte_comparison=byte_record,
        controls=semantics, fresh_corruptions_rejected=negative, written_derivation=key(PROOF),
        shared_components=['Frozen independent base encoding and normalization gates.', 'Independent standard JSON/hash/require helpers; no producer code.'],
        outputs_sha256={key(p): digest(p) for p in args.out.iterdir() if p.is_file()},
        limitations=['Not pointwise equality of primary assignment sets.', 'No residual D or complete99 graph is provided.', 'Any UNSAT assertion requires a separately replayed complete proof.'],
        solver_calls=0, target_resolution=False, external_review=False, artifact_availability='LOCAL_ONLY', elapsed_seconds=time.monotonic()-start)
    save(args.out/'summary.json', report)
    print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'), elapsed_seconds=report['elapsed_seconds'])))


if __name__ == '__main__': main()
