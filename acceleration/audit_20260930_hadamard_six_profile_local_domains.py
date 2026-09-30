"""Independent literal local-domain reconstruction; no producer imports."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_six_profile_local_domains'
G=B/'20260930_independent_review/hadamard_six_rank4_profiles'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
FIX=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
CID='C-FIXED-HADAMARD-SIX-EXCEPTION-LOCAL-DOMAIN-FILTER'
PINS={D/'summary.json':'b402b07d6d34776a9c54c8dc3905a37ac5e9cf880a7ce98283c788f3627c7809',G/'summary.json':'0430355de5159a5223c464d3766ec54206a37177b90e18cf92364d276dd483e3',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIX:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')
def identity(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def gram(columns):
    counts=Counter()
    for column in columns:
        for r in column:
            for s in column:counts[r,s]+=1
    return counts
def allowed(columns,K):
    return all(len(a & b)<=2 for a,b in combinations(columns,2)) and all(n<=K[r][s] for (r,s),n in gram(columns).items())
def catalog(K):
    # Select positions of fibre0 then fibre1; lexicographically sort only after
    # the independently generated complete word population is materialized.
    words=[]
    for p0 in combinations(range(6),2):
        for p1 in combinations([a for a in range(6) if a not in p0],2):
            words.append(tuple(0 if a in p0 else 1 if a in p1 else 2 for a in range(6)))
    words.sort();need(len(words)==len(set(words))==90,'ninety balanced words')
    cols=[frozenset(12*f+2*a for a,f in enumerate(word)) for word in words]
    # Direct raw pair counts: no catalogue signature supplied by producer.
    triples=[];by_signature=defaultdict(list)
    for t in tqdm(combinations(range(90),3),total=117480,desc='Independent local triples',mininterval=1):
        chosen=[cols[i] for i in t]
        if not allowed(chosen,K):continue
        rank=len(triples);triples.append(list(t))
        sig=tuple(sum(12*f+2*a in c for c in chosen) for a in range(6) for f in range(3))
        by_signature[sig].append(rank)
    return words,triples,by_signature

def local_integer_choices(groups):
    H=[[1]*6]+[[int(a in g) for g in groups] for a in range(12)]
    kernel=[v for v in product(range(-1,3),repeat=6) if all(sum(h*x for h,x in zip(row,v))==0 for row in H)]
    choices=[]
    for a in range(12):
        vectors=[v for v in kernel if all(a in groups[j] or x==0 for j,x in enumerate(v))];vs=set(vectors);row=[]
        for first in vectors:
            for second in vectors:
                third=tuple(-x-y for x,y in zip(first,second))
                if third in vs:row.append([list(first),list(second),list(third)])
        choices.append(row)
    return H,choices

def decode_path(path,choices,groups,H):
    need(len(path)==12 and all(type(v) is int and 0<=v<len(choices[a]) for a,v in enumerate(path)),'complete legal integer path')
    dev=[choices[a][v] for a,v in enumerate(path)]
    need(all(sum(dev[a][f][j] for f in range(3))==0 for a in range(12) for j in range(6)),'coordinate fibre sums')
    need(all(sum(dev[a][f][j] for a in range(12))==0 for f in range(3) for j in range(6)),'group fibre quotas')
    need(all(any(dev[a][f][j] for a in range(12) for f in range(3)) for j in range(6)),'exactly six active groups')
    for a in range(12):
        for f in range(3):
            v=dev[a][f]
            need(all(-1<=x<=2 and (a in groups[j] or x==0) for j,x in enumerate(v)),'support/count bounds')
            need(all(sum(h*x for h,x in zip(row,v))==0 for row in H),'literal kernel constraints')
    return dev

def check_domain(saved,sig,indices):
    need(saved['count_signature']==list(sig),'exact eighteen counts')
    need(saved['local_catalog_path']==key(LOCAL) and saved['local_catalog_sha256']==PINS[LOCAL],'raw local catalogue binding')
    need(saved['local_survivor_indices']==indices and saved['count']==len(indices),'complete ordered catalogue rank list')

def check_record(rec,expected,domains):
    for field in ['id','rank4_case','group_ids','choice_path','profile_sha256','coordinate_fibre_deviations']:
        need(rec[field]==expected[field],'exact profile '+field)
    need(rec['normalization_used_for_filtering'] is False,'no diagnostic orbit pruning')
    need(rec['empty_groups']==[] and rec['retained_by_individual_local_domains'] is True,'local nonempty result only')
    need(len(rec['local_domains'])==6,'all exceptional groups represented')
    for ref,(g,sig,indices) in zip(rec['local_domains'],domains,strict=True):
        need(ref['group']==g and ref['count']==len(indices)>0,'group/domain count')
        expected_path=key(D/'domains'/(identity(list(sig))+'.json'))
        need(ref['path']==expected_path,'literal domain signature identifier')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,expected=None):
        h=sha(p);need(expected is None or h==expected,'hash '+key(p));pins[key(p)]=h;return h
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D/'summary.json');previous=read(G/'summary.json')
        need(previous['status']=='INDEPENDENT_SIX_RANK4_INTEGER_MARGINAL_CENSUS_PASS','independent complete population gate')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        positive_path=G/'all_positive_marginal_profiles.json';pin(positive_path,previous['outputs_sha256'][key(positive_path)]);population=read(positive_path)
        need(population['total_labelled_profiles']==984 and len(population['records'])==9,'independent complete nine-case population')
        raw=read(RAW);L=raw['L'];groups=list(dict.fromkeys(tuple(a for a in range(12) if L[a][j]) for j in range(60)))
        need(len(groups)==20 and all(len(g)==6 and {a//2 for a in g}==set(range(6)) for g in groups),'twenty matched-pair transversals')
        C=[[int((r%12==s%12 and r//12!=s//12) or (r//12==s//12 and r%12^1==s%12)) for s in range(36)] for r in range(36)]
        need(C==raw['core_adjacency'],'raw core convention')
        K=[[12*int(r==s)+2-C[r][s]-sum(C[r][t]*C[t][s] for t in range(36))-int(r//12==s//12) for s in range(36)] for r in range(36)]
        need(K==raw['prescribed_Gram36'],'literal prescribed Gram')
        for group in groups:
            need(all(K[12*f+a][12*h+b]==K[12*f+2*i][12*h+2*j] for i,a in enumerate(group) for j,b in enumerate(group) for f in range(3) for h in range(3)),'every group transports local raw Gram')
        words,triples,by_signature=catalog(K);local=read(LOCAL)
        need([list(w) for w in words]==local['words'] and triples==local['survivors'] and len(triples)==31110,'complete catalogue and all saved ranks')
        need(len(by_signature[(1,)*18])==150,'complete balanced local positive')
        fixture=read(FIX)['factor60x180'];KF=[[sum(x*y for x,y in zip(a,b)) for b in fixture] for a in fixture]
        columns=[frozenset(i for i in range(60) if fixture[i][j]) for j in range(180)]
        positive_controls=0
        for selected in combinations(range(8),3):
            need(allowed([columns[i] for i in selected],KF),'genuine243 three-column positive');positive_controls+=1
        need(not allowed([columns[0],columns[0],columns[1]],KF),'duplicated positive column cap corruption')
        with gzip.open(D/'profiles.jsonl.gz','rt',encoding='utf8') as stream:saved=[json.loads(line) for line in stream]
        need(len(saved)==984,'all raw profile records')
        by_id={r['id']:r for r in saved};need(len(by_id)==984,'unique raw stable IDs')
        result=[];hist=Counter();unique_domains={};all_hashes=set();case_counts={};seen=set();example=None
        for case in population['records']:
            ci=case['case'];groupids=case['groups'];selected=[groups[g] for g in groupids];H,choices=local_integer_choices(selected)
            paths=case['ordered_choice_paths'];need(paths==sorted(paths) and len(paths)==len({tuple(p) for p in paths}),'exact prior independent path order')
            case_counts[ci]=len(paths);case_hist=Counter();casehashes=[]
            for pi,path in enumerate(paths):
                dev=decode_path(path,choices,selected,H);ph=identity(dict(groups=groupids,deviations=dev));need(ph not in all_hashes,'distinct complete deviations');all_hashes.add(ph);casehashes.append(ph)
                expected=dict(id=f'rank4_{ci:02d}_profile_{pi:04d}',rank4_case=ci,group_ids=groupids,choice_path=path,profile_sha256=ph,coordinate_fibre_deviations=dev)
                rec=by_id[expected['id']];seen.add(rec['id']);refs=[]
                for j,g in enumerate(groupids):
                    sig=tuple(1+dev[a][f][j] for a in groups[g] for f in range(3));indices=by_signature.get(sig,[]);need(indices,'literal local domain nonempty')
                    refs.append((g,sig,indices));hist[len(indices)]+=1;case_hist[len(indices)]+=1
                check_record(rec,expected,refs)
                for ref,(_,sig,indices) in zip(rec['local_domains'],refs,strict=True):
                    dp=ROOT/ref['path'];pin(dp,ref['sha256']);ds=read(dp);check_domain(ds,sig,indices)
                    if sig not in unique_domains:unique_domains[sig]=dict(path=ref['path'],sha256=ref['sha256'],count=len(indices),local_survivor_indices=indices)
                if example is None:example=(rec,expected,refs)
                result.append(dict(id=rec['id'],case=ci,profile_sha256=ph,group_ids=groupids,counts=[len(v[2]) for v in refs],witness_catalog_ranks=[v[2][0] for v in refs]))
            if paths:
                record=next(r for r in summary['cases'] if r['case']==ci)
                need(record==dict(case=ci,groups=groupids,expected=len(paths),backtracked=len(paths),unique=len(paths),empty_local_domain_profiles=0,retained_profiles=len(paths),domain_size_histogram={str(k):v for k,v in sorted(case_hist.items())}),'all complete case counts')
                need(read(D/f'case_{ci:02d}_checkpoint.json')==record,'checkpoint contents')
                need(read(D/f'case_{ci:02d}_profile_hashes.json')==dict(case=ci,profile_hashes=casehashes),'ordered exact profile identities')
        need(seen==set(by_id) and len(all_hashes)==984 and sum(hist.values())==5904,'no missing or extra marginal profiles/group domains')
        need(case_counts==dict(enumerate([96,108,0,96,96,24,0,0,564])),'independently checked case populations')
        need(len(unique_domains)==534 and summary['unique_local_count_domains']==534,'all distinct signature domains')
        actualfiles={key(p) for p in (D/'domains').glob('*.json')};need(actualfiles=={r['path'] for r in unique_domains.values()},'complete unique domain file population')
        need(all(summary[k]==984 for k in ['labelled_profiles','completed_profiles','unique_profile_hashes','retained_profiles']) and summary['profiles_with_empty_local_domain']==0 and summary['native_solver_calls']==0,'producer exact narrow stage counts')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError,TypeError):rejected.append(label)
            else:raise ValueError('corruption accepted '+label)
        rec,expected,refs=example;sig=refs[0][1];indices=refs[0][2];domain=read(ROOT/rec['local_domains'][0]['path'])
        for label,field,value in [('missing_rank','local_survivor_indices',indices[:-1]),('wrong_count','count',len(indices)+1),('reversed_rank_order','local_survivor_indices',list(reversed(indices))),('wrong_catalogue','local_catalog_sha256','0'*64),('bad_signature','count_signature',[4]+list(sig[1:]))]:
            bad=deepcopy(domain);bad[field]=value;reject(label,lambda bad=bad:check_domain(bad,sig,indices))
        for label,field,value in [('changed_profile_hash','profile_sha256','0'*64),('changed_path','choice_path',[999]+rec['choice_path'][1:]),('changed_deviations','coordinate_fibre_deviations',[]),('missing_group','local_domains',rec['local_domains'][:-1]),('orbit_pruning','normalization_used_for_filtering',True),('false_exclusion','empty_groups',[rec['group_ids'][0]])]:
            bad=deepcopy(rec);bad[field]=value;reject(label,lambda bad=bad:check_record(bad,expected,refs))
        reject('missing_profile',lambda:need(set(by_id)-{rec['id']}==seen,'entire labelled population'))
        reject('count_four_domain',lambda:need(bool(by_signature.get((4,0,-1)+(1,)*15)),'invalid local signature'))
        save(out/'controls.json',dict(genuine243_positive_triples=positive_controls,balanced_local_domain=150,duplicate_column_rejected=True,corruptions_rejected=rejected))
        save(out/'independent_domain_counts.json',dict(records=result,local_domain_occurrences=5904,domain_size_histogram=dict(sorted(hist.items())),unique_domain_signatures=534,counts_by_case=case_counts))
        save(out/'independent_rank_lists.json',dict(records=[dict(count_signature=list(sig),**v) for sig,v in sorted(unique_domains.items())]))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SIX_LOCAL_DOMAINS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat()
        claim=dict(id=CID,revision=1,statement='For every one of the984 explicitly labelled exactly-six-active integer marginal profiles in the checked nine-case fixed-Hadamard support census, each of its six nominated exceptional groups has a nonempty local domain of three distinct balanced six-coordinate column words satisfying its exact18coordinate/fibre counts, the prescribed partial Gram upper bounds, and all three within-group outside-column overlap caps. The complete raw catalogue rank lists are exactly those saved in the hash-bound filter artifacts.',kind='empirical/engineering result',basis=['COMPUTED','DERIVED'],status='VERIFIED',review_state='CLEAR',scope='All984 literal marginal profiles and5904 individual group domains only; no cross-group compatibility, full factor, D, or global fibre-orbit reduction is established.',assumptions=['The literal fixed six-prism Hadamard support and prescribed Gram.','Within-group outside-column caps are imposed; this is not a Gram-only local catalogue.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-INTEGER-MARGINAL-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise')],artifact_hashes=pins,verifier='/root/structural_attack',checking_method='Independent artifact checking with full local catalogue reconstruction and exact complete prior population binding; no producer imports.',shared_components=['Python integer arithmetic, hashlib/json/gzip and tqdm.','The prior independently enumerated complete path list is an explicit coverage input; no producer DP backtracking routine is imported.'],limitations=['Global fibre-image and diagnostic orbit fields are not approved or used.','No pair or joint feasibility is inferred from local nonemptiness.','No new SAT or native solver execution.'],created_at=now,updated_at=now)
        save(out/'claim_binding.json',claim)
        save(out/'summary.json',dict(status='INDEPENDENT_SIX_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},claim_id=CID,claim_revision=1,labelled_profiles=984,local_domain_occurrences=5904,unique_local_count_domains=534,local_catalogue_candidates=117480,local_catalogue_survivors=31110,profiles_with_empty_local_domain=0,domain_size_histogram=dict(sorted(hist.items())),corruptions_rejected=len(rejected),genuine243_positive_controls=positive_controls,fibre_orbit_diagnostics_checked=False,cross_group_relations_checked=False,solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status='INDEPENDENT_SIX_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
