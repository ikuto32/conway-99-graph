"""Independent exact 353-to356 metadata impact; no registrar imports or math replay."""
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
SOURCE = 'acceleration/audit_20261003_wave40_transition_v1.py'
SPEC = 'acceleration/audit_20261003_wave40_transition_v1_spec.md'
REGISTRAR = 'acceleration/register_20261003_bound_claims_v15.py'
REGISTRAR_SHA = '0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9'
REGISTRAR_SPEC_SHA = '4b3998133dde62d10bfdd36d53377b66bebefd095905805d5ae19214c8f954b2'
BASELINE = '4b64876083f128382f48335a9b7e3cec08c56e0c1eb90aa24461901860e848da'
N5 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT'
PILOT = 'C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS'
RANK = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86'
LOW67 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67'
LOW346 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
BINDINGS = {
    N5: ('acceleration/results/20261003_triangle_image_weight5_binding01/claim_binding_schema2.json',
         'e816aff2942094e61efc2652acc222fa5de8f60b9b2435c81750a4ba19e65ea7'),
    PILOT: ('acceleration/results/20261003_root_focused_pilot_binding01/claim_binding_schema2.json',
            'b160388913cc014a2ea1d8a407a150e657078cd9c81ad6333378eac633c4de2f'),
    RANK: ('acceleration/results/20261003_triangle_rank86_binding01/claim_binding_schema2.json',
           '5d1aa5266a8dd3aaee40e8bdb4f8c10c2093d92969c1f29bdb03587080cec831'),
}
REPORTS = {
    N5: 'dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2',
    PILOT: '7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558',
    RANK: '3cc0ae7fbd0d340c00a4b1e3b00221ef70df6767812b846875a9483413745674',
}
ROLES = {N5: ('/root/structural', '/root/checkpoint_audit', 'independent_derivation'),
         PILOT: ('/root/native_driver', '/root/checkpoint_audit', 'independent_artifact_check'),
         RANK: ('/root/structural', '/root', 'independent_artifact_check')}


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
    need(type(binding['revision']) is int and binding['revision'] == 1
         and type(binding['claim_revision']) is int and binding['claim_revision'] == 1, 'TYPED_BOUND_REVISION')
    need(binding['id'] == cid and binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and (binding['producer'], binding['verifier'], binding['method']) == ROLES[cid], 'EXACT_BOUND_ROLES')
    need(set(binding['scope']) == {'description', 'unrestricted_target', 'target_resolution'}
         and binding['scope']['unrestricted_target'] is (cid != PILOT)
         and binding['scope']['target_resolution'] == 'NONE', 'EXACT_BOUND_SCOPE')
    need(binding['report_sha256'] == REPORTS[cid] and isinstance(binding['shared_components'], list), 'EXACT_BOUND_REPORT')
    need((report['producer'], report['verifier'], report['method']) == ROLES[cid]
         and report['target_resolution'] == 'NONE', 'EXACT_REPORT_ROLES')
    if cid == N5:
        equal([report['status'], report['universal_derivation_checked'], report['rank_bound_claimed'],
               report['new_exclusions'], report['target_unordered_paths'], report['target_weight5_lower_count']],
              ['INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS', True, False, 0, 24948, 12474], 'EXACT_N5_SCOPE')
        equal(report['statement'], binding['statement'], 'EXACT_N5_LITERAL_STATEMENT')
        need(binding['dependencies'] == [] and binding['kind'] == 'mathematical result'
             and binding['basis'] == ['DERIVED'], 'EXACT_N5_DEPENDENCIES')
    elif cid == PILOT:
        need('statement' not in report, 'ABSENT_RAW_HEADLINE')
        equal([report['status'], report['saved_state_files'], report['saved_states'], report['saved_trace_records'],
               report['complete_anchored_proposals'], report['locally_checked_global_gaps'],
               report['saved_selected_object_files'], report['saved_localzero_object_observations'],
               report['zero_target_candidates'], report['native_reported_proposals'], report['complete_trajectory_checked']],
              ['INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS', 102, 101, 10099, 10099, 0, 0, 0, 0, 10000000, False],
              'EXACT_PILOT_SCOPE')
        equal(binding['recorded_validation']['current'], dict(Froot=10, E_lambda=0, Rroot=10, E_mu=5476, identity_mismatches=5500), 'EXACT_PILOT_CURRENT')
        equal(binding['recorded_validation']['best_root'], dict(Froot=10, E_lambda=0, Rroot=10, E_mu=5520, identity_mismatches=5580), 'EXACT_PILOT_BEST')
        need(binding['dependencies'] == [] and binding['kind'] == 'empirical/engineering result'
             and binding['basis'] == ['COMPUTED'], 'EXACT_PILOT_DEPENDENCIES')
    else:
        need('statement' not in report, 'ABSENT_RAW_HEADLINE')
        equal([report['status'], report['weight_domain'], report['complete_exact_coefficients_checked'],
               report['complete_nonnegative_dual_coordinates_checked'], report['complete_exact_weight_inequalities_checked'],
               report['exact_size_upper'], report['maximum_linear_dimension'], report['conditional_incidence_rank_lower'],
               report['actual_strict_corruption_controls'], report['lower_word_counts'], report['optimum_asserted']],
              ['INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_COMPLETE_DUAL_V2_PASS', 'even13', 1287, 99, 13,
               [97502464, 9739], 13, 86, 10, {'3':231, '4':2079, '5':12474, '6':24486}, False], 'EXACT_RANK86_SCOPE')
        equal([{key: dependency[key] for key in ('id','revision','relation')} for dependency in binding['dependencies']],
              [dict(id=LOW67, revision=1, relation='uses_result'), dict(id=LOW346, revision=1, relation='uses_result'),
               dict(id=N5, revision=1, relation='uses_result')], 'EXACT_RANK86_DEPENDENCIES')
        need(binding['premise_state'] == 'UNKNOWN' and 'rank67 is not a premise' in binding['dependencies'][0]['reason']
             and binding['kind'] == 'mathematical result' and binding['basis'] == ['DERIVED','COMPUTED'], 'EXACT_WEIGHT_ONLY_PREMISE')


