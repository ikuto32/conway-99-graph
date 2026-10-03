"""Gated finite parity sampling and candidate GF(3) screening.

Creation of this source launches nothing. Research is an explicit separate mode.
Every mathematical screen remains CANDIDATE until a separate case audit.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4
import audit_20260930_hadamard_parity_support_cuts as objects
import theory_20260930_hadamard_general_f3_system as phases

ROOT = helper.ROOT
B = ROOT/'acceleration/results'
BASE = B/'20260930_hadamard_parity_support_cuts/instance.cnf'
MODEL = BASE.with_name('model.json')
INITIAL = B/'20260930_independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'
INITIAL_GATE = INITIAL.with_name('summary.json')
INITIAL_F3 = B/'20260930_independent_review/hadamard_f3_phase_obstruction/summary.json'
GENERAL = B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json'
SPEC = Path(__file__).with_name('theory_20260930_hadamard_parity_phase_batch_spec.md')
PINS = {
    BASE: 'db9816ddf037250efc04b1e093e407eac0ec2c4fadf2f24b5774fb3249eba07f',
    MODEL: 'c477693bbf634609c234bf5b791c499f8f9ded091795b01bec297746288b4f4f',
    objects.RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    INITIAL: 'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
    INITIAL_GATE: '02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
    INITIAL_F3: '0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
    GENERAL: '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
    Path(helper.__file__): 'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
    Path(ext4.__file__): 'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
    Path(phases.linear.__file__): '154d145af9f23a3b150ec8c798598d63779fab28a1474468b622a718fc82beaa',
    helper.NATIVE: helper.NATIVE_SHA,
    helper.CHECKER: helper.CHECKER_SHA,
}
MAX_CASES, WALL, CONFLICTS, TOTAL = 16, 10, 20000, 180
OUTER, LAUNCH_RESERVE = 18, 25


def now():
    return datetime.now(timezone.utc).isoformat()


def source_closure():
    # Every imported repository module is pinned, including transitive imports.
    paths = {Path(__file__).resolve(), SPEC.resolve(), (ROOT/'uv.lock').resolve(), (ROOT/'pyproject.toml').resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix == '.py':
                paths.add(path)
    return paths


def preflight(args):
    inputs = {}
    for path, digest in PINS.items():
        helper.require(helper.digest(path) == digest, 'frozen identity '+helper.key(path))
        inputs[helper.key(path)] = digest
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS')
    gen = helper.checked_gate(args.general_necessity_gate, args.general_necessity_gate_sha256, 'INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OBJECT_CALIBRATION_PASS')
    helper.require(args.general_necessity_gate.resolve() == GENERAL.resolve() and args.general_necessity_gate_sha256 == PINS[GENERAL], 'frozen general necessity review')
    for gate in (enc, gen, obj):
        for name, digest in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT/name) == digest, 'gate input remains unchanged '+name)
            inputs[name] = digest
    for path in (BASE, MODEL):
        helper.require(enc['inputs_sha256'][helper.key(path)] == PINS[path], 'encoding binds exact base')
        helper.require(obj['inputs_sha256'][helper.key(path)] == PINS[path], 'batch calibration binds exact base')
    for path, digest in [(args.encoding_gate, args.encoding_gate_sha256), (args.general_necessity_gate, args.general_necessity_gate_sha256)]:
        helper.require(obj['inputs_sha256'][helper.key(path)] == digest, 'batch calibration binds same semantic gates')
    for path in source_closure():
        digest = helper.digest(path)
        helper.require(obj['inputs_sha256'][helper.key(path)] == digest, 'batch calibration binds every loaded repository source/environment '+helper.key(path))
        inputs[helper.key(path)] = digest
    for name, digest, status in [
        ('20260930_native_cli_calibration/summary.json', 'f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb', 'INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('20260930_native_proof_location/summary.json', 'd1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619', 'NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        helper.checked_gate(B/name, digest, status)
        inputs[helper.key(B/name)] = digest
    for path in (args.encoding_gate, args.general_necessity_gate, args.object_gate):
        inputs[helper.key(path)] = helper.digest(path)
    clauses, groups, pairs, _ = objects.reconstruct(helper.read(MODEL), helper.read(objects.OLD_MODEL), helper.read(objects.RAW))
    helper.require(objects.base.cnf_bytes(clauses) == BASE.read_bytes(), 'complete independent base reconstruction')
    initial_gate = helper.read(INITIAL_GATE)
    helper.require(initial_gate['status'] == 'INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS' and initial_gate['outputs_sha256'][helper.key(INITIAL)] == PINS[INITIAL], 'initial projection raw binding')
    return inputs, clauses, groups, pairs


def block_record(path, initial=False):
    projection = helper.read(path)
    selected = projection['selected_group_selector_ids']
    helper.require(len(selected) == 20 and all(type(v) is int and 11*g+1 <= v <= 11*g+11 for g, v in enumerate(selected)), 'one selected selector per ordered group')
    return dict(projection_path=helper.key(path), projection_sha256=helper.digest(path), selected_group_selector_ids=selected,
        purpose='DISTINCT_CANDIDATE_SAMPLING', mathematical_exclusion_approved=initial,
        independent_exclusion_gate=helper.key(INITIAL_F3) if initial else None,
        independent_exclusion_gate_sha256=PINS[INITIAL_F3] if initial else None,
        exclusion_null_reason=None if initial else 'New producer screen awaits a separate independent case review; sampling needs no exclusion claim.')


def write_case_cnf(path, clauses, blocked):
    seen = set()
    extra = []
    for record in blocked:
        source = ROOT/record['projection_path']
        helper.require(helper.digest(source) == record['projection_sha256'], 'unaltered prior projection')
        helper.require(helper.read(source)['selected_group_selector_ids'] == record['selected_group_selector_ids'], 'full block raw selector identity')
        selected = tuple(record['selected_group_selector_ids'])
        helper.require(selected not in seen, 'distinct prior complete projections')
        seen.add(selected)
        extra.append([-value for value in selected])
    complete = clauses+extra
    with path.open('xb') as stream:
        stream.write(objects.base.cnf_bytes(complete))
    return complete


def bounded_trace_identity(linux_path, folder, deadline):
    result = dict(linux_path=linux_path, artifact_availability='LOCAL_ONLY', preserved=True,
                  sha256=None, sha256_null_reason='No completed bounded hash yet.', bytes=None,
                  bytes_null_reason='No completed bounded stat yet.',
                  windows_copy=None, windows_copy_null_reason='Explicit post-batch archive collection is separate from the 180-second research budget.')
    for label, command in [('stat', ['/usr/bin/stat', '--format=%s', linux_path]), ('hash', ['/usr/bin/sha256sum', linux_path])]:
        remaining = deadline-time.monotonic()
        if remaining < 2:
            result[label+'_unavailable_reason'] = 'Batch deadline reserve; artifact remains on ext4.'
            continue
        receipt = helper.run_record(ext4.command(min(3, remaining-1), command), folder/('proof_'+label), min(4, remaining))
        result[label+'_receipt'] = receipt
        if receipt['actual_exit_code'] == 0:
            text = (folder/('proof_'+label+'.stdout.log')).read_text().strip()
            if label == 'stat':
                result['bytes'] = int(text)
                result['bytes_null_reason'] = None
                helper.require(result['bytes'] <= ext4.FILE_LIMIT, 'proof size cap')
            else:
                digest = text.split()[0]
                helper.require(len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'raw proof hash syntax')
                result['sha256'] = digest
                result['sha256_null_reason'] = None
        else:
            result[label+'_unavailable_reason'] = 'Bounded post-run metadata command failed or timed out; no fabricated identity.'
    return result


def run(args):
    inputs, clauses, groups, pairs = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    helper.require(shutil.disk_usage(ROOT).free >= 21*1024**3, 'host reserve21GiB')
    filesystem, text = ext4.local_capture(['/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], out/'filesystem')
    helper.require('ext4' in text.split(), 'calibrated ext4 mount')
    disk, text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', '/tmp'], out/'disk_free')
    helper.require(int(text.splitlines()[-1]) >= 11*1024**3, 'ext4 reserve11GiB')
    helper.save(out/'manifest.json', dict(schema='HADAMARD_PARITY_PHASE_BATCH_PROTOCOL_V1', timestamp=now(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs,
        mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH', filesystem_receipt=filesystem, disk_receipt=disk,
        limits=dict(maximum_fresh_SAT_cases=MAX_CASES, native_wall_seconds=WALL, native_conflicts=CONFLICTS,
                    address_space_bytes=ext4.AS_LIMIT, trace_file_bytes=ext4.FILE_LIMIT, kill_after_seconds=5,
                    outer_windows_guard_seconds=OUTER, research_budget_seconds=TOTAL, launch_reserve_seconds=LAUNCH_RESERVE,
                    automatic_retry=False, random_seed=None, random_seed_null_reason='Native default retained.'),
        scope='Sampling necessary balanced parity projections on one fixed Hadamard support; candidate linear obstructions per sampled branch only. Full20 selector sampling blocks are not all entailed exclusions.',
        shared_components=['Frozen native/ext4 helpers; frozen independently authored projection checker is repeated during production.',
                           'Frozen first-branch producer RREF is shared with this candidate general screen. Independent batch review must not import it.'],
        budget_boundary='Research clock starts immediately before fresh ext4 workspace creation after gated preflight/resource observations. Proof copying is never automatic; separate archival work is outside this clock. Budget deviations are recorded, never hidden.'))
    if args.preflight:
        helper.save(out/'summary.json', dict(status='HADAMARD_PARITY_PHASE_BATCH_PREFLIGHT_PASS', research_calls=0, inputs_sha256=inputs))
        return
    started = time.monotonic()
    deadline = started+TOTAL
    cases, blocked = [], [block_record(INITIAL, True)]
    launched = 0
    stop = 'MAXIMUM_FRESH_SAT_CASES'
    workspace = None
    try:
        receipt, workspace = ext4.local_capture(['/usr/bin/mktemp', '-d', '/tmp/conway99-parity-phase-batch-XXXXXX'], out/'mktemp', guard=5)
        helper.require(workspace.startswith('/tmp/conway99-parity-phase-batch-') and '\n' not in workspace, 'fresh ext4 workspace')
        helper.save(out/'workspace.json', dict(path=workspace, preserved=True, receipt=receipt))
        for index in range(MAX_CASES):
            if deadline-time.monotonic() < LAUNCH_RESERVE:
                stop = 'BATCH_TIME_RESERVE'
                break
            folder = out/f'case_{index:02d}'
            folder.mkdir()
            helper.save(folder/'blocked_projections.json', blocked)
            actual_clauses = write_case_cnf(folder/'instance.cnf', clauses, blocked)
            disk_receipt, free_text = ext4.local_capture(['/usr/bin/df', '--output=avail', '-B1', workspace], folder/'disk_free', guard=3)
            ext4_free, host_free = int(free_text.splitlines()[-1]), shutil.disk_usage(ROOT).free
            if ext4_free < 11*1024**3 or host_free < 21*1024**3:
                stop = 'RESOURCE_RESERVE_STOP_NO_RETRY'
                helper.save(folder/'resource_stop.json', dict(ext4_free_bytes=ext4_free, host_free_bytes=host_free,
                    native_call_launched=False, ext4_minimum_bytes=11*1024**3, host_minimum_bytes=21*1024**3))
                break
            if deadline-time.monotonic() < LAUNCH_RESERVE:
                stop = 'BATCH_TIME_RESERVE'
                helper.save(folder/'time_reserve_stop.json', dict(native_call_launched=False, remaining_seconds=deadline-time.monotonic()))
                break
            proof = workspace+f'/case_{index:02d}.drat'
            command = ext4.command(WALL, [helper.linux(helper.NATIVE), '--no-binary', '-c', str(CONFLICTS), helper.linux(folder/'instance.cnf'), proof])
            helper.save(folder/'launch.json', dict(timestamp=now(), command=command, variables=520, clauses=len(actual_clauses),
                cnf_sha256=helper.digest(folder/'instance.cnf'), ext4_proof=proof, remaining_batch_seconds=deadline-time.monotonic()))
            launched += 1
            native = helper.run_record(command, folder/'solver', OUTER)
            record = dict(index=index, receipt=native, independent_approval=False, status='CANDIDATE_EXECUTION_RECORD')
            cases.append(record)
            code = native['actual_exit_code']
            if native['outer_windows_guard_expired']:
                record['result'] = 'UNKNOWN_OUTER_GUARD'
                stop = 'UNKNOWN_OUTER_GUARD_PROCESS_STATE_UNKNOWN'
            elif code == 10:
                text = (folder/'solver.stdout.log').read_text()
                assignment = helper.parse_sat_stdout(text, 520)
                values = objects.base.assignment(assignment, 520)
                helper.require(objects.base.native(text, 520) == values, 'separate raw native parser agrees')
                helper.require(not objects.base.satisfied(actual_clauses, values), 'all actual augmented clauses')
                projection = objects.check_object(values, clauses, groups, pairs)
                helper.save(folder/'parsed_model.json', dict(assignment=assignment))
                helper.save(folder/'decoded_projection.json', projection)
                system = phases.build(helper.read(objects.RAW), projection)
                helper.save(folder/'phase_system.json', system)
                screen = phases.screen(system)
                helper.save(folder/'phase_screen.json', screen)
                record.update(result='SAT_PROJECTION_CANDIDATE_SCREEN', rank=screen['rank'], nullity=screen['nullity'],
                    candidate_obstruction=screen['obstruction'] is not None, mixed_groups=system['mixed_groups'])
                blocked = [*blocked, block_record(folder/'decoded_projection.json')]
            elif code == 20:
                helper.require([line.strip() for line in (folder/'solver.stdout.log').read_text().splitlines() if line.startswith('s ')] == ['s UNSATISFIABLE'], 'UNSAT status/code agreement')
                record['result'] = 'UNSAT_AUGMENTED_SAMPLING_INSTANCE_UNCHECKED'
                stop = 'UNSAT_STOP_PENDING_PROOF_REPLAY_AND_BLOCK_COVERAGE'
            else:
                record['result'] = 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
                stop = 'UNKNOWN_STOP_NO_RETRY'
            if not native['outer_windows_guard_expired']:
                record['trace'] = bounded_trace_identity(proof, folder, deadline)
            else:
                record['trace'] = dict(linux_path=proof, artifact_availability='LOCAL_ONLY', sha256=None,
                    sha256_null_reason='Outer guard expired; Linux process state is unknown, no final bytes asserted.')
            record['outputs_sha256'] = {helper.key(p): helper.digest(p) for p in folder.iterdir() if p.is_file()}
            helper.save(folder/'summary.json', record)
            helper.save(out/f'checkpoint_{index:02d}.json', dict(timestamp=now(), completed_attempts=len(cases),
                fresh_SAT_cases=len(blocked)-1, blocked_projections=blocked, cases=cases, elapsed_seconds=time.monotonic()-started,
                mathematical_exclusions_independently_approved_in_this_batch=0, overall_search_coverage='UNKNOWN; no validated denominator.'))
            print(json.dumps(dict(case=index, result=record['result'], rank=record.get('rank'), candidate_obstruction=record.get('candidate_obstruction'))), flush=True)
            if code != 10 or native['outer_windows_guard_expired']:
                break
    except BaseException as error:
        stop = 'ERROR_STOP_NO_RETRY'
        helper.save(out/'failure.json', dict(timestamp=now(), error=repr(error), research_calls=launched, returned_native_receipts=len(cases), workspace=workspace))
        raise
    finally:
        elapsed = time.monotonic()-started
        helper.save(out/'summary.json', dict(schema='HADAMARD_PARITY_PHASE_BATCH_RESULT_V1', status='CANDIDATE_BATCH_RECORD_PENDING_INDEPENDENT_REVIEW',
            timestamp=now(), stop_reason=stop, inputs_sha256=inputs, research_calls=launched, returned_native_receipts=len(cases), fresh_SAT_cases=len(blocked)-1,
            candidate_obstruction_cases=sum(bool(x.get('candidate_obstruction')) for x in cases),
            cases=cases, elapsed_seconds=elapsed, budget_overrun_seconds=max(0, elapsed-TOTAL),
            mathematical_exclusions_independently_approved_in_this_batch=0, target_resolution=False,
            artifact_availability='LOCAL_ONLY', proof_artifact_location=workspace,
            scope='Finite distinct parity sampling only. No augmented UNSAT is a family exclusion without complete trace replay and independently approved exclusion of every sampling block.',
            outputs_sha256={helper.key(p): helper.digest(p) for p in out.rglob('*') if p.is_file()}))


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight', action='store_true')
    mode.add_argument('--research', action='store_true')
    for name in ('out', 'encoding-gate', 'general-necessity-gate', 'object-gate'):
        parser.add_argument('--'+name, type=Path, required=True)
    for name in ('encoding-gate-sha256', 'general-necessity-gate-sha256', 'object-gate-sha256'):
        parser.add_argument('--'+name, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
