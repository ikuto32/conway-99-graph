"""Independent actual 356-to358 metadata impact; no registrar/math imports."""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import yaml
from command_deadline import CommandDeadline
from audit_20261003_wave37_transition_v1 import AuditError, need, save, transition
from audit_20261002_wave31_transition_v1 import UniqueLoader, indexed

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_wave41_transition_v2.py'
SPEC = 'acceleration/audit_20261003_wave41_transition_v2_spec.md'
REGISTRAR = 'acceleration/register_20261003_bound_claims_v16.py'
REGISTRAR_SHA = 'a8e7c2694817970df28ff1ec7be3d8265ba2f6e3ffe3d88798241832426c2026'
REGISTRAR_SPEC_SHA = '274bb9768c186225676f79ff8954a7d0a2832961d14f78d381f451b2898c8969'
BASELINE = 'a4f2f5b2ff41ea7aebf99413cdc825fc1e08f5269079d43e305da713f4af29ef'
GATE_SHA = 'ca0a4c7d9026cf314a7e08f352bc17543d861b071dbfadf6f9683454bba14b18'
GATE_TERMINAL_SHA = '6749776f6f617790c02fe9d1023f4d137c79f14d1567001981127b45a7417e34'
C4 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
RANK = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87'
N5 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT'
LOW67 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67'
LOW346 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
COMBINED_METHOD = 'independent_derivation_and_complete_artifact_checking'
BINDINGS = {
    C4: ('acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json',
         '6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee'),
    RANK: ('acceleration/results/20261003_triangle_rank87_binding01/claim_binding_schema2.json',
           'dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d'),
}
REPORTS = {C4: '75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5',
           RANK: '663c7fffc558e6a45232c08f272230970ff31bcc2d542e3f5c826aaa53dccbc9'}
CALIBRATIONS = {C4: 'e4ba5e7dbe927ce2b3c60b80600bb8436d9e6b47de2a87af784e9157853c27bf',
                RANK: '2a4b999a53075560dc4d38f0af4fd7d10b3aaa63086b5a2e6e56fc9ba709d9a8'}
PROOFS = {C4: 'bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12',
          RANK: 'd464ee1b3522a0e61784031b2f47efcc4ecf84926dcc64e306f6f2855e384ea0'}
STATEMENTS = {
    C4: 'For every finite simple graph with exactly one common neighbor for each adjacent pair, the binary triangle-incidence image contains at least max(ceil(P/2), P-c4(G)) weight-five words, where P is the unordered three-triangle path count and c4(G) the induced four-cycle count. Consequently any srg(99,14,1,2) has N5>=22869 and its exact degree-five kernel-character shifted right-hand side is71500275.',
    RANK: 'For every srg(99,14,1,2), its complete 99-by231 triangle-incidence matrix B has binary rank at least87: its binary kernel has size at most12187808/2723<8192, hence dimension at most12. This conditional implication allows the zero kernel and uses the even36..60 nonzero-weight interval and image counts N3>=231,N4>=2079,N5>=22869,N6>=24486.',
}


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def equal(left, right, stage):
    need(typed(left) == typed(right), stage)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def unique_yaml(text):
    try:
        return yaml.load(text, Loader=UniqueLoader)
    except ValueError as error:
        if str(error).startswith('duplicate YAML key '):
            raise AuditError('DUPLICATE_YAML_KEY', str(error)) from error
        raise


def unique_ids(records):
    try:
        return indexed(records)
    except ValueError as error:
        if str(error) == 'duplicate record ID':
            raise AuditError('DUPLICATE_RECORD_ID') from error
        raise


def evidence_closure(cid, binding):
    paths = {BINDINGS[cid][0]: BINDINGS[cid][1], binding['report']: binding['report_sha256']}
    for name, identity in binding['inputs_sha256'].items():
        need(name not in paths or paths[name] == identity, 'CONSISTENT_CLOSURE')
        paths[name] = identity
    for key in ('artifacts', 'evidence'):
        rows = binding.get(key, [])
        if type(rows) is dict:
            for label, name in rows.items():
                if not label.endswith('_sha256'):
                    need(label + '_sha256' in rows, 'PAIRED_EVIDENCE')
                    identity = rows[label + '_sha256']
                    need(name not in paths or paths[name] == identity, 'CONSISTENT_CLOSURE')
                    paths[name] = identity
        else:
            need(type(rows) is list, 'EVIDENCE_COLLECTION')
            for row in rows:
                if type(row) is dict and 'path' in row:
                    need(row['path'] not in paths or paths[row['path']] == row['sha256'], 'CONSISTENT_CLOSURE')
                    paths[row['path']] = row['sha256']
    return dict(paths=paths, controls=binding['controls'])


