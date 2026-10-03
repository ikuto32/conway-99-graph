"""Independent Counter/byte/truth-table audit of frozen restart parser controls.

No parser/producer module imports. The shared, separately frozen DRAT checker
authentication/replay path is disclosed. Run in a contained Windows invocation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'acceleration/results/20261002_drat_restart_controls01'
PROFILE = 'PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1'
PINS = {
 'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/prepare_20261002_drat_restart_v1.py': '5a212bef0eadede50ee9857d6b1b1d328027a17dea967818688ec103947f7554',
 'acceleration/drat_restart_20261002_v1.cpp': 'fded432e0e7b694b9cab7db0b41cea923342abbc68939878ae726eadb38c144f',
 'acceleration/prepare_20261002_drat_restart_v1_spec.md': '03e5742072cba3b80f34553b990ac4213611d5025b9b19dbca9a61bd550afce5',
 'acceleration/native_20261002_exact_eight_budget_v1.py': 'df59431bb284bc9f8b247c6949555873d5e8f8d474a2210874870127416c6d36',
 'acceleration/native_20261002_exact_eight_budget_v1_spec.md': '090a22efaa2e29267f00d7e20068310e4519b84bc8372b82f2dfe18ced5efec7',
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/native_budget_env_v1/pyproject.toml': '96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
 'acceleration/native_budget_env_v1/uv.lock': '54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
 'build/rook-drat-checker/drat-trim.c': '82835512d4eda7dee1e0e3f610a0672fa1d216ea91246bcb576022020fe18f4c',
 'acceleration/results/20261002_drat_restart_build02/drat_restart_parser': '71bd0a9fdf9f5afd0f0ebff07d73d721bbd002340db6b90a4870bbb5c44f21db',
 'acceleration/results/20261002_drat_restart_build02/build_manifest.json': '9c7ad5b77858094ad96639527ab73a06669520f65f75d84dc4151015c56166e0',
 'acceleration/audit_20261002_policy_drat_core_v2.py': '540d10ae8d14cbbf53e3da678057a8612218784d956467ac2f4d32ce0c0206e1',
}
# Exactly the independently requested frozen controls, not inferred outputs.
UNSAT = b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
MULTI = b'p cnf 3 4\n1 2 0\n2 1 0\n3 0\n-1 -2 0\n'
FIXTURES = {
 'complete_prefix': (UNSAT, b'-2 0\n', 0),
 'multiset_delete_one': (MULTI, b'd 1 2 0\n1 2 0\nd 2 1 0\nd 3 0\nd 3 0\nd -3 0\nd 1 -2 0\n2 2 1 0\n', 0),
 'truncated_tail': (UNSAT, b'-2 0\n1', 0),
 'zero_without_newline': (UNSAT, b'-2 0', 0),
 'ignored_unit_delete': (UNSAT, b'-2 0\nd -2 0\n', 0),
 'missing_nonunit_delete': (UNSAT, b'd 1 -2 -1 0\n', 0),
 'internal_unterminated': (UNSAT, b'-2 0\n1\n', 2),
 'malformed_integer': (UNSAT, b'z 0\n', 2),
 'extra_variable': (UNSAT, b'3 0\n', 2),
 'extra_token_after_zero': (UNSAT, b'-2 0 1\n', 2),
 'extra_token_after_zero_EOF': (UNSAT, b'-2 0 1', 2),
 'malformed_integer_EOF': (UNSAT, b'garbage', 2),
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def integers(raw, variables, terminated=True):
    tokens = raw.split()
    need(all(re.fullmatch(rb'-?[0-9]+', token) for token in tokens), 'integer syntax')
    values = [int(token) for token in tokens]
    need(all(-2147483648 < value <= 2147483647 and abs(value) <= variables for value in values), 'literal universe')
    if terminated:
        need(values and values[-1] == 0 and 0 not in values[:-1], 'unique final zero')
        values.pop()
    else:
        need(0 not in values, 'zero before unfinished final record')
    return values


def cnf(raw):
    lines = raw.splitlines()
    header = lines.pop(0).split()
    need(len(header) == 4 and header[:2] == [b'p', b'cnf'], 'DIMACS header')
    n, declared = map(int, header[2:])
    rows = [integers(line, n) for line in lines if line and not line.startswith(b'c')]
    need(len(rows) == declared, 'DIMACS clause count')
    return n, rows


def expected(cnf_bytes, proof_bytes):
    n, rows = cnf(cnf_bytes)
    count, order, counts = Counter(), [], Counter()
    counts['variables'] = n
    counts['original_clauses'] = len(rows)
    counts['original_proof_bytes'] = len(proof_bytes)
    counts['appended_boundary_newline'] = False
    def add(values):
        normalized = tuple(sorted(set(values)))
        counts['duplicate_literals_normalized'] += len(values) - len(normalized)
        counts['tautology_records_retained'] += any(-literal in normalized for literal in normalized)
        if normalized in order:
            counts['duplicate_clause_additions'] += 1
        else:
            order.append(normalized)
        count[normalized] += 1
        return normalized
    for values in rows:
        counts['original_literals'] += len(set(values))
        add(values)
    retained = bytearray()
    records = proof_bytes.splitlines(keepends=True)
    for index, record in enumerate(records):
        terminated_line = record.endswith(b'\n')
        line = record[:-1] if terminated_line else record
        raw = line.strip()
        if not raw or raw.startswith(b'c'):
            retained.extend(line + b'\n')
            counts['retained_original_bytes'] += len(record)
            counts['appended_boundary_newline'] = not terminated_line
            continue
        deletion = raw.startswith(b'd')
        if deletion:
            need(raw == b'd' or len(raw) > 1 and raw[1:2].isspace(), 'deletion keyword')
            raw = raw[1:].strip()
        if not terminated_line and (not raw or raw.split()[-1] != b'0'):
            integers(raw, n, terminated=False)
            need(index + 1 == len(records), 'only final record may truncate')
            counts['trailing_dropped_bytes'] = len(record)
            break
        values = integers(raw, n)
        if deletion:
            normalized = tuple(sorted(set(values)))
            counts['duplicate_literals_normalized'] += len(values) - len(normalized)
            counts['tautology_records_retained'] += any(-literal in normalized for literal in normalized)
            counts['proof_deletions'] += 1
            if len(normalized) <= 1:
                counts['ignored_small_deletions'] += 1
            elif count[normalized]:
                count[normalized] -= 1
                counts['effective_deletions'] += 1
            else:
                counts['missing_deletions'] += 1
        else:
            add(values)
            counts['proof_additions'] += 1
        retained.extend(line + b'\n')
        counts['retained_original_bytes'] += len(record)
        counts['appended_boundary_newline'] = not terminated_line
    counts['active_clause_occurrences'] = sum(count.values())
    counts['unique_recorded_clauses'] = len(order)
    counts['stored_literals'] = sum(map(len, order))
    # Include all counters even when zero, and literal false for boundary flag.
    fields = ['variables', 'original_clauses', 'original_literals', 'active_clause_occurrences',
        'unique_recorded_clauses', 'stored_literals', 'proof_additions', 'proof_deletions',
        'effective_deletions', 'missing_deletions', 'ignored_small_deletions',
        'duplicate_literals_normalized', 'duplicate_clause_additions', 'tautology_records_retained',
        'original_proof_bytes', 'retained_original_bytes', 'trailing_dropped_bytes', 'appended_boundary_newline']
    stats = {field: counts[field] for field in fields}
    derivative = f'p cnf {n} {sum(count.values())}\n'.encode()
    derivative += b''.join((' '.join(map(str, row)) + (' ' if row else '') + '0\n').encode()
                          for row in order for _ in range(count[row]))
    return derivative, bytes(retained), stats, count


def validate(derivative, prefix, summary, oracle):
    wanted, retained, counters, active = oracle
    need(derivative == wanted, 'all deterministic derivative bytes')
    n, clauses = cnf(derivative)
    need(Counter(tuple(sorted(set(row))) for row in clauses) == +active, 'complete active multiset')
    need(prefix == retained, 'all retained bytes and pivot ordering')
    need(summary['schema'] == 'DRAT_ACTIVE_MULTISET_PARSER_V1' and
        summary['status'] == 'CANDIDATE_RESTART_STATE' and summary['profile'] == PROFILE,
        'declared profile/schema')
    for field, value in counters.items():
        need(summary[field] == value and type(summary[field]) is type(value), 'independent counter ' + field)
    need(summary['rat_rup_checked'] is False and summary['equisatisfiability_asserted'] is False
         and summary['target_resolution'] is False, 'no unsupported promotion')
    return n, clauses


def models(n, rows):
    return [bits for bits in range(1 << n)
            if all(any(bool(bits & 1 << (abs(literal)-1)) == (literal > 0) for literal in row) for row in rows)]


def run(args):
    start = time.monotonic()
    deadline = CommandDeadline(args.seconds, allocation_reason='Twelve tiny syntax/multiset controls plus authenticated exact DRAT replays; no scientific solver.')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs, tests, corruptions = {}, [], []
    def pin(path, wanted=None):
        path = Path(path).resolve()
        deadline.status()
        actual = sha(path)
        need(wanted is None or actual == wanted, 'unchanged input identity ' + key(path))
        inputs[key(path)] = actual
    try:
        for path, identity in PINS.items():
            pin(ROOT/path, identity)
        pin(Path(__file__))
        for name in ['manifest.json', 'summary.json']:
            pin(CONTROL/name)
        manifest, summary = read(CONTROL/'manifest.json'), read(CONTROL/'summary.json')
        need(manifest['mode'] == summary['mode'] == 'controls' and manifest['profile'] == PROFILE, 'frozen controls invocation')
        for path, identity in manifest['inputs_sha256'].items():
            need(PINS.get(path) == identity, 'complete declared code/binary closure matches frozen review')
        need(len(manifest['inputs_sha256']) == 12, 'all twelve producer closure pins')
        need(summary['inputs_sha256'] == manifest['inputs_sha256'], 'consistent producer closure')
        supervision = ROOT/manifest['supervision']['manifest_path']
        pin(supervision, manifest['supervision']['manifest_sha256'])
        pin(supervision.with_name('summary.json'))
        cleanup = read(supervision.with_name('summary.json'))
        need(cleanup['command_exit_code'] == 0 and cleanup['cleanup']['reaped'] is True and
             cleanup['cleanup']['process_group_live_pids'] == [], 'observed completed contained controls')
        build = read(ROOT/'acceleration/results/20261002_drat_restart_build02/build_manifest.json')
        need(build['schema'] == 'DRAT_RESTART_PARSER_BUILD_V1' and build['source_cpp_sha256'] == PINS['acceleration/drat_restart_20261002_v1.cpp']
             and build['parser_sha256'] == PINS[build['parser_path']] and build['compile_receipt']['actual_exit_code'] == 0,
             'preserved successful exact source/binary build receipt')
        for stream in ['stdout', 'stderr']:
            pin(ROOT/build['compile_receipt'][stream], build['compile_receipt'][stream+'_sha256'])
        need(build['command'][1:6] == ['-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror'], 'exact build flags')
        need(build['compiler_sha256'] == '1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
             and build['compiler_version_stdout'].startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'), 'pinned observed compiler provenance')
        records = {row['label']: row for row in summary['records']}
        need(len(records) == len(summary['records']) == 12 and set(records) == set(FIXTURES), 'complete declared twelve controls')
        positive = {}
        for label, (formula, proof, expected_exit) in FIXTURES.items():
            folder, row = CONTROL/label, records[label]
            for path, identity in [(folder/'original.cnf', row['cnf_sha256']), (folder/'original_prefix.drat', row['proof_sha256'])]:
                pin(path, identity)
            need((folder/'original.cnf').read_bytes() == formula and (folder/'original_prefix.drat').read_bytes() == proof, 'raw frozen fixture ' + label)
            receipt = read(folder/'parser.receipt.json')
            pin(folder/'parser.receipt.json')
            need(receipt == row['parser_receipt'] and receipt['actual_exit_code'] == expected_exit and receipt['reaped'] is True, 'raw completed control receipt')
            for stream in ['stdout', 'stderr']:
                pin(ROOT/receipt[stream], receipt[stream+'_sha256'])
            try:
                oracle = expected(formula, proof)
            except ValueError as error:
                need(expected_exit == 2, 'oracle rejects only failed parse')
                need(not (folder/'candidate/parser_summary.json').exists(), 'failed control not promoted')
                pin(folder/'candidate/parser_failure.txt')
                tests.append(dict(label=label, independent_outcome='REJECT', parser_exit=expected_exit, reason=str(error)))
                continue
            need(expected_exit == 0, 'oracle accepts only successful parse')
            for name in ['restart.cnf', 'retained_prefix.drat', 'parser_summary.json']:
                pin(folder/'candidate'/name)
            raw_cnf = (folder/'candidate/restart.cnf').read_bytes()
            raw_proof = (folder/'candidate/retained_prefix.drat').read_bytes()
            raw_summary = read(folder/'candidate/parser_summary.json')
            n, rows = validate(raw_cnf, raw_proof, raw_summary, oracle)
            original_n, original_rows = cnf(formula)
            original_models, derivative_models = models(original_n, original_rows), models(n, rows)
            need(derivative_models == models(n, [list(item) for item in oracle[3].elements()]), 'full independent truth table')
            tests.append(dict(label=label, independent_outcome='PASS_COMPLETE_STATE', parser_exit=0,
                variables=n, clause_occurrences=len(rows), models_original=original_models, models_derivative=derivative_models,
                counters=oracle[2]))
            positive[label] = (raw_cnf, raw_proof, raw_summary, oracle)
        def rejects(label, action):
            try:
                action()
            except (ValueError, KeyError, IndexError):
                corruptions.append(label)
            else:
                raise ValueError('corrupted control accepted ' + label)
        raw_cnf, raw_proof, raw_summary, oracle = positive['complete_prefix']
        rejects('changed_derivative_clause', lambda: validate(raw_cnf.replace(b'-2 0\n', b'2 0\n'), raw_proof, raw_summary, oracle))
        rejects('removed_live_occurrence', lambda: validate(raw_cnf.replace(b'-2 0\n', b'', 1), raw_proof, raw_summary, oracle))
        rejects('wrong_variable_universe', lambda: validate(raw_cnf.replace(b'p cnf 2', b'p cnf 3'), raw_proof, raw_summary, oracle))
        rejects('changed_prefix_pivot', lambda: validate(raw_cnf, b'2 0\n', raw_summary, oracle))
        rejects('wrong_prefix_boundary', lambda: validate(raw_cnf, raw_proof[:-1], raw_summary, oracle))
        rejects('changed_profile', lambda: validate(raw_cnf, raw_proof, {**raw_summary, 'profile': 'UNREVIEWED'}, oracle))
        rejects('wrong_counter', lambda: validate(raw_cnf, raw_proof, {**raw_summary, 'proof_additions': 2}, oracle))
        rejects('unsupported_equivalence', lambda: validate(raw_cnf, raw_proof, {**raw_summary, 'equisatisfiability_asserted': True}, oracle))
        raw_cnf, raw_proof, raw_summary, oracle = positive['multiset_delete_one']
        rejects('delete_all_duplicate_copies', lambda: validate(raw_cnf.replace(b'1 2 0\n', b''), raw_proof, raw_summary, oracle))
        rejects('wrong_unit_deletion_profile', lambda: validate(raw_cnf.replace(b'3 0\n', b''), raw_proof, raw_summary, oracle))
        rejects('changed_source_identity', lambda: need(hashlib.sha256((ROOT/'acceleration/drat_restart_20261002_v1.cpp').read_bytes() + b' ').hexdigest() == PINS['acceleration/drat_restart_20261002_v1.cpp'], 'mutated source'))
        core_path = ROOT/'acceleration/audit_20261002_policy_drat_core_v2.py'
        module_spec = importlib.util.spec_from_file_location('frozen_drat_core_v2', core_path)
        core = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(core)
        provenance = core.authenticate(pin)
        # Preserve original suffix bytes; append only to the audited derivative
        # prefix. A valid prefix alone is sufficient on this UNSAT fixture.
        for name, data in [('tiny_valid_suffix.drat', b'1 0\n0\n'), ('tiny_wrong_suffix.drat', b'3 0\n0\n')]:
            pin(CONTROL/name)
            need((CONTROL/name).read_bytes() == data, 'raw suffix fixture')
        cp = CONTROL/'complete_prefix'
        prefix = (cp/'candidate/retained_prefix.drat').read_bytes()
        valid = (CONTROL/'tiny_valid_suffix.drat').read_bytes()
        wrong = (CONTROL/'tiny_wrong_suffix.drat').read_bytes()
        local = {'combined_valid.drat': prefix + valid, 'combined_wrong_after_sufficient_prefix.drat': prefix + wrong,
                 'empty_only.drat': b'0\n', 'changed_sat.cnf': b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n'}
        for name, data in local.items():
            (out/name).write_bytes(data)
        need(models(*cnf((out/'changed_sat.cnf').read_bytes())) == [3], 'changed SAT input exhaustive truth table')
        replays = []
        for label, formula, proof, accept in [
            ('suffix_on_restart', cp/'candidate/restart.cnf', CONTROL/'tiny_valid_suffix.drat', True),
            ('combined_on_original', cp/'original.cnf', out/'combined_valid.drat', True),
            ('sufficient_prefix_alone', cp/'original.cnf', cp/'candidate/retained_prefix.drat', True),
            ('wrong_suffix_without_prefix', cp/'original.cnf', CONTROL/'tiny_wrong_suffix.drat', False),
            ('missing_reasoning_on_original', cp/'original.cnf', out/'empty_only.drat', False),
            ('changed_SAT_original', out/'changed_sat.cnf', out/'combined_valid.drat', False),
            ('wrong_suffix_after_sufficient_prefix', cp/'original.cnf', out/'combined_wrong_after_sufficient_prefix.drat', True),
            ('wrong_suffix_on_UP_UNSAT_restart', cp/'candidate/restart.cnf', CONTROL/'tiny_wrong_suffix.drat', True),
        ]:
            replays.append(core.replay(label, formula, proof, out, deadline, accept))
        result = dict(schema='INDEPENDENT_DRAT_RESTART_PREPARATION_AUDIT_V1',
            status='INDEPENDENT_DRAT_RESTART_PREPARATION_V1_PASS',
            timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root/structural',
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python_version=platform.python_version(),
            inputs_sha256=inputs, checker_profile=PROFILE, controls=tests, corrupted_state_controls_rejected=corruptions,
            complete_control_active_multisets_checked=True, complete_control_prefix_bytes_checked=True,
            complete_tiny_truth_tables_checked=True, raw_drat_replays=replays, checker_provenance=provenance,
            scope='Frozen parser/code/profile/binary engineering calibration and twelve tiny raw controls only; no actual large derivative reviewed.',
            shared_components=['CommandDeadline and supervisor policy are shared.', 'Frozen independent core v2 authenticates and invokes the preserved DRAT-trim checker; no producer/parser module imported.', 'MSVC checker/compiler/runtime and g++ parser build receipts remain trusted.'],
            deviations=['The supplied wrong suffix does not falsify proof checking after this already-sufficient valid prefix, or on an initial-UP-UNSAT derivative. Negative proof controls are applied to the original without a valid prefix and to a changed SAT original; actual acceptance of the masked cases is recorded.'],
            rat_rup_checked=False, rat_rup_checked_reason='Only tiny complete proofs checked; the substantial historical prefix is not checked.',
            equisatisfiability_asserted=False, mathematical_exclusions_asserted=0, target_resolution=False,
            elapsed_seconds=time.monotonic()-start,
            outputs_sha256={key(path): sha(path) for path in out.iterdir() if path.is_file()},
            limitations=['Finite controls and a source review are not a formal proof of parser correctness.', 'Substantial artifacts require a separate complete independent Counter/byte audit.', 'An eventual UNSAT restart requires full combined-proof replay against the original independently encoded CNF.'])
        save(out/'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out/'summary.json'))), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), tests=tests, corruptions=corruptions, elapsed_seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    run(parser.parse_args())
