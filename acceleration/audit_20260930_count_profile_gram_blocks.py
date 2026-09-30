"""Independent exact Cartesian-product audit of one count profile's Gram blocks."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';DATA=B+'count_profile_gram_blocks/';PROFILE=B+'independent_review/count_master_sat_outcome/independent_count_profile.json';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
PINS={DATA+'summary.json':'2c14151354cf699c7ef421b51d7fa745298a8fecfe792481daec0ae0ee679216',PROFILE:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776'}
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def need(ok,msg):
    if not ok:raise ValueError(msg)
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def matrix(words,triple,ia,ib):
    # Explicit two3x3 incidence matrices; no producer's colour-index accumulation.
    left=[[int(words[w][ia]==f)for w in triple]for f in range(3)]
    right=[[int(words[w][ib]==f)for w in triple]for f in range(3)]
    return tuple(sum(x*y for x,y in zip(a,b))for a in left for b in right)
def verify(rec,expected,target):
    need(rec['target']==list(target)and rec['group_records']==expected,'all actual local support matrices and realizing triples')
    supports=[r['matrices']for r in expected];layers=rec['DP_layers'];need(len(layers)==6,'six complete layers');products=0
    for k in range(6):
        reachable=set()
        for choice in product(*supports[:k]):
            products+=1;summed=tuple(sum(v[i]for v in choice)for i in range(9))
            if all(v<=t for v,t in zip(summed,target)):reachable.add(summed)
        need(layers[k]['states']==[list(v)for v in sorted(reachable)],'complete independent Cartesian prefix sums')
        layer=layers[k]
        if k==0:need(layer==dict(states=[[0]*9],predecessors=[None],option_indices=[None],attempted_transitions=0,oversized_transitions=0),'zero layer');continue
        previous=layers[k-1]['states'];support=supports[k-1]
        need(layer['attempted_transitions']==len(previous)*len(support),'complete transition count')
        oversized=sum(any(a+b>t for a,b,t in zip(state,m,target))for state in previous for m in support)
        need(layer['oversized_transitions']==oversized,'only nonnegative target overshoot pruning')
        need(len(layer['predecessors'])==len(layer['option_indices'])==len(layer['states']),'all predecessor bindings')
        for state,pi,mi in zip(layer['states'],layer['predecessors'],layer['option_indices']):
            need(0<=pi<len(previous)and 0<=mi<len(support),'valid predecessor indices');need(state==[a+b for a,b in zip(previous[pi],support[mi])],'concrete predecessor sum')
    feasible=list(target)in layers[-1]['states'];need(rec['feasible']==feasible,'feasibility')
    if feasible:
        witness=rec['witness'];need(len(witness)==5,'five actual local witnesses')
        for w,group in zip(witness,expected):
            k=w['matrix_index'];need(w['group']==group['group']and w['matrix']==group['matrices'][k]and w['local_survivor_index']in group['realizing_local_indices'][k],'witness realization')
        need(tuple(sum(w['matrix'][i]for w in witness)for i in range(9))==target,'actual target sum')
    return products
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False,parents=True);start=time.monotonic();pins={}
    try:
        for p,h in PINS.items():need(sha(p)==h,'pin '+p);pins[p]=h
        summary=read(DATA+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in summary[field].items():need(sha(p)==h,'actual source/artifact '+p);pins[p]=h
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_COUNT_PROFILE_GRAM_BLOCKS.md']:pins[p]=sha(p)
        profile=read(PROFILE);raw=read(RAW);local=read(LOCAL);words=local['words'];triples=local['survivors'];groups=list(dict.fromkeys(tuple(i for i in range(12)if raw['L'][i][d])for d in range(60)))
        counts=profile['coordinate_group_fibre_counts'];classmap=defaultdict(list)
        for index,t in enumerate(triples):classmap[tuple(sum(int(words[w][i]==f)for w in t)for i in range(6)for f in range(3))].append(index)
        ranks=[classmap[tuple(v for i in group for v in counts[i][g])]for g,group in enumerate(groups)]
        need(ranks==profile['local_survivor_indices_by_group'],'all complete original local classes');need(read(DATA+'initial_domain_ranks.json')==dict(groups=[list(x)for x in groups],local_survivor_indices_by_group=ranks,profile_sha256=profile['profile_sha256']),'all saved ranks')
        checked=[];controls=[];cartesian=0
        pairs=[(a,b)for a,b in combinations(range(12),2)if a//2!=b//2];need(len(pairs)==60 and len(summary['pair_records'])==60,'entire population')
        for i,(a,b)in enumerate(pairs):
            row=summary['pair_records'][i];need(row['pair_index']==i and row['coordinates']==[a,b],'pair identity')
            with gzip.open(ROOT/row['path'],'rt',encoding='utf8')as f:rec=json.load(f)
            need(rec['pair_index']==i and rec['coordinates']==[a,b],'raw pair identity');expected=[]
            for g,group in enumerate(groups):
                if a not in group or b not in group:continue
                ia=group.index(a);ib=group.index(b);support=defaultdict(list)
                for ti in ranks[g]:support[matrix(words,triples[ti],ia,ib)].append(ti)
                matrices=sorted(support);expected.append(dict(group=g,local_positions=[ia,ib],full_local_indices=ranks[g],matrices=[list(m)for m in matrices],realizing_local_indices=[support[m]for m in matrices]))
            target=tuple(raw['prescribed_Gram36'][12*f+a][12*h+b]for f in range(3)for h in range(3));need(len(expected)==5,'all five groups');cartesian+=verify(rec,expected,target);need(rec['feasible'],'literal positive only')
            need(row['support_sizes']==[len(g['matrices'])for g in expected]and row['layer_sizes']==[len(x['states'])for x in rec['DP_layers']],'summary sizes')
            checked.append(dict(pair_index=i,coordinates=[a,b],feasible=True,sha256=row['sha256']))
            if i==0:
                for label in ['matrix','missing_state','target','witness']:
                    bad=deepcopy(rec)
                    if label=='matrix':bad['group_records'][0]['matrices'][0][0]+=1
                    elif label=='missing_state':bad['DP_layers'][-1]['states'].pop()
                    elif label=='target':bad['target'][0]+=1
                    else:bad['witness'][0]['local_survivor_index']=-1
                    try:verify(bad,expected,target)
                    except (ValueError,IndexError):controls.append(label)
                    else:raise ValueError('accepted corruption '+label)
            need(time.monotonic()-start<120,'120second verification allocation')
        save(out/'checked_pairs.json',checked)
        result=dict(status='INDEPENDENT_COUNT_PROFILE_GRAM_BLOCKS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={str((out/'checked_pairs.json').relative_to(ROOT)).replace('\\','/'):sha((out/'checked_pairs.json').relative_to(ROOT))},checked_pairs=60,feasible_pairs=60,complete_Cartesian_prefix_products=cartesian,rejected_corruptions=controls,verifier='/root',producer='/root/state_literature_audit',checking_method='Explicit3x3 incidence products for every original local option; exhaustive Cartesian products for every prefix, rather than producer DP. All supports, states, valid predecessors and literal target witnesses checked.',shared_components=['Raw independently established complete local catalogue and count profile as explicit premises.','Python standard-library exact arithmetic; no producer imports.'],scope='One exact count profile passes60 separate necessary3x3block constraints. No consistent global factor or target graph follows.',native_calls=0,elapsed_seconds=time.monotonic()-start,target_resolution=False)
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['inputs_sha256','outputs_sha256']}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
