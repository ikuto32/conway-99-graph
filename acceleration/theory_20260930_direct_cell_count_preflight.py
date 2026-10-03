"""Candidate exact size inventory of labelled F cells, not a CNF build."""
from pathlib import Path
from itertools import combinations, product
from collections import Counter
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,platform,sys,time
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
PINS={
 'acceleration/results/20260930_hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 'acceleration/results/20260930_hadamard_count_master_cnf/model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 'acceleration/results/20260930_hadamard_count_master_cnf/scope.json':'719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',
 'acceleration/results/20260930_independent_review/hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',
 'acceleration/results/20260930_hadamard_count_master_cnf/baseline.cnf':'609a606c2b228e3956e43ab7d2589dcbcdca797f5978ffa51c8029aa042b7ba7',
 'acceleration/results/20260930_hadamard_count_master_cnf/at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',
 'acceleration/results/20260930_independent_review/count_master_sat_outcome/independent_count_profile.json':'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',
 'acceleration/results/20260930_independent_review/count_master_sat_outcome/summary.json':'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',
 'acceleration/results/20260930_hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
 'acceleration/results/20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',
 'acceleration/results/20260930_hadamard_prism_ordered_cnf/summary.json':'02d3996a7e12f6b2e119d59bb184c79ebdea0f11352e47217e8b424b173ef721',
 'acceleration/results/20260930_all_triple_count_preflight_v3/summary.json':'7ed9bc4170703472057ba9549d2959d5533e480fbc109f4792defbcaab071518',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def need(ok,s):
 if not ok:raise ValueError(s)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
 with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def peak():
 class PMC(ctypes.Structure):
  _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(k,ctypes.c_size_t) for k in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
 p=PMC();p.cb=ctypes.sizeof(p);k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.argtypes=[];k.GetCurrentProcess.restype=ctypes.c_void_p;a=ctypes.WinDLL('psapi',use_last_error=True);a.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PMC),ctypes.c_ulong];a.GetProcessMemoryInfo.restype=ctypes.c_int;need(a.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(p),p.cb)!=0 and p.PeakWorkingSetSize>0,'positive successful memory probe');return int(p.PeakWorkingSetSize)
def budget(t):need(time.monotonic()-t<120,'120s inventory bound');need(peak()<512*1024**2,'512MiB inventory bound')
def exact(xs,k):
 for q in combinations(xs,k+1):yield [-v for v in q]
 for q in combinations(xs,len(xs)-k+1):yield list(q)
def conjunction(x,y,z):return [[-x,-y,z],[x,-z],[y,-z]]
def eqflag(x,y,e):return [[-x[f],-y[f],e] for f in range(3)]+[[-x[f],y[f],-e] for f in range(3)]
def channel_count(c,x,k):
 for b in product((False,True),repeat=3):
  if sum(b)!=k:yield [-c,*[-v if bit else v for v,bit in zip(x,b)]]
def satisfied(cs,v):return all(any(v[abs(x)]==(x>0) for x in c)for c in cs)
def val(x,v):return x if type(x)is bool else v[x]
def relation(z,q,x,r):
 ids=sorted({v for v in (z,q,x,r)if type(v)is not bool})
 for bits in product((False,True),repeat=len(ids)):
  v=dict(zip(ids,bits))
  if v[z]!=(val(q,v) or(val(x,v)and val(r,v))):yield [-a if b else a for a,b in zip(ids,bits)]
class CounterOnly:
 def __init__(self,n=0):self.top=n;self.sections={};self.section=None
 def new(self):self.top+=1;return self.top
 def start(self,s):
  self.section=s;self.sections[s]=dict(variables_before=self.top,clauses=0,literals=0,negative_literals=0,ascii_body_bytes=0,max_clause_literals=0)
 def add(self,c):
  need(all(type(x)is int and 0<abs(x)<=self.top for x in c),'literal allocation');s=self.sections[self.section];s['clauses']+=1;s['literals']+=len(c);s['negative_literals']+=sum(x<0 for x in c);s['ascii_body_bytes']+=sum(len(str(x))for x in c)+len(c)+2;s['max_clause_literals']=max(s['max_clause_literals'],len(c))
 def addall(self,cs):
  for c in cs:self.add(c)
 def end(self):self.sections[self.section]['variables_after']=self.top
 def totals(self):return {k:sum(v[k] for v in self.sections.values())for k in ('clauses','literals','negative_literals','ascii_body_bytes')}
