"""Candidate full separate-block DP screen, authenticated scalar population."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';S=B/'20260930_exact_eight_scalar_screen';RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
STATUS='INDEPENDENT_EXACT_EIGHT_SCALAR_INTERVAL_SCREEN_PASS'
PINS={S/'summary.json':'58a483301606ae9fcc418b10d091ef6bd524683fda513a79e7d536d07b3d953f',S/'surviving_representatives.json.gz':'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',ROOT/'acceleration/theory_20260930_third_count_profile_gram_diagnostic.py':'7dc9fe68ad427de8f6292898c9b14e0c62cbfe5a48efa2a5fb4eea00abbbd404',ROOT/'acceleration/theory_20260930_third_count_profile_gram_diagnostic_spec.md':'8b686bfe0f546d4b89be81d93d6e5705c27cef0216f039df49a0bc43b437867f'}
WITNESSES=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
def need(c,m):
 if not c:raise ValueError(m)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def gzread(p):
 with gzip.open(p,'rt',encoding='utf-8')as f:return json.load(f)
def save(p,d):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,indent=2);f.write('\n')
def gzsave(p,d):
 with Path(p).open('xb')as f:
  with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as g:g.write((json.dumps(d,separators=(',',':'))+'\n').encode())
def canonical(counts):
 v=tuple(x for row in counts for t in row for x in t);return min(tuple(v[k+p[f]]for k in range(0,len(v),3)for f in range(3))for p in permutations(range(3)))
def dp(populations,target,deadline=float('inf')):
 need(len(target)>0 and all(type(x)is int and x>=0 for x in target),'target integer shape')
 for pop in populations:need(len(pop)==len(set(map(tuple,pop)))and all(len(v)==len(target)and all(type(x)is int and x>=0 for x in v)for v in pop),'matrix population dimension/nonnegative/unique')
 layers=[dict(states=[[0]*len(target)],predecessors=[None],option_indices=[None],attempted_transitions=0,oversized_transitions=0)]
 for pop in populations:
  previous=layers[-1]['states'];reached={};attempted=0;oversized=0
  for si,state in enumerate(previous):
   if si%64==0 and time.perf_counter()>=deadline:raise TimeoutError('bounded DP deadline')
   for mi,m in enumerate(pop):
    attempted+=1;v=tuple(a+b for a,b in zip(state,m))
    if any(x>t for x,t in zip(v,target)):oversized+=1;continue
    reached.setdefault(v,(si,mi))
  now=sorted(reached);layers.append(dict(states=[list(v)for v in now],predecessors=[reached[v][0]for v in now],option_indices=[reached[v][1]for v in now],attempted_transitions=attempted,oversized_transitions=oversized))
 witness=None
 if list(target)in layers[-1]['states']:
  state_index=layers[-1]['states'].index(list(target));path=[]
  for layer in reversed(layers[1:]):path.append(layer['option_indices'][state_index]);state_index=layer['predecessors'][state_index]
  witness=list(reversed(path))
 return dict(target=list(target),populations=[[list(v)for v in p]for p in populations],layers=layers,feasible=witness is not None,witness_option_indices=witness)
def controls():
 n=0;universes=[[(0,0),(1,0)],[(0,1),(1,1)],[(0,0),(0,1)]]
 for masks in product(range(1,4),repeat=3):
  pops=[[v for i,v in enumerate(u)if mask>>i&1]for u,mask in zip(universes,masks)]
  for t in product(range(4),repeat=2):
   r=dp(pops,t)
   for k,layer in enumerate(r['layers']):
    sums={tuple(sum(v[i]for v in combo)for i in range(2))for combo in product(*pops[:k])};bounded=sorted(v for v in sums if all(x<=y for x,y in zip(v,t)));need(layer['states']==[list(v)for v in bounded],'all prefix exact Cartesian sets')
   n+=1
 ident=(1,0,0,0,1,0,0,0,1);cycle=(0,1,0,0,0,1,1,0,0);reverse=(0,0,1,1,0,0,0,1,0);pops=[[ident],[cycle],[cycle],[reverse],[reverse]];t=(1,2,2,2,1,2,2,2,1);r=dp(pops,t);need(r['feasible'],'balanced5matrix positive');need(not dp([*pops[:4],[]],t)['feasible']and not dp(pops,(0,*t[1:]))['feasible'],'essential member and RHS negative')
 rejected=[]
 def reject(name,fn):
  try:fn()
  except(ValueError,IndexError):rejected.append(name)
  else:raise ValueError('accepted corruption '+name)
 reject('dimension',lambda:dp([[(1,2,3)]],(1,2)));reject('negative_target',lambda:dp([[(0,)]],(-1,)));reject('negative_entry',lambda:dp([[(-1,)]],(1,)));reject('duplicate_matrix',lambda:dp([[(0,),(0,)]],(1,)))
 corrupted=json.loads(json.dumps(r));corrupted['layers'][1]['predecessors'][0]=4
 reject('invalid_predecessor',lambda:need(all(0<=x<len(corrupted['layers'][i-1]['states'])for i,l in enumerate(corrupted['layers'][1:],1)for x in l['predecessors']),'predecessors'))
 return dict(tiny_complete_prefix_cases=n,positive_permutation_block=True,negative_essential_member_and_rhs=True,malformed_controls=rejected,full_factor=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scalar-gate',type=Path,required=True);ap.add_argument('--scalar-gate-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume-from',type=Path);ap.add_argument('--resume-summary-sha256');args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();deadline=start+120;pins={}
 def pin(p,h=None):
  v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
 try:
  pin(args.scalar_gate,args.scalar_gate_sha256);gate=read(args.scalar_gate);need(gate['status']==STATUS,'independent scalar gate');gp=gate['inputs_sha256']
  for p,h in PINS.items():pin(p,h)
  for p in [S/'summary.json',S/'surviving_representatives.json.gz',RAW,LOCAL]:need(gp.get(key(p))==PINS[p],'gate direct input '+key(p))
  for name,h in read(S/'summary.json')['outputs_sha256'].items():pin(ROOT/name,h);need(gp.get(name)==h,'scalar gate full output '+name)
  for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  control=controls();raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));local=read(LOCAL);words=local['words'];triples=local['survivors'];partition=defaultdict(list)
  for i,t in enumerate(triples):partition[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
  sigs=sorted(partition);index={s:i for i,s in enumerate(sigs)};need(len(sigs)==6061 and len(triples)==31110,'full raw count classes');pairs=[(a,b)for a,b in combinations(range(12),2)if a^1!=b];K=raw['prescribed_Gram36'];C=raw['core_adjacency'];need(K==[[12*int(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)],'literal complete Gram')
  data=gzread(S/'surviving_representatives.json.gz');reps=data['records'];need(data['complete']and len(reps)==792 and len({r['canonical_fibre_profile_sha256']for r in reps})==792,'complete scalar survivors');ordered=[r['canonical_fibre_profile_sha256']for r in reps];pool={};cache={};cache_uses=0;completed=[];partial=None
  def projection(si,p,q):
   name=f'{si}:{p}:{q}'
   if name not in pool:
    by=defaultdict(list)
    for ti in partition[sigs[si]]:
     m=[0]*9
     for w in triples[ti]:m[3*words[w][p]+words[w][q]]+=1
     by[tuple(m)].append(ti)
    matrices=sorted(by);pool[name]=dict(projection_key=name,signature_index=si,signature_counts=list(sigs[si]),local_positions=[p,q],full_local_survivor_indices=partition[sigs[si]],matrices=[list(m)for m in matrices],realizing_local_indices=[by[m]for m in matrices])
   return pool[name]
  def block_inputs(counts,a,b):
   records=[];pops=[]
   for g,s in enumerate(groups):
    if a in s and b in s:
     si=index[tuple(x for x in s for x in counts[x][g])];pr=projection(si,s.index(a),s.index(b));records.append(dict(group=g,projection_key=pr['projection_key']));pops.append(pr['matrices'])
   target=[K[12*f+a][12*h+b]for f in range(3)for h in range(3)];need(len(pops)==5 and target==[1,2,2,2,1,2,2,2,1],'literal five-group target');return records,pops,target
  # Historical positives are controls and do not remove any population members.
  historical=[]
  for label,folder,h in WITNESSES:
   p=B/f'20260930_independent_review/{folder}/independent_count_profile.json';pin(p,h);w=read(p);counts=w['coordinate_group_fibre_counts'];dg=hashlib.sha256(bytes(canonical(counts))).hexdigest()
   if label=='second':need(dg not in ordered,'second scalar failure outside population');historical.append(dict(label=label,canonical_digest=dg,in_population=False,blocks_checked=0));continue
   need(dg in ordered,'historical positive in population')
   for a,b in pairs:
    gr,pops,t=block_inputs(counts,a,b);need(dp(pops,t,deadline)['feasible'],'first/third complete separate-block positives')
   historical.append(dict(label=label,canonical_digest=dg,in_population=True,blocks_checked=60,all_feasible=True))
  control['historical_memberships']=historical;save(out/'controls.json',control)
  if args.resume_from:
   need(args.resume_summary_sha256,'resume digest required');rp=args.resume_from.resolve()/'summary.json';pin(rp,args.resume_summary_sha256);prior=read(rp);need(prior['producer_sha256']==sha(Path(__file__))and prior['spec_sha256']==sha(SPEC)and prior['scalar_gate_sha256']==args.scalar_gate_sha256 and prior['ordered_representatives']==ordered,'exact resume scope/source/gate')
   completed=prior['completed_profile_records'];cache=prior['cache_records']
   for i,r in enumerate(completed):need(r['profile_index']==i and r['canonical_fibre_profile_sha256']==ordered[i]and r['complete'],'completed profile prefix');pin(ROOT/r['path'],r['sha256'])
   for k,r in cache.items():pin(ROOT/r['path'],r['sha256']);certificate=gzread(ROOT/r['path']);need(hashlib.sha256(json.dumps(certificate['cache_key'],separators=(',',':')).encode()).hexdigest()==k,'resume literal cache key')
   pp=ROOT/prior['projection_catalogue']['path'];pin(pp,prior['projection_catalogue']['sha256'])
   for old in gzread(pp)['records']:need(projection(old['signature_index'],*old['local_positions'])==old,'resumed exact raw projection')
  else:need(args.resume_summary_sha256 is None,'orphan resume digest')
  (out/'cache').mkdir();save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limit_seconds=120,ordered_representatives=ordered,resume_completed_prefix=len(completed),cache_semantics='Only exact ordered five-population/target JSON equality; computational reuse, not independent cases.',algorithm_reference='Frozen third-profile producer recurrence only; no repository imports or independent approval.'))
  for pi in range(len(completed),len(reps)):
   rep=reps[pi];results=[]
   try:
    for qi,(a,b)in enumerate(pairs):
     if time.perf_counter()>=deadline:raise TimeoutError('profile/pair boundary')
     gr,pops,t=block_inputs(rep['counts'],a,b);ck=dict(target=t,populations=pops);cid=hashlib.sha256(json.dumps(ck,separators=(',',':')).encode()).hexdigest();hit=cid in cache
     if hit:
      cert=gzread(ROOT/cache[cid]['path']);need(cert['cache_key']==ck,'literal cache equality');cache_uses+=1
     else:
      result=dp(pops,t,deadline);need(result['feasible']or not result['layers'][-1]['states'],'failed final reachable set empty');cert=dict(cache_key=ck,DP=result,first_empty_layer=next((i for i,l in enumerate(result['layers'])if not l['states']),None));cp=out/'cache'/f'{cid}.json.gz';gzsave(cp,cert);cache[cid]=dict(path=key(cp),sha256=sha(cp),feasible=result['feasible'],layer_sizes=[len(l['states'])for l in result['layers']])
     result=cert['DP'];w=None
     if result['feasible']:
      w=[dict(group=g['group'],projection_key=g['projection_key'],matrix_index=mi,matrix=pool[g['projection_key']]['matrices'][mi],local_survivor_index=pool[g['projection_key']]['realizing_local_indices'][mi][0])for g,mi in zip(gr,result['witness_option_indices'])];need([sum(x['matrix'][k]for x in w)for k in range(9)]==t,'positive literal combination')
     results.append(dict(pair_index=qi,coordinates=[a,b],target=t,group_projections=gr,cache_key_sha256=cid,cache_path=cache[cid]['path'],cache_sha256=cache[cid]['sha256'],cache_reused=hit,feasible=result['feasible'],witness=w))
   except TimeoutError:
    partial=dict(profile_index=pi,canonical_fibre_profile_sha256=ordered[pi],complete=False,pairs_completed=len(results),records=results);save(out/'partial_profile.json',partial);break
   path=out/f'profile_{pi:04d}.json.gz';fail=[r['pair_index']for r in results if not r['feasible']];gzsave(path,dict(profile_index=pi,representative=rep,complete=True,records=results,failed_pairs=fail,scope='Sixty separate choices, not a joint factor.'));rec=dict(profile_index=pi,canonical_fibre_profile_sha256=ordered[pi],complete=True,failed_pairs=fail,path=key(path),sha256=sha(path));completed.append(rec)
   if (pi+1)%50==0:save(out/f'checkpoint_{pi+1:04d}.json',dict(completed=len(completed),selected=792,completed_profile_records=completed,unique_DP_cache_entries=len(cache)));print(json.dumps(dict(completed=len(completed),excluded=sum(bool(r['failed_pairs'])for r in completed),cache_entries=len(cache),elapsed_seconds=time.perf_counter()-start)),flush=True)
  projection_path=out/'projection_catalogue.json.gz';gzsave(projection_path,dict(records=[pool[k]for k in sorted(pool)],complete_for_saved_profiles=True));excluded=[reps[r['profile_index']]for r in completed if r['failed_pairs']];survived=[reps[r['profile_index']]for r in completed if not r['failed_pairs']];gzsave(out/'excluded_representatives.json.gz',dict(complete=len(completed)==792,records=excluded));gzsave(out/'surviving_representatives.json.gz',dict(complete=len(completed)==792,records=survived));result=dict(status='CANDIDATE_COMPLETE_EXACT_EIGHT_SEPARATE_BLOCK_SCREEN'if len(completed)==792 else'CANDIDATE_PARTIAL_EXACT_EIGHT_SEPARATE_BLOCK_SCREEN',producer_sha256=sha(Path(__file__)),spec_sha256=sha(SPEC),scalar_gate_sha256=args.scalar_gate_sha256,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},ordered_representatives=ordered,completed_profile_records=completed,partial_profile=partial,cache_records=cache,projection_catalogue=dict(path=key(projection_path),sha256=sha(projection_path)),complete=len(completed)==792,representatives_checked=len(completed),representatives_excluded=len(excluded),representatives_surviving=len(survived),complete_profile_pair_tests=60*len(completed),unique_DP_cache_entries=len(cache),cache_hits_this_run=cache_uses,elapsed_seconds=time.perf_counter()-start,native_calls=0,independent_approval=False,prior_exclusions_subtracted=False,scope='Separate exact necessary3x3Gram blocks only; local within-group caps inherited. No cross-group caps, joint consistency, AC or residualD claim.');save(out/'summary.json',result);print(json.dumps({k:result[k]for k in('status','complete','representatives_checked','representatives_excluded','representatives_surviving','unique_DP_cache_entries','elapsed_seconds')}));print('summary_sha256',sha(out/'summary.json'))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
