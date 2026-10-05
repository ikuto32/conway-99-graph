"""Check the actual registered YAML against the independently accepted copy."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from collections import Counter
import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
COPY = 'acceleration/results/20261004_independent_review/registrar_v20_eleven_copy02'
ACTUAL = 'acceleration/results/20261004_wave44_claim_registration01'
SUP = 'acceleration/results/20261004_wave44_claim_registration_supervision01'
PLAN = 'acceleration/plan_20261004_wave44_claim_registration_v2.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', required=True, type=float)
    ap.add_argument('--out', required=True)
    ap.add_argument('--pins', required=True)
    ap.add_argument('--pins-sha256', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact registered eleven YAML comparison; original independent copy is the checking antecedent, no math replay')
    out = (ROOT / args.out).resolve()
    assert out.is_relative_to(ROOT) and not out.exists()
    out.mkdir(parents=True)
    inputs = {}

    def tick():
        state = deadline.status()
        assert not state['stop_required'] and state['remaining_seconds'] > 20

    def raw(name, expected):
        tick()
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file()
        chunks, h = [], hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                tick()
                chunks.append(block)
                h.update(block)
        assert h.hexdigest() == expected
        inputs[name] = expected
        tick()
        return b''.join(chunks)

    def same(left, right):
        if type(left) is not type(right):
            return False
        if type(left) is dict:
            tick()
            return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
        if type(left) is list:
            tick()
            return len(left) == len(right) and all(same(x, y) for x, y in zip(left, right))
        return left == right

    def save(name, value):
        tick()
        with (out / name).open('x', encoding='utf8') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
        tick()

    try:
        pins = json.loads(raw(args.pins, args.pins_sha256))
        documents = {name: raw(name, identity) for name, identity in pins.items()}
        actual = json.loads(documents[ACTUAL + '/summary.json'])
        terminal = json.loads(documents[SUP + '/summary.json'])
        manifest = json.loads(documents[SUP + '/manifest.json'])
        plan = json.loads(documents[PLAN])
        copied = json.loads(documents[COPY + '/summary.json'])
        assert actual['status'] == 'EXACT_BOUND_SCOPED_CLAIMS_REGISTERED'
        assert actual['claim_records'] == 400 and actual['new_claim_ids'] == copied['projection']['ids']
        assert copied['status'] == 'INDEPENDENT_REGISTRAR_V20_ELEVEN_PROTECTED_COPY_PASS'
        assert copied['write_barriers'] == 1 and copied['precise_corrupted_projection_controls'] == 55
        assert actual['before_ledger_sha256'] == plan['protected_context']['ledger_sha256']
        assert same(actual['command'][1:], plan['worker_argv']) and same(manifest['command'], plan['child_argv'])
        assert terminal['invocation_id'] == manifest['invocation_id']
        assert type(terminal['command_exit_code']) is int and terminal['command_exit_code'] == 0
        assert terminal['error'] is None and terminal['deadline_reached'] is False
        assert terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True
        assert terminal['cleanup']['cleanup_errors'] == []
        assert documents['CLAIMS.yaml'] == documents[ACTUAL + '/CLAIMS.after.yaml']
        assert hashlib.sha256(documents['CLAIMS.yaml']).hexdigest() == actual['ledger_sha256']
        assert hashlib.sha256(documents[ACTUAL + '/CLAIMS.before.yaml']).hexdigest() == actual['before_ledger_sha256']
        expected = yaml.safe_load(documents[COPY + '/eleven_protected_copy/CLAIMS.after.yaml'])
        observed = yaml.safe_load(documents['CLAIMS.yaml'])
        assert len(expected['claims']) == len(observed['claims']) == 400
        # Exactly the declared new timestamp fields may differ between genuine invocations.
        expected['updated_at'] = actual['timestamp']
        for claim in expected['claims'][389:]:
            claim['created_at'] = claim['updated_at'] = actual['timestamp']
        assert same(expected, observed)
        controls = [('bool_integer', True, 1), ('float_integer', 1.0, 1),
                    ('missing_key', {'x': 1}, {}), ('changed_statement', ['a'], ['b'])]
        assert all(not same(x, y) for _, x, y in controls)
        validation = json.loads(documents[ACTUAL + '/validation.json'])
        assert validation['valid'] is True and validation['errors'] == []
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == plan['protected_context']['head']
        raw('.git/index', plan['protected_context']['index_sha256'])
        raw('CLAIMS.yaml', actual['ledger_sha256'])
        save('summary.json', dict(status='EXACT_REGISTERED_ELEVEN_MATCHES_INDEPENDENT_COPY',
            timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root', method='independent_engineering_artifact_check',
            inputs_sha256=inputs, mathematical_replays=0, claim_records=400,
            status_counts=dict(Counter(c['status'] for c in observed['claims'])),
            review_state_counts=dict(Counter(c['review_state'] for c in observed['claims'])),
            target_resolution=observed.get('target', {}).get('resolution', 'UNKNOWN'),
            changed_fields=['root.updated_at', 'eleven new claims.created_at', 'eleven new claims.updated_at'],
            typed_failure_controls=[c[0] for c in controls], schema_hashes_checked=validation['hashes_checked'],
            schema_skipped_count=len(validation['skipped']), command=[sys.executable, *sys.argv],
            shared_components=['Python YAML/SHA/JSON, exact independent protected-copy checker antecedent; no registrar/producer import'],
            limitations='Registry integration only. Prior schema skips and old artifact availability unchanged; no fresh old mathematics, target proof or publication. Actual V20 separately hashed its exact new binding closure.',
            deadline=deadline.status()))
        tick()
        raw('.git/index', plan['protected_context']['index_sha256'])
        raw('CLAIMS.yaml', actual['ledger_sha256'])
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == plan['protected_context']['head']
        tick()
    except BaseException as error:
        with (out / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'error': repr(error), 'pass_summary_not_a_gate': True, 'deadline': deadline.status()}, stream)
        raise


if __name__ == '__main__':
    main()
