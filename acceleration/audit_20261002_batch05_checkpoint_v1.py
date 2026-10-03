"""Independent frozen batch05 identity audit; no solver, encoding reconstruction or proof replay."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'acceleration/results/20261001_user_stop/checkpoint.json': None,
    'acceleration/results/20261001_user_stop/resume_plan.json': 'cb534d093f6273b4f0dc6c1e7f8f3f617c97f8e3a027d46697573cf053155153',
    'acceleration/results/20261001_exact_eight_prefix64_batch05_selection/selection.json': '4a424855302e8f2145e2e6733bdcab892eb253cb5009522ba63c1f5c924f150c',
    'acceleration/results/20261001_exact_eight_prefix64_batch05_consolidated/summary.json': '453fad6c344150b2d9bf7f67da06801e830ae765dd8a2506f20d27bc3f26a7aa',
    'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_cnfs_v3/summary.json': 'c55bb42ff25e44752dbed0f2ba22cf2f6628fb06638b5921f175987951224305',
    'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_object_calibration/summary.json': '2cd273733d3d8e1dce62619a1a4796c6f1955bc64253e80635ff6637a71de02b',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, 'duplicate JSON key ' + name)
        result[name] = value
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs)


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check_cnf(path, variables, clauses):
    """Strict independent streaming DIMACS shape check, not equivalence review."""
    with path.open('rb') as stream:
        require(stream.readline() == f'p cnf {variables} {clauses}\n'.encode(), 'exact header')
        count = 0
        for raw in stream:
            tokens = raw.split()
            require(tokens and tokens[-1] == b'0', 'one terminated clause per line')
            require(all(re.fullmatch(rb'-?[1-9][0-9]*', x) for x in tokens[:-1]), 'literal syntax')
            require(all(1 <= abs(int(x)) <= variables for x in tokens[:-1]), 'literal range')
            count += 1
        require(count == clauses, 'complete CNF clause count')
        return count


def controls(out):
    good = out / 'valid_shape.cnf'
    good.write_bytes(b'p cnf 2 2\n1 2 0\n-1 -2 0\n')
    require(check_cnf(good, 2, 2) == 2, 'positive DIMACS fixture')
    rejected = []
    for name, content in {
        'wrong_header': b'p cnf 2 3\n1 2 0\n-1 -2 0\n',
        'out_of_range': b'p cnf 2 2\n1 3 0\n-1 -2 0\n',
        'missing_zero': b'p cnf 2 2\n1 2\n-1 -2 0\n',
        'extra_clause': b'p cnf 2 2\n1 2 0\n-1 -2 0\n1 0\n',
        'interior_zero': b'p cnf 2 2\n1 0 2 0\n-1 -2 0\n',
    }.items():
        path = out / (name + '.cnf')
        path.write_bytes(content)
        try:
            check_cnf(path, 2, 2)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted corruption ' + name)
    try:
        json.loads('{"x":1,"x":2}', object_pairs_hook=unique_pairs)
    except ValueError:
        rejected.append('duplicate_json_key')
    else:
        raise ValueError('accepted duplicate JSON key')
    return {'positive_shape_control': 'PASS', 'rejected_corruptions': rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scan-full-gate-closure', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    pins = {}
    def pin(path, expected=None, size=None):
        path = path.resolve()
        name = key(path)
        if name not in pins:
            pins[name] = digest(path)
        require(expected is None or pins[name] == expected, 'hash mismatch ' + name)
        require(size is None or path.stat().st_size == size, 'size mismatch ' + name)
        return pins[name]
    try:
        calibration = controls(out)
        for name, expected in PINS.items():
            pin(ROOT / name, expected)
        checkpoint = read(ROOT / list(PINS)[0])
        # No ledger rewrite; authenticate the stop's historical identity only.
        current_ledger = pin(ROOT / 'CLAIMS.yaml')
        require(current_ledger == checkpoint['ledger_sha256'], 'ledger changed from frozen stop')
        for row in checkpoint['registrations'] + checkpoint['completed_literal_batches']:
            pin(ROOT / row['path'], row['sha256'])
        selection = read(ROOT / list(PINS)[2])
        build = read(ROOT / list(PINS)[3])
        enc = read(ROOT / list(PINS)[4])
        obj = read(ROOT / list(PINS)[5])
        ids = selection['ordered_case_ids']
        require(len(ids) == len(set(ids)) == 64, '64 distinct selected cases')
        require(ids == build['selected_case_ids'] == enc['selected_case_ids'] == obj['selected_case_ids'], 'same ordered selection')
        require(build['completed_formulas'] == 64 and build['pending_case_ids'] == [] and build['native_calls'] == 0, 'prepared-only batch')
        require(enc['status'] == 'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS', 'encoding gate status')
        require(obj['status'] == 'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_OBJECT_CALIBRATION_PASS', 'object gate status')
        require(obj['inputs_sha256'][list(PINS)[4]] == PINS[list(PINS)[4]], 'object bound encoding gate')
        checked = {row['case_id']: row for row in enc['checked_cases']}
        require(set(checked) == set(ids), 'checked formula population')
        for report in [enc, obj]:
            require(report['population_size'] == 792 and report['complete_formulas'] == 64, 'literal population')
            require(report['target_resolution'] is False and report['cross_group_column_caps_encoded'] is False and report['residual_D_encoded'] is False, 'scope omissions')
            for name in report['checker_source_closure']:
                pin(ROOT / name, report['inputs_sha256'][name])
                tree = ast.parse((ROOT / name).read_text(encoding='utf-8-sig'))
                for node in ast.walk(tree):
                    names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
                    require(not any(n.startswith(('theory_', 'native_')) for n in names), 'producer/native import in checker closure')
        records = []
        clauses = 0
        for record in tqdm(build['records'], desc='Authenticate frozen cases', unit='case'):
            cid = record['case_id']
            for name, item in record['files'].items():
                pin(ROOT / item['path'], item['sha256'], item['bytes'])
                require(enc['inputs_sha256'][item['path']] == obj['inputs_sha256'][item['path']] == item['sha256'], 'both gates bind case artifact')
            for file_name, field in [('instance.cnf', 'cnf'), ('model.json', 'model'), ('scope.json', 'scope')]:
                item = record['files'][file_name]
                require(checked[cid][field + '_path'] == item['path'] and checked[cid][field + '_sha256'] == item['sha256'], 'checked exact artifact')
            count = check_cnf(ROOT / record['files']['instance.cnf']['path'], record['variables'], record['clauses'])
            scope = read(ROOT / record['files']['scope.json']['path'])
            require(scope['campaign_case_id'] == cid and scope['target_graph'] is False and scope['residual_D_encoded'] is False and scope['cross_group_column_caps_encoded'] is False, 'literal case scope')
            clauses += count
            records.append({'case_id': cid, 'case_index': record['case_index'], 'cnf_path': record['files']['instance.cnf']['path'], 'cnf_sha256': record['files']['instance.cnf']['sha256'], 'variables': record['variables'], 'clauses': count})
            save(out / f'case_{record["case_index"]:04d}.json', records[-1])
        require(clauses == 10532344 == enc['complete_clauses_checked'] == obj['complete_clauses_checked'], 'exact aggregate clauses')
        closure = dict(enc['inputs_sha256'])
        for name, expected in obj['inputs_sha256'].items():
            require(name not in closure or closure[name] == expected, 'consistent gate shared input identity')
            closure[name] = expected
        missing = [name for name in closure if not (ROOT / name).is_file()]
        require(not missing, 'missing gate input artifacts')
        if args.scan_full_gate_closure:
            for name, expected in tqdm(closure.items(), desc='Authenticate historical gate closure', unit='file'):
                pin(ROOT / name, expected)
        pin(Path(__file__))
        save(out / 'summary.json', {
            'status': 'INDEPENDENT_BATCH05_FROZEN_CHECKPOINT_IDENTITY_PASS',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(),
            'verifier': '/root/checkpoint_audit', 'inputs_sha256': pins,
            'selection_path': list(PINS)[2], 'selection_sha256': PINS[list(PINS)[2]],
            'batch_summary_path': list(PINS)[3], 'batch_summary_sha256': PINS[list(PINS)[3]],
            'encoding_gate_path': list(PINS)[4], 'encoding_gate_sha256': PINS[list(PINS)[4]],
            'object_gate_path': list(PINS)[5], 'object_gate_sha256': PINS[list(PINS)[5]],
            'case_records': records, 'checked_cases': len(records), 'complete_clauses_shape_checked': clauses,
            'gate_closure_available_paths': len(closure), 'gate_closure_missing_paths': missing,
            'full_historical_gate_closure_hashes_checked': args.scan_full_gate_closure,
            'historical_gate_hashes_skipped': [] if args.scan_full_gate_closure else sorted(set(closure) - set(pins)),
            'controls': calibration, 'new_solver_calls': 0, 'new_proof_replays': 0,
            'target_resolution': False, 'artifact_availability': 'LOCAL_ONLY',
            'limitations': ['Raw CNF shape and artifact identity are checked; historical encoding reconstruction is not repeated.', 'Historical checkpoint tallies are authenticated saved records, not fresh mathematical proof review.', 'No gate approval transfers to a changed driver/checker; a new engineering calibration is required.', 'Process state is UNKNOWN from this file audit; obtain an actual process observation before launching.'],
            'elapsed_seconds': time.monotonic() - start,
        })
        print(json.dumps({'status': 'PASS', 'cases': len(records), 'clauses': clauses, 'elapsed_seconds': time.monotonic() - start}), flush=True)
    except BaseException as error:
        save(out / 'failure.json', {'error': repr(error), 'timestamp': datetime.now(timezone.utc).isoformat(), 'inputs_sha256': pins})
        raise


if __name__ == '__main__':
    main()
