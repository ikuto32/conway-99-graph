"""Independent extended-assignment and exact raw-factor check for M1 normalization."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import io
import json
import platform
import subprocess
import sys
import time
import audit_20260930_variable_core_factor_object as base
import audit_20260930_variable_core_m1_orbits as normalization

ROOT = Path(__file__).resolve().parents[1]
D = normalization.OUTBASE
GATE = ROOT/'acceleration/results/20260930_independent_review/variable_core_m1_orbits/summary.json'
GATE_SHA = 'ef13877c79a1115cf34a105a9704bb58c0ad981189dfe6acda9b4de4a27d6584'
CALIBRATION = ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json'
CALIBRATION_SHA = '7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a'
BASE_OBJECT_SHA = '8146a2d1c3eedd9d623ee5074b96b0657da5d2786f1f556898c720352165ee82'
need, read, save, digest, key = normalization.need, normalization.read, normalization.save, normalization.digest, normalization.key
common, native = base.common, base.native


def bind():
    need(digest(GATE) == GATE_SHA and digest(CALIBRATION) == CALIBRATION_SHA, 'independent encoding and raw-object gates')
    gate, calibration = read(GATE), read(CALIBRATION)
    need(gate['status'] == 'INDEPENDENT_VARIABLE_CORE_M1_ORBIT_NORMALIZATION_PASS', 'normalization gate status')
    need(calibration['status'] == 'INDEPENDENT_VARIABLE_CORE_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS', 'base object calibration status')
    model, scope, primary, bindings = base.bind_inputs()
    bindings.update(gate['inputs_sha256'])
    bindings.update({key(GATE): GATE_SHA, key(CALIBRATION): CALIBRATION_SHA,
                     key(ROOT/'acceleration/audit_20260930_variable_core_factor_object.py'): BASE_OBJECT_SHA,
                     key(__file__): digest(__file__)})
    for p, value in bindings.items(): need(digest(ROOT/p) == value, 'bound source/artifact identity '+p)
    extension = read(D/'extension.json')
    suffix, _ = normalization.build_suffix(model, extension['representatives'])
    need(extension['appended_clauses'] == suffix, 'recomputed selector suffix')
    with (base.D/'instance.cnf').open('rb') as b, (D/'instance.cnf').open('rb') as e:
        normalization.compare_bytes(b, e, suffix)
    return model, scope, primary, extension, bindings


def check_selector_object(values, extension, base_model, raw=None):
    selectors = extension['selectors']
    selected = [i for i, variable in enumerate(selectors) if values[variable]]
    need(len(selected) == 1, 'exactly one representative selected')
    stage = selected[0]; rep = extension['representatives'][stage]
    for item in base_model['matching_variables']:
        if item['fibre'] != 1: continue
        a, b = item['endpoints']
        need(values[item['id']] == int(rep[a] == b), 'all 66 M1 edge values equal selected representative')
    if raw is not None:
        need(raw['M1'] == [[int(rep[a] == b) for b in range(12)] for a in range(12)], 'independently decoded matching equals selected representative')
    return dict(representative_index=stage, selector_variable=selectors[stage], matching_vector=rep,
                matching_edge_bits_checked=66)


def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        inputs_sha256=bindings, verifier='/root/structural_attack independent extended SAT-object checker',
        producer_imports=False, external_review=False, artifact_availability='LOCAL_ONLY', target_resolution=False,
        shared_components=['Pinned independent native/JSON complete-assignment and raw-CNF parsers.',
            'Pinned independent arbitrary-core primary decode and full integer raw-factor/partial99 checker.',
            'Separately authored normalization byte and selector checks; no producer imports.'],
        limitations=['A valid factor and partial99 object is not a completed99 target graph.',
                     'The selected M1 representative is a harmless normalization, not a target automorphism.',
                     'Residual D existence is not asserted.'])


def synthetic_values(model, extension, stage):
    signed = list(range(1, 110916))
    rep = extension['representatives'][stage]
    for item in model['matching_variables']:
        if item['fibre'] == 1:
            a, b = item['endpoints']; signed[item['id']-1] = item['id'] if rep[a] == b else -item['id']
    for i, variable in enumerate(extension['selectors']): signed[variable-1] = variable if i == stage else -variable
    return signed


def encode_native(signed):
    return b'c synthetic codec control; not research SAT\ns SATISFIABLE\n'+b''.join(
        ('v '+' '.join(map(str, signed[i:i+100]))+(' 0' if i+100 >= len(signed) else '')+'\n').encode()
        for i in range(0, len(signed), 100))


def calibrate(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, scope, primary, extension, bindings = bind(); rejected = []
    def reject(name, call):
        try: call()
        except (ValueError, KeyError, IndexError, TypeError): rejected.append(name)
        else: raise ValueError('corrupt control accepted '+name)
    # All selector choices are positively exercised without asserting full research satisfiability.
    selected_controls = []
    for stage in range(11):
        signed = synthetic_values(model, extension, stage)
        values = common.assignment_values(signed, 110915)
        selected_controls.append(check_selector_object(values, extension, model))
        suffix = b'p cnf 110915 67\n'+b''.join((' '.join(map(str, c))+' 0\n').encode() for c in extension['appended_clauses'])
        common.check_cnf_stream(io.BytesIO(suffix), values, 110915, 67)
    signed = synthetic_values(model, extension, 5); values = common.assignment_values(signed, 110915)
    raw = encode_native(signed)
    native_values, native_record = native.native_values(io.BytesIO(raw), 110915)
    need(native_values == values, 'all full-size native/JSON values')
    # The prefix is a codec fixture, while the real 67-clause suffix is retained literally.
    cnf = b'p cnf 110915 518227\n'+b''.join((str(signed[i % 110904])+' 0\n').encode() for i in range(518160))
    cnf += b''.join((' '.join(map(str, c))+' 0\n').encode() for c in extension['appended_clauses'])
    cnf_record = common.check_cnf_stream(io.BytesIO(cnf), values, 110915, 518227)
    projected = [i if values[i] else -i for i in range(1, 110905)]
    projected_values = common.assignment_values(projected, 110904)
    need(projected_values == values[:110905], 'all 110904 projected values preserved')
    m = [[0, 1], [1, 0]]; p = [[1, 0], [0, 1]]
    rook = base.raw_factor(m, m, p, [[] for _ in range(6)], research=False)
    common.validate_srg(rook['partial_adjacency_full99'], 9, 4, 1, 2)
    save(args.out/'rook9_raw_positive.json', {**rook, 'label': 'Known-valid generic raw factor with emptyY, not research36.'})
    with gzip.open(args.out/'synthetic_native.txt.gz', 'wb') as stream: stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz', 'wb') as stream: stream.write(cnf)
    reject('old_assignment_size', lambda: common.assignment_values(signed[:110904], 110915))
    reject('duplicate_final_variable', lambda: common.assignment_values(signed[:-1]+[signed[-2]], 110915))
    for name, changed in [('missing_status', raw.replace(b's SATISFIABLE\n', b'')),
                          ('missing_final_value', raw.replace(str(signed[-1]).encode()+b' 0\n', b'0\n')),
                          ('missing_terminator', raw.replace(b' 0\n', b'\n'))]:
        reject(name, lambda changed=changed: native.native_values(io.BytesIO(changed), 110915))
    for name, changed in [('old_header', cnf.replace(b'110915 518227', b'110904 518160', 1)),
                          ('missing_suffix_clause', cnf[:cnf.rfind(b'\n', 0, -1)+1]),
                          ('false_unit_in_prefix', cnf.replace((str(signed[0])+' 0\n').encode(), (str(-signed[0])+' 0\n').encode(), 1))]:
        reject(name, lambda changed=changed: common.check_cnf_stream(io.BytesIO(changed), values, 110915, 518227))
    no_selector = values[:]
    for variable in extension['selectors']: no_selector[variable] = 0
    reject('zero_selectors', lambda: check_selector_object(no_selector, extension, model))
    two = values[:]; two[extension['selectors'][0]] = 1
    reject('two_selectors', lambda: check_selector_object(two, extension, model))
    wrong_edge = values[:]
    variable = next(r['id'] for r in model['matching_variables'] if r['fibre'] == 1)
    wrong_edge[variable] ^= 1
    reject('selected_matching_edge_changed', lambda: check_selector_object(wrong_edge, extension, model))
    reject('nonresearch_dimension_mislabelled', lambda: base.raw_factor(m, m, p, [[] for _ in range(6)]))
    need(all(digest(ROOT/k) == h for k, h in bindings.items()), 'stable calibration inputs')
    report = {**provenance(bindings), 'status': 'INDEPENDENT_VARIABLE_CORE_M1_ORBIT_OBJECT_CHECKER_CALIBRATION_PASS',
        'variables': 110915, 'clauses': 518227, 'full_size_codec': dict(native=native_record, clauses=cnf_record,
            projected_base_variables=110904, research_SAT_witness=False),
        'all_eleven_selector_controls': selected_controls, 'known_valid_generic_raw_fixture': rook['exact_checks'],
        'fresh_corruptions_rejected': rejected, 'prior_raw_object_calibration_sha256': CALIBRATION_SHA,
        'positive_research_factor': None, 'positive_research_factor_null_reason': 'No verified complete36row research factor exists in current artifacts; synthetic codec and known rook9 are explicitly separated.',
        'outputs_sha256': {key(p): digest(p) for p in args.out.iterdir() if p.is_file()},
        'solver_calls': 0, 'elapsed_seconds': time.monotonic()-start}
    save(args.out/'summary.json', report)
    print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def sat(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, scope, primary, extension, bindings = bind()
    values = common.assignment_values(read(args.assignment)['assignment'], 110915)
    with args.native_output.open('rb') as stream: native_values, native_record = native.native_values(stream, 110915)
    need(native_values == values, 'all extended native/JSON values agree')
    with (D/'instance.cnf').open('rb') as stream:
        clause_record = common.check_cnf_stream(stream, values, 110915, 518227)
    projection = [i if values[i] else -i for i in range(1, 110905)]
    projected_values = common.assignment_values(projection, 110904)
    # The actual base CNF is checked again, not inferred solely from the extension recipe.
    with (base.D/'instance.cnf').open('rb') as stream:
        base_clause_record = common.check_cnf_stream(stream, projected_values, 110904, 518160)
    raw = base.decode(projected_values, primary)
    selector_record = check_selector_object(values, extension, model, raw)
    if args.decoded:
        produced = read(args.decoded)
        for field in ['M1', 'M2', 'P', 'core_adjacency', 'incidence_matrix', 'prescribed_gram', 'partial_adjacency_full99']:
            need(produced[field] == raw[field], 'independent raw decode '+field)
        if 'encoding_model_sha256' in produced: need(produced['encoding_model_sha256'] == digest(base.D/'model.json'), 'base decoder model identity')
        if 'scope_sha256' in produced: need(produced['scope_sha256'] == digest(base.D/'scope.json'), 'base decoder scope identity')
        if 'full99_graph' in produced: need(produced['full99_graph'] is False, 'partial graph boundary')
    save(args.out/'base_assignment_projection.json', dict(assignment=projection, source_assignment_sha256=digest(args.assignment),
        label='Literal base-variable projection after checking all actual extended native values and clauses.'))
    save(args.out/'independent_factor_and_partial99.json', {**raw, 'encoding_model_sha256': digest(base.D/'model.json'),
        'scope_sha256': digest(base.D/'scope.json'), 'normalization_extension_sha256': digest(D/'extension.json'),
        'selected_representative': selector_record, 'full99_graph': False})
    for path in [args.assignment, args.native_output]+([args.decoded] if args.decoded else []): bindings[key(path)] = digest(path)
    need(all(digest(ROOT/k) == h for k, h in bindings.items()), 'stable research inputs')
    report = {**provenance(bindings), 'status': 'INDEPENDENT_VARIABLE_CORE_M1_ORBIT_SAT_OBJECT_PASS',
        'native_assignment': native_record, 'all_extended_raw_clauses': clause_record,
        'base_projection_raw_clauses': base_clause_record, 'selected_representative': selector_record,
        'raw_exact_checks': raw['exact_checks'],
        'independent_factor_sha256': digest(args.out/'independent_factor_and_partial99.json'),
        'projection_sha256': digest(args.out/'base_assignment_projection.json'), 'elapsed_seconds': time.monotonic()-start}
    save(args.out/'summary.json', report)
    print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='mode', required=True)
    cal = sub.add_parser('calibrate'); cal.add_argument('--out', type=Path, required=True)
    command = sub.add_parser('sat'); command.add_argument('--out', type=Path, required=True)
    command.add_argument('--assignment', type=Path, required=True); command.add_argument('--native-output', type=Path, required=True)
    command.add_argument('--decoded', type=Path)
    args = ap.parse_args()
    try: (calibrate if args.mode == 'calibrate' else sat)(args)
    except BaseException as exc:
        if args.out.exists() and not (args.out/'failure.json').exists(): save(args.out/'failure.json', dict(status='CHECK_FAILED', error=repr(exc)))
        raise


if __name__ == '__main__': main()
