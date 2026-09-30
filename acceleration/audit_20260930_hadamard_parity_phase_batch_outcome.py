"""Bind the finite parity sample, independent case gates and native receipts.

No producer imports, solver execution, ledger edits or trace-proof claims.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import audit_20260930_hadamard_parity_phase_batch as objects

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
BATCH = B + 'hadamard_parity_phase_batch_pilot'
PRE = B + 'hadamard_parity_phase_batch_preflight/summary.json'
CAL = I + 'hadamard_parity_phase_batch_object_calibration/summary.json'
CASES = I + 'hadamard_parity_phase_batch_cases'
PINS = {
    'acceleration/audit_20260930_hadamard_parity_phase_batch.py': 'cda0c17f4262050ad7668186845842ede0e7f2a02a324f11a659c8dc4d8fceaf',
    CAL: '21f5bfd1067ecee763401ab1c2933b7a392ecc644b241b9ab7664d241a366b09',
    CASES + '/case_00/summary.json': 'd5d404fea6fd8d8e2e8c4f60e4b2ce8eaa83a04a1abed45109eaec1b0eb17eb8',
    CASES + '/case_01/summary.json': '8cf9bf3842fe675973011eb33d6a8909bf64bf2715a8cd9c409858ec593af4f6',
    CASES + '/case_02/summary.json': '08d7cf3be4593d90e34419555bc87c44ab27e3d064559201aff970223fb15995',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def linux(path):
    path = Path(path).resolve()
    need(path.drive.lower() == 'c:', 'observed C drive mapping')
    return '/mnt/c/' + path.as_posix()[3:]


def expected_command(folder, proof):
    return ['wsl.exe', '--distribution', 'Ubuntu-24.04', '--exec',
            '/usr/bin/timeout', '--signal=TERM', '--kill-after=5s', '10s',
            '/usr/bin/prlimit', '--as=4294967296:4294967296',
            '--fsize=10737418240:10737418240', '--core=0:0',
            linux(ROOT/'build/research-cadical195/source/build/cadical'),
            '--no-binary', '-c', '20000', linux(folder/'instance.cnf'), proof]


def native_outcome(text, receipt, launch, folder, index):
    expected = expected_command(folder, launch['ext4_proof'])
    need(receipt['command'] == launch['command'] == expected, 'exact native invocation and limits')
    need(receipt['cwd'] == str(ROOT), 'native working directory')
    need(receipt['outer_windows_guard_seconds'] == 18 and receipt['outer_windows_guard_expired'] is False,
         'observed returned native wrapper, eighteen-second outer guard')
    need(receipt['linux_process_state'] == 'WRAPPED_COMMAND_RETURNED' and receipt['wall_seconds'] >= 0,
         'returned process receipt')
    need(launch['variables'] == 520 and launch['clauses'] == 4542+index and launch['remaining_batch_seconds'] >= 25,
         'actual clause count and launch reserve')
    need(re.findall(r'^c Version (.+)$', text, re.M) == ['1.9.5 146207318796f094dcded87349a64f0c6927309e'], 'native exact version')
    need(re.findall(r"^c found 'p cnf (\d+) (\d+)' header$", text, re.M) == [('520', str(4542+index))],
         'native actual parsed header')
    need("c setting conflict limit to 20000 conflicts (due to '20000')" in text, 'configured conflict cap')
    need(f"c DRAT proof file '{launch['ext4_proof']}' closed" in text, 'trace closed before native return')
    states = re.findall(r'^s (.+)$', text, re.M)
    exits = re.findall(r'^c exit (-?\d+)$', text, re.M)
    need(len(exits) == 1 and int(exits[0]) == receipt['actual_exit_code'], 'native footer and receipt exit agree')
    conflicts = re.findall(r'^c conflicts:\s+(\d+)\s', text, re.M)
    need(len(conflicts) == 1, 'one observed final conflict count')
    conflicts = int(conflicts[0])
    code = receipt['actual_exit_code']
    if code == 10:
        need(states == ['SATISFIABLE'] and 'c UNKNOWN' not in text, 'SAT status and native exit')
        result = 'SAT_PROJECTION'
    elif code == 0:
        need(states == [] and re.findall(r'^c UNKNOWN$', text, re.M) == ['c UNKNOWN']
             and conflicts == 20000, 'actual UNKNOWN conflict-cap outcome; no SAT or UNSAT')
        result = 'UNKNOWN_CONFLICT_CAP'
    else:
        raise ValueError('Unexpected outcome requires separate checking path')
    numbers = {}
    for name, pattern in [
        ('native_cpu_seconds', r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$'),
        ('native_wall_seconds', r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$'),
        ('native_maximum_resident_MB', r'^c maximum resident set size of process:\s+([0-9.]+)\s+MB$'),
        ('trace_bytes_observed_by_native', r'^c DRAT (\d+) bytes')]:
        values = re.findall(pattern, text, re.M)
        need(len(values) == 1, 'one native statistic '+name)
        numbers[name] = int(values[0]) if name.endswith('native') else float(values[0])
    return dict(index=index, result=result, native_exit=code, configured_conflicts=20000,
                observed_conflicts=conflicts, wrapper_wall_seconds=receipt['wall_seconds'], **numbers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs, controls = {}, []

    def pin(path, expected=None):
        path = Path(path)
        path = (ROOT/path if not path.is_absolute() else path).resolve()
        need(path.is_relative_to(ROOT), 'repository artifact path')
        key = path.relative_to(ROOT).as_posix()
        digest = sha(path)
        need(expected is None or digest == expected, 'exact artifact identity '+key)
        inputs[key] = digest
        return path

    def load(path, expected=None):
        return json.loads(pin(path, expected).read_bytes())

    def reject(label, action):
        try:
            action()
        except (ValueError, KeyError, TypeError, IndexError):
            controls.append(label)
        else:
            raise ValueError('corruption accepted '+label)

    try:
        for path, digest in PINS.items():
            pin(path, digest)
        batch = load(BATCH+'/summary.json')
        manifest = load(BATCH+'/manifest.json')
        preflight = load(PRE)
        need(preflight['status'] == 'HADAMARD_PARITY_PHASE_BATCH_PREFLIGHT_PASS'
             and preflight['research_calls'] == 0 and manifest['mode'] == 'RESEARCH', 'real preflight then research')
        need(manifest['inputs_sha256'] == batch['inputs_sha256'] == preflight['inputs_sha256'], 'unchanged gated inputs')
        for path, digest in manifest['inputs_sha256'].items():
            pin(path, digest)
        for path, digest in batch['outputs_sha256'].items():
            pin(path, digest)
        need(manifest['source_commit'] == subprocess.check_output(['git', 'rev-parse', manifest['source_commit']], cwd=ROOT, text=True).strip(),
             'real immutable source commit')
        expected_limits = dict(maximum_fresh_SAT_cases=16, native_wall_seconds=10, native_conflicts=20000,
            address_space_bytes=4294967296, trace_file_bytes=10737418240, kill_after_seconds=5,
            outer_windows_guard_seconds=18, research_budget_seconds=180, launch_reserve_seconds=25,
            automatic_retry=False, random_seed=None, random_seed_null_reason='Native default retained.')
        need(manifest['limits'] == expected_limits, 'complete frozen resource allocation')
        need('--research' in manifest['command'] and '--preflight' not in manifest['command'], 'actual research invocation')
        need(batch['schema'] == 'HADAMARD_PARITY_PHASE_BATCH_RESULT_V1' and batch['research_calls'] == 4
             and batch['returned_native_receipts'] == 4 and len(batch['cases']) == 4
             and batch['fresh_SAT_cases'] == 3 and batch['candidate_obstruction_cases'] == 2
             and batch['stop_reason'] == 'UNKNOWN_STOP_NO_RETRY', 'finite attempt and stage-specific counts')
        need(batch['mathematical_exclusions_independently_approved_in_this_batch'] == 0 and batch['target_resolution'] is False,
             'producer did not selfapprove mathematical outputs')
        need(batch['elapsed_seconds'] >= 0 and batch['budget_overrun_seconds'] == max(0,batch['elapsed_seconds']-180), 'cooperative budget accounting')
        folders = sorted(p.name for p in (ROOT/BATCH).glob('case_*') if p.is_dir())
        need(folders == ['case_00','case_01','case_02','case_03'], 'no hidden additional attempt directory')
        clauses, groups, pairs = objects.canonical_base(load(objects.RAW), load(objects.OLD_MODEL))
        records, case_reports, trace_records = [], [], []
        all_selected = []
        for index in range(4):
            folder = ROOT/BATCH/f'case_{index:02d}'
            prefix = folder.relative_to(ROOT).as_posix()
            case = load(prefix+'/summary.json')
            receipt = load(prefix+'/solver.receipt.json')
            launch = load(prefix+'/launch.json')
            need(case == batch['cases'][index] and case['receipt'] == receipt and case['index'] == index, 'case-summary identity')
            need(pin(folder/'instance.cnf', launch['cnf_sha256']), 'launch CNF authenticated')
            for stream in ('stdout','stderr'):
                need(receipt[stream] == prefix+'/solver.'+stream+'.log', 'exact native stream path')
                pin(receipt[stream], receipt[stream+'_sha256'])
            text = (folder/'solver.stdout.log').read_text(encoding='utf-8')
            actual = native_outcome(text, receipt, launch, folder, index)
            records.append(actual)
            blocks = load(prefix+'/blocked_projections.json')
            need(len(blocks) == index+1, 'one initial plus all earlier sampling blocks')
            for j, block in enumerate(blocks):
                need(block['purpose'] == 'DISTINCT_CANDIDATE_SAMPLING'
                     and block['mathematical_exclusion_approved'] == (j==0), 'sampling and prior-approved exclusion distinguished')
                if j:
                    need(block['projection_path'] == BATCH+f'/case_{j-1:02d}/decoded_projection.json'
                         and block['independent_exclusion_gate'] is None
                         and block['independent_exclusion_gate_sha256'] is None, 'all preceding candidates in original order')
                else:
                    need(block['independent_exclusion_gate'] == I+'hadamard_f3_phase_obstruction/summary.json'
                         and block['independent_exclusion_gate_sha256'] == '0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346', 'initial exclusion reference')
            actual_clauses, _ = objects.blocked_formula(clauses, blocks, groups, load)
            need((folder/'instance.cnf').read_bytes() == objects.parity.cnf_bytes(actual_clauses), 'all actual base-plus-block bytes, including terminal UNKNOWN')
            if index < 3:
                report = load(CASES+f'/case_{index:02d}/summary.json', PINS[CASES+f'/case_{index:02d}/summary.json'])
                need(report['status'] == 'INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_CASE_PASS'
                     and report['result']['case_index'] == index, 'complete independent mathematical case gate')
                for mapping in ('inputs_sha256','outputs_sha256'):
                    for path, digest in report[mapping].items():
                        pin(path,digest)
                need(case['rank'] == report['result']['rank'] and case['nullity'] == report['result']['nullity']
                     and case['candidate_obstruction'] == report['result']['exact_exclusion']
                     and actual['result'] == 'SAT_PROJECTION', 'case outcome and mathematical-check agreement')
                projection = load(CASES+f'/case_{index:02d}/independent_projection.json')
                all_selected.append(tuple(projection['selected_group_selector_ids']))
                case_reports.append(report['result'])
            else:
                need(actual['result'] == 'UNKNOWN_CONFLICT_CAP' and case['result'] == 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME', 'terminal actual UNKNOWN')
                need(not any((folder/name).exists() for name in ['parsed_model.json','decoded_projection.json','phase_system.json','phase_screen.json']),
                     'no fabricated terminal witness or certificate')
            checkpoint = load(BATCH+f'/checkpoint_{index:02d}.json')
            need(checkpoint['completed_attempts'] == index+1 and checkpoint['fresh_SAT_cases'] == min(index+1,3)
                 and checkpoint['cases'] == batch['cases'][:index+1], 'each exact progressive checkpoint')
            expected_block_count = min(index+1,3)+1
            need(len(checkpoint['blocked_projections']) == expected_block_count
                 and checkpoint['mathematical_exclusions_independently_approved_in_this_batch'] == 0, 'checkpoint sampling-only interpretation')
            # Historical successful stat/hash receipts are evidence of what existed,
            # not evidence of availability now. Independently observe each exact path.
            trace = case['trace']
            need(trace['linux_path'] == launch['ext4_proof'] and trace['preserved'] is True
                 and trace['artifact_availability'] == 'LOCAL_ONLY', 'historical producer trace metadata')
            for method in ('stat','hash'):
                saved = load(prefix+'/proof_'+method+'.receipt.json')
                need(saved == trace[method+'_receipt'] and saved['actual_exit_code'] == 0
                     and saved['outer_windows_guard_expired'] is False, 'historical successful metadata command')
                for stream in ('stdout','stderr'):
                    pin(saved[stream], saved[stream+'_sha256'])
            need(int((folder/'proof_stat.stdout.log').read_text().strip()) == trace['bytes']
                 == actual['trace_bytes_observed_by_native'], 'three historical trace-size observations')
            need((folder/'proof_hash.stdout.log').read_text().strip().split() == [trace['sha256'],trace['linux_path']],
                 'historical full trace hash and exact path')
            command = ['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/stat','--format=%s',trace['linux_path']]
            observation = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=10)
            (out/f'case_{index:02d}_trace_stat.stdout.log').write_bytes(observation.stdout)
            (out/f'case_{index:02d}_trace_stat.stderr.log').write_bytes(observation.stderr)
            available = observation.returncode == 0
            if available:
                need(int(observation.stdout.strip()) == trace['bytes'], 'currently available trace size')
            else:
                need(observation.returncode != 0 and b'No such file or directory' in observation.stderr,
                     'direct missing-file observation; distinguish from permission or runtime errors')
            trace_records.append(dict(index=index,linux_path=trace['linux_path'],historical_sha256=trace['sha256'],
                historical_bytes=trace['bytes'],historical_hash_receipt=prefix+'/proof_hash.receipt.json',
                current_availability='LOCAL_ONLY' if available else 'MISSING',current_command=command,
                current_exit=observation.returncode,current_timestamp=datetime.now(timezone.utc).isoformat(),
                proof_status='Not an UNSAT proof. SAT-run traces or terminal UNKNOWN partial trace.',
                loss_cause=None,loss_cause_null_reason='Missing path observed; no cause established by this audit.'))
        need(len(set(all_selected)) == 3, 'three unique complete fresh projections')
        need([r['result'] for r in records] == ['SAT_PROJECTION']*3+['UNKNOWN_CONFLICT_CAP'], 'actual native result sequence')
        need([r['rank'] for r in case_reports] == [119,113,119]
             and [r['exact_exclusion'] for r in case_reports] == [True,False,True], 'separate phase conclusions')
        need(sum(r['wrapper_wall_seconds'] for r in records) <= batch['elapsed_seconds'], 'measured wrapper boundaries')
        # Outcome-parser controls mutate genuine raw evidence, not a claimed new run.
        folder = ROOT/BATCH/'case_03'
        receipt=load(BATCH+'/case_03/solver.receipt.json'); launch=load(BATCH+'/case_03/launch.json')
        text=(folder/'solver.stdout.log').read_text(encoding='utf-8')
        for label,key,value in [('false_SAT_exit','actual_exit_code',10),('false_UNSAT_exit','actual_exit_code',20),
                               ('outer_guard_expired','outer_windows_guard_expired',True),('wrong_outer_limit','outer_windows_guard_seconds',19)]:
            bad=deepcopy(receipt);bad[key]=value
            reject(label,lambda bad=bad:native_outcome(text,bad,launch,folder,3))
        bad=deepcopy(receipt);bad['command'][7]='11s'
        reject('changed_native_wall_limit',lambda:native_outcome(text,bad,launch,folder,3))
        reject('fake_UNSAT_status',lambda:native_outcome(text.replace('c UNKNOWN','s UNSATISFIABLE'),receipt,launch,folder,3))
        reject('false_observed_conflicts',lambda:native_outcome(text.replace('c conflicts:                 20000','c conflicts:                 19999'),receipt,launch,folder,3))
        reject('false_parsed_CNF_header',lambda:native_outcome(text.replace("p cnf 520 4545","p cnf 520 4544"),receipt,launch,folder,3))
        bad=deepcopy(launch);bad['remaining_batch_seconds']=24
        reject('launch_below_frozen_reserve',lambda:native_outcome(text,receipt,bad,folder,3))
        for path in ['failure.json','manifest.json','case_00_transfer_hash.receipt.json','case_00_transfer_hash.stdout.log','case_00_transfer_hash.stderr.log']:
            pin(B+'hadamard_parity_phase_batch_trace_archive/'+path)
        save(out/'native_outcomes.json',records)
        save(out/'trace_availability.json',trace_records)
        save(out/'controls.json',dict(corruptions_rejected=controls,positive_controls='The three actual SAT receipts and terminal actual UNKNOWN receipt pass with raw logs.'))
        timestamp=datetime.now(timezone.utc).isoformat()
        common=dict(revision=1,basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            created_at=timestamp,updated_at=timestamp,verifier='/root/eight_domain_audit',
            external_review=False,artifact_availability='LOCAL_ONLY',
            verification_method='Complete independent raw assignment/CNF/phase checks plus immutable case-report binding; no producer imports.')
        bindings=[dict(common,id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-PROJECTIONS',kind='construction',
            statement='The three exact saved projections in cases00,01,02 are distinct and satisfy all4541 clauses of the fixed-support strengthened parity formula, and respectively its1,2,3 complete twenty-selector sampling blocks.',
            scope='Three specified parity projections on the single frozen six-prism Hadamard support; no full Gram factor or graph.',
            assumptions=['Coordinatewise balanced support triples are an additional construction restriction.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-PROJECTION',revision=1,relation='encoding_equivalence')],
            evidence=[CASES+f'/case_{i:02d}/summary.json' for i in range(3)],
            limitations=['Finite sample, not exhaustive coverage.','A satisfying projection need not lift to a factor.','Sampling blocks are not all mathematical exclusions.']),
          dict(common,id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-LOCAL-PHASE-EXCLUSIONS',kind='exclusion',
            statement='For each of the exact saved parity assignments in cases00 and02, the necessary general GF(3) phase equations force a mixed-group same-sign phase difference to zero; hence neither assignment has a coordinatewise balanced coloring lift realizing the prescribed full Gram matrix.',
            scope='Exactly two specified balanced fixed-support parity branches; not the entire support, any core, or the unrestricted target.',
            assumptions=['The selected parity patterns and frozen six-prism Hadamard supports.','The general phase necessity theorem is used only within its balanced-triple scope.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='premise'),
                          dict(id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-PROJECTIONS',revision=1,relation='premise')],
            evidence=[CASES+f'/case_{i:02d}/summary.json' for i in [0,2]],
            limitations=['The explicit row combinations are exact; ranks alone are not exclusion certificates.','Case01 is not excluded by these checks.','No target-level consequence or exhaustive branch cover.']),
          dict(common,id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-LINEAR-SURVIVOR',kind='empirical/engineering result',
            statement='For the exact saved case01 projection, the declared172-by120 homogeneous GF(3) phase matrix has rank113 and nullity7, and none of its72 mixed-group same-sign difference functionals vanishes on the whole nullspace.',
            scope='One specified linear necessary-condition screen, with its72 declared individual rejection functionals.',
            assumptions=['The exact saved case01 projection and declared phase-system schema.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='premise'),
                          dict(id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-PROJECTIONS',revision=1,relation='premise')],
            evidence=[CASES+'/case_01/summary.json'],
            limitations=['Separate nonzero evaluations do not establish a vector satisfying all inequalities simultaneously.','No nonlinear phase solution, coloring, full factor or graph is claimed.'])]
        save(out/'claim_bindings.json',bindings)
        pin(Path(__file__))
        for path in ['uv.lock','pyproject.toml']:
            pin(path)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OUTCOME_PASS',timestamp=timestamp,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,
            outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},
            counts=dict(native_attempts=4,distinct_fresh_SAT_projections=3,independently_checked_SAT_projections=3,
                exact_local_phase_exclusions=2,linear_screen_survivors=1,UNKNOWN_native_outcomes=1,
                UNSAT_native_outcomes=0,full_factors=0,target_graphs=0),
            batch_elapsed_seconds=batch['elapsed_seconds'],corruption_controls=len(controls),
            current_trace_availability=[t['current_availability'] for t in trace_records],
            current_process_state='UNKNOWN; no fresh live-process census is claimed by this audit.',
            execution_scope='Four completed native receipts and a frozen terminal stop; no retry or ongoing run implied.',
            shared_components=['Frozen independently authored batch-object checker and its parity parser/reconstructor reused with exact source pins.',
                'New native receipt parser, exact aggregate bindings, direct trace-availability observations; no producer imports.'],
            limitations=['Historical trace hashes are retained, but unavailable artifacts are not currently replayable.',
                'No native UNSAT occurred; none of these trace files is promoted as a proof.',
                'The third sampling block removes a branch surviving this linear screen, so augmented UNSAT would not itself exclude the full family.',
                'Overall search coverage: UNKNOWN; no validated denominator.'],
            verifier='/root/eight_domain_audit',artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OUTCOME_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)))
        raise


if __name__ == '__main__':
    main()
