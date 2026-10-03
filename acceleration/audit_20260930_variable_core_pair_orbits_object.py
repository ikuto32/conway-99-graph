"""Exact enlarged-object wrapper around the frozen independent base checker.

The pair-normalization producer authors this orchestration wrapper; its raw
factor checking path is independently authored and pinned. This code never
approves the pair encoding or promotes its own research output.
"""
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

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/'acceleration/results/20260930_variable_core_pair_orbits'
VARIABLES, CLAUSES, BASE_VARIABLES, BASE_CLAUSES = 114484, 561121, 110904, 518160
ENCODING_STATUS = 'INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_NORMALIZATION_PASS'
CAL = ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json'
CAL_SHA = '7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a'
PINS = {
    D/'instance.cnf': 'a2b336d4d5e49742a81866da01c813c4b4ca34e19fd215155351da7d42a68b40',
    D/'extension.json': '2eea0d0a71fb6346c0a6a47f2ac687383a588248e52711edf97d535237f21f59',
    D/'coverage.json': '739dea275bc32b07ff13aff0f67d7ae69030051a1f00aeef3a723b5b3edf0714',
    ROOT/'acceleration/audit_20260930_variable_core_factor_object.py': '8146a2d1c3eedd9d623ee5074b96b0657da5d2786f1f556898c720352165ee82',
}
need, read, save, digest, key = base.need, base.read, base.save, base.digest, base.key
common, native = base.common, base.native


def bind(args):
    need(digest(args.encoding_gate) == args.encoding_gate_sha256, 'explicit independent normalization gate hash')
    gate = read(args.encoding_gate); need(gate['status'] == ENCODING_STATUS, 'independent pair normalization status')
    need(digest(CAL) == CAL_SHA and read(CAL)['status'] == 'INDEPENDENT_VARIABLE_CORE_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS', 'independent base object calibration')
    model, scope, primary, bindings = base.bind_inputs()
    for p, h in PINS.items():
        need(digest(p) == h, 'frozen wrapper input '+key(p)); bindings[key(p)] = h
    for p in [D/'instance.cnf', D/'extension.json', D/'coverage.json', base.D/'model.json', base.D/'scope.json']:
        need(gate['inputs_sha256'][key(p)] == digest(p), 'new gate binds required scope '+key(p))
    bindings.update(gate['inputs_sha256'])
    bindings.update({key(args.encoding_gate): args.encoding_gate_sha256, key(CAL): CAL_SHA, key(__file__): digest(__file__)})
    for p, h in bindings.items(): need(digest(ROOT/p) == h, 'bound source or artifact '+p)
    extension = read(D/'extension.json'); coverage = read(D/'coverage.json')
    need((extension['variables'], extension['clauses']) == (VARIABLES, CLAUSES), 'exact enlarged dimensions')
    need(extension['selectors'] == list(range(BASE_VARIABLES+1, VARIABLES+1)), 'consecutive new selectors')
    need(extension['representative_pairs'] == coverage['pair_representatives'], 'gate-bound exact ordered representatives')
    need(len(extension['representative_pairs']) == 3580, 'complete representative count')
    # Decode edge implications from the exact model, separately from producer generation.
    ids = {(item['fibre'], *item['endpoints']): item['id'] for item in model['matching_variables']}
    expected = [extension['selectors']]
    for selector, rep in zip(extension['selectors'], extension['representative_pairs']):
        for fibre in (1, 2):
            q = rep[f'M{fibre}']
            for a in range(12):
                if a < q[a]: expected.append([-selector, ids[fibre, a, q[a]]])
    need(expected == extension['appended_clauses'] and len(expected) == 42961, 'independent suffix reconstruction')
    with (base.D/'instance.cnf').open('rb') as before, (D/'instance.cnf').open('rb') as after:
        need(before.readline() == b'p cnf 110904 518160\n', 'base exact header')
        need(after.readline() == b'p cnf 114484 561121\n', 'extension exact header')
        for block in iter(lambda: before.read(1048576), b''): need(after.read(len(block)) == block, 'all original clause-body bytes')
        need(after.read() == b''.join((' '.join(map(str, row))+' 0\n').encode() for row in expected), 'all appended bytes only')
    return model, scope, primary, extension, bindings


