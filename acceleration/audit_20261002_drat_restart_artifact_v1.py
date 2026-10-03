"""Complete independent streaming Counter/byte check of candidate DRAT restart.

No parser or producer imports. This checks exact syntax/state transformation,
not RAT/RUP validity, model reconstruction, or equisatisfiability. The earlier
independent tiny-control oracle is shared only for calibrating this new checker.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1'
CONTROL_ORACLE = ROOT/'acceleration/audit_20261002_drat_restart_controls_v1.py'
CONTROL_GATE = ROOT/'acceleration/results/20261002_drat_restart_controls_audit01/summary.json'
CONTROL_GATE_SHA = '0abe2311462f6821913231e42dbd0861c4fe3d2b75f2be1017af9c7e6fb34134'
ORIGINAL_CNF_SHA = '7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138'
ORIGINAL_PROOF_SHA = '11abdc29b502b8b09d4dc6ac3e9f03fa7ea8947496bc8e538a5043d113272f22'


def need(value, message):
    if not value:
        raise ValueError(message)


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def parse(raw, n, terminated):
    tokens = raw.split()
    values = []
    for token in tokens:
        need(re.fullmatch(rb'-?[0-9]+', token), 'exact integer token')
        value = int(token)
        need(-2147483648 < value <= 2147483647 and abs(value) <= n, 'fixed literal universe')
        values.append(value)
    if terminated:
        need(values and values[-1] == 0 and 0 not in values[:-1], 'single final clause zero')
        values.pop()
    else:
        need(0 not in values, 'unterminated final record has no earlier zero')
    literals = sorted(set(values))
    return struct.pack('<' + 'i'*len(literals), *literals), len(values)-len(literals), any(-value in literals for value in literals)


def check(formula, proof, derivative, retained, candidate_summary, deadline, progress=None):
    """Four binary streams; independent exact ordered Counter reconstruction."""
    header = formula.readline().split()
    need(len(header) == 4 and header[:2] == [b'p', b'cnf'], 'original single DIMACS header')
    n, declared = map(int, header[2:])
    need(0 < n <= 2147483647 and 0 <= declared < 4294967295, 'original dimensions')
    state, stats = Counter(), Counter()
    stats.update(variables=n, original_clauses=declared, appended_boundary_newline=False)
    originals, ticks = 0, 0
    def pulse(size):
        nonlocal ticks
        ticks += 1
        if progress is not None:
            progress.update(size)
        if not ticks % 8192:
            need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
    def add(identity):
        if identity in state:
            stats['duplicate_clause_additions'] += 1
        else:
            stats['unique_recorded_clauses'] += 1
            stats['stored_literals'] += len(identity)//4
        state[identity] += 1
    for record in formula:
        pulse(len(record))
        if not record.strip() or record.startswith(b'c'):
            continue
        identity, duplicates, tautology = parse(record, n, True)
        stats['duplicate_literals_normalized'] += duplicates
        stats['tautology_records_retained'] += tautology
        stats['original_literals'] += len(identity)//4
        add(identity)
        originals += 1
    need(originals == declared, 'complete original clause count')
    dropped = False
    for record in proof:
        pulse(len(record))
        need(not dropped, 'only final raw record may be dropped')
        stats['original_proof_bytes'] += len(record)
        has_lf = record.endswith(b'\n')
        line = record[:-1] if has_lf else record
        raw = line.strip()
        if raw and not raw.startswith(b'c'):
            deletion = raw.startswith(b'd')
            if deletion:
                need(raw == b'd' or len(raw) > 1 and raw[1:2].isspace(), 'deletion separator')
                raw = raw[1:].strip()
            if not has_lf and (not raw or raw.split()[-1] != b'0'):
                parse(raw, n, False)
                stats['trailing_dropped_bytes'] = len(record)
                dropped = True
                continue
            identity, duplicates, tautology = parse(raw, n, True)
            stats['duplicate_literals_normalized'] += duplicates
            stats['tautology_records_retained'] += tautology
            if deletion:
                stats['proof_deletions'] += 1
                if len(identity)//4 <= 1:
                    stats['ignored_small_deletions'] += 1
                elif state.get(identity, 0):
                    state[identity] -= 1
                    stats['effective_deletions'] += 1
                else:
                    stats['missing_deletions'] += 1
            else:
                stats['proof_additions'] += 1
                add(identity)
        expected_prefix_line = line + b'\n'
        need(retained.readline() == expected_prefix_line, 'every exact retained prefix byte and pivot')
        stats['retained_original_bytes'] += len(record)
        stats['appended_boundary_newline'] = not has_lf
    need(retained.read(1) == b'', 'retained prefix has no extra bytes')
    stats['active_clause_occurrences'] = sum(state.values())
    expected_header = f'p cnf {n} {stats["active_clause_occurrences"]}\n'.encode()
    need(derivative.readline() == expected_header, 'derivative dimensions/count preserve variable universe')
    emitted = 0
    for identity, multiplicity in state.items():
        if not multiplicity:
            continue
        values = [cell[0] for cell in struct.iter_unpack('<i', identity)]
        expected_line = (' '.join(map(str, values)) + (' ' if values else '') + '0\n').encode()
        for _ in range(multiplicity):
            need(derivative.readline() == expected_line, 'every deterministic active clause occurrence')
            emitted += 1
            if not emitted % 8192:
                need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
    need(derivative.read(1) == b'', 'derivative has no extra clauses/bytes')
    need(candidate_summary['schema'] == 'DRAT_ACTIVE_MULTISET_PARSER_V1' and
         candidate_summary['status'] == 'CANDIDATE_RESTART_STATE' and candidate_summary['profile'] == PROFILE, 'candidate profile/schema')
    fields = ['variables', 'original_clauses', 'original_literals', 'active_clause_occurrences',
        'unique_recorded_clauses', 'stored_literals', 'proof_additions', 'proof_deletions',
        'effective_deletions', 'missing_deletions', 'ignored_small_deletions',
        'duplicate_literals_normalized', 'duplicate_clause_additions', 'tautology_records_retained',
        'original_proof_bytes', 'retained_original_bytes', 'trailing_dropped_bytes', 'appended_boundary_newline']
    counters = {field: stats[field] for field in fields}
    for field, wanted in counters.items():
        need(candidate_summary[field] == wanted and type(candidate_summary[field]) is type(wanted), 'exact candidate statistic ' + field)
    need(candidate_summary['rat_rup_checked'] is False and candidate_summary['equisatisfiability_asserted'] is False
         and candidate_summary['target_resolution'] is False, 'no unsupported mathematical promotion')
    return counters


def run(args):
    from io import BytesIO
    start = time.monotonic()
    deadline = CommandDeadline(args.seconds, allocation_reason='Complete independent compact Counter replay of431.5MB inputs and exact retained/derivative bytes; reserve60seconds for hashes/shutdown.')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs, controls = {}, []
    def pin(path, wanted=None):
        need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
        path = Path(path).resolve()
        actual = sha(path)
        need(wanted is None or actual == wanted, 'exact artifact/source hash ' + key(path))
        inputs[key(path)] = actual
    try:
        pin(CONTROL_GATE, CONTROL_GATE_SHA)
        gate = read(CONTROL_GATE)
        need(gate['status'] == 'INDEPENDENT_DRAT_RESTART_PREPARATION_V1_PASS', 'fresh independent control gate')
        pin(CONTROL_ORACLE, gate['inputs_sha256'][key(CONTROL_ORACLE)])
        for path, identity in gate['inputs_sha256'].items():
            # Full source/profile/binary closure; controls and checker receipts
            # stay bound to their preserved original identities too.
            pin(ROOT/path, identity)
        pin(Path(__file__))
        module_spec = importlib.util.spec_from_file_location('frozen_independent_control_oracle', CONTROL_ORACLE)
        oracle = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(oracle)
        # Calibrate new compact streaming implementation against all frozen
        # independently checked tiny controls, without executing the parser.
        for label, (formula, proof, exit_code) in oracle.FIXTURES.items():
            if exit_code:
                try:
                    # Preserve valid preceding records so rejection reaches
                    # the malformed record, instead of a prefix mismatch.
                    partial = b'-2 0\n' if proof.startswith(b'-2 0\n') else b''
                    check(BytesIO(formula), BytesIO(proof), BytesIO(), BytesIO(partial), {}, deadline)
                except (ValueError, KeyError):
                    controls.append(dict(label=label, result='REJECT'))
                else:
                    raise ValueError('new checker accepted malformed tiny fixture')
            else:
                expected_cnf, expected_prefix, expected_stats, _ = oracle.expected(formula, proof)
                tiny_summary = dict(schema='DRAT_ACTIVE_MULTISET_PARSER_V1', status='CANDIDATE_RESTART_STATE', profile=PROFILE,
                    rat_rup_checked=False, equisatisfiability_asserted=False, target_resolution=False, **expected_stats)
                actual = check(BytesIO(formula), BytesIO(proof), BytesIO(expected_cnf), BytesIO(expected_prefix), tiny_summary, deadline)
                need(actual == expected_stats, 'new checker calibration counters')
                controls.append(dict(label=label, result='PASS_COMPLETE_STATE'))
        # Observable corrupted derivative/prefix controls on the valid tiny case.
        formula, proof, _ = oracle.FIXTURES['complete_prefix']
        expected_cnf, expected_prefix, expected_stats, _ = oracle.expected(formula, proof)
        tiny_summary = dict(schema='DRAT_ACTIVE_MULTISET_PARSER_V1', status='CANDIDATE_RESTART_STATE', profile=PROFILE,
            rat_rup_checked=False, equisatisfiability_asserted=False, target_resolution=False, **expected_stats)
        corruptions = []
        for name, bad_cnf, bad_prefix, bad_summary in [
            ('changed_clause', expected_cnf.replace(b'-2 0\n', b'2 0\n'), expected_prefix, tiny_summary),
            ('changed_prefix', expected_cnf, b'2 0\n', tiny_summary),
            ('wrong_boundary', expected_cnf, expected_prefix[:-1], tiny_summary),
            ('changed_profile', expected_cnf, expected_prefix, {**tiny_summary, 'profile': 'UNREVIEWED'}),
            ('wrong_count', expected_cnf, expected_prefix, {**tiny_summary, 'proof_additions': 2}),
        ]:
            try:
                check(BytesIO(formula), BytesIO(proof), BytesIO(bad_cnf), BytesIO(bad_prefix), bad_summary, deadline)
            except ValueError:
                corruptions.append(name)
            else:
                raise ValueError('new checker accepted corrupted fixture ' + name)
        if args.calibrate_only:
            result = dict(status='INDEPENDENT_DRAT_RESTART_STREAMING_CALIBRATION_V1_PASS',
                timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
                controls=controls, corrupted_controls_rejected=corruptions,
                command=[sys.executable, *sys.argv], cwd=str(ROOT), target_resolution=False,
                elapsed_seconds=time.monotonic()-start)
            save(out/'summary.json', result)
            print(json.dumps(dict(status=result['status'], summary_sha256=sha(out/'summary.json'))), flush=True)
            return
        need(args.plan and args.plan_sha256 and args.prepared, 'explicit full artifact audit paths and plan identity')
        pin(args.plan, args.plan_sha256)
        plan = read(args.plan)
        need(plan['schema'] == 'DRAT_RESTART_PREPARATION_PLAN_V1' and plan['checker_profile'] == PROFILE, 'frozen actual preparation scope')
        paths = {}
        for role in ['original_cnf', 'original_partial_proof', 'historical_native_receipt', 'encoding_gate']:
            descriptor = plan[role]
            paths[role] = ROOT/descriptor['path']
            pin(paths[role], descriptor['sha256'])
            need(paths[role].stat().st_size == descriptor['bytes'], 'complete exact input length ' + role)
        need(plan['original_cnf']['sha256'] == ORIGINAL_CNF_SHA and plan['original_partial_proof']['sha256'] == ORIGINAL_PROOF_SHA, 'preserved original unrestricted calculation input pins')
        encoding = read(paths['encoding_gate'])
        need(encoding['status'] == 'INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS'
             and encoding['cnf_sha256'] == ORIGINAL_CNF_SHA, 'preserved original unrestricted encoding gate')
        for path, identity in encoding['inputs_sha256'].items():
            pin(ROOT/path, identity)
        prepared = args.prepared.resolve()
        for name in ['manifest.json', 'summary.json', 'parser.receipt.json']:
            pin(prepared/name)
        manifest, producer = read(prepared/'manifest.json'), read(prepared/'summary.json')
        need(manifest['mode'] == producer['mode'] == 'prepare' and manifest['profile'] == PROFILE, 'actual preparation invocation')
        for path, identity in manifest['inputs_sha256'].items():
            pin(ROOT/path, identity)
        need(producer['plan'] == plan and producer['rat_rup_checked'] is False and producer['equisatisfiability_asserted'] is False, 'exact unpromoted preparation plan')
        supervisor_path = ROOT/manifest['supervision']['manifest_path']
        pin(supervisor_path, manifest['supervision']['manifest_sha256'])
        pin(supervisor_path.with_name('summary.json'))
        supervisor_summary = read(supervisor_path.with_name('summary.json'))
        need(supervisor_summary['command_exit_code'] == 0 and supervisor_summary['cleanup']['reaped'] is True
             and supervisor_summary['cleanup']['process_group_live_pids'] == [], 'actual preparation completed and contained')
        receipt = read(prepared/'parser.receipt.json')
        need(receipt['actual_exit_code'] == 0 and receipt['reaped'] is True, 'complete actual parser receipt')
        for stream in ['stdout', 'stderr']:
            pin(ROOT/receipt[stream], receipt[stream+'_sha256'])
        actual_paths = {name: prepared/'candidate'/name for name in ['restart.cnf', 'retained_prefix.drat', 'parser_summary.json']}
        recorded_outputs = {record['path']: record for record in producer['records'][0]['outputs']}
        for path in actual_paths.values():
            descriptor = recorded_outputs[key(path)]
            pin(path, descriptor['sha256'])
            need(path.stat().st_size == descriptor['bytes'], 'complete produced artifact length')
        candidate_summary = read(actual_paths['parser_summary.json'])
        with paths['original_cnf'].open('rb') as formula, paths['original_partial_proof'].open('rb') as proof, \
             actual_paths['restart.cnf'].open('rb') as derivative, actual_paths['retained_prefix.drat'].open('rb') as retained, \
             tqdm(total=paths['original_cnf'].stat().st_size+paths['original_partial_proof'].stat().st_size,
                  desc='independent input replay', unit='B', unit_scale=True, mininterval=5) as progress:
            counters = check(formula, proof, derivative, retained, candidate_summary, deadline, progress)
        # Final source/artifact re-pin binds promotion to immutable checked bytes.
        for path, identity in list(inputs.items()):
            pin(ROOT/path, identity)
        result = dict(schema='INDEPENDENT_DRAT_RESTART_ARTIFACT_AUDIT_V1', status='INDEPENDENT_DRAT_RESTART_ARTIFACT_V1_PASS',
            timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root/structural',
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python_version=platform.python_version(),
            source_commit_at_original_preparation=plan['source_commit'], inputs_sha256=inputs,
            checker_profile=PROFILE, complete_active_multiset_checked=True, complete_prefix_bytes_checked=True,
            variables_unchanged=True, counters=counters, streaming_calibration_controls=controls,
            corrupted_controls_rejected=corruptions, rat_rup_checked=False, equisatisfiability_asserted=False,
            mathematical_exclusions_asserted=0, target_resolution=False,
            scope='Every literal/occurrence of the derivative active multiset and every retained proof byte reconstructed under the exact pinned backward-checker profile; syntactic transformation only.',
            shared_components=['Independent stage1 tiny oracle used only to calibrate a distinct compact streaming representation.', 'CommandDeadline and computation supervisor shared with producer; no parser/producer code imported.'],
            limitations=['Historical partial prefix RAT/RUP validity is not established.', 'No derivative equisatisfiability/model reconstruction witness is asserted.', 'Target UNSAT requires full combined proof replay against the original independently checked encoding.'],
            elapsed_seconds=time.monotonic()-start, artifact_availability='LOCAL_ONLY',
            availability_reason='Complete local raw originals/derivatives; public retrieval not established by this gate.')
        save(out/'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out/'summary.json'), counters=counters)), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), controls=controls, elapsed_seconds=time.monotonic()-start,
             target_resolution=False, unfinished_description='not completed within the allocated budget' if deadline.status()['stop_required'] else None))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--prepared', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--plan-sha256')
    parser.add_argument('--calibrate-only', action='store_true')
    parser.add_argument('--seconds', type=float, required=True)
    run(parser.parse_args())
