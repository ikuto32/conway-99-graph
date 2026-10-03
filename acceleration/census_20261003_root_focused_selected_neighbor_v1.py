"""Exact fixed-root two-line census from a separately checked graph-only neighbor."""
import argparse,copy,hashlib,importlib.metadata,importlib.util,json,platform,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
SELF='acceleration/census_20261003_root_focused_selected_neighbor_v1.py'
SPEC='acceleration/census_20261003_root_focused_selected_neighbor_v1_spec.md'
PROJECTOR='acceleration/project_20261003_root_focused_neighbor_graph_v1.py'
PROJECTOR_SHA='593b04087da6d54f9d25c159466100dc2b215615d088caf1af7b0eb33009353c'
PROJECTOR_SPEC='acceleration/project_20261003_root_focused_neighbor_graph_v1_spec.md'
PROJECTOR_SPEC_SHA='9842e294d920094140776246c6a36ed2b840f948cefac5607129be23bf0864ec'
CONTROLS_STATUS='INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_CONTROLS_PASS'
INPUT_STATUS='INDEPENDENT_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_V1_COMPLETE_PASS'
class CheckError(ValueError):
 def __init__(self,stage,message):self.stage=stage;super().__init__(stage+': '+message)
def need(ok,stage,message):
 if not ok:raise CheckError(stage,message)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def lib():
 need(sha(ROOT/PROJECTOR)==PROJECTOR_SHA and sha(ROOT/PROJECTOR_SPEC)==PROJECTOR_SPEC_SHA,'SOURCE','unchanged graph-only projection reader')
 spec=importlib.util.spec_from_file_location('selected_neighbor_graph_projection',ROOT/PROJECTOR)
 p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 return p,p.lib()
def review_input(gate,graph_path,graph_sha,projector,engine):
 need(type(gate)is dict and gate.get('status')==INPUT_STATUS and gate.get('producer')=='/root/native_driver'
  and gate.get('verifier')=='/root/checkpoint_audit' and gate.get('method')=='independent_artifact_check'
  and gate.get('target_resolution')=='NONE' and gate.get('historical_native_state_written')is False,'INPUT_GATE','new graph-only input approval/roles/scope')
 dims={'n':99,'point_degree':7,'root':11,'ordered_triples':231,'mutable_lines':224,'frozen_lines':7,'selected_proposal_id':121302}
 need(all(type(gate.get(k))is int and gate[k]==v for k,v in dims.items()),'INPUT_GATE','exact selected labelled99domain')
 need(gate.get('graph_input_path')==graph_path and gate.get('graph_input_sha256')==graph_sha
  and gate.get('source_matrix_sha256')==projector.MATRIX_SHA and gate.get('source_triples_sha256')==projector.TRIPLES_SHA
  and gate.get('source_complete_audit_sha256')==projector.FULL_SHA,'INPUT_GATE','new derivative and original selected raw identity')
 need(projector.equal(gate.get('metrics'),dict(E_lambda=0,E_mu=5408,R_root=10))
  and projector.equal(gate.get('frozen_original_literal_rows'),engine.FROZEN_ROWS),'INPUT_GATE','exact literal original root lines and metrics')
 for path,identity in [(graph_path,graph_sha),(projector.MATRIX,projector.MATRIX_SHA),(projector.TRIPLES,projector.TRIPLES_SHA),
  (projector.FULL,projector.FULL_SHA),(PROJECTOR,PROJECTOR_SHA),(PROJECTOR_SPEC,PROJECTOR_SPEC_SHA)]:
  need(gate.get('inputs_sha256',{}).get(path)==identity,'INPUT_GATE','independent raw graph/input closure '+path)
def review_controls(gate,software):
 need(type(gate)is dict and gate.get('status')==CONTROLS_STATUS and gate.get('producer')=='/root/native_driver'
  and gate.get('verifier')=='/root/checkpoint_audit'and gate.get('method')=='independent_artifact_check'
  and gate.get('target_resolution')=='NONE','CONTROLS_GATE','new reader/wrapper exact finite engineering gate')
 for path,identity in software.items():need(gate.get('inputs_sha256',{}).get(path)==identity,'CONTROLS_GATE','new wrapper/reader and unchanged kernel/runtime '+path)
