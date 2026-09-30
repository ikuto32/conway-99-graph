"""Candidate full cap extension; every option pair, no solver calls."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse, json, platform, subprocess, sys, time
from tqdm import tqdm
import theory_20260930_hadamard_balanced_gram_cnf as base

ROOT, B = base.ROOT, base.B
D = B/'20260930_hadamard_balanced_gram_cnf'
CNF, MODEL, SCOPE = D/'instance.cnf', D/'model.json', D/'scope.json'
PINS = {
    CNF: 'c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37',
    MODEL: '82717d648ad00255fe06c97f2c55ae25e6a3ba73e2e064287a15059c8be6cf98',
    SCOPE: '9cc4630a4d7f7b5a36da321465f58f86f1ed918a99e507b50f76f6e485eb334a',
    D/'summary.json': '686b73bb4678f1c2f92afcc0f93cd7e18f6d7d3fbe87e6bbafb5c4045aaf2497',
    Path(base.__file__): 'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',
    Path(base.__file__).with_name('theory_20260930_hadamard_balanced_gram_cnf_spec.md'): '937e9ae29f4818822b0516cc61f35060cc8352b5cfca9abda2ba2648c53d6a6d',
    base.RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
}


def word_code(values):
    return values[0]+3*values[1]+9*values[2]


def profile_mask(permutations3):
    return sum(1 << word_code([p[x] for p in permutations3]) for x in range(3))


def controls():
    generic = base.controls()
    profiles = list(product(list(permutations(range(3))), repeat=3))
    masks = [profile_mask(p) for p in profiles]
    for i, a in enumerate(profiles):
        for j, b in enumerate(profiles):
            literal = any(all(a[k][x] == b[k][y] for k in range(3)) for x in range(3) for y in range(3))
            base.need(bool(masks[i] & masks[j]) == literal, 'all three-shared-coordinate profile pairs')
    base.need(bool(masks[0] & masks[0]) and not bool(0 & masks[0]), 'corrupted profile mask differs from positive cap')
    for a, b in product((False, True), repeat=2):
        base.need((not a or not b) == (not (a and b)), 'binary cap nogood truth')
    raw_columns = [{0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {6, 7, 8, 9, 10, 11}]
    base.need(len(raw_columns[0] & raw_columns[1]) == 6, 'duplicated within-option column detected')
    return dict(base_generic_controls=generic, three_shared_profile_count=216, complete_profile_pairs=46656,
        binary_nogood_truth_cases=4, corrupted_controls=['zeroed_profile_mask', 'duplicated_within_option_column'],
        scope='Finite cap predicate and generic243 factor calibration; no positive research factor or solver result.')


def raw_option_masks(domain):
    result = []
    for option in domain['choices']:
        pi = option['coordinate_permutations']
        rows = [[12*pi[i][x]+a for i, a in enumerate(domain['support'])] for x in range(3)]
        base.need(rows == option['lifted_rows'], 'every raw lifted row from literal coordinate permutation')
        base.need(all(len(row) == len(set(row)) == 6 for row in rows), 'six distinct raw rows each column')
        result.append([sum(1 << a for a in row) for row in rows])
    return result


def shared_profiles(domain, triples):
    return [[profile_mask([option['coordinate_permutations'][domain['support'].index(a)] for a in triple]) for triple in triples] for option in domain['choices']]


def decode(assignment, extension_path, cnf_path):
    extension = base.read(extension_path)
    values = {}
    for lit in assignment:
        base.need(type(lit) is int and lit and abs(lit) not in values, 'complete unique signed assignment')
        values[abs(lit)] = lit > 0
    base.need(set(values) == set(range(1, 10481)), 'all10480 assignment IDs')
    count = 0
    with Path(cnf_path).open() as stream:
        base.need(stream.readline().strip() == f"p cnf 10480 {extension['clauses']}", 'exact augmented header')
        for line in stream:
            clause = [int(x) for x in line.split()]
            base.need(clause and clause[-1] == 0 and all(x for x in clause[:-1]), 'raw augmented clause syntax')
            base.need(base.satisfied([clause[:-1]], values), 'every augmented clause')
            count += 1
    base.need(count == extension['clauses'], 'complete augmented clause count')
    for path in (CNF, MODEL, SCOPE):
        base.need(base.sha(path) == PINS[path] == extension['base_inputs_sha256'][base.key(path)], 'frozen base decode identity')
    result = base.decode(assignment, MODEL, SCOPE, CNF)
    base.need(not result['checks']['column_cap_violations'], 'all1770 actual column caps')
    result.update(cap_extension_sha256=base.sha(extension_path), augmented_cnf_sha256=base.sha(cnf_path),
        outside_column_caps_encoded=True, factor_also_passes_column_caps=True,
        scope='Capped complete balanced incidence Gram factor on one fixed support; residualD remains absent.', independent_approval=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    completed, forbidden_total = 0, 0
    try:
        for path, digest in PINS.items():
            base.need(base.sha(path) == digest, 'frozen input '+base.key(path))
        inputs = {base.key(p): d for p, d in PINS.items()}
        for path, digest in base.PINS.items():
            base.need(base.sha(path) == digest, 'shared calibration input '+base.key(path))
            inputs[base.key(path)] = digest
        for path in [Path(__file__), Path(__file__).with_name('theory_20260930_hadamard_balanced_gram_caps_spec.md'), ROOT/'uv.lock', ROOT/'pyproject.toml']:
            inputs[base.key(path)] = base.sha(path)
        base.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs,
            status='PREREGISTERED_CANDIDATE_COMPLETE_CAP_EXTENSION', limits=dict(seconds=120, solver_calls=0),
            selection_rule='All190 distinct-group pairs and every150x150 option pair; all3000 within-option triples.',
            base_independent_gate=None, base_independent_gate_null_reason='Independent base review is being prepared separately; extension cannot be promoted or launched until an exact gate is bound by independent review.'))
        base.save(out/'controls.json', controls())
        model, scope = base.read(MODEL), base.read(SCOPE)
        domains = model['domains']
        base.need(len(domains) == 20 and all(len(d['choices']) == 150 for d in domains), 'all20x150 domains')
        masks = [raw_option_masks(d) for d in domains]
        within, units = [], []
        for g, domain in enumerate(domains):
            for i, option in enumerate(domain['choices']):
                overlaps = [(masks[g][i][x] & masks[g][i][y]).bit_count() for x, y in combinations(range(3), 2)]
                conflict = any(x > 2 for x in overlaps)
                within.append(dict(group=g, choice_index=i, selector=option['selector'], overlaps=overlaps, forbidden=conflict))
                if conflict:
                    units.append([-option['selector']])
        base.save(out/'within_group_checks.json', dict(records=within, literal_intersections=9000, emitted_units=units))
        pairdir = out/'pairs'
        pairdir.mkdir()
        pair_index, support_histogram = [], Counter()
        clause_count = len(units)
        with (out/'clauses.cnfpart').open('x', encoding='ascii', newline='\n') as stream, (out/'progress.jsonl').open('x', encoding='utf-8', newline='\n') as progress:
            for clause in units:
                stream.write(' '.join(map(str, clause))+' 0\n')
            for pair_number, (g, h) in enumerate(tqdm(list(combinations(range(20), 2)), desc='Complete cap pairs', mininterval=1)):
                shared = sorted(set(domains[g]['support']) & set(domains[h]['support']))
                support_histogram[len(shared)] += 1
                triples = list(combinations(shared, 3))
                left_profiles, right_profiles = shared_profiles(domains[g], triples), shared_profiles(domains[h], triples)
                bitmaps, forbidden = [], 0
                first = 74200+clause_count+1
                for i in range(150):
                    bitmap = 0
                    lm = masks[g][i]
                    for j in range(150):
                        rm = masks[h][j]
                        # All nine intersections, including after a first conflict.
                        intersections = [(a & b).bit_count() for a in lm for b in rm]
                        literal = max(intersections) > 2
                        fast = any(a & b for a, b in zip(left_profiles[i], right_profiles[j], strict=True))
                        base.need(literal == fast, f'full fast/literal equivalence pair{g},{h} choices{i},{j}')
                        if literal:
                            bitmap |= 1 << j
                            stream.write(f"-{domains[g]['choices'][i]['selector']} -{domains[h]['choices'][j]['selector']} 0\n")
                            forbidden += 1
                    bitmaps.append(format(bitmap, 'x'))
                clause_count += forbidden
                forbidden_total += forbidden
                path = pairdir/f'pair_{pair_number:03d}.json'
                record = dict(index=pair_number, groups=[g, h], original_columns=[domains[g]['columns'], domains[h]['columns']],
                    shared_coordinates=shared, shared_triples=[list(t) for t in triples], forbidden_right_masks_hex=bitmaps,
                    choice_pairs=22500, literal_column_intersections=202500, fast_literal_disagreements=0,
                    forbidden_choice_pairs=forbidden, first_clause=first, clause_count=forbidden)
                base.save(path, record)
                pair_index.append(dict(path=base.key(path), sha256=base.sha(path), groups=[g, h], clause_count=forbidden, first_clause=first))
                completed += 1
                progress.write(json.dumps(dict(completed_group_pairs=completed, completed_choice_pairs=completed*22500,
                    emitted_conflict_clauses=forbidden_total, pair_path=base.key(path), pair_sha256=base.sha(path), elapsed_seconds=time.monotonic()-started), separators=(',', ':'))+'\n')
                progress.flush()
                base.need(time.monotonic()-started < 120, 'complete extension build allocation')
        base.need(completed == 190, 'full190 group-pair population')
        data = CNF.read_bytes()
        header, separator, body = data.partition(b'\n')
        base.need(header == b'p cnf 10480 74200' and separator == b'\n', 'exact frozen base header')
        with (out/'instance.cnf').open('xb') as stream:
            stream.write(f'p cnf 10480 {74200+clause_count}\n'.encode('ascii'))
            stream.write(body)
            with (out/'clauses.cnfpart').open('rb') as suffix:
                for block in iter(lambda: suffix.read(1048576), b''):
                    stream.write(block)
        extended_scope = dict(schema='FIXED_HADAMARD_BALANCED_GRAM_ALL_CAPS_SCOPE_V1', base_scope_path=base.key(SCOPE), base_scope_sha256=PINS[SCOPE],
            outside_column_caps_encoded=True, outside_column_pairs=1770, between_group_column_pairs=1710, within_group_column_pairs=60,
            balance_is_additional_assumption=True, residual_D_encoded=False, target_graph=False,
            scope='Same exact balanced fixedL fullGram family with every outside-column common-core cap; no residual completion or unrestricted coverage.')
        base.save(out/'scope.json', extended_scope)
        extension = dict(schema='FIXED_HADAMARD_BALANCED_GRAM_ALL_CAPS_EXTENSION_V1', variables=10480, clauses=74200+clause_count,
            base_clauses=74200, added_clauses=clause_count, within_option_unit_clauses=len(units), intergroup_conflict_clauses=forbidden_total,
            base_inputs_sha256={base.key(p): PINS[p] for p in (CNF, MODEL, SCOPE)}, pair_records=pair_index,
            within_group_checks_path=base.key(out/'within_group_checks.json'), within_group_checks_sha256=base.sha(out/'within_group_checks.json'),
            suffix_path=base.key(out/'clauses.cnfpart'), suffix_sha256=base.sha(out/'clauses.cnfpart'),
            scope_sha256=base.sha(out/'scope.json'), augmented_cnf_sha256=base.sha(out/'instance.cnf'))
        base.save(out/'extension.json', extension)
        summary = dict(status='CANDIDATE_COMPLETE_BALANCED_GRAM_CAP_EXTENSION_BUILT', timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
            outputs_sha256={base.key(p): base.sha(p) for p in out.rglob('*') if p.is_file()}, variables=10480, clauses=extension['clauses'],
            complete_group_pairs=190, complete_choice_pairs=4275000, literal_between_intersections=38475000, literal_within_intersections=9000,
            fast_literal_disagreements=0, within_option_unit_clauses=len(units), intergroup_conflict_clauses=forbidden_total,
            support_intersection_histogram={str(k): v for k, v in sorted(support_histogram.items())}, elapsed_seconds=time.monotonic()-started,
            solver_calls=0, independent_approval=False, target_resolution=False, artifact_availability='LOCAL_ONLY', scope=extended_scope['scope'])
        base.save(out/'summary.json', summary)
        print(json.dumps({k: v for k, v in summary.items() if k not in ('inputs_sha256', 'outputs_sha256')}))
    except BaseException as error:
        base.save(out/'failure.json', dict(error=repr(error), completed_group_pairs=completed, emitted_intergroup_conflicts=forbidden_total, source_sha256=base.sha(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
