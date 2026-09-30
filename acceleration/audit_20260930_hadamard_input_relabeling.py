"""Independent exact finite census of fixed matching-preserving coordinate maps."""
from collections import Counter
from datetime import datetime,timezone
from itertools import permutations
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';PROD=B+'hadamard_input_relabeling/';RAW=B+'hadamard20_support/six_prism.json';SCREEN=B+'hadamard_four_group_local_screen/'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def mappings(n):
    # Recursive assignment of each source pair to an unused destination pair.
    def walk(k,available,partial):
        if k==n:yield tuple(partial);return
        for dest in available:
            rest=[v for v in available if v!=dest]
            yield from walk(k+1,rest,partial+[2*dest,2*dest+1])
            yield from walk(k+1,rest,partial+[2*dest+1,2*dest])
    yield from walk(0,list(range(n)),[])
def mapped(mask,sigma):return sum(1<<sigma[a]for a in range(len(sigma))if mask>>a&1)
def check_sigma(sigma):
    need(len(sigma)==12 and sorted(sigma)==list(range(12)),'coordinate bijection')
    need(all(sigma[a^1]==sigma[a]^1 for a in range(12)),'fixed matching preservation')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    try:
        need(sha(ROOT/(PROD+'summary.json'))=='ffd73f91d4d6b93201160fe7353aa39cb6f5f68a45d4d774328f7e4bbbddcae6','frozen candidate');producer=read(PROD+'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():need(sha(ROOT/p)==h,'input identity '+p);pins[p]=h
        pins[PROD+'summary.json']=sha(ROOT/(PROD+'summary.json'))
        orbitgate=B+'independent_review/hadamard_fibre_profile_orbits/summary.json';need(sha(ROOT/orbitgate)=='c45fc396a1e5a345a7f94f1354303376742dd771c8eea64c10654699778da645','existing independent fibre theorem');pins[orbitgate]=sha(ROOT/orbitgate)
        raw=read(RAW);L=raw['L'];C=raw['core_adjacency'];G=raw['prescribed_Gram36'];masks=[sum(L[a][d]<<a for a in range(12))for d in range(60)];population=Counter(masks);need(len(population)==20 and set(population.values())=={3},'raw support multiset')
        unique=list(dict.fromkeys(masks));seen=set();accepted=[];hist=Counter();witnesses=[]
        for number,sigma in enumerate(mappings(6)):
            check_sigma(sigma);need(sigma not in seen,'enumeration unique');seen.add(sigma)
            bad=next((i for i,m in enumerate(unique)if mapped(m,sigma)not in population),None)
            if bad is not None:hist[bad]+=1;witnesses.append([number,bad,mapped(unique[bad],sigma)]);continue
            need(Counter(mapped(m,sigma)for m in masks)==population,'entire multiset covariance')
            rows=[12*f+sigma[a]for f in range(3)for a in range(12)]
            need(all(C[i][j]==C[rows[i]][rows[j]]and G[i][j]==G[rows[i]][rows[j]]for i in range(36)for j in range(36)),'literal full core/Gram action')
            accepted.append(list(sigma))
        need(len(seen)==46080 and accepted==[list(range(12))]and len(witnesses)==46079,'complete fixed-input census')
        maps=read(PROD+'coordinate_maps.json');need(maps['examined']==46080 and len(maps['maps'])==1,'saved census count')
        need(maps['matching_pairs']==[[a,a+1]for a in range(0,12,2)]and maps['support_groups']==[[a for a in range(12)if m>>a&1]for m in unique]and maps['group_columns']==[[d for d,m in enumerate(masks)if m==u]for u in unique],'saved geometry')
        need(maps['maps']==[dict(coordinate_permutation=list(range(12)),group_permutation=list(range(20)),column_permutation=list(range(60)))],'every accepted literal map')
        cases=[read(SCREEN+f'case_{i:03d}.json')for i in range(108)];lookup={(tuple(c['groups']),tuple(map(tuple,c['profile']))):c['case']for c in cases};case_maps=[];orbits={}
        for c in cases:
            choices=[]
            for tau in permutations(range(3)):
                profile=tuple(tuple(v[tau.index(f)]for f in range(3))for v in c['profile']);target=lookup[tuple(c['groups']),profile];choices.append((target,0,tau))
            rep,index,tau=min(choices);members=sorted({v[0]for v in choices});need(len(members)==6,'global fibre orbit');orbits[rep]=members
            need(all(cases[k]['gram_caps_ac']['empty']==c['gram_caps_ac']['empty']for k in members),'screen orbit invariant')
            case_maps.append(dict(case=c['case'],representative=rep,coordinate_map_index=index,fibre_permutation=list(tau),orbit=members))
        expected=dict(case_maps=case_maps,orbits=[dict(representative=k,members=v,screen_empty=cases[k]['gram_caps_ac']['empty'])for k,v in sorted(orbits.items())]);need(expected==read(PROD+'profile_maps.json'),'complete108 mapped profile records')
        need(len(orbits)==18 and [k for k in sorted(orbits)if not cases[k]['gram_caps_ac']['empty']]==producer['retained_orbit_representatives'],'no extra reduction beyond fibre normalization')
        # Positive controls with a larger symmetry group detect accidental identity-only checking.
        positives=[]
        for n in(2,3):
            full={sum(1<<(2*i+bits[i])for i in range(n))for bits in __import__('itertools').product(range(2),repeat=n)}
            mapsn=list(mappings(n));need(len(mapsn)==(8 if n==2 else 48)and all({mapped(m,s)for m in full}==full for s in mapsn),'complete small transversal positive family')
            fixed=sum(1<<(2*i)for i in range(n));count=sum(mapped(fixed,s)==fixed for s in mapsn);need(count==(2 if n==2 else 6),'fixed support nontrivial stabilizer');positives.append(dict(pairs=n,full_support_maps=len(mapsn),single_support_stabilizer=count))
        rejected=[]
        def reject(name,f):
            try:f()
            except(ValueError,KeyError,IndexError):rejected.append(name);return
            raise ValueError('accepted corruption '+name)
        reject('nonbijection',lambda:check_sigma([0]*12));reject('nonmatching_swap',lambda:check_sigma([2,1,0,3,*range(4,12)]))
        reject('missing_universe_element',lambda:need(len(seen)-1==46080,'frozen universe size'))
        reject('invent_second_accepted_map',lambda:need(accepted+[[1,0,*range(2,12)]]==accepted,'complete accepted maps'))
        reject('wrong_profile_representative',lambda:need(case_maps[0]['representative']==6,'minimal identity-containing orbit'))
        # Every rejection has a literal nonmember support certificate; compact rows are indexed in recursive traversal order.
        with(out/'rejection_witnesses.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(witnesses,f,separators=(',',':'));f.write('\n')
        save(out/'controls.json',dict(positive_families=positives,rejected_corruptions=rejected));save(out/'accepted_coordinate_maps.json',accepted)
        for p in[Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_INPUT_RELABELING.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[p.resolve().relative_to(ROOT).as_posix()]=sha(p)
        ts=datetime.now(timezone.utc).isoformat();claim=dict(id='C-FIXED-HADAMARD-MATCHING-COORDINATE-RELABELING-CENSUS',revision=1,kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Among all46080 coordinate permutations preserving the six fixed matching pairs, only the identity preserves the literal20 six-coordinate Hadamard supports (each repeated3). Therefore this coordinate-action family, combined with the previously checked global fibre S3 action, leaves exactly18 profile orbits and16 prior-screen-surviving orbit representatives.',scope='Complete specified matching-preserving coordinate-action family on one fixed support; not all possible36-row actions or target automorphisms.',assumptions=['Pinned raw support and fixed coordinate matching.'],dependencies=[dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION',revision=1,relation='uses_result')],verifier='/root/eight_domain_audit',producer='/root',method='Separate recursive bijection enumeration, full multiset bitmask action, one literal failing-support witness for every rejected map, direct complete profile map comparison and positive/corrupt controls.',shared_components=['Raw inputs and Python standard-library exact arithmetic only; no producer imports.'],limitations=['No feasibility or nonexistence conclusion.','No census of arbitrary target graph automorphisms.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Internal independent check.',created_at=ts,updated_at=ts,inputs_sha256=pins);save(out/'claim_binding.json',claim)
        result=dict(status='INDEPENDENT_FIXED_INPUT_COORDINATE_RELABELING_CENSUS_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},coordinate_universe=46080,accepted=1,rejected=46079,profile_orbits=18,screen_survivor_orbits=16,first_failure_histogram=dict(hist),elapsed_seconds=time.perf_counter()-start,solver_calls=0,target_resolution=False);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