def report_scope(cid, binding, report):
    equal([binding['revision'], binding['claim_revision']], [1, 1], 'TYPED_BOUND_REVISION')
    equal([binding['id'], binding['status'], binding['review_state'], binding['producer'], binding['verifier'], binding['method']],
          [cid, 'VERIFIED', 'CLEAR', '/root/structural', '/root', 'independent_derivation'], 'EXACT_BOUND_ROLES')
    need(set(binding['scope']) == {'description', 'unrestricted_target', 'target_resolution'}
         and binding['scope']['unrestricted_target'] is True and binding['scope']['target_resolution'] == 'NONE', 'EXACT_BOUND_SCOPE')
    equal(binding['statement'], STATEMENTS[cid], 'EXACT_BOUND_STATEMENT')
    need(binding['report_sha256'] == REPORTS[cid] and type(binding['shared_components']) is list
         and len(binding['shared_components']) > 0, 'EXACT_BOUND_REPORT')
    equal([report['producer'], report['verifier'], report['method'], report['target_resolution'],
           report['claim_revision'], report['checker_implementation_version']],
          ['/root/structural', '/root', COMBINED_METHOD, 'NONE', 1, 3], 'EXACT_REPORT_ROLES')
    field = 'universal_statement' if cid == C4 else 'statement'
    equal(report[field], STATEMENTS[cid], 'EXACT_LITERAL_RAW_HEADLINE')
    need(binding['original_independent_report_method'] == COMBINED_METHOD
         and binding['written_audit_sha256'] == PROOFS[cid]
         and binding['controls']['independent_preoutput']['sha256'] == CALIBRATIONS[cid]
         and binding['premise_state'] == 'UNKNOWN', 'EXACT_PROOF_CONTROL_PREMISE')
    if cid == C4:
        need('statement' not in report, 'EXACT_C4_HEADLINE_FIELD')
        equal([report['status'], report['universal_derivation_checked'], report['rank_asserted'], report['graph_exclusions'],
               report['target_unordered_paths'], report['target_induced_c4_count'], report['target_weight5_lower_count'],
               report['target_character_rhs'], report['complete_original_fixtures'], report['complete_three_triangle_combinations'],
               report['unordered_paths'], report['separate_fixture_supports'], report['complete_induced_c4s'],
               report['complete_double_fibers'], report['complete_small_image_coefficient_masks'],
               report['complete_character_coefficients'], report['complete_normalized_weights'],
               report['strict_interface_corruptions'], report['actual_saved_strict_corruptions'],
               report['paired_relabel_map_checked'], report['numerical_solver_invocations']],
              ['INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS', True, False, 0,
               24948, 2079, 22869, 71500275, 7, 62, 23, 14, 10, 9, 234, 100, 99, 27, 18, True, 0], 'EXACT_C4_SCOPE')
        equal([{key:d[key] for key in ('id', 'revision', 'relation')} for d in binding['dependencies']],
              [dict(id=N5, revision=1, relation='uses_result')], 'EXACT_C4_DEPENDENCIES')
        need('previous target lower12474 is not treated as the strengthened count' in binding['dependencies'][0]['reason']
             and binding['kind'] == 'mathematical result' and binding['basis'] == ['DERIVED'], 'EXACT_C4_INVERSE_ONLY')
        need('exact_certificate' not in binding and binding['original_independent_report_statement_field'] == field,
             'EXACT_C4_OPTIONAL_METADATA')
    else:
        need('universal_statement' not in report, 'EXACT_RANK_HEADLINE_FIELD')
        equal([report['status'], report['weight_domain'], report['complete_exact_coefficients_checked'],
               report['complete_nonnegative_dual_coordinates_checked'], report['complete_exact_weight_inequalities_checked'],
               report['exact_size_upper'], report['maximum_linear_dimension'], report['conditional_incidence_rank_lower'],
               report['strict_corruptions'], report['complete_literal_characters'], report['lower_word_counts'],
               report['universal_conditional_derivation_checked'], report['optimum_asserted'], report['rank_upper_asserted'],
               report['nonzero_kernel_asserted'], report['graph_exclusions'], report['numerical_solver_invocations']],
              ['INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_COMPLETE_DUAL_V1_PASS', 'even13', 1287, 99, 13,
               [12187808, 2723], 12, 87, 34, 140, {'3':231, '4':2079, '5':22869, '6':24486},
               True, False, False, False, 0, 0], 'EXACT_RANK87_SCOPE')
        equal([{key:d[key] for key in ('id', 'revision', 'relation')} for d in binding['dependencies']],
              [dict(id=LOW67, revision=1, relation='uses_result'), dict(id=LOW346, revision=1, relation='uses_result'),
               dict(id=C4, revision=1, relation='uses_result')], 'EXACT_RANK87_DEPENDENCIES')
        equal(report['exact_endpoint_system'], binding['exact_certificate']['endpoint_system'], 'EXACT_ENDPOINT_SYSTEM')
        need(binding['exact_certificate']['sha256'] == 'fcff92d4b47c53838f1e9532f6953bed120fef0eb40610cc258555deeafd609f'
             and binding['basis'] == ['DERIVED', 'COMPUTED'] and binding['kind'] == 'mathematical result'
             and 'not rank67' in binding['dependencies'][0]['reason'], 'EXACT_EVEN_INTERVAL_ONLY')
        need('original_independent_report_statement_field' not in binding, 'EXACT_RANK_OPTIONAL_METADATA')


