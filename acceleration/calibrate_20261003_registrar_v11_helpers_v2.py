"""Author-side finite V11 helper calibration; never calls registrar main."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v10.py'
OLD_SHA='cf6a12cee68ff206f6493953cd6ab8a07c1c8d04dbe1ad91d944694acb6d348d'
NEW='acceleration/register_20261003_bound_claims_v11_2.py'
BINDINGS=[
 ('acceleration/results/20261003_independent_review/root8_mod2_full01/claim_binding.json','49f8bf5af0f9c634ff751b41a572bc6219e91b07bb75126ad9575c03b5f76bc1'),
 ('acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json','24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501'),
]
LEGACY=[
 ('acceleration/results/20261003_independent_review/root7_mod2_full02/claim_binding.json','59be79ef4fed77ee65ce500dcbaf22eb1f4788dd53d187f97166e909d2b881e3'),
 ('acceleration/results/20261003_weight60_root_census_binding01/claim_binding_schema2_draft.json','b3fd150fe6a36c0bac66984c4940fe48957c64dd323fbeb15ba7c91069feb2fb'),
 ('acceleration/results/20261003_independent_review/rejected_incidence_rank01/claim_binding.json','518ac2e90784fe6d14d0ac5a933f77ca4fd4255ad1ab58b48262b5c6b4a64d4b'),
]


def need(ok,why):
 if not ok:raise ValueError(why)


def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def save(path,value):
 with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def ast_restoration(old_source,new_source):
 old,new=ast.parse(old_source),ast.parse(new_source);retained=[];removed=[]
 for node in new.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='V11_ROOT_EXACT' for t in node.targets):removed.append('V11_ROOT_EXACT');continue
  if isinstance(node,ast.FunctionDef) and node.name in ('v11_root_role','v11_root_report','v11_root_calibration'):removed.append(node.name);continue
  retained.append(node)
 need(sorted(removed)==['V11_ROOT_EXACT','v11_root_calibration','v11_root_report','v11_root_role'],'only declared new top-level adapters')
 new.body=retained;old_main=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main');new_main=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main');changes=[]
 old_check=next(n for n in ast.walk(old_main) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='need' and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value=='separate checking identity for the exact recorded discovery')
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   if any(isinstance(t,ast.Name) and t.id=='exact_v11' for t in node.targets):
    need(ast.unparse(node.value)=='v11_root_role(cid, expected, binding)','exact role call');changes.append('role');return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   call=node.value
   if isinstance(call,ast.Call) and isinstance(call.func,ast.Name):
    if call.func.id=='v11_root_report':
     need(ast.unparse(call)=='v11_root_report(cid, report_sha, binding, report)','exact report call');changes.append('report');return None
    if call.func.id=='need' and len(call.args)>1 and isinstance(call.args[1],ast.Constant) and call.args[1].value=='separate checking identity for the exact recorded discovery':
     need('exact_v11' in ast.unparse(node),'only declared role alternative');changes.append('role_alternative');return copy.deepcopy(old_check)
   return self.generic_visit(node)
 Restore().visit(new_main)
 need(sorted(changes)==['report','role','role_alternative'],'exact three main changes')
 need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'all prior executable AST preserved')
 return dict(new_top_level=removed,main_changes=changes,normalized_ast_identical=True)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--registrar-sha256',required=True);args=ap.parse_args()
 deadline=CommandDeadline(args.seconds,allocation_reason='Author-side registrarV11 finite helpers/sourceAST calibration, no ledger/index/main/science invocation')
 out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];before=(ROOT/'CLAIMS.yaml').read_bytes()
 def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated metadata budget')
 def pin(name,identity=None):
  tick();digest=sha(ROOT/name);need(identity is None or digest==identity,'exact input '+name);pins[name]=digest
  return json.loads((ROOT/name).read_bytes()) if name.endswith('.json') else None
 def reject(label,expected,call):
  try:call()
  except ValueError as error:
   need(type(error) is ValueError and str(error)==expected,'strict diagnostic '+label+' got '+repr(error));controls.append(dict(label=label,diagnostic=str(error)))
  else:raise ValueError('corruption accepted '+label)
 def changed(value,path,replacement):
  value=copy.deepcopy(value);target=value
  for key in path[:-1]:target=target[key]
  target[path[-1]]=replacement;return value
 pin(OLD,OLD_SHA);pin(NEW,args.registrar_sha256)
 for name in ['acceleration/register_20261003_bound_claims_v11_2_spec.md',Path(__file__).relative_to(ROOT).as_posix(),
              'acceleration/calibrate_20261003_registrar_v11_helpers_v2_spec.md','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py']:pin(name)
 pin('acceleration/register_20261003_bound_claims_v11.py','e853b9f882633c61f9a296f739c18edf7d7ab4fb63a8f01b0e007f09c6c5762a')
 pin('acceleration/calibrate_20261003_registrar_v11_helpers_v1.py','20eceaf1b4aed5beb8f3aad484b69e3d7a8ce996613a6a6861b41c267d38ba85')
 for name in ['acceleration/register_20261003_bound_claims_v11_spec.md','acceleration/calibrate_20261003_registrar_v11_helpers_v1_spec.md',
              'acceleration/results/20261003_registrar_v11_author_controls_supervision01/manifest.json',
              'acceleration/results/20261003_registrar_v11_author_controls_supervision01/summary.json',
              'acceleration/results/20261003_registrar_v11_author_controls_supervision01/stderr.log']:pin(name)
 restoration=ast_restoration((ROOT/OLD).read_text(),(ROOT/NEW).read_text());old=load_module('subject_v10',ROOT/OLD);new=load_module('subject_v11',ROOT/NEW)
 positives=[]
 for name,identity in BINDINGS:
  binding=pin(name,identity);cid=binding['id'];report=pin(binding['report'],binding['report_sha256']);exact=new.V11_ROOT_EXACT[cid]
  calibration=pin(exact['calibration'],exact['calibration_sha256'])
  need(new.v11_root_role(cid,identity,binding) is True,'exact positive role');new.v11_root_report(cid,binding['report_sha256'],binding,report)
  new.v11_root_calibration(cid,binding,report,calibration);positives.append(cid)
  reject(cid+':binding_identity','v11 exact binding identity',lambda:new.v11_root_role(cid,'0'*64,binding))
  for path,replacement in [(['revision'],2),(['claim_revision'],2),(['status'],'CANDIDATE'),(['review_state'],'NEEDS_RECHECK'),(['producer'],'/root'),(['verifier'],'/root/native_driver'),(['method'],'repeated_execution'),(['kind'],'mathematical result'),(['basis'],['DERIVED'])]:
   bad=changed(binding,path,replacement);reject(cid+':'+'.'.join(path),'v11 exact revision status method and separate roles',lambda bad=bad:new.v11_root_role(cid,identity,bad))
  for path,replacement in [(['scope','unrestricted_target'],True),(['scope','target_resolution'],'POSITIVE'),(['scope','description'],'broader graphs')]:
   bad=changed(binding,path,replacement);reject(cid+':'+'.'.join(path),'v11 exact scope',lambda bad=bad:new.v11_root_role(cid,identity,bad))
  bad=changed(binding,['report_sha256'],'0'*64);reject(cid+':report_reference','v11 exact report reference',lambda:new.v11_root_role(cid,identity,bad))
  reject(cid+':report_hash','v11 exact independent report',lambda:new.v11_root_report(cid,'0'*64,binding,report))
  bad=changed(report,['producer'],'/root');reject(cid+':report_roles','v11 report roles',lambda:new.v11_root_report(cid,binding['report_sha256'],binding,bad))
  if cid.startswith('C-UNRESTRICTED'):
   for key,val in [('normalization_rows_checked',86433),('complete_scalar_primal_row_checks',345735),('complete_scalar_relation_column_checks',1),('compatible_profiles',650),('excluded_profiles',1),('rank_asserted',True),('target_resolution','POSITIVE')]:
    bad=changed(report,[key],val);reject(cid+':'+key,'v11 root8 complete literal scope',lambda bad=bad:new.v11_root_report(cid,binding['report_sha256'],binding,bad))
   bad=changed(binding,['dependencies',0,'revision'],2);reject(cid+':dependency','v11 root8 exact dependency',lambda:new.v11_root_report(cid,binding['report_sha256'],bad,report))
   bad=changed(binding,['recorded_validation','coordinates_per_vector'],23333);reject(cid+':vector_width','v11 root8 recorded validation',lambda:new.v11_root_report(cid,binding['report_sha256'],bad,report))
   for path,val in [(['strict_negative_controls'],16),(['full_producer_output_inspected'],True),(['positive_controls'],4)]:
    bad=changed(calibration,path,val);reject(cid+':cal_'+path[0],'v11 root8 preoutput and full controls',lambda bad=bad:new.v11_root_calibration(cid,binding,report,bad))
  else:
   for key,val in [('complete_reset_scalar_entries',39203),('lambda_energy',1),('mu_energy',3607),('identity_mismatches',0),('target_resolution',True),('target_resolution',False)]:
    bad=changed(report,[key],val);reject(cid+':'+key,'v11 reset exact object scope',lambda bad=bad:new.v11_root_report(cid,binding['report_sha256'],binding,bad))
   bad=changed(binding,['dependencies'],[dict(id='UNPROVEN',revision=1,relation='premise')]);reject(cid+':dependency','v11 reset exact object scope',lambda:new.v11_root_report(cid,binding['report_sha256'],bad,report))
   for key,val in [('seed',99032060),('step',1),('admissible',1),('accepted',1),('best_updates',1),('t_start',60),('mix_steps',1)]:
    bad=changed(report,['parameters',key],val);reject(cid+':'+key,'v11 reset exact parameters',lambda bad=bad:new.v11_root_report(cid,binding['report_sha256'],binding,bad))
   bad=changed(report,['inputs_sha256','acceleration/results/20261003_weight60_graph_reset01/reset.state'],'0'*64);reject(cid+':reset_input','v11 reset exact source object identities',lambda:new.v11_root_report(cid,binding['report_sha256'],binding,bad))
   for path,val in [(['controls','strict_negative_controls'],14),(['controls','positive_controls'],1),(['controls','producer_output_inspected'],True)]:
    bad=changed(calibration,path,val);reject(cid+':cal_'+path[-1],'v11 reset preoutput controls',lambda bad=bad:new.v11_root_calibration(cid,binding,report,bad))
 need(new.v11_root_role('UNRELATED-ROOT-CLAIM','0'*64,{}) is False,'unknown ID not admitted')
 new.v11_root_report('UNRELATED-ROOT-CLAIM','0'*64,{},{});legacy=[]
 for name,identity in LEGACY:
  binding=pin(name,identity);report=pin(binding['report'],binding['report_sha256']);cid=binding['id']
  need(old.wave37_role(cid,identity,binding)==new.wave37_role(cid,identity,binding) is True,'old role unchanged')
  old.wave37_report(cid,binding['report_sha256'],binding,report);new.wave37_report(cid,binding['report_sha256'],binding,report);legacy.append(cid)
 need((ROOT/'CLAIMS.yaml').read_bytes()==before,'live ledger unchanged')
 save(out/'summary.json',dict(status='AUTHOR_REGISTRAR_V11_HELPER_CALIBRATION_PASS_PENDING_INDEPENDENT_REVIEW',
      timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',command=[sys.executable,*sys.argv],cwd=str(ROOT),
      inputs_sha256=pins,source_restoration=restoration,new_positive_adapters=positives,legacy_positive_adapters=legacy,
      strict_negative_count=len(controls),strict_negative_controls=controls,unknown_id_not_admitted=True,
      live_ledger_sha256_before=hashlib.sha256(before).hexdigest(),live_ledger_sha256_after=sha(ROOT/'CLAIMS.yaml'),
      registrar_main_called=False,ledger_mutations=0,index_mutations=0,scientific_invocations=0,
      independent_approval=False,target_resolution='NONE',limitations=['Same author as new registrar; this is preliminary helper calibration only.','No registrar main execution or live registration; separate author review/gate required.']))


if __name__=='__main__':main()
