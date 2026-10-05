"""Candidate streamed direct-cell CNF build and producer raw-factor decoder."""
from pathlib import Path
from itertools import combinations,product
from datetime import datetime,timezone
import argparse,copy,gzip,hashlib,importlib.util,json,platform,shutil,sys,time
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
HELPER=ROOT/'acceleration/theory_20260930_direct_cell_count_preflight.py'
PRE=B/'20260930_direct_cell_count_preflight'
PINS={
 'acceleration/theory_20260930_direct_cell_count_preflight.py':'902bafedf5099fc27727caf17819e50080e514ed9e0b6788fdd5345fb3d5ffdd',
 'acceleration/theory_20260930_direct_cell_count_preflight_spec.md':'b95c02a2ed80fee55260a57dfce0a05e1b26f84bd48aaae4f770da4c28b05368',
 'acceleration/results/20260930_direct_cell_count_preflight/summary.json':'d6aa4b70697ab7122a2b88ffb54388a804843c694a6dc98ecbe3b580f054be3d',
 'acceleration/results/20260930_direct_cell_count_preflight/standalone_inventory.json':'c6d199f0bef0e898dfd3fb0d392479ba5a0d4c71ea91fa475a65b490180f77ac',
 'acceleration/results/20260930_direct_cell_count_preflight/at_least_seven_inventory.json':'5b236ae3fab131c1e24e214f312e4977374cdc20a17fefc1bd815c7a45774d01',
 'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
TARGETS={'standalone':(23112,320484,7208403),'at_least_seven':(169151,968960,18279995)}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
 with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def helper():
 need(sha(HELPER)==PINS[key(HELPER)],'frozen shared production helper');s=importlib.util.spec_from_file_location('frozen_direct_cell_producer',HELPER);h=importlib.util.module_from_spec(s);s.loader.exec_module(h);return h
def assignment_values(assignment,n):
 need(type(assignment)is list and len(assignment)==n,'complete assignment length');v=[False]*(n+1);seen=set()
 for x in assignment:need(type(x)is int and 0<abs(x)<=n and abs(x)not in seen,'unique complete integer literals');seen.add(abs(x));v[abs(x)]=x>0
 need(len(seen)==n,'all IDs');return v
def check_cnf(path,v,n,expected):
 count=0
 with Path(path).open(encoding='ascii')as stream:
  need(stream.readline()==f'p cnf {n} {expected}\n','exact actual header')
  for line in stream:
   c=list(map(int,line.split()));need(c and c[-1]==0 and all(0<abs(x)<=n for x in c[:-1]),'actual clause syntax');need(any(v[abs(x)]==(x>0)for x in c[:-1]),'actual clause satisfaction');count+=1
 need(count==expected,'complete actual clause population');return count
def gram_target(C,n):return [[n*int(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(3*n))+2-int(i//n==j//n)for j in range(3*n)]for i in range(3*n)]
def check_factor(F,C,G,n,L=None):
 rows=3*n;need(type(F)is list and len(F)==rows and F and type(F[0])is list,'factor shape');width=len(F[0]);need(all(type(row)is list and len(row)==width and all(type(x)is int and x in(0,1)for x in row)for row in F),'binary rectangular factor')
 need(len(C)==rows and len(G)==rows and all(len(x)==rows for x in C+G),'core/Gram shape');masks=[sum(x<<d for d,x in enumerate(row))for row in F];actual=[[int((masks[i]&masks[j]).bit_count())for j in range(rows)]for i in range(rows)];need(actual==G,'all integer Gram entries');row_sums=[sum(row)for row in F];fibre_sums=[[sum(F[n*h+a][d]for a in range(n))for h in range(3)]for d in range(width)];need(row_sums==[n-2]*rows and all(x==[2]*3 for x in fibre_sums),'row and fibre margins')
 aggregate=[[sum(F[n*h+a][d]for h in range(3))for d in range(width)]for a in range(n)];need(L is None or aggregate==L,'literal aggregate L');cols=[sum(F[r][d]<<r for r in range(rows))for d in range(width)];caps=[dict(columns=[d,e],overlap=(cols[d]&cols[e]).bit_count())for d,e in combinations(range(width),2)];need(all(x['overlap']<=2 for x in caps),'all outside-column caps');mixed=[[F[r][d]+sum(C[r][s]*F[s][d]for s in range(rows))for d in range(width)]for r in range(rows)];need(all(v<=2 for row in mixed for v in row),'all closed-neighbourhood mixed caps')
 return dict(actual_Gram=actual,column_pair_overlaps=caps,mixed_closed_neighbourhood_values=mixed,row_sums=row_sums,column_fibre_sums=fibre_sums,aggregate_L=aggregate)
def controls(h,out):
 result=dict(frozen_preflight_controls=h.controls());fx=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json');F=fx['factor60x180'];C=fx['cubic_core60'];G=gram_target(C,20);good=check_factor(F,C,G,20);result['genuine243_positive']=dict(rows=60,columns=180,Gram_entries=3600,column_pairs=len(good['column_pair_overlaps']),mixed_entries=10800,research99=False)
 rejected=[]
 for name in ('flipped_factor_bit','changed_Gram','missing_row'):
  f=copy.deepcopy(F);g=copy.deepcopy(G)
  if name=='flipped_factor_bit':f[0][0]^=1
  elif name=='changed_Gram':g[0][0]+=1
  else:f.pop()
  try:check_factor(f,C,g,20)
  except ValueError:rejected.append(name)
  else:raise ValueError('corrupt factor accepted '+name)
 tiny=out/'tiny.cnf';tiny.write_text('p cnf 3 2\n1 2 0\n-1 3 0\n',encoding='ascii');v=assignment_values([1,-2,3],3);check_cnf(tiny,v,3,2)
 for name,lits in [('duplicate',[1,1,3]),('missing',[1,3]),('zero',[1,0,3]),('out_of_range',[1,-2,4])]:
  try:assignment_values(lits,3)
  except ValueError:rejected.append(name)
  else:raise ValueError('bad assignment accepted '+name)
 for name,text in [('changed_header','p cnf 4 2\n1 2 0\n-1 3 0\n'),('false_clause','p cnf 3 2\n1 2 0\n-3 0\n')]:
  p=out/(name+'.cnf');p.write_text(text,encoding='ascii')
  try:check_cnf(p,v,3,2)
  except ValueError:rejected.append(name)
  else:raise ValueError('bad tinyCNF accepted '+name)
 result['new_corruptions_rejected']=rejected;result['research_SAT_positive_available']=False;return result
def decode(assignment,model_path,scope_path,cnf_path=None):
 model=read(model_path);scope=read(scope_path);need(model['scope_sha256']==sha(scope_path),'scope identity');cnf=ROOT/model['cnf_path']if cnf_path is None else Path(cnf_path);need(sha(cnf)==model['cnf_sha256'],'CNF identity');v=assignment_values(assignment,model['variables']);checked=check_cnf(cnf,v,model['variables'],model['clauses']);recipe=model['recipe'];F=[[0]*60 for _ in range(36)]
 for g,d,a,h,x in recipe['cell_variables']:F[12*h+a][d]=int(v[x])
 checks=check_factor(F,scope['core_adjacency36'],scope['prescribed_Gram36'],12,scope['L12x60']);counts=[];exceptional=[]
 for g,support in enumerate(recipe['groups']):
  table=[[sum(F[12*h+a][d]for d in recipe['group_columns'][g])for h in range(3)]for a in support];counts.append(table)
  if any(x!=[1]*3 for x in table):exceptional.append(g)
 if model['variant']=='at_least_seven':need(len(exceptional)>=7,'literal exception-count lower bound')
 return dict(factor=F,core_adjacency36=scope['core_adjacency36'],target_Gram36=scope['prescribed_Gram36'],L12x60=scope['L12x60'],checks=checks,group_count_tables=counts,exceptional_groups=exceptional,exception_count=len(exceptional),actual_clauses_checked=checked,model_sha256=sha(model_path),scope_sha256=sha(scope_path),cnf_sha256=sha(cnf),literal_column_order=True,target_graph=False,residual_D=None,independent_approval=False)
def package(path,out,h,t):
 records=[];full=hashlib.sha256();offset=0
 with path.open('rb')as stream:
  while raw:=stream.read(8*1024**2):
   target=out/f'{path.name}.part{len(records):04d}.gz'
   with target.open('xb')as dest:
    with gzip.GzipFile(filename='',mode='wb',fileobj=dest,compresslevel=9,mtime=0)as gz:gz.write(raw)
   need(target.stat().st_size<10*1024**2,'package part<10MiB');recovered=gzip.decompress(target.read_bytes());need(recovered==raw,'literal chunk recovery');full.update(recovered);records.append(dict(index=len(records),path=key(target),gzip_sha256=sha(target),gzip_bytes=target.stat().st_size,raw_offset=offset,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest()));offset+=len(raw);h.budget(t)
 need(offset==path.stat().st_size and full.hexdigest()==sha(path),'whole raw identity');return dict(raw_path=key(path),raw_sha256=sha(path),raw_bytes=offset,parts=records,deterministic_gzip=dict(level=9,mtime=0,filename=''),recovery='Decompress each part in increasing index and concatenate; verify raw part and whole hashes.',all_bytes_recovered=True,original_preserved=True,proof_or_encoding_approval=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);t=time.monotonic()
 try:
  pins=dict(PINS);pins.update(read(PRE/'summary.json')['inputs_sha256'])
  for p,d in pins.items():need(sha(ROOT/p)==d,'input identity '+p)
  for p in [Path(__file__),Path(__file__).with_name('theory_20260930_direct_cell_count_cnf_spec.md')]:pins[key(p)]=sha(p)
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=120,working_set_bytes=512*1024**2),selection=list(TARGETS),native_calls=0,shared_production_code=key(HELPER),independent_approval=False))
  h=helper();cal=out/'controls';cal.mkdir();save(cal/'summary.json',controls(h,cal));h.budget(t);raw=read(B/'20260930_hadamard20_support/six_prism.json');master=read(B/'20260930_hadamard_count_master_cnf/model.json');saved=[];packages=[];Counter=h.CounterOnly
  for variant,pred in TARGETS.items():
   folder=out/variant;folder.mkdir();expected=read(PRE/f'{variant}_inventory.json');need(tuple(expected['all_caps'][k]for k in ('variables','clauses','ASCII_bytes'))==pred,'predeclared dimensions');temporary=folder/'instance.cnf.partial'
   with temporary.open('x',encoding='ascii',newline='\n')as stream:
    stream.write(f'p cnf {pred[0]} {pred[1]}\n')
    if expected['base']:
     base=expected['base'];bp=ROOT/base['cnf_path'];need(sha(bp)==base['cnf_sha256'],'base exact bytes')
     with bp.open(encoding='ascii',newline='')as src:
      need(src.readline()==f"p cnf {base['variables']} {base['clauses']}\n",'base header');shutil.copyfileobj(src,stream,1024*1024)
    class StreamingCounter(Counter):
     def add(self,c):
      super().add(c);stream.write((' '.join(map(str,c))+' 0\n')if c else '0\n')
    h.CounterOnly=StreamingCounter
    try:recipe=h.inventory(variant,master,raw,t)
    finally:h.CounterOnly=Counter
   need(recipe==expected,'complete recipe equals frozen preflight');need(temporary.stat().st_size==pred[2],'exact DIMACS ASCII bytes');cnf=folder/'instance.cnf';temporary.rename(cnf)
   scope=dict(schema='FIXED_LITERAL_HADAMARD_DIRECT_CELL_ALL_CAPS_SCOPE_V1',variant=variant,raw_support_path='acceleration/results/20260930_hadamard20_support/six_prism.json',raw_support_sha256=pins['acceleration/results/20260930_hadamard20_support/six_prism.json'],core_adjacency36=raw['core_adjacency'],prescribed_Gram36=raw['prescribed_Gram36'],L12x60=raw['L'],support_columns=raw['support_columns'],groups=recipe['groups'],group_columns=recipe['group_columns'],row_sum=10,column_fibre_sum=2,full_Gram_encoded=True,within_group_caps_encoded=True,cross_group_caps_encoded=True,count_master_included=variant!='standalone',minimum_exception_count=7 if variant=='at_least_seven'else None,minimum_exception_count_null_reason='No exception-count bound in standalone.'if variant=='standalone'else None,residual_D_encoded=False,target_automorphism_assumed=False,column_normalization=None,column_normalization_null_reason='All original labelled outside columns retained.',scope='Literal fixedL full integerGram and all column caps'+('; at least seven unbalanced groups.'if variant=='at_least_seven'else '.'),target_graph=False)
   clause_sections={};cursor=0
   if recipe['base']:clause_sections['count_master_prefix']=dict(first_clause=1,clause_count=recipe['base']['clauses'],last_clause=recipe['base']['clauses']);cursor=recipe['base']['clauses']
   for name,section in recipe['sections'].items():clause_sections[name]=dict(first_clause=cursor+1,clause_count=section['clauses'],last_clause=cursor+section['clauses'],variables_before=section['variables_before'],variables_after=section['variables_after']);cursor+=section['clauses']
   need(cursor==pred[1],'complete explicit clause ranges')
   save(folder/'scope.json',scope);model=dict(schema='FIXED_LITERAL_HADAMARD_DIRECT_CELL_ALL_CAPS_CNF_V1',variant=variant,variables=pred[0],clauses=pred[1],cnf_path=key(cnf),cnf_sha256=sha(cnf),scope_path=key(folder/'scope.json'),scope_sha256=sha(folder/'scope.json'),recipe=recipe,clause_sections=clause_sections,inputs_sha256=pins,decode_ABI='decode(assignment,model_path,scope_path,cnf_path=None)',primary_cell_count=1080,full_target_graph=False,producer_approval=False);save(folder/'model.json',model)
   for artifact in [cnf,folder/'model.json',folder/'scope.json']:
    if artifact.stat().st_size>10*1024**2:packages.append(package(artifact,folder,h,t))
   record=dict(variant=variant,variables=pred[0],clauses=pred[1],ASCII_bytes=pred[2],cnf_path=key(cnf),cnf_sha256=sha(cnf),model_path=key(folder/'model.json'),model_sha256=sha(folder/'model.json'),scope_path=key(folder/'scope.json'),scope_sha256=sha(folder/'scope.json'),all_caps=True);saved.append(record);save(folder/'summary.json',dict(status='CANDIDATE_DIRECT_CELL_FORMULA_BUILT',**record,inputs_sha256=pins,independent_approval=False,native_calls=0));print(json.dumps(record),flush=True);h.budget(t)
  save(out/'artifact_packages.json',dict(schema='DIRECT_CELL_GZIP_PART_TRANSPORT_V1',records=packages,raw_originals_preserved=True,artifact_availability='LOCAL_ONLY'));summary=dict(status='CANDIDATE_DIRECT_CELL_ALL_CAPS_FORMULAS_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},records=saved,package_records=len(packages),peak_working_set_bytes=h.peak(),elapsed_seconds=time.monotonic()-t,native_calls=0,independent_approval=False,artifact_availability='LOCAL_ONLY',limitations=['Literal fixed support and core only; no universal support/target coverage.','No residual D or99vertex graph.','Count≥7 is separately scoped; no≥8 substitution.','New encoding/decoded objects require independent review; shared producer code is disclosed.']);save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ('inputs_sha256','outputs_sha256','records')}))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-t));raise
if __name__=='__main__':main()