def mappings(bindings, reports):
    result = {}
    for cid, binding in bindings.items():
        field = 'universal_statement' if cid == C4 else 'statement'
        equal(reports[cid][field], binding['statement'], 'EXACT_LITERAL_RAW_HEADLINE')
        result[cid] = dict(claim_id=cid, claim_revision=1,
            original_report=binding['report'], original_report_sha256=REPORTS[cid],
            original_report_statement_field=field, original_report_statement=reports[cid][field],
            recorded_binding=BINDINGS[cid][0], recorded_binding_sha256=BINDINGS[cid][1],
            recorded_binding_statement=binding['statement'],
            recorded_binding_statement_sha256=hashlib.sha256(binding['statement'].encode('utf8')).hexdigest(),
            original_independent_report_method=COMBINED_METHOD, schema_method='independent_derivation',
            original_written_audit=binding['written_audit'], original_written_audit_sha256=PROOFS[cid],
            original_calibration=binding['controls']['independent_preoutput']['path'],
            original_calibration_sha256=CALIBRATIONS[cid],
            reason='Exact two-ID metadata projection preserves the existing literal raw headline and combined independent derivation/artifact method. The schema records independent_derivation and retains the original method here. Universal mathematics and exact certificates were already checked by ROOT; this registrar does not replay them or infer any wider result.',
            raw_statement_changed=False, mathematical_replays=0, target_resolution='NONE')
    return result


def checked_transition(before, after, bindings, gold, mapping):
    equal(after['claims'][:len(before['claims'])], before['claims'], 'TYPED_PRIOR_CLAIMS')
    equal(after['artifacts'][:len(before['artifacts'])], before['artifacts'], 'TYPED_PRIOR_ARTIFACTS')
    for key in set(before) | set(after):
        if key not in ('claims', 'artifacts', 'updated_at'):
            equal(before.get(key), after.get(key), 'TYPED_TARGET_TOPLEVEL')
    claims = unique_ids(after['claims']); unique_ids(after['artifacts'])
    need(list(claims)[len(before['claims']):] == list(BINDINGS), 'EXACT_NEW_ORDER')
    for cid, binding in bindings.items():
        claim = claims[cid]
        for key in ('id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state', 'assumptions', 'limitations', 'scope'):
            equal(claim[key], binding[key], 'TYPED_BOUND_' + key)
        equal(claim['dependencies'], [{key:d[key] for key in ('id', 'revision', 'relation')} for d in binding['dependencies']],
              'TYPED_DEPENDENCIES')
        need(type(claim['verification'][0]['claim_revision']) is int, 'TYPED_VERIFICATION_REVISION')
        for dependency in claim['dependencies']:
            need(dependency['id'] in claims and claims[dependency['id']]['revision'] == dependency['revision'], 'RESOLVING_DEPENDENCY')
        equal(json.loads(claim['unknowns']['editorial_statement_mapping']), mapping[cid], 'EXACT_LITERAL_METHOD_MAPPING')
    transition(before, after, BINDINGS, bindings, gold)
    return claims


