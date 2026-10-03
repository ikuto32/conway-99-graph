"""Independent V13 metadata engineering audit; protected sandbox, no mathematics."""
import argparse,ast,copy,hashlib,importlib.util,json,os,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v12.py'
NEW='acceleration/register_20261003_bound_claims_v13.py'
RANK='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85'
CENSUS='C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
LOW='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
PINS={OLD:'70d4082b2f73fd23e4d8fb295e36eeb0092976c01f78e99fcd342f3a96598044',NEW:'1cfac35e19e473822583adfec8be7dfbd2ec73f59d0508febec14d24aeceef1a',
'acceleration/register_20261003_bound_claims_v13_spec.md':'1313f03b28abcf4e7a8411a26387663ec9c11c8c52daf538e1c2acdddcbf620f',
'acceleration/calibrate_20261003_registrar_v13_helpers_v2.py':'0de0aaa5bde6fd4ab9b56ec5d3d27b42b73f88e829285bdfcd3f24ae18613ac1',
'acceleration/calibrate_20261003_registrar_v13_helpers_v2_spec.md':'65a058655d78c84db8abea275e4a8a4a4bf320bb42e18a506beee4220a6782c8',
'acceleration/results/20261003_registrar_v13_helpers02/summary.json':'6dd5e2036159763a9fb50c17b5334bd75bbf912f78439caab438d47931343f2b'}
BINDINGS=[('acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json','40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05'),
('acceleration/results/20261003_incidence_low_weight_bindings02/rank85_claim_binding_schema2_v2.json','2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189'),
('acceleration/results/20261003_fixed_two_line_census_binding03/claim_binding_schema2_draft.json','b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1')]
BEFORE='cc8184dbe3c0c1bc6d539e8925fc392b80a3a4344c29e051118af0157d948a2c'
class AuditError(ValueError):pass
class ProtectedLedgerWrite(RuntimeError):pass
def need(ok,msg):
 if not ok:raise AuditError(msg)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def equivalence(old_source,new_source):
 old,new=ast.parse(old_source),ast.parse(new_source);removed=[];body=[]
 for node in new.body:
  if isinstance(node,ast.FunctionDef)and node.name in ('v13_root_role','v13_root_report'):removed.append(node.name)
  else:body.append(node)
 need(sorted(removed)==['v13_root_report','v13_root_role'],'exactly two new function definitions');new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='main');newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name=='main');message='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)and n.value.args[1].value==message);extended=copy.deepcopy(guard);need(isinstance(extended.value.args[0],ast.BoolOp)and isinstance(extended.value.args[0].values[-1],ast.BoolOp),'old guard shape');extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v13',ctx=ast.Load()));changes=[]
 class Normalize(ast.NodeTransformer):
  def visit_Assign(self,n):
   if any(isinstance(t,ast.Name)and t.id=='exact_v13'for t in n.targets):need(ast.unparse(n.value)=='v13_root_role(cid, expected, binding)','exact role insertion');changes.append('role_assignment');return None
   return self.generic_visit(n)
  def visit_Expr(self,n):
   if isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name):
    if n.value.func.id=='v13_root_report':need(ast.unparse(n.value)=='v13_root_report(cid, report_sha, binding, report)','exact report insertion');changes.append('report_call');return None
    if n.value.func.id=='need'and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)and n.value.args[1].value==message:need(ast.dump(n,include_attributes=False)==ast.dump(extended,include_attributes=False),'only exact_v13 role alternative');changes.append('role_alternative');return copy.deepcopy(guard)
   return self.generic_visit(n)
 Normalize().visit(newmain);need(sorted(changes)==['report_call','role_alternative','role_assignment'],'exactly three main edits');need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'entire prior V12 executable AST unchanged');return dict(new_functions=removed,main_insertions=changes,restored_ast_identical=True)
