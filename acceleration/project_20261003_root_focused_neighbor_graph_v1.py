"""Lossless selected-neighbor graph projection; no native state or search."""
import argparse,copy,hashlib,importlib.util,json,platform,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
ENGINE='acceleration/census_20261003_root_focused_two_line_v1.py'
ENGINE_SHA='bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017'
ENGINE_SPEC='acceleration/census_20261003_root_focused_two_line_v1_spec.md'
ENGINE_SPEC_SHA='9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8'
SELF='acceleration/project_20261003_root_focused_neighbor_graph_v1.py'
SPEC='acceleration/project_20261003_root_focused_neighbor_graph_v1_spec.md'
SCHEMA='FROZEN_ROOT_SELECTED_NEIGHBOR_GRAPH_INPUT_V1'
FULL='acceleration/results/20261003_independent_review/root_focused_census_full01/summary.json'
FULL_SHA='ef948e877938dec885b5155768d7f46c102f011d8e79c090ad9116d42da03d09'
MANIFEST='acceleration/results/20261003_root_focused_two_line_census01/manifest.json'
MANIFEST_SHA='4fc77b2f2b738d33901f6bea1f5d11c92daee561b210e0f2a370b17bbedfd056'
MATRIX='acceleration/results/20261003_root_focused_two_line_census01/best_root_neighbor.adj'
MATRIX_SHA='c01ce27d15cad11f4bdee63b6bdba91c5b18a8a6e8022c40317427cc314d6ce3'
TRIPLES='acceleration/results/20261003_root_focused_two_line_census01/best_root_neighbor_triples.json'
TRIPLES_SHA='b2d12a902a13e4c73ae10b1d3e2c78455612215565dfb7efbb878580f36a1bf0'
FIXTURES={
 'rook9':('acceleration/results/20261003_root_focused_two_line_controls01/rook9.json','a98b36598b2c36796ff895f45564bd5b83c112f1792fd9d80632b88f7d53c821'),
 'prism9':('acceleration/results/20261003_root_focused_two_line_controls01/prism9.json','009f8ada57464ccb1c0c3c24d426a1e244ccd69b501377c61d0519ad29ecabff'),
 'cube12':('acceleration/results/20261003_root_focused_two_line_controls01/cube12.json','9424900a176eece648eeef84eb2d7acf6758109e15c88a2e1acb7e2b3ea66220')}
class CheckError(ValueError):
 def __init__(self,stage,message):self.stage=stage;super().__init__(stage+': '+message)
def need(ok,stage,message):
 if not ok:raise CheckError(stage,message)
