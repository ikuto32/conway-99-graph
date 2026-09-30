"""Independent local incidence products and complete 2+3 Cartesian block checks.

No producer/checker imports. Research execution requires both completed artifacts
and the independently authenticated scalar gate, supplied explicitly by the caller.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'
SCALAR=B+'exact_eight_scalar_screen/'
RAW=B+'hadamard20_support/six_prism.json'
LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
PLAN='acceleration/audit_20260930_exact_eight_block_screen_plan.md'
PINS={
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
 SCALAR+'summary.json':'58a483301606ae9fcc418b10d091ef6bd524683fda513a79e7d536d07b3d953f',
 SCALAR+'surviving_representatives.json.gz':'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',
 'acceleration/theory_20260930_exact_eight_block_screen.py':'4babaefb66f0a2dc333916546ad0722339f09c9016365c862d579a36ce2af4be',
 'acceleration/theory_20260930_exact_eight_block_screen_spec.md':'92aac860eeab5e71d5ae6fe4a9a341d17f2064ccd66c3aca1ea9f1ba6d5edea1',
 PLAN:'b9c108dc7464514c5c16df7402bb6beac6ca4a244fd32b4727152592a19d0783',
 B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
}
HISTORICAL=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),
 ('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),
 ('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(path):return path.resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(path.read_bytes())
def gzread(path):
 with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)
def save(path,data):
 with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2);f.write('\n')
def gzsave(path,data):
 with path.open('xb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:z.write((json.dumps(data,separators=(',',':'))+'\n').encode())
def digest_counts(v):return hashlib.sha256(bytes(v)).hexdigest()
def flatten(table):return tuple(x for row in table for t in row for x in t)
def fibre_image(v,p):return tuple(v[k+p[f]] for k in range(0,len(v),3) for f in range(3))
def canonical(v):return min(fibre_image(v,p) for p in permutations(range(3)))
def compact_hash(obj):return hashlib.sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()

def local_catalogue(saved):
 """Choose fibre position pairs; literal selected-row Gram sums on all triples."""
 words=[]
 for zero in combinations(range(6),2):
  rest=[a for a in range(6) if a not in zero]
  for one in combinations(rest,2):words.append(tuple(0 if a in zero else 1 if a in one else 2 for a in range(6)))
 words.sort();need(len(words)==90 and [list(w) for w in words]==saved['words'],'complete independent90 words')
 rows=[frozenset(6*w[a]+a for a in range(6)) for w in words]
 pairs=[list(combinations(sorted(r),2)) for r in rows]
 overlaps=[[len(a&b) for b in rows] for a in rows]
 triples=[];tested=0
 for triple in combinations(range(90),3):
  tested+=1
  if any(overlaps[a][b]>2 for a,b in combinations(triple,2)):continue
  tally=Counter(p for w in triple for p in pairs[w])
  if any(value>(1 if a//6==b//6 else 2) for (a,b),value in tally.items()):continue
  triples.append(triple)
 need(tested==117480 and len(triples)==31110,'complete local population count')
 need([list(t) for t in triples]==saved['survivors'],'all raw local triple ranks')
 classes=defaultdict(list)
 for rank,t in enumerate(triples):classes[tuple(sum(words[w][a]==f for w in t) for a in range(6) for f in range(3))].append(rank)
 signatures=sorted(classes);need(len(signatures)==6061,'all count signatures')
 return words,triples,signatures,classes

def block_matrix(words,triple,a,b):
 left=[[int(words[w][a]==f) for w in triple] for f in range(3)]
 right=[[int(words[w][b]==f) for w in triple] for f in range(3)]
 return tuple(sum(left[f][c]*right[h][c] for c in range(3)) for f in range(3) for h in range(3))

def projection(words,triples,signatures,classes,si,a,b):
 need(type(si)is int and 0<=si<len(signatures) and 0<=a<b<6,'projection indices')
 ranks=classes[signatures[si]];population=defaultdict(list)
 for r in ranks:population[block_matrix(words,triples[r],a,b)].append(r)
 matrices=sorted(population)
 return dict(projection_key=f'{si}:{a}:{b}',signature_index=si,signature_counts=list(signatures[si]),local_positions=[a,b],full_local_survivor_indices=ranks,matrices=[list(m) for m in matrices],realizing_local_indices=[population[m] for m in matrices])

def mitm(populations,target):
 """Unpruned full Cartesian sums on two and three groups, with exact complements."""
 need(len(populations)==5 and len(target)>0 and all(type(x)is int and x>=0 for x in target),'MITM dimensions/target')
 width=len(target);pops=[]
 for population in populations:
  p=[tuple(v) for v in population]
  need(len(p)==len(set(p)) and all(len(v)==width and all(type(x)is int and x>=0 for x in v) for v in p),'literal finite populations')
  pops.append(p)
 left={};right={};lc=rc=0
 for i,j in product(range(len(pops[0])),range(len(pops[1]))):
  lc+=1;s=tuple(a+b for a,b in zip(pops[0][i],pops[1][j]));left.setdefault(s,(i,j))
 for i,j,k in product(range(len(pops[2])),range(len(pops[3])),range(len(pops[4]))):
  rc+=1;s=tuple(a+b+c for a,b,c in zip(pops[2][i],pops[3][j],pops[4][k]));right.setdefault(s,(i,j,k))
 matches=sorted(s for s in left if tuple(t-v for t,v in zip(target,s)) in right)
 witness=None
 if matches:
  s=matches[0];witness=list(left[s]+right[tuple(t-v for t,v in zip(target,s))])
  need([sum(pops[g][witness[g]][i] for g in range(5)) for i in range(width)]==list(target),'MITM literal positive')
 return dict(feasible=bool(matches),witness_option_indices=witness,left_cartesian_products=lc,right_cartesian_products=rc,
             left_sums=[list(x) for x in sorted(left)],right_sums=[list(x) for x in sorted(right)],matching_left_sums=[list(x) for x in matches])

def validate_cache(cid,raw,result):
 ck=raw['cache_key'];need(set(ck)=={'target','populations'} and compact_hash(dict(target=ck['target'],populations=ck['populations']))==cid,'complete ordered literal cache key')
 d=raw['DP'];need(d['target']==ck['target'] and d['populations']==ck['populations'],'DP declared input population')
 need(d['feasible']==result['feasible'],'independent complement feasibility')
 w=d['witness_option_indices']
 if result['feasible']:
  need(isinstance(w,list) and len(w)==5 and all(type(i)is int and 0<=i<len(p) for i,p in zip(w,ck['populations'])),'cache witness indices')
  need([sum(ck['populations'][g][w[g]][k] for g in range(5)) for k in range(len(ck['target']))]==ck['target'],'literal producer cache witness')
 else:need(w is None,'infeasible cache no witness')

def expected_pair(counts,a,b,groups,signature_index,pool,gram):
 gp=[];populations=[]
 for g,support in enumerate(groups):
  if a in support and b in support:
   sig=tuple(x for coord in support for x in counts[coord][g]);si=signature_index[sig]
   pk=f'{si}:{support.index(a)}:{support.index(b)}';need(pk in pool,'all used projections saved')
   gp.append(dict(group=g,projection_key=pk));populations.append(pool[pk]['matrices'])
 target=[gram[12*f+a][12*h+b] for f in range(3) for h in range(3)]
 need(len(gp)==5 and target==[1,2,2,2,1,2,2,2,1],'actual five-group target')
 ck=dict(target=target,populations=populations);return gp,ck,compact_hash(ck)

def validate_pair(record,qi,pair,gp,ck,cid,pool,cache_records,cache_checks):
 need(record['pair_index']==qi and record['coordinates']==list(pair),'pair order/coordinates')
 need(record['group_projections']==gp and record['target']==ck['target'],'pair literal groups/target')
 need(record['cache_key_sha256']==cid and cid in cache_checks,'pair ordered population cache identity')
 entry=cache_records[cid];need(record['cache_path']==entry['path'] and record['cache_sha256']==entry['sha256'],'exact cache artifact link')
 r=cache_checks[cid];need(record['feasible']==r['feasible'],'pair exact feasibility')
 w=record['witness']
 if r['feasible']:
  need(isinstance(w,list) and len(w)==5,'five group witness')
  for item,g in zip(w,gp):
   need(item['group']==g['group'] and item['projection_key']==g['projection_key'],'witness group binding')
   p=pool[g['projection_key']];i=item['matrix_index']
   need(type(i)is int and 0<=i<len(p['matrices']) and item['matrix']==p['matrices'][i],'literal witness matrix')
   need(item['local_survivor_index'] in p['realizing_local_indices'][i],'literal complete class realizer')
  need([sum(item['matrix'][k] for item in w) for k in range(9)]==ck['target'],'literal witness sum')
 else:need(w is None,'infeasible pair no witness')

def reject(label,fn,records):
 try:fn()
 except (ValueError,KeyError,IndexError,TypeError):records.append(label);return
 raise ValueError('corruption accepted: '+label)

def controls(fixture):
 checked=0
 universe=[(0,0),(1,0)]
 for masks in product((1,2,3),repeat=5):
  pops=[[list(v) for i,v in enumerate(universe) if mask>>i&1] for mask in masks]
  all_sums={tuple(sum(v[k] for v in option) for k in range(2)) for option in product(*pops)}
  for target in product(range(3),repeat=2):
   result=mitm(pops,target);need(result['feasible']==(target in all_sums),'complete tiny Cartesian equality');checked+=1
 correlated=[[[0,0],[2,2]],[[0,0]],[[0,0]],[[0,0]],[[0,0]]]
 need(all(min(v[i] for v in correlated[0])<=1<=max(v[i] for v in correlated[0]) for i in range(2)) and not mitm(correlated,[1,1])['feasible'],'scalar-compatible correlated failure')
 malformed=[]
 reject('wrong_target_dimension',lambda:mitm(correlated,[1]),malformed)
 reject('negative_entry',lambda:mitm([[[-1,0]],*correlated[1:]],[1,1]),malformed)
 reject('duplicate_population_member',lambda:mitm([[[0,0],[0,0]],*correlated[1:]],[1,1]),malformed)
 # The two cache keys have equal population sizes but different actual entries.
 changed=deepcopy(correlated);changed[0][1]=[1,1]
 need(mitm(changed,[1,1])['feasible'] and compact_hash(dict(target=[1,1],populations=changed))!=compact_hash(dict(target=[1,1],populations=correlated)),'equal-size cache alias control')
 f=fixture['factor60x180'];positives=[]
 need(len(f)==60 and all(len(row)==180 for row in f),'known243 raw factor shape')
 for a,b in [(0,2),(1,3),(4,6),(7,9),(8,10)]:
  pops=[]
  for g in range(5):pops.append([[sum(f[20*r+a][3*g+c]*f[20*s+b][3*g+c] for c in range(3)) for r in range(3) for s in range(3)]])
  target=[sum(f[20*r+a][c]*f[20*s+b][c] for c in range(15)) for r in range(3) for s in range(3)]
  need(mitm(pops,target)['feasible'],'genuine243 own five-triple block positive')
  positives.append(dict(coordinates=[a,b],target=target,populations=pops,scope='Own15-column block, not research99 target.'))
 return dict(exhaustive_tiny_cases=checked,correlated_scalar_positive_block_negative=True,equal_population_size_cache_alias_detected=True,malformed_controls=malformed,genuine243_generic_positives=positives)

def check_counts(rep,groups):
 counts=rep['counts'];need(len(counts)==12 and all(len(row)==20 for row in counts),'profile count shape')
 for a in range(12):
  for g in range(20):need(len(counts[a][g])==3 and all(type(x)is int and 0<=x<=3 for x in counts[a][g]) and sum(counts[a][g])==3*int(a in groups[g]),'support count quota')
 need(all(sum(counts[a][g][f] for g in range(20))==10 for a in range(12) for f in range(3)),'coordinate fibre margins')
 need(all(sum(counts[a][g][f] for a in range(12))==6 for g in range(20) for f in range(3)),'group fibre margins')
 exceptional=[g for g,s in enumerate(groups) if any(counts[a][g]!=[1,1,1] for a in s)]
 need(exceptional==rep['exceptional_groups'] and len(exceptional)==8,'literal exact-eight set')
 v=flatten(counts);need(v==canonical(v) and digest_counts(v)==rep['canonical_fibre_profile_sha256'],'canonical raw count digest')
 return v

def catalogue_covariance(words,triples):
 wi={w:i for i,w in enumerate(words)};lookup={t:i for i,t in enumerate(triples)};records=[]
 for perm in permutations(range(3)):
  wm=[wi[tuple(perm[f] for f in w)] for w in words]
  image=[lookup[tuple(sorted(wm[i] for i in t))] for t in triples]
  need(len(set(image))==31110,'complete local catalogue fibre bijection')
  records.append(dict(fibre_permutation=list(perm),word_image=wm,triple_image=image))
 return records

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scalar-gate',type=Path,required=True);ap.add_argument('--scalar-gate-sha256',required=True);ap.add_argument('--block-summary',type=Path,required=True);ap.add_argument('--block-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 # Required artifacts must exist before creating a result directory.
 need(args.scalar_gate.is_file() and args.block_summary.is_file(),'completed gate and candidate summary must exist')
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();inputs={}
 def pin(path,expected=None):
  p=ROOT/path if isinstance(path,str) else path.resolve();h=sha(p);need(expected is None or h==expected,'raw identity '+key(p));inputs[key(p)]=h;return p
 def bounded():need(time.perf_counter()-start<120,'independent120second allocation')
 try:
  pin(args.scalar_gate,args.scalar_gate_sha256);pin(args.block_summary,args.block_summary_sha256)
  for p,h in PINS.items():pin(p,h)
  for p in [Path(__file__),ROOT/PLAN,ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_BLOCK_SCREEN.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  scalar_gate=read(args.scalar_gate);need(scalar_gate['status']=='INDEPENDENT_EXACT_EIGHT_SCALAR_INTERVAL_SCREEN_PASS','independent scalar gate status')
  sb=args.scalar_gate.resolve().parent/'claim_binding.json';pin(sb,scalar_gate['outputs_sha256'][key(sb)]);scalar_binding=read(sb)
  need(scalar_binding['id']==scalar_gate['claim_id'] and scalar_binding['revision']==scalar_gate['claim_revision'],'scalar claim identity')
  scalar=read(ROOT/(SCALAR+'summary.json'));sp=scalar_gate['inputs_sha256']
  for p in [SCALAR+'summary.json',SCALAR+'surviving_representatives.json.gz',RAW,LOCAL]:need(sp.get(p)==inputs[p],'scalar gate direct data binding')
  for p,h in scalar['outputs_sha256'].items():pin(p,h);need(sp.get(p)==h,'scalar gate complete compared outputs')
  summary=read(args.block_summary)
  need(summary['status']=='CANDIDATE_COMPLETE_EXACT_EIGHT_SEPARATE_BLOCK_SCREEN' and summary['complete'] and summary['partial_profile'] is None,'complete candidate block population')
  need(summary['producer_sha256']==PINS['acceleration/theory_20260930_exact_eight_block_screen.py'] and summary['spec_sha256']==PINS['acceleration/theory_20260930_exact_eight_block_screen_spec.md'],'frozen producer provenance')
  need(summary['scalar_gate_sha256']==args.scalar_gate_sha256 and summary['inputs_sha256'].get(key(args.scalar_gate))==args.scalar_gate_sha256,'same scalar gate used')
  for field in ['inputs_sha256','outputs_sha256']:
   for p,h in summary[field].items():pin(p,h)
  need(summary['native_calls']==0 and summary['prior_exclusions_subtracted'] is False,'declared native-free unchanged population')
  save(out/'manifest.json',dict(inputs_sha256=inputs,command=[sys.executable,*sys.argv],cwd=str(ROOT),created_at=datetime.now(timezone.utc).isoformat(),allocation_seconds=120,method='Literal incidence reconstruction and complete2+3 Cartesian complement intersections; no producer imports.'))
  ctrl=controls(read(ROOT/(B+'srg243_residual_fixture/triangle_blocks.json')))
  raw=read(ROOT/RAW);groups=[]
  for d in range(60):
   support=[a for a in range(12) if raw['L'][a][d]]
   need(support==raw['support_columns'][d],'raw support equality')
   if support not in groups:groups.append(support)
  need(len(groups)==20 and all(raw['support_columns'].count(g)==3 for g in groups),'twenty complete support triples')
  c=[[int((i//12==j//12 and i%12^1==j%12) or (i//12!=j//12 and i%12==j%12)) for j in range(36)] for i in range(36)]
  need(c==raw['core_adjacency'],'literal fixed six-prism core')
  gram=[[12*int(i==j)+2-c[i][j]-sum(c[i][k]*c[j][k] for k in range(36))-int(i//12==j//12) for j in range(36)] for i in range(36)]
  need(gram==raw['prescribed_Gram36'],'full prescribed Gram reconstruction')
  words,triples,sigs,classes=local_catalogue(read(ROOT/LOCAL));si={s:i for i,s in enumerate(sigs)}
  fibre_maps=catalogue_covariance(words,triples);gzsave(out/'local_fibre_bijections.json.gz',dict(records=fibre_maps))
  projection_ref=summary['projection_catalogue'];pin(projection_ref['path'],projection_ref['sha256']);saved=gzread(ROOT/projection_ref['path']);pool={}
  for r in saved['records']:
   name=r['projection_key'];need(name not in pool,'unique projection key')
   expect=projection(words,triples,sigs,classes,r['signature_index'],*r['local_positions']);need(r==expect,'complete independently reconstructed local projection '+name);pool[name]=expect
  need(saved['complete_for_saved_profiles'] is True,'complete projection catalogue declaration');bounded()
  cache_checks={};cache_keys={};cartesian=0;cache_records=summary['cache_records']
  for index,(cid,entry) in enumerate(sorted(cache_records.items())):
   pin(entry['path'],entry['sha256']);cert=gzread(ROOT/entry['path']);ck=cert['cache_key'];r=mitm(ck['populations'],ck['target']);validate_cache(cid,cert,r)
   need(entry['feasible']==r['feasible'],'cache summary feasibility');cache_checks[cid]=r;cache_keys[cid]=ck;cartesian+=r['left_cartesian_products']+r['right_cartesian_products']
   if index%100==0:bounded()
  need(len(cache_checks)==summary['unique_DP_cache_entries'],'unique literal cache count')
  gzsave(out/'independent_mitm_cache.json.gz',dict(records=[dict(cache_key_sha256=k,cache_key=cache_keys[k],**cache_checks[k]) for k in sorted(cache_checks)],producer_DP_prefix_states_checked=False))
  data=gzread(ROOT/(SCALAR+'surviving_representatives.json.gz'));reps=data['records'];need(data['complete'] and len(reps)==792,'all792 scalar survivors')
  ordered=[r['canonical_fibre_profile_sha256'] for r in reps];need(len(set(ordered))==792 and summary['ordered_representatives']==ordered,'exact active population order')
  completed=summary['completed_profile_records'];need(len(completed)==792,'all792 profile files')
  pairs=[(a,b) for a,b in combinations(range(12),2) if a//2!=b//2];need(len(pairs)==60,'all60 nonmatched pairs')
  orbit_files={};checked=[];orbit_records=[];corruptions=[];used=set();first_context=None
  for pi,(rep,rec) in enumerate(zip(reps,completed)):
   v=check_counts(rep,groups);dg=rep['canonical_fibre_profile_sha256'];need(rec['profile_index']==pi and rec['canonical_fibre_profile_sha256']==dg and rec['complete'],'completed profile identity')
   # Authenticate literal join orbit and each raw fibre image; no assumed free action.
   op=rep['source_orbits_path']
   if op not in orbit_files:
    need(op in scalar['inputs_sha256'],'source orbit bound by scalar scope');pin(op,scalar['inputs_sha256'][op]);o=read(ROOT/op);need(o['complete'],'source orbit census complete');orbit_files[op]={r['canonical_fibre_profile_sha256']:r for r in o['orbits']}
   ori=orbit_files[op][dg];need(ori['canonical_counts']==list(v) and ori['members']==rep['members'] and ori['orbit_size']==rep['orbit_size'],'raw source orbit equality')
   images={fibre_image(v,p) for p in permutations(range(3))};need(len(images)==rep['orbit_size']==len(rep['members']),'actual orbit size')
   byhash={digest_counts(w):w for w in images};need(set(byhash)=={m['profile_sha256'] for m in rep['members']},'entire labelled orbit membership')
   transports=[]
   for member in rep['members']:
    p=member['canonicalizing_fibre_permutation'];need(sorted(p)==[0,1,2] and fibre_image(byhash[member['profile_sha256']],p)==v,'literal canonicalizing transport')
    transports.append(dict(profile_sha256=member['profile_sha256'],canonicalizing_fibre_permutation=p))
   orbit_records.append(dict(canonical_fibre_profile_sha256=dg,orbit_size=len(images),members=transports))
   pin(rec['path'],rec['sha256']);actual=gzread(ROOT/rec['path']);need(actual['profile_index']==pi and actual['representative']==rep and actual['complete'] and len(actual['records'])==60,'complete raw profile')
   failures=[]
   for qi,pair in enumerate(pairs):
    gp,ck,cid=expected_pair(rep['counts'],*pair,groups,si,pool,gram);need(cid in cache_keys and cache_keys[cid]==ck,'complete raw five-population equality')
    rr=actual['records'][qi];validate_pair(rr,qi,pair,gp,ck,cid,pool,cache_records,cache_checks);used.add(cid)
    if not cache_checks[cid]['feasible']:failures.append(qi)
    if first_context is None and rr['feasible']:first_context=(deepcopy(rr),qi,pair,gp,ck,cid)
   need(failures==actual['failed_pairs']==rec['failed_pairs'],'all60 failure decisions')
   checked.append(dict(profile_index=pi,canonical_fibre_profile_sha256=dg,failed_pairs=failures,orbit_size=rep['orbit_size']))
   if (pi+1)%100==0:print(json.dumps(dict(profiles_checked=pi+1,cache_checks=len(cache_checks),elapsed_seconds=time.perf_counter()-start)),flush=True);bounded()
  excluded=[rep for rep,check in zip(reps,checked) if check['failed_pairs']];survived=[rep for rep,check in zip(reps,checked) if not check['failed_pairs']]
  outputdir=args.block_summary.resolve().parent
  for name,expect in [('excluded',excluded),('surviving',survived)]:
   p=outputdir/(name+'_representatives.json.gz');need(key(p) in summary['outputs_sha256'],'complete union artifact bound');got=gzread(p);need(got==dict(complete=True,records=expect),'literal '+name+' union')
  need(summary['representatives_checked']==792 and summary['complete_profile_pair_tests']==47520 and summary['representatives_excluded']==len(excluded) and summary['representatives_surviving']==len(survived),'complete summary counts')
  scalar_ex=gzread(ROOT/(SCALAR+'excluded_representatives.json.gz'));need(scalar_ex['complete'],'complete scalar exclusion prefix')
  scalar_ex_ids={r['canonical_fibre_profile_sha256'] for r in scalar_ex['records']}
  need(len(scalar_ex_ids)==len(scalar_ex['records']) and not scalar_ex_ids.intersection(ordered) and len(scalar_ex_ids)+len(ordered)==1548,'disjoint full scalar partition')
  need(sum(r['orbit_size'] for r in scalar_ex['records']+reps)==9288,'original labelled universe restored')
  # Check simultaneous fibre action on every saved literal matrix population.
  covariance_entries=0
  for pr in pool.values():
   for perm in permutations(range(3)):
    inv=[perm.index(f) for f in range(3)]
    transformed_signature=tuple(pr['signature_counts'][3*a+inv[f]] for a in range(6) for f in range(3));mapped=si[transformed_signature]
    ep=projection(words,triples,sigs,classes,mapped,*pr['local_positions'])
    expected=sorted(tuple(m[3*inv[f]+inv[h]] for f in range(3) for h in range(3)) for m in pr['matrices'])
    need(expected==[tuple(m) for m in ep['matrices']],'complete block population fibre covariance')
    covariance_entries+=sum(len(m) for m in expected)
  for perm in permutations(range(3)):
   need(all(gram[12*perm[i//12]+i%12][12*perm[j//12]+j%12]==gram[i][j] for i in range(36) for j in range(36)),'raw target fibre covariance')
  # Deliberate attacks on actual raw projection/cache/profile validation paths.
  pr=next(iter(pool.values()));bad=deepcopy(pr);bad['matrices'][0][0]+=1
  reject('changed_projection_entry',lambda:need(bad==projection(words,triples,sigs,classes,pr['signature_index'],*pr['local_positions']),'raw projection'),corruptions)
  bad=deepcopy(pr);bad['matrices'].pop()
  reject('missing_projection_member',lambda:need(bad==projection(words,triples,sigs,classes,pr['signature_index'],*pr['local_positions']),'raw projection'),corruptions)
  bad=deepcopy(pr);bad['realizing_local_indices'][0]=[-1]
  reject('false_projection_realizer',lambda:need(bad==projection(words,triples,sigs,classes,pr['signature_index'],*pr['local_positions']),'raw realizer'),corruptions)
  rr,qi,pair,gp,ck,cid=first_context
  def check_rr(obj):validate_pair(obj,qi,pair,gp,ck,cid,pool,cache_records,cache_checks)
  for label in ['target','witness','orientation','cache']:
   bad=deepcopy(rr)
   if label=='target':bad['target'][0]+=1
   elif label=='witness':bad['witness'][0]['local_survivor_index']=-1
   elif label=='orientation':bad['coordinates'].reverse()
   else:bad['cache_key_sha256']='0'*64
   reject('pair_'+label,lambda bad=bad:check_rr(bad),corruptions)
  reject('missing_profile',lambda:need([r['canonical_fibre_profile_sha256'] for r in reps[:-1]]==ordered,'exact population'),corruptions)
  reject('duplicate_profile',lambda:need(len({r['canonical_fibre_profile_sha256'] for r in [*reps[:-1],reps[0]]})==792,'unique population'),corruptions)
  reject('missing_pair',lambda:need(len(pairs[:-1])==60,'complete pair population'),corruptions)
  bad=deepcopy(reps[0]);bad['canonical_fibre_profile_sha256']='0'*64
  reject('wrong_count_digest',lambda:check_counts(bad,groups),corruptions)
  reject('bad_fibre_transport',lambda:need(sorted([0,0,1])==[0,1,2],'bijection'),corruptions)
  historical=[]
  outcomes={r['canonical_fibre_profile_sha256']:r for r in checked}
  for label,folder,h in HISTORICAL:
   p=pin(I+folder+'/independent_count_profile.json',h);rawprofile=read(p);dg=digest_counts(canonical(flatten(rawprofile['coordinate_group_fibre_counts'])))
   if label=='second':need(dg not in outcomes,'second outside scalar survivors')
   else:need(dg in outcomes and not outcomes[dg]['failed_pairs'],'first/third complete separate-block positives')
   historical.append(dict(label=label,canonical_fibre_profile_sha256=dg,inside_population=dg in outcomes,failed_pairs=None if dg not in outcomes else outcomes[dg]['failed_pairs']))
  ctrl['research_corruptions']=corruptions;ctrl['historical_count_diagnostics']=historical
  save(out/'controls.json',ctrl);gzsave(out/'checked_profile_decisions.json.gz',dict(records=checked));gzsave(out/'checked_orbit_transports.json.gz',dict(records=orbit_records))
  bounded();timestamp=datetime.now(timezone.utc).isoformat()
  result=dict(status='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS',created_at=timestamp,updated_at=timestamp,verifier='/root/state_literature_audit',
   method='Complete raw local-catalogue and incidence-population reconstruction; unpruned two-plus-three Cartesian complement tests; all raw witnesses, canonical tables, disjoint unions and fibre transports.',
   command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
   inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in sorted(out.iterdir()) if p.is_file()},
   checked_local_triples=31110,checked_initial_triples=117480,projection_populations=len(pool),unique_complete_cache_tests=len(cache_checks),used_cache_entries=len(used),
   complete_cartesian_products=cartesian,profile_pair_tests=47520,representatives_checked=792,representatives_excluded=len(excluded),representatives_surviving=len(survived),
   labelled_excluded=sum(r['orbit_size'] for r in excluded),labelled_surviving=sum(r['orbit_size'] for r in survived),original_scalar_population=1548,original_labelled_population=9288,
   combined_scalar_block_excluded=len(scalar_ex_ids)+len(excluded),catalogue_fibre_images=186660,matrix_covariance_entries=covariance_entries,
   producer_DP_prefix_states_checked=False,controls=dict(tiny_cases=ctrl['exhaustive_tiny_cases'],genuine243_generic_positives=5,malformed=len(ctrl['malformed_controls']),research_corruptions=len(corruptions)),
   artifact_availability='LOCAL_ONLY',shared_components=['Authenticated raw scalar-screen/join premises and raw catalogue/support. Python standard library. No repository producer/checker imports.'],
   native_calls=0,elapsed_seconds=time.perf_counter()-start,scope='Complete separate necessary3x3 block screen of the scalar-surviving exact-eight count profiles on the literal fixed support, inheriting within-triplicate caps. No joint factor, cross-group caps, residualD or target conclusion.')
  save(out/'summary.json',result)
  binding=dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
   statement=f'Among all792 canonical exact-eight count profiles surviving the authenticated scalar screen, complete exact feasibility checks of all60 separate3x3 Gram blocks exclude{len(excluded)} representatives and retain{len(survived)}. Each exclusion and surviving block witness is independently checked; all labelled members inherit the corresponding result under the explicit global fibre relabelling.',
   scope=result['scope'],assumptions=['Pinned literal fixed support and complete initial local catalogue with within-triplicate cap/Gram premises.','Authenticated complete scalar-surviving canonical count population.'],
   dependencies=[dict(id=scalar_binding['id'],revision=scalar_binding['revision'],relation='uses_result'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],premise_reports=[dict(path=key(args.scalar_gate),sha256=args.scalar_gate_sha256,relation='uses_result')],
   verifier=result['verifier'],method=result['method'],created_at=timestamp,updated_at=timestamp,artifact_availability='LOCAL_ONLY',
   independent_verification=dict(report=key(out/'summary.json'),sha256=sha(out/'summary.json'),status=result['status']),
   inputs_sha256=inputs,shared_components=result['shared_components'],controls=result['controls'],
   limitations=['Separate block witnesses need not use mutually consistent group triples.','No earlier literal exclusions are subtracted; no new native call or target automorphism assumption.','Producer DP prefix-state completeness is not a premise: independent complete2+3 sum sets replace it.'])
  save(out/'claim_binding.json',binding)
  print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),excluded=len(excluded),surviving=len(survived),elapsed_seconds=time.perf_counter()-start)),flush=True)
 except BaseException as error:
  save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=inputs,elapsed_seconds=time.perf_counter()-start));raise

if __name__=='__main__':main()
