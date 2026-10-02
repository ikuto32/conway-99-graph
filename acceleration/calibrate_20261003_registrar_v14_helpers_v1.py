"""Same-author V14 editorial/AST controls, never registrar main or approval."""
import argparse,ast,copy,hashlib,importlib.util,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v13.py'
OLD_SHA='1cfac35e19e473822583adfec8be7dfbd2ec73f59d0508febec14d24aeceef1a'
NEW='acceleration/register_20261003_bound_claims_v14.py'
NEW_SHA='6cf12f3dcb3b1e95d692d773df9e266c73101ce6ed0e9bebba0e79d00669c79b'
SPEC='acceleration/register_20261003_bound_claims_v14_spec.md'
SPEC_SHA='d4ea135b838fd6d536b9566ca2168d01481fa003adc7431bdf7c99ad405330db'
ID='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
BIND='acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json'
BIND_SHA='40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05'
def need(ok,message):
 if not ok:raise ValueError(message)
def write(path,value):
 with path.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True);a=p.parse_args()
 d=CommandDeadline(a.seconds,allocation_reason='Same-author V14 finite AST/editorial helpers only; no main, no target computation, no ledger/index mutation;20save reserve')
 start=time.monotonic();out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);pins={};cases=[]
 def pin(name,h=None):
  need(d.status()['remaining_seconds']>20,'metadata budget reserve')
  with(ROOT/name).open('rb')as f:x=hashlib.file_digest(f,'sha256').hexdigest()
  need(h is None or x==h,'exact input '+name);pins[name]=x;return x
 def read(name,h=None):pin(name,h);return json.loads((ROOT/name).read_bytes())
 def reject(name,diag,fn):
  try:fn()
  except ValueError as e:need(str(e)==diag,'exact negative '+name+': '+str(e));cases.append(dict(case=name,outcome='REJECTED',diagnostic=diag));return
  raise ValueError('unexpected acceptance '+name)
 try:
  live=pin('CLAIMS.yaml');idx=pin('.git/index');pin(OLD,OLD_SHA);pin(NEW,NEW_SHA);pin(SPEC,SPEC_SHA)
  for n in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/calibrate_20261003_registrar_v14_helpers_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock','acceleration/register_20261003_bound_claims_v13_spec.md','acceleration/results/20261003_registrar_v13_helpers02/summary.json']:pin(n)
  old=ast.parse((ROOT/OLD).read_text(encoding='utf-8-sig'));new=ast.parse((ROOT/NEW).read_text(encoding='utf-8-sig'))
  olddefs={v.name for v in old.body if isinstance(v,ast.FunctionDef)};newdefs={v.name for v in new.body if isinstance(v,ast.FunctionDef)}
  need(newdefs-olddefs=={'v14_lowword_editorial'} and olddefs<=newdefs,'one new definition only')
  restored=copy.deepcopy(new);restored.body=[v for v in restored.body if not(isinstance(v,ast.FunctionDef)and v.name=='v14_lowword_editorial')]
  class Restore(ast.NodeTransformer):
   def visit_Assign(self,n):
    if any(isinstance(t,ast.Name)and t.id=='editorial_statement_mapping' for t in n.targets):return None
    if any(isinstance(t,ast.Subscript)and isinstance(t.value,ast.Name)and t.value.id=='report' and isinstance(t.slice,ast.Constant)and t.slice.value=='editorial_statement_mappings' for t in n.targets):return None
    return self.generic_visit(n)
   def visit_If(self,n):
    if isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='editorial_statement_mapping':
     if len(n.body)==1 and isinstance(n.body[0],ast.Pass):need(len(n.orelse)==1,'exact new elif');return self.visit(n.orelse[0])
     need(not n.orelse,'exact metadata-only mapping insertion');return None
    return self.generic_visit(n)
  need(ast.dump(Restore().visit(restored),include_attributes=False)==ast.dump(old,include_attributes=False),'complete V13 AST restoration')
  cases.append(dict(case='full_V13_AST_preserved',outcome='PASS'))
  spec=importlib.util.spec_from_file_location('author_v14',ROOT/NEW);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  b=read(BIND,BIND_SHA);r=read(b['report'],b['report_sha256'])
  for n in [b['written_audit'],'acceleration/results/20261003_independent_review/incidence_low_weights01/controls.json','acceleration/results/20261003_independent_review/incidence_low_weights01/normalized_rows.json']:pin(n,b['inputs_sha256'][n])
  mapped=m.v14_lowword_editorial(ID,BIND_SHA,b,b['report_sha256'],r)
  need(mapped['original_report_statement']==r['statement'] and mapped['recorded_binding_statement']==b['statement'] and r['statement']!=b['statement'] and mapped['mathematical_replays']==0,'precise preserved editorial mapping')
  cases.append(dict(case='actual_explicit_binding_original_headline_preserved',outcome='PASS'))
  need(m.v14_lowword_editorial('C-OTHER',BIND_SHA,b,b['report_sha256'],r)is None,'no generic exception');cases.append(dict(case='unknown_id_no_adapter',outcome='PASS'))
  reject('wrong binding hash','v14 exact editorial binding',lambda:m.v14_lowword_editorial(ID,'0'*64,b,b['report_sha256'],r))
  diag='v14 exact ordinary revision roles kind basis method dependencies'
  mutations=[('revision',lambda x:x.update(revision=2)),('boolean revision',lambda x:x.update(revision=True)),('boolean claim revision',lambda x:x.update(claim_revision=True)),
   ('status',lambda x:x.update(status='CANDIDATE')),('review state',lambda x:x.update(review_state='QUARANTINED')),('kind',lambda x:x.update(kind='exclusion')),('basis',lambda x:x.update(basis=['COMPUTED'])),
   ('producer self approval',lambda x:x.update(producer='/root/checkpoint_audit')),('ROOT permission',lambda x:x.update(verifier='/root')),('method',lambda x:x.update(method='independent_artifact_check')),('dependency',lambda x:x.update(dependencies=[dict(id='other',revision=1,relation='premise')]))]
  for name,change in mutations:
   v=copy.deepcopy(b);change(v);reject(name,diag,lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  for name,change in [('scope',lambda x:x['scope'].update(description='All codes')),('scope boolean',lambda x:x['scope'].update(unrestricted_target=1)),('known premise',lambda x:x.update(premise_state='VERIFIED')),('target promotion',lambda x:x.update(target_resolution='NONEXISTENT'))]:
   v=copy.deepcopy(b);change(v);reject(name,'v14 exact conditional editorial scope',lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  v=copy.deepcopy(b);v['statement']='Broader target conclusion';reject('binding statement','v14 exact two editorial statement strings',lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  v=copy.deepcopy(r);v['statement']=b['statement'];reject('overwritten original raw statement','v14 exact two editorial statement strings',lambda:m.v14_lowword_editorial(ID,BIND_SHA,b,b['report_sha256'],v))
  for name,change in [('report hash',lambda x:x.update(report_sha256='0'*64)),('report path',lambda x:x.update(report='other.json')),('proof path',lambda x:x.update(written_audit='other.md')),('proof identity',lambda x:x['inputs_sha256'].update({b['written_audit']:'0'*64}))]:
   v=copy.deepcopy(b);change(v);reject(name,'v14 exact independent report and written derivation',lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  for name,change in [('report role',lambda x:x.update(verifier='/root')),('proof not complete',lambda x:x.update(universal_derivation_checked=False)),('rank promotion',lambda x:x.update(rank_bound_claimed=True)),('new target exclusions',lambda x:x.update(new_exclusions=1)),('Boolean exclusions',lambda x:x.update(new_exclusions=False)),('false prior interval reproof',lambda x:x.update(prior_weight_interval_rederived=True)),('count mutation',lambda x:x['target_lower_word_counts'].update({'6':24487}))]:
   v=copy.deepcopy(r);change(v);reject(name,'v14 exact written theorem outcome and limitations',lambda:m.v14_lowword_editorial(ID,BIND_SHA,b,b['report_sha256'],v))
  v=copy.deepcopy(b);v['recorded_validation']['strict_negative_controls']=9;reject('lost finite corruption','v14 exact recorded independent finite controls',lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  v=copy.deepcopy(r);v['positive_fixtures'].pop();reject('missing positive fixture','v14 exact recorded independent finite controls',lambda:m.v14_lowword_editorial(ID,BIND_SHA,b,b['report_sha256'],v))
  v=copy.deepcopy(b);v['controls_references'].pop();reject('missing literal controls ref','v14 exact immutable control and sharp row artifacts',lambda:m.v14_lowword_editorial(ID,BIND_SHA,v,v['report_sha256'],r))
  for cid,path,h in [('C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85','acceleration/results/20261003_incidence_low_weight_bindings02/rank85_claim_binding_schema2_v2.json','2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189'),('C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS','acceleration/results/20261003_fixed_two_line_census_binding03/claim_binding_schema2_draft.json','b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1')]:
   v=read(path,h);vr=read(v['report'],v['report_sha256']);need(m.v13_root_role(cid,h,v)is True,'preserved V13 role');m.v13_root_report(cid,v['report_sha256'],v,vr);need(m.v14_lowword_editorial(cid,h,v,v['report_sha256'],vr)is None,'other exact adapters not rewritten');cases.append(dict(case=cid+'_V13_unchanged',outcome='PASS'))
  need(pin('CLAIMS.yaml')==live and pin('.git/index')==idx,'live ledger/index preserved')
  write(out/'editorial_mapping.json',mapped)
  report=dict(status='AUTHOR_REGISTRAR_V14_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_GATE',timestamp=datetime.now(timezone.utc).isoformat(),author='/root/checkpoint_audit',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
   controls=cases,positive_controls=sum(v['outcome']=='PASS'for v in cases),strict_negative_controls=sum(v['outcome']=='REJECTED'for v in cases),complete_V13_AST_preserved=True,registrar_main_called=False,independent_approval=False,mathematical_replays=0,ledger_mutations=0,index_mutations=0,target_resolution='NONE',
   editorial_mapping_sha256=pin((out/'editorial_mapping.json').relative_to(ROOT).as_posix()),elapsed_seconds=time.monotonic()-start,deadline=d.status(),limitations=['Same-author finite metadata controls only; structural must independently gate actual protected350->353 before ROOT live use.','No universal theorem replay, report rewriting, broad statement inference or new ROOT permission.'])
  write(out/'summary.json',report);print(json.dumps(dict(status=report['status'],positive=report['positive_controls'],strict_negative=report['strict_negative_controls'])))
 except BaseException as e:write(out/'failure.json',dict(error=repr(e),completed_controls=cases,inputs_sha256=pins,deadline=d.status()));raise
if __name__=='__main__':main()
