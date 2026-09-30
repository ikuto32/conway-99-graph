"""Bounded proof core extraction and exact shared-block domain propagation."""
import argparse, collections, gzip, hashlib, importlib.util, itertools, json, platform, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
CHECKER=ROOT/'build/rook-drat-checker/drat-trim.exe'
HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
PRIOR=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
CASES=[('first','20260930_eight_count_profile_lift','20260930_eight_count_profile_native_pilot','eight_count_profile_unsat','c846d32c668910bb1254b840ca3bff6b97ec8bb5878e3092e48575e5bbe3e1ed'),('third','20260930_eight_count_profile_lift_third','20260930_eight_count_profile_lift_third_native_pilot','third_eight_count_profile_unsat','b7a7c19c59e456ce574fb6b8aa89cff55b5943e0a29ddcd7e49ba53c6c61a49c')]
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def cnf(p):
    rows=[];head=None;pending=[]
    for line in p.read_text().splitlines():
        if not line or line.startswith('c'):continue
        if line.startswith('p '):head=tuple(map(int,line.split()[2:]));continue
        for v in map(int,line.split()):
            if v:pending.append(v)
            else:rows.append(tuple(sorted(pending)));pending=[]
    need(not pending and head and head[1]==len(rows),'complete DIMACS');return head,rows
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def bounded_add(a,b,t):
    s=add(a,b);return s if all(x<=y for x,y in zip(s,t)) else None
def supports(populations,target):
    zero=(0,)*len(target);prefix=[{zero}]
    for vals in populations:
        prefix.append({s for x in prefix[-1] for y in vals if (s:=bounded_add(x,y,target)) is not None})
    suffix=[set() for _ in range(len(populations)+1)];suffix[-1]={zero}
    for i in range(len(populations)-1,-1,-1):
        suffix[i]={s for x in suffix[i+1] for y in populations[i] if (s:=bounded_add(x,y,target)) is not None}
    allowed=[]
    for i,vals in enumerate(populations):
        accepted=set()
        for v in vals:
            if any(tuple(target[j]-x[j]-v[j] for j in range(len(target))) in suffix[i+1] for x in prefix[i]):accepted.add(v)
        allowed.append(accepted)
    return allowed,prefix,suffix
def controls():
    n=0
    alphabet=[(0,0),(0,1),(1,0),(1,1)]
    for mask1 in range(1,16):
        for mask2 in range(1,16):
            populations=[{v for i,v in enumerate(alphabet) if mask1>>i&1},{v for i,v in enumerate(alphabet) if mask2>>i&1},{(0,0),(1,1)}]
            for target in [(0,0),(1,1),(2,1),(3,3)]:
                actual,_,_=supports(populations,target);expected=[set() for _ in populations]
                for choice in itertools.product(*populations):
                    if tuple(map(sum,zip(*choice)))==target:
                        for i,v in enumerate(choice):expected[i].add(v)
                need(actual==expected,'complete Cartesian support control');n+=1
    valid,_,_=supports([{(0,)},{(1,)}],(1,));need(valid==[{(0,)},{(1,)}],'known positive')
    corrupt,_,_=supports([{(0,)},{(2,)}],(1,));need(corrupt!=valid and corrupt==[set(),set()],'corrupt contribution detected')
    need(valid!=[set(),{(1,)}],'corrupt stored support rejected')
    return dict(cartesian_cases=n,positive=True,impossible_target=True,corrupted_contribution_rejected=True,corrupted_support_rejected=True)
def call(args,out,name,deadline,expected=True):
    remaining=deadline-time.perf_counter()
    if remaining<=0:raise TimeoutError('declared total allocation')
    command=[str(CHECKER),*map(str,args)];start=time.perf_counter();limit=min(20,remaining)
    try:r=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=limit)
    except subprocess.TimeoutExpired as ex:
        (out/(name+'.stdout.log')).write_bytes(ex.stdout or b'');(out/(name+'.stderr.log')).write_bytes(ex.stderr or b'')
        save(out/(name+'.receipt.json'),dict(command=command,status='TIMEOUT',limit_seconds=limit));raise TimeoutError(name)
    (out/(name+'.stdout.log')).write_bytes(r.stdout);(out/(name+'.stderr.log')).write_bytes(r.stderr)
    accepted=r.returncode==0 and b's VERIFIED' in r.stdout
    result=dict(command=command,exit_code=r.returncode,accepted=accepted,expected=expected,elapsed_seconds=time.perf_counter()-start,limit_seconds=limit)
    save(out/(name+'.receipt.json'),result);need(accepted==expected,'proof extraction/replay '+name);return result