def threshold(f,xs,k):
 states={};rows=[]
 for i,x in enumerate(xs,1):
  for j in range(1,min(i,k+1)+1):
   q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);z=f.new();f.addall(relation(z,q,x,r));states[i,j]=z;rows.append(dict(i=i,j=j,id=z,q=q,x=x,r=r))
 if k:f.add([states[len(xs),k]])
 if (len(xs),k+1)in states:f.add([-states[len(xs),k+1]])
 return rows
def controls():
 andn=eqn=countn=prefixn=channeln=0
 for bits in product((False,True),repeat=3):need(satisfied(conjunction(1,2,3),dict(enumerate(bits,1)))==(bits[2]==(bits[0]and bits[1])),'AND truth');andn+=1
 for bits in product((False,True),repeat=7):
  if sum(bits[:3])==sum(bits[3:6])==1:need(satisfied(eqflag([1,2,3],[4,5,6],7),dict(enumerate(bits,1)))==(bits[6]==(bits[:3]==bits[3:6])),'equality flag under one-hot premise');eqn+=1
 for n,k in [(3,1),(6,2),(15,1),(15,2)]:
  cs=list(exact(list(range(1,n+1)),k))
  for bits in product((False,True),repeat=n):need(satisfied(cs,dict(enumerate(bits,1)))==(sum(bits)==k),'exact count controls');countn+=1
 triples=[p for p in product(range(4),repeat=3)if sum(p)==3]
 for colours in product(range(3),repeat=3):
  for t in triples:
   v={1:True};xs=[[2+3*d+f for d in range(3)]for f in range(3)]
   for d,f in product(range(3),repeat=2):v[2+3*d+f]=colours[d]==f
   cs=[cl for f in range(3)for cl in channel_count(1,xs[f],t[f])];need(satisfied(cs,v)==(tuple(colours.count(f)for f in range(3))==t),'all local count channels');channeln+=1
 for n in range(1,7):
  for k in range(n+1):
   f=CounterOnly(n);f.start('prefix');rows=threshold(f,list(range(1,n+1)),k)
   cs=[c for r in rows for c in relation(r['id'],r['q'],r['x'],r['r'])]
   if k:cs.append([next(r['id']for r in rows if r['i']==n and r['j']==k)])
   if k<n:cs.append([-next(r['id']for r in rows if r['i']==n and r['j']==k+1)])
   for bits in product((False,True),repeat=n):
    v=dict(enumerate(bits,1));v.update({r['id']:sum(bits[:r['i']])>=r['j']for r in rows});need(satisfied(cs,v)==(sum(bits)==k),'prefix exact lower and upper');prefixn+=1
    if sum(bits)==k and rows:
     v[rows[0]['id']]^=True;need(not satisfied(cs,v),'corrupted prefix rejected')
 samples=[[1,-9,10],[-99,100,-999,1000],[99999,-100000],[-999999,1000000],[]];q=CounterOnly(1000000);q.start('bytes');q.addall(samples);need(q.totals()['ascii_body_bytes']==sum(len(((' '.join(map(str,c))+' 0\n')if c else '0\n').encode())for c in samples),'ASCII digits/boundaries including canonical empty clause')
 bad={1:True,2:False,3:False,4:True,5:False,6:False,7:False};need(not satisfied(eqflag([1,2,3],[4,5,6],7),bad),'incorrect equality bit rejected')
 return dict(AND_assignments=andn,equality_valid_onehot_assignments=eqn,exact_count_assignments=countn,conditional_count_cases=channeln,prefix_input_assignments=prefixn,ASCII_digit_boundary_cases=len(samples),corruptions_rejected=['wrong_equality_flag','wrong_prefix_state','wrong_selected_local_count'],research_factor_positive=False)
