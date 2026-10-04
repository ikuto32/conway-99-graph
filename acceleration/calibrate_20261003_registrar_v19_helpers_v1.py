"""Source-only V19 author metadata/AST controls; never call registrar main."""
import argparse, ast, copy, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v18.py'
NEW = 'acceleration/register_20261003_bound_claims_v19.py'
SPEC = 'acceleration/calibrate_20261003_registrar_v19_helpers_v1_spec.md'
REGISTRAR_SPEC = 'acceleration/register_20261003_bound_claims_v19_spec.md'
DESCRIPTOR = 'acceleration/proposal_20261003_registrar_v19_exact_existing_v1.json'
PINS = {
 OLD:'b310e6772f853af3e8faa867c3c60896b27234fe70b3e0c930f5bd46d1123207',
 NEW:'e508d0ffab3f5e9f7b20f4713282f5fd88e9dc73492b3068dd532ea4e844f939',
 DESCRIPTOR:'2254b33bb130e6a9c409a1dda334279b4906a5d6a2c2623c7287a33caf60d275',
 REGISTRAR_SPEC:'ba5b60a2708a62c9304f1969fc651aacebcfa5657f12d2575e34d65f893d8f5e',
 'acceleration/register_20261003_bound_claims_v19_additions_v1.py.txt':'5034ec585c1f05aeda29fba6ccb217c2afa4b7ca5b5c7e6ea23d22ea8093d2fb',
 'acceleration/results/20261003_registrar_v19_source_proposal01/source_diff.txt':'deef199f7de59f0d55801f6fe78e0242fcb3dfe838cda4c224d6c6c10976135b',
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/validate_claims.py':'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
 'docs/claims.schema.json':'0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db'}
UNROUTED = [
 'C-FIXED17-EXTERIOR-FILTERED-MOMENT-RELAXATION-RATIONAL-FEASIBLE',
 'C-SEVENTEEN-POINT-LABELLED-TRIANGLE-FAMILY-COMPLETE-FINITE-CENSUS',
 'C-ADJACENCY-SWITCH-ACTUAL-API-FINITE-PACKET-ENGINEERING',
 'C-SYNTHETIC-UNRELATED']

class ControlError(ValueError): pass
def need(ok, stage):
 if not ok: raise ControlError(stage)
def dump(node): return ast.dump(node,include_attributes=False)
def changed(value,key,replacement):
 result=copy.deepcopy(value); result[key]=replacement; return result

