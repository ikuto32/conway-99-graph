"""Prepared single gated native pilot for a complete balanced Gram model."""
from datetime import datetime, timezone
from pathlib import Path
import argparse, json, platform, shutil, subprocess, sys
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_hadamard_balanced_gram_cnf as producer

ROOT = h.ROOT
B = ROOT/'acceleration/results'
DATA = B/'20260930_hadamard_balanced_gram_cnf'
CNF, MODEL, SCOPE = DATA/'instance.cnf', DATA/'model.json', DATA/'scope.json'
SPEC = Path(__file__).with_name('native_20260930_hadamard_balanced_gram_spec.md')
PRODUCER_SPEC = Path(producer.__file__).with_name('theory_20260930_hadamard_balanced_gram_cnf_spec.md')
PINS = {
    CNF: 'c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37',
    MODEL: '82717d648ad00255fe06c97f2c55ae25e6a3ba73e2e064287a15059c8be6cf98',
    SCOPE: '9cc4630a4d7f7b5a36da321465f58f86f1ed918a99e507b50f76f6e485eb334a',
    DATA/'summary.json': '686b73bb4678f1c2f92afcc0f93cd7e18f6d7d3fbe87e6bbafb5c4045aaf2497',
    producer.RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    Path(producer.__file__): 'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',
    PRODUCER_SPEC: '937e9ae29f4818822b0516cc61f35060cc8352b5cfca9abda2ba2648c53d6a6d',
    Path(h.__file__): 'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
    Path(e.__file__): 'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
    ROOT/'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    ROOT/'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    h.NATIVE: h.NATIVE_SHA, h.CHECKER: h.CHECKER_SHA,
}