def synthetic(bindings, gold, mapping):
    names = [N5, LOW67, LOW346]
    before = dict(schema_version=2, updated_at='2026-10-03T00:00:00+00:00',
        claims=[dict(id=names[i] if i < 3 else 'ENGINEERING_ONLY_' + str(i), revision=1, status='UNKNOWN', review_state='CLEAR') for i in range(356)],
        artifacts=[dict(id='old-public-control', path='synthetic-only', sha256='1'*64, availability='PUBLIC')],
        target=dict(status='UNKNOWN', overall_search_coverage=None))
    after = copy.deepcopy(before)
    for cid, binding in bindings.items():
        evidence = []; hashes = {}
        for i, (path, identity) in enumerate(sorted(gold[cid]['paths'].items())):
            aid = 'fixture-' + cid + '-' + str(i); evidence.append(aid); hashes[aid] = identity
            after['artifacts'].append(dict(id=aid, path=path, sha256=identity, availability='LOCAL_ONLY'))
        notes = [{key:d[key] for key in ('id', 'revision', 'reason')} for d in binding['dependencies'] if 'reason' in d]
        claim = {key:copy.deepcopy(binding[key]) for key in ('id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state', 'assumptions', 'limitations', 'scope')}
        claim.update(dependencies=[{key:d[key] for key in ('id', 'revision', 'relation')} for d in binding['dependencies']],
            evidence=evidence, external_source=None, created_at=before['updated_at'], updated_at=before['updated_at'],
            unknowns=dict(dependency_notes=json.dumps(notes), premises=json.dumps(binding['premise_state']),
                original_binding_method=binding['method'], original_binding_kind=binding['kind'],
                original_binding_scope='No schema projection; binding uses the schema scope fields directly.',
                editorial_statement_mapping=json.dumps(mapping[cid])),
            verification=[dict(claim_revision=1, verifier=binding['verifier'], method=binding['method'], outcome='PASS',
                timestamp=binding['verification_timestamp'], command_or_audit=binding['report'], scope=binding['scope']['description'],
                limitations=binding['limitations'], shared_components=binding['shared_components'],
                controls=[json.dumps(gold[cid]['controls'])], artifact_hashes=hashes)],
            reproducibility=dict(manifest=next(aid for aid in evidence if indexed(after['artifacts'])[aid]['path'] == binding['report'])))
        after['claims'].append(claim)
    return before, after


