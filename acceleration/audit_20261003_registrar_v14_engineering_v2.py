"""Independent V14 exact editorial/metadata engineering audit; no mathematics."""
import argparse,ast,copy,hashlib,importlib.util,json,os,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/register_20261003_bound_claims_v12.py'
OLD='acceleration/register_20261003_bound_claims_v13.py'
NEW='acceleration/register_20261003_bound_claims_v14.py'
RANK='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85'
CENSUS='C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
LOW='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
PINS={BASE:'70d4082b2f73fd23e4d8fb295e36eeb0092976c01f78e99fcd342f3a96598044',OLD:'1cfac35e19e473822583adfec8be7dfbd2ec73f59d0508febec14d24aeceef1a',NEW:'6cf12f3dcb3b1e95d692d773df9e266c73101ce6ed0e9bebba0e79d00669c79b',
'acceleration/audit_20261003_registrar_v14_engineering_v1.py':'81e326dc4553d90dad49c8875f6dc28f0a8dd8589c56d1c168a2edadfa2fda58',
'acceleration/audit_20261003_registrar_v14_engineering_v1_spec.md':'1a848eae9a25d0f9bcfabc3e3721d3be5df89515909dea98cef7f6e8a7d708d3',
'acceleration/results/20261003_wave38_public_confirmation01/receipt.json':'86bf29a5baf14189f600e29065c2024d3ab92f9700c652b1d87b1048ccbb176b',
'acceleration/confirm_20261003_wave38_publication_v1.py':'20eb0e41d03bd88b37355077b67f9fa1d6636e241193dd70f4b4bf1aeb5b3495',
'acceleration/register_20261003_bound_claims_v14_spec.md':'d4ea135b838fd6d536b9566ca2168d01481fa003adc7431bdf7c99ad405330db',
'acceleration/calibrate_20261003_registrar_v14_helpers_v1.py':'c094d2cb2b8d002b2c8629928a208546d678496c2c4f4f603a51c1b6fa9f4ef4',
'acceleration/calibrate_20261003_registrar_v14_helpers_v1_spec.md':'d38c3e8d728d3356f69fbf155e52d3cd13943800713dc9be826079161a649f3b',
'acceleration/results/20261003_registrar_v14_helpers01/summary.json':'e903c10439cfa3aeb6ef706bc7079d907491f03cfed6af2f170f15af03d87a8e',
'acceleration/register_20261003_bound_claims_v13_spec.md':'1313f03b28abcf4e7a8411a26387663ec9c11c8c52daf538e1c2acdddcbf620f',
'acceleration/calibrate_20261003_registrar_v13_helpers_v2.py':'0de0aaa5bde6fd4ab9b56ec5d3d27b42b73f88e829285bdfcd3f24ae18613ac1',
'acceleration/calibrate_20261003_registrar_v13_helpers_v2_spec.md':'65a058655d78c84db8abea275e4a8a4a4bf320bb42e18a506beee4220a6782c8',
'acceleration/results/20261003_registrar_v13_helpers02/summary.json':'6dd5e2036159763a9fb50c17b5334bd75bbf912f78439caab438d47931343f2b'}
BINDINGS=[('acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json','40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05'),
('acceleration/results/20261003_incidence_low_weight_bindings02/rank85_claim_binding_schema2_v2.json','2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189'),
('acceleration/results/20261003_fixed_two_line_census_binding03/claim_binding_schema2_draft.json','b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1')]
BEFORE='ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a'
INDEX_BEFORE='68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152'
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
def v13_equivalence(old_source,new_source):
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
def equivalence(old_source,new_source):
 old,new=ast.parse(old_source),ast.parse(new_source);removed=[];body=[]
 for node in new.body:
  if isinstance(node,ast.FunctionDef)and node.name=='v14_lowword_editorial':removed.append(node.name)
  else:body.append(node)
 need(removed==['v14_lowword_editorial'],'exactly one new editorial function');new.body=body;newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name=='main');changes=[]
 expected_claim=ast.parse("claim['unknowns']['editorial_statement_mapping'] = json.dumps(editorial_statement_mapping,sort_keys=True)").body[0]
 expected_report=ast.parse("report['editorial_statement_mappings'] = [json.loads(c['unknowns']['editorial_statement_mapping']) for c in data['claims'][len(old['claims']):] if 'editorial_statement_mapping' in c['unknowns']]").body[0]
 class Normalize(ast.NodeTransformer):
  def visit_Assign(self,node):
   if any(isinstance(t,ast.Name)and t.id=='editorial_statement_mapping'for t in node.targets):need(ast.unparse(node.value)=='v14_lowword_editorial(cid, expected, binding, report_sha, report)','exact editorial call assignment');changes.append('editorial_call');return None
   if ast.dump(node,include_attributes=False)==ast.dump(expected_report,include_attributes=False):changes.append('registration_mapping_list');return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='editorial_statement_mapping is not None':
    if len(node.body)==1 and isinstance(node.body[0],ast.Pass):need(len(node.orelse)==1 and isinstance(node.orelse[0],ast.If)and ast.unparse(node.orelse[0].test)=="'statement' in report",'exact editorial statement alternative');changes.append('editorial_statement_alternative');return self.visit(node.orelse[0])
    need(len(node.body)==1 and not node.orelse and ast.dump(node.body[0],include_attributes=False)==ast.dump(expected_claim,include_attributes=False),'exact claim original-statement mapping');changes.append('claim_mapping');return None
   return self.generic_visit(node)
 Normalize().visit(newmain);need(sorted(changes)==['claim_mapping','editorial_call','editorial_statement_alternative','registration_mapping_list'],'exact four editorial main insertions');need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'entire prior V13 executable AST unchanged');return dict(new_functions=removed,main_insertions=changes,restored_ast_identical=True)
