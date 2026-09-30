"""One gated fixed-six-prism factor-plus-caps native pilot; root launches research."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import native_20260930_prism_first_choice as prior

helper, ext4, ROOT = prior.helper, prior.ext4, prior.ROOT
D = ROOT/'acceleration/results/20260930_prism_column_caps_v3'
CNF, MODEL, SCOPE = D/'instance.cnf', D/'model.json', D/'scope.json'
CNF_SHA = '2b013ebf7f0d7090c192d5b54ec236241d8f4cab0a6efbde90b9498f707bde88'
MODEL_SHA = '524b7bf0bdbdaa617acfca4ebece53560d5adb7b3e700a9bae25cfddbab7cf72'
SCOPE_SHA = 'f4c8914db51ac62f2d796aff3ac789ef60196b204a891905f157c5fb58711540'
ENCODING_SHA = '5c137eb4b497433d02d99e7b1105c34e06f679b55cd5cbe722b8f265d3f47edf'
OBJECT_SHA = 'a0ffaef3a8088a3cf6dd33a1eb7f18696c6b9ddff7e6ad8ac72ffb4a174a7b75'
SPEC = Path(__file__).with_name('native_20260930_prism_column_caps_spec.md')
SECONDS, CONFLICTS, OUTER_SECONDS = 900, 5000000, 920
VARIABLES, CLAUSES, BASE_VARIABLES = 247320, 920401, 245880


def preflight(args):
    helper.require(helper.digest(prior.__file__) == 'fba7a7d5d43cfc549ea9a60680affa845c437859be5f555a6f43edc97ed3cefb', 'frozen native first-choice helper')
    baseline_args = argparse.Namespace(
        encoding_gate=ROOT/'acceleration/results/20260930_independent_review/prism_first_choice_normalization/summary.json',
        encoding_gate_sha256='c5963305cff69ef0242db04d373fdf7cba1339e547191554b64b319165bf8223',
        object_gate=ROOT/'acceleration/results/20260930_independent_review/prism_first_choice_object_calibration/summary.json',
        object_gate_sha256='17927bfbc8355b37f45b42c2bcc9e8ed80b3a5c0f2454da8231a9c72a16d3db2')
    bindings = prior.preflight(baseline_args)
    helper.require(args.encoding_gate_sha256 == ENCODING_SHA and args.object_gate_sha256 == OBJECT_SHA, 'exact new independent gates')
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_SIX_PRISM_COLUMN_CAP_EXTENSION_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_SIX_PRISM_COLUMN_CAP_OBJECT_CHECKER_CALIBRATION_PASS')
    for gate in [enc, obj]:
        for p, h in [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA)]:
            helper.require(gate['inputs_sha256'][helper.key(p)] == h and helper.digest(p) == h, 'exact new cap scope binding')
        for p, h in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT/p) == h, 'every gate-bound input unchanged'); bindings[p] = h
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == ENCODING_SHA, 'object calibration binds exact cap encoding audit')
    model = helper.read(MODEL); scope = helper.read(SCOPE)
    helper.require(model['variables'] == VARIABLES and model['clauses'] == CLAUSES and len(model['incidence_variables']) == 1440, 'exact cap dimensions')
    helper.require(model['outside_column_caps_encoded'] is True and model['residual_D_encoded'] is False and model['target_graph_encoded'] is False, 'caps encoded, residual and target absent')
    helper.require(scope['normalization_choice_id'] == 1 and scope['fixed_six_prism_only'] is True and scope['assumed_target_automorphism'] is False, 'fixed-core normalized scope')
    with CNF.open('rb') as stream: helper.require(stream.readline() == b'p cnf 247320 920401\n', 'exact cap native input header')
    for p in [Path(__file__), SPEC, Path(prior.__file__), args.encoding_gate, args.object_gate,
            ROOT/'acceleration/audit_20260930_prism_column_caps_object.py']:
        bindings[helper.key(p)] = helper.digest(p)
    return bindings


def decode(assignment):
    helper.require(len(assignment) == VARIABLES and {abs(v) for v in assignment} == set(range(1, VARIABLES+1)), 'complete extended assignment')
    projected = [v for v in assignment if abs(v) <= BASE_VARIABLES]
    decoded = prior.decode(projected)
    factor = decoded['factor']; truth = {abs(v): int(v > 0) for v in assignment}
    mismatches = [[r, d] for r in range(12, 36) for d in range(60) if truth[245881+(r-12)*60+d] != factor[r][d]]
    caps = decoded.pop('outside_column_cap_diagnostic')
    caps['encoded'] = True
    helper.require(decoded['producer_exact_check']['valid'] and not mismatches and not caps['violations'], 'candidate factor, all channels and required caps must pass')
    return {**decoded, 'status':'CANDIDATE_FIXED_SIX_PRISM_FACTOR_PLUS_CAPS_PENDING_INDEPENDENT_CHECK',
        'encoding_model_sha256':MODEL_SHA, 'producer_required_column_caps':caps,
        'producer_exact_channels':dict(checked=1440, mismatches=mismatches), 'target_graph':False, 'independent_approval':False}, projected


def run(args):
    bindings = preflight(args); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free; helper.require(host_free >= 21*1024**3, 'host free below21GiB')
    host_available = prior.host_memory_available(); helper.require(host_available >= 9*1024**3, 'host available RAM below9GiB reserve')
    memory, memory_text = ext4.local_capture(['/usr/bin/free', '--bytes'], out/'memory_free')
    linux_available = int(next(line for line in memory_text.splitlines() if line.startswith('Mem:')).split()[-1])
    helper.require(linux_available >= 9*1024**3, 'WSL available RAM below9GiB reserve')
    mount, mount_text = ext4.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out/'filesystem')
    helper.require('ext4' in mount_text.split(), 'calibrated ext4 filesystem required')
    disk, disk_text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out/'disk_free')
    helper.require(int(disk_text.splitlines()[-1]) >= 11*1024**3, 'ext4 free below11GiB')
    helper.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',
        scope='Complete96-choice normalized factor-plus-all1770Ycaps for the fixed six-prism core; no residual D or unrestricted coverage.',
        limits=dict(native_seconds=SECONDS, conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT, file_bytes=ext4.FILE_LIMIT,
            kill_after_seconds=5, outer_windows_guard_seconds=OUTER_SECONDS, maximum_research_attempts=1, automatic_retry=False),
        rationale='Required target column caps strengthen the already normalized fixed-core factor model; one attempt, no comparative performance claim.',
        disk_free_host=host_free, available_host_RAM=host_available, available_WSL_RAM=linux_available, memory_receipt=memory,
        host_memory_method='Windows GlobalMemoryStatusEx via frozen standard-library ctypes helper', filesystem_receipt=mount, ext4_disk_receipt=disk,
        random_seed=None, random_seed_null_reason='Native default retained.',
        shared_components=['Pinned first-choice native preflight, authenticated binary/checker and CLI/ext4 calibrations.',
            'Pinned producer base decoder used only on saved first245880-variable projection for candidate output.',
            'New independent complete assignment, required channel, raw factor and column-cap object gate.']))
    if args.preflight:
        helper.save(out/'summary.json', dict(status='SIX_PRISM_COLUMN_CAP_NATIVE_PREFLIGHT_PASS', research_calls=0, native_call_launched=False,
            encoding_and_object_gates_checked=True, source_sha256=helper.digest(__file__), scope='One fixed-core necessary factor-plus-caps problem'))
        print(json.dumps(dict(status='SIX_PRISM_COLUMN_CAP_NATIVE_PREFLIGHT_PASS', research_calls=0))); return
    made, linux_dir = ext4.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-prism-column-caps-XXXXXX'], out/'mktemp')
    helper.require(linux_dir.startswith('/tmp/conway99-prism-column-caps-') and '\n' not in linux_dir, 'exclusive ext4 proof directory')
    helper.save(out/'workspace.json', dict(path=linux_dir, preserved=True, mktemp=made))
    folder = out/'main'; folder.mkdir(); linux_proof = linux_dir+'/proof.drat'
    command = ext4.command(SECONDS, [helper.linux(helper.NATIVE), '--no-binary', '-c', str(CONFLICTS), helper.linux(CNF), linux_proof])
    helper.save(folder/'launch.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command=command, cnf_sha256=CNF_SHA, model_sha256=MODEL_SHA, ext4_proof=linux_proof))
    print(json.dumps(dict(state='SIX_PRISM_COLUMN_CAP_NATIVE_LAUNCHING', variables=VARIABLES, clauses=CLAUSES, native_seconds=SECONDS)), flush=True)
    receipt = helper.run_record(command, folder/'solver', OUTER_SECONDS)
    result = dict(actual_exit_code=receipt['actual_exit_code'], receipt=receipt, research_calls=1,
        status='FIXED_SIX_PRISM_CAP_ARTIFACTS_PENDING_INDEPENDENT_REVIEW', target_resolution=False,
        scope='Factors plus required Y-caps of one fixed six-prism core only; residual D absent', automatic_retry=False)
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(linux_proof, folder/'proof.drat', folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT, 'proof cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(type=type(error).__name__, message=str(error), linux_original_retained=linux_proof)
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout, VARIABLES); helper.save(folder/'parsed_model.json', dict(assignment=assignment))
                decoded, projected = decode(assignment)
                helper.save(folder/'base_projection_model.json', dict(assignment=projected, source_assignment_sha256=helper.digest(folder/'parsed_model.json'), scope='First245880IDs only; full certificate remains in parsed_model.json'))
                helper.save(folder/'decoded_factor.json', decoded)
                result['producer_local_factor_check'] = decoded['producer_exact_check']
                result['producer_exact_channels'] = decoded['producer_exact_channels']
                result['producer_required_column_caps'] = decoded['producer_required_column_caps']
            except BaseException as error:
                result['parse_decode_failure'] = dict(type=type(error).__name__, message=str(error))
    else: result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'FACTOR_PLUS_CAPS_SAT_RAW_UNCHECKED' if code == 10 else 'FIXED_SIX_PRISM_CAP_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['SAT requires independent full native/assignment/clause/channel/raw-factor/all-column-cap checking.',
        'A factor is not a target graph; residual D is absent.',
        'UNSAT requires complete independent proof replay and excludes only targets with this fixed six-prism core.',
        'UNKNOWN and incomplete proof traces imply no exclusion.']
    helper.save(out/'summary.json', result); print(json.dumps(dict(actual_exit_code=code, interpreted_result=result['interpreted_result'], research_calls=1)), flush=True)


def main():
    ap = argparse.ArgumentParser(); mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight', action='store_true'); mode.add_argument('--research', action='store_true')
    for name in ('out', 'encoding-gate', 'object-gate'): ap.add_argument('--'+name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256'): ap.add_argument('--'+name, required=True)
    run(ap.parse_args())


if __name__ == '__main__': main()
