"""Candidate streaming inventory only; never constructs a research CNF."""
from pathlib import Path
from itertools import combinations, product
from collections import Counter
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, platform, subprocess, sys, time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
PINS={
 'acceleration/theory_20260930_all_triple_count_preflight.py':'fd0c9d09e1e9c1139ff1cf43b3630243caff96c6b4e34e221537b429e822ff74',
 'acceleration/results/20260930_all_triple_count_preflight/failure.json':'73a906db51c2cd3cb15e69f12b493c988134d2cdd3bee25817fabb749d682feb',
 'acceleration/results/20260930_hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 'acceleration/results/20260930_hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
 'acceleration/results/20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',
 'acceleration/results/20260930_independent_review/hadamard_few_exception_marginals/summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',
 'acceleration/results/20260930_hadamard_prism_ordered_cnf/summary.json':'02d3996a7e12f6b2e119d59bb184c79ebdea0f11352e47217e8b424b173ef721',
 'acceleration/results/20260930_hadamard_count_master_cnf/model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 'acceleration/results/20260930_hadamard_count_master_cnf/scope.json':'719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',
 'acceleration/results/20260930_independent_review/hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',
 'acceleration/results/20260930_independent_review/count_master_sat_outcome/independent_count_profile.json':'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',
 'acceleration/results/20260930_independent_review/count_master_sat_outcome/summary.json':'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',
 'acceleration/results/20260930_hadamard_count_master_cnf/baseline.cnf':'609a606c2b228e3956e43ab7d2589dcbcdca797f5978ffa51c8029aa042b7ba7',
 'acceleration/results/20260930_hadamard_count_master_cnf/at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',
 'acceleration/theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',
 'acceleration/theory_20260930_hadamard_count_master_cnf.py':'470cbec724f891264593dc5b438648dc2995b3f860f89decf4b6ac8bc1c4f28b',
 'acceleration/theory_20260930_hadamard_prism_ordered_cnf.py':'7520b147cc67ac0f01cd8a754ab3060ad6add27583e28f2cf8d7e065340fea8a',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
N=31110; S=20*N
def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(d,f,indent=2);f.write('\n')
def peak():
 class PMC(ctypes.Structure):
  _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(k,ctypes.c_size_t) for k in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
 p=PMC();p.cb=ctypes.sizeof(p);ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(p),p.cb);return int(p.PeakWorkingSetSize)
def budget(start):need(time.monotonic()-start<120,'120s cooperative inventory limit');need(peak()<512*1024**2,'512MiB inventory working set')
def digits(a):
 a=np.asarray(a,dtype=np.int64);d=np.ones(a.shape,dtype=np.int16)
 for t in (10,100,1000,10000,100000,1000000,10000000):d+=(a>=t)
 return d
def blank():return dict(clauses=0,literals=0,negative_literals=0,ascii_body_bytes=0,max_clause_literals=0)
def stats_add(s,c,l,d,neg,maxlen):
 s['clauses']+=int(c);s['literals']+=int(l);s['negative_literals']+=int(neg);s['ascii_body_bytes']+=int(d+neg+l+2*c);s['max_clause_literals']=max(s['max_clause_literals'],int(maxlen))
def litadd(s,c):stats_add(s,1,len(c),sum(len(str(abs(x))) for x in c),sum(x<0 for x in c),len(c))
def onehot_stats(ids,p):
 n=len(ids);s=blank();dx=digits(ids);dp=digits(p);stats_add(s,1,n,dx.sum(),0,n)
 stats_add(s,1,2,int(dx[0]+dp[0]),1,2)
 if n>2:
  stats_add(s,3*(n-2),6*(n-2),int(2*dx[1:-1].sum()+2*dp[1:].sum()+2*dp[:-1].sum()),4*(n-2),2)
 stats_add(s,1,2,int(dx[-1]+dp[-1]),2,2);return s
def or_stats(x,q):
 s=blank();n=len(x);stats_add(s,n+1,3*n+1,2*int(digits(x).sum())+(n+1)*len(str(q)),n+1,n+1);return s
def onehot(ids,p):
 yield ids;yield [-ids[0],p[0]]
 for i in range(1,len(ids)-1):yield [-ids[i],p[i]];yield [-p[i-1],p[i]];yield [-ids[i],-p[i-1]]
 yield [-ids[-1],-p[-1]]
def OR(q,x):
 for a in x:yield [-a,q]
 yield [-q,*x]
def exact(xs,k):
 for c in combinations(xs,k+1):yield [-x for x in c]
 for c in combinations(xs,len(xs)-k+1):yield list(c)
