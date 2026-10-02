"""Independent V11.2 exact-source/finite/protected engineering review, no math."""
import argparse,ast,copy,hashlib,importlib.util,json,os,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v10.py'
FAILED='acceleration/register_20261003_bound_claims_v11.py'
NEW='acceleration/register_20261003_bound_claims_v11_2.py'
PINS={OLD:'cf6a12cee68ff206f6493953cd6ab8a07c1c8d04dbe1ad91d944694acb6d348d',FAILED:'e853b9f882633c61f9a296f739c18edf7d7ab4fb63a8f01b0e007f09c6c5762a',NEW:'c8ae676ac9785b99f7be10dd8569088e0aa084ab4137a1bcdf37fa9c3098c67d','acceleration/register_20261003_bound_claims_v11_2_spec.md':'65d55b9e2098e7a5335edae3ad6180cb7a9ae8cf7b508d03ae937546acd6c36b'}
BINDINGS=[('acceleration/results/20261003_independent_review/root8_mod2_full01/claim_binding.json','49f8bf5af0f9c634ff751b41a572bc6219e91b07bb75126ad9575c03b5f76bc1'),('acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json','24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501')]
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
  if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='V11_ROOT_EXACT' for x in n.targets):removed.append('V11_ROOT_EXACT')
  elif isinstance(n,ast.FunctionDef) and n.name in ('v11_root_role','v11_root_calibration','v11_root_report'):removed.append(n.name)
  else:body.append(n)
 need(sorted(removed)==sorted(['V11_ROOT_EXACT','v11_root_role','v11_root_calibration','v11_root_report']),'only declared constant/three helpers added');new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main');newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main');message='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message);changes=[]
 extended=copy.deepcopy(guard);need(isinstance(extended.value.args[0],ast.BoolOp) and isinstance(extended.value.args[0].values[-1],ast.BoolOp),'old role guard shape');extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v11',ctx=ast.Load()))
 class Normalize(ast.NodeTransformer):
  def visit_Assign(self,n):
   if any(isinstance(t,ast.Name) and t.id=='exact_v11' for t in n.targets):need(ast.unparse(n.value)=='v11_root_role(cid, expected, binding)','exact role insertion');changes.append('role');return None
   return self.generic_visit(n)
  def visit_Expr(self,n):
   if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name):
    if n.value.func.id=='v11_root_report':need(ast.unparse(n.value)=='v11_root_report(cid, report_sha, binding, report)','exact report insertion');changes.append('report');return None
    if n.value.func.id=='need' and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message:need(ast.dump(n,include_attributes=False)==ast.dump(extended,include_attributes=False),'only exact_v11 role alternative added');changes.append('role_alternative');return copy.deepcopy(guard)
   return self.generic_visit(n)
 Normalize().visit(newmain);need(sorted(changes)==['report','role','role_alternative'],'exact three main changes');need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'all prior V10 executable AST preserved');return {'new_top_level':removed,'main_changes':changes,'normalized_ast_identical':True}
