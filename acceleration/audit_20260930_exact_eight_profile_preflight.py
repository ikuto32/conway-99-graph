"""Independent explicit-set/work-queue count-table universe audit."""
from pathlib import Path
from itertools import product, permutations
from collections import Counter, deque
from datetime import datetime, timezone
import argparse, copy, hashlib, json, math, platform, subprocess, sys, time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'exact_eight_profile_preflight/';COORD=B+'hadamard_coordinate_marginal_domains/'
PINS={D+'summary.json':'a479ab298a74884df96dc946ed15c94a7245b1b3312779aacea6f56de43ff2dc',D+'subset_inventory.jsonl':'ede227a007f13679750fe1eb8c2ffa5c201c996c632beef33f36abfa89b88f5b',I+'coordinate_marginal_domains/summary.json':'9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39',I+'hadamard_eight_exception_census/summary.json':'95176ae42241c3745fe1e017fbeca3798b04bc49f1113455605c3ed928e204f6',I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def same(a,b):need(a==b,'complete exact comparison')

def propagate(domains,variables,relations,inverted,value):
    """Generic projection-table semijoins; no integer bitsets."""
    ds=[set(d)for d in domains];rs=[set(r)for r in relations]
    incidence=[[]for _ in ds]
    for t,vs in enumerate(variables):
        for a in vs:incidence[a].append(t)
    todo=deque(range(len(rs)));pending=set(todo)
    while todo:
        t=todo.popleft();pending.remove(t);vs=variables[t];new=set(rs[t])
        for p,a in enumerate(vs):
            choices={value(a,i,t)for i in ds[a]};allowed=set()
            for x in choices:allowed.update(inverted[p].get(x,()))
            new.intersection_update(allowed)
        rs[t]=new
        if not new:return None,rs
        for p,a in enumerate(vs):
            good={x for x,ids in inverted[p].items()if not new.isdisjoint(ids)}
            reduced={i for i in ds[a]if value(a,i,t)in good}
            if not reduced:return None,rs
            if reduced!=ds[a]:
                ds[a]=reduced
                for neighbor in incidence[a]:
                    if neighbor not in pending:todo.append(neighbor);pending.add(neighbor)
    return ds,rs

def controls():
    table=list(product(range(2),repeat=3));inverted=[{v:{j for j,row in enumerate(table)if row[p]==v}for v in range(2)}for p in range(3)];n=0
    for mask in range(256):
        relation={j for j in range(8)if mask>>j&1}
        for domains in product([{0},{1},{0,1}],repeat=3):
            truth=[row for row in product(*domains)if row in [table[j]for j in relation]]
            got,_=propagate(domains,[(0,1,2)],[relation],inverted,lambda a,i,t:i)
            want=None if not truth else [{row[p]for row in truth}for p in range(3)]
            same(got,want);n+=1
    need(n==6912,'complete ternary controls');return n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        digest=sha(p);need(h is None or digest==h,'identity '+str(p));need(p not in pins or pins[p]==digest,'consistent pin');pins[str(p)]=digest
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in producer[field].items():pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_EXACT_EIGHT_PROFILE_PREFLIGHT.md','uv.lock','pyproject.toml']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0,limit_seconds=120))
        control_count=controls();raw=read(B+'hadamard20_support/six_prism.json');groups=[]
        for x in raw['support_columns']:
            if tuple(x)not in groups:groups.append(tuple(x))
        need(len(groups)==20 and all(len(s)==6 for s in groups),'raw supports')
        local=read(B+'hadamard_triplicate_counts/local_triples.json');words=local['words'];signatures=set()
        for triple in local['survivors']:
            signatures.add(tuple(tuple(sum(int(words[w][p]==f)for w in triple)for f in range(3))for p in range(6)))
        signatures=sorted(signatures);need(len(signatures)==6061 and len(local['survivors'])==31110,'complete raw signatures')
        balanced=signatures.index(((1,1,1),)*6);all_ids=set(range(6061));active_ids=all_ids-{balanced};inverted=[{}for _ in range(6)]
        for j,row in enumerate(signatures):
            for p,value in enumerate(row):inverted[p].setdefault(value,set()).add(j)
        coord=[];activity=[]
        for a in range(12):
            rows=read(COORD+f'coordinate_{a:02d}.json')['ordered_three_fibre_choices'];values=[];masks=[]
            for i,row in enumerate(rows):
                need(row['index']==i,'coordinate index');counts=tuple(tuple(v)for v in row['full20_count_signature']);need(len(counts)==20,'coordinate shape')
                need(all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)and sum(v)==3*int(a in groups[g])for g,v in enumerate(counts)),'literal margins')
                mask={g for g,v in enumerate(counts)if a in groups[g]and v!=(1,1,1)};need(row['activity_mask']==sum(1<<g for g in mask),'activity reconstruction')
                for f in range(3):
                    delta=[counts[g][f]-int(a in groups[g])for g in range(20)]
                    need(sum(delta)==0 and all(sum(delta[g]for g in range(20)if b in groups[g])==0 for b in range(12)),'exact coordinate constraints')
                values.append(counts);masks.append(mask)
            need(len(set(values))==len(values),'unique coordinate choices');coord.append(values);activity.append(masks)
        need(sum(map(len,coord))==2226,'complete coordinate count')
        for name in ['count_master_sat_outcome','count_master_eight_orbit_cut_sat_outcome','count_master_partial_cut_sat_outcome']:
            w=read(I+name+'/independent_count_profile.json')['coordinate_group_fibre_counts']
            need(all(tuple(tuple(x)for x in w[a])in coord[a]for a in range(12))and all(tuple(tuple(w[a][g])for a in s)in signatures for g,s in enumerate(groups)),'known count positive')
        need(all(tuple((1,1,1)if a in s else(0,0,0)for s in groups)in coord[a]for a in range(12)),'balanced positive')
        census=read(B+'hadamard_eight_exception_census/remaining_candidates.json')['records'];records=[json.loads(line)for line in (ROOT/D/'subset_inventory.jsonl').read_text().splitlines()]
        need(len(census)==len(records)==4184 and len({tuple(r['groups'])for r in census})==4184,'complete frozen universe')
        totals=Counter();ranks=Counter();before_sum=after_sum=max_after=0;survivors={};approved=[]
        for k,(prior,saved)in enumerate(tqdm(zip(census,records,strict=True),total=4184,desc='Independent subset semijoins')):
            E=set(prior['groups']);need(len(E)==8,'eight distinct groups');ds=[{i for i,m in enumerate(activity[a])if m<=E}for a in range(12)]
            before=list(map(len,ds));before_sum+=math.prod(before);union=set().union(*(activity[a][i]for a in range(12)for i in ds[a]))
            same(saved['groups'],prior['groups']);same(saved['retained_index'],k);same(saved['original_index'],prior['index']);same(saved['rank'],prior['certificate']['rank']);same(saved['before_sizes'],before);same(saved['before_Cartesian_product'],math.prod(before))
            if union!=E:status='ACTIVITY_CANNOT_COVER';reduced=None;rs=None
            else:
                relations=[active_ids if g in E else {balanced}for g in range(20)]
                reduced,rs=propagate(ds,groups,relations,inverted,lambda a,i,g:coord[a][i][g]);status='GAC_EMPTY'if reduced is None else'GAC_NONEMPTY'
            same(saved['status'],status);totals[status]+=1
            if reduced is None:need(saved['coordinate_choice_indices']is None and saved['after_sizes']is None and saved['after_Cartesian_product']==0,'empty record')
            else:
                indices=[sorted(x)for x in reduced];sizes=list(map(len,reduced));same(saved['coordinate_choice_indices'],indices);same(saved['after_sizes'],sizes);same(saved['group_signature_populations'],list(map(len,rs)))
                size=math.prod(sizes);same(saved['after_Cartesian_product'],size);after_sum+=size;max_after=max(max_after,size);ranks[saved['rank']]+=1;survivors[tuple(sorted(E))]=indices
                approved.append(dict(groups=sorted(E),coordinate_choice_indices=indices,group_signature_ids=[sorted(r)for r in rs],retained_index=k))
            need(time.monotonic()-start<110,'preflight review budget')
        same(dict(totals),producer['status_counts']);same(before_sum,producer['sum_restricted_Cartesian_products']);same(after_sum,producer['sum_post_AC_Cartesian_products']);same(max_after,producer['max_post_AC_Cartesian_product']);same({str(k):v for k,v in ranks.items()},producer['retained_rank_histogram'])
        need(totals==Counter(ACTIVITY_CANNOT_COVER=3847,GAC_EMPTY=270,GAC_NONEMPTY=67),'full counts');sampled=[]
        selected=read(D+'join_selection.json')['groups'];need(len(selected)==3,'three saved pilot subsets')
        for j,Elist in enumerate(selected):
            E=tuple(Elist);doms=survivors[E];brute=[]
            for assigned in product(*doms):
                if any(tuple(coord[a][assigned[a]][g]for a in groups[g])not in signatures or tuple(coord[a][assigned[a]][g]for a in groups[g])==signatures[balanced]for g in E):continue
                flat=tuple(x for a in range(12)for g in E for x in coord[a][assigned[a]][g]);images={tuple(flat[k+p[f]]for k in range(0,len(flat),3)for f in range(3))for p in permutations(range(3))}
                brute.append(dict(coordinate_choice_indices=list(assigned),profile_counts_sha256=hashlib.sha256(bytes(flat)).hexdigest(),canonical_fibre_counts_sha256=hashlib.sha256(bytes(min(images))).hexdigest(),fibre_orbit_size=len(images)))
            saved=[json.loads(line)for line in (ROOT/D/f'join_{j:02d}_leaves.jsonl').read_text().splitlines()];key=lambda r:tuple(r['coordinate_choice_indices']);same(sorted(brute,key=key),sorted(saved,key=key))
            stats=read(D+f'join_{j:02d}_summary.json');need(stats['complete']and not stats['counts_are_lower_bounds'],'pilot completeness');same(stats['labelled_profiles_found'],len(brute));same(stats['distinct_fibre_orbit_keys_found'],len({r['canonical_fibre_counts_sha256']for r in brute}));sampled.append(dict(groups=list(E),complete_Cartesian_assignments=math.prod(map(len,doms)),labelled_profiles=len(brute)))
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,TypeError,KeyError,IndexError):rejected.append(name)
            else:raise ValueError('corrupt control accepted '+name)
        reject('missing_subset',lambda:same(len(records[:-1]),4184));wrong=dict(totals);wrong['GAC_NONEMPTY']+=1;reject('wrong_survivor_count',lambda:same(wrong,dict(totals)))
        wrong=copy.deepcopy(approved[0]['coordinate_choice_indices']);wrong[0]=wrong[0][:-1];reject('deleted_surviving_option',lambda:same(wrong,approved[0]['coordinate_choice_indices']))
        reject('wrong_local_signature',lambda:need(((0,0,0),)*6 in signatures,'not a local triple signature'))
        wrong=copy.deepcopy(brute);wrong[0]['fibre_orbit_size']=1;reject('invented_orbit_size',lambda:same(wrong,brute))
        save(out/'approved_surviving_subsets.json',dict(records=approved,complete=True,scope='All necessary count profiles over the prior4184 kernel-retained subsets survive this exact reduction.'))
        save(out/'controls.json',dict(ternary_Cartesian_controls=control_count,rejected=rejected,known_count_positives=3,balanced_positive=True,pilot_Cartesian_checks=sampled))
        need(time.monotonic()-start<120,'audit limit');stamp=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-FIXED-HADAMARD-EIGHT-COUNT-TABLE-SUBSET-REDUCTION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Among the frozen4184 kernel-retained eight-subsets,3847 cannot cover all eight exceptional groups using the complete coordinate marginal domains, and270 additional subsets have an empty exact local count-table propagation fixed point. Every count profile satisfying those domains and local triple membership lies in one of the remaining67 subsets with the exact saved coordinate domains. The sum of their Cartesian sizes is7122626. Complete separate Cartesian checks recover24,24,6 profiles in the three declared pilot subsets.',scope='Exactly eight unbalanced groups on the literal six-prism Hadamard support, under complete prior kernel-census, coordinate-marginal and within-triplicate-cap catalogue premises. This reduces a necessary count relaxation, not all target graphs.',assumptions=['Earlier independently checked exhaustive eight-subset kernel census.','Earlier independently checked complete coordinate marginal domains and local triple catalogue.'],dependencies=[dict(id='C-FIXED-HADAMARD-EIGHT-EXCEPTION-KERNEL-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-COMPLETE-COORDINATE-MARGINAL-DOMAINS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],verifier='/root',producer='/root/eight_domain_audit',method='Independent explicit-set asynchronous semijoins for all4184 subsets, raw signature reconstruction, three exhaustive Cartesian pilot joins and adversarial controls.',shared_components=['Prior independent census/domain coverage reports and raw artifacts are premises. No producer imports.','Python exact sets and integers; tqdm progress only.'],inputs_sha256=pins,limitations=['Nonempty propagated domains do not establish a count solution. Only three pilot joins were completed here.','No full Gram, cross-group caps, residualD or unrestricted target conclusion.','No percentages of target-wide coverage are justified.'],created_at=stamp,updated_at=stamp);save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_EXACT_EIGHT_PROFILE_PREFLIGHT_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT))for p in out.iterdir()if p.is_file()},checked_subsets=4184,status_counts=dict(totals),surviving_subsets=67,sum_post_AC_Cartesian_products=after_sum,max_post_AC_Cartesian_product=max_after,pilot_joins=sampled,controls_rejected=len(rejected),solver_calls=0,shared_components=binding['shared_components'],elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