def sat(cs,v):return all(any(v[abs(x)]==(x>0) for x in c) for c in cs)
def merge(ss):
 s=blank()
 for r in ss:
  for k in s:s[k]=max(s[k],r[k]) if k=='max_clause_literals' else s[k]+r[k]
 return s
def controls():
 truth=bytecases=ortruth=0
 for n in range(2,7):
  x=list(range(1,n+1));p=list(range(n+1,2*n));cs=list(onehot(x,p));a=onehot_stats(x,p);b=blank()
  for c in cs:litadd(b,c)
  need(a==b and b['ascii_body_bytes']==len(''.join(' '.join(map(str,c))+' 0\n' for c in cs).encode()),'onehot arithmetic byte count');bytecases+=1
  for bits in product((False,True),repeat=2*n-1):
   v={i+1:t for i,t in enumerate(bits)};expected=sum(bits[:n])==1 and all(v[p[j]]==any(v[k] for k in x[:j+1]) for j in range(n-1));need(sat(cs,v)==expected,'onehot exact unique extension');truth+=1
 for n in range(5):
  x=list(range(1,n+1));q=n+1;cs=list(OR(q,x));b=blank()
  for c in cs:litadd(b,c)
  need(or_stats(x,q)==b,'OR byte counter including empty');bytecases+=1
  for bits in product((False,True),repeat=n+1):need(sat(cs,dict(enumerate(bits,1)))==(bits[-1]==any(bits[:-1])),'OR exact truth');ortruth+=1
 counttruth=0
 for k in (1,2):
  cs=list(exact(list(range(1,11)),k))
  for bits in product((False,True),repeat=10):need(sat(cs,dict(enumerate(bits,1)))==(sum(bits)==k),'ten-channel exact count');counttruth+=1
 # Threshold representation is literal multiplicity, not a Boolean shortcut.
 need(all(sum(c>=t for t in (1,2))==c for c in range(3)),'weighted thresholds');need(sum(2>=t for t in (1,))!=2,'wrong single threshold rejected')
 return dict(onehot_full_assignments=truth,or_full_assignments=ortruth,exact_count_assignments=counttruth,byte_cases=bytecases,corruptions_rejected=['missing_multiplicity2_threshold'],full_research_factor_positive=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 try:
  for path,d in PINS.items():need(sha(ROOT/path)==d,'input identity '+path)
  inputs=dict(PINS)
  for path in [Path(__file__),Path(__file__).with_name('theory_20260930_all_triple_count_preflight_v2_spec.md'),ROOT/'docs/DESIGN_20260930_ALL_TRIPLE_COUNT_GRAM.md']:inputs[path.relative_to(ROOT).as_posix()]=sha(path)
  overlap=['theory_20260930_hadamard_all_triple_descent.py','theory_20260930_hadamard_gram_affine_gf2.py','theory_20260930_hadamard_prism_ordered_cnf_spec.md','theory_20260930_hadamard_count_master_preflight_spec.md']
  for name in overlap:inputs['acceleration/'+name]=sha(ROOT/'acceleration'/name)
  save(out/'manifest.json',dict(inputs_sha256=inputs,command=[sys.executable,*sys.argv],cwd=str(ROOT),timestamp=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,limits=dict(seconds=120,working_set_bytes=512*1024**2),native_calls=0,research_CNF_built=False))
  ctrl=controls();local=read(B/'20260930_hadamard_triplicate_counts/local_triples.json');raw=read(B/'20260930_hadamard20_support/six_prism.json');model=read(B/'20260930_hadamard_count_master_cnf/model.json');words=np.asarray(local['words'],dtype=np.int8);tri=np.asarray(local['survivors'],dtype=np.int32);need(words.shape==(90,6) and tri.shape==(N,3),'local catalogue shape');colours=words[tri]
  groups=model['groups'];raw_first=[list(x) for x in dict.fromkeys(tuple(s) for s in raw['support_columns'])];need(len(groups)==20 and groups==raw_first and sorted(groups)==sorted(x['support'] for x in raw['support_multiplicities']),'literal20supports in authenticated first-occurrence order')
  counts=np.stack([(colours==f).sum(axis=1) for f in range(3)],axis=2).reshape(N,18)
  sigs={tuple(s['counts']):s['index'] for s in model['local_signatures']};sid=np.asarray([sigs[tuple(c)] for c in counts],dtype=np.int32);need(len(sigs)==6061,'complete signature count')
  for s in model['local_signatures']:need(np.flatnonzero(sid==s['index']).tolist()==s['local_survivor_indices'],'exact signature class ranks')
  pairs=[(u,v) for u,v in combinations(range(12),2) if u^1!=v];need(len(pairs)==60 and all(sum(u in g and v in g for g in groups)==5 for u,v in pairs),'all60 pair incidences')
  G=np.asarray(raw['prescribed_Gram36']);zero=[];positive=[]
  for u,v in combinations(range(36),2):
   aa,bb=u%12,v%12
   if aa!=bb and aa^1!=bb:need(G[u,v]==(1 if u//12==v//12 else 2),'cross target');positive.append((u,v))
   else:need(G[u,v]==0,'remaining structural zero');zero.append((u,v))
  need(len(positive)==540 and len(zero)==90 and all(G[i,i]==10 for i in range(36)),'all666 targets accounted')
  marginal_checks=0
  for d in model['coordinate_domains']:
   for table in d['count_tables']:
    t=np.asarray(table);need(t.shape==(20,3) and t.sum(axis=0).tolist()==[10]*3 and all(t[g].sum()==(3 if g in d['incident_groups'] else 0) for g in range(20)),'master complete domain enforces each row margin');marginal_checks+=3
  coeff={};masks={};coefficient_hist=Counter();colsum=np.zeros(N,dtype=np.int16)
  for u,v in combinations(range(6),2):
   for f,z in product(range(3),repeat=2):
    c=((colours[:,:,u]==f)&(colours[:,:,v]==z)).sum(axis=1).astype(np.int8);need(int(c.max())<= (1 if f==z else 2),'local Gram bounds');coeff[u,v,f,z]=c;colsum+=c;coefficient_hist.update(map(int,c))
    for t in (1,2):masks[u,v,f,z,t]=np.flatnonzero(c>=t).astype(np.int32)
  need(np.all(colsum==45),'actual per-option45 weighted occurrences');budget(start)
  save(out/'local_inventory.json',dict(triples=N,signature_count=6061,triple_signature_indices=sid.tolist(),coefficient_histogram=dict(coefficient_hist),threshold_masks=[dict(key=list(k),count=len(x),indices_sha256=hashlib.sha256(x.astype('<i4').tobytes()).hexdigest()) for k,x in masks.items()],row_margin_entries_checked=marginal_checks,Gram_accounting=dict(diagonal=36,positive_off_diagonal=540,structural_zero_off_diagonal=90)))
  # Actual master-compatible count-only positives, deliberately not Gram positives.
  balanced_sid=sigs[tuple([1]*18)];positive_checks=[]
  known=read(B/'20260930_independent_review/count_master_sat_outcome/independent_count_profile.json')
  for variant,selected in [('balanced',[balanced_sid]*20),('verified_eight_count_only',known['selected_global_signature_indices'])]:
   for d,j in zip(model['group_domains'],selected):need(j in d['signature_indices'] and len(np.flatnonzero(sid==j))>0,'balanced count signature local extension')
   positive_checks.append(dict(name=variant,local_triples_chosen=20,full_Gram_asserted=False))
  # A signature implication rejects a selected local triple paired to another
  # master signature, and a retained explicit unit rejects an absent class.
  need(not sat([[-1,2]],{1:True,2:False}),'wrong count signature rejected');need(not sat([[-1]],{1:True}),'missing master class unit rejected');ctrl['corruptions_rejected']+=['wrong_selected_signature','selected_absent_signature']
  for d in model['group_domains']:
   bad=next((j for j in range(6061) if j not in set(d['signature_indices'])),None)
   if bad is not None:need(len(np.flatnonzero(sid==bad))>0,'absent master signature still has local triples');ctrl['corruptions_rejected'].append('unsupported_signature_link_group_'+str(d['group']));break
  ctrl['count_only_positives']=positive_checks;save(out/'controls.json',ctrl)
  records=[]
  for variant in ('baseline','at_least_seven'):
   base=model['variants'][variant];basepath=ROOT/base['cnf_path'];body=basepath.stat().st_size-len(f"p cnf {base['variables']} {base['clauses']}\n".encode());selector0=base['variables']+1;prefix0=selector0+S;nextvar=prefix0+S-20;sections=[];gd=[]
   for g in range(20):
    ids=np.arange(selector0+g*N,selector0+(g+1)*N,dtype=np.int64);prefix=np.arange(prefix0+g*(N-1),prefix0+(g+1)*(N-1),dtype=np.int64);one=onehot_stats(ids,prefix);sections.append(one);d=model['group_domains'][g];mapping=dict(zip(d['signature_indices'],d['selectors']));linked=np.asarray([mapping.get(int(j),0) for j in sid],dtype=np.int64);valid=linked>0;link=blank();stats_add(link,int(valid.sum()),2*int(valid.sum()),int(digits(ids[valid]).sum()+digits(linked[valid]).sum()),int(valid.sum()),2);stats_add(link,int((~valid).sum()),int((~valid).sum()),int(digits(ids[~valid]).sum()),int((~valid).sum()),1);sections.append(link);gd.append(dict(group=g,selectors=[int(ids[0]),int(ids[-1])],prefixes=[int(prefix[0]),int(prefix[-1])],mapped_options=int(valid.sum()),false_selector_units=int((~valid).sum()),onehot=one,signature_link=link))
   cells=[];channel_sections=[];count_sections=[]
   for aa,bb in pairs:
    incident=[g for g,support in enumerate(groups) if aa in support and bb in support]
    for f,z in product(range(3),repeat=2):
     channels=[]
     for g in incident:
      u,v=groups[g].index(aa),groups[g].index(bb)
      for t in (1,2):
       ids=selector0+g*N+masks[u,v,f,z,t];q=nextvar;nextvar+=1;cs=or_stats(ids,q);channel_sections.append(cs);channels.append(dict(group=g,threshold=t,variable=q,local_mask_key=[u,v,f,z,t],members=len(ids),inventory=cs))
     target=1 if f==z else 2;qs=[c['variable'] for c in channels];cs=blank()
     for clause in exact(qs,target):litadd(cs,clause)
     count_sections.append(cs);cells.append(dict(coordinates=[aa,bb],fibres=[f,z],target=target,channels=channels,count_inventory=cs))
   sections+=channel_sections+count_sections;tot=merge(sections);n=nextvar-1;c=base['clauses']+tot['clauses'];ascii_bytes=body+tot['ascii_body_bytes']+len(f'p cnf {n} {c}\n'.encode());need(n==base['variables']+2*S+5380,'computed variable population');need(tot['clauses']==49*S+60420,'recounted clauses including signature links, no hidden row-margin assumption')
   config=dict(variant=variant,base=dict(path=base['cnf_path'],sha256=base['cnf_sha256'],variables=base['variables'],clauses=base['clauses'],body_bytes=body),groups=gd,cells=cells,variables=n,clauses=c,ASCII_bytes=ascii_bytes,appended=tot,channels=merge(channel_sections),cell_counts=merge(count_sections),signature_link=merge([r['signature_link'] for r in gd]),onehot=merge([r['onehot'] for r in gd]),scope='Full Gram and within-group caps on literal support; '+('no exception-count lower bound.' if variant=='baseline' else 'additional at-least-seven restriction; cross-group caps remain omitted.'))
   save(out/f'{variant}_inventory.json',config);records.append({k:config[k] for k in ('variant','variables','clauses','ASCII_bytes','appended','channels','cell_counts','signature_link','onehot','scope')});budget(start)
  live_arrays=sum(x.nbytes for x in [words,tri,colours,counts,sid,colsum])+sum(x.nbytes for x in coeff.values())+sum(x.nbytes for x in masks.values());largest=max(r['appended']['max_clause_literals'] for r in records);memory=dict(explicit_shared_numeric_arrays_bytes=live_arrays,proposed_stream_text_buffer_bytes=1024**2,largest_clause_literals=largest,largest_clause_ascii_upper_bound=largest*9+3,observed_preflight_peak_working_set_bytes=peak(),no_research_clause_list_allocated=True,solver_memory_unknown=True,python_clause_lists_base_container_estimate_bytes=records[-1]['appended']['clauses']*56+records[-1]['appended']['literals']*8,packed_32bit_appended_literals_bytes=4*records[-1]['appended']['literals'])
  summary=dict(status='CANDIDATE_ALL_TRIPLE_COUNT_GRAM_PREFLIGHT_COMPLETE',inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},variants=records,memory=memory,prior_ordered_single_column=dict(variables=595464,clauses=3336642,scope='Full prescribed Gram plus all cross-group caps; no count lower bound; prior UNKNOWN is not exclusion.'),selection='All31110 local triples per20groups; no new pruning/orbits; verified master signature impossibilities are explicit units.',coverage_candidate_only=True,independent_approval=False,research_CNF_built=False,native_calls=0,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
  save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256','variants')}));print(json.dumps([dict(variant=r['variant'],variables=r['variables'],clauses=r['clauses'],ASCII_bytes=r['ASCII_bytes'])for r in records]))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