def reject(records,label,diagnostic,call):
 try:call()
 except ValueError as e:need(type(e) is ValueError and str(e)==diagnostic,'precise rejection '+label+' got '+repr(e));records.append({'label':label,'diagnostic':str(e),'outcome':'REJECTED'})
 else:raise AuditError('false control acceptance '+label)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();started=time.monotonic();d=CommandDeadline(a.seconds,allocation_reason='New independent V11.2 source/finite/protected343to345 bookkeeping controls;180outer150worker20reserve no math/index')
 out=a.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];barriers=[];before=(ROOT/'CLAIMS.yaml').read_bytes();beforeh=hashlib.sha256(before).hexdigest();need(len(yaml.safe_load(before)['claims'])==343,'exact stable343 control baseline')
 index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute() else ROOT/index;indexh=sha(index)
 def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within the allocated budget')
 def pin(p,h=None):tick();v=sha(ROOT/p);need(h is None or v==h,'exact input '+p);pins[p]=v
 try:
  for p,h in PINS.items():pin(p,h)
  for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_registrar_v11_engineering_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']:pin(p)
  eq=equivalence((ROOT/OLD).read_text(),(ROOT/NEW).read_text());failedtext=(ROOT/FAILED).read_text();newtext=(ROOT/NEW).read_text();fragment="and report['target_resolution']=='NONE' and binding['target_resolution'] is False";need(newtext.count(fragment)==1,'unique reset typed predicate correction');normalized=newtext.replace(fragment,"and report['target_resolution'] is False and binding['target_resolution'] is False");need(ast.dump(ast.parse(normalized),include_attributes=False)==ast.dump(ast.parse(failedtext),include_attributes=False),'failedV11 corrected only exact typed predicate')
  old,new=module('subject_v10',ROOT/OLD),module('subject_v11_2',ROOT/NEW);loaded=[]
  for p,h in BINDINGS:
   pin(p,h);b=json.loads((ROOT/p).read_bytes());pin(b['report'],b['report_sha256']);r=json.loads((ROOT/b['report']).read_bytes());c=b['pre_output_calibration'];cp=c if isinstance(c,str) else c['path'];ch=b['pre_output_calibration_sha256'] if isinstance(c,str) else c['sha256'];pin(cp,ch);cal=json.loads((ROOT/cp).read_bytes());loaded.append((p,h,b,r,cal))
  need(set(new.V11_ROOT_EXACT)=={q[2]['id'] for q in loaded},'exact two-only whitelist')
  for p,h,b,r,cal in loaded:
   cid=b['id'];exact=new.V11_ROOT_EXACT[cid];need((exact['binding'],exact['report'],exact['report_path'],exact['producer'])==(h,b['report_sha256'],b['report'],b['producer']),'independently assembled exact two identities');need(new.v11_root_role(cid,h,b) is True,'positive exact role');new.v11_root_report(cid,b['report_sha256'],b,r);new.v11_root_calibration(cid,b,r,cal)
   reject(controls,cid+':bindinghash','v11 exact binding identity',lambda:new.v11_root_role(cid,'0'*64,b))
   for field,value in [('id',cid+'-ALIAS'),('revision',2),('claim_revision',2),('status','CANDIDATE'),('review_state','QUARANTINED'),('producer','/root'),('verifier',b['producer']),('method','repeated_execution'),('kind','mathematical result'),('basis',['DERIVED'])]:
    bad=copy.deepcopy(b);bad[field]=value;reject(controls,cid+':'+field,'v11 exact revision status method and separate roles',lambda:new.v11_root_role(cid,h,bad))
   for field,value in [('description','Broader target theorem'),('unrestricted_target',True),('target_resolution','NONEXISTENCE')]:
    bad=copy.deepcopy(b);bad['scope'][field]=value;reject(controls,cid+':scope_'+field,'v11 exact scope',lambda:new.v11_root_role(cid,h,bad))
   bad=copy.deepcopy(b);bad['report_sha256']='0'*64;reject(controls,cid+':reportref','v11 exact report reference',lambda:new.v11_root_role(cid,h,bad));need(new.v11_root_role(cid+'-ALIAS',h,b) is False,'aliases receive no adapter');reject(controls,cid+':reporthash','v11 exact independent report',lambda:new.v11_root_report(cid,'0'*64,b,r))
   bad=copy.deepcopy(r);bad['verifier']=b['producer'];reject(controls,cid+':report_roles','v11 report roles',lambda:new.v11_root_report(cid,b['report_sha256'],b,bad))
   if cid==loaded[0][2]['id']:
    for field,value in [('normalization_rows_checked',86433),('complete_scalar_primal_row_checks',345735),('complete_scalar_relation_column_checks',1),('compatible_profiles',650),('excluded_profiles',1),('rank_asserted',True),('target_resolution','NONEXISTENCE')]:
     bad=copy.deepcopy(r);bad[field]=value;reject(controls,cid+':report_'+field,'v11 root8 complete literal scope',lambda:new.v11_root_report(cid,b['report_sha256'],b,bad))
    bad=copy.deepcopy(b);bad['dependencies'][0]['relation']='premise';reject(controls,cid+':dependency','v11 root8 exact dependency',lambda:new.v11_root_report(cid,b['report_sha256'],bad,r));bad=copy.deepcopy(b);bad['recorded_validation']['binary_vectors']=3;reject(controls,cid+':validation','v11 root8 recorded validation',lambda:new.v11_root_report(cid,b['report_sha256'],bad,r))
    for field,value in [('positive_controls',4),('strict_negative_controls',14),('full_producer_output_inspected',True)]:
     bad=copy.deepcopy(cal);bad[field]=value;reject(controls,cid+':cal_'+field,'v11 root8 preoutput and full controls',lambda:new.v11_root_calibration(cid,b,r,bad))
   else:
    for field,value in [('complete_reset_scalar_entries',39203),('lambda_energy',1),('mu_energy',3607),('identity_mismatches',0),('target_resolution',False),('graphs_preserved',['current'])]:
     bad=copy.deepcopy(r);bad[field]=value;reject(controls,cid+':report_'+field,'v11 reset exact object scope',lambda:new.v11_root_report(cid,b['report_sha256'],b,bad))
    for field,value in [('seed',99032060),('step',1),('accepted',1),('mix_steps',1),('t_start',9.0)]:
     bad=copy.deepcopy(r);bad['parameters'][field]=value;reject(controls,cid+':params_'+field,'v11 reset exact parameters',lambda:new.v11_root_report(cid,b['report_sha256'],b,bad))
    bad=copy.deepcopy(r);key='acceleration/results/20261003_weight60_graph_reset01/reset.state';bad['inputs_sha256'][key]='0'*64;reject(controls,cid+':source_identity','v11 reset exact source object identities',lambda:new.v11_root_report(cid,b['report_sha256'],b,bad))
    bad=copy.deepcopy(cal);bad['controls']['producer_output_inspected']=True;reject(controls,cid+':cal_inspected','v11 reset preoutput controls',lambda:new.v11_root_calibration(cid,b,r,bad))
   bad=copy.deepcopy(cal);bad['verifier']=b['producer'];reject(controls,cid+':cal_verifier','v11 calibration verifier',lambda:new.v11_root_calibration(cid,b,r,bad))
  corrupt=newtext.replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')")
  try:equivalence((ROOT/OLD).read_text(),corrupt)
  except AuditError as e:need(str(e)=='all prior V10 executable AST preserved','exact AST control');controls.append({'label':'changed_prior_target_guard','diagnostic':str(e),'outcome':'REJECTED'})
  else:raise AuditError('source guard mutation accepted')
  def dry(subject,label,items):
   tick();dest=out/label;argv=sys.argv;replace=os.replace
   def guard(src,target):need(Path(target).resolve()==ROOT/'CLAIMS.yaml' and (ROOT/'CLAIMS.yaml').read_bytes()==before,'protected exact ledger barrier');barriers.append({'label':label,'pending':str(src),'target':str(target)});raise ProtectedLedgerWrite()
   try:
    os.replace=guard;sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',beforeh]
    for p,h in items:sys.argv+=['--binding',str(ROOT/p),'--binding-sha256',h]
    try:subject.main()
    except ProtectedLedgerWrite:pass
    else:raise AuditError('positive did not reach protected barrier')
   finally:os.replace=replace;sys.argv=argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no dryrun ledger mutation');return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text())
  # Exact prior ordinary method checked with a synthetic-ID clone, never published.
  ordinary=json.loads((ROOT/'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/claim_binding_schema2.json').read_bytes());ordinary['id']='C-ENGINEERING-ONLY-ORDINARY-V11-PROJECTION';op=out/'ordinary_synthetic_binding.json';save(op,ordinary);pair=(op.relative_to(ROOT).as_posix(),sha(op));v10=dry(old,'ordinary_v10',[pair]);v11=dry(new,'ordinary_v11',[pair])
  def strip(data):
   data=copy.deepcopy(data);data.pop('updated_at');data['claims'][-1]['created_at']=data['claims'][-1]['updated_at']=None;return data
  need(strip(v10)==strip(v11),'ordinary prior projection unchanged');after=dry(new,'two_actual_bindings_v11',BINDINGS);original=yaml.safe_load(before);need(len(after['claims'])==345 and after['claims'][:343]==original['claims'] and after['artifacts'][:len(original['artifacts'])]==original['artifacts'] and after['target']==original['target'],'protected343to345 prior records target unchanged');appended=after['claims'][343:];need([(c['id'],c['status'],c['scope']) for c in appended]==[(b['id'],b['status'],b['scope']) for p,h,b,r,c in loaded],'exact two scoped protected projections');need(Counter(c['status'] for c in after['claims'])=={'VERIFIED':337,'CANDIDATE':3,'REFUTED':5},'exact protected counts')
  bad=copy.deepcopy(loaded[0][2]);bad['statement']='Target general nonexistence';bp=out/'wrong_statement_binding.json';save(bp,bad);argv=sys.argv
  try:sys.argv=[str(ROOT/NEW),'--out',str(out/'wrong_statement_main'),'--previous-sha256',beforeh,'--binding',str(bp),'--binding-sha256',BINDINGS[0][1]];reject(controls,'wrong_statement_real_main','immutable binding',new.main)
  finally:sys.argv=argv
  failed=ROOT/'acceleration/results/20261003_registrar_v11_author_controls_supervision01';pin((failed/'summary.json').relative_to(ROOT).as_posix());r=json.loads((failed/'summary.json').read_bytes());need(r['command_exit_code']==1 and r['cleanup']['reaped'] and r['cleanup']['job_active_zero_observed'],'failed author control preserved terminal')
  for p in [failed/'manifest.json',failed/'stderr.log',ROOT/'acceleration/results/20261003_registrar_v11_author_controls02/summary.json']:pin(p.relative_to(ROOT).as_posix())
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(index)==indexh,'live ledger/index unchanged at completion')
  report={'status':'INDEPENDENT_REGISTRAR_V11_2_EXACT_ADAPTER_ENGINEERING_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root/native_driver','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_ledger_sha256':beforeh,'index_before_sha256':indexh,'index_after_sha256':sha(index),'source_equivalence':eq,'failedV11_single_typed_correction_verified':True,'positive_exact_adapters':2,'ordinary_V10_V11_projection_equal':True,'actual_protected_two_binding_projection':{'claims_before':343,'claims_after':345,'new_exact_ids':[q['id'] for q in appended],'prior_claims_artifacts_target_unchanged':True,'new_exclusions':0,'status_counts':dict(Counter(q['status'] for q in after['claims']))},'controls':controls,'protected_write_barriers':barriers,'ledger_mutated':False,'index_mutated':False,'mathematical_replays':0,'target_resolution':'UNKNOWN','shared_components':['Registrar modules imported as engineering subjects under independent AST/finite/protected-write controls; no discovery/proof checking source imported.','Existing schema validator/YAML/serialization and command deadline trusted for engineering only.'],'limitations':['No mathematical reapproval or actual ledger registration. Root must execute exact subject separately; later actual snapshot impact review required.','ROOT roles allowed only for two exact bindings/reports/calibrations; parity compatibility is not rank/integer/graph feasibility, reset is not a scientific result.','V11 failed typedFalse predicate and author receipts preserved; exact new reset stringNONE negative control independently tested.','Protected synthetic ordinary claim is a control artifact only and must never be copied into the live ledger.'],'elapsed_seconds':time.monotonic()-started,'deadline':d.status()};save(out/'summary.json',report);print(json.dumps({'status':report['status'],'sha256':sha(out/'summary.json'),'strict_controls':len(controls),'elapsed_seconds':report['elapsed_seconds']}))
 except BaseException as e:save(out/'failure.json',{'error':repr(e),'inputs_sha256':pins,'ledger_unchanged':(ROOT/'CLAIMS.yaml').read_bytes()==before,'index_unchanged':sha(index)==indexh,'outputs_preserved':True,'deadline':d.status()});raise
if __name__=='__main__':main()