def source_closure():
    paths = {Path(__file__).resolve(), SPEC.resolve(), PRODUCER_SPEC.resolve(), (ROOT/'uv.lock').resolve(), (ROOT/'pyproject.toml').resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix == '.py':
                paths.add(path)
    return paths


def preflight(args):
    bindings = {}
    for path, digest in PINS.items():
        h.require(h.digest(path) == digest, 'frozen source/input/tool '+h.key(path))
        bindings[h.key(path)] = digest
    reports = []
    for path, digest, status in [
        (args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_HADAMARD_BALANCED_GRAM_ENCODING_PASS'),
        (args.object_gate, args.object_gate_sha256, 'INDEPENDENT_HADAMARD_BALANCED_GRAM_OBJECT_CALIBRATION_PASS')]:
        report = h.checked_gate(path, digest, status)
        reports.append(report)
        for name, value in report['inputs_sha256'].items():
            h.require(h.digest(ROOT/name) == value, 'unchanged gate input '+name)
            bindings[name] = value
        for raw in [CNF, MODEL, SCOPE, producer.RAW, Path(producer.__file__), PRODUCER_SPEC]:
            h.require(report['inputs_sha256'][h.key(raw)] == PINS[raw], 'direct exact model binding')
        bindings[h.key(path)] = digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds same encoding review')
    for path in source_closure():
        digest = h.digest(path)
        h.require(reports[1]['inputs_sha256'][h.key(path)] == digest, 'object gate binds full native closure '+h.key(path))
        bindings[h.key(path)] = digest
    for name, digest, status in [
        ('20260930_native_cli_calibration', 'f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb', 'INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('20260930_native_proof_location', 'd1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619', 'NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        path = B/name/'summary.json'
        h.checked_gate(path, digest, status)
        bindings[h.key(path)] = digest
    with CNF.open('rb') as stream:
        h.require(stream.readline() == b'p cnf 10480 74200\n', 'exact native formula dimensions')
    scope = h.read(SCOPE)
    h.require(scope['balance_is_additional_assumption'] and scope['prescribed_Gram_encoded'] and not scope['outside_column_caps_encoded'] and not scope['residual_D_encoded'] and not scope['target_graph'], 'exact restricted Gram scope and omissions')
    return bindings


def literal_factor_check(decoded):
    scope = h.read(SCOPE)
    F, C = decoded['factor'], scope['core_adjacency36']
    h.require(len(F) == 36 and all(len(row) == 60 and all(type(x) is int and x in (0, 1) for x in row) for row in F), 'literal36x60 binary matrix')
    gram = [[sum(F[a][d]*F[b][d] for d in range(60)) for b in range(36)] for a in range(36)]
    h.require(gram == scope['prescribed_Gram36'], 'all1296 literal Gram entries')
    h.require(all(sum(row) == 10 for row in F), 'all36 row margins')
    h.require(all(sum(F[12*g+a][d] for a in range(12)) == 2 for g in range(3) for d in range(60)), 'all180 fibre margins')
    L = [[sum(F[12*g+a][d] for g in range(3)) for d in range(60)] for a in range(12)]
    h.require(L == scope['L12x60'], 'all720 prescribed coordinate-support entries')
    caps = [dict(columns=[d, f], overlap=sum(F[a][d]*F[a][f] for a in range(36))) for d in range(60) for f in range(d+1, 60)]
    mixed = [[F[a][d]+sum(C[a][b]*F[b][d] for b in range(36)) for d in range(60)] for a in range(36)]
    violations = [item for item in caps if item['overlap'] > 2]
    mixed_violations = [dict(row=a, column=d, value=mixed[a][d]) for a in range(36) for d in range(60) if mixed[a][d] > 2]
    h.require(caps == decoded['checks']['column_pair_records'] and violations == decoded['checks']['column_cap_violations'] and mixed_violations == decoded['checks']['mixed_cap_violations'], 'literal diagnostics agree with candidate decoder')
    return dict(status='PRODUCER_LITERAL_GRAM_FACTOR_CHECK', integer_Gram_entries_checked=1296, column_pairs_checked=1770,
        mixed_entries_checked=2160, column_pair_records=caps, column_cap_violations=violations, mixed_cap_violations=mixed_violations,
        Gram_factor=True, column_caps_pass=not violations, mixed_caps_pass=not mixed_violations,
        independent_approval=False, target_graph=False, residual_D=None,
        scope='Complete raw incidence Gram factor only. Cap failures are preserved diagnostics because caps were omitted from the input CNF.')


def run(args):
    bindings = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free
    h.require(host_free >= 21*1024**3, 'host21GiB disk reserve')
    mount, mounttext = e.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out/'filesystem')
    h.require('ext4' in mounttext.split(), 'calibrated ext4 proof mount')
    disk, disktext = e.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out/'disk_free')
    h.require(int(disktext.splitlines()[-1]) >= 11*1024**3, 'ext4 11GiB reserve')
    h.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH', selection_rule='First native result for exact unmodified complete balanced Gram CNF; native default seed.',
        limits=dict(native_wall_seconds=60, conflicts=1000000, address_space_bytes=e.AS_LIMIT, trace_file_bytes=e.FILE_LIMIT,
            kill_after_seconds=5, outer_guard_seconds=70, maximum_research_calls=1, automatic_retry=False),
        cpu_limit=None, cpu_limit_null_reason='Calibrated wall guard; no separate CPU rlimit.', random_seed=None, random_seed_null_reason='Native default retained.',
        scope='Complete balanced incidence Gram on one fixed support; outside caps omitted and reported only as exact diagnostics. No residualD/full99 graph.',
        filesystem_receipt=mount, ext4_disk_receipt=disk, host_free_bytes=host_free,
        shared_components=['Frozen authenticated native/parser/ext4 helpers.', 'Frozen candidate producer decoder; separate literal checks remain producer safeguards, not independent approval.']))
    if args.preflight:
        h.save(out/'summary.json', dict(status='BALANCED_GRAM_NATIVE_PREFLIGHT_PASS', research_calls=0, inputs_sha256=bindings))
        return
    observed, _ = e.local_capture(['/usr/bin/ps', '-eo', 'pid,ppid,comm,pcpu,rss,args'], out/'processes_before')
    made, directory = e.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-balanced-gram-XXXXXX'], out/'mktemp')
    h.require(directory.startswith('/tmp/conway99-balanced-gram-') and '\n' not in directory, 'fresh ext4 workspace')
    h.save(out/'workspace.json', dict(path=directory, preserved=True, receipt=made, process_observation=observed))
    # Recheck both reserves immediately before the only research call.
    disk, disktext = e.local_capture(['/usr/bin/df', '--output=avail', '-B1', directory], out/'disk_before_launch')
    h.require(shutil.disk_usage(ROOT).free >= 21*1024**3 and int(disktext.splitlines()[-1]) >= 11*1024**3, 'immediate host/ext4 launch reserves')
    folder = out/'main'
    folder.mkdir()
    proof = directory+'/proof.drat'
    command = e.command(60, [h.linux(h.NATIVE), '--no-binary', '-c', '1000000', h.linux(CNF), proof])
    h.save(folder/'launch.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command=command, cnf_sha256=PINS[CNF], ext4_proof=proof))
    print(json.dumps(dict(state='BALANCED_GRAM_NATIVE_LAUNCH', wall_seconds=60, variables=10480, clauses=74200)), flush=True)
    native = h.run_record(command, folder/'solver', 70)
    result = dict(status='BALANCED_GRAM_NATIVE_PENDING_INDEPENDENT_REVIEW', timestamp=datetime.now(timezone.utc).isoformat(),
        receipt=native, research_calls=1, target_resolution=False, automatic_retry=False,
        linux_process_state='UNKNOWN_AFTER_OUTER_GUARD' if native['outer_windows_guard_expired'] else 'WRAPPED_COMMAND_RETURNED')
    if not native['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = e.proof_copy(proof, folder/'proof.drat', folder/'transfer')
            h.require((folder/'proof.drat').stat().st_size <= e.FILE_LIMIT, 'trace file cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(error=repr(error), linux_original_path=proof, sha256=None,
                sha256_null_reason='Full transfer identity unavailable; inspect preserved transfer receipts and ext4 artifact.', artifact_availability='UNKNOWN_PENDING_OBSERVATION')
        if native['actual_exit_code'] == 10:
            try:
                stdout = (folder/'solver.stdout.log').read_text(encoding='utf-8')
                assignment = h.parse_sat_stdout(stdout, 10480)
                h.save(folder/'parsed_model.json', dict(assignment=assignment))
                decoded = producer.decode(assignment, MODEL, SCOPE, CNF)
                h.save(folder/'decoded_Gram_factor.json', decoded)
                checks = literal_factor_check(decoded)
                h.save(folder/'literal_factor_check.json', checks)
                result['raw_Gram_factor_saved'] = True
                result['raw_factor_column_caps_pass'] = checks['column_caps_pass']
                result['raw_factor_mixed_caps_pass'] = checks['mixed_caps_pass']
            except BaseException as error:
                result['parse_decode_failure'] = dict(error=repr(error))
        try:
            observation, _ = e.local_capture(['/usr/bin/ps', '-eo', 'pid,ppid,comm,pcpu,rss,args'], out/'processes_after')
            result['fresh_process_observation'] = observation
        except BaseException as error:
            result['process_observation_failure'] = repr(error)
    code = native['actual_exit_code']
    result['interpreted_result'] = 'BALANCED_GRAM_SAT_RAW_UNCHECKED' if code == 10 else 'BALANCED_GRAM_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {h.key(path): h.digest(path) for path in folder.iterdir() if path.is_file()}
    result['limitations'] = [
        'SAT requires the separate complete-assignment/actual-clause/raw-factor checker; producer safeguards are not independent approval.',
        'Outside-column caps were omitted; diagnostic failures preserve a weaker Gram factor. No residualD/full99 graph follows even if caps pass.',
        'UNSAT requires complete independent proof replay and the exact balanced fixed-support equivalence; no unrestricted nonexistence follows.',
        'UNKNOWN excludes nothing. Full trace hashing/copy time is separately recorded outside the native wall allocation.']
    h.save(out/'summary.json', result)
    print(json.dumps(dict(result=result['interpreted_result'], code=code)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight', action='store_true')
    mode.add_argument('--research', action='store_true')
    for name in ('out', 'encoding-gate', 'object-gate'):
        parser.add_argument('--'+name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'object-gate-sha256'):
        parser.add_argument('--'+name, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
