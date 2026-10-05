"""Budget-aware build/controls/candidate extraction of a preserved DRAT prefix.

This producer establishes no RAT/RUP validity or mathematical equivalence.
All modes must run inside Linux under the existing command supervisor.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

import native_20261002_exact_eight_budget_v1 as shared
from command_deadline import CommandDeadline

ROOT = shared.ROOT
CPP = ROOT/'acceleration/drat_restart_20261002_v1.cpp'
SPEC = Path(__file__).with_name(Path(__file__).stem+'_spec.md')
PROFILE = ROOT/'build/rook-drat-checker/drat-trim.c'
PROFILE_SHA = '82835512d4eda7dee1e0e3f610a0672fa1d216ea91246bcb576022020fe18f4c'
COMPILER = Path('/usr/bin/g++')
COMPILER_SHA = '1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
PROFILE_NAME = 'PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1'
CODE = list(dict.fromkeys(path.resolve() for path in [Path(__file__), CPP, SPEC, *shared.CODE, PROFILE]))


def supervision(args, pins, deadline):
    shared.need(sys.platform.startswith('linux'), 'compile/parse supervision must run inside Linux')
    path = args.supervision_out.resolve()/'manifest.json'
    data = shared.read(path)
    shared.pin(ROOT/'acceleration/run_compute_command.py', data['source_sha256'], pins, deadline)
    shared.need(data['seconds'] <= 21600 and data['seconds'] >= args.seconds+10 and
                data['automatic_retry'] is False and data['cumulative_across_commands'] is False,
                'outer per-command supervisor and shorter parser sub-allocation')
    pgid = os.getpgid(0)
    leader = [part.decode() for part in (Path('/proc')/str(pgid)/'cmdline').read_bytes().split(b'\0') if part]
    shared.need(leader and Path(leader[0]).name == 'timeout' and '--signal=KILL' in leader,
                'live enclosing native process-group guard')
    shared.need(str(Path(__file__).resolve()) in data['command'] or shared.key(Path(__file__)) in data['command'],
                'actual supervised preparation source')
    return dict(manifest_path=shared.key(path), manifest_sha256=shared.sha(path, deadline),
                invocation_id=data['invocation_id'], outer_seconds=data['seconds'],
                producer_seconds=args.seconds, process_group=pgid, guard_argv=leader)


def execute(argv, prefix, deadline, expected):
    start = time.monotonic()
    with Path(str(prefix)+'.stdout.log').open('xb') as stdout, Path(str(prefix)+'.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
        try:
            shared.need(os.getpgid(process.pid) == os.getpgid(0), 'preparation child remains in enclosing group')
            while process.poll() is None:
                status = deadline.status()
                if status['stop_required'] or status['remaining_seconds'] <= 20:
                    raise RuntimeError('not completed within the allocated budget')
                time.sleep(.05)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            code = process.wait(timeout=5)
    result = dict(timestamp=shared.stamp(), command=argv, cwd=str(ROOT), actual_exit_code=code,
        expected_exit_code=expected, reaped=True, wall_seconds=time.monotonic()-start,
        child_pid=process.pid, process_group=os.getpgid(0),
        stdout=shared.key(Path(str(prefix)+'.stdout.log')), stderr=shared.key(Path(str(prefix)+'.stderr.log')))
    for field in ['stdout', 'stderr']:
        result[field+'_sha256'] = shared.sha(ROOT/result[field], deadline)
    shared.save(Path(str(prefix)+'.receipt.json'), result)
    shared.need(code == expected, 'observed build/parser exit differs from declared expectation')
    return result


def parser_call(args, cnf, proof, destination, prefix, deadline, expected=0):
    seconds = deadline.child_seconds(args.parser_seconds, reserve_seconds=30)
    argv = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{seconds:.6f}s',
            '/usr/bin/prlimit', f'--as={args.address_space_bytes}:{args.address_space_bytes}', '--core=0:0',
            str(args.parser.resolve()), '--cnf', str(cnf), '--proof', str(proof), '--out', str(destination),
            '--seconds', f'{max(.001, seconds-5):.6f}']
    return execute(argv, prefix, deadline, expected)


def authenticate_parser(args, pins, deadline):
    shared.need(args.parser and args.parser_sha256 and args.build_manifest and args.build_manifest_sha256,
                'explicit fresh parser/build identities')
    shared.pin(args.parser, args.parser_sha256, pins, deadline)
    shared.pin(args.build_manifest, args.build_manifest_sha256, pins, deadline)
    build = shared.read(args.build_manifest)
    shared.need(build['schema'] == 'DRAT_RESTART_PARSER_BUILD_V1' and
                build['parser_path'] == shared.key(args.parser) and build['parser_sha256'] == args.parser_sha256 and
                build['compiler_sha256'] == COMPILER_SHA and build['compiler_version_stdout'].startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'),
                'exact observed new compiler/build/parser receipt')
    shared.need(build['source_cpp_sha256'] == pins[shared.key(CPP)] and
                build['command'][1:5] == ['-std=c++17', '-O2', '-Wall', '-Wextra'] and '-Werror' in build['command'],
                'unchanged compiled source and explicit compiler configuration')


def build(args, out, deadline):
    shared.need(shared.sha(COMPILER, deadline) == COMPILER_SHA, 'pinned observed g++ binary')
    version = subprocess.run([str(COMPILER), '--version'], capture_output=True, text=True, timeout=10)
    shared.need(version.returncode == 0 and version.stdout.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'),
                'pinned observed compiler version')
    binary = out/'drat_restart_parser'
    command = [str(COMPILER), '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', str(CPP), '-o', str(binary)]
    receipt = execute(command, out/'compile', deadline, 0)
    result = dict(schema='DRAT_RESTART_PARSER_BUILD_V1', timestamp=shared.stamp(), command=command,
        compiler_path=str(COMPILER), compiler_sha256=COMPILER_SHA, compiler_version_stdout=version.stdout,
        source_cpp_path=shared.key(CPP), source_cpp_sha256=shared.sha(CPP, deadline),
        parser_path=shared.key(binary), parser_sha256=shared.sha(binary, deadline),
        parser_bytes=binary.stat().st_size, compile_receipt=receipt, independent_approval=False)
    shared.save(out/'build_manifest.json', result)
    return dict(build_manifest_path=shared.key(out/'build_manifest.json'),
                build_manifest_sha256=shared.sha(out/'build_manifest.json', deadline), **result)


def controls(args, out, deadline):
    unsat = b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
    multiset = b'p cnf 3 4\n1 2 0\n2 1 0\n3 0\n-1 -2 0\n'
    cases = [
        ('complete_prefix', unsat, b'-2 0\n', 0),
        ('multiset_delete_one', multiset, b'd 1 2 0\n1 2 0\nd 2 1 0\nd 3 0\nd 3 0\nd -3 0\nd 1 -2 0\n2 2 1 0\n', 0),
        ('truncated_tail', unsat, b'-2 0\n1', 0),
        ('zero_without_newline', unsat, b'-2 0', 0),
        ('ignored_unit_delete', unsat, b'-2 0\nd -2 0\n', 0),
        ('missing_nonunit_delete', unsat, b'd 1 -2 -1 0\n', 0),
        ('internal_unterminated', unsat, b'-2 0\n1\n', 2),
        ('malformed_integer', unsat, b'z 0\n', 2),
        ('extra_variable', unsat, b'3 0\n', 2),
        ('extra_token_after_zero', unsat, b'-2 0 1\n', 2),
        ('extra_token_after_zero_EOF', unsat, b'-2 0 1', 2),
        ('malformed_integer_EOF', unsat, b'garbage', 2),
    ]
    rows = []
    for label, cnf, proof, expected in cases:
        folder = out/label
        folder.mkdir()
        cnf_path, proof_path = folder/'original.cnf', folder/'original_prefix.drat'
        cnf_path.write_bytes(cnf)
        proof_path.write_bytes(proof)
        receipt = parser_call(args, cnf_path, proof_path, folder/'candidate', folder/'parser', deadline, expected)
        rows.append(dict(label=label, cnf_path=shared.key(cnf_path), cnf_sha256=shared.sha(cnf_path, deadline),
            proof_path=shared.key(proof_path), proof_sha256=shared.sha(proof_path, deadline),
            expected_exit_code=expected, parser_receipt=receipt, independent_approval=False))
    # Independent reviewers can check suffix against derivative and concatenated
    # original. These exact fixtures are not checked/promoted by the producer.
    (out/'tiny_valid_suffix.drat').write_bytes(b'1 0\n0\n')
    (out/'tiny_wrong_suffix.drat').write_bytes(b'3 0\n0\n')
    return rows


def preparation(args, out, pins, deadline):
    shared.need(args.plan and args.plan_sha256, 'explicit independently reviewable frozen preparation plan')
    shared.pin(args.plan, args.plan_sha256, pins, deadline)
    plan = shared.read(args.plan)
    shared.need(plan['schema'] == 'DRAT_RESTART_PREPARATION_PLAN_V1' and plan['checker_profile'] == PROFILE_NAME,
                'exact declared checking profile')
    for field in ['question', 'scope', 'success_criterion', 'falsification_criterion', 'independent_verification_criterion',
                  'baseline_and_uncertainty', 'source_commit']:
        shared.need(isinstance(plan.get(field), str) and plan[field].strip(), 'declared plan '+field)
    shared.need(re.fullmatch('[0-9a-f]{40}', plan['source_commit']), 'source commit identity')
    paths = {}
    for role in ['original_cnf', 'original_partial_proof', 'historical_native_receipt', 'encoding_gate']:
        descriptor = plan[role]
        path = shared.repository_path(descriptor['path'])
        shared.pin(path, descriptor['sha256'], pins, deadline)
        shared.need(path.stat().st_size == descriptor['bytes'], 'exact original artifact length '+role)
        paths[role] = path
    gate = shared.read(paths['encoding_gate'])
    shared.need(gate['status'] == 'INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS' and
                gate['cnf_sha256'] == plan['original_cnf']['sha256'], 'original unrestricted formula independent gate')
    if args.mode == 'preflight':
        return [], plan
    shared.need(args.control_gate and args.control_gate_sha256, 'fresh independent parser semantic calibration required')
    shared.pin(args.control_gate, args.control_gate_sha256, pins, deadline)
    controls_gate = shared.read(args.control_gate)
    shared.need(controls_gate['status'] == 'INDEPENDENT_DRAT_RESTART_PREPARATION_V1_PASS', 'new parser calibration PASS')
    for path in CODE+[args.parser]:
        shared.need(controls_gate['inputs_sha256'].get(shared.key(path)) == pins[shared.key(path)], 'fresh full code/profile/parser gate closure')
    receipt = parser_call(args, paths['original_cnf'], paths['original_partial_proof'], out/'candidate',
                          out/'parser', deadline)
    parser = shared.read(out/'candidate/parser_summary.json')
    shared.need(parser['status'] == 'CANDIDATE_RESTART_STATE' and parser['profile'] == PROFILE_NAME and
                parser['original_proof_bytes'] == plan['original_partial_proof']['bytes'] and
                parser['retained_original_bytes']+parser['trailing_dropped_bytes'] == parser['original_proof_bytes'] and
                parser['rat_rup_checked'] is False and parser['equisatisfiability_asserted'] is False,
                'honest exact candidate prefix accounting')
    rows = [dict(parser_receipt=receipt, parser_summary=parser,
        outputs=[dict(path=shared.key(out/'candidate'/name), sha256=shared.sha(out/'candidate'/name, deadline),
                      bytes=(out/'candidate'/name).stat().st_size)
                 for name in ['restart.cnf', 'retained_prefix.drat', 'parser_summary.json']])]
    return rows, plan


def run(args):
    shared.need(40 < args.seconds <= 1800 and 0 < args.parser_seconds < args.seconds-30,
                'preparation allowance/review cadence and shutdown reserve')
    shared.need(type(args.address_space_bytes) is int and 256*1024**2 <= args.address_space_bytes <= 8*1024**3,
                'explicit parser address-space guard')
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason)
    out = args.out.resolve()
    shared.need(out.is_relative_to(ROOT), 'existing repository immutable outputs')
    out.mkdir(parents=True, exist_ok=False)
    pins, rows, plan = {}, [], None
    try:
        supervisor = supervision(args, pins, deadline)
        for path in CODE:
            pins[shared.key(path)] = shared.sha(path, deadline)
        shared.pin(PROFILE, PROFILE_SHA, pins, deadline)
        if args.mode != 'build':
            authenticate_parser(args, pins, deadline)
        manifest = dict(schema='DRAT_RESTART_PREPARATION_INVOCATION_V1', timestamp=shared.stamp(), mode=args.mode,
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=pins, supervision=supervisor,
            parser_seconds=args.parser_seconds, address_space_bytes=args.address_space_bytes,
            allocation_reason=args.allocation_reason, profile=PROFILE_NAME,
            independent_approval=False, target_resolution=False, automatic_retry=False, automatic_resume=False)
        shared.save(out/'manifest.json', manifest)
        if args.mode == 'build':
            rows = [build(args, out, deadline)]
        elif args.mode == 'controls':
            rows = controls(args, out, deadline)
        else:
            rows, plan = preparation(args, out, pins, deadline)
        summary = dict(schema='DRAT_RESTART_PREPARATION_OUTPUTS_V1', timestamp=shared.stamp(), mode=args.mode,
            status='CANDIDATE_OUTPUTS_PENDING_INDEPENDENT_VERIFICATION', records=rows, plan=plan,
            manifest_path=shared.key(out/'manifest.json'), manifest_sha256=shared.sha(out/'manifest.json', deadline),
            inputs_sha256=pins, independent_approval=False, rat_rup_checked=False,
            equisatisfiability_asserted=False, mathematical_exclusions_asserted=0, target_resolution=False,
            elapsed_seconds=deadline.status()['elapsed_seconds'], automatic_resume=False,
            unmet_requirements=['Independent parser/artifact checks; any exclusion requires complete combined proof replay against original CNF.'])
        shared.save(out/'summary.json', summary)
        print(json.dumps(dict(status=summary['status'], summary_sha256=shared.sha(out/'summary.json', deadline))), flush=True)
        return 0
    except BaseException as error:
        shared.save(out/'failure.json', dict(timestamp=shared.stamp(), error=repr(error), records=rows,
            independent_approval=False, target_resolution=False, rat_rup_checked=False,
            unfinished_description='not completed within the allocated budget', automatic_resume=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'controls', 'preflight', 'prepare'])
    for name in ['out', 'supervision-out']:
        parser.add_argument('--'+name, type=Path, required=True)
    for name in ['parser', 'build-manifest', 'plan', 'control-gate']:
        parser.add_argument('--'+name, type=Path)
        parser.add_argument('--'+name+'-sha256')
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--parser-seconds', type=float, required=True)
    parser.add_argument('--address-space-bytes', type=int, required=True)
    parser.add_argument('--allocation-reason', required=True)
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise InterruptedError(f'Restart preparation received signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
