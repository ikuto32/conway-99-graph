"""Candidate exact-one oriented-triple projection. No solver invocation."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
RAW = B/'20260930_hadamard20_support/six_prism.json'
SUPPORT_GATE = B/'20260930_independent_review/hadamard20_support_v2/summary.json'
GENERAL_GATE = B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json'
PINS = {
    RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    SUPPORT_GATE: 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
    GENERAL_GATE: '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def oriented(triple, direction):
    a, b, c = sorted(triple)
    cycle = [a, b, c] if direction == 0 else [a, c, b]
    arcs = [[cycle[i], cycle[(i+1) % 3]] for i in range(3)]
    phases = {vertex: i for i, vertex in enumerate(cycle)}
    require(all((phases[v]-phases[u]) % 3 == 1 for u, v in arcs), 'literal orientation-to-phase difference')
    return dict(cycle=cycle, directed_arcs=arcs, phases_by_coordinate={str(a): phases[a] for a in sorted(triple)})


def choices(support):
    require(support == sorted(set(support)) and len(support) == 6, 'six sorted coordinates')
    result = []
    for tail in combinations(support[1:], 2):
        positive = [support[0], *tail]
        negative = [a for a in support if a not in positive]
        for a, b in product(range(2), repeat=2):
            p, n = oriented(positive, a), oriented(negative, b)
            parity = [int(x in negative) for x in support]
            phases = [int((p if x in positive else n)['phases_by_coordinate'][str(x)]) for x in support]
            result.append(dict(choice_index=len(result), positive_triple=positive, negative_triple=negative,
                orientation_bits=[a, b], positive_cycle=p['cycle'], negative_cycle=n['cycle'],
                directed_arcs=p['directed_arcs']+n['directed_arcs'], normalized_parity_pattern=parity,
                local_phase_representative=phases))
    require(len(result) == 40 and len({tuple(tuple(x) for x in r['directed_arcs']) for r in result}) == 40, 'forty unique oriented choices')
    return result


def exact_one(ids):
    yield list(ids)
    for a, b in combinations(ids, 2):
        yield [-a, -b]


def satisfied(clauses, values):
    return all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)


def controls():
    truth_cases = 0
    for n in range(1, 7):
        clauses = list(exact_one(list(range(1, n+1))))
        for mask in range(1 << n):
            values = {i+1: bool(mask & (1 << i)) for i in range(n)}
            require(satisfied(clauses, values) == (mask.bit_count() == 1), 'complete exact-one truth table')
            truth_cases += 1
    options = choices(list(range(6)))
    for item in options:
        phases, pattern = item['local_phase_representative'], item['normalized_parity_pattern']
        require(pattern[0] == 0 and sum(pattern) == 3 and phases[0] == 0, 'normalized local gauge')
        require(all(sorted(phases[i] for i in range(6) if pattern[i] == sign) == [0, 1, 2] for sign in (0, 1)), 'both local phase triples')
        require(len(item['directed_arcs']) == 6 and len(set(map(tuple, item['directed_arcs']))) == 6, 'six local arcs')
        for u, v in item['directed_arcs']:
            require((phases[v]-phases[u]) % 3 == 1, 'local raw phase direction')
    faces = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
    arcs = Counter((face[i], face[(i+1) % 3]) for face in faces for i in range(3))
    require(arcs == Counter({(a, b): 1 for a in range(4) for b in range(4) if a != b}), 'generic tetrahedron oriented cover control')
    bad = faces[:]
    bad[0] = [0, 2, 1]
    require(Counter((face[i], face[(i+1) % 3]) for face in bad for i in range(3)) != arcs, 'one reversed face rejected')
    require(not satisfied(list(exact_one([1, 2, 3])), {1: True, 2: True, 3: False}), 'two chosen selectors rejected')
    phases = options[0]['local_phase_representative'][:]
    phases[1] = (phases[1]+1) % 3
    require(any((phases[v]-phases[u]) % 3 != 1 for u, v in options[0]['directed_arcs']), 'changed local phase rejected')
    corrupt = arcs.copy()
    corrupt[0, 1] += 1
    require(corrupt != arcs, 'duplicate directed arc rejected')
    return dict(exact_one_truth_cases=truth_cases, local_oriented_choices=len(options), tetrahedron_faces=faces,
        positive_control_scope='Generic local phase/arc checks and tetrahedron directed cover only; no full research factor or research oriented-cover witness.',
        corruptions_rejected=['two_true_onehot', 'reversed_tetrahedron_face', 'changed_local_phase', 'duplicate_directed_arc'])


def build_scope(raw):
    L = raw['L']
    supports = [[a for a in range(12) if L[a][d]] for d in range(60)]
    groups = []
    for support in supports:
        if support not in groups:
            groups.append(support)
    require(len(groups) == 20 and all(supports.count(g) == 3 and len(g) == 6 for g in groups), 'twenty six-coordinate triple supports')
    require(all(sum(x in g for x in (2*a, 2*a+1)) == 1 for g in groups for a in range(6)), 'one coordinate per fixed component pair')
    arcs = [[a, b] for a in range(12) for b in range(12) if a != b and a ^ 1 != b]
    require(len(arcs) == 120 and all(sum(a in g and b in g for g in groups) == 5 for a, b in arcs), 'five supports per allowed coordinate pair')
    return dict(schema='FIXED_HADAMARD_ALL_MIXED_ORIENTED_TRIPLE_SCOPE_V1', raw_support_path=key(RAW), raw_support_sha256=PINS[RAW],
        coordinate_matching=[a ^ 1 for a in range(12)], L12x60=L, support_columns=supports, groups=groups, directed_arcs=arcs,
        balance_is_additional_assumption=True, all_groups_mixed=True, local_even_phase_screen_only=True,
        odd_phase_equations_encoded=False, outside_column_caps_encoded=False, full_factor=False, target_graph=False,
        residual_D=None, residual_D_null_reason='No residual completion is part of this projection.',
        scope='All oriented same-sign triples on one frozen support; exact equivalent local mixed/even-phase screen, pending independent review. No claim of arbitrary-factor coverage.')


def build_model(scope):
    domains = []
    for g, support in enumerate(scope['groups']):
        options = choices(support)
        for item in options:
            item['selector'] = 40*g+item['choice_index']+1
        domains.append(dict(group=g, support=support, choices=options))
    rows = []
    for domain in domains:
        rows.append(dict(index=len(rows), kind='group_exact_one', group=domain['group'], selectors=[x['selector'] for x in domain['choices']], rhs=1))
    for arc in scope['directed_arcs']:
        selectors = [item['selector'] for domain in domains for item in domain['choices'] if arc in item['directed_arcs']]
        require(len(selectors) == 40, 'forty options per directed arc')
        rows.append(dict(index=len(rows), kind='directed_arc_exact_one', directed_arc=arc, selectors=selectors, rhs=1))
    clause = 1
    for row in rows:
        require(len(row['selectors']) == 40, 'forty selectors each row')
        row['first_clause'] = clause
        row['clause_count'] = 1+40*39//2
        clause += row['clause_count']
    require(len(rows) == 140 and clause-1 == 109340, 'derived exact model dimensions')
    return dict(schema='FIXED_HADAMARD_ALL_MIXED_ORIENTED_TRIPLE_CNF_V1', variables=800, clauses=clause-1,
        primary_selectors=800, auxiliary_variables=0, domains=domains, exact_one_rows=rows,
        clause_order='20 groups then120 directed arcs; positive row then lexicographic negative selector pairs',
        scope_sha256=None, scope_sha256_null_reason='Filled when the immutable scope is saved.', independent_approval=False)


def decode(assignment, model_path, scope_path):
    model, scope = read(model_path), read(scope_path)
    require(model['scope_sha256'] == digest(scope_path), 'exact decoder scope identity')
    values = {}
    for lit in assignment:
        require(type(lit) is int and lit != 0 and abs(lit) not in values, 'unique signed integer IDs')
        values[abs(lit)] = lit > 0
    require(set(values) == set(range(1, 801)), 'complete800-ID assignment')
    selected = []
    for domain in model['domains']:
        active = [x for x in domain['choices'] if values[x['selector']]]
        require(len(active) == 1, 'one oriented choice per group')
        selected.append(active[0])
    counts = Counter(tuple(arc) for choice in selected for arc in choice['directed_arcs'])
    require(counts == Counter({tuple(arc): 1 for arc in scope['directed_arcs']}), 'all120 directed arcs exactly once')
    for row in model['exact_one_rows']:
        require(sum(values[i] for i in row['selectors']) == 1, 'every exact-one model row')
    return dict(selected_selector_ids=[x['selector'] for x in selected], selected_choices=selected,
        selected_group_parity_patterns=[x['normalized_parity_pattern'] for x in selected],
        directed_arc_counts=[dict(arc=arc, count=counts[tuple(arc)]) for arc in scope['directed_arcs']],
        model_sha256=digest(model_path), scope_sha256=digest(scope_path), full_factor=False, target_graph=False,
        odd_phase_equations_checked=False, outside_column_caps_checked=False, residual_D=None,
        independent_approval=False, scope='Oriented local/even-phase cover only; twenty negative-triple offsets remain to be solved.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        for path, sha in PINS.items():
            require(digest(path) == sha, 'frozen input '+key(path))
        inputs = {key(p): h for p, h in PINS.items()}
        for path in [Path(__file__), Path(__file__).with_name('theory_20260930_hadamard_oriented_triples_spec.md'), ROOT/'uv.lock', ROOT/'pyproject.toml']:
            inputs[key(path)] = digest(path)
        save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs,
            status='PREREGISTERED_CANDIDATE_BUILD', limits=dict(seconds=30, solver_calls=0), selection_rule='All ten unordered partitions and both orientations independently for both triples in every one of20 groups.'))
        save(out/'controls.json', controls())
        scope = build_scope(read(RAW))
        save(out/'scope.json', scope)
        model = build_model(scope)
        model['scope_sha256'] = digest(out/'scope.json')
        model['scope_sha256_null_reason'] = None
        save(out/'model.json', model)
        emitted = 0
        with (out/'instance.cnf').open('x', encoding='ascii', newline='\n') as stream:
            stream.write('p cnf 800 109340\n')
            for row in model['exact_one_rows']:
                require(emitted+1 == row['first_clause'], 'exact row clause offset')
                for clause in exact_one(row['selectors']):
                    stream.write(' '.join(map(str, clause))+' 0\n')
                    emitted += 1
        require(emitted == model['clauses'], 'all emitted clauses')
        require(time.monotonic()-started < 30, 'build allocation')
        summary = dict(status='CANDIDATE_ALL_MIXED_ORIENTED_TRIPLE_CNF_BUILT', timestamp=datetime.now(timezone.utc).isoformat(),
            inputs_sha256=inputs, outputs_sha256={key(p): digest(p) for p in out.iterdir() if p.is_file()},
            variables=800, clauses=emitted, group_domains=20, choices_per_group=40, directed_arc_rows=120, exact_one_rows=140,
            solver_calls=0, independent_approval=False, target_resolution=False, elapsed_seconds=time.monotonic()-started,
            scope=scope['scope'], artifact_availability='LOCAL_ONLY')
        save(out/'summary.json', summary)
        print(json.dumps(summary))
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), source_sha256=digest(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