def controls(bindings, reports, gold, mapping):
    before, after = synthetic(bindings, gold, mapping)
    checked_transition(before, after, bindings, gold, mapping)
    records = [dict(label='complete_synthetic356to358', outcome='PASS')]
    def reject(label, stage, call):
        try:
            call()
        except AuditError as error:
            need(error.stage == stage, 'PRECISE_CONTROL_STAGE', str(error))
            records.append(dict(label=label, outcome='REJECTED', diagnostic=error.stage)); return
        raise AuditError('CORRUPTION_ACCEPTED', label)
    def claim(value, cid=C4): return indexed(value['claims'])[cid]
    changes = [
        ('prior_revision_bool', 'TYPED_PRIOR_CLAIMS', lambda x:x['claims'][0].update(revision=True)),
        ('prior_status', 'TYPED_PRIOR_CLAIMS', lambda x:x['claims'][1].update(status='VERIFIED')),
        ('prior_PUBLIC_availability', 'TYPED_PRIOR_ARTIFACTS', lambda x:x['artifacts'][0].update(availability='LOCAL_ONLY')),
        ('target_promotion', 'TYPED_TARGET_TOPLEVEL', lambda x:x['target'].update(status='VERIFIED')),
        ('dependency_order_reversed', 'EXACT_NEW_ORDER', lambda x:x['claims'].__setitem__(slice(-2, None), list(reversed(x['claims'][-2:])))),
        ('new_revision_float', 'TYPED_BOUND_revision', lambda x:claim(x).update(revision=1.0)),
        ('c4_claim_broadened', 'TYPED_BOUND_statement', lambda x:claim(x).update(statement='Every graph has N5>=22869')),
        ('rank_contradiction', 'TYPED_BOUND_statement', lambda x:claim(x, RANK).update(statement='No target exists')),
        ('new_kind_changed', 'TYPED_BOUND_kind', lambda x:claim(x).update(kind='exclusion')),
        ('new_basis_changed', 'TYPED_BOUND_basis', lambda x:claim(x).update(basis=['CITED'])),
        ('new_review_quarantined', 'TYPED_BOUND_review_state', lambda x:claim(x).update(review_state='QUARANTINED')),
        ('lost_lambda1_premise', 'TYPED_BOUND_assumptions', lambda x:claim(x).update(assumptions=[])),
        ('scope_bool_as_integer', 'TYPED_BOUND_scope', lambda x:claim(x, RANK)['scope'].update(unrestricted_target=1)),
        ('scope_target_resolution', 'TYPED_BOUND_scope', lambda x:claim(x)['scope'].update(target_resolution='NONEXISTENCE')),
        ('lost_kernel_limitations', 'TYPED_BOUND_limitations', lambda x:claim(x, RANK).update(limitations=[])),
        ('wrong_dependency_relation', 'TYPED_DEPENDENCIES', lambda x:claim(x, RANK)['dependencies'][0].update(relation='premise')),
        ('wrong_dependency_revision', 'TYPED_DEPENDENCIES', lambda x:claim(x, RANK)['dependencies'][0].update(revision=1.0)),
        ('lost_interval_only_reason', 'BOUND_DEPENDENCY_REASON', lambda x:claim(x, RANK)['unknowns'].update(dependency_notes='[]')),
        ('premise_VERIFIED', 'BOUND_PREMISE_STATE', lambda x:claim(x, RANK)['unknowns'].update(premises='"VERIFIED"')),
        ('self_approval', 'BOUND_VERIFICATION_ROLE_METHOD', lambda x:claim(x)['verification'][0].update(verifier='/root/structural')),
        ('method_broadening', 'BOUND_VERIFICATION_ROLE_METHOD', lambda x:claim(x)['verification'][0].update(method='external_review')),
        ('missing_shared_components', 'BOUND_SHARED_COMPONENTS', lambda x:claim(x)['verification'][0].update(shared_components=[])),
        ('missing_control_record', 'BOUND_CONTROLS', lambda x:claim(x)['verification'][0].update(controls=[])),
        ('new_PUBLIC_promotion', 'NO_UNCONFIRMED_PUBLIC_PROMOTION', lambda x:x['artifacts'][-1].update(availability='PUBLIC')),
        ('missing_evidence', 'COMPLETE_EXACT_BOUND_EVIDENCE', lambda x:claim(x)['evidence'].pop()),
        ('changed_evidence_hash', 'EXACT_REVISION_HASH_BINDING', lambda x:claim(x)['verification'][0]['artifact_hashes'].update({claim(x)['evidence'][0]:'0'*64})),
        ('bool_verification_revision', 'TYPED_VERIFICATION_REVISION', lambda x:claim(x, RANK)['verification'][0].update(claim_revision=True)),
        ('c4_mapping_changed', 'EXACT_LITERAL_METHOD_MAPPING', lambda x:claim(x)['unknowns'].update(editorial_statement_mapping='{}')),
        ('rank_mapping_changed', 'EXACT_LITERAL_METHOD_MAPPING', lambda x:claim(x, RANK)['unknowns'].update(editorial_statement_mapping='{}')),
        ('unbound_new_artifact', 'NO_UNBOUND_NEW_ARTIFACTS', lambda x:x['artifacts'].append(dict(id='unbound', path='unbound', sha256='0'*64, availability='LOCAL_ONLY'))),
        ('duplicate_new_claim', 'DUPLICATE_RECORD_ID', lambda x:x['claims'].append(copy.deepcopy(x['claims'][-1]))),
        ('duplicate_artifact', 'DUPLICATE_RECORD_ID', lambda x:x['artifacts'].append(copy.deepcopy(x['artifacts'][-1]))),
    ]
    for label, stage, change in changes:
        bad = copy.deepcopy(after); change(bad)
        reject(label, stage, lambda bad=bad:checked_transition(before, bad, bindings, gold, mapping))
    report_changes = [
        (C4, 'universal_derivation_checked', 1, 'EXACT_C4_SCOPE'),
        (C4, 'target_weight5_lower_count', 12474, 'EXACT_C4_SCOPE'),
        (C4, 'graph_exclusions', False, 'EXACT_C4_SCOPE'),
        (C4, 'complete_double_fibers', 9.0, 'EXACT_C4_SCOPE'),
        (C4, 'paired_relabel_map_checked', False, 'EXACT_C4_SCOPE'),
        (RANK, 'conditional_incidence_rank_lower', 87.0, 'EXACT_RANK87_SCOPE'),
        (RANK, 'weight_domain', 'div4seven', 'EXACT_RANK87_SCOPE'),
        (RANK, 'exact_size_upper', [12187809, 2723], 'EXACT_RANK87_SCOPE'),
        (RANK, 'maximum_linear_dimension', 13, 'EXACT_RANK87_SCOPE'),
        (RANK, 'optimum_asserted', 0, 'EXACT_RANK87_SCOPE'),
        (RANK, 'nonzero_kernel_asserted', True, 'EXACT_RANK87_SCOPE'),
        (RANK, 'method', 'independent_derivation', 'EXACT_REPORT_ROLES'),
        (C4, 'universal_statement', 'Invented stronger statement', 'EXACT_LITERAL_RAW_HEADLINE'),
        (C4, 'statement', STATEMENTS[C4], 'EXACT_C4_HEADLINE_FIELD'),
        (RANK, 'universal_statement', STATEMENTS[RANK], 'EXACT_RANK_HEADLINE_FIELD'),
    ]
    for cid, key, value, stage in report_changes:
        bad = copy.deepcopy(reports[cid]); bad[key] = value
        reject('report_' + key, stage, lambda bad=bad,cid=cid:report_scope(cid, bindings[cid], bad))
    for label, stage, change in [
        ('binding_boolean_revision', 'TYPED_BOUND_REVISION', lambda x:x.update(revision=True)),
        ('binding_self_verifier', 'EXACT_BOUND_ROLES', lambda x:x.update(verifier='/root/structural')),
        ('binding_wrong_statement', 'EXACT_BOUND_STATEMENT', lambda x:x.update(statement='Stronger unrecorded theorem')),
        ('binding_wrong_report_hash', 'EXACT_BOUND_REPORT', lambda x:x.update(report_sha256='0'*64)),
        ('binding_wrong_proof_hash', 'EXACT_PROOF_CONTROL_PREMISE', lambda x:x.update(written_audit_sha256='0'*64)),
    ]:
        bad = copy.deepcopy(bindings[C4]); change(bad)
        reject(label, stage, lambda bad=bad:report_scope(C4, bad, reports[C4]))
    reject('duplicate_yaml_key', 'DUPLICATE_YAML_KEY', lambda:unique_yaml('a: 1\na: 2\n'))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['calibrate', 'check'], required=True)
    parser.add_argument('--seconds', type=float, required=True); parser.add_argument('--out', required=True)
    fields = ('calibration', 'registration_summary', 'after_ledger', 'supervision_summary', 'supervision_manifest',
              'engineering_gate', 'engineering_terminal')
    for field in fields:
        parser.add_argument('--' + field.replace('_', '-')); parser.add_argument('--' + field.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent356to358 exact metadata impact and typed controls;150worker20save reserve;no registrar imports/math replay')
    out = (ROOT / args.out).resolve(); need(out.is_relative_to(ROOT), 'OUTPUT_BOUNDARY'); out.mkdir(parents=True, exist_ok=False)
    pins = {}; protected = {name:digest(ROOT/name) for name in ('CLAIMS.yaml', '.git/index')}
    def pin(name, wanted=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
        path = (ROOT/name).resolve(); need(path.is_relative_to(ROOT), 'INPUT_BOUNDARY')
        identity = digest(path); need(wanted is None or identity == wanted, 'INPUT_HASH', name)
        need(name not in pins or pins[name] == identity, 'INPUT_STABLE'); pins[name] = identity; return identity
    def read(name, wanted=None):
        pin(name, wanted); return json.loads((ROOT/name).read_bytes())
    try:
        for name in (SOURCE, SPEC, 'pyproject.toml', 'uv.lock', 'acceleration/command_deadline.py', 'acceleration/run_compute_command.py',
                     'acceleration/audit_20261003_wave40_transition_v1.py', 'acceleration/audit_20261003_wave40_transition_v1_spec.md'):
            pin(name)
        pin('acceleration/audit_20261003_wave37_transition_v1.py', '2dddfc6aa574692f45f1cf02e1f62d0793681687e1ff80b316bb967acb4c6a67')
        pin('acceleration/audit_20261002_wave31_transition_v1.py', '5cdb4a68f14d19f97f6326d0fd594e84e8ca732c10225207b9a1b10f29e7b75e')
        bindings = {cid:read(*pair) for cid,pair in BINDINGS.items()}
        reports = {cid:read(binding['report'], REPORTS[cid]) for cid,binding in bindings.items()}
        gold = {cid:evidence_closure(cid,binding) for cid,binding in bindings.items()}
        for cid in bindings: report_scope(cid, bindings[cid], reports[cid])
        mapping = mappings(bindings, reports); tested = controls(bindings, reports, gold, mapping)
        save(out/'controls.json', tested); save(out/'expected_literal_method_mappings.json', mapping)
        outcome = dict(status='INDEPENDENT_WAVE41_TYPED_TRANSITION_V2_CALIBRATION_PASS', actual_transition_inspected=False)
        if args.mode == 'check':
            for field in fields:
                need(getattr(args, field) and getattr(args, field + '_sha256'), 'EXPLICIT_ACTUAL_IDENTITIES', field)
            cal = read(args.calibration, args.calibration_sha256)
            need(cal['status'] == 'INDEPENDENT_WAVE41_TYPED_TRANSITION_V2_CALIBRATION_PASS'
                 and cal['actual_transition_inspected'] is False, 'PREACTUAL_CALIBRATION')
            need(all(cal['inputs_sha256'].get(name) == identity for name,identity in pins.items() if name != args.calibration), 'EXACT_CALIBRATED_INPUTS')
            for name, identity in cal['inputs_sha256'].items(): pin(name, identity)
            pin(REGISTRAR, REGISTRAR_SHA); pin(REGISTRAR.replace('.py', '_spec.md'), REGISTRAR_SPEC_SHA)
            need(args.engineering_gate_sha256 == GATE_SHA and args.engineering_terminal_sha256 == GATE_TERMINAL_SHA, 'EXACT_ENGINEERING_IDENTITIES')
            gate = read(args.engineering_gate, GATE_SHA)
            equal([gate['status'], gate['producer'], gate['verifier'], gate['method'], gate['claims_before'], gate['claims_after'],
                   gate['status_counts'], gate['ledger_mutated'], gate['index_mutated'], gate['mathematical_replays']],
                  ['INDEPENDENT_REGISTRAR_V16_TWO_EXACT_BINDINGS_ENGINEERING_PASS', '/root/checkpoint_audit', '/root',
                   'independent_engineering_artifact_check', 356, 358, {'VERIFIED':350, 'CANDIDATE':3, 'REFUTED':5}, False, False, 0], 'EXACT_ENGINEERING_GATE')
            need(gate['inputs_sha256'].get(REGISTRAR) == REGISTRAR_SHA
                 and gate['inputs_sha256'].get(REGISTRAR.replace('.py', '_spec.md')) == REGISTRAR_SPEC_SHA, 'ENGINEERING_SOURCE_PINS')
            for name,identity in gate['inputs_sha256'].items(): pin(name,identity)
            engineering_terminal = read(args.engineering_terminal, GATE_TERMINAL_SHA)
            equal([engineering_terminal['command_exit_code'], engineering_terminal['error'], engineering_terminal['deadline_reached'],
                   engineering_terminal['cleanup']['reaped'], engineering_terminal['cleanup']['job_active_zero_observed'],
                   engineering_terminal['cleanup']['cleanup_errors']], [0, None, False, True, True, []], 'ENGINEERING_EMPTY_JOB')
            summary = read(args.registration_summary, args.registration_summary_sha256)
            directory = (ROOT/args.registration_summary).parent
            before_path = (directory/'CLAIMS.before.yaml').relative_to(ROOT).as_posix()
            pin(before_path, BASELINE); before = unique_yaml((ROOT/before_path).read_text(encoding='utf8'))
            pin(args.after_ledger, args.after_ledger_sha256); after = unique_yaml((ROOT/args.after_ledger).read_text(encoding='utf8'))
            claims = checked_transition(before, after, bindings, gold, mapping)
            need(len(before['claims']) == 356 and len(claims) == 358, 'EXACT_CLAIM_POPULATION')
            equal(dict(Counter(claim['status'] for claim in claims.values())), {'VERIFIED':350, 'CANDIDATE':3, 'REFUTED':5}, 'EXACT_STATUS_POPULATION')
            need(all(claim['review_state'] == 'CLEAR' for claim in claims.values()), 'EXACT_REVIEW_POPULATION')
            expected = [summary['command'][0], REGISTRAR, '--out', directory.relative_to(ROOT).as_posix(), '--previous-sha256', BASELINE]
            for pair in BINDINGS.values(): expected += ['--binding', pair[0], '--binding-sha256', pair[1]]
            need(Path(expected[0]).resolve() == Path(sys.executable).resolve(), 'DIRECT_LOCKED_PYTHON')
            equal(summary['command'], expected, 'EXACT_REGISTRAR_ARGV')
            equal([summary['status'], summary['before_ledger_sha256'], summary['ledger_sha256'], summary['source_sha256'],
                   summary['new_claim_ids'], summary['claim_records'], summary['mathematical_replays'], summary['new_exclusions'],
                   summary['target_resolution'], summary['editorial_statement_mappings']],
                  ['EXACT_BOUND_SCOPED_CLAIMS_REGISTERED', BASELINE, args.after_ledger_sha256, REGISTRAR_SHA,
                   list(BINDINGS), 358, 0, 0, 'UNKNOWN', list(mapping.values())], 'EXACT_ACTUAL_REGISTRATION_REPORT')
            terminal = read(args.supervision_summary, args.supervision_summary_sha256)
            launch = read(args.supervision_manifest, args.supervision_manifest_sha256)
            need(Path(launch['command'][0]).resolve() == Path(expected[0]).resolve(), 'DIRECT_SUPERVISOR_PYTHON')
            equal(launch['command'][1:], ['-B', *expected[1:]], 'EXACT_SUPERVISOR_ARGV')
            need(launch['seconds'] == 180 and launch['shutdown_reserve_seconds'] == 30
                 and terminal['invocation_id'] == launch['invocation_id'], 'EXACT_REGISTRATION_CONTAINMENT')
            equal([terminal['command_exit_code'], terminal['error'], terminal['deadline_reached'], terminal['cleanup']['reaped'],
                   terminal['cleanup']['job_active_zero_observed'], terminal['cleanup']['cleanup_errors']],
                  [0, None, False, True, True, []], 'ACTUAL_EMPTY_JOB')
            for record in gold.values():
                for name,identity in record['paths'].items(): pin(name,identity)
            need(digest(ROOT/'CLAIMS.yaml') == args.after_ledger_sha256, 'LIVE_AFTER_HASH')
            equal(unique_yaml((ROOT/'CLAIMS.yaml').read_text(encoding='utf8')), after, 'LIVE_AFTER_MATCH')
            outcome = dict(status='INDEPENDENT_WAVE41_EXACT356_TO358_TRANSITION_V2_PASS', actual_transition_inspected=True,
                before_ledger_sha256=BASELINE, after_ledger_sha256=args.after_ledger_sha256, unchanged_prior_claims=356, current_claims=358,
                new_claim_ids=list(BINDINGS), status_counts={'VERIFIED':350,'CANDIDATE':3,'REFUTED':5}, review_counts={'CLEAR':358},
                prior_claims_artifacts_target_unchanged=True, new_exclusions=0, new_unrestricted_exclusions=0,
                exact_literal_method_mappings=mapping, terminal_record=dict(path=args.supervision_summary,
                    sha256=args.supervision_summary_sha256, elapsed_seconds=terminal['elapsed_seconds'], exit_code=0, reaped=True, job_empty=True))
        need(all(digest(ROOT/name) == identity for name,identity in protected.items()), 'PROTECTED_STATE_UNCHANGED')
        save(out/'summary.json', dict(**outcome, timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root/checkpoint_audit',
            method='independent_artifact_check', checker_implementation_version=2, inputs_sha256=pins,
            command=[sys.executable,*sys.argv], cwd=str(ROOT), python=platform.python_version(),
            positive_controls=1, strict_negative_controls=len(tested)-1, mathematical_replays=0, registrar_imports=0,
            ledger_mutations=0, index_mutations=0, target_resolution='UNKNOWN', historical_protected_execution_state=protected,
            deadline=deadline.status(), shared_components=[
                'Prior independently authored Wave37 evidence projection and Wave31 unique YAML/ID parser; new typed equality, exact two-claim semantics and corruption controls.',
                'Preserved Wave40 source supplied the metadata-checking design only; neither registrar subject nor mathematical discovery/checker code is imported.',
                'Python JSON/YAML/SHA256, locked environment, deadline and supported containment trusted.',
                'This verifier authored the V16 metadata registrar. ROOT separately independently gated that subject; this raw transition path does not import it or approve discovery mathematics.'],
            limitations=[
                'Metadata impact only; does not independently reapprove ROOT mathematics, recheck universal derivations or replay exact certificates.',
                'Preserves every prior material claim, verification and artifact field, including PUBLIC availability; new evidence remains LOCAL_ONLY.',
                'Both original report headlines are literal and nonnull; only combined-method schema projection is recorded, with no generic statement exception.',
                'C4 bound and rank87 are necessary conditional results, compatible with the zero kernel; no graph, exclusion, upper rank, numerical optimum or external review.']))
        print(outcome['status'])
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), stage=getattr(error,'stage',None), inputs_sha256=pins,
            outputs_preserved=True, live_mutations=False, deadline=deadline.status()))
        raise


if __name__ == '__main__': main()
