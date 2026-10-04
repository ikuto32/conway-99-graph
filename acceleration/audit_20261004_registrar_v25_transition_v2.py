"""SOURCE_ONLY distinct CP projection of the closed V25 four-claim append.

Calibration and post never import the registrar. Protected-copy executes the
subject solely under one intercepted os.replace; that is subject execution,
not an independent checking algorithm. No mathematical result is reapproved.
"""
import argparse
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_registrar_v25_transition_v2.py'
SPEC = 'acceleration/audit_20261004_registrar_v25_transition_v2_spec.md'
SUBJECT = 'acceleration/register_20261004_bound_claims_v25.py'
SUBJECT_SPEC = 'acceleration/register_20261004_bound_claims_v25_spec.md'
ANCESTOR = 'acceleration/register_20261004_bound_claims_v23.py'
DESCRIPTOR = 'acceleration/proposal_20261004_wave45_focal_and_rank_four_bound_claims_v1.json'
SUP = 'acceleration/run_compute_command_v2.py'
PINS = {
    SUBJECT: '540a1203a57e5dfd772233995c850382ce521ea9cba455c550d2b1d88cb6919b',
    SUBJECT_SPEC: '93a638cb4063a8f259500364bcd82b7392357affcf735c9321292344157d563c',
    ANCESTOR: 'fb7c9ce93c15713086d4149f15afac6e8c6c4fec978dba180012b6664a0c434d',
    DESCRIPTOR: 'b06bc418bf7f794f9635c25780b6085b13da2d7e50351a41bc5f1ca6d8ed7eaf',
    SUP: '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'docs/claims.schema.json': '0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
IDS = [
    'C-TARGET-INDEPENDENT-SUPPORT-FOCAL-NEIGHBOR-MATCHING-CUTS',
    'C-FIXED17-PLAIN-FOCAL-NEIGHBOR-SYSTEMS-INTEGER-FEASIBLE',
    'C-FIXED17-FOCAL-SELECTOR-MATCHING-SYSTEMS-INTEGER-FEASIBLE',
    'C-UNRESTRICTED-TARGET-TERNARY-DIVIDED-GRAM-FORM-RANK77',
]
EXACT = [
    ('6288d24cd39736c1577b5093d38aa514f59cfed932c78f479d99bd1f164b92c9', '848d35933fe2b2876ac20631a3370a73d6696cd053a7e07004b113703220a7d3'),
    ('320028e62a66aaf7adea1b78107c347ad21b26d8e62f0cc460ddec5cd7b5e502', 'ae11274983db5b43834f7f8dec4f0e1945d2c53e2a391133bf8d36346378453c'),
    ('760b9bd690649617baa40659ab804fcc91c550589e4d466186af50df66153c14', 'efde74be34983d7ededd200da5ae3d195966234ef33a4941aecab72e7112bcca'),
    ('658438c82fa24b2a11cac073bfe4f47b75a6e9a4e0bef5c8c0d1799a01a282ea', '7ceb72cae1825ab3883ac3b6911ca6fa7fc9b334e6a0838112cbdd1f89c54b50'),
]
ROLES = [('/root', '/root/structural', 'independent_derivation'),
         ('/root/checkpoint_audit', '/root/native_driver', 'independent_artifact_check'),
         ('/root/structural', '/root/native_driver', 'independent_artifact_check'),
         ('/root/structural', '/root/native_driver', 'independent_derivation')]
RETRIEVAL = 'Exact workspace path; checking reports give raw input and replay commands.'
UNAVAILABLE = 'Immutable publication of this newly bound evidence has not yet been confirmed.'
COUNTS = dict(VERIFIED=413, CANDIDATE=3, REFUTED=6)
CONTROL_COUNTS = dict(positive=11, negative=49, total=60)
FAMILY = 'REGISTRAR_V25_FOUR_CLAIM_TRANSITION_V2_'


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


def raw_json(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'JSON_DUPLICATE')
            result[key] = value
        return result
    def constant(_):
        raise Reject('JSON_NONFINITE')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


class LedgerLoader(yaml.SafeLoader):
    pass


LedgerLoader.yaml_implicit_resolvers = {
    key: [(tag, expr) for tag, expr in values if tag != 'tag:yaml.org,2002:timestamp']
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def yaml_mapping(loader, node, deep=False):
    result = {}
    for key, value in loader.construct_pairs(node, deep=True):
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
    need(type(path) is str and type(identity) is str and re.fullmatch('[0-9a-f]{64}', identity), 'EVIDENCE_TYPE')
    need(path not in target or target[path] == identity, 'EVIDENCE_CONFLICT')
    target[path] = identity


def metadata_evidence(descriptor):
    # This is the public artifact contract, not a call to the registrar adapter.
    result = {key: PINS[key] for key in (DESCRIPTOR, ANCESTOR, SUBJECT, SUBJECT_SPEC,
        'acceleration/validate_claims.py', 'docs/claims.schema.json')}
    need(type(descriptor.get('fresh_metadata_sha256')) is dict, 'METADATA_MAP')
    for path, identity in descriptor['fresh_metadata_sha256'].items():
        merge(result, path, identity)
    return result


def bound_contract(binding, report, row, ordinal):
    need(type(binding) is dict and binding.get('schema') == 'CLAIM_BINDING_SCHEMA2', 'BINDING_SCHEMA')
    need(type(binding.get('revision')) is int and type(binding.get('claim_revision')) is int
         and binding['revision'] == binding['claim_revision'] == 1, 'BOUND_REVISION')
    need('assumptions' in binding and type(binding['assumptions']) is list
         and all(type(x) is str for x in binding['assumptions']), 'ASSUMPTIONS_METADATA')
    need(type(binding.get('limitations')) is list and all(type(x) is str for x in binding['limitations']), 'LIMITATIONS_METADATA')
    for key in ('id', 'revision', 'status', 'review_state', 'kind', 'basis', 'statement',
                'assumptions', 'producer', 'verifier', 'method', 'scope', 'dependencies'):
        need(key in binding and same(binding[key], row[key]), 'BOUND_CORE:' + key)
    need(binding['id'] == IDS[ordinal] and binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and (binding['producer'], binding['verifier'], binding['method']) == ROLES[ordinal]
         and binding['producer'] != binding['verifier'] and binding['target_resolution'] == 'NONE', 'BOUND_ROLES')
    stamp(binding['verification_timestamp'])
    need(binding['verification_timestamp'] == row['verification_timestamp_literal']
         and binding['report'] == row['report']['path'] and binding['report_sha256'] == EXACT[ordinal][1]
         and row['binding']['sha256'] == EXACT[ordinal][0] and row['report']['sha256'] == EXACT[ordinal][1], 'BOUND_IDENTITY')
    need(type(report) is dict and report['status'] == row['report']['status']
         and report['claim_id'] == binding['id'] and type(report['claim_revision']) is int
         and report['claim_revision'] == 1 and report['statement'] == binding['statement']
         and (report['producer'], report['verifier'], report['method']) == ROLES[ordinal]
         and same(report['scope'], binding['scope']) and report['target_resolution'] == 'NONE', 'REPORT_CONTRACT')
    scope = binding['scope']
    need(type(scope) is dict and set(scope) == {'description', 'unrestricted_target', 'target_resolution'}
         and type(scope['description']) is str and type(scope['unrestricted_target']) is bool
         and scope['target_resolution'] == 'NONE', 'SCOPE_TYPE')


def dependencies(binding, preceding):
    result = []
    need(type(binding['dependencies']) is list, 'DEPENDENCY_TYPE')
    for dep in binding['dependencies']:
        need(type(dep) is dict and {'id', 'revision', 'relation'} <= set(dep)
             and set(dep) <= {'id', 'revision', 'relation', 'reason'} and type(dep['id']) is str
             and type(dep['revision']) is int and dep['revision'] == 1, 'DEPENDENCY_TYPE')
        need(dep['relation'] == 'uses_result', 'DEPENDENCY_RELATION')
        prior = [claim for claim in preceding if claim['id'] == dep['id']]
        need(len(prior) == 1 and type(prior[0]['revision']) is int and prior[0]['revision'] == dep['revision']
             and prior[0]['status'] == 'VERIFIED' and prior[0]['review_state'] == 'CLEAR', 'DEPENDENCY_PRECEDING')
        if 'reason' in dep:
            need(type(dep['reason']) is str, 'DEPENDENCY_REASON')
        result.append(copy.deepcopy(dep))
    return result


def evidence(binding, row, descriptor):
    result = metadata_evidence(descriptor)
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


def projected_claim(binding, report, row, descriptor, preceding, now, ordinal):
    bound_contract(binding, report, row, ordinal)
    scope = copy.deepcopy(binding['scope'])
    deps = dependencies(binding, preceding)
    artifacts, ids, hashes = [], [], {}
    for index, (path, identity) in enumerate(sorted(evidence(binding, row, descriptor).items())):
        aid = binding['id'].lower() + '-r1-evidence-' + str(index)
        artifacts.append(dict(id=aid, path=path, sha256=identity, availability='LOCAL_ONLY',
                              retrieval=RETRIEVAL, unavailable_reason=UNAVAILABLE))
        ids.append(aid)
        hashes[aid] = identity
    mapping = dict(adapter_version=25, descriptor=dict(path=DESCRIPTOR, sha256=PINS[DESCRIPTOR]),
        recorded_binding=row['binding']['path'], recorded_binding_sha256=row['binding']['sha256'],
        recorded_report=binding['report'], recorded_report_sha256=binding['report_sha256'],
        recorded_binding_statement=binding['statement'], raw_statement_changed=False,
        original_binding_scope=copy.deepcopy(binding['scope']), original_report_scope=copy.deepcopy(report['scope']),
        original_dependencies=copy.deepcopy(binding['dependencies']), schema_scope=scope,
        original_verification_timestamp=binding['verification_timestamp'], theorem_verification_outcome='PASS',
        no_new_mathematical_approval=True, generic_role_waiver=False, target_resolution='NONE',
        controls_semantics=copy.deepcopy(descriptor['controls_semantics']), schema_dependencies=copy.deepcopy(deps))
    check = dict(claim_revision=1, verifier=binding['verifier'], method=binding['method'],
        command_or_audit=binding['report'], timestamp=binding['verification_timestamp'], outcome='PASS',
        scope=scope['description'], artifact_hashes=hashes,
        shared_components=copy.deepcopy(binding['shared_components'] if 'shared_components' in binding else report['shared_components']),
        controls=[jd(binding.get('controls', report.get('controls', report.get('corrupted_controls_rejected'))))],
        limitations=copy.deepcopy(binding['limitations']))
    claim = {key: copy.deepcopy(binding[key]) for key in ('id', 'revision', 'statement', 'kind', 'basis',
        'status', 'review_state', 'assumptions', 'limitations')}
    reasons = [{key: dep[key] for key in ('id', 'revision', 'reason')} for dep in deps if 'reason' in dep]
    claim.update(dependencies=[{key: dep[key] for key in ('id', 'revision', 'relation')} for dep in deps],
        scope=scope, evidence=ids, verification=[check], created_at=now, updated_at=now, external_source=None,
        unknowns=dict(external_source='Internal scoped checking; no external or novelty status inferred.',
            premises=jd(binding.get('premise_state', binding.get('mathematical_scope', {}))),
            dependency_notes=jd(reasons), original_binding_method=binding['method'], original_binding_kind=binding['kind'],
            original_binding_scope=jd(binding['scope']), editorial_statement_mapping=jd(mapping)),
        reproducibility=dict(manifest=next(a['id'] for a in artifacts if a['path'] == binding['report'])))
    return claim, artifacts


def build_projection(before, descriptor, bindings, reports, now):
    stamp(now)
    need(len(bindings) == len(reports) == len(descriptor['records']) == 4, 'BOUND_POPULATION')
    expected = copy.deepcopy(before)
    expected['updated_at'] = now
    for ordinal, (row, binding, report) in enumerate(zip(descriptor['records'], bindings, reports)):
        need(binding['id'] not in {c['id'] for c in expected['claims']}, 'NEW_ID')
        claim, artifacts = projected_claim(binding, report, row, descriptor, expected['claims'], now, ordinal)
        expected['claims'].append(claim)
        expected['artifacts'].extend(artifacts)
    return expected


def projection(before, after, descriptor, bindings, reports):
    need(type(before['claims']) is list and len(before['claims']) == 418
         and type(after['claims']) is list and len(after['claims']) == 422, 'CLAIM_POPULATION')
    need(same(after['claims'][:418], before['claims']), 'PRIOR_CLAIMS')
    need(type(before['artifacts']) is list and type(after['artifacts']) is list
         and same(after['artifacts'][:len(before['artifacts'])], before['artifacts']), 'PRIOR_ARTIFACTS')
    need(set(before) == set(after), 'ROOT_KEYS')
    for key in before:
        if key not in {'claims', 'artifacts', 'updated_at'}:
            need(same(before[key], after[key]), 'PRIOR_ROOT:' + key)
    need(type(before['target']) is dict and before['target']['status'] == 'UNKNOWN', 'TARGET_UNKNOWN')
    public = [a for a in before['artifacts'] if a['availability'] == 'PUBLIC']
    need(len(public) == 6054, 'PRIOR_PUBLIC_POPULATION')
    need(same(dict(Counter(c['status'] for c in before['claims'])), dict(VERIFIED=409, CANDIDATE=3, REFUTED=6)), 'PRIOR_STATUS_COUNTS')
    expected = build_projection(before, descriptor, bindings, reports, after['updated_at'])
    for actual, wanted in zip(after['claims'][418:], expected['claims'][418:]):
        need(set(actual) == set(wanted), 'NEW_CLAIM_KEYS')
        for key in wanted:
            need(same(actual[key], wanted[key]), 'NEW_CLAIM:' + key)
    need(same(after['artifacts'][len(before['artifacts']):], expected['artifacts'][len(before['artifacts']):]), 'APPENDED_ARTIFACTS')
    all_ids = [a['id'] for a in after['artifacts']]
    need(len(all_ids) == len(set(all_ids)), 'ARTIFACT_IDS')
    need(same(dict(Counter(c['status'] for c in after['claims'])), COUNTS), 'STATUS_COUNTS')
    need(all(c['review_state'] == 'CLEAR' for c in after['claims']), 'REVIEW_COUNTS')
    appended = after['claims'][418:]
    need([c['id'] for c in appended] == IDS
         and all(c['verification'][0]['outcome'] == 'PASS' for c in appended), 'APPENDED_OUTCOMES')
    return dict(before=418, after=422, added=4, status_counts=COUNTS, review_state_counts=dict(CLEAR=422),
        prior_claim_records_preserved=418, prior_artifact_records_preserved=len(before['artifacts']),
        prior_PUBLIC_preserved=len(public), exact_ids=IDS, appended_theorem_outcomes=dict(PASS=4, FAIL=0),
        target_resolution='UNKNOWN', newly_appended_availability='LOCAL_ONLY', mathematical_reapproval=False)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def runtime(plan, manifest, terminal):
    need(type(plan) is dict and type(plan.get('command')) is list and all(type(x) is str for x in plan['command']), 'PLAN_COMMAND')
    command = plan['command']
    need(command.count('--') == 1 and same(command[command.index('--') + 1:], plan['child_argv']), 'PLAN_SUFFIX')
    need(type(plan['worker_argv']) is list and all(type(x) is str for x in plan['worker_argv'])
         and same(plan['child_argv'][-len(plan['worker_argv']):], plan['worker_argv']), 'PLAN_WORKER_SUFFIX')
    need(same(manifest['command'], plan['child_argv']), 'RUNTIME_COMMAND')
    need(type(manifest['schema_version']) is int and manifest['schema_version'] == 1
         and manifest['source_sha256'] == PINS[SUP] and manifest['runtime_scope'] == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and manifest['process_scope'] == 'Local non-escaping process tree only; remote/daemonized compute is unsupported', 'RUNTIME_SOURCE')
    allocation = plan['allocation']
    need(number(manifest['seconds']) and manifest['seconds'] == allocation['outer_seconds']
         and number(manifest['shutdown_reserve_seconds']) and manifest['shutdown_reserve_seconds'] == allocation['shutdown_reserve_seconds']
         and manifest['cumulative_across_commands'] is False and manifest['automatic_retry'] is False, 'RUNTIME_ALLOCATION')
    need(type(manifest['invocation_id']) is str and re.fullmatch('[0-9a-f]{32}', manifest['invocation_id'])
         and terminal['invocation_id'] == manifest['invocation_id'], 'RUNTIME_INVOCATION')
    need(terminal['status'] == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and terminal['stop_reason'] == 'COMMAND_EXITED'
         and type(terminal['command_exit_code']) is int and terminal['command_exit_code'] == 0
         and terminal['error'] is None and terminal['deadline_reached'] is False and terminal['hard_limit_observed'] is True, 'RUNTIME_TERMINAL')
    clean = terminal['cleanup']
    need(clean['created_suspended'] is True and clean['resumed'] is True and clean['reaped'] is True
         and type(clean['actual_exit_code']) is int and clean['actual_exit_code'] == 0
         and type(clean['pid']) is int and clean['pid'] > 0 and type(clean['suspended_job_active']) is int
         and clean['suspended_job_active'] == 1 and clean['job_active_zero_observed'] is True
         and clean['cleanup_errors'] == [], 'RUNTIME_CLEANUP')
    need(number(terminal['elapsed_seconds']) and 0 <= terminal['elapsed_seconds'] <= manifest['seconds'], 'RUNTIME_ELAPSED')


def synthetic_before(descriptor):
    dependency_ids = list(dict.fromkeys(dep['id'] for row in descriptor['records'] for dep in row['dependencies'] if dep['id'] not in IDS))
    ids = dependency_ids + ['C-FIXTURE-' + str(i) for i in range(418 - len(dependency_ids))]
    claims = [dict(id=cid, revision=1, statement='Synthetic preservation record ' + cid,
        status='VERIFIED' if i < 409 else 'CANDIDATE' if i < 412 else 'REFUTED',
        review_state='CLEAR', verification=[], scope={'fixture': True}) for i, cid in enumerate(ids)]
    artifacts = [dict(id='old-' + str(i), path='fixture/public/' + str(i), sha256='1' * 64,
        availability='PUBLIC', retrieval='Exact immutable prefix\ncontinued path ' + str(i), unavailable_reason=None) for i in range(6054)]
    return dict(schema_version=2, updated_at='2000-01-01T00:00:00Z', claims=claims,
        artifacts=artifacts, archives=[], target=dict(status='UNKNOWN'))


def controls(before, after, descriptor, bindings, reports, tick):
    positives, negatives = [], []
    def yes(name, ok):
        tick()
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
    yes('complete_typed_projection', result['after'] == 422)
    yes('all418_and6054_preserved', result['prior_claim_records_preserved'] == 418 and result['prior_PUBLIC_preserved'] == 6054)
    yes('all4_PASS', result['appended_theorem_outcomes'] == dict(PASS=4, FAIL=0))
    yes('exact4_dependency_order', [c['id'] for c in after['claims'][418:]] == IDS)
    yes('literal4_verification_timestamps', all(c['verification'][0]['timestamp'] == b['verification_timestamp'] for c, b in zip(after['claims'][418:], bindings)))
    yes('rank77_exact_statement_and_assumptions', same(after['claims'][421]['statement'], bindings[3]['statement']) and same(after['claims'][421]['assumptions'], bindings[3]['assumptions']))
    yes('internal_matching_predecessor', after['claims'][420]['dependencies'][0] == dict(id=IDS[0], revision=1, relation='uses_result'))
    sample_plan = dict(command=['python', 'supervisor', '--', 'python', 'fixture'], child_argv=['python', 'fixture'], worker_argv=['python', 'fixture'], allocation=dict(outer_seconds=120, shutdown_reserve_seconds=20))
    sample_manifest = dict(schema_version=1, source_sha256=PINS[SUP], runtime_scope='LOCAL_WINDOWS_SUSPENDED_JOB_V1', process_scope='Local non-escaping process tree only; remote/daemonized compute is unsupported', command=sample_plan['child_argv'][:], seconds=120.0, shutdown_reserve_seconds=20.0, cumulative_across_commands=False, automatic_retry=False, invocation_id='2' * 32)
    sample_terminal = dict(invocation_id='2' * 32, status='COMMAND_COMPLETED_VERIFICATION_PENDING', stop_reason='COMMAND_EXITED', command_exit_code=0, error=None, deadline_reached=False, hard_limit_observed=True, elapsed_seconds=1.0, cleanup=dict(created_suspended=True, resumed=True, reaped=True, actual_exit_code=0, pid=1234, suspended_job_active=1, job_active_zero_observed=True, cleanup_errors=[]))
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
    mutate('late_old_claim417_statement', 'PRIOR_CLAIMS', lambda x: x['claims'][417].update(statement='Changed late claim'))
    public_last_index = [i for i, artifact in enumerate(before['artifacts']) if artifact['availability'] == 'PUBLIC'][6053]
    mutate('late_old_PUBLIC6053_continuation', 'PRIOR_ARTIFACTS', lambda x: x['artifacts'][public_last_index].update(retrieval='Exact immutable prefix\nchanged continuation'))
    mutate('root_target', 'PRIOR_ROOT:target', lambda x: x.update(target='SOLVED'))
    mutate('missing4th', 'CLAIM_POPULATION', lambda x: x['claims'].pop())
    mutate('new_extra_key', 'NEW_CLAIM_KEYS', lambda x: x['claims'][418].update(extra=True))
    changes = [('statement', 'Broader.'), ('revision', True), ('status', 'REFUTED'), ('kind', 'exclusion'),
        ('basis', []), ('review_state', 'NEEDS_RECHECK'), ('scope', {}), ('dependencies', []),
        ('assumptions', []), ('limitations', []), ('evidence', []), ('created_at', '2000-01-01T00:00:00Z'),
        ('updated_at', '2000-01-01T00:00:00Z'), ('external_source', 'NEW'), ('reproducibility', {}), ('unknowns', {})]
    for key, value in changes:
        index = next(i for i in range(418, 422) if not same(after['claims'][i][key], value))
        mutate('new_' + key, 'NEW_CLAIM:' + key, lambda x, i=index, k=key, v=value: x['claims'][i].__setitem__(k, v))
    mutate('rank_PASS_to_FAIL', 'NEW_CLAIM:verification', lambda x: x['claims'][421]['verification'][0].update(outcome='FAIL'))
    mutate('plain_role_changed', 'NEW_CLAIM:verification', lambda x: x['claims'][419]['verification'][0].update(verifier='/root/other'))
    mutate('literal_timestamp_changed', 'NEW_CLAIM:verification', lambda x: x['claims'][418]['verification'][0].update(timestamp='2000-01-01T00:00:00Z'))
    mutate('new_artifact_PUBLIC', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'][-1].update(availability='PUBLIC'))
    mutate('new_artifact_hash', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'][-1].update(sha256='0' * 64))
    mutate('extra_artifact', 'APPENDED_ARTIFACTS', lambda x: x['artifacts'].append(copy.deepcopy(x['artifacts'][-1])))
    for name, change, stage in [('rank_revision_bool', lambda x: x.update(revision=True), 'BOUND_REVISION'),
        ('rank_assumptions_missing', lambda x: x.pop('assumptions'), 'ASSUMPTIONS_METADATA'),
        ('rank_assumptions_bool_member', lambda x: x.update(assumptions=[True]), 'ASSUMPTIONS_METADATA'),
        ('rank_scope_bool_alias', lambda x: x['scope'].update(unrestricted_target=1), 'BOUND_CORE:scope')]:
        bad = copy.deepcopy(bindings)
        change(bad[3])
        no(name, stage, lambda value=bad: build_projection(before, descriptor, value, reports, after['updated_at']))
    bad_rank = copy.deepcopy(bindings[3])
    bad_rank['dependencies'][0]['revision'] = True
    no('dependency_bool_revision', 'DEPENDENCY_TYPE', lambda: dependencies(bad_rank, before['claims']))
    rank_dependency = bindings[3]['dependencies'][0]['id']
    no('dependency_missing_predecessor', 'DEPENDENCY_PRECEDING',
       lambda: dependencies(bindings[3], [c for c in before['claims'] if c['id'] != rank_dependency]))
    bad_prior = copy.deepcopy(before['claims'])
    next(c for c in bad_prior if c['id'] == rank_dependency)['status'] = 'CANDIDATE'
    no('dependency_candidate_predecessor', 'DEPENDENCY_PRECEDING', lambda: dependencies(bindings[3], bad_prior))
    control_worker = binding_argv(expected_main_worker(str(ROOT / 'acceleration/results/fixture_subject'), '1' * 64), descriptor)
    control_recorded = recorded_main_command(control_worker, descriptor)
    control_report = dict(status='EXACT_BOUND_SCOPED_CLAIMS_REGISTERED', source_sha256=PINS[ANCESTOR],
        source_commit='2' * 40, before_ledger_sha256='1' * 64, ledger_sha256='3' * 64, new_claim_ids=IDS,
        claim_records=422, status_counts=COUNTS, review_state_counts=dict(CLEAR=422), mathematical_replays=0,
        new_exclusions=0, target_resolution='UNKNOWN', command=control_recorded, timestamp=after['updated_at'],
        editorial_statement_mappings=[raw_json(c['unknowns']['editorial_statement_mapping']) for c in after['claims'][418:]])
    main_report(control_report, '1' * 64, '3' * 64, after, '2' * 40, control_recorded)
    yes('inherited_report_source_and_stripped_argv', True)
    for name, key, value in [('report_subject_source_alias', 'source_sha256', PINS[SUBJECT]),
        ('report_unstripped_worker_argv', 'command', control_worker),
        ('report_registration_timestamp', 'timestamp', '2000-01-01T00:00:00Z')]:
        bad_report = copy.deepcopy(control_report)
        bad_report[key] = value
        no(name, 'MAIN_SCOPE', lambda value=bad_report: main_report(value, '1' * 64, '3' * 64, after, '2' * 40, control_recorded))
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
    need(len(positives) == CONTROL_COUNTS['positive'] and len(negatives) == CONTROL_COUNTS['negative'], 'CONTROL_POPULATION')
    return dict(positive=positives, strict_negative=negatives, damaged_full_bytes_all_durable=False,
        mutation_scope='Memory copies; case names/source and exact stages durable.')


class Reader:
    def __init__(self, clock):
        self.clock, self.inputs, self.cache, self.stats = clock, {}, {}, {}

    def tick(self):
        state = self.clock.status()
        need(state['stop_required'] is False and state['remaining_seconds'] > 20, 'SAVE_RESERVE')

    def path(self, name):
        need(type(name) is str and name and not Path(name).is_absolute()
             and '\\' not in name and ':' not in name and all(c >= ' ' for c in name)
             and all(p not in ('', '.', '..') for p in name.split('/')), 'INPUT_PATH')
        value = ROOT / name
        for ancestor in (value, *value.parents):
            if ancestor == ROOT.parent:
                break
            if ancestor.exists():
                stat = ancestor.lstat()
                need(not ancestor.is_symlink() and not getattr(stat, 'st_file_attributes', 0) & 0x400, 'INPUT_REPARSE')
        need(value.resolve().is_relative_to(ROOT) and value.is_file(), 'BOUNDED_FILE')
        return value

    def bytes(self, name, identity=None, reuse=False):
        self.tick()
        path = self.path(name)
        before = path.stat()
        if reuse and name in self.cache:
            need(self.stats[name] == (before.st_size, before.st_mtime_ns), 'INPUT_STAT_CHANGED')
            data, observed = self.cache[name]
        else:
            h, blocks = hashlib.sha256(), []
            with path.open('rb') as stream:
                while block := stream.read(1024 * 1024):
                    self.tick()
                    h.update(block)
                    blocks.append(block)
            after = path.stat()
            need((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'INPUT_CHANGED')
            data, observed = b''.join(blocks), h.hexdigest()
            need(name not in self.cache or self.cache[name][1] == observed, 'CHANGED_DURING_RUN')
            self.cache[name], self.stats[name] = (data, observed), (after.st_size, after.st_mtime_ns)
        if identity is not None:
            need(observed == identity, 'INPUT_IDENTITY:' + name)
            merge(self.inputs, name, identity)
        self.tick()
        return data

    def pin(self, name, identity):
        self.bytes(name, identity, reuse=True)

    def ref(self, ref):
        need(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'REFERENCE_SHAPE')
        return raw_json(self.bytes(ref['path'], ref['sha256'], reuse=True))

    def closing(self):
        for name, identity in list(self.inputs.items()):
            self.bytes(name, identity, reuse=False)


def load_bindings(reader, descriptor):
    need(descriptor['schema'] == 'WAVE45_FOCAL_AND_RANK_FOUR_BOUND_CLAIMS_SOURCE_ONLY_V1'
         and type(descriptor['record_population']) is int and descriptor['record_population'] == 4
         and same(descriptor['dependency_order'], IDS)
         and [row['id'] for row in descriptor['records']] == IDS, 'DESCRIPTOR_POPULATION')
    bindings, reports = [], []
    for ordinal, row in enumerate(descriptor['records']):
        reader.tick()
        binding = reader.ref(dict(path=row['binding']['path'], sha256=row['binding']['sha256']))
        report = reader.ref(dict(path=row['report']['path'], sha256=row['report']['sha256']))
        bound_contract(binding, report, row, ordinal)
        bindings.append(binding)
        reports.append(report)
    return bindings, reports


def prerequisite(reader, block, kind, source_sha, spec_sha, before_sha=None):
    plan, summary = reader.ref(block['plan']), reader.ref(block['summary'])
    manifest, terminal = reader.ref(block['manifest']), reader.ref(block['terminal'])
    acceptance = reader.ref(block['acceptance'])
    runtime(plan, manifest, terminal)
    need(acceptance['result'] == 'PASS' and all(same(acceptance[key], block[key])
         for key in ('plan', 'summary', 'manifest', 'terminal')), 'ROOT_GATE')
    if kind == 'author':
        need(summary['schema'] == 'REGISTRAR_V25_AUTHOR_HELPER_CONTROLS_V1'
             and summary['status'] == 'REGISTRAR_V25_AUTHOR_HELPER_CONTROLS_PASS'
             and all(type(summary[key]) is int and summary[key] == wanted for key, wanted in
                     [('positive_controls', 20), ('strict_negative_controls', 83), ('controls', 103), ('mapping_population', 4)])
             and summary['all_stages_match'] is True and summary['registrar_main_called'] is False
             and summary['scientific_member_hashes_checked'] is False and summary['mathematical_replays'] == 0,
             'AUTHOR_GATE')
        need(plan['source']['path'] in summary['inputs_sha256']
             and summary['inputs_sha256'][plan['source']['path']] == plan['source']['sha256']
             and summary['inputs_sha256'][SUBJECT] == PINS[SUBJECT]
             and summary['inputs_sha256'][DESCRIPTOR] == PINS[DESCRIPTOR], 'AUTHOR_SOURCE')
        wanted = {'controls.json', 'mappings.json', 'bridge.json'}
    else:
        need(summary['status'] == FAMILY + ('CALIBRATION_PASS' if kind == 'cal' else 'PROTECTED_COPY_PASS')
             and summary['source_sha256'] == source_sha and summary['spec_sha256'] == spec_sha
             and type(summary['implementation_version']) is int and summary['implementation_version'] == 2
             and type(summary['positive_controls']) is int and summary['positive_controls'] == CONTROL_COUNTS['positive']
             and type(summary['strict_negative_controls']) is int and summary['strict_negative_controls'] == CONTROL_COUNTS['negative']
             and summary['live_ledger_mutated'] is False and summary['mathematical_replays'] == 0, 'PROJECTION_GATE')
        if kind == 'copy':
            need(type(summary['write_barriers']) is int and summary['write_barriers'] == 1
                 and summary['registrar_main_called'] is True and summary['protected_ledger_sha256'] == before_sha, 'COPY_BASELINE_GATE')
        wanted = set(summary['outputs_sha256'])
    payloads = block['payloads']
    need(type(payloads) is dict and set(payloads) == wanted, 'GATE_PAYLOAD_POPULATION')
    parent = Path(block['summary']['path']).parent
    need({path.relative_to(ROOT / parent).as_posix() for path in (ROOT / parent).rglob('*') if path.is_file()}
         == wanted | {'summary.json'}, 'GATE_DIRECTORY')
    for name, ref in payloads.items():
        need(type(ref) is dict and set(ref) == {'path', 'sha256'}
             and Path(ref['path']).is_relative_to(parent)
             and Path(ref['path']).relative_to(parent).as_posix() == name, 'GATE_PAYLOAD_PATH')
        reader.pin(ref['path'], ref['sha256'])
        declared_key = ref['path'] if kind == 'author' else name
        need(summary['outputs_sha256'][declared_key] == ref['sha256'], 'GATE_PAYLOAD_HASH')
        if name == 'controls.json':
            table = reader.ref(ref)
            if kind == 'author':
                need(type(table) is list and len(table) == 103 and all(type(row['index']) is int and row['index'] == i
                     and row['match'] is True and row['expected'] == row['actual'] for i, row in enumerate(table)), 'GATE_CONTROL_STAGES')
                need(sum(row['expected'] == 'PASS' for row in table) == 20, 'GATE_CONTROL_POPULATION')
            else:
                need(len(table['positive']) == CONTROL_COUNTS['positive'] and len(table['strict_negative']) == CONTROL_COUNTS['negative']
                     and all(row['observed'] is True for row in table['positive'])
                     and all(row['expected'] == row['actual'] for row in table['strict_negative']), 'GATE_CONTROL_STAGES')
    # Authenticate only declared gate maps, not recursively discovered mathematics.
    for name, identity in summary['inputs_sha256'].items():
        reader.pin(name, identity)
    return summary


def expected_main_worker(output, previous):
    worker = [str(ROOT / 'build/research-venv/Scripts/python.exe').replace('\\', '/'), '-B',
        str(ROOT / SUBJECT).replace('\\', '/'), '--out', output, '--previous-sha256', previous,
        '--source-sha256', PINS[SUBJECT], '--spec-sha256', PINS[SUBJECT_SPEC]]
    return worker


def binding_argv(worker, descriptor):
    for row in descriptor['records']:
        worker += ['--binding', str(ROOT / row['binding']['path']).replace('\\', '/'),
                   '--binding-sha256', row['binding']['sha256']]
    return worker


def recorded_main_command(worker, descriptor):
    # V25 strips its source/spec pairs and constructs native Path strings before
    # immutable V23 main records [sys.executable,*sys.argv]. The -B launcher flag
    # is not in sys.argv. Keep these literal Windows spellings distinct from uv.
    recorded = [str(Path(worker[0])), str(ROOT / SUBJECT), '--out', str(Path(worker[4])),
                '--previous-sha256', worker[6]]
    for row in descriptor['records']:
        recorded += ['--binding', str(ROOT / row['binding']['path']), '--binding-sha256', row['binding']['sha256']]
    return recorded


def main_report(report, before_sha, after_sha, after, head, recorded_command):
    need(report['status'] == 'EXACT_BOUND_SCOPED_CLAIMS_REGISTERED'
         and report['source_sha256'] == PINS[ANCESTOR] and report['source_commit'] == head
         and report['before_ledger_sha256'] == before_sha and report['ledger_sha256'] == after_sha
         and report['new_claim_ids'] == IDS and type(report['claim_records']) is int and report['claim_records'] == 422
         and same(report['status_counts'], COUNTS) and same(report['review_state_counts'], dict(CLEAR=422))
         and report['mathematical_replays'] == 0 and report['new_exclusions'] == 0
         and report['target_resolution'] == 'UNKNOWN' and same(report['command'], recorded_command)
         and report['timestamp'] == after['updated_at']
         and same(report['editorial_statement_mappings'],
                  [raw_json(c['unknowns']['editorial_statement_mapping']) for c in after['claims'][418:]]), 'MAIN_SCOPE')


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
    clock = CommandDeadline(a.seconds, allocation_reason='V25 distinct418to422 typed projection;20second save reserve; no mathematical replay')
    reader = Reader(clock)
    out = Path(a.out).resolve()
    need(out.is_relative_to(ROOT / 'acceleration/results') and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    outputs, completed, barriers = {}, None, 0
    live_bytes = None
    prior_argv = sys.argv[:]

    def save(name, value):
        reader.tick()
        with (out / name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
        reader.tick()

    def protected():
        reader.tick()
        need(reader.bytes('CLAIMS.yaml') == live_bytes and hashlib.sha256(live_bytes).hexdigest() == a.ledger_sha256
             and hashlib.sha256(reader.bytes('.git/index')).hexdigest() == a.index_sha256, 'PROTECTED_CONTEXT')
        remaining = clock.status()['remaining_seconds'] - 20
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=min(60, remaining))
        need(result.returncode == 0 and result.stdout.decode('ascii').strip() == a.expected_head, 'PROTECTED_CONTEXT')
        reader.tick()

    try:
        live_bytes = reader.bytes('CLAIMS.yaml')
        protected()
        reader.pin(SELF, a.source_sha256)
        reader.pin(SPEC, a.spec_sha256)
        for path, identity in PINS.items():
            reader.pin(path, identity)
        descriptor = reader.ref(dict(path=DESCRIPTOR, sha256=PINS[DESCRIPTOR]))
        bindings, reports = load_bindings(reader, descriptor)
        for path, identity in metadata_evidence(descriptor).items():
            reader.pin(path, identity)
        now = datetime.now(timezone.utc).isoformat()
        if a.mode == 'calibrate':
            need(a.packet is None and a.packet_sha256 is None, 'CAL_PACKET_ABSENT')
            before = synthetic_before(descriptor)
            after = build_projection(before, descriptor, bindings, reports, now)
        else:
            need(type(a.packet) is str and type(a.packet_sha256) is str, 'PACKET_REQUIRED')
            packet = reader.ref(dict(path=a.packet, sha256=a.packet_sha256))
            need(packet['schema'] == 'REGISTRAR_V25_FOUR_CLAIM_TRANSITION_RUNTIME_PACKET_V2'
                 and packet['mode'] == a.mode and same(packet['subject'], dict(path=SUBJECT, sha256=PINS[SUBJECT]))
                 and same(packet['subject_specification'], dict(path=SUBJECT_SPEC, sha256=PINS[SUBJECT_SPEC]))
                 and same(packet['descriptor'], dict(path=DESCRIPTOR, sha256=PINS[DESCRIPTOR])), 'PACKET_SOURCE')
            reader.ref(packet['root_authority'])
            prerequisite(reader, packet['author'], 'author', a.source_sha256, a.spec_sha256)
            prerequisite(reader, packet['transition_calibration'], 'cal', a.source_sha256, a.spec_sha256)
            if a.mode == 'protected-copy':
                # Import is solely actual subject execution under the write barrier.
                # The independently authored projection functions above import no helpers.
                import importlib.util
                import os
                before = ledger(live_bytes)
                spec = importlib.util.spec_from_file_location('v25_protected_subject', ROOT / SUBJECT)
                subject = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(subject)
                reader.tick()
                dest = out / 'protected_copy'
                worker = binding_argv(expected_main_worker(str(dest).replace('\\', '/'), a.ledger_sha256), descriptor)
                original_replace, original_argv = os.replace, sys.argv
                def intercept(source, target):
                    nonlocal barriers
                    need(Path(target).resolve() == ROOT / 'CLAIMS.yaml'
                         and Path(source).resolve() == dest / 'CLAIMS.pending.yaml', 'SOLE_WRITE_BARRIER')
                    barriers += 1
                    need(barriers == 1, 'ONE_WRITE_BARRIER')
                    protected()
                    save('intercepted_report.json', copy.deepcopy(sys._getframe(1).f_locals['report']))
                    raise InterceptedWrite()
                try:
                    os.replace = intercept
                    sys.argv = worker[2:]
                    try:
                        subject.main()
                    except InterceptedWrite:
                        pass
                    else:
                        raise Reject('WRITE_BARRIER_NOT_REACHED')
                finally:
                    os.replace, sys.argv = original_replace, original_argv
                before_bytes = reader.bytes((dest / 'CLAIMS.before.yaml').relative_to(ROOT).as_posix())
                after_bytes = reader.bytes((dest / 'CLAIMS.after.yaml').relative_to(ROOT).as_posix())
                pending_bytes = reader.bytes((dest / 'CLAIMS.pending.yaml').relative_to(ROOT).as_posix())
                need(before_bytes == live_bytes and pending_bytes == after_bytes, 'COPY_LEDGER_BYTES')
                after = ledger(after_bytes)
                validation = raw_json(reader.bytes((dest / 'validation.json').relative_to(ROOT).as_posix()))
                need(validation['valid'] is True and validation['errors'] == [], 'COPY_VALIDATION')
                intercepted = raw_json(reader.bytes((out / 'intercepted_report.json').relative_to(ROOT).as_posix()))
                recorded = recorded_main_command(worker, descriptor)
                main_report(intercepted, a.ledger_sha256, hashlib.sha256(after_bytes).hexdigest(), after, a.expected_head, recorded)
            else:
                before_ref, after_ref = packet['main']['before'], packet['main']['after']
                prerequisite(reader, packet['protected_copy'], 'copy', a.source_sha256, a.spec_sha256, before_ref['sha256'])
                plan = reader.ref(packet['main']['plan'])
                manifest, terminal = reader.ref(packet['main']['manifest']), reader.ref(packet['main']['terminal'])
                runtime(plan, manifest, terminal)
                report = reader.ref(packet['main']['summary'])
                before_bytes = reader.bytes(before_ref['path'], before_ref['sha256'])
                after_bytes = reader.bytes(after_ref['path'], after_ref['sha256'])
                need(after_bytes == live_bytes and after_ref['sha256'] == a.ledger_sha256, 'MAIN_LEDGER_BYTES')
                worker = binding_argv(expected_main_worker(plan['output_root'], before_ref['sha256']), descriptor)
                need(same(plan['worker_argv'], worker) and same(plan['source'], dict(path=SUBJECT, sha256=PINS[SUBJECT]))
                     and same(plan['specification'], dict(path=SUBJECT_SPEC, sha256=PINS[SUBJECT_SPEC])), 'MAIN_LITERAL_WORKER')
                validation = reader.ref(packet['main']['validation'])
                need(validation['valid'] is True and validation['errors'] == [], 'MAIN_VALIDATION')
                before, after = ledger(before_bytes), ledger(after_bytes)
                recorded = recorded_main_command(worker, descriptor)
                main_report(report, before_ref['sha256'], after_ref['sha256'], after, a.expected_head, recorded)
        reader.tick()
        result = projection(before, after, descriptor, bindings, reports)
        closure = {}
        if a.mode != 'calibrate':
            for artifact in after['artifacts'][len(before['artifacts']):]:
                merge(closure, artifact['path'], artifact['sha256'])
            for path, identity in closure.items():
                reader.pin(path, identity)
        completed = controls(before, after, descriptor, bindings, reports, reader.tick)
        protected()
        save('controls.json', completed)
        save('projection.json', result)
        if a.mode == 'calibrate':
            save('synthetic.before.json', before)
            save('synthetic.after.json', after)
        for path in sorted(out.rglob('*')):
            if path.is_file():
                name = path.relative_to(ROOT).as_posix()
                outputs[path.relative_to(out).as_posix()] = hashlib.sha256(reader.bytes(name)).hexdigest()
        reader.closing()
        protected()
        save('summary.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), status=FAMILY + {
            'calibrate': 'CALIBRATION_PASS', 'protected-copy': 'PROTECTED_COPY_PASS', 'post': 'ACTUAL_POST_PASS'}[a.mode],
            implementation_version=2, source_sha256=a.source_sha256, spec_sha256=a.spec_sha256,
            checking_source_author='/root/checkpoint_audit', subject_adapter_author='/root/structural',
            actual_executor='ROOT_ONLY_BY_SEPARATE_AUTHORITY', method='engineering_typed_artifact_projection',
            independent_mathematical_approval=False, mode=a.mode, positive_controls=CONTROL_COUNTS['positive'],
            strict_negative_controls=CONTROL_COUNTS['negative'], projection=result, inputs_sha256=reader.inputs,
            outputs_sha256=outputs, unique_new_declared_artifacts_hashed=len(closure),
            registrar_main_called=a.mode == 'protected-copy', registrar_helpers_imported_by_projection=False,
            subject_imported_for_execution=a.mode == 'protected-copy', write_barriers=barriers,
            live_ledger_mutated=False, index_mutated=False, mathematical_replays=0, target_resolution='UNKNOWN',
            command=[sys.executable, *prior_argv], protected_HEAD=a.expected_head,
            protected_ledger_sha256=a.ledger_sha256, protected_index_sha256=a.index_sha256,
            limitations=['CP authored the plain focal discovery producer; this metadata projection reapproves no mathematical result.',
                'Projection parser/utility ancestry from452c is disclosed; registrar mapping functions are not imported by checking.',
                'All418 prior objects/all6054 PUBLIC tuples are preserved as typed ledger content; no old PUBLIC bulk or remote byte replay.',
                '60 finite cases preserve names/exact stages; full mutated memory objects are not all durable.',
                'Protected-copy subject execution/import is distinct from independently rebuilt projection checking.',
                'Atomic parsing, subject main and filesystem operations are not hard-real-time interruptible; require clean actual outer containment.'],
            deadline=clock.status()))
        protected()
    except BaseException as error:
        with (out / 'failure.json').open('x', encoding='utf8', newline='\n') as stream:
            json.dump(dict(timestamp=datetime.now(timezone.utc).isoformat(), error_type=type(error).__name__, message=str(error),
                controls=completed, inputs_sha256=reader.inputs, provisional_PASS_not_accepted=True, deadline=clock.status()),
                stream, indent=2, allow_nan=False)
            stream.write('\n')
        raise


if __name__ == '__main__':
    main()
