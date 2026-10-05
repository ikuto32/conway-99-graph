"""Independent V12 exact-source/finite/protected engineering review, no math."""
import argparse,ast,copy,hashlib,importlib.util,json,os,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v11_2.py'
NEW='acceleration/register_20261003_bound_claims_v12.py'
PINS={OLD:'c8ae676ac9785b99f7be10dd8569088e0aa084ab4137a1bcdf37fa9c3098c67d',
NEW:'70d4082b2f73fd23e4d8fb295e36eeb0092976c01f78e99fcd342f3a96598044',
'acceleration/register_20261003_bound_claims_v12_spec.md':'406080dd9ea11f7d8c34fa5aec13ded64db1b53946997947e2dcc16fae100e6e',
'acceleration/results/20261003_registrar_v12_author_controls01/summary.json':'8017fb558817f010d216ef8ca7b0ab9f78c048cd294151485af1ef3c4f24a95d'}
BINDINGS=[('acceleration/results/20261003_independent_review/incidence_griesmer01/claim_binding.json','4e018e2be2705f4684b31266797571d0eaab1eeb5ce15603d4765a77265e4848'),
('acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json','e49ba355e4ca8cf99e883d69594d6a972480b55aade5c6f60ecf9fe7d4566bff')]
BEFORE='879892c682f0a98e20373341621629407e5f5fba74b19be04db0776ca5e7c7a9'
class AuditError(ValueError):pass
class ProtectedLedgerWrite(RuntimeError):pass
def need(ok,msg):
 if not ok:raise AuditError(msg)
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,v):
 with p.open('x',encoding='utf8',newline='\n') as s:json.dump(v,s,indent=2);s.write('\n')
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def equivalence(old_source,new_source):
 old,new=ast.parse(old_source),ast.parse(new_source);removed=[];body=[]
 for n in new.body:
  if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='V12_ROOT_EXACT' for x in n.targets):removed.append('V12_ROOT_EXACT')
  elif isinstance(n,ast.FunctionDef) and n.name in ('v12_root_role','v12_root_controls','v12_root_report'):removed.append(n.name)
  else:body.append(n)
 need(sorted(removed)==sorted(['V12_ROOT_EXACT','v12_root_role','v12_root_controls','v12_root_report']),'only declared constant/three helpers added');new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main');newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main');message='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message);changes=[]
 extended=copy.deepcopy(guard);need(isinstance(extended.value.args[0],ast.BoolOp) and isinstance(extended.value.args[0].values[-1],ast.BoolOp),'old role guard shape');extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v12',ctx=ast.Load()))
 class Normalize(ast.NodeTransformer):
  def visit_Assign(self,n):
   if any(isinstance(t,ast.Name) and t.id=='exact_v12' for t in n.targets):need(ast.unparse(n.value)=='v12_root_role(cid, expected, binding)','exact role insertion');changes.append('role');return None
   return self.generic_visit(n)
  def visit_Expr(self,n):
   if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name):
    if n.value.func.id=='v12_root_report':need(ast.unparse(n.value)=='v12_root_report(cid, report_sha, binding, report)','exact report insertion');changes.append('report');return None
    if n.value.func.id=='need' and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message:need(ast.dump(n,include_attributes=False)==ast.dump(extended,include_attributes=False),'only exact_v12 role alternative added');changes.append('role_alternative');return copy.deepcopy(guard)
   return self.generic_visit(n)
 Normalize().visit(newmain);need(sorted(changes)==['report','role','role_alternative'],'exact three main changes');need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'all prior V11.2 executable AST preserved');return {'new_top_level':removed,'main_changes':changes,'normalized_ast_identical':True}
