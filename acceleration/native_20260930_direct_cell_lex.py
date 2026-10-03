"""Prepared single native call for either frozen equal-support lex formula."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time

import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_direct_cell_lex as producer

ROOT = h.ROOT
B = ROOT / 'acceleration/results'
DATA = B / '20260930_direct_cell_lex'
BASE_DATA = B / '20260930_direct_cell_count_cnf'
SPEC = Path(__file__).with_name('native_20260930_direct_cell_lex_spec.md')
PRODUCER_SPEC = ROOT / 'acceleration/theory_20260930_direct_cell_lex_spec.md'
ORIGINAL_PRODUCER = ROOT / 'acceleration/theory_20260930_direct_cell_count_cnf.py'
ORIGINAL_SPEC = ORIGINAL_PRODUCER.with_name(ORIGINAL_PRODUCER.stem + '_spec.md')
DYNAMIC_HELPER = ROOT / 'acceleration/theory_20260930_direct_cell_count_preflight.py'
DYNAMIC_SPEC = DYNAMIC_HELPER.with_name(DYNAMIC_HELPER.stem + '_spec.md')
ENCODING_STATUS = 'INDEPENDENT_DIRECT_CELL_LEX_ENCODING_PASS'
OBJECT_STATUS = 'INDEPENDENT_DIRECT_CELL_LEX_OBJECT_CALIBRATION_PASS'
LIMITS = dict(native_wall_seconds=60, conflicts=1000000,
              address_space_bytes=4294967296, trace_file_bytes=10737418240,
              kill_grace_seconds=5, outer_guard_seconds=70,
              maximum_research_calls=1, automatic_retry=False,
              host_reserve_bytes=21 * 1024**3, ext4_reserve_bytes=11 * 1024**3)
BASE_VARIANTS = {'standalone': {'variables': 23112,
                'clauses': 320484,
                'cnf': '45bac5dddcc805010dd4da150cc1c4613855b5d0e1e436f7b584067875c85250',
                'model': 'c74a90c4e81218d98623fa7fa683a5680c67e3b82f2e33fefc453c705c411b87',
                'scope': 'aa7f0e9ce4cd1679a1acc0aff0a8a76bbf60d2834013e419289be82ce8331e1e'},
 'at_least_seven': {'variables': 169151,
                    'clauses': 968960,
                    'cnf': '07323c9fbbd75e328dfa0d1a99c760823799ecf7bba74722e2720d7dbb97c959',
                    'model': 'ea45aa8045ac7193e9492daae383d599cccdfcf0741d3a9357984dcadd5e0cbb',
                    'scope': '8455669b3eec2edecd3e37bf7accebca75d8a65798b08a35f07fabb24edd96bf'}}
VARIANTS = {'standalone': {'variables': 23272,
                'clauses': 321684,
                'cnf': 'c1bb9e7a14008b40ce4e93eee3b222bd78599d450fc25ab1852b80bb1b825bfa',
                'model': 'e40cbc3d7497339b9c063e0566909e3b7702d41b4201584756b71c2b210d14b6',
                'scope': '026c040815d590bbdc37adedfa3a4e2808aeab09ecd01972b0a888f7c57b1724',
                'extension': '6625dc495fc1bca9c09acebdc8af51b3be5a30309d6a8d030b98581c6eaf6270'},
 'at_least_seven': {'variables': 169311,
                    'clauses': 970160,
                    'cnf': 'b536d8461be954bb76a4f25087fa450527edc90904f4c26c3bfe8dbcc4f79649',
                    'model': '973f86db6f026c8db9d81ef74f59d94679c4523cfadbee732fd8d0b38a3af51b',
                    'scope': '43a35fe406cf6951d9af7f937a94261cd08171d037681fef70195aa75aa65e43',
                    'extension': 'ce8ed4bf3d76375928c314d8f8e0fa3ad46c6dabdd54ccf3ceed04da116acaf4'}}
PINS = {
    DATA / 'summary.json': '2077b3a005191d9c3a777c0e16b79e273f18b0aab60737dd880e199a833a1f22',
    Path(producer.__file__): '56ee886ade80403743fd260d8b2ef9c227d9d1e2741c3edbb09b509fac9ade57',
    ORIGINAL_PRODUCER: 'ea7a07b7adcea4d5faebd174d3b3755ae8ed7e05d2fa844f135db39c7e075fc3',
    ORIGINAL_SPEC: '294a25a5734d7283761fba9b10d65c9533c49417b1c12e77486f6d2559787c2a',
    PRODUCER_SPEC: '1fe7cb6e2517e274c90ff9d4a64ed751be6340ae49da41ed9215762573c6cc1b',
    DYNAMIC_HELPER: '902bafedf5099fc27727caf17819e50080e514ed9e0b6788fdd5345fb3d5ffdd',
    DYNAMIC_SPEC: 'b95c02a2ed80fee55260a57dfce0a05e1b26f84bd48aaae4f770da4c28b05368',
    Path(h.__file__): 'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
    Path(e.__file__): 'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
    h.NATIVE: h.NATIVE_SHA, h.CHECKER: h.CHECKER_SHA,
    ROOT / 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    ROOT / 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}


def source_closure():
    # The lex decoder and original builder have explicit importlib dependencies.
    paths = {Path(__file__).resolve(), SPEC.resolve(), PRODUCER_SPEC.resolve(),
             DYNAMIC_HELPER.resolve(), DYNAMIC_SPEC.resolve(),
             ORIGINAL_PRODUCER.resolve(), ORIGINAL_SPEC.resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT / 'acceleration') and path.suffix == '.py':
                paths.add(path)
                spec = path.with_name(path.stem + '_spec.md')
                if spec.exists():
                    paths.add(spec)
    return paths


def preflight(args):
    config = VARIANTS[args.variant]
    folder = DATA / args.variant
    cnf, model_path, scope_path = [folder / name for name in ('instance.cnf', 'model.json', 'scope.json')]
    pins = dict(PINS)
    extension_path = folder / 'extension.json'
    pins.update({cnf: config['cnf'], model_path: config['model'], scope_path: config['scope'], extension_path: config['extension']})
    bindings = {}
    for path, digest in pins.items():
        h.require(h.digest(path) == digest, 'frozen input/source/tool ' + h.key(path))
        bindings[h.key(path)] = digest
    summary = h.read(DATA / 'summary.json')
    h.require(summary['status'] == 'CANDIDATE_DIRECT_CELL_LEX_FORMULAS_BUILT', 'complete frozen build')
    for name, digest in {**summary['inputs_sha256'], **summary['outputs_sha256']}.items():
        h.require(h.digest(ROOT / name) == digest, 'producer artifact ' + name)
        bindings[name] = digest
    model, scope = h.read(model_path), h.read(scope_path)
    n, m = config['variables'], config['clauses']
    h.require(model['schema'] == 'DIRECT_CELL_EQUAL_SUPPORT_LEX_REFERENCE_MODEL_V1', 'model schema')
    h.require(scope['schema'] == 'FIXED_LITERAL_DIRECT_CELL_EQUAL_SUPPORT_LEX_SCOPE_V1', 'scope schema')
    h.require(model['variant'] == scope['variant'] == args.variant, 'same literal variant')
    h.require((model['variables'], model['clauses']) == (n, m), 'exact formula dimensions')
    h.require(model['cnf_path'] == h.key(cnf) and model['cnf_sha256'] == config['cnf'], 'model/CNF identity')
    h.require(model['scope_path'] == h.key(scope_path) and model['scope_sha256'] == config['scope'], 'model/scope identity')
    h.require(all(scope[k] for k in ('full_Gram_encoded', 'within_group_caps_encoded', 'cross_group_caps_encoded')), 'full Gram/all caps')
    h.require(not any(scope[k] for k in ('residual_D_encoded', 'target_automorphism_assumed', 'target_graph')), 'scope exclusions')
    h.require(scope['normalization_group'] == 'S3^20 acting within the fixed equal-support triples only' and scope['column_normalization'] is not None and scope['auxiliary_permutation_claimed'] is False, 'equal-support column normalization only')
    h.require(model['extension_path'] == h.key(extension_path) and model['extension_sha256'] == config['extension'], 'literal extension reference')
    extension = h.read(extension_path)
    h.require(extension['schema'] == 'DIRECT_CELL_EQUAL_SUPPORT_LEX_EXTENSION_V1' and extension['variant'] == args.variant, 'extension schema and variant')
    h.require(extension['new_variables'] == 160 and extension['new_clauses'] == 1200 and len(extension['comparators']) == 40, 'exact lex suffix dimensions')
    base = model['base']
    h.require(extension['base'] == base, 'same base model reference')
    h.require(base['variables'] + 160 == n and base['clauses'] + 1200 == m and base['variant'] == args.variant, 'same base dimensions')
    base_paths = []
    for kind, filename in (('cnf', 'instance.cnf'), ('model', 'model.json'), ('scope', 'scope.json')):
        path = BASE_DATA / args.variant / filename
        digest = BASE_VARIANTS[args.variant][kind]
        h.require(base[kind + '_path'] == h.key(path) and base[kind + '_sha256'] == digest and h.digest(path) == digest, 'exact original ' + kind)
        bindings[h.key(path)] = digest
        base_paths.append(path)
    h.require(scope['base_scope_path'] == base['scope_path'] and scope['base_scope_sha256'] == base['scope_sha256'], 'original scope reference')
    counted = args.variant == 'at_least_seven'
    h.require(scope['count_master_included'] == counted and scope['minimum_exception_count'] == (7 if counted else None), 'exact count scope')
    h.require(e.AS_LIMIT == LIMITS['address_space_bytes'] and e.FILE_LIMIT == LIMITS['trace_file_bytes'], 'helper limits')
    with cnf.open('rb') as stream:
        h.require(stream.readline() == f'p cnf {n} {m}\n'.encode(), 'exact DIMACS header')
    reports = []
    direct = [cnf, model_path, scope_path, extension_path, DATA / 'summary.json', Path(producer.__file__), PRODUCER_SPEC, *base_paths]
    for path, digest, status in ((args.encoding_gate, args.encoding_gate_sha256, ENCODING_STATUS),
                                 (args.object_gate, args.object_gate_sha256, OBJECT_STATUS)):
        report = h.checked_gate(path, digest, status)
        reports.append(report)
        for name, value in report['inputs_sha256'].items():
            h.require(h.digest(ROOT / name) == value, 'unchanged independent input ' + name)
            bindings[name] = value
        for raw in direct:
            h.require(report['inputs_sha256'][h.key(raw)] == h.digest(raw), 'direct formula binding ' + h.key(raw))
        bindings[h.key(path)] = digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)] == args.encoding_gate_sha256, 'same encoding gate')
    for path in source_closure() | {args.object_checker.resolve(), h.NATIVE, h.CHECKER}:
        digest = h.digest(path)
        h.require(reports[1]['inputs_sha256'][h.key(path)] == digest, 'object/runtime closure ' + h.key(path))
        bindings[h.key(path)] = digest
    for name, digest, status in (
        ('20260930_native_cli_calibration', 'f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb', 'INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('20260930_native_proof_location', 'd1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619', 'NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')):
        path = B / name / 'summary.json'
        h.checked_gate(path, digest, status)
        bindings[h.key(path)] = digest
    return bindings, cnf, model_path, scope_path, n, m


def observe(prefix):
    receipt = h.run_record([*h.WSL, '/usr/bin/ps', '-C', 'cadical', '-o', 'pid,ppid,comm,pcpu,rss,args'], prefix, 10)
    h.require(not receipt['outer_windows_guard_expired'] and receipt['actual_exit_code'] in (0, 1), 'targeted native observation')
    if receipt['actual_exit_code'] == 1:
        h.require(len(Path(str(prefix) + '.stdout.log').read_text().strip().splitlines()) <= 1, 'no exact-named process')
    return receipt


def run(args):
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        bindings, cnf, model_path, scope_path, n, m = preflight(args)
        mount, text = e.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out / 'filesystem')
        h.require('ext4' in text.split(), 'ext4 proof mount')
        disk, text = e.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out / 'disk_free')
        host, ext4 = shutil.disk_usage(ROOT).free, int(text.splitlines()[-1])
        h.require(host >= LIMITS['host_reserve_bytes'] and ext4 >= LIMITS['ext4_reserve_bytes'], 'host/ext4 reserves')
        h.save(out / 'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            variant=args.variant, inputs_sha256=bindings, limits=LIMITS,
            mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH', host_free_bytes=host, ext4_free_bytes=ext4,
            mount_receipt=mount, disk_receipt=disk, scope='Literal fixed-support full-Gram/all-caps factor with equal-support column lex normalization; no residual D or target graph.',
            random_seed=None, random_seed_null_reason='Native default retained.', cpu_limit=None,
            cpu_limit_null_reason='Wall guard; no additional CPU rlimit.',
            shared_components=['Authenticated parser/native/ext4 engineering helpers.', 'Lex producer decoder dynamically loads the original frozen raw-factor decoder; its result remains candidate.', 'Original decoder/spec and dynamic production preflight helper/spec explicitly pinned; no helper build called.']))
        if args.preflight:
            h.save(out / 'summary.json', dict(status='DIRECT_CELL_LEX_NATIVE_PREFLIGHT_PASS', variant=args.variant, research_calls=0, inputs_sha256=bindings))
            return
        before = observe(out / 'processes_before')
        made, directory = e.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-direct-cell-lex-XXXXXX'], out / 'mktemp')
        h.require(directory.startswith('/tmp/conway99-direct-cell-lex-') and '\n' not in directory, 'fresh ext4 directory')
        h.save(out / 'workspace.json', dict(path=directory, creation_observed=True, receipt=made,
            retention_intent='This driver does not delete the ext4 workspace.',
            future_availability='UNKNOWN',
            limitation='Creation and immediate transfer observations do not guarantee permanent ext4 retention.'))
        folder = out / 'main'
        folder.mkdir()
        proof = directory + '/proof.drat'
        _, text = e.local_capture(['/usr/bin/df', '--output=avail', '-B1', directory], out / 'disk_before_launch')
        h.require(shutil.disk_usage(ROOT).free >= LIMITS['host_reserve_bytes'] and int(text.splitlines()[-1]) >= LIMITS['ext4_reserve_bytes'], 'immediate launch reserves')
        command = e.command(60, [h.linux(h.NATIVE), '--no-binary', '-c', '1000000', h.linux(cnf), proof])
        h.save(folder / 'launch.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command=command, variant=args.variant, cnf_sha256=h.digest(cnf), ext4_proof=proof))
        print(json.dumps(dict(state='DIRECT_CELL_LEX_NATIVE_LAUNCH', variant=args.variant, variables=n, clauses=m, wall_seconds=60)), flush=True)
        native = h.run_record(command, folder / 'solver', 70)
        result = dict(status='DIRECT_CELL_LEX_NATIVE_PENDING_INDEPENDENT_REVIEW', variant=args.variant,
            inputs_sha256=bindings, receipt=native, processes_before=before, research_calls=1,
            automatic_retry=False, target_resolution=False, independent_approval=False)
        if not native['outer_windows_guard_expired']:
            transfer_start = time.monotonic()
            try:
                result['proof_copy'] = e.proof_copy(proof, folder / 'proof.drat', folder / 'transfer')
                h.require(result['proof_copy']['bytes'] <= LIMITS['trace_file_bytes'], 'trace cap')
            except BaseException as error:
                result['proof_copy_failure'] = dict(error=repr(error), linux_original_path=proof, sha256=None, reason='Complete identity unavailable; retain raw original and receipts.')
            result['proof_transfer_and_hash_wall_seconds'] = time.monotonic() - transfer_start
            if native['actual_exit_code'] == 10:
                try:
                    assignment = h.parse_sat_stdout((folder / 'solver.stdout.log').read_text(), n)
                    h.save(folder / 'parsed_model.json', dict(assignment=assignment))
                except BaseException as error:
                    result['parse_failure'] = repr(error)
                if (folder / 'parsed_model.json').exists():
                    try:
                        decoded = producer.decode(assignment, model_path, scope_path, cnf)
                        h.save(folder / 'decoded_factor.json', decoded)
                    except BaseException as error:
                        result['producer_decode_failure'] = repr(error)
                    try:
                        cmd = [sys.executable, '-B', str(args.object_checker), 'sat', '--variant', args.variant,
                            '--encoding-gate', str(args.encoding_gate), '--encoding-gate-sha256', args.encoding_gate_sha256,
                            '--assignment', str(folder / 'parsed_model.json'), '--native-output', str(folder / 'solver.stdout.log'),
                            '--out', str(out / 'independent_object')]
                        if (folder / 'decoded_factor.json').exists():
                            cmd += ['--decoded', str(folder / 'decoded_factor.json')]
                        result['independent_object_receipt'] = h.run_record(cmd, out / 'independent_object_command', 240)
                    except BaseException as error:
                        result['independent_object_failure'] = repr(error)
                result['stop_reason'] = 'SAT_FACTOR_PENDING_INDEPENDENT_REVIEW_NO_RESIDUAL_D'
            try:
                result['fresh_process_observation'] = observe(out / 'processes_after')
            except BaseException as error:
                result['process_observation_failure'] = repr(error)
        code = native['actual_exit_code']
        result['interpreted_result'] = 'SAT_RAW_UNCHECKED' if code == 10 else 'UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
        result['end_to_end_wall_seconds'] = time.monotonic() - started
        result['outputs_sha256'] = {h.key(path): h.digest(path) for path in out.rglob('*') if path.is_file()}
        result['limitations'] = ['SAT requires separate complete native/assignment/clause/raw-factor checking.',
            'No residual D, 99-vertex target construction, or unrestricted support coverage.',
            'UNSAT requires complete proof replay and exact variant scope; UNKNOWN excludes nothing.',
            'Decoder and execution receipt do not independently approve the result.',
            'Ext4 creation and immediate transfer are observations; future ext4 availability remains UNKNOWN.']
        h.save(out / 'summary.json', result)
        print(json.dumps(dict(result=result['interpreted_result'], variant=args.variant, code=code)))
    except BaseException as error:
        h.save(out / 'failure.json', dict(error=repr(error), source_sha256=h.digest(Path(__file__))))
        raise


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight', action='store_true')
    mode.add_argument('--research', action='store_true')
    parser.add_argument('--variant', choices=tuple(VARIANTS), required=True)
    for name in ('out', 'encoding-gate', 'object-gate', 'object-checker'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256'):
        parser.add_argument('--' + name, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
