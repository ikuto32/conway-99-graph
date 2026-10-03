"""One gated native attempt for one member of the frozen four-core batch."""
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
BATCH = ROOT / 'acceleration/results/20260930_connected_fixed_core_cnf/summary.json'
BATCH_SHA = '39425b88f3fa5e46d95c3f4231b044c05484fc9d209250d7c045de6589cd82d6'
SPEC = Path(__file__).with_name('native_20260930_connected_fixed_core_spec.md')
SECONDS, CONFLICTS, OUTER_SECONDS = 300, 2000000, 320


def preflight(args):
    helper.require(helper.digest(prior.__file__) == 'e6b00b1a5f1400c925f41b800dbb69bf8d777e16aea0c30fe5343e11fe71438d', 'frozen base native harness')
    base_args = argparse.Namespace(
        encoding_gate=ROOT / 'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json',
        encoding_gate_sha256='ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
        object_gate=ROOT / 'acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json',
        object_gate_sha256='7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a')
    bindings = prior.preflight(base_args)
    helper.require(helper.digest(BATCH) == BATCH_SHA, 'frozen four-core batch')
    batch = helper.read(BATCH)
    helper.require(batch['instances'] == 4 and batch['solver_calls'] == 0, 'frozen preparation population')
    record = batch['records'][args.core_index]
    helper.require(record['core_index'] == args.core_index and record['variables'] == 110904 and record['clauses'] == 518184, 'selected fixed instance')
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_CONNECTED_FIXED_CORE_CNF_BATCH_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_CONNECTED_FIXED_CORE_OBJECT_CHECKER_CALIBRATION_PASS')
    required = {helper.key(BATCH): BATCH_SHA, helper.key(prior.MODEL): prior.MODEL_SHA, helper.key(prior.SCOPE): prior.SCOPE_SHA}
    for kind in ('core', 'units', 'cnf'):
        required[record[kind + '_path']] = record[kind + '_sha256']
    for gate in (enc, obj):
        for p, h in required.items():
            helper.require(gate['inputs_sha256'][p] == h, 'exact batch/raw/core clause gate binding')
        for p, h in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT / p) == h, 'every gate-bound input unchanged: ' + p)
            bindings[p] = h
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds exact independent encoding audit')
    cnf = ROOT / record['cnf_path']
    with cnf.open('rb') as stream:
        helper.require(stream.readline() == b'p cnf 110904 518184\n', 'exact fixed-core CNF header')
    core = helper.read(ROOT / record['core_path'])
    helper.require(core['P'] == list(range(12)) and core['connected36'] is True, 'chosen connected identity-P core')
    for p in (Path(__file__), SPEC, Path(prior.__file__), args.encoding_gate, args.object_gate):
        bindings[helper.key(p)] = helper.digest(p)
    return bindings, record


