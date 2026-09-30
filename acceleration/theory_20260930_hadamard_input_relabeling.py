"""Candidate exact fixed-input coordinate relabellings, no solver."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import permutations,product
import argparse,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json';D=B/'20260930_hadamard_four_group_local_screen'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def need(b,m):
    if not b:raise ValueError(m)
def permute_profile(c,sigma,pi,tau,look,reference):
    gs=tuple(sorted(pi[g]for g in c['groups']));ref=reference[gs]
    signs={pi[g]:s for g,s in zip(c['groups'],c['relation'])}
    ratios={signs[g]*s for g,s in zip(gs,ref['relation'])};need(len(ratios)==1,'circuit line preserved');mult=ratios.pop()
    values={}
    for a,row in zip(c['common_support'],c['profile']):
        r=[None]*3
        for f in range(3):r[tau[f]]=mult*row[f]
        values[sigma[a]]=r
    need(sorted(values)==ref['common_support'],'common support covariance')
    return look[(gs,tuple(tuple(values[a])for a in ref['common_support']))]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(h(RAW)=='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d','raw pin')
        raw=read(RAW);C=raw['core_adjacency'];G=raw['prescribed_Gram36'];L=raw['L']
        pairs=[(a,b)for a in range(12)for b in range(a+1,12)if C[a][b]]
        need(len(pairs)==6 and sorted(sum((list(p)for p in pairs),[]))==list(range(12)),'six matching pairs')
        supports=[];columns=[]
        for d in range(60):
            s=tuple(a for a in range(12)if L[a][d])
            if s not in supports:supports.append(s);columns.append([])
            columns[supports.index(s)].append(d)
        need(len(supports)==20 and all(len(c)==3 for c in columns),'twenty triplicates')
        index={s:i for i,s in enumerate(supports)};accepted=[];examined=0
        for pair_map in tqdm(list(permutations(range(6))),desc='input relabellings'):
            need(time.monotonic()-start<120,'resource limit')
            for flips in product(range(2),repeat=6):
                sigma=[None]*12
                for i,p in enumerate(pairs):
                    dest=pairs[pair_map[i]]
                    for side in range(2):sigma[p[side]]=dest[side^flips[i]]
                images=[tuple(sorted(sigma[a]for a in s))for s in supports];examined+=1
                if not all(s in index for s in images):continue
                pi=[index[s]for s in images];need(len(set(pi))==20,'support bijection')
                rows=[12*f+sigma[a]for f in range(3)for a in range(12)]
                need(all(C[rows[a]][rows[b]]==C[a][b]and G[rows[a]][rows[b]]==G[a][b]for a in range(36)for b in range(36)),'core and Gram invariance')
                colmap=[None]*60
                for g in range(20):
                    for d,e in zip(columns[g],columns[pi[g]]):colmap[d]=e
                need(all(L[sigma[a]][colmap[d]]==L[a][d]for a in range(12)for d in range(60)),'raw L covariance')
                accepted.append(dict(coordinate_permutation=sigma,group_permutation=pi,column_permutation=colmap))
        need(examined==46080,'complete matching-preserving universe')
        summary=read(D/'summary.json');need(h(D/'summary.json')=='7773d527456ea88913a543a19d0d49c0b5c339f7dfdccddce604822682620b7d','screen pin')
        cases=[];pins={key(RAW):h(RAW),key(D/'summary.json'):h(D/'summary.json')}
        for i in range(108):
            p=D/f'case_{i:03d}.json';need(h(p)==summary['outputs_sha256'][key(p)],'case pin');pins[key(p)]=h(p);cases.append(read(p))
        lookup={(tuple(c['groups']),tuple(tuple(r)for r in c['profile'])):c['case']for c in cases}
        reference={tuple(c['groups']):c for c in cases};taus=list(permutations(range(3)));maps=[];orbits={}
        for c in tqdm(cases,desc='profile covariance'):
            need(time.monotonic()-start<120,'resource limit')
            actions=[]
            for j,trans in enumerate(accepted):
                for tau in taus:
                    dest=permute_profile(c,trans['coordinate_permutation'],trans['group_permutation'],tau,lookup,reference)
                    need(c['gram_caps_ac']['empty']==cases[dest]['gram_caps_ac']['empty'],'screen outcome invariant')
                    actions.append((dest,j,tau))
            representative,trans,tau=min(actions);orbit=sorted({d for d,_,_ in actions})
            need(representative in orbit,'representative present');orbits.setdefault(representative,set()).update(orbit)
            maps.append(dict(case=c['case'],representative=representative,coordinate_map_index=trans,fibre_permutation=tau,orbit=orbit))
        need(sorted(x for o in orbits.values()for x in o)==list(range(108)),'disjoint complete orbits')
        save(out/'coordinate_maps.json',dict(examined=examined,maps=accepted,matching_pairs=pairs,support_groups=supports,group_columns=columns))
        save(out/'profile_maps.json',dict(case_maps=maps,orbits=[dict(representative=k,members=sorted(v),screen_empty=cases[k]['gram_caps_ac']['empty'])for k,v in sorted(orbits.items())]))
        # A swap across matching pairs does not preserve the core.
        bad=list(range(36));bad[0],bad[2]=bad[2],bad[0]
        need(any(C[bad[a]][bad[b]]!=C[a][b]for a in range(36)for b in range(36)),'unmatched swap rejected')
        need(len(set([0]*12))!=12,'nonbijection rejected')
        save(out/'controls.json',dict(unmatched_swap_rejected=True,nonbijection_rejected=True,identity_in_accepted=any(r['coordinate_permutation']==list(range(12))for r in accepted)))
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=h(p)
        result=dict(status='CANDIDATE_FIXED_INPUT_PROFILE_RELABELING',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},examined_coordinate_permutations=examined,input_preserving_permutations=len(accepted),profile_population=108,orbits=len(orbits),retained_orbit_representatives=[k for k in sorted(orbits)if not cases[k]['gram_caps_ac']['empty']],excluded_screen_orbit_representatives=[k for k in sorted(orbits)if cases[k]['gram_caps_ac']['empty']],elapsed_seconds=time.monotonic()-start,independent_approval=False,target_resolution=False,solver_calls=0,scope='Explicit input relabellings; no target object assumed invariant. Prior screen conclusions require their independent gate.')
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items()if k not in['inputs_sha256','outputs_sha256']}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(Path(__file__))));raise
if __name__=='__main__':main()