def extract(model,formula,proof,out,deadline):
    core=out/'core.cnf';lemmas=out/'core.drat'
    receipt=call([formula,proof,'-c',core,'-l',lemmas],out,'extract',deadline)
    head,raw=cnf(formula);ch,cr=cnf(core);locations=collections.defaultdict(list)
    for i,row in enumerate(raw):locations[row].append(i)
    used=collections.Counter(cr);need(all(n<=len(locations[row]) for row,n in used.items()),'core literal multiset subset')
    ids=[]
    for row,n in used.items():ids.extend(locations[row][:n])
    labels=[None]*len(raw)
    def label(rec,category,semantic):
        for j in range(rec['first_clause']-1,rec['first_clause']-1+rec['clause_count']):need(labels[j] is None,'disjoint clause ranges');labels[j]=[category,semantic]
    for row in model['exact_one_prefix_rows']:label(row,'onehot',row['group'])
    for cell in model['pair_cell_counts']:
        semantic=cell['coordinates']+cell['fibres']
        label(cell,'gram_count',semantic)
        for group in cell['group_contributions']:
            for channel in group['channels']:label(channel,'threshold',semantic+[group['group'],channel['threshold']])
    need(all(x is not None for x in labels),'complete clause map')
    mapping=[dict(original_clause=i+1,semantic=labels[i]) for i in sorted(ids)]
    save(out/'core_original_mapping.json',mapping)
    replay=call([core,lemmas],out,'replay_core',deadline)
    families=collections.Counter(x[0] for i in ids for x in [labels[i]])
    cells=sorted({tuple(labels[i][1][:4]) for i in ids if labels[i][0]!='onehot'})
    return dict(original_clauses=len(raw),core_clauses=len(cr),core_bytes=core.stat().st_size,trimmed_proof_bytes=lemmas.stat().st_size,families=dict(families),gram_cells=cells,coordinate_pairs=sorted({tuple(x[:2]) for x in cells}),extraction=receipt,replay=replay,scope='Verified clausal subset; neither minimality nor a human-readable mathematical core is implied.')
def derive_blocks(model):
    domains=model['domains'];blocks=[]
    for a in range(12):
        for b in range(a+1,12):
            if a//2==b//2:continue
            groups=[g for g,d in enumerate(domains) if a in d['support'] and b in d['support']];need(len(groups)==5,'five raw supporting groups')
            projections=[]
            for g in groups:
                d=domains[g];ia=d['support'].index(a);ib=d['support'].index(b);vectors=[]
                for choice in d['choices']:
                    vector=[0]*9
                    for word in choice['colour_words']:vector[3*word[ia]+word[ib]]+=1
                    vectors.append(tuple(vector))
                projections.append(vectors)
            target=tuple(1 if f==h else 2 for f in range(3) for h in range(3))
            for f in range(3):
                for h in range(3):
                    cell=next(x for x in model['pair_cell_counts'] if x['coordinates']==[a,b] and x['fibres']==[f,h])
                    need(cell['bound']==target[3*f+h] and [x['group'] for x in cell['group_contributions']]==groups,'raw target and groups')
                    for i,row in enumerate(cell['group_contributions']):need(row['coefficients']==[v[3*f+h] for v in projections[i]],'literal word coefficients match audited metadata')
            blocks.append(dict(coordinates=[a,b],groups=groups,projections=projections,target=target))
    need(len(blocks)==60,'all coordinate blocks');return blocks
