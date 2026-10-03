"""Independent exact raw twelve-column object checker, no producer imports."""
import argparse, copy, hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
GATE=B/'20260930_independent_review/hadamard_four_group_local_screen/summary.json'
WIT=B/'20260930_hadamard_four_group_joint_v2/case_000/first_witness.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',GATE:'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67',WIT:'b4973edd9d4cbf2ca965b36ccfa9cb22515e81a68315368c772487b57b6e7b9d'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def context():
    raw=read(RAW);C=[[int((i%12==j%12 and i//12!=j//12) or (i//12==j//12 and (i%12)^1==j%12)) for j in range(36)] for i in range(36)]
    K=[[12*int(i==j)+2-C[i][j]-sum(C[i][k]*C[k][j] for k in range(36))-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(C==raw['core_adjacency'] and K==raw['prescribed_Gram36'],'independent core and Gram')
    groups=list(dict.fromkeys(tuple(i for i in range(12) if raw['L'][i][d]) for d in range(60)))
    return K,groups,read(LOCAL)
def decompose(matrix):
    """Literal perfect-matching removal for a 3x3 integer regular matrix."""
    from itertools import permutations
    M=[r[:] for r in matrix];q=sum(M[0]);need(all(sum(r)==q for r in M) and all(sum(M[i][j] for i in range(3))==q for j in range(3)),'regular margins')
    result=[]
    for _ in range(q):
        p=next((p for p in permutations(range(3)) if all(M[i][p[i]]>0 for i in range(3))),None)
        need(p is not None,'explicit residual pair matching')
        result.append(list(p))
        for i in range(3):M[i][p[i]]-=1
    need(not any(v for row in M for v in row),'complete pairwise decomposition')
    return result
def check(w,case,K,groups,local):
    need(w['case']==case['case'] and w['groups']==case['groups'],'exact profile case')
    F=w['factor36x12'];need(len(F)==36 and all(len(r)==12 for r in F),'36x12 shape')
    need(all(type(v) is int and v in [0,1] for r in F for v in r),'binary exact entries')
    chosen=w['chosen'];ids=[];reconstructed=[[0]*12 for _ in range(36)]
    need(len(chosen)==4,'four choices')
    for side,(g,index) in enumerate(zip(case['groups'],chosen,strict=True)):
        need(type(index) is int and 0<=index<len(case['local_survivor_indices'][side]),'domain index')
        need(int(case['gram_caps_ac']['final_masks'][side],16)>>index&1,'choice in final AC domain')
        cat=case['local_survivor_indices'][side][index];ids.append(cat)
        for d,word in enumerate(local['survivors'][cat]):
            for pos,a in enumerate(groups[g]):reconstructed[12*local['words'][word][pos]+a][3*side+d]=1
    need(ids==w['local_survivor_indices'] and F==reconstructed,'exact independently decoded columns')
    columns=[{i for i in range(36) if F[i][d]} for d in range(12)]
    need(all(len(col)==6 and all(sum(i//12==f for i in col)==2 for f in range(3)) for col in columns),'column margins')
    G=[[len({d for d in range(12) if F[i][d]}&{d for d in range(12) if F[j][d]}) for j in range(36)] for i in range(36)]
    R=[[K[i][j]-G[i][j] for j in range(36)] for i in range(36)]
    need(all(x>=0 for r in R for x in r),'all1296 residual entries nonnegative')
    need(R==w['residual_Gram36'],'entire residual matrix')
    overlaps=[len(a&b) for a,b in combinations(columns,2)];need(all(x<=2 for x in overlaps),'all66 column caps')
    decomposition=[];expected=[]
    for a,b in combinations(range(12),2):
        if b==a^1:continue
        remaining=5-sum(a in groups[g] and b in groups[g] for g in case['groups'])
        m=[[R[12*f+a][12*h+b] for h in range(3)] for f in range(3)]
        need(all(sum(r)==remaining for r in m) and all(sum(m[i][j] for i in range(3))==remaining for j in range(3)),'all60 exact balanced pair margins')
        expected.append(dict(coordinates=[a,b],remaining_groups=remaining,matrix=m))
        decomposition.append(dict(coordinates=[a,b],permutations=decompose(m)))
    need(w['remaining_balanced_pair_margins']==expected,'raw pair-margin records')
    need(w['target_graph'] is False and w['completion_claim'] is False,'explicit partial scope')
    return dict(case=case['case'],groups=case['groups'],choices=chosen,local_survivor_indices=ids,Gram_entries=1296,column_pairs=66,max_column_overlap=max(overlaps),nonnegative_residual=True,pairwise_permutation_decompositions=decomposition,scope='Only these twelve columns and separately decomposed coordinate-pair residuals; no common remaining48-column factor.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        pins={}
        for p,h in PINS.items():need(sha(p)==h,'pin '+key(p));pins[key(p)]=h
        g=read(GATE);casepath=B/'20260930_hadamard_four_group_local_screen/case_000.json';need(sha(casepath)==g['inputs_sha256'][key(casepath)],'gate-authenticated exact case');pins[key(casepath)]=sha(casepath)
        K,groups,local=context();w=read(WIT);case=read(casepath);result=check(w,case,K,groups,local);write(out/'independent_object.json',result)
        rejected=[]
        def reject(name,bad):
            try:check(bad,case,K,groups,local)
            except(ValueError,IndexError,KeyError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corrupt object '+name)
        bad=copy.deepcopy(w);bad['factor36x12'][0][0]^=1;reject('flipped_raw_bit',bad)
        bad=copy.deepcopy(w);bad['factor36x12'][0][0]=2;reject('nonbinary_bit',bad)
        bad=copy.deepcopy(w);bad['chosen'][0]=999;reject('wrong_choice',bad)
        bad=copy.deepcopy(w);bad['local_survivor_indices'][0]+=1;reject('wrong_catalogue_id',bad)
        bad=copy.deepcopy(w);bad['residual_Gram36'][0][0]+=1;reject('wrong_residual',bad)
        bad=copy.deepcopy(w);bad['remaining_balanced_pair_margins'][0]['remaining_groups']+=1;reject('wrong_pair_margin',bad)
        bad=copy.deepcopy(w);bad['target_graph']=True;reject('false_completion_metadata',bad)
        for p in [Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        ts=datetime.now(timezone.utc).isoformat();write(out/'controls.json',dict(corruptions_rejected=rejected))
        report=dict(status='INDEPENDENT_FOUR_GROUP_PARTIAL12_OBJECT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},case=0,raw_columns=12,all_Gram_entries=1296,all_column_caps=66,independent_pairwise_decompositions=60,corruptions_rejected=len(rejected),producer_imports=False,solver_calls=0,target_resolution=False,scope='An exact twelve-column partial construction only. Residual pair matchings are separate witnesses, not a joint extension.')
        write(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