def reject(records,label,diagnostic,call):
 try:call()
 except ValueError as e:need(type(e) is ValueError and str(e)==diagnostic,'precise rejection '+label+' got '+repr(e));records.append({'label':label,'diagnostic':str(e),'outcome':'REJECTED'})
 else:raise AuditError('false control acceptance '+label)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();started=time.monotonic();d=CommandDeadline(a.seconds,allocation_reason='Fresh V12 two exact adapter source/finite/protected347to349 bookkeeping controls;180outer150worker20reserve no math/index')
 out=a.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];barriers=[];before=(ROOT/'CLAIMS.yaml').read_bytes();beforeh=hashlib.sha256(before).hexdigest();need(beforeh==BEFORE,'exact347 frozen ledger')
 index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute() else ROOT/index;indexh=sha(index)
 def tick():need(d.status()['remaining_seconds']>20,'not completed within allocated budget')
 def pin(p,h=None):
  tick();actual=sha(ROOT/p);need(h is None or actual==h,'input hash '+p);pins[p]=actual;return actual
 def path_mutation(obj,path,value):
  obj=copy.deepcopy(obj);at=obj
  for key in path[:-1]:at=at[key]
  at[path[-1]]=value;return obj
 try:
  for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_registrar_v12_engineering_v1_spec.md','acceleration/audit_20261003_registrar_v11_engineering_v1.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml','docs/claims.schema.json','acceleration/validate_claims.py']:pin(p)
  for p,h in PINS.items():pin(p,h)
  eq=equivalence((ROOT/OLD).read_text(),(ROOT/NEW).read_text());old=module('independent_v12_old',ROOT/OLD);new=module('independent_v12_subject',ROOT/NEW);need(len(new.V12_ROOT_EXACT)==2,'only exact two new identities');loaded=[]
  for p,h in BINDINGS:
   pin(p,h);b=json.loads((ROOT/p).read_bytes());pin(b['report'],b['report_sha256']);r=json.loads((ROOT/b['report']).read_bytes());exact=new.V12_ROOT_EXACT[b['id']];pin(exact['controls'],exact['controls_sha256']);cal=json.loads((ROOT/exact['controls']).read_bytes());loaded.append((p,h,b,r,cal))
   for name,digest in b['inputs_sha256'].items():pin(name,digest)
   cid=b['id'];need((exact['binding'],exact['report'],exact['report_path'],exact['producer'])==(h,b['report_sha256'],b['report'],b['producer']),'independently assembled exact identities');need(new.v12_root_role(cid,h,b) is True,'positive exact adapter');new.v12_root_report(cid,b['report_sha256'],b,r);new.v12_root_controls(cid,b,r,cal)
   need(new.v12_root_role(cid+'-ALIAS',h,b) is False and old.v11_root_role(cid,h,b) is False,'no generic prior/new ROOT permission')
   reject(controls,cid+':binding_hash','v12 exact binding identity',lambda:new.v12_root_role(cid,'0'*64,b))
   for field,value in [('id',cid+'-ALIAS'),('revision',2),('claim_revision',2),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('producer','/root'),('verifier',b['producer']),('method','repeated_execution'),('kind','exclusion'),('basis',['CITED'])]:
    bad=copy.deepcopy(b);bad[field]=value;reject(controls,cid+':'+field,'v12 exact revision status method and separate roles',lambda bad=bad:new.v12_root_role(cid,h,bad))
   for field,value in [('description','Broader target theorem'),('unrestricted_target',not b['scope']['unrestricted_target']),('target_resolution','NONEXISTENCE')]:
    bad=copy.deepcopy(b);bad['scope'][field]=value;reject(controls,cid+':scope_'+field,'v12 exact scope',lambda bad=bad:new.v12_root_role(cid,h,bad))
   for label,field,value,diagnostic in [('statement','statement','Target nonexistence','v12 exact statement'),('report_path','report','build/unknown.json','v12 exact report reference'),('report_hash','report_sha256','0'*64,'v12 exact report reference'),('dependencies','dependencies',[{'id':'UNPROVED','revision':1,'relation':'premise'}],'v12 exact dependencies')]:
    bad=copy.deepcopy(b);bad[field]=value;reject(controls,cid+':'+label,diagnostic,lambda bad=bad:new.v12_root_role(cid,h,bad))
   reject(controls,cid+':report_hash_arg','v12 exact independent report',lambda:new.v12_root_report(cid,'0'*64,b,r))
   for field,value in [('producer','/root'),('verifier',b['producer']),('method','repeated_execution')]:
    bad=copy.deepcopy(r);bad[field]=value;reject(controls,cid+':report_'+field,'v12 report roles and method',lambda bad=bad:new.v12_root_report(cid,b['report_sha256'],b,bad))
   if cid==loaded[0][2]['id']:
    for field,value in [('minimum_rank',68),('maximum_kernel_dimension',31),('nonzero_kernel_weights',[34]),('conditional_premise','Existence VERIFIED'),('target_resolution','NONEXISTENCE'),('graph_constructed',True),('target_nonexistence',True),('rank_upper72_status','VERIFIED')]:
     bad=copy.deepcopy(r);bad[field]=value;reject(controls,cid+':report_'+field,'v12 exact conditional Griesmer scope',lambda bad=bad:new.v12_root_report(cid,b['report_sha256'],b,bad))
    for field,value in [('premise_state','VERIFIED'),('rank_upper72_state','VERIFIED')]:
     bad=copy.deepcopy(b);bad[field]=value;reject(controls,cid+':binding_'+field,'v12 exact conditional Griesmer scope',lambda bad=bad:new.v12_root_report(cid,b['report_sha256'],bad,r))
    bad=copy.deepcopy(b);bad['inputs_sha256'][exact['proof']]='0'*64;reject(controls,cid+':proof_hash','v12 exact independently written proof',lambda:new.v12_root_report(cid,b['report_sha256'],bad,r))
    for field,value in [('complete_kernel_population',15),('nonzero_kernel_words_checked',14),('total_subspaces',3289),('minimum_word_residual_checks',5854),('general_code_without_incidence_not_given_distance36',False),('target_dimension33_sum',99)]:
     bad=copy.deepcopy(cal);bad[field]=value;reject(controls,cid+':cal_'+field,'v12 Griesmer complete finite controls',lambda bad=bad:new.v12_root_controls(cid,b,r,bad))
    bad=copy.deepcopy(b);bad['recorded_validation']['finite_controls_are_general_proof']=True;reject(controls,cid+':finite_not_universal','v12 Griesmer recorded controls',lambda:new.v12_root_controls(cid,bad,r,cal))
   else:
    for field,value in [('raw_graphs',3),('complete_roots',197),('literal_triangle_population',313697),('complete_scalar_matrix_entries',19601),('target_resolution','NONEXISTENCE')]:
     bad=copy.deepcopy(r);bad[field]=value;reject(controls,cid+':report_'+field,'v12 exact finite warm census population',lambda bad=bad:new.v12_root_report(cid,b['report_sha256'],b,bad))
    for path,value in [(['graph_records',0,'minimum_root_ties'],[11]),(['graph_records',1,'fully_cn2_roots'],1),(['graph_records',0,'global_mu_energy'],3481)]:
     bad=path_mutation(r,path,value);reject(controls,cid+':record_'+str(path),'v12 exact warm census graph records',lambda bad=bad:new.v12_root_report(cid,b['report_sha256'],b,bad))
    raw='acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj';bad=copy.deepcopy(r);bad['inputs_sha256'][raw]='0'*64;reject(controls,cid+':raw_graph_hash','v12 exact two warm raw graph identities',lambda:new.v12_root_report(cid,b['report_sha256'],b,bad))
    bad=copy.deepcopy(b);bad['pre_output_calibration']['negative_control_count']=4;reject(controls,cid+':cal_count','v12 warm census complete finite controls',lambda:new.v12_root_controls(cid,bad,r,cal))
   bad=copy.deepcopy(b);bad['inputs_sha256'][exact['controls']]='0'*64;reject(controls,cid+':cal_hash','v12 exact control bytes',lambda:new.v12_root_report(cid,b['report_sha256'],bad,r))
  # The unchanged older exact adapters must still accept their own frozen roles.
  for p in ['acceleration/results/20261003_independent_review/root8_mod2_full01/claim_binding.json','acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json']:
   pin(p);b=json.loads((ROOT/p).read_bytes());need(old.v11_root_role(b['id'],sha(ROOT/p),b)==new.v11_root_role(b['id'],sha(ROOT/p),b),'prior exact role unchanged')
  corrupt=(ROOT/NEW).read_text().replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')")
  try:equivalence((ROOT/OLD).read_text(),corrupt)
  except AuditError as e:need(str(e)=='all prior V11.2 executable AST preserved','precise prior AST guard rejection');controls.append({'label':'changed_prior_target_guard','diagnostic':str(e),'outcome':'REJECTED'})
  else:raise AuditError('source guard mutation accepted')
  def dry(subject,label,items):
   tick();dest=out/label;argv=sys.argv;replace=os.replace
   def guard(src,target):need(Path(target).resolve()==ROOT/'CLAIMS.yaml' and (ROOT/'CLAIMS.yaml').read_bytes()==before,'protected ledger barrier');barriers.append({'label':label,'pending':str(src),'target':str(target)});raise ProtectedLedgerWrite()
   try:
    os.replace=guard;sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',beforeh]
    for p,h in items:sys.argv+=['--binding',str(ROOT/p),'--binding-sha256',h]
    try:subject.main()
    except ProtectedLedgerWrite:pass
    else:raise AuditError('positive failed to reach protected barrier')
   finally:os.replace=replace;sys.argv=argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no protected ledger mutation');return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text())
  ordinary=json.loads((ROOT/'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/claim_binding_schema2.json').read_bytes());ordinary['id']='C-ENGINEERING-ONLY-ORDINARY-V12-PROJECTION';op=out/'ordinary_synthetic_binding.json';save(op,ordinary);pair=(op.relative_to(ROOT).as_posix(),sha(op));oldproj=dry(old,'ordinary_v11',[pair]);newproj=dry(new,'ordinary_v12',[pair])
  def strip(value):
   value=copy.deepcopy(value);value.pop('updated_at');value['claims'][-1]['created_at']=value['claims'][-1]['updated_at']=None;return value
  need(strip(oldproj)==strip(newproj),'ordinary baseline projection unchanged');after=dry(new,'two_actual_bindings_v12',BINDINGS);original=yaml.safe_load(before)
  need(len(original['claims'])==347 and len(after['claims'])==349 and after['claims'][:347]==original['claims'] and after['artifacts'][:len(original['artifacts'])]==original['artifacts'] and after['target']==original['target'],'protected347to349 exact prior preservation')
  appended=after['claims'][347:];need([(c['id'],c['statement'],c['status'],c['scope']) for c in appended]==[(b['id'],b['statement'],b['status'],b['scope']) for p,h,b,r,cal in loaded],'two exact protected scoped projections');counts=Counter(c['status'] for c in original['claims']);counts['VERIFIED']+=2;need(Counter(c['status'] for c in after['claims'])==counts,'protected exact counts')
  bad=copy.deepcopy(loaded[0][2]);bad['statement']='Target general nonexistence';bp=out/'wrong_statement_binding.json';save(bp,bad);argv=sys.argv
  try:sys.argv=[str(ROOT/NEW),'--out',str(out/'wrong_statement_main'),'--previous-sha256',beforeh,'--binding',str(bp),'--binding-sha256',sha(bp)];reject(controls,'wrong_statement_real_main_newhash','v12 exact binding identity',new.main)
  finally:sys.argv=argv
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(index)==indexh,'live ledger/index unchanged at completion')
  report={'status':'INDEPENDENT_REGISTRAR_V12_EXACT_ADAPTER_ENGINEERING_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root/structural','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_ledger_sha256':beforeh,'index_before_sha256':indexh,'index_after_sha256':sha(index),'source_equivalence':eq,'positive_exact_adapters':2,'ordinary_V11_V12_projection_equal':True,'actual_protected_two_binding_projection':{'claims_before':347,'claims_after':349,'new_exact_ids':[c['id'] for c in appended],'prior_claims_artifacts_target_unchanged':True,'new_exclusions':0,'status_counts':dict(counts)},'controls':controls,'protected_write_barriers':barriers,'ledger_mutated':False,'index_mutated':False,'mathematical_replays':0,'target_resolution':'UNKNOWN','shared_components':['Registrar modules imported only as engineering subjects under independent AST/finite/protected-write controls; discovery/proof computations not imported.','Existing schema validator/YAML/serialization and bounded command helpers trusted for engineering.'],'limitations':['No mathematical reapproval or actual ledger registration; root must separately execute exact subject and later actual impact checker.','ROOT role restricted to the two exact binding/report/control/proof hashes, including conditional rank67 and finite198root census.','Synthetic ordinary-ID control must never be registered as a mathematical claim.'],'elapsed_seconds':time.monotonic()-started,'deadline':d.status()};save(out/'summary.json',report);print(json.dumps({'status':report['status'],'sha256':sha(out/'summary.json'),'strict_controls':len(controls),'elapsed_seconds':report['elapsed_seconds']}))
 except BaseException as e:save(out/'failure.json',{'error':repr(e),'inputs_sha256':pins,'ledger_unchanged':(ROOT/'CLAIMS.yaml').read_bytes()==before,'index_unchanged':sha(index)==indexh,'outputs_preserved':True,'deadline':d.status()});raise

if __name__=='__main__':main()
