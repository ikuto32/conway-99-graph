"""Independent exact V15 registrar metadata audit; protected copies, no mathematics."""
import argparse, ast, copy, hashlib, importlib.util, json, os, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v14.py'
NEW = 'acceleration/register_20261003_bound_claims_v15.py'
SPEC = 'acceleration/audit_20261003_registrar_v15_engineering_v1_spec.md'
N5 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT'
PILOT = 'C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS'
RANK = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86'
BINDINGS = [
 ('acceleration/results/20261003_triangle_image_weight5_binding01/claim_binding_schema2.json', 'e816aff2942094e61efc2652acc222fa5de8f60b9b2435c81750a4ba19e65ea7'),
 ('acceleration/results/20261003_root_focused_pilot_binding01/claim_binding_schema2.json', 'b160388913cc014a2ea1d8a407a150e657078cd9c81ad6333378eac633c4de2f'),
 ('acceleration/results/20261003_triangle_rank86_binding01/claim_binding_schema2.json', '5d1aa5266a8dd3aaee40e8bdb4f8c10c2093d92969c1f29bdb03587080cec831')]
PINS = {
 OLD: '6cf12f3dcb3b1e95d692d773df9e266c73101ce6ed0e9bebba0e79d00669c79b',
 NEW: '0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9',
 'acceleration/register_20261003_bound_claims_v15_spec.md': '4b3998133dde62d10bfdd36d53377b66bebefd095905805d5ae19214c8f954b2',
 'acceleration/calibrate_20261003_registrar_v15_helpers_v1.py': '73e96050b61054f03f264911473c6f3635fb623cb39f646df9c07a0b189f08cf',
 'acceleration/calibrate_20261003_registrar_v15_helpers_v1_spec.md': 'dee0dcbade8b704fd98513e6df3980aade8f1e16c994149b2a8f95f018135ce4',
 'acceleration/results/20261003_registrar_v15_helpers01/summary.json': '3fa624266a6228e98ff3d94f975f41d46ca44c717efd5cdc1883e14f1917e1ee',
 'acceleration/results/20261003_registrar_v15_helpers_supervision01/summary.json': 'e30f97c18d6bb5e372cf9f173419de439d763b5d59937e28e32a76fb03269ca2',
 'acceleration/audit_20261003_registrar_v14_engineering_v2.py': '2fbf9131c6f64da384cc59b01c5a19774ab77fd23cbadaf0ba831d95c90844b9',
 'acceleration/audit_20261003_registrar_v14_engineering_v2_spec.md': '1d91ca8fec650996f260e6ef77f6ed0ad6fca2a49a77b56e648cd4c1e9c12e44'}
BEFORE = '4b64876083f128382f48335a9b7e3cec08c56e0c1eb90aa24461901860e848da'
INDEX = '709d1d0b6cfbdc69214c996c440e86e373d719bdb2a918b49303c7edbcf3e3d1'

class AuditError(ValueError): pass
class ProtectedLedgerWrite(RuntimeError): pass
def need(ok, message):
 if not ok: raise AuditError(message)
def sha(path):
 with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(path, value):
 with path.open('x', encoding='utf8', newline='\n') as stream:
  json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')
def typed(left, right):
 if type(left) is not type(right): return False
 if type(left) is dict: return set(left)==set(right) and all(typed(left[k],right[k]) for k in left)
 if type(left) in (list, tuple): return len(left)==len(right) and all(typed(a,b) for a,b in zip(left,right))
 return left==right
def changed(value, path, replacement):
 value=copy.deepcopy(value); node=value
 for key in path[:-1]: node=node[key]
 node[path[-1]]=replacement; return value
def load_module(name, path):
 spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
def dump(node): return ast.dump(node, include_attributes=False)

