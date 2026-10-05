"""Two ordinary finite bindings; bounded fresh identities, no mathematical replay."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/record_20261003_fixed_move_census_bindings_v1.py'
SPEC = 'acceleration/record_20261003_fixed_move_census_bindings_v1_spec.md'
BASE = 'acceleration/results/20261003_fixed_move_census_binding_proposals01/'
IDS = ['C-ROOTFOCUSED-STRICT-LEX-STEP1-FIXED-TWO-LINE-CENSUS',
       'C-ROOTFOCUSED-SELECTED145287-RESTRICTED-THREE-LINE-CENSUS']
FROZEN = [
    ('step1', '3e464add7c91ac175bb9ad66c22836f6635d3fda3effeae5fb0c595c2ffcace0',
     '11d37bd57a6fc8541f6a7575a0c21e5efb1ce159b4406c04ad2c3ca76b4dce7f', 2376),
    ('restricted_three_line', 'a92d94d4224d570e0748250ed9eb5fae2cf294166ba29486c214796ca4843f3d',
     'b1e420b2dcb695a569482e6cb11374f3e24f29d2efffa7c63ff40867198d362c', 3066),
]
REPORTS = ['c62722ac0bf54f5166ee692d84822dd0124dde5af2a2b4fb4c9c620cc4c6e471',
           'da193d705dc054e6dcf33f2780309ea8446b0d4f06e424f1a427d8ac29662299']
PROJECTION = 'b664c631ec37c8d4cbd08d395aebed538f8acdfebf8f4c751be731fd0b9152de'
CAL_STATUS = 'FIXED_MOVE_CENSUS_BINDING_METADATA_V1_CONTROLS_PASS'
PINS = {
    'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


def need(ok, diagnostic):
    if not ok:
        raise ValueError(diagnostic)


def same(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(same(x, y) for x, y in zip(left, right))
    return left == right


def unique_pairs(values):
    result = {}
    for key, value in values:
        need(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def strict_json(raw):
    def constant(value):
        raise ValueError('NONFINITE_JSON')
    return json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=constant)


def local_path(name):
    need(type(name) is str and name and '\\' not in name, 'PATH_TYPE')
    candidate = Path(name)
    need(not candidate.is_absolute() and '..' not in candidate.parts, 'WORKSPACE_PATH')
    result = (ROOT / candidate).resolve()
    need(result.is_relative_to(ROOT), 'WORKSPACE_PATH')
    need(result not in {(ROOT/'CLAIMS.yaml').resolve(), (ROOT/'.git/index').resolve()},
         'PROTECTED_STATE_NOT_IMMUTABLE')
    return result


def hash_text(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'HASH_SYNTAX')


def merge_maps(*maps):
    result = {}
    for mapping in maps:
        need(type(mapping) is dict, 'INPUT_MAP_TYPE')
        for name, identity in mapping.items():
            local_path(name)
            hash_text(identity)
            need(name not in result or result[name] == identity, 'CONFLICTING_IMMUTABLE_PIN')
            result[name] = identity
    return result


def dependencies(index, draft):
    original = draft.get('dependencies')
    if index == 0:
        need(original is None, 'EXACT_DRAFT_EMPTY_DEPENDENCY')
        return []
    expected = dict(id=IDS[0], revision=1, relation='verification_dependency')
    need(same(original, expected), 'EXACT_DRAFT_DEPENDENCY_OBJECT')
    return [deepcopy(expected)]


def basic(index, draft, report):
    need(type(draft) is dict and type(report) is dict, 'METADATA_CONTAINER')
    need(draft.get('id') == IDS[index] and type(draft.get('revision')) is int
         and draft['revision'] == 1 and type(draft.get('claim_revision')) is int
         and draft['claim_revision'] == 1, 'EXACT_ID_REVISION')
    need(all(draft.get(k) == v for k,v in dict(producer='/root/native_driver',
         verifier='/root/structural',method='independent_artifact_check',status='VERIFIED',
         review_state='CLEAR',kind='exclusion').items()) and draft.get('basis') == ['COMPUTED'],
         'EXACT_ORDINARY_ROLES_STATUS')
    need(report.get('producer') == draft['producer'] and report.get('verifier') == draft['verifier']
         and report.get('method') == draft['method'], 'EXACT_PRIMARY_REPORT_ROLES')
    scope = draft.get('scope')
    need(type(scope) is dict and set(scope) == {'description','unrestricted_target','target_resolution'}
         and type(scope['description']) is str and bool(scope['description'])
         and scope['unrestricted_target'] is False and scope['target_resolution'] == 'NONE'
         and draft.get('target_resolution') == report.get('target_resolution') == 'NONE',
         'EXACT_FINITE_THREE_KEY_SCOPE')
    need(type(draft.get('statement')) is str and bool(draft['statement']), 'EXACT_STATEMENT_TYPE')
    need('verification_records' not in draft and type(draft.get('shared_components')) is list
         and all(type(x) is str for x in draft['shared_components']), 'ORDINARY_METADATA_CONTAINER')
    dependencies(index, draft)
    if index == 0:
        need('statement' not in report and 'scope' not in report, 'ORIGINAL_ABSENT_HEADLINE')
    else:
        need(same(report.get('statement'),draft['statement'])
             and same(report.get('scope'),scope), 'ORIGINAL_LITERAL_HEADLINE')


def controls():
    outcomes = []
    def fixture(index):
        draft = dict(id=IDS[index],revision=1,claim_revision=1,producer='/root/native_driver',
            verifier='/root/structural',method='independent_artifact_check',status='VERIFIED',
            review_state='CLEAR',kind='exclusion',basis=['COMPUTED'],statement='literal finite statement',
            scope=dict(description='one fixture',unrestricted_target=False,target_resolution='NONE'),
            target_resolution='NONE',shared_components=[],dependencies=None if index==0 else
            dict(id=IDS[0],revision=1,relation='verification_dependency'))
        report = dict(producer=draft['producer'],verifier=draft['verifier'],method=draft['method'],
                      target_resolution='NONE')
        if index == 1:
            report.update(statement=draft['statement'],scope=deepcopy(draft['scope']))
        return draft,report
    for index in [0,1]:
        basic(index,*fixture(index))
        outcomes.append(dict(name='ordinary_synthetic_'+str(index),outcome='PASS',
                             normalized_dependencies=dependencies(index,fixture(index)[0])))
    cases = [
        ('revision_bool',0,'EXACT_ID_REVISION',lambda b,r:b.update(revision=True)),
        ('claim_revision_float',0,'EXACT_ID_REVISION',lambda b,r:b.update(claim_revision=1.0)),
        ('wrong_id',0,'EXACT_ID_REVISION',lambda b,r:b.update(id=IDS[1])),
        ('root_role',0,'EXACT_ORDINARY_ROLES_STATUS',lambda b,r:b.update(verifier='/root')),
        ('candidate_status',0,'EXACT_ORDINARY_ROLES_STATUS',lambda b,r:b.update(status='CANDIDATE')),
        ('report_role',0,'EXACT_PRIMARY_REPORT_ROLES',lambda b,r:r.update(verifier='/root')),
        ('scope_extra',0,'EXACT_FINITE_THREE_KEY_SCOPE',lambda b,r:b['scope'].update(extra=0)),
        ('scope_bool_alias',0,'EXACT_FINITE_THREE_KEY_SCOPE',lambda b,r:b['scope'].update(unrestricted_target=0)),
        ('scope_unrestricted',0,'EXACT_FINITE_THREE_KEY_SCOPE',lambda b,r:b['scope'].update(unrestricted_target=True)),
        ('resolution',0,'EXACT_FINITE_THREE_KEY_SCOPE',lambda b,r:r.update(target_resolution='SAT')),
        ('nonstatement',0,'EXACT_STATEMENT_TYPE',lambda b,r:b.update(statement=7)),
        ('legacy_records',0,'ORDINARY_METADATA_CONTAINER',lambda b,r:b.update(verification_records=[])),
        ('components_dict',0,'ORDINARY_METADATA_CONTAINER',lambda b,r:b.update(shared_components={})),
        ('empty_dependency_changed',0,'EXACT_DRAFT_EMPTY_DEPENDENCY',lambda b,r:b.update(dependencies=[])),
        ('dependency_revision_bool',1,'EXACT_DRAFT_DEPENDENCY_OBJECT',lambda b,r:b['dependencies'].update(revision=True)),
        ('dependency_relation',1,'EXACT_DRAFT_DEPENDENCY_OBJECT',lambda b,r:b['dependencies'].update(relation='uses_result')),
        ('invented_headline',0,'ORIGINAL_ABSENT_HEADLINE',lambda b,r:r.update(statement=b['statement'])),
        ('wrong_literal_statement',1,'ORIGINAL_LITERAL_HEADLINE',lambda b,r:r.update(statement='other')),
        ('wrong_literal_scope',1,'ORIGINAL_LITERAL_HEADLINE',lambda b,r:r['scope'].update(description='broader')),
    ]
    for name,index,expected,mutate in cases:
        b,r=fixture(index);mutate(b,r)
        try:
            basic(index,b,r)
        except ValueError as error:
            need(str(error)==expected, 'WRONG_CONTROL_STAGE:'+name)
            outcomes.append(dict(name=name,expected=expected,actual=str(error),outcome='PASS'))
        else:
            raise ValueError('NEGATIVE_ACCEPTED:'+name)
    additional=[('duplicate_json','DUPLICATE_JSON_KEY',lambda:strict_json('{"x":1,"x":2}')),
        ('nonfinite_json','NONFINITE_JSON',lambda:strict_json('{"x":NaN}')),
        ('escape_path','WORKSPACE_PATH',lambda:local_path('../other')),
        ('protected_map','PROTECTED_STATE_NOT_IMMUTABLE',lambda:local_path('CLAIMS.yaml')),
        ('uppercase_hash','HASH_SYNTAX',lambda:hash_text('A'*64)),
        ('conflicting_map','CONFLICTING_IMMUTABLE_PIN',lambda:merge_maps({'docs/x':'a'*64},{'docs/x':'b'*64}))]
    for name,expected,action in additional:
        try: action()
        except ValueError as error:
            need(str(error)==expected,'WRONG_CONTROL_STAGE:'+name)
            outcomes.append(dict(name=name,expected=expected,actual=str(error),outcome='PASS'))
        else: raise ValueError('NEGATIVE_ACCEPTED:'+name)
    return outcomes


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['calibrate','record'],required=True)
    parser.add_argument('--seconds',type=float,required=True)
    parser.add_argument('--save-reserve-seconds',type=float,required=True)
    parser.add_argument('--self-sha256',required=True)
    parser.add_argument('--spec-sha256',required=True)
    parser.add_argument('--expected-ledger-sha256',required=True)
    parser.add_argument('--expected-index-sha256',required=True)
    parser.add_argument('--calibration')
    parser.add_argument('--calibration-sha256')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Two finite ordinary metadata bindings; fresh declared2376/3066 input closures and serialization inside one invocation; no mathematics,registrar or native replay')
    need(0<args.save_reserve_seconds<args.seconds,'SAVE_RESERVE')
    out=local_path(args.out);need(not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
    pins={};observed={};protected_before=None
    def digest(path,reserve=0):
        value=hashlib.sha256();size=0
        with path.open('rb') as stream:
            while True:
                state=deadline.status()
                need(not state['stop_required'] and state['remaining_seconds']>reserve,'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
                block=stream.read(1024*1024)
                if not block:break
                value.update(block);size+=len(block)
        return value.hexdigest(),size
    def pin(name,expected):
        hash_text(expected);path=local_path(name)
        need(name not in pins or pins[name]==expected,'CONFLICTING_IMMUTABLE_PIN')
        if name not in observed:
            actual,size=digest(path,args.save_reserve_seconds)
            need(actual==expected,'INPUT_IDENTITY:'+name)
            pins[name]=expected;observed[name]=dict(sha256=actual,bytes=size)
    def load(name,expected):
        pin(name,expected)
        return strict_json(local_path(name).read_bytes())
    def protect():
        return {name:digest(ROOT/name)[0] for name in ['CLAIMS.yaml','.git/index']}
    def save(path,value):
        with path.open('x',encoding='utf8',newline='\n') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    try:
        protected_before=protect()
        need(protected_before=={'CLAIMS.yaml':args.expected_ledger_sha256,'.git/index':args.expected_index_sha256},'PROTECTED_STATE_EXPECTATION')
        pin(SOURCE,args.self_sha256);pin(SPEC,args.spec_sha256)
        for name,h in PINS.items():pin(name,h)
        outcomes=controls();save(out/'controls.json',outcomes)
        records=[];pending=[]
        if args.mode=='record':
            need(args.calibration is not None and args.calibration_sha256 is not None,'CALIBRATION_REQUIRED')
            cal=load(args.calibration,args.calibration_sha256)
            need(cal['status']==CAL_STATUS and cal['source_sha256']==args.self_sha256
                 and cal['spec_sha256']==args.spec_sha256 and cal['positive_controls']==2
                 and cal['strict_negative_controls']==25,'APPLICABLE_CALIBRATION')
            for name,h in cal['inputs_sha256'].items():pin(name,h)
            cal_controls=str(Path(args.calibration).parent.as_posix())+'/controls.json'
            pin(cal_controls,cal['controls_sha256'])
            for index,(directory,draft_hash,closure_hash,count) in enumerate(FROZEN):
                draft_path=BASE+directory+'/claim_binding_schema2_draft.json'
                closure_path=BASE+directory+'/declared_checking_closure.json'
                draft=load(draft_path,draft_hash);closure=load(closure_path,closure_hash)
                report=load(draft['report'],REPORTS[index]);basic(index,draft,report)
                need(draft['report_sha256']==REPORTS[index] and closure['primary_report']==draft['report']
                     and closure['primary_report_sha256']==REPORTS[index],'EXACT_PRIMARY_IDENTITY')
                if index==0:
                    extra=draft['supplementary_selected_export_report']
                    projection=load(extra['path'],PROJECTION)
                    need('statement' not in projection and 'scope' not in projection
                         and projection['status']=='INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS'
                         and projection['source_complete_audit_sha256']==REPORTS[0]
                         and same(projection['metrics'],{'E_lambda':0,'E_mu':5292,'R_root':10})
                         and projection['selected_proposal_id']==145287 and projection['historical_native_state_written'] is False,
                         'EXACT_SEPARATE_EXPORT_METADATA')
                    expected_map=merge_maps(report['inputs_sha256'],projection['inputs_sha256'])
                    need(report['status']=='INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_COMPLETE_PASS'
                         and type(report['complete_labelled_proposals']) is int and report['complete_labelled_proposals']==224784
                         and report['minimum_root_tie_scalar_matrices']==114 and report['selected_proposal_id']==145287,
                         'EXACT_STEP1_METADATA')
                else:
                    expected_map=merge_maps(report['inputs_sha256'])
                    need(report['status']=='INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_COMPLETE_PASS'
                         and report['result']['complete_roles']==187650 and same(report['result']['aggregate']['counts'],
                         {'invalid_linearity':78540,'invalid_selection':13458,'valid_lambda_changed':95652}),
                         'EXACT_RESTRICTED_METADATA')
                need(len(expected_map)==count and same(closure['inputs_sha256'],expected_map),'EXACT_DECLARED_CHECKING_MAP')
                for name,h in merge_maps(expected_map,draft['inputs_sha256']).items():pin(name,h)
                now=datetime.now(timezone.utc).isoformat();binding=deepcopy(draft)
                binding['dependencies']=dependencies(index,draft)
                binding['created_at']=binding['updated_at']=now
                binding['metadata_proposal_status']='FINAL_FRESH_IDENTITY_METADATA_NOT_REGISTERED'
                binding['fresh_transitive_hashes_performed']=True
                binding['complete_declared_historical_checking_closure']['role']='Complete declared prior checking inputs freshly hash-authenticated within this metadata invocation; prior mathematical verdicts are not replayed'
                binding['retrieval']='Exact original reports, preserved drafts and complete declared checking closure; separate publication required for public availability'
                binding['limitations']=[x for x in binding['limitations'] if 'SOURCE_ONLY intended' not in x and 'must be freshly authenticated' not in x]
                binding['limitations'].append('Final metadata writer freshly authenticates declared evidence bytes only; no mathematical replay, independent reapproval, registration or index mutation.')
                binding['shared_components'][-1]='Complete prior checking maps are stored once and freshly hashed by this metadata-only writer; no arbitrary recursive archive scan or mathematical gate transfer.'
                binding['draft_preservation']=dict(path=draft_path,sha256=draft_hash,original_dependency_container=draft['dependencies'],
                    normalized_dependency_array=binding['dependencies'],statement_scope_roles_unchanged=True)
                binding['writer_identity']=dict(source=SOURCE,source_sha256=args.self_sha256,spec=SPEC,spec_sha256=args.spec_sha256,
                    command=[sys.executable,*sys.argv],calibration=args.calibration,calibration_sha256=args.calibration_sha256,
                    role='Checkpoint metadata author only; independent mathematics/artifact verdict remains Structural')
                if index==1:
                    completion_path='acceleration/results/20261003_independent_review/restricted_three_line_target_full01/completion.json'
                    completion=load(completion_path,'2005e68960d595892cfc145b1d7a4e478bb9a89511ce64d30a5f36bc15ea1fbb')
                    need(completion['report_sha256']==REPORTS[1] and completion['verifier_cleanup']['job_active_zero_observed'] is True,
                         'EXACT_VERIFIER_CLEANUP_COMPLETION')
                    binding['verifier_cleanup_clarification']=dict(path=completion_path,sha256=pins[completion_path],
                        text=completion['producer_cleanup_scope'],original_report_unchanged=True)
                binding['inputs_sha256'].update({SOURCE:args.self_sha256,SPEC:args.spec_sha256,args.calibration:args.calibration_sha256,
                                                cal_controls:cal['controls_sha256'],draft_path:draft_hash,**PINS})
                destination=out/directory;destination.mkdir()
                pending.append((destination,binding,count,index))
        protected_after=protect();need(protected_after==protected_before,'PROTECTED_STATE_CHANGED')
        if args.mode=='record':
            receipt_path=out/'fresh_closure_receipt.json'
            save(receipt_path,dict(status='TWO_FIXED_CENSUS_COMPLETE_DECLARED_CLOSURE_IDENTITY_ONLY_PASS',
                timestamp=datetime.now(timezone.utc).isoformat(),author='/root/checkpoint_audit',method='metadata_identity_record_only',
                source=SOURCE,source_sha256=args.self_sha256,spec=SPEC,spec_sha256=args.spec_sha256,
                calibration=args.calibration,calibration_sha256=args.calibration_sha256,
                complete_declared_maps=[dict(path=BASE+d+'/declared_checking_closure.json',sha256=h,members=n)
                    for d,_,h,n in FROZEN],unique_members_hashed=len(observed),total_bytes_hashed=sum(x['bytes'] for x in observed.values()),
                observed_member_descriptors_sha256=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                command=[sys.executable,*sys.argv],historical_protected_execution_state=dict(before=protected_before,after=protected_after),
                mathematical_replays=0,ledger_mutations=0,index_mutations=0,
                limitation='Fresh identity record of the exact declared maps only; no mathematical replay or independent result reapproval'))
            receipt_hash,_=digest(receipt_path)
            for destination,binding,count,index in pending:
                receipt_name=receipt_path.relative_to(ROOT).as_posix()
                binding['fresh_identity_receipt']=dict(path=receipt_name,sha256=receipt_hash,mathematical_replay=False)
                binding['inputs_sha256'][receipt_name]=receipt_hash
                save(destination/'claim_binding_schema2.json',binding)
                binding_hash,_=digest(destination/'claim_binding_schema2.json')
                records.append(dict(id=binding['id'],revision=1,path=(destination/'claim_binding_schema2.json').relative_to(ROOT).as_posix(),
                    sha256=binding_hash,declared_checking_members=count,report_sha256=REPORTS[index]))
        summary=dict(status=CAL_STATUS if args.mode=='calibrate' else 'TWO_FIXED_MOVE_CENSUS_ORDINARY_R1_BINDINGS_METADATA_V1_RECORDED',
            timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/checkpoint_audit',method='metadata_identity_record_only',
            source_sha256=args.self_sha256,spec_sha256=args.spec_sha256,command=[sys.executable,*sys.argv],cwd=str(ROOT),
            python=sys.version,positive_controls=2,strict_negative_controls=25,controls_sha256=digest(out/'controls.json')[0],inputs_sha256=pins,
            unique_members_hashed=len(observed),total_bytes_hashed=sum(x['bytes'] for x in observed.values()),records_in_dependency_order=records,
            historical_protected_execution_state=dict(before=protected_before,after=protected_after),mathematical_replays=0,
            native_calls=0,ledger_mutations=0,index_mutations=0,target_resolution='NONE',deadline=deadline.status(),
            scope='Exactly two finite ordinary metadata records; prior Structural complete checks remain the mathematical evidence')
        save(out/'summary.json',summary)
    except Exception as error:
        save(out/'failure.json',dict(error_type=type(error).__name__,error=str(error),inputs_sha256=pins,
            completed_members=len(observed),historical_protected_before=protected_before,mathematical_replays=0,
            ledger_mutations=0,index_mutations=0,outputs_preserved=True,deadline=deadline.status()))
        raise


if __name__=='__main__':
    main()
