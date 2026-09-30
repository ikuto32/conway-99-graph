"""Candidate append of six universal scalar cuts to the six-orbit count CSP."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,importlib.util,json,platform,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';OLD=B+'count_master_eight_orbit_cuts/';CUT=B+'second_count_partial_cut/';MASTER=B+'hadamard_count_master_cnf/';PRODUCER='acceleration/theory_20260930_hadamard_count_master_cnf.py'
PINS={OLD+'summary.json':'6a0e2c8acde3eccf6fd4ee74044041d3ebcf932ff65a345264ba840c3e7b4be7',OLD+'instance.cnf':'c3c0a9c0533d41bb814011d3736a4115d388e529f4c9cd2f89af609dc94793e2',OLD+'model.json':'a4376d5ee0e4cd8e990d311444f8ccda61d4b39af1c1c2371ade73e96dbe3d22',OLD+'scope.json':'5d604cc2c7725bee0865d9c746c97a005d2cd3aed08db078acb676d44cbf8518',MASTER+'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',MASTER+'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',PRODUCER:'470cbec724f891264593dc5b438648dc2995b3f860f89decf4b6ac8bc1c4f28b','acceleration/theory_20260930_hadamard_count_master_cnf_spec.md':'67b5e379c1b5e6d1dcb6e6aff0c022821a56169a55e1656abf3d353aac5b5d19',CUT+'summary.json':'75b3fe176b749a24778921253f8ac842d13b05c239f41c50e9b715443a50a0a0',CUT+'model.json':'42145953fbc9397bc7e8ce902502ff3c6510b7f0d0eaf948f56a4dc4e2fd7c1d',CUT+'ordered_fibre_instances.json':'f14efac809f8e1c30413ffd37b10a6a1326c995cd5de54b0e17306da9f08ae0d',CUT+'universal_six_bound_cuts.cnfpart':'7aa393e2df630f189cb004591e793a8ba0278b59cfff0ad70d20243faaef30c4',I+'count_master_eight_orbit_cuts/summary.json':'4c919b9b48d4c9d6bf085480f9ae166172f33b457e85713c50c109c29bc57493',I+'hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',I+'count_master_eight_orbit_cut_sat_outcome/summary.json':'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',B+'count_master_eight_orbit_cut_native_pilot/main/parsed_model.json':'40174793158d22cb17a0fff711102e9f3053ab04c9b23ba632d94c2976727189','uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
N=155939;OLD_M=705839;NEW_M=705845
SCALAR_GATE=I+'second_count_partial_cut/summary.json'
PINS[SCALAR_GATE]='727f9aa9aec1b3fe3f0f422e440dd0fb6fb5bfc63602c3aeee28ba3082bccfc8'
PINS[I+'second_count_partial_cut/claim_binding.json']='6462eb2b89843de3dd6d87666c841b3cbbfed6e34089edbf7f94df8ef128aecb'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
 with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def values(literals,n):
 need(type(literals)is list and len(literals)==n and all(type(x)is int and 0<abs(x)<=n for x in literals)and len(set(map(abs,literals)))==n,'complete unique signed IDs');v=[False]*(n+1)
 for x in literals:v[abs(x)]=x>0
 return v
def evaluate(path,v,n,m):
 false=[];count=0;maxvar=0
 with Path(path).open('rb')as f:
  need(f.readline()==f'p cnf {n} {m}\n'.encode(),'exact actual header')
  for line in f:
   row=list(map(int,line.split()));need(row and row[-1]==0 and all(0<abs(x)<=n for x in row[:-1]),'valid actual clause');count+=1
   if row[:-1]:maxvar=max(maxvar,max(map(abs,row[:-1])))
   if not any(v[abs(x)]==(x>0)for x in row[:-1]):false.append(count)
 need(count==m,'complete clause count');return dict(clauses=count,false_clause_indices=false,maximum_variable=maxvar)
def check_composition(base,full,suffix,n,oldm,newm):
 h=hashlib.sha256();total=0
 with Path(base).open('rb')as old,Path(full).open('rb')as new:
  need(old.readline()==f'p cnf {n} {oldm}\n'.encode()and new.readline()==f'p cnf {n} {newm}\n'.encode(),'composition headers')
  while block:=old.read(1048576):need(new.read(len(block))==block,'every retained base body byte');h.update(block);total+=len(block)
  need(new.read()==Path(suffix).read_bytes(),'exact only-six-clause suffix')
 return dict(base_body_sha256=h.hexdigest(),base_body_bytes=total,suffix_sha256=sha(suffix),suffix_bytes=Path(suffix).stat().st_size)
def controls(folder):
 base=folder/'tiny_base.cnf';suffix=folder/'tiny_suffix.cnfpart';full=folder/'tiny_full.cnf';base.write_bytes(b'p cnf 3 2\n1 0\n2 3 0\n');suffix.write_bytes(b'-2 3 0\n');full.write_bytes(b'p cnf 3 3\n1 0\n2 3 0\n-2 3 0\n');check_composition(base,full,suffix,3,2,3);need(not evaluate(full,values([1,-2,3],3),3,3)['false_clause_indices'],'tiny synthetic positive');rejected=[]
 def reject(name,fn):
  try:fn()
  except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
  else:raise ValueError('corruption accepted '+name)
 for name,lits in [('duplicate',[1,1,3]),('missing',[1,3]),('out_of_range',[1,-2,4]),('zero',[1,0,3])]:reject('assignment_'+name,lambda lits=lits:values(lits,3))
 cases={'header':b'p cnf 3 4\n1 0\n2 3 0\n-2 3 0\n','missing_row':b'p cnf 3 3\n1 0\n2 3 0\n','extra_row':b'p cnf 3 3\n1 0\n2 3 0\n-2 3 0\n1 0\n','terminator':b'p cnf 3 3\n1 0\n2 3 0\n-2 3\n','range':b'p cnf 3 3\n1 0\n2 3 0\n4 0\n'}
 for name,data in cases.items():
  p=folder/('corrupt_'+name+'.cnf');p.write_bytes(data);reject(name,lambda p=p:evaluate(p,values([1,-2,3],3),3,3))
 changed=folder/'corrupt_sign.cnf';changed.write_bytes(b'p cnf 3 3\n1 0\n2 3 0\n2 -3 0\n');reject('suffix_sign_composition',lambda:check_composition(base,changed,suffix,3,2,3));need(evaluate(changed,values([1,-2,3],3),3,3)['false_clause_indices']==[3],'false suffix diagnostic')
 return dict(tiny_synthetic_positive=True,tiny_is_research=False,rejected=rejected,new_actual_SAT_positive_available=False)
def original_decoder():
 need(sha(ROOT/PRODUCER)==PINS[PRODUCER],'pinned original producer decoder');spec=importlib.util.spec_from_file_location('original_count_producer',ROOT/PRODUCER);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);return p
def decode(assignment,model_path,variant='at_least_seven',cnf_path=None):
 need(variant=='at_least_seven','fixed >=7 variant');m=read(model_path);need(m['variables']==N and m['clauses']==NEW_M,'new model dimensions');cnf=ROOT/m['cnf_path']if cnf_path is None else Path(cnf_path);need(sha(cnf)==m['cnf_sha256'],'new exact CNF');scope=ROOT/m['scope_path'];need(sha(scope)==m['scope_sha256'],'new scope identity');v=values(assignment,N);check=evaluate(cnf,v,N,NEW_M);need(not check['false_clause_indices'],'complete new clause satisfaction')
 for p,h in m['decoder_inputs_sha256'].items():need(sha(ROOT/p)==h,'frozen decoder input '+p)
 raw=original_decoder().decode(assignment,ROOT/m['base_count_model_path'],variant);table=raw['coordinate_group_fibre_counts'];scalar=[]
 for r in m['scalar_clause_records']:
  outside=[dict(group=t['group'],coordinate=t['coordinate'],fibre=t['fibre'],value=table[t['coordinate']][t['group']][t['fibre']],upper_bound=t['upper_bound'])for t in r['partial_restrictions']];escapes=any(x['value']>x['upper_bound']for x in outside);need(escapes and any(v[x]for x in r['clause']),'raw scalar condition/actual channel clause');scalar.append(dict(fibres=r['fibres'],terms=outside,condition_satisfied=escapes))
 old=read(ROOT/m['old_model_path']);old_avoidances=[]
 for c in old['clause_records']:
  avoids=any(not v[-x]for x in c['clause']);need(avoids,'six old profile avoidances');old_avoidances.append(dict(clause_index=c['index'],profile_sha256=c['profile_sha256'],avoided=avoids))
 raw.update(actual_cnf_clauses_checked=NEW_M,new_model_sha256=sha(model_path),new_cnf_sha256=sha(cnf),new_scope_sha256=sha(scope),scalar_cut_checks=scalar,old_profile_avoidances=old_avoidances,producer_decode_reuse=PRODUCER,full_factor=False,target_graph=False,residual_D=None,independent_approval=False);return raw
def package(path):
 parts=[];offset=0;whole=hashlib.sha256()
 with path.open('rb')as stream:
  while block:=stream.read(8*1024**2):
   dest=path.with_name(path.name+f'.part{len(parts):04d}.gz')
   with dest.open('xb')as f:
    with gzip.GzipFile(fileobj=f,filename='',mtime=0,compresslevel=9,mode='wb')as z:z.write(block)
   actual=gzip.decompress(dest.read_bytes());need(actual==block and dest.stat().st_size<=10*1024**2,'literal transport/size');whole.update(actual);parts.append(dict(index=len(parts),path=key(dest),gzip_sha256=sha(dest),gzip_bytes=dest.stat().st_size,raw_offset=offset,raw_bytes=len(block),raw_sha256=hashlib.sha256(block).hexdigest()));offset+=len(block)
 need(offset==path.stat().st_size and whole.hexdigest()==sha(path),'whole package identity');return dict(raw_path=key(path),raw_sha256=sha(path),raw_bytes=offset,parts=parts,recovery='Concatenate decompressed parts in increasing index; verify each part and full identity.',literal_recovery_checked=True)
def build(out):
 start=time.monotonic();pins=dict(PINS)
 try:
  for p,h in pins.items():need(sha(ROOT/p)==h,'frozen input '+p)
  need(read(ROOT/SCALAR_GATE)['status']=='INDEPENDENT_SECOND_COUNT_PARTIAL_SCALAR_CUTS_PASS','independent scalar necessity gate')
  for p in [Path(__file__),Path(__file__).with_name('theory_20260930_count_master_scalar_cuts_spec.md'),ROOT/'docs/PLAN_20260930_COUNT_MASTER_SCALAR_OBJECT.md']:pins[key(p)]=sha(p)
  cut_summary=read(ROOT/(CUT+'summary.json'))
  for p,h in cut_summary['inputs_sha256'].items():need(sha(ROOT/p)==h,'cut source closure '+p);pins[p]=h
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],python=platform.python_version(),cwd=str(ROOT),inputs_sha256=pins,variables=N,base_clauses=OLD_M,clauses=NEW_M,new_variables=0,added_clauses=6,native_calls=0,solver_calls=0,limit_seconds=60,independent_scalar_gate_pending=False,independent_scalar_gate=SCALAR_GATE,independent_scalar_gate_sha256=PINS[SCALAR_GATE],independent_approval=False))
  folder=out/'controls';folder.mkdir();cal=controls(folder);records=read(ROOT/(CUT+'ordered_fibre_instances.json'))['records'];need(len(records)==6 and [r['fibres']for r in records]==[[0,1],[0,2],[1,0],[1,2],[2,0],[2,1]],'exact ordered six instances');suffix=(ROOT/(CUT+'universal_six_bound_cuts.cnfpart')).read_bytes();need(suffix==b''.join((' '.join(map(str,r['clause']))+' 0\n').encode()for r in records)and all(len(r['clause'])==25 and all(type(x)is int and 0<x<=N for x in r['clause'])for r in records),'only authenticated six25positive clauses');(out/'cuts.cnfpart').write_bytes(suffix)
  cnf=out/'instance.cnf'
  with cnf.open('xb')as dst:
   dst.write(f'p cnf {N} {NEW_M}\n'.encode())
   with (ROOT/(OLD+'instance.cnf')).open('rb')as src:
    need(src.readline()==f'p cnf {N} {OLD_M}\n'.encode(),'frozen old header')
    while chunk:=src.read(1048576):dst.write(chunk)
   dst.write(suffix)
  composed=check_composition(ROOT/(OLD+'instance.cnf'),cnf,out/'cuts.cnfpart',N,OLD_M,NEW_M);actual=values(read(ROOT/(B+'count_master_eight_orbit_cut_native_pilot/main/parsed_model.json'))['assignment'],N);walk=evaluate(cnf,actual,N,NEW_M);need(walk['false_clause_indices']==[NEW_M]and walk['maximum_variable']==N,'old realSATprefix/new final scalar violation');cal.update(actual_previous_SAT_assignment_check=walk,interpretation='A negative control on the new formula, not new SAT/UNSAT research.');save(folder/'summary.json',cal)
  oldmeta=read(ROOT/(OLD+'model.json'));master=read(ROOT/(MASTER+'model.json'));scope=dict(schema='COUNT_MASTER_SIX_ORBIT_PLUS_SIX_SCALAR_CUT_SCOPE_V1',base_variant='at_least_seven',minimum_exception_count=7,base_count_model_path=MASTER+'model.json',base_count_model_sha256=PINS[MASTER+'model.json'],old_orbit_scope_path=OLD+'scope.json',old_orbit_scope_sha256=PINS[OLD+'scope.json'],old_full_profile_nogoods=6,new_scalar_necessary_clauses=6,new_clause_lengths=[25]*6,raw_literal_support=master['groups'],scalar_coordinate_pair=[9,11],ordered_distinct_fibre_instances=[r['fibres']for r in records],new_clauses_use_local_caps=False,new_clauses_use_symmetry=False,local_group_catalogue_membership_retained=True,full_Gram_encoded=False,all_column_caps_encoded=False,residual_D_encoded=False,full_factor=False,target_graph=False,residual_D=None,meaning='Exactly the >=7 count-table CSP plus six earlier whole-profile cuts plus six new scalar necessary conditions. Count solutions need not lift to a full-Gram factor.',independent_new_encoding_and_scalar_gate_required=True);save(out/'scope.json',scope)
  clause_records=[dict(index=OLD_M+i+1,fibres=r['fibres'],coordinates=r['coordinates'],clause=r['clause'],partial_restrictions=r['partial_restrictions'])for i,r in enumerate(records)];save(out/'clause_records.json',dict(records=clause_records,new_variables=0,negative_exact_channel_comparison_not_appended=True))
  decoder_pins={p:PINS[p]for p in [PRODUCER,MASTER+'model.json',MASTER+'at_least_seven.cnf',OLD+'model.json',OLD+'instance.cnf',OLD+'scope.json']};model=dict(schema='COUNT_MASTER_SCALAR_CUT_REFERENCE_MODEL_V1',variables=N,clauses=NEW_M,base_variant='at_least_seven',base_count_model_path=MASTER+'model.json',base_count_model_sha256=PINS[MASTER+'model.json'],old_model_path=OLD+'model.json',old_model_sha256=PINS[OLD+'model.json'],old_cnf_path=OLD+'instance.cnf',old_cnf_sha256=PINS[OLD+'instance.cnf'],old_clause_count=OLD_M,old_full_profile_clauses=oldmeta['clause_records'],cnf_path=key(cnf),cnf_sha256=sha(cnf),scope_path=key(out/'scope.json'),scope_sha256=sha(out/'scope.json'),suffix_path=key(out/'cuts.cnfpart'),suffix_sha256=sha(out/'cuts.cnfpart'),composition=composed,scalar_clause_records=clause_records,decoder_inputs_sha256=decoder_pins,decode_ABI="decode(assignment, model_path, variant='at_least_seven', cnf_path=None)",inputs_sha256=pins,full_factor=False,target_graph=False,independent_approval=False);save(out/'model.json',model)
  packages=[]
  for p in [cnf,out/'model.json',out/'scope.json']:
   if p.stat().st_size>10*1024**2:packages.append(package(p))
  save(out/'artifact_packages.json',dict(schema='COUNT_MASTER_SCALAR_CUTS_GZIP_TRANSPORT_V1',records=packages,raw_originals_preserved=True,independent_transport_approval=False));need(time.monotonic()-start<60,'bounded60second build');summary=dict(status='CANDIDATE_COUNT_MASTER_SIX_ORBIT_AND_SIX_SCALAR_CUT_CNF_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},variables=N,clauses=NEW_M,old_clauses=OLD_M,new_variables=0,new_scalar_clauses=6,new_scalar_clause_lengths=[25]*6,CNF_bytes=cnf.stat().st_size,cnf_path=key(cnf),cnf_sha256=sha(cnf),model_path=key(out/'model.json'),model_sha256=sha(out/'model.json'),scope_path=key(out/'scope.json'),scope_sha256=sha(out/'scope.json'),elapsed_seconds=time.monotonic()-start,native_calls=0,solver_calls=0,independent_approval=False,full_factor=False,target_graph=False,artifact_availability='LOCAL_ONLY',limitations=['Full count profile relaxation only; no simultaneous local colouring/full Gram factor.','Only these six new scalar clauses appended, no extra exact-channel comparison clause.','New independent encoding/object gates required before research native use.']);save(out/'summary.json',summary);print(json.dumps({k:summary[k]for k in ['status','variables','clauses','cnf_sha256','model_sha256','scope_sha256','elapsed_seconds']}));print('summary_sha256 '+sha(out/'summary.json'))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);p=sub.add_parser('build');p.add_argument('--out',type=Path,required=True);p=sub.add_parser('decode');p.add_argument('--assignment',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--variant',choices=['at_least_seven'],default='at_least_seven');p.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 if a.mode=='build':build(out)
 else:
  try:save(out/'decoded_count_profile.json',decode(read(a.assignment)['assignment'],a.model,a.variant))
  except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
