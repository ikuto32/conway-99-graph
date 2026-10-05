"""Candidate necessary Gram interval screen on complete local count signatures."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PRE=B+'hadamard_count_master_preflight/';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';PROFILES=B+'hadamard_six_profile_local_domains/profiles.jsonl.gz'
PINS={PRE+'summary.json':'f290fc687ac1723354e9b4acf7429de087547f8a422bb4ee7770b2473d62e7bb',B+'independent_review/hadamard_count_master_preflight/summary.json':'5b23e5a188522c669128ec9f79ec8fb975d75e251c15be4ebc0857b96d4876b3',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',PROFILES:'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def gzsave(p,v):
    with p.open('xb')as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0)as g:g.write(json.dumps(v,separators=(',',':')).encode()+b'\n')
def sig(words,triple):return tuple(sum(words[t][a]==f for t in triple)for a in range(6)for f in range(3))
def local_values(words,triple,cells):
    masks=[sum(1<<c for c,t in enumerate(triple)if words[t][a]==f)for a in range(6)for f in range(3)]
    return[(masks[3*a+f]&masks[3*b+h]).bit_count()for a,b,f,h in cells]
def inside(values,low,high):return all(l<=x<=h for x,l,h in zip(values,low,high))
def controls():
    # Exact synthetic product domain: enumerate every full sum and compare extrema.
    domains=[[(0,1),(1,0)],[(1,1),(2,0)],[(0,0),(0,1)]]
    low=[sum(min(v[i]for v in d)for d in domains)for i in range(2)];high=[sum(max(v[i]for v in d)for d in domains)for i in range(2)]
    sums=[tuple(sum(v[i]for v in choice)for i in range(2))for choice in product(*domains)]
    need(all(inside(v,low,high)for v in sums),'all genuine product choices in exact interval')
    need(low==[min(v[i]for v in sums)for i in range(2)]and high==[max(v[i]for v in sums)for i in range(2)],'independent exhaustive extrema')
    need(not inside([0,0],low,high)and not inside([4,0],low,high),'out-of-interval target controls')
    narrowed=low[:];narrowed[0]+=1;need(any(not inside(v,narrowed,high)for v in sums),'corrupted lower bound detected')
    widened=high[:];widened[1]-=1;need(any(not inside(v,low,widened)for v in sums),'corrupted upper bound detected')
    return dict(product_choices=len(sums),exact_low=low,exact_high=high,rejected_corruptions=['target_below','target_above','narrowed_lower','narrowed_upper'],research_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        pins[p]=sha(ROOT/p);need(h is None or pins[p]==h,'input '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        pre=read(PRE+'summary.json')
        for p in ['local_signatures.json','inventory.json']:pin(PRE+p,pre['outputs_sha256'][PRE+p])
        for p in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=30,local_triples=31110,count_signatures=6061,calibration_profiles=984,native_calls=0),scope='All540 necessary Gram interval rows for all984 saved six-exception count profiles. Discovery/calibration only; no exhaustive arbitrary-exception search.'))
        save(out/'controls.json',controls());raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));catalog=read(LOCAL);words=catalog['words'];triples=catalog['survivors'];signatures=read(PRE+'local_signatures.json')['signatures'];index={tuple(s['counts']):s['index']for s in signatures}
        cells=[(a,b,f,h)for a,b in combinations(range(6),2)for f in range(3)for h in range(3)];cellindex={x:i for i,x in enumerate(cells)};bounds=[]
        for s in tqdm(signatures,desc='Complete signature Gram intervals',mininterval=1):
            low=[4]*135;high=[-1]*135;arglow=[None]*135;arghigh=[None]*135
            for ti in s['local_survivor_indices']:
                need(sig(words,triples[ti])==tuple(s['counts']),'complete signature partition identity');vals=local_values(words,triples[ti],cells)
                for k,v in enumerate(vals):
                    if v<low[k]:low[k]=v;arglow[k]=ti
                    if v>high[k]:high[k]=v;arghigh[k]=ti
            need(all(0<=lo<=hi<=3 for lo,hi in zip(low,high)),'exact nonempty integer ranges');bounds.append(dict(signature_index=s['index'],minimum=low,maximum=high,minimum_witnesses=arglow,maximum_witnesses=arghigh))
            if s['index']%128==0:need(time.perf_counter()-start<30,'frozen wall allocation')
        gzsave(out/'signature_intervals.json.gz',dict(local_cells=[list(c)for c in cells],records=bounds))
        globalcells=[(a,b,f,h)for a,b in combinations(range(12),2)if a//2!=b//2 for f in range(3)for h in range(3)];need(len(globalcells)==540,'all nonmatched Gram cells')
        incidence={}
        for a,b,f,h in globalcells:
            terms=[(g,cellindex[s.index(a),s.index(b),f,h])for g,s in enumerate(groups)if a in s and b in s];need(len(terms)==5,'exact five groups per nonmatched pair');incidence[a,b,f,h]=terms
        def screen(counts):
            selected=[index[tuple(v for a in support for v in counts[a][g])]for g,support in enumerate(groups)];lower=[];upper=[];failures=[]
            for k,cell in enumerate(globalcells):
                a,b,f,h=cell;terms=incidence[cell];lo=sum(bounds[selected[g]]['minimum'][j]for g,j in terms);hi=sum(bounds[selected[g]]['maximum'][j]for g,j in terms);target=raw['prescribed_Gram36'][12*f+a][12*h+b];lower.append(lo);upper.append(hi)
                if not lo<=target<=hi:failures.append(dict(cell_index=k,coordinates=[a,b],fibres=[f,h],target=target,lower=lo,upper=hi,terms=[dict(group=g,signature_index=selected[g],local_cell=j,minimum=bounds[selected[g]]['minimum'][j],maximum=bounds[selected[g]]['maximum'][j],minimum_witness=bounds[selected[g]]['minimum_witnesses'][j],maximum_witness=bounds[selected[g]]['maximum_witnesses'][j])for g,j in terms]))
            return dict(group_signature_indices=selected,lower_bounds=lower,upper_bounds=upper,violations=failures)
        balanced=[[[1,1,1]if a in s else[0,0,0]for s in groups]for a in range(12)];balanced_result=screen(balanced);need(not balanced_result['violations'],'known feasible count relaxation positive survives intervals');save(out/'balanced_count_control.json',dict(counts=balanced,screen=balanced_result,full_factor=False))
        with gzip.open(ROOT/PROFILES,'rt',encoding='utf-8')as f:profiles=[json.loads(line)for line in f]
        results=[]
        for pi,p in enumerate(tqdm(profiles,desc='Frozen984 count-table probes',mininterval=1)):
            counts=[[v[:]for v in row]for row in balanced]
            for a in range(12):
                for side,g in enumerate(p['group_ids']):counts[a][g]=[counts[a][g][f]+p['coordinate_fibre_deviations'][a][f][side]for f in range(3)]
            result=screen(counts);results.append(dict(index=pi,id=p['id'],profile_sha256=p['profile_sha256'],**result))
            if pi%64==0:need(time.perf_counter()-start<30,'frozen wall allocation')
        need(len(results)==984,'whole preregistered population');gzsave(out/'profile_screens.json.gz',dict(global_cells=[list(c)for c in globalcells],records=results))
        excluded=[r['id']for r in results if r['violations']];save(out/'excluded_profile_ids.json',dict(ids=excluded,scope='Candidate interval exclusions of these existing literal count profiles only.'))
        summary=dict(status='CANDIDATE_COUNT_SIGNATURE_GRAM_INTERVAL_SCREEN_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},local_triples=31110,local_signatures=6061,exact_local_cells_per_signature=135,global_Gram_cells=540,calibration_profiles=984,interval_excluded_profiles=len(excluded),interval_surviving_profiles=984-len(excluded),total_failed_cells=sum(len(r['violations'])for r in results),first_excluded_profile=excluded[0]if excluded else None,first_excluded_null_reason=None if excluded else'No saved probe violates any interval.',balanced_count_profile_survives=True,independent_approval=False,scope='Necessary coefficient-wise Gram intervals for arbitrary count choices; finite probe covers only saved984 six-exception profiles, not arbitrary exception counts or full factors.',new_native_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start,artifact_availability='LOCAL_ONLY');save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
