"""Source-only V20 author metadata/AST controls; never call registrar main."""
import argparse, ast, copy, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v18.py'
V19 = 'acceleration/register_20261003_bound_claims_v19.py'
NEW = 'acceleration/register_20261003_bound_claims_v20.py'
SPEC = 'acceleration/calibrate_20261003_registrar_v20_helpers_v1_spec.md'
REGISTRAR_SPEC = 'acceleration/register_20261003_bound_claims_v20_spec.md'
DESCRIPTOR = 'acceleration/proposal_20261003_registrar_v19_exact_existing_v1.json'
FINAL_DESCRIPTOR = 'acceleration/proposal_20261003_registrar_v20_two_final_v1.json'
PINS = {
  "acceleration/calibrate_20261003_registrar_v19_helpers_v1.py": "64d8fd96f28eaf7c1dfa8f7de2fc6668d6eccb30372fe3c22aaff93460e9dad7",
  "acceleration/calibrate_20261003_registrar_v19_helpers_v1_spec.md": "4c16421a5c114457fb9b298ac637514ce04421ed465c2e3e4c22586b0edbe303",
  "acceleration/register_20261003_bound_claims_v18.py": "b310e6772f853af3e8faa867c3c60896b27234fe70b3e0c930f5bd46d1123207",
  "acceleration/register_20261003_bound_claims_v19.py": "e508d0ffab3f5e9f7b20f4713282f5fd88e9dc73492b3068dd532ea4e844f939",
  "acceleration/proposal_20261003_registrar_v19_exact_existing_v1.json": "2254b33bb130e6a9c409a1dda334279b4906a5d6a2c2623c7287a33caf60d275",
  "acceleration/register_20261003_bound_claims_v19_spec.md": "ba5b60a2708a62c9304f1969fc651aacebcfa5657f12d2575e34d65f893d8f5e",
  "acceleration/register_20261003_bound_claims_v19_additions_v1.py.txt": "5034ec585c1f05aeda29fba6ccb217c2afa4b7ca5b5c7e6ea23d22ea8093d2fb",
  "acceleration/results/20261003_registrar_v19_source_proposal01/source_diff.txt": "deef199f7de59f0d55801f6fe78e0242fcb3dfe838cda4c224d6c6c10976135b",
  "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
  "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
  "acceleration/validate_claims.py": "a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265",
  "docs/claims.schema.json": "0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac",
  "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
  "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
  "acceleration/results/20261003_independent_review/fixed17_exterior_moment_rational_feasible01/claim_binding_schema2.json": "1834df526949501ed6c7767d0b9ba4d52fc06f02b85c6b50ea44704ddf1451f1",
  "acceleration/results/20261003_independent_review/fixed17_exterior_moment_rational_feasible01/summary.json": "ad15a0bf516d39f03b8def41c3a551a18c04ba09ba1c7df9e5af905bfafa03d3",
  "acceleration/results/20261003_external_moment_support_primal_checker_v1_root_actual_full_acceptance01.json": "625f27b48dcf2aedae522926c352ef0a82a1b22132ecdc95ead1133ea99fde21",
  "acceleration/results/20261003_fixed17_rational_feasible_root_binding_metadata_acceptance01.json": "61e8becc811e5412fb341b37737ac8eed7fe4a7389ee1f0232a20aab6988a712",
  "acceleration/results/20261003_independent_review/exterior_type_cross_cn_cap01/claim_binding_schema2.json": "ce592293782b207739ac87c34929c6c6417f69c2e71e2f49a5c53a6d0ed352d7",
  "acceleration/results/20261003_independent_review/exterior_type_cross_cn_cap01/summary.json": "652da071e5026d320eff105573f907c54aead9a0381ab66dadab43e5aa3a1ee4",
  "acceleration/results/20261003_external_type_cross_cn_cap_root_binding_metadata_acceptance01.json": "bea80f99ab93e26983039954dba341a34bedfba3a58dc76ec35356d9d78b1124",
  "acceleration/results/20261003_independent_review/fixed17_exterior_moment_outside_cn_filter47201/claim_binding_schema2.json": "82d77964934cade61b9e10296d649584c01174c29460675a63dde25523f4280e",
  "acceleration/results/20261003_independent_review/fixed17_exterior_moment_outside_cn_filter47201/summary.json": "1fb1abe815189a5560f4c47c49f93288abb1aba1fb3ce8b69f619e21c3248c69",
  "acceleration/results/20261003_external_moment_outside_cn_filter_v1_root_actual_full_acceptance01.json": "9a710a653bee069e119b0479589c2867974b7f8392f8c2d417a96f33b9663007",
  "acceleration/results/20261003_savedbest_filter472_root_claim_metadata_review01.json": "c12a54e3dfb017456933bead3c303af000136095f52a7753f34f2518e2dc06ad",
  "acceleration/results/20261003_independent_review/exterior_type_pair_triple_caps01/claim_binding_schema2.json": "a1ed4e4dd1b039a2aeb8e94df4b05be182285cb8c7ef83940986d2ec3d706151",
  "acceleration/results/20261003_independent_review/exterior_type_pair_triple_caps01/summary.json": "d3e2f27aca979839edb3e612cd825d2cce18346d81ca2bfa868e86b6b1baffee",
  "acceleration/results/20261003_external_type_pair_triple_caps_root_written_packet_acceptance01.json": "37b782ffe72c047a19d0f3123310113a45d3a0486b3e3f668965567c387d4497",
  "acceleration/results/20261003_independent_review/seventeen_point_family_four_classes01/claim_binding_schema2.json": "99573f66be7be07e0ec22867e250b7395537f82fe07b6d9ea941839540cc9fe4",
  "acceleration/results/20261003_independent_review/seventeen_point_family_four_classes01/summary.json": "16675b2e86db9feb343900b310f409b3ac1722a9f7c164de8d6529cf5e7cecf6",
  "acceleration/results/20261003_seventeen_point_family_four_classes_root_written_packet_acceptance01.json": "f1dce2b282b46d7d6a3c9c87336ba94982f5fbd50d1b465bdd686cc1fc42d32c",
  "acceleration/results/20261003_independent_review/target_ternary_affine_unbalanced_circuit01/claim_binding_schema2.json": "967691cde75d57d5ae4c28f40861ae49e074695312531a146a60d9d7de425fa5",
  "acceleration/results/20261003_independent_review/target_ternary_affine_unbalanced_circuit01/summary.json": "985fa1cc5898f71ec38ed0644513adbb0fe1e58f7fb1eeb8af7c27ec7bca6fb0",
  "acceleration/results/20261003_native_written_ternary_two_bindings_root_metadata_review01.json": "a0399d4dadc4c7fdfd51fb71adeb8a55dd89b7cedd62e20b72067d5c634a1ec4",
  "acceleration/results/20261003_independent_review/target_ternary_unbalanced_circuit_upper98_01/claim_binding_schema2.json": "e9128774855a9c9e7eae3265e7919b631bacab08f303dbd511d6473f988bcda3",
  "acceleration/results/20261003_independent_review/target_ternary_unbalanced_circuit_upper98_01/summary.json": "398664a51fa6c9a5ed9e808db833e2438e3f0778109eba408779e67cb8a447b0",
  "acceleration/results/20261003_target_ternary_unbalanced_circuit_upper98_root_written_packet_acceptance01.json": "c1a6738481224d67be40569538c6afcdfa7f7e92fbc74eccdab19d35118d075a",
  "acceleration/results/20261003_registrar_v19_source_proposal01/proposal.json": "49b3bc7872b1b1d570950542d8d8178cd0495c8f50eeb2723afbc654d74607aa",
  "acceleration/register_20261003_bound_claims_v20.py": "58f4fd6fe5c69296a55cddf00e4a0185c21a13ef3d97c173984f030038d4f78b",
  "acceleration/register_20261003_bound_claims_v20_spec.md": "5457f3878696dc373c7af422589f108efcd1b0b85fb77a3ca36ffe7068b7bed7",
  "acceleration/register_20261003_bound_claims_v20_additions_v1.py.txt": "c8dfdf9d7bf2aadcd058a78a3300ee6fee17ef36419bf0ba1ebcd6b008103e44",
  "acceleration/results/20261003_registrar_v20_source_proposal01/source_diff.txt": "fc4c98a2ee9b9c32b6d75bb06ef4573bcf50470f769a2989a117921ede01a3b2",
  "acceleration/proposal_20261003_registrar_v20_two_final_v1.json": "b56816abdaa8bfca6177e7a189f5e15858a4a10ba8645f537be7bc54882bf9a9",
  "acceleration/results/20261003_independent_review/seventeen_point_labelled_triangle_family_complete_finite_census01/claim_binding_schema2.json": "1c01bee9c34ae407512270ec05c66f39e763a829f4e27102da97c86df10a70bb",
  "acceleration/results/20261003_independent_review/seventeen_point_labelled_triangle_family_complete_finite_census01/summary.json": "98fea7e58697cb41824f59ecc7871ba00ca7798f9a4e1147d80884f285b90237",
  "acceleration/results/20261003_seventeen_point_family_v3_root_actual_full_acceptance01.json": "ef56b765e80d1e9b353398bb5482665f2a4303ccef4c02dc00b2ef35471d6edc",
  "acceleration/results/20261003_wave44_three_draft_wrappers_root_metadata_acceptance01.json": "e11d49bfb1e8f7fedc763ee584d8304b88c45cf30a3a51daed66c906e03d93e0",
  "acceleration/results/20261003_independent_review/adjacency_switch_actual_api_finite_packet_engineering01/claim_binding_schema2.json": "189a71a021c5772dc0125a35e579e6226f5347a5b4bc4e75dfd7beced916df29",
  "acceleration/results/20261003_independent_review/adjacency_switch_actual_api_finite_packet_engineering01/summary.json": "bbd5ec509918e997bfd1f9aff6cc8581d3c2dbedb0a53bd7192af2400e247818",
  "acceleration/results/20261003_adjacency_switch_actual_api_v3_root_actual_full_acceptance01.json": "ce50a25cbc21aa5276f7cb1b43013e2fdc841d365eb80de762de8f859e21e348"
}
UNROUTED = [
 'C-FIXED17-EXTERIOR-FILTERED-MOMENT-RELAXATION-RATIONAL-FEASIBLE',
 'C-FIXED-SAVEDBEST-ALLMUTABLE-TERNARY-TWO-LINE-CENSUS',
 'C-SEVENTEEN-POINT-CLASS-I-UPPER-GRAM-EXTRA-EDGE-BOUNDARIES',
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

def restore_v20_ast(v19_source,new_source):
 old=ast.parse(v19_source);new=ast.parse(new_source);removed=[];kept=[]
 functions={'v20_descriptor','v20_role','v20_report'}
 for node in new.body:
  if isinstance(node,ast.FunctionDef) and node.name in functions:removed.append(node.name)
  elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'V20_DESCRIPTOR','V20_EXACT'}:
   name=node.targets[0].id
   need((name=='V20_DESCRIPTOR' and isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='dict') or (name=='V20_EXACT' and isinstance(node.value,ast.Dict)),'exact new final descriptor/config assignments');removed.append(name)
  else:kept.append(node)
 need(len(removed)==5 and set(removed)==functions|{'V20_DESCRIPTOR','V20_EXACT'},'five exact new final top-level nodes');new.body=kept
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main');newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 diagnostic='separate checking identity for the exact recorded discovery'
 guard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==diagnostic)
 extended=copy.deepcopy(guard);extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v20',ctx=ast.Load()))
 dispatcher=ast.parse("if wave44_final_mapping is not None:\n need(editorial_statement_mapping is None, 'v20 disjoint exact final binding adapter')\n editorial_statement_mapping = wave44_final_mapping").body[0];edits=[]
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   names={t.id for t in node.targets if isinstance(t,ast.Name)}
   if 'exact_v20' in names:
    need(ast.unparse(node)=='exact_v20 = v20_role(cid, expected, binding)','exact v20 role call');edits.append('role_call');return None
   if 'wave44_final_mapping' in names:
    need(ast.unparse(node)=='wave44_final_mapping = v20_report(cid, report_sha, binding, report)','exact v20 report call');edits.append('report_call');return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='wave44_final_mapping is not None':
    need(dump(node)==dump(dispatcher),'exact v20 disjoint dispatcher');edits.append('dispatcher');return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value==diagnostic:
    need(dump(node)==dump(extended),'exact one new final-role alternative');edits.append('role_alternative');return copy.deepcopy(guard)
   return self.generic_visit(node)
 Restore().visit(newmain);need(sorted(edits)==['dispatcher','report_call','role_alternative','role_call'],'four exact final main insertion groups');need(dump(old)==dump(new),'complete V19 AST restored')
 return dict(removed_top_level_nodes=removed,removed_main_insertion_groups=edits,complete_V19_AST_restored=True)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True)
 for name in ['source-sha256','spec-sha256','protected-ledger-sha256','protected-index-sha256','expected-head']:
  p.add_argument('--'+name,required=True)
 a=p.parse_args(); d=CommandDeadline(a.seconds,allocation_reason='V20 exact author metadata/AST controls; setup/hash/outputs inside worker20save, no main/math')
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
  old_source=(ROOT/OLD).read_text(encoding='utf8');v19_source=(ROOT/V19).read_text(encoding='utf8');new_source=(ROOT/NEW).read_text(encoding='utf8')
  guard();v19_equality=restore_v20_ast(v19_source,new_source);equality=restore_ast(old_source,v19_source);guard();positives.extend([dict(label='whole_V19_AST_restored',outcome='PASS'),dict(label='whole_V18_AST_restored',outcome='PASS')])
  for label,oldtext,middle,newtext,stage in [('inherited_V18_change',old_source+'\npass\n',v19_source,new_source,'complete V18 AST restored'),('inherited_V19_change',old_source,v19_source+'\npass\n',new_source,'complete V19 AST restored'),('unrelated_V20_change',old_source,v19_source,new_source+'\npass\n','complete V19 AST restored')]:
   try:restore_v20_ast(middle,newtext);restore_ast(oldtext,middle)
   except ControlError as e:need(str(e)==stage,'exact AST corruption stage');negatives.append(dict(label=label,expected_stage=stage,actual_stage=str(e)))
   else:raise ControlError('AST_CORRUPTION_ACCEPTED')
  descriptor=json.loads((ROOT/DESCRIPTOR).read_bytes());final_descriptor=json.loads((ROOT/FINAL_DESCRIPTOR).read_bytes());records=descriptor['adapters']+final_descriptor['adapters'];guard()
  module_spec=importlib.util.spec_from_file_location('v19_author_subject',ROOT/NEW)
  subject=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(subject);guard()
  ids=[r['id'] for r in records];need(list(subject.V19_EXACT)+list(subject.V20_EXACT)==ids and len(ids)==9,'exact nine-ID config')
  present=[dict(id=cid,revision=1) for cid in ids]
  for record in records:
   guard();cid=record['id'];identity=record['binding']['sha256'];report_sha=record['primary_report']['sha256']
   pin(record['binding']['path'],identity);pin(record['primary_report']['path'],report_sha)
   for review in record['review_records']:pin(review['path'],review['sha256'])
   binding=json.loads((ROOT/record['binding']['path']).read_bytes());report=json.loads((ROOT/record['primary_report']['path']).read_bytes())
   final=cid in subject.V20_EXACT;role_fn=subject.v20_role if final else subject.v19_role;report_fn=subject.v20_report if final else subject.v19_report
   prefix='v20' if final else 'v19'
   nonmap_binding_stage=prefix+(' complete typed nonmap final binding contract' if final else ' complete typed nonmap binding contract')
   nonmap_report_stage=prefix+(' complete typed nonmap final report contract' if final else ' complete typed nonmap report contract')
   need(role_fn(cid,identity,binding) is True,'positive exact role');positives.append(dict(label=cid+':role',outcome='PASS'))
   mapping=report_fn(cid,report_sha,binding,report)
   need(mapping['raw_statement_changed'] is False and mapping['missing_headline_waiver'] is False
    and subject.v15_same(mapping['original_report_scope'],report['scope'])
    and subject.v15_same(mapping['original_dependencies'],binding['dependencies']),'positive complete literal report mapping')
   mappings.append(mapping);positives.append(dict(label=cid+':report',outcome='PASS'))
   need(subject.v15_same((binding['scope'] if final else subject.v19_scope(cid,identity,binding)),(record['scope'] if final else record['schema_scope'])),'positive exact scope');positives.append(dict(label=cid+':scope',outcome='PASS'))
   need(subject.v15_same((binding['dependencies'] if final else subject.v19_dependencies(cid,identity,binding,present)),(record['dependencies'] if final else record['schema_dependencies'])),'positive exact dependencies');positives.append(dict(label=cid+':dependencies',outcome='PASS'))
   role=lambda b:role_fn(cid,identity,b)
   reject(cid+':wrong_binding_hash',prefix+(' exact frozen final binding identity' if final else ' exact frozen binding identity'),lambda:role_fn(cid,'0'*64,binding))
   mutations=[('id','C-UNRELATED'),('revision',2),('claim_revision',True),('claim_revision',1.0),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('producer',binding['verifier']),('verifier','/root'),('method','UNKNOWN'),('kind','exclusion'),('basis',[]),('scope',{}),('dependencies',[dict(id='C-UNRELATED')]),('statement','Broader.'),('report','fake.json'),('report_sha256','0'*64),('verification_timestamp','2000-01-01T00:00:00+00:00'),('availability','PUBLIC')]
   for n,(key,value) in enumerate(mutations):reject(cid+':binding_'+key+':'+str(n),nonmap_binding_stage,lambda key=key,value=value:role(changed(binding,key,value)))
   extra=changed(binding,'unexpected',True);missing=copy.deepcopy(binding);del missing['scope']
   for label,bad in [('extra_binding_field',extra),('missing_binding_scope',missing)]:reject(cid+':'+label,nonmap_binding_stage,lambda bad=bad:role(bad))
   reject(cid+':binding_map',prefix+(' complete literal final binding including input map' if final else ' complete literal binding including input map'),lambda:role(changed(binding,'inputs_sha256',{})))
   rep=lambda r:report_fn(cid,report_sha,binding,r)
   reject(cid+':wrong_report_hash',prefix+(' exact final claim-bound report identity' if final else ' exact claim-bound report identity'),lambda:report_fn(cid,'0'*64,binding,report))
   rm=[('status','UNKNOWN'),('claim_id','C-UNRELATED'),('claim_revision',True),('claim_revision',1.0),('statement','Broader.'),('scope',{}),('producer',binding['verifier']),('verifier','/root'),('method','UNKNOWN'),('target_resolution','POSITIVE'),(record['report_timestamp_field'],'2000-01-01T00:00:00+00:00')]
   for n,(key,value) in enumerate(rm):reject(cid+':report_'+key+':'+str(n),nonmap_report_stage,lambda key=key,value=value:rep(changed(report,key,value)))
   missing=copy.deepcopy(report);del missing['statement'];reject(cid+':missing_report_statement',nonmap_report_stage,lambda:rep(missing))
   reject(cid+':report_map',prefix+(' complete literal final report including input map' if final else ' complete literal report including input map'),lambda:rep(changed(report,'inputs_sha256',{})))
   for dep in (record['dependencies'] if final else record['schema_dependencies']):
    for n,value in enumerate([None,2,True,1.0]):
     bad=[x for x in present if x['id']!=dep['id']]
     if value is not None:bad.append(dict(id=dep['id'],revision=value))
     reject(cid+':prerequisite_revision_'+str(n),'v19 exact prerequisite revision present before dependent',lambda bad=bad:subject.v19_dependencies(cid,identity,binding,bad))
   need(subject.v15_same(binding,json.loads((ROOT/record['binding']['path']).read_bytes())),'immutable binding not changed by projection')
  for cid in UNROUTED:
   need(subject.v19_role(cid,'0'*64,{}) is False and subject.v20_role(cid,'0'*64,{}) is False,'no new unrouted role');positives.append(dict(label=cid+':role_false',outcome='PASS'))
   need(subject.v19_report(cid,'0'*64,{}, {}) is None and subject.v20_report(cid,'0'*64,{}, {}) is None,'no new unrouted report mapping');positives.append(dict(label=cid+':report_none',outcome='PASS'))
  for label,callback in [('wrong_stage',lambda:(_ for _ in ()).throw(ValueError('different'))),('wrong_type',lambda:(_ for _ in ()).throw(TypeError('expected')))]:
   try:reject(label,'expected',callback)
   except ControlError as e:need(str(e).startswith('WRONG_STAGE:'+label+':'),'harness rejects wrong stage/type')
   else:raise ControlError('HARNESS_FALSE_ACCEPT')
  need(len(positives)==46 and len(negatives)==335 and len(mappings)==9,'declared46positive335negative9mappings')
  protected();save('controls.json',dict(positive=positives,strict_negative=negatives,harness_wrong_stage_and_type_rejected=2));save('mappings.json',mappings)
  protected();save('summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='V20_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW',producer='/root/checkpoint_audit',verifier=None,verifier_null_reason='Author controls cannot independently approve this registrar',source_sha256=a.source_sha256,spec_sha256=a.spec_sha256,positive_controls=46,strict_negative_controls=335,harness_negative_controls=2,metadata_mappings=9,complete_AST_restoration=equality,complete_V19_AST_restoration=v19_equality,exact_ids=ids,new_Native_roles=7,exact_ROOT_API_roles=1,ordinary_scope_only=1,command=[sys.executable,*sys.argv],inputs_sha256=inputs,source_context=a.expected_head,protected_ledger_sha256=a.protected_ledger_sha256,protected_index_sha256=index_before,registrar_main_called=False,mathematical_replays=0,bulk_scientific_closure_rehashed=False,ledger_mutations=0,index_mutations=0,target_resolution='NONE',independent_approval=False,deadline=d.status()));guard();protected()
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