def propagate(model,out,deadline):
    domains=[set(range(len(d['choices']))) for d in model['domains']];initial=[sorted(d) for d in domains];blocks=derive_blocks(model);sweep=0;checks=0;removed_total=0;status='RUNNING'
    with (out/'block_checks.jsonl.gz').open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=6) as log:
            while status=='RUNNING':
                sweep+=1;changed=False
                for bi,b in enumerate(blocks):
                    if time.perf_counter()>=deadline:status='PARTIAL_RESOURCE_BOUND';break
                    current=[sorted(domains[g]) for g in b['groups']];pop=[{b['projections'][i][k] for k in ks} for i,ks in enumerate(current)]
                    allowed,pre,suf=supports(pop,b['target']);removed=[]
                    for i,g in enumerate(b['groups']):
                        bad=[k for k in current[i] if b['projections'][i][k] not in allowed[i]]
                        if bad:removed.append(dict(group=g,choice_indices=bad));domains[g].difference_update(bad)
                    record=dict(index=checks,sweep=sweep,block=bi,coordinates=b['coordinates'],groups=b['groups'],input_domains=current,projected_populations=[sorted(s) for s in pop],prefix=[sorted(s) for s in pre],suffix=[sorted(s) for s in suf],supported_vectors=[sorted(s) for s in allowed],removed=removed)
                    log.write((json.dumps(record,separators=(',',':'))+'\n').encode());checks+=1
                    n=sum(len(r['choice_indices']) for r in removed);removed_total+=n;changed|=bool(n)
                    if any(not domains[g] for g in b['groups']):status='EMPTY_NECESSARY_DOMAIN';break
                if status=='RUNNING' and not changed:status='FIXED_POINT_NO_EXCLUSION'
    result=dict(status=status,initial_domains=initial,final_domains=[sorted(d) for d in domains],sweeps=sweep,block_checks=checks,removed_options=removed_total,scope='Only exact 3x3 block constraints with shared local options; fixed point is not joint feasibility.')
    save(out/'domain_propagation.json',result);return {k:v for k,v in result.items() if k not in ['initial_domains','final_domains']}|dict(final_domain_sizes=list(map(len,domains)))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();deadline=started+120;pins={};cases=[]
    def pin(p,h=None):
        actual=sha(p);need(h is None or actual==h,'hash '+key(p));pins[key(p)]=actual
    try:
        pin(PRIOR,'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5');pin(HELPER,read(PRIOR)['inputs_sha256'][key(HELPER)])
        sp=importlib.util.spec_from_file_location('reviewed_auth',HELPER);h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
        pin(CHECKER,'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac');auth=h.authenticate(pin)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        save(out/'controls.json',controls())
        tiny=out/'tiny.cnf';tiny.write_text('p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n');proof=out/'tiny.drat';proof.write_text('-2 0\n1 0\n0\n')
        call([tiny,proof,'-c',out/'tiny_core.cnf','-l',out/'tiny_core.drat'],out,'tiny_extract',deadline)
        need(collections.Counter(cnf(out/'tiny_core.cnf')[1])==collections.Counter(cnf(tiny)[1]),'complete tiny core')
        call([out/'tiny_core.cnf',out/'tiny_core.drat'],out,'tiny_core_replay',deadline)
        sat=out/'tiny_sat.cnf';sat.write_text('p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n');call([sat,out/'tiny_core.drat'],out,'tiny_changed_input',deadline,False)
        for name,directory,run,gate,gh in CASES:
            d=B/directory;r=B/run;g=B/'20260930_independent_review'/gate/'summary.json';pin(g,gh);review=read(g)
            for p in [d/'instance.cnf',d/'model.json',d/'scope.json',d/'selected_profile.json']:
                pin(p,review['inputs_sha256'][key(p)])
            trace=r/'main/proof.drat';pin(trace,review['proof']['sha256']);model=read(d/'model.json');co=out/name;co.mkdir();result=dict(name=name)
            try:result['core']=extract(model,d/'instance.cnf',trace,co,deadline);result['propagation']=propagate(model,co,deadline)
            except TimeoutError as ex:result['status']='PARTIAL_RESOURCE_BOUND';result['boundary']=str(ex)
            save(co/'summary.json',result);cases.append(result)
            print(json.dumps(dict(case=name,result=result.get('propagation',result.get('status')))),flush=True)
            if time.perf_counter()>=deadline:break
        result=dict(status='CANDIDATE_PROOF_OBSTRUCTION_SCOUT',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),command=[sys.executable,*sys.argv],configured_wall_seconds=120,elapsed_seconds=time.perf_counter()-started,cases=cases,unattempted=[x[0] for x in CASES[len(cases):]],checker_authentication=auth,new_sat_calls=0,claim_status='CANDIDATE; separate review needed for new mathematical use')
        save(out/'summary.json',result);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=pins));raise
if __name__=='__main__':main()
