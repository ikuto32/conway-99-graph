"""Cheap candidate modular-rank extension tests on frozen local witnesses."""
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
OUT=B/'20260930_modular_rank_screen'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def rank(a,p):
    b=[[x%p for x in row]for row in a];r=0;piv=[]
    for col in range(len(b[0])):
        hit=next((i for i in range(r,len(b)) if b[i][col]),None)
        if hit is None:continue
        b[r],b[hit]=b[hit],b[r]
        inv=pow(b[r][col],-1,p);b[r]=[(x*inv)%p for x in b[r]]
        for i in range(len(b)):
            if i!=r:
                c=b[i][col];b[i]=[(x-c*y)%p for x,y in zip(b[i],b[r])]
        piv.append(col);r+=1
        if r==len(b):break
    return r,piv,b
def main():
    paths=[B/'20260930_rook_free_internal_independent_certificate/independent_full59.json']
    paths += [B/f'20260930_rook_lazy_wave01/round_{i:02d}/independent_sat/independent_full59.json'for i in range(1,9)]
    paths += [B/'20260930_rook_box_lazy_wave02/round_01/independent_sat/independent_full59.json',B/'20260930_independent_review/rook_orbit_sat_replay_v2/independent_full59.json']
    assert all(p.exists()for p in paths)
    OUT.mkdir(exist_ok=False)
    save(OUT/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in [Path(__file__),*paths,ROOT/'uv.lock']},
        'question':'Do three exact modular rank necessities reject the eleven saved local59 witnesses?',
        'selection':'Exactly the original witness, all eight wave01 witnesses, one wave02 witness, and the orbit witness; no outcome-based selection.',
        'scope':'Candidate necessary extension tests on eleven exact principal submatrices only.',
        'limits':{'matrices':33,'matrix_order':59,'seconds':30},'thresholds':{'rank_A_mod2_max':54,'rank_A_mod3_max':45,'rank_G_mod2_max':44},
        'status':'CANDIDATE','independent_review_required':True,'random_seed':None,'random_seed_null_reason':'Deterministic finite arithmetic.'})
    for p in (2,3):
        assert rank([[1,0],[0,1]],p)[0]==2 and rank([[1,1],[1,1]],p)[0]==1 and rank([[0,0],[0,0]],p)[0]==0
        assert rank([[1,1],[1,0]],p)[0]==2
    records=[];seen=set()
    for path in paths:
        a=json.loads(path.read_bytes())['adjacency_full59'];n=len(a);assert n==59
        assert all(len(row)==n and all(type(x)is int and x in(0,1)for x in row)for row in a)
        assert all(a[i][j]==a[j][i]for i in range(n)for j in range(n)) and all(a[i][i]==0for i in range(n))
        graphhash=sha256(bytes(x for row in a for x in row)).hexdigest();seen.add(graphhash)
        g=[[27*(i==j)-9*a[i][j]+1for j in range(n)]for i in range(n)]
        tests=[]
        for label,m,p,bound in [('A_mod2',a,2,54),('A_mod3',a,3,45),('G_mod2',g,2,44)]:
            r,piv,reduced=rank(m,p)
            tests.append({'matrix':label,'prime':p,'rank':r,'target_max':bound,'obstruction_candidate':r>bound,'pivot_columns':piv,'reduced_matrix':reduced})
        records.append({'path':path.relative_to(ROOT).as_posix(),'raw_sha256':h(path),'matrix_bytes_sha256':graphhash,'tests':tests})
    save(OUT/'results.json',{'status':'CANDIDATE_PENDING_INDEPENDENT_REVIEW','records':records,'distinct_raw_matrices':len(seen),
        'proof_candidate':'Over Q a target has characteristic polynomial (t-14)(t-3)^54(t+4)^44, by the target identity, regularity and trace. Mod2, A^2=A so the squarefree annihilator and characteristic multiplicities give rank54. Mod3, A(A+I)^2=0 because A^2+A=-J and (A+I)J=0, so the zero-primary component has dimension54 and is killed by A; rank45. G^2=63G and real characteristic polynomial t^55(t-63)^44 imply mod2 idempotence and rank44. A principal submatrix cannot have larger rank than the full matrix over the same field.',
        'limitations':['No novelty claim.','These are principal-submatrix obstructions, not whole-family exclusions.','Gaussian elimination and universal rank derivations require separate review before promotion.']})
    print(json.dumps({'cases':len(records),'distinct':len(seen),'ranks':[[t['rank']for t in r['tests']]for r in records]}))
if __name__=='__main__':main()
