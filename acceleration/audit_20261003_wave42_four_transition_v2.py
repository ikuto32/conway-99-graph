"""Independent actual four-claim transition against ROOT-checked protected copy.

No registrar imports or mathematical execution. The only ignored differences
from that exact protected copy are the five generated metadata timestamps.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_wave42_four_transition_v2.py'
SPEC = 'acceleration/audit_20261003_wave42_four_transition_v2_spec.md'
BEFORE_SHA = '10b7636dafced40101ccf257d5f80468914f53aa2ee2d3c89db43be268bdcc09'
GOLD_BASE = 'acceleration/results/20261003_independent_review/registrar_v17_engineering01/four_exact_V17/'
GOLD_SHA = 'c0c9fa530f7f184bdb615f67e9a501d5090e22df0dd54c8d8de7853bd7d2cc65'
PLAN = 'acceleration/results/20261003_registrar_v17_registration_prospective01/plan.json'
PLAN_SHA = 'c40cc515d7e0ca72580e83e28a2ef76875d7f0047ea75a10e6addec20bf2cc88'
IDS = ['C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98',
       'C-FIXED-ROOTFOCUSED-SELECTED45369-COMPLETE99-ROOT-RESIDUALS',
       'C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUE-ENERGY-BOUNDS',
       'C-UNRESTRICTED-DEGREE14-TERNARY-ADJACENCY-EXACTNESS']
PINS = {
    'acceleration/audit_20261002_wave31_transition_v1.py': '5cdb4a68f14d19f97f6326d0fd594e84e8ca732c10225207b9a1b10f29e7b75e',
    GOLD_BASE + 'CLAIMS.before.yaml': BEFORE_SHA,
    GOLD_BASE + 'CLAIMS.after.yaml': GOLD_SHA,
    'acceleration/results/20261003_independent_review/registrar_v17_engineering01/summary.json':
        '559be31e327bdfa1ec9606f687f4f8a27924673a18ed59dec7b9b3a3941c14b3',
    'acceleration/results/20261003_independent_review/registrar_v17_engineering_supervision01/summary.json':
        '6527e77d64a34dbf607001f345d4e3007109a43ce00c66dc7854827b7eb28b4c',
    PLAN: PLAN_SHA,
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def timestamp(value):
    need(type(value) is str, 'GENERATED_TIMESTAMPS')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (TypeError, ValueError):
        raise ValueError('GENERATED_TIMESTAMPS') from None
    need(result.tzinfo is not None, 'GENERATED_TIMESTAMPS')


def check(after, gold, generated):
    timestamp(generated)
    need(type(after) is dict and type(after.get('claims')) is list
         and len(after['claims']) == 362, 'EXACT_POPULATION')
    need([c['id'] for c in after['claims'][358:]] == IDS, 'EXACT_NEW_IDS')
    need(after.get('updated_at') == generated, 'GENERATED_TIMESTAMPS')
    normalized = copy.deepcopy(after)
    normalized['updated_at'] = gold['updated_at']
    for actual, expected in zip(normalized['claims'][358:], gold['claims'][358:]):
        need(actual.get('created_at') == generated and actual.get('updated_at') == generated,
             'GENERATED_TIMESTAMPS')
        actual['created_at'] = expected['created_at']
        actual['updated_at'] = expected['updated_at']
    need(typed(normalized) == typed(gold), 'ENTIRE_TYPED_PROTECTED_COPY')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['calibration', 'check'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seconds', required=True, type=float)
    for name in ['self-sha256', 'spec-sha256', 'expected-head', 'protected-index-sha256']:
        parser.add_argument('--' + name, required=True)
    for name in ['registration-summary', 'runtime-manifest', 'runtime-summary', 'calibration']:
        parser.add_argument('--' + name)
        parser.add_argument('--' + name + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact four-claim metadata impact only;20save; no mathematical replay')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins = {}
    def pin(name, expected):
        need(deadline.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(actual == expected, 'INPUT_IDENTITY:' + name)
        pins[name] = actual
    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
    def read(name):
        return json.loads((ROOT / name).read_bytes())
    try:
        pin(SOURCE, args.self_sha256); pin(SPEC, args.spec_sha256)
        for name, expected in PINS.items():
            pin(name, expected)
        need(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
             == args.expected_head, 'CONTEXT_HEAD')
        need(hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest()
             == args.protected_index_sha256, 'CONTEXT_INDEX')
        before = yaml.load((ROOT / (GOLD_BASE + 'CLAIMS.before.yaml')).read_bytes(), Loader=UniqueLoader)
        gold = yaml.load((ROOT / (GOLD_BASE + 'CLAIMS.after.yaml')).read_bytes(), Loader=UniqueLoader)
        need(len(before['claims']) == 358 and typed(gold['claims'][:358]) == typed(before['claims'])
             and typed(gold['target']) == typed(before['target']), 'GOLD_BASELINE')
        check(gold, gold, gold['updated_at'])
        negatives = []
        if args.mode == 'calibration':
            mutations = [
                ('population', 'EXACT_POPULATION', lambda x: x['claims'].pop()),
                ('id', 'EXACT_NEW_IDS', lambda x: x['claims'][-1].update(id='unbound')),
                ('old_statement', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][0].update(statement='changed')),
                ('new_statement', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1].update(statement='broader')),
                ('scope', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1]['scope'].update(target_resolution='POSITIVE')),
                ('status', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1].update(status='CANDIDATE')),
                ('old_availability', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['artifacts'][0].update(availability='MISSING')),
                ('new_artifact_hash', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['artifacts'][-1].update(sha256='0'*64)),
                ('extra_artifact', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['artifacts'].append({'id':'unbound'})),
                ('dependency', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1]['dependencies'].append({'id':'unbound'})),
                ('boolean_revision', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1].update(revision=True)),
                ('float_revision', 'ENTIRE_TYPED_PROTECTED_COPY', lambda x: x['claims'][-1].update(revision=1.0)),
                ('date', 'GENERATED_TIMESTAMPS', lambda x: x['claims'][-1].update(created_at=None)),
                ('ledger_date', 'GENERATED_TIMESTAMPS', lambda x: x.update(updated_at='invalid')),
            ]
            for label, stage, mutate in mutations:
                corrupted = copy.deepcopy(gold); mutate(corrupted)
                try:
                    check(corrupted, gold, gold['updated_at'])
                except ValueError as error:
                    need(str(error) == stage, 'CONTROL_WRONG_STAGE:' + label)
                    negatives.append(dict(label=label, expected_stage=stage, actual_stage=str(error), outcome='REJECTED'))
                else:
                    raise ValueError('CONTROL_ACCEPTED:' + label)
            actual = gold
            status = 'INDEPENDENT_WAVE42_FOUR_TRANSITION_V2_CALIBRATION_PASS'
        else:
            for name in ['registration-summary', 'runtime-manifest', 'runtime-summary', 'calibration']:
                need(getattr(args, name.replace('-', '_')) is not None, 'CHECK_ARGUMENTS')
                pin(getattr(args, name.replace('-', '_')), getattr(args, name.replace('-', '_') + '_sha256'))
            report, runtime, terminal, cal = [read(getattr(args, name.replace('-', '_'))) for name in
                                             ['registration-summary', 'runtime-manifest', 'runtime-summary', 'calibration']]
            need(cal['status'] == 'INDEPENDENT_WAVE42_FOUR_TRANSITION_V2_CALIBRATION_PASS'
                 and cal['negative_count'] == 14 and cal['source_sha256'] == args.self_sha256, 'CALIBRATION_GATE')
            plan = read(PLAN)
            need(typed(runtime['command']) == typed(plan['child_argv'])
                 and runtime['source_sha256'] == PINS['acceleration/run_compute_command.py'], 'EXACT_RUNTIME_COMMAND')
            need(terminal['invocation_id'] == runtime['invocation_id'] and type(terminal['command_exit_code']) is int
                 and terminal['command_exit_code'] == 0 and terminal['error'] is None
                 and terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True
                 and terminal['cleanup']['cleanup_errors'] == [], 'ACTUAL_TERMINAL')
            expected_command = [plan['worker_argv'][0], *plan['worker_argv'][2:]]
            expected_command[0] = str(Path(expected_command[0]))
            need(typed(report['command']) == typed(expected_command) and report['source_commit'] == args.expected_head
                 and report['before_ledger_sha256'] == BEFORE_SHA and report['new_claim_ids'] == IDS
                 and report['target_resolution'] == 'UNKNOWN' and report['mathematical_replays'] == 0, 'ACTUAL_REGISTRATION_SCOPE')
            directory = Path(args.registration_summary).parent
            pin((directory / 'CLAIMS.before.yaml').as_posix(), BEFORE_SHA)
            pin((directory / 'CLAIMS.after.yaml').as_posix(), report['ledger_sha256'])
            pin('CLAIMS.yaml', report['ledger_sha256'])
            actual = yaml.load((ROOT / directory / 'CLAIMS.after.yaml').read_bytes(), Loader=UniqueLoader)
            check(actual, gold, report['timestamp'])
            status = 'INDEPENDENT_WAVE42_FOUR_ACTUAL_TRANSITION_V2_PASS'
        save('controls.json', negatives)
        result = dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=args.self_sha256,
            verifier='/root', method='independent_engineering_artifact_check', mode=args.mode,
            source_context=args.expected_head, command=[sys.executable, *sys.argv], cwd=str(ROOT),
            python=platform.python_version(), inputs_sha256=pins, negative_count=len(negatives),
            claims_before=358, claims_after=362, status_counts=dict(Counter(c['status'] for c in actual['claims'])),
            new_claim_ids=IDS, mathematical_replays=0, target_resolution='NONE', ledger_mutations=0,
            limitations=['Metadata identity check only; no mathematical approval from schema or copied-record equality.',
                'Uses the exact independently ROOT-reviewed protected copy as a finite oracle; every other field and type compared.',
                'Only five generated timestamp locations may differ, all must equal the actual registration timestamp.'])
        result['deadline'] = deadline.status(); save('summary.json', result)
        print(json.dumps({k: result[k] for k in ['status', 'negative_count', 'claims_after']}))
    except BaseException as error:
        save('failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), target_resolution='NONE'))
        raise


if __name__ == '__main__':
    main()
