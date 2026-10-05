"""V16 author helper/AST controls only; no registrar main or mathematical replay."""
import argparse, ast, copy, hashlib, importlib.util, json, platform, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v15.py'
NEW = 'acceleration/register_20261003_bound_claims_v16.py'
SPEC = 'acceleration/calibrate_20261003_registrar_v16_helpers_v1_spec.md'
PINS = {
 OLD:'0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9',
 NEW:'a8e7c2694817970df28ff1ec7be3d8265ba2f6e3ffe3d88798241832426c2026',
 'acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json':
 '6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee',
 'acceleration/results/20261003_triangle_rank87_binding01/claim_binding_schema2.json':
 'dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d'}
BEFORE = 'a4f2f5b2ff41ea7aebf99413cdc825fc1e08f5269079d43e305da713f4af29ef'
INDEX = '8bcd46056145e09d225a01e553151abd1958364077a85b5c6d1bc33fe4f4cacd'
C4 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
RANK = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87'

class ControlError(ValueError):pass
def need(ok,message):
 if not ok:raise ControlError(message)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def dump(node):return ast.dump(node,include_attributes=False)
def change(value,path,replacement):
 result=copy.deepcopy(value);node=result
 for key in path[:-1]:node=node[key]
 node[path[-1]]=replacement;return result
