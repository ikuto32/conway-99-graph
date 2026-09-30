"""Candidate complete finite3x3 block-support DP on one count profile; no solver."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';PROFILE=B+'independent_review/count_master_sat_outcome/independent_count_profile.json';GATE=B+'independent_review/count_master_sat_outcome/summary.json';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
PINS={PROFILE:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',GATE:'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B+'independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def gzsave(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as g:g.write(json.dumps(x,separators=(',',':')).encode()+b'\n')
def dp(supports,target):
    zero=(0,)*len(target);previous=[zero];layers=[dict(states=[list(zero)],predecessors=[None],option_indices=[None],attempted_transitions=0,oversized_transitions=0)];paths={zero:()}
    for support in supports:
        reached={};attempts=0;oversized=0;newpaths={}
        for si,state in enumerate(previous):
            for mi,m in enumerate(support):
                attempts+=1;v=tuple(a+b for a,b in zip(state,m))
                if any(a>b for a,b in zip(v,target)):oversized+=1;continue
                if v not in reached:reached[v]=(si,mi);newpaths[v]=paths[state]+(mi,)
        now=sorted(reached);layers.append(dict(states=[list(s)for s in now],predecessors=[reached[s][0]for s in now],option_indices=[reached[s][1]for s in now],attempted_transitions=attempts,oversized_transitions=oversized));previous=now;paths=newpaths
    return layers,paths.get(tuple(target))
def controls():
    cases=0
    universes=[[(0,0),(1,0)],[(0,1),(1,1)],[(0,0),(0,1)]]
    for masks in product(range(1,4),repeat=3):
        supports=[[v for i,v in enumerate(u)if mask>>i&1]for u,mask in zip(universes,masks)]
        literal={tuple(sum(v[i]for v in choice)for i in range(2))for choice in product(*supports)}
        for target in product(range(4),repeat=2):
            layers,w=dp(supports,target);need((w is not None)==(target in literal),'DP versus exhaustive product');cases+=1
    identity=(1,0,0,0,1,0,0,0,1);cycle=(0,1,0,0,0,1,1,0,0);reverse=(0,0,1,1,0,0,0,1,0);target=(1,2,2,2,1,2,2,2,1);supports=[[identity],[cycle],[cycle],[reverse],[reverse]];layers,w=dp(supports,target);need(w==(0,0,0,0,0),'actual balanced block shape')
    need(dp(supports,(0,*target[1:]))[1]is None,'corrupted RHS')
    damaged=[*supports[:4],[]];need(dp(damaged,target)[1]is None,'missing needed member')
    return dict(exhaustive_product_cases=cases,balanced_five_permutation_positive=True,corruptions_rejected=['wrong_RHS','missing_required_support_member'],full_research_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={};done=[]
    try:
        for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p);pins[p]=h
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=120,planning_memory_bytes=768*1024**2,native_calls=0),selection='All60unordered nonmatched coordinate pairs for the one authentic count witness.'))
        save(out/'controls.json',controls());p=read(PROFILE);raw=read(RAW);local=read(LOCAL);need(p['exception_count']==8 and p['profile_sha256']=='d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9','exact literal count witness');groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));words=local['words'];triples=local['survivors'];counts=p['coordinate_group_fibre_counts'];catalog=defaultdict(list)
        for i,t in enumerate(triples):catalog[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
        ranks=[]
        for g,s in enumerate(groups):
            ids=catalog[tuple(x for a in s for x in counts[a][g])];need(ids==p['local_survivor_indices_by_group'][g]and ids,'complete raw initial rank list');ranks.append(ids)
        save(out/'initial_domain_ranks.json',dict(groups=groups,local_survivor_indices_by_group=ranks,profile_sha256=p['profile_sha256']));(out/'progress.jsonl').touch(exist_ok=False)
        pairs=[(a,b)for a,b in combinations(range(12),2)if a//2!=b//2];need(len(pairs)==60,'whole pair population')
        for pi,(a,b)in enumerate(pairs):
            if time.monotonic()-start>=120:raise TimeoutError('120-second allocation before next complete pair')
            group_records=[];supports=[]
            for g,s in enumerate(groups):
                if a not in s or b not in s:continue
                ia=s.index(a);ib=s.index(b);by_matrix=defaultdict(list)
                for ti in ranks[g]:
                    m=[0]*9
                    for w in triples[ti]:m[3*words[w][ia]+words[w][ib]]+=1
                    need(sum(m)==3,'three raw columns');by_matrix[tuple(m)].append(ti)
                matrices=sorted(by_matrix);supports.append(matrices);group_records.append(dict(group=g,local_positions=[ia,ib],full_local_indices=ranks[g],matrices=[list(m)for m in matrices],realizing_local_indices=[by_matrix[m]for m in matrices]))
            target=tuple(raw['prescribed_Gram36'][12*f+a][12*h+b]for f in range(3)for h in range(3));need(len(supports)==5 and target==(1,2,2,2,1,2,2,2,1),'five groups/literaltarget');layers,w=dp(supports,target)
            witness=None if w is None else[dict(group=r['group'],matrix_index=k,matrix=r['matrices'][k],local_survivor_index=r['realizing_local_indices'][k][0])for r,k in zip(group_records,w)]
            if witness:need(tuple(sum(r['matrix'][i]for r in witness)for i in range(9))==target,'literal target witness sum')
            rec=dict(pair_index=pi,coordinates=[a,b],target=list(target),group_records=group_records,DP_layers=layers,feasible=w is not None,witness=witness,witness_null_reason=None if w is not None else'No target after complete bounded entrywise sum-set recurrence.',scope='One necessary3x3Gramblock only; no simultaneous choices across pairs.')
            path=out/f'pair_{pi:02d}.json.gz';gzsave(path,rec);report=dict(pair_index=pi,coordinates=[a,b],path=key(path),sha256=sha(path),feasible=rec['feasible'],support_sizes=[len(s)for s in supports],layer_sizes=[len(r['states'])for r in layers],attempted_transitions=sum(r['attempted_transitions']for r in layers),oversized_transitions=sum(r['oversized_transitions']for r in layers));done.append(report)
            with(out/'progress.jsonl').open('a',encoding='utf-8',newline='\n')as f:f.write(json.dumps(report)+'\n')
        summary=dict(status='CANDIDATE_LITERAL_COUNT_PROFILE_GRAM_BLOCK_SCREEN_COMPLETE',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},profile_sha256=p['profile_sha256'],pair_records=done,pairs_completed=len(done),infeasible_pairs=sum(not r['feasible']for r in done),feasible_pairs=sum(r['feasible']for r in done),attempted_transitions=sum(r['attempted_transitions']for r in done),peak_layer_states=max(max(r['layer_sizes'])for r in done),elapsed_seconds=time.monotonic()-start,native_calls=0,solver_calls=0,independent_approval=False,full_factor=False,target_graph=False,artifact_availability='LOCAL_ONLY',scope='Necessary exact3x3blocks for this one count profile; no all-pairs simultaneous local choice or full-factor conclusion.');save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256','pair_records']}));print('summary_sha256',sha(out/'summary.json'))
    except TimeoutError as e:save(out/'summary.json',dict(status='PARTIAL_UNKNOWN',reason=str(e),inputs_sha256=pins,pair_records=done,pairs_completed=len(done),pairs_unattempted=60-len(done),elapsed_seconds=time.monotonic()-start,solver_calls=0,independent_approval=False))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,completed_pair_records=done));raise
if __name__=='__main__':main()
