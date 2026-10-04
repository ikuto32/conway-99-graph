"""SOURCE_ONLY V22 projection controls, protected main interception and post check.

Structural authored both the registrar adapter and this distinct projection.
Root execution/review and Checkpoint source review are separate engineering
checks; this source does not reverify mathematical claims.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_registrar_v22_transition_v1.py'
SPEC = 'acceleration/audit_20261004_registrar_v22_transition_v1_spec.md'
SUBJECT = 'acceleration/register_20261004_bound_claims_v22.py'
DESCRIPTOR = 'acceleration/proposal_20261004_wave45_eighteen_bound_claims_v2.json'
SUP = 'acceleration/run_compute_command_v2.py'
PINS = {
    SUBJECT: 'cbd034064a01511a87cbf62945cce35490cebc22ca05ae6c6253302e5abaf327',
    DESCRIPTOR: 'f79290306199ce59662fe914a2d207d0d2bd252e189481dc10fa2cc042d9a3af',
    SUP: '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'docs/claims.schema.json': '0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    'acceleration/calibrate_20261004_registrar_v22_helpers_v1.py': '313849e2e4ad50b8d7bd98928c8dcdbbe620421343cbdb9fe2f484e2598b64f6',
    'acceleration/calibrate_20261004_registrar_v22_helpers_v1_spec.md': '4936d138a1a5e3473ecedbda7ff19e529b1745c4b9cc990ff1f0dddf8cbe2925',
    'acceleration/plan_20261004_registrar_v22_author_helpers_v1.json': 'b4ab5338bfcde83298e5f4481524753deac081de3cc5074cef3586a9c2fd4e42',
}
REFUTED = 'C-FIXED-COUNT-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE'
QUALIFIED = 'C-FIXED-COUNT-NONTRIVIAL-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE'
RETRIEVAL = 'Exact workspace path; checking reports give raw input and replay commands.'
UNAVAILABLE = 'Immutable publication of this newly bound evidence has not yet been confirmed.'


class Reject(ValueError):
    pass


class InterceptedWrite(RuntimeError):
    pass


def need(ok, stage):
    if not ok:
        raise Reject(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def jd(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


def pairs(rows):
    value = {}
    for key, item in rows:
        need(key not in value, 'JSON_DUPLICATE')
        value[key] = item
    return value


def raw_json(data):
    def bad_constant(_):
        raise Reject('JSON_NONFINITE')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad_constant)


class LedgerLoader(yaml.SafeLoader):
    pass


LedgerLoader.yaml_implicit_resolvers = {
    key: [(tag, expr) for tag, expr in values if tag != 'tag:yaml.org,2002:timestamp']
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def yaml_mapping(loader, node, deep=False):
    rows = loader.construct_pairs(node, deep=True)
    result = {}
    for key, value in rows:
        need(key not in result, 'YAML_DUPLICATE')
        result[key] = value
    return result


LedgerLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping)


def ledger(data):
    value = yaml.load(data, Loader=LedgerLoader)
    need(type(value) is dict, 'LEDGER_OBJECT')
    return value


def stamp(value):
    need(type(value) is str, 'TIMESTAMP_TYPE')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise Reject('TIMESTAMP_VALUE') from error
    need(parsed.tzinfo is not None, 'TIMESTAMP_ZONE')


def merge(target, path, identity):
    need(type(path) is str and type(identity) is str and re.fullmatch('[0-9a-f]{64}', identity) is not None, 'EVIDENCE_TYPE')
    need(path not in target or target[path] == identity, 'EVIDENCE_CONFLICT')
    target[path] = identity


def metadata_evidence(descriptor):
    result = {DESCRIPTOR: PINS[DESCRIPTOR]}
    for row in descriptor['root_existing_metadata_reviews']:
        need(type(row) is dict and set(row) == {'path', 'sha256'}, 'REVIEW_REFERENCE')
        merge(result, row['path'], row['sha256'])
    proof = descriptor['original_generic_refutation_contract']['proof']
    need(type(proof) is dict and set(proof) == {'path', 'sha256'}, 'PROOF_REFERENCE')
    merge(result, proof['path'], proof['sha256'])
    return result


def scope_and_dependencies(binding, row, preceding):
    original = binding['scope']
    text = original['description'] if 'description' in original else original['population']
    flag = original['unrestricted_target'] if 'unrestricted_target' in original else original['unrestricted']
    need(type(text) is str and type(flag) is bool and original['target_resolution'] == 'NONE', 'SCOPE_TYPE')
    scope = dict(description=text, unrestricted_target=flag, target_resolution='NONE')
    need(same(scope, row['proposed_three_key_scope']), 'SCOPE_PROJECTION')
    dependencies = []
    for dep in binding['dependencies']:
        need(type(dep) is dict and set(dep) <= {'id', 'revision', 'relation', 'type', 'reason'}
             and ('relation' in dep) != ('type' in dep) and type(dep['revision']) is int
             and dep['revision'] == 1, 'DEPENDENCY_TYPE')
        relation = dep['relation'] if 'relation' in dep else dep['type']
        need(relation == 'uses_result', 'DEPENDENCY_RELATION')
        matches = [c for c in preceding if c['id'] == dep['id']]
        need(len(matches) == 1 and type(matches[0]['revision']) is int
             and matches[0]['revision'] == dep['revision'] and matches[0]['status'] == 'VERIFIED'
             and matches[0]['review_state'] == 'CLEAR', 'DEPENDENCY_PRECEDING')
        projected = dict(id=dep['id'], revision=dep['revision'], relation=relation)
        if 'reason' in dep:
            need(type(dep['reason']) is str, 'DEPENDENCY_REASON')
            projected['reason'] = dep['reason']
        dependencies.append(projected)
    return scope, dependencies


def evidence(binding, row, extra):
    result = dict(extra)
    merge(result, row['binding']['path'], row['binding']['sha256'])
    merge(result, binding['report'], binding['report_sha256'])
    need(type(binding.get('inputs_sha256', {})) is dict, 'INPUT_MAP_TYPE')
    for path, identity in binding.get('inputs_sha256', {}).items():
        merge(result, path, identity)
    for collection in ('artifacts', 'evidence'):
        items = binding.get(collection, [])
        if type(items) is dict:
            for key, path in items.items():
                if not key.endswith('_sha256'):
                    need(key + '_sha256' in items, 'PAIRED_EVIDENCE')
                    merge(result, path, items[key + '_sha256'])
        else:
            need(type(items) is list, 'EVIDENCE_COLLECTION')
            for item in items:
                if type(item) is dict and 'path' in item:
                    merge(result, item['path'], item['sha256'])
    return result


def projected_claim(binding, report, row, descriptor, preceding, now):
    scope, dependencies = scope_and_dependencies(binding, row, preceding)
    outcome = 'FAIL' if binding['id'] == REFUTED else 'PASS'
    need(same(descriptor['status_semantics'][binding['id']],
              dict(status=binding['status'], verification_outcome=outcome)), 'STATUS_SEMANTICS')
    if binding['id'] == REFUTED:
        contract = descriptor['original_generic_refutation_contract']
        need(binding['status'] == 'REFUTED' and binding['verification_outcome'] == 'FAIL'
             and binding['refutation']['exact_statement_disproved'] is True
             and report['outcome'] == 'FAIL' and report['counterexample_audit_outcome'] == 'PASS'
             and binding['refutation']['proof'] == report['proof'] == contract['proof']['path']
             and binding['refutation']['sha256'] == report['proof_sha256'] == contract['proof']['sha256'], 'REFUTED_SPLIT')
    else:
        need(binding['status'] == 'VERIFIED', 'VERIFIED_STATUS')
    paths = evidence(binding, row, metadata_evidence(descriptor))
    artifacts, ids, hashes = [], [], {}
    for ordinal, (path, identity) in enumerate(sorted(paths.items())):
        aid = binding['id'].lower() + '-r1-evidence-' + str(ordinal)
        artifacts.append(dict(id=aid, path=path, sha256=identity, availability='LOCAL_ONLY',
                              retrieval=RETRIEVAL, unavailable_reason=UNAVAILABLE))
        ids.append(aid)
        hashes[aid] = identity
    mapping = dict(adapter_version=22, descriptor=dict(path=DESCRIPTOR, sha256=PINS[DESCRIPTOR]),
        recorded_binding=row['binding']['path'], recorded_binding_sha256=row['binding']['sha256'],
        recorded_report=binding['report'], recorded_report_sha256=binding['report_sha256'],
        recorded_binding_statement=binding['statement'], raw_statement_changed=False,
        original_binding_scope=copy.deepcopy(binding['scope']), original_report_scope=copy.deepcopy(report.get('scope')),
        original_dependencies=copy.deepcopy(binding['dependencies']), schema_scope=scope,
        original_verification_timestamp=binding['verification_timestamp'], theorem_verification_outcome=outcome,
        successful_counterexample_audit_outcome=report['counterexample_audit_outcome'] if outcome == 'FAIL' else None,
        no_new_mathematical_approval=True, generic_role_waiver=False, target_resolution='NONE',
        schema_dependencies=copy.deepcopy(dependencies))
    checks = dict(claim_revision=1, verifier=binding['verifier'], method=binding['method'],
        command_or_audit=binding['report'], timestamp=binding['verification_timestamp'], outcome=outcome,
        scope=scope['description'], artifact_hashes=hashes,
        shared_components=copy.deepcopy(binding['shared_components'] if 'shared_components' in binding else report['shared_components']),
        controls=[jd(binding.get('controls', report.get('controls', report.get('corrupted_controls_rejected'))))],
        limitations=copy.deepcopy(binding['limitations']))
    claim = {key: copy.deepcopy(binding[key]) for key in ('id', 'revision', 'statement', 'kind', 'basis',
        'status', 'review_state', 'assumptions', 'limitations')}
    reasons = [{key: dep[key] for key in ('id', 'revision', 'reason')} for dep in dependencies if 'reason' in dep]
    claim.update(dependencies=[{key: dep[key] for key in ('id', 'revision', 'relation')} for dep in dependencies],
        scope=scope, evidence=ids, verification=[checks], created_at=now, updated_at=now, external_source=None,
        unknowns=dict(external_source='Internal scoped checking; no external or novelty status inferred.',
            premises=jd(binding.get('premise_state', binding.get('mathematical_scope', {}))),
            dependency_notes=jd(reasons), original_binding_method=binding['method'], original_binding_kind=binding['kind'],
            original_binding_scope=jd(binding['scope']), editorial_statement_mapping=jd(mapping)),
        reproducibility=dict(manifest=next(a['id'] for a in artifacts if a['path'] == binding['report'])))
    return claim, artifacts


def build_projection(before, descriptor, bindings, reports, now):
    stamp(now)
    expected = copy.deepcopy(before)
    expected['updated_at'] = now
    for row, binding, report in zip(descriptor['records'], bindings, reports):
        claim, artifacts = projected_claim(binding, report, row, descriptor, expected['claims'], now)
        expected['claims'].append(claim)
        expected['artifacts'].extend(artifacts)
    return expected


def projection(before, after, descriptor, bindings, reports, require_public=True):
    need(type(before['claims']) is list and len(before['claims']) == 400
         and type(after['claims']) is list and len(after['claims']) == 418, 'CLAIM_POPULATION')
    need(same(after['claims'][:400], before['claims']), 'PRIOR_CLAIMS')
    need(same(after['artifacts'][:len(before['artifacts'])], before['artifacts']), 'PRIOR_ARTIFACTS')
    need(set(before) == set(after), 'ROOT_KEYS')
    for key in before:
        if key not in {'claims', 'artifacts', 'updated_at'}:
            need(same(before[key], after[key]), 'PRIOR_ROOT:' + key)
    need(type(before['target']) is dict and before['target']['status'] == 'UNKNOWN', 'TARGET_UNKNOWN')
    public = [a for a in before['artifacts'] if a['availability'] == 'PUBLIC']
    need(not require_public or len(public) == 6054, 'PRIOR_PUBLIC_POPULATION')
    expected = build_projection(before, descriptor, bindings, reports, after['updated_at'])
    for actual, wanted in zip(after['claims'][400:], expected['claims'][400:]):
        need(set(actual) == set(wanted), 'NEW_CLAIM_KEYS')
        for key in wanted:
            need(same(actual[key], wanted[key]), 'NEW_CLAIM:' + key)
    need(same(after['artifacts'][len(before['artifacts']):], expected['artifacts'][len(before['artifacts']):]), 'APPENDED_ARTIFACTS')
    all_ids = [a['id'] for a in after['artifacts']]
    need(len(all_ids) == len(set(all_ids)), 'ARTIFACT_IDS')
    need(same(dict(Counter(c['status'] for c in after['claims'])), dict(VERIFIED=409, CANDIDATE=3, REFUTED=6)), 'STATUS_COUNTS')
    need(all(c['review_state'] == 'CLEAR' for c in after['claims']), 'REVIEW_COUNTS')
    appended = after['claims'][400:]
    need(sum(c['verification'][0]['outcome'] == 'PASS' for c in appended) == 17
         and appended[-1]['id'] == REFUTED and appended[-1]['verification'][0]['outcome'] == 'FAIL', 'APPENDED_OUTCOMES')
    return dict(before=400, after=418, added=18, status_counts=dict(VERIFIED=409, CANDIDATE=3, REFUTED=6),
        review_state_counts=dict(CLEAR=418), prior_claim_records_preserved=400,
        prior_artifact_records_preserved=len(before['artifacts']), prior_PUBLIC_preserved=len(public),
        exact_ids=[c['id'] for c in appended], appended_theorem_outcomes=dict(PASS=17, FAIL=1),
        target_resolution='UNKNOWN', newly_appended_availability='LOCAL_ONLY',
        refuted_generic_theorem_is_target_exclusion=False)


def runtime(plan, manifest, terminal):
    need(type(plan) is dict and type(plan['command']) is list and all(type(v) is str for v in plan['command']), 'PLAN_COMMAND')
    command = plan['command']
    need(command.count('--') == 1 and same(command[command.index('--') + 1:], plan['child_argv']), 'PLAN_SUFFIX')
    need(type(plan['worker_argv']) is list and all(type(v) is str for v in plan['worker_argv'])
         and same(plan['child_argv'][-len(plan['worker_argv']):], plan['worker_argv']), 'PLAN_WORKER_SUFFIX')
    need(same(manifest['command'], plan['child_argv']), 'RUNTIME_COMMAND')
    need(type(manifest['schema_version']) is int and manifest['schema_version'] == 1
         and manifest['source_sha256'] == PINS[SUP] and manifest['runtime_scope'] == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and manifest['process_scope'] == 'Local non-escaping process tree only; remote/daemonized compute is unsupported', 'RUNTIME_SOURCE')
    allocation = plan['allocation']
    need(type(manifest['seconds']) in (int, float) and manifest['seconds'] == allocation['outer_seconds']
         and type(manifest['shutdown_reserve_seconds']) in (int, float)
         and manifest['shutdown_reserve_seconds'] == allocation['shutdown_reserve_seconds']
         and manifest['cumulative_across_commands'] is False and manifest['automatic_retry'] is False, 'RUNTIME_ALLOCATION')
    need(type(manifest['invocation_id']) is str and re.fullmatch('[0-9a-f]{32}', manifest['invocation_id']) is not None
         and terminal['invocation_id'] == manifest['invocation_id'], 'RUNTIME_INVOCATION')
    need(terminal['status'] == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and terminal['stop_reason'] == 'COMMAND_EXITED'
         and type(terminal['command_exit_code']) is int and terminal['command_exit_code'] == 0
         and terminal['error'] is None and terminal['deadline_reached'] is False
         and terminal['hard_limit_observed'] is True, 'RUNTIME_TERMINAL')
    clean = terminal['cleanup']
    need(clean['created_suspended'] is True and clean['resumed'] is True and clean['reaped'] is True
         and type(clean['actual_exit_code']) is int and clean['actual_exit_code'] == 0
         and type(clean['pid']) is int and clean['pid'] > 0
         and type(clean['suspended_job_active']) is int and clean['suspended_job_active'] == 1
         and clean['job_active_zero_observed'] is True and clean['cleanup_errors'] == [], 'RUNTIME_CLEANUP')
    need(type(terminal['elapsed_seconds']) in (int, float) and 0 <= terminal['elapsed_seconds'] <= manifest['seconds'], 'RUNTIME_ELAPSED')


def synthetic_before(descriptor):
    dependency_ids = list(dict.fromkeys(e['dependency_id'] for e in descriptor['proposed_dependency_topology']
                                      if e['dependency_id'] not in {r['id'] for r in descriptor['records']}))
    ids = dependency_ids + ['C-FIXTURE-' + str(i) for i in range(400 - len(dependency_ids))]
    claims = [dict(id=cid, revision=1, statement='Synthetic preservation record ' + cid,
                   status='VERIFIED' if i < 392 else ('CANDIDATE' if i < 395 else 'REFUTED'),
                   review_state='CLEAR', verification=[], scope={'fixture': True}) for i, cid in enumerate(ids)]
    artifacts = [dict(id='old-' + str(i), path='fixture/public/' + str(i), sha256='1' * 64,
                      availability='PUBLIC', retrieval='Exact immutable prefix\ncontinued path ' + str(i), unavailable_reason=None)
                 for i in range(6054)]
    return dict(schema_version=2, updated_at='2000-01-01T00:00:00Z', claims=claims, artifacts=artifacts,
                archives=[], target=dict(status='UNKNOWN'))


def controls(before, after, descriptor, bindings, reports, tick):
    positives, negatives = [], []
    def yes(name, ok):
        need(ok, 'CONTROL_POSITIVE:' + name)
        positives.append(dict(case=name, observed=True))
    def no(name, expected, call):
        tick()
        try:
            call()
        except Reject as error:
            need(str(error) == expected, 'CONTROL_STAGE:' + name + ':' + str(error))
            negatives.append(dict(case=name, expected=expected, actual=str(error)))
        else:
            raise Reject('CONTROL_ACCEPTED:' + name)
        tick()
    result = projection(before, after, descriptor, bindings, reports)
    yes('complete_typed_projection', result['after'] == 418)
    yes('all400_and6054_preserved', result['prior_claim_records_preserved'] == 400 and result['prior_PUBLIC_preserved'] == 6054)
    yes('17PASS_1FAIL_original_refuted', result['appended_theorem_outcomes'] == dict(PASS=17, FAIL=1))
    yes('distinct_qualified_original_ids', after['claims'][-2]['id'] == QUALIFIED and after['claims'][-1]['id'] == REFUTED)
    yes('literal18_verification_timestamps', all(c['verification'][0]['timestamp'] == b['verification_timestamp']
        for c, b in zip(after['claims'][400:], bindings)))
    sample_plan = dict(command=['python', 'supervisor', '--', 'python', 'fixture'], child_argv=['python', 'fixture'], worker_argv=['python', 'fixture'],
                       allocation=dict(outer_seconds=120, shutdown_reserve_seconds=20))
    sample_manifest = dict(schema_version=1, source_sha256=PINS[SUP], runtime_scope='LOCAL_WINDOWS_SUSPENDED_JOB_V1',
        process_scope='Local non-escaping process tree only; remote/daemonized compute is unsupported',
        command=sample_plan['child_argv'][:], seconds=120.0, shutdown_reserve_seconds=20.0,
        cumulative_across_commands=False, automatic_retry=False, invocation_id='2' * 32)
    sample_terminal = dict(invocation_id='2' * 32, status='COMMAND_COMPLETED_VERIFICATION_PENDING', stop_reason='COMMAND_EXITED',
        command_exit_code=0, error=None, deadline_reached=False, hard_limit_observed=True, elapsed_seconds=1.0,
        cleanup=dict(created_suspended=True, resumed=True, reaped=True, actual_exit_code=0,
                     pid=1234, suspended_job_active=1, job_active_zero_observed=True, cleanup_errors=[]))
    runtime(sample_plan, sample_manifest, sample_terminal)
    yes('authentic_SUP2_shaped_runtime', True)
    yes('typed_numeric_distinction', not same(True, 1) and not same(1, 1.0))
    yes('strict_JSON_positive', same(raw_json('{"a":[1,true,null]}'), dict(a=[1, True, None])))
    def mutate(name, stage, change):
        value = copy.deepcopy(after)
        change(value)
        no(name, stage, lambda: projection(before, value, descriptor, bindings, reports))
    mutate('old_claim_statement', 'PRIOR_CLAIMS', lambda x: x['claims'][0].update(statement='Changed'))
    mutate('old_PUBLIC_retrieval', 'PRIOR_ARTIFACTS', lambda x: x['artifacts'][0].update(retrieval='Changed'))
    mutate('root_target', 'PRIOR_ROOT:target', lambda x: x.update(target='SOLVED'))
    mutate('missing18th', 'CLAIM_POPULATION', lambda x: x['claims'].pop())
    mutate('new_extra_key', 'NEW_CLAIM_KEYS', lambda x: x['claims'][400].update(extra=True))
    changes = [('statement', 'Broader.'), ('revision', True), ('status', 'REFUTED'), ('kind', 'exclusion'),
        ('basis', []), ('review_state', 'NEEDS_RECHECK'), ('scope', {}), ('dependencies', []),
        ('assumptions', []), ('limitations', []), ('evidence', []), ('created_at', '2000-01-01T00:00:00Z'),
        ('updated_at', '2000-01-01T00:00:00Z'), ('external_source', 'NEW'), ('reproducibility', {}), ('unknowns', {})]
    # Pick a genuinely nonempty dependency/assumption/limitation field, not an alias or a no-op.
    for key, value in changes:
        index = next(i for i in range(400, 418) if not same(after['claims'][i][key], value))
        mutate('new_' + key, 'NEW_CLAIM:' + key, lambda x, i=index, k=key, v=value: x['claims'][i].__setitem__(k, v))
    mutate('refuted_FAIL_to_PASS', 'NEW_CLAIM:verification', lambda x: x['claims'][-1]['verification'][0].update(outcome='PASS'))
    mutate('qualified_role_changed', 'NEW_CLAIM:verification', lambda x: x['claims'][-2]['verification'][0].update(verifier='/root/other'))
    mutate('literal_timestamp_changed', 'NEW_CLAIM:verification', lambda x: x['claims'][400]['verification'][0].update(timestamp='2000-01-01T00:00:00Z'))
    mutate('new_artifact_PUBLIC', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'][-1].update(availability='PUBLIC'))
    mutate('new_artifact_hash', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'][-1].update(sha256='0' * 64))
    mutate('extra_artifact', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'].append(copy.deepcopy(x['artifacts'][-1])))
    for name, stage, target, key, value in [
        ('runtime_source', 'RUNTIME_SOURCE', 'manifest', 'source_sha256', '0' * 64),
        ('runtime_scope', 'RUNTIME_SOURCE', 'manifest', 'runtime_scope', 'UNSUPPORTED'),
        ('runtime_command', 'RUNTIME_COMMAND', 'manifest', 'command', ['other']),
        ('runtime_bool_seconds', 'RUNTIME_ALLOCATION', 'manifest', 'seconds', True),
        ('runtime_invocation', 'RUNTIME_INVOCATION', 'terminal', 'invocation_id', '3' * 32),
        ('runtime_bool_exit', 'RUNTIME_TERMINAL', 'terminal', 'command_exit_code', False),
        ('runtime_deadline', 'RUNTIME_TERMINAL', 'terminal', 'deadline_reached', True),
        ('runtime_cleanup', 'RUNTIME_CLEANUP', 'terminal', 'cleanup', dict(sample_terminal['cleanup'], job_active_zero_observed=False))]:
        man, term = copy.deepcopy(sample_manifest), copy.deepcopy(sample_terminal)
        (man if target == 'manifest' else term)[key] = value
        no(name, stage, lambda m=man, t=term: runtime(sample_plan, m, t))
    no('JSON_duplicate', 'JSON_DUPLICATE', lambda: raw_json('{"x":1,"x":2}'))
    no('JSON_nonfinite', 'JSON_NONFINITE', lambda: raw_json('{"x":NaN}'))
    need(len(positives) == 8 and len(negatives) == 37, 'CONTROL_POPULATION')
    return dict(positive=positives, strict_negative=negatives,
                damaged_full_bytes_all_durable=False, mutation_scope='Memory copies; case names/source and exact stages durable.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=['calibrate', 'protected-copy', 'post'], required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', required=True)
    for key in ('source-sha256', 'spec-sha256', 'expected-head', 'ledger-sha256', 'index-sha256'):
        ap.add_argument('--' + key, required=True)
    ap.add_argument('--packet')
    ap.add_argument('--packet-sha256')
    a = ap.parse_args()
    clock = CommandDeadline(a.seconds, allocation_reason='V22 exact typed400to418 engineering projection;20second save reserve; no mathematics')
    out = Path(a.out).resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    before_live = (ROOT / 'CLAIMS.yaml').read_bytes()
    inputs, outputs, cache, cache_stats = {}, {}, {}, {}
    completed = None
    barrier_count = 0
    prior_replace, prior_argv = os.replace, sys.argv

    def tick(closing=False):
        state = clock.status()
        need(not state['stop_required'] and state['remaining_seconds'] > (0 if closing else 20), 'CLOSING_DEADLINE' if closing else 'SAVE_RESERVE')

    def bounded(path):
        value = Path(path)
        value = (ROOT / value).resolve() if not value.is_absolute() else value.resolve()
        need(value.is_relative_to(ROOT) and value.is_file(), 'BOUNDED_FILE')
        return value

    def digest(path, closing=False, reuse=False):
        value = bounded(path)
        name = value.relative_to(ROOT).as_posix()
        tick(closing)
        if reuse and name in cache:
            observed = value.stat()
            need(cache_stats[name] == (observed.st_size, observed.st_mtime_ns), 'INPUT_STAT_CHANGED')
            return cache[name]
        h = hashlib.sha256()
        with value.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                tick(closing)
                h.update(block)
        identity = h.hexdigest()
        need(name not in cache or cache[name] == identity, 'CHANGED_DURING_RUN')
        cache[name] = identity
        observed = value.stat()
        cache_stats[name] = (observed.st_size, observed.st_mtime_ns)
        tick(closing)
        return identity

    def pin(path, identity):
        need(digest(path, reuse=True) == identity, 'INPUT_IDENTITY:' + str(path))
        merge(inputs, str(path), identity)

    def read_ref(ref):
        need(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'REFERENCE_SHAPE')
        pin(ref['path'], ref['sha256'])
        return raw_json(bounded(ref['path']).read_bytes())

    def save(name, value, closing=False):
        tick(closing)
        with (out / name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
        tick(closing)

    def protected(closing=False):
        tick(closing)
        need((ROOT / 'CLAIMS.yaml').read_bytes() == before_live
             and hashlib.sha256(before_live).hexdigest() == a.ledger_sha256
             and digest('.git/index', closing) == a.index_sha256
             and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == a.expected_head, 'PROTECTED_CONTEXT')
        tick(closing)

    def prerequisite(block, kind):
        plan, summary = read_ref(block['plan']), read_ref(block['summary'])
        manifest, terminal = read_ref(block['manifest']), read_ref(block['terminal'])
        read_ref(block['acceptance'])
        runtime(plan, manifest, terminal)
        need(summary['source_sha256'] == plan['source']['sha256'] and summary['spec_sha256'] == plan['specification']['sha256'], 'GATE_SOURCE')
        if kind == 'author':
            need(summary['status'] == 'V22_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW'
                 and same([summary[k] for k in ('positive_controls', 'strict_negative_controls', 'metadata_mappings', 'VERIFIED_mappings', 'REFUTED_mappings')], [94, 91, 18, 17, 1])
                 and summary['registrar_main_called'] is False and summary['independent_approval'] is False, 'AUTHOR_GATE')
            wanted = {'controls.json', 'mappings.json', 'mutation_instructions.json', 'ast_restoration.json'}
        else:
            need(summary['status'] == ('REGISTRAR_V22_PROJECTION_CALIBRATION_PASS' if kind == 'cal' else 'REGISTRAR_V22_PROTECTED_COPY_PASS')
                 and summary['source_sha256'] == a.source_sha256 and summary['spec_sha256'] == a.spec_sha256
                 and same([summary['positive_controls'], summary['strict_negative_controls']], [8, 37])
                 and summary['live_ledger_mutated'] is False and summary['mathematical_replays'] == 0, 'PROJECTION_GATE')
            if kind == 'copy':
                need(summary['write_barriers'] == 1 and summary['registrar_main_called'] is True
                     and summary['protected_ledger_sha256'] == packet['main']['before']['sha256'], 'COPY_BASELINE_GATE')
            wanted = set(summary['outputs_sha256'])
        payloads = block['payloads']
        need(type(payloads) is dict and set(payloads) == wanted, 'GATE_PAYLOAD_POPULATION')
        for name, ref in payloads.items():
            need(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'REFERENCE_SHAPE')
            pin(ref['path'], ref['sha256'])
            parent = Path(block['summary']['path']).parent
            need(Path(ref['path']).is_relative_to(parent)
                 and Path(ref['path']).relative_to(parent).as_posix() == name, 'GATE_PAYLOAD_PATH')
            if kind != 'author':
                need(summary['outputs_sha256'][name] == ref['sha256'], 'GATE_PAYLOAD_HASH')
            if name == 'controls.json':
                value = raw_json(bounded(ref['path']).read_bytes())
                need(len(value['positive']) == (94 if kind == 'author' else 8)
                     and len(value['strict_negative']) == (91 if kind == 'author' else 37), 'GATE_CONTROL_POPULATION')
                expected_key, actual_key = ('expected_stage', 'actual_stage') if kind == 'author' else ('expected', 'actual')
                need(all(r[expected_key] == r[actual_key] for r in value['strict_negative']), 'GATE_CONTROL_STAGES')
        # Gate direct input maps qualify source/runtime identities; no recursive scientific gate crawl.
        for path, identity in summary['inputs_sha256'].items():
            pin(path, identity)
        return summary

    try:
        protected()
        pin(SELF, a.source_sha256)
        pin(SPEC, a.spec_sha256)
        for path, identity in PINS.items():
            pin(path, identity)
        descriptor = raw_json((ROOT / DESCRIPTOR).read_bytes())
        rows = descriptor['records']
        need(len(rows) == 18 and rows[-1]['id'] == REFUTED and rows[-2]['id'] == QUALIFIED
             and len({r['id'] for r in rows}) == 18, 'DESCRIPTOR_POPULATION')
        bindings, reports = [], []
        for row in rows:
            tick()
            binding = read_ref(dict(path=row['binding']['path'], sha256=row['binding']['sha256']))
            report = read_ref(dict(path=row['bound_report']['path'], sha256=row['bound_report']['declared_sha256']))
            for key in ('id', 'revision', 'status', 'review_state', 'kind', 'basis', 'statement', 'producer', 'verifier', 'method'):
                need(same(binding[key], row[key]), 'BOUND_CORE:' + key)
            need(type(binding['revision']) is int and binding['revision'] == 1
                 and binding['verification_timestamp'] == row['verification_timestamp_literal']
                 and same(binding['scope'], row['original_scope']) and same(binding['dependencies'], row['original_dependencies'])
                 and binding['report'] == row['bound_report']['path'] and binding['report_sha256'] == row['bound_report']['declared_sha256']
                 and report['statement'] == binding['statement'] and report['status'] == row['bound_report']['headline'], 'BOUND_CONTRACT')
            bindings.append(binding)
            reports.append(report)
        for path, identity in metadata_evidence(descriptor).items():
            pin(path, identity)
        now = datetime.now(timezone.utc).isoformat()
        if a.mode == 'calibrate':
            need(a.packet is None and a.packet_sha256 is None, 'CAL_PACKET_ABSENT')
            before = synthetic_before(descriptor)
            after = build_projection(before, descriptor, bindings, reports, now)
        else:
            need(type(a.packet) is str and type(a.packet_sha256) is str, 'PACKET_REQUIRED')
            packet = read_ref(dict(path=a.packet, sha256=a.packet_sha256))
            need(packet['schema'] == 'REGISTRAR_V22_TRANSITION_RUNTIME_PACKET_V1' and packet['mode'] == a.mode
                 and same(packet['registrar'], dict(path=SUBJECT, sha256=PINS[SUBJECT]))
                 and same(packet['descriptor'], dict(path=DESCRIPTOR, sha256=PINS[DESCRIPTOR])), 'PACKET_SOURCE')
            read_ref(packet['root_authority'])
            prerequisite(packet['author'], 'author')
            prerequisite(packet['projection_cal'], 'cal')
            if a.mode == 'protected-copy':
                before = ledger(before_live)
                spec = importlib.util.spec_from_file_location('v22_protected_subject', ROOT / SUBJECT)
                subject = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(subject)
                tick()
                subject.digest = lambda path: digest(path, reuse=True)
                dest = out / 'protected_copy'
                def intercept(source, target):
                    nonlocal barrier_count
                    need(Path(target).resolve() == ROOT / 'CLAIMS.yaml'
                         and Path(source).resolve() == dest / 'CLAIMS.pending.yaml', 'SOLE_WRITE_BARRIER')
                    barrier_count += 1
                    need(barrier_count == 1, 'ONE_WRITE_BARRIER')
                    protected()
                    save('intercepted_report.json', copy.deepcopy(sys._getframe(1).f_locals['report']))
                    raise InterceptedWrite()
                os.replace = intercept
                sys.argv = [str(ROOT / SUBJECT), '--out', str(dest), '--previous-sha256', a.ledger_sha256]
                for row in rows:
                    sys.argv += ['--binding', str(ROOT / row['binding']['path']), '--binding-sha256', row['binding']['sha256']]
                try:
                    subject.main()
                except InterceptedWrite:
                    pass
                else:
                    raise Reject('WRITE_BARRIER_NOT_REACHED')
                finally:
                    os.replace, sys.argv = prior_replace, prior_argv
                after = ledger((dest / 'CLAIMS.after.yaml').read_bytes())
                need((dest / 'CLAIMS.before.yaml').read_bytes() == before_live
                     and (dest / 'CLAIMS.pending.yaml').read_bytes() == (dest / 'CLAIMS.after.yaml').read_bytes(), 'COPY_LEDGER_BYTES')
                validation = raw_json((dest / 'validation.json').read_bytes())
                need(validation['valid'] is True and validation['errors'] == [], 'COPY_VALIDATION')
                intercepted = raw_json((out / 'intercepted_report.json').read_bytes())
                need(intercepted['source_sha256'] == PINS[SUBJECT] and intercepted['before_ledger_sha256'] == a.ledger_sha256
                     and intercepted['ledger_sha256'] == hashlib.sha256((dest / 'CLAIMS.after.yaml').read_bytes()).hexdigest()
                     and intercepted['new_claim_ids'] == [r['id'] for r in rows]
                     and intercepted['claim_records'] == 418 and intercepted['mathematical_replays'] == 0
                     and intercepted['new_exclusions'] == 0 and intercepted['target_resolution'] == 'UNKNOWN', 'COPY_REPORT')
            else:
                prerequisite(packet['protected_copy'], 'copy')
                subject_plan = read_ref(packet['main']['plan'])
                subject_manifest = read_ref(packet['main']['manifest'])
                subject_terminal = read_ref(packet['main']['terminal'])
                runtime(subject_plan, subject_manifest, subject_terminal)
                subject_summary = read_ref(packet['main']['summary'])
                need(subject_plan['source']['sha256'] == PINS[SUBJECT]
                     and subject_summary['source_sha256'] == PINS[SUBJECT]
                     and subject_summary['status'] == 'EXACT_BOUND_SCOPED_CLAIMS_REGISTERED'
                     and subject_summary['target_resolution'] == 'UNKNOWN' and subject_summary['mathematical_replays'] == 0
                     and subject_summary['new_exclusions'] == 0 and subject_summary['new_claim_ids'] == [r['id'] for r in rows], 'MAIN_SCOPE')
                before_ref, after_ref = packet['main']['before'], packet['main']['after']
                pin(before_ref['path'], before_ref['sha256'])
                pin(after_ref['path'], after_ref['sha256'])
                before = ledger(bounded(before_ref['path']).read_bytes())
                expected_worker = [str(ROOT / 'build/research-venv/Scripts/python.exe').replace('\\', '/'), '-B',
                    str(ROOT / SUBJECT).replace('\\', '/'), '--out', subject_plan['output_root'],
                    '--previous-sha256', before_ref['sha256']]
                for row in rows:
                    expected_worker += ['--binding', str(ROOT / row['binding']['path']).replace('\\', '/'),
                                        '--binding-sha256', row['binding']['sha256']]
                need(same(subject_plan['worker_argv'], expected_worker), 'MAIN_LITERAL_WORKER')
                after_bytes = bounded(after_ref['path']).read_bytes()
                need(after_bytes == before_live and after_ref['sha256'] == a.ledger_sha256
                     and subject_summary['before_ledger_sha256'] == before_ref['sha256']
                     and subject_summary['ledger_sha256'] == after_ref['sha256'], 'MAIN_LEDGER_BYTES')
                after = ledger(after_bytes)
                validation = read_ref(packet['main']['validation'])
                need(validation['valid'] is True and validation['errors'] == [], 'MAIN_VALIDATION')
                need(same(subject_summary['status_counts'], dict(VERIFIED=409, CANDIDATE=3, REFUTED=6))
                     and type(subject_summary['claim_records']) is int and subject_summary['claim_records'] == 418, 'MAIN_COUNTS')
        tick()
        result = projection(before, after, descriptor, bindings, reports)
        # Each unique new declared artifact is authenticated once inside this worker.
        # No old PUBLIC member content or recursive nested scientific report is rehashed.
        closure = {}
        if a.mode != 'calibrate':
            for artifact in after['artifacts'][len(before['artifacts']):]:
                merge(closure, artifact['path'], artifact['sha256'])
            for path, identity in closure.items():
                pin(path, identity)
        completed = controls(before, after, descriptor, bindings, reports, tick)
        protected()
        save('controls.json', completed)
        save('projection.json', result)
        if a.mode == 'calibrate':
            save('synthetic.before.json', before)
            save('synthetic.after.json', after)
        tick()
        for path in sorted(out.rglob('*')):
            tick()
            if path.is_file():
                outputs[path.relative_to(out).as_posix()] = digest(path)
        for name, stat_identity in cache_stats.items():
            tick()
            value = bounded(name).stat()
            need(stat_identity == (value.st_size, value.st_mtime_ns), 'CLOSING_INPUT_STAT_CHANGED')
        protected(closing=True)
        status = {'calibrate': 'REGISTRAR_V22_PROJECTION_CALIBRATION_PASS',
                  'protected-copy': 'REGISTRAR_V22_PROTECTED_COPY_PASS', 'post': 'REGISTRAR_V22_ACTUAL_TRANSITION_PASS'}[a.mode]
        save('summary.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), status=status,
            implementation_version=1, source_sha256=a.source_sha256, spec_sha256=a.spec_sha256,
            producer='/root/structural', verifier=None, actual_executor='ROOT_BY_SEPARATE_AUTHORITY',
            method='engineering_typed_artifact_projection', independent_mathematical_approval=False,
            mode=a.mode, positive_controls=8, strict_negative_controls=37, projection=result,
            inputs_sha256=inputs, outputs_sha256=outputs, unique_new_declared_artifacts_hashed=len(closure),
            registrar_main_called=a.mode == 'protected-copy', registrar_helpers_imported=a.mode == 'protected-copy',
            write_barriers=barrier_count, live_ledger_mutated=False, index_mutated=False, mathematical_replays=0,
            target_resolution='UNKNOWN', command=[sys.executable, *prior_argv],
            protected_HEAD=a.expected_head, protected_ledger_sha256=a.ledger_sha256, protected_index_sha256=a.index_sha256,
            limitations=['Structural authored V22 adapter and this independent projection implementation; Root/Checkpoint engineering review is required.',
                'All400 prior objects/all6054 PUBLIC tuples are preserved as typed ledger content; no old PUBLIC bulk or remote byte replay.',
                '37 damaged memory objects are source-reproducible; full damaged bytes are not all durable.',
                'Provisional PASS requires clean supported runtime/Root review; exception/hard kill need not flush all pending outputs.'],
            deadline=clock.status()), closing=True)
        tick(closing=True)
        protected(closing=True)
    except BaseException as error:
        with (out / 'failure.json').open('x', encoding='utf8', newline='\n') as stream:
            json.dump(dict(timestamp=datetime.now(timezone.utc).isoformat(), error_type=type(error).__name__, message=str(error),
                controls=completed, inputs_sha256=inputs, provisional_PASS_not_accepted=True, deadline=clock.status()),
                stream, indent=2, allow_nan=False)
            stream.write('\n')
        raise
    finally:
        os.replace, sys.argv = prior_replace, prior_argv
        need((ROOT / 'CLAIMS.yaml').read_bytes() == before_live
             and hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest() == a.index_sha256
             and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == a.expected_head,
             'PROTECTED_FINAL_STATE')


if __name__ == '__main__':
    main()