def load(path):
 spec=importlib.util.spec_from_file_location('v16_author_subject',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def restore_ast(old_source,new_source):
 old=ast.parse(old_source);new=ast.parse(new_source);removed=[];body=[]
 for node in new.body:
  if isinstance(node,ast.FunctionDef) and node.name in {'v16_role','v16_dependency_order','v16_report'}:removed.append(node.name)
  elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='V16_EXACT':
   need(isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='json.loads' and len(node.value.args)==1 and type(node.value.args[0].value)is str,'exact literal config assignment');removed.append('V16_EXACT')
  else:body.append(node)
 need(sorted(removed)==['V16_EXACT','v16_dependency_order','v16_report','v16_role'],'four exact new top-level nodes');new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 diagnostic='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==diagnostic)
 extended=copy.deepcopy(guard);extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v16',ctx=ast.Load()))
 dispatcher=ast.parse("if wave41_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v16 disjoint exact metadata adapter')\n editorial_statement_mapping = wave41_statement_mapping").body[0]
 edits=[]
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   if any(isinstance(t,ast.Name) and t.id=='exact_v16' for t in node.targets):
    need(ast.unparse(node)=='exact_v16 = v16_role(cid, expected, binding)','exact role call');edits.append('role_call');return None
   if any(isinstance(t,ast.Name) and t.id=='wave41_statement_mapping' for t in node.targets):
    need(ast.unparse(node)=='wave41_statement_mapping = v16_report(cid, report_sha, binding, report)','exact report call');edits.append('report_call');return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='wave41_statement_mapping is not None':
    need(dump(node)==dump(dispatcher),'exact disjoint metadata dispatcher');edits.append('dispatcher');return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='v16_dependency_order':
    need(ast.unparse(node)=="v16_dependency_order(cid, {c['id'] for c in data['claims']})",'exact dependency order call');edits.append('dependency_order');return None
   if isinstance(node.value,ast.Call) and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value==diagnostic:
    need(dump(node)==dump(extended),'exact one new ROOT-role alternative');edits.append('role_alternative');return copy.deepcopy(guard)
   return self.generic_visit(node)
 Restore().visit(newmain)
 need(sorted(edits)==['dependency_order','dispatcher','report_call','role_alternative','role_call'],'five exact main insertions')
 need(dump(old)==dump(new),'complete V15 AST restored')
 return dict(removed_top_level_nodes=removed,removed_main_insertions=edits,complete_V15_AST_restored=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 deadline=CommandDeadline(args.seconds,allocation_reason='V16 source/AST and author helper-only exact metadata controls; prior V15 engineering34.453s,150worker/20save reserve; no main, mathematics or scientific computation')
 out=args.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False)
 before=(ROOT/'CLAIMS.yaml').read_bytes();index_before=sha(ROOT/'.git/index');pins={};positive=[];negative=[];mappings=[]
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>20,'not completed within the allocated budget: input checks/save reserve')
  path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'bounded input '+name);identity=sha(path)
  need(wanted is None or identity==wanted,'immutable input '+name);need(name not in pins or pins[name]==identity,'stable input '+name);pins[name]=identity;return identity
 def reject(label,diagnostic,callback):
  try:callback()
  except Exception as error:
   if type(error)is not ValueError or str(error)!=diagnostic:raise ControlError('WRONG_STAGE:'+label+':'+repr(error))
   negative.append(dict(label=label,expected_diagnostic=diagnostic,actual_diagnostic=str(error),outcome='REJECTED'));return
  raise ControlError('CORRUPTION_ACCEPTED:'+label)
 try:
  need(hashlib.sha256(before).hexdigest()==BEFORE and index_before==INDEX,'exact observed356 ledger/index baseline')
  for name in [Path(__file__).relative_to(ROOT).as_posix(),SPEC,'acceleration/register_20261003_bound_claims_v16_spec.md','acceleration/prepare_20261003_registrar_v16_source_v1.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']:pin(name)
  for name,identity in PINS.items():pin(name,identity)
  eq=restore_ast((ROOT/OLD).read_text(encoding='utf8'),(ROOT/NEW).read_text(encoding='utf8'))
  subject=load(ROOT/NEW);need(list(subject.V16_EXACT)==[C4,RANK],'exact two-ID dependency-ordered config')
  for cid,config in subject.V16_EXACT.items():
   path=config['binding_path'];identity=PINS[path];binding=json.loads((ROOT/path).read_bytes());report=json.loads((ROOT/binding['report']).read_bytes())
   pin(binding['report'],binding['report_sha256'])
   for name,wanted in binding['inputs_sha256'].items():pin(name,wanted)
   need(subject.v16_role(cid,identity,binding)is True,'literal positive role '+cid);positive.append(dict(label=cid+':role',outcome='PASS'))
   mapping=subject.v16_report(cid,binding['report_sha256'],binding,report)
   need(mapping['raw_statement_changed']is False and mapping['original_report_statement']==binding['statement']
        and mapping['original_independent_report_method']=='independent_derivation_and_complete_artifact_checking'
        and mapping['schema_method']=='independent_derivation' and mapping['mathematical_replays']==0,'literal original headline/method preservation')
   mappings.append(mapping);positive.append(dict(label=cid+':report',outcome='PASS'))
   need(subject.v16_dependency_order(cid,{C4})is None,'literal dependency order positive');positive.append(dict(label=cid+':dependency_order',outcome='PASS'))
   role=lambda b:subject.v16_role(cid,identity,b)
   rep=lambda r:subject.v16_report(cid,binding['report_sha256'],binding,r)
   reject(cid+':wrong_binding_hash','v16 exact frozen binding identity',lambda:subject.v16_role(cid,'0'*64,binding))
   stage='v16 exact typed revision status roles method kind basis'
   for key,value in [('id','C-SYNTHETIC-UNRELATED'),('revision',2),('claim_revision',2),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('producer','/root'),('verifier','/root/checkpoint_audit'),('method','independent_artifact_check'),('kind','exclusion'),('basis',[])]:
    reject(cid+':binding_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   for key in ['revision','claim_revision']:
    for value in [True,1.0]:reject(cid+':typed_'+key+':'+type(value).__name__,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   stage='v16 exact scope assumptions dependencies and unresolved premise'
   for path,value in [(['scope','description'],'Unrestricted nonexistence'),(['scope','unrestricted_target'],False),(['scope','target_resolution'],'NEGATIVE'),(['assumptions'],[]),(['dependencies'],[]),(['dependencies',0,'revision'],True),(['dependencies',0,'relation'],'coverage'),(['dependencies',0,'reason'],'Broader unproved reuse'),(['target_resolution'],'POSITIVE'),(['premise_state'],'VERIFIED')]:
    reject(cid+':scope_'+'.'.join(map(str,path)),stage,lambda path=path,value=value:role(change(binding,path,value)))
   stage='v16 exact literal statement primary report and no legacy fallback'
   for key,value in [('statement',binding['statement']+' General nonexistence.'),('report','synthetic.json'),('report_sha256','0'*64),('verification_records',[])]:
    reject(cid+':primary_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   stage='v16 exact proof controls certificate and original method metadata'
   for key,value in [('controls',{}),('written_audit','synthetic.md'),('written_audit_sha256','0'*64),('exact_certificate',[]),('original_independent_report_method','independent_artifact_check'),('original_independent_report_statement_field','synthetic')]:
    reject(cid+':proof_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   for path,value in [(['controls','independent_preoutput','producer_outputs_checked'],True),(['controls','independent_actual','complete_coefficients' if cid==RANK else 'unordered_paths'],1287.0 if cid==RANK else 23.0)]:
    reject(cid+':typed_controls_'+'.'.join(path),stage,lambda path=path,value=value:role(change(binding,path,value)))
   stage='v16 complete literal binding metadata'
   for key,value in [('inputs_sha256',{}),('shared_components',[]),('limitations',['Stronger result.']),('created_at','2000-01-01T00:00:00+00:00')]:
    reject(cid+':complete_binding_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   reject(cid+':wrong_report_hash','v16 exact primary report identity',lambda:subject.v16_report(cid,'0'*64,binding,report))
   stage='v16 exact typed independent report identity and method'
   for key,value in [('status','UNKNOWN'),('producer','/root'),('verifier','/root/checkpoint_audit'),('method','independent_derivation'),('claim_revision',True),('checker_implementation_version',3.0),('target_resolution','NEGATIVE'),('producer_outputs_checked',False)]:
    reject(cid+':report_'+key,stage,lambda key=key,value=value:rep(change(report,[key],value)))
   field=config['statement_field'];stage='v16 exact existing raw headline field'
   reject(cid+':alter_headline',stage,lambda:rep(change(report,[field],report[field]+' Altered.')))
   missing=copy.deepcopy(report);del missing[field];reject(cid+':missing_headline',stage,lambda:rep(missing))
   if cid==C4:
    injected=copy.deepcopy(report);injected['statement']=binding['statement'];reject(cid+':invent_ordinary_headline',stage,lambda:rep(injected))
   stage='v16 exact checked results and nonresolution limitations'
   already={'status','producer','verifier','method','claim_revision','checker_implementation_version','target_resolution','producer_outputs_checked'}
   for key,value in config['report_fields'].items():
    if key in already:continue
    if type(value)is bool:bad=not value
    elif type(value)is int:bad=value+1
    elif type(value)is str:bad=value+' altered'
    elif type(value)is dict:bad={}
    else:bad=[]
    reject(cid+':result_'+key,stage,lambda key=key,bad=bad:rep(change(report,[key],bad)))
   integer_key='target_weight5_lower_count' if cid==C4 else 'conditional_incidence_rank_lower'
   for bad in [True,float(report[integer_key])]:reject(cid+':typed_result_'+type(bad).__name__,stage,lambda bad=bad:rep(change(report,[integer_key],bad)))
   for key,value in [('inputs_sha256',{}),('timestamp','2000-01-01T00:00:00+00:00')]:
    reject(cid+':complete_report_'+key,'v16 complete literal report metadata',lambda key=key,value=value:rep(change(report,[key],value)))
  need(subject.v16_role('C-SYNTHETIC-UNRELATED','0'*64,{})is False,'unrelated role preservation');positive.append(dict(label='unrelated_role_false',outcome='PASS'))
  need(subject.v16_report('C-SYNTHETIC-UNRELATED','0'*64,{}, {})is None,'unrelated report preservation');positive.append(dict(label='unrelated_report_none',outcome='PASS'))
  need(subject.v16_dependency_order('C-SYNTHETIC-UNRELATED',set())is None,'unrelated dependency preservation');positive.append(dict(label='unrelated_order_none',outcome='PASS'))
  reject('rank87_missing_or_reverse_C4','v16 C4 dependency must precede rank87',lambda:subject.v16_dependency_order(RANK,set()))
  try:reject('wrong_stage_harness','expected exact failure',lambda:(_ for _ in ()).throw(ValueError('wrong stage')))
  except ControlError as error:need(str(error).startswith('WRONG_STAGE:wrong_stage_harness:'),'precise wrong-stage harness veto')
  else:raise ControlError('wrong-stage exception was accepted')
  try:reject('wrong_type_harness','expected exact failure',lambda:(_ for _ in ()).throw(TypeError('expected exact failure')))
  except ControlError as error:need(str(error).startswith('WRONG_STAGE:wrong_type_harness:'),'precise wrong-type harness veto')
  else:raise ControlError('wrong-type exception was accepted')
  need(len(positive)==9,'predeclared nine positive helper routes')
  need(len(negative)==155,'predeclared155 exact negative helper routes')
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==index_before,'historical protected observations unchanged')
  save(out/'controls.json',dict(positive=positive,strict_negative=negative,harness_wrong_stage_and_type_rejected=2))
  save(out/'mappings.json',mappings)
  report=dict(status='V16_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW',
    timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/checkpoint_audit',verifier=None,
    verifier_null_reason='Author controls are not an independent gate; ROOT must separately commission engineering review.',
    independent_approval=False,registrar_main_called=False,positive_controls=len(positive),strict_negative_controls=len(negative),
    harness_negative_controls=2,exact_claim_ids=[C4,RANK],complete_AST_restoration=eq,
    original_headline_and_combined_method_mappings=mappings,mathematical_replays=0,scientific_invocations=0,
    ledger_mutations=0,index_mutations=0,target_resolution='NONE',new_exclusions=0,
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    source_commit_role='Context only; exact new working sources are separately pinned, not asserted in HEAD.',
    command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
    historical_protected_execution_state=dict(before={'CLAIMS.yaml':BEFORE,'.git/index':index_before},after={'CLAIMS.yaml':hashlib.sha256((ROOT/'CLAIMS.yaml').read_bytes()).hexdigest(),'.git/index':sha(ROOT/'.git/index')}),
    artifacts={path.relative_to(ROOT).as_posix():sha(path) for path in [out/'controls.json',out/'mappings.json']},
    shared_components=['Unchanged V15 typed-equality/need/digest helpers and standard Python AST/JSON/SHA are reused.','Exact immutable bindings/reports are metadata inputs; no discovery producer, solver or mathematical checker is imported.','Author tests helper source; separate independent protected356to358 main projection remains required.'],
    limitations=['Finite author bookkeeping controls only, not independent engineering or mathematical approval.','No registrar main, complete ledger projection, mathematical replay, native optimization or target coverage calculation.','Recorded universal proofs and exact certificates are metadata-authenticated; their mathematics is not rechecked here.'],deadline=deadline.status())
  save(out/'summary.json',report);print(json.dumps({key:report[key] for key in ['status','positive_controls','strict_negative_controls','registrar_main_called','independent_approval']}))
 except BaseException as error:
  save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),type=type(error).__name__,message=str(error),completed_positive=len(positive),completed_negative=len(negative),inputs_sha256=pins,deadline=deadline.status()))
  raise
 finally:
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==index_before,'protected ledger/index unchanged even on failure')

if __name__=='__main__':main()
