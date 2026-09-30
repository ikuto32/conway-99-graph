"""Gated candidate complete count-table join; no SAT/native calls."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import permutations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';P=B/'20260930_exact_eight_profile_preflight';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
STATUS='INDEPENDENT_EXACT_EIGHT_PROFILE_PREFLIGHT_PASS'
PINS={P/'summary.json':'a479ab298a74884df96dc946ed15c94a7245b1b3312779aacea6f56de43ff2dc',P/'subset_inventory.jsonl':'ede227a007f13679750fe1eb8c2ffa5c201c996c632beef33f36abfa89b88f5b',P/'manifest.json':'6342c838e16ae002009e4eec28789dfc72a9be1cba683c28876ec64e95bc18bd',ROOT/'acceleration/theory_20260930_exact_eight_profile_preflight.py':'178de3c5bd8d204c50f6940e8c14a47b87b3b3726a780cfcb65b617aac3e670b',ROOT/'acceleration/theory_20260930_exact_eight_profile_preflight_spec.md':'a887964592b52b4b1c1b126e5fe74da61a66932bd87706c7473cf848f9f0c27d'}
WITNESSES=[('count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
def need(c,m):
 if not c:raise ValueError(m)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,indent=2);f.write('\n')
def code(t):return 16*t[0]+4*t[1]+t[2]
def digest_counts(flat):return hashlib.sha256(bytes(flat)).hexdigest()
def canonical(flat):
 images=[(tuple(flat[k+p[f]]for k in range(0,len(flat),3)for f in range(3)),p)for p in permutations(range(3))];best,perm=min(images);return best,perm,len({x for x,p in images})
def walk(domains,updates,masks,order,onleaf,deadline):
 assigned=[None]*len(domains);nodes=0;complete=True
 def visit(depth,live):
  nonlocal nodes,complete
  nodes+=1
  if time.perf_counter()>=deadline:complete=False;return
  if depth==len(order):onleaf(tuple(assigned),live);return
  a=order[depth]
  for i in domains[a]:
   nxt=live.copy();ok=True
   for g,mask in updates[a][i]:
    nxt[g]&=mask
    if not nxt[g]:ok=False;break
   if ok:assigned[a]=i;visit(depth+1,nxt)
   if not complete:return
 if all(masks):visit(0,masks)
 return nodes,complete
def controls():
 checks=0
 for l in range(16):
  for r in range(16):
   tables=[[(a,b)for a,b in product(range(2),repeat=2)if bits>>(2*a+b)&1]for bits in(l,r)];updates=[{}for _ in range(3)]
   for a in range(3):
    for v in range(2):updates[a][v]=[(g,sum(1<<i for i,t in enumerate(tables[g])if t[a-g]==v))for g in range(2)if g<=a<=g+1]
   got=[];nodes,complete=walk([range(2)]*3,updates,[(1<<len(t))-1 for t in tables],[0,1,2],lambda x,m:got.append(x),float('inf'));expected=[x for x in product(range(2),repeat=3)if x[:2]in tables[0]and x[1:]in tables[1]];need(complete and got==expected,'all256 actual DFS/Cartesian controls');checks+=1
 need(canonical((0,1,2))[2]==6 and canonical((0,0,3))[2]==3 and canonical((1,1,1))[2]==1,'nonfree S3 positive controls')
 rejected=[]
 def reject(name,fn):
  try:fn()
  except ValueError:rejected.append(name)
  else:raise ValueError('accepted '+name)
 reject('wrong_orbit_size',lambda:need(canonical((0,0,3))[2]==6,'orbit'))
 reject('false_hash',lambda:need(hashlib.sha256(b'changed').hexdigest()==hashlib.sha256(b'original').hexdigest(),'hash'))
 reject('duplicate_coordinate_ids',lambda:need(len(set([0,1,1]))==3,'coordinate uniqueness'))
 return dict(exhaustive_tiny_relation_pairs=checks,Cartesian_assignments_per_pair=8,actual_DFS_used=True,S3_control_orbit_sizes=[1,3,6],rejected_corruptions=rejected,full_factor=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight-gate',type=Path,required=True);ap.add_argument('--preflight-gate-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume-from',type=Path);ap.add_argument('--resume-summary-sha256');args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();deadline=start+120;pins={}
 def pin(p,h=None):
  v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
 try:
  pin(args.preflight_gate,args.preflight_gate_sha256);gate=read(args.preflight_gate);need(gate['status']==STATUS,'independent preflight status');gatepins=gate['inputs_sha256']
  for p,h in PINS.items():pin(p,h);need(gatepins.get(key(p))==h,'gate direct preflight input '+key(p))
  inputpins=read(P/'manifest.json')['inputs_sha256']
  for k,h in inputpins.items():pin(ROOT/k,h);need(gatepins.get(k)==h,'gate raw domain input '+k)
  for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  ctrl=controls();raw=read(B/'20260930_hadamard20_support/six_prism.json');groups=[]
  for col in zip(*raw['L']):
   s=tuple(a for a,x in enumerate(col)if x)
   if s not in groups:groups.append(s)
  need(len(groups)==20,'support groups');local=read(B/'20260930_hadamard_triplicate_counts/local_triples.json');words=local['words'];sigs=sorted({tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))for t in local['survivors']});need(len(sigs)==6061,'raw signatures');balance=sigs.index((1,)*18);balbit=1<<balance;allbits=(1<<len(sigs))-1;inv=[defaultdict(int)for _ in range(6)]
  for i,s in enumerate(sigs):
   for p in range(6):inv[p][code(s[3*p:3*p+3])]|=1<<i
  choices=[];values=[];coordinate_lookup=[]
  for a in range(12):
   path=B/f'20260930_hadamard_coordinate_marginal_domains/coordinate_{a:02d}.json';pin(path,inputpins[key(path)]);cs=read(path)['ordered_three_fibre_choices'];choices.append(cs);values.append([tuple(code(t)for t in c['full20_count_signature'])for c in cs]);lookup={v:i for i,v in enumerate(values[a])};need(len(lookup)==len(cs),'unique coordinate domains');coordinate_lookup.append(lookup)
  records=[json.loads(l)for l in(P/'subset_inventory.jsonl').read_text().splitlines()];need(len(records)==4184,'complete reduction population');surv=sorted([r for r in records if r['status']=='GAC_NONEMPTY'],key=lambda r:r['groups']);need(len(surv)==67 and sum(r['status']=='ACTIVITY_CANNOT_COVER'for r in records)==3847 and sum(r['status']=='GAC_EMPTY'for r in records)==270,'exact independent partition');need(len({tuple(r['groups'])for r in surv})==67,'no subset duplicates');selected=[r['groups']for r in surv]
  positives=[]
  for name,h in WITNESSES:
   p=B/f'20260930_independent_review/{name}/independent_count_profile.json';pin(p,h);w=read(p);table=w['coordinate_group_fibre_counts'];need(all(tuple(code(t)for t in table[a])in coordinate_lookup[a]for a in range(12)),'positive coordinate membership');need(all(tuple(x for a in support for x in table[a][g])in sigs for g,support in enumerate(groups)),'positive group signatures');rec=next(r for r in surv if r['groups']==w['exceptional_groups']);need(all(coordinate_lookup[a][tuple(code(t)for t in table[a])]in rec['coordinate_choice_indices'][a]for a in range(12)),'positive preflight domains');positives.append(dict(path=key(p),sha256=h,groups=w['exceptional_groups']));bad=list(table[0]);bad[groups.index(next(s for s in groups if 0 in s))]=[3,3,3];need(tuple(code(t)for t in bad)not in coordinate_lookup[0],'corrupted witness count rejected')
  ctrl['authentic_count_positives']=positives;ctrl['corrupted_counts_rejected']=3;save(out/'controls.json',ctrl)
  completed=[]
  if args.resume_from:
   need(args.resume_summary_sha256,'resume hash required');rp=args.resume_from.resolve()/'summary.json';pin(rp,args.resume_summary_sha256);prior=read(rp);need(prior['producer_sha256']==sha(Path(__file__))and prior['spec_sha256']==sha(SPEC)and prior['preflight_gate_sha256']==args.preflight_gate_sha256,'same resume producer/spec/gate');need(prior['selected_subsets']==selected,'same resume universe');completed=prior['completed_subset_records']
   for i,c in enumerate(completed):
    need(c['subset_index']==i and c['groups']==selected[i]and c['complete'],'completed exact prefix')
    for name,h in c['artifacts_sha256'].items():pin(ROOT/name,h)
  else:need(args.resume_summary_sha256 is None,'orphan resume hash')
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),gate_status=STATUS,limit_seconds=120,selected_subsets=selected,resume_completed_prefix=len(completed),native_calls=0,shared_components='Raw independently checked catalogue/domain/census artifacts only; no repository imports.'))
  partial=None
  for si in range(len(completed),len(surv)):
   if time.perf_counter()>=deadline:break
   rec=surv[si];E=rec['groups'];active=set(E);dom=rec['coordinate_choice_indices'];need(all(len(d)==len(set(d))and all(type(i)is int and 0<=i<len(choices[a])for i in d)for a,d in enumerate(dom)),'valid complete coordinate domains');masks=[allbits^balbit if g in active else balbit for g in range(20)]
   for g in E:
    for p,a in enumerate(groups[g]):
     allowed=0
     for x in {values[a][i][g]for i in dom[a]}:allowed|=inv[p][x]
     masks[g]&=allowed
   need(all(masks),'gated GAC positive');updates=[{}for _ in range(12)]
   for a in range(12):
    for i in dom[a]:updates[a][i]=[(g,inv[groups[g].index(a)][values[a][i][g]])for g in range(20)if a in groups[g]]
   order=sorted(range(12),key=lambda a:(len(dom[a]),a));folder=out/f'subset_{si:03d}';folder.mkdir();path=folder/'profiles.jsonl.gz';orbit={};n=0;tick=time.perf_counter()
   with path.open('xb')as packed:
    with gzip.GzipFile(fileobj=packed,mode='wb',mtime=0,filename='')as stream:
     def leaf(ids,live):
      nonlocal n
      need(all(x and x&(x-1)==0 for x in live),'unique20 signatures');table=[choices[a][ids[a]]['full20_count_signature']for a in range(12)];actual=[g for g,s in enumerate(groups)if any(table[a][g]!=[1,1,1]for a in s)];need(actual==E,'exact exception set');flat=tuple(x for row in table for t in row for x in t);can,perm,os=canonical(flat);dg=digest_counts(flat);cg=digest_counts(can);entry=orbit.setdefault(cg,dict(canonical_counts=list(can),orbit_size=os,members=[]));need(entry['canonical_counts']==list(can)and entry['orbit_size']==os,'canonical collision check');entry['members'].append(dict(index=n,profile_sha256=dg,canonicalizing_fibre_permutation=list(perm)));record=dict(index=n,coordinate_choice_indices=list(ids),group_signature_indices=[x.bit_length()-1 for x in live],coordinate_group_fibre_counts=table,exceptional_groups=E,profile_sha256=dg,canonical_fibre_profile_sha256=cg,canonicalizing_fibre_permutation=list(perm),fibre_orbit_size=os);stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());n+=1
     nodes,complete=walk(dom,updates,masks,order,leaf,deadline)
   if complete:need(all(len(v['members'])==v['orbit_size']and len({m['profile_sha256']for m in v['members']})==len(v['members'])for v in orbit.values()),'complete distinct fibre orbits')
   save(folder/'orbits.json',dict(complete=complete,orbits=[dict(canonical_fibre_profile_sha256=k,**v)for k,v in sorted(orbit.items())]));c=dict(subset_index=si,groups=E,complete=complete,labelled_profiles=n,fibre_orbits=len(orbit),coordinate_order=order,nodes=nodes,elapsed_seconds=time.perf_counter()-tick,artifacts_sha256={key(p):sha(p)for p in folder.iterdir()});save(folder/'summary.json',c);c['artifacts_sha256'][key(folder/'summary.json')]=sha(folder/'summary.json')
   if complete:completed.append(c);save(out/f'checkpoint_{si+1:03d}.json',dict(completed=len(completed),selected=67,labelled_profiles=sum(x['labelled_profiles']for x in completed),fibre_orbits=sum(x['fibre_orbits']for x in completed),completed_subset_records=completed))
   else:partial=c;break
   print(json.dumps(dict(completed=len(completed),labelled_profiles=sum(x['labelled_profiles']for x in completed),elapsed_seconds=time.perf_counter()-start)),flush=True)
  result=dict(status='CANDIDATE_COMPLETE_EXACT_EIGHT_COUNT_PROFILE_JOIN'if len(completed)==67 else'CANDIDATE_PARTIAL_EXACT_EIGHT_COUNT_PROFILE_JOIN',producer_sha256=sha(Path(__file__)),spec_sha256=sha(SPEC),preflight_gate_sha256=args.preflight_gate_sha256,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},selected_subsets=selected,completed_subset_records=completed,incomplete_subset=partial,unattempted_subsets=selected[len(completed)+(partial is not None):],complete=len(completed)==67,labelled_profiles=sum(x['labelled_profiles']for x in completed),fibre_orbits=sum(x['fibre_orbits']for x in completed),elapsed_seconds=time.perf_counter()-start,native_calls=0,independent_approval=False,scope='Exact necessary count-table profiles only; no full Gram/cross-group caps/residual D/full factor. Earlier literal exclusions were not subtracted.')
  save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],complete=result['complete'],labelled_profiles=result['labelled_profiles'],fibre_orbits=result['fibre_orbits'],summary_sha256=sha(out/'summary.json'))))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
