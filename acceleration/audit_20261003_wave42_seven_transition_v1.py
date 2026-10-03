"""Independent exact seven-paper metadata impact; no registrar/math imports."""
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
SOURCE = 'acceleration/audit_20261003_wave42_seven_transition_v1.py'
SPEC = SOURCE.replace('.py', '_spec.md')
PLAN = 'acceleration/results/20261003_ternary_paper_registration_concrete01/plan.json'
PLAN_SHA = '168ffe16cb09d9e5029e339e28442a5f9d4aa1ef78d51fa9fafe914a97307f7b'
BASE = 'acceleration/results/20261003_wave42_registration01/CLAIMS.after.yaml'
BEFORE_SHA = '9b4e2f19b6ae594f5d5273a56a04cb29311a4b62a070391e687121794e6e6a19'
REG = 'acceleration/results/20261003_wave42_registration02'
SUP = 'acceleration/results/20261003_wave42_registration_supervision02'
PINS = {
    'acceleration/audit_20261002_wave31_transition_v1.py': '5cdb4a68f14d19f97f6326d0fd594e84e8ca732c10225207b9a1b10f29e7b75e',
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


def stamp(value):
    need(type(value) is str, 'TIMESTAMPS')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        raise ValueError('TIMESTAMPS') from None
    need(parsed.tzinfo is not None, 'TIMESTAMPS')


def raw_json(raw):
    def pairs(rows):
        out = {}
        for key, value in rows:
            need(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    def constant(value):
        raise ValueError('NONFINITE_JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def expected_after(before, descriptors, bindings, generated):
    """Separate complete schema projection from pinned raw written bindings."""
    stamp(generated)
    need(len(before['claims']) == 362, 'BASE_POPULATION')
    out = copy.deepcopy(before)
    present = {c['id']: c for c in out['claims']}
    for row, binding in zip(descriptors, bindings):
        cid = row['id']
        need(binding['id'] == cid and type(binding['revision']) is int and binding['revision'] == 1
             and binding['claim_revision'] == 1 and type(binding['claim_revision']) is int,
             'BOUND_ID_REVISION')
        need(cid not in present and binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
             and binding['producer'] != binding['verifier'] and binding['method'] == 'independent_derivation',
             'BOUND_ROLES')
        paths = {row['path']: row['sha256'], binding['report']: binding['report_sha256']}
        for name, identity in binding['inputs_sha256'].items():
            need(name not in paths or paths[name] == identity, 'CLOSURE_CONFLICT')
            paths[name] = identity
        for key in ('artifacts', 'evidence'):
            records = binding.get(key, [])
            need(type(records) is list, 'ORDINARY_PAPER_EVIDENCE')
            for item in records:
                if type(item) is dict and 'path' in item:
                    need(item['path'] not in paths or paths[item['path']] == item['sha256'], 'CLOSURE_CONFLICT')
                    paths[item['path']] = item['sha256']
        aids, hashes = [], {}
        for index, (name, identity) in enumerate(sorted(paths.items())):
            aid = cid.lower() + '-r1-evidence-' + str(index)
            aids.append(aid); hashes[aid] = identity
            out['artifacts'].append(dict(id=aid, path=name, sha256=identity, availability='LOCAL_ONLY',
                retrieval='Exact workspace path; checking reports give raw input and replay commands.',
                unavailable_reason='Immutable publication of this newly bound evidence has not yet been confirmed.'))
        claim = {key: copy.deepcopy(binding[key]) for key in
            ('id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state', 'assumptions', 'limitations')}
        deps = [{key: d[key] for key in ('id', 'revision', 'relation')} for d in binding['dependencies']]
        for dep in deps:
            need(dep['id'] in present and type(dep['revision']) is int
                 and present[dep['id']]['revision'] == dep['revision']
                 and present[dep['id']]['status'] == 'VERIFIED' and present[dep['id']]['review_state'] == 'CLEAR',
                 'ORDERED_DEPENDENCY')
        notes = [{key: d[key] for key in ('id', 'revision', 'reason')} for d in binding['dependencies'] if 'reason' in d]
        scope = binding['scope']
        need(type(scope) is dict and set(scope) == {'description', 'unrestricted_target', 'target_resolution'}
             and scope['unrestricted_target'] is True and scope['target_resolution'] == 'NONE', 'BOUND_SCOPE')
        verification = dict(claim_revision=1, verifier=binding['verifier'], method='independent_derivation',
            command_or_audit=binding['report'], timestamp=binding['verification_timestamp'], outcome='PASS',
            scope=scope['description'], artifact_hashes=hashes, shared_components=binding['shared_components'],
            controls=[json.dumps(binding['controls'], sort_keys=True)], limitations=binding['limitations'])
        manifest = next(aid for aid, (name, _) in zip(aids, sorted(paths.items())) if name == binding['report'])
        claim.update(dependencies=deps, scope=copy.deepcopy(scope), evidence=aids, verification=[verification],
            created_at=generated, updated_at=generated, external_source=None,
            unknowns=dict(external_source='Internal scoped checking; no external or novelty status inferred.',
                premises=json.dumps(binding.get('premise_state', binding.get('mathematical_scope', {})), sort_keys=True),
                dependency_notes=json.dumps(notes, sort_keys=True), original_binding_method=binding['method'],
                original_binding_kind=binding['kind'],
                original_binding_scope='No schema projection; binding uses the schema scope fields directly.'),
            reproducibility=dict(manifest=manifest))
        out['claims'].append(claim); present[cid] = claim
    out['updated_at'] = generated
    return out


def check(after, expected):
    need(type(after) is dict and type(after.get('claims')) is list and len(after['claims']) == 369,
         'AFTER_POPULATION')
    need([c['id'] for c in after['claims']] == [c['id'] for c in expected['claims']], 'AFTER_IDS')
    need(typed(after) == typed(expected), 'ENTIRE_TYPED_PROJECTION')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['calibration', 'check'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seconds', required=True, type=float)
    for name in ('self-sha256', 'spec-sha256', 'expected-head', 'protected-index-sha256'):
        parser.add_argument('--' + name, required=True)
    for name in ('calibration', 'registration-summary', 'runtime-manifest', 'runtime-summary'):
        parser.add_argument('--' + name)
        parser.add_argument('--' + name + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact seven written-paper bookkeeping; 20save; no mathematical replay')
    out = args.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins = {}
    def pin(name, identity):
        need(deadline.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')
        path = (ROOT / name).resolve(); need(path.is_relative_to(ROOT) and path.is_file(), 'PIN_PATH')
        with path.open('rb') as stream:
            value = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(value == identity, 'PIN_IDENTITY:' + name); pins[name] = value
    def read(name):
        return raw_json((ROOT / name).read_bytes())
    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
    try:
        for name, identity in {**PINS, SOURCE: args.self_sha256, SPEC: args.spec_sha256,
                               PLAN: PLAN_SHA, BASE: BEFORE_SHA}.items():
            pin(name, identity)
        plan = read(PLAN); descriptors = plan['bindings_in_dependency_order']
        need(len(descriptors) == 7 and plan['new_registrar_adapters'] == 0, 'SEVEN_ORDINARY_PLAN')
        for name, identity in plan['immutable_declared_inputs_sha256'].items():
            pin(name, identity)
        bindings = []
        for row in descriptors:
            pin(row['path'], row['sha256']); binding = read(row['path']); bindings.append(binding)
            for key in ('id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state',
                        'producer', 'verifier', 'method', 'scope', 'dependencies'):
                need(typed(binding[key]) == typed(row[key]), 'LITERAL_PLAN_BINDING:' + key)
            pin(binding['report'], binding['report_sha256']); report = read(binding['report'])
            need(report['statement'] == binding['statement'] and typed(report['scope']) == typed(binding['scope'])
                 and report['verifier'] == binding['verifier'], 'LITERAL_WRITTEN_REPORT')
            for name, identity in binding['inputs_sha256'].items():
                pin(name, identity)
        before = yaml.load((ROOT / BASE).read_bytes(), Loader=UniqueLoader)
        expected = expected_after(before, descriptors, bindings, '2026-10-03T00:00:00+00:00')
        negatives = []
        if args.mode == 'calibration':
            check(expected, expected)
            mutations = [
                ('population', 'AFTER_POPULATION', lambda x: x['claims'].pop()),
                ('id', 'AFTER_IDS', lambda x: x['claims'][-1].update(id='unbound')),
                ('old_statement', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][0].update(statement='changed')),
                ('new_statement', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1].update(statement='broader')),
                ('scope', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1]['scope'].update(target_resolution='POSITIVE')),
                ('dependency', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1]['dependencies'][0].update(revision=1.0)),
                ('self_review', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1]['verification'][0].update(verifier='/root')),
                ('missing_controls', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1]['verification'][0].update(controls=[])),
                ('missing_evidence', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1]['evidence'].pop()),
                ('old_availability', 'ENTIRE_TYPED_PROJECTION', lambda x: x['artifacts'][0].update(availability='MISSING')),
                ('new_hash', 'ENTIRE_TYPED_PROJECTION', lambda x: x['artifacts'][-1].update(sha256='0'*64)),
                ('extra_artifact', 'ENTIRE_TYPED_PROJECTION', lambda x: x['artifacts'].append({'id': 'unbound'})),
                ('bool_revision', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1].update(revision=True)),
                ('date', 'ENTIRE_TYPED_PROJECTION', lambda x: x['claims'][-1].update(created_at=None)),
                ('target', 'ENTIRE_TYPED_PROJECTION', lambda x: x['target'].update(status='VERIFIED')),
            ]
            for label, stage, mutate in mutations:
                need(deadline.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')
                corrupted = copy.deepcopy(expected); mutate(corrupted)
                try:
                    check(corrupted, expected)
                except ValueError as error:
                    need(str(error) == stage, 'WRONG_NEGATIVE_STAGE:' + label)
                    negatives.append(dict(case=label, expected_stage=stage, actual_stage=str(error)))
                else:
                    raise ValueError('ACCEPTED_CORRUPTION:' + label)
            status = 'INDEPENDENT_WAVE42_SEVEN_TRANSITION_V1_CALIBRATION_PASS'
            actual = expected
        else:
            values = []
            for label in ('calibration', 'registration_summary', 'runtime_manifest', 'runtime_summary'):
                name = getattr(args, label); identity = getattr(args, label + '_sha256')
                need(name is not None and identity is not None, 'CHECK_ARGUMENTS'); pin(name, identity)
                values.append(read(name))
            cal, registration, runtime, terminal = values
            need(cal['status'] == 'INDEPENDENT_WAVE42_SEVEN_TRANSITION_V1_CALIBRATION_PASS'
                 and cal['strict_negative_controls'] == 15 and cal['source_sha256'] == args.self_sha256
                 and all(cal['inputs_sha256'].get(name) == identity for name, identity in pins.items()
                         if name not in (args.calibration, args.registration_summary, args.runtime_manifest, args.runtime_summary)),
                 'CALIBRATION_GATE')
            need(typed(runtime['command']) == typed(plan['child_argv']) and runtime['seconds'] == 180.0
                 and runtime['shutdown_reserve_seconds'] == 30.0, 'RUNTIME_COMMAND')
            need(terminal['invocation_id'] == runtime['invocation_id'] and type(terminal['command_exit_code']) is int
                 and terminal['command_exit_code'] == 0 and terminal['error'] is None
                 and terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True
                 and terminal['cleanup']['cleanup_errors'] == [], 'TERMINAL')
            need(typed(registration['command']) == typed([str(Path(plan['worker_argv'][0])), *plan['worker_argv'][2:]])
                 and registration['source_commit'] == args.expected_head and registration['before_ledger_sha256'] == BEFORE_SHA
                 and registration['new_claim_ids'] == [r['id'] for r in descriptors]
                 and registration['target_resolution'] == 'UNKNOWN' and registration['mathematical_replays'] == 0
                 and registration['editorial_statement_mappings'] == [], 'REGISTRATION_SCOPE')
            stamp(registration['timestamp'])
            expected = expected_after(before, descriptors, bindings, registration['timestamp'])
            pin(REG + '/CLAIMS.before.yaml', BEFORE_SHA)
            pin(REG + '/CLAIMS.after.yaml', registration['ledger_sha256']); pin('CLAIMS.yaml', registration['ledger_sha256'])
            actual = yaml.load((ROOT / REG / 'CLAIMS.after.yaml').read_bytes(), Loader=UniqueLoader)
            check(actual, expected)
            status = 'INDEPENDENT_WAVE42_SEVEN_ACTUAL_TRANSITION_V1_PASS'
        need(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == args.expected_head,
             'CONTEXT_HEAD')
        need(hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest() == args.protected_index_sha256, 'CONTEXT_INDEX')
        save('controls.json', negatives)
        save('summary.json', dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root',
            method='independent_engineering_artifact_check', mode=args.mode, source_sha256=args.self_sha256,
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            strict_negative_controls=len(negatives), claims_before=362, claims_after=len(actual['claims']),
            status_counts=dict(Counter(c['status'] for c in actual['claims'])), new_claim_ids=[r['id'] for r in descriptors],
            mathematical_replays=0, target_resolution='NONE', ledger_mutations=0, deadline=deadline.status(),
            limitations=['Exact bookkeeping/evidence identity only; original independent derivations are not replayed.',
                'Separate complete projection of seven ordinary bindings; no registrar imports or existing math gates reapproval.',
                'All prior typed fields and every new typed field checked, including fifteen generated timestamp fields.',
                'New artifact availability remains LOCAL_ONLY; no world literature or external review inference.']))
    except BaseException as error:
        save('failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
                                 preserved_outputs=True, automatic_retry=False, target_resolution='NONE'))
        raise


if __name__ == '__main__':
    main()