def selected_pair(values, extension, model, raw=None):
    selected = [i for i, variable in enumerate(extension['selectors']) if values[variable]]
    need(len(selected) == 1, 'exactly one ordered representative selected')
    stage = selected[0]; rep = extension['representative_pairs'][stage]
    need(rep['pair_representative_index'] == stage, 'stable representative index')
    for item in model['matching_variables']:
        a, b = item['endpoints']; q = rep[f'M{item["fibre"]}']
        need(values[item['id']] == int(q[a] == b), 'all 132 matching edges equal selected pair')
    if raw is not None:
        for field in ('M1', 'M2'):
            q = rep[field]
            need(raw[field] == [[int(q[a] == b) for b in range(12)] for a in range(12)], 'raw decoded '+field+' equals selected representative')
    return dict(pair_representative_index=stage, selector_variable=extension['selectors'][stage],
        first_stage=rep['first_stage'], second_orbit=rep['second_orbit'], M1=rep['M1'], M2=rep['M2'], matching_edge_bits_checked=132)


def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        inputs_sha256=bindings, checking_path='Full enlarged assignment/CNF wrapper plus frozen independent arbitrary-core object checker',
        wrapper_author='/root/structural_attack (also the pair-normalization producer)',
        raw_checker_author='/root/eight_domain_audit', producer_code_imported=False,
        self_promotion_authorized=False, external_review=False, target_resolution=False,
        artifact_availability='LOCAL_ONLY',
        shared_components=['Frozen independently authored native/JSON and literal CNF parsers.',
            'Frozen independently authored base primary decode, exact Gram/margin/cap and partial99 checks.',
            'New selector/projection wrapper authored by the pair-normalization producer; separate review required.'],
        limitations=['A factor and partial99 graph do not provide residual D or a complete target graph.',
            'The independent encoding gate is a premise; this wrapper does not approve its own encoding.',
            'Research results require separate reviewer promotion.'])


def native_bytes(signed):
    return b'c synthetic codec only; not research SAT\ns SATISFIABLE\n'+b''.join(
        ('v '+' '.join(map(str, signed[i:i+100]))+(' 0' if i+100 >= len(signed) else '')+'\n').encode()
        for i in range(0, len(signed), 100))