def reject(records,label,diagnostic,call):
 try:call()
 except ValueError as error:need(type(error)is ValueError and str(error)==diagnostic,'precise rejection '+label+' got '+repr(error));records.append(dict(label=label,outcome='REJECTED',diagnostic=str(error)))
 else:raise AuditError('CORRUPTION_ACCEPTED:'+label)
def changed(obj,path,value):
 result=copy.deepcopy(obj);node=result
 for key in path[:-1]:node=node[key]
 node[path[-1]]=value;return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent V14 editorial plus preserved V13 adapter AST/boundary/350to353 protected projections; previous analogous25.7s,150worker20reserve, no math/science/live writes');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];barriers=[];before=(ROOT/'CLAIMS.yaml').read_bytes();need(hashlib.sha256(before).hexdigest()==BEFORE,'exact current350 ledger');index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute()else ROOT/index;index_before=sha(index)
 need(index_before==INDEX_BEFORE,'exact current publication index')
 def pin(name,identity=None):
  need(deadline.status()['remaining_seconds']>20,'not completed within allocation');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'bounded input '+name);actual=sha(path);need(identity is None or identity==actual,'exact input '+name);need(name not in pins or pins[name]==actual,'stable input '+name);pins[name]=actual;return actual
 try:
  for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_registrar_v14_engineering_v2_spec.md','acceleration/audit_20261003_registrar_v12_engineering_v1.py','acceleration/audit_20261003_registrar_v12_engineering_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','uv.lock','pyproject.toml']:pin(name)
  for name,identity in PINS.items():pin(name,identity)
  old_source=(ROOT/OLD).read_text(encoding='utf8');new_source=(ROOT/NEW).read_text(encoding='utf8');eq0=v13_equivalence((ROOT/BASE).read_text(encoding='utf8'),old_source);eq=equivalence(old_source,new_source);old=module('independent_v13_baseline',ROOT/OLD);new=module('independent_v13_subject',ROOT/NEW);bodies={n.name:n for n in ast.parse(new_source).body if isinstance(n,ast.FunctionDef)};role_dict=next(n for n in ast.walk(bodies['v13_root_role'])if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='exacts'for t in n.targets));need([k.value for k in role_dict.value.keys]==[RANK,CENSUS],'exact two local identity keys');loaded={}
  for path,identity in BINDINGS:
   pin(path,identity);binding=json.loads((ROOT/path).read_bytes());pin(binding['report'],binding['report_sha256']);report=json.loads((ROOT/binding['report']).read_bytes());loaded[binding['id']]=(path,identity,binding,report)
   for name,digest in binding['inputs_sha256'].items():pin(name,digest)
  need(set(loaded)=={LOW,RANK,CENSUS},'exact three requested revisions')
  for cid in (RANK,CENSUS):
   path,identity,b,r=loaded[cid];need(new.v13_root_role(cid,identity,b)is True and old.v13_root_role(cid,identity,b)is True,'positive preserved exact role');new.v13_root_report(cid,b['report_sha256'],b,r);old.v13_root_report(cid,b['report_sha256'],b,r);need(new.v13_root_role(cid+'-OTHER',identity,b)is False and old.v12_root_role(cid,identity,b)is False,'no general or earlier baseline ROOT exception')
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
  low=loaded[LOW];need(low[2]['statement']!=low[3]['statement'],'original editorial strings genuinely differ');mapping=new.v14_lowword_editorial(LOW,low[1],low[2],low[2]['report_sha256'],low[3]);expected_mapping=dict(claim_id=LOW,claim_revision=1,binding_sha256=low[1],report=low[2]['report'],report_sha256=low[2]['report_sha256'],written_derivation='acceleration/audit_20261003_incidence_low_weights_v1_proof.md',written_derivation_sha256='45e3e4fbb8f39547ea169f65ad0df456f09396442fceed23c4483fb9d2be9f4a',original_report_statement=low[3]['statement'],original_report_statement_sha256='2ca15439483a3c908f42f03d4ae88e153bffec5e5546906cff15a7dbb28e8a6e',recorded_binding_statement=low[2]['statement'],recorded_binding_statement_sha256='dc6bf21cf24d90fc2111ee366ac990bbe1437cb51e8e2e2cfaffe5023294a9f4',reason='Exact ROOT-reviewed editorial expansion gives explicit character/zero-word/three-degree convention already proved in the pinned written audit; no semantic inference by registrar and no raw statement overwritten.',mathematical_replays=0);need(mapping==expected_mapping,'exact original-to-recorded editorial mapping');need(new.v14_lowword_editorial(LOW+'-OTHER','f'*64,{},'f'*64,{})is None,'no generic ordinary editorial mapping')
  reject(controls,'editorial_binding_identity','v14 exact editorial binding',lambda:new.v14_lowword_editorial(LOW,'f'*64,low[2],low[2]['report_sha256'],low[3]))
  for field,value in [('revision',True),('claim_revision',2),('status','UNKNOWN'),('review_state','NEEDS_RECHECK'),('kind','exclusion'),('basis',['COMPUTED']),('producer','/root'),('verifier','/root'),('method','repeated_execution'),('dependencies',[dict(id='UNESTABLISHED',revision=1,relation='premise')])]:
   bad=changed(low[2],[field],value);reject(controls,'editorial_role_'+field,'v14 exact ordinary revision roles kind basis method dependencies',lambda bad=bad:new.v14_lowword_editorial(LOW,low[1],bad,bad['report_sha256'],low[3]))
  for fields,value in [(['scope','description'],'Generic weaker code theorem'),(['scope','unrestricted_target'],False),(['scope','target_resolution'],'NONEXISTENCE'),(['target_resolution'],'NONEXISTENCE'),(['premise_state'],'VERIFIED')]:
   bad=changed(low[2],fields,value);reject(controls,'editorial_scope_'+str(fields),'v14 exact conditional editorial scope',lambda bad=bad:new.v14_lowword_editorial(LOW,low[1],bad,bad['report_sha256'],low[3]))
  for which in ('binding','report'):
   bad=changed(low[2]if which=='binding'else low[3],['statement'],(low[2]if which=='binding'else low[3])['statement']+' ');reject(controls,'editorial_'+which+'_statement','v14 exact two editorial statement strings',lambda bad=bad,which=which:new.v14_lowword_editorial(LOW,low[1],bad if which=='binding'else low[2],low[2]['report_sha256'],bad if which=='report'else low[3]))
  for fields,value,stage in [(['written_audit'],'acceleration/unknown.md','v14 exact independent report and written derivation'),(['inputs_sha256','acceleration/audit_20261003_incidence_low_weights_v1_proof.md'],'f'*64,'v14 exact independent report and written derivation'),(['target_lower_word_counts','4'],2080,'v14 exact written theorem outcome and limitations'),(['recorded_validation','complete_pair_inverse_checks'],24,'v14 exact recorded independent finite controls'),(['recorded_validation','finite_controls_are_universal_proof'],True,'v14 exact recorded independent finite controls'),(['inputs_sha256','acceleration/results/20261003_independent_review/incidence_low_weights01/normalized_rows.json'],'f'*64,'v14 exact immutable control and sharp row artifacts')]:
   bad=changed(low[2],fields,value);reject(controls,'editorial_binding_'+str(fields),stage,lambda bad=bad:new.v14_lowword_editorial(LOW,low[1],bad,bad['report_sha256'],low[3]))
  for fields,value,stage in [(['status'],'CANDIDATE','v14 exact written theorem outcome and limitations'),(['producer'],'/root','v14 exact written theorem outcome and limitations'),(['verifier'],'/root','v14 exact written theorem outcome and limitations'),(['universal_derivation_checked'],False,'v14 exact written theorem outcome and limitations'),(['rank_bound_claimed'],True,'v14 exact written theorem outcome and limitations'),(['prior_weight_interval_rederived'],True,'v14 exact written theorem outcome and limitations'),(['new_exclusions'],True,'v14 exact written theorem outcome and limitations'),(['strict_negative_controls'],9,'v14 exact recorded independent finite controls'),(['positive_fixtures'],low[3]['positive_fixtures'][:-1],'v14 exact recorded independent finite controls')]:
   bad=changed(low[3],fields,value);reject(controls,'editorial_report_'+str(fields),stage,lambda bad=bad:new.v14_lowword_editorial(LOW,low[1],low[2],low[2]['report_sha256'],bad))
  # Prior exact permission predicates are genuinely called, while the AST check
  # proves all other old implementation paths remain unchanged.
  for path in ['acceleration/results/20261003_independent_review/incidence_griesmer01/claim_binding.json','acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json']:
   identity=pin(path);b=json.loads((ROOT/path).read_bytes());need(old.v12_root_role(b['id'],identity,b)is True and new.v12_root_role(b['id'],identity,b)is True,'preserved old exact roles')
  for label,modified,diagnostic in [('prior_target_guard',new_source.replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')"),'entire prior V13 executable AST unchanged'),('new_editorial_call',new_source.replace('editorial_statement_mapping = v14_lowword_editorial(cid, expected, binding, report_sha, report)','editorial_statement_mapping = True'),'exact editorial call assignment')]:
   try:equivalence(old_source,modified)
   except AuditError as error:need(str(error)==diagnostic,'precise AST corruption rejection');controls.append(dict(label=label,outcome='REJECTED',diagnostic=str(error)))
   else:raise AuditError('AST_CORRUPTION_ACCEPTED:'+label)
  def dry(subject,label,items):
   need(deadline.status()['remaining_seconds']>20,'not completed within allocation');dest=out/label;argv=sys.argv;replace=os.replace
   def guard(source,target):
    need(Path(target).resolve()==ROOT/'CLAIMS.yaml'and Path(source).resolve()==dest/'CLAIMS.pending.yaml'and(ROOT/'CLAIMS.yaml').read_bytes()==before,'protected exact final atomic replacement');projected_report=copy.deepcopy(sys._getframe(1).f_locals['report']);save(dest/'protected_registration_report.json',dict(atomic_replacement_prevented=True,registration_report=projected_report));barriers.append(dict(label=label,source=str(source),target=str(target),replacement_prevented=True));raise ProtectedLedgerWrite()
   try:
    os.replace=guard;sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',BEFORE]
    for path,identity in items:sys.argv+=['--binding',str(ROOT/path),'--binding-sha256',identity]
    try:subject.main()
    except ProtectedLedgerWrite:pass
    else:raise AuditError('NO_PROTECTED_FINAL_WRITE_BARRIER:'+label)
   finally:os.replace=replace;sys.argv=argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'protected live ledger unchanged');return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text(encoding='utf8'))
  ordinary=copy.deepcopy(low[2]);ordinary['id']='C-ENGINEERING-ONLY-V14-ORDINARY-PROJECTION';ordinary['statement']=low[3]['statement'];op=out/'synthetic_ordinary_binding.json';save(op,ordinary);ordinary_pair=(op.relative_to(ROOT).as_posix(),sha(op));old_projection=dry(old,'ordinary_synthetic_v13',[ordinary_pair]);new_projection=dry(new,'ordinary_synthetic_v14',[ordinary_pair])
  def timeless(value):
   value=copy.deepcopy(value);value.pop('updated_at');value['claims'][-1]['created_at']=value['claims'][-1]['updated_at']=None;return value
  need(timeless(old_projection)==timeless(new_projection),'ordinary independent projection unchanged');after=dry(new,'three_exact_revisions_v14',BINDINGS);original=yaml.safe_load(before)
  need(len(original['claims'])==350 and len(after['claims'])==353 and after['claims'][:350]==original['claims']and after['artifacts'][:len(original['artifacts'])]==original['artifacts']and after['target']==original['target'],'protected exact350to353 prior preservation');appended=after['claims'][350:];need([(c['id'],c['revision'],c['statement'],c['status'],c['review_state'],c['scope'],c['kind'],c['basis'])for c in appended]==[(b['id'],1,b['statement'],'VERIFIED','CLEAR',b['scope'],b['kind'],b['basis'])for _,_,b,_ in (loaded[LOW],loaded[RANK],loaded[CENSUS])],'exact three recorded scope projections');need([c['id']for c in appended]==[LOW,RANK,CENSUS],'lowword premise precedes dependent rank');counts=Counter(c['status']for c in original['claims']);counts['VERIFIED']+=3;need(Counter(c['status']for c in after['claims'])==counts and all(c['review_state']=='CLEAR'for c in after['claims']),'exact protected status counts')
  need(json.loads(appended[0]['unknowns']['editorial_statement_mapping'])==expected_mapping and all('editorial_statement_mapping'not in c['unknowns']for c in appended[1:]),'exactly one claim preserves both raw statements');projected_registration=json.loads((out/'three_exact_revisions_v14/protected_registration_report.json').read_bytes())['registration_report'];need(projected_registration['editorial_statement_mappings']==[expected_mapping]and projected_registration['new_claim_ids']==[LOW,RANK,CENSUS]and projected_registration['claim_records']==353,'exact registration-report editorial mapping');save(out/'checked_editorial_statement_mapping.json',expected_mapping)
  for label,binding,diagnostic in [('wrong_exact_statement',changed(rank[2],['statement'],'General target nonexistence'),'v13 exact binding identity'),('unapproved_ROOT',changed(rank[2],['id'],'C-UNAPPROVED-GENERIC-ROOT'),'separate checking identity for the exact recorded discovery'),('unrelated_ordinary_statement',changed(ordinary,['statement'],'General target nonexistence'),'exact recorded statement')]:
   path=out/(label+'.json');save(path,binding);argv=sys.argv
   try:sys.argv=[str(ROOT/NEW),'--out',str(out/(label+'_main')),'--previous-sha256',BEFORE,'--binding',str(path),'--binding-sha256',sha(path)];reject(controls,label+'_real_main',diagnostic,new.main)
   finally:sys.argv=argv
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(index)==index_before,'live350 ledger/index unchanged at completion');save(out/'controls.json',controls)
  report=dict(status='INDEPENDENT_REGISTRAR_V14_EXACT_EDITORIAL_ADAPTER_ENGINEERING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/structural',producer='/root/checkpoint_audit',method='independent_engineering_artifact_check',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,before_ledger_sha256=BEFORE,index_before_sha256=index_before,index_after_sha256=sha(index),source_equivalence=eq,prior_V12_V13_source_equivalence=eq0,positive_exact_adapters=2,exact_editorial_mapping=expected_mapping,ordinary_synthetic_V13_V14_projection_equal=True,protected_transition=dict(claims_before=350,claims_after=353,new_exact_ids=[c['id']for c in appended],prior_claims_artifacts_target_unchanged=True,new_finite_exclusion_kind_claims=1,new_unrestricted_exclusion_claims=0,status_counts=dict(counts),review_state_counts={'CLEAR':353}),strict_negative_controls=len(controls),controls=controls,protected_write_barriers=barriers,ledger_mutated=False,index_mutated=False,mathematical_replays=0,scientific_launched=False,target_resolution='UNKNOWN',shared_components=['Prior independently authored V12 engineering source used as disclosed algorithm/template evidence; V13-specific controls and exact AST normalization newly authored.','Registrar modules imported as engineering subjects only; mathematical producer/checker computations not imported or reexecuted.','Existing registry YAML/schema/serialization and supported deadline helpers used in protected projections.'],limitations=['No actual registration, mathematics reapproval, PUBLIC promotion or target resolution. Synthetic ordinary projection remains audit-only.','Only exact two ROOT binding adapters added; unknown ROOT IDs still rejected.','One fixed labelled-move exclusion-kind claim is separate from zero unrestricted target exclusions.','Protected atomic replacement interception prevents live ledger write; pending YAML/control artifacts remain only below this audit output.'],elapsed_seconds=time.monotonic()-started,deadline=deadline.status());save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),strict_negative_controls=len(controls),elapsed_seconds=report['elapsed_seconds'])))
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,completed_controls=controls,ledger_unchanged=(ROOT/'CLAIMS.yaml').read_bytes()==before,index_unchanged=sha(index)==index_before,outputs_preserved=True,mathematical_replays=0,scientific_launched=False,deadline=deadline.status()));raise
if __name__=='__main__':main()
