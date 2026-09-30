"""Independent literal outer-product and low-pivot GF2 certificate audit."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,combinations_with_replacement,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_gram_affine_gf2'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';COUNT=B/'20260930_independent_review/count_master_sat_outcome/independent_count_profile.json';BATCH=B/'20260930_hadamard_seven_remaining_cnfs/run02/summary.json'
PLAN=ROOT/'docs/AUDIT_20260930_HADAMARD_GRAM_AFFINE_GF2.md'
PINS={D/'summary.json':'cd2a3a876f676b28c76e08cc28584a60f1909a5f8a45e994bfb8c55e1a7f33db',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',COUNT:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',BATCH:'eabd989bd427c6fcfc57564d62b907d80630f1b5c7b7d56df17fa09f2df16119',B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',B/'20260930_independent_review/hadamard_seven_profile_local_domains/summary.json':'764918cdb953f10f378304db4448000a8eee9b8e721e750fc62870df98fdbe2d',B/'20260930_independent_review/eight_count_profile_lift/summary.json':'270d6c53406887c328f4ccbcdc670da5a0e3de156733a2dbd9145582f0cb1802'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,v):
    with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def xor_selected(vectors,bits):
    result=0
    while bits:
        one=bits&-bits;i=one.bit_length()-1;need(i<len(vectors),'representation index');result^=vectors[i];bits-=one
    return result
def low_reduce(vector,basis):
    while vector:
        p=(vector&-vector).bit_length()-1
        if p not in basis:return vector
        vector^=basis[p][0]
    return 0
def low_basis(vectors):
    basis={}
    for i in range(len(vectors)-1,-1,-1):
        v=vectors[i];rep=1<<i
        while v:
            p=(v&-v).bit_length()-1
            if p not in basis:basis[p]=(v,rep);break
            v^=basis[p][0];rep^=basis[p][1]
    for p,(v,rep)in basis.items():need(v and (v&-v).bit_length()-1==p and xor_selected(vectors,rep)==v,'literal independent rank lower-bound certificate')
    need(all(low_reduce(v,basis)==0 for v in vectors),'rank upper-bound span coverage')
    return basis
def serialize_basis(basis):return [dict(pivot=p,vector_hex=hex(v),original_generator_combination_hex=hex(rep))for p,(v,rep)in sorted(basis.items())]
def calibration():
    checked=0;rejected=[]
    for vectors in product(range(4),repeat=3):
        reachable={0}
        for v in vectors:reachable|={x^v for x in list(reachable)}
        basis=low_basis(vectors);need(2**len(basis)==len(reachable),'small exact rank')
        for target in range(4):need((low_reduce(target,basis)==0)==(target in reachable),'all exhaustive subset sums');checked+=1
    need(low_reduce(3,low_basis([1,2]))==0 and low_reduce(2,low_basis([1]))!=0,'known positive and negative')
    for name,fn in [('false_combination',lambda:need(xor_selected([3,5],1)==6,'false XOR')),('wrong_rank',lambda:need(len(low_basis([3,5]))==1,'false rank')),('out_of_range_index',lambda:xor_selected([3,5],4))]:
        try:fn()
        except ValueError:rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    return dict(exhaustive_tiny_membership_cases=checked,rank_cases=64,rejected=rejected)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or v==h,'input identity '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        report=read(D/'summary.json')
        for name,h in {**report['inputs_sha256'],**report['outputs_sha256']}.items():pin(ROOT/name,h)
        pin(Path(__file__));pin(PLAN);control=calibration();save(out/'controls.json',control)
        raw=read(RAW);cat=read(LOCAL);words=cat['words'];triples=cat['survivors'];need(len(words)==90 and len(triples)==31110,'authenticated full catalogue population')
        C=raw['core_adjacency'];neighbors=[{j for j,v in enumerate(row)if v}for row in C]
        K=[[12*int(i==j)+2-int(i//12==j//12)-C[i][j]-len(neighbors[i]&neighbors[j])for j in range(36)]for i in range(36)];need(K==raw['prescribed_Gram36'],'literal core-neighbour Gram')
        groups=[]
        for d in range(60):
            s=[a for a in range(12)if raw['L'][a][d]]
            if s not in groups:groups.append(s)
        need(len(groups)==20 and all(len(s)==6 and sum([a in s for a in range(12)])==6 for s in groups),'twenty raw supports')
        cells=[(a,f,a,f)for a in range(6)for f in range(3)]+[(a,f,b,z)for a,b in combinations(range(6),2)for f,z in product(range(3),repeat=2)];localindex={cell:i for i,cell in enumerate(cells)}
        fullcells=[(a,f,a,f)for a in range(12)for f in range(3)]+[(a,f,b,z)for a,b in combinations(range(12),2)if a^1!=b for f,z in product(range(3),repeat=2)];globalindex={cell:i for i,cell in enumerate(fullcells)}
        need(len(cells)==153 and len(fullcells)==576,'independently ordered cell lists')
        mapping=[[globalindex[s[a],f,s[b],z]for a,f,b,z in cells]for s in groups];vectors=[];countindex=defaultdict(list)
        for ti,tri in enumerate(triples):
            v=0;counts=[[0]*3 for _ in range(6)]
            for wi in tri:
                rows=[3*a+f for a,f in enumerate(words[wi])]
                for a,f in enumerate(words[wi]):counts[a][f]+=1
                for u,w in combinations_with_replacement(rows,2):
                    a,f=divmod(u,3);b,z=divmod(w,3);v^=1<<localindex[a,f,b,z]
            vectors.append(v);countindex[tuple(sum(counts,[]))].append(ti)
        balanced=countindex[(1,)*18];need(len(balanced)==150,'full balanced rank class')
        def lift(vector,g):
            result=0
            for i,j in enumerate(mapping[g]):
                if vector>>i&1:result|=1<<j
            return result
        target=sum((K[12*f+a][12*z+b]%2)<<i for i,(a,f,b,z)in enumerate(fullcells))
        need(all(K[12*f+a][12*z+b]==0 for a in range(12)for b in range(12)for f,z in product(range(3),repeat=2)if a^1==b or(a==b and f!=z)),'omitted Gram entries automatically zero')
        count=read(COUNT);eight=[]
        for g,s in enumerate(groups):
            wanted=tuple(x for a in s for x in count['coordinate_group_fibre_counts'][a][g]);ids=countindex[wanted];need(ids==count['local_survivor_indices_by_group'][g],'complete eight-profile class');eight.append(ids)
        cases=[('full_local_catalogue',[list(range(31110))for _ in range(20)]),('literal_eight_count_profile',eight)]
        batch=read(BATCH);need(len(batch['records'])==215 and len({r['profile_id']for r in batch['records']})==215,'frozen215 distinct selected cases')
        for r in batch['records']:
            p=read((ROOT/r['scope_path']).parent/'selected_profile.json');domains=[]
            for g,s in enumerate(groups):
                if g in p['group_ids']:
                    side=p['group_ids'].index(g);ref=p['local_domains'][side];pin(ROOT/ref['path'],ref['sha256']);domain=read(ROOT/ref['path']);wanted=tuple(1+p['coordinate_fibre_deviations'][a][f][side]for a in s for f in range(3));ids=countindex[wanted]
                    need(ids==domain['local_survivor_indices']and len(ids)==ref['count'],'complete seven-profile class from every raw local triple')
                else:ids=balanced
                domains.append(ids)
            cases.append((p['id'],domains))
        need([x[0]for x in cases]==[r['identity']for r in report['records']]and len(cases)==217,'whole named model population and order')
        cache={};saved=[];corrupt=[]
        def check_case(rec,domains,write_basis=False):
            need(rec['domain_counts']==list(map(len,domains))and len(rec['references'])==20,'complete domain count metadata');auth=[];rhs=target;localinfo=[]
            need(all(type(x)is int and x in ids for x,ids in zip(rec['references'],domains)),'authentic references')
            for g,ids in enumerate(domains):
                ref=rec['references'][g];need(ref==ids[0],'frozen original reference convention');rhs^=lift(vectors[ref],g)
                entries=[x for x in rec['generators']if x['group']==g];chosen=[x['local_survivor_index']for x in entries]
                need(len(chosen)==len(set(chosen))and all(x in ids and x!=ref for x in chosen),'authentic distinct raw generator options');need(all(x['reference_local_survivor_index']==ref for x in entries),'generator reference consistency')
                cachekey=(tuple(ids),ref,tuple(chosen))
                if cachekey not in cache:
                    differences=[vectors[i]^vectors[ref]for i in chosen];basis=low_basis(differences);need(len(basis)==len(chosen),'saved local generator subset independent')
                    need(all(low_reduce(vectors[i]^vectors[ref],basis)==0 for i in ids),'all initial domain differences spanned')
                    entry=dict(domain_ids=ids,reference=ref,saved_generator_local_indices=chosen,local_affine_rank=len(basis),domain_size=len(ids),basis=serialize_basis(basis),all_domain_differences_checked=True);cache[cachekey]=len(cache);save(out/f'local_span_{cache[cachekey]:03d}.json',entry)
                localinfo.append(cache[cachekey])
            need(all(type(r['group'])is int and 0<=r['group']<20 for r in rec['generators']),'valid generator groups')
            for r in rec['generators']:auth.append(lift(vectors[r['local_survivor_index']]^vectors[r['reference_local_survivor_index']],r['group']))
            cert=rec['certificate'];need(cert['feasible']is True and cert['residual_hex']=='0x0'and cert['separating_functional_hex']is None,'explicit positive certificate')
            selected=cert['selected_generators'];need(isinstance(selected,list)and len(set(selected))==len(selected)and all(type(i)is int and 0<=i<len(auth)for i in selected),'exact selected generator list');value=0
            for i in selected:value^=auth[i]
            need(value==rhs==int(rec['target_minus_references_hex'],16),'literal original XOR witness equals raw target minus references')
            basis=low_basis(auth);need(len(basis)==cert['rank'],'independent reverse/low-pivot rank agrees')
            return dict(identity=rec['identity'],local_span_records=localinfo,global_generators=len(auth),global_rank=len(basis),selected_generator_count=len(selected),target_hex=hex(target),residual_target_hex=hex(rhs),certificate_XOR_hex=hex(value),independent_global_basis=serialize_basis(basis),complete_domain_coverage=True,affine_membership=True)
        for i,(identity,domains)in enumerate(cases):
            rec=read(D/(identity+'.json'));need(rec['identity']==identity,'exact case record');checked=check_case(rec,domains);need(checked['global_rank']==report['records'][i]['rank']and checked['global_generators']==report['records'][i]['generators'],'summary rank/generator binding');save(out/f'case_{i:03d}.json',checked);saved.append({k:v for k,v in checked.items()if k!='independent_global_basis'})
            if i in(0,1):
                for name in('bad_xor','wrong_rank','duplicate_generator','false_domain','wrong_target'):
                    bad=deepcopy(rec)
                    if name=='bad_xor':bad['certificate']['selected_generators'].pop()
                    elif name=='wrong_rank':bad['certificate']['rank']+=1
                    elif name=='duplicate_generator':bad['generators'].append(deepcopy(bad['generators'][0]))
                    elif name=='false_domain':bad['generators'][0]['local_survivor_index']=31110
                    else:bad['target_minus_references_hex']=hex(int(bad['target_minus_references_hex'],16)^1)
                    try:check_case(bad,domains)
                    except(ValueError,IndexError,KeyError):corrupt.append(dict(case=identity,name=name))
                    else:raise ValueError('accepted corruption '+name)
            need(time.perf_counter()-start<180,'180-second audit allocation')
        need(len(cache)==report['compressed_distinct_domains']==215,'exact unique complete local-domain spans')
        hist=Counter(r['global_rank']for r in saved);need(hist==Counter({193:216,323:1}),'actual independent rank histogram');save(out/'records.json',saved);save(out/'research_corruptions.json',corrupt)
        stamp=datetime.now(timezone.utc).isoformat();statement='For the217 explicitly named fixed-support local-domain models (full31110 local catalogue in each group, one saved eight-count profile, and215 saved seven-count profiles), the prescribed576-entry Gram parity vector lies in the sum of the20 complete local affine spans over GF(2). Every saved XOR witness is valid. The complete global difference-span ranks are323 for the full catalogue model and193 for each216 fixed-count model. This is affine relaxation consistency only, not selection of one local option per group.'
        save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-217-AFFINE-GRAM-GF2-NONOBSTRUCTIONS',revision=1,kind='finite_check',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope='Exactly217 authenticated fixed-support local-domain models; no factor or target existence/exclusion conclusion.',dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='verification_dependency')],verifier='/root/structural_attack',producer='/root',checking_method='Raw rank-one column outer products, complete original-domain span checking, literal XOR certificates and reverse/low-pivot exact ranks with saved representations.',shared_components=['Authenticated raw catalogue and previously reviewed literal domain records are premises; rechecked full count classes here.','Python integer/XOR arithmetic and standard-library hashing.','No producer imports or elimination helper sharing.'],inputs_sha256=pins,limitations=['Arbitrary affine XOR sums need not select one local triple per group.','The passing parity screen does not undo any exact integral/CNF exclusion.','No target-wide coverage or residual D conclusion.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal review only.',created_at=stamp,updated_at=stamp))
        summary=dict(status='INDEPENDENT_FIXED_SUPPORT_AFFINE_GRAM_GF2_SCREEN_PASS',timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},models=217,positive_XOR_certificates=217,local_Gram_vectors_reconstructed=31110,complete_distinct_local_spans=215,global_rank_histogram=dict(hist),local_cells=153,global_cells=576,controls=control,research_corruptions_rejected=len(corrupt),statement=statement,solver_calls=0,native_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
