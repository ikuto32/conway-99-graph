"""New graph-only selected-neighbor census checker; no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from types import SimpleNamespace
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S
import audit_20261003_root_focused_census_records_v2 as R
import audit_20261003_root_focused_neighbor_graph_v1 as G

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/audit_20261003_root_focused_neighbor_census_v1.py'
SPEC='acceleration/audit_20261003_root_focused_neighbor_census_v1_spec.md'
PRODUCER='acceleration/census_20261003_root_focused_selected_neighbor_v1.py'
PRODUCER_SPEC='acceleration/census_20261003_root_focused_selected_neighbor_v1_spec.md'
CAL='INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_RECORDS_V1_CALIBRATION_PASS'
CONTROLS='INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_CONTROLS_PASS'
PASS='INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_COMPLETE_PASS'
PINS={**G.PINS,
 PRODUCER:'092a4b7f895724832583909d22e373611960386f2a12a098d1583638b8925f2a',
 PRODUCER_SPEC:'7a4678e30b256ef5185d1a65385806e192c83dcf4b7431c81791f4d5b38c7617',
 G.SOURCE:'434ba53ed2e00663fa8464930bd3000457fd04158265fa0d7184048deb19be02',
 G.SPEC:'f6dd849519a13ca4abd9bab812631313dc52580f3afac9a43cf03c043cfc0f8a'}
SOFTWARE={name:PINS[name] for name in [PRODUCER,PRODUCER_SPEC,G.PRODUCER,G.PRODUCER_SPEC,
 'acceleration/census_20261003_root_focused_two_line_v1.py','acceleration/census_20261003_root_focused_two_line_v1_spec.md']}
SOFTWARE.update({'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/native_budget_env_v1/pyproject.toml':'96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
 'acceleration/native_budget_env_v1/uv.lock':'54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434'})

def need(ok,stage,message):K.require(ok,stage,message)
def sha(path):return R.sha(path)
def save(path,value):R.save(path,value)
def read_json(path):return G.loads(path.read_bytes())

def review_input(gate,graph_path,graph_sha):
 need(type(gate)is dict and R.literal_equal([gate.get(k)for k in['status','producer','verifier','method','target_resolution','historical_native_state_written']],
  [G.PASS,'/root/native_driver','/root/checkpoint_audit','independent_artifact_check','NONE',False]),'INPUT_GATE','canonical graph-only roles and history')
 dims={'n':99,'point_degree':7,'root':11,'ordered_triples':231,'mutable_lines':224,'frozen_lines':7,'selected_proposal_id':121302}
 need(all(type(gate.get(k))is int and gate[k]==v for k,v in dims.items()),'INPUT_GATE','literal selected labelled99 domain')
 need(R.literal_equal([gate.get(k)for k in['graph_input_path','graph_input_sha256','source_matrix_sha256','source_triples_sha256','source_complete_audit_sha256']],
  [graph_path,graph_sha,G.ACTUAL[G.MATRIX],G.ACTUAL[G.TRIPLES],G.ACTUAL[G.FULL]]),'INPUT_GATE','derivative and original raw identities')
 need(R.literal_equal(gate.get('metrics'),dict(E_lambda=0,E_mu=5408,R_root=10)) and R.literal_equal(gate.get('frozen_original_literal_rows'),R.FROZEN),
  'INPUT_GATE','literal frozen rows and integer components')
 required={graph_path:graph_sha,**{name:G.ACTUAL[name]for name in[G.MATRIX,G.TRIPLES,G.FULL]},G.PRODUCER:PINS[G.PRODUCER],G.PRODUCER_SPEC:PINS[G.PRODUCER_SPEC]}
 need(type(gate.get('inputs_sha256'))is dict and all(gate['inputs_sha256'].get(name)==identity for name,identity in required.items()),'INPUT_GATE','complete graph source scope')

def review_controls(gate):
 need(type(gate)is dict and R.literal_equal([gate.get(k)for k in['status','producer','verifier','method','target_resolution']],
  [CONTROLS,'/root/native_driver','/root/checkpoint_audit','independent_artifact_check','NONE']), 'CONTROLS_GATE','new exact wrapper finite gate')
 need(type(gate.get('inputs_sha256'))is dict and all(gate['inputs_sha256'].get(name)==identity for name,identity in SOFTWARE.items()),
  'CONTROLS_GATE','all ten literal software identities')

def synthetic_input():
 graph_path='synthetic/graph_only_input.json';graph_sha='0'*64
 gate=dict(status=G.PASS,producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',
  historical_native_state_written=False,n=99,point_degree=7,root=11,ordered_triples=231,mutable_lines=224,frozen_lines=7,selected_proposal_id=121302,
  graph_input_path=graph_path,graph_input_sha256=graph_sha,source_matrix_sha256=G.ACTUAL[G.MATRIX],source_triples_sha256=G.ACTUAL[G.TRIPLES],
  source_complete_audit_sha256=G.ACTUAL[G.FULL],metrics=dict(E_lambda=0,E_mu=5408,R_root=10),frozen_original_literal_rows=copy.deepcopy(R.FROZEN),
  inputs_sha256={graph_path:graph_sha,**{name:G.ACTUAL[name]for name in[G.MATRIX,G.TRIPLES,G.FULL]},G.PRODUCER:PINS[G.PRODUCER],G.PRODUCER_SPEC:PINS[G.PRODUCER_SPEC]})
 return graph_path,graph_sha,gate

def reject(records,name,stage,call):
 try:call()
 except K.CensusError as error:
  need(error.stage==stage,'CONTROL','exact rejection diagnostic');records.append(dict(case=name,stage=stage,outcome='REJECTED'));return
 raise K.CensusError('CONTROL','corruption accepted: '+name)

def gate_calibration(out):
 graph_path,graph_sha,good=synthetic_input();review_input(good,graph_path,graph_sha);records=[]
 mutations=[]
 for k in['status','producer','verifier','method','target_resolution']:mutations.append(('wrong_'+k,lambda x,k=k:x.update({k:'wrong'})))
 mutations.append(('forged_history',lambda x:x.update(historical_native_state_written=True)))
 for k in['n','point_degree','root','ordered_triples','mutable_lines','frozen_lines','selected_proposal_id']:
  for value,label in[(good[k]+1,'wrong'),(True,'bool'),(float(good[k]),'float')]:mutations.append((label+'_'+k,lambda x,k=k,v=value:x.update({k:v})))
 for k in['graph_input_path','graph_input_sha256','source_matrix_sha256','source_triples_sha256','source_complete_audit_sha256']:
  mutations.append(('wrong_'+k,lambda x,k=k:x.update({k:'wrong'})))
 mutations.append(('reordered_frozen',lambda x:x['frozen_original_literal_rows'][0].reverse()))
 for k in['E_lambda','E_mu','R_root']:mutations.append(('wrong_metric_'+k,lambda x,k=k:x['metrics'].__setitem__(k,x['metrics'][k]+1)))
 mutations += [('bool_metric',lambda x:x['metrics'].__setitem__('E_mu',True)),('float_metric',lambda x:x['metrics'].__setitem__('E_mu',5408.0)),
  ('missing_graph_pin',lambda x:x['inputs_sha256'].pop(graph_path)),('wrong_projector_pin',lambda x:x['inputs_sha256'].__setitem__(G.PRODUCER,'0'*64)),
  ('missing_input_map',lambda x:x.pop('inputs_sha256'))]
 for name,change in mutations:
  bad=copy.deepcopy(good);change(bad);reject(records,name,'INPUT_GATE',lambda bad=bad:review_input(bad,graph_path,graph_sha))
 need(len(records)==41,'CALIBRATION','all41 exact input-gate corruptions')
 controls=dict(status=CONTROLS,producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',inputs_sha256=dict(SOFTWARE))
 review_controls(controls);software_records=[]
 for k in['status','producer','verifier','method','target_resolution']:
  bad=copy.deepcopy(controls);bad[k]='wrong';reject(software_records,'controls_'+k,'CONTROLS_GATE',lambda bad=bad:review_controls(bad))
 for name in SOFTWARE:
  for action in['missing','wrong']:
   bad=copy.deepcopy(controls)
   if action=='missing':bad['inputs_sha256'].pop(name)
   else:bad['inputs_sha256'][name]='0'*64
   reject(software_records,action+'_'+name,'CONTROLS_GATE',lambda bad=bad:review_controls(bad))
 need(len(software_records)==25,'CALIBRATION','all25 exact controls-gate corruptions')
 save(out/'gate_controls.json',dict(synthetic_input_positive=good,synthetic_controls_positive=controls,input_negatives=records,controls_negatives=software_records))
 return dict(synthetic_input_positives=1,precise_input_negatives=41,synthetic_controls_positives=1,precise_software_gate_negatives=25)

def reader_controls(directory,pin):
 summary=read_json(directory/'summary.json');pin((directory/'summary.json').relative_to(ROOT).as_posix())
 need(summary['status']=='AUTHOR_FROZEN_ROOT_NEIGHBOR_GRAPH_PROJECTION_CONTROLS_PENDING_INDEPENDENT_GATE' and summary['strict_negative_count']==24
  and summary['source_review_strict_negative_count']==14 and summary['actual_selected_graph_read']is False,'READER','exact actual tiny reader population')
 objects=[];records=[];reviews=[]
 for name in['rook9','prism9','cube12']:
  path=directory/(name+'.graph.json');pin(path.relative_to(ROOT).as_posix());obj,base,scalar=G.decode(path.read_bytes());need(G.same(obj['provenance'],G.provenance(False)),'READER','synthetic actual fixture scope');objects.append(dict(name=name,scalar=scalar))
 stages={'PROJECTION_SCHEMA':'GRAPH_SCHEMA','PROJECTION_DOMAIN':'GRAPH_DOMAIN','DOMAIN':'TOPOLOGY_DOMAIN','LINEARITY':'TOPOLOGY_DOMAIN','DEGREE':'TOPOLOGY_DOMAIN',
  'PROJECTION_FROZEN':'FROZEN_LABELS','PROJECTION_ENERGY':'EXACT_SCORES','PROJECTION_PROVENANCE':'PROVENANCE','TARGET_SCOPE':'TARGET_SCOPE'}
 for record in summary['strict_negatives']:
  path=directory/(record['case']+'.json');pin(path.relative_to(ROOT).as_posix());raw=path.read_bytes()
  stage=('JSON_DUPLICATE'if record['case']=='duplicate_key'else'JSON_SYNTAX')if record['stage']=='PROJECTION_JSON'else stages[record['stage']]
  need(record['outcome']=='REJECTED','READER','literal recorded rejection');G.reject(records,record['case'],stage,lambda raw=raw,stage=stage:G.decode(raw,actual=stage=='TARGET_SCOPE'))
 path=directory/'synthetic_source_review_fixture.json';pin(path.relative_to(ROOT).as_posix());G.review(read_json(path))
 for record in summary['source_review_strict_negatives']:
  path=directory/(record['case']+'.json');pin(path.relative_to(ROOT).as_posix());bad=read_json(path)
  need(record['stage']=='SOURCE_REVIEW'and record['outcome']=='REJECTED','READER','literal source-review rejection');G.reject(reviews,record['case'],'SOURCE_REVIEW',lambda bad=bad:G.review(bad))
 need(len(records)==24 and len(reviews)==14,'READER','complete actual reader corruptions')
 return dict(objects=objects,graph_negatives=records,review_negatives=reviews)

def terminal(report):
 need(type(report.get('command_exit_code'))is int and report['command_exit_code']==0 and report.get('error')is None and report.get('deadline_reached')is False
  and report.get('stop_reason')=='COMMAND_EXITED'and report.get('cleanup',{}).get('reaped')is True and report['cleanup'].get('job_active_zero_observed')is True
  and report['cleanup'].get('cleanup_errors')==[], 'TERMINAL','complete contained command observed empty')

def check_manifest(path,base,pin,deadline,audit_out,graph_sha):
 # Literal path adapted from independent R: only new checking-progress identity
 # is graph-only. Never overwrite R's old original-state/MATRIX globals.
 pin(path.relative_to(ROOT).as_posix());manifest=read_json(path);universe=K.labelled_universe(base);total=len(universe);completed=manifest['completed_proposals']
 need(manifest['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_MANIFEST_V1'and type(completed)is int and 0<=completed<=total
  and type(manifest['population'])is int and manifest['population']==total,'MANIFEST','exact labelled population')
 need(R.literal_equal(manifest['baseline'],dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=base['root'],root_residual=base['root_residual'],
  frozen_rows=base['frozen'],mutable_labels=base['mutable'])),'MANIFEST','complete exact new graph baseline')
 need(all(type(manifest[k])is int for k in['starting_proposal_id','proposals_evaluated_this_invocation'])and 0<=manifest['starting_proposal_id']<=completed
  and manifest['proposals_evaluated_this_invocation']==completed-manifest['starting_proposal_id'],'MANIFEST','literal invocation prefix counts')
 identity=manifest['identity'];need(R.literal_equal({k:identity[k]for k in['n','degree','root','total','frozen_rows','mutable_labels']},
  dict(n=base['n'],degree=base['degree'],root=base['root'],total=total,frozen_rows=base['frozen'],mutable_labels=base['mutable'])),'MANIFEST','exact raw domain')
 for name,wanted in identity['software'].items():pin(name,wanted)
 need(manifest['independent_approval']is False and manifest['target_resolution']is False,'MANIFEST','producer pending scope')
 expected=[];end=0;bar=tqdm(total=completed,desc='Independent selected-neighbor literal rows',unit='record',mininterval=1)
 for part in manifest['parts']:
  need(deadline.status()['remaining_seconds']>20,'DEADLINE','checking serialization reserve');need(part['start']==end,'PART_SEQUENCE','gap-free manifest coverage')
  raw=R.read_part(part,pin)
  for record in raw:
   wanted=R.expected_record(base,record['proposal_id'],universe);R.check_record(record,wanted);expected.append(wanted);bar.update(1)
  end=part['end'];save(audit_out/('checked_prefix_'+str(end)+'.json'),dict(status='UNKNOWN_PREFIX_CHECKED_NO_COMPLETE_CENSUS_CLAIM',
   checked_proposal_records=end,raw_part_sha256=part['raw_sha256'],gzip_part_sha256=part['gzip_sha256'],input_graph_json_sha256=graph_sha,
   input_matrix_sha256=hashlib.sha256(K.matrix_bytes(base['bits'])).hexdigest(),graph_only_input=True,historical_native_state_written=False,deadline=deadline.status()))
 bar.close();need(end==completed and len(expected)==completed,'PART_SEQUENCE','complete raw prefix population');want=R.aggregate(expected)
 need(R.literal_equal(manifest['aggregate'],want),'AGGREGATE','all labels counts minima ties and literal graph identities')
 need(manifest['status']==('CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK'if completed==total else'UNKNOWN_PREFIX_ONLY'),'MANIFEST','complete versus prefix status')
 for descriptor in manifest['checkpoints']:
  pin(descriptor['path'],descriptor['sha256']);cp=read_json(ROOT/descriptor['path']);upto=cp['next_proposal_id']
  need(type(upto)is int and 0<=upto<=completed and cp['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_CHECKPOINT_V1'
   and R.literal_equal(cp['identity'],identity),'CHECKPOINT','exact source/input/prefix identity')
  matching=[part for part in manifest['parts']if part['end']<=upto]
  need(R.literal_equal(cp['parts'],matching)and(matching[-1]['end']if matching else 0)==upto
   and R.literal_equal(cp['aggregate'],R.aggregate(expected[:upto])),'CHECKPOINT','all complete prefix parts and aggregate coverage')
 directory=path.parent
 for filename,ids in[('best_root_ties.json',want['best_root_proposal_ids']),('minimum_mu_ties.json',want['minimum_mu_proposal_ids']),
  ('root_neutral_minimum_mu_ties.json',want['root_neutral_minimum_mu_proposal_ids'])]:
  member=(directory/filename).relative_to(ROOT).as_posix();pin(member);saved=read_json(ROOT/member)
  need(R.literal_equal(saved['records'],[expected[pid]for pid in ids]),'TIES','complete literal tie population')
 selected=min((expected[pid]for pid in want['best_root_proposal_ids']),key=lambda record:(record['new_mu'],record['proposal_id']),default=None)
 need(R.literal_equal(manifest['selected_proposal_id'],None if selected is None else selected['proposal_id']),'SELECTED','lex R mu ID selection')
 selected_scalar=None
 if selected is not None:
  candidate=K.evaluate(base,universe[selected['proposal_id']]);rows=K.reconstruct_triples(base,candidate);matrix=directory/'best_root_neighbor.adj';pin(matrix.relative_to(ROOT).as_posix())
  need(matrix.read_bytes()==K.matrix_bytes(candidate['candidate_bits']),'SELECTED','entire new selected raw adjacency')
  triple=directory/'best_root_neighbor_triples.json';pin(triple.relative_to(ROOT).as_posix());saved=read_json(triple)
  need(R.literal_equal(saved,dict(n=base['n'],degree=base['degree'],root=base['root'],frozen_rows=base['frozen'],mutable_labels=base['mutable'],triples=rows,
   proposal_id=selected['proposal_id'])),'SELECTED','entire ordered selected triples and original frozen rows')
  selected_scalar=S.scalar_matrix(matrix.read_bytes(),base['n'],base['degree'],base['root'])
  need((selected_scalar['lambda_energy'],selected_scalar['mu_energy'],selected_scalar['root_residual'])
   ==(selected['new_lambda'],selected['new_mu'],selected['new_root_residual']),'SELECTED','separate full scalar selected components')
 return dict(completed=completed,population=total,aggregate=want,selected_proposal_id=manifest['selected_proposal_id'],selected_scalar=selected_scalar),expected

def caller_path_calibration(out,record_out,pin,deadline):
 rows=[[3*r+c for c in range(3)]for r in range(3)]+[[3*r+c for r in range(3)]for c in range(3)];base=K.from_triples(rows,9,2,0)
 positive_out=out/'caller_positive';positive_out.mkdir();audit,records=check_manifest(record_out/'synthetic_manifest'/'manifest.json',base,pin,deadline,positive_out,'0'*64)
 need(audit['completed']==54 and audit['selected_scalar']['srg_valid']is True,'CALLER_CALIBRATION','independent complete rook synthetic stream and selected matrix')
 rejected=[]
 for name,stage in[('float_population','MANIFEST'),('bool_baseline_root','MANIFEST'),('dropped_part','PART_SEQUENCE'),('wrong_aggregate','AGGREGATE'),
  ('float_selected_id','SELECTED'),('checkpoint_aggregate','CHECKPOINT'),('missing_tie','TIES'),('selected_matrix','SELECTED')]:
  checked_out=out/('caller_'+name);checked_out.mkdir()
  reject(rejected,name,stage,lambda name=name,checked_out=checked_out:check_manifest(record_out/name/'manifest.json',base,pin,deadline,checked_out,'0'*64))
 save(out/'caller_path_controls.json',dict(positive_audit=audit,precise_negatives=rejected,input_history_scope='Synthetic graph-only path, no native history or actual selected99input'))
 return dict(positive_complete_caller_streams=1,positive_caller_records=54,precise_caller_path_negatives=8)

def controls(out,pin,deadline,args):
 summary=read_json(ROOT/args.producer_summary);ended=read_json(ROOT/args.supervisor);terminal(ended)
 need(summary['status']=='AUTHOR_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE'and summary['producer']=='/root/native_driver'
  and summary['independent_approval']is False and summary['actual_selected_graph_read']is False and summary['scientific_census_launched']is False
  and summary['historical_native_state_written']is False,'AUTHOR','new wrapper finite-only scope')
 need(R.literal_equal([summary[k]for k in['unique_complete_proposal_records_checked','recorded_proposal_evaluation_calls','additional_known_overlap_evaluation_calls',
  'kernel_negative_controls','whole_split_equal','graph_reader_positive_fixtures','graph_reader_specific_negatives','source_review_specific_negatives','input_gate_synthetic_positive','input_gate_specific_negative_count']],
  [243,486,1,41,True,['rook9','prism9','cube12'],24,14,1,32]),'AUTHOR','exact integrated finite population')
 folder=(ROOT/args.producer_summary).parent;kernel=summary['unchanged_kernel_report'];pin(kernel['path'],kernel['sha256'])
 kernel_out=out/'actual_kernel';kernel_out.mkdir();kernel_audit=R.controls(kernel_out,pin,deadline,SimpleNamespace(producer_summary=kernel['path'],producer_summary_sha256=kernel['sha256'],
  supervisor=args.supervisor,supervisor_sha256=args.supervisor_sha256))
 reader_audit=reader_controls(folder/'graph_reader',pin);save(out/'actual_reader_audit.json',reader_audit)
 path=folder/'synthetic_input_gate.json';pin(path.relative_to(ROOT).as_posix());gate=read_json(path);graph_path='synthetic/graph_only_input.json';graph_sha='0'*64;review_input(gate,graph_path,graph_sha)
 negatives=[]
 for record in summary['input_gate_specific_negatives']:
  path=folder/(record['case']+'.json');pin(path.relative_to(ROOT).as_posix());bad=read_json(path)
  need(record['stage']=='INPUT_GATE'and record['outcome']=='REJECTED','AUTHOR','specific recorded interface rejection')
  reject(negatives,record['case'],'INPUT_GATE',lambda bad=bad:review_input(bad,graph_path,graph_sha))
 need(len(negatives)==32,'AUTHOR','complete saved new input-gate negatives');save(out/'actual_input_gate_negatives.json',negatives)
 for path in sorted(folder.rglob('*')):
  if path.is_file():pin(path.relative_to(ROOT).as_posix())
 return dict(kernel_audit=kernel_audit,actual_reader_graphs=3,actual_reader_negatives=24,actual_source_review_negatives=14,
  actual_input_gate_synthetic_positive=1,actual_input_gate_negatives=32,actual_selected99graph_read=False,scientific_census_checked=False,
  terminal_record=dict(path=args.supervisor,sha256=args.supervisor_sha256,elapsed_seconds=ended['elapsed_seconds'],reaped=True,job_empty=True))

def full(out,pin,closure,deadline,args):
 graph=ROOT/args.graph_input;gate=read_json(ROOT/args.input_gate);review_input(gate,args.graph_input,args.graph_input_sha256);closure(gate)
 raw=graph.read_bytes();obj,base,input_scalar=G.decode(raw,actual=True)
 need(base['frozen']==R.FROZEN and len(base['mutable'])==224 and len(K.labelled_universe(base))==224784,'INPUT','complete new graph-only universe')
 control=read_json(ROOT/args.controls_gate);review_controls(control);closure(control)
 ended=read_json(ROOT/args.supervisor);terminal(ended)
 path=ROOT/args.manifest;manifest=read_json(path);identity=manifest['identity'];R.full_checkpoint_population(manifest,path)
 need(identity.get('graph_only_input')is True and identity.get('historical_native_state_written')is False and identity.get('graph_input_schema')==G.SCHEMA
  and R.literal_equal(identity.get('frozen_rows'),R.FROZEN) and R.literal_equal(identity.get('mutable_labels'),base['mutable'])
  and (identity.get('n'),identity.get('degree'),identity.get('root'),identity.get('total'))==(99,7,11,224784),'INPUT','explicit graph-only invocation scope')
 need(R.literal_equal(identity.get('software'),SOFTWARE),'INPUT','literal ten-source wrapper runtime closure')
 need(identity['inputs_sha256'].get(args.graph_input)==args.graph_input_sha256 and identity['inputs_sha256'].get(args.input_gate)==args.input_gate_sha256
  and identity['inputs_sha256'].get(args.controls_gate)==args.controls_gate_sha256,'INPUT','actual graph and new separate gate identities');closure(identity)
 audit,records=check_manifest(path,base,pin,deadline,audit_out=out,graph_sha=args.graph_input_sha256)
 need(audit['completed']==audit['population']==224784,'COVERAGE','all labelled one-move proposals independently checked')
 universe=K.labelled_universe(base);matrices=[];zeros=[]
 for pid in tqdm(audit['aggregate']['best_root_proposal_ids'],desc='Exact neighbor all minimum-R scalar matrices',unit='matrix',mininterval=1):
  need(deadline.status()['remaining_seconds']>20,'DEADLINE','retained tie matrix preservation reserve')
  candidate=K.evaluate(base,universe[pid]);raw=K.matrix_bytes(candidate['candidate_bits']);scalar=S.scalar_matrix(raw,99,7,11);record=records[pid]
  need((scalar['lambda_energy'],scalar['mu_energy'],scalar['root_residual'])==(record['new_lambda'],record['new_mu'],record['new_root_residual']),
   'TIES','complete separate scalar integer component check')
  matrices.append(dict(proposal_id=pid,matrix_sha256=hashlib.sha256(raw).hexdigest(),scalar=scalar))
  if scalar['srg_valid']:
   member='target_candidate_'+str(pid)+'.adj';(out/member).write_bytes(raw);save(out/('target_candidate_'+str(pid)+'_triples.json'),K.reconstruct_triples(base,candidate))
   zeros.append(dict(proposal_id=pid,path=(out/member).relative_to(ROOT).as_posix(),sha256=sha(out/member)));print('FULL99_TARGET_MATRIX_CANDIDATE_PENDING_ROOT_REVIEW '+str(pid),flush=True)
 receipt=path.parent/'run_receipt.json';pin(receipt.relative_to(ROOT).as_posix());reported=read_json(receipt)
 need(reported['manifest_sha256']==args.manifest_sha256 and reported['producer']=='/root/native_driver'and reported['independent_approval']is False
  and reported['target_resolution']=='NONE'and reported['historical_native_state_written']is False
  and reported['independently_approved_input_gate']==args.input_gate_sha256 and reported['new_wrapper_controls_gate']==args.controls_gate_sha256,
  'RECEIPT','exact new invocation pending receipt, no native history')
 save(out/'census_audit.json',audit);save(out/'minimum_root_tie_scalar_audits.json',matrices)
 return dict(complete_labelled_proposals=224784,scope_graph_input_path=args.graph_input,scope_graph_input_sha256=args.graph_input_sha256,
  scope_input_matrix_sha256=G.ACTUAL[G.MATRIX],graph_only_input=True,historical_native_state_written=False,input_scalar=input_scalar,
  frozen_original_literal_rows=R.FROZEN,mutable_label_count=224,aggregate=audit['aggregate'],selected_proposal_id=audit['selected_proposal_id'],
  minimum_root_tie_scalar_matrices=len(matrices),target_candidate_objects=zeros,literal_one_move_population_only=True,
  source_commit_context=identity['source_reference_commit'],census_audit_sha256=sha(out/'census_audit.json'),minimum_root_tie_scalar_audits_sha256=sha(out/'minimum_root_tie_scalar_audits.json'),
  terminal_record=dict(path=args.supervisor,sha256=args.supervisor_sha256,elapsed_seconds=ended['elapsed_seconds'],reaped=True,job_empty=True))

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','controls','full']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True)
 for field in['calibration','producer_summary','supervisor','manifest','controls_gate','graph_input','input_gate']:
  p.add_argument('--'+field.replace('_','-'));p.add_argument('--'+field.replace('_','-')+'-sha256')
 a=p.parse_args();deadline=CommandDeadline(a.seconds,allocation_reason='Independent new graph-only wrapper typed gates and complete raw parts/checkpoints; no producer imports/native/census calls;20s preservation reserve')
 out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT),'PATH','workspace output');out.mkdir(parents=True,exist_ok=False);pins={};protected={name:sha(ROOT/name)for name in['CLAIMS.yaml','.git/index']}
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>20,'DEADLINE','invocation output reserve');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT)and path.is_file(),'PATH','workspace existing input')
  found=sha(path);need(wanted is None or found==wanted,'IDENTITY','exact immutable input '+name);need(name not in pins or pins[name]==found,'IDENTITY','stable repeated input');pins[name]=found
 def read(name,wanted=None):pin(name,wanted);return read_json(ROOT/name)
 def closure(report):
  for name,wanted in report['inputs_sha256'].items():need(name not in['CLAIMS.yaml','.git/index'],'INPUT_ROLE','historical protected state is not immutable software');pin(name,wanted)
 try:
  for name,wanted in {**PINS,**SOFTWARE}.items():pin(name,wanted)
  for name in[SOURCE,SPEC,'pyproject.toml','uv.lock']:pin(name)
  kernel=read(R.KERNEL_CAL,R.KERNEL_CAL_SHA);need(kernel['status']=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_KERNEL_V1_CALIBRATION_PASS','KERNEL','unchanged primitive calibration');closure(kernel)
  record_out=out/'own_records';record_out.mkdir();record_cal=R.calibration(record_out,pin,deadline);caller_cal=caller_path_calibration(out,record_out,pin,deadline)
  graph_out=out/'own_graphs';graph_out.mkdir();graph_cal=G.calibration(graph_out);gate_cal=gate_calibration(out)
  result=dict(status=CAL,record_calibration=record_cal,caller_path_calibration=caller_cal,graph_calibration=graph_cal,gate_calibration=gate_cal,producer_outputs_checked=False)
  if a.mode!='calibration':
   need(all([a.calibration,a.calibration_sha256,a.supervisor,a.supervisor_sha256]),'ACTUAL','explicit calibration and terminal identities')
   calibrated=read(a.calibration,a.calibration_sha256);need(calibrated['status']==CAL and calibrated['producer_outputs_checked']is False
    and calibrated['inputs_sha256'][SOURCE]==pins[SOURCE]and calibrated['inputs_sha256'][SPEC]==pins[SPEC],'CALIBRATION','applicable changed wrapper checker calibration');closure(calibrated)
   pin(a.supervisor,a.supervisor_sha256)
   if a.mode=='controls':
    need(a.producer_summary and a.producer_summary_sha256,'ACTUAL','explicit author integration summary');author=read(a.producer_summary,a.producer_summary_sha256);closure(author)
    result=dict(status=CONTROLS,**controls(out,pin,deadline,a),producer_outputs_checked=True)
   else:
    for field in['manifest','controls_gate','graph_input','input_gate']:
     name=getattr(a,field);identity=getattr(a,field+'_sha256');need(name and identity,'ACTUAL','explicit '+field+' identity');pin(name,identity)
    result=dict(status=PASS,**full(out,pin,closure,deadline,a),producer_outputs_checked=True)
  need(all(sha(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED','ledger/index unchanged')
  limits={'calibration':['Own synthetic parts/records/45-checkpoint metadata, three tiny graphs and two gate positives only; no new producer outputs or actual selected input inspected.'],
   'controls':['Complete243tiny distinct labels and597whole/prefix/resume record observations, new graph-reader3/24/14 and32saved gate corruptions only; actual224784census requires a separate complete audit.'],
   'full':['Complete224784labelled one-move neighborhood of one selected121302 graph, all45fixed generated prefixes and all minimum-R tie scalar matrices; no complete trajectory, whole plateau, global-minimum or unrestricted exclusion.']}[a.mode]
  save(out/'summary.json',dict(**result,checker_implementation_version=1,timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',
   inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),deadline=deadline.status(),target_resolution='NONE',native_calls=0,census_calls=0,ledger_mutations=0,index_mutations=0,
   historical_protected_execution_state=dict(observations_sha256=protected,role='Historical before/after observations; not immutable dependencies'),
   shared_components=['Independent prior K integer bitmask/CN swap scorer, S adjacency/scalar checker, R literal21field/part/prefix/tie path and G typed graph-only decoder are reused as disclosed unchanged checking primitives.',
    'New caller independently defines wrapper/input/software gate semantics, new graph-only input closure and actual pending receipt; no producer import, old main or mutable global override.',
    'Python/JSON/gzip/SHA256/tqdm and locked deadline/containment runtime are trusted; old gates alone do not approve this changed caller.'],
   limitations=limits+['Literal graph counts are net labelled adjacency toggles, not isomorphism classes or unrestricted coverage; no automorphism or support uniqueness assumption.',
    'Actual full99 exact identity zero is exported immediately for separate ROOT target review regardless conservative NONE field; no manufactured native state/RNG/counters/history.']))
  print(result['status'])
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),outputs_preserved=True,native_calls=0,census_calls=0));raise
if __name__=='__main__':main()