def synthetic_gate(projector,engine):
 graph_path='synthetic/graph_only_input.json';graph_sha='0'*64
 gate=dict(status=INPUT_STATUS,producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',
  target_resolution='NONE',historical_native_state_written=False,n=99,point_degree=7,root=11,ordered_triples=231,
  mutable_lines=224,frozen_lines=7,selected_proposal_id=121302,graph_input_path=graph_path,graph_input_sha256=graph_sha,
  source_matrix_sha256=projector.MATRIX_SHA,source_triples_sha256=projector.TRIPLES_SHA,source_complete_audit_sha256=projector.FULL_SHA,
  metrics=dict(E_lambda=0,E_mu=5408,R_root=10),frozen_original_literal_rows=engine.FROZEN_ROWS,
  inputs_sha256={graph_path:graph_sha,projector.MATRIX:projector.MATRIX_SHA,projector.TRIPLES:projector.TRIPLES_SHA,projector.FULL:projector.FULL_SHA,
   PROJECTOR:PROJECTOR_SHA,PROJECTOR_SPEC:PROJECTOR_SPEC_SHA})
 return graph_path,graph_sha,gate
def engineering(out,deadline,software,source_commit,projector,engine):
 out.mkdir(parents=True,exist_ok=False)
 # Same deadline; no old main, target read, global override, separate child or retry.
 engine.engineering(out/'unchanged_kernel',deadline,software,source_commit)
 reader=out/'graph_reader';reader.mkdir();reader_pins=dict(software);projector.controls(reader,deadline,engine,reader_pins)
 graph_path,graph_sha,gate=synthetic_gate(projector,engine);save(out/'synthetic_input_gate.json',gate)
 review_input(gate,graph_path,graph_sha,projector,engine);negatives=[]
 def reject(name,change):
  need(deadline.status()['remaining_seconds']>20,'CONTROL_DEADLINE','same invocation preservation reserve')
  bad=copy.deepcopy(gate);change(bad);save(out/(name+'.json'),bad)
  try:review_input(bad,graph_path,graph_sha,projector,engine)
  except CheckError as e:need(e.stage=='INPUT_GATE','CONTROL','exact metadata veto');negatives.append(dict(case=name,stage=e.stage,outcome='REJECTED'));return
  raise CheckError('CONTROL','accepted malformed input gate')
 for key in ['status','producer','verifier','method','target_resolution']:
  reject('wrong_gate_'+key,lambda x,k=key:x.__setitem__(k,'wrong'))
 reject('forged_native_history',lambda x:x.__setitem__('historical_native_state_written',True))
 for key in ['n','point_degree','root','ordered_triples','mutable_lines','frozen_lines','selected_proposal_id']:
  reject('wrong_gate_'+key,lambda x,k=key:x.__setitem__(k,x[k]+1))
  reject('boolean_gate_'+key,lambda x,k=key:x.__setitem__(k,True))
 for key in ['graph_input_path','graph_input_sha256','source_matrix_sha256','source_triples_sha256','source_complete_audit_sha256']:
  reject('wrong_gate_'+key,lambda x,k=key:x.__setitem__(k,'wrong'))
 reject('reordered_frozen',lambda x:x['frozen_original_literal_rows'][0].reverse())
 for key in ['E_lambda','E_mu','R_root']:reject('wrong_metric_'+key,lambda x,k=key:x['metrics'].__setitem__(k,x['metrics'][k]+1))
 reject('bool_metric',lambda x:x['metrics'].__setitem__('E_mu',True))
 reject('missing_graph_pin',lambda x:x['inputs_sha256'].pop(graph_path))
 reject('wrong_projector_pin',lambda x:x['inputs_sha256'].__setitem__(PROJECTOR,'0'*64))
 # The synthetic gate above is expressly not a historical99 checking record.
 kernel=projector.loads((out/'unchanged_kernel'/'summary.json').read_bytes())
 reader_report=projector.loads((reader/'summary.json').read_bytes())
 save(out/'summary.json',dict(status='AUTHOR_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE',
  timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',source_reference_commit=source_commit,
  command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),
  inputs_sha256=reader_pins,unchanged_kernel_report=dict(path=(out/'unchanged_kernel'/'summary.json').relative_to(ROOT).as_posix(),sha256=sha(out/'unchanged_kernel'/'summary.json')),
  unique_complete_proposal_records_checked=kernel['unique_complete_proposal_records_checked'],recorded_proposal_evaluation_calls=kernel['recorded_proposal_evaluation_calls'],
  additional_known_overlap_evaluation_calls=kernel['additional_known_overlap_evaluation_calls'],kernel_negative_controls=kernel['strict_negative_count'],
  whole_split_equal=kernel['whole_split_equal'],graph_reader_positive_fixtures=reader_report['positive_fixtures'],
  graph_reader_specific_negatives=reader_report['strict_negative_count'],source_review_specific_negatives=reader_report['source_review_strict_negative_count'],
  input_gate_synthetic_positive=1,input_gate_specific_negative_count=len(negatives),input_gate_specific_negatives=negatives,
  actual_selected_graph_read=False,historical_native_state_written=False,scientific_census_launched=False,independent_approval=False,
  target_resolution='NONE',deadline=deadline.status(),
  limitations=['Unchanged original kernel controls are repeated as finite integration tests with the new reader/wrapper identity; they do not gate old main on a new graph.',
   'Synthetic gate/provenance metadata is marked as engineering data, not a fabricated historical check. Separate independent full derivative and changed-wrapper gates required.']))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['controls','census']);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--seconds',type=float,required=True);p.add_argument('--source-commit',required=True)
 p.add_argument('--graph-input',type=Path);p.add_argument('--graph-input-sha256');p.add_argument('--input-gate',type=Path);p.add_argument('--input-gate-sha256')
 p.add_argument('--controls-gate',type=Path);p.add_argument('--controls-gate-sha256');p.add_argument('--resume',type=Path);p.add_argument('--resume-sha256')
 a=p.parse_args();deadline=CommandDeadline(a.seconds,allocation_reason='Graph-only input or finite integration controls for one selected-neighbor fixed-root census; all preparation/hashing/write share this deadline')
 out=a.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'PATH','fresh bounded output')
 pins={}
 def pin(path,identity=None):
  need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'DEADLINE','preserve complete prefix/receipt')
  path=(ROOT/path).resolve();need(path.is_relative_to(ROOT)and path.is_file(),'PATH','bounded existing source/input')
  actual=sha(path);need(identity is None or actual==identity,'SOURCE','exact source/input '+str(path));pins[path.relative_to(ROOT).as_posix()]=actual;return path
 try:
  pin(PROJECTOR,PROJECTOR_SHA);pin(PROJECTOR_SPEC,PROJECTOR_SPEC_SHA);projector,engine=lib()
  pin(projector.ENGINE,projector.ENGINE_SHA);pin(projector.ENGINE_SPEC,projector.ENGINE_SPEC_SHA)
  pin(SELF);pin(SPEC)
  for path,identity in engine.SOFTWARE.items():pin(path,identity)
  software=dict(pins)
  if a.mode=='controls':engineering(out,deadline,software,a.source_commit,projector,engine);return
  need(all(v is not None for v in [a.graph_input,a.graph_input_sha256,a.input_gate,a.input_gate_sha256,a.controls_gate,a.controls_gate_sha256]),'GATES','complete new graph/wrapper gate interface')
  graph=pin(a.graph_input,a.graph_input_sha256);gatepath=pin(a.input_gate,a.input_gate_sha256)
  gate=projector.loads(gatepath.read_bytes());review_input(gate,graph.relative_to(ROOT).as_posix(),a.graph_input_sha256,projector,engine)
  controlpath=pin(a.controls_gate,a.controls_gate_sha256);control=projector.loads(controlpath.read_bytes());review_controls(control,software)
  for report in [gate,control]:
   for path,identity in report['inputs_sha256'].items():pin(path,identity)
  base,raw=projector.decode(graph.read_bytes(),engine,target=True)
  need(base['total']==224784 and base['frozen_rows']==engine.FROZEN_ROWS,'INPUT_DOMAIN','unchanged labelled/frozen-root population')
  identity=dict(inputs_sha256=dict(pins),software=software,n=99,degree=7,root=11,total=224784,source_reference_commit=a.source_commit,
   source_reference_scope='Publishedbaseline context only; changed graph/wrapper/checker closure is separately LOCAL_ONLY.',
   graph_input_schema=projector.SCHEMA,graph_only_input=True,historical_native_state_written=False,
   frozen_rows=base['frozen_rows'],mutable_labels=base['mutable_labels'],
   proposal_order='lex original mutable labels i<j;selected ix,jy lex;9*pair_index+3*ix+jy',
   question='exists admissible lambda-preserving strictly rootR-descending proposal from ONE exact selected121302 graph;mu may worsen',
   input_selection='Prior independent census selected121302 lexR then mu then pid; graphlambda0/R10/mu5408;no fabricated native final.state or history.')
  resume=None
  if a.resume is not None:
   need(a.resume_sha256 is not None,'CHECKPOINT_IDENTITY','explicit checkpoint identity required')
   cp=pin(a.resume,a.resume_sha256);resume=projector.loads(cp.read_bytes())
  manifest=engine.enumerate_to(base,out,deadline,identity,resume=resume)
  save(out/'run_receipt.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',source_reference_commit=a.source_commit,
   command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),
   manifest_sha256=sha(out/'manifest.json'),deadline=deadline.status(),historical_native_state_written=False,
   independently_approved_input_gate=a.input_gate_sha256,new_wrapper_controls_gate=a.controls_gate_sha256,
   target_resolution='NONE',independent_approval=False,overall_search_coverage='UNKNOWN;no validated denominator.'))
 except BaseException as e:
  out.mkdir(parents=True,exist_ok=True);save(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,deadline=deadline.status(),historical_native_state_written=False,target_resolution='NONE'));raise
if __name__=='__main__':main()
