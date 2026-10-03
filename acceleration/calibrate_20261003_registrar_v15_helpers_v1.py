"""Same-author V15 exact metadata/AST controls; no main or outcome approval."""
import argparse,ast,copy,hashlib,importlib.util,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v14.py'
OLD_SHA='6cf12f3dcb3b1e95d692d773df9e266c73101ce6ed0e9bebba0e79d00669c79b'
NEW='acceleration/register_20261003_bound_claims_v15.py'
NEW_SHA='0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9'
SPEC='acceleration/register_20261003_bound_claims_v15_spec.md'
SPEC_SHA='4b3998133dde62d10bfdd36d53377b66bebefd095905805d5ae19214c8f954b2'
def need(ok,message):
 if not ok:raise ValueError(message)
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True);a=p.parse_args()
 d=CommandDeadline(a.seconds,allocation_reason='Same-author V15 helpers/typed metadata/complete V14AST only; no main or mathematical replay;20save reserve')
 start=time.monotonic();out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT)and not out.exists(),'fresh boundedoutput');out.mkdir(parents=True);pins={};cases=[];mappings=[]
 def pin(name,identity=None):
  need(not d.status()['stop_required']and d.status()['remaining_seconds']>20,'metadata deadline')
  with(ROOT/name).open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  need(identity is None or h==identity,'exact input '+name);pins[name]=h;return h
 def read(name,identity=None):pin(name,identity);return json.loads((ROOT/name).read_bytes())
 def reject(label,diag,call):
  try:call()
  except ValueError as e:need(str(e)==diag,'precise failure '+label+': '+str(e));cases.append(dict(case=label,outcome='REJECTED',diagnostic=diag));return
  raise ValueError('unexpected acceptance '+label)
 try:
  ledger=pin('CLAIMS.yaml');index=pin('.git/index');pin(OLD,OLD_SHA);pin(NEW,NEW_SHA);pin(SPEC,SPEC_SHA)
  for file in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/calibrate_20261003_registrar_v15_helpers_v1_spec.md','acceleration/register_20261003_bound_claims_v14_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(file)
  old=ast.parse((ROOT/OLD).read_text(encoding='utf-8-sig'));new=ast.parse((ROOT/NEW).read_text(encoding='utf-8-sig'))
  olddefs={n.name for n in old.body if isinstance(n,ast.FunctionDef)};newdefs={n.name for n in new.body if isinstance(n,ast.FunctionDef)}
  need(newdefs-olddefs=={'v15_same','v15_role','v15_report'}and olddefs<=newdefs,'exact three new definitions')
  class Restore(ast.NodeTransformer):
   def visit_FunctionDef(self,node):
    if node.name in {'v15_same','v15_role','v15_report'}:return None
    return self.generic_visit(node)
   def visit_Assign(self,node):
    if any(isinstance(t,ast.Name)and t.id in {'V15_EXACT','exact_v15','wave40_statement_mapping'}for t in node.targets):return None
    return self.generic_visit(node)
   def visit_If(self,node):
    if isinstance(node.test,ast.Compare)and isinstance(node.test.left,ast.Name)and node.test.left.id=='wave40_statement_mapping':return None
    return self.generic_visit(node)
   def visit_BoolOp(self,node):
    node.values=[value for value in node.values if not(isinstance(value,ast.Name)and value.id=='exact_v15')];return self.generic_visit(node)
  need(ast.dump(Restore().visit(copy.deepcopy(new)),include_attributes=False)==ast.dump(old,include_attributes=False),'complete V14 AST preservation')
  cases.append(dict(case='complete_V14_AST_preserved',outcome='PASS'))
  spec=importlib.util.spec_from_file_location('author_v15',ROOT/NEW);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  need(m.v15_role('C-UNKNOWN','0'*64,{})is False and m.v15_report('C-UNKNOWN','0'*64,{},{})is None,'no generic adapter');cases.append(dict(case='unknown_id_no_override',outcome='PASS'))
  need(m.v15_same({'a':[1,False]},{'a':[1,False]})and not m.v15_same({'a':1},{'a':True})and not m.v15_same([1],[1.0]),'strict typed metadata');cases.append(dict(case='typed_equal_positive_and_numeric_vetoes',outcome='PASS'))
  for cid,exact in m.V15_EXACT.items():
   b=read(exact['binding_path'],exact['binding_sha256']);r=read(exact['report'],exact['report_sha256'])
   for c in exact['controls'].values():
    if type(c)is dict and c.get('sha256')and(c.get('path')or c.get('report')):pin(c.get('path',c.get('report')),c['sha256'])
   if exact['written_audit']:pin(exact['written_audit'],exact['written_audit_sha256'])
   need(m.v15_role(cid,exact['binding_sha256'],b)is True,'exact new role');cases.append(dict(case=cid+'_role',outcome='PASS'))
   mapped=m.v15_report(cid,exact['report_sha256'],b,r)
   if cid.endswith('WEIGHT5-PATH-IMAGE-LOWER-COUNT'):need(mapped is None and r['statement']==b['statement'],'N5 preserved ordinary literal path')
   else:need(mapped['original_report_statement']is None and mapped['original_report_statement_null_reason']and mapped['recorded_binding_statement']==b['statement']and mapped['mathematical_replays']==0,'exact no-headline projection');mappings.append(mapped)
   cases.append(dict(case=cid+'_report',outcome='PASS'))
   def bad_binding(label,diag,change,report_mode=False):
    bad=copy.deepcopy(b);change(bad)
    reject(cid+'_'+label,diag,lambda:m.v15_report(cid,exact['report_sha256'],bad,r)if report_mode else m.v15_role(cid,exact['binding_sha256'],bad))
   def bad_report(label,diag,change):
    bad=copy.deepcopy(r);change(bad);reject(cid+'_'+label,diag,lambda:m.v15_report(cid,exact['report_sha256'],b,bad))
   reject(cid+'_binding_hash','v15 exact frozen binding identity',lambda:m.v15_role(cid,'0'*64,b))
   diag='v15 exact revision status independent roles method kind basis'
   for label,change in [('revision',lambda x:x.update(revision=2)),('boolrevision',lambda x:x.update(revision=True)),('boolclaimrevision',lambda x:x.update(claim_revision=True)),('status',lambda x:x.update(status='CANDIDATE')),('quarantine',lambda x:x.update(review_state='QUARANTINED')),('selfapproval',lambda x:x.update(producer=x['verifier'])),('wrongverifier',lambda x:x.update(verifier='/root'if x['verifier']!='/root'else'/root/checkpoint_audit')),('method',lambda x:x.update(method='repeated_execution')),('kind',lambda x:x.update(kind='exclusion')),('basis',lambda x:x.update(basis=['CITED']))]:bad_binding(label,diag,change)
   diag='v15 exact conditional or finite scope dependencies and unresolved target'
   for label,change in [('broadscope',lambda x:x['scope'].update(description='All graphs')),('boolscope',lambda x:x['scope'].update(unrestricted_target=int(x['scope']['unrestricted_target']))),('targetpromotion',lambda x:x.update(target_resolution='NONEXISTENT')),('dependency',lambda x:x['dependencies'].append(dict(id='C-UNRELATED',revision=1,relation='premise')))]:bad_binding(label,diag,change)
   diag='v15 exact primary report statement and no legacy fallback'
   for label,change in [('statement',lambda x:x.update(statement=x['statement']+' broader')),('reportpath',lambda x:x.update(report='other.json')),('reporthash',lambda x:x.update(report_sha256='0'*64)),('legacyrecords',lambda x:x.update(verification_records=[dict(report='legacy')]))]:bad_binding(label,diag,change)
   bad_binding('controls','v15 exact recorded control references',lambda x:x['controls'].update(illegal=True),True)
   for label,change in [('reportproducer',lambda x:x.update(producer='/root/other')),('reportverifier',lambda x:x.update(verifier='/root/other')),('reportmethod',lambda x:x.update(method='repeated_execution')),('reporttarget',lambda x:x.update(target_resolution='NONEXISTENT'))]:bad_report(label,'v15 exact independent report roles and identity',change)
   reject(cid+'_report_identity','v15 exact independent report roles and identity',lambda:m.v15_report(cid,'0'*64,b,r))
   if cid.endswith('WEIGHT5-PATH-IMAGE-LOWER-COUNT'):
    diag='v15 exact N5 universal derivation and necessary count only'
    for label,change in [('headline',lambda x:x.update(statement='Unconditional solution')),('universal',lambda x:x.update(universal_derivation_checked=False)),('rankpromotion',lambda x:x.update(rank_bound_claimed=True)),('exclusions',lambda x:x.update(new_exclusions=1)),('boolzero',lambda x:x.update(new_exclusions=False)),('lowercount',lambda x:x.update(target_weight5_lower_count=22869))]:bad_report(label,diag,change)
    bad_binding('N5recordedcount','v15 exact N5 recorded derivation',lambda x:x['recorded_validation'].update(target_weight5_lower_count=22869),True)
   elif cid.endswith('BINARY-RANK-LOWER86'):
    diag='v15 exact even13 conditional rank86 full certificate'
    for label,change in [('weightdomain',lambda x:x.update(weight_domain='quarter7')),('optimum',lambda x:x.update(optimum_asserted=True)),('fraction',lambda x:x.update(exact_size_upper=[97502465,9739])),('rank',lambda x:x.update(conditional_incidence_rank_lower=87)),('boolrows',lambda x:x.update(complete_exact_weight_inequalities_checked=True)),('N5strengthening',lambda x:x['lower_word_counts'].update({'5':22869}))]:bad_report(label,diag,change)
    bad_binding('certificate','v15 exact conditional rank certificate and written derivation',lambda x:x['exact_certificate'].update(upper=[1,1]),True)
    bad_binding('supplementalrevision','v15 exact rank revision-bound supplemental provenance',lambda x:x['supplemental_verification_records'][0].update(claim_revision=True),True)
    bad_report('inventedheadline','v15 absent original report statement remains absent',lambda x:x.update(statement=b['statement']))
   else:
    diag='v15 exact pilot saved-object and stored-proposal population'
    for label,change in [('trajectory',lambda x:x.update(complete_trajectory_checked=True)),('states',lambda x:x.update(saved_state_files=101)),('boolcounter',lambda x:x.update(native_reported_proposals=True)),('storedproposal',lambda x:x.update(complete_anchored_proposals=10098)),('localzero',lambda x:x.update(saved_localzero_object_observations=1)),('targetzero',lambda x:x.update(zero_target_candidates=1))]:bad_report(label,diag,change)
    bad_binding('savedscore','v15 exact saved current best object statement fields',lambda x:x['recorded_validation']['current'].update(E_mu=1),True)
    bad_report('inventedheadline','v15 absent original report statement remains absent',lambda x:x.update(statement=b['statement']))
  # One preexisting real editorial adapter is exercised; all others are AST-preserved.
  oldbinding=read('acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json','40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05')
  oldreport=read(oldbinding['report'],oldbinding['report_sha256'])
  need(m.v14_lowword_editorial(oldbinding['id'],'40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05',oldbinding,oldbinding['report_sha256'],oldreport)is not None,'preserved V14 exact adapter')
  cases.append(dict(case='actual_V14_editorial_adapter_preserved',outcome='PASS'))
  need(pin('CLAIMS.yaml')==ledger and pin('.git/index')==index,'live ledger index unchanged')
  save(out/'statement_mappings.json',mappings)
  save(out/'summary.json',dict(status='AUTHOR_REGISTRAR_V15_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_GATE',timestamp=datetime.now(timezone.utc).isoformat(),author='/root/native_driver',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
   inputs_sha256=pins,controls=cases,positive_controls=sum(r['outcome']=='PASS'for r in cases),strict_negative_controls=sum(r['outcome']=='REJECTED'for r in cases),complete_V14_AST_preserved=True,
   registrar_main_called=False,independent_approval=False,mathematical_replays=0,ledger_mutations=0,index_mutations=0,target_resolution='NONE',elapsed_seconds=time.monotonic()-start,deadline=d.status(),
   limitations=['Same-author metadata controls; author also authored native pilot, no outcome or theorem approval.','Separate ROOT source/helper/projected353->356 engineering gate must pass before any live registration.','No mathematical replay, unconditional scope inference, generic ROOT role, legacy fallback or overwritten raw statement.']))
  print(json.dumps(dict(positive=sum(r['outcome']=='PASS'for r in cases),strict_negative=sum(r['outcome']=='REJECTED'for r in cases))))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),completed_controls=cases,inputs_sha256=pins,deadline=d.status()));raise
if __name__=='__main__':main()
