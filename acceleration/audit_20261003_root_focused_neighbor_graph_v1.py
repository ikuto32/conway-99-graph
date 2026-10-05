"""Independent graph-only neighbor projection audit; no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S
import audit_20261003_root_focused_census_records_v2 as R

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/audit_20261003_root_focused_neighbor_graph_v1.py'
SPEC='acceleration/audit_20261003_root_focused_neighbor_graph_v1_spec.md'
PRODUCER='acceleration/project_20261003_root_focused_neighbor_graph_v1.py'
PRODUCER_SPEC='acceleration/project_20261003_root_focused_neighbor_graph_v1_spec.md'
FULL='acceleration/results/20261003_independent_review/root_focused_census_full01/summary.json'
MANIFEST='acceleration/results/20261003_root_focused_two_line_census01/manifest.json'
MATRIX='acceleration/results/20261003_root_focused_two_line_census01/best_root_neighbor.adj'
TRIPLES='acceleration/results/20261003_root_focused_two_line_census01/best_root_neighbor_triples.json'
PINS={PRODUCER:'593b04087da6d54f9d25c159466100dc2b215615d088caf1af7b0eb33009353c',
 PRODUCER_SPEC:'9842e294d920094140776246c6a36ed2b840f948cefac5607129be23bf0864ec',
 'acceleration/census_20261003_root_focused_two_line_v1.py':'bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017',
 'acceleration/census_20261003_root_focused_two_line_v1_spec.md':'9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8',
 'acceleration/audit_20261003_root_focused_census_core_v1.py':'78fdaa10e0056ca048b9e31049dc2e30951cfaa7dba418751a98008a2a69168c',
 'acceleration/audit_20261003_root_focused_core_v2.py':'5cd58d2936e5ffea2b86f0ed85ae85038b056a9fbe4205039eb867443b0d1579',
 'acceleration/audit_20261003_root_focused_census_records_v2.py':'aa38a907d7962c475d7fc5fd25e9c0c95c15732d5285d9b0848d877fe79bea96'}
ACTUAL={FULL:'ef948e877938dec885b5155768d7f46c102f011d8e79c090ad9116d42da03d09',
 MANIFEST:'4fc77b2f2b738d33901f6bea1f5d11c92daee561b210e0f2a370b17bbedfd056',
 MATRIX:'c01ce27d15cad11f4bdee63b6bdba91c5b18a8a6e8022c40317427cc314d6ce3',
 TRIPLES:'b2d12a902a13e4c73ae10b1d3e2c78455612215565dfb7efbb878580f36a1bf0'}
SCHEMA='FROZEN_ROOT_SELECTED_NEIGHBOR_GRAPH_INPUT_V1'
CAL='INDEPENDENT_FROZEN_ROOT_NEIGHBOR_GRAPH_CHECKER_V1_CALIBRATION_PASS'
CONTROLS='INDEPENDENT_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_V1_CONTROLS_PASS'
PASS='INDEPENDENT_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_V1_COMPLETE_PASS'

class AuditError(ValueError):
 def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
 if not ok:raise AuditError(stage)
def same(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def loads(raw):
 def unique(items):
  result={}
  for key,value in items:need(key not in result,'JSON_DUPLICATE');result[key]=value
  return result
 def constant(value):raise AuditError('JSON_CONSTANT')
 try:return json.loads(raw.decode('utf8'),object_pairs_hook=unique,parse_constant=constant)
 except (UnicodeError,json.JSONDecodeError)as error:raise AuditError('JSON_SYNTAX')from error
def provenance(actual):
 if not actual:
  return dict(mode='synthetic_engineering_fixture',selected_proposal_id=None,source_manifest=None,source_matrix=None,source_triples=None,
   source_complete_audit=None,null_reason='Generic engineering fixture, not an actual selected99graph or historical computation.',
   historical_native_state_written=False,line_order='Literal synthetic fixture order.')
 return dict(mode='actual_independently_checked_selected_artifact',selected_proposal_id=121302,
  source_manifest=dict(path=MANIFEST,sha256=ACTUAL[MANIFEST]),source_matrix=dict(path=MATRIX,sha256=ACTUAL[MATRIX]),
  source_triples=dict(path=TRIPLES,sha256=ACTUAL[TRIPLES]),
  source_complete_audit=dict(path=FULL,sha256=ACTUAL[FULL],status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS'),
  historical_native_state_written=False,line_order='Exact ordered source triples, seven original literal rows preserved.')
def decode(raw,actual=False):
 obj=loads(raw)
 need(type(obj)is dict and set(obj)=={'schema','n','degree','root','ordered_triples','frozen_rows','mutable_labels','metrics','provenance'}
  and obj['schema']==SCHEMA,'GRAPH_SCHEMA')
 need(all(type(obj[k])is int for k in['n','degree','root']),'GRAPH_DOMAIN')
 prov=obj['provenance'];need(same(prov,provenance(False))or same(prov,provenance(True)),'PROVENANCE')
 if actual:need(same(prov,provenance(True))and(obj['n'],obj['degree'],obj['root'])==(99,7,11),'TARGET_SCOPE')
 try:base=K.from_triples(obj['ordered_triples'],obj['n'],obj['degree'],obj['root'])
 except K.CensusError as error:raise AuditError('TOPOLOGY_DOMAIN')from error
 need(same(obj['frozen_rows'],base['frozen'])and same(obj['mutable_labels'],base['mutable']),'FROZEN_LABELS')
 metrics=dict(E_lambda=base['lambda_energy'],E_mu=base['mu_energy'],R_root=base['root_residual'])
 need(same(obj['metrics'],metrics),'EXACT_SCORES')
 matrix=K.matrix_bytes(base['bits']);scalar=S.scalar_matrix(matrix,obj['n'],obj['degree'],obj['root'])
 need((scalar['lambda_energy'],scalar['mu_energy'],scalar['root_residual'])==tuple(metrics.values()),'SEPARATE_SCALAR_SCORES')
 if actual:
  need(base['frozen']==R.FROZEN and len(base['triples'])==231 and len(base['mutable'])==224
   and metrics==dict(E_lambda=0,E_mu=5408,R_root=10),'TARGET_GRAPH')
  need(hashlib.sha256(matrix).hexdigest()==ACTUAL[MATRIX],'TARGET_MATRIX')
 return obj,base,scalar
def payload(triples,n,degree,root):
 base=K.from_triples(triples,n,degree,root)
 return dict(schema=SCHEMA,n=n,degree=degree,root=root,ordered_triples=triples,frozen_rows=base['frozen'],mutable_labels=base['mutable'],
  metrics=dict(E_lambda=base['lambda_energy'],E_mu=base['mu_energy'],R_root=base['root_residual']),provenance=provenance(False))
def blob(obj):return(json.dumps(obj,allow_nan=False)+'\n').encode()
def review(report):
 need(type(report)is dict and same([report.get(k)for k in['status','producer','verifier','method','target_resolution']],
  ['INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS','/root/native_driver','/root/checkpoint_audit','independent_artifact_check','NONE']),'SOURCE_REVIEW')
 need(same([report.get(k)for k in['complete_labelled_proposals','selected_proposal_id','mutable_label_count','literal_one_move_population_only']],
  [224784,121302,224,True]),'SOURCE_REVIEW')
 need(all(report.get('inputs_sha256',{}).get(name)==ACTUAL[name]for name in[MANIFEST,MATRIX,TRIPLES]),'SOURCE_REVIEW')
def fake_review():
 return dict(status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS',producer='/root/native_driver',verifier='/root/checkpoint_audit',
  method='independent_artifact_check',target_resolution='NONE',complete_labelled_proposals=224784,selected_proposal_id=121302,mutable_label_count=224,
  literal_one_move_population_only=True,inputs_sha256={name:ACTUAL[name]for name in[MANIFEST,MATRIX,TRIPLES]})
def reject(records,name,stage,call):
 try:call()
 except AuditError as error:
  need(error.stage==stage,'EXACT_CONTROL_STAGE');records.append(dict(case=name,stage=stage,outcome='REJECTED'));return
 raise AuditError('CORRUPTION_ACCEPTED')
def calibration(out):
 positives=[]
 for name in['rook9','prism9','cube12_defect']:
  n=12 if name=='cube12_defect' else 9
  fixture=payload(S.fixture(name),n,2,0);obj,base,scalar=decode(blob(fixture));save(out/(name+'.json'),fixture)
  if name=='rook9':need(scalar['srg_valid']is True and scalar['lambda_energy']==scalar['mu_energy']==scalar['root_residual']==0,'KNOWN_VALID_ROOK')
  positives.append(dict(case=name,scalar=scalar))
 good=payload(S.fixture('rook9'),9,2,0);records=[]
 for name,raw,stage in[('malformed',b'{broken','JSON_SYNTAX'),('duplicate',b'{"n":9,"n":9}','JSON_DUPLICATE'),('NaN',b'{"n":NaN}','JSON_CONSTANT')]:
  reject(records,name,stage,lambda raw=raw:decode(raw))
 cases=[('extra','GRAPH_SCHEMA',lambda x:x.update(extra=1)),('native_magic','GRAPH_SCHEMA',lambda x:x.update(schema='ROOT_FOCUSED_ANNEAL_STATE_V1'))]
 for k in['n','degree','root']:cases.append(('bool_'+k,'GRAPH_DOMAIN',lambda x,k=k:x.update({k:True})))
 cases += [('float_root','GRAPH_DOMAIN',lambda x:x.update(root=0.0)),
  ('duplicate_vertex','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(1,x['ordered_triples'][0][0])),
  ('duplicate_triple','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'].__setitem__(1,list(x['ordered_triples'][0]))),
  ('repeated_pair','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'].__setitem__(1,[3,4,0])),
  ('bool_point','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(0,False)),
  ('outside_vertex','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(0,9)),
  ('missing_line','TOPOLOGY_DOMAIN',lambda x:x['ordered_triples'].pop()),
  ('wrong_frozen','FROZEN_LABELS',lambda x:x['frozen_rows'][0].reverse()),
  ('missing_mutable','FROZEN_LABELS',lambda x:x['mutable_labels'].pop()),
  ('bool_mutable','FROZEN_LABELS',lambda x:x['mutable_labels'].__setitem__(0,True))]
 for k in['E_lambda','E_mu','R_root']:cases.append(('score_'+k,'EXACT_SCORES',lambda x,k=k:x['metrics'].__setitem__(k,1)))
 cases += [('bool_score','EXACT_SCORES',lambda x:x['metrics'].__setitem__('E_mu',False)),('float_score','EXACT_SCORES',lambda x:x['metrics'].__setitem__('E_mu',0.0)),
  ('invented_native_history','PROVENANCE',lambda x:x['provenance'].update(historical_native_state_written=True)),
  ('wrong_provenance','PROVENANCE',lambda x:x['provenance'].update(mode='actual99'))]
 for name,stage,change in cases:
  bad=copy.deepcopy(good);change(bad);reject(records,name,stage,lambda bad=bad:decode(blob(bad)))
 reject(records,'tiny_not99','TARGET_SCOPE',lambda:decode(blob(good),actual=True))
 bad=copy.deepcopy(good);bad['provenance']=provenance(True)
 reject(records,'actual_metadata_not99','TARGET_SCOPE',lambda:decode(blob(bad),actual=True))
 need(len(records)==27,'GRAPH_CONTROL_POPULATION')
 interface=fake_review();review(interface);metadata=[]
 for key in['status','producer','verifier','method','target_resolution']:
  bad=copy.deepcopy(interface);bad[key]='wrong';reject(metadata,'review_'+key,'SOURCE_REVIEW',lambda bad=bad:review(bad))
 for key in['complete_labelled_proposals','selected_proposal_id','mutable_label_count']:
  for value,label in[(interface[key]+1,'wrong'),(True,'bool'),(float(interface[key]),'float')]:
   bad=copy.deepcopy(interface);bad[key]=value;reject(metadata,'review_'+label+'_'+key,'SOURCE_REVIEW',lambda bad=bad:review(bad))
 bad=copy.deepcopy(interface);bad['literal_one_move_population_only']=False;reject(metadata,'whole_graph_scope','SOURCE_REVIEW',lambda:review(bad))
 for name,label in[(MATRIX,'missing_matrix'),(TRIPLES,'wrong_triples')]:
  bad=copy.deepcopy(interface)
  if label=='missing_matrix':bad['inputs_sha256'].pop(name)
  else:bad['inputs_sha256'][name]='0'*64
  reject(metadata,label,'SOURCE_REVIEW',lambda bad=bad:review(bad))
 need(len(metadata)==17,'METADATA_CONTROL_POPULATION')
 save(out/'calibration_controls.json',dict(positive_graphs=positives,synthetic_review_positive=interface,graph_negatives=records,metadata_negatives=metadata))
 return dict(positive_graphs=3,synthetic_review_positives=1,precise_graph_negatives=27,precise_review_negatives=17,producer_outputs_checked=False)

def terminal(report):
 need(report.get('command_exit_code')==0 and type(report.get('command_exit_code'))is int and report.get('error')is None
  and report.get('deadline_reached')is False and report.get('cleanup',{}).get('reaped')is True
  and report['cleanup'].get('job_active_zero_observed')is True and report['cleanup'].get('cleanup_errors')==[],'EMPTY_PRODUCER_JOB')

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','controls','full']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True)
 for field in['calibration','controls_gate','producer_summary','supervisor']:
  p.add_argument('--'+field.replace('_','-'));p.add_argument('--'+field.replace('_','-')+'-sha256')
 a=p.parse_args();deadline=CommandDeadline(a.seconds,allocation_reason='Independent graph-only projection typed controls/raw checking;20second preservation reserve;no native or census invocation')
 out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT)and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True);pins={}
 protected={name:sha(ROOT/name)for name in['CLAIMS.yaml','.git/index']}
 def pin(name,identity=None):
  need(deadline.status()['remaining_seconds']>20,'PRESERVATION_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT)and path.is_file(),'INPUT_BOUNDARY')
  found=sha(path);need(identity is None or found==identity,'INPUT_IDENTITY');need(name not in pins or pins[name]==found,'INPUT_STABLE');pins[name]=found
 def read(name,identity=None):pin(name,identity);return loads((ROOT/name).read_bytes())
 def closure(report):
  for name,identity in report['inputs_sha256'].items():need(name not in['CLAIMS.yaml','.git/index'],'IMMUTABLE_INPUT_ROLE');pin(name,identity)
 try:
  for name,identity in PINS.items():pin(name,identity)
  for name in[SOURCE,SPEC,'pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py',
   'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']:pin(name)
  tested=calibration(out);result=dict(status=CAL,**tested)
  if a.mode!='calibration':
   need(all([a.calibration,a.calibration_sha256,a.producer_summary,a.producer_summary_sha256,a.supervisor,a.supervisor_sha256]),'EXPLICIT_ACTUAL_IDENTITIES')
   cal=read(a.calibration,a.calibration_sha256)
   need(cal['status']==CAL and cal['producer_outputs_checked']is False and cal['inputs_sha256'][SOURCE]==pins[SOURCE]
    and cal['inputs_sha256'][SPEC]==pins[SPEC],'APPLICABLE_CALIBRATION');closure(cal)
   author=read(a.producer_summary,a.producer_summary_sha256);ended=read(a.supervisor,a.supervisor_sha256);terminal(ended)
   closure(author);need(author['producer']=='/root/native_driver'and author['independent_approval']is False
    and author['historical_native_state_written']is False,'AUTHOR_SCOPE')
   folder=(ROOT/a.producer_summary).parent
   if a.mode=='controls':
    need(same([author['status'],author['positive_fixtures'],author['strict_negative_count'],author['source_review_synthetic_positive'],author['source_review_strict_negative_count'],author['actual_selected_graph_read'],author['scientific_launched']],
     ['AUTHOR_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_CONTROLS_PENDING_INDEPENDENT_GATE',['rook9','prism9','cube12'],24,1,14,False,False]),'AUTHOR_CONTROL_POPULATION')
    objects=[]
    for name in['rook9','prism9','cube12']:
     member=(folder/(name+'.graph.json')).relative_to(ROOT).as_posix();obj,base,scalar=decode((ROOT/member).read_bytes());pin(member)
     need(obj['provenance']==provenance(False),'SYNTHETIC_CONTROL_SCOPE');objects.append(dict(name=name,scalar=scalar))
    stage_map={'PROJECTION_JSON':None,'PROJECTION_SCHEMA':'GRAPH_SCHEMA','PROJECTION_DOMAIN':'GRAPH_DOMAIN','DOMAIN':'TOPOLOGY_DOMAIN','LINEARITY':'TOPOLOGY_DOMAIN','DEGREE':'TOPOLOGY_DOMAIN','PROJECTION_FROZEN':'FROZEN_LABELS','PROJECTION_ENERGY':'EXACT_SCORES','PROJECTION_PROVENANCE':'PROVENANCE','TARGET_SCOPE':'TARGET_SCOPE'}
    raw_negatives=[]
    for record in author['strict_negatives']:
     name=record['case'];member=(folder/(name+'.json')).relative_to(ROOT).as_posix();pin(member);raw=(ROOT/member).read_bytes()
     stage=('JSON_DUPLICATE'if name=='duplicate_key'else'JSON_SYNTAX')if record['stage']=='PROJECTION_JSON'else stage_map[record['stage']]
     need(record['outcome']=='REJECTED','AUTHOR_NEGATIVE_RECORD');reject(raw_negatives,name,stage,lambda raw=raw,stage=stage:decode(raw,actual=stage=='TARGET_SCOPE'))
    member=(folder/'synthetic_source_review_fixture.json').relative_to(ROOT).as_posix();interface=read(member);review(interface);raw_review=[]
    for record in author['source_review_strict_negatives']:
     member=(folder/(record['case']+'.json')).relative_to(ROOT).as_posix();bad=read(member)
     need(record['stage']=='SOURCE_REVIEW'and record['outcome']=='REJECTED','AUTHOR_NEGATIVE_RECORD')
     reject(raw_review,record['case'],'SOURCE_REVIEW',lambda bad=bad:review(bad))
    need(len(raw_negatives)==24 and len(raw_review)==14,'COMPLETE_SAVED_NEGATIVES')
    save(out/'actual_controls_audit.json',dict(objects=objects,graph_negatives=raw_negatives,source_review_negatives=raw_review,
     author_stage_note='Producer reported stages are preserved separately; independent parser uses its own exact diagnostics on the raw corruptions.'))
    result=dict(status=CONTROLS,producer_outputs_checked=True,actual_positive_graphs=3,actual_graph_corruptions=24,actual_review_corruptions=14,
     own_precise_graph_controls=27,own_precise_review_controls=17,actual_selected_graph_checked=False)
   else:
    need(a.controls_gate and a.controls_gate_sha256,'EXPLICIT_CONTROLS_GATE');gate=read(a.controls_gate,a.controls_gate_sha256)
    need(gate['status']==CONTROLS and gate['verifier']=='/root/checkpoint_audit'and gate['producer']=='/root/native_driver'
     and gate['method']=='independent_artifact_check','CONTROLS_GATE');closure(gate)
    need(author['status']=='CANDIDATE_FROZEN_ROOT_SELECTED_NEIGHBOR_GRAPH_INPUT_V1_PENDING_INDEPENDENT_CHECK'
     and author['scientific_launched']is False and author['target_resolution']=='NONE','AUTHOR_PROJECT_SCOPE')
    for name,identity in ACTUAL.items():pin(name,identity)
    complete=read(FULL,ACTUAL[FULL]);review(complete);closure(complete)
    selected=read(TRIPLES,ACTUAL[TRIPLES]);original=S.parse_state((ROOT/R.STATE).read_bytes());base=K.from_triples(original['current'],99,7,11)
    evaluated=K.evaluate(base,K.labelled_universe(base)[121302]);rebuilt=K.reconstruct_triples(base,evaluated)
    need(same(selected['triples'],rebuilt)and selected['proposal_id']==121302 and type(selected['proposal_id'])is int,'EXACT_SELECTED_TRIPLES')
    expected_record=R.expected_record(base,121302,K.labelled_universe(base));ties=read(MANIFEST.replace('manifest.json','best_root_ties.json'))
    R.check_record(next(record for record in ties['records']if record['proposal_id']==121302),expected_record)
    need(min(ties['records'],key=lambda record:(record['new_root_residual'],record['new_mu'],record['proposal_id']))['proposal_id']==121302,'EXACT_SELECTION_RULE')
    description=author['graph_input'];pin(description['path'],description['sha256']);raw=(ROOT/description['path']).read_bytes()
    need(type(description['bytes'])is int and len(raw)==description['bytes'],'RAW_BYTES');obj,newbase,scalar=decode(raw,actual=True)
    need(same(obj['ordered_triples'],selected['triples'])and same(obj['frozen_rows'],selected['frozen_rows'])
     and same(obj['mutable_labels'],selected['mutable_labels'])and K.matrix_bytes(newbase['bits'])==(ROOT/MATRIX).read_bytes(),'LOSSLESS_ORDERED_INPUT')
    need(same([author['metrics'],author['ordered_triples'],author['mutable_lines'],author['frozen_lines'],author['selected_proposal_id']],
     [dict(E_lambda=0,E_mu=5408,R_root=10),231,224,7,121302]),'EXACT_PROJECT_REPORT')
    save(out/'graph_input_audit.json',dict(graph_input=description,selected_record=expected_record,scalar=scalar,frozen_rows=newbase['frozen'],mutable_labels=newbase['mutable']))
    result=dict(status=PASS,producer_outputs_checked=True,actual_selected_graph_checked=True,graph_input_sha256=description['sha256'],graph_input_path=description['path'],
     source_matrix_sha256=ACTUAL[MATRIX],source_triples_sha256=ACTUAL[TRIPLES],source_complete_audit_sha256=ACTUAL[FULL],selected_proposal_id=121302,metrics=obj['metrics'],
     n=99,point_degree=7,root=11,ordered_triples=231,frozen_lines=7,mutable_lines=224,frozen_original_literal_rows=newbase['frozen'],
     complete_scalar_entries=9801,identity_mismatches=scalar['identity_mismatches'],
     target_candidate_object=None if not scalar['srg_valid']else description)
   result.update(terminal_record=dict(path=a.supervisor,sha256=a.supervisor_sha256,elapsed_seconds=ended['elapsed_seconds'],exit_code=0,reaped=True,job_empty=True))
  need(all(sha(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED_STATE_UNCHANGED')
  save(out/'summary.json',dict(**result,timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',
   inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),native_calls=0,census_calls=0,ledger_mutations=0,index_mutations=0,
   historical_native_state_written=False,target_resolution='NONE',historical_protected_execution_state=protected,deadline=deadline.status(),
   shared_components=['Previously independently calibrated bitmask graph/scorer K, adjacency-set/native-state/scalar-matrix checker S, and literal selected-record checker R; no producer imports.',
    'Own new graph-only typed JSON/provenance and source-gate path; old gates do not approve this changed checking interface.',
    'Python/JSON/SHA256, locked environment and contained deadline runtime are trusted.'],
   limitations=['A lossless derivative of one exact independently checked labelled neighbor only; no new neighborhood, trajectory, global-minimum or target exclusion claim.',
    'Original native state/RNG/counters/cache/history are never manufactured; retained graph-only provenance is literal and scoped.',
    'Synthetic cube12_defect calibration differs from the producer truecube12 fixture; raw controls check that producer fixture separately.',
    'Any actual99 matrix identity zero requires separate ROOT candidate-resolution review regardless conservative target_resolution field.']))
  print(result['status'])
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),preserved_outputs=True));raise
if __name__=='__main__':main()