def inventory(variant,model,raw,t):
 base=model['variants'].get(variant);prefixbytes=0
 if base:
  p=ROOT/base['cnf_path'];header=f"p cnf {base['variables']} {base['clauses']}\n".encode()
  with p.open('rb')as stream:need(stream.readline()==header,'exact base header')
  prefixbytes=p.stat().st_size-len(header)
 f=CounterOnly(0 if base is None else base['variables']);groups=model['groups'];columns=raw['support_columns'];gcols=[[d for d,s in enumerate(columns)if s==support]for support in groups];need(all(len(c)==3 for c in gcols),'literal three columns each group');x={};cells=[]
 f.start('primary_cells')
 for g,s in enumerate(groups):
  for d,a,h in product(gcols[g],s,range(3)):v=f.new();x[d,a,h]=v;cells.append([g,d,a,h,v])
 f.end();need(len(x)==1080,'all1080 cells')
 f.start('one_fibre_per_coordinate')
 for d,s in enumerate(columns):
  for a in s:f.addall(exact([x[d,a,h]for h in range(3)],1))
 f.end();f.start('two_per_fibre_per_column')
 for d,s in enumerate(columns):
  for h in range(3):f.addall(exact([x[d,a,h]for a in s],2))
 f.end();links=[];rowcounters=[];f.start('row_counts_via_master' if base else 'explicit_row_counts')
 if base:
  for c in model['count_channels']:
   a,g=c['coordinate'],c['group']
   for val_,q in zip(c['values'],c['variables']):
    for h,k in enumerate(val_):xs=[x[d,a,h]for d in gcols[g]];f.addall(channel_count(q,xs,k));links.append(dict(group=g,coordinate=a,fibre=h,selector=q,value=k,inputs=xs))
 else:
  for a,h in product(range(12),range(3)):
   xs=[x[d,a,h]for d,s in enumerate(columns)if a in s];need(len(xs)==30,'thirty literal row cells');rowcounters.append(dict(coordinate=a,fibre=h,inputs=xs,states=threshold(f,xs,10)))
 f.end();pairs=[(a,b)for a,b in combinations(range(12),2)if a^1!=b];products=[];gram=[];f.start('full_Gram_products_and_counts')
 seen=set()
 for a,b in pairs:
  ds=[d for g,s in enumerate(groups)if a in s and b in s for d in gcols[g]];need(len(ds)==15,'15 product terms')
  for h,k in product(range(3),repeat=2):
   qs=[]
   for d in ds:
    u,v=x[d,a,h],x[d,b,k];key=tuple(sorted((u,v)));need(key not in seen,'no duplicated AND product');seen.add(key);q=f.new();f.addall(conjunction(u,v,q));qs.append(q);products.append([u,v,q])
   bound=1 if h==k else 2;f.addall(exact(qs,bound));gram.append(dict(coordinates=[a,b],fibres=[h,k],target=bound,products=qs))
 f.end();need(len(products)==8100 and len(gram)==540,'complete rawGram product/row population');budget(t)
 pairs_by_group=[(d,e)for ds in gcols for d,e in combinations(ds,2)];need(len(set(pairs_by_group))==60,'all within pairs');caps=[]
 def cap(d,e,kind):
  common=sorted(set(columns[d])&set(columns[e]));es=[]
  if len(common)>2:
   for a in common:
    q=f.new();f.addall(eqflag([x[d,a,h]for h in range(3)],[x[e,a,h]for h in range(3)],q));es.append(q)
   for tri in combinations(es,3):f.add([-q for q in tri])
  caps.append(dict(columns=[d,e],kind=kind,common_coordinates=common,equality_flags=es,automatic=len(common)<=2))
 f.start('within_group_column_caps')
 for d,e in pairs_by_group:cap(d,e,'within')
 f.end();main=f.totals();mainn=f.top;mainc=(0 if base is None else base['clauses'])+main['clauses'];mainbytes=prefixbytes+main['ascii_body_bytes']+len(f'p cnf {mainn} {mainc}\n'.encode());mainsections=dict(f.sections);f.start('optional_cross_group_column_caps');within=set(pairs_by_group)
 for d,e in combinations(range(60),2):
  if (d,e)not in within:cap(d,e,'cross')
 f.end();total=f.totals();alln=f.top;allc=(0 if base is None else base['clauses'])+total['clauses'];allbytes=prefixbytes+total['ascii_body_bytes']+len(f'p cnf {alln} {allc}\n'.encode());need(len(caps)==1770,'complete cap inventory');budget(t)
 config=dict(variant=variant,base=base,groups=groups,group_columns=gcols,cell_variables=cells,count_links=links,standalone_row_counters=rowcounters,Gram_products=products,Gram_rows=gram,column_caps=caps,sections=f.sections,within_only=dict(variables=mainn,clauses=mainc,ASCII_bytes=mainbytes,appended=main),all_caps=dict(variables=alln,clauses=allc,ASCII_bytes=allbytes,appended=total),optional_cross_cap_suffix=f.sections['optional_cross_group_column_caps'],literal_column_labels=True,within_group_triple_ordering=False,full_target=False,residual_D=None)
 return config
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);t=time.monotonic()
 try:
  for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p)
  inputs=dict(PINS);paths=[Path(__file__),Path(__file__).with_name('theory_20260930_direct_cell_count_preflight_spec.md'),ROOT/'docs/DESIGN_20260930_DIRECT_CELL_COUNT_GRAM.md']
  paths += [ROOT/'acceleration'/s for s in ['theory_20260930_triangle_joint_factor_cnf.py','theory_20260930_triangle_joint_factor_cnf_spec.md','theory_20260930_triangle_factor_column_caps.py','theory_20260930_variable_core_factor_preflight_spec.md','theory_20260930_hadamard_prism_ordered_cnf_spec.md']]
  for p in paths:inputs[p.relative_to(ROOT).as_posix()]=sha(p)
  save(out/'manifest.json',dict(inputs_sha256=inputs,command=[sys.executable,*sys.argv],cwd=str(ROOT),timestamp=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),limits=dict(seconds=120,working_set_bytes=512*1024**2),research_CNF_built=False,native_calls=0))
  ctrl=controls();raw=read(B/'20260930_hadamard20_support/six_prism.json');model=read(B/'20260930_hadamard_count_master_cnf/model.json');G=raw['prescribed_Gram36'];need(model['groups']==[list(x)for x in dict.fromkeys(tuple(s)for s in raw['support_columns'])],'literal first occurrence groups');zero=positive=0
  need(read(B/'20260930_independent_review/hadamard_count_master_cnf_v2/summary.json')['status']=='INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS','actual independent base encoding status')
  need(sum(len(d['values'])for d in model['count_channels'])==927 and all(len(v)==3 and sum(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for d in model['count_channels']for v in d['values']),'complete927 integer count triples')
  for u,v in combinations(range(36),2):
   a,b=u%12,v%12
   if a!=b and a^1!=b:need(G[u][v]==(1 if u//12==v//12 else 2),'nonzero Gram target');positive+=1
   else:need(G[u][v]==0,'structural zero');zero+=1
  need(positive==540 and zero==90 and all(G[i][i]==10 for i in range(36)),'complete666 Gram decomposition')
  for d in model['coordinate_domains']:
   for table in d['count_tables']:need(all(sum(c[h]for c in table)==10 for h in range(3)),'master row totals10')
  local=read(B/'20260930_hadamard_triplicate_counts/local_triples.json');words=local['words'];tri=local['survivors'];known=read(B/'20260930_independent_review/count_master_sat_outcome/independent_count_profile.json');balanced=next(s['index']for s in model['local_signatures']if s['counts']==[1]*18);positives=[]
  for name,sids in [('balanced',[balanced]*20),('verified_eight_count_only',known['selected_global_signature_indices'])]:
   tables=[]
   for g,sid in enumerate(sids):
    s=model['local_signatures'][sid];option=tri[s['local_survivor_indices'][0]];actual=[sum(words[w][p]==h for w in option)for p in range(6)for h in range(3)];need(actual==s['counts'],'positive raw local count link');tables.append(actual)
   need(all(sum(tables[g][3*support.index(a)+h]for g,support in enumerate(model['groups'])if a in support)==10 for a,h in product(range(12),range(3))),'positive36 margins');positives.append(dict(name=name,group_count=20,full_Gram_asserted=False))
  ctrl['raw_count_only_positive_controls']=positives;save(out/'controls.json',ctrl);budget(t);records=[]
  for variant in ('standalone','baseline','at_least_seven'):
   result=inventory(variant,model,raw,t);save(out/f'{variant}_inventory.json',result);records.append({k:result[k]for k in ['variant','within_only','all_caps','optional_cross_cap_suffix']});print(json.dumps(records[-1]),flush=True)
  supports=raw['support_columns'];hist=Counter(len(set(supports[d])&set(supports[e]))for d,e in combinations(range(60),2));summary=dict(status='CANDIDATE_DIRECT_CELL_COUNT_GRAM_PREFLIGHT_COMPLETE',inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()},variants=records,raw_cells=1080,Gram_products=8100,full_Gram=dict(diagonal=36,nonzero_offdiagonal=540,structural_zero=90),all_column_pair_intersection_histogram=dict(hist),observed_peak_working_set_bytes=peak(),elapsed_seconds=time.monotonic()-t,research_CNF_built=False,native_calls=0,independent_approval=False,artifact_availability='LOCAL_ONLY',scope='One literalL, full integerGram and within caps; all crosscaps separately inventoried, noD; ≥7 is a separate additional target-family restriction.',solver_performance_unknown=True)
  save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ('inputs_sha256','outputs_sha256','variants')}))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-t));raise
if __name__=='__main__':main()
