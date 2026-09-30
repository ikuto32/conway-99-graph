"""Small orbit/count inventory only; no enumeration of integer graph lifts."""
import argparse, datetime, hashlib, itertools, json, math, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W='external_conway99_research/attempts/wave205-nonedge-fourth-trace-proof-a/'
PINS={W+'controls.json':'e52c068f5fdba18110debdd1455195ec22145f07993437b5438e8f77ae03fdcf',
W+'exact-results.json':'48a09ca524d62a1d2b2ee352a4d6689dbf3fa3127c70b03e7358edad452e05cc',
'external_conway99_research/verification/wave205-fourth-trace-globalization-verifier/post_source_result.json':'0e9a1091d3863be3f9b69d1b4903c4d14db2b59f27820cde81906f1fe06459c5'}
def need(q,m):
    if not q:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
def normalized(C):
    if [r[:2] for r in C[:2]]!=[[1,2],[2,1]]:return False
    if C[0][2:]!=[2,1,1,1,1] or C[1][2:]!=[1,2,1,1,1]:return False
    if [r[:2] for r in C[2:]]!=[[2,1],[1,2],[1,1],[1,1],[1,1]]:return False
    return all(sum(r)==6 for r in C[2:]) and all(sum(C[i][j] for i in range(7))==6 for j in range(2,7)) and all(C[i][j] in (0,1) for i in range(2,7) for j in range(2,7))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p)
    raw=read(W+'controls.json');c=next(r for r in raw['controls'] if r['name']=='t6_h1');C=[[int(v) for v in r] for r in c['cross_gram_rows']];need(normalized(C),'base normalized')
    prior=read('external_conway99_research/verification/wave205-fourth-trace-globalization-verifier/post_source_result.json')['proof_a']['normalized_census']['6'];need(prior['admissible_by_h']=={'0':0,'1':18,'2':0},'archived complete admissible count')
    actions=[];images={}
    for trans,swap in itertools.product((False,True),repeat=2):
        for rtail in itertools.permutations(range(4,7)):
            for ctail in itertools.permutations(range(4,7)):
                rp=([1,0,3,2] if swap else [0,1,2,3])+list(rtail);cp=([1,0,3,2] if swap else [0,1,2,3])+list(ctail)
                D=[[C[cp[j]][rp[i]] if trans else C[rp[i]][cp[j]] for j in range(7)] for i in range(7)]
                need(sorted(rp)==sorted(cp)==list(range(7)) and normalized(D),'valid normalized action')
                key=tuple(tuple(r) for r in D);idx=images.setdefault(key,len(images));actions.append(dict(transpose_first=trans,row_permutation=rp,column_permutation=cp,image_index=idx))
    need(not normalized([C[1],C[0]]+C[2:]),'wrong marked swap rejected')
    core=[r[2:] for r in C[2:]];allocations=[]
    for side,mat in [('X',core),('Y',[list(r) for r in zip(*core)])]:
        for i,row in enumerate(mat):
            incident=[j for j,v in enumerate(row) if v];first_need=1 if i<2 else 2
            choices=list(itertools.combinations(incident,first_need));need(len(choices)==math.comb(len(incident),first_need),'combination control')
            allocations.append(dict(side=side,ordinary_position=i,incident_cells=incident,first_vertex_required_core_degree=first_need,second_vertex_required_core_degree=len(incident)-first_need,first_vertex_cell_choices=choices,count=len(choices)))
    per_side={side:math.prod(r['count'] for r in allocations if r['side']==side) for side in ['X','Y']}
    initial_normalized=math.prod(per_side.values());unnormalized=16*initial_normalized
    need(time.monotonic()-start<10,'10s inventory bound')
    save(out/'orbit.json',dict(actions=actions,images=[list(map(list,k)) for k,v in sorted(images.items(),key=lambda kv:kv[1])],archived_count=18,conditional_one_orbit=len(images)==18))
    save(out/'endpoint_inventory.json',dict(allocations=allocations,per_side_counts=per_side,
        normalized_degree_correct_candidates=initial_normalized,four_special_endpoint_choices=16,unnormalized_degree_correct_candidates=unnormalized,
        valid_local_cap_lifts=None,valid_local_cap_lifts_reason='Not enumerated; counts above precede all remaining local lambda/mu checks.',
        residual_internal_pair_flip_group_order=64,residual_action_quotient_used=False))
    inputs=dict(PINS)
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    summary=dict(status='CANDIDATE_T6_ORBIT_AND_PRECAP_LIFT_INVENTORY',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python_version=sys.version,
        uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=inputs,
        outputs_sha256={p.as_posix():sha(p) for p in out.iterdir() if p.is_file()},
        generated_actions=len(actions),distinct_normalized_matrices=len(images),conditional_one_orbit=len(images)==18,
        archived_matrix_count_relied_upon=True,independent_census_rerun=False,
        degree_correct_candidates_after_special_endpoint_normalization=initial_normalized,valid_lift_count='UNKNOWN',
        new_graph_lifts_examined=0,solver_calls=0,ledger_writes=0,elapsed_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['status','distinct_normalized_matrices','conditional_one_orbit','degree_correct_candidates_after_special_endpoint_normalization','valid_lift_count']}))
if __name__=='__main__':main()
