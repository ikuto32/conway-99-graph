"""Independent raw catalogue, relation, and deletion-certificate review; no producer imports."""
import argparse, copy, hashlib, json, platform, subprocess, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_four_group_local_screen'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
CIR=B/'20260930_independent_review/hadamard_four_group_circuits'
FIX=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS={D/'summary.json':'7773d527456ea88913a543a19d0d49c0b5c339f7dfdccddce604822682620b7d',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',CIR/'summary.json':'efc6df8951399b99c6c3a68ebb084ead094f3cd147832f806d3604df4c65fb46',CIR/'claim_binding.json':'0021449d34970ee7bc1a9c1d857445cbd3a1038f30158c6f337349ab1f4b0278'}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def read(p): return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def sparse(columns):
    counts=Counter()
    for col in columns:
        for i,j in combinations_with_replacement(sorted(col),2):counts[i,j]+=1
    return counts
def gram_ok(a,b,K):
    # Direct integer sum for all possibly occupied entries; no producer bit masks.
    return all(v+b.get((i,j),0)<=K[i][j] for (i,j),v in a.items()) and all(v<=K[i][j] for (i,j),v in b.items())
def cap_ok(a,b):return all(len(x.intersection(y))<=2 for x in a for y in b)
def tables_from_forward(rows,n):
    back=[0]*n
    for i,bits in enumerate(rows):
        need(bits>=0 and bits>>n==0,'forward mask range')
        for j in range(n):
            if bits>>j&1:back[j]|=1<<i
    return back
def replay_ac(saved,sizes,tables):
    masks=[(1<<n)-1 for n in sizes]
    for s in saved['removals']:
        i,j,k=s['left'],s['right'],s['option_index']
        need(0<=i<4 and 0<=j<4 and i!=j and 0<=k<sizes[i],'deletion indices')
        need(masks[i]>>k&1,'deleted option currently live')
        need(int(s['right_domain_mask'],16)==masks[j],'exact contemporaneous support domain')
        need(tables[i,j][k]&masks[j]==0,'deletion has no live support')
        masks[i]&=~(1<<k)
    need([int(v,16) for v in saved['final_masks']]==masks,'replayed final domains')
    need(saved['final_domain_sizes']==[x.bit_count() for x in masks],'final domain sizes')
    need(saved['empty']==any(x==0 for x in masks),'empty classification')
    supports=[]
    for i in range(4):
        for j in range(4):
            if i==j:continue
            for k in range(sizes[i]):
                if masks[i]>>k&1:
                    live=tables[i,j][k]&masks[j];need(live!=0,'every final option has a support in every other domain')
                    supports.append([i,j,k,(live&-live).bit_length()-1])
    return masks,supports
def profiles(k):
    # Exhaust integer count bounds for both signs, rather than assuming a vector list.
    vectors=[v for v in product(range(-2,3),repeat=3) if sum(v)==0 and all(0<=1+x<=3 and 0<=1-x<=3 for x in v)]
    vectors.sort(key=lambda v:(v!=(0,0,0),v))
    return [p for p in product(vectors,repeat=k) if any(any(v) for v in p) and all(sum(v[f] for v in p)==0 for f in range(3))]
def derive_gram(raw):
    C=[[int((i%12==j%12 and i//12!=j//12) or (i//12==j//12 and (i%12)^1==j%12)) for j in range(36)] for i in range(36)]
    need(C==raw['core_adjacency'],'literal six-prism core')
    K=[[12*int(i==j)+2-C[i][j]-sum(C[i][k]*C[k][j] for k in range(36))-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(K==raw['prescribed_Gram36'],'Gram derived from raw core')
    return K
def catalogue(K):
    words=[w for w in product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))]
    columns=[frozenset(12*f+2*a for a,f in enumerate(w)) for w in words]
    survivors=[];signatures=defaultdict(list)
    # All unordered triples are complete: a duplicate column repeats a fibre pair
    # of prescribed Gram one, and so cannot occur in an actual factor.
    for tri in combinations(range(90),3):
        cols=[columns[w] for w in tri]
        if any(len(cols[i]&cols[j])>2 for i,j in combinations(range(3),2)):continue
        counts=sparse(cols)
        if any(v>K[i][j] for (i,j),v in counts.items()):continue
        index=len(survivors);survivors.append(list(tri))
        signature=tuple(sum(words[w][a]==f for w in tri) for a in range(6) for f in range(3))
        signatures[signature].append(index)
    return words,survivors,signatures
def controls(K):
    f=read(FIX)['factor60x180'];G=[[sum(x*y for x,y in zip(a,b)) for b in f] for a in f]
    cols=[frozenset(i for i in range(60) if f[i][d]) for d in range(180)]
    positive=0
    for i,j in combinations(range(8),2):
        a,b=cols[3*i:3*i+3],cols[3*j:3*j+3]
        need(gram_ok(sparse(a),sparse(b),G) and cap_ok(a,b),'known243 exact positive');positive+=1
    need(not cap_ok(cols[:3],cols[:3]),'duplicated known column rejected')
    # A two-colour triangle is arc-consistent but has no joint choice.
    tables={(i,j):[2,1] if i<3 and j<3 else [3,3] for i in range(4) for j in range(4) if i!=j}
    empty_record=dict(removals=[],final_masks=['0x3']*4,final_domain_sizes=[2]*4,empty=False)
    _,sp=replay_ac(empty_record,[2]*4,tables)
    joint=[x for x in product(range(2),repeat=4) if all(tables[i,j][x[i]]>>x[j]&1 for i in range(4) for j in range(4) if i!=j)]
    need(not joint and len(sp)==24,'AC is not joint feasibility')
    need([len(profiles(k)) for k in [1,2,3]]==[0,6,30],'complete integer profile calibration')
    need(Counter(sum(any(v) for v in p) for p in profiles(3))=={2:18,3:12},'three-coordinate structural profile count')
    return dict(genuine243_pair_positives=positive,arc_consistent_joint_unsat_control=True,profile_counts=[0,6,30])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or v==h,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        s=read(D/'summary.json')
        for p,h in {**s['inputs_sha256'],**s['outputs_sha256']}.items():pin(ROOT/p,h)
        gate=read(CIR/'summary.json');need(gate['status']=='INDEPENDENT_HADAMARD_FOUR_GROUP_CIRCUIT_NECESSITY_PASS','circuit gate')
        pin(CIR/'independent_circuits.json',gate['outputs_sha256'][key(CIR/'independent_circuits.json')])
        raw=read(RAW);K=derive_gram(raw);words,triples,signatures=catalogue(K);local=read(LOCAL)
        need([list(w) for w in words]==local['words'] and triples==local['survivors'],'complete independently regenerated 31110 local catalogue')
        need(len(triples)==31110,'catalogue population')
        groups=list(dict.fromkeys(tuple(i for i in range(12) if raw['L'][i][d]) for d in range(60)))
        cir=[c for c in read(CIR/'independent_circuits.json')['records'] if len(c['common_support'])>=2]
        universe=read(D/'profile_universe.json');need(universe['circuits']==cir,'exact fourteen-circuit order')
        expected=[dict(case=i,circuit_index=ci,profile_index=pi,profile=[list(v) for v in p]) for i,(ci,pi,p) in enumerate((ci,pi,p) for ci,c in enumerate(cir) for pi,p in enumerate(profiles(len(c['common_support']))))]
        need(universe['records']==expected and universe['population']==108,'complete profile coverage')
        cache={};audits=[];counts=Counter();support_records=[];checks=controls(K)
        def features(group,index):
            ck=(group,index)
            if ck not in cache:
                cols=[frozenset(12*words[w][a]+coordinate for a,coordinate in enumerate(groups[group])) for w in triples[index]]
                val=sparse(cols);need(all(v<=K[i][j] for (i,j),v in val.items()),'mapped local Gram caps')
                cache[ck]=(cols,val)
            return cache[ck]
        for item in tqdm(expected,desc='Independent four-group pair tables',mininterval=1):
            ci=item['circuit_index'];c=cir[ci];rec=read(D/f"case_{item['case']:03d}.json")
            for field in ['case','circuit_index','profile_index','profile']:need(rec[field]==item[field],'case identity '+field)
            for field in ['groups','relation','common_support']:need(rec[field]==c[field],'circuit binding '+field)
            prof=dict(zip(c['common_support'],item['profile']));domains=[]
            for g,sign in zip(c['groups'],c['relation']):
                sig=tuple(1+sign*prof.get(a,(0,0,0))[f] for a in groups[g] for f in range(3));domains.append(signatures.get(sig,[]))
            need(rec['local_survivor_indices']==domains and rec['domain_sizes']==list(map(len,domains)),'complete profile domains')
            Tg={};Tb={};need(len(rec['pairs'])==6,'all six group-pair relations')
            for (left,right),pr in zip(combinations(range(4),2),rec['pairs'],strict=True):
                fg=[];fb=[]
                for li in domains[left]:
                    ca,ga=features(c['groups'][left],li);bitsg=bitsb=0
                    for j,ri in enumerate(domains[right]):
                        cb,gb=features(c['groups'][right],ri);gok=gram_ok(ga,gb,K);bok=gok and cap_ok(ca,cb)
                        if gok:bitsg|=1<<j
                        if bok:bitsb|=1<<j
                        counts['option_pairs']+=1
                    fg.append(bitsg);fb.append(bitsb)
                need(pr['sides']==[left,right] and pr['population']==len(domains[left])*len(domains[right]),'pair identity/population')
                need([int(x,16) for x in pr['gram_forward_masks']]==fg,'complete literal Gram relation')
                need([int(x,16) for x in pr['both_forward_masks']]==fb,'complete literal Gram+cap relation')
                need(pr['gram_compatible']==sum(x.bit_count() for x in fg) and pr['gram_and_caps_compatible']==sum(x.bit_count() for x in fb),'relation counts')
                Tg[left,right]=fg;Tg[right,left]=tables_from_forward(fg,len(domains[right]))
                Tb[left,right]=fb;Tb[right,left]=tables_from_forward(fb,len(domains[right]))
            ar=[]
            for field,tables in [('gram_ac',Tg),('gram_caps_ac',Tb)]:
                masks,supports=replay_ac(rec[field],list(map(len,domains)),tables)
                counts[field+'_removals']+=len(rec[field]['removals']);counts[field+'_empty']+=any(x==0 for x in masks)
                support_records.append(dict(case=item['case'],relation=field,supports=supports))
                ar.append(dict(relation=field,final_sizes=[x.bit_count() for x in masks],removals=len(rec[field]['removals']),support_witnesses=len(supports),empty=any(x==0 for x in masks)))
            audits.append(dict(**item,groups=c['groups'],domain_sizes=list(map(len,domains)),relations=ar))
            cs=s['case_summaries'][item['case']]
            need(cs['case']==item['case'] and cs['domain_sizes']==rec['domain_sizes'] and cs['final_sizes']==rec['gram_caps_ac']['final_domain_sizes'] and cs['gram_ac_empty']==rec['gram_ac']['empty'] and cs['gram_caps_ac_empty']==rec['gram_caps_ac']['empty'],'saved per-case summary')
            need(cs['path']==key(D/f"case_{item['case']:03d}.json") and cs['sha256']==pins[cs['path']],'case raw hash')
        need(counts['option_pairs']==1358856==s['option_pair_attempts'],'all pair attempts')
        need(counts['gram_ac_empty']==counts['gram_caps_ac_empty']==12 and s['unresolved_cases']==96,'complete scoped outcomes')
        need(s['completed_cases']==s['profile_cases']==108 and s['circuits']==14 and s['initial_empty_cases']==0,'stage counts')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        reject('missing_profile',lambda:need(universe['records'][:-1]==expected,'coverage'))
        reject('nonconserving_profile',lambda:need(((1,-1,0),(0,1,-1)) in profiles(2),'conservation'))
        reject('amplitude_two_profile',lambda:need(((2,-1,-1),(-2,1,1)) in profiles(2),'opposite sign nonnegativity'))
        reject('missing_local_triple',lambda:need(local['survivors'][:-1]==triples,'complete catalogue'))
        reject('out_of_range_forward_mask',lambda:tables_from_forward([4],2))
        rec=read(D/'case_048.json');sizes=rec['domain_sizes'];tg={}
        for pr in rec['pairs']:
            i,j=pr['sides'];rows=[int(x,16) for x in pr['both_forward_masks']];tg[i,j]=rows;tg[j,i]=tables_from_forward(rows,sizes[j])
        bad=copy.deepcopy(rec['gram_caps_ac']);bad['removals'][0]['right_domain_mask']='0x0';reject('wrong_deletion_domain',lambda:replay_ac(bad,sizes,tg))
        bad=copy.deepcopy(rec['gram_caps_ac']);bad['final_domain_sizes'][0]+=1;reject('wrong_final_size',lambda:replay_ac(bad,sizes,tg))
        bad=copy.deepcopy(rec['gram_caps_ac']);bad['empty']=not bad['empty'];reject('wrong_outcome',lambda:replay_ac(bad,sizes,tg))
        bad=copy.deepcopy(rec['gram_caps_ac']);bad['removals']=bad['removals'][1:];reject('missing_deletion',lambda:replay_ac(bad,sizes,tg))
        save(out/'controls.json',dict(**checks,corruptions_rejected=rejected))
        save(out/'independent_cases.json',dict(records=audits,counts=dict(counts),excluded_cases=[r['case'] for r in audits if r['relations'][1]['empty']]))
        save(out/'fixed_point_supports.json',dict(records=support_records,scope='Explicit support witnesses only; no simultaneous four-choice witness.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_LOCAL_SCREEN.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,native_solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For the fixed six-prism Hadamard support, every binary prescribed-Gram factor satisfying all outside-column overlap caps and having exactly four unbalanced support groups belongs to one of the 108 saved signed count profiles on the 14 necessary circuit quartets. The complete local-cap-filtered triple catalogue and pair relations exclude exactly 12 profiles by replayed arc-consistency deletion certificates; the other 96 reach nonempty checked fixed points only.',scope='108 explicitly labelled necessary profiles for exactly four exceptional groups in the fixed-support Gram-plus-column-cap family; 96 outcomes remain unresolved.',assumptions=['The exact fixed support and prescribed integer Gram.','All distinct outside columns have overlap at most two.','Exactly four triplicate-support groups have nonzero coordinate/fibre count deviations.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-FOUR-GROUP-CIRCUIT-NECESSITY',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Independent full word-triple enumeration, raw sparse integer Gram sums and literal set intersections for every option pair; replayed deletions and explicit final supports.',shared_components=['Raw support and saved artifacts only; no producer code imports.','Independent earlier circuit theorem; Python integer arithmetic and standard libraries.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Workspace review artifacts pending parent publication.',external_review=None,external_review_reason='No external peer review asserted.',limitations=['Local domains already impose within-group column caps; not an abstract Gram-only exclusion.','Pairwise Gram bounds and arc consistency do not establish simultaneous four-group feasibility.','No full factor, residual graph or target construction; no unrestricted exclusion or coverage measure.','Profile counts are labelled and may be related by relabelling; exclusions must not be summed as graph coverage.'],created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_HADAMARD_FOUR_GROUP_LOCAL_PROFILE_SCREEN_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},local_word_triples_examined=117480,local_survivors=31110,circuits=14,profiles=108,complete_option_pair_checks=counts['option_pairs'],excluded_profiles=12,unresolved_profiles=96,counts=dict(counts),corruptions_rejected=len(rejected),native_solver_calls=0,target_resolution=False)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=time.perf_counter()-start)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
