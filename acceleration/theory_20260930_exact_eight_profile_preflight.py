"""Candidate exact-eight count-table universe preflight; no native solver."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,hashlib,json,math,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';COORD=B/'20260930_hadamard_coordinate_marginal_domains';REM=B/'20260930_hadamard_eight_exception_census/remaining_candidates.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',REM:'b397429f8352baee4e7e16bd42f4d191e5d916823011d1d4ffbb7bed4082f2f6',COORD/'summary.json':'3382d4f11eeba3259300ae0e8361b434afc671353e3a2a83823668de63b0410f',B/'20260930_independent_review/coordinate_marginal_domains/summary.json':'9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39',B/'20260930_independent_review/hadamard_eight_exception_census/summary.json':'95176ae42241c3745fe1e017fbeca3798b04bc49f1113455605c3ed928e204f6',B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',B/'20260930_independent_review/hadamard_count_master_preflight/summary.json':'5b23e5a188522c669128ec9f79ec8fb975d75e251c15be4ebc0857b96d4876b3'}
WITNESSES=[('count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
KNOWN=(1,3,5,11,13,15,18,19)
def need(c,m):
 if not c:raise ValueError(m)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,indent=2);f.write('\n')
def code(t):return 16*t[0]+4*t[1]+t[2]
def signature(words,t):return tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))
def tiny_controls():
 # Two variables over0,1,2 and one explicitly tabulated equality relation.
 rel={(0,0),(1,1),(2,2)};checks=0
 for l in range(1,8):
  for r in range(1,8):
   A={i for i in range(3)if l>>i&1};C={i for i in range(3)if r>>i&1};truth={(a,b)for a in A for b in C if(a,b)in rel};rows={t for t in rel if t[0]in A and t[1]in C};aa={t[0]for t in rows};bb={t[1]for t in rows};got={(a,b)for a in aa for b in bb if(a,b)in rel};need(got==truth,'tiny table propagation/Cartesian equality');checks+=1
 return dict(tiny_Cartesian_controls=checks,positive_count_objects=3,all_balanced_control=True,full_factor=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
 def pin(p,h=None):
  v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
 try:
  for p,h in PINS.items():pin(p,h)
  for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  raw=read(RAW);groups=[]
  for col in zip(*raw['L']):
   s=tuple(a for a,v in enumerate(col)if v)
   if s not in groups:groups.append(s)
  need(len(groups)==20 and all(len(s)==6 for s in groups),'20 groups')
  local=read(LOCAL);words=local['words'];triples=local['survivors'];sigs=sorted(set(signature(words,t)for t in triples));need(len(sigs)==6061 and len(triples)==31110,'signature census')
  balance=sigs.index((1,)*18);balbit=1<<balance;allbits=(1<<len(sigs))-1;inv=[{}for _ in range(6)]
  for i,s in enumerate(sigs):
   need(all(sum(s[3*p:3*p+3])==3 for p in range(6))and all(sum(s[3*p+f]for p in range(6))==6 for f in range(3)),'local margins')
   for p in range(6):v=code(s[3*p:3*p+3]);inv[p][v]=inv[p].get(v,0)|(1<<i)
  def validate_choice(a,c):
   counts=c['full20_count_signature'];need(len(counts)==20,'coordinate shape')
   need(all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)and sum(v)==(3 if a in groups[g]else 0)for g,v in enumerate(counts)),'coordinate bounds/support')
   delta=[[counts[g][f]-int(a in groups[g])for g in range(20)]for f in range(3)]
   need(all(sum(v)==0 and all(sum(v[g]for g,s in enumerate(groups)if b in s)==0 for b in range(12))for v in delta),'all literal marginals')
   mask=sum(1<<g for g in range(20)if a in groups[g]and counts[g]!=[1,1,1]);need(mask==c['activity_mask'],'activity');return mask,tuple(code(v)for v in counts)
  Ds=[];choices=[];seenkeys=[];coordsummary=read(COORD/'summary.json')
  for a in range(12):
   p=COORD/f'coordinate_{a:02d}.json';pin(p,coordsummary['outputs_sha256'][key(p)]);d=read(p);cs=d['ordered_three_fibre_choices'];keys=set();adapt=[]
   for i,c in enumerate(cs):
    counts=c['full20_count_signature'];need(c['index']==i and len(counts)==20,'coordinate index/shape');vals=tuple(code(v)for v in counts);need(vals not in keys,'duplicate coordinate choice');keys.add(vals)
    adapt.append(validate_choice(a,c))
   choices.append(cs);Ds.append(adapt);seenkeys.append(keys)
  need(sum(map(len,Ds))==2226,'coordinate total')
  controls=tiny_controls();rejected=[]
  def reject(name,fn):
   try:fn()
   except ValueError:rejected.append(name)
   else:raise ValueError('accepted corrupt '+name)
  bad=json.loads(json.dumps(choices[0][0]));bad['full20_count_signature'][groups.index(next(s for s in groups if 0 in s))][0]+=1
  reject('bad_margin',lambda:validate_choice(0,bad))
  bad_activity=json.loads(json.dumps(choices[0][0]));bad_activity['activity_mask']^=1
  reject('bad_activity',lambda:validate_choice(0,bad_activity))
  reject('duplicate_choice',lambda:need(len({(1,2),(1,2)})==2,'duplicates'))
  reject('bad_signature',lambda:need((0,)*18 in sigs,'signature'))
  for name,h in WITNESSES:
   p=B/f'20260930_independent_review/{name}/independent_count_profile.json';pin(p,h);w=read(p);table=w['coordinate_group_fibre_counts'];need(all(tuple(code(t)for t in table[a])in seenkeys[a]for a in range(12)),'positive coordinate witness');need(all(tuple(x for a in s for x in table[a][g])in sigs for g,s in enumerate(groups)),'positive signature witness')
  need(all(tuple(code((1,1,1)if a in s else(0,0,0))for s in groups)in seenkeys[a]for a in range(12)),'all-balanced positive')
  controls['corruptions_rejected']=rejected;save(out/'controls.json',controls)
  records=read(REM)['records'];need(len(records)==4184 and len({tuple(r['groups'])for r in records})==4184,'distinct retained subsets');positions=[[(g,groups[g].index(a))for g in range(20)if a in groups[g]]for a in range(12)]
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(total_seconds=120,AC_seconds=85,join_seconds_each=10,join_nodes=100000,join_leaves=20000),universe='4184 exact retained eight-subsets; no coordinate quotient; complete initial count-signature tables.',producer_imports=False,scope='Necessary count-table relaxation; no full factor.'))
  def gac(E,domains):
   active=set(E);gm=[allbits^balbit if g in active else balbit for g in range(20)];iterations=0
   while True:
    iterations+=1;changed=False
    for g in E:
     old=gm[g];v=old
     for p,a in enumerate(groups[g]):
      allowed=0
      for x in {Ds[a][i][1][g]for i in domains[a]}:allowed|=inv[p].get(x,0)
      v&=allowed
     gm[g]=v
     if not v:return None,gm,iterations
     changed|=v!=old
    for a in range(12):
     good={g:{x for x,bits in inv[p].items()if bits&gm[g]}for g,p in positions[a]if g in active};old=domains[a];new=[i for i in old if all(Ds[a][i][1][g]in good[g]for g in good)]
     if not new:return None,gm,iterations
     domains[a]=new;changed|=new!=old
    if not changed:return domains,gm,iterations
  completed=[];surviving={};start_ac=time.perf_counter()
  with(out/'subset_inventory.jsonl').open('x',encoding='utf-8',newline='\n')as log:
   for ri,r in enumerate(records):
    if time.perf_counter()-start_ac>85 or time.perf_counter()-start>90:break
    E=tuple(r['groups']);mask=sum(1<<g for g in E);dom=[[i for i,(m,v)in enumerate(Ds[a])if not(m&~mask)]for a in range(12)];before=list(map(len,dom));union=0
    for a in range(12):
     for i in dom[a]:union|=Ds[a][i][0]
    if union!=mask:after=None;gm=[];rounds=0;why='ACTIVITY_CANNOT_COVER'
    else:after,gm,rounds=gac(E,dom);why='GAC_EMPTY'if after is None else'GAC_NONEMPTY'
    rec=dict(retained_index=ri,original_index=r['index'],groups=E,rank=r['certificate']['rank'],before_sizes=before,before_Cartesian_product=math.prod(before),status=why,iterations=rounds,after_sizes=None if after is None else list(map(len,after)),after_Cartesian_product=0 if after is None else math.prod(map(len,after)),coordinate_choice_indices=after,group_signature_populations=[x.bit_count()for x in gm]);completed.append(rec);log.write(json.dumps(rec,separators=(',',':'))+'\n')
    if after is not None:surviving[E]=(after,gm)
    if ri%500==0:log.flush();print(json.dumps(dict(stage='GAC',completed=ri+1,nonempty=len(surviving),seconds=time.perf_counter()-start)),flush=True)
  inv_elapsed=time.perf_counter()-start_ac;save(out/'inventory_checkpoint.json',dict(completed=len(completed),total=4184,complete=len(completed)==4184,status_counts=dict(Counter(r['status']for r in completed)),elapsed_seconds=inv_elapsed))
  selected=[]
  if KNOWN in surviving:selected.append(KNOWN)
  if surviving:
   lex=min(surviving)
   if lex not in selected:selected.append(lex)
   rest=[E for E in surviving if E not in selected]
   if rest:selected.append(min(rest,key=lambda E:(math.prod(map(len,surviving[E][0])),E)))
  save(out/'join_selection.json',dict(groups=selected,rule='known, then lexicographically first, then distinct minimum post-AC product'))
  joins=[]
  for ji,E in enumerate(selected):
   if time.perf_counter()-start>110:break
   dom,gm=surviving[E];order=sorted(range(12),key=lambda a:(len(dom[a]),a));tick=time.perf_counter();nodes=0;leaves=0;aborted=False;orbit_sizes=Counter();canons=set();assigned=[None]*12
   with(out/f'join_{ji:02d}_leaves.jsonl').open('x',encoding='utf-8',newline='\n')as log:
    def visit(depth,masks):
     nonlocal nodes,leaves,aborted
     if aborted:return
     nodes+=1
     if nodes>=100000 or leaves>=20000 or time.perf_counter()-tick>=10 or time.perf_counter()-start>=118:aborted=True;return
     if depth==12:
      leaves+=1;flat=tuple(v for a in range(12)for g in E for v in choices[a][assigned[a]]['full20_count_signature'][g]);images=[tuple(flat[k+p[f]]for k in range(0,len(flat),3)for f in range(3))for p in permutations(range(3))];canon=min(images);orbit_sizes[len(set(images))]+=1;ch=hashlib.sha256(bytes(canon)).hexdigest();canons.add(ch);log.write(json.dumps(dict(coordinate_choice_indices=assigned,profile_counts_sha256=hashlib.sha256(bytes(flat)).hexdigest(),canonical_fibre_counts_sha256=ch,fibre_orbit_size=len(set(images))),separators=(',',':'))+'\n');return
     a=order[depth]
     for i in dom[a]:
      nextm=masks.copy();ok=True
      for g,p in positions[a]:
       if g in E:
        nextm[g]&=inv[p][Ds[a][i][1][g]]
        if not nextm[g]:ok=False;break
      if ok:assigned[a]=i;visit(depth+1,nextm)
      if aborted:return
    visit(0,gm.copy())
   result=dict(groups=E,coordinate_order=order,complete=not aborted,nodes=nodes,labelled_profiles_found=leaves,distinct_fibre_orbit_keys_found=len(canons),orbit_size_histogram=dict(orbit_sizes),elapsed_seconds=time.perf_counter()-tick,counts_are_lower_bounds=aborted,Cartesian_product=math.prod(map(len,dom)));joins.append(result);save(out/f'join_{ji:02d}_summary.json',result)
  result=dict(status='CANDIDATE_EXACT_EIGHT_COUNT_PROFILE_PREFLIGHT_COMPLETE'if len(completed)==4184 else'CANDIDATE_EXACT_EIGHT_COUNT_PROFILE_PREFLIGHT_PARTIAL',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},initial_eight_subsets=125970,prior_retained_subsets=4184,checked_subsets=len(completed),AC_complete=len(completed)==4184,status_counts=dict(Counter(r['status']for r in completed)),retained_rank_histogram=dict(Counter(r['rank']for r in completed if r['status']=='GAC_NONEMPTY')),sum_restricted_Cartesian_products=sum(r['before_Cartesian_product']for r in completed),sum_post_AC_Cartesian_products=sum(r['after_Cartesian_product']for r in completed),max_post_AC_Cartesian_product=max((r['after_Cartesian_product']for r in completed),default=0),joins=joins,elapsed_seconds=time.perf_counter()-start,native_calls=0,independent_approval=False,scope='Exactly-eight necessary count-table CSP only; inherited local caps. No full Gram, cross-group caps, D or factor claim.',next_step='Independently verify this restricted-domain/AC inventory, then exact memoized signature-bitset joins on the surviving subsets; do not treat preflight samples as complete coverage.')
  save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items()if k not in['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