def reject(records,label,diagnostic,call):
 try:call()
 except ValueError as error:need(type(error)is ValueError and str(error)==diagnostic,'precise rejection '+label+' got '+repr(error));records.append(dict(label=label,outcome='REJECTED',diagnostic=str(error)))
 else:raise AuditError('CORRUPTION_ACCEPTED:'+label)
def changed(obj,path,value):
 result=copy.deepcopy(obj);node=result
 for key in path[:-1]:node=node[key]
 node[path[-1]]=value;return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent V13 metadata AST/boundary/350to353 protected projections; previous analogous25.7s,150worker20reserve, no math/science/live writes');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];barriers=[];before=(ROOT/'CLAIMS.yaml').read_bytes();need(hashlib.sha256(before).hexdigest()==BEFORE,'exact current350 ledger');index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute()else ROOT/index;index_before=sha(index)
 def pin(name,identity=None):
  need(deadline.status()['remaining_seconds']>20,'not completed within allocation');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'bounded input '+name);actual=sha(path);need(identity is None or identity==actual,'exact input '+name);need(name not in pins or pins[name]==actual,'stable input '+name);pins[name]=actual;return actual
 try:
  for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_registrar_v13_engineering_v1_spec.md','acceleration/audit_20261003_registrar_v12_engineering_v1.py','acceleration/audit_20261003_registrar_v12_engineering_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','uv.lock','pyproject.toml']:pin(name)
  for name,identity in PINS.items():pin(name,identity)
  old_source=(ROOT/OLD).read_text(encoding='utf8');new_source=(ROOT/NEW).read_text(encoding='utf8');eq=equivalence(old_source,new_source);old=module('independent_v13_baseline',ROOT/OLD);new=module('independent_v13_subject',ROOT/NEW);bodies={n.name:n for n in ast.parse(new_source).body if isinstance(n,ast.FunctionDef)};role_dict=next(n for n in ast.walk(bodies['v13_root_role'])if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='exacts'for t in n.targets));need([k.value for k in role_dict.value.keys]==[RANK,CENSUS],'exact two local identity keys');loaded={}
  for path,identity in BINDINGS:
   pin(path,identity);binding=json.loads((ROOT/path).read_bytes());pin(binding['report'],binding['report_sha256']);report=json.loads((ROOT/binding['report']).read_bytes());loaded[binding['id']]=(path,identity,binding,report)
   for name,digest in binding['inputs_sha256'].items():pin(name,digest)
  need(set(loaded)=={LOW,RANK,CENSUS},'exact three requested revisions')
  for cid in (RANK,CENSUS):
   path,identity,b,r=loaded[cid];need(new.v13_root_role(cid,identity,b)is True,'positive exact role');new.v13_root_report(cid,b['report_sha256'],b,r);need(new.v13_root_role(cid+'-OTHER',identity,b)is False and old.v12_root_role(cid,identity,b)is False,'no general or baseline ROOT exception')
   reject(controls,cid+':binding_identity','v13 exact binding identity',lambda:new.v13_root_role(cid,'f'*64,b))
   for field,value in [('id',cid+'-OTHER'),('revision',2),('revision',True),('claim_revision',1.0),('status','UNKNOWN'),('review_state','QUARANTINED'),('producer','/root'),('producer','/root/unapproved'),('verifier',b['producer']),('method','independent_derivation'),('kind','encoding'),('basis',['CITED'])]:
    bad=changed(b,[field],value);reject(controls,cid+':role_'+field+'_'+repr(value),'v13 exact revision status method and separate roles',lambda bad=bad:new.v13_root_role(cid,identity,bad))
   for field,value in [('description',b['scope']['description']+' Other graphs.'),('unrestricted_target',not b['scope']['unrestricted_target']),('unrestricted_target',int(b['scope']['unrestricted_target'])),('target_resolution','NONEXISTENCE')]:
    bad=changed(b,['scope',field],value);reject(controls,cid+':scope_'+field+'_'+repr(value),'v13 exact scope',lambda bad=bad:new.v13_root_role(cid,identity,bad))
   for field,value,diagnostic in [('statement',b['statement']+' ','v13 exact statement'),('report','acceleration/other.json','v13 exact report reference'),('report_sha256','f'*64,'v13 exact report reference'),('dependencies',[dict(id='UNESTABLISHED',revision=1,relation='premise')],'v13 exact dependencies'),('verification_records',[],'v13 legacy record namespace absent')]:
    bad=changed(b,[field],value);reject(controls,cid+':'+field,diagnostic,lambda bad=bad:new.v13_root_role(cid,identity,bad))
   reject(controls,cid+':report_identity','v13 exact independent report',lambda:new.v13_root_report(cid,'f'*64,b,r))
   for field,value in [('producer','/root/unapproved'),('verifier',b['producer']),('method','repeated_execution'),('target_resolution',False)]:
    bad=changed(r,[field],value);reject(controls,cid+':report_'+field,'v13 report roles and target scope',lambda bad=bad:new.v13_root_report(cid,b['report_sha256'],b,bad))
  rank=loaded[RANK];census=loaded[CENSUS]
  for field,value in [('status','NOT_VERIFIED'),('complete_exact_coefficients_checked',1288),('complete_nonnegative_dual_coordinates_checked',98),('complete_exact_weight_inequalities_checked',12),('actual_strict_corruption_controls',6),('exact_size_upper',[216950223385397837449,11529151026462413]),('maximum_linear_dimension',15),('conditional_incidence_rank_lower',84),('lower_word_counts',{'3':231,'4':2078,'6':24486}),('optimum_asserted',True)]:
   bad=changed(rank[3],[field],value);reject(controls,'rank85_report_'+field,'v13 exact conditional rank85 scope',lambda bad=bad:new.v13_root_report(RANK,rank[2]['report_sha256'],rank[2],bad))
  for fields,value,stage in [(['premise_state'],'VERIFIED','v13 exact conditional rank85 scope'),(['rank_upper_assumed'],True,'v13 exact conditional rank85 scope'),(['target_resolution'],'NONEXISTENCE','v13 exact conditional rank85 scope'),(['written_audit'],'acceleration/other.md','v13 exact written audit'),(['pre_output_calibration_sha256'],'f'*64,'v13 exact rank85 calibration reference'),(['inputs_sha256','acceleration/audit_20261003_triangle_kernel_low_weight_lp_v1.md'],'f'*64,'v13 exact rank85 source proof calibration pins'),(['recorded_validation','nonnegative_rational_coordinates'],98,'v13 exact rank85 recorded controls'),(['recorded_validation','numerical_status_used_as_certificate'],True,'v13 exact rank85 recorded controls'),(['recorded_validation','preoutput_synthetic_precise_corruptions'],6,'v13 exact rank85 recorded controls')]:
   bad=changed(rank[2],fields,value);reject(controls,'rank85_binding_'+str(fields),stage,lambda bad=bad:new.v13_root_report(RANK,bad['report_sha256'],bad,rank[3]))
  for fields,value in [(['complete_proposals_checked'],239084),(['frozen_labelled_proposals'],239085.0),(['complete_universe'],False),(['absence_of_descent_asserted'],False),(['aggregate','counts','invalid_selection'],10396),(['aggregate','counts','valid_lambda_preserving_mu_equal'],1),(['aggregate','unique_valid_neighbor_graphs'],239085),(['aggregate','best_mu'],3478),(['aggregate','best_proposal_ids'],[68908]),(['independently_checked_chosen_neighbor','proposal_id'],68912),(['independently_checked_chosen_neighbor','ordered_srg_identity_mismatches'],0)]:
   bad=changed(census[3],fields,value);reject(controls,'census_report_'+str(fields),'v13 exact fixed census outcome',lambda bad=bad:new.v13_root_report(CENSUS,census[2]['report_sha256'],census[2],bad))
  for fields,value,stage in [(['target_resolution'],True,'v13 exact fixed census outcome'),(['inputs_sha256','acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj'],'f'*64,'v13 exact census source input calibration pins'),(['pre_output_calibration','complete_unique_records'],269,'v13 exact census finite calibration'),(['pre_output_calibration','known_overlap_checked'],False,'v13 exact census finite calibration'),(['controls','pre_output_independent','strict_corruption_count'],14,'v13 exact explicit census controls'),(['controls','full_independent','complete_trajectory_checked'],True,'v13 exact explicit census controls'),(['inputs_sha256','acceleration/results/20261003_fixed_two_line_census_binding02/claim_binding_schema2_draft.json'],'f'*64,'v13 exact preserved editorial records'),(['supplemental_verification_records',0,'claim_revision'],2,'v13 exact supplemental record preservation'),(['supplemental_verification_records',1,'independent_of_discovery_producer'],False,'v13 exact supplemental record preservation'),(['unavailable_information',0,'value'],'imagined commit','v13 explicit unavailable information'),(['unavailable_information',1,'reason'],'','v13 explicit unavailable information'),(['computational_evidence','labelled_triples'],230,'v13 exact finite census evidence'),(['computational_evidence','raw_gzip_parts'],47,'v13 exact finite census evidence')]:
   bad=changed(census[2],fields,value);reject(controls,'census_binding_'+str(fields),stage,lambda bad=bad:new.v13_root_report(CENSUS,bad['report_sha256'],bad,census[3]))
  # Prior exact permission predicates are genuinely called, while the AST check
  # proves all other old implementation paths remain unchanged.
  for path in ['acceleration/results/20261003_independent_review/incidence_griesmer01/claim_binding.json','acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json']:
   identity=pin(path);b=json.loads((ROOT/path).read_bytes());need(old.v12_root_role(b['id'],identity,b)is True and new.v12_root_role(b['id'],identity,b)is True,'preserved old exact roles')
  for label,modified,diagnostic in [('prior_target_guard',new_source.replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')"),'entire prior V12 executable AST unchanged'),('new_role_call',new_source.replace('exact_v13 = v13_root_role(cid, expected, binding)','exact_v13 = True'),'exact role insertion')]:
   try:equivalence(old_source,modified)
   except AuditError as error:need(str(error)==diagnostic,'precise AST corruption rejection');controls.append(dict(label=label,outcome='REJECTED',diagnostic=str(error)))
   else:raise AuditError('AST_CORRUPTION_ACCEPTED:'+label)
  def dry(subject,label,items):
   need(deadline.status()['remaining_seconds']>20,'not completed within allocation');dest=out/label;argv=sys.argv;replace=os.replace
   def guard(source,target):
    need(Path(target).resolve()==ROOT/'CLAIMS.yaml'and Path(source).resolve()==dest/'CLAIMS.pending.yaml'and(ROOT/'CLAIMS.yaml').read_bytes()==before,'protected exact final atomic replacement');barriers.append(dict(label=label,source=str(source),target=str(target),replacement_prevented=True));raise ProtectedLedgerWrite()
   try:
    os.replace=guard;sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',BEFORE]
    for path,identity in items:sys.argv+=['--binding',str(ROOT/path),'--binding-sha256',identity]
    try:subject.main()
    except ProtectedLedgerWrite:pass
    else:raise AuditError('NO_PROTECTED_FINAL_WRITE_BARRIER:'+label)
   finally:os.replace=replace;sys.argv=argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'protected live ledger unchanged');return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text(encoding='utf8'))
  old_projection=dry(old,'ordinary_lowword_v12',[BINDINGS[0]]);new_projection=dry(new,'ordinary_lowword_v13',[BINDINGS[0]])
  def timeless(value):
   value=copy.deepcopy(value);value.pop('updated_at');value['claims'][-1]['created_at']=value['claims'][-1]['updated_at']=None;return value
  need(timeless(old_projection)==timeless(new_projection),'ordinary independent lowword projection unchanged');after=dry(new,'three_exact_revisions_v13',BINDINGS);original=yaml.safe_load(before)
  need(len(original['claims'])==350 and len(after['claims'])==353 and after['claims'][:350]==original['claims']and after['artifacts'][:len(original['artifacts'])]==original['artifacts']and after['target']==original['target'],'protected exact350to353 prior preservation');appended=after['claims'][350:];need([(c['id'],c['revision'],c['statement'],c['status'],c['review_state'],c['scope'],c['kind'],c['basis'])for c in appended]==[(b['id'],1,b['statement'],'VERIFIED','CLEAR',b['scope'],b['kind'],b['basis'])for _,_,b,_ in (loaded[LOW],loaded[RANK],loaded[CENSUS])],'exact three recorded scope projections');need([c['id']for c in appended]==[LOW,RANK,CENSUS],'lowword premise precedes dependent rank');counts=Counter(c['status']for c in original['claims']);counts['VERIFIED']+=3;need(Counter(c['status']for c in after['claims'])==counts and all(c['review_state']=='CLEAR'for c in after['claims']),'exact protected status counts')
  for label,binding,diagnostic in [('wrong_exact_statement',changed(rank[2],['statement'],'General target nonexistence'),'v13 exact binding identity'),('unapproved_ROOT',changed(rank[2],['id'],'C-UNAPPROVED-GENERIC-ROOT'),'separate checking identity for the exact recorded discovery')]:
   path=out/(label+'.json');save(path,binding);argv=sys.argv
   try:sys.argv=[str(ROOT/NEW),'--out',str(out/(label+'_main')),'--previous-sha256',BEFORE,'--binding',str(path),'--binding-sha256',sha(path)];reject(controls,label+'_real_main',diagnostic,new.main)
   finally:sys.argv=argv
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(index)==index_before,'live350 ledger/index unchanged at completion');save(out/'controls.json',controls)
  report=dict(status='INDEPENDENT_REGISTRAR_V13_EXACT_ADAPTER_ENGINEERING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/structural',producer='/root/checkpoint_audit',method='independent_engineering_artifact_check',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,before_ledger_sha256=BEFORE,index_before_sha256=index_before,index_after_sha256=sha(index),source_equivalence=eq,positive_exact_adapters=2,ordinary_lowword_V12_V13_projection_equal=True,protected_transition=dict(claims_before=350,claims_after=353,new_exact_ids=[c['id']for c in appended],prior_claims_artifacts_target_unchanged=True,new_finite_exclusion_kind_claims=1,new_unrestricted_exclusion_claims=0,status_counts=dict(counts),review_state_counts={'CLEAR':353}),strict_negative_controls=len(controls),controls=controls,protected_write_barriers=barriers,ledger_mutated=False,index_mutated=False,mathematical_replays=0,scientific_launched=False,target_resolution='UNKNOWN',shared_components=['Prior independently authored V12 engineering source used as disclosed algorithm/template evidence; V13-specific controls and exact AST normalization newly authored.','Registrar modules imported as engineering subjects only; mathematical producer/checker computations not imported or reexecuted.','Existing registry YAML/schema/serialization and supported deadline helpers used in protected projections.'],limitations=['No actual registration, mathematics reapproval, PUBLIC promotion or target resolution.','Only exact two ROOT binding adapters added; unknown ROOT IDs still rejected.','One fixed labelled-move exclusion-kind claim is separate from zero unrestricted target exclusions.','Protected atomic replacement interception prevents live ledger write; pending YAML/control artifacts remain only below this audit output.'],elapsed_seconds=time.monotonic()-started,deadline=deadline.status());save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),strict_negative_controls=len(controls),elapsed_seconds=report['elapsed_seconds'])))
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,completed_controls=controls,ledger_unchanged=(ROOT/'CLAIMS.yaml').read_bytes()==before,index_unchanged=sha(index)==index_before,outputs_preserved=True,mathematical_replays=0,scientific_launched=False,deadline=deadline.status()));raise
if __name__=='__main__':main()