def calibrate(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, scope, primary, extension, bindings = bind(args); rejected = []
    def reject(name, call):
        try: call()
        except (ValueError, KeyError, IndexError, TypeError): rejected.append(name)
        else: raise ValueError('corrupt control accepted '+name)
    values = bytearray([1])*(VARIABLES+1); values[0] = 2
    for v in extension['selectors']: values[v] = 0
    positive_count = 0
    for stage, rep in enumerate(extension['representative_pairs']):
        if stage: values[extension['selectors'][stage-1]] = 0
        values[extension['selectors'][stage]] = 1
        for item in model['matching_variables']:
            a, b = item['endpoints']; values[item['id']] = int(rep[f'M{item["fibre"]}'][a] == b)
        selected_pair(values, extension, model)
        # True-selector implications are checked explicitly; every other binary clause
        # is true on its negative selector literal. One at-least-one clause is true.
        for row in extension['appended_clauses'][1+12*stage:1+12*(stage+1)]:
            need(values[row[1]] == 1 and row[0] == -extension['selectors'][stage], 'all twelve selected implications')
        positive_count += 1
    signed = [i if values[i] else -i for i in range(1, VARIABLES+1)]
    need(common.assignment_values(signed, VARIABLES) == values, 'full signed assignment codec')
    raw = native_bytes(signed); parsed, native_record = native.native_values(io.BytesIO(raw), VARIABLES)
    need(parsed == values, 'full enlarged native/JSON agreement')
    cnf = f'p cnf {VARIABLES} {CLAUSES}\n'.encode()+b''.join((str(signed[i % BASE_VARIABLES])+' 0\n').encode() for i in range(BASE_CLAUSES))
    cnf += b''.join((' '.join(map(str, row))+' 0\n').encode() for row in extension['appended_clauses'])
    cnf_record = common.check_cnf_stream(io.BytesIO(cnf), values, VARIABLES, CLAUSES)
    projection = [i if values[i] else -i for i in range(1, BASE_VARIABLES+1)]
    need(common.assignment_values(projection, BASE_VARIABLES) == values[:BASE_VARIABLES+1], 'exact complete base projection')
    m = [[0, 1], [1, 0]]; p = [[1, 0], [0, 1]]
    rook = base.raw_factor(m, m, p, [[] for _ in range(6)], research=False)
    common.validate_srg(rook['partial_adjacency_full99'], 9, 4, 1, 2)
    save(args.out/'rook9_raw_positive.json', {**rook, 'label': 'Generic exact positive; emptyY, not research36.'})
    with gzip.open(args.out/'synthetic_native.txt.gz', 'wb') as stream: stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz', 'wb') as stream: stream.write(cnf)
    reject('missing_selector_tail_assignment', lambda: common.assignment_values(signed[:BASE_VARIABLES], VARIABLES))
    reject('duplicate_final_literal', lambda: common.assignment_values(signed[:-1]+[signed[-2]], VARIABLES))
    reject('out_of_range_literal', lambda: common.assignment_values(signed[:-1]+[VARIABLES+1], VARIABLES))
    for name, changed in [('missing_status', raw.replace(b's SATISFIABLE\n', b'')),
                          ('missing_last_literal', raw.replace(str(signed[-1]).encode()+b' 0\n', b'0\n')),
                          ('missing_terminator', raw.replace(b' 0\n', b'\n')),
                          ('duplicate_native_literal', raw.replace(b'v 1 2 ', b'v 1 1 ', 1))]:
        reject(name, lambda changed=changed: native.native_values(io.BytesIO(changed), VARIABLES))
    for name, changed in [('old_header', cnf.replace(b'114484 561121', b'110904 518160', 1)),
                          ('missing_last_clause', cnf[:cnf.rfind(b'\n', 0, -1)+1]),
                          ('false_prefix_literal', cnf.replace(b'1 0\n', b'-1 0\n', 1))]:
        reject(name, lambda changed=changed: common.check_cnf_stream(io.BytesIO(changed), values, VARIABLES, CLAUSES))
    no_selector = values[:]; no_selector[extension['selectors'][-1]] = 0
    reject('zero_selectors', lambda: selected_pair(no_selector, extension, model))
    two = values[:]; two[extension['selectors'][0]] = 1
    reject('two_selectors', lambda: selected_pair(two, extension, model))
    for fibre in (1, 2):
        bad = values[:]; variable = next(item['id'] for item in model['matching_variables'] if item['fibre'] == fibre); bad[variable] ^= 1
        reject('changed_M'+str(fibre)+'_edge', lambda bad=bad: selected_pair(bad, extension, model))
    reject('small_control_as_research', lambda: base.raw_factor(m, m, p, [[] for _ in range(6)]))
    reject('raw_fixedpoint_M1', lambda: base.raw_factor([[1, 0], [0, 1]], m, p, [[] for _ in range(6)], research=False))
    reject('raw_nonpermutation_P', lambda: base.raw_factor(m, m, [[1, 0], [1, 0]], [[] for _ in range(6)], research=False))
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'stable calibration inputs')
    report = {**provenance(bindings), 'status': 'VARIABLE_CORE_PAIR_ORBIT_OBJECT_CHECKER_CALIBRATION_PASS',
        'variables': VARIABLES, 'clauses': CLAUSES, 'positive_selector_suffix_cases': positive_count,
        'synthetic_fullsize_codec': dict(native=native_record, cnf=cnf_record, research_SAT_witness=False),
        'known_valid_raw_generic': rook['exact_checks'], 'fresh_corruptions_rejected': rejected,
        'positive_research_factor': None, 'positive_research_factor_null_reason': 'No complete research36 witness is assumed; codec and rook9 positive controls are separate.',
        'independent_wrapper_review': 'PENDING', 'solver_calls': 0,
        'outputs_sha256': {key(p): digest(p) for p in args.out.iterdir() if p.is_file()},
        'elapsed_seconds': time.monotonic()-start}
    save(args.out/'summary.json', report); print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def sat(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, scope, primary, extension, bindings = bind(args)
    values = common.assignment_values(read(args.assignment)['assignment'], VARIABLES)
    with args.native_output.open('rb') as stream: parsed, native_record = native.native_values(stream, VARIABLES)
    need(parsed == values, 'complete enlarged native/JSON agreement')
    with (D/'instance.cnf').open('rb') as stream: clause_record = common.check_cnf_stream(stream, values, VARIABLES, CLAUSES)
    projection = [i if values[i] else -i for i in range(1, BASE_VARIABLES+1)]
    projected_values = common.assignment_values(projection, BASE_VARIABLES)
    with (base.D/'instance.cnf').open('rb') as stream: base_clauses = common.check_cnf_stream(stream, projected_values, BASE_VARIABLES, BASE_CLAUSES)
    raw = base.decode(projected_values, primary); selected = selected_pair(values, extension, model, raw)
    if args.decoded:
        produced = read(args.decoded)
        for field in ['M1', 'M2', 'P', 'core_adjacency', 'incidence_matrix', 'prescribed_gram', 'partial_adjacency_full99']:
            need(produced[field] == raw[field], 'raw independent decode '+field)
        if 'encoding_model_sha256' in produced: need(produced['encoding_model_sha256'] == digest(base.D/'model.json'), 'base model identity')
        if 'scope_sha256' in produced: need(produced['scope_sha256'] == digest(base.D/'scope.json'), 'base scope identity')
        if 'full99_graph' in produced: need(produced['full99_graph'] is False, 'partial graph boundary')
    save(args.out/'base_assignment_projection.json', dict(assignment=projection, source_assignment_sha256=digest(args.assignment)))
    save(args.out/'independent_path_factor_and_partial99.json', {**raw, 'full99_graph': False,
        'selected_pair': selected, 'encoding_model_sha256': digest(base.D/'model.json'),
        'scope_sha256': digest(base.D/'scope.json'), 'normalization_extension_sha256': digest(D/'extension.json')})
    for path in [args.assignment, args.native_output]+([args.decoded] if args.decoded else []): bindings[key(path)] = digest(path)
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'stable research inputs')
    report = {**provenance(bindings), 'status': 'VARIABLE_CORE_PAIR_ORBIT_SAT_OBJECT_CHECK_PASS_PENDING_REVIEW',
        'native_assignment': native_record, 'all_enlarged_raw_clauses': clause_record, 'base_projection_raw_clauses': base_clauses,
        'selected_pair': selected, 'raw_exact_checks': raw['exact_checks'],
        'independent_path_factor_sha256': digest(args.out/'independent_path_factor_and_partial99.json'),
        'projection_sha256': digest(args.out/'base_assignment_projection.json'), 'elapsed_seconds': time.monotonic()-start}
    save(args.out/'summary.json', report); print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='mode', required=True)
    for mode in ('calibrate', 'sat'):
        p = sub.add_parser(mode); p.add_argument('--out', type=Path, required=True)
        p.add_argument('--encoding-gate', type=Path, required=True); p.add_argument('--encoding-gate-sha256', required=True)
        if mode == 'sat':
            p.add_argument('--assignment', type=Path, required=True); p.add_argument('--native-output', type=Path, required=True); p.add_argument('--decoded', type=Path)
    args = ap.parse_args()
    try: (calibrate if args.mode == 'calibrate' else sat)(args)
    except BaseException as exc:
        if args.out.exists() and not (args.out/'failure.json').exists(): save(args.out/'failure.json', dict(status='CHECK_FAILED', error=repr(exc)))
        raise


if __name__ == '__main__': main()
