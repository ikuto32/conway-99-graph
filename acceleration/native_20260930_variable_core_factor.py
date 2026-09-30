"""Gated native arbitrary-core factor pilot; root controls research launch."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4
import theory_20260930_variable_core_factor_cnf as decoder

ROOT = helper.ROOT
DATA = ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
CNF, MODEL, SCOPE = DATA/'instance.cnf', DATA/'model.json', DATA/'scope.json'
CNF_SHA = '21b2cd8067971da66317afb3814e2b4f9232528fc8b1daceda4ff80594425684'
MODEL_SHA = '42071b881973450db0f1813356133688b7532dd7d0495d37962acc5fa8c071f2'
SCOPE_SHA = 'd5366bd061ab9f248d861522241fd28862f7164f591788f859bba90c91936d60'
DECODER_SHA = 'ed95e25e9d33c96e5b207e8ebb0f7a515d66d6d2710af3507b30c861e8bbec4a'
COVERAGE = ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json'
COVERAGE_SHA = 'a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd'
SPEC = Path(__file__).with_name('native_20260930_variable_core_factor_spec.md')
ENGINEERING_GATES = [
    ('acceleration/results/20260930_native_cli_calibration/summary.json', 'f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb', 'INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
    ('acceleration/results/20260930_native_proof_location/summary.json', 'd1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619', 'NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS'),
]


def preflight(args):
    bindings = {}
    exact = [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA), (Path(decoder.__file__), DECODER_SHA),
             (helper.NATIVE, helper.NATIVE_SHA), (helper.CHECKER, helper.CHECKER_SHA)]
    for path, expected in exact:
        helper.require(helper.digest(path) == expected, 'exact input/native identity: '+helper.key(path))
        bindings[helper.key(path)] = expected
    helper.checked_gate(COVERAGE, COVERAGE_SHA, 'INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS')
    bindings[helper.key(COVERAGE)] = COVERAGE_SHA
    for name, expected, status in ENGINEERING_GATES:
        helper.checked_gate(ROOT/name, expected, status)
        bindings[name] = expected
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS')
    for path, expected in [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA), (COVERAGE, COVERAGE_SHA)]:
        helper.require(enc['inputs_sha256'][helper.key(path)] == expected, 'arbitrary-core encoding and coverage binding')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_VARIABLE_CORE_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS')
    for path, expected in [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA)]:
        helper.require(obj['inputs_sha256'][helper.key(path)] == expected, 'arbitrary-core object scope binding')
    for path in [Path(__file__), SPEC, Path(helper.__file__), Path(ext4.__file__), ext4.SPEC,
                 args.encoding_gate, args.object_gate, ROOT/'uv.lock', ROOT/'pyproject.toml']:
        bindings[helper.key(path)] = helper.digest(path)
    model, scope = helper.read(MODEL), helper.read(SCOPE)
    helper.require(model['schema'] == 'ARBITRARY_TRIANGLE_CORE_FACTOR_CHANNEL_PREFIX_CNF_V1', 'exact arbitrary-core schema')
    helper.require(model['variables'] == 110904 and model['clauses'] == 518160, 'exact variables/clauses')
    helper.require(model['scope_sha256'] == SCOPE_SHA and scope['normalization_coverage_gate_sha256'] == COVERAGE_SHA, 'scope/coverage pins')
    helper.require(scope['core_extra_restrictions'] == [] and scope['component_restrictions'] is False, 'arbitrary core scope')
    helper.require(scope['fixed_Q1_Q2'] is False and scope['zero_incidence_folds'] == 0, 'all free incidence entries')
    helper.require(scope['target_automorphism_assumed'] is False and scope['residual_D_included'] is False, 'necessary model boundary')
    helper.require(model['full_target_graph_encoded'] is False and model['primary_variables'] == 1716, 'partial factor only')
    with CNF.open('rb') as f:
        helper.require(f.readline() == b'p cnf 110904 518160\n', 'exact native input header')
    return bindings


def run(args):
    bindings = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free
    helper.require(host_free >= 21*1024**3, 'host free below21GiB')
    mount, mount_text = ext4.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out/'filesystem')
    helper.require('ext4' in mount_text.split(), 'calibrated ext4 filesystem required')
    disk, disk_text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out/'disk_free')
    helper.require(int(disk_text.splitlines()[-1]) >= 11*1024**3, 'ext4 free below11GiB')
    helper.save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(),
        'inputs_sha256': bindings, 'mode': 'PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',
        'scope': 'Universally necessary arbitrary normalized core/factor with exact Gram and both cap families; no residualD or full target graph.',
        'limits': {'native_seconds': 300, 'conflicts': 1000000, 'address_space_bytes': ext4.AS_LIMIT,
                   'file_bytes': ext4.FILE_LIMIT, 'kill_after_seconds': 5, 'outer_windows_guard_seconds': 320},
        'disk_free_host': host_free, 'filesystem_receipt': mount, 'ext4_disk_receipt': disk,
        'random_seed': None, 'random_seed_null_reason': 'Native default retained.',
        'shared_components': ['Frozen native parser/subprocess/ext4-copy helpers', 'Authenticated native executable/checker and engineering calibrations',
                              'Frozen producer decoder; independent raw-object checker remains mandatory'],
        'fixed_core_or_Q1_exclusion_premise': False})
    if args.preflight:
        helper.save(out/'summary.json', {'status': 'VARIABLE_CORE_FACTOR_NATIVE_PREFLIGHT_PASS', 'research_calls': 0,
                    'normalization_encoding_object_gates_checked': True, 'source_sha256': helper.digest(Path(__file__)),
                    'native_call_launched': False, 'full_target_graph_encoded': False})
        print(json.dumps({'status': 'VARIABLE_CORE_FACTOR_NATIVE_PREFLIGHT_PASS', 'research_calls': 0}))
        return
    made, linux_dir = ext4.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-variable-core-factor-XXXXXX'], out/'mktemp')
    helper.require(linux_dir.startswith('/tmp/conway99-variable-core-factor-') and '\n' not in linux_dir, 'exclusive proof directory')
    helper.save(out/'workspace.json', {'path': linux_dir, 'preserved': True, 'mktemp': made})
    folder = out/'main'
    folder.mkdir()
    linux_proof = linux_dir+'/proof.drat'
    command = ext4.command(300, [helper.linux(helper.NATIVE), '--no-binary', '-c', '1000000', helper.linux(CNF), linux_proof])
    helper.save(folder/'launch.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'command': command,
                                     'cnf_sha256': CNF_SHA, 'model_sha256': MODEL_SHA, 'ext4_proof': linux_proof})
    print(json.dumps({'state': 'VARIABLE_CORE_FACTOR_NATIVE_LAUNCHING', 'variables': 110904, 'clauses': 518160, 'native_seconds': 300}), flush=True)
    receipt = helper.run_record(command, folder/'solver', 320)
    result = {'actual_exit_code': receipt['actual_exit_code'], 'receipt': receipt, 'research_calls': 1,
              'status': 'ARBITRARY_CORE_FACTOR_ARTIFACTS_PENDING_INDEPENDENT_REVIEW', 'target_resolution': False,
              'scope': 'Arbitrary normalized necessary core/factor model; no complete target graph.', 'automatic_retry': False}
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(linux_proof, folder/'proof.drat', folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT, 'proof file cap')
        except BaseException as e:
            result['proof_copy_failure'] = {'type': type(e).__name__, 'message': str(e), 'linux_original_retained': linux_proof}
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout, 110904)
                helper.save(folder/'parsed_model.json', {'assignment': assignment})
                decoder.decode(argparse.Namespace(model=MODEL, assignment=folder/'parsed_model.json', out=folder/'decoded_factor.json'))
                result['producer_local_factor_check'] = helper.read(folder/'decoded_factor.json')['producer_exact_check']
            except BaseException as e:
                result['parse_decode_failure'] = {'type': type(e).__name__, 'message': str(e)}
    else:
        result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'PARTIAL_FACTOR_SAT_RAW_UNCHECKED' if code == 10 else 'NECESSARY_MODEL_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p): helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['SAT requires independent clause/object checking and provides no residualD or target graph.',
                             'UNSAT alone is unproved; target implications require complete independent proof replay and exact encoding/coverage gates.',
                             'This runner never approves or publishes a target-level resolution.']
    helper.save(out/'summary.json', result)
    print(json.dumps({'actual_exit_code': code, 'interpreted_result': result['interpreted_result'], 'research_calls': 1}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    modes = ap.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight', action='store_true')
    modes.add_argument('--research', action='store_true')
    for name in ('out', 'encoding-gate', 'object-gate'):
        ap.add_argument('--'+name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256'):
        ap.add_argument('--'+name, required=True)
    run(ap.parse_args())


if __name__ == '__main__':
    main()