def mappings(bindings, reports):
    result = {}
    reasons = {
        PILOT: 'Exact frozen saved-object statement projects the pinned checkpoint full artifact report and object_audits; raw summary has no statement field. Native proposal counter is authenticated metadata, not a complete-trajectory verification. Adapter author also authored the native engine; this performs bookkeeping only and requires independent registrar engineering review.',
        RANK: 'Exact frozen conditional theorem statement is an editorial projection of the pinned ROOT even13 certificate and written derivation. Original raw report has no statement field; no generic semantic inference, optimum or target resolution is admitted.'}
    for cid in (PILOT, RANK):
        binding = bindings[cid]
        need('statement' not in reports[cid], 'ABSENT_RAW_HEADLINE')
        result[cid] = dict(claim_id=cid, original_report=binding['report'], original_report_sha256=REPORTS[cid],
            original_report_statement=None,
            original_report_statement_null_reason='Pinned original report has no statement field; its independently checked literal results remain unchanged.',
            recorded_binding=BINDINGS[cid][0], recorded_binding_sha256=BINDINGS[cid][1],
            recorded_binding_statement=binding['statement'],
            recorded_binding_statement_sha256=hashlib.sha256(binding['statement'].encode('utf8')).hexdigest(),
            reason=reasons[cid], mathematical_replays=0, target_resolution='NONE')
    return result


def checked_transition(before, after, bindings, gold, mapping):
    equal(after['claims'][:len(before['claims'])], before['claims'], 'TYPED_PRIOR_CLAIMS')
    equal(after['artifacts'][:len(before['artifacts'])], before['artifacts'], 'TYPED_PRIOR_ARTIFACTS')
    for key in set(before) | set(after):
        if key not in ('claims','artifacts','updated_at'):
            equal(before.get(key), after.get(key), 'TYPED_TARGET_TOPLEVEL')
    claims = indexed(after['claims'])
    need(list(claims)[len(before['claims']):] == list(BINDINGS), 'EXACT_NEW_ORDER')
    for cid, binding in bindings.items():
        claim = claims[cid]
        for key in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations','scope'):
            equal(claim[key], binding[key], 'TYPED_BOUND_' + key)
        equal(claim['dependencies'], [{k:d[k] for k in ('id','revision','relation')} for d in binding['dependencies']], 'TYPED_DEPENDENCIES')
        need(type(claim['verification'][0]['claim_revision']) is int, 'TYPED_VERIFICATION_REVISION')
        for dependency in claim['dependencies']:
            need(dependency['id'] in claims and claims[dependency['id']]['revision'] == dependency['revision'], 'RESOLVING_DEPENDENCY')
    transition(before, after, BINDINGS, bindings, gold)
    need('editorial_statement_mapping' not in claims[N5]['unknowns'], 'ONLY_TWO_HEADLINE_MAPPINGS')
    for cid in (PILOT, RANK):
        equal(json.loads(claims[cid]['unknowns']['editorial_statement_mapping']), mapping[cid], 'EXACT_NULL_HEADLINE_MAPPING')
    return claims