def equivalence(old_source, new_source):
 old=ast.parse(old_source); new=ast.parse(new_source); removed=[]; body=[]
 for node in new.body:
  if isinstance(node,ast.FunctionDef) and node.name in {'v15_same','v15_role','v15_report'}: removed.append(node.name)
  elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='V15_EXACT':
   need(isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='json.loads' and len(node.value.args)==1 and isinstance(node.value.args[0],ast.Constant) and type(node.value.args[0].value)is str,'exact JSON config assignment'); removed.append('V15_EXACT')
  else: body.append(node)
 need(sorted(removed)==['V15_EXACT','v15_report','v15_role','v15_same'],'exact four added top-level nodes'); new.body=body
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 newmain=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 message='separate checking identity for the exact recorded discovery'
 oldguard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message)
 extended=copy.deepcopy(oldguard); extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v15',ctx=ast.Load()))
 mapping_if=ast.parse("if wave40_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v15 disjoint editorial adapter')\n editorial_statement_mapping = wave40_statement_mapping").body[0]
 edits=[]
 class Restore(ast.NodeTransformer):
  def visit_Assign(self,node):
   if any(isinstance(t,ast.Name) and t.id=='exact_v15' for t in node.targets):
    need(ast.unparse(node)=='exact_v15 = v15_role(cid, expected, binding)','exact role call insertion'); edits.append('role_call'); return None
   if any(isinstance(t,ast.Name) and t.id=='wave40_statement_mapping' for t in node.targets):
    need(ast.unparse(node)=='wave40_statement_mapping = v15_report(cid, report_sha, binding, report)','exact report call insertion'); edits.append('report_call'); return None
   return self.generic_visit(node)
  def visit_If(self,node):
   if ast.unparse(node.test)=='wave40_statement_mapping is not None':
    need(dump(node)==dump(mapping_if),'exact disjoint editorial dispatcher'); edits.append('editorial_dispatch'); return None
   return self.generic_visit(node)
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value==message:
    need(dump(node)==dump(extended),'exact one new role alternative'); edits.append('role_alternative'); return copy.deepcopy(oldguard)
   return self.generic_visit(node)
 Restore().visit(newmain)
 need(sorted(edits)==['editorial_dispatch','report_call','role_alternative','role_call'],'exact four main insertions')
 need(dump(old)==dump(new),'complete V14 executable AST preserved')
 return dict(removed_top_level_nodes=removed,removed_main_insertions=edits,entire_V14_AST_restored=True)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seconds',type=float,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
 start=time.monotonic(); deadline=CommandDeadline(args.seconds,allocation_reason='New independent V15 finite metadata and protected353to356 gate; analogous full V14 about26s;150worker with20save reserve;no mathematics or live mutations')
 out=args.out.resolve(); need(out.is_relative_to(ROOT),'bounded output'); out.mkdir(parents=True,exist_ok=False)
 before=(ROOT/'CLAIMS.yaml').read_bytes(); index=ROOT/'.git/index'; index_before=sha(index); pins={}; controls=[]; barriers=[]; mappings=[]
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>20,'not completed within allocated budget'); path=(ROOT/name).resolve(); need(path.is_relative_to(ROOT),'bounded input '+name)
  actual=sha(path); need(wanted is None or actual==wanted,'exact input '+name); need(name not in pins or pins[name]==actual,'stable input '+name); pins[name]=actual; return actual
 def reject(label,diagnostic,callback):
  try: callback()
  except ValueError as error:
   need(type(error)is ValueError and str(error)==diagnostic,'precise rejection '+label+' received '+repr(error)); controls.append(dict(label=label,outcome='REJECTED',diagnostic=diagnostic)); return
  raise AuditError('CORRUPTION_ACCEPTED:'+label)
 try:
  need(hashlib.sha256(before).hexdigest()==BEFORE and index_before==INDEX,'exact353 ledger and index baseline')
  for name in [Path(__file__).relative_to(ROOT).as_posix(),SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','uv.lock','pyproject.toml']: pin(name)
  for name,wanted in PINS.items(): pin(name,wanted)
  author=json.loads((ROOT/'acceleration/results/20261003_registrar_v15_helpers01/summary.json').read_bytes())
  need(author['positive_controls']==10 and author['strict_negative_controls']==99 and author['registrar_main_called']is False and author['independent_approval']is False,'author finite helper scope only')
  receipt=json.loads((ROOT/'acceleration/results/20261003_registrar_v15_helpers_supervision01/summary.json').read_bytes())
  need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped']is True and receipt['cleanup']['job_active_zero_observed']is True and receipt['cleanup']['cleanup_errors']==[],'actual terminal author helper receipt')
  old_source=(ROOT/OLD).read_text(encoding='utf8'); new_source=(ROOT/NEW).read_text(encoding='utf8'); eq=equivalence(old_source,new_source)
  old=load_module('independent_v15_old',ROOT/OLD); new=load_module('independent_v15_subject',ROOT/NEW); loaded={}
  need(list(new.V15_EXACT)==[N5,PILOT,RANK],'exact three config identities and order')
  for path,identity in BINDINGS:
   pin(path,identity); binding=json.loads((ROOT/path).read_bytes()); cid=binding['id']; pin(binding['report'],binding['report_sha256']); report=json.loads((ROOT/binding['report']).read_bytes()); loaded[cid]=(path,identity,binding,report)
   for name,wanted in binding['inputs_sha256'].items(): pin(name,wanted)
   expected={key:binding.get(key) for key in ['id','kind','basis','method','producer','verifier','scope','dependencies','report','report_sha256','controls','pre_output_calibration','written_audit','recorded_validation','target_resolution','premise_state']}
   expected.update(binding_path=path,binding_sha256=identity,statement_sha256=hashlib.sha256(binding['statement'].encode('utf8')).hexdigest(),written_audit_sha256=binding['inputs_sha256'].get(binding.get('written_audit')))
   if cid==RANK: expected['exact_certificate']=binding['exact_certificate']
   need(typed(new.V15_EXACT[cid],expected),'config independently agrees with exact frozen binding metadata '+cid)
  need(loaded[N5][2]['producer']=='/root/structural' and loaded[N5][2]['verifier']=='/root/checkpoint_audit' and loaded[PILOT][2]['producer']=='/root/native_driver' and loaded[PILOT][2]['verifier']=='/root/checkpoint_audit' and loaded[RANK][2]['producer']=='/root/structural' and loaded[RANK][2]['verifier']=='/root','exact separate discovery and checking roles')
  need(new.v15_role('C-UNAPPROVED-ROOT','f'*64,{})is False and new.v15_report('C-UNAPPROVED-ROOT','f'*64,{},{})is None,'unknown identity has no overrides')
  for left,right,wanted in [({'a':[1,False]},{'a':[1,False]},True),({'a':1},{'a':True},False),([1],[1.0],False),({'a':0},{'a':False},False),({'a':1},{'a':1,'b':2},False),([1,2],[2,1],False),((1,),[1],False)]:
   need(new.v15_same(left,right)is wanted,'typed equality independent controls')
  for cid in [N5,PILOT,RANK]:
   path,identity,b,r=loaded[cid]; need(new.v15_role(cid,identity,b)is True,'exact new adapter role'); mapped=new.v15_report(cid,b['report_sha256'],b,r)
   if cid==N5: need(mapped is None and b['statement']==r['statement'],'N5 ordinary statement remains identical')
   else:
    need('statement'not in r and mapped['claim_id']==cid and mapped['original_report_statement']is None and mapped['original_report_statement_null_reason'] and mapped['recorded_binding_statement']==b['statement'] and mapped['recorded_binding_sha256']==identity and mapped['mathematical_replays']==0 and mapped['target_resolution']=='NONE','exact absent-statement projection'); mappings.append(mapped)
   reject(cid+':hash','v15 exact frozen binding identity',lambda:new.v15_role(cid,'f'*64,b))
   for field,value in [('id',cid+'-OTHER'),('revision',2),('revision',True),('claim_revision',1.0),('status','UNKNOWN'),('review_state','NEEDS_RECHECK'),('producer',b['verifier']),('verifier','/root/unapproved'),('method','repeated_execution'),('kind','exclusion'),('basis',['CITED'])]:
    bad=changed(b,[field],value); reject(cid+':'+field+repr(value),'v15 exact revision status independent roles method kind basis',lambda bad=bad:new.v15_role(cid,identity,bad))
   for keys,value in [(['scope','description'],'All graphs'),(['scope','unrestricted_target'],int(b['scope']['unrestricted_target'])),(['scope','target_resolution'],'NONEXISTENCE'),(['dependencies'],[dict(id='UNESTABLISHED',revision=1,relation='premise')]),(['target_resolution'],'NONEXISTENCE'),(['premise_state'],'VERIFIED')]:
    bad=changed(b,keys,value); reject(cid+':scope'+str(keys),'v15 exact conditional or finite scope dependencies and unresolved target',lambda bad=bad:new.v15_role(cid,identity,bad))
   for key,value in [('statement',b['statement']+' '),('report','other.json'),('report_sha256','f'*64),('verification_records',[])]:
    bad=changed(b,[key],value); reject(cid+':primary'+key,'v15 exact primary report statement and no legacy fallback',lambda bad=bad:new.v15_role(cid,identity,bad))
   reject(cid+':report_hash','v15 exact independent report roles and identity',lambda:new.v15_report(cid,'f'*64,b,r))
   for key,value in [('producer','/root/unapproved'),('verifier',b['producer']),('method','repeated_execution'),('target_resolution','NONEXISTENCE')]:
    bad=changed(r,[key],value); reject(cid+':report'+key,'v15 exact independent report roles and identity',lambda bad=bad:new.v15_report(cid,b['report_sha256'],b,bad))
   bad=changed(b,['controls'],{}); reject(cid+':controls','v15 exact recorded control references',lambda:new.v15_report(cid,b['report_sha256'],bad,r))
  n5=loaded[N5]; pilot=loaded[PILOT]; rank=loaded[RANK]
  def report_cases(record,cases,diagnostic):
   cid=record[2]['id']; b,r=record[2:]
   for keys,value in cases:
    bad=changed(r,keys,value); reject(cid+':result'+str(keys)+repr(value),diagnostic,lambda bad=bad:new.v15_report(cid,b['report_sha256'],b,bad))
  def binding_cases(record,cases,diagnostic):
   cid=record[2]['id']; b,r=record[2:]
   for keys,value in cases:
    bad=changed(b,keys,value); reject(cid+':detail'+str(keys)+repr(value),diagnostic,lambda bad=bad:new.v15_report(cid,b['report_sha256'],bad,r))
  report_cases(n5,[(['status'],'CANDIDATE'),(['statement'],n5[2]['statement']+' '),(['universal_derivation_checked'],False),(['rank_bound_claimed'],True),(['new_exclusions'],False),(['new_exclusions'],1),(['target_unordered_paths'],24947),(['target_weight5_lower_count'],22869)],'v15 exact N5 universal derivation and necessary count only')
  binding_cases(n5,[(['recorded_validation','target_weight5_lower_count'],22869),(['written_audit'],'other.md')],'v15 exact N5 recorded derivation')
  report_cases(rank,[(['status'],'CANDIDATE'),(['weight_domain'],'divisible4_seven'),(['optimum_asserted'],True),(['exact_size_upper'],[97502465,9739]),(['complete_exact_coefficients_checked'],1286),(['complete_nonnegative_dual_coordinates_checked'],98),(['complete_exact_weight_inequalities_checked'],True),(['maximum_linear_dimension'],12),(['conditional_incidence_rank_lower'],87),(['actual_strict_corruption_controls'],9),(['lower_word_counts','5'],22869)],'v15 exact even13 conditional rank86 full certificate')
  binding_cases(rank,[(['exact_certificate','upper'],[1,1]),(['exact_certificate','optimum_asserted'],True),(['written_audit_sha256'],'f'*64)],'v15 exact conditional rank certificate and written derivation')
  binding_cases(rank,[(['supplemental_verification_records',0,'claim_revision'],True),(['supplemental_verification_records',0,'verifier'],'/root/structural'),(['supplemental_verification_records',0,'outcome'],'UNKNOWN')],'v15 exact rank revision-bound supplemental provenance')
  report_cases(pilot,[(['status'],'CANDIDATE'),(['complete_trajectory_checked'],True),(['saved_state_files'],101),(['saved_states'],102),(['saved_trace_records'],10098),(['complete_anchored_proposals'],10098),(['locally_checked_global_gaps'],1),(['saved_selected_object_files'],1),(['saved_localzero_object_observations'],1),(['zero_target_candidates'],1),(['native_reported_proposals'],True)],'v15 exact pilot saved-object and stored-proposal population')
  binding_cases(pilot,[(['recorded_validation','current','E_mu'],5475),(['recorded_validation','best_root','Rroot'],0),(['recorded_validation','complete_trajectory_checked'],True)],'v15 exact saved current best object statement fields')
  for record in [pilot,rank]: report_cases(record,[(['statement'],record[2]['statement'])],'v15 absent original report statement remains absent')
  for record in [n5,rank]:
   b,r=record[2:]; path=b['written_audit']; bad=changed(b,['inputs_sha256',path],'f'*64); reject(record[2]['id']+':proof_pin','v15 exact source proof control or raw artifact',lambda bad=bad,b=b,r=r:new.v15_report(b['id'],b['report_sha256'],bad,r))
  # Preserve and exercise the preexisting ordinary editorial path, without granting a new role.
  legacy_path='acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json'; legacy_sha=pin(legacy_path,'40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05'); legacy=json.loads((ROOT/legacy_path).read_bytes()); pin(legacy['report'],legacy['report_sha256']); legacy_report=json.loads((ROOT/legacy['report']).read_bytes())
  need(typed(old.v14_lowword_editorial(legacy['id'],legacy_sha,legacy,legacy['report_sha256'],legacy_report),new.v14_lowword_editorial(legacy['id'],legacy_sha,legacy,legacy['report_sha256'],legacy_report)),'old exact editorial path unchanged')
  for label,bad_source,message in [
   ('changed_old_target_guard',new_source.replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')"),'complete V14 executable AST preserved'),
   ('changed_new_role_call',new_source.replace('exact_v15 = v15_role(cid, expected, binding)','exact_v15 = True'),'exact role call insertion'),
   ('changed_mapping_dispatch',new_source.replace("need(editorial_statement_mapping is None, 'v15 disjoint editorial adapter')","need(True, 'v15 disjoint editorial adapter')"),'exact disjoint editorial dispatcher')]:
   try: equivalence(old_source,bad_source)
   except AuditError as error: need(str(error)==message,'precise AST veto'); controls.append(dict(label=label,outcome='REJECTED',diagnostic=message))
   else: raise AuditError('AST_CORRUPTION_ACCEPTED:'+label)
  def dry(subject,label,items):
   need(deadline.status()['remaining_seconds']>20,'not completed within allocated budget'); dest=out/label; original_argv=sys.argv; original_replace=os.replace
   def guard(source,target):
    need(Path(target).resolve()==ROOT/'CLAIMS.yaml' and Path(source).resolve()==dest/'CLAIMS.pending.yaml' and (ROOT/'CLAIMS.yaml').read_bytes()==before,'exact protected final replacement')
    report=copy.deepcopy(sys._getframe(1).f_locals['report']); save(dest/'protected_registration_report.json',dict(atomic_replacement_prevented=True,registration_report=report)); barriers.append(dict(label=label,replacement_prevented=True)); raise ProtectedLedgerWrite()
   try:
    os.replace=guard; sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',BEFORE]
    for path,identity in items: sys.argv+=['--binding',str(ROOT/path),'--binding-sha256',identity]
    try: subject.main()
    except ProtectedLedgerWrite: pass
    else: raise AuditError('NO_PROTECTED_WRITE_BARRIER:'+label)
   finally: os.replace=original_replace; sys.argv=original_argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'live ledger unchanged'); return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text(encoding='utf8'))
  ordinary=copy.deepcopy(n5[2]); ordinary['id']='C-ENGINEERING-ONLY-V15-ORDINARY-PROJECTION'; ordinary_path=out/'ordinary_synthetic_binding.json'; save(ordinary_path,ordinary); pair=(ordinary_path.relative_to(ROOT).as_posix(),sha(ordinary_path))
  old_projection=dry(old,'ordinary_V14',[pair]); new_projection=dry(new,'ordinary_V15',[pair])
  def timeless(value):
   value=copy.deepcopy(value); value.pop('updated_at'); value['claims'][-1]['created_at']=value['claims'][-1]['updated_at']=None; return value
  need(typed(timeless(old_projection),timeless(new_projection)),'old ordinary registration behavior unchanged')
  after=dry(new,'three_exact_bindings_V15',BINDINGS); original=yaml.safe_load(before); need(len(original['claims'])==353 and len(after['claims'])==356,'exact protected353to356')
  need(typed(after['claims'][:353],original['claims']) and typed(after['artifacts'][:len(original['artifacts'])],original['artifacts']) and typed(after['target'],original['target']),'all prior claims artifacts target unchanged')
  appended=after['claims'][353:]; need([c['id']for c in appended]==[N5,PILOT,RANK],'exact dependency order')
  for claim,record in zip(appended,[n5,pilot,rank]):
   b=record[2]; need(typed({key:claim[key]for key in ['id','revision','statement','kind','basis','status','review_state','scope','assumptions','limitations']},{key:b[key]for key in ['id','revision','statement','kind','basis','status','review_state','scope','assumptions','limitations']}),'literal scoped new claim projection')
   need(typed(claim['dependencies'],[{key:d[key]for key in ['id','revision','relation']}for d in b['dependencies']]),'literal dependency projection')
   v=claim['verification'][0]; need(v['verifier']==b['verifier'] and v['method']==b['method'] and v['command_or_audit']==b['report'] and v['claim_revision']==1,'revision-specific provenance projection')
  counts=Counter(c['status']for c in original['claims']); counts['VERIFIED']+=3; need(Counter(c['status']for c in after['claims'])==counts and all(c['review_state']=='CLEAR'for c in after['claims']),'exact status totals')
  need('editorial_statement_mapping'not in appended[0]['unknowns'] and [json.loads(c['unknowns']['editorial_statement_mapping'])for c in appended[1:]]==mappings,'only two absent raw statement mappings preserved')
  protected=json.loads((out/'three_exact_bindings_V15/protected_registration_report.json').read_bytes())['registration_report']; need(protected['editorial_statement_mappings']==mappings and protected['new_claim_ids']==[N5,PILOT,RANK] and protected['claim_records']==356,'actual copied end-to-end report metadata')
  for label,binding,diagnostic in [('unknown_ROOT',changed(rank[2],['id'],'C-UNAPPROVED-GENERIC-ROOT'),'separate checking identity for the exact recorded discovery'),('changed_exact_statement',changed(rank[2],['statement'],'Unrestricted nonexistence'),'v15 exact frozen binding identity'),('unrelated_ordinary_statement',changed(ordinary,['statement'],'Unrestricted nonexistence'),'exact recorded statement')]:
   path=out/(label+'.json'); save(path,binding); original_argv=sys.argv
   try: sys.argv=[str(ROOT/NEW),'--out',str(out/(label+'_main')),'--previous-sha256',BEFORE,'--binding',str(path),'--binding-sha256',sha(path)]; reject(label+'_actual_main',diagnostic,new.main)
   finally: sys.argv=original_argv
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(index)==index_before,'live ledger index unchanged on completion'); save(out/'controls.json',controls); save(out/'checked_statement_mappings.json',mappings)
  result=dict(status='INDEPENDENT_REGISTRAR_V15_EXACT_THREE_BINDINGS_ENGINEERING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/structural',producer='/root/native_driver',method='independent_engineering_artifact_check',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=pins,source_AST_restoration=eq,exact_positive_adapter_pairs=3,ordinary_V14_V15_projection_equal=True,strict_negative_controls=len(controls),protected_write_barriers=barriers,protected_transition=dict(claims_before=353,claims_after=356,new_ids=[N5,PILOT,RANK],prior_claims_artifacts_target_unchanged=True,status_counts=dict(counts),review_state_counts={'CLEAR':356},new_finite_exclusions=0,new_unrestricted_exclusions=0),before_ledger_sha256=BEFORE,index_before_sha256=index_before,index_after_sha256=sha(index),editorial_statement_mappings=mappings,ledger_mutated=False,index_mutated=False,mathematical_replays=0,scientific_launched=False,target_resolution='UNKNOWN',shared_components=['Preserved independently authored V14 engineering template supplies protected atomic-write interception and ordinary-projection comparison. V15-specific AST/config/mutation controls newly authored.','Registrar modules imported as engineering subjects only; mathematical discovery/verifier computations are not imported or rerun.','Existing YAML/schema validator, exact evidence files and supported deadline helpers are trusted shared components.'],limitations=['Only three frozen metadata identities admitted, including one exact ROOT-verifier identity; no generic ROOT role or statement semantic matcher.','Hashing prior evidence is identity checking, not mathematical reapproval or external review.','Two copied projections and one three-binding copied projection never replace the live ledger.','No current proof of target existence/nonexistence; cumulative finite and unrestricted exclusion counts are not inferred from this engineering gate.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
  save(out/'summary.json',result); print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),strict_negative_controls=len(controls),elapsed_seconds=result['elapsed_seconds'])))
 except BaseException as error:
  save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,completed_controls=controls,ledger_unchanged=(ROOT/'CLAIMS.yaml').read_bytes()==before,index_unchanged=sha(index)==index_before,outputs_preserved=True,mathematical_replays=0,scientific_launched=False,deadline=deadline.status())); raise

if __name__=='__main__': main()
