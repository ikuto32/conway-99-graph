"""Independent complete count-object checking after six proved-profile cuts.

Reuses frozen independent native/CNF parsers and count decoder, never producers.
The new encoding gate is a required argument, authenticated before calibration.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, copy, hashlib, json, platform, subprocess, sys, time, traceback
import audit_20260930_hadamard_count_master_object as base

ROOT, B, D = base.ROOT, base.B, base.D
need, read, sha, save = base.need, base.read, base.sha, base.save
independent = base.independent
CUT = B + 'count_master_eight_orbit_cuts/'
CNF = CUT + 'instance.cnf'
ENCODING_PATH = B + 'independent_review/count_master_eight_orbit_cuts/summary.json'
ENCODING_STATUS = 'INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUTS_PASS'
N, M = 155939, 705839
SOURCE_PINS = {
 'acceleration/native_20260930_count_master_eight_orbit_cuts.py': '915aa5f9def41e21a6f707688045d5b446f10e33370a8d7596c143cbe1fafbd6',
 'acceleration/native_20260930_count_master_eight_orbit_cuts_spec.md': 'ad1ca1696ed159fcd51f51bf463874e154d758890fb844b07566fdbe4cc6c27e',
 'acceleration/native_20260930_unrestricted_full99.py': 'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
 'acceleration/native_20260930_proof_location.py': 'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
 'acceleration/theory_20260930_hadamard_count_master_cnf.py': '470cbec724f891264593dc5b438648dc2995b3f860f89decf4b6ac8bc1c4f28b',
 'acceleration/theory_20260930_hadamard_count_master_cnf_spec.md': '67b5e379c1b5e6d1dcb6e6aff0c022821a56169a55e1656abf3d353aac5b5d19',
 'acceleration/theory_20260930_count_master_eight_orbit_cuts.py': '80b651186fa36822b44fdc6c2ea9b1b8a249eb3e33fb0b4e6088b89c84f9c4f4',
 'acceleration/theory_20260930_count_master_eight_orbit_cuts_spec.md': '489530470ae3a8a0e6aecf82ed8aaa5a997681cd021dbd57fc82dc85975bfc00',
 'acceleration/audit_20260930_hadamard_count_master_object.py': '1054083b36d7a3876e9ba1320911ada7e56532a9da1b5c858788460a6f95686d',
 'acceleration/audit_20260930_hadamard_count_master_cnf_v2.py': 'd32cd6db0f252852594e619662b1d9ec12ce60f51ed3a0920a435c6dbf3b6780',
}
DATA_PINS = {
 CNF: 'c3c0a9c0533d41bb814011d3736a4115d388e529f4c9cd2f89af609dc94793e2',
 CUT + 'model.json': 'a4376d5ee0e4cd8e990d311444f8ccda61d4b39af1c1c2371ade73e96dbe3d22',
 CUT + 'scope.json': '5d604cc2c7725bee0865d9c746c97a005d2cd3aed08db078acb676d44cbf8518',
 CUT + 'summary.json': '6a0e2c8acde3eccf6fd4ee74044041d3ebcf932ff65a345264ba840c3e7b4be7',
 D + 'model.json': 'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 D + 'at_least_seven.cnf': 'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',
 D + 'scope.json': '719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',
 D + 'summary.json': '2137fe0c32043a82166a484085d366309e4037d24aa558dabca20a44e73bff04',
 base.GATE: base.GATE_SHA,
}
DOC = 'docs/AUDIT_20260930_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT.md'
SPEC = 'acceleration/audit_20260930_count_master_eight_orbit_cut_object_spec.md'


def key(path):
    path = Path(path)
    return (path if path.is_absolute() else ROOT / path).resolve().relative_to(ROOT).as_posix()


def authenticate(args):
    gate_path = key(args.encoding_gate)
    need(gate_path == ENCODING_PATH and sha(ROOT / gate_path) == args.encoding_gate_sha256,
         'actual supplied independent six-cut encoding gate')
    gate = read(gate_path)
    need(gate['status'] == ENCODING_STATUS, 'independent six-cut encoding approval')
    pins = {gate_path: args.encoding_gate_sha256}
    for path, digest in gate['inputs_sha256'].items():
        need(sha(ROOT / path) == digest, 'unchanged encoding premise ' + path)
        pins[path] = digest
    for path, digest in DATA_PINS.items():
        need(sha(ROOT / path) == digest, 'fixed object input ' + path)
        need(gate['inputs_sha256'][path] == digest, 'direct independent encoding binding ' + path)
        pins[path] = digest
    for path in [D + 'extension.json', CUT + 'excluded_profiles.json']:
        need(gate['inputs_sha256'][path] == sha(ROOT / path), 'direct scope metadata ' + path)
        pins[path] = sha(ROOT / path)
    for path, digest in SOURCE_PINS.items():
        need(sha(ROOT / path) == digest, 'unchanged native/checker source closure ' + path)
        pins[path] = digest
    for path in [key(__file__), SPEC, DOC, 'uv.lock', 'pyproject.toml']:
        pins[path] = sha(ROOT / path)
    meta, scope = read(CUT + 'model.json'), read(CUT + 'scope.json')
    need((meta['variables'], meta['clauses']) == (N, M), 'new exact dimensions')
    need(meta['base_model_path'] == D + 'model.json' and meta['base_model_sha256'] == DATA_PINS[D + 'model.json'],
         'original independent count decoder scope')
    need(scope['base_variant'] == 'at_least_seven' and scope['new_variables'] == 0
         and scope['added_clauses'] == 6 and scope['excluded_full_count_profiles'] == 6,
         'exact six full-profile cuts')
    return pins


def cut_records():
    meta = read(CUT + 'model.json')
    records = read(CUT + 'excluded_profiles.json')['records']
    need(len(records) == len(meta['clause_records']) == 6, 'six raw excluded profiles')
    for i, (record, clause) in enumerate(zip(records, meta['clause_records'])):
        need(record['action_index'] == clause['action_index'] == i
             and clause['index'] == 705834 + i, 'ordered clause identity')
        need(record['profile_sha256'] == clause['profile_sha256']
             and record['clause'] == clause['clause'] == [-v for v in record['selected_group_selector_ids']],
             'literal full-group nogood mapping')
        need(len(record['clause']) == 20 and len(set(record['selected_group_selector_ids'])) == 20,
             'one literal for every group')
    return records


def cut_truth(result, values, records):
    answers = []
    for record in records:
        same_table = result['coordinate_group_fibre_counts'] == record['coordinate_group_fibre_counts']
        same_groups = result['selected_group_selector_ids'] == record['selected_group_selector_ids']
        need(same_table == same_groups, 'literal selected signatures determine complete count table')
        truth = independent.clause_pass(record['clause'], values)
        need(truth == (not same_table), 'clause excludes exactly its full count table')
        answers.append(truth)
    return answers


def evaluate(args):
    need(args.variant == 'at_least_seven', 'sole fixed variant')
    model = read(D + 'model.json')
    assignment = json.loads(args.assignment.read_bytes())['assignment']
    values = independent.signed_values(assignment, N)
    need(values == base.native_model(args.native_output, N), 'complete native/JSON assignment equality')
    checked = base.cnf_object(ROOT / CNF, values, M)
    result = independent.literal_decode(model, values, 'at_least_seven')
    truths = cut_truth(result, values, cut_records())
    need(all(truths), 'avoids all six proved-impossible profiles')
    if args.decoded:
        # The frozen producer decoder intentionally checks the OLD base formula.
        # Its 705833 field is compared honestly; this checker separately checks705839.
        base.compare_decoded(json.loads(args.decoded.read_bytes()), result,
                             DATA_PINS[D + 'model.json'], 705833)
    return result, checked, truths


def calibration(out, pins):
    model, records = read(D + 'model.json'), cut_records()
    rejected, orbit_controls, cut_only = [], [], []

    def reject(name, function):
        try:
            function()
        except (ValueError, KeyError, IndexError, TypeError):
            rejected.append(name)
            return
        raise ValueError('corruption unexpectedly accepted ' + name)

    raw_summary = read(CUT + 'summary.json')
    for i in range(6):
        path = CUT + f'control_orbit_{i}_assignment.json'
        need(sha(ROOT / path) == raw_summary['outputs_sha256'][path], 'saved old-count control identity')
        pins[path] = sha(ROOT / path)
        assignment = read(path)['assignment']
        values = independent.signed_values(assignment, N)
        native = out / f'orbit_{i}_synthetic_native.log'
        base.write_native(native, assignment)
        need(base.native_model(native, N) == values, 'complete old-count native codec control')
        base.cnf_object(ROOT / (D + 'at_least_seven.cnf'), values, 705833)
        result = independent.literal_decode(model, values, 'at_least_seven')
        truth = cut_truth(result, values, records)
        need(truth == [j != i for j in range(6)], 'six by six exact rejected-profile truth table')
        need(result['profile_sha256'] == records[i]['profile_sha256'], 'raw control count digest')
        reject(f'orbit_{i}_excluded_by_actual_new_formula', lambda v=values: base.cnf_object(ROOT / CNF, v, M))
        bad = values.copy()
        variable = result['selected_group_selector_ids'][0]
        bad[variable] = not bad[variable]
        reject(f'orbit_{i}_changed_group_selector', lambda v=bad: base.cnf_object(ROOT / (D + 'at_least_seven.cnf'), v, 705833))
        orbit_controls.append(dict(action_index=i, assignment_path=path, assignment_sha256=pins[path],
            exception_count=result['exception_count'], base_clauses_checked=705833, new_cut_truth=truth,
            synthetic_native_path=key(native), is_new_formula_positive=False))

    # Authentic lower-exception baseline objects satisfy every cut, but correctly
    # fail the at-least-seven requirement. They are only cut-layer positives.
    for path in sorted((ROOT / D).glob('*_assignment.json')):
        assignment = json.loads(path.read_bytes())['assignment']
        values = independent.signed_values(assignment, 155750)
        base.cnf_object(ROOT / (D + 'baseline.cnf'), values, 704454)
        result = independent.literal_decode(model, values, 'baseline')
        need(all(cut_truth(result, values, records)), 'unrelated valid baseline count object passes each cut')
        augmented = values + [False] * 189
        for state in model['extension']['states']:
            augmented[state['id']] = sum(augmented[v] for v in model['extension']['input_variables'][:state['i']]) >= state['j']
        reject(path.stem + '_below_seven', lambda v=augmented: base.cnf_object(ROOT / CNF, v, M))
        pins[key(path)] = sha(path)
        cut_only.append(dict(path=key(path), sha256=sha(path), exception_count=result['exception_count'],
                             all_six_cuts_satisfied=True, is_new_formula_positive=False))
    need(len(cut_only) == 2, 'two authentic baseline cut-only positives')

    # A small complete base-plus-six-suffix fixture tests successful clause walking.
    toy = out / 'tiny_base_plus_six_cuts.cnf'
    toy.write_bytes(b'p cnf 3 8\n1 0\n-2 0\n1 2 0\n1 -2 0\n1 3 0\n-2 3 0\n1 -3 0\n-2 -3 0\n')
    need(base.cnf_object(toy, [None, True, False, True], 8) == 8, 'complete small strengthened-formula positive')
    codec = [i if i % 2 else -i for i in range(1, N + 1)]
    native = out / 'fullsize_codec_only.log'
    base.write_native(native, codec)
    need(base.native_model(native, N) == independent.signed_values(codec, N), 'full155939 native codec positive')
    for name, values in [('missing', codec[:-1]), ('duplicate', codec[:-1] + [codec[0]]),
                         ('range', codec[:-1] + [N + 1]), ('boolean', codec[:-1] + [True]),
                         ('zero', codec[:-1] + [0])]:
        reject('assignment_' + name, lambda v=values: independent.signed_values(v, N))
    for label, text in [('status', 's UNSATISFIABLE\nv 1 -2 0\n'),
                        ('duplicate', 's SATISFIABLE\nv 1 -1 0\n'),
                        ('missing', 's SATISFIABLE\nv 1 0\n'),
                        ('unterminated', 's SATISFIABLE\nv 1 -2\n'),
                        ('internalzero', 's SATISFIABLE\nv 1 0 -2 0\n'),
                        ('doublestatus', 's SATISFIABLE\ns SATISFIABLE\nv 1 -2 0\n'),
                        ('badtoken', 's SATISFIABLE\nv 1 false 0\n')]:
        path = out / ('corrupt_native_' + label + '.log')
        path.write_text(text, encoding='ascii', newline='\n')
        reject('native_' + label, lambda p=path: base.native_model(p, 2))
    for label, content in [('header', b'p cnf 4 2\n1 0\n-2 0\n'),
                           ('falsecut', b'p cnf 3 2\n1 0\n-1 0\n'),
                           ('missing', b'p cnf 3 2\n1 0\n'),
                           ('range', b'p cnf 3 2\n1 0\n4 0\n')]:
        path = out / ('corrupt_cnf_' + label + '.cnf')
        path.write_bytes(content)
        reject('cnf_' + label, lambda p=path: base.cnf_object(p, [None, True, False, True], 2))
    expected = independent.literal_decode(model, independent.signed_values(read(CUT + 'control_orbit_0_assignment.json')['assignment'], N), 'at_least_seven')
    valid_decoded = dict(expected, model_sha256=DATA_PINS[D + 'model.json'], actual_cnf_clauses_checked=705833)
    base.compare_decoded(valid_decoded, expected, DATA_PINS[D + 'model.json'], 705833)
    for label in ['exception_count', 'count_table', 'new_count_misattributed_to_old_decoder']:
        altered = copy.deepcopy(valid_decoded)
        if label == 'exception_count': altered['exception_count'] += 1
        elif label == 'count_table': altered['coordinate_group_fibre_counts'][0][0][0] += 1
        else: altered['actual_cnf_clauses_checked'] = M
        reject('decoded_' + label, lambda q=altered: base.compare_decoded(q, expected, DATA_PINS[D + 'model.json'], 705833))
    bad_records = copy.deepcopy(records)
    bad_records[0]['clause'][0] *= -1
    values = independent.signed_values(read(CUT + 'control_orbit_0_assignment.json')['assignment'], N)
    reject('wrong_cut_sign', lambda: cut_truth(expected, values, bad_records))
    save(out / 'controls.json', dict(old_count_orbit_controls=orbit_controls,
        unrelated_cut_only_positives=cut_only, complete_small_strengthened_positive=True,
        fullsize_native_codec_variables=N, rejected_corruptions=rejected,
        new_formula_research_positive=None,
        new_formula_research_positive_null_reason='No satisfying assignment of the new formula was supplied; all six old orbit objects must fail it.',
        synthetic_native_is_solver_output=False, full_factor_positive=False,
        inherited_decoder_clause_count=705833, new_actual_clause_count=M))
    return dict(status='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT_CALIBRATION_PASS',
        old_count_CSP_positives=6, exact_new_formula_rejections=6, cut_only_positives=2,
        synthetic_native_codec_variables=N, new_formula_actual_clauses=M,
        rejected_corruptions=len(rejected), scope='Complete raw native/JSON and fresh705839-clause validation plus exact original count decoding and all six count-table exclusions. No new research witness or factor.')


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='mode', required=True)
    for mode in ['calibrate', 'sat']:
        p = sub.add_parser(mode)
        p.add_argument('--encoding-gate', type=Path, required=True)
        p.add_argument('--encoding-gate-sha256', required=True)
        p.add_argument('--variant', choices=['at_least_seven'], default='at_least_seven')
        p.add_argument('--out', type=Path, required=True)
        if mode == 'sat':
            p.add_argument('--assignment', type=Path, required=True)
            p.add_argument('--native-output', type=Path, required=True)
            p.add_argument('--decoded', type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins, started = {}, time.perf_counter()
    try:
        pins = authenticate(args)
        if args.mode == 'calibrate':
            result = calibration(out, pins)
        else:
            for path in [args.assignment, args.native_output, args.decoded]:
                if path is not None: pins[key(path)] = sha(path)
            decoded, count, truths = evaluate(args)
            save(out / 'independent_count_profile.json', decoded)
            save(out / 'independent_cut_avoidance.json', dict(cut_satisfaction=truths,
                excluded_profile_digests=[r['profile_sha256'] for r in cut_records()],
                actual_profile_sha256=decoded['profile_sha256'], all_six_avoided=True))
            result = dict(status='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_SAT_OBJECT_PASS',
                variant=args.variant, actual_clauses_checked=count, exception_count=decoded['exception_count'],
                independent_count_profile=key(out / 'independent_count_profile.json'),
                independent_count_profile_sha256=sha(out / 'independent_count_profile.json'),
                profile_sha256=decoded['profile_sha256'], all_six_excluded_profiles_avoided=True,
                scope='One exact count-CSP witness outside six forbidden profiles; no full Gram, interval test, cross-group caps, full factor or target graph.')
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            inputs_sha256=pins, outputs_sha256={key(p): sha(p) for p in out.iterdir()},
            solver_calls=0, target_resolution=False,
            shared_code='Frozen independently authored native/CNF parser and literal count decoder; no producer or native-driver import.',
            elapsed_seconds=time.perf_counter() - started)
        save(out / 'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out / 'summary.json'), elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), traceback=traceback.format_exc(),
            inputs_sha256=pins, source_sha256=sha(Path(__file__))))
        raise


if __name__ == '__main__': main()