def synthetic(bindings, gold, mapping):
    before = dict(schema_version=2, updated_at='2026-10-03T00:00:00+00:00',
        claims=[dict(id=LOW67 if i==0 else LOW346 if i==1 else 'ENGINEERING_ONLY_' + str(i), revision=1, status='UNKNOWN', review_state='CLEAR') for i in range(353)],
        artifacts=[dict(id='old-public-control', path='unexecuted-synthetic-only', sha256='1'*64, availability='PUBLIC')],
        target=dict(status='UNKNOWN', overall_search_coverage=None))
    after = copy.deepcopy(before)
    for cid, binding in bindings.items():
        evidence = []; hashes = {}
        for i, (path, identity) in enumerate(sorted(gold[cid]['paths'].items())):
            aid = 'fixture-' + cid + '-' + str(i)
            evidence.append(aid); hashes[aid] = identity
            after['artifacts'].append(dict(id=aid,path=path,sha256=identity,availability='LOCAL_ONLY'))
        notes = [{k:d[k] for k in ('id','revision','reason')} for d in binding['dependencies'] if 'reason' in d]
        claim = {key:copy.deepcopy(binding[key]) for key in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations','scope')}
        claim.update(dependencies=[{k:d[k] for k in ('id','revision','relation')} for d in binding['dependencies']],
            evidence=evidence, external_source=None, created_at=before['updated_at'], updated_at=before['updated_at'],
            unknowns=dict(dependency_notes=json.dumps(notes), premises=json.dumps(binding.get('premise_state',binding.get('mathematical_scope',{}))),
                original_binding_method=binding['method'], original_binding_kind=binding['kind'],
                original_binding_scope='No schema projection; binding uses the schema scope fields directly.'),
            verification=[dict(claim_revision=1,verifier=binding['verifier'],method=binding['method'],outcome='PASS',
                timestamp=binding['verification_timestamp'],command_or_audit=binding['report'],scope=binding['scope']['description'],
                limitations=binding['limitations'],shared_components=binding['shared_components'],
                controls=[json.dumps(gold[cid]['controls'])],artifact_hashes=hashes)],
            reproducibility=dict(manifest=next(aid for aid in evidence if indexed(after['artifacts'])[aid]['path']==binding['report'])))
        if cid in mapping:
            claim['unknowns']['editorial_statement_mapping'] = json.dumps(mapping[cid])
        after['claims'].append(claim)
    return before, after


def controls(bindings, reports, gold, mapping):
    before, after = synthetic(bindings,gold,mapping)
    checked_transition(before,after,bindings,gold,mapping)
    records = [dict(label='complete_synthetic353to356', outcome='PASS')]
    def reject(label, stage, call):
        try:
            call()
        except AuditError as error:
            need(error.stage == stage, 'PRECISE_CONTROL_STAGE', str(error))
            records.append(dict(label=label, outcome='REJECTED', diagnostic=error.stage))
            return
        raise AuditError('CORRUPTION_ACCEPTED', label)
    changes = [
        ('prior_revision_bool','TYPED_PRIOR_CLAIMS',lambda x:x['claims'][0].update(revision=True)),
        ('prior_status','TYPED_PRIOR_CLAIMS',lambda x:x['claims'][1].update(status='VERIFIED')),
        ('prior_PUBLIC_availability','TYPED_PRIOR_ARTIFACTS',lambda x:x['artifacts'][0].update(availability='LOCAL_ONLY')),
        ('target_promotion','TYPED_TARGET_TOPLEVEL',lambda x:x['target'].update(status='VERIFIED')),
        ('new_revision_float','TYPED_BOUND_revision',lambda x:indexed(x['claims'])[N5].update(revision=1.0)),
        ('scope_bool_as_integer','TYPED_BOUND_scope',lambda x:indexed(x['claims'])[RANK]['scope'].update(unrestricted_target=1)),
        ('pilot_as_target','TYPED_BOUND_scope',lambda x:indexed(x['claims'])[PILOT]['scope'].update(unrestricted_target=True)),
        ('lost_sparse_limitations','TYPED_BOUND_limitations',lambda x:indexed(x['claims'])[PILOT].update(limitations=[])),
        ('wrong_dependency_relation','TYPED_DEPENDENCIES',lambda x:indexed(x['claims'])[RANK]['dependencies'][0].update(relation='premise')),
        ('wrong_dependency_revision','TYPED_DEPENDENCIES',lambda x:indexed(x['claims'])[RANK]['dependencies'][0].update(revision=1.0)),
        ('lost_weight_only_reason','BOUND_DEPENDENCY_REASON',lambda x:indexed(x['claims'])[RANK]['unknowns'].update(dependency_notes='[]')),
        ('premise_VERIFIED','BOUND_PREMISE_STATE',lambda x:indexed(x['claims'])[RANK]['unknowns'].update(premises='"VERIFIED"')),
        ('self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda x:indexed(x['claims'])[N5]['verification'][0].update(verifier='/root/structural')),
        ('missing_shared_components','BOUND_SHARED_COMPONENTS',lambda x:indexed(x['claims'])[PILOT]['verification'][0].update(shared_components=[])),
        ('new_PUBLIC_promotion','NO_UNCONFIRMED_PUBLIC_PROMOTION',lambda x:x['artifacts'][-1].update(availability='PUBLIC')),
        ('missing_evidence','COMPLETE_EXACT_BOUND_EVIDENCE',lambda x:indexed(x['claims'])[PILOT]['evidence'].pop()),
        ('changed_evidence_hash','EXACT_REVISION_HASH_BINDING',lambda x:indexed(x['claims'])[N5]['verification'][0]['artifact_hashes'].update({indexed(x['claims'])[N5]['evidence'][0]:'0'*64})),
        ('bool_verification_revision','TYPED_VERIFICATION_REVISION',lambda x:indexed(x['claims'])[RANK]['verification'][0].update(claim_revision=True)),
        ('invented_raw_headline','EXACT_NULL_HEADLINE_MAPPING',lambda x:indexed(x['claims'])[PILOT]['unknowns'].update(editorial_statement_mapping='{}')),
        ('rank_wrong_mapping','EXACT_NULL_HEADLINE_MAPPING',lambda x:indexed(x['claims'])[RANK]['unknowns'].update(editorial_statement_mapping='{}')),
        ('third_generic_mapping','ONLY_TWO_HEADLINE_MAPPINGS',lambda x:indexed(x['claims'])[N5]['unknowns'].update(editorial_statement_mapping='{}')),
    ]
    for label, stage, change in changes:
        bad=copy.deepcopy(after);change(bad)
        reject(label,stage,lambda bad=bad:checked_transition(before,bad,bindings,gold,mapping))
    report_changes = [(N5,'universal_derivation_checked',1,'EXACT_N5_SCOPE'),(N5,'target_weight5_lower_count',22869,'EXACT_N5_SCOPE'),
        (N5,'new_exclusions',False,'EXACT_N5_SCOPE'),(PILOT,'complete_trajectory_checked',True,'EXACT_PILOT_SCOPE'),
        (PILOT,'saved_state_files',102.0,'EXACT_PILOT_SCOPE'),(PILOT,'native_reported_proposals',True,'EXACT_PILOT_SCOPE'),
        (RANK,'conditional_incidence_rank_lower',86.0,'EXACT_RANK86_SCOPE'),(RANK,'weight_domain','div4seven','EXACT_RANK86_SCOPE'),
        (RANK,'optimum_asserted',0,'EXACT_RANK86_SCOPE')]
    for cid, key, value, stage in report_changes:
        bad=copy.deepcopy(reports[cid]);bad[key]=value
        reject('report_'+cid+'_'+key,stage,lambda bad=bad,cid=cid:report_scope(cid,bindings[cid],bad))
    bad=copy.deepcopy(reports[PILOT]);bad['statement']=bindings[PILOT]['statement']
    reject('added_original_report_headline','ABSENT_RAW_HEADLINE',lambda:report_scope(PILOT,bindings[PILOT],bad))
    reject('duplicate_yaml_key','DUPLICATE_YAML_KEY',lambda:unique_yaml('a: 1\na: 2\n'))
    return records


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['calibrate','check'],required=True)
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',required=True)
    for field in ('calibration','registration_summary','after_ledger','supervision_summary','supervision_manifest','engineering_gate'):
        parser.add_argument('--'+field.replace('_','-'));parser.add_argument('--'+field.replace('_','-')+'-sha256')
    args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Independent353to356 exact metadata impact and typed corruption controls;150worker20save reserve;no registrar imports or mathematical replay')
    out=(ROOT/args.out).resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False)
    pins={};protected={name:digest(ROOT/name) for name in ('CLAIMS.yaml','.git/index')}
    def pin(name,wanted=None):
        need(deadline.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'INPUT_BOUNDARY')
        identity=digest(path);need(wanted is None or identity==wanted,'INPUT_HASH',name)
        need(name not in pins or pins[name]==identity,'INPUT_STABLE');pins[name]=identity
        return identity
    def read(name,wanted=None):
        pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    try:
        for name in (SOURCE,SPEC,'pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py',
                     'acceleration/audit_20261003_wave39_transition_v2.py','acceleration/audit_20261003_wave39_transition_v2_spec.md'):
            pin(name)
        pin('acceleration/audit_20261003_wave37_transition_v1.py','2dddfc6aa574692f45f1cf02e1f62d0793681687e1ff80b316bb967acb4c6a67')
        pin('acceleration/audit_20261002_wave31_transition_v1.py','5cdb4a68f14d19f97f6326d0fd594e84e8ca732c10225207b9a1b10f29e7b75e')
        bindings={cid:read(*pair) for cid,pair in BINDINGS.items()}
        reports={cid:read(binding['report'],REPORTS[cid]) for cid,binding in bindings.items()}
        gold={cid:evidence_closure(cid,binding) for cid,binding in bindings.items()}
        for cid in bindings:report_scope(cid,bindings[cid],reports[cid])
        mapping=mappings(bindings,reports);tested=controls(bindings,reports,gold,mapping)
        save(out/'controls.json',tested);save(out/'expected_null_headline_mappings.json',mapping)
        outcome=dict(status='INDEPENDENT_WAVE40_TYPED_TRANSITION_V1_CALIBRATION_PASS',actual_transition_inspected=False)
        if args.mode=='check':
            for field in ('calibration','registration_summary','after_ledger','supervision_summary','supervision_manifest','engineering_gate'):
                need(getattr(args,field) and getattr(args,field+'_sha256'),'EXPLICIT_ACTUAL_IDENTITIES',field)
            cal=read(args.calibration,args.calibration_sha256)
            need(cal['status']=='INDEPENDENT_WAVE40_TYPED_TRANSITION_V1_CALIBRATION_PASS' and cal['actual_transition_inspected'] is False,'PREACTUAL_CALIBRATION')
            need(all(cal['inputs_sha256'].get(name)==identity for name,identity in pins.items() if name!=args.calibration),'EXACT_CALIBRATED_INPUTS')
            pin(REGISTRAR,REGISTRAR_SHA);pin(REGISTRAR.replace('.py','_spec.md'),REGISTRAR_SPEC_SHA)
            gate=read(args.engineering_gate,args.engineering_gate_sha256)
            need(gate['status']=='INDEPENDENT_REGISTRAR_V15_EXACT_THREE_BINDINGS_ENGINEERING_PASS'
                 and gate['verifier']=='/root/structural' and gate['producer']=='/root/native_driver'
                 and gate['inputs_sha256'].get(REGISTRAR)==REGISTRAR_SHA
                 and gate['inputs_sha256'].get(REGISTRAR.replace('.py','_spec.md'))==REGISTRAR_SPEC_SHA,
                 'EXACT_ENGINEERING_GATE')
            for name,identity in gate['inputs_sha256'].items():pin(name,identity)
            summary=read(args.registration_summary,args.registration_summary_sha256)
            directory=(ROOT/args.registration_summary).parent
            before_path=(directory/'CLAIMS.before.yaml').relative_to(ROOT).as_posix()
            pin(before_path,BASELINE);before=unique_yaml((ROOT/before_path).read_text(encoding='utf8'))
            pin(args.after_ledger,args.after_ledger_sha256);after=unique_yaml((ROOT/args.after_ledger).read_text(encoding='utf8'))
            claims=checked_transition(before,after,bindings,gold,mapping)
            need(len(before['claims'])==353 and len(claims)==356,'EXACT_CLAIM_POPULATION')
            equal(dict(Counter(claim['status'] for claim in claims.values())),{'VERIFIED':348,'CANDIDATE':3,'REFUTED':5},'EXACT_STATUS_POPULATION')
            need(all(claim['review_state']=='CLEAR' for claim in claims.values()),'EXACT_REVIEW_POPULATION')
            registration_out=directory.relative_to(ROOT).as_posix()
            expected=[summary['command'][0],REGISTRAR,'--out',registration_out,'--previous-sha256',BASELINE]
            for cid,pair in BINDINGS.items():expected+=['--binding',pair[0],'--binding-sha256',pair[1]]
            equal(summary['command'],expected,'EXACT_REGISTRAR_ARGV')
            equal([summary['status'],summary['before_ledger_sha256'],summary['ledger_sha256'],summary['source_sha256'],
                   summary['new_claim_ids'],summary['claim_records'],summary['mathematical_replays'],summary['new_exclusions'],summary['target_resolution'],summary['editorial_statement_mappings']],
                  ['EXACT_BOUND_SCOPED_CLAIMS_REGISTERED',BASELINE,args.after_ledger_sha256,REGISTRAR_SHA,list(BINDINGS),356,0,0,'UNKNOWN',list(mapping.values())],
                  'EXACT_ACTUAL_REGISTRATION_REPORT')
            terminal=read(args.supervision_summary,args.supervision_summary_sha256)
            launch=read(args.supervision_manifest,args.supervision_manifest_sha256)
            equal(launch['command'][1:],expected[1:],'EXACT_SUPERVISOR_ARGV')
            need(launch['seconds']==180 and launch['shutdown_reserve_seconds']==30
                 and terminal['invocation_id']==launch['invocation_id'] and terminal['command_exit_code']==0
                 and terminal['error'] is None and terminal['deadline_reached'] is False
                 and terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True
                 and terminal['cleanup']['cleanup_errors']==[],'ACTUAL_EMPTY_JOB')
            for record in gold.values():
                for name,identity in record['paths'].items():pin(name,identity)
            pin('CLAIMS.yaml',args.after_ledger_sha256);equal(unique_yaml((ROOT/'CLAIMS.yaml').read_text(encoding='utf8')),after,'LIVE_AFTER_MATCH')
            outcome=dict(status='INDEPENDENT_WAVE40_EXACT353_TO356_TRANSITION_V1_PASS',actual_transition_inspected=True,
                before_ledger_sha256=BASELINE,after_ledger_sha256=args.after_ledger_sha256,unchanged_prior_claims=353,current_claims=356,
                new_claim_ids=list(BINDINGS),status_counts={'VERIFIED':348,'CANDIDATE':3,'REFUTED':5},review_counts={'CLEAR':356},
                prior_claims_artifacts_target_unchanged=True,new_exclusions=0,new_unrestricted_exclusions=0,
                exact_null_headline_mappings=mapping,terminal_record=dict(path=args.supervision_summary,sha256=args.supervision_summary_sha256,
                    elapsed_seconds=terminal['elapsed_seconds'],exit_code=0,reaped=True,job_empty=True))
        need(all(digest(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED_STATE_UNCHANGED')
        save(out/'summary.json',dict(**outcome,timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',
            method='independent_artifact_check',inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            positive_controls=1,strict_negative_controls=len(tested)-1,mathematical_replays=0,registrar_imports=0,ledger_mutations=0,index_mutations=0,
            target_resolution='UNKNOWN',historical_protected_execution_state=protected,deadline=deadline.status(),
            shared_components=['Prior independently authored Wave37 exact evidence/projection checker and Wave31 unique YAML/ID parser, wrapped by new typed comparisons and corruption controls.',
                'Wave39 typed metadata design reused as disclosed starting evidence; no registrar, solver or mathematical producer/checker imports.',
                'Python JSON/YAML/SHA256 and locked environment/deadline/containment are trusted.'],
            limitations=['Metadata evidence impact only; no mathematical replay, discovery approval, target construction or exclusion.',
                'New registered evidence remains LOCAL_ONLY pending a separate immutable publication check; all old PUBLIC fields must remain unchanged.',
                'Only pilot and rank86 permit explicit null original headlines, via exact frozen hash-bound mappings; N5 retains literal statement equality.',
                'The full stored pilot population differs from its authenticated ten-million-proposal counter; no trajectory promotion.']))
        print(outcome['status'])
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,live_mutations=False,deadline=deadline.status()))
        raise


if __name__=='__main__':main()
