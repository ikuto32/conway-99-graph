"""Independent complete scalar/Cartesian block audit; no producer imports."""
from pathlib import Path
from itertools import combinations,product
from collections import defaultdict,Counter
from copy import deepcopy
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'second_count_profile_gram_diagnostic/'
PROFILE=I+'count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
CID='C-FIXED-HADAMARD-SECOND-EIGHT-COUNT-PROFILE-SCALAR-EXCLUSION'
PINS={D+'summary.json':'6964c137b4b81d2db3c6f654ee31de3cbd7f88f9c481374453ea8800e5b0641f',PROFILE:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',I+'count_master_eight_orbit_cut_sat_outcome/summary.json':'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def need(b,m):
    if not b:raise ValueError(m)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def catalogue():
    words=[w for w in product(range(3),repeat=6)if all(w.count(f)==2 for f in range(3))];triples=[]
    pairs=list(combinations(range(6),2))
    for ids in combinations(range(90),3):
        ws=[words[i]for i in ids]
        if any(sum(x==y for x,y in zip(u,v))>2 for u,v in combinations(ws,2)):continue
        good=True
        for a,b in pairs:
            actual=[[sum(w[a]==f and w[b]==h for w in ws)for h in range(3)]for f in range(3)]
            if any(actual[f][h]>(1 if f==h else 2)for f,h in product(range(3),repeat=2)):good=False;break
        if good:triples.append(ids)
    return words,triples
def scalar_check(row,groups,values,target):
    need(row['target']==target and [x['group']for x in row['terms']]==groups,'bound exact target/contributor set')
    for term,table in zip(row['terms'],values,strict=True):
        need(term['minimum']==min(table.values()) and term['maximum']==max(table.values()),'complete local extrema')
        for bound in ['minimum','maximum']:need(term[bound+'_witness']in table and table[term[bound+'_witness']]==term[bound],'raw extremum attainer')
    lo=sum(min(x.values())for x in values);hi=sum(max(x.values())for x in values)
    need(row['lower']==lo and row['upper']==hi and row['passes']==(lo<=target<=hi),'literal interval sum/verdict')
def cartesian(supports,target):
    result=set();count=0
    for choice in product(*supports):
        count+=1;s=tuple(sum(m[i] for m in choice) for i in range(len(target)))
        if all(x<=y for x,y in zip(s,target)):result.add(s)
    return result,count
def controls(fixture):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
        else:raise ValueError('accepted corruption '+name)
    identity=(1,0,0,0,1,0,0,0,1);cycle=(0,1,0,0,0,1,1,0,0);inverse=(0,0,1,1,0,0,0,1,0);target=(1,2,2,2,1,2,2,2,1)
    sets,n=cartesian([[identity],[cycle],[cycle],[inverse],[inverse]],target);need(sets=={target}and n==1,'known exact block positive')
    good=dict(target=2,terms=[dict(group=3,minimum=0,maximum=2,minimum_witness=0,maximum_witness=1)],lower=0,upper=2,passes=True);values=[{0:0,1:2}];scalar_check(good,[3],values,2)
    for label,path,v in [('target',['target'],1),('upper',['upper'],1),('verdict',['passes'],False)]:
        b=deepcopy(good);b[path[0]]=v;reject(label,lambda b=b:scalar_check(b,[3],values,2))
    for key,v in [('group',4),('minimum',1),('maximum',1),('maximum_witness',0),('minimum_witness',4)]:
        b=deepcopy(good);b['terms'][0][key]=v;reject(key,lambda b=b:scalar_check(b,[3],values,2))
    def genuine(F):
        C=fixture['cubic_core60'];need(len(F)==60 and all(len(r)==180 and all(type(v)is int and v in(0,1)for v in r)for r in F),'strict genuine factor')
        need(all(sum(F[i][d]*F[j][d]for d in range(180))==20*(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(60))+2-int(i//20==j//20)for i in range(60)for j in range(60)),'genuine integer Gram')
    F=fixture['factor60x180'];genuine(F);bad=deepcopy(F);bad[0][0]^=1;reject('genuine243_changed_bit',lambda:genuine(bad))
    return dict(known_exact_block_positive=True,known_bound_with_attainers_positive=True,genuine243_positive=True,rejected=rejected,fixed_support_full_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def load(p,h=None):
        got=sha(ROOT/p);need(h is None or got==h,'identity '+p);pins[p]=got;data=(ROOT/p).read_bytes();return json.loads(gzip.decompress(data)if p.endswith('.gz')else data)
    try:
        for p,h in PINS.items():load(p,h)
        discovery=load(D+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in discovery[field].items():need(sha(ROOT/p)==h,'frozen candidate identity '+p);pins[p]=h
        ctrl=controls(load(B+'srg243_residual_fixture/triangle_blocks.json'));write(out/'controls.json',ctrl)
        raw=load(RAW);p=load(PROFILE);local=load(LOCAL);words,triples=catalogue()
        need([list(w)for w in words]==local['words']and[list(t)for t in triples]==local['survivors']and len(triples)==31110,'all117480 original local triples checked')
        cols=raw['support_columns'];groups=[list(x)for x in dict.fromkeys(map(tuple,cols))];counts=p['coordinate_group_fibre_counts'];rankmap=defaultdict(list)
        need(p['profile_sha256']==discovery['profile_sha256']=='086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17','literal second profile')
        for i,t in enumerate(triples):rankmap[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
        ranks=[rankmap[tuple(v for a in s for v in counts[a][g])]for g,s in enumerate(groups)]
        need(ranks==p['local_survivor_indices_by_group']==load(D+'initial_domain_ranks.json')['local_survivor_indices_by_group']and all(ranks),'all20 complete initial domains')
        C=raw['core_adjacency'];G=[[12*(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(36))+2-int(i//12==j//12)for j in range(36)]for i in range(36)];need(G==raw['prescribed_Gram36'],'literal target Gram')
        saved=load(D+'all540_intervals.json');flat=[];fail=[];blockcounts=[];wholeproducts=prefixproducts=0;certificate=None
        pairs=[q for q in combinations(range(12),2)if q[0]//2!=q[1]//2]
        for pi,(a,b)in enumerate(pairs):
            q=load(D+f'pair_{pi:02d}.json.gz');need(q['coordinates']==[a,b]and q['pair_index']==pi,'complete pair order');gs=[g for g,s in enumerate(groups)if a in s and b in s];need(len(gs)==5,'five exact supports');allmat=[];allmaps=[]
            for g,gr in zip(gs,q['group_records'],strict=True):
                aa,bb=groups[g].index(a),groups[g].index(b);mapping={i:tuple(sum(words[w][aa]==f and words[w][bb]==h for w in triples[i])for f,h in product(range(3),repeat=2))for i in ranks[g]};realizing=defaultdict(list)
                for i,m in mapping.items():realizing[m].append(i)
                matrices=sorted(realizing);need(gr['group']==g and gr['local_positions']==[aa,bb]and gr['full_local_indices']==ranks[g]and gr['matrices']==[list(m)for m in matrices]and gr['realizing_local_indices']==[realizing[m]for m in matrices],'literal complete local matrix support')
                allmat.append(matrices);allmaps.append(mapping)
            target=tuple(G[12*f+a][12*h+b]for f,h in product(range(3),repeat=2));need(q['target']==list(target),'raw target block')
            for cell,row in enumerate(q['scalar_intervals']):
                values=[{i:m[cell]for i,m in mp.items()}for mp in allmaps];need(row['coordinates']==[a,b]and row['fibres']==list(divmod(cell,3)),'scalar cell order');scalar_check(row,gs,values,target[cell]);flat.append(row)
                if not row['passes']:
                    fail.append(row);certificate=dict(profile_sha256=p['profile_sha256'],coordinates=[a,b],fibres=list(divmod(cell,3)),target=target[cell],total_upper=sum(max(v.values())for v in values),groups=[dict(group=g,full_local_indices=ranks[g],minimum=min(table.values()),maximum=max(table.values()),options=[dict(local_index=i,word_indices=list(triples[i]),words=[list(words[w])for w in triples[i]],contribution=table[i])for i in ranks[g]])for g,table in zip(gs,values)])
            layers=q['DP_layers'];need(len(layers)==6,'all block prefixes')
            for depth in range(6):
                states,number=cartesian(allmat[:depth],target);prefixproducts+=number
                need(layers[depth]['states']==[list(s)for s in sorted(states)],'Cartesian prefix equality')
                if depth==5:wholeproducts+=number;feasible=target in states
                if depth:
                    for state,prev,idx in zip(layers[depth]['states'],layers[depth]['predecessors'],layers[depth]['option_indices'],strict=True):
                        need(tuple(state)==tuple(x+y for x,y in zip(layers[depth-1]['states'][prev],allmat[depth-1][idx])),'saved predecessor witness')
            need(q['feasible']==feasible,'actual complete block verdict')
            if feasible:
                witness=q['witness'];need(len(witness)==5,'five local witness options');summed=[0]*9
                for g,w,mp in zip(gs,witness,allmaps):
                    need(w['group']==g and tuple(w['matrix'])==mp[w['local_survivor_index']],'literal realizing witness')
                    summed=[x+y for x,y in zip(summed,w['matrix'])]
                need(summed==list(target),'positive block witness exact target')
            else:need(q['witness']is None,'no nonexistent witness')
            blockcounts.append(dict(pair_index=pi,coordinates=[a,b],feasible=feasible,support_sizes=list(map(len,allmat))))
        need(flat==saved['records']and fail==saved['violations']and len(flat)==540 and len(fail)==1,'all540 intervals exact')
        need(fail[0]==discovery['first_failed_scalar']and fail[0]['coordinates']==[9,11]and fail[0]['fibres']==[2,1]and fail[0]['upper']==1 and fail[0]['target']==2,'specified contradiction')
        need([r['pair_index']for r in blockcounts if not r['feasible']]==[59]and wholeproducts==261876,'all60 Cartesian blocks')
        write(out/'independent_scalar_certificate.json',certificate);write(out/'all_block_outcomes.json',dict(records=blockcounts,complete_products=wholeproducts,prefix_products=prefixproducts,scope='Separate block choices only; no simultaneous factor.'))
        for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_SECOND_COUNT_SCALAR_OBSTRUCTION.md','uv.lock','pyproject.toml']:pins[path]=sha(ROOT/path)
        stamp=datetime.now(timezone.utc).isoformat();scope='One exact second count profile on the literal six-prism Hadamard support, prescribed integer Gram and within-triplicate column caps. Cross-group caps and residual D are not used.'
        limitations=['No exclusion of other count profiles, the whole support, core or unrestricted target.','The59 surviving blocks are independent choices, not a joint factor.','Prior count-CSP SAT witness remains valid in its weaker model.','Reviewer produced the separate second-lift CNF earlier; this checking path does not read or import that formula/source.','No solver or DRAT replay.']
        shared=['Raw independently established profile/core/catalogue inputs; standard-library integer arithmetic only. No producer imports or DP reuse.','All local triples independently enumerated and complete prefix products computed directly; no assumed hypothetical graph automorphism.']
        binding=dict(id=CID,revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For literal count profile086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17, the required Gram entry between coordinate9/fibre2 and coordinate11/fibre1 is2, while complete count-compatible within-cap local domains in groups1,5,8,18,19 bound its contribution by0+0+1+0+0=1. Therefore no prescribed-Gram factor with within-triplicate column caps realizes this profile. Independently checked540 scalar intervals have exactly this one failed cell; complete separate block checks find pair(9,11) infeasible and the other59 feasible.',scope=scope,assumptions=['Exact pinned second count table, raw core/support and complete local catalogue with within-triplicate caps.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-CUT-COUNT-CSP-WITNESS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],verifier='/root/eight_domain_audit',producer='/root/structural_attack',checking_method='Literal local catalogue reconstruction and full domain matrix evaluation; exhaustive Cartesian prefix products rather than producer DP, exact extrema and attainers.',shared_components=shared,limitations=limitations,created_at=stamp,updated_at=stamp,inputs_sha256=pins,outputs_sha256={x.relative_to(ROOT).as_posix():sha(x)for x in out.iterdir()if x.is_file()})
        write(out/'claim_binding.json',binding);need(time.perf_counter()-start<120,'120second bounded review')
        write(out/'summary.json',dict(status='INDEPENDENT_SECOND_COUNT_PROFILE_SCALAR_OBSTRUCTION_PASS',timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={x.relative_to(ROOT).as_posix():sha(x)for x in out.iterdir()if x.is_file()},claim_id=CID,claim_revision=1,local_triples_checked=117480,local_survivors=31110,initial_domains=20,scalar_cells=540,failed_scalar_cells=1,feasible_blocks=59,infeasible_blocks=1,complete_block_products=wholeproducts,complete_prefix_products=prefixproducts,obstruction=dict(coordinates=[9,11],fibres=[2,1],groups=[1,5,8,18,19],maxima=[0,0,1,0,0],upper=1,target=2),controls=ctrl,scope=scope,shared_components=shared,limitations=limitations,native_calls=0,proof_replays=0,target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status='INDEPENDENT_SECOND_COUNT_PROFILE_SCALAR_OBSTRUCTION_PASS',summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
