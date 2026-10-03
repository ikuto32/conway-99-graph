"""Candidate complete exact-eight scalar extrema screen, gated and native-free."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';J=B/'20260930_exact_eight_profile_join';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md');RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';SIG=B/'20260930_hadamard_count_master_preflight/local_signatures.json';TABLE=B/'20260930_hadamard_count_gram_intervals/signature_intervals.json.gz';TG=B/'20260930_independent_review/count_gram_intervals/summary.json'
PINS={J/'summary.json':'77ae94974105ffe11d77e88d88e4d7e35670e13118d868def35a69f2079abb70',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',SIG:'075120017568ecbb0da5369f8e45c0dafd015ae4953681491bab66f04e9fdb45',TABLE:'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a',TG:'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33'}
WITNESSES=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
def need(c,m):
 if not c:raise ValueError(m)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,indent=2);f.write('\n')
def gzsave(p,d):
 with Path(p).open('xb')as f:
  with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as g:g.write((json.dumps(d,separators=(',',':'))+'\n').encode())
def flat(table):return tuple(v for row in table for t in row for v in t)
def table_from_flat(v):
 need(len(v)==720 and all(type(x)is int and 0<=x<=3 for x in v),'720 literal count entries');return[[list(v[60*a+3*g:60*a+3*g+3])for g in range(20)]for a in range(12)]
def can(v):return min(tuple(v[k+p[f]]for k in range(0,len(v),3)for f in range(3))for p in permutations(range(3)))
def digest(v):return hashlib.sha256(bytes(v)).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--join-gate',type=Path,required=True);ap.add_argument('--join-gate-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
 def pin(p,h=None):
  v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
 try:
  pin(args.join_gate,args.join_gate_sha256);gate=read(args.join_gate);need(gate['status']=='INDEPENDENT_COMPLETE_EXACT_EIGHT_PROFILE_JOIN_PASS','independent join gate');gp=gate['inputs_sha256']
  for p,h in PINS.items():pin(p,h)
  need(gp.get(key(J/'summary.json'))==PINS[J/'summary.json'],'join gate summary identity');joined=read(J/'summary.json');need(joined['complete']and joined['labelled_profiles']==9288 and joined['fibre_orbits']==1548 and len(joined['completed_subset_records'])==67,'complete authenticated universe')
  for name,h in joined['outputs_sha256'].items():pin(ROOT/name,h);need(gp.get(name)==h,'join gate output '+name)
  tablegate=read(TG);need(tablegate['status']=='INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS','verified exact extrema')
  for p in [RAW,LOCAL,SIG,TABLE]:need(tablegate['inputs_sha256'][key(p)]==PINS[p],'table direct input pin')
  for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));K=raw['prescribed_Gram36'];local=read(LOCAL);words=local['words'];triples=local['survivors'];partition=defaultdict(list)
  for i,t in enumerate(triples):partition[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
  sigs=sorted(partition);saved=read(SIG)['signatures'];need(len(sigs)==6061 and len(triples)==31110,'complete signature population');need(all(s['index']==i and tuple(s['counts'])==sigs[i]and s['local_survivor_indices']==partition[sigs[i]]for i,s in enumerate(saved)),'full signature index mapping');index={s:i for i,s in enumerate(sigs)}
  with gzip.open(TABLE,'rt',encoding='utf-8')as f:tab=json.load(f)
  cells=[(a,b,f,h)for a,b in combinations(range(6),2)for f in range(3)for h in range(3)];need(tab['local_cells']==[list(c)for c in cells],'local cell ordering');ci={c:i for i,c in enumerate(cells)};bounds=tab['records'];need(len(bounds)==6061 and all(r['signature_index']==i and all(len(r[k])==135 for k in('minimum','maximum','minimum_witnesses','maximum_witnesses'))and all(0<=lo<=hi<=2 for lo,hi in zip(r['minimum'],r['maximum']))for i,r in enumerate(bounds)),'complete exact coefficient array')
  globalcells=[(a,b,f,h)for a,b in combinations(range(12),2)if a^1!=b for f in range(3)for h in range(3)];terms=[[(g,ci[s.index(a),s.index(b),f,h])for g,s in enumerate(groups)if a in s and b in s]for a,b,f,h in globalcells];need(len(globalcells)==540 and all(len(t)==5 for t in terms),'all540 exact five-group cells')
  for p in permutations(range(3)):need(all(K[12*p[i//12]+i%12][12*p[j//12]+j%12]==K[i][j]for i in range(36)for j in range(36)),'six literal Gram fibre covariances')
  def selected(counts):
   need(all(sum(counts[a][g])==(3 if a in s else 0)for a in range(12)for g,s in enumerate(groups)),'support count margins');return[index[tuple(v for a in s for v in counts[a][g])]for g,s in enumerate(groups)]
  def screen(counts):
   ids=selected(counts);lo=[];hi=[];bad=[]
   for k,((a,b,f,h),ts)in enumerate(zip(globalcells,terms)):
    low=sum(bounds[ids[g]]['minimum'][j]for g,j in ts);high=sum(bounds[ids[g]]['maximum'][j]for g,j in ts);target=K[12*f+a][12*h+b];lo.append(low);hi.append(high)
    if not low<=target<=high:bad.append(k)
   return ids,lo,hi,bad
  def attainer(si,j,kind):
   ti=bounds[si][kind+'_witnesses'][j];need(ti in partition[sigs[si]],'attainer exact count class');a,b,f,h=cells[j];value=sum(words[w][a]==f and words[w][b]==h for w in triples[ti]);need(value==bounds[si][kind][j],'literal attainer value');return dict(local_survivor_index=ti,word_indices=triples[ti],colour_words=[words[w]for w in triples[ti]],value=value)
  def certificate(ids,k):
   a,b,f,h=globalcells[k];records=[]
   for g,j in terms[k]:
    si=ids[g];records.append(dict(group=g,support=list(groups[g]),signature_index=si,signature_counts=list(sigs[si]),local_cell_index=j,local_cell=list(cells[j]),class_size=len(partition[sigs[si]]),minimum=bounds[si]['minimum'][j],maximum=bounds[si]['maximum'][j],minimum_attainer=attainer(si,j,'minimum'),maximum_attainer=attainer(si,j,'maximum')))
   lo=sum(t['minimum']for t in records);hi=sum(t['maximum']for t in records);target=K[12*f+a][12*h+b];need(not lo<=target<=hi,'actual violated necessary interval');return dict(cell_index=k,coordinates=[a,b],fibres=[f,h],target=target,lower=lo,upper=hi,violation='TARGET_BELOW_LOWER'if target<lo else'TARGET_ABOVE_UPPER',terms=records)
  controls=[];historical=[]
  for name,folder,h in WITNESSES:
   p=B/f'20260930_independent_review/{folder}/independent_count_profile.json';pin(p,h);w=read(p);counts=w['coordinate_group_fibre_counts'];ids,lo,hi,bad=screen(counts)
   if name=='second':k=globalcells.index((9,11,2,1));need(k in bad and hi[k]==1 and K[33][23]==2,'known second negative');certificate(ids,k)
   else:need(not bad,'known first/third interval positive')
   historical.append(dict(name=name,raw_path=key(p),raw_sha256=h,historical_deviation_digest=w['profile_sha256'],literal_full_count_sha256=digest(flat(counts)),canonical_full_count_sha256=digest(can(flat(counts))),original_orientation_failed_cell_indices=bad,prior_exclusion_subtracted=False))
  balanced=[[[1,1,1]if a in s else[0,0,0]for s in groups]for a in range(12)];need(not screen(balanced)[3],'balanced relaxation positive');checks=0
  for A in [(0,),(1,),(0,1),(0,2),(1,2)]:
   for C in [(0,),(1,),(0,1),(0,2),(1,2)]:
    sums=[a+c for a,c in product(A,C)];need(min(sums)==min(A)+min(C)and max(sums)==max(A)+max(C),'tiny exhaustive extrema');checks+=1
  rejected=[]
  def reject(name,fn):
   try:fn()
   except(ValueError,KeyError,IndexError):rejected.append(name)
   else:raise ValueError('accepted corruption '+name)
  reject('malformed_counts',lambda:table_from_flat([0]*719));bad=[[[*v]for v in row]for row in balanced];bad[0][0]=[3,3,3];reject('changed_signature',lambda:selected(bad));reject('wrong_canonical_digest',lambda:need(digest(can(flat(balanced)))=='0'*64,'canonical hash'))
  # Exercise the same raw-attainer checker with a mutated bound, then restore exactly.
  old=bounds[0]['minimum'][0];bounds[0]['minimum'][0]=old+1;reject('changed_minimum_bound',lambda:attainer(0,0,'minimum'));bounds[0]['minimum'][0]=old
  old=bounds[0]['maximum_witnesses'][0];bounds[0]['maximum_witnesses'][0]=len(triples);reject('out_of_range_attainer',lambda:attainer(0,0,'maximum'));bounds[0]['maximum_witnesses'][0]=old
  save(out/'controls.json',dict(exhaustive_extrema_cases=checks,known_controls=historical,balanced_relaxation_positive=True,corruptions_rejected=rejected,full_factor=False))
  representatives=[];seen=set();labelled=0
  for rec in joined['completed_subset_records']:
   op=next(ROOT/k for k in rec['artifacts_sha256']if k.endswith('/orbits.json'));orbs=read(op);need(orbs['complete'],'complete subset orbit file')
   for orbit in orbs['orbits']:
    v=tuple(orbit['canonical_counts']);counts=table_from_flat(v);need(v==can(v)and digest(v)==orbit['canonical_fibre_profile_sha256'],'actual canonical full counts');os=len({tuple(v[k+p[f]]for k in range(0,720,3)for f in range(3))for p in permutations(range(3))});need(os==orbit['orbit_size']==len(orbit['members']),'actual complete orbit size');dg=digest(v);need(dg not in seen,'disjoint canonical population');seen.add(dg);labelled+=os;representatives.append(dict(canonical_fibre_profile_sha256=dg,subset_index=rec['subset_index'],exceptional_groups=rec['groups'],counts=counts,orbit_size=os,members=orbit['members'],source_orbits_path=key(op)))
  need(len(representatives)==1548 and labelled==9288,'entire canonical/labelled population')
  for h in historical:need(h['canonical_full_count_sha256']in seen,'all historical witnesses present')
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(seconds=120,native_calls=0),scope='Complete1548 exact-eight count representatives; literal verified local extrema table.'))
  survivors=[];excluded=[];checked=0;failurehist=Counter();screenpath=out/'screens.jsonl.gz'
  with screenpath.open('xb')as packed:
   with gzip.GzipFile(fileobj=packed,mode='wb',filename='',mtime=0)as stream:
    for rep in representatives:
     if time.perf_counter()-start>=118:break
     ids,lo,hi,bad=screen(rep['counts']);first=certificate(ids,bad[0])if bad else None;record=dict(canonical_fibre_profile_sha256=rep['canonical_fibre_profile_sha256'],subset_index=rep['subset_index'],group_signature_indices=ids,lower_bounds=lo,upper_bounds=hi,failed_cell_indices=bad,first_failure=first);stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());item={**rep,'failed_cell_indices':bad,'first_failure':first}
     (excluded if bad else survivors).append(item);failurehist.update(bad);checked+=1
     if checked%100==0:print(json.dumps(dict(checked=checked,excluded=len(excluded),surviving=len(survivors),elapsed_seconds=time.perf_counter()-start)),flush=True)
  for h in historical:
   match=next((r for r in survivors+excluded if r['canonical_fibre_profile_sha256']==h['canonical_full_count_sha256']),None);h['representative_screened']=match is not None;h['canonical_failed_cell_indices']=None if match is None else match['failed_cell_indices'];h['exact_member_reference']=None if match is None else next(m for m in match['members']if m['profile_sha256']==h['literal_full_count_sha256'])
  gzsave(out/'surviving_representatives.json.gz',dict(complete=checked==1548,records=survivors));gzsave(out/'excluded_representatives.json.gz',dict(complete=checked==1548,records=excluded));save(out/'historical_memberships.json',dict(records=historical,prior_exclusions_subtracted=False,digest_conventions='Historical deviation digest is distinct from literal/canonical720-byte fullcount digest. Literal raw count equality determines membership.'))
  summary=dict(status='CANDIDATE_COMPLETE_EXACT_EIGHT_SCALAR_INTERVAL_SCREEN'if checked==1548 else'CANDIDATE_PARTIAL_EXACT_EIGHT_SCALAR_INTERVAL_SCREEN',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},complete=checked==1548,representatives_total=1548,labelled_total=9288,representatives_checked=checked,representatives_excluded=len(excluded),representatives_surviving=len(survivors),labelled_excluded=sum(r['orbit_size']for r in excluded),labelled_surviving=sum(r['orbit_size']for r in survivors),failed_cell_histogram=dict(failurehist),elapsed_seconds=time.perf_counter()-start,native_calls=0,independent_approval=False,scope='Only necessary scalar extrema from complete local count classes with within-group caps; survivors are not full Gram factors. No prior exclusions subtracted, block-DP or residual graph inferred.')
  save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in['inputs_sha256','outputs_sha256','failed_cell_histogram']}));print('summary_sha256',sha(out/'summary.json'))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