def sha(path):
 with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def equal(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return set(a)==set(b)and all(equal(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
 return a==b
def unique(pairs):
 result={}
 for k,v in pairs:need(k not in result,'PROJECTION_JSON','duplicate key');result[k]=v
 return result
def loads(raw):
 try:return json.loads(raw.decode('utf8'),object_pairs_hook=unique)
 except CheckError:raise
 except (ValueError,UnicodeError)as e:raise CheckError('PROJECTION_JSON','literal UTF8 JSON')from e
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def lib():
 need(sha(ROOT/ENGINE)==ENGINE_SHA and sha(ROOT/ENGINE_SPEC)==ENGINE_SPEC_SHA,'ENGINE_SOURCE','unchanged original generic functions')
 spec=importlib.util.spec_from_file_location('unchanged_fixed_root_engine',ROOT/ENGINE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def actual_provenance():
 return dict(mode='actual_independently_checked_selected_artifact',selected_proposal_id=121302,
  source_manifest=dict(path=MANIFEST,sha256=MANIFEST_SHA),source_matrix=dict(path=MATRIX,sha256=MATRIX_SHA),
  source_triples=dict(path=TRIPLES,sha256=TRIPLES_SHA),source_complete_audit=dict(path=FULL,sha256=FULL_SHA,status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS'),
  historical_native_state_written=False,line_order='Exact ordered source triples, seven original literal rows preserved.')
def synthetic_provenance():
 return dict(mode='synthetic_engineering_fixture',selected_proposal_id=None,source_manifest=None,source_matrix=None,source_triples=None,source_complete_audit=None,
  null_reason='Generic engineering fixture, not an actual selected99graph or historical computation.',historical_native_state_written=False,line_order='Literal synthetic fixture order.')
def payload(base,provenance):
 return dict(schema=SCHEMA,n=base['n'],degree=base['degree'],root=base['root'],ordered_triples=copy.deepcopy(base['triples']),
  frozen_rows=copy.deepcopy(base['frozen_rows']),mutable_labels=base['mutable_labels'][:],
  metrics=dict(E_lambda=base['lambda_energy'],E_mu=base['mu_energy'],R_root=base['root_residual']),provenance=provenance)
def decode(raw,engine,target=False):
 obj=loads(raw)
 need(type(obj)is dict and set(obj)=={'schema','n','degree','root','ordered_triples','frozen_rows','mutable_labels','metrics','provenance'}and obj['schema']==SCHEMA,'PROJECTION_SCHEMA','exact graph-only schema')
 need(all(type(obj[k])is int for k in('n','degree','root')),'PROJECTION_DOMAIN','literal integer dimensions')
 prov=obj['provenance']
 need(equal(prov,actual_provenance())or equal(prov,synthetic_provenance()),'PROJECTION_PROVENANCE','exact actual or declared synthetic provenance')
 if target:need(equal(prov,actual_provenance())and(obj['n'],obj['degree'],obj['root'])==(99,7,11),'TARGET_SCOPE','actual checked99selected graph only')
 base=engine.domain(obj['n'],obj['degree'],obj['ordered_triples'],obj['root'])
 need(equal(obj['frozen_rows'],base['frozen_rows'])and equal(obj['mutable_labels'],base['mutable_labels']),'PROJECTION_FROZEN','complete literal frozen rows and mutable labels')
 need(equal(obj['metrics'],dict(E_lambda=base['lambda_energy'],E_mu=base['mu_energy'],R_root=base['root_residual'])),'PROJECTION_ENERGY','complete recomputed integer components')
 if target:
  need(base['frozen_rows']==engine.FROZEN_ROWS and base['total']==224784 and len(base['triples'])==231
   and(base['lambda_energy'],base['mu_energy'],base['root_residual'])==(0,5408,10),'TARGET_GRAPH','exact selected graph scope')
  need(hashlib.sha256(engine.adjacency_bytes(base['masks'])).hexdigest()==MATRIX_SHA,'TARGET_MATRIX','entire raw selected matrix')
 return base,obj
def review(gate):
 need(type(gate)is dict and gate.get('status')=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS'
  and gate.get('producer')=='/root/native_driver'and gate.get('verifier')=='/root/checkpoint_audit'and gate.get('method')=='independent_artifact_check'
  and gate.get('target_resolution')=='NONE','SOURCE_REVIEW','exact complete original census audit')
 need(type(gate.get('complete_labelled_proposals'))is int and gate['complete_labelled_proposals']==224784
  and type(gate.get('selected_proposal_id'))is int and gate['selected_proposal_id']==121302
  and type(gate.get('mutable_label_count'))is int and gate['mutable_label_count']==224 and gate.get('literal_one_move_population_only')is True,'SOURCE_REVIEW','complete finite population and exact selection')
 for path,identity in[(MANIFEST,MANIFEST_SHA),(MATRIX,MATRIX_SHA),(TRIPLES,TRIPLES_SHA)]:
  need(gate.get('inputs_sha256',{}).get(path)==identity,'SOURCE_REVIEW','independent source artifact binding')
def fixture_review():
 # Synthetic interface control, not a historical verifier record or fabricated replay.
 return dict(status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS',producer='/root/native_driver',verifier='/root/checkpoint_audit',
  method='independent_artifact_check',target_resolution='NONE',complete_labelled_proposals=224784,selected_proposal_id=121302,
  mutable_label_count=224,literal_one_move_population_only=True,inputs_sha256={MANIFEST:MANIFEST_SHA,MATRIX:MATRIX_SHA,TRIPLES:TRIPLES_SHA})
def controls(out,d,engine,pins):
 records=[];positives=[]
 for name,(path,identity)in FIXTURES.items():
  need(sha(ROOT/path)==identity,'CONTROL_FIXTURE','exact preserved fixture');pins[path]=identity
  fixture=loads((ROOT/path).read_bytes());base=engine.domain(**fixture);obj=payload(base,synthetic_provenance())
  raw=(json.dumps(obj,indent=2)+'\n').encode();(out/(name+'.graph.json')).write_bytes(raw);parsed,read=decode(raw,engine)
  need(read==obj and engine.adjacency_bytes(parsed['masks'])==engine.adjacency_bytes(base['masks']),'CONTROL','lossless literal graph projection')
  positives.append(name)
  if name!='rook9':continue
  need((base['lambda_energy'],base['mu_energy'],base['root_residual'])==(0,0,0),'CONTROL','known generic rook9 SRG')
  def reject(label,stage,bad,call=None):
   need(d.status()['remaining_seconds']>20,'CONTROL_DEADLINE','save reserve')
   blob=bad if type(bad)is bytes else(json.dumps(bad,indent=2)+'\n').encode();(out/(label+'.json')).write_bytes(blob)
   try:(call or(lambda:decode(blob,engine)))()
   except (CheckError,engine.CheckError)as e:need(e.stage==stage,'CONTROL','precise rejected stage '+label);records.append(dict(case=label,stage=stage,outcome='REJECTED'));return
   raise CheckError('CONTROL','unexpected acceptance '+label)
  def mutation(label,stage,change):
   bad=copy.deepcopy(obj);change(bad);reject(label,stage,bad)
  reject('malformed_json','PROJECTION_JSON',b'{broken')
  reject('duplicate_key','PROJECTION_JSON',b'{"n":9,"n":9}')
  mutation('extra_field','PROJECTION_SCHEMA',lambda x:x.update(extra=1))
  mutation('schema','PROJECTION_SCHEMA',lambda x:x.update(schema='ROOT_FOCUSED_ANNEAL_STATE_V1'))
  for key in['n','degree','root']:mutation('bool_'+key,'PROJECTION_DOMAIN',lambda x,k=key:x.update({k:True}))
  mutation('duplicate_vertex','DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(1,x['ordered_triples'][0][0]))
  mutation('duplicate_triple','DOMAIN',lambda x:x['ordered_triples'].__setitem__(1,list(x['ordered_triples'][0])))
  mutation('repeated_pair','LINEARITY',lambda x:x['ordered_triples'].__setitem__(1,[3,4,0]))
  mutation('bool_point','DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(0,False))
  mutation('point_out_of_range','DOMAIN',lambda x:x['ordered_triples'][0].__setitem__(0,9))
  mutation('removed_line','DEGREE',lambda x:x['ordered_triples'].pop())
  mutation('reordered_frozen','PROJECTION_FROZEN',lambda x:x['frozen_rows'][0].reverse())
  mutation('missing_mutable','PROJECTION_FROZEN',lambda x:x['mutable_labels'].pop())
  mutation('bool_mutable','PROJECTION_FROZEN',lambda x:x['mutable_labels'].__setitem__(0,True))
  for key in['E_lambda','E_mu','R_root']:
   mutation('wrong_'+key,'PROJECTION_ENERGY',lambda x,k=key:x['metrics'].__setitem__(k,x['metrics'][k]+1))
  mutation('bool_energy','PROJECTION_ENERGY',lambda x:x['metrics'].__setitem__('E_mu',False))
  mutation('forged_native_history','PROJECTION_PROVENANCE',lambda x:x['provenance'].update(historical_native_state_written=True))
  mutation('wrong_provenance','PROJECTION_PROVENANCE',lambda x:x['provenance'].update(mode='actual99'))
  reject('rook_is_not_target99','TARGET_SCOPE',obj,call=lambda:decode(raw,engine,target=True))
  actual=payload(base,actual_provenance())
  reject('actual_provenance_not_enough','TARGET_SCOPE',actual,call=lambda:decode((json.dumps(actual)+'\n').encode(),engine,target=True))
 synthetic_gate=fixture_review();review(synthetic_gate);save(out/'synthetic_source_review_fixture.json',synthetic_gate)
 review_controls=[]
 def review_reject(label,change):
  need(d.status()['remaining_seconds']>20,'CONTROL_DEADLINE','save reserve')
  bad=copy.deepcopy(synthetic_gate);change(bad);save(out/(label+'.json'),bad)
  try:review(bad)
  except CheckError as e:need(e.stage=='SOURCE_REVIEW','CONTROL','exact source review diagnostic');review_controls.append(dict(case=label,stage=e.stage,outcome='REJECTED'));return
  raise CheckError('CONTROL','unexpected source review acceptance')
 for key in ['status','producer','verifier','method','target_resolution']:
  review_reject('review_wrong_'+key,lambda g,k=key:g.__setitem__(k,'wrong'))
 for key in ['complete_labelled_proposals','selected_proposal_id','mutable_label_count']:
  review_reject('review_wrong_'+key,lambda g,k=key:g.__setitem__(k,g[k]+1))
  review_reject('review_bool_'+key,lambda g,k=key:g.__setitem__(k,True))
 review_reject('review_whole_graph_space',lambda g:g.__setitem__('literal_one_move_population_only',False))
 review_reject('review_missing_matrix',lambda g:g['inputs_sha256'].pop(MATRIX))
 review_reject('review_wrong_triples_hash',lambda g:g['inputs_sha256'].__setitem__(TRIPLES,'0'*64))
 save(out/'summary.json',dict(status='AUTHOR_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_CONTROLS_PENDING_INDEPENDENT_GATE',
  timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',positive_fixtures=positives,strict_negative_count=len(records),strict_negatives=records,
  source_review_synthetic_positive=1,source_review_strict_negative_count=len(review_controls),source_review_strict_negatives=review_controls,
  inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),independent_approval=False,actual_selected_graph_read=False,
  historical_native_state_written=False,scientific_launched=False,deadline=d.status()))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','project']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--source-commit',required=True)
 p.add_argument('--controls-gate',type=Path);p.add_argument('--controls-gate-sha256');a=p.parse_args()
 d=CommandDeadline(a.seconds,allocation_reason='Graph-only selected neighbor conversion or generic finite controls; all hashing/derivation/write included; no search/native state')
 out=a.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'PATH','fresh bounded projection output');out.mkdir(parents=True)
 pins={}
 def pin(path,identity=None):
  need(not d.status()['stop_required']and d.status()['remaining_seconds']>20,'DEADLINE','preserve output reserve')
  full=(ROOT/path).resolve();need(full.is_relative_to(ROOT)and full.is_file(),'PATH','bounded existing input')
  actual=sha(full);need(identity is None or actual==identity,'SOURCE','exact input '+str(path));pins[Path(path).as_posix()]=actual;return actual
 try:
  pin(ENGINE,ENGINE_SHA);pin(ENGINE_SPEC,ENGINE_SPEC_SHA);pin(SELF);pin(SPEC);engine=lib()
  for path,identity in engine.SOFTWARE.items():pin(path,identity)
  if a.mode=='controls':controls(out,d,engine,pins);return
  need(a.controls_gate is not None and a.controls_gate_sha256 is not None,'CONTROLS_GATE','new independent projection controls required')
  gatepath=a.controls_gate.resolve();need(gatepath.is_relative_to(ROOT),'PATH','bounded controls gate');name=gatepath.relative_to(ROOT).as_posix();pin(name,a.controls_gate_sha256);gate=loads(gatepath.read_bytes())
  need(gate.get('status')=='INDEPENDENT_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_V1_CONTROLS_PASS'and gate.get('producer')=='/root/native_driver'
   and gate.get('verifier')=='/root/checkpoint_audit'and gate.get('method')=='independent_artifact_check','CONTROLS_GATE','separate exact graph projection engineering scope')
  for path,identity in pins.items():
   if path!=name:need(gate.get('inputs_sha256',{}).get(path)==identity,'CONTROLS_GATE','exact projection source/software '+path)
  for path,identity in[(FULL,FULL_SHA),(MANIFEST,MANIFEST_SHA),(MATRIX,MATRIX_SHA),(TRIPLES,TRIPLES_SHA)]:pin(path,identity)
  verified=loads((ROOT/FULL).read_bytes());review(verified)
  for path,identity in verified['inputs_sha256'].items():pin(path,identity)
  selected=loads((ROOT/TRIPLES).read_bytes())
  need(set(selected)=={'n','degree','root','frozen_rows','mutable_labels','triples','proposal_id'}and selected['proposal_id']==121302 and type(selected['proposal_id'])is int,'SOURCE_TRIPLES','exact raw ordered selection')
  base=engine.domain(selected['n'],selected['degree'],selected['triples'],selected['root'])
  obj=payload(base,actual_provenance());raw=(json.dumps(obj,indent=2)+'\n').encode();decode(raw,engine,target=True)
  need(equal(selected['frozen_rows'],base['frozen_rows'])and equal(selected['mutable_labels'],base['mutable_labels'])and engine.adjacency_bytes(base['masks'])==(ROOT/MATRIX).read_bytes(),'SOURCE_MATRIX','entire source matrix and frozen/mutable rows reproduced')
  path=out/'graph_input.json';path.write_bytes(raw)
  save(out/'summary.json',dict(status='CANDIDATE_FROZEN_ROOT_SELECTED_NEIGHBOR_GRAPH_INPUT_V1_PENDING_INDEPENDENT_CHECK',
   timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_reference_commit=a.source_commit,
   source_reference_scope='Published baseline only; new producer/spec/gates/raw candidate closure remains separate LOCAL_ONLY working inputs.',
   inputs_sha256=pins,graph_input=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=len(raw)),metrics=obj['metrics'],
   ordered_triples=231,mutable_lines=224,frozen_lines=7,selected_proposal_id=121302,historical_native_state_written=False,scientific_launched=False,
   independent_approval=False,target_resolution='NONE',deadline=d.status(),limitations=['Lossless graph-only derivative; original native state, RNG and counters are not reproduced or overwritten.','Original complete census is scoped to one old graph; this new graph has no neighborhood claim until a separately gated census.','Separate checkpoint full derivative/object/provenance check and ROOT review are mandatory before new census.']))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,scientific_launched=False,historical_native_state_written=False,deadline=d.status()));raise
if __name__=='__main__':main()