def restore_ast(old_source,new_source):
 old=ast.parse(old_source); new=ast.parse(new_source); removed=[]; kept=[]
 functions={'v19_descriptor','v19_role','v19_report','v19_scope','v19_dependencies'}
 for node in new.body:
  if isinstance(node,ast.FunctionDef) and node.name in functions: removed.append(node.name)
  elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'V19_DESCRIPTOR','V19_EXACT'}:
   name=node.targets[0].id
   need((name=='V19_DESCRIPTOR' and isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='dict')
        or (name=='V19_EXACT' and isinstance(node.value,ast.Dict)), 'exact new literal descriptor/config assignments')
   removed.append(name)
  else: kept.append(node)
 need(len(removed)==7 and set(removed)==functions|{'V19_DESCRIPTOR','V19_EXACT'},'seven exact new top-level nodes')
 new.body=kept
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 diagnostic='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
   and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==diagnostic)
 extended=copy.deepcopy(guard); extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v19',ctx=ast.Load()))
 dispatcher=ast.parse("if wave44_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v19 disjoint exact existing binding adapter')\n editorial_statement_mapping = wave44_statement_mapping").body[0]
 scope=ast.parse("if cid in V19_EXACT:\n original_scope = copy.deepcopy(binding['scope'])\n projected_scope = v19_scope(cid, expected, binding)\n projected_dependencies = v19_dependencies(cid, expected, binding, data['claims'])\n binding = copy.deepcopy(binding)\n binding['scope'] = projected_scope\n binding['dependencies'] = projected_dependencies").body[0]
 edits=[]
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   names={t.id for t in node.targets if isinstance(t,ast.Name)}
   if 'exact_v19' in names:
    need(ast.unparse(node)=='exact_v19 = v19_role(cid, expected, binding)','exact v19 role call'); edits.append('role_call'); return None
   if 'wave44_statement_mapping' in names:
    need(ast.unparse(node)=='wave44_statement_mapping = v19_report(cid, report_sha, binding, report)','exact v19 report call'); edits.append('report_call'); return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='wave44_statement_mapping is not None':
    need(dump(node)==dump(dispatcher),'exact v19 disjoint dispatcher'); edits.append('dispatcher'); return None
   if ast.unparse(node.test)=='cid in V19_EXACT':
    need(dump(node)==dump(scope),'exact v19 in-memory scope/dependency projection'); edits.append('scope_projection'); return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value==diagnostic:
    need(dump(node)==dump(extended),'exact one new Native-role alternative'); edits.append('role_alternative'); return copy.deepcopy(guard)
   return self.generic_visit(node)
 Restore().visit(newmain)
 need(sorted(edits)==['dispatcher','report_call','role_alternative','role_call','scope_projection'],'five exact main insertion groups')
 need(dump(old)==dump(new),'complete V18 AST restored')
 return dict(removed_top_level_nodes=removed,removed_main_insertion_groups=edits,complete_V18_AST_restored=True)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True)
 for name in ['source-sha256','spec-sha256','protected-ledger-sha256','protected-index-sha256','expected-head']:
  p.add_argument('--'+name,required=True)
 a=p.parse_args(); d=CommandDeadline(a.seconds,allocation_reason='V19 exact author metadata/AST controls; setup/hash/outputs inside worker20save, no main/math')
 out=Path(a.out).resolve(); need(out.is_relative_to(ROOT) and not out.exists(),'fresh bounded output');out.mkdir(parents=True)
 inputs={}; positives=[];negatives=[];mappings=[]
 def guard():
  status=d.status();need(not status['stop_required'] and status['remaining_seconds']>20,'SAVE_RESERVE')
 def sha(path):
  h=hashlib.sha256()
  with path.open('rb') as f:
   while block:=f.read(1024**2):guard();h.update(block)
  guard();return h.hexdigest()
 def pin(name,expected):
  q=ROOT/name;need(q.resolve().is_relative_to(ROOT) and not q.is_symlink() and q.is_file(),'bounded regular input')
  need(sha(q)==expected,'immutable input '+name);need(name not in inputs or inputs[name]==expected,'stable input '+name);inputs[name]=expected
 def save(name,value):
  guard();q=out/name
  with q.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
  guard()
 def reject(label,stage,callback):
  guard()
  try:callback()
  except Exception as e:
   if type(e) is not ValueError or str(e)!=stage:raise ControlError('WRONG_STAGE:'+label+':'+repr(e))
   negatives.append(dict(label=label,expected_stage=stage,actual_stage=str(e)));return
  raise ControlError('CORRUPTION_ACCEPTED:'+label)
 before=(ROOT/'CLAIMS.yaml').read_bytes();index_before=sha(ROOT/'.git/index')
 def protected():
  guard();need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==index_before
   and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==a.expected_head,'protected HEAD/ledger/index unchanged');guard()
 try:
  need(hashlib.sha256(before).hexdigest()==a.protected_ledger_sha256 and index_before==a.protected_index_sha256,'exact protected input hashes');protected()
  pin(Path(__file__).relative_to(ROOT).as_posix(),a.source_sha256);pin(SPEC,a.spec_sha256)
  for name,identity in PINS.items():pin(name,identity)
  old_source=(ROOT/OLD).read_text(encoding='utf8');new_source=(ROOT/NEW).read_text(encoding='utf8')
  guard();equality=restore_ast(old_source,new_source);guard();positives.append(dict(label='whole_V18_AST_restored',outcome='PASS'))
  for label,oldtext,newtext in [('inherited_old_change',old_source+'\npass\n',new_source),('unrelated_new_change',old_source,new_source+'\npass\n')]:
   try:restore_ast(oldtext,newtext)
   except ControlError as e:need(str(e)=='complete V18 AST restored','exact AST corruption stage');negatives.append(dict(label=label,expected_stage=str(e),actual_stage=str(e)))
   else:raise ControlError('AST_CORRUPTION_ACCEPTED')
  descriptor=json.loads((ROOT/DESCRIPTOR).read_bytes());guard()
  module_spec=importlib.util.spec_from_file_location('v19_author_subject',ROOT/NEW)
  subject=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(subject);guard()
  ids=[r['id'] for r in descriptor['adapters']];need(list(subject.V19_EXACT)==ids and len(ids)==7,'exact seven-ID config')
  present=[dict(id=cid,revision=1) for cid in ids]
  for record in descriptor['adapters']:
   guard();cid=record['id'];identity=record['binding']['sha256'];report_sha=record['primary_report']['sha256']
   pin(record['binding']['path'],identity);pin(record['primary_report']['path'],report_sha)
   for review in record['review_records']:pin(review['path'],review['sha256'])
   binding=json.loads((ROOT/record['binding']['path']).read_bytes());report=json.loads((ROOT/record['primary_report']['path']).read_bytes())
   need(subject.v19_role(cid,identity,binding) is True,'positive exact role');positives.append(dict(label=cid+':role',outcome='PASS'))
   mapping=subject.v19_report(cid,report_sha,binding,report)
   need(mapping['raw_statement_changed'] is False and mapping['missing_headline_waiver'] is False
    and subject.v15_same(mapping['original_report_scope'],report['scope'])
    and subject.v15_same(mapping['original_dependencies'],binding['dependencies']),'positive complete literal report mapping')
   mappings.append(mapping);positives.append(dict(label=cid+':report',outcome='PASS'))
   need(subject.v15_same(subject.v19_scope(cid,identity,binding),record['schema_scope']),'positive exact scope');positives.append(dict(label=cid+':scope',outcome='PASS'))
   need(subject.v15_same(subject.v19_dependencies(cid,identity,binding,present),record['schema_dependencies']),'positive exact dependencies');positives.append(dict(label=cid+':dependencies',outcome='PASS'))
   role=lambda b:subject.v19_role(cid,identity,b)
   reject(cid+':wrong_binding_hash','v19 exact frozen binding identity',lambda:subject.v19_role(cid,'0'*64,binding))
   mutations=[('id','C-UNRELATED'),('revision',2),('claim_revision',True),('claim_revision',1.0),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('producer',binding['verifier']),('verifier','/root'),('method','UNKNOWN'),('kind','exclusion'),('basis',[]),('scope',{}),('dependencies',[dict(id='C-UNRELATED')]),('statement','Broader.'),('report','fake.json'),('report_sha256','0'*64),('verification_timestamp','2000-01-01T00:00:00+00:00'),('availability','PUBLIC')]
   for n,(key,value) in enumerate(mutations):reject(cid+':binding_'+key+':'+str(n),'v19 complete typed nonmap binding contract',lambda key=key,value=value:role(changed(binding,key,value)))
   extra=changed(binding,'unexpected',True);missing=copy.deepcopy(binding);del missing['scope']
   for label,bad in [('extra_binding_field',extra),('missing_binding_scope',missing)]:reject(cid+':'+label,'v19 complete typed nonmap binding contract',lambda bad=bad:role(bad))
   reject(cid+':binding_map','v19 complete literal binding including input map',lambda:role(changed(binding,'inputs_sha256',{})))
   rep=lambda r:subject.v19_report(cid,report_sha,binding,r)
   reject(cid+':wrong_report_hash','v19 exact claim-bound report identity',lambda:subject.v19_report(cid,'0'*64,binding,report))
   rm=[('status','UNKNOWN'),('claim_id','C-UNRELATED'),('claim_revision',True),('claim_revision',1.0),('statement','Broader.'),('scope',{}),('producer',binding['verifier']),('verifier','/root'),('method','UNKNOWN'),('target_resolution','POSITIVE'),(record['report_timestamp_field'],'2000-01-01T00:00:00+00:00')]
   for n,(key,value) in enumerate(rm):reject(cid+':report_'+key+':'+str(n),'v19 complete typed nonmap report contract',lambda key=key,value=value:rep(changed(report,key,value)))
   missing=copy.deepcopy(report);del missing['statement'];reject(cid+':missing_report_statement','v19 complete typed nonmap report contract',lambda:rep(missing))
   reject(cid+':report_map','v19 complete literal report including input map',lambda:rep(changed(report,'inputs_sha256',{})))
   for dep in record['schema_dependencies']:
    for n,value in enumerate([None,2,True,1.0]):
     bad=[x for x in present if x['id']!=dep['id']]
     if value is not None:bad.append(dict(id=dep['id'],revision=value))
     reject(cid+':prerequisite_revision_'+str(n),'v19 exact prerequisite revision present before dependent',lambda bad=bad:subject.v19_dependencies(cid,identity,binding,bad))
   need(subject.v15_same(binding,json.loads((ROOT/record['binding']['path']).read_bytes())),'immutable binding not changed by projection')
  for cid in UNROUTED:
   need(subject.v19_role(cid,'0'*64,{}) is False,'no new unrouted role');positives.append(dict(label=cid+':role_false',outcome='PASS'))
   need(subject.v19_report(cid,'0'*64,{}, {}) is None,'no new unrouted report mapping');positives.append(dict(label=cid+':report_none',outcome='PASS'))
  for label,callback in [('wrong_stage',lambda:(_ for _ in ()).throw(ValueError('different'))),('wrong_type',lambda:(_ for _ in ()).throw(TypeError('expected')))]:
   try:reject(label,'expected',callback)
   except ControlError as e:need(str(e).startswith('WRONG_STAGE:'+label+':'),'harness rejects wrong stage/type')
   else:raise ControlError('HARNESS_FALSE_ACCEPT')
  need(len(positives)==37 and len(negatives)==262 and len(mappings)==7,'declared37positive262negative7mappings')
  protected();save('controls.json',dict(positive=positives,strict_negative=negatives,harness_wrong_stage_and_type_rejected=2));save('mappings.json',mappings)
  protected();save('summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='V19_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW',producer='/root/checkpoint_audit',verifier=None,verifier_null_reason='Author controls cannot independently approve this registrar',source_sha256=a.source_sha256,spec_sha256=a.spec_sha256,positive_controls=37,strict_negative_controls=262,harness_negative_controls=2,metadata_mappings=7,complete_AST_restoration=equality,exact_ids=ids,new_Native_roles=6,ordinary_scope_only=1,command=[sys.executable,*sys.argv],inputs_sha256=inputs,source_context=a.expected_head,protected_ledger_sha256=a.protected_ledger_sha256,protected_index_sha256=index_before,registrar_main_called=False,mathematical_replays=0,bulk_scientific_closure_rehashed=False,ledger_mutations=0,index_mutations=0,target_resolution='NONE',independent_approval=False,deadline=d.status()));guard();protected()
 except BaseException as e:
  # Failure saving uses the already reserved closing interval, under the same
  # contained invocation. A failed ordinary guard cannot suppress its receipt.
  with (out/'failure.json').open('x',encoding='utf8',newline='\n') as f:
   json.dump(dict(timestamp=datetime.now(timezone.utc).isoformat(),error_type=type(e).__name__,message=str(e),positive_completed=len(positives),negative_completed=len(negatives),inputs_sha256=inputs,deadline=d.status()),f,indent=2,allow_nan=False);f.write('\n')
  raise
 finally:
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==index_before
   and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==a.expected_head,'protected HEAD/ledger/index unchanged even on failure')

if __name__=='__main__':main()
