"""V18 author helper/whole-AST metadata controls only; never call registrar main."""
import argparse, ast, copy, hashlib, importlib.util, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v17.py'
NEW = 'acceleration/register_20261003_bound_claims_v18.py'
SPEC = 'acceleration/calibrate_20261003_registrar_v18_helpers_v1_spec.md'
REGISTRAR_SPEC = 'acceleration/register_20261003_bound_claims_v18_spec.md'
DESCRIPTOR = 'acceleration/proposal_20261003_registrar_v18_exact_written_v1.json'
PINS = {
 OLD: '1ae20114929478bbfbcde7acdc42582453aefe003e76c801bd48353eb2a74e84',
 NEW: 'b310e6772f853af3e8faa867c3c60896b27234fe70b3e0c930f5bd46d1123207',
 DESCRIPTOR: '2692248d4274793d5fb162503d1eb3b9e5b02a517ef13f5fd6080ffc80f49629',
 'acceleration/register_20261003_bound_claims_v18_additions_v1.py.txt': '9890ee43b890977480e0e18c658b8969236b51737b2f5d9ff1986d0a3490296c',
 'acceleration/results/20261003_independent_review/ternary_prospective_bindings_metadata01/summary.json': 'bad6d398504d6fd25ad0d77fe4459a5781abfce542157fb823b18235614091ac',
 'acceleration/results/20261003_parity_bindings_timestamp_editorial03/summary.json': '85ba1edad0232b471f53f63cd2e524e9d3fa534d549e0895e241f7ed140afe23',
 'acceleration/results/20261003_parity_bindings_timestamp_editorial03_root_review.json': '595581f23521455beec05368518ad46029434c83193f48301aa277647fcdb7ca',
 'acceleration/audit_20261003_ternary_prospective_bindings_metadata_v1.md': 'fb0fbc61cc96ce39e7d8c644f23f7c0827c91553a40476fcb5668605c52d9822'}
ORDINARY = [
 'C-UNRESTRICTED-DEGREE14-TERNARY-EIGHT-DEFECT-NONREALIZABILITY',
 'C-UNRESTRICTED-DEGREE14-TERNARY-TEN-DEFECT-NONREALIZABILITY',
 'C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-K2-6-SUPPORT-NONREALIZABILITY',
 'C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-OCTAHEDRAL-SUPPORT-NONREALIZABILITY',
 'C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER13',
 'C-SYNTHETIC-UNRELATED']

class ControlError(ValueError): pass
def need(ok, stage):
 if not ok: raise ControlError(stage)
def sha(path):
 with path.open('rb') as handle: return hashlib.file_digest(handle, 'sha256').hexdigest()
def save(path, value):
 with path.open('x', encoding='utf8', newline='\n') as handle:
  json.dump(value, handle, indent=2, allow_nan=False); handle.write('\n')
def dump(node): return ast.dump(node, include_attributes=False)
def change(value, path, replacement):
 result=copy.deepcopy(value); node=result
 for key in path[:-1]: node=node[key]
 node[path[-1]]=replacement; return result
