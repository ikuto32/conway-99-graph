"""Gated 900-second native ordered-matching-pair pilot; root launches research mode."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import native_20260930_variable_core_factor as prior

helper, ext4, decoder = prior.helper, prior.ext4, prior.decoder
ROOT = helper.ROOT
DATA = ROOT/'acceleration/results/20260930_variable_core_pair_orbits'
CNF, EXTENSION = DATA/'instance.cnf', DATA/'extension.json'
CNF_SHA = 'a2b336d4d5e49742a81866da01c813c4b4ca34e19fd215155351da7d42a68b40'
EXTENSION_SHA = '2eea0d0a71fb6346c0a6a47f2ac687383a588248e52711edf97d535237f21f59'
SPEC = Path(__file__).with_name('native_20260930_variable_core_pair_orbits_spec.md')
SECONDS, CONFLICTS, OUTER_SECONDS = 900, 5000000, 920
BASE_ENCODING = ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json'
BASE_OBJECT = ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json'
ENCODING_STATUS = 'INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_NORMALIZATION_PASS'
OBJECT_STATUS = 'VARIABLE_CORE_PAIR_ORBIT_OBJECT_CHECKER_CALIBRATION_PASS'
OBJECT_REVIEW_STATUS = 'INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_OBJECT_WRAPPER_REVIEW_PASS'


def preflight(args):
    helper.require(helper.digest(Path(prior.__file__)) == 'e6b00b1a5f1400c925f41b800dbb69bf8d777e16aea0c30fe5343e11fe71438d', 'frozen calibrated base runner')
    base_args = argparse.Namespace(encoding_gate=BASE_ENCODING,
        encoding_gate_sha256='ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
        object_gate=BASE_OBJECT, object_gate_sha256='7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a')
    bindings = prior.preflight(base_args)
    for path, expected in [(CNF, CNF_SHA), (EXTENSION, EXTENSION_SHA)]:
        helper.require(helper.digest(path) == expected, 'normalized input bytes'); bindings[helper.key(path)] = expected
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, ENCODING_STATUS)
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, OBJECT_STATUS)
    review = helper.checked_gate(args.object_review, args.object_review_sha256, OBJECT_REVIEW_STATUS)
    helper.require(review['inputs_sha256'][helper.key(args.object_gate)] == args.object_gate_sha256, 'independent wrapper review binds exact calibration')
    wrapper = ROOT/'acceleration/audit_20260930_variable_core_pair_orbits_object.py'
    helper.require(review['inputs_sha256'][helper.key(wrapper)] == helper.digest(wrapper), 'independent wrapper review binds exact checking source')
    for gate in [enc, obj]:
        for path, expected in [(CNF, CNF_SHA), (EXTENSION, EXTENSION_SHA), (prior.MODEL, prior.MODEL_SHA), (prior.SCOPE, prior.SCOPE_SHA)]:
            helper.require(gate['inputs_sha256'][helper.key(path)] == expected, 'new normalization/object input binding')
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds exact new normalization gate')
    extension = helper.read(EXTENSION)
    helper.require(extension['variables'] == 114484 and extension['clauses'] == 561121, 'exact extension dimensions')
    helper.require(extension['base_cnf_sha256'] == prior.CNF_SHA and extension['base_model_sha256'] == prior.MODEL_SHA, 'exact old base')
    helper.require(extension['selectors'] == list(range(110905, 114485)) and len(extension['appended_clauses']) == 42961, 'exact selector extension')
    helper.require(extension['P_restricted'] is False and extension['target_automorphism_assumed'] is False and extension['residual_D_included'] is False, 'normalization scope')
    with CNF.open('rb') as stream: helper.require(stream.readline() == b'p cnf 114484 561121\n', 'native normalized input header')
    for p in [Path(__file__), SPEC, Path(prior.__file__), args.encoding_gate, args.object_gate, args.object_review, wrapper]: bindings[helper.key(p)] = helper.digest(p)
    return bindings


def run(args):
    bindings = preflight(args); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free; helper.require(host_free >= 21*1024**3, 'host free below21GiB')
    mount, mount_text = ext4.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out/'filesystem')
    helper.require('ext4' in mount_text.split(), 'calibrated ext4 filesystem required')
    disk, disk_text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out/'disk_free')
    helper.require(int(disk_text.splitlines()[-1]) >= 11*1024**3, 'ext4 free below11GiB')
    helper.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        inputs_sha256=bindings, mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',
        scope='Universal necessary arbitrary-core factor after complete3580 ordered-pair normalization; P arbitrary; no residual D.',
        limits=dict(native_seconds=SECONDS, conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT,
            file_bytes=ext4.FILE_LIMIT, kill_after_seconds=5, outer_windows_guard_seconds=OUTER_SECONDS,
            maximum_research_attempts=1, automatic_retry=False),
        rationale='Complete ordered-pair relabelling reduction; one bounded attempt, no performance claim.',
        disk_free_host=host_free, filesystem_receipt=mount, ext4_disk_receipt=disk,
        random_seed=None, random_seed_null_reason='Native default retained.',
        shared_components=['Pinned native base preflight, subprocess/parser and calibrated ext4 helpers.',
            'Frozen producer base decoder applied only to the explicitly saved base-variable projection.',
            'Independent extended-object checker remains mandatory.']))
    if args.preflight:
        helper.save(out/'summary.json', dict(status='VARIABLE_CORE_PAIR_ORBIT_NATIVE_PREFLIGHT_PASS',
            research_calls=0, native_call_launched=False, normalization_encoding_object_gates_checked=True,
            source_sha256=helper.digest(Path(__file__)), full_target_graph_encoded=False))
        print(json.dumps(dict(status='VARIABLE_CORE_PAIR_ORBIT_NATIVE_PREFLIGHT_PASS', research_calls=0))); return
    made, linux_dir = ext4.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-variable-core-pair-orbits-XXXXXX'], out/'mktemp')
    helper.require(linux_dir.startswith('/tmp/conway99-variable-core-pair-orbits-') and '\n' not in linux_dir, 'exclusive ext4 proof directory')
    helper.save(out/'workspace.json', dict(path=linux_dir, preserved=True, mktemp=made))
    folder = out/'main'; folder.mkdir(); linux_proof = linux_dir+'/proof.drat'
    command = ext4.command(SECONDS, [helper.linux(helper.NATIVE), '--no-binary', '-c', str(CONFLICTS), helper.linux(CNF), linux_proof])
    helper.save(folder/'launch.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command=command,
        cnf_sha256=CNF_SHA, extension_sha256=EXTENSION_SHA, base_model_sha256=prior.MODEL_SHA, ext4_proof=linux_proof))
    print(json.dumps(dict(state='VARIABLE_CORE_PAIR_ORBIT_NATIVE_LAUNCHING', variables=114484, clauses=561121, native_seconds=SECONDS)), flush=True)
    receipt = helper.run_record(command, folder/'solver', OUTER_SECONDS)
    result = dict(actual_exit_code=receipt['actual_exit_code'], receipt=receipt, research_calls=1,
        status='PAIR_ORBIT_FACTOR_ARTIFACTS_PENDING_INDEPENDENT_REVIEW', target_resolution=False,
        scope='Normalized universally necessary core/factor only; no complete target graph.', automatic_retry=False)
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(linux_proof, folder/'proof.drat', folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT, 'proof file cap')
        except BaseException as exc:
            result['proof_copy_failure'] = dict(type=type(exc).__name__, message=str(exc), linux_original_retained=linux_proof)
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout, 114484)
                helper.save(folder/'parsed_model.json', dict(assignment=assignment))
                projection = [literal for literal in assignment if abs(literal) <= 110904]
                helper.require(len(projection) == 110904, 'complete base-variable projection')
                helper.save(folder/'base_assignment_projection.json', dict(assignment=projection,
                    source_assignment_sha256=helper.digest(folder/'parsed_model.json')))
                decoder.decode(argparse.Namespace(model=prior.MODEL, assignment=folder/'base_assignment_projection.json', out=folder/'decoded_factor.json'))
                result['producer_local_factor_check'] = helper.read(folder/'decoded_factor.json')['producer_exact_check']
            except BaseException as exc:
                result['parse_decode_failure'] = dict(type=type(exc).__name__, message=str(exc))
    else: result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'PARTIAL_FACTOR_SAT_RAW_UNCHECKED' if code == 10 else 'NECESSARY_MODEL_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p): helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['SAT requires complete independent clause/object checks and still supplies no residual D.',
        'UNSAT requires complete proof replay; encoding and coverage gates alone are not a resolution.',
        'Incomplete traces and native/resource UNKNOWN outcomes establish no mathematical exclusion.']
    helper.save(out/'summary.json', result)
    print(json.dumps(dict(actual_exit_code=code, interpreted_result=result['interpreted_result'], research_calls=1)), flush=True)


def main():
    ap = argparse.ArgumentParser(); modes = ap.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight', action='store_true'); modes.add_argument('--research', action='store_true')
    for name in ('out', 'encoding-gate', 'object-gate', 'object-review'): ap.add_argument('--'+name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256', 'object-review-sha256'): ap.add_argument('--'+name, required=True)
    run(ap.parse_args())


if __name__ == '__main__': main()
