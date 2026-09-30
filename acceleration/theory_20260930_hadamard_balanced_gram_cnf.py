"""Candidate exact balanced fixed-support Gram model; no solver calls."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
RAW = B/'20260930_hadamard20_support/six_prism.json'
FIXTURE = B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS = {
    RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    FIXTURE: '3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
    B/'20260930_independent_review/hadamard20_support_v2/summary.json': 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
    B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json': '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
    B/'20260930_independent_review/srg243_residual_fixture/summary.json': '28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
}
PERMS = list(permutations(range(3)))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
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


def local_options():
    options = []
    for rest in product(PERMS, repeat=5):
        pi = [(0, 1, 2), *rest]
        words = [[p[x] for p in pi] for x in range(3)]
        if any(word.count(f) != 2 for word in words for f in range(3)):
            continue
        signs = [(p[1]-p[0]) % 3 for p in pi]
        phases = [p[0] for p in pi]
        need(all((signs[i]*x+phases[i]) % 3 == pi[i][x] for i in range(6) for x in range(3)), 'literal affine local maps')
        options.append(dict(choice_index=len(options), coordinate_permutations=[list(p) for p in pi], colour_words=words,
                            signs=signs, phases=phases, normalized_parity_pattern=[int(s == 2) for s in signs]))
    need(len(options) == 150 and sum(not any(o['normalized_parity_pattern']) for o in options) == 30 and sum(sum(o['normalized_parity_pattern']) == 3 for o in options) == 120, 'complete150 local domains')
    return options


def relative(pa, pb):
    return tuple(pb[pa.index(x)] for x in range(3))


def OR(output, inputs):
    return [[-x, output] for x in inputs]+[[-output, *inputs]]


def exact_count(inputs, bound):
    return [[-x for x in subset] for subset in combinations(inputs, bound+1)]+[list(subset) for subset in combinations(inputs, len(inputs)-bound+1)]


def exact_one_prefix(inputs, prefixes):
    need(len(inputs) >= 2 and len(prefixes) == len(inputs)-1, 'prefix dimensions')
    clauses = OR(prefixes[0], inputs[:1])
    for i in range(1, len(prefixes)):
        clauses.extend(OR(prefixes[i], [prefixes[i-1], inputs[i]]))
        clauses.append([-prefixes[i-1], -inputs[i]])
    clauses.extend([[prefixes[-1], inputs[-1]], [-prefixes[-1], -inputs[-1]]])
    return clauses


def satisfied(clauses, values):
    return all(any(values[abs(x)] == (x > 0) for x in clause) for clause in clauses)


def target_gram(core, n):
    return [[n*int(i == j)-core[i][j]-sum(core[i][k]*core[k][j] for k in range(3*n))+2-int(i//n == j//n) for j in range(3*n)] for i in range(3*n)]


def check_factor(F, core, expected, n, expected_L=None):
    columns = len(F[0])
    need(len(F) == 3*n and all(len(r) == columns and all(type(x) is int and x in (0, 1) for x in r) for r in F), 'binary complete factor shape')
    rows = [set(d for d in range(columns) if F[a][d]) for a in range(3*n)]
    sets = [set(a for a in range(3*n) if F[a][d]) for d in range(columns)]
    actual = [[len(a & b) for b in rows] for a in rows]
    need(actual == expected, 'all literal integer Gram entries')
    need(all(len(r) == n-2 for r in rows) and all(sum(F[n*g+a][d] for a in range(n)) == 2 for g in range(3) for d in range(columns)), 'row and fibre margins')
    L = [[sum(F[n*g+a][d] for g in range(3)) for d in range(columns)] for a in range(n)]
    need(expected_L is None or L == expected_L, 'exact prescribed coordinate support')
    caps = [dict(columns=[d, e], overlap=len(sets[d] & sets[e])) for d, e in combinations(range(columns), 2)]
    mixed = [[F[a][d]+sum(core[a][b]*F[b][d] for b in range(3*n)) for d in range(columns)] for a in range(3*n)]
    return dict(actual_Gram=actual, coordinate_support=L, column_pair_records=caps,
        column_cap_violations=[r for r in caps if r['overlap'] > 2],
        mixed_cap_violations=[dict(row=a, column=d, value=mixed[a][d]) for a in range(3*n) for d in range(columns) if mixed[a][d] > 2])


def controls():
    prefix_cases = 0
    for n in range(2, 6):
        prim, aux = list(range(1, n+1)), list(range(n+1, 2*n))
        clauses = exact_one_prefix(prim, aux)
        for mask in range(1 << (2*n-1)):
            values = {i: bool(mask & (1 << (i-1))) for i in range(1, 2*n)}
            expected = sum(values[i] for i in prim) == 1 and all(values[aux[j]] == any(values[i] for i in prim[:j+1]) for j in range(n-1))
            need(satisfied(clauses, values) == expected, 'complete prefix unique-extension truth')
            prefix_cases += 1
    or_cases = 0
    for n in range(1, 5):
        for mask in range(1 << (n+1)):
            values = {i+1: bool(mask & (1 << i)) for i in range(n+1)}
            need(satisfied(OR(n+1, list(range(1, n+1))), values) == (values[n+1] == any(values[i] for i in range(1, n+1))), 'full OR truth')
            or_cases += 1
    for bound in (1, 2):
        for mask in range(32):
            values = {i+1: bool(mask & (1 << i)) for i in range(5)}
            need(satisfied(exact_count(list(range(1, 6)), bound), values) == (mask.bit_count() == bound), 'exact five-bit count truth')
    for pa, pb in product(PERMS, repeat=2):
        rel = relative(pa, pb)
        need(all(rel[pa[x]] == pb[x] for x in range(3)), 'literal relative-permutation orientation')
    fixture = read(FIXTURE)
    F, C = fixture['factor60x180'], fixture['cubic_core60']
    gram = target_gram(C, 20)
    positive = check_factor(F, C, gram, 20)
    need(not positive['column_cap_violations'] and not positive['mixed_cap_violations'], 'actual243 positive generic factor')
    bad = [row[:] for row in F]
    bad[0][0] ^= 1
    try:
        check_factor(bad, C, gram, 20)
    except ValueError:
        pass
    else:
        raise ValueError('corrupted factor accepted')
    need(not satisfied(exact_count([1, 2, 3, 4, 5], 2), {i: i == 1 for i in range(1, 6)}), 'wrong cardinality rejected')
    return dict(prefix_truth_cases=prefix_cases, OR_truth_cases=or_cases, five_bit_count_cases=64,
        relative_permutation_letter_cases=108, local_tuples_enumerated=7776, local_options_retained=150,
        known_positive='Generic SRG243 factor; not a research fixed-support or balanced-family witness.',
        corruptions_rejected=['factor_bit', 'wrong_cell_count'])


def scope_from_raw(raw):
    L = raw['L']
    supports = [[a for a in range(12) if L[a][d]] for d in range(60)]
    groups = []
    for support in supports:
        if support not in groups:
            groups.append(support)
    need(len(groups) == 20 and all(len(g) == 6 and supports.count(g) == 3 for g in groups), 'twenty repeated supports')
    need(all(sum(a in g for a in (2*c, 2*c+1)) == 1 for g in groups for c in range(6)), 'component transversal support')
    need(all(sum(a in g for g in groups) == 10 for a in range(12)), 'ten groups per coordinate')
    pairs = [list(pair) for pair in combinations(range(12), 2) if pair[0] ^ 1 != pair[1]]
    need(len(pairs) == 60 and all(sum(a in g and b in g for g in groups) == 5 for a, b in pairs), 'five shared groups per nonmatched pair')
    C = raw['core_adjacency']
    K = raw['prescribed_Gram36']
    need(K == target_gram(C, 12), 'exact prescribed Gram from raw core')
    return dict(schema='FIXED_HADAMARD_COMPLETE_BALANCED_GRAM_SCOPE_V1', raw_support_path=key(RAW), raw_support_sha256=PINS[RAW],
        core_adjacency36=C, prescribed_Gram36=K, L12x60=L, support_columns=supports, groups=groups,
        group_columns=[[d for d, support in enumerate(supports) if support == g] for g in groups], coordinate_pairs=pairs,
        balance_is_additional_assumption=True, normalization='First coordinate permutation identity by independent relabelling of each group of three equal-support columns.',
        all_normalized_local_options=True, prescribed_Gram_encoded=True, outside_column_caps_encoded=False, residual_D_encoded=False,
        target_graph=False, assumed_target_automorphism=None, assumed_target_automorphism_null_reason='No target automorphism is assumed.',
        scope='All normalized balanced36x60 factors on this one fixedL with the full prescribed integer Gram; outside caps and residualD omitted.')


def build(scope, options):
    clauses, domains, onehots, channels, cells = [], [], [], [], []
    nextvar = 3001

    def fresh():
        nonlocal nextvar
        value = nextvar
        nextvar += 1
        return value

    def append(section):
        start = len(clauses)+1
        clauses.extend(section)
        return dict(first_clause=start, clause_count=len(section))

    for g, support in enumerate(scope['groups']):
        choices = []
        for option in options:
            item = {**option, 'selector': 150*g+option['choice_index']+1}
            item['lifted_rows'] = [[12*word[i]+support[i] for i in range(6)] for word in option['colour_words']]
            choices.append(item)
        domains.append(dict(group=g, support=support, columns=scope['group_columns'][g], choices=choices))
    for domain in domains:
        ids = [x['selector'] for x in domain['choices']]
        prefixes = [fresh() for _ in range(149)]
        onehots.append(dict(group=domain['group'], selectors=ids, prefixes=prefixes, **append(exact_one_prefix(ids, prefixes))))
    for a, b in scope['coordinate_pairs']:
        incident = [g for g, support in enumerate(scope['groups']) if a in support and b in support]
        for g in incident:
            support = scope['groups'][g]
            ia, ib = support.index(a), support.index(b)
            for pi in PERMS:
                ids = [x['selector'] for x in domains[g]['choices'] if relative(x['coordinate_permutations'][ia], x['coordinate_permutations'][ib]) == pi]
                output = fresh()
                channels.append(dict(coordinates=[a, b], group=g, permutation=list(pi), variable=output, selectors=ids, **append(OR(output, ids))))
    lookup = {(tuple(c['coordinates']), c['group'], tuple(c['permutation'])): c['variable'] for c in channels}
    for a, b in scope['coordinate_pairs']:
        incident = [g for g, support in enumerate(scope['groups']) if a in support and b in support]
        for x, y in product(range(3), repeat=2):
            flags = []
            for g in incident:
                inputs = [lookup[((a, b), g, pi)] for pi in PERMS if pi[x] == y]
                need(len(inputs) == 2, 'two permutations per matrix cell')
                variable = fresh()
                flags.append(dict(group=g, variable=variable, relative_indicator_inputs=inputs, **append(OR(variable, inputs))))
            bound = 1 if x == y else 2
            cells.append(dict(coordinates=[a, b], fibres=[x, y], bound=bound, flags=flags,
                **append(exact_count([f['variable'] for f in flags], bound))))
    need(len(domains) == 20 and len(channels) == 1800 and len(cells) == 540, 'complete semantic populations')
    need(nextvar-1 == 10480 and len(clauses) == 74200, 'derived total dimensions')
    need(sum(row['clause_count'] for row in onehots) == 11920 and sum(row['clause_count'] for row in channels) == 46800, 'section clause dimensions')
    need(sum(f['clause_count'] for row in cells for f in row['flags']) == 8100 and sum(row['clause_count'] for row in cells) == 7380, 'flag/count dimensions')
    return dict(schema='FIXED_HADAMARD_COMPLETE_BALANCED_GRAM_CNF_V1', variables=10480, clauses=74200, primary_selectors=3000,
        domains=domains, exact_one_prefix_rows=onehots, relative_channels=channels, pair_cell_counts=cells, permutations=[list(p) for p in PERMS],
        variable_populations=dict(selectors=3000, exact_one_prefixes=2980, relative_indicators=1800, cell_flags=2700)), clauses


def decode(assignment, model_path, scope_path, cnf_path):
    model, scope = read(model_path), read(scope_path)
    need(model['scope_sha256'] == sha(scope_path), 'bound scope')
    values = {}
    for lit in assignment:
        need(type(lit) is int and lit != 0 and abs(lit) not in values, 'unique integer assignment')
        values[abs(lit)] = lit > 0
    need(set(values) == set(range(1, 10481)), 'all10480 IDs assigned')
    count = 0
    with Path(cnf_path).open() as stream:
        need(stream.readline().strip() == 'p cnf 10480 74200', 'actual formula header')
        for line in stream:
            clause = [int(x) for x in line.split()]
            need(clause and clause[-1] == 0 and all(x != 0 for x in clause[:-1]), 'literal clause syntax')
            need(satisfied([clause[:-1]], values), 'all actual raw clauses')
            count += 1
    need(count == 74200, 'all actual raw clauses counted')
    F = [[0]*60 for _ in range(36)]
    selected = []
    for domain in model['domains']:
        active = [x for x in domain['choices'] if values[x['selector']]]
        need(len(active) == 1, 'one local option per group')
        choice = active[0]
        selected.append(choice['selector'])
        for d, rows in zip(domain['columns'], choice['lifted_rows'], strict=True):
            for row in rows:
                F[row][d] = 1
    checks = check_factor(F, scope['core_adjacency36'], scope['prescribed_Gram36'], 12, scope['L12x60'])
    pairs = [list(pair) for pair in combinations(range(12), 2) if pair[0] ^ 1 != pair[1]]
    rawpairs = [[a for a in range(12) if F[a][d]] for d in range(60)]
    need(sorted(rawpairs) == pairs, 'complete canonicalC0 pair bijection')
    order = [rawpairs.index(pair) for pair in pairs]
    return dict(factor=F, L=scope['L12x60'], selected_selector_ids=selected, canonical_column_order=order,
        canonical_factor=[[row[d] for d in order] for row in F], core_adjacency=scope['core_adjacency36'], target_gram=scope['prescribed_Gram36'],
        checks=checks, Gram_factor=True, factor_also_passes_column_caps=not checks['column_cap_violations'],
        factor_also_passes_mixed_caps=not checks['mixed_cap_violations'], target_graph=False, residual_D=None,
        balance_is_additional_assumption=True, model_sha256=sha(model_path), scope_sha256=sha(scope_path), independent_approval=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        for path, digest in PINS.items():
            need(sha(path) == digest, 'frozen input '+key(path))
        inputs = {key(p): d for p, d in PINS.items()}
        for path in [Path(__file__), Path(__file__).with_name('theory_20260930_hadamard_balanced_gram_cnf_spec.md'), ROOT/'uv.lock', ROOT/'pyproject.toml']:
            inputs[key(path)] = sha(path)
        save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs,
            status='PREREGISTERED_CANDIDATE_COMPLETE_BALANCED_GRAM_BUILD', limits=dict(seconds=30, solver_calls=0)))
        control = controls()
        options = local_options()
        save(out/'controls.json', control)
        save(out/'all150_local_options.json', options)
        scope = scope_from_raw(read(RAW))
        save(out/'scope.json', scope)
        model, clauses = build(scope, options)
        model['scope_sha256'] = sha(out/'scope.json')
        save(out/'model.json', model)
        with (out/'instance.cnf').open('x', encoding='ascii', newline='\n') as stream:
            stream.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for clause in clauses:
                stream.write(' '.join(map(str, clause))+' 0\n')
        need(time.monotonic()-started < 30, 'build allocation')
        summary = dict(status='CANDIDATE_COMPLETE_BALANCED_FIXED_SUPPORT_GRAM_CNF_BUILT', timestamp=datetime.now(timezone.utc).isoformat(),
            inputs_sha256=inputs, outputs_sha256={key(p): sha(p) for p in out.iterdir() if p.is_file()},
            variables=10480, clauses=74200, selectors=3000, local_choices_per_group=150, constant_choices_per_group=30, mixed_choices_per_group=120,
            group_rows=20, relative_channels=1800, exact_Gram_cell_rows=540, outside_column_caps_encoded=False,
            independent_approval=False, solver_calls=0, elapsed_seconds=time.monotonic()-started, target_resolution=False,
            scope=scope['scope'], artifact_availability='LOCAL_ONLY')
        save(out/'summary.json', summary)
        print(json.dumps(summary))
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), source_sha256=sha(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