def load(path):
 spec=importlib.util.spec_from_file_location('v18_author_subject',path)
 module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def restore_ast(old_source, new_source):
 old=ast.parse(old_source); new=ast.parse(new_source); removed=[]; body=[]
 funcs={'v18_descriptor','v18_role','v18_report','v18_scope'}
 for node in new.body:
  if isinstance(node,ast.FunctionDef) and node.name in funcs: removed.append(node.name)
  elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'V18_DESCRIPTOR','V18_EXACT'}:
   need(isinstance(node.value,ast.Call) and ast.unparse(node.value.func)==('dict' if node.targets[0].id=='V18_DESCRIPTOR' else 'json.loads'), 'exact new literal descriptor/config assignments')
   removed.append(node.targets[0].id)
  else: body.append(node)
 need(set(removed)==funcs|{'V18_DESCRIPTOR','V18_EXACT'} and len(removed)==6, 'six exact new top-level nodes'); new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 diagnostic='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==diagnostic)
 extended=copy.deepcopy(guard); extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v18',ctx=ast.Load()))
 dispatcher=ast.parse("if wave43_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v18 disjoint exact written metadata adapter')\n editorial_statement_mapping = wave43_statement_mapping").body[0]
 scope=ast.parse("if cid in V18_EXACT:\n original_scope = copy.deepcopy(binding['scope'])\n projected_scope = v18_scope(cid, expected, binding)\n binding = copy.deepcopy(binding)\n binding['scope'] = projected_scope").body[0]
 edits=[]
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   if any(isinstance(t,ast.Name) and t.id=='exact_v18' for t in node.targets):
    need(ast.unparse(node)=='exact_v18 = v18_role(cid, expected, binding)','exact v18 role call'); edits.append('role_call'); return None
   if any(isinstance(t,ast.Name) and t.id=='wave43_statement_mapping' for t in node.targets):
    need(ast.unparse(node)=='wave43_statement_mapping = v18_report(cid, report_sha, binding, report)','exact v18 report call'); edits.append('report_call'); return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='wave43_statement_mapping is not None':
    need(dump(node)==dump(dispatcher),'exact v18 disjoint dispatcher'); edits.append('dispatcher'); return None
   if ast.unparse(node.test)=='cid in V18_EXACT':
    need(dump(node)==dump(scope),'exact v18 in-memory scope projection'); edits.append('scope_projection'); return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value==diagnostic:
    need(dump(node)==dump(extended),'exact one new ROOT-role alternative'); edits.append('role_alternative'); return copy.deepcopy(guard)
   return self.generic_visit(node)
 Restore().visit(newmain)
 need(sorted(edits)==['dispatcher','report_call','role_alternative','role_call','scope_projection'],'five exact main insertion groups')
 need(dump(old)==dump(new),'complete V17 AST restored')
 return dict(removed_top_level_nodes=removed,removed_main_insertion_groups=edits,complete_V17_AST_restored=True)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seconds',type=float,required=True); ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--source-sha256',required=True); ap.add_argument('--spec-sha256',required=True); ap.add_argument('--registrar-spec-sha256',required=True)
 ap.add_argument('--protected-ledger-sha256',required=True); ap.add_argument('--protected-index-sha256',required=True); ap.add_argument('--expected-head',required=True)
 a=ap.parse_args(); d=CommandDeadline(a.seconds,allocation_reason='V18 helper-only/whole AST metadata controls; hashing/setup within original invocation,20save; no registrar main or mathematical replay')
 out=a.out.resolve(); need(out.is_relative_to(ROOT),'bounded output'); out.mkdir(parents=True,exist_ok=False)
 before=(ROOT/'CLAIMS.yaml').read_bytes(); index_before=sha(ROOT/'.git/index'); pins={}; positives=[]; negatives=[]; mappings=[]
 def pin(name,wanted=None):
  need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within the allocated budget: input checks/save reserve')
  path=(ROOT/name).resolve(); need(path.is_relative_to(ROOT),'bounded input '+name); identity=sha(path)
  need(wanted is None or identity==wanted,'immutable input '+name); need(name not in pins or pins[name]==identity,'stable input '+name); pins[name]=identity
 def reject(label,stage,callback):
  try: callback()
  except Exception as error:
   if type(error) is not ValueError or str(error)!=stage: raise ControlError('WRONG_STAGE:'+label+':'+repr(error))
   negatives.append(dict(label=label,expected_diagnostic=stage,actual_diagnostic=str(error),outcome='REJECTED')); return
  raise ControlError('CORRUPTION_ACCEPTED:'+label)
 try:
  need(hashlib.sha256(before).hexdigest()==a.protected_ledger_sha256 and index_before==a.protected_index_sha256
       and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==a.expected_head,'explicit observed ledger/index/HEAD')
  pin(Path(__file__).relative_to(ROOT).as_posix(),a.source_sha256); pin(SPEC,a.spec_sha256); pin(REGISTRAR_SPEC,a.registrar_spec_sha256)
  for name in ['acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']: pin(name)
  for name,identity in PINS.items(): pin(name,identity)
  equality=restore_ast((ROOT/OLD).read_text(encoding='utf8'),(ROOT/NEW).read_text(encoding='utf8'))
  subject=load(ROOT/NEW); descriptor=json.loads((ROOT/DESCRIPTOR).read_bytes()); ids=[r['id'] for r in descriptor['adapters']]
  need(list(subject.V18_EXACT)==ids and len(ids)==8,'exact eight-ID config')
  correction=json.loads((ROOT/'acceleration/results/20261003_parity_bindings_timestamp_editorial03/summary.json').read_bytes())
  for name,wanted in correction['inputs_sha256'].items(): pin(name,wanted)
  for cid in ids:
   exact=subject.V18_EXACT[cid]; record=subject.v18_descriptor(cid); identity=exact['binding_sha256']
   binding=json.loads((ROOT/exact['binding_path']).read_bytes()); report=json.loads((ROOT/binding['report']).read_bytes())
   pin(exact['binding_path'],identity); pin(binding['report'],binding['report_sha256'])
   for name,wanted in binding['inputs_sha256'].items(): pin(name,wanted)
   need(subject.v18_role(cid,identity,binding) is True,'positive exact role'); positives.append(dict(label=cid+':role',outcome='PASS'))
   mapping=subject.v18_report(cid,binding['report_sha256'],binding,report)
   need(mapping['raw_statement_changed'] is False and mapping['original_report_statement']==binding['statement']
        and mapping['original_report_scope']==binding['scope'] and mapping['schema_scope']==record['schema_scope']
        and set(mapping['original_report_absent_headline_fields'])==set(record['report_headlines']['absent'])
        and mapping['mathematical_replays']==0,'positive exact written metadata mapping')
   mappings.append(mapping); positives.append(dict(label=cid+':report',outcome='PASS'))
   projected=subject.v18_scope(cid,identity,binding)
   need(subject.v15_same(projected,record['schema_scope']) and set(projected)=={'description','unrestricted_target','target_resolution'}
        and subject.v15_same(binding,json.loads((ROOT/exact['binding_path']).read_bytes())),'positive scope retains immutable binding')
   positives.append(dict(label=cid+':scope',outcome='PASS'))
   role=lambda b:subject.v18_role(cid,identity,b); rep=lambda r:subject.v18_report(cid,binding['report_sha256'],binding,r)
   reject(cid+':wrong_binding_hash','v18 exact frozen binding identity',lambda:subject.v18_role(cid,'0'*64,binding))
   stage='v18 exact typed revision status roles method kind basis'
   for key,value in [('id','C-SYNTHETIC-UNRELATED'),('revision',2),('claim_revision',2),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('producer','/root'),('verifier','/root/checkpoint_audit'),('method','independent_artifact_check'),('kind','exclusion'),('basis',[])]:
    reject(cid+':binding_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   for key in ['revision','claim_revision']:
    for value in [True,1.0]: reject(cid+':typed_'+key+':'+type(value).__name__,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   stage='v18 exact original scope dependencies and nonresolution'
   for key,value in [('scope',{}),('dependencies',[dict(id='C-SYNTHETIC',revision=1,relation='premise')]),('target_resolution','POSITIVE')]:
    reject(cid+':scope_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   stage='v18 exact literal statement report proof controls and no legacy fallback'
   for key,value in [('statement',binding['statement']+' Broader.'),('report','synthetic.json'),('report_sha256','0'*64),('proof','synthetic.md'),('proof_sha256','0'*64),('controls',{}),('verification_records',[])]:
    reject(cid+':primary_'+key,stage,lambda key=key,value=value:role(change(binding,[key],value)))
   for key,value in [('inputs_sha256',{}),('assumptions',[]),('shared_components',[]),('availability','PUBLIC'),('updated_at','2000-01-01T00:00:00+00:00')]:
    reject(cid+':complete_'+key,'v18 complete literal binding metadata',lambda key=key,value=value:role(change(binding,[key],value)))
   bad=copy.deepcopy(binding); del bad['revision']; reject(cid+':missing_revision','v18 exact typed revision status roles method kind basis',lambda:role(bad))
   reject(cid+':wrong_report_hash','v18 exact primary report identity',lambda:subject.v18_report(cid,'0'*64,binding,report))
   stage='v18 exact typed independent report identity and method'
   for key,value in [('status','UNKNOWN'),('claim_id','C-SYNTHETIC'),('producer','/root'),('verifier','/root/checkpoint_audit'),('method','independent_artifact_check'),('claim_revision',True),('claim_revision',1.0),('target_resolution','NEGATIVE')]:
    reject(cid+':report_'+key+':'+type(value).__name__,stage,lambda key=key,value=value:rep(change(report,[key],value)))
   stage='v18 exact literal report headlines and absences'
   for key,value in [('claim_status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('kind','exclusion'),('basis',[])]:
    reject(cid+':headline_'+key,stage,lambda key=key,value=value:rep(change(report,[key],value)))
   stage='v18 exact written statement original scope assumptions dependencies'
   for key,value in [('statement','Broader.'),('scope',{}),('assumptions',[]),('dependencies',[dict(id='C-SYNTHETIC')])]:
    reject(cid+':written_'+key,stage,lambda key=key,value=value:rep(change(report,[key],value)))
   stage='v18 exact written command null and reason'
   for key,value in [('command',['invented']),('command_null_reason','')]:
    reject(cid+':null_'+key,stage,lambda key=key,value=value:rep(change(report,[key],value)))
   if 'controls' in report:
    countkey=next(k for k,v in report['controls'].items() if type(v) is int); countpath=['controls',countkey]
   else: countpath=['written_boundary_reviews']
   count=report[countpath[0]] if len(countpath)==1 else report[countpath[0]][countpath[1]]
   for wrong in [bool(count),float(count)]:
    reject(cid+':typed_written_count:'+type(wrong).__name__,'v18 exact nonexecuted written control metadata',lambda wrong=wrong:rep(change(report,countpath,wrong)))
   for key,value in [('timestamp','2000-01-01T00:00:00+00:00'),('inputs_sha256',{})]:
    reject(cid+':complete_report_'+key,'v18 complete literal report metadata',lambda key=key,value=value:rep(change(report,[key],value)))
  for cid in ORDINARY:
   need(subject.v18_role(cid,'0'*64,{}) is False,'no unrelated/ordinary ROOT-role permission'); positives.append(dict(label=cid+':role_false',outcome='PASS'))
   need(subject.v18_report(cid,'0'*64,{}, {}) is None,'no unrelated/ordinary report projection'); positives.append(dict(label=cid+':report_none',outcome='PASS'))
  for label,callback in [('wrong_stage',lambda:(_ for _ in ()).throw(ValueError('wrong stage'))),('wrong_type',lambda:(_ for _ in ()).throw(TypeError('expected stage')))]:
   try: reject(label,'expected stage',callback)
   except ControlError as error: need(str(error).startswith('WRONG_STAGE:'+label+':'),'precise wrong-stage/type harness veto')
   else: raise ControlError('HARNESS_FALSE_ACCEPT')
  need(len(positives)==36 and len(negatives)==432 and len(mappings)==8,'predeclared36positive432negative8metadata mappings')
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==index_before,'protected observations unchanged')
  save(out/'controls.json',dict(positive=positives,strict_negative=negatives,harness_wrong_stage_and_type_rejected=2)); save(out/'mappings.json',mappings)
  save(out/'summary.json',dict(status='V18_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),
    producer='/root/checkpoint_audit',verifier=None,verifier_null_reason='Author helper controls cannot independently approve this registrar.',
    registrar_main_called=False,independent_approval=False,positive_controls=36,strict_negative_controls=432,harness_negative_controls=2,
    exact_claim_ids=ids,complete_AST_restoration=equality,metadata_mappings=mappings,scope_projection_records=6,original_absent_headline_records=2,
    ordinary_routes_unchanged=True,mathematical_replays=0,ledger_mutations=0,index_mutations=0,target_resolution='NONE',
    command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
    historical_protected_execution_state=dict(before={'CLAIMS.yaml':a.protected_ledger_sha256,'.git/index':index_before},after={'CLAIMS.yaml':sha(ROOT/'CLAIMS.yaml'),'.git/index':sha(ROOT/'.git/index')}),
    source_context_commit=a.expected_head,source_context_role='Published context only; working source identities separately pinned.',
    shared_components=['Byte-preserved V17 need/digest and V15 recursively typed equality; standard Python AST/JSON/SHA.', 'Frozen descriptors, bindings and accepted written reports are metadata evidence; no mathematical or discovery-producer checker is imported.'],
    limitations=['Author helper/AST controls only; no main-copy or actual ledger projection, mathematics, independent approval, science, staging or publication.', 'Separate ROOT engineering and actual transition checks are required.'],deadline=d.status()))
 except BaseException as error:
  save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),type=type(error).__name__,message=str(error),completed_positive=len(positives),completed_negative=len(negatives),inputs_sha256=pins,deadline=d.status())); raise
 finally: need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==index_before,'protected ledger/index unchanged even on failure')

if __name__=='__main__': main()