def run(args):
    bindings, record = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free
    helper.require(host_free >= 21*1024**3, 'host free below21GiB')
    mount, mount_text = ext4.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out / 'filesystem')
    helper.require('ext4' in mount_text.split(), 'calibrated ext4 required')
    disk, disk_text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out / 'disk_free')
    helper.require(int(disk_text.splitlines()[-1]) >= 11*1024**3, 'ext4 free below11GiB')
    helper.save(out / 'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        inputs_sha256=bindings, core_index=args.core_index, fixed_instance=record,
        mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',
        scope='One of four explicitly chosen connected identity-P core necessary factor models; no residual D or exhaustive core coverage.',
        limits=dict(native_seconds=SECONDS, conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT,
            file_bytes=ext4.FILE_LIMIT, kill_after_seconds=5, outer_windows_guard_seconds=OUTER_SECONDS,
            maximum_research_attempts=1, automatic_retry=False),
        random_seed=None, random_seed_null_reason='Native default retained.',
        disk_free_host=host_free, filesystem_receipt=mount, ext4_disk_receipt=disk,
        shared_components=['Pinned base native harness, native binary, CLI and ext4 calibration.',
            'Producer base decoder is not the separate independent raw checker.']))
    if args.preflight:
        helper.save(out / 'summary.json', dict(status='CONNECTED_FIXED_CORE_NATIVE_PREFLIGHT_PASS', core_index=args.core_index,
            research_calls=0, native_call_launched=False, source_sha256=helper.digest(__file__)))
        print(json.dumps(dict(status='CONNECTED_FIXED_CORE_NATIVE_PREFLIGHT_PASS', core_index=args.core_index, research_calls=0)))
        return
    prefix = f'/tmp/conway99-connected-core-{args.core_index:02d}-'
    made, linux_dir = ext4.local_capture(['/usr/bin/mktemp', '-d', prefix + 'XXXXXX'], out / 'mktemp')
    helper.require(linux_dir.startswith(prefix) and '\n' not in linux_dir, 'exclusive ext4 workspace')
    helper.save(out / 'workspace.json', dict(path=linux_dir, preserved=True, mktemp=made))
    folder = out / 'main'
    folder.mkdir()
    linux_proof = linux_dir + '/proof.drat'
    command = ext4.command(SECONDS, [helper.linux(helper.NATIVE), '--no-binary', '-c', str(CONFLICTS), helper.linux(ROOT / record['cnf_path']), linux_proof])
    helper.save(folder / 'launch.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command=command,
        core_index=args.core_index, cnf_sha256=record['cnf_sha256'], core_sha256=record['core_sha256'],
        model_sha256=prior.MODEL_SHA, ext4_proof=linux_proof))
    print(json.dumps(dict(state='CONNECTED_FIXED_CORE_NATIVE_LAUNCHING', core_index=args.core_index, seconds=SECONDS)), flush=True)
    receipt = helper.run_record(command, folder / 'solver', OUTER_SECONDS)
    result = dict(status='FIXED_CONNECTED_CORE_ARTIFACTS_PENDING_INDEPENDENT_REVIEW', core_index=args.core_index,
        actual_exit_code=receipt['actual_exit_code'], receipt=receipt, research_calls=1,
        target_resolution=False, automatic_retry=False,
        scope='One fixed connected core; complete factor only, residual D absent.')
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(linux_proof, folder / 'proof.drat', folder / 'transfer')
            helper.require((folder / 'proof.drat').stat().st_size <= ext4.FILE_LIMIT, 'proof file cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(type=type(error).__name__, message=str(error), linux_original_retained=linux_proof)
        stdout = (folder / 'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout, 110904)
                helper.save(folder / 'parsed_model.json', dict(assignment=assignment))
                decoder.decode(argparse.Namespace(model=prior.MODEL, assignment=folder / 'parsed_model.json', out=folder / 'decoded_factor.json'))
                result['producer_local_factor_check'] = helper.read(folder / 'decoded_factor.json')['producer_exact_check']
            except BaseException as error:
                result['parse_decode_failure'] = dict(type=type(error).__name__, message=str(error))
    else:
        result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'PARTIAL_FACTOR_SAT_RAW_UNCHECKED' if code == 10 else 'FIXED_CORE_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p): helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['Independent complete assignment and raw core/factor checking required on SAT; D remains absent.',
        'A complete independently replayed UNSAT trace excludes only this fixed core through the audited necessary encoding.',
        'Partial traces and resource outcomes establish no exclusion.']
    helper.save(out / 'summary.json', result)
    print(json.dumps(dict(core_index=args.core_index, actual_exit_code=code, interpreted_result=result['interpreted_result'])), flush=True)


def main():
    ap = argparse.ArgumentParser()
    modes = ap.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight', action='store_true')
    modes.add_argument('--research', action='store_true')
    ap.add_argument('--core-index', type=int, choices=range(4), required=True)
    for name in ('out', 'encoding-gate', 'object-gate'):
        ap.add_argument('--' + name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256'):
        ap.add_argument('--' + name, required=True)
    run(ap.parse_args())


if __name__ == '__main__':
    main()
