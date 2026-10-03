"""Candidate exhaustive finite phase lift for one fixed parity branch."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time
from tqdm import tqdm
import theory_20260930_hadamard_general_f3_system as general
linear = general.linear
ROOT = linear.ROOT
B = ROOT/'acceleration/results'
CASE = B/'20260930_hadamard_parity_phase_batch_pilot/case_01'
FIXTURE = B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS = {
    CASE/'phase_system.json': 'c6f31ba77b060ccddefc5274be3a130f3cdaf1d83c612ec507c69f588f80dfe2',
    CASE/'phase_screen.json': '8eebf239cca0bf7aca1f1a8120c2f82494ec2545211031c173948a48e33400dc',
    CASE/'decoded_projection.json': '31c8d00f69c5694121aca82dc99ac103ae9ed769ea00b0a334e87b55c391081e',
    linear.RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json': '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
    FIXTURE: '3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
    B/'20260930_independent_review/srg243_residual_fixture/summary.json': '28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
    Path(general.__file__): '77877e34ca6a6f73f98546d0221faef375e091e54ba4c9b4f8b8a2e23b0d0162',
    Path(linear.__file__): '154d145af9f23a3b150ec8c798598d63779fab28a1474468b622a718fc82beaa',
}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def local_failure(signs, phase):
    counts = {str(s): [sum(t == v for sign, t in zip(signs, phase, strict=True) if sign == s) for v in range(3)] for s in (1, 2)}
    mixed = 2 in signs
    expected = {'1': [1, 1, 1], '2': [1, 1, 1]} if mixed else {'1': [2, 2, 2], '2': [0, 0, 0]}
    if counts != expected:
        return dict(rule='mixed_phase_distinctness' if mixed else 'constant_phase_multiplicity', actual=counts, expected=expected)
    columns = [[(sign*x+t) % 3 for sign, t in zip(signs, phase, strict=True)] for x in range(3)]
    linear.need(all([col.count(i) for i in range(3)] == [2, 2, 2] for col in columns), 'local profile implies literal balanced columns')
    return None


def pair_matrix(relative_signs, relative_phases):
    return [[sum((sign*x+t) % 3 == y for sign, t in zip(relative_signs, relative_phases, strict=True)) for y in range(3)] for x in range(3)]


def pair_failures(system, phase):
    target = [[2-int(x == y) for y in range(3)] for x in range(3)]
    failures = []
    for pair in system['pair_records']:
        signs = [r['relative_sign'] for r in pair['relative_maps']]
        intercepts = [linear.dot(r['relative_phase_coefficients'], phase) for r in pair['relative_maps']]
        actual = pair_matrix(signs, intercepts)
        if actual != target:
            failures.append(dict(coordinates=pair['coordinates'], relative_signs=signs, relative_phases=intercepts, actual=actual, expected=target))
    return failures


def gram_target(core, n):
    m = 3*n
    return [[n*int(a == b)-core[a][b]-sum(core[a][k]*core[k][b] for k in range(m))+2-int(a//n == b//n) for b in range(m)] for a in range(m)]


def factor_checks(factor, core, expected, n, L=None):
    m, columns = len(factor), len(factor[0])
    linear.need(m == 3*n and all(len(row) == columns and all(type(x) is int and x in (0, 1) for x in row) for row in factor), 'binary rectangular factor')
    rows = [{d for d in range(columns) if factor[a][d]} for a in range(m)]
    supports = [{a for a in range(m) if factor[a][d]} for d in range(columns)]
    actual_gram = [[len(rows[a] & rows[b]) for b in range(m)] for a in range(m)]
    errors = [dict(rows=[a, b], actual=actual_gram[a][b], expected=expected[a][b]) for a in range(m) for b in range(m) if actual_gram[a][b] != expected[a][b]]
    caps = [dict(columns=[d, e], overlap=len(supports[d] & supports[e])) for d, e in combinations(range(columns), 2)]
    mixed = [[factor[a][d]+sum(core[a][b]*factor[b][d] for b in range(m)) for d in range(columns)] for a in range(m)]
    margins = all(len(row) == n-2 for row in rows) and all(sum(factor[n*g+a][d] for a in range(n)) == 2 for g in range(3) for d in range(columns))
    coordinate_L = [[sum(factor[n*g+a][d] for g in range(3)) for d in range(columns)] for a in range(n)]
    L_ok = L is None or coordinate_L == L
    violations = [item for item in caps if item['overlap'] > 2]
    mixed_violations = [dict(row=a, column=d, value=mixed[a][d]) for a in range(m) for d in range(columns) if mixed[a][d] > 2]
    return dict(Gram_pass=not errors, Gram_mismatches=errors, actual_Gram=actual_gram, margins_pass=margins, raw_L_pass=L_ok,
        all_column_pair_records=caps, cap_violations=violations, mixed_cap_violations=mixed_violations,
        complete_partial_factor_pass=not errors and margins and L_ok and not violations and not mixed_violations)


def controls():
    linear.need(local_failure([1, 1, 1, 2, 2, 2], [0, 1, 2, 0, 1, 2]) is None, 'mixed local positive')
    linear.need(local_failure([1]*6, [0, 0, 1, 1, 2, 2]) is None, 'constant local positive')
    linear.need(local_failure([1, 1, 1, 2, 2, 2], [0, 0, 2, 0, 1, 2]) is not None, 'corrupted mixed profile')
    linear.need(local_failure([1]*6, [0, 0, 0, 1, 2, 2]) is not None, 'corrupted constant profile')
    target = [[2-int(i == j) for j in range(3)] for i in range(3)]
    pair_counts = {}
    for odd in (0, 3):
        signs = [2]*odd+[1]*(5-odd)
        positives = 0
        for ts in product(range(3), repeat=5):
            expected = sorted(ts) == [0, 1, 1, 2, 2] if odd == 0 else sorted(ts[:3]) == [0, 1, 2] and sorted(ts[3:]) == [1, 2]
            good = pair_matrix(signs, ts) == target
            linear.need(good == expected, 'literal pair profile equivalence')
            positives += good
        pair_counts[str(odd)] = positives
    fixture = linear.read(FIXTURE)
    factor, core = fixture['factor60x180'], fixture['cubic_core60']
    expected = gram_target(core, 20)
    good = factor_checks(factor, core, expected, 20)
    linear.need(good['complete_partial_factor_pass'], 'actual SRG243 generic factor positive')
    bad = [row[:] for row in factor]
    bad[0][0] ^= 1
    linear.need(not factor_checks(bad, core, expected, 20)['complete_partial_factor_pass'], 'changed raw factor bit rejected')
    bad = [row[:] for row in factor]
    for row in bad:
        row[1] = row[0]
    duplicated = factor_checks(bad, core, expected, 20)
    linear.need(any(x['columns'] == [0, 1] and x['overlap'] == 6 for x in duplicated['cap_violations']), 'duplicated column cap rejected')
    return dict(local_positive_profiles=2, pair_phase_assignments=486, pair_positive_counts=pair_counts,
        generic_positive_fixture='Independently checked SRG243 factor only; not this support, balance premise, or a target99 object.',
        generic_positive_Gram_entries=3600, generic_positive_column_pairs=16110,
        corruptions_rejected=['mixed_multiplicity', 'constant_multiplicity', 'raw_factor_bit', 'duplicate_column_cap'])


def construct_factor(raw, system, phase):
    factor = [[0]*60 for _ in range(36)]
    for g, support in enumerate(system['groups']):
        columns = [d for d in range(60) if [a for a in range(12) if raw['L'][a][d]] == support]
        linear.need(len(columns) == 3, 'three original columns per group')
        for x, d in enumerate(columns):
            for i, a in enumerate(support):
                fibre = (system['signs'][g][i]*x+phase[6*g+i]) % 3
                factor[12*fibre+a][d] = 1
    return factor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    counts = Counter()
    failures = Counter()
    try:
        for path, digest in PINS.items():
            linear.need(linear.h(path) == digest, 'frozen input '+linear.key(path))
        inputs = {linear.key(p): d for p, d in PINS.items()}
        for path in [Path(__file__), Path(__file__).with_name('theory_20260930_hadamard_phase_case01_enumeration_v2_spec.md'), ROOT/'uv.lock', ROOT/'pyproject.toml']:
            inputs[linear.key(path)] = linear.h(path)
        linear.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
            inputs_sha256=inputs, limits=dict(seconds=120, expected_vectors=2187, solver_calls=0), status='PREREGISTERED_CANDIDATE_FINITE_ENUMERATION'))
        linear.save(out/'controls.json', controls())
        raw = linear.read(linear.RAW)
        system = general.build(raw, linear.read(CASE/'decoded_projection.json'))
        linear.need(system == linear.read(CASE/'phase_system.json'), 'entire reconstructed general system')
        linear.need(system['mixed_groups'] == 12 and system['constant_groups'] == 8 and len(system['rows']) == 172, 'actual mixed/constant domain')
        matrix = [r['coefficients'] for r in system['rows']]
        saved = linear.read(CASE/'phase_screen.json')['linear_certificate']
        linear.verify_linear(matrix, saved)
        recomputed = linear.rref(matrix, 120)
        linear.need(recomputed == saved and recomputed['rank'] == 113 and recomputed['nullity'] == 7, 'full recomputed RREF/certificate identity')
        basis = recomputed['nullspace_basis']
        linear.save(out/'recomputed_linear_certificate.json', recomputed)
        expected = raw['prescribed_Gram36']
        core = raw['core_adjacency36']
        linear.need(expected == gram_target(core, 12), 'all exact prescribed core Gram coefficients')
        witness_directory = out/'local_survivors'
        witness_directory.mkdir()
        with (out/'enumeration.jsonl').open('x', encoding='utf-8', newline='\n') as stream:
            for index, coefficients in enumerate(tqdm(product(range(3), repeat=7), total=2187, desc='Exact GF3 kernel', mininterval=1)):
                phase = [sum(coefficients[j]*basis[j][i] for j in range(7)) % 3 for i in range(120)]
                counts['kernel_vectors_enumerated'] += 1
                record = dict(index=index, coefficients=list(coefficients), phase_sha256=canonical_hash(phase))
                failed = None
                for g in range(20):
                    bad = local_failure(system['signs'][g], phase[6*g:6*g+6])
                    if bad is not None:
                        failed = dict(group=g, **bad)
                        break
                if failed is not None:
                    failures[failed['rule']] += 1
                    record['first_failure'] = failed
                else:
                    counts['local_profile_survivors'] += 1
                    pair_bad = pair_failures(system, phase)
                    factor = construct_factor(raw, system, phase)
                    check = factor_checks(factor, core, expected, 12, raw['L'])
                    if not pair_bad:
                        counts['complete_pair_Gram_survivors'] += 1
                    linear.need((not pair_bad) == check['Gram_pass'], 'separate literal factor Gram agrees with all pair matrices')
                    if check['Gram_pass']:
                        counts['complete_integer_Gram_factors'] += 1
                    if check['complete_partial_factor_pass']:
                        counts['Gram_and_caps_factors'] += 1
                    else:
                        failures['pair_Gram' if pair_bad else 'column_or_mixed_caps'] += 1
                    path = witness_directory/f'vector_{index:04d}.json'
                    linear.save(path, dict(coefficients=list(coefficients), phase=phase, factor=factor, local_profile_pass=True,
                        pair_failures=pair_bad, factor_checks=check, full_target_graph=False, residual_D=None, independent_approval=False))
                    record.update(first_failure=pair_bad[0] if pair_bad else None, local_survivor_path=linear.key(path),
                        local_survivor_sha256=linear.h(path), Gram_pass=check['Gram_pass'], full_partial_factor_pass=check['complete_partial_factor_pass'])
                stream.write(json.dumps(record, separators=(',', ':'))+'\n')
                linear.need(time.monotonic()-started < 120, 'finite enumeration allocation')
        linear.need(counts['kernel_vectors_enumerated'] == 2187, 'complete3^7 universe')
        for name in ['local_profile_survivors', 'complete_pair_Gram_survivors', 'complete_integer_Gram_factors', 'Gram_and_caps_factors']:
            counts.setdefault(name, 0)
        summary = dict(status='CANDIDATE_CASE01_COMPLETE_PHASE_ENUMERATION', timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
            outputs_sha256={linear.key(p): linear.h(p) for p in out.rglob('*') if p.is_file()}, kernel_dimension=7, frozen_universe=2187,
            mixed_groups=12, constant_groups=8, counts=dict(counts), first_failure_counts=dict(failures),
            complete=True, candidate_branch_exclusion=counts['Gram_and_caps_factors'] == 0, independent_approval=False,
            target_resolution=False, solver_calls=0, elapsed_seconds=time.monotonic()-started,
            scope='Only this one exact case01 parity assignment in the balanced fixed-support family; no full factor or target conclusion beyond saved raw candidates.')
        linear.save(out/'summary.json', summary)
        print(json.dumps(summary))
    except BaseException as error:
        linear.save(out/'failure.json', dict(error=repr(error), counts=dict(counts), source_sha256=linear.h(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
